"""Flapping bird — sheet-hyperobjects cartridge (Pliego).

The traditional flapping bird from the bird base: the two lower flaps are inside-reverse-folded up
as a long neck and a tail, the tip of the neck becomes the head, and the wings are folded down and
opened to a resting V. Mode `fold` is the fold program; mode `flap` starts from the finished bird
and its `flap` control runs the operating cycle — pull the tail, the wings beat — as rigid hinge
motions of the wings (the pull itself bends the body; that is the physics engine's part).
Every fold is a `pliego.flatops` operation on a layer-ordered flat state, checked for a
consistent layer order and for Kawasaki and Maekawa; the crease pattern is the finished bird
unfolded. Every line is computed here; no published diagram or crease pattern is copied.
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
rise = float(PARAM(lambda: rise, 50.0))  # noqa: F821
neck = float(PARAM(lambda: neck, 0.8))  # noqa: F821
rest = float(PARAM(lambda: rest, 60.0))  # noqa: F821
beat = float(PARAM(lambda: beat, 30.0))  # noqa: F821
stock = PARAM(lambda: stock, "kami")  # noqa: F821
run_mode = PARAM(lambda: mode, "fold")  # noqa: F821 - injected by the runner
size = max(80.0, min(300.0, size))
rise = max(35.0, min(60.0, rise))
neck = max(0.7, min(0.85, neck))
rest = max(20.0, min(90.0, rest))
beat = max(5.0, min(min(40.0, rest), 180.0 - rest))
if run_mode not in ("fold", "flap"):
    raise ValueError(f"unknown mode {run_mode!r}")

S, H = size, size / 2.0


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
}
T.update({
    "neck": L4("Inside reverse fold the left flap up between the layers: the long neck",
               "Pliegue invertido interior de la solapa izquierda hacia arriba: el cuello largo",
               "Pli inversé intérieur du rabat gauche vers le haut : le long cou",
               "Dobra invertida interna da aba esquerda para cima: o pescoço comprido"),
    "rest": L4("Open the wings into a V", "Abre las alas en V", "Ouvrez les ailes en V",
               "Abra as asas em V"),
    "pull": L4("Pull the tail: the wings beat in", "Tira de la cola: las alas se cierran",
               "Tirez la queue : les ailes se referment", "Puxe a cauda: as asas fecham-se"),
    "release": L4("Let the tail go: the wings open again",
                  "Suelta la cola: las alas se vuelven a abrir",
                  "Relâchez la queue : les ailes se rouvrent",
                  "Solte a cauda: as asas voltam a abrir"),
})
REVERSE_NOTE = L4(
    "Preview: a rigid flap cannot reverse with its root closed, so the preview turns the tip as "
    "one stack and flips its back half inside at the end; the paper bends instead.",
    "Vista previa: una solapa rígida no puede invertirse con la raíz cerrada; la vista previa gira "
    "la punta como un bloque y al final pasa su mitad trasera hacia dentro; el papel se curva.",
    "Aperçu : un rabat rigide ne peut pas s'inverser racine fermée ; l'aperçu tourne la pointe "
    "d'un bloc puis fait passer sa moitié arrière à l'intérieur à la fin ; le papier se courbe.",
    "Pré-visualização: uma aba rígida não se inverte com a raiz fechada; a pré-visualização gira "
    "a ponta como um bloco e no fim passa a metade de trás para dentro; o papel curva-se.")

FLAP_NOTE = L4(
    "Kinematic stand-in: the wings turn on their hinges as rigid plates. The pull itself bends "
    "the body, which only the physics engine can show; the tail does not move in the preview.",
    "Sustituto cinemático: las alas giran sobre sus bisagras como placas rígidas. El tirón curva "
    "el cuerpo, y eso solo lo muestra el motor físico; la cola no se mueve en la vista previa.",
    "Substitut cinématique : les ailes tournent sur leurs charnières comme des plaques rigides. "
    "La traction courbe le corps, ce que seul le moteur physique peut montrer ; la queue ne bouge "
    "pas dans l'aperçu.",
    "Substituto cinemático: as asas giram nas suas dobradiças como placas rígidas. CTR puxão curva "
    "o corpo, e só o motor físico o mostra; a cauda não se mexe na pré-visualização.")

# ── the fold program: a bird base ─────────────────────────────────────────────
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


CTR, B, LFT, RGT = diamond(fp.state)
lo = math.atan2(RGT[1] - B[1], RGT[0] - B[0])
bis = (lo + math.pi / 2) / 2
KR = meet(B, (math.cos(bis), math.sin(bis)), CTR, (RGT[0] - CTR[0], RGT[1] - CTR[1]))
KL = meet(B, (-math.cos(bis), math.sin(bis)), CTR, (LFT[0] - CTR[0], LFT[1] - CTR[1]))


def petal_side(tag, top):
    fp.fold(f"kite-r-{tag}", T["kite-r"], (B, KR), "valley", at=(RGT[0] - 8, RGT[1]), layers=2)
    fp.fold(f"kite-l-{tag}", T["kite-l"], (KL, B), "valley", at=(LFT[0] + 8, LFT[1]), layers=2)
    if top:
        fp.fold(f"top-{tag}", T["top"], (KL, KR), "valley", at=(CTR[0] + 3, CTR[1] - 8), layers=1)
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



# ── neck, tail and head ──────────────────────────────────────────────────────
HY = KL[1]
Y1 = B[1] + neck * (HY - B[1])
P1 = (B[0], Y1)
th = (90.0 - rise) / 2.0
legw = math.tan(math.radians(22.5))
probe = B[1] + 0.25 * (HY - B[1])
NECK = ray(P1, th)
TAIL = (ray(P1, 180.0 - th)[1], P1)
fp.reverse_fold("neck", T["neck"], NECK, at=(B[0] - 0.4 * legw * (probe - B[1]), probe),
                note=REVERSE_NOTE)
fp.reverse_fold("tail", T["tail"], TAIL, at=(B[0] + 0.4 * legw * (probe - B[1]), probe),
                note=REVERSE_NOTE)
psi = math.radians(180.0 - rise)
neck_len = Y1 - B[1]
u = (math.cos(psi), math.sin(psi))
tip = (P1[0] + neck_len * u[0], P1[1] + neck_len * u[1])
side_n = (-u[1], u[0])
head_done = False
for frac in (0.2, 0.19, 0.21, 0.18, 0.22):
    dh = frac * neck_len
    hp = (tip[0] - dh * u[0], tip[1] - dh * u[1])
    seed = (tip[0] - 0.5 * dh * u[0] + 0.06 * dh * side_n[0],
            tip[1] - 0.5 * dh * u[1] + 0.06 * dh * side_n[1])
    try:
        fp.reverse_fold("head", T["head"], ray(hp, math.degrees(psi) + 55.0), at=seed,
                        note=REVERSE_NOTE)
        head_done = True
        break
    except pliego.FlatStateError as exc:
        if "from the vertex" not in str(exc):
            raise
if not head_done:
    raise ValueError("no head line clear of the neck's vertices")

# ── wings: down along the petal hinge, then opened into a V ──────────────────
WING = ((KL[0], HY), (KR[0], HY))
TOP = (B[0], 2 * HY - B[1])
up_seed = (B[0] + 3, (HY + TOP[1]) / 2)
fp.fold("wing-f", T["wing-f"], WING, "valley", at=up_seed, layers=1)
fp.fold("wing-b", T["wing-b"], WING, "mountain", at=up_seed, layers=1)
low = (B[0] + 3, HY - 0.1 * (TOP[1] - HY))
wing_f = {"line": WING, "at": low, "layers": 1}
wing_b = {"line": WING, "at": low, "layers": 1, "from_": "bottom"}
fp.hinges("rest", T["rest"], [dict(wing_f, turn=-(180.0 - rest)),
                              dict(wing_b, turn=180.0 - rest)], ms=1500)
# the operating cycle: pulling the tail makes the wings beat. The tail itself cannot turn as a
# rigid plate (it is wedged between the body's two halves; in paper the pull bends the body), so
# the cycle drives the wings, the part that moves as rigid plates on their hinges.
for k in (1, 2):
    fp.hinges(f"pull-{k}", T["pull"], [dict(wing_f, turn=beat), dict(wing_b, turn=-beat)],
              ms=700, note=FLAP_NOTE if k == 1 else None)
    fp.hinges(f"release-{k}", T["release"], [dict(wing_f, turn=-beat),
                                             dict(wing_b, turn=beat)], ms=700)

built = fp.build("square", start_after="rest" if run_mode == "flap" else None)
reports, issues = pliego.flatfold.check(built.state.unfold("check", folded_only=True).build())
errors = [i["detail"] for i in issues if i["level"] == "error"]
if errors:
    raise ValueError("the bird's crease pattern is not flat-foldable: " + "; ".join(errors))
print(built.summary())
print(f"flatfold: vertices={len(reports)} maekawa=ok kawasaki=ok big_little_big=ok "
      f"bird_base_faces={len(bird_base.faces)} bird_faces={len(built.state.faces)}")

if run_mode == "flap":
    result = pliego.Assembly(
        [built.sheet],
        controls=[pliego.sequence_control("flap", label=L4(
            "Flap (pull the tail)", "Aletear (tira de la cola)", "Battre des ailes (tirez la "
            "queue)", "Bater as asas (puxe a cauda)"))],
        sequence=built.sequence,
        initial=built.initial("square"),
        targets={"flat-folded": built.target()},
        title="Flapping bird",
    )
else:
    result = pliego.Assembly(
        [built.sheet],
        controls=[pliego.sequence_control(label=L4(
            "Fold program", "Secuencia de pliegues", "Séquence de pliage", "Sequência de dobras"))],
        sequence=built.sequence,
        targets={"flat-folded": built.target()},
        title="Flapping bird",
    )
