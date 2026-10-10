"""Platonic solids — sheet-hyperobjects cartridge (Pliego).

The five regular convex polyhedra (tetrahedron, cube, octahedron, dodecahedron, icosahedron) as
tabbed card nets, chosen by `solid`, or all five as one set. Each solid is built here from its
vertex coordinates (the convex hull, `pliego.mesh.hull`, with coplanar triangles merged into
the regular faces), sized by its edge length or by the radius of the sphere through its
vertices (Euclid's construction in Book XIII inscribes all five in one sphere), and stood on a
face. The kernel unfolder (`pliego.unfold.net`) cuts it open into a net, adds the glue tabs and
the edge numbers, and lays it out on A4 or Letter pages. No net is copied from a book or a
template: every net is generated.

The fold program raises the net ring by ring: ring 1 is every face hinged to the piece's first
face (the base), ring 2 every face hinged to ring 1, and so on, until the solid closes. Every
piece is a tree of hinges, so every state in between is rigid and exact. Mode `glued` is the
finished solid held by its glue tabs, for the paper physics engine.

Vertex coordinates (circumradius before scaling, φ the golden ratio):
- tetrahedron: alternate corners of a cube, (±1, ±1, ±1) with an even number of minus signs;
- cube: (±1, ±1, ±1);
- octahedron: (±1, 0, 0), (0, ±1, 0), (0, 0, ±1);
- dodecahedron: (±1, ±1, ±1), (0, ±1/φ, ±φ), (±1/φ, ±φ, 0), (±φ, 0, ±1/φ);
- icosahedron: (0, ±1, ±φ), (±1, ±φ, 0), (±φ, 0, ±1).
"""

import math

import pliego


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


solid = str(PARAM(lambda: solid, "dodecahedron"))                  # noqa: F821
measure = str(PARAM(lambda: measure, "circumradius"))               # noqa: F821
size = float(PARAM(lambda: size, 40.0))                             # noqa: F821
page = str(PARAM(lambda: page, "a4"))                               # noqa: F821
method = str(PARAM(lambda: method, "min-perimeter"))                # noqa: F821
tab_style = str(PARAM(lambda: tab_style, "trapezoid"))              # noqa: F821
tab_angle = float(PARAM(lambda: tab_angle, 45.0))                   # noqa: F821
tab_height = float(PARAM(lambda: tab_height, 6.0))                  # noqa: F821
stock = str(PARAM(lambda: stock, "cardstock-250"))                  # noqa: F821
mode = str(PARAM(lambda: mode, "fold"))                             # noqa: F821

M = pliego.mesh
PHI = (1.0 + math.sqrt(5.0)) / 2.0
STOCKS = ("cardstock-160", "cardstock-250", "cardstock-300")
SOLIDS = ("tetrahedron", "cube", "octahedron", "dodecahedron", "icosahedron")
if solid not in SOLIDS + ("set",):
    raise ValueError(f"platonic-solids: solid must be one of {SOLIDS + ('set',)}, got {solid!r}")
if measure not in ("circumradius", "edge"):
    raise ValueError(f"platonic-solids: measure must be circumradius or edge, got {measure!r}")
if stock not in STOCKS:
    raise ValueError(f"platonic-solids: stock must be one of {STOCKS}, got {stock!r}")
if mode not in ("fold", "glued"):
    raise ValueError(f"platonic-solids: mode must be fold or glued, got {mode!r}")
size = pliego.clamp(size, 15.0, 120.0)


def cube_corners(even_only=False):
    out = []
    for x in (-1.0, 1.0):
        for y in (-1.0, 1.0):
            for z in (-1.0, 1.0):
                if not even_only or x * y * z > 0:
                    out.append((x, y, z))
    return out


def cyclic(a, b):
    """(0, ±a, ±b) and its two cyclic permutations."""
    out = []
    for s in (-1.0, 1.0):
        for t in (-1.0, 1.0):
            out += [(0.0, s * a, t * b), (s * a, t * b, 0.0), (t * b, 0.0, s * a)]
    return out


def vertices(name):
    if name == "tetrahedron":
        return cube_corners(even_only=True)
    if name == "cube":
        return cube_corners()
    if name == "octahedron":
        return [(1.0, 0.0, 0.0), (-1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, -1.0, 0.0),
                (0.0, 0.0, 1.0), (0.0, 0.0, -1.0)]
    if name == "dodecahedron":
        return cube_corners() + cyclic(1.0 / PHI, PHI)
    return cyclic(1.0, PHI)


def stood_on_a_face(m):
    """Rotated so face 0 points straight down (the solid stands on it)."""
    n = m.normal(0)
    axis = (n[2], 0.0, -n[0])                       # n × (0, −1, 0)
    s = math.hypot(axis[0], axis[2])
    if s < 1e-12:
        return m if n[1] < 0 else m.rotated((1.0, 0.0, 0.0), 180.0)
    return m.rotated(axis, math.degrees(math.atan2(s, -n[1])))


def regular(name):
    """The solid at the requested size: circumradius or edge length `size` mm."""
    m = stood_on_a_face(M.hull(vertices(name)))
    radius = max(math.sqrt(sum(c * c for c in v)) for v in m.vertices)
    f = m.faces[0]
    edge = math.dist(m.vertices[f[0]], m.vertices[f[1]])
    k = size / (radius if measure == "circumradius" else edge)
    lo, _hi = m.scaled(k).bounds()
    return m.scaled(k).moved(0.0, -lo[1], 0.0), edge * k, radius * k


# Plato, Timaeus 53c–56c: fire, earth, air and water, the fifth for the whole (colours are ours).
ELEMENT = {"tetrahedron": "#d1495b", "cube": "#6a994e", "octahedron": "#edae49",
           "icosahedron": "#00798c", "dodecahedron": "#5e548e"}
NAMES = {"tetrahedron": "tetrahedron", "cube": "cube", "octahedron": "octahedron",
         "dodecahedron": "dodecahedron", "icosahedron": "icosahedron", "set": "five solids"}

if solid == "set":
    parts, x = [], 0.0
    for name in SOLIDS:
        m, a, r = regular(name)
        lo, hi = m.bounds()
        parts.append(m.moved(x - lo[0], 0.0, -(lo[2] + hi[2]) / 2.0))
        x += hi[0] - lo[0] + 0.25 * size
    model = M.merged(*parts)
    colour = "#f4efe6"
    print(f"platonic-solids: set of five, {measure} {size:.1f} mm")
else:
    model, a, r = regular(solid)
    colour = ELEMENT[solid]
    print(f"platonic-solids: {solid}, edge {a:.2f} mm, circumradius {r:.2f} mm")

lo, hi = model.bounds()
extent = max(hi[i] - lo[i] for i in range(3))
net = pliego.unfold.net(model, size=extent, page=page, method=method, tabs=tab_style,
                        tab_height=tab_height, tab_angle=tab_angle)
result = net.assembly(mode, stock=stock, front=colour,
                      title=f"Platonic solids: {NAMES[solid]}")


# ── the fold program, ring by ring (fold mode) ──────────────────────────────

def ring_label(piece, k, pieces):
    if pieces == 1:
        return {"en": f"Fold up ring {k}", "es": f"Levanta el anillo {k}",
                "fr": f"Relevez la couronne {k}", "pt": f"Levante o anel {k}"}
    return {"en": f"Piece {piece}: fold up ring {k}", "es": f"Pieza {piece}: levanta el anillo {k}",
            "fr": f"Pièce {piece} : relevez la couronne {k}",
            "pt": f"Peça {piece}: levante o anel {k}"}


RING_NOTE = {
    "en": "A ring is every face hinged to the ring before it; ring 1 is hinged to the base.",
    "es": "Un anillo son las caras unidas por bisagra al anillo anterior; el anillo 1 está "
          "unido a la base.",
    "fr": "Une couronne réunit les faces articulées sur la couronne précédente ; la couronne 1 "
          "est articulée sur la base.",
    "pt": "Um anel são as faces articuladas no anel anterior; o anel 1 é articulado na base.",
}


def glue_note(numbers):
    s = ", ".join(str(k) for k in numbers)
    return {"en": f"Close the solid: glue each tab under the edge with the same number ({s}).",
            "es": f"Cierra el sólido: pega cada pestaña bajo la arista con el mismo número ({s}).",
            "fr": f"Fermez le solide : collez chaque languette sous l'arête de même numéro ({s}).",
            "pt": f"Feche o sólido: cole cada aba sob a aresta com o mesmo número ({s})."}


if mode == "fold":
    pieces = len(net.islands)
    old = result.sequence.steps
    steps = [s for s in old if s.id == "fold-tabs"]
    for isl, sheet in zip(net.islands, result.sheets, strict=True):
        depth = {isl.root: 0}
        rings = {}
        for k, (f, g, _a, _b) in enumerate(isl.tree):
            depth[g] = depth[f] + 1
            rings.setdefault(depth[g], []).append(sheet.marks[k])
        cuts = sorted({c.number for c in net.cuts if any(s[0] == isl.index for s in c.sides)})
        n = isl.index + 1
        for k in sorted(rings):
            last = k == max(rings)
            note = glue_note(cuts) if last and cuts else (RING_NOTE if k == 1 else None)
            steps.append(pliego.Step(f"piece-{n}-ring-{k}", ring_label(n, k, pieces),
                                     [(m, None) for m in rings[k]], duration_ms=1600,
                                     note=note))
    result.sequence = pliego.Sequence(steps, mode="kinematic")

# ── papercut check: every piece in one piece, no bridge thinner than the card allows ─────
MIN_FEATURE = {"cardstock-160": 1.5, "cardstock-250": 2.0, "cardstock-300": 2.0}
bridges = []
for sheet in result.sheets:
    rep = pliego.papercut.analyze(sheet, min_feature_mm=MIN_FEATURE[stock])
    if rep.components != 1:
        raise ValueError(f"platonic-solids: {sheet.id} falls apart into {rep.components} parts")
    thin = [i for i in rep.issues if i["kind"] == "bridge_too_thin"]
    if thin:
        raise ValueError(f"platonic-solids: {sheet.id}: {thin[0]['detail']}")
    if rep.min_bridge_mm is not None:
        bridges.append(rep.min_bridge_mm)
print(net.summary())
print(f"papercut: pieces={len(result.sheets)} min_bridge="
      f"{min(bridges) if bridges else 'none'} min_feature={MIN_FEATURE[stock]}")
