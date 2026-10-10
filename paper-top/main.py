"""Paper top — sheet-hyperobjects cartridge (Pliego).

A spinning top made of card: a disc on an axle. The axle is folded from a strip too: three panels
make a triangular prism (a glue tab closes it), and a triangle under each panel folds in to make a
pyramid point, the tip it spins on. The disc has a triangular hole that keys it to the axle, so the
two turn together.

The point: with the prism's cross-section an equilateral triangle of side w (in-radius
r = w / (2√3)) and the tip a depth d below the prism, each tip face is an isosceles triangle of
base w and height √(d² + r²), folded in by atan(r / d) from its panel.

Designs printed on the disc (original): `newton` (seven colour sectors that blend towards white
when spun, after Newton's colour wheel), `spiral` (a two-arm spiral that seems to grow or shrink)
and `rings` (concentric rings that stay still while the top turns).

Mode `spin` is the assembled top (the axle's glue joint and the initial frame) turning on a
`hinge` mechanism about its axis (the axle's centre line), on the `spin` control. Mode `make` folds the axle. A real top's
spinning (gyroscopic stability, the wobble and precession, friction at the tip, slowing down) needs
the physics engine.
"""

import math

import pliego


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


mode = PARAM(lambda: mode, "spin")                     # noqa: F821
diameter = float(PARAM(lambda: diameter, 80.0))        # noqa: F821
axle_length = float(PARAM(lambda: axle_length, 70.0))  # noqa: F821
axle_width = float(PARAM(lambda: axle_width, 8.0))     # noqa: F821
design = PARAM(lambda: design, "newton")               # noqa: F821

if mode not in ("spin", "make"):
    raise ValueError(f"paper-top: unknown mode {mode!r}")
if design not in ("newton", "spiral", "rings"):
    raise ValueError(f"paper-top: unknown design {design!r}")
DIA = pliego.clamp(diameter, 40.0, 160.0)
R = DIA / 2.0
L = pliego.clamp(axle_length, 0.6 * DIA, 2.0 * DIA)
W = pliego.clamp(axle_width, 5.0, 15.0)
RIN = W / (2 * math.sqrt(3.0))                 # in-radius of the axle's cross-section
RCI = W / math.sqrt(3.0)                       # its circumradius
D = 1.4 * W                                    # tip depth below the prism
HT = math.sqrt(D * D + RIN * RIN)              # height of a tip face in the net
TILT = math.degrees(math.atan2(RIN, D))        # fold of a tip face
GLUE_W = min(6.0, 0.8 * W)
DISC_AT = D + 0.3 * L                          # height of the disc above the tip
CLEAR = 0.2                                    # hole clearance (mm)


def L4(en, es, fr, pt):
    return {"en": en, "es": es, "fr": fr, "pt": pt}


# ── the axle: three panels, a glue tab, three tip faces ─────────────────────────
ring = [(0.0, HT), (W / 2, 0.0), (W, HT), (1.5 * W, 0.0), (2 * W, HT), (2.5 * W, 0.0),
        (3 * W, HT), (3 * W + GLUE_W, HT + GLUE_W), (3 * W + GLUE_W, HT + L - GLUE_W),
        (3 * W, HT + L), (0.0, HT + L)]
axle = pliego.Sheet("axle", ring, stock="cardstock-160", grain_deg=90.0,
                    label=L4("Axle", "Eje", "Axe", "Eixo"), front="#3d405b", back="#f4efe6",
                    kinematic="spin" if mode == "spin" else None)
edges = [axle.mountain((k * W, HT), (k * W, HT + L), 120.0, treatment="score", name="axle-edge")
         for k in (1, 2, 3)]
tips = [axle.mountain((k * W, HT), ((k + 1) * W, HT), TILT, treatment="score", name="tip")
        for k in range(3)]


def axle_world(u, v):
    """The folded axle: the prism standing on its point at the origin (y up)."""
    k = min(int(u // W), 3)
    k, s = (0, u - 3 * W) if k >= 3 else (k, u - k * W)
    a0, a1 = 2 * math.pi * k / 3, 2 * math.pi * (k + 1) / 3
    c0 = (RCI * math.cos(a0), RCI * math.sin(a0))
    c1 = (RCI * math.cos(a1), RCI * math.sin(a1))
    x, z = c0[0] + (c1[0] - c0[0]) * s / W, c0[1] + (c1[1] - c0[1]) * s / W
    if v >= HT:
        return (x, D + (v - HT), -z)
    t = (HT - v) / HT                             # 0 at the prism, 1 at the point
    m = (c0[0] + c1[0]) / 2, (c0[1] + c1[1]) / 2  # the face's base midpoint
    # in the face: across = along the base, down = from the base midpoint to the point
    return (x + (0.0 - m[0]) * t, D * (1 - t), -(z + (0.0 - m[1]) * t))


# checks: the folded axle is an isometry of the net, its front faces outwards
for p, q in (((0.0, HT), (W / 2, 0.0)), ((W / 2, 0.0), (W, HT)), ((0.5 * W, HT), (0.5 * W, HT + L))):
    if abs(math.dist(axle_world(*p), axle_world(*q)) - math.dist(p, q)) > 1e-6:
        raise ValueError("paper-top: the axle's net does not fold onto the axle")
p0, p1, p2 = axle_world(0.2 * W, HT + 5), axle_world(0.6 * W, HT + 5), axle_world(0.2 * W, HT + 9)
e1, e2 = [p1[i] - p0[i] for i in range(3)], [p2[i] - p0[i] for i in range(3)]
nx, nz = e1[1] * e2[2] - e1[2] * e2[1], e1[0] * e2[1] - e1[1] * e2[0]
if nx * p0[0] + nz * p0[2] <= 0:
    raise ValueError("paper-top: the axle's print would face inwards")

# ── the disc ──────────────────────────────────────────────────────────────────


def disc_art():
    """Original disc pattern over the disc's bounding box (image y down)."""
    c, out = R, [f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {DIA:.2f} {DIA:.2f}'>"]
    if design == "newton":
        cols = ["#e4572e", "#f28c28", "#f3d34a", "#4c9f70", "#2e86ab", "#3d405b", "#a23b72"]
        for k, col in enumerate(cols):
            a0, a1 = 2 * math.pi * k / 7, 2 * math.pi * (k + 1) / 7
            out.append(f"<path d='M{c:.2f},{c:.2f} L{c + R * math.cos(a0):.2f},"
                       f"{c - R * math.sin(a0):.2f} A{R:.2f},{R:.2f} 0 0 0 "
                       f"{c + R * math.cos(a1):.2f},{c - R * math.sin(a1):.2f} Z' fill='{col}'/>")
    elif design == "spiral":
        out.append(f"<circle cx='{c:.2f}' cy='{c:.2f}' r='{R:.2f}' fill='#fdfaf3'/>")
        for arm in (0, math.pi):
            pts = [(c + R * t * math.cos(arm + 4 * math.pi * t), c - R * t * math.sin(arm + 4 * math.pi * t))
                   for t in (j / 120 for j in range(121))]
            out.append("<polyline points='" + " ".join(f"{x:.2f},{y:.2f}" for x, y in pts)
                       + f"' fill='none' stroke='#1d1d1f' stroke-width='{R / 10:.2f}'/>")
    else:
        for j in range(8, 0, -1):
            out.append(f"<circle cx='{c:.2f}' cy='{c:.2f}' r='{R * j / 8:.2f}' "
                       f"fill='{['#e4572e', '#fdfaf3', '#2e86ab', '#f3a712'][j % 4]}'/>")
    svg = "".join(out) + "</svg>"
    for a, b in (("%", "%25"), ("#", "%23"), ("<", "%3C"), (">", "%3E"), (" ", "%20"),
                 ("'", "%27")):
        svg = svg.replace(a, b)
    return "data:image/svg+xml;charset=utf-8," + svg


disc = pliego.Sheet("disc", pliego.circle((R, R), R, 96), stock="cardstock-300", grain_deg=90.0,
                    label=L4("Disc", "Disco", "Disque", "Disco"),
                    front=pliego.Face(None, disc_art()), kinematic="spin" if mode == "spin" else None)
key = [(R + (RCI + CLEAR) * math.cos(2 * math.pi * k / 3),
        R - (RCI + CLEAR) * math.sin(2 * math.pi * k / 3)) for k in range(3)]
disc.hole(key)

# ── programs ──────────────────────────────────────────────────────────────────
if mode == "make":
    steps = [pliego.Step("prism", L4("Fold the axle into a triangular tube and glue the tab",
                                     "Dobla el eje en un tubo triangular y pega la pestaña",
                                     "Plier l'axe en tube triangulaire et coller la languette",
                                     "Dobre o eixo num tubo triangular e cole a aba"),
                         [(m, -120.0) for m in edges], duration_ms=2000),
             pliego.Step("point", L4("Fold the three tip faces in to make the point",
                                     "Dobla hacia dentro las tres caras de la punta",
                                     "Replier les trois faces de la pointe",
                                     "Dobre para dentro as três faces da ponta"),
                         [(m, -TILT) for m in tips], duration_ms=1500)]
    result = pliego.Assembly([axle, disc], controls=[pliego.sequence_control(
        label=L4("Make it", "Armarlo", "Le fabriquer", "Montá-lo"))],
        sequence=pliego.Sequence(steps, mode="kinematic"), title="Paper top")
else:
    glue = pliego.glue("axle-seam", axle, [(3 * W + 1.0, HT + GLUE_W), (3 * W + GLUE_W - 1.0, HT + GLUE_W + 1.0),
                                          (3 * W + GLUE_W - 1.0, HT + L - GLUE_W - 1.0),
                                          (3 * W + 1.0, HT + L - GLUE_W)],
                       axle, (1.0, 0.0, 0.0, 1.0, -3 * W, 0.0), side="back")

    def initial(sheet_id, uv):
        if sheet_id == "axle":
            return axle_world(uv[0], uv[1])
        return (uv[0] - R, DISC_AT, R - uv[1])

    result = pliego.Assembly(
        [axle, disc], joins=[glue], initial=initial,
        mechanisms=[pliego.hinge("spin", (0.0, 0.0, 0.0), (0.0, 1.0, 0.0), "spin", [disc, axle])],
        controls=[pliego.angle_control("spin", L4("Spin", "Girar", "Faire tourner", "Girar"),
                                       default=0.0, min=0.0, max=360.0)],
        title="Paper top")
print(f"paper-top: mode={mode} disc={DIA:g}mm axle={W:g}x{L:g}mm tip={D:.1f}mm "
      f"tilt={TILT:.1f}deg design={design}")
