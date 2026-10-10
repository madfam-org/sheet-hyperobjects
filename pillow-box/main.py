"""Pillow box — sheet-hyperobjects cartridge (Pliego).

The curved-score pillow pack: one blank of folding boxboard, two bulging panels joined by two
straight side scores, closed at each end by two lens-shaped flaps that fold in along curved
scores. Generated from inside dimensions (closed width, tip-to-tip length, pillow thickness),
thickness-compensated by the board caliper t (centre-line rule: inside + t). The seam is a lap
joint down the middle of the back panel, so the blank is symmetric.

**Geometry (reflection construction).** Each panel bends into a cylinder whose generators run
along the box; its cross-section is a polygon of ``facets`` equal facets approximating a
circular arc. An end of the box is the plane ``Y + k|Z| = const`` (k = tan ``end_tilt``), tilted
from the cross-section by ``end_tilt``; the paper beyond it is *reflected* across it. A cylinder
cut by a plane and reflected is an exact curved fold (both sides stay developable; the fold
angle varies along the crease). With ``z(u)`` the panel's height above the box's mid-plane:

- the curved score is ``y = y_end − k·z(u)`` (a planar ellipse in 3-D, a cosine-like curve flat);
- the flap's outer cut is where the reflected paper reaches the mid-plane,
  ``y = y_end + z(u)·(1 − k²)/(2k)``: the front and back flaps meet edge to edge there;
- both curves meet at the side scores (z = 0), so every flap is a lens; ``end_tilt`` = 30°
  (k = 1/√3) makes the lens symmetric (equal score and cut sagittas).

Curvature is drawn as polylines, one vertex per ruling (facet edge). Rulings are plain board
(FOLD ``F`` lines, treatment ``none``, patched into the built document), so the die carries only
the side scores and the curved scores.

**Program (kinematic, exact).** Fold the blank into the flattened, glued tube (two straight
folds), then erect it. Erecting is a one-parameter family of exact rigid-ruling states: for an
end tilt ψ running from 90° down to ``end_tilt``, the heights scale as ``z'(u) = z(u)·k/tan ψ``
(the creases stay where the die put them) and the paper beyond each end plane is reflected
again — squeezing the flat tube makes the panels bulge and all four lens flaps fold in
together, as a pillow box is popped open by hand. Every key pose is computed in closed form and
checked with ``pliego.kinematics.closure_residual``. With the rulings fixed, one end cannot close
on its own once the panels bulge (the motion solver finds no rigid path), so the ends close
together; real board also bends between the rulings, which is the physics engine's part.
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


width = float(PARAM(lambda: width, 90.0))           # noqa: F821 - inside closed width (mm)
length = float(PARAM(lambda: length, 160.0))        # noqa: F821 - inside tip-to-tip length
thickness = float(PARAM(lambda: thickness, 34.0))   # noqa: F821 - inside pillow thickness
end_tilt = float(PARAM(lambda: end_tilt, 30.0))     # noqa: F821 - end-plane tilt (deg)
facets = round(float(PARAM(lambda: facets, 9)))     # noqa: F821 - facets per panel (odd)
stock = str(PARAM(lambda: stock, "folding-boxboard-300"))   # noqa: F821
branding = bool(PARAM(lambda: branding, True))      # noqa: F821

STOCKS = ("folding-boxboard-300", "sbs-board-350", "cardstock-300", "kraftliner-150")
if stock not in STOCKS:
    raise ValueError(f"pillow-box: stock must be one of {STOCKS}, got {stock!r}")
width = pliego.clamp(width, 40.0, 250.0)
length = pliego.clamp(length, 60.0, 400.0)
thickness = pliego.clamp(thickness, 0.12 * width, 0.6 * width)
end_tilt = pliego.clamp(end_tilt, 20.0, 40.0)
n = 2 * (int(pliego.clamp(facets, 5, 15)) // 2) + 1   # odd: the middle facet lies level
m = n // 2                                             # the middle facet's index

t = pliego.board.caliper(stock)
C = width + t                  # centre-line chord of one panel (closed width)
T = thickness + t              # centre-line pillow thickness
Lp = length + t                # centre-line tip-to-tip length
k = math.tan(math.radians(end_tilt))
c = max(t, 0.5)                # flap clearance at the seam
ERECT = 8                      # key poses of the erecting motion


# ── the panel's cross-section: n equal facets turning symmetrically (a discrete arc) ──────────
def section(phi):
    xs_, zs_ = [0.0], [0.0]
    for i in range(n):
        al = phi * (1.0 - (2 * i + 1) / n)
        xs_.append(xs_[-1] + math.cos(al))
        zs_.append(zs_[-1] + math.sin(al))
    return xs_, zs_


lo, hi = 1e-4, math.radians(89.0)
for _ in range(80):                       # bisection: height / chord grows with phi
    mid = (lo + hi) / 2.0
    xs, zs = section(mid)
    if max(zs) / xs[-1] < (T / 2.0) / C:
        lo = mid
    else:
        hi = mid
xs, zs = section((lo + hi) / 2.0)
a = C / xs[-1]                             # facet width (flat)
Z = [z * a for z in zs]                    # closed heights at the rulings (front, S_L → S_R)
w = n * a                                  # flat width of one panel
U = 2.0 * w                                # the blank's width from seam to seam
zmax = max(Z)
s_cut = zmax * (1.0 - k * k) / (2.0 * k)   # cut sagitta; the score's is k·zmax
y0 = s_cut                                 # bottom tips (the sheet starts at y = 0)
y1 = y0 + Lp                               # top tips
G = min(14.0, 0.4 * w)                     # lap of the seam


def ys(z):
    """Bottom cut, bottom score, top score, top cut where the closed height is z."""
    return (y0 - z * (1.0 - k * k) / (2.0 * k), y0 + k * z, y1 - k * z,
            y1 + z * (1.0 - k * k) / (2.0 * k))


# ── strips in blank order: half of the back's middle facet, back, front, back, other half ─────
# a column is ("F", i) front ruling i, ("B", i) back ruling i, or ("S", m) the seam
cols = ([("S", m)] + [("B", i) for i in range(m, -1, -1)] + [("F", i) for i in range(1, n + 1)]
        + [("B", i) for i in range(n - 1, m, -1)] + [("S", m)])
us = [0.0] + [a / 2.0 + j * a for j in range(len(cols) - 2)] + [U]
zc = [Z[i] for _, i in cols]               # closed height of each column (the seam: Z[m])
strips = ["front" if cols[j + 1][0] == "F" else "back" for j in range(len(cols) - 1)]
SIDE_FOLDS = {j for j in range(1, len(cols) - 1) if cols[j][0] in "BF" and cols[j][1] in (0, n)
              and strips[j - 1] != strips[j]}


def state(kp):
    """3-D (X, Z) of every column for end-plane slope kp (None: the flattened tube)."""
    zz = [0.0 if kp is None else z * k / kp for z in Z]
    X = [0.0]
    for i in range(n):
        X.append(X[-1] + math.sqrt(max(a * a - (zz[i + 1] - zz[i]) ** 2, 0.0)))
    out = []
    for kind, i in cols:
        if kind == "F":
            out.append((X[i], zz[i]))
        elif kind == "B":
            out.append((X[i], -zz[i]))
        else:
            out.append(((X[m] + X[m + 1]) / 2.0, -zz[m]))
    return out


def dot(p, q):
    return p[0] * q[0] + p[1] * q[1] + p[2] * q[2]


def unit(p):
    s = math.sqrt(dot(p, p))
    return (p[0] / s, p[1] / s, p[2] / s)


def maps_for(kp):
    """Flat (u, y) → 3-D for every strip panel and its flaps, at end-plane slope kp."""
    xz = state(kp)
    sq = math.sqrt(1.0 + kp * kp)
    out = {}
    for j, side in enumerate(strips):
        (xa, za), (xb, zb) = xz[j], xz[j + 1]
        u0, du = us[j], us[j + 1] - us[j]
        sgn = 1.0 if side == "front" else -1.0          # the end plane is Y + kp·|Z| = y_end

        def f(p, xa=xa, za=za, xb=xb, zb=zb, u0=u0, du=du, end=None, sgn=sgn):
            s = (p[0] - u0) / du
            q = (xa + s * (xb - xa), p[1], za + s * (zb - za))
            if end is None:
                return q
            nrm = (0.0, 1.0 / sq, sgn * kp / sq) if end == "top" else (0.0, 1.0 / sq,
                                                                       -sgn * kp / sq)
            dd = (y1 if end == "top" else y0) / sq
            r = 2.0 * (dot(q, nrm) - dd)
            return (q[0] - r * nrm[0], q[1] - r * nrm[1], q[2] - r * nrm[2])
        out[f"{side}-{j}"] = f
        out[f"{side}-top-{j}"] = (lambda p, f=f: f(p, end="top"))
        out[f"{side}-bottom-{j}"] = (lambda p, f=f: f(p, end="bottom"))
    return out


# ── the dieline: one panel per facet strip, so every hinge is straight ────────────────────────
d = pliego.dieline.Dieline(
    "pillow", "pillow box (curved scores, centre seam)", "folding-carton",
    {"length": length, "width": width, "depth": thickness}, stock, t,
    label=L4("Pillow box blank", "Suaje de la caja almohada", "Flan de la boîte berlingot",
             "Corte da caixa travesseiro"), grain_deg=90.0)
NAMES = {"front": L4("Front", "Frente", "Face avant", "Frente"),
         "back": L4("Back", "Parte trasera", "Face arrière", "Traseira")}
END = {"top": L4("top flap", "solapa superior", "rabat supérieur", "aba superior"),
       "bottom": L4("bottom flap", "solapa inferior", "rabat inférieur", "aba inferior")}


def lab(side, end=None):
    base = NAMES[side]
    return dict(base) if end is None else {g: f"{base[g]}: {END[end][g]}" for g in base}


def ring(pts):
    out = []
    for p in pts:
        if not out or math.hypot(p[0] - out[-1][0], p[1] - out[-1][1]) > 1e-9:
            out.append(p)
    if math.hypot(out[0][0] - out[-1][0], out[0][1] - out[-1][1]) < 1e-9:
        out.pop()
    return out


def at(j, u, which):
    """Score / cut height at flat u inside strip j (straight within the strip)."""
    s = (u - us[j]) / (us[j + 1] - us[j])
    return ys(zc[j])[which] + s * (ys(zc[j + 1])[which] - ys(zc[j])[which])


last = len(strips) - 1
for j, side in enumerate(strips):
    ua, ub = us[j], us[j + 1]
    (bca, bsa, tsa, tca), (bcb, bsb, tsb, tcb) = ys(zc[j]), ys(zc[j + 1])
    body = [(ua, bsa), (ub, bsb), (ub, tsb), (ua, tsa)]
    if j == last:                                  # the lap of the seam, over the first half
        body = [(ua, bsa), (ub, bsb), (ub, bsb + 1.0), (ub + G, bsb + 1.0 + G),
                (ub + G, tsb - 1.0 - G), (ub, tsb - 1.0), (ub, tsb), (ua, tsa)]
    d.panel(f"{side}-{j}", body, "panel", lab(side))
    fa, fb = (c if j == 0 else ua), (U - c if j == last else ub)
    d.panel(f"{side}-top-{j}", ring([(fa, at(j, fa, 2)), (fb, at(j, fb, 2)), (fb, at(j, fb, 3)),
                                     (fa, at(j, fa, 3))]), "flap", lab(side, "top"),
            print_area=False)
    d.panel(f"{side}-bottom-{j}", ring([(fa, at(j, fa, 0)), (fb, at(j, fb, 0)),
                                        (fb, at(j, fb, 1)), (fa, at(j, fa, 1))]), "flap",
            lab(side, "bottom"), print_area=False)
d.glue_zone("seam-lap", [(U + 1.0, ys(Z[m])[1] + 2.0 + G), (U + G - 1.0, ys(Z[m])[1] + 2.0 + G),
                         (U + G - 1.0, ys(Z[m])[2] - 2.0 - G), (U + 1.0, ys(Z[m])[2] - 2.0 - G)],
            on=f"back-{last}")


def newell(poly3):
    nx = ny = nz = 0.0
    for i, p in enumerate(poly3):
        q = poly3[(i + 1) % len(poly3)]
        nx += (p[1] - q[1]) * (p[2] + q[2])
        ny += (p[2] - q[2]) * (p[0] + q[0])
        nz += (p[0] - q[0]) * (p[1] + q[1])
    return unit((nx, ny, nz))


def shared(pa, pb):
    """The edge p→q of panel pa that panel pb also borders (pa on its left: CCW rings)."""
    ra, rb = d.panels[pa].polygon, d.panels[pb].polygon
    for i, p in enumerate(ra):
        q = ra[(i + 1) % len(ra)]
        dx, dy = q[0] - p[0], q[1] - p[1]
        ln = math.hypot(dx, dy)
        for jj, r in enumerate(rb):
            s = rb[(jj + 1) % len(rb)]
            off = max(abs((r[0] - p[0]) * dy - (r[1] - p[1]) * dx),
                      abs((s[0] - p[0]) * dy - (s[1] - p[1]) * dx)) / ln
            if off < 1e-6 and ((s[0] - r[0]) * dx + (s[1] - r[1]) * dy) < 0:
                return p, q
    raise ValueError(f"panels {pa} and {pb} share no edge")


def dihedral(maps, pa, pb):
    """Signed fold angle (deg, valley > 0) from pa to pb in a 3-D state."""
    p, q = shared(pa, pb)
    na = newell([maps[pa](v) for v in d.panels[pa].polygon])
    nb = newell([maps[pb](v) for v in d.panels[pb].polygon])
    e = unit(tuple(x - y for x, y in zip(maps[pa](q), maps[pa](p))))
    cr = (na[1] * nb[2] - na[2] * nb[1], na[2] * nb[0] - na[0] * nb[2],
          na[0] * nb[1] - na[1] * nb[0])
    return -math.degrees(math.atan2(dot(cr, e), dot(na, nb)))


hinges = []                                        # (panel a, panel b, name)
for j in range(len(strips)):
    sa = f"{strips[j]}-{j}"
    for end in ("top", "bottom"):
        hinges.append((sa, f"{strips[j]}-{end}-{j}", f"{sa}-{end}-score"))
    if j == 0:
        continue
    pa = f"{strips[j - 1]}-{j - 1}"
    if j in SIDE_FOLDS:
        hinges.append((pa, sa, "side-score-1" if strips[j] == "front" else "side-score-2"))
        continue
    hinges.append((pa, sa, f"ruling-{j}"))
    for end in ("top", "bottom"):
        hinges.append((f"{strips[j - 1]}-{end}-{j - 1}", f"{strips[j]}-{end}-{j}",
                       f"{end}-flap-ruling-{j}"))
closed_maps = maps_for(k)
for pa, pb, name in hinges:
    ang = dihedral(closed_maps, pa, pb)
    d.hinge(pa, pb, ang if abs(ang) > 1e-9 else -1e-6, name=name)
d.dimension((us[m + 1], y1), (us[m + 1] + w, y1),
            f"panel {w:.1f} (closed width {width:g} inside)", 12.0 + s_cut)
d.dimension((U + G, y0), (U + G, y1), f"L {length:g} (inside, tip to tip)", -12.0)
pack = d.build(rest_on="back-0")
sheet = pack.sheet
arr = sheet.build()
rest_pt = pliego.Vec2(*pack.initial["pillow"]["root"])
if pack.initial["pillow"]["angles"]:
    raise ValueError("pillow-box: the seam's first half must be the sheet's first face")


def angles_at(kp):
    if kp is None:                                 # the flattened tube
        return {name: (-180.0 if name.startswith("side-score") else 0.0)
                for _a, _b, name in hinges}
    mp = maps_for(kp)
    return {name: dihedral(mp, pa, pb) for pa, pb, name in hinges}


def residual(values):
    out = {}
    for h, ms in pack.marks.items():
        for mk in ms:
            for e in mk.edges():
                out[e] = values[h]
    return pliego.kinematics.closure_residual(arr, out, rest_pt)


# ── the program ──────────────────────────────────────────────────────────────────────────────
def targets(values, names=None):
    return [(mk, values[h]) for h in (names or values) for mk in pack.marks[h]]


flat_tube = angles_at(None)
steps = [
    pliego.Step("fold-back-half", L4("Fold the back's second half over the front",
                                     "Dobla la segunda mitad de la parte trasera sobre el frente",
                                     "Rabattez la seconde moitié du dos sur la face avant",
                                     "Dobre a segunda metade da traseira sobre a frente"),
                targets(flat_tube, ["side-score-2"]), duration_ms=1300),
    pliego.Step("fold-front-over", L4("Fold the front over and glue the seam's lap",
                                      "Dobla el frente encima y pega el traslape de la unión",
                                      "Rabattez la face avant et collez le recouvrement du joint",
                                      "Dobre a frente por cima e cole a sobreposição da junta"),
                targets(flat_tube, ["side-score-1"]), duration_ms=1300,
                note=L4("The flattened, glued tube: the box can be stored and shipped like this.",
                        "El tubo aplanado y pegado: así puede guardarse y enviarse la caja.",
                        "Le tube aplati et collé : la boîte peut être stockée et expédiée ainsi.",
                        "O tubo achatado e colado: assim a caixa pode ser guardada e enviada."))]
worst = 0.0
for s in range(1, ERECT + 1):
    psi = 90.0 - (90.0 - end_tilt) * s / ERECT
    kp = k if s == ERECT else math.tan(math.radians(psi))
    vals = angles_at(kp)
    worst = max(worst, residual(vals))
    steps.append(pliego.Step(
        f"erect-{s}", L4(f"Squeeze the tube: the panels bulge, the ends fold in ({s}/{ERECT})",
                         f"Aprieta el tubo: los paneles se abomban y los extremos se hunden "
                         f"({s}/{ERECT})",
                         f"Pressez le tube : les panneaux se bombent, les extrémités "
                         f"s'enfoncent ({s}/{ERECT})",
                         f"Aperte o tubo: os painéis abaulam e as extremidades afundam "
                         f"({s}/{ERECT})"),
        targets(vals), duration_ms=500,
        note=(L4("Each pose is an exact rigid-ruling state (reflection construction).",
                 "Cada pose es un estado exacto de generatrices rígidas (construcción por "
                 "reflexión).",
                 "Chaque pose est un état exact à génératrices rigides (construction par "
                 "réflexion).",
                 "Cada pose é um estado exato de geratrizes rígidas (construção por reflexão).")
              if s == 1 else None)))
if worst > 1e-6 * Lp:
    raise ValueError(f"pillow-box: erecting closure residual {worst:.2e} mm")
closed = angles_at(k)
print(f"pillow-box: facets={n} facet={a:.2f} mm phi={math.degrees((lo + hi) / 2):.2f} deg "
      f"score sagitta={k * zmax:.2f} cut sagitta={s_cut:.2f} mm "
      f"centre score {closed[f'front-{2 * m + 1}-top-score']:.1f} deg "
      f"worst closure residual={worst:.1e} mm over {ERECT} poses")

artwork = []
fm = f"front-{2 * m + 1}"                          # the front's middle facet
if branding:
    xs_f = [p[0] for p in d.panels[fm].polygon]
    side_len = 0.42 * min(w, Lp - 2 * k * zmax)
    cx, cy = (min(xs_f) + max(xs_f)) / 2.0, (y0 + y1) / 2.0
    artwork.append(pliego.press.artwork(
        "brand-mark", sheet, "assets/brand-mark.svg", (cx - side_len / 2, cy - side_len / 2),
        (side_len, side_len), side="front", panel=fm, clip="none"))

# one print panel per face (the whole front; the back in two halves), not one per facet
block = pack.block
keep = [p for p in block["panels"] if p["kind"] not in ("panel", "flap")]
groups = [("front", [j for j, s in enumerate(strips) if s == "front"]),
          ("back-1", list(range(0, m + 1))), ("back-2", list(range(len(strips) - m - 1,
                                                                   len(strips))))]
for name, idx in groups:
    lo_j, hi_j = idx[0], idx[-1]
    for end, (score, cut_) in (("top", (2, 3)), ("bottom", (1, 0))):
        u_a = c if lo_j == 0 else us[lo_j]
        u_b = U - c if hi_j == last else us[hi_j + 1]
        line = [u_a] + [us[j] for j in range(lo_j + 1, hi_j + 1)] + [u_b]
        jj = [max(lo_j, min(hi_j, next(j for j in range(len(strips)) if us[j + 1] >= u - 1e-9)))
              for u in line]
        lens = ([(u, at(j, u, score)) for u, j in zip(line, jj)]
                + [(u, at(j, u, cut_)) for u, j in reversed(list(zip(line, jj)))])
        side = "front" if name == "front" else "back"
        lens = ring(lens) if end == "top" else ring(lens)[::-1]      # CCW
        keep.append({"name": f"{name}-{end}-flap", "kind": "flap", "label": lab(side, end),
                     "polygon": [[x, y] for x, y in lens], "print": False})
    poly = ([(us[j], ys(zc[j])[1]) for j in range(lo_j, hi_j + 2)]
            + [(us[j], ys(zc[j])[2]) for j in range(hi_j + 1, lo_j - 1, -1)])
    cut = [0.0] * len(poly)
    if name == "back-1":
        cut[-1] = block["bleed_mm"]                # the seam edge is a cut
    keep.append({"name": name, "kind": "panel",
                 "label": lab("front" if name == "front" else "back"),
                 "polygon": [[x, y] for x, y in poly], "print": True,
                 "safe": [[round(x, 6), round(y, 6)] for x, y in pliego.dieline.mitre_offset(
                     poly, [-block["safe_mm"]] * len(poly))],
                 "bleed": [[round(x, 6), round(y, 6)] for x, y in
                           pliego.dieline.mitre_offset(poly, cut)]})
block["panels"] = keep

assembly = pliego.Assembly(
    [sheet], controls=[pliego.sequence_control(label=L4(
        "Fold program", "Secuencia de armado", "Séquence de montage", "Sequência de montagem"))],
    sequence=pliego.Sequence(steps, mode="kinematic"), initial=pack.initial,
    targets={"closed": {"pillow": {"angles": {mk: closed[h] for h, ms in pack.marks.items()
                                              for mk in ms},
                                   "root": pack.initial["pillow"]["root"]}}},
    dielines=[block], artwork=artwork, title="Pillow box (curved scores)")
params = {"width": width, "length": length, "thickness": thickness, "end_tilt": end_tilt,
          "facets": n, "stock": stock, "branding": branding}
doc = assembly.build(cartridge="pillow-box", mode="pillow", params=params)
# rulings are bending lines of plain board (spec §4: F + `none`), not scores on the die;
# free cut edges keep their face's name (front, back, front-top…), not the facet's
names = doc.data["pliego:edges_name"]
tr, asg, fa_ = (doc.data["pliego:edges_treatment"], doc.data["edges_assignment"],
                doc.data["edges_foldAngle"])
for e, nm in enumerate(names):
    if nm and "ruling-" in nm:
        tr[e], asg[e], fa_[e] = "none", "F", 0.0
    elif nm and asg[e] == "B" and nm.split("-")[-1].isdigit():
        names[e] = "-".join(nm.split("-")[:-1])
result = doc.stamp()
