"""Papercraft unfold — sheet-hyperobjects cartridge (Pliego).

Any low-poly mesh unfolded into printable papercraft nets: tabbed, numbered pieces laid out on
A4 or US Letter pages, with a program that folds every piece from the flat page into its place
on the model. The bridge from solids to sheets: the same unfolder takes a mesh from anywhere
(here an icosphere, a torus, or the embedded crystal below, which stands in for a mesh exported
by another platform such as Yantra4D).

The geometry is the kernel's `pliego.unfold.net()` (kernel.md §5): uniform scaling to the target
size; a greedy cut tree (min-perimeter or steepest-edge order) that joins two pieces only when the
joined piece stays overlap-free, keeps room for its tabs, and still fits the page; one glue tab per
cut, alternating sides; the cut's number printed on both sides; mountain or valley from the sign
of each 3-D dihedral. Mode `fold` is the kinematic fold-up; mode `glued` is the assembled model
with a glue join under every tab, for the physics engine.
"""

import pliego


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


shape = str(PARAM(lambda: shape, "icosphere"))                      # noqa: F821
subdivisions = round(float(PARAM(lambda: subdivisions, 1)))         # noqa: F821
torus_segments = round(float(PARAM(lambda: torus_segments, 12)))    # noqa: F821
torus_sides = round(float(PARAM(lambda: torus_sides, 6)))           # noqa: F821
torus_tube = float(PARAM(lambda: torus_tube, 0.38))                 # noqa: F821
size = float(PARAM(lambda: size, 120.0))                            # noqa: F821
page = str(PARAM(lambda: page, "a4"))                               # noqa: F821
method = str(PARAM(lambda: method, "min-perimeter"))                # noqa: F821
tab_style = str(PARAM(lambda: tab_style, "trapezoid"))              # noqa: F821
tab_angle = float(PARAM(lambda: tab_angle, 45.0))                   # noqa: F821
tab_height = float(PARAM(lambda: tab_height, 6.0))                  # noqa: F821
stock = str(PARAM(lambda: stock, "cardstock-250"))                  # noqa: F821
mode = str(PARAM(lambda: mode, "fold"))                             # noqa: F821

SHAPES = ("icosphere", "torus", "crystal")
STOCKS = ("cardstock-160", "cardstock-250", "cardstock-300")
if shape not in SHAPES:
    raise ValueError(f"papercraft-unfold: shape must be one of {SHAPES}, got {shape!r}")
if stock not in STOCKS:
    raise ValueError(f"papercraft-unfold: stock must be one of {STOCKS}, got {stock!r}")
if mode not in ("fold", "glued"):
    raise ValueError(f"papercraft-unfold: mode must be fold or glued, got {mode!r}")
subdivisions = int(pliego.clamp(subdivisions, 0, 2))
torus_segments = int(pliego.clamp(torus_segments, 8, 16))
torus_sides = int(pliego.clamp(torus_sides, 4, 8))
torus_tube = pliego.clamp(torus_tube, 0.25, 0.5)

# ── the embedded mesh: an original quartz-like crystal (MADFAM) ─────────────
# Plain vertex and face lists, the form any exported low-poly mesh takes: faces counter-clockwise
# seen from outside. The prism's top ring is its base ring scaled by 3/4 toward a point on the
# axis, so every side quad is exactly planar; the tip leans off the axis.
CRYSTAL_VERTICES = [
    (40, 0, 0), (20, 0, -36), (-20, 0, -32), (-44, 0, 0), (-24, 0, 36), (16, 0, 32),
    (30, 96, 0), (15, 96, -27), (-15, 96, -24), (-33, 96, 0), (-18, 96, 27), (12, 96, 24),
    (6, 140, -4),
]
CRYSTAL_FACES = (
    [[5, 4, 3, 2, 1, 0]]
    + [[k, (k + 1) % 6, 6 + (k + 1) % 6, 6 + k] for k in range(6)]
    + [[6 + k, 6 + (k + 1) % 6, 12] for k in range(6)]
)

if shape == "icosphere":
    model = pliego.mesh.icosphere(subdivisions)
    title = f"Papercraft icosphere ({20 * 4 ** subdivisions} faces)"
elif shape == "torus":
    model = pliego.mesh.torus(1.0, torus_tube, torus_segments, torus_sides)
    title = f"Papercraft torus ({torus_segments} x {torus_sides})"
else:
    model = pliego.mesh.Mesh(CRYSTAL_VERTICES, CRYSTAL_FACES)
    title = "Papercraft crystal"

net = pliego.unfold.net(model, size=size, page=page, method=method, tabs=tab_style,
                        tab_height=tab_height, tab_angle=tab_angle)
result = net.assembly(mode, stock=stock, title=title)
print(net.summary())
