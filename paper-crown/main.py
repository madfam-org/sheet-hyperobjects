"""Paper crown — sheet-hyperobjects cartridge (Pliego).

A band of card with a decorated top edge (zigzag points, castellated battlements or scallops), cut
out, rolled into a ring and glued with an overlap. One generator: the edge style is a select
parameter; the head size, band and point heights and the number of points are parameters.

Segmentation. The ring is a curved band, modelled as a prism of narrow panels: vertical `F` lines
(treatment `none`: plain paper, never scored) from the bottom edge up to the decorated top edge.
There are `sub` panels per point, aligned so that a line passes through every valley, peak and
battlement step; the closed form is an exact isometry of the sheet: a regular N-gon prism whose
side is one panel wide (circumradius w / (2 sin(π/N))), standing upright. The overlap at the end
is a plain band (no points), chamfered, segmented like the rest; in the closed crown it lies
exactly on the first panels, inside, where a `glue` join welds it (map = translation by −C).

Modes.
- `make`: kinematic program on the panel lines (curl, close, tuck the overlap); the studio preview
  plays it and it ends in the ring (`target:crown`).
- `glued`: the finished crown for the physics engine: glue weld, `initial` frame standing on the
  table, and a physical program that presses it flat (two layers, folds at the seam and opposite)
  and opens it again; the weld holds in both states (`target:flat`).
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


SLUG = "paper-crown"
STOCKS = {"cardstock-160": 1.5, "cardstock-250": 2.0, "foil-paper": 1.5, "kraft-120": 1.0}
EDGES = ("zigzag", "castellated", "scalloped")
OVERLAP_MM = 25.0
CHAMFER = 5.0

mode = str(PARAM(lambda: mode, "make"))                                     # noqa: F821
edge = str(PARAM(lambda: edge, "zigzag"))                                   # noqa: F821
head = pliego.clamp(PARAM(lambda: head, 560.0), 400.0, 640.0)              # noqa: F821
band = pliego.clamp(PARAM(lambda: band, 40.0), 20.0, 80.0)                 # noqa: F821
point = pliego.clamp(PARAM(lambda: point, 50.0), 15.0, 120.0)              # noqa: F821
points = int(pliego.clamp(PARAM(lambda: points, 8), 5, 16))                # noqa: F821
sub = int(pliego.clamp(PARAM(lambda: sub, 6), 4, 12))                      # noqa: F821
stock = str(PARAM(lambda: stock, "cardstock-250"))                         # noqa: F821
colour = str(PARAM(lambda: colour, "#e8b923"))                             # noqa: F821
if mode not in ("make", "glued"):
    raise ValueError(f"paper-crown: mode must be make or glued, got {mode!r}")
if edge not in EDGES:
    raise ValueError(f"paper-crown: edge must be one of {EDGES}, got {edge!r}")
if stock not in STOCKS:
    raise ValueError(f"paper-crown: stock must be one of {tuple(STOCKS)}, got {stock!r}")
sub += sub % 2                 # even: a line through every peak, valley and step

C = head                       # the ring's circumference (the band's inner length)
N = points * sub               # panels around the ring
w = C / N                      # panel width
tw = C / points                # one point (tooth) width
m = max(1, math.ceil(OVERLAP_MM / w))
ov = m * w
if CHAMFER >= band / 2.0 or CHAMFER >= ov / 2.0:
    raise ValueError("paper-crown: the overlap is too small for its chamfer")


def top(t):
    """Height of the decorated top edge at fraction t ∈ [0, 1) of one point (tooth)."""
    if edge == "zigzag":
        return band + point * (1.0 - abs(2.0 * t - 1.0))
    if edge == "scalloped":
        return band + point * math.sin(math.pi * t)
    return band + point if t < 0.5 else band                 # castellated


# ── outline: bottom edge left→right, the overlap end, then the top edge right→left ──
outline = [(0.0, 0.0), (C + ov - CHAMFER, 0.0), (C + ov, CHAMFER), (C + ov, band - CHAMFER),
           (C + ov - CHAMFER, band), (C, band)]
res = 4 * sub if edge == "scalloped" else sub     # every panel line ends on an outline vertex
forward = []
for k in range(points):
    for j in range(res):
        x = (k + j / res) * tw
        if edge == "castellated" and j == 0:
            forward += [(x, band), (x, band + point)]          # step up into the battlement
        elif edge == "castellated" and 2 * j == res:
            forward += [(x, band + point), (x, band)]          # step down into the gap
        else:
            forward.append((x, top(j / res)))
outline += list(reversed(forward))
crown = pliego.Sheet("crown", outline, stock=stock, grain_deg=0.0,
                     label=L4("Crown band", "Banda de la corona", "Bandeau de la couronne",
                              "Faixa da coroa"),
                     front="#f6f1e7", back=colour)

for k in range(1, N + m):
    j = k % sub
    if k >= N or (edge == "castellated" and 2 * j in (0, sub)):
        h = band
    else:
        h = top(j / sub)
    crown.crease((k * w, 0.0), (k * w, h), "flat", 0.0, treatment="crease",
                 name="overlap" if k == N else None)

cut_check = pliego.papercut.analyze(crown, min_feature_mm=STOCKS[stock])
if not cut_check.ok:
    raise ValueError(f"paper-crown: the band fails the papercut check: {cut_check.issues}")

# ── the closed crown: an upright regular N-gon prism ──
R = w / (2.0 * math.sin(math.pi / N))


def corner(k):
    a = 2.0 * math.pi * k / N
    return (R * math.cos(a), R * math.sin(a))


def ring(sheet_id, uv):
    u, v = uv
    k = min(max(int(u / w + 1e-9), 0), N + m - 1)
    s = (u - k * w) / w
    (x0, z0), (x1, z1) = corner(k % N), corner((k + 1) % N)
    return (x0 + s * (x1 - x0), v, z0 + s * (z1 - z0))


arr = crown.build()


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
    pts = [pose("crown", (v.x, v.y)) for v in arr.vertices]
    left = {}
    for fi, f in enumerate(arr.faces):
        for k in range(len(f)):
            left[(f[k], f[(k + 1) % len(f)])] = fi
    normals = [newell([pts[v] for v in f]) for f in arr.faces]
    out = {}
    for e, (a, b) in enumerate(arr.edges):
        if arr.assignment[e] in ("F", "M", "V") and (a, b) in left and (b, a) in left:
            d = tuple(pts[b][i] - pts[a][i] for i in range(3))
            out[e] = pliego.tessellate.signed_fold_angle(normals[left[(a, b)]],
                                                         normals[left[(b, a)]], d)
    return out


angles = fold_angles(ring)
if min(angles.values()) <= 0.0:
    raise ValueError("paper-crown: the ring pose is not a valley roll (orientation error)")
verts = arr.vertices


def edge_x(e):
    a, b = arr.edges[e]
    return (verts[a].x + verts[b].x) / 2.0


band_e = [e for e in angles if edge_x(e) < C - w / 2.0]
lap_e = [e for e in angles if e not in band_e]
seam_e = [e for e in lap_e if abs(edge_x(e) - C) < w / 2.0]
opposite_e = [e for e in band_e if abs(edge_x(e) - C / 2.0) < w / 2.0]

# ── glue: the overlap, inset, onto the first m panels ──
inset = 1.5
region = [(C + inset, inset), (C + ov - CHAMFER, inset), (C + ov - inset, CHAMFER),
          (C + ov - inset, band - CHAMFER), (C + ov - CHAMFER, band - inset),
          (C + inset, band - inset)]
glue_map = (1.0, 0.0, 0.0, 1.0, -C, 0.0)
for p in region:
    if not crown.region_contains(p):
        raise ValueError(f"paper-crown: glue point {p} is off the overlap")
    gap = math.dist(ring("crown", p), ring("crown", (p[0] - C, p[1])))
    if gap > 1e-6:
        raise ValueError(f"paper-crown: weld point {p} misses its glue zone by {gap} mm")

params = {"edge": edge, "head": head, "band": band, "point": point, "points": points,
          "sub": sub, "stock": stock, "colour": colour}
print(f"paper-crown: edge={edge} panels={N} panel_width={w:.2f}mm ring_radius={R:.2f}mm "
      f"overlap_panels={m} strip={C + ov:.0f}x{band + point:.0f}mm "
      f"min_bridge_mm={cut_check.min_bridge_mm}")


def ref(e):
    return pliego.assembly.EdgeRef(crown, e)


if mode == "make":
    steps = [
        pliego.Step("curl", L4("Curl the band into a loose ring, coloured side out",
                               "Curva la banda en un aro holgado, con el lado de color hacia "
                               "fuera", "Courbez le bandeau en un anneau lâche, face colorée à "
                               "l'extérieur", "Curve a faixa num aro folgado, com o lado colorido "
                               "para fora"),
                    [(ref(e), 0.5 * angles[e]) for e in band_e], duration_ms=2500),
        pliego.Step("close", L4("Close the ring until the ends meet", "Cierra el aro hasta que "
                                "se toquen los extremos", "Fermez l'anneau jusqu'à ce que les "
                                "extrémités se rejoignent", "Feche o aro até as pontas se "
                                "encontrarem"),
                    [(ref(e), angles[e]) for e in band_e], duration_ms=2500),
        pliego.Step("glue-overlap", L4("Slide the plain overlap inside and glue it",
                                       "Mete la parte lisa por dentro y pégala",
                                       "Glissez le recouvrement uni à l'intérieur et collez-le",
                                       "Passe a sobreposição lisa por dentro e cole-a"),
                    [(ref(e), angles[e]) for e in lap_e], duration_ms=2000),
    ]
    assembly = pliego.Assembly(
        [crown], controls=[pliego.sequence_control(label=L4("Roll the crown", "Enrollar la "
                                                            "corona", "Rouler la couronne",
                                                            "Enrolar a coroa"))],
        sequence=pliego.Sequence(steps, mode="kinematic"),
        targets={"crown": {"angles": dict(angles)}}, title="Paper crown")
else:
    flat = {e: 0.0 for e in angles}
    for e in seam_e + opposite_e:
        flat[e] = 180.0
    steps = [
        pliego.Step("press-flat", L4("Press the crown flat to store it", "Aplana la corona para "
                                     "guardarla", "Aplatissez la couronne pour la ranger",
                                     "Achate a coroa para guardá-la"),
                    [(ref(e), a) for e, a in flat.items()], duration_ms=2500),
        pliego.Step("open", L4("Open it into a ring again", "Ábrela de nuevo en aro",
                               "Rouvrez-la en anneau", "Abra-a de novo em aro"),
                    [(ref(e), a) for e, a in angles.items()], duration_ms=2500),
    ]
    assembly = pliego.Assembly(
        [crown], joins=[pliego.glue("overlap-to-band", crown, region, crown, glue_map, "front")],
        initial=ring,
        controls=[pliego.sequence_control(label=L4("Flatten and open", "Aplanar y abrir",
                                                   "Aplatir et ouvrir", "Achatar e abrir"))],
        sequence=pliego.Sequence(steps, mode="physical"),
        targets={"crown": ring, "flat": {"angles": flat}}, title="Paper crown")

doc = assembly.build(cartridge=SLUG, mode=mode, params=params)
# The panel lines are plain paper (spec §4: F + `none`); the Sheet API authors F lines with a
# treatment, so they are marked untreated here: exporters must not score a curved band.
tr = doc.data["pliego:edges_treatment"]
for e, a in enumerate(doc.data["edges_assignment"]):
    if a == "F" and tr[e] == "crease":
        tr[e] = "none"
result = doc.stamp()
