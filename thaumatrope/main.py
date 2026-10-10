"""Thaumatrope — sheet-hyperobjects cartridge (Pliego).

A card disc with a different picture on each side and a string through each side of a diameter.
Twirling the strings flips the disc fast about that diameter, and the two pictures merge into one
(a bird appears inside its cage). The pictures here are original drawings, made of simple paths
in this script and printed as the disc's art: the front picture as seen from the front, the back
one upside down, so that it stands upright when the disc flips about the horizontal string axis.

Designs: `bird-cage` (a bird and a cage), `fish-bowl` (a fish and a bowl), `flower-pot` (a flower
and a pot). The flip is a `hinge` mechanism about the string axis (through the two string holes) on
the `flip` control. The merging of the pictures happens in the eye when the disc turns many times
a second; the preview turns it as fast as the control is moved.
"""

import math

import pliego


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


diameter = float(PARAM(lambda: diameter, 90.0))        # noqa: F821
design = PARAM(lambda: design, "bird-cage")            # noqa: F821
stock = PARAM(lambda: stock, "cardstock-250")          # noqa: F821

if design not in ("bird-cage", "fish-bowl", "flower-pot"):
    raise ValueError(f"thaumatrope: unknown design {design!r}")
if stock not in ("cardstock-250", "cardstock-300", "cardstock-160"):
    raise ValueError(f"thaumatrope: unknown stock {stock!r}")
DIA = pliego.clamp(diameter, 50.0, 200.0)
R = DIA / 2.0
HOLE = 3.0                     # string hole diameter (mm)
HOLE_IN = max(5.0, 0.08 * DIA) # hole centre from the rim
LIFT = R + 40.0                # the disc hangs at this height


def L4(en, es, fr, pt):
    return {"en": en, "es": es, "fr": fr, "pt": pt}


# ── the pictures: path drawings in a unit frame (x right, y up, the disc's radius = 1) ──

INK = "#1d1d1f"


def stroke(d, w=0.05, fill="none"):
    return (f"<path d='{d}' fill='{fill}' stroke='{INK}' stroke-width='{w}' "
            "stroke-linecap='round' stroke-linejoin='round'/>")


def bird():
    return "<g transform='scale(0.75) translate(0.05,0.05)'>" + "".join([
        stroke("M-0.45,-0.05 C-0.45,0.25 0.1,0.3 0.2,0.1 C0.3,-0.1 0.05,-0.3 -0.2,-0.25 "
               "C-0.35,-0.22 -0.45,-0.15 -0.45,-0.05 Z", fill="#f3a712"),            # body
        stroke("M0.12,0.18 C0.12,0.42 0.42,0.42 0.42,0.2 C0.42,0.02 0.14,0.02 0.12,0.18 Z",
               fill="#f3a712"),                                                     # head
        stroke("M0.42,0.25 L0.58,0.2 L0.42,0.14 Z", fill="#e4572e"),               # beak
        "<circle cx='0.3' cy='0.26' r='0.035' fill='#1d1d1f'/>",                   # eye
        stroke("M-0.4,0.0 C-0.25,0.15 -0.05,0.12 0.05,0.0"),                        # wing
        stroke("M-0.45,-0.05 L-0.72,0.08 L-0.68,-0.12 Z", fill="#e4572e"),         # tail
        stroke("M-0.1,-0.26 L-0.12,-0.42 M0.05,-0.26 L0.05,-0.42"),                 # legs
        stroke("M-0.45,-0.42 L0.45,-0.42", 0.06),                                   # perch
    ]) + "</g>"


def cage():
    bars = "".join(stroke(f"M{x:.2f},-0.6 L{x:.2f},{0.25 + 0.4 * math.sqrt(max(0.0, 1 - (x / 0.62) ** 2)):.3f}", 0.035)
                   for x in (-0.48, -0.32, -0.16, 0.0, 0.16, 0.32, 0.48))
    return "".join([
        bars,
        stroke("M-0.62,0.25 C-0.62,0.9 0.62,0.9 0.62,0.25", 0.05),                  # dome
        stroke("M-0.65,-0.6 L0.65,-0.6 L0.6,-0.7 L-0.6,-0.7 Z", 0.05, "#2e86ab"),  # base
        stroke("M0,0.67 C-0.12,0.67 -0.12,0.85 0,0.85 C0.12,0.85 0.12,0.67 0,0.67", 0.045),
    ])


def fish():
    return "".join([
        stroke("M-0.4,0.0 C-0.2,0.28 0.25,0.28 0.38,0.0 C0.25,-0.28 -0.2,-0.28 -0.4,0.0 Z",
               fill="#e4572e"),
        stroke("M-0.4,0.0 L-0.62,0.18 L-0.58,0.0 L-0.62,-0.18 Z", fill="#f3a712"),
        "<circle cx='0.22' cy='0.06' r='0.035' fill='#1d1d1f'/>",
        stroke("M0.05,0.2 C0.0,0.05 0.0,-0.05 0.05,-0.2"),
        "<circle cx='0.5' cy='0.25' r='0.04' fill='none' stroke='#2e86ab' stroke-width='0.03'/>",
        "<circle cx='0.56' cy='0.4' r='0.03' fill='none' stroke='#2e86ab' stroke-width='0.03'/>",
    ])


def bowl():
    return "".join([
        stroke("M-0.55,0.35 C-0.85,-0.1 -0.6,-0.62 0,-0.62 C0.6,-0.62 0.85,-0.1 0.55,0.35",
               0.05),
        stroke("M-0.62,0.18 C-0.3,0.26 0.3,0.1 0.62,0.18", 0.04),                   # water line
        stroke("M-0.55,0.35 C-0.3,0.42 0.3,0.42 0.55,0.35", 0.04),
        stroke("M-0.35,-0.62 L0.35,-0.62 L0.3,-0.72 L-0.3,-0.72 Z", 0.04, "#4c9f70"),
        stroke("M-0.2,-0.55 C-0.25,-0.4 -0.15,-0.3 -0.22,-0.15", 0.035),            # weed
    ])


def flower():
    petals = "".join(f"<ellipse cx='0' cy='0.42' rx='0.07' ry='0.14' fill='#a23b72' "
                     f"stroke='{INK}' stroke-width='0.03' transform='rotate({a} 0 0.28)'/>"
                     for a in range(0, 360, 45))
    return "".join([
        stroke("M0,0.14 C0.02,-0.1 -0.02,-0.3 0,-0.45", 0.05),
        stroke("M0,-0.2 C0.15,-0.12 0.25,-0.2 0.3,-0.3 C0.15,-0.3 0.05,-0.28 0,-0.2 Z",
               fill="#4c9f70"),
        petals,
        "<circle cx='0' cy='0.28' r='0.08' fill='#f3a712' stroke='#1d1d1f' stroke-width='0.03'/>",
    ])


def pot():
    return "".join([
        stroke("M-0.35,-0.45 L0.35,-0.45 L0.25,-0.8 L-0.25,-0.8 Z", 0.05, "#b5651d"),
        stroke("M-0.42,-0.45 L0.42,-0.45 L0.42,-0.36 L-0.42,-0.36 Z", 0.05, "#b5651d"),
        stroke("M-0.3,-0.36 C-0.1,-0.3 0.1,-0.3 0.3,-0.36", 0.035),                 # soil
    ])


PICTURES = {"bird-cage": (bird, cage), "fish-bowl": (fish, bowl), "flower-pot": (flower, pot)}


def art(draw, upside_down):
    """The disc's art over its bounding box (2R × 2R): unit frame → image (y down)."""
    turn = " rotate(180)" if upside_down else ""
    svg = (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {DIA:.2f} {DIA:.2f}'>"
           f"<rect width='{DIA:.2f}' height='{DIA:.2f}' fill='#fdfaf3'/>"
           f"<g transform='translate({R:.2f},{R:.2f}) scale({0.82 * R:.3f},{-0.82 * R:.3f}){turn}'>"
           f"{draw()}</g></svg>")
    for a, b in (("%", "%25"), ("#", "%23"), ("<", "%3C"), (">", "%3E"), (" ", "%20"),
                 ("'", "%27")):
        svg = svg.replace(a, b)
    return "data:image/svg+xml;charset=utf-8," + svg


front_draw, back_draw = PICTURES[design]
h = 0.5 ** 0.5
disc = pliego.Sheet("disc", pliego.circle((R, R), R, 96), stock=stock, grain_deg=90.0,
                    label=L4("Disc", "Disco", "Disque", "Disco"),
                    front=pliego.Face(None, art(front_draw, False)),
                    back=pliego.Face(None, art(back_draw, True)), kinematic="flip",
                    placement=pliego.Placement(origin=(-R, LIFT - R, 0.0), rotation=(h, 0.0, 0.0, h)))
for x in (HOLE_IN, DIA - HOLE_IN):
    disc.hole(pliego.circle((x, R), HOLE / 2.0, 16))
flip = pliego.hinge("flip", (0.0, LIFT, 0.0), (1.0, 0.0, 0.0), "flip", [disc])
controls = [pliego.angle_control("flip", L4("Flip the disc", "Girar el disco",
                                            "Faire tourner le disque", "Girar o disco"),
                                 default=0.0, min=0.0, max=360.0)]
print(f"thaumatrope: design={design} diameter={DIA:g}mm holes={HOLE:g}mm at {HOLE_IN:g}mm")
result = pliego.Assembly([disc], mechanisms=[flip], controls=controls, title="Thaumatrope")
