"""Pinwheel — sheet-hyperobjects cartridge (Pliego).

The traditional cut-and-fold windmill toy. A square is cut along its diagonals from the corners
towards the centre, stopping short of it; one corner of each of the four triangles is brought over
to the centre, and a pin through the centre and the four corners holds the blades on a stick.

* `blades` = 4: one square.
* `blades` = 8: two squares pinned together, the upper one smaller and turned 45°, its blades
  nested under the arches of the lower one.

The curl. Every blade is curled about three lines perpendicular to its corner's diagonal, folded
70°, 110° and 110° (valley, towards the viewer): up, over and back down, so the corner lands
exactly on the centre. With the curl split at distances s, s + a and s + a + b along the diagonal
D from the centre, the corner arrives at the centre when the arch's legs are equal (a) and
b = s + 2a·cos 70°, so a = (D − 2s) / (2 + 2·cos 70°). Real paper curls smoothly between these
lines, which the physics engine bends; the preview folds the three lines.

The spin is a `rotate` mechanism about the pin (the normal of the pinwheel at its centre) on the
`spin` control, and the fold program shows the making. A pinwheel turned by the wind needs the
engine's air model (wave 3): the `wind` control is declared for it and does nothing in the preview.
"""

import math

import pliego


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


blades = int(round(float(PARAM(lambda: blades, 4))))     # noqa: F821
size = float(PARAM(lambda: size, 180.0))                 # noqa: F821
centre = float(PARAM(lambda: centre, 0.22))              # noqa: F821
palette = PARAM(lambda: palette, "sunset")               # noqa: F821
stock = PARAM(lambda: stock, "copy-80")                  # noqa: F821

if blades not in (4, 8):
    raise ValueError(f"pinwheel: blades must be 4 or 8, got {blades}")
if stock not in ("copy-80", "kami", "cardstock-160"):
    raise ValueError(f"pinwheel: unknown stock {stock!r}")
PALETTES = {"sunset": (("#e4572e", "#f3a712"), ("#2e86ab", "#f6f3ec")),
            "garden": (("#4c9f70", "#f3d34a"), ("#a23b72", "#f6f3ec")),
            "paper": ((None, None), (None, None))}
if palette not in PALETTES:
    raise ValueError(f"pinwheel: unknown palette {palette!r}")
S = pliego.clamp(size, 100.0, 300.0)
RC = pliego.clamp(centre, 0.12, 0.3)       # the uncut centre, ÷ half the diagonal
TURNS = (70.0, 110.0, 110.0)               # the three curl folds
STICK_W, STICK_L = 10.0, 1.4 * S           # a card stick behind the wheel
PIN = 2.0                                  # pin hole diameter (mm)
PIN_Y = STICK_L - STICK_W / 2              # the pin, on the stick near its top


def L4(en, es, fr, pt):
    return {"en": en, "es": es, "fr": fr, "pt": pt}


def wheel(sid, side, colours, z, turn_deg, label):
    """One square wheel: cuts, curl creases, pin hole; standing upright (front towards +z),
    centred on the pin near the stick's top, turned by turn_deg about its centre."""
    D = side / math.sqrt(2.0)                # half-diagonal
    c = (side / 2.0, side / 2.0)
    rc, s0 = RC * D, RC * D + 0.06 * D       # cuts stop at rc; the curl starts at s0
    a = (D - 2 * s0) / (2.0 + 2.0 * math.cos(math.radians(TURNS[0])))
    b = s0 + 2 * a * math.cos(math.radians(TURNS[0]))
    if a < 4.0 or b < 4.0:
        raise ValueError(f"pinwheel: blades of {side:g} mm leave no room for the curl")
    q = math.radians(turn_deg) / 2.0
    # upright: x-axis +90° (sheet front → +z), then turn about z by turn_deg
    h = math.sqrt(0.5)
    rot = (h * math.cos(q), h * math.sin(q), h * math.sin(q), h * math.cos(q))
    cx, cy = c[0] * math.cos(2 * q) - c[1] * math.sin(2 * q), c[0] * math.sin(2 * q) + c[1] * math.cos(2 * q)
    sh = pliego.Sheet(sid, pliego.square(side), stock=stock, grain_deg=90.0, label=label,
                      front=colours[0], back=colours[1], kinematic="spin-wheel",
                      placement=pliego.Placement(origin=(-cx, PIN_Y - cy, z), rotation=rot))
    corners = [(0.0, 0.0), (side, 0.0), (side, side), (0.0, side)]
    steps = []
    for x, y in corners:
        u = ((x - c[0]) / D, (y - c[1]) / D)                    # unit, centre → corner
        sh.cut([(x, y), (c[0] + u[0] * rc, c[1] + u[1] * rc)], name="blade-cut")
    for k, (x, y) in enumerate(corners):
        # triangle k (corner k, corner k+1, centre) curls its first corner, k; so the face that
        # holds corner (0, 0) on the left triangle stays flat and is the preview's root
        u = ((x - c[0]) / D, (y - c[1]) / D)
        nx, ny = corners[(k + 1) % 4]
        w = ((nx - c[0]) / D, (ny - c[1]) / D)          # the triangle's other side (⟂ u)
        marks = []
        for d, turn in zip((s0, s0 + a, s0 + a + b), TURNS):
            p = (c[0] + u[0] * d, c[1] + u[1] * d)
            # perpendicular to the diagonal, into the triangle, up to the outer edge
            t_edge = (D - d)                        # right-angled wedge: the edge x + y = D
            e = (p[0] + w[0] * t_edge, p[1] + w[1] * t_edge)
            marks.append((sh.valley(p, e, turn, name="curl"), turn))
        steps.append(marks)
    sh.hole(pliego.circle(c, PIN / 2.0, 16))
    return sh, steps, c


CURL = L4("Curl blade {n} over to the centre", "Curva el aspa {n} hasta el centro",
          "Courber la pale {n} jusqu'au centre", "Curve a pá {n} até o centro")
pal = PALETTES[palette]
big, steps_big, c_big = wheel("wheel", S, pal[0], 0.0, 0.0,
                              L4("Pinwheel", "Rehilete", "Moulinet", "Cata-vento"))
sheets, all_steps = [big], [steps_big]
if blades == 8:
    small, steps_small, _ = wheel("wheel-top", 0.72 * S, pal[1], 0.3, 45.0,
                                  L4("Upper pinwheel", "Rehilete superior", "Moulinet du dessus",
                                     "Cata-vento de cima"))
    sheets.append(small)
    all_steps.append(steps_small)
stick = pliego.Sheet("stick", pliego.rectangle(STICK_W, STICK_L), stock="cardstock-300",
                     grain_deg=90.0, label=L4("Stick", "Palito", "Bâton", "Vareta"),
                     placement=pliego.Placement(origin=(-STICK_W / 2, 0.0, -1.0),
                                                rotation=(math.sin(math.pi / 4), 0.0, 0.0,
                                                          math.cos(math.pi / 4))))
for a, b in (((STICK_W / 2 - PIN, PIN_Y), (STICK_W / 2 + PIN, PIN_Y)),
             ((STICK_W / 2, PIN_Y - PIN), (STICK_W / 2, PIN_Y + PIN))):
    stick.halfcut([a, b], name="pin-mark")       # where the pin goes into the stick

program, n = [], 0
for layer in all_steps:
    for marks in layer:
        n += 1
        program.append(pliego.Step(f"curl-{n}", {k: v.format(n=n) for k, v in CURL.items()},
                                   [(m, t) for m, t in marks], duration_ms=1200))
controls = [
    pliego.sequence_control(label=L4("Make it", "Armarlo", "Le fabriquer", "Montá-lo")),
    pliego.angle_control("spin", L4("Spin", "Girar", "Faire tourner", "Girar"), default=0.0,
                         min=0.0, max=360.0),
    pliego.control("wind", "wind", L4("Wind (needs the engine's air model)",
                                      "Viento (requiere el modelo de aire del motor)",
                                      "Vent (requiert le modèle d'air du moteur)",
                                      "Vento (requer o modelo de ar do motor)"),
                   default=0.0, min=0.0, max=10.0, unit="m/s"),
]
mech = pliego.rotate("spin-wheel", (stick, (STICK_W / 2, PIN_Y)), "spin", sheets[:])
print(f"pinwheel: blades={blades} size={S:g}mm centre={RC:g} stick={STICK_L:g}mm")
result = pliego.Assembly(sheets + [stick], mechanisms=[mech], controls=controls,
                         sequence=pliego.Sequence(program, mode="kinematic"), title="Pinwheel")
