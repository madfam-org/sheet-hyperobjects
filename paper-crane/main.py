"""Paper crane (orizuru) — sheet-hyperobjects cartridge (Pliego).

The traditional crane, folded the way the diagrams read: a square becomes a preliminary base (two
folds and two squashes), then a bird base (kite precreases and two petal folds); the lower flaps
are narrowed front and back, reverse-folded up inside as the neck and the tail, the head is
reverse-folded, and the wings come down. Every move is a `pliego.flatops` operation on a
layer-ordered flat state (`pliego.FoldProgram`): each result is checked for a consistent layer
order (taco and tortilla conditions, transitivity) and for Kawasaki and Maekawa at every vertex,
and the crease pattern is the final state unfolded onto the square. Every line is computed here;
no published diagram or crease pattern is copied.
"""

import math

import pliego


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


def L4(en, es, fr, pt):
    return {"en": en, "es": es, "fr": fr, "pt": pt}


size = float(PARAM(lambda: size, 150.0))  # noqa: F821
rise = float(PARAM(lambda: rise, 60.0))  # noqa: F821
head = float(PARAM(lambda: head, 110.0))  # noqa: F821
wings = PARAM(lambda: wings, "down")  # noqa: F821
spread = float(PARAM(lambda: spread, 80.0))  # noqa: F821
stock = PARAM(lambda: stock, "kami")  # noqa: F821
size = max(80.0, min(300.0, size))
rise = max(40.0, min(65.0, rise))   # steeper, the tail's line runs into the narrowed layers
head = max(80.0, min(140.0, head))
spread = max(10.0, min(90.0, spread))
if wings not in ("down", "spread"):
    raise ValueError(f"wings must be 'down' or 'spread', not {wings!r}")

S, H = size, size / 2.0
NARROW = math.radians(90.0 - 11.25)   # a lower edge laid on the centre line, from the leg tip


def meet(p, d, q, e):
    den = d[0] * e[1] - d[1] * e[0]
    t = ((q[0] - p[0]) * e[1] - (q[1] - p[1]) * e[0]) / den
    return (p[0] + t * d[0], p[1] + t * d[1])


def mirror(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    ln = math.hypot(dx, dy)
    dx, dy = dx / ln, dy / ln
    t = (p[0] - a[0]) * dx + (p[1] - a[1]) * dy
    return (2 * (a[0] + t * dx) - p[0], 2 * (a[1] + t * dy) - p[1])


def ray(p, deg):
    return (p, (p[0] + math.cos(math.radians(deg)), p[1] + math.sin(math.radians(deg))))


# ── labels ────────────────────────────────────────────────────────────────────
T = {
    "diagonal": L4("Fold the square in half along the diagonal",
                   "Dobla el cuadrado por la mitad, por la diagonal",
                   "Pliez le carré en deux selon la diagonale",
                   "Dobre o quadrado ao meio pela diagonal"),
    "half": L4("Fold the triangle in half", "Dobla el triángulo por la mitad",
               "Pliez le triangle en deux", "Dobre o triângulo ao meio"),
    "squash": L4("Lift the top flap, open it and squash it into a square",
                 "Levanta la solapa de arriba, ábrela y aplánala en un cuadrado",
                 "Relevez le rabat du dessus, ouvrez-le et écrasez-le en carré",
                 "Levante a aba de cima, abra-a e esmague-a num quadrado"),
    "kite-r": L4("Fold the lower right edge of the front flap to the centre line",
                 "Lleva el borde inferior derecho de la solapa delantera a la línea central",
                 "Rabattez le bord inférieur droit du rabat avant sur la ligne médiane",
                 "Leve a aresta inferior direita da aba da frente até à linha central"),
    "kite-l": L4("Fold the lower left edge to the centre line",
                 "Lleva el borde inferior izquierdo a la línea central",
                 "Rabattez le bord inférieur gauche sur la ligne médiane",
                 "Leve a aresta inferior esquerda até à linha central"),
    "top": L4("Fold the top triangle down over the flaps",
              "Dobla el triángulo de arriba hacia abajo sobre las solapas",
              "Rabattez le triangle du haut sur les rabats",
              "Dobre o triângulo de cima para baixo sobre as abas"),
    "open": L4("Unfold", "Desdobla", "Dépliez", "Desdobre"),
    "petal": L4("Petal fold: lift the bottom corner of the front layer along the crease",
                "Pliegue pétalo: levanta la esquina inferior de la capa delantera por el pliegue",
                "Pli pétale : relevez le coin inférieur de la couche avant le long du pli",
                "Dobra pétala: levante o canto de baixo da camada da frente pelo vinco"),
    "narrow-r": L4("Narrow: fold the lower right edge of the front flap to the centre",
                   "Estrecha: lleva el borde inferior derecho de la solapa delantera al centro",
                   "Affinez : rabattez le bord inférieur droit du rabat avant au centre",
                   "Afine: leve a aresta inferior direita da aba da frente ao centro"),
    "narrow-l": L4("Narrow the lower left edge to the centre",
                   "Estrecha el borde inferior izquierdo hacia el centro",
                   "Affinez le bord inférieur gauche vers le centre",
                   "Afine a aresta inferior esquerda até ao centro"),
    "neck": L4("Inside reverse fold the left flap up between the layers: the neck",
               "Pliegue invertido interior de la solapa izquierda hacia arriba: el cuello",
               "Pli inversé intérieur du rabat gauche vers le haut : le cou",
               "Dobra invertida interna da aba esquerda para cima: o pescoço"),
    "tail": L4("Inside reverse fold the right flap up: the tail",
               "Pliegue invertido interior de la solapa derecha hacia arriba: la cola",
               "Pli inversé intérieur du rabat droit vers le haut : la queue",
               "Dobra invertida interna da aba direita para cima: a cauda"),
    "head": L4("Inside reverse fold the tip of the neck: the head",
               "Pliegue invertido interior de la punta del cuello: la cabeza",
               "Pli inversé intérieur de la pointe du cou : la tête",
               "Dobra invertida interna da ponta do pescoço: a cabeça"),
    "wing-f": L4("Fold the front wing down", "Baja el ala delantera",
                 "Rabattez l'aile avant vers le bas", "Baixe a asa da frente"),
    "wing-b": L4("Fold the back wing down behind", "Baja el ala trasera por detrás",
                 "Rabattez l'aile arrière vers le bas, derrière",
                 "Baixe a asa de trás por detrás"),
    "spread-f": L4("Spread the front wing", "Abre el ala delantera",
                   "Écartez l'aile avant", "Abra a asa da frente"),
    "spread-b": L4("Spread the back wing", "Abre el ala trasera",
                   "Écartez l'aile arrière", "Abra a asa de trás"),
}
REVERSE_NOTE = L4(
    "Preview: a rigid flap cannot reverse with its root closed, so the preview turns the tip as "
    "one stack and flips its back half inside at the end; the paper bends instead.",
    "Vista previa: una solapa rígida no puede invertirse con la raíz cerrada; la vista previa gira "
    "la punta como un bloque y al final pasa su mitad trasera hacia dentro; el papel se curva.",
    "Aperçu : un rabat rigide ne peut pas s'inverser racine fermée ; l'aperçu tourne la pointe "
    "d'un bloc puis fait passer sa moitié arrière à l'intérieur à la fin ; le papier se courbe.",
    "Pré-visualização: uma aba rígida não se inverte com a raiz fechada; a pré-visualização gira "
    "a ponta como um bloco e no fim passa a metade de trás para dentro; o papel curva-se.")

# ── the fold program ─────────────────────────────────────────────────────────
fp = pliego.FoldProgram(
    pliego.square(S), stock=stock, label=L4("Square", "Cuadrado", "Carré", "Quadrado"),
    front="#f2ede4", back="#c0392b")
fp.fold("diagonal", T["diagonal"], ((S, 0.0), (0.0, S)), "valley", at=(S * 0.1, S * 0.1))
fp.fold("half", T["half"], ((H, H), (S, S)), "valley", at=(S * 0.9, S * 0.6))
fp.squash("squash-front", T["squash"], ((H, H), (S, S)), at=(H * 0.9, S * 0.85))
fp.turn_over()
fp.squash("squash-back", T["squash"], ((H, H), (0.0, S)), at=(H * 1.3, S * 0.93))
fp.rotate(135.0, (H, H))


def diamond(state):
    """Top, bottom, left and right corners of the diamond (exact vertex positions)."""
    x0, y0, x1, y1 = state.bbox()
    near = state.vertex_near
    return (near(((x0 + x1) / 2, y1)), near(((x0 + x1) / 2, y0)),
            near((x0, (y0 + y1) / 2)), near((x1, (y0 + y1) / 2)))


O, B, LFT, RGT = diamond(fp.state)
lo = math.atan2(RGT[1] - B[1], RGT[0] - B[0])
bis = (lo + math.pi / 2) / 2
KR = meet(B, (math.cos(bis), math.sin(bis)), O, (RGT[0] - O[0], RGT[1] - O[1]))
KL = meet(B, (-math.cos(bis), math.sin(bis)), O, (LFT[0] - O[0], LFT[1] - O[1]))


def petal_side(tag, top):
    fp.fold(f"kite-r-{tag}", T["kite-r"], (B, KR), "valley", at=(RGT[0] - 8, RGT[1]), layers=2)
    fp.fold(f"kite-l-{tag}", T["kite-l"], (KL, B), "valley", at=(LFT[0] + 8, LFT[1]), layers=2)
    if top:
        fp.fold(f"top-{tag}", T["top"], (KL, KR), "valley", at=(O[0] + 3, O[1] - 8), layers=1)
        fp.unfold_last(f"open-top-{tag}", T["open"])
    for name, k, c in (("l", KL, LFT), ("r", KR, RGT)):
        cr = mirror(c, B, k)
        seed = ((B[0] + k[0] + cr[0]) / 3, (B[1] + k[1] + cr[1]) / 3)
        fp.fold(f"open-k{name}-{tag}", T["open"], (k, B) if name == "l" else (B, k), "valley",
                at=seed, layers=2)
    fp.petal(f"petal-{tag}", T["petal"], (KL, KR), B)


petal_side("f", True)
fp.turn_over()
petal_side("b", False)      # the hinge K₁–K₂ already runs through every layer above it
bird_base = fp.state


def narrow(tag):
    hw = (KR[0] - KL[0]) / 2
    fp.fold(f"narrow-r-{tag}", T["narrow-r"], ray(B, 90.0 - 11.25), "valley",
            at=(B[0] + 0.6 * hw, B[1] + 0.8 * (KL[1] - B[1])), layers=1)
    fp.fold(f"narrow-l-{tag}", T["narrow-l"], (ray(B, 90.0 + 11.25)[1], B), "valley",
            at=(B[0] - 0.6 * hw, B[1] + 0.8 * (KL[1] - B[1])), layers=1)


narrow("f")
fp.turn_over()
narrow("b")
# neck and tail: each lower flap turns up about a line through its inner edge at Y1
Y1 = B[1] + 0.62 * (KL[1] - B[1])
P1 = (B[0], Y1)
th = (90.0 - rise) / 2.0
legw = math.tan(math.radians(11.25))
probe = B[1] + 0.25 * (KL[1] - B[1])
fp.reverse_fold("neck", T["neck"], ray(P1, th), at=(B[0] - 0.5 * legw * (probe - B[1]), probe),
                note=REVERSE_NOTE)
fp.reverse_fold("tail", T["tail"], (ray(P1, 180.0 - th)[1], P1),
                at=(B[0] + 0.5 * legw * (probe - B[1]), probe), note=REVERSE_NOTE)
# head: the neck's tip turns down
psi = math.radians(180.0 - rise)
neck_len = Y1 - B[1]
u = (math.cos(psi), math.sin(psi))
tip = (P1[0] + neck_len * u[0], P1[1] + neck_len * u[1])
side_n = (-u[1], u[0])
# the head line sits about a fifth of the neck from its tip; a line grazing a vertex of the neck's
# layers (closer than the kernel's 0.05 mm near-miss bound) is moved along the neck a little
head_done = False
for frac in (0.22, 0.21, 0.23, 0.20, 0.24):
    dh = frac * neck_len
    hp = (tip[0] - dh * u[0], tip[1] - dh * u[1])
    seed = (tip[0] - 0.5 * dh * u[0] + 0.05 * dh * side_n[0],
            tip[1] - 0.5 * dh * u[1] + 0.05 * dh * side_n[1])
    try:
        fp.reverse_fold("head", T["head"], ray(hp, math.degrees(psi) + head / 2.0), at=seed,
                        note=REVERSE_NOTE)
        head_done = True
        break
    except pliego.FlatStateError as exc:
        if "from the vertex" not in str(exc):
            raise
if not head_done:
    raise ValueError("no head line clear of the neck's vertices")
# wings: down along the line through the ends of the narrowing creases on the wings
TOP = (B[0], 2 * KL[1] - B[1])
Y = fp.state.vertex_near(meet(B, (math.cos(NARROW), math.sin(NARROW)), KR,
                              (TOP[0] - KR[0], TOP[1] - KR[1])), 0.5)
WING = ((2 * B[0] - Y[0], Y[1]), Y)
up_seed = (B[0] + 3, (Y[1] + TOP[1]) / 2)
fp.fold("wing-f", T["wing-f"], WING, "valley", at=up_seed, layers=1)
fp.fold("wing-b", T["wing-b"], WING, "mountain", at=up_seed, layers=1)
if wings == "spread":
    low = (B[0] + 3, Y[1] - 0.25 * (Y[1] - KL[1]))
    fp.hinge("spread-f", T["spread-f"], WING, -spread, at=low, layers=1)
    fp.hinge("spread-b", T["spread-b"], WING, spread, at=low, layers=1, from_="bottom")

built = fp.build("square")
reports, issues = pliego.flatfold.check(built.state.unfold("check", folded_only=True).build())
errors = [i["detail"] for i in issues if i["level"] == "error"]
if errors:
    raise ValueError("the crane's crease pattern is not flat-foldable: " + "; ".join(errors))
print(built.summary())
print(f"flatfold: vertices={len(reports)} maekawa=ok kawasaki=ok big_little_big=ok "
      f"bird_base_faces={len(bird_base.faces)} crane_faces={len(built.state.faces)}")

targets = {"flat-folded": built.target()}
if wings == "spread":
    targets["wings-spread"] = built.target(pose=True)
result = pliego.Assembly(
    [built.sheet],
    controls=[pliego.sequence_control(label=L4(
        "Fold program", "Secuencia de pliegues", "Séquence de pliage", "Sequência de dobras"))],
    sequence=built.sequence,
    targets=targets,
    title="Paper crane",
)
