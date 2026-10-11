"""Japanese stab binding — sheet-hyperobjects cartridge (Pliego).

A stab-bound book (fukuro-toji, pouch binding): a stack of text leaves between two covers, holes
stabbed through the whole stack beside the spine, and a thread sewn through the holes, round the
spine and round the head and tail. Two modes: `fukuro` (each text leaf is a sheet folded in half,
the fold at the fore-edge and the open edges at the spine, both halves holed) and `single` (single
leaves). Four stitch patterns: four-hole (yotsume toji), tortoise-shell (kikkō toji), hemp leaf
(asa-no-ha toji) and noble (kōki toji, the Kangxi binding).

Every hole position is generated from the book height and the spine margin by the rules written
in `layout()` below (MADFAM's own rules, see the article): no diagram is copied. Each pattern's
stitches form a thread graph (front and back of the book, through-passes and outside stitches);
the script builds one closed sewing route over it and writes it into the step notes.

Fabrication honesty: every sheet carries the same holes (`sheet.hole`, checked with
`pliego.papercut.analyze`); the only score is the front cover's hinge, the crease bookbinders put
beside the thread line so the cover opens there. The thread is recorded as `string` joins (outside
stitches, wraps and through-passes) and in the step notes; nothing is drawn on the fabrication
layers for it. The preview opens the cover with a sequence on the hinge score (string joins never
disable a sequence control); holding the stack together with thread needs the physics engine.
"""

import math

import pliego


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


mode = PARAM(lambda: mode, "fukuro")                            # noqa: F821
pattern = PARAM(lambda: pattern, "four-hole")                   # noqa: F821
page_width = float(PARAM(lambda: page_width, 150.0))            # noqa: F821
book_height = float(PARAM(lambda: book_height, 220.0))          # noqa: F821
spine_margin = float(PARAM(lambda: spine_margin, 10.0))         # noqa: F821
hole_diameter = float(PARAM(lambda: hole_diameter, 2.0))        # noqa: F821
hinge_gap = float(PARAM(lambda: hinge_gap, 1.0))                # noqa: F821
leaves = PARAM(lambda: leaves, 6)                               # noqa: F821
text_stock = PARAM(lambda: text_stock, "washi-kozo-30")         # noqa: F821
cover_stock = PARAM(lambda: cover_stock, "kraft-120")           # noqa: F821

# (thickness mm, minimum feature mm), mirroring materials/<slug>/stock.json
STOCK = {"washi-kozo-30": (0.08, 1.0), "copy-80": (0.10, 1.0),
         "kraft-120": (0.16, 1.0), "cardstock-160": (0.20, 1.5), "elephant-hide-110": (0.12, 1.0)}
TEXT_STOCKS = ("washi-kozo-30", "copy-80")
COVER_STOCKS = ("kraft-120", "cardstock-160", "elephant-hide-110")
PATTERNS = ("four-hole", "tortoise-shell", "hemp-leaf", "noble")
if mode not in ("fukuro", "single"):
    raise ValueError(f"stab-binding: mode must be fukuro or single, got {mode!r}")
if pattern not in PATTERNS:
    raise ValueError(f"stab-binding: pattern must be one of {PATTERNS}, got {pattern!r}")
if text_stock not in TEXT_STOCKS:
    raise ValueError(f"stab-binding: text_stock must be one of {TEXT_STOCKS}")
if cover_stock not in COVER_STOCKS:
    raise ValueError(f"stab-binding: cover_stock must be one of {COVER_STOCKS}")

FOLDED = mode == "fukuro"
W = pliego.clamp(page_width, 80.0, 300.0)       # spine → fore-edge
H = pliego.clamp(book_height, 100.0, 400.0)     # head → tail
d = pliego.clamp(spine_margin, 8.0, 25.0)       # main sewing row, from the spine edge
r = pliego.clamp(hole_diameter, 1.5, 4.0) / 2.0
N = int(pliego.clamp(int(leaves), 1, 24))
t_text, min_text = STOCK[text_stock]
t_cover, min_cover = STOCK[cover_stock]
MIN = max(min_text, min_cover)
gap = max(pliego.clamp(hinge_gap, 0.5, 5.0), min_cover)   # hole rim → hinge score
if 2 * r < MIN:
    raise ValueError(f"stab-binding: a {2 * r:g} mm hole is under the stock's minimum feature")
OPEN = 178.0                    # the opened cover rests a little short of flat
SHOWN = 179.5                   # the preview draws shut folds at most this far
NSEG = 16                       # polygon sides of a hole
RIM = r / math.cos(math.pi / NSEG) + 0.05   # thread anchors sit just outside the hole


def L4(en, es, fr, pt):
    return {"en": en, "es": es, "fr": fr, "pt": pt}


# ── hole layout (generated rules, see the article) ───────────────────────────
# y is measured from the head. Four main stations on the row x = d: the outer two e = H/8 in
# from head and tail, the inner two dividing the span between them in thirds.


def layout(kind):
    e = H / 8.0
    g = (H - 2 * e) / 3.0
    ys = [e, e + g, e + 2 * g, H - e]
    holes = {f"m{i + 1}": (d, ys[i]) for i in range(4)}
    rows = [("m1", "m2"), ("m2", "m3"), ("m3", "m4")]
    heads, tails = ["m1"], ["m4"]
    if kind in ("noble", "hemp-leaf"):
        # corner holes halfway along the diagonal from the outer station to the corner
        holes["c1"] = (d / 2.0, e / 2.0)
        holes["c4"] = (d / 2.0, H - e / 2.0)
        rows += [("c1", "m1"), ("c4", "m4")]
        heads.append("c1")
        tails.append("c4")
    if kind == "hemp-leaf":
        # a second row at 2d, one hole midway between neighbouring stations: a Y of stitches
        for i in range(3):
            k = f"h{i + 1}"
            holes[k] = (2 * d, (ys[i] + ys[i + 1]) / 2.0)
            rows += [(k, f"m{i + 1}"), (k, f"m{i + 2}")]
    if kind == "tortoise-shell":
        # triangular groups: each station with two holes on the row 2d, s above and below it;
        # the groups are linked along the second row, so the spine wraps make hexagons
        s = min(g / 4.0, e / 2.0)
        rows = []
        for i in range(4):
            a, b = f"t{i + 1}a", f"t{i + 1}b"
            holes[a] = (2 * d, ys[i] - s)
            holes[b] = (2 * d, ys[i] + s)
            rows += [(f"m{i + 1}", a), (f"m{i + 1}", b)]
            if i:
                rows.append((f"t{i}b", a))
    spines = sorted(holes)
    return holes, rows, spines, heads, tails


holes, rows, spines, heads, tails = layout(pattern)
order = sorted(holes, key=lambda k: (round(holes[k][1], 6), holes[k][0]))
number = {k: i + 1 for i, k in enumerate(order)}
x_deep = max(x for x, _ in holes.values())
hinge_x = x_deep + r + gap
if W - hinge_x < 40.0:
    raise ValueError(f"stab-binding: the hinge ({hinge_x:.1f} mm) leaves under 40 mm of page")


def seg_dist(p, a, b):
    ax, ay = b[0] - a[0], b[1] - a[1]
    t = max(0.0, min(1.0, ((p[0] - a[0]) * ax + (p[1] - a[1]) * ay) / (ax * ax + ay * ay)))
    return math.hypot(p[0] - a[0] - t * ax, p[1] - a[1] - t * ay)


def stitch_segments():
    """Every outside stitch as a drawn segment on the front (the back mirrors it)."""
    out = []
    for a, b in rows:
        out.append(((a, b), holes[a], holes[b]))
    for k in spines:
        out.append(((k,), holes[k], (0.0, holes[k][1])))
    for k in heads:
        out.append(((k,), holes[k], (holes[k][0], 0.0)))
    for k in tails:
        out.append(((k,), holes[k], (holes[k][0], H)))
    return out


# Self-checks on the layout: bridges to the spine and head/tail, hole spacing, and no stitch
# running over a hole it does not use.
for k, (x, y) in holes.items():
    if min(x, y, H - y) - r < MIN:
        raise ValueError(f"stab-binding: hole {number[k]} is closer than {MIN} mm to an edge")
for i, a in enumerate(order):
    for b in order[i + 1:]:
        if math.dist(holes[a], holes[b]) - 2 * r < MIN:
            raise ValueError(f"stab-binding: holes {number[a]} and {number[b]} are too close")
for ends, a, b in stitch_segments():
    for k, p in holes.items():
        if k not in ends and seg_dist(p, a, b) < r + MIN:
            raise ValueError(f"stab-binding: a stitch runs over hole {number[k]}")

# ── the thread graph and one sewing route ─────────────────────────────────────
# Nodes are (hole, side) with side F (front cover) or B (back cover). Outside stitches: a row
# stitch on each side, and spine / head / tail wraps from F to B. Through-passes go from F to B
# through the stack; at every node the thread alternates between the two kinds, so each node
# needs as many passes as it has outside stitches.

edges = []
for a, b in rows:
    edges += [((a, "F"), (b, "F"), "o", ("row", a, b)), ((a, "B"), (b, "B"), "o", ("row", a, b))]
for wrap, ks in (("spine", spines), ("head", heads), ("tail", tails)):
    for k in ks:
        edges.append(((k, "F"), (k, "B"), "o", (wrap, k)))
deg = {}
for a, b, _, _ in edges:
    deg[a] = deg.get(a, 0) + 1
    deg[b] = deg.get(b, 0) + 1
for k in order:
    if deg.get((k, "F"), 0) != deg.get((k, "B"), 0) or not deg.get((k, "F"), 0):
        raise ValueError(f"stab-binding: hole {number[k]} cannot be sewn evenly front and back")
    for _ in range(deg[(k, "F")]):
        edges.append(((k, "F"), (k, "B"), "t", ("through", k)))
used = [False] * len(edges)
incident = {}
for i, (a, b, _, _) in enumerate(edges):
    incident.setdefault(a, []).append(i)
    incident.setdefault(b, []).append(i)


def walk(v, kind):
    seq = []
    while True:
        nxt = next((i for i in incident[v] if not used[i] and edges[i][2] == kind), None)
        if nxt is None:
            return seq, v
        used[nxt] = True
        seq.append((v, nxt))
        a, b = edges[nxt][0], edges[nxt][1]
        v = b if a == v else a
        kind = "o" if kind == "t" else "t"


start = ("m2", "F")
route, end = walk(start, "t")
while not all(used):
    for pos, (v, i) in enumerate(route):
        sub, back = walk(v, edges[i][2])
        if sub:
            if back != v or edges[sub[-1][1]][2] == edges[i][2]:
                raise ValueError("stab-binding: the sewing route does not close")
            route = route[:pos] + sub + route[pos:]
            break
    else:
        raise ValueError("stab-binding: the thread graph is not connected")
if end != start:
    raise ValueError("stab-binding: the sewing route does not return to its start")
for (v, i), (w, _) in zip(route, route[1:] + route[:1]):
    a, b = edges[i][0], edges[i][1]
    if (b if a == v else a) != w:
        raise ValueError("stab-binding: the sewing route is broken")

WORDS = {"spine": L4("spine", "lomo", "dos", "lombada"),
         "head": L4("head", "cabeza", "tête", "cabeça"),
         "tail": L4("tail", "pie", "queue", "pé")}


def route_text(lang):
    out = []
    for v, i in route:
        info = edges[i][3]
        if info[0] == "through":
            out.append(f"{number[info[1]]}{'↓' if v[1] == 'F' else '↑'}")
        elif info[0] == "row":
            a, b = (info[1], info[2]) if (info[1], v[1]) == v else (info[2], info[1])
            out.append(f"{number[a]}–{number[b]}")
        else:
            out.append(WORDS[info[0]][lang])
    return " · ".join(out)


# ── sheets ───────────────────────────────────────────────────────────────────


def ring(cx, cy, turn):
    """A hole: NSEG-gon with inscribed radius r, turned by `turn` of a side. Each hole gets its
    own turn so no two holes share a vertex line (aligned vertices can upset hole bridging)."""
    rr = r / math.cos(math.pi / NSEG)
    return [(cx + rr * math.cos(2 * math.pi * (k + turn) / NSEG),
             cy + rr * math.sin(2 * math.pi * (k + turn) / NSEG)) for k in range(NSEG)]


def uv(k, folded_half=False):
    """Sheet point of hole k (v measured from the tail; the head is the top edge v = H)."""
    x, y = holes[k]
    return ((2 * W - x) if folded_half else x, H - y)


TURN = 0.5                            # every hole polygon turned by half a side


def make_sheet(sid, label, stock, folded, hinge_at=None):
    """One sheet with every hole (each a polygon turned by TURN of a side)."""
    width = 2 * W if folded else W
    # Outline vertices on the spine edge(s) level with every hole give each hole a near, plain
    # target for its bridges.
    vs = sorted({round(H - y, 9) for _, y in holes.values()})
    outline = ([(0, 0), (width, 0)] + ([(width, v) for v in vs] if folded else [])
               + [(width, H), (0, H)] + [(0, v) for v in reversed(vs)])
    s = pliego.Sheet(sid, outline, stock=stock, grain_deg=90.0, label=label)
    for k in order:
        s.hole(ring(*uv(k), TURN))
        if folded:
            s.hole(ring(*uv(k, True), TURN))
    s.label_edge("spine", (0, 0), (0, H))
    fold = hinge_mark = None
    if folded:
        s.label_edge("spine", (width, 0), (width, H))
        fold = s.mountain((W, 0), (W, H), name="fore-edge",
                          label=L4("Fore-edge fold", "Doblez del corte delantero",
                                   "Pli de la gouttière", "Dobra do corte da frente"))
    else:
        s.label_edge("fore-edge", (W, 0), (W, H))
    if hinge_at is not None:
        hinge_mark = s.score((hinge_at, 0), (hinge_at, H), "valley", OPEN, name="hinge",
                             label=L4("Hinge score", "Hendido de la bisagra",
                                      "Rainage de la charnière", "Vinco da dobradiça"))
    return s, fold, hinge_mark


front, _, hinge = make_sheet("cover-front", L4("Front cover", "Tapa delantera",
                                               "Couverture avant", "Capa da frente"),
                             cover_stock, False, hinge_x)
back, _, _ = make_sheet("cover-back", L4("Back cover", "Tapa trasera", "Couverture arrière",
                                         "Capa de trás"), cover_stock, False)
text = []
for n in range(1, N + 1):
    leaf, fold, _ = make_sheet(f"leaf-{n}", L4(f"Leaf {n}", f"Hoja {n}", f"Feuillet {n}",
                                               f"Folha {n}"), text_stock, FOLDED)
    text.append((leaf, fold))

# Papercut checks: one connected piece, every bridge at least the stock's minimum feature.
for s, mf in ((front, min_cover), (text[0][0], min_text)):
    rep = pliego.papercut.analyze(s, min_feature_mm=mf)
    if rep.components != 1 or rep.issues:
        raise ValueError(f"stab-binding: {s.id} fails the papercut check: {rep.issues}")
# the narrowest bridge: a hole to the spine, head or tail edge, or two holes to each other
bridge = min([min(x, y, H - y) - r for x, y in holes.values()]
             + [math.dist(holes[a], holes[b]) - 2 * r
                for i, a in enumerate(order) for b in order[i + 1:]])

# The preview roots each sheet's face tree at its first face: it must be the stitched strip,
# so that the hinge turns the page and not the strip.
farr = front.build()
if max(farr.vertices[v].x for v in farr.faces[0]) > hinge_x + 1e-9:
    raise ValueError("stab-binding: the front cover's first face is not the stitched strip")

# ── the stack in 3-D (world: sheet (u, v) → (u, y, −v), Y up) ─────────────────
# Layers top to bottom: front cover, the leaves (folded leaves: the upper half, then the half
# folded under it), back cover. The preview draws a shut fold at 179.5°, so a folded leaf's lower
# half opens W·sin 0.5° at the spine; the back cover sits that much lower to leave it room.
layers = [("cover-front", t_cover)]
for n in range(1, N + 1):
    layers.append((f"leaf-{n}", t_text))
    if FOLDED:
        layers.append((f"leaf-{n}~", t_text))
layers.append(("cover-back", t_cover))
y, centre = 0.0, {}
for i, (lid, t) in enumerate(layers):
    if i:
        y -= (layers[i - 1][1] + t) / 2.0
    centre[lid] = y
dip = W * math.sin(math.radians(180.0 - SHOWN)) if FOLDED else 0.0
centre["cover-back"] -= dip
T_real = math.fsum(t for _, t in layers)
for lid in list(centre):
    if FOLDED and lid.endswith("~"):
        centre[lid] = centre[lid[:-1]]      # the lower half hangs from the upper half's fold
for s in [front, back] + [x[0] for x in text]:
    s.placement = pliego.Placement(origin=(0.0, centre[s.id], 0.0))
initial = {}
if FOLDED:
    for s, fold in text:
        # posed at the preview's shut angle: exactly −180° leaves the side of the fold ambiguous
        initial[s.id] = {"angles": {fold: -SHOWN}, "root": (1.0, H / 2.0)}

# ── the thread as string joins ───────────────────────────────────────────────


def anchor(k, toward, folded_half=False):
    x, y0 = holes[k]
    dx, dy = toward[0] - x, toward[1] - y0
    n = math.hypot(dx, dy)
    hx, hy = x + RIM * dx / n, y0 + RIM * dy / n
    return ((2 * W - hx) if folded_half else hx, H - hy)


def world(sid, p):
    """World point of sheet point p on layer sid (a `~` layer is a folded leaf's lower half)."""
    if not sid.endswith("~"):
        return (p[0], centre[sid], -p[1])
    s_ = p[0] - W                           # distance past the fore-edge fold
    a = math.radians(180.0 - SHOWN)
    return (W - s_ * math.cos(a), centre[sid] - s_ * math.sin(a), -p[1])


joins, outside = [], 0.0
for a, b in rows:
    pa, pb = anchor(a, holes[b]), anchor(b, holes[a])
    length = math.dist(pa, pb)
    for side, s in (("f", front), ("b", back)):
        joins.append(pliego.string(f"stitch-{side}-{number[a]}-{number[b]}", (s, pa), (s, pb),
                                   length))
    outside += 2 * length
for wrap, ks in (("spine", spines), ("head", heads), ("tail", tails)):
    for k in ks:
        x, y0 = holes[k]
        edge_pt = {"spine": (0.0, y0), "head": (x, 0.0), "tail": (x, H)}[wrap]
        p = anchor(k, edge_pt)
        reach = math.dist((p[0], H - p[1]), edge_pt)
        chord = math.dist(world("cover-front", p), world("cover-back", p))
        length = max(2 * reach + T_real, chord)
        joins.append(pliego.string(f"{wrap}-{number[k]}", (front, p), (back, p), length))
        outside += 2 * reach + T_real
passes = 0
for k in order:
    chain = [("cover-front", front, False)]
    for s, _ in text:
        chain.append((s.id, s, False))
        if FOLDED:
            chain.append((s.id + "~", s, True))
    chain.append(("cover-back", back, False))
    for (la, sa, fa), (lb, sb, fb) in zip(chain, chain[1:]):
        pa = anchor(k, (0.0, holes[k][1]), fa)
        pb = anchor(k, (0.0, holes[k][1]), fb)
        chord = math.dist(world(la, pa), world(lb, pb))
        joins.append(pliego.string(f"pass-{number[k]}-{len(joins)}", (sa, pa), (sb, pb),
                                   max(chord, 0.05)))
    passes += deg[(k, "F")]
path = outside + passes * T_real
diag = math.hypot(W, H)
if pattern == "four-hole" and path > 3 * H + diag:
    raise ValueError(f"stab-binding: the route ({path:.0f} mm) exceeds the thread allowance")

# ── the program ──────────────────────────────────────────────────────────────

NAMES = {"four-hole": L4("Four-hole", "de cuatro agujeros", "à quatre trous", "de quatro furos"),
         "tortoise-shell": L4("Tortoise-shell", "de caparazón de tortuga", "carapace de tortue",
                              "de casco de tartaruga"),
         "hemp-leaf": L4("Hemp-leaf", "de hoja de cáñamo", "feuille de chanvre",
                         "de folha de cânhamo"),
         "noble": L4("Noble", "noble", "noble", "nobre")}
p_ = {lang: route_text(lang) for lang in ("en", "es", "fr", "pt")}
nh = len(order)
sew_note = L4(
    f"{NAMES[pattern]['en']} pattern, {nh} holes numbered from the head (↓ front to back, ↑ back "
    f"to front): {p_['en']}. The route is {path:.0f} mm long; add thread for the needle and the "
    "knot.",
    f"Patrón {NAMES[pattern]['es']}, {nh} agujeros numerados desde la cabeza (↓ del frente "
    f"hacia atrás, ↑ de atrás hacia el frente): {p_['es']}. El recorrido mide {path:.0f} mm; "
    "deja hilo de más para la aguja y el nudo.",
    f"Motif {NAMES[pattern]['fr']}, {nh} trous numérotés depuis la tête (↓ de l'avant vers "
    f"l'arrière, ↑ de l'arrière vers l'avant) : {p_['fr']}. Le parcours mesure {path:.0f} mm ; "
    "prévoyez du fil en plus pour l'aiguille et le nœud.",
    f"Padrão {NAMES[pattern]['pt']}, {nh} furos numerados a partir da cabeça (↓ da frente "
    f"para trás, ↑ de trás para a frente): {p_['pt']}. O percurso mede {path:.0f} mm; deixe "
    "linha a mais para a agulha e o nó.")
open_note = L4(
    f"The cover turns on its hinge score, {gap:g} mm outside the holes; the stitched strip "
    "stays put.",
    f"La tapa gira sobre su hendido, a {gap:g} mm de los agujeros; la franja cosida no se "
    "mueve.",
    f"La couverture tourne sur son rainage, à {gap:g} mm des trous ; la bande cousue ne bouge "
    "pas.",
    f"A capa gira sobre o vinco, a {gap:g} mm dos furos; a faixa costurada não se mexe.")
steps = [
    pliego.Step("sew", L4("Stab the holes and sew", "Perfora los agujeros y cose",
                          "Percez les trous et cousez", "Fure os furos e costure"),
                [], duration_ms=1500, note=sew_note),
    pliego.Step("open", L4("Open the cover on the hinge", "Abre la tapa por la bisagra",
                           "Ouvrez la couverture sur la charnière",
                           "Abra a capa pela dobradiça"),
                [(hinge, OPEN)], duration_ms=2600, note=open_note),
]

print(f"stab: pattern={pattern} form={mode} holes={nh} leaves={N} book={W:g}x{H:g}mm "
      f"row={d:g}mm hinge={hinge_x:.2f}mm bridge={bridge:.2f}mm stack={T_real:.2f}mm "
      f"route={len(route)} moves passes={passes} path={path:.0f}mm strings={len(joins)}")

result = pliego.Assembly(
    [front] + [x[0] for x in text] + [back],
    joins=joins,
    controls=[pliego.sequence_control(label=L4("Sew and open", "Coser y abrir",
                                               "Coudre et ouvrir", "Costurar e abrir"))],
    sequence=pliego.Sequence(steps, mode="kinematic"),
    initial=initial or None,
    title="Stab binding",
    min_feature_mm=MIN,
)
