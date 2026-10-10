# pleat-and-crimp — mountain/valley pairs, on a single layer (pleat) or through a strip already
# folded in half (crimp).
#
# Each pair is a valley line and a mountain line that cross the reference edge `pleat_width`
# apart: the bottom edge for a pleat, the centre fold for a crimp. Folding a pair flat reflects
# the far part of the strip across the first line and then across the second. Two parallel lines
# (`turn` = 0) compose to a translation: the far part slides back by twice their distance, and a
# `tilt` shifts it sideways as well. Two lines `turn`/2 degrees apart compose to a rotation by
# `turn` degrees: the strip turns, as a crimped neck or leg does.
#
# Crimp: the strip is first valley-folded along its centre line, then pleated through both
# layers. In the flat crease pattern each pleat line becomes a chevron mirrored about the centre
# line, and the centre segment between the two lines of a pair reverses to a mountain. Every
# vertex on the centre line is a degree-4 vertex with sector angles φ, 180−φ, 180−φ, φ
# (Kawasaki holds for any φ) and three creases of one kind (Maekawa). The script checks local
# flat-foldability with pliego.flatfold before it returns, and fails loud otherwise.
import math

import pliego


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


def clamp(value, lo, hi):
    return max(lo, min(hi, float(value)))


FACES = {  # the `appearance` block of each stock card (materials/<slug>/stock.json)
    "kami": ("#d9382b", "#f6f3ec"),
    "copy-80": ("#f7f7f2", "#f7f7f2"),
    "kraft-120": ("#b98a5a", "#b98a5a"),
}
L4 = ("en", "es", "fr", "pt")


def i18n(*texts):
    return dict(zip(L4, texts, strict=True))


technique = PARAM(lambda: technique, "pleat")
length = clamp(PARAM(lambda: length, 200.0), 120.0, 400.0)
width = clamp(PARAM(lambda: width, 80.0), 40.0, 150.0)
pleat_width = clamp(PARAM(lambda: pleat_width, 15.0), 5.0, 30.0)
pleats = int(clamp(PARAM(lambda: pleats, 1), 1, 4))
tilt = clamp(PARAM(lambda: tilt, 0.0), 0.0, 30.0)
turn = clamp(PARAM(lambda: turn, 0.0), 0.0, 30.0)
stock = PARAM(lambda: stock, "kami")
if technique not in ("pleat", "crimp"):
    raise ValueError(f"technique {technique!r} must be 'pleat' or 'crimp'")
if stock not in FACES:
    raise ValueError(f"stock {stock!r} is not offered by pleat-and-crimp (choose {sorted(FACES)})")
# Fit (the manifest's error constraint): with every line tilted at most 45° (tilt + turn/2), a
# line runs at most one strip width sideways, so a pitch of pleat_width + width between pairs
# keeps every line inside the strip and no two lines crossing.
if length < (pleats + 1) * (pleat_width + width):
    raise ValueError(f"{pleats} pleat(s) of {pleat_width} mm do not fit on a {length} mm strip "
                     f"{width} mm wide: need length >= (pleats + 1) * (pleat_width + width)")

front, back = FACES[stock]
strip = pliego.Sheet("strip", pliego.rectangle(length, width), stock=stock,
                     label=i18n("Strip", "Tira", "Bande", "Tira"), front=front, back=back)
# (offset along the reference edge, kind, horizontal run per mm of height) for the two lines
LINES = ((-pleat_width / 2.0, "valley", math.tan(math.radians(tilt))),
         (pleat_width / 2.0, "mountain", math.tan(math.radians(tilt + turn / 2.0))))
centres = [length * k / (pleats + 1) for k in range(1, pleats + 1)]
mid = width / 2.0

steps = []
flat_angles = {}
if technique == "pleat":
    for k, x in enumerate(centres, start=1):
        pair = []
        for dx, kind, run in LINES:
            x0 = x + dx
            m = strip.crease((x0, 0.0), (x0 + run * width, width), kind, 180.0)
            pair.append(m)
            flat_angles[m] = m.fold_angle
        steps.append(pliego.Step(
            f"pleat-{k}",
            i18n(f"Pleat {k}: valley, then mountain", f"Pliegue escalonado {k}: valle y montaña",
                 f"Pli escalier {k} : vallée puis montagne", f"Prega {k}: vale e montanha"),
            [(m, None) for m in pair], duration_ms=2000))
else:
    xs = [0.0]
    for x in centres:
        xs += [x + LINES[0][0], x + LINES[1][0]]
    xs.append(length)
    spine = []
    for j in range(len(xs) - 1):
        inside = j % 2 == 1                      # between the two lines of a pair
        m = strip.crease((xs[j], mid), (xs[j + 1], mid), "mountain" if inside else "valley",
                         180.0)
        spine.append((m, inside))
        flat_angles[m] = m.fold_angle
    pairs = []
    for x in centres:
        pair = []
        for dx, kind, run in LINES:
            x0 = x + dx
            for y_end in (width, 0.0):           # the chevron: one leg up, its mirror down
                m = strip.crease((x0, mid), (x0 + run * mid, y_end), kind, 180.0)
                pair.append(m)
                flat_angles[m] = m.fold_angle
        pairs.append(pair)
    steps.append(pliego.Step(
        "fold-in-half",
        i18n("Valley-fold the strip in half lengthwise", "Dobla la tira a la mitad, a lo largo",
             "Plier la bande en deux dans la longueur", "Dobre a tira ao meio, no comprimento"),
        [(m, 180.0) for m, _ in spine], duration_ms=1500))
    steps.append(pliego.Step(
        "open-slightly",
        i18n("Open it to a right angle", "Ábrela hasta formar un ángulo recto",
             "L'ouvrir à angle droit", "Abra até formar um ângulo reto"),
        [(m, 90.0) for m, _ in spine], duration_ms=1000))
    for k, pair in enumerate(pairs, start=1):
        reversed_segment = [m for m, inside in spine if inside][k - 1]
        steps.append(pliego.Step(
            f"crimp-{k}",
            i18n(f"Crimp {k}: pleat through both layers", f"Crimp {k}: pliegue escalonado a "
                 "través de las dos capas", f"Crimp {k} : pli escalier à travers les deux "
                 "couches", f"Crimp {k}: prega através das duas camadas"),
            [(m, None) for m in pair] + [(reversed_segment, None)], duration_ms=2500,
            note=i18n("The centre fold reverses between the two lines.",
                      "El doblez central se invierte entre las dos líneas.",
                      "Le pli central s'inverse entre les deux lignes.",
                      "A dobra central se inverte entre as duas linhas.")))
    steps.append(pliego.Step(
        "close",
        i18n("Close the strip flat", "Cierra la tira y aplánala", "Refermer la bande à plat",
             "Feche a tira e achate-a"),
        [(m, None) for m, inside in spine if not inside], duration_ms=1500))

arrangement = strip.build()
if not pliego.flatfold.is_flat_foldable(arrangement):
    _, issues = pliego.flatfold.check(arrangement)
    raise ValueError(f"generated crease pattern is not flat-foldable: {issues[:3]}")

result = pliego.Assembly(
    [strip],
    controls=[pliego.sequence_control(label=i18n("Fold program", "Secuencia de pliegues",
                                                 "Séquence de pliage", "Sequência de dobras"))],
    sequence=pliego.Sequence(steps, mode="physical"),
    targets={"flat-folded": {"angles": flat_angles}},
    title="Pleat and crimp",
)
