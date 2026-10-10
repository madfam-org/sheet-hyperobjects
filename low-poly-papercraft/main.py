"""Low-poly papercraft — sheet-hyperobjects cartridge (Pliego).

One family of original MADFAM low-poly models, chosen by `design`: a heart, a ringed planet, a
vase, a gem, a fox head, a mask and a car. Each model is generated here from mesh primitives
(`pliego.mesh`): no commercial papercraft model or pattern file is copied or traced. Each one is
unfolded by the kernel (`pliego.unfold.net`, kernel.md §5) into tabbed, numbered pieces packed
onto pages, with a program that folds every piece from the page into its place on the model.

How each design is built:

- heart: a heart outline (the classic parametric heart curve, 14 points) extruded into a slab,
  both faces bevelled toward a smaller copy (a pillow heart);
- planet: a lathe whose profile runs up a faceted sphere, out along a flat ring and back, all one
  closed surface, then tilted;
- vase: a lathe with a flat foot and an open mouth (an open mesh: the lip is a plain cut edge);
- gem: a lathe with a pointed pavilion, a girdle band and a flat table;
- fox: the convex hull of a few control points (pointed snout, wide cheeks), with two pyramid
  ears extruded from the faces nearest the ear positions;
- mask: a patch of an ellipsoid, narrowed toward the chin, with a raised nose and brow and two
  eye holes (an open mesh);
- car: a side profile with the wheels drawn into it, extruded across the car's width (the
  paper-toy car).
"""

import math

import pliego


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


design = str(PARAM(lambda: design, "fox"))                          # noqa: F821
size = float(PARAM(lambda: size, 150.0))                            # noqa: F821
page = str(PARAM(lambda: page, "a4"))                               # noqa: F821
method = str(PARAM(lambda: method, "min-perimeter"))                # noqa: F821
tab_style = str(PARAM(lambda: tab_style, "trapezoid"))              # noqa: F821
tab_angle = float(PARAM(lambda: tab_angle, 45.0))                   # noqa: F821
tab_height = float(PARAM(lambda: tab_height, 6.0))                  # noqa: F821
stock = str(PARAM(lambda: stock, "cardstock-250"))                  # noqa: F821
mode = str(PARAM(lambda: mode, "fold"))                             # noqa: F821

M = pliego.mesh
STOCKS = ("cardstock-160", "cardstock-250", "cardstock-300")
if stock not in STOCKS:
    raise ValueError(f"low-poly-papercraft: stock must be one of {STOCKS}, got {stock!r}")
if mode not in ("fold", "glued"):
    raise ValueError(f"low-poly-papercraft: mode must be fold or glued, got {mode!r}")


def mirrored(points):
    """Points on the right (x > 0) plus their mirror images; points on x = 0 once."""
    out = []
    for x, y, z in points:
        out.append((x, y, z))
        if x > 0:
            out.append((-x, y, z))
    return out


def heart():
    outline = []
    for k in range(14):
        t = 2 * math.pi * k / 14
        outline.append((16 * math.sin(t) ** 3,
                        13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t)
                        - math.cos(4 * t)))
    m = M.prism(outline, 9.0)          # faces 0 and 1 are the front and back outlines
    m = M.extrude(m, 0, 4.0, 0.55)     # bevel the front (the back is now face 0)
    return M.extrude(m, 0, 4.0, 0.55)  # bevel the back


def sphere_point(r, deg):
    """(radius, height) of a sphere's meridian at `deg` from the south pole."""
    return (r * math.sin(math.radians(deg)), -r * math.cos(math.radians(deg)))


def planet():
    r, half, ring = 1.0, 0.04, 1.7
    profile = [(0.0, -r)] + [sphere_point(r, a) for a in (28, 56, 80)]
    profile += [(r, -half), (ring, -half), (ring, half), (r, half)]
    profile += [sphere_point(r, a) for a in (100, 124, 152)] + [(0.0, r)]
    return M.lathe(profile, 12).rotated((1.0, 0.0, 0.35), 20.0)


def vase():
    profile = [(0.55, 0.0), (0.8, 0.25), (0.95, 0.7), (0.75, 1.15), (0.42, 1.5), (0.4, 1.75),
               (0.55, 1.95)]
    return M.lathe(profile, 9, cap_top=False)


def gem():
    return M.lathe([(0.0, 0.0), (1.0, 0.86), (1.0, 0.94), (0.58, 1.32)], 8)


def fox():
    head = M.hull(mirrored([
        (0.0, -0.08, 1.7), (0.0, -0.3, 1.55), (0.2, -0.16, 1.2),       # nose and muzzle
        (0.0, 0.3, 0.7), (0.43, 0.4, 0.28), (0.0, 0.66, -0.15),        # bridge, brow, crown
        (0.36, 0.52, -0.68), (0.0, 0.12, -0.95),                       # back of the head
        (0.98, -0.12, -0.05), (0.5, -0.52, 0.5), (0.0, -0.58, 0.9),    # cheek ruff, jaw, chin
        (0.0, -0.66, -0.3), (0.52, -0.5, -0.55),                       # throat and neck
    ]))
    for side in (1.0, -1.0):
        head = M.extrude(head, M.nearest_face(head, (0.42 * side, 0.6, -0.3)), 0.95, 0.0)
    return head


def mask():
    cols = [math.radians(a) for a in (-64, -48, -32, -16, 0, 16, 32, 48, 64)]
    rows = [math.radians(a) for a in (-62, -44, -24, -6, 10, 28, 46)]
    a, b, c = 0.8, 1.05, 0.62
    points = []
    for j, t in enumerate(rows):
        taper = 1.0 - 0.38 * max(0.0, -math.sin(t))             # the jaw narrows to the chin
        for i, p in enumerate(cols):
            x = a * taper * math.cos(t) * math.sin(p)
            y = b * math.sin(t)
            z = c * math.cos(t) * math.cos(p) - 0.12 * max(0.0, math.sin(t))  # brow leans back
            if i == 4:
                z += {1: 0.06, 2: 0.22, 3: 0.14}.get(j, 0.0)    # the nose
            if abs(i - 4) == 1 and j == 2:
                z += 0.05                                        # the nostrils
            if abs(i - 4) in (1, 2) and j == 5:
                z += 0.05                                        # the brow ridge
            points.append((x, y, z))
    n = len(cols)
    gaps = {(0, 0), (1, 0), (6, 0), (7, 0), (0, 5), (7, 5), (2, 4), (5, 4)}  # outline, eyes
    faces = [[j * n + i, j * n + i + 1, (j + 1) * n + i + 1, (j + 1) * n + i]
             for j in range(len(rows) - 1) for i in range(n - 1) if (i, j) not in gaps]
    used = sorted({v for f in faces for v in f})
    index = {v: k for k, v in enumerate(used)}
    return M.Mesh([points[v] for v in used], [[index[v] for v in f] for f in faces])


def car():
    def wheel(cx):
        return [(cx + 0.32 * math.cos(math.pi + math.pi * k / 4),
                 0.3 + 0.32 * math.sin(math.pi + math.pi * k / 4)) for k in range(5)]

    side = [(0.0, 0.3)] + wheel(0.72) + wheel(2.48) + [
        (3.2, 0.3), (3.25, 0.66), (2.35, 0.82), (1.85, 1.28), (0.95, 1.28), (0.38, 0.86),
        (0.0, 0.76)]
    return M.prism(side, 1.45)


DESIGNS = {
    "heart": (heart, "#c8102e", {"en": "Heart", "es": "Corazón", "fr": "Cœur", "pt": "Coração"}),
    "planet": (planet, "#e3a857", {"en": "Ringed planet", "es": "Planeta con anillos",
                                   "fr": "Planète à anneaux", "pt": "Planeta com anéis"}),
    "vase": (vase, "#2a6f97", {"en": "Vase", "es": "Jarrón", "fr": "Vase", "pt": "Vaso"}),
    "gem": (gem, "#5bc0be", {"en": "Gem", "es": "Gema", "fr": "Gemme", "pt": "Gema"}),
    "fox": (fox, "#e07a2e", {"en": "Fox head", "es": "Cabeza de zorro", "fr": "Tête de renard",
                             "pt": "Cabeça de raposa"}),
    "mask": (mask, "#efe3c8", {"en": "Mask", "es": "Máscara", "fr": "Masque", "pt": "Máscara"}),
    "car": (car, "#3a86ff", {"en": "Car", "es": "Coche", "fr": "Voiture", "pt": "Carro"}),
}
if design not in DESIGNS:
    raise ValueError(f"low-poly-papercraft: design must be one of {sorted(DESIGNS)}, "
                     f"got {design!r}")

build, colour, name = DESIGNS[design]
net = pliego.unfold.net(build(), size=size, page=page, method=method, tabs=tab_style,
                        tab_height=tab_height, tab_angle=tab_angle)
result = net.assembly(mode, stock=stock, front=colour, title=f"Low-poly {name['en'].lower()}")
print(net.summary())
