# crease-and-unfold — fold a line flat, press it, open it again: the paper remembers.
#
# Each crease gets four physical steps: fold it to 180° (valley), press it for `hold` seconds, let
# go (RELEASE: the hinge loses its target and relaxes toward its plastic rest angle, which moved
# while the crease was held beyond the stock's yield angle — crease_yield_deg, crease_set_rate in
# the document's stock snapshot — so it opens only a little), then unfold it flat by hand (target
# 0°, held while the next crease is made). A last step lets go of every crease: each relaxes to
# its rest angle and stands open. That rest angle is the crease memory: the sheet does not return
# flat. Origami calls this "crease and unfold", the precreasing move.
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
    "copy-80": ("#f7f7f2", "#f7f7f2"),
    "foil-paper": ("#c0c4c8", "#f4f1ea"),
    "washi-kozo-30": ("#f3eee2", "#f3eee2"),
}
NAMES = {
    "diagonal": ("the diagonal", "la diagonal", "la diagonale", "a diagonal"),
    "other-diagonal": ("the other diagonal", "la otra diagonal", "l'autre diagonale",
                       "a outra diagonal"),
    "vertical": ("in half, left to right", "a la mitad, de izquierda a derecha",
                 "en deux, de gauche à droite", "ao meio, da esquerda para a direita"),
    "horizontal": ("in half, bottom to top", "a la mitad, de abajo hacia arriba",
                   "en deux, de bas en haut", "ao meio, de baixo para cima"),
}
SETS = {
    "one": ("diagonal",),
    "diagonals": ("diagonal", "other-diagonal"),
    "star": ("diagonal", "other-diagonal", "vertical", "horizontal"),
}

size = clamp(PARAM(lambda: size, 150.0), 50.0, 300.0)
stock = PARAM(lambda: stock, "kami")
creases = PARAM(lambda: creases, "one")
hold = clamp(PARAM(lambda: hold, 2.0), 0.5, 10.0)
if stock not in FACES:
    raise ValueError(f"stock {stock!r} is not offered by crease-and-unfold (choose "
                     f"{sorted(FACES)})")
if creases not in SETS:
    raise ValueError(f"creases {creases!r} must be one of {sorted(SETS)}")

s = size
ENDS = {
    "diagonal": ((0.0, 0.0), (s, s)),
    "other-diagonal": ((s, 0.0), (0.0, s)),
    "vertical": ((s / 2.0, 0.0), (s / 2.0, s)),
    "horizontal": ((0.0, s / 2.0), (s, s / 2.0)),
}
front, back = FACES[stock]
square = pliego.Sheet("square", pliego.square(size), stock=stock,
                      label={"en": "Square", "es": "Cuadrado", "fr": "Carré", "pt": "Quadrado"},
                      front=front, back=back)

steps = []
marks = []
first = None
for key in SETS[creases]:
    en, es, fr, pt = NAMES[key]
    a, b = ENDS[key]
    mark = square.valley(a, b, angle=180.0,
                         label={"en": f"Crease {en}", "es": f"Pliegue por {es}",
                                "fr": f"Pli selon {fr}", "pt": f"Vinco por {pt}"})
    first = first or mark
    steps.append(pliego.Step(
        f"fold-{key}",
        {"en": f"Valley-fold {en}", "es": f"Dobla en valle por {es}",
         "fr": f"Plier en vallée selon {fr}", "pt": f"Dobre em vale por {pt}"},
        [(mark, 180.0)], duration_ms=1500))
    steps.append(pliego.Step(
        f"press-{key}",
        {"en": "Press the crease flat", "es": "Marca bien el pliegue",
         "fr": "Marquer le pli bien à plat", "pt": "Vinque bem a dobra"},
        [(mark, 180.0)], duration_ms=round(hold * 1000.0),
        note={"en": "Held beyond its elastic limit, the crease takes a permanent set.",
              "es": "Sostenido más allá de su límite elástico, el pliegue queda marcado.",
              "fr": "Maintenu au-delà de sa limite élastique, le pli se fixe.",
              "pt": "Mantido além do seu limite elástico, o vinco fica marcado."}))
    steps.append(pliego.Step(
        f"let-go-{key}",
        {"en": "Let go: it opens only a little", "es": "Suéltalo: se abre solo un poco",
         "fr": "Lâcher : il ne s'ouvre qu'un peu", "pt": "Solte: abre só um pouco"},
        release=[mark], duration_ms=1500,
        note={"en": "Pressed past its elastic limit, the crease has taken a set, so it springs "
                    "back only a little.",
              "es": "Marcado más allá de su límite elástico, el pliegue quedó fijado: por eso "
                    "regresa solo un poco.",
              "fr": "Marqué au-delà de sa limite élastique, le pli s'est fixé : il ne revient "
                    "donc qu'un peu.",
              "pt": "Vincado além do limite elástico, o vinco ficou fixado: por isso volta só "
                    "um pouco."}))
    steps.append(pliego.Step(
        f"unfold-{key}",
        {"en": "Unfold it flat", "es": "Desdóblalo hasta dejarlo plano",
         "fr": "Le déplier à plat", "pt": "Desdobre até ficar plano"},
        [(mark, 0.0)], duration_ms=1500))
    marks.append(mark)

steps.append(pliego.Step(
    "let-go",
    {"en": "Let go: the paper remembers", "es": "Suéltalo: el papel recuerda",
     "fr": "Lâcher : le papier se souvient", "pt": "Solte: o papel se lembra"},
    release=marks, duration_ms=2000,
    note={"en": "Released, each crease relaxes to its rest angle instead of lying flat.",
          "es": "Al soltarlo, cada pliegue se relaja hasta su ángulo de reposo en vez de "
                "quedar plano.",
          "fr": "Relâché, chaque pli revient à son angle de repos au lieu de se remettre à plat.",
          "pt": "Solto, cada vinco relaxa até o seu ângulo de repouso em vez de ficar plano."}))

result = pliego.Assembly(
    [square],
    controls=[pliego.sequence_control(label={"en": "Fold program", "es": "Secuencia de pliegues",
                                             "fr": "Séquence de pliage",
                                             "pt": "Sequência de dobras"})],
    sequence=pliego.Sequence(steps, mode="physical"),
    targets={"first-crease-folded": {"angles": {first: 180.0}}},
    title="Crease and unfold",
)
