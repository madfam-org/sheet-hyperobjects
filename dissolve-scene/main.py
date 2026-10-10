"""Dissolve scene (venetian-blind picture change) — sheet-hyperobjects cartridge (Pliego).

A window in a frame filled with `slats` louvres. Each slat carries one band of picture A on its
front and the matching band of picture B on its back; turning every slat half a turn about its own
centre line, together, changes the scene from A to B, like the slats of a venetian blind.

Each slat is a kinematic board turned by its own `hinge` mechanism about its centre line, and every
hinge reads the same `change` angle control (0° picture A, 180° picture B). The slats are as wide
as the pitch less a 0.6 mm gap, so neighbours, which stay parallel at every angle, never collide.
A narrow tongue at each end of a slat, on its axis, runs 8 mm under the frame: that is where the
slat is held (a thread or wire axle, or a pocket behind the frame). The pivots and the linkage
that turns all slats together (a strip tied to one edge of every slat, like a blind's cord) are not
sheets or joins of the document: they are what the shared hinge axes and the one control stand
for, so the preview can drive the change.
"""

import math

import pliego


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


slats = int(round(float(PARAM(lambda: slats, 9))))           # noqa: F821
direction = PARAM(lambda: direction, "horizontal")           # noqa: F821
window_width = float(PARAM(lambda: window_width, 120.0))     # noqa: F821
window_height = float(PARAM(lambda: window_height, 90.0))    # noqa: F821
frame_margin = float(PARAM(lambda: frame_margin, 25.0))      # noqa: F821
picture_a = PARAM(lambda: picture_a, "#2b3f6b")              # noqa: F821
picture_b = PARAM(lambda: picture_b, "#e8b7b0")              # noqa: F821

if direction not in ("horizontal", "vertical"):
    raise ValueError(f"dissolve-scene: unknown slat direction {direction!r}")
PALETTE = ("#f7f5ef", "#efe3c8", "#b98a5a", "#b23a3a", "#2f6b4f", "#2b3f6b", "#e8b7b0",
           "#3a3a3a")
if picture_a not in PALETTE or picture_b not in PALETTE:
    raise ValueError("dissolve-scene: picture colours must come from the palette")

n = int(pliego.clamp(slats, 3, 24))
ww = pliego.clamp(window_width, 40.0, 260.0)
wh = pliego.clamp(window_height, 40.0, 260.0)
m = pliego.clamp(frame_margin, 15.0, 60.0)
GAP = 0.6               # between neighbouring slats
CLEAR = 0.5             # between a slat's end and the window's edge
TONGUE = 8.0            # how far the axle tongue runs under the frame
TONGUE_W = 4.0          # width of the tongue
LIFT = 0.3              # the frame lies this far in front of the slats
FRAME_STOCK, SLAT_STOCK = "cardstock-300", "cardstock-250"


def L4(en, es, fr, pt):
    return {"en": en, "es": es, "fr": fr, "pt": pt}


W, H = ww + 2 * m, wh + 2 * m
wx0, wy0 = m, m
# slats run along u; they are stacked across the other direction of the window
run, across = (ww, wh) if direction == "horizontal" else (wh, ww)
pitch = across / n
sw = pitch - GAP
if sw < 4.0:
    raise ValueError(f"dissolve-scene: {n} slats in {across:g} mm are {sw:.2f} mm wide; use fewer "
                     "slats or a bigger window (minimum 4 mm)")
if TONGUE_W > sw - 1.0:
    tongue_w = max(1.5, sw - 1.0)
else:
    tongue_w = TONGUE_W
if TONGUE > m - 4.0:
    raise ValueError("dissolve-scene: the frame margin is too narrow to hold the slats' tongues")
body = run - 2 * CLEAR


def quat_y(deg):
    h = math.radians(deg) / 2.0
    return (0.0, math.sin(h), 0.0, math.cos(h))


frame = pliego.Sheet("frame", [(0, 0), (W, 0), (W, H), (0, H)], stock=FRAME_STOCK,
                     grain_deg=90.0, label=L4("Frame", "Marco", "Cadre", "Moldura"),
                     placement=pliego.Placement(origin=(0.0, LIFT, 0.0)))
frame.hole([(wx0, wy0), (wx0 + ww, wy0), (wx0 + ww, wy0 + wh), (wx0, wy0 + wh)])
frame.label_edge("window", (wx0, wy0), (wx0 + ww, wy0))

sheets, mechanisms = [frame], []
c0, c1 = sw / 2.0 - tongue_w / 2.0, sw / 2.0 + tongue_w / 2.0
outline = [(0.0, c0), (TONGUE, c0), (TONGUE, 0.0), (TONGUE + body, 0.0), (TONGUE + body, c0),
           (2 * TONGUE + body, c0), (2 * TONGUE + body, c1), (TONGUE + body, c1),
           (TONGUE + body, sw), (TONGUE, sw), (TONGUE, c1), (0.0, c1)]
for k in range(n):
    sid = f"slat-{k + 1}"
    off = k * pitch + GAP / 2.0                   # the slat's lower (or left) edge in the window
    if direction == "horizontal":
        # local (u, v) → page (wx0 + CLEAR − TONGUE + u, wy0 + off + v)
        tx, ty = wx0 + CLEAR - TONGUE, wy0 + off
        pl = pliego.Placement(origin=(tx, 0.0, -ty))
        a0 = (wx0, 0.0, -(ty + sw / 2.0))
        a1 = (wx0 + ww, 0.0, -(ty + sw / 2.0))
    else:
        # local (u, v) → page (wx0 + off + sw − v, wy0 + CLEAR − TONGUE + u): a quarter turn
        tx, ty = wx0 + off + sw, wy0 + CLEAR - TONGUE
        pl = pliego.Placement(origin=(tx, 0.0, -ty), rotation=quat_y(90.0))
        a0 = (wx0 + off + sw / 2.0, 0.0, -wy0)
        a1 = (wx0 + off + sw / 2.0, 0.0, -(wy0 + wh))
    sh = pliego.Sheet(sid, outline, stock=SLAT_STOCK, grain_deg=0.0,
                      label=L4(f"Slat {k + 1}", f"Lama {k + 1}", f"Lamelle {k + 1}",
                               f"Lâmina {k + 1}"),
                      front=picture_a, back=picture_b, placement=pl, kinematic="turn-" + sid)
    sh.label_edge("axle", (0.0, c0), (0.0, c1))
    mechanisms.append(pliego.hinge("turn-" + sid, a0, (a1[0] - a0[0], 0.0, a1[2] - a0[2]),
                                   "change", [sh], rest=0.0))
    sheets.append(sh)

controls = [pliego.angle_control("change", L4("Change the picture", "Cambiar la imagen",
                                               "Changer l'image", "Trocar a imagem"),
                                 default=120.0, min=0.0, max=180.0)]
print(f"dissolve: slats={n} direction={direction} slat={body:.1f}x{sw:.2f}mm pitch={pitch:.2f}mm "
      f"frame={W:g}x{H:g}mm")

result = pliego.Assembly(sheets, mechanisms=mechanisms, controls=controls, title="Dissolve scene")
