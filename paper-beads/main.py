"""Paper beads — sheet-hyperobjects cartridge (Pliego).

A long strip of paper wound tightly round a needle from its wide end to its tip, then glued: a
rolled paper bead. One generator, three strip shapes (`style`):

- `bicone`: a long isosceles triangle (straight sides from the full width W to a blunt tip). The
  bead is fattest in the middle and tapers to both ends.
- `tube`: a rectangle. Every turn has the full width: a cylinder.
- `oval`: a strip with convex (bowed-out) sides, derived so that the bead's profile is an ellipse
  (see below). It depends on the paper's caliper and the needle, so it is computed per run.

Coil geometry. The paper's midsurface winds as an Archimedean spiral r(φ) = r0 + t·φ/2π, with t
the stock's caliper (the TRUE caliper: no exaggerated layer gap, so successive layers lie 0.06 to
0.16 mm apart and look coincident in a viewer) and r0 = needle radius + t/2. After winding a length
u the radius is r(u) ≈ √(r0² + t·u/π) (the paper's cross-section fills the annulus). A layer reaches
the axial half-width w(u)/2 of the strip at that point, so the bead's radius at axial position z is
r(u*) where w(u*) = 2|z|. Choosing w(u) = TIP + (W − TIP)·√(1 − ((r(u) − r0)/(R − r0))²), with
R = r(Ls), makes the profile an ellipse with semi-axes (W − TIP)/2 and R − r0 standing on the core:
the `oval` strip. A straight triangle gives r(z)² linear in |z| (pointed ends); a rectangle gives
a cylinder.

Segmentation. The strip is cut into narrow panels by `F` lines across its length (plain paper,
treatment `none`: never scored). The coiled pose is a prism over a polygon inscribed in the spiral:
vertex k sits on the spiral at the arclength position of F line k, so the pose is an exact isometry
of the strip. Panel chords follow c = 0.85·√(8·r·t) (clamped to 0.6–6 mm): the polygon's sagitta
c²/8r then stays below 0.73·t, so a turn's chords never cut into the turn beneath it. Past 480
panels (the render budget) the factor grows until the strip fits; the run prints the resulting
sagitta/caliper ratio (about 1.0 at worst: 450 mm of foil paper on the thinnest needle). The strip's
tip is blunted to TIP = 2 × the stock's minimum feature so the last panel is cuttable.

The sheet lies with the TIP at x = 0 and the wide end at x = Ls: the studio preview keeps the
lowest face (the tip panel) on the table, so the coil forms at the far end and rolls up the strip
toward the tip, as it does on a table under the needle. Valley rolls: the front ends up inside,
the colour (`back`) outside. The needle is not modelled.

Mode `make`: a kinematic program on the F lines (wrap the wide end round the needle, wind three
stretches, wind the tip and glue it). It ends in the bead, also written as the frame `target:bead`.
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


SLUG = "paper-beads"
STYLES = ("bicone", "tube", "oval")
# caliper (mm) and minimum cuttable feature (mm) from $KR/materials/<stock>/stock.json
CALIPER = {"copy-80": 0.100, "kami": 0.072, "kraft-120": 0.160, "foil-paper": 0.060}
MIN_FEATURE = {"copy-80": 1.0, "kami": 1.0, "kraft-120": 1.0, "foil-paper": 1.5}
SAG = 0.85                 # chord = SAG·√(8 r t): sagitta ≤ SAG²·t
CHORD_MIN, CHORD_MAX = 0.6, 6.0
MAX_PANELS = 480           # render budget: about 4 render vertices per panel

mode = str(PARAM(lambda: mode, "make"))                                 # noqa: F821
style = str(PARAM(lambda: style, "bicone"))                             # noqa: F821
length = pliego.clamp(PARAM(lambda: length, 280.0), 150.0, 450.0)      # noqa: F821
width = pliego.clamp(PARAM(lambda: width, 25.0), 10.0, 40.0)           # noqa: F821
core = pliego.clamp(PARAM(lambda: core, 3.0), 1.5, 6.0)                # noqa: F821
stock = str(PARAM(lambda: stock, "copy-80"))                            # noqa: F821
colour = str(PARAM(lambda: colour, "#2e86ab"))                          # noqa: F821
if mode != "make":
    raise ValueError(f"paper-beads: mode must be make, got {mode!r}")
if style not in STYLES:
    raise ValueError(f"paper-beads: style must be one of {STYLES}, got {style!r}")
if stock not in CALIPER:
    raise ValueError(f"paper-beads: stock must be one of {tuple(CALIPER)}, got {stock!r}")

t = CALIPER[stock]
Ls, W = length, width
TIP = 2.0 * MIN_FEATURE[stock]
r0 = core / 2.0 + t / 2.0


def r_of(u):
    """Midsurface radius after winding a length u (area relation)."""
    return math.sqrt(r0 * r0 + t * u / math.pi)


R = r_of(Ls)


def strip_width(u):
    if style == "tube":
        return W
    if style == "bicone":
        return TIP + (W - TIP) * (1.0 - u / Ls)
    q = min(1.0, (r_of(u) - r0) / (R - r0))
    return TIP + (W - TIP) * math.sqrt(max(0.0, 1.0 - q * q))


# ── F-line positions along the strip (u from the wide end), sagitta-limited chords ──
def chord_stations(sag):
    raw = [0.0]
    while raw[-1] < Ls:
        step = sag * math.sqrt(8.0 * r_of(raw[-1]) * t)
        raw.append(raw[-1] + min(max(step, CHORD_MIN), CHORD_MAX))
    n = len(raw) - 1 if raw[-1] - Ls < 0.5 * (raw[-1] - raw[-2]) else len(raw) - 2
    scale = Ls / raw[n]                # stretch or shrink every chord a little to land on Ls
    return [x * scale for x in raw[:n]] + [Ls]


sag = SAG
us = chord_stations(sag)
while len(us) - 1 > MAX_PANELS:        # render budget binds: longer chords (viewer overlap only)
    sag *= 1.04
    us = chord_stations(sag)
n_pan = len(us) - 1


# ── the strip: tip at x = 0, wide end at x = Ls, symmetric about y = W/2 ──
if style == "oval":
    ring = [(Ls - u, W / 2.0 - strip_width(u) / 2.0) for u in reversed(us)]
    ring += [(Ls - u, W / 2.0 + strip_width(u) / 2.0) for u in us]
else:
    hw = strip_width(Ls) / 2.0
    ring = [(0.0, W / 2.0 - hw), (Ls, 0.0), (Ls, W), (0.0, W / 2.0 + hw)]
strip = pliego.Sheet(
    "strip", ring, stock=stock, grain_deg=0.0,
    label=L4("Bead strip", "Tira para cuenta", "Bande à perle", "Tira para conta"),
    front="#f6f1e7", back=colour)
for u in us[1:-1]:
    strip.crease((Ls - u, -1.0), (Ls - u, W + 1.0), "flat", 0.0, treatment="crease")
cut_check = pliego.papercut.analyze(strip, min_feature_mm=MIN_FEATURE[stock])
if not cut_check.ok:
    raise ValueError(f"paper-beads: the strip fails the papercut check: {cut_check.issues}")

# ── the coil: polygon vertices on the Archimedean spiral at arclength positions us[k] ──


def spiral_pt(phi):
    rad = r0 + t * phi / (2.0 * math.pi)
    return (rad * math.cos(phi), rad * math.sin(phi))


phis = [0.0]
for k in range(n_pan):
    c = us[k + 1] - us[k]
    p0 = spiral_pt(phis[-1])
    lo, hi = 0.0, math.pi
    for _ in range(80):                    # chord length grows with Δφ on (0, π)
        mid = 0.5 * (lo + hi)
        if math.dist(p0, spiral_pt(phis[-1] + mid)) < c:
            lo = mid
        else:
            hi = mid
    phis.append(phis[-1] + 0.5 * (lo + hi))
C = [spiral_pt(p) for p in phis]
SPIN = -1.0                                # mirror so the rolls come out as valleys


def bead(sheet_id, uv):
    u = Ls - uv[0]
    k = 0
    while k < n_pan - 1 and u > us[k + 1]:
        k += 1
    s = (u - us[k]) / (us[k + 1] - us[k])
    x = C[k][0] + s * (C[k + 1][0] - C[k][0])
    y = C[k][1] + s * (C[k + 1][1] - C[k][1])
    return (x, uv[1] - W / 2.0, SPIN * y)


arr = strip.build()


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


angles = fold_angles(bead)
if len(angles) != n_pan - 1:
    raise ValueError(f"paper-beads: expected {n_pan - 1} F lines, found {len(angles)}")
if min(angles.values()) <= 0.0:
    raise ValueError("paper-beads: the coil pose is not a valley roll (orientation error)")
for e, (a, b) in enumerate(arr.edges):                   # isometry self-check on the outline
    pa, pb = bead("strip", (arr.vertices[a].x, arr.vertices[a].y)), bead(
        "strip", (arr.vertices[b].x, arr.vertices[b].y))
    flat = math.dist((arr.vertices[a].x, arr.vertices[a].y), (arr.vertices[b].x,
                                                               arr.vertices[b].y))
    if abs(math.dist(pa, pb) - flat) > 1e-6:
        raise ValueError(f"paper-beads: edge {e} stretches by {math.dist(pa, pb) - flat} mm")


def edge_u(e):
    a, b = arr.edges[e]
    return Ls - 0.5 * (arr.vertices[a].x + arr.vertices[b].x)


turns = phis[-1] / (2.0 * math.pi)
first_turn = 2.0 * math.pi * r0
cuts = [first_turn, first_turn + (Ls - 2 * first_turn) / 3.0,
        first_turn + 2.0 * (Ls - 2 * first_turn) / 3.0, Ls - 2.0 * math.pi * R, Ls + 1.0]
groups = [[] for _ in cuts]
for e in sorted(angles, key=edge_u):
    groups[next(i for i, x in enumerate(cuts) if edge_u(e) < x)].append(e)
groups = [g for g in groups if g]

params = {"style": style, "length": Ls, "width": W, "core": core, "stock": stock,
          "colour": colour}
info = {"panels": n_pan, "turns": round(turns, 2), "caliper_mm": t,
        "bead_diameter_mm": round(2.0 * (R + t / 2.0), 2),
        "bead_length_mm": round(W, 1), "tip_mm": TIP,
        "sagitta_over_caliper": round(sag * sag, 2),
        "max_panel_angle_deg": round(max(angles.values()), 2),
        "min_bridge_mm": cut_check.min_bridge_mm}
print(f"paper-beads: {info}")

LABELS = [
    ("wrap", L4("Wrap the wide end once round the needle, coloured side down",
                "Enrolla una vuelta del extremo ancho en la aguja, con el lado de color hacia "
                "abajo", "Enroulez une fois le bout large autour de l'aiguille, face colorée "
                "dessous", "Enrole uma volta da ponta larga na agulha, com o lado colorido "
                "para baixo")),
    ("wind-1", L4("Keep winding tightly, keeping the strip centred",
                  "Sigue enrollando apretado, con la tira bien centrada",
                  "Continuez à enrouler serré, la bande bien centrée",
                  "Continue enrolando bem apertado, com a tira centrada")),
    ("wind-2", L4("Wind on: the bead grows in the middle",
                  "Sigue enrollando: la cuenta engorda en el centro",
                  "Enroulez encore : la perle grossit au milieu",
                  "Continue enrolando: a conta engorda no meio")),
    ("wind-3", L4("Wind almost to the tip", "Enrolla casi hasta la punta",
                  "Enroulez presque jusqu'à la pointe", "Enrole quase até a ponta")),
    ("glue-tip", L4("Glue the tip and wind the last turn; slide the bead off the needle",
                    "Pon pegamento en la punta y enrolla la última vuelta; saca la cuenta de "
                    "la aguja", "Encollez la pointe et enroulez le dernier tour ; retirez la "
                    "perle de l'aiguille", "Passe cola na ponta e enrole a última volta; "
                    "tire a conta da agulha")),
]
LABELS = LABELS[:len(groups) - 1] + [LABELS[-1]]
steps = []
for (sid, lab), g in zip(LABELS, groups):
    steps.append(pliego.Step(sid, lab, [(pliego.assembly.EdgeRef(strip, e), angles[e])
                                        for e in g], duration_ms=2000))
steps[-1] = pliego.Step(steps[-1].id, steps[-1].label, steps[-1].targets, duration_ms=2000,
                        note=L4("Seal it with varnish or PVA glue once dry.",
                                "Séllala con barniz o pegamento blanco cuando seque.",
                                "Une fois sèche, vernissez-la ou passez de la colle vinylique.",
                                "Depois de seca, sele-a com verniz ou cola branca."))

assembly = pliego.Assembly(
    [strip], controls=[pliego.sequence_control(label=L4("Roll the bead", "Enrollar la cuenta",
                                                        "Rouler la perle", "Enrolar a conta"))],
    sequence=pliego.Sequence(steps, mode="kinematic"),
    targets={"bead": {"angles": dict(angles)}}, title="Paper bead")
doc = assembly.build(cartridge=SLUG, mode=mode, params=params)
# The F lines are plain paper (spec §4: F + `none`): exporters must not score a rolled strip.
tr = doc.data["pliego:edges_treatment"]
for e, a in enumerate(doc.data["edges_assignment"]):
    if a == "F" and tr[e] == "crease":
        tr[e] = "none"
result = doc.stamp()
