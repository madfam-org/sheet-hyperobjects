"""Carousel book — sheet-hyperobjects cartridge (Pliego).

A book that opens 360° into a star of chambers. One long strip of card, scored into 2·N panels:
the front cover, N − 1 double walls (each a page folded at its fore-edge, its two layers back to
back) and the back cover. The scores alternate:

* spine folds (valley): every wall meets the spine here — all of them lie on one vertical axis;
* fore-edge folds (mountain, shut at 180°): the outer edge of each double wall.

Opened, the walls stand (360° − GAP)/N apart round the spine, so the strip makes N chambers and the
two covers meet GAP degrees apart, where two ribbons (`string` joins, top and bottom) tie them.
Every spine fold turns about the same axis, so any set of spine-fold angles is a rigid state and
the fold program, linear in the angles, is exact.

`windows` cuts the same window through both layers of every wall (mirrored about its fore-edge
fold) so the chambers look into each other; the cut sheet is checked with
`pliego.papercut.analyze` (one piece, every bridge at least the stock's minimum feature).

The book stands upright (placement: the sheet's v axis is world up). The initial frame is the
displayed state — open, ribbons tied — and the program closes the book and opens it again.
"""

import math

import pliego


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


chambers = round(float(PARAM(lambda: chambers, 5)))          # noqa: F821
page_width = float(PARAM(lambda: page_width, 100.0))         # noqa: F821
page_height = float(PARAM(lambda: page_height, 140.0))       # noqa: F821
stock = PARAM(lambda: stock, "cardstock-250")                # noqa: F821
windows = PARAM(lambda: windows, "arch")                     # noqa: F821

MIN_FEATURE = {"cardstock-250": 2.0, "cardstock-160": 1.5, "kraft-120": 1.5}
if stock not in MIN_FEATURE:
    raise ValueError(f"carousel-book: unsupported stock {stock!r}")
if windows not in ("none", "arch", "circle"):
    raise ValueError(f"carousel-book: windows must be none, arch or circle, got {windows!r}")
if not 3 <= chambers <= 8:
    raise ValueError(f"carousel-book: chambers must be an integer in [3, 8], got {chambers}")

N = chambers
w = pliego.clamp(page_width, 60.0, 200.0)
h = pliego.clamp(page_height, 80.0, 300.0)
GAP = 2.0                        # the covers meet this many degrees apart (card thickness)
ALPHA = (360.0 - GAP) / N        # angle between neighbouring walls, open
SHUT = 178.0                     # closed: each spine fold stops 2° short of flat
RIBBON_IN = 6.0                  # ribbon points: this far in from the covers' fore-edges
UPRIGHT = (math.sqrt(0.5), 0.0, 0.0, math.sqrt(0.5))      # +90° about X: sheet v → world up
min_feature = MIN_FEATURE[stock]


def L4(en, es, fr, pt):
    return {"en": en, "es": es, "fr": fr, "pt": pt}


strip = pliego.Sheet("carousel", [(0, 0), (2 * N * w, 0), (2 * N * w, h), (0, h)], stock=stock,
                     grain_deg=90.0, placement=pliego.Placement(rotation=UPRIGHT),
                     label=L4("Carousel strip", "Tira del carrusel", "Bande du carrousel",
                              "Tira do carrossel"))
strip.label_edge("cover-front-edge", (0, 0), (0, h))
strip.label_edge("cover-back-edge", (2 * N * w, 0), (2 * N * w, h))
spine_folds, fore_folds = [], []
for j in range(2 * N - 1):
    x = (j + 1) * w
    if j % 2 == 0:
        spine_folds.append(strip.crease((x, 0), (x, h), "valley", 180.0 - ALPHA,
                                        treatment="score", name="spine"))
    else:
        fore_folds.append(strip.crease((x, 0), (x, h), "mountain", 180.0, treatment="score",
                                       name="fore-edge"))


def window(cx):
    """One window outline centred on x = cx (sheet frame)."""
    ww = 0.46 * w
    y0 = 0.16 * h
    if windows == "circle":
        r = min(ww / 2.0, 0.3 * h)
        cy = 0.5 * h
        return [(cx + r * math.cos(2 * math.pi * k / 32), cy + r * math.sin(2 * math.pi * k / 32))
                for k in range(32)]
    top = 0.72 * h
    pts = [(cx - ww / 2.0, y0), (cx + ww / 2.0, y0), (cx + ww / 2.0, top - ww / 2.0)]
    for k in range(1, 16):
        t = math.pi * k / 16
        pts.append((cx + ww / 2.0 * math.cos(t), top - ww / 2.0 + ww / 2.0 * math.sin(t)))
    pts.append((cx - ww / 2.0, top - ww / 2.0))
    return pts


if windows != "none":
    r_c = 0.52 * w               # window centre, measured from the spine along the wall
    for k in range(1, N):
        x_axis_a, x_fore = (2 * k - 1) * w, 2 * k * w
        strip.hole(window(x_axis_a + r_c))               # layer a: spine → fore-edge
        strip.hole(window(x_fore + (w - r_c)))           # layer b: mirrored about the fore-edge
    report = pliego.papercut.analyze(strip, min_feature_mm=min_feature)
    errors = [i for i in report.issues if i["level"] == "error"]
    if errors:
        raise ValueError("carousel-book: papercut check failed: "
                         + "; ".join(i["detail"] for i in errors))

arr = strip.build()


def angles(spine_deg):
    out = {}
    for m in spine_folds:
        for e in m.edges():
            out[e] = spine_deg
    for m in fore_folds:
        for e in m.edges():
            out[e] = -180.0
    return out


# Self-checks on the open state: walls ALPHA apart, covers GAP apart, nothing passes the front.
open_state = angles(180.0 - ALPHA)
if pliego.kinematics.closure_residual(arr, open_state) > 1e-6:
    raise ValueError("carousel-book: the open strip is not a rigid state")
tr = pliego.kinematics.face_transforms(arr, open_state, 0)


def world(fi, u, v):
    rm, t = tr[fi]
    p = (u, 0.0, -v)
    return tuple(rm[i][0] * p[0] + rm[i][1] * p[1] + rm[i][2] * p[2] + t[i] for i in range(3))


panel = {}
for fi, f in enumerate(arr.faces):
    xs = [arr.vertices[v].x for v in f]
    panel.setdefault(int((min(xs) + max(xs)) / 2.0 // w), []).append(fi)
if sorted(panel) != list(range(2 * N)):
    raise ValueError("carousel-book: the strip did not divide into its panels")
heading = []
for i in range(2 * N):
    fi = panel[i][0]
    axis_x = (i + 1) * w if i % 2 == 0 else i * w        # the panel's spine end
    out_x = i * w if i % 2 == 0 else (i + 1) * w
    a, b = world(fi, axis_x, 0.0), world(fi, out_x, 0.0)
    heading.append(math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])))
turn = [(heading[0] - heading[i]) % 360.0 for i in range(2 * N)]
turn[-1] = turn[-1] if turn[-1] > 1.0 else turn[-1] + 360.0
for k in range(1, N):
    for i in (2 * k - 1, 2 * k):
        if abs(turn[i] - k * ALPHA) > 1e-6:
            raise ValueError(f"carousel-book: wall {k} stands at {turn[i]:.3f}°, not "
                             f"{k * ALPHA:.3f}°")
if abs(turn[-1] - (360.0 - GAP)) > 1e-6:
    raise ValueError("carousel-book: the covers do not meet")

# Ribbons: tied between the covers' fore-edges, top and bottom, at their open-state distance.
joins = []
for name, y in (("top", h - 15.0), ("bottom", 15.0)):
    pa = (RIBBON_IN, y)
    pb = (2 * N * w - RIBBON_IN, y)
    d = math.dist(world(panel[0][0], *pa), world(panel[2 * N - 1][0], *pb))
    joins.append(pliego.string(f"ribbon-{name}", (strip, pa), (strip, pb), round(d, 3) + 0.5))

open_label = L4(f"Open it all the way round: {N} chambers, {ALPHA:.1f}° apart",
                f"Ábrelo por completo: {N} cámaras, a {ALPHA:.1f}° una de otra",
                f"Ouvrez-le jusqu'au bout : {N} chambres, à {ALPHA:.1f}° l'une de l'autre",
                f"Abra-o por inteiro: {N} câmaras, a {ALPHA:.1f}° uma da outra")
steps = [
    pliego.Step("close", L4("Untie the ribbons and close the book",
                            "Desata los listones y cierra el libro",
                            "Dénouez les rubans et fermez le livre",
                            "Desamarre as fitas e feche o livro"),
                [(m, SHUT) for m in spine_folds], duration_ms=2500,
                release_joins=[j["id"] for j in joins]),
    pliego.Step("open", open_label, [(m, 180.0 - ALPHA) for m in spine_folds], duration_ms=3500,
                note=L4("Bring the covers together.", "Junta las tapas.",
                        "Rapprochez les couvertures.", "Junte as capas.")),
    pliego.Step("tie", L4("Tie the ribbons at top and bottom", "Ata los listones arriba y abajo",
                          "Nouez les rubans en haut et en bas",
                          "Amarre as fitas em cima e em baixo"),
                [], duration_ms=800),
]
# spec §5.20: the ribbons tied in the displayed state come undone as the book closes; tied again
# once it is open (a released join stays released, so the second knot is its own join, §5.19)
joins += [dict(j, id=f"{j['id']}-again", active_from="tie") for j in list(joins)]
for st in (st for st in steps if st.targets):
    state = angles(st.targets[0][1])
    if pliego.kinematics.closure_residual(arr, state) > 1e-6:
        raise ValueError(f"carousel-book: step {st.id} is not a rigid state")

print(f"carousel: chambers={N} page={w:g}x{h:g}mm strip={2 * N * w:g}mm alpha={ALPHA:.3f}deg "
      f"windows={windows} ribbons={[round(j['length'], 2) for j in joins[:2]]} "
      f"untied@close retied@tie")

result = pliego.Assembly(
    [strip], joins=joins,
    controls=[pliego.sequence_control(label=L4("Close and open", "Cerrar y abrir",
                                               "Fermer et ouvrir", "Fechar e abrir"),
                                      default=3.0)],
    sequence=pliego.Sequence(steps, mode="kinematic"),
    initial={"angles": {m: 180.0 - ALPHA for m in spine_folds}
             | {m: -180.0 for m in fore_folds}, "root": (w / 2.0, h / 2.0)},
    min_feature_mm=None,
    title="Carousel book",
)
