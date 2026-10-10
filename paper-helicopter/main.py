"""Paper helicopter — sheet-hyperobjects cartridge (Pliego).

The classic falling spinner (also called a whirlybird or rotocopter). One strip: the top is split
down the middle into two blades; below them a waist the full width; below that a narrow body, its
corners cut away, whose bottom folds up as a weight. The blades fold out in opposite directions, so
that when it falls, the air pushes them round and it spins down slowly (autorotation).

* `blade_length` — length of each blade (the central cut).
* `pitch` — the blades' tilt above the horizontal once folded out (the fold is 90° − pitch), the
  angle the air meets them at.

The fold program makes it: fold one blade forward, the other back, fold the weight up. The spin is a
`hinge` mechanism about the body's vertical axis on the `spin` control, a kinematic illustration.
The real descent and autorotation (the blades' lift and drag, the spin rate, the slow fall) need
the engine's air model (wave 3).
"""

import pliego


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


blade_length = float(PARAM(lambda: blade_length, 80.0))    # noqa: F821
pitch = float(PARAM(lambda: pitch, 12.0))                  # noqa: F821
width = float(PARAM(lambda: width, 60.0))                  # noqa: F821
body_length = float(PARAM(lambda: body_length, 70.0))      # noqa: F821
stock = PARAM(lambda: stock, "copy-80")                    # noqa: F821

if stock not in ("copy-80", "kami", "kraft-120"):
    raise ValueError(f"paper-helicopter: unknown stock {stock!r}")
W = pliego.clamp(width, 30.0, 120.0)
LB = pliego.clamp(blade_length, 0.8 * W, 3.0 * W)
PITCH = pliego.clamp(pitch, 0.0, 30.0)
LBODY = pliego.clamp(body_length, 0.6 * W, 2.0 * W)
WAIST = 0.25 * W                       # full-width band between the blades and the body
WEIGHT = 0.2 * LBODY                   # the weight tab folded up at the bottom of the body
x0, x1 = W / 3.0, 2.0 * W / 3.0        # the narrow body
yc, yb = LBODY, LBODY + WAIST          # body top, blade fold
H = yb + LB
LIFT = 20.0                            # hangs this far above the ground


def L4(en, es, fr, pt):
    return {"en": en, "es": es, "fr": fr, "pt": pt}


outline = [(x0, 0.0), (x1, 0.0), (x1, yc), (W, yc), (W, H), (0.0, H), (0.0, yc), (x0, yc)]
# upright: the sheet's front faces +z, the body's centre line on the world y-axis
h = 0.5 ** 0.5
sheet = pliego.Sheet("strip", outline, stock=stock, grain_deg=90.0,
                     label=L4("Helicopter strip", "Tira del helicóptero",
                              "Bande de l'hélicoptère", "Tira do helicóptero"),
                     front="#2e86ab", back="#f3a712", kinematic="spin",
                     placement=pliego.Placement(origin=(-W / 2, LIFT, 0.0),
                                                rotation=(h, 0.0, 0.0, h)))
sheet.cut([(W / 2, H), (W / 2, yb)], name="rotor-cut")
fold = 90.0 - PITCH
left = sheet.valley((0.0, yb), (W / 2, yb), fold, name="blade-fold",
                    label=L4("Fold this blade towards you", "Dobla esta aspa hacia ti",
                             "Plier cette pale vers soi", "Dobre esta pá para a frente"))
right = sheet.mountain((W / 2, yb), (W, yb), fold, name="blade-fold",
                       label=L4("Fold this blade away", "Dobla esta aspa hacia atrás",
                                "Plier cette pale vers l'arrière", "Dobre esta pá para trás"))
weight = sheet.valley((x0, WEIGHT), (x1, WEIGHT), 180.0, name="weight-fold")

steps = [
    pliego.Step("blade-front", L4("Fold the left blade towards you",
                                  "Dobla el aspa izquierda hacia ti",
                                  "Plier la pale gauche vers soi",
                                  "Dobre a pá esquerda para a frente"), [(left, fold)],
                duration_ms=1200),
    pliego.Step("blade-back", L4("Fold the right blade away from you",
                                 "Dobla el aspa derecha hacia atrás",
                                 "Plier la pale droite vers l'arrière",
                                 "Dobre a pá direita para trás"), [(right, -fold)],
                duration_ms=1200),
    pliego.Step("weight", L4("Fold the bottom up: the weight", "Dobla la base hacia arriba: el lastre",
                             "Replier le bas vers le haut : le lest",
                             "Dobre a base para cima: o lastro"), [(weight, 180.0)],
                duration_ms=1200),
]
spin = pliego.hinge("spin", (0.0, 0.0, 0.0), (0.0, 1.0, 0.0), "spin", [sheet])
controls = [pliego.sequence_control(label=L4("Make it", "Armarlo", "Le fabriquer", "Montá-lo")),
            pliego.angle_control("spin", L4("Spin (illustration)", "Girar (ilustración)",
                                            "Tourner (illustration)", "Girar (ilustração)"),
                                 default=0.0, min=0.0, max=360.0)]
print(f"paper-helicopter: width={W:g}mm blades={LB:g}mm pitch={PITCH:g}deg body={LBODY:g}mm "
      f"strip={W:g}x{H:g}mm")
result = pliego.Assembly([sheet], mechanisms=[spin], controls=controls,
                         sequence=pliego.Sequence(steps, mode="kinematic"),
                         title="Paper helicopter")
