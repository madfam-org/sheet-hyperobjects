# mountain-fold — the same square, folded the other way: the two halves rotate toward the BACK.
#
# FOLD sign convention: a mountain crease has a NEGATIVE fold angle (valley > 0, mountain < 0).
# A mountain fold is a valley fold made from the back of the sheet, so with kami (red front,
# white back) the white back faces close onto each other and the red front stays outside — the
# opposite of `valley-fold`. One physical step drives the crease to −angle; `target:folded` is
# the kernel's exact face-tree pose of that state.
import pliego


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


def clamp(value, lo, hi):
    return max(lo, min(hi, float(value)))


# Face colours mirror the `appearance` block of each stock card (materials/<slug>/stock.json).
FACES = {
    "kami": ("#d9382b", "#f6f3ec"),
    "foil-paper": ("#c0c4c8", "#f4f1ea"),
    "copy-80": ("#f7f7f2", "#f7f7f2"),
    "tant": ("#2f6fb0", "#2f6fb0"),
}
LINE_LABELS = {
    "diagonal": {"en": "Mountain-fold along the diagonal",
                 "es": "Dobla en montaña por la diagonal",
                 "fr": "Plier en montagne selon la diagonale",
                 "pt": "Dobre em montanha pela diagonal"},
    "book": {"en": "Mountain-fold in half, edge to edge",
             "es": "Dobla en montaña a la mitad, borde con borde",
             "fr": "Plier en montagne en deux, bord contre bord",
             "pt": "Dobre em montanha ao meio, borda com borda"},
}

size = clamp(PARAM(lambda: size, 150.0), 50.0, 300.0)
stock = PARAM(lambda: stock, "kami")
fold_line = PARAM(lambda: fold_line, "diagonal")
angle = clamp(PARAM(lambda: angle, 180.0), 30.0, 180.0)
if stock not in FACES:
    raise ValueError(f"stock {stock!r} is not offered by mountain-fold (choose {sorted(FACES)})")
if fold_line not in LINE_LABELS:
    raise ValueError(f"fold_line {fold_line!r} must be one of {sorted(LINE_LABELS)}")

front, back = FACES[stock]
square = pliego.Sheet("square", pliego.square(size), stock=stock,
                      label={"en": "Square", "es": "Cuadrado", "fr": "Carré", "pt": "Quadrado"},
                      front=front, back=back)
if fold_line == "diagonal":
    a, b = (0.0, 0.0), (size, size)
else:
    a, b = (size / 2.0, 0.0), (size / 2.0, size)
# `angle` is a magnitude; Sheet.mountain() writes it as a negative fold angle.
crease = square.mountain(a, b, angle=angle, label=LINE_LABELS[fold_line])
if crease.fold_angle >= 0:
    raise ValueError("a mountain crease must carry a negative fold angle")

step = pliego.Step("mountain-fold", LINE_LABELS[fold_line], [(crease, None)], duration_ms=1500,
                   note={"en": "The back faces close onto each other; the front stays outside.",
                         "es": "Las caras del reverso se cierran una sobre otra; el frente queda "
                               "por fuera.",
                         "fr": "Les faces du verso se referment l'une sur l'autre ; le recto reste "
                               "à l'extérieur.",
                         "pt": "As faces do verso se fecham uma sobre a outra; a frente fica "
                               "do lado de fora."})
result = pliego.Assembly(
    [square],
    controls=[pliego.sequence_control(label={"en": "Fold program", "es": "Secuencia de pliegues",
                                             "fr": "Séquence de pliage",
                                             "pt": "Sequência de dobras"})],
    sequence=pliego.Sequence([step], mode="physical"),
    targets={"folded": {"angles": {crease: crease.fold_angle}}},
    title="Mountain fold",
)
