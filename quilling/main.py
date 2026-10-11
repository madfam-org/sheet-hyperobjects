"""Quilling (paper filigree) — sheet-hyperobjects cartridge (Pliego).

A narrow strip of paper rolled on a slotted tool into a coil, then shaped. One generator, five
basic shapes (`style`): `tight` (tight coil), `loose` (the tight coil released to relax, end
glued), `teardrop` (a loose coil pinched at one point), `marquise` (pinched at two opposite points:
the eye) and `scroll` (released and left open-ended).

Coils in closed form. The strip's midsurface is a spiral ρ(φ) in polar form, t = the stock's
caliper (true value, no exaggerated layer gap), r0 = 0.5 mm (the tool's slot) + t/2.
- tight: ρ = r0 + t·φ/2π (Archimedean, one caliper per turn).
- loose: ρ = r0 + t·φ/2π + B·H(min(x/(1 − δ), 1)), x = φ/Φ, H(y) = y³(4 − 3y), δ = 2π/Φ: the
  spacing grows outward over two thirds of the turns (density decreasing as the coil relaxes),
  then closes up, and the last turn is a tight turn, so the glued end lies one caliper outside the
  turn beneath. Φ (the turns left after relaxing) is solved so the spiral is exactly the strip's
  length with outer radius D/2 (B = D/2 − r0 − t·Φ/2π).
- scroll: the same with h = x³ (no closing turn): the outer turns open out and the end is free.
- teardrop / marquise: the loose coil's turns are pinched by a polar shape function S(θ) blended in
  with the turn's radius: r = ρ(φ)·(1 + w·(S(θ) − 1)), w = (ρ − r0)/(ρmax − r0), so the inner
  turns stay round and the outer ones take the shape. Teardrop S: a unit circle with two tangent
  lines meeting at a tip at distance d = 1.7 (tip angle 72°). Marquise S: a lens of two circular
  arcs with tips at ±d = ±1.8 (tip angle 64°). B is re-solved so the pinched coil keeps the strip's
  length; the number of turns stays that of the loose coil.

Segmentation. `F` lines across the strip (plain paper, treatment `none`) split it into narrow
panels. Every pose is a prism over a polygon whose sides are the panels (an exact isometry). The
stations (where the F lines fall) are walked on the final shape: chords c = 0.85·√(8·r·t) with r
the tight-coil radius there (so the tight coil's chords never cut the turn beneath), and a vertex
exactly at every pinch corner (each turn's tip). The same chord lengths are then walked along the
tight and loose spirals. The kinematic program blends the panel angles between these exact poses.

The sheet lies with the strip's OUTER end at x = 0 (the studio preview keeps that panel on the
table, so the coil stands on its edge on it); the slot end is at x = length. Valley rolls: the
colour (`back`) ends up outside.
"""

import math

import pliego


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


def L4(en, es, fr, pt):
    return {"en": en, "es": es, "fr": fr, "pt": pt}


SLUG = "quilling"
STYLES = ("tight", "loose", "teardrop", "marquise", "scroll")
CALIPER = {"copy-80": 0.100, "kami": 0.072, "kraft-120": 0.160, "elephant-hide-110": 0.120}
MIN_FEATURE = {"copy-80": 1.0, "kami": 1.0, "kraft-120": 1.0, "elephant-hide-110": 1.0}
SLOT_R = 0.5               # mm, radius of the slotted tool's tine
SAG = 0.85
CHORD_MIN, CHORD_MAX = 0.7, 4.0
PANEL_MIN = 0.4           # mm, shortest panel (with a 3 mm strip: 1.2 mm², above the 1 mm² floor)
MAX_PANELS = 480           # render budget (~4 vertices per panel)
TEAR_D, EYE_D = 1.7, 1.8   # tip distance of the pinch shapes (unit round radius)

mode = str(PARAM(lambda: mode, "make"))                                 # noqa: F821
style = str(PARAM(lambda: style, "teardrop"))                           # noqa: F821
length = pliego.clamp(PARAM(lambda: length, 150.0), 60.0, 300.0)       # noqa: F821
width = pliego.clamp(PARAM(lambda: width, 5.0), 3.0, 10.0)             # noqa: F821
diameter = pliego.clamp(PARAM(lambda: diameter, 12.0), 6.0, 25.0)      # noqa: F821
stock = str(PARAM(lambda: stock, "copy-80"))                            # noqa: F821
colour = str(PARAM(lambda: colour, "#7768ae"))                          # noqa: F821
if mode != "make":
    raise ValueError(f"quilling: mode must be make, got {mode!r}")
if style not in STYLES:
    raise ValueError(f"quilling: style must be one of {STYLES}, got {style!r}")
if stock not in CALIPER:
    raise ValueError(f"quilling: stock must be one of {tuple(CALIPER)}, got {stock!r}")

t = CALIPER[stock]
Ls, W = length, width
r0 = SLOT_R + t / 2.0
TAU = 2.0 * math.pi
R_tight = math.sqrt(r0 * r0 + t * Ls / math.pi)
if diameter < 4.0 * R_tight:
    raise ValueError(f"quilling: a {Ls:g} mm strip rolls into a {2 * R_tight:.1f} mm tight coil; "
                     f"a relaxed coil needs a diameter of at least {4.0 * R_tight:.1f} mm")
R_out = diameter / 2.0


def r_tight(s):
    return math.sqrt(r0 * r0 + t * s / math.pi)


# ── the spirals ───────────────────────────────────────────────────────────────


def h_loose(x, delta):
    y = min(max(x / (1.0 - delta), 0.0), 1.0)
    return y * y * y * (4.0 - 3.0 * y)


def h_scroll(x, delta):
    return max(x, 0.0) ** 3


def s_tear(th):
    a = math.atan2(math.sin(th), math.cos(th))           # (−π, π], tip at 0
    tt = math.acos(1.0 / TEAR_D)
    return 1.0 / math.cos(abs(a) - tt) if abs(a) < tt else 1.0


def s_eye(th):
    c = (EYE_D * EYE_D - 1.0) / 2.0
    s = abs(math.sin(th))
    return -c * s + math.sqrt(c * c * s * s + EYE_D * EYE_D)


def make_curve(kind, Phi=0.0, B=0.0, h=None, shape=None):
    delta = TAU / Phi if Phi else 0.0
    rmax = r0 + t * Phi / TAU + B

    def rho(phi):
        if kind == "tight":
            return r0 + t * phi / TAU
        return r0 + t * phi / TAU + B * h(phi / Phi, delta)

    def at(phi):
        r = rho(phi)
        if shape is not None:
            w = min(1.0, (r - r0) / (rmax - r0))
            r *= 1.0 + w * (shape(phi) - 1.0)
        return (r * math.cos(phi), r * math.sin(phi))
    return at


def arc_length(at, phi_end, n=3000):
    total, p = 0.0, at(0.0)
    for i in range(1, n + 1):
        q = at(phi_end * i / n)
        total += math.dist(p, q)
        p = q
    return total


def bisect(f, lo, hi, target, it=60):
    """x in [lo, hi] with f(x) = target, f increasing."""
    for _ in range(it):
        mid = 0.5 * (lo + hi)
        if f(mid) < target:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


Phi_tight = TAU * (R_tight - r0) / t
relaxed_h = h_scroll if style == "scroll" else h_loose


def relaxed(Phi):
    return make_curve("relaxed", Phi, R_out - r0 - t * Phi / TAU, relaxed_h)


Phi_max = TAU * (R_out - r0) / t - 1e-6            # B ≥ 0
Phi_lo, Phi_hi = 2.5 * TAU, min(Phi_tight, Phi_max)
if Phi_lo >= Phi_hi or arc_length(relaxed(Phi_lo), Phi_lo) > Ls:
    raise ValueError(f"quilling: a {Ls:g} mm strip cannot make 2.5 turns at {diameter:g} mm; "
                     f"use a longer strip or a smaller diameter")
Phi = bisect(lambda P: arc_length(relaxed(P), P), Phi_lo, Phi_hi, Ls)
B_loose = R_out - r0 - t * Phi / TAU
curves = {"tight": make_curve("tight"), "loose": relaxed(Phi)}
corners = []
if style in ("teardrop", "marquise"):
    shape = s_tear if style == "teardrop" else s_eye

    def pinched(B):
        return make_curve("relaxed", Phi, B, h_loose, shape)
    B_pinch = bisect(lambda b: arc_length(pinched(b), Phi), 0.0, B_loose, Ls)
    curves[style] = pinched(B_pinch)
    period = TAU if style == "teardrop" else math.pi
    corners = [k * period for k in range(1, int(Phi / period) + 2)]
final = style if style in curves else "loose"
if style == "scroll":
    curves["scroll"] = curves.pop("loose")
    final = "scroll"


def advance(at, phi, c):
    """The parameter beyond `phi` where the curve is at chord distance c from at(phi)."""
    p = at(phi)
    lo, hi = phi, phi + 0.05
    while math.dist(p, at(hi)) < c:
        lo, hi = hi, hi + 0.05
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if math.dist(p, at(mid)) < c:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


# ── stations: walked on the final shape, with a vertex at every pinch corner ──
def walk_final(sag):
    at = curves[final]
    phi, s, chords, nxt = 0.0, 0.0, [], 0
    landed.clear()
    while Ls - s > 1e-9:
        c = min(max(sag * math.sqrt(8.0 * r_tight(s) * t), CHORD_MIN), CHORD_MAX)
        while nxt < len(corners) and corners[nxt] <= phi + 1e-9:
            nxt += 1
        cand_c, cand_phi = c, None
        if nxt < len(corners):
            d = math.dist(at(phi), at(corners[nxt]))
            if d < PANEL_MIN:                       # a station already sits on this corner
                nxt += 1
                continue
            if d <= c:                              # land exactly on the corner
                cand_c, cand_phi = d, corners[nxt]
            elif d < 2.0 * c:                       # halve the way, then land on it
                cand_c = d / 2.0
        if Ls - s < 1.5 * c:                        # finish: one or two last panels
            rest = Ls - s
            if rest < PANEL_MIN and chords:
                chords[-1] += rest
            else:
                chords += [rest] if rest < 1.2 * c else [rest / 2.0, rest / 2.0]
            break
        if cand_phi is not None:
            landed.append(cand_phi)
        phi = cand_phi if cand_phi is not None else advance(at, phi, cand_c)
        chords.append(cand_c)
        s += cand_c
    return chords


landed = []
sag = SAG
chords = walk_final(sag)
while len(chords) > MAX_PANELS:
    sag *= 1.04
    chords = walk_final(sag)
n_pan = len(chords)
us = [0.0]
for c in chords:
    us.append(us[-1] + c)
us[-1] = Ls


def polygon(at):
    pts, phi = [at(0.0)], 0.0
    for c in chords:
        phi = advance(at, phi, c)
        pts.append(at(phi))
    return pts


polys = {name: polygon(at) for name, at in curves.items()}

# ── the strip: outer end at x = 0, slot end at x = Ls ──
strip = pliego.Sheet(
    "strip", [(0.0, 0.0), (Ls, 0.0), (Ls, W), (0.0, W)], stock=stock, grain_deg=0.0,
    label=L4("Quilling strip", "Tira para filigrana", "Bande de paperolle", "Tira de quilling"),
    front="#f6f1e7", back=colour)
for u in us[1:-1]:
    strip.bend((Ls - u, 0.0), (Ls - u, W))
cut_check = pliego.papercut.analyze(strip, min_feature_mm=MIN_FEATURE[stock])
if not cut_check.ok:
    raise ValueError(f"quilling: the strip fails the papercut check: {cut_check.issues}")
arr = strip.build()
SPIN = -1.0                                # mirror so the rolls come out as valleys


def pose_of(V):
    def pose(sheet_id, uv):
        u = Ls - uv[0]
        k = 0
        while k < n_pan - 1 and u > us[k + 1]:
            k += 1
        s = (u - us[k]) / (us[k + 1] - us[k])
        return (V[k][0] + s * (V[k + 1][0] - V[k][0]), uv[1] - W / 2.0,
                SPIN * (V[k][1] + s * (V[k + 1][1] - V[k][1])))
    return pose


def newell(pts):
    n = [0.0, 0.0, 0.0]
    for i, p in enumerate(pts):
        q = pts[(i + 1) % len(pts)]
        n[0] += (p[1] - q[1]) * (p[2] + q[2])
        n[1] += (p[2] - q[2]) * (p[0] + q[0])
        n[2] += (p[0] - q[0]) * (p[1] + q[1])
    s = math.sqrt(n[0] ** 2 + n[1] ** 2 + n[2] ** 2)
    return (n[0] / s, n[1] / s, n[2] / s)


def fold_angles(pose):
    """Signed fold angle (FOLD convention, deg) of every interior F/M/V edge in `pose`."""
    pts = [pose("strip", (v.x, v.y)) for v in arr.vertices]
    left = {}
    for fi, f in enumerate(arr.faces):
        for k in range(len(f)):
            left[(f[k], f[(k + 1) % len(f)])] = fi
    normals = [newell([pts[v] for v in f]) for f in arr.faces]
    out = {}
    for e, (a, b) in enumerate(arr.edges):
        if arr.assignment[e] in ("F", "M", "V") and (a, b) in left and (b, a) in left:
            edge = tuple(pts[b][i] - pts[a][i] for i in range(3))
            out[e] = pliego.tessellate.signed_fold_angle(normals[left[(a, b)]],
                                                         normals[left[(b, a)]], edge)
    return out


angles = {}
for name, V in polys.items():
    pose = pose_of(V)
    for a, b in arr.edges:                         # isometry self-check, every edge
        pa, pb = (pose("strip", (arr.vertices[i].x, arr.vertices[i].y)) for i in (a, b))
        flat = math.dist((arr.vertices[a].x, arr.vertices[a].y),
                         (arr.vertices[b].x, arr.vertices[b].y))
        if abs(math.dist(pa, pb) - flat) > 1e-6:
            raise ValueError(f"quilling: the {name} pose stretches an edge by "
                             f"{math.dist(pa, pb) - flat} mm")
    angles[name] = fold_angles(pose)
    if len(angles[name]) != n_pan - 1:
        raise ValueError(f"quilling: expected {n_pan - 1} F lines, found {len(angles[name])}")
if min(angles["tight"].values()) <= 0.0:
    raise ValueError("quilling: the tight coil is not a valley roll (orientation error)")
if style == "loose":                               # the glued end lies on the turn beneath
    end = curves["loose"](Phi)
    below = curves["loose"](Phi - TAU)
    if abs(math.hypot(*end) - math.hypot(*below) - t) > 1e-9:
        raise ValueError("quilling: the loose coil's end does not lie on the turn beneath")


def edge_u(e):
    a, b = arr.edges[e]
    return Ls - 0.5 * (arr.vertices[a].x + arr.vertices[b].x)


slot_part = [e for e in angles["tight"] if edge_u(e) < 2.0 * TAU * r0]
rest_part = [e for e in angles["tight"] if e not in slot_part]
rest_part.sort(key=edge_u)
half = len(rest_part) // 2


def targets(name, edges):
    return [(pliego.assembly.EdgeRef(strip, e), angles[name][e]) for e in edges]


steps = [
    pliego.Step("slot", L4("Slip the strip's end into the tool's slot and turn the first turns",
                           "Mete la punta de la tira en la ranura de la herramienta y da las "
                           "primeras vueltas", "Glissez le bout de la bande dans la fente de "
                           "l'outil et faites les premiers tours", "Encaixe a ponta da tira na "
                           "fenda da ferramenta e dê as primeiras voltas"),
                targets("tight", slot_part), duration_ms=1500),
    pliego.Step("roll", L4("Roll evenly, keeping the edges aligned",
                           "Enrolla parejo, con los bordes alineados",
                           "Roulez régulièrement, bords alignés",
                           "Enrole por igual, com as bordas alinhadas"),
                targets("tight", rest_part[:half]), duration_ms=2000),
    pliego.Step("roll-on", L4("Roll to the end: a tight coil", "Enrolla hasta el final: una "
                              "espiral cerrada", "Roulez jusqu'au bout : un rouleau serré",
                              "Enrole até o fim: um rolinho fechado"),
                targets("tight", rest_part[half:]), duration_ms=2000,
                note=L4("For a tight coil, glue the end now and slide it off the tool.",
                        "Para una espiral cerrada, pega la punta ahora y sácala de la "
                        "herramienta.", "Pour un rouleau serré, collez le bout maintenant et "
                        "retirez-le de l'outil.", "Para um rolinho fechado, cole a ponta agora "
                        "e tire-o da ferramenta.")),
]
all_e = sorted(angles["tight"], key=edge_u)
if style in ("loose", "teardrop", "marquise"):
    steps.append(pliego.Step("release", L4(
        "Slide it off and let it go: it relaxes into a loose coil; glue the end",
        "Sácala y suéltala: se afloja en una espiral abierta; pega la punta",
        "Retirez-le et lâchez-le : il se détend en spirale lâche ; collez le bout",
        "Tire-o e solte-o: ele se afrouxa numa espiral aberta; cole a ponta"),
        targets("loose", all_e), duration_ms=2500))
if style == "scroll":
    steps.append(pliego.Step("release", L4(
        "Slide it off and let it open; leave the end free: a scroll",
        "Sácala y déjala abrirse; deja la punta suelta: una voluta",
        "Retirez-le et laissez-le s'ouvrir ; laissez le bout libre : une volute",
        "Tire-o e deixe-o abrir; deixe a ponta solta: um arabesco"),
        targets("scroll", all_e), duration_ms=2500))
if style == "teardrop":
    steps.append(pliego.Step("pinch", L4(
        "Pinch the coil at one point: a teardrop", "Pellizca la espiral en un punto: una gota",
        "Pincez la spirale en un point : une goutte", "Belisque a espiral num ponto: uma gota"),
        targets("teardrop", all_e), duration_ms=2000))
if style == "marquise":
    steps.append(pliego.Step("pinch", L4(
        "Pinch it at two opposite points: a marquise (eye)",
        "Pellízcala en dos puntos opuestos: un ojo (marquesa)",
        "Pincez-la en deux points opposés : un œil (marquise)",
        "Belisque-a em dois pontos opostos: um olho (marquise)"),
        targets("marquise", all_e), duration_ms=2000))

params = {"style": style, "length": Ls, "width": W, "diameter": diameter, "stock": stock,
          "colour": colour}
info = {"panels": n_pan, "caliper_mm": t, "tight_diameter_mm": round(2 * (R_tight + t / 2), 2),
        "relaxed_turns": round(Phi / TAU, 2), "loose_spread_mm": round(B_loose, 3),
        "pinch_corners": len(landed), "sagitta_over_caliper": round(sag * sag, 2),
        "min_bridge_mm": cut_check.min_bridge_mm}
if style in ("teardrop", "marquise"):
    info["pinched_spread_mm"] = round(B_pinch, 3)
print(f"quilling: {info}")

assembly = pliego.Assembly(
    [strip], controls=[pliego.sequence_control(label=L4("Roll and shape", "Enrollar y dar forma",
                                                        "Rouler et façonner", "Enrolar e "
                                                        "modelar"))],
    sequence=pliego.Sequence(steps, mode="kinematic"),
    targets={name: {"angles": dict(a)} for name, a in angles.items()}, title="Quilling")
doc = assembly.build(cartridge=SLUG, mode=mode, params=params)
result = doc.stamp()
