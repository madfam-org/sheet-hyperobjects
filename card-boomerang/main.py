"""Card boomerang — sheet-hyperobjects cartridge (Pliego).

A small indoor boomerang cut from card: three rounded blades 120° apart around a hub, with rounded
inner corners. Its tips are bent up slightly by hand before throwing; a flick on one tip sends it
spinning out and back.

The outline is computed here: each blade is a strip `blade_width` wide whose edges run parallel to
its axis out to a semicircular tip at `blade_length` from the centre; neighbouring blade edges meet
in a fillet arc of radius `fillet`, tangent to both. A small kiss-cut ring marks the centre, and an
arrow on the printed face shows the direction of spin.

The preview shows the shape and turns it about its centre on the `spin` control (a `rotate`
mechanism). The flight (lift on the spinning blades, gyroscopic precession that curves the path
back) needs the engine's air model (wave 3); the slight bend of the tips is done by hand and is the
engine's to bend, so the cut file has no fold lines.
"""

import math

import pliego


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


blade_length = float(PARAM(lambda: blade_length, 70.0))   # noqa: F821
blade_width = float(PARAM(lambda: blade_width, 22.0))     # noqa: F821
fillet = float(PARAM(lambda: fillet, 6.0))                # noqa: F821
colour = PARAM(lambda: colour, "#2e86ab")                 # noqa: F821
stock = PARAM(lambda: stock, "cardstock-300")             # noqa: F821

if stock not in ("cardstock-300", "cardstock-250", "pp-300"):
    raise ValueError(f"card-boomerang: unknown stock {stock!r}")
if not (isinstance(colour, str) and len(colour) == 7 and colour[0] == "#"):
    raise ValueError(f"card-boomerang: colour must be #rrggbb, got {colour!r}")
W = pliego.clamp(blade_width, 12.0, 40.0)
LB = pliego.clamp(blade_length, 2.0 * W, 6.0 * W)
F = pliego.clamp(fillet, 2.0, 0.6 * W)
SEG = 16
C = LB + 2.0                                  # the centre, in sheet coordinates


def L4(en, es, fr, pt):
    return {"en": en, "es": es, "fr": fr, "pt": pt}


def outline():
    pts = []
    for k in range(3):
        th = math.radians(90.0 + 120.0 * k)
        ax, ay = math.cos(th), math.sin(th)              # blade axis
        nx, ny = -ay, ax                                 # its left normal
        tip = LB - W / 2                                 # centre of the tip's semicircle
        # right edge going out, the tip arc, the left edge coming back
        for i in range(SEG + 1):
            a = -math.pi / 2 + math.pi * i / SEG
            pts.append((C + ax * tip + W / 2 * (math.cos(a) * ax + math.sin(a) * nx),
                        C + ay * tip + W / 2 * (math.cos(a) * ay + math.sin(a) * ny)))
        # fillet between this blade's left edge and the next blade's right edge
        bis = th + math.radians(60.0)
        d = (W / 2 + F) / math.sin(math.radians(60.0))   # fillet centre from the hub centre
        fx, fy = C + d * math.cos(bis), C + d * math.sin(bis)
        # tangent points: the foot of the fillet centre on each edge line
        t0 = ((fx - C) * ax + (fy - C) * ay)
        p0 = (C + ax * t0 + nx * W / 2, C + ay * t0 + ny * W / 2)
        th2 = th + math.radians(120.0)
        bx, by = math.cos(th2), math.sin(th2)
        mx, my = -by, bx
        t1 = ((fx - C) * bx + (fy - C) * by)
        p1 = (C + bx * t1 - mx * W / 2, C + by * t1 - my * W / 2)
        a_0, a_1 = math.atan2(p0[1] - fy, p0[0] - fx), math.atan2(p1[1] - fy, p1[0] - fx)
        if a_1 > a_0:
            a_1 -= 2 * math.pi                            # clockwise round the fillet
        pts.pop()                                         # the left edge ends at p0
        for i in range(SEG + 1):
            a = a_0 + (a_1 - a_0) * i / SEG
            pts.append((fx + F * math.cos(a), fy + F * math.sin(a)))
    return pts


ring = outline()


xs, ys = [p[0] for p in ring], [p[1] for p in ring]
U0, V1 = min(xs), max(ys)            # the art covers the outline's bounding box


def art():
    """Printed face: the colour, a band along each blade and a spin arrow round the hub."""
    s = V1                           # image y = V1 − sheet y, image x = sheet x − U0
    out = [f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='{U0:.2f} 0 {max(xs) - U0:.2f} "
           f"{V1 - min(ys):.2f}'>",
           "<polygon points='" + " ".join(f"{x:.2f},{s - y:.2f}" for x, y in ring)
           + f"' fill='{colour}'/>"]
    for k in range(3):
        th = math.radians(90.0 + 120.0 * k)
        x0, y0 = C + math.cos(th) * W * 0.9, s - (C + math.sin(th) * W * 0.9)
        x1, y1 = C + math.cos(th) * (LB - W * 0.6), s - (C + math.sin(th) * (LB - W * 0.6))
        out.append(f"<line x1='{x0:.2f}' y1='{y0:.2f}' x2='{x1:.2f}' y2='{y1:.2f}' "
                   f"stroke='#fdfaf3' stroke-width='{W * 0.18:.2f}' stroke-linecap='round'/>")
    r, yc = W * 0.55, s - C
    arc = [(C + r * math.cos(math.radians(a)), yc - r * math.sin(math.radians(a)))
           for a in range(-40, 230, 10)]
    tx, ty = arc[-1]
    out.append("<polyline points='" + " ".join(f"{x:.2f},{y:.2f}" for x, y in arc)
               + f"' fill='none' stroke='#fdfaf3' stroke-width='{W * 0.08:.2f}'/>"
               f"<circle cx='{tx:.2f}' cy='{ty:.2f}' r='{W * 0.1:.2f}' fill='#fdfaf3'/>")
    svg = "".join(out) + "</svg>"
    for a, b in (("%", "%25"), ("#", "%23"), ("<", "%3C"), (">", "%3E"), (" ", "%20"),
                 ("'", "%27")):
        svg = svg.replace(a, b)
    return "data:image/svg+xml;charset=utf-8," + svg


if min(xs) < 0 or min(ys) < 0:
    raise ValueError("card-boomerang: the outline leaves the sheet frame")
board = pliego.Sheet("boomerang", ring, stock=stock, grain_deg=90.0,
                     label=L4("Boomerang", "Bumerán", "Boomerang", "Bumerangue"),
                     front=pliego.Face(None, art()), kinematic="spin",
                     placement=pliego.Placement(origin=(-C, 0.0, C)))
mark = pliego.circle((C, C), 3.0, 24)
board.halfcut(mark + [mark[0]], name="centre-mark")
print(f"card-boomerang: blades=3 length={LB:g}mm width={W:g}mm fillet={F:g}mm "
      f"span={max(xs) - min(xs):.1f}x{max(ys) - min(ys):.1f}mm")
result = pliego.Assembly(
    [board], mechanisms=[pliego.rotate("spin", (board, (C, C)), "spin", [board])],
    controls=[pliego.angle_control("spin", L4("Spin", "Girar", "Faire tourner", "Girar"),
                                   default=0.0, min=0.0, max=360.0)],
    title="Card boomerang")
