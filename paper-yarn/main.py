"""Paper yarn, cord and rope — sheet-hyperobjects cartridge (Pliego).

A narrow strip of paper twisted into yarn; two yarns plied into a cord; three into a rope. Paper
thread of this kind (kami-ito) is what Japanese shifu cloth is woven from.

What is modelled (and what is not). A strip twisted about its own long axis is not developable: the
real thread is rolled, crushed and twisted at once. The developable shape closest to it is the strip
**wound as a helical ribbon round a tube**: unroll the tube (a cylinder is developable) and the
strip is a straight band crossing it at the twist angle β, the angle between the paper's length and
the yarn's axis. Segmentation: the tube is a prism of `facets` sides, and its generators (lines
parallel to the axis) are `F` lines on the strip — straight lines at angle β to the strip's length,
a perpendicular distance h = C / facets apart, C being the tube's perimeter. They are plain paper
(treatment `none`): they are not scored and not on the cut file.

Why the twist is kinematic. All the F lines are parallel and none of them cross, and folding every
one by the same angle φ turns the strip about axes that stay parallel: the strip coils into a
polygonal helix whose cross-section is a regular polygon with exterior angle φ. At φ = 360°/facets
the polygon closes and the turns butt edge to edge: the yarn. Every intermediate state is an exact
rigid state, so the program is a `kinematic` one and the studio preview plays it exactly.

Plies. A cord or a rope is modelled as two or three identical strips (one sheet each) wound round
one tube, side by side, so each turn of the tube is made of m bands: m·w = C·cos β. In the flat
start the plies lie next to each other on the table, ply k shifted by k·w/sin β along the tube's
axis direction; a shift along that direction commutes with every fold (the F lines are parallel to
it), so the plies stay interleaved at every step of the program. This shows the ply count and the
ply twist; it does not show each ply's own twist or its round cross-section (real plies are crushed
and bent, which no flat strip can do without stretching) — the article says so.

Twist direction: Z (right-handed helix) or S (left-handed), the ISO 2 letters.
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


SLUG = "paper-yarn"
STOCKS = {"washi-kozo-30": 1.0, "kraft-120": 1.0, "copy-80": 1.0}   # min feature, mm
PLIES = {"yarn": 1, "cord": 2, "rope": 3}
PLY_IDS = ("ply-a", "ply-b", "ply-c")
PLY_LABELS = (L4("Ply A", "Cabo A", "Brin A", "Cabo A"), L4("Ply B", "Cabo B", "Brin B", "Cabo B"),
              L4("Ply C", "Cabo C", "Brin C", "Cabo C"))
COLOURS = ("#efe6d2", "#2f4b7c", "#c8553d", "#3d6b45", "#2b2b2b")   # natural, indigo, persimmon…

mode = str(PARAM(lambda: mode, "yarn"))                                    # noqa: F821
width = pliego.clamp(PARAM(lambda: strip_width, 12.0), 4.0, 40.0)          # noqa: F821
beta_deg = pliego.clamp(PARAM(lambda: twist_angle, 35.0), 20.0, 60.0)     # noqa: F821
length = pliego.clamp(PARAM(lambda: length, 200.0), 60.0, 400.0)           # noqa: F821
facets = int(pliego.clamp(PARAM(lambda: facets, 8), 6, 16))                # noqa: F821
twist = str(PARAM(lambda: twist, "Z"))                                     # noqa: F821
stock = str(PARAM(lambda: stock, "washi-kozo-30"))                         # noqa: F821
colour = str(PARAM(lambda: colour, "#efe6d2"))                             # noqa: F821
if mode not in PLIES:
    raise ValueError(f"paper-yarn: mode must be yarn, cord or rope, got {mode!r}")
if twist not in ("Z", "S"):
    raise ValueError(f"paper-yarn: twist must be Z or S, got {twist!r}")
if stock not in STOCKS:
    raise ValueError(f"paper-yarn: stock must be one of {tuple(STOCKS)}, got {stock!r}")
if not (len(colour) == 7 and colour.startswith("#")):
    raise ValueError(f"paper-yarn: colour must be #rrggbb, got {colour!r}")

m = PLIES[mode]
beta = math.radians(beta_deg)
sb, cb = math.sin(beta), math.cos(beta)
s = -1.0 if twist == "Z" else 1.0           # mirror of the pattern: the twist letter
C = m * width / cb                          # tube perimeter: m bands per turn, butt to butt
# Each end of the strip is cut on the bias, so its acute corner is a facet wide (h) where it meets
# the first line: the facet count is capped so that h is at least the stock's minimum feature.
K = min(facets, max(3, math.floor(C / STOCKS[stock])))
if K < facets:
    print(f"paper-yarn: facets limited to {K} so that every panel is at least "
          f"{STOCKS[stock]} mm wide (the stock's minimum feature)")
h = C / K                                   # facet width (perpendicular distance between F lines)
Rp = h / (2.0 * math.sin(math.pi / K))      # prism circumradius
pitch = C / math.tan(beta)                  # axial advance of one strip per turn
S_len = length / cb                         # strip length: its centreline advances `length`
shift = width / sb                          # axial offset between neighbouring plies
PHI = 360.0 / K                             # every F line's fold angle in the yarn


# ── development: strip (u, v) → unrolled tube (X around, Z along the axis) ──
# X = (u − A)·sin β − s·v·cos β : the F lines are X = j·h, j = 1 … N − 1. The strip's two ends are
# cut on the lines X = 0 and X = N·h (on the bias, parallel to the twist lines), so every panel is
# the same parallelogram and no sliver is left at the ends.
N_PANELS = max(4, round(S_len * sb / h))
A = width * cb / sb if s < 0 else 0.0       # keeps the outline at u ≥ 0
if m * N_PANELS > 700:
    raise ValueError(f"paper-yarn: {m * N_PANELS} panels is too fine a model; use fewer facets, "
                     "a wider strip or a shorter yarn")


def dev(u, v):
    return ((u - A) * sb - s * v * cb, (u - A) * cb + s * v * sb)


def on_line(c, v):
    """u of the point of the line X = c on the strip's long line at height v."""
    return (c + s * v * cb) / sb + A


strip_outline = [(on_line(0.0, 0.0), 0.0), (on_line(N_PANELS * h, 0.0), 0.0),
                 (on_line(N_PANELS * h, width), width), (on_line(0.0, width), width)]


def make_ply(k):
    sheet = pliego.Sheet(
        PLY_IDS[k], strip_outline, stock=stock, grain_deg=0.0, label=PLY_LABELS[k],
        back=COLOURS[(COLOURS.index(colour) + k) % len(COLOURS)]
        if colour in COLOURS else colour,
        placement=pliego.Placement(origin=(k * width * cb / sb, 0.0, -s * k * width))
        if k else None)
    for j in range(1, N_PANELS):
        sheet.crease((on_line(j * h, 0.0), 0.0), (on_line(j * h, width), width), "flat", 0.0,
                     treatment="crease")
    return sheet


plies = [make_ply(k) for k in range(m)]
cut_check = pliego.papercut.analyze(plies[0], min_feature_mm=STOCKS[stock])
if not cut_check.ok:
    raise ValueError(f"paper-yarn: the strip fails the papercut check: {cut_check.issues}")

SPIN = 1.0      # winding sense of the prism; flipped below if the roll is not a valley roll


def tube(sheet_id, uv):
    """The finished yarn: every ply on one K-prism of perimeter C (axis = world z)."""
    k = PLY_IDS.index(sheet_id)
    X, Z = dev(uv[0] + k * width * cb / sb, uv[1] + s * k * width)
    j = math.floor(X / h)
    t = X / h - j
    a0, a1 = SPIN * 2.0 * math.pi * j / K, SPIN * 2.0 * math.pi * (j + 1) / K
    x = Rp * ((1.0 - t) * math.cos(a0) + t * math.cos(a1))
    y = Rp * ((1.0 - t) * math.sin(a0) + t * math.sin(a1))
    return (x, y, Z)


arr = plies[0].build()


def newell(pts):
    n = [0.0, 0.0, 0.0]
    for i, p in enumerate(pts):
        q = pts[(i + 1) % len(pts)]
        n[0] += (p[1] - q[1]) * (p[2] + q[2])
        n[1] += (p[2] - q[2]) * (p[0] + q[0])
        n[2] += (p[0] - q[0]) * (p[1] + q[1])
    r = math.sqrt(n[0] ** 2 + n[1] ** 2 + n[2] ** 2)
    return (n[0] / r, n[1] / r, n[2] / r)


def fold_angles(pose, sheet_id):
    """Signed fold angle (FOLD convention, deg) of every interior F/M/V edge in `pose`."""
    pts = [pose(sheet_id, (v.x, v.y)) for v in arr.vertices]
    left = {}
    for fi, f in enumerate(arr.faces):
        for i in range(len(f)):
            left[(f[i], f[(i + 1) % len(f)])] = fi
    normals = [newell([pts[v] for v in f]) for f in arr.faces]
    out = {}
    for e, (a, b) in enumerate(arr.edges):
        if arr.assignment[e] in ("F", "M", "V") and (a, b) in left and (b, a) in left:
            edge = tuple(pts[b][i] - pts[a][i] for i in range(3))
            out[e] = pliego.tessellate.signed_fold_angle(normals[left[(a, b)]],
                                                         normals[left[(b, a)]], edge)
    return out


angles = fold_angles(tube, PLY_IDS[0])
if max(angles.values()) < 0.0:
    SPIN = -1.0
    angles = fold_angles(tube, PLY_IDS[0])
# vertices sit on the kernel's 1e-6 mm grid, so measured angles carry ~1e-5° of grid noise
for k in range(m):                          # every ply is the same uniform valley roll
    worst = max(abs(a - PHI) for a in fold_angles(tube, PLY_IDS[k]).values())
    if worst > 1e-3:
        raise ValueError(f"paper-yarn: ply {k} is not a uniform valley roll of {PHI}° ({worst})")
angles = {e: PHI for e in angles}           # the program drives the exact angle

# isometry: every edge of every ply keeps its length on the tube
for k in range(m):
    for a, b in arr.edges:
        pa, pb = arr.vertices[a], arr.vertices[b]
        d0 = math.dist((pa.x, pa.y), (pb.x, pb.y))
        d1 = math.dist(tube(PLY_IDS[k], (pa.x, pa.y)), tube(PLY_IDS[k], (pb.x, pb.y)))
        if abs(d1 - d0) > 1e-6 * max(1.0, d0):
            raise ValueError(f"paper-yarn: the tube stretches an edge of ply {k} ({d0} → {d1})")

# handedness: Z = right-handed (the angle about the axis grows with z along a strip edge)
p0, p1 = tube(PLY_IDS[0], (0.25 * S_len, 0.0)), tube(PLY_IDS[0], (0.25 * S_len + h / sb, 0.0))
turn = math.atan2(p0[0] * p1[1] - p0[1] * p1[0], p0[0] * p1[0] + p0[1] * p1[1])
right_handed = turn * (p1[2] - p0[2]) > 0.0
if right_handed != (twist == "Z"):
    raise ValueError("paper-yarn: the helix has the wrong handedness for its twist letter")

# the turns close up: one perimeter C around the tube, the plies' outer edge meets ply A's
# inner edge at the same height (the bands butt; the K-prism is closed, so there is no seam gap)
v_far = width if s > 0 else 0.0
gap = 0.0
for i in range(1, 8):
    u = on_line(N_PANELS * h * i / 8.0, v_far)
    X, Z = dev(u + (m - 1) * width * cb / sb, v_far + s * (m - 1) * width)
    u2 = (Z - s * (width - v_far) * sb) / cb + A
    X2 = dev(u2, width - v_far)[0]
    gap = max(gap, abs(abs(X - X2) - C))
if gap > 1e-6:
    raise ValueError(f"paper-yarn: the bands do not butt ({gap} mm)")

render_vertices = m * sum(len(f) for f in arr.faces)
params = {"strip_width": width, "twist_angle": beta_deg, "length": length, "facets": facets,
          "twist": twist, "stock": stock, "colour": colour}
info = {"plies": m, "facets_used": K, "yarn_diameter_mm": round(2.0 * Rp, 3),
        "perimeter_mm": round(C, 3),
        "pitch_mm": round(pitch, 3), "turns": round(length / pitch, 3),
        "twist_per_metre": round(1000.0 / pitch, 1),
        "strip_mm": [round(N_PANELS * h / sb, 1), width],
        "panels_per_ply": len(arr.faces), "fold_deg": round(PHI, 6),
        "render_vertices": render_vertices, "min_bridge_mm": cut_check.min_bridge_mm}
print(f"paper-yarn: {info}")

NAMES = {
    "yarn": L4("Twist the strip into yarn", "Torcer la tira hasta hacer hilo",
               "Tordre la bande en fil", "Torcer a tira até virar fio"),
    "cord": L4("Twist two plies into a cord", "Torcer dos cabos en un cordón",
               "Tordre deux brins en cordelette", "Torcer dois cabos num cordão"),
    "rope": L4("Twist three plies into a rope", "Torcer tres cabos en una cuerda",
               "Tordre trois brins en corde", "Torcer três cabos numa corda"),
}
WHAT = {
    "yarn": L4("the strip", "la tira", "la bande", "a tira"),
    "cord": L4("the two plies", "los dos cabos", "les deux brins", "os dois cabos"),
    "rope": L4("the three plies", "los tres cabos", "les trois brins", "os três cabos"),
}[mode]


def targets(frac):
    return [(pliego.assembly.EdgeRef(p, e), frac * a) for p in plies for e, a in angles.items()]


steps = [
    pliego.Step("start-twist", L4(f"Start twisting {WHAT['en']}: it curls into a loose helix",
                                  f"Empieza a torcer {WHAT['es']}: se enrosca en una hélice "
                                  "abierta", f"Commencez à tordre {WHAT['fr']} : elle s'enroule "
                                  "en une hélice lâche" if m == 1 else f"Commencez à tordre "
                                  f"{WHAT['fr']} : ils s'enroulent en une hélice lâche",
                                  f"Comece a torcer {WHAT['pt']}: enrola-se numa hélice aberta"
                                  if m == 1 else f"Comece a torcer {WHAT['pt']}: enrolam-se numa "
                                  "hélice aberta"),
                targets(1.0 / 3.0), duration_ms=2500),
    pliego.Step("tighten", L4("Keep twisting: the helix tightens and narrows",
                              "Sigue torciendo: la hélice se aprieta y se angosta",
                              "Continuez à tordre : l'hélice se resserre et s'affine",
                              "Continue torcendo: a hélice aperta e afina"),
                targets(2.0 / 3.0), duration_ms=2500),
    pliego.Step("close-up", L4("Twist until the turns close up edge to edge",
                               "Tuerce hasta que las vueltas se junten borde con borde",
                               "Tordez jusqu'à ce que les spires se touchent bord à bord",
                               "Torça até as voltas se encostarem borda com borda"),
                targets(1.0), duration_ms=2500,
                note=L4("Real paper yarn is rolled tight and crushed; here the strip stays a "
                        "hollow, butt-wound tube.",
                        "El hilo de papel real queda enrollado apretado y aplastado; aquí la tira "
                        "queda como un tubo hueco, con las vueltas a tope.",
                        "Le vrai fil de papier est roulé serré et écrasé ; ici la bande reste un "
                        "tube creux aux spires jointives.",
                        "O fio de papel real fica enrolado apertado e amassado; aqui a tira fica "
                        "um tubo oco, com as voltas encostadas.")),
]

assembly = pliego.Assembly(
    plies, controls=[pliego.sequence_control(label=NAMES[mode])],
    sequence=pliego.Sequence(steps, mode="kinematic"),
    targets={mode: {"angles": dict(angles)}}, title="Paper yarn")
doc = assembly.build(cartridge=SLUG, mode=mode, params=params)
# The generators are plain paper (spec §4: F + `none`); the Sheet API authors F lines with a
# treatment, so they are marked untreated here: exporters must not score a curved surface.
tr = doc.data["pliego:edges_treatment"]
for e, a in enumerate(doc.data["edges_assignment"]):
    if a == "F" and tr[e] == "crease":
        tr[e] = "none"
result = doc.stamp()
