# valley-fold — a square folded once toward its front: the first fold of every origami diagram.
#
# One valley crease (FOLD sign convention: positive fold angle = valley, the two halves rotate
# toward the FRONT face). The fold program has one physical step that drives the crease to
# `angle`; the target frame `target:folded` is the kernel's exact face-tree pose of that state.
# With kami (red front, white back) the red faces close onto each other and the white back is
# what you see from outside: that is how you recognise a valley fold.
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
    "diagonal": {"en": "Valley-fold along the diagonal", "es": "Dobla en valle por la diagonal",
                 "fr": "Plier en vallée selon la diagonale", "pt": "Dobre em vale pela diagonal"},
    "book": {"en": "Valley-fold in half, edge to edge",
             "es": "Dobla en valle a la mitad, borde con borde",
             "fr": "Plier en vallée en deux, bord contre bord",
             "pt": "Dobre em vale ao meio, borda com borda"},
}

size = clamp(PARAM(lambda: size, 150.0), 50.0, 300.0)
stock = PARAM(lambda: stock, "kami")
fold_line = PARAM(lambda: fold_line, "diagonal")
angle = clamp(PARAM(lambda: angle, 180.0), 30.0, 180.0)
if stock not in FACES:
    raise ValueError(f"stock {stock!r} is not offered by valley-fold (choose {sorted(FACES)})")
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
crease = square.valley(a, b, angle=angle, label=LINE_LABELS[fold_line])

step = pliego.Step("valley-fold", LINE_LABELS[fold_line], [(crease, None)], duration_ms=1500,
                   note={"en": "The front faces close onto each other; the back stays outside.",
                         "es": "Las caras del frente se cierran una sobre otra; el reverso queda "
                               "por fuera.",
                         "fr": "Les faces avant se referment l'une sur l'autre ; le verso reste "
                               "à l'extérieur.",
                         "pt": "As faces da frente se fecham uma sobre a outra; o verso fica "
                               "do lado de fora."})
result = pliego.Assembly(
    [square],
    controls=[pliego.sequence_control(label={"en": "Fold program", "es": "Secuencia de pliegues",
                                             "fr": "Séquence de pliage",
                                             "pt": "Sequência de dobras"})],
    sequence=pliego.Sequence([step], mode="physical"),
    targets={"folded": {"angles": {crease: angle}}},
    title="Valley fold",
)
