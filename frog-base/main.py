"""Frog base — sheet-hyperobjects cartridge (Pliego).

The traditional frog base: a preliminary base whose four flaps are squashed and then petal-folded.
Every move is a `pliego.flatops` operation on a layer-ordered flat state (`pliego.FoldProgram`),
checked for a consistent layer order (taco and tortilla conditions, transitivity) and for
Kawasaki and Maekawa at every vertex; the crease pattern is the base unfolded onto the square,
with the four-fold symmetry of the traditional pattern. Every line is computed here; no published
diagram or crease pattern is copied.
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


def meet(p, d, q, e):
    den = d[0] * e[1] - d[1] * e[0]
    t = ((q[0] - p[0]) * e[1] - (q[1] - p[1]) * e[0]) / den
    return (p[0] + t * d[0], p[1] + t * d[1])


def ray(p, deg):
    return (p, (p[0] + math.cos(math.radians(deg)), p[1] + math.sin(math.radians(deg))))


size = float(PARAM(lambda: size, 150.0))  # noqa: F821
stock = PARAM(lambda: stock, "kami")  # noqa: F821
size = max(80.0, min(300.0, size))
S, H = size, size / 2.0
FRONT, BACK = "#f4efe6", "#2e7d5b"

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
    "squash-flap": L4("Squash the flap: stand it on the centre line, open it and press it flat",
                      "Aplasta la solapa: levántala sobre la línea central, ábrela y presiónala",
                      "Écrasez le rabat : dressez-le sur la ligne médiane, ouvrez-le et aplatissez",
                      "Esmague a aba: levante-a na linha central, abra-a e pressione-a"),
    "page": L4("Turn a page: fold the top layers over to the other side",
               "Pasa una página: lleva las capas de arriba al otro lado",
               "Tournez une page : rabattez les couches du dessus de l'autre côté",
               "Vire uma página: leve as camadas de cima para o outro lado"),
    "petal": L4("Petal fold: lift the bottom point of the top layer; the sides fold in",
                "Pliegue pétalo: levanta la punta inferior de la capa de arriba; los lados "
                "se cierran",
                "Pli pétale : relevez la pointe inférieure de la couche du dessus ; les côtés "
                "se rabattent",
                "Dobra pétala: levante a ponta de baixo da camada de cima; os lados fecham-se"),
}

fp = pliego.FoldProgram(
    pliego.square(S), stock=stock, label=L4("Square", "Cuadrado", "Carré", "Quadrado"),
    front=FRONT, back=BACK)
fp.fold("diagonal", T["diagonal"], ((S, 0.0), (0.0, S)), "valley", at=(S * 0.1, S * 0.1))
fp.fold("half", T["half"], ((H, H), (S, S)), "valley", at=(S * 0.9, S * 0.6))
fp.squash("squash-front", T["squash"], ((H, H), (S, S)), at=(H * 0.9, S * 0.85))
fp.turn_over()
fp.squash("squash-back", T["squash"], ((H, H), (0.0, S)), at=(H * 1.3, S * 0.93))
fp.rotate(135.0, (H, H))
x0, y0, x1, y1 = fp.state.bbox()
near = fp.state.vertex_near
CTR = near(((x0 + x1) / 2, y1))
B = near(((x0 + x1) / 2, y0))
LFT, RGT = near((x0, (y0 + y1) / 2)), near((x1, (y0 + y1) / 2))
# squash the four flaps of the preliminary base, turning a page between the two on each side
for tag in ("f", "b"):
    fp.squash(f"squash-r-{tag}", T["squash-flap"], (CTR, B), at=(RGT[0] - 0.08 * S, RGT[1]),
              layers=1)
    fp.fold(f"page-{tag}", T["page"], (B, CTR), "valley",
            at=(CTR[0] - 0.027 * S, CTR[1] - 0.2 * S), layers=2)
    fp.squash(f"squash-l-{tag}", T["squash-flap"], (CTR, B), at=(LFT[0] + 0.08 * S, LFT[1]),
              layers=1)
    fp.turn_over()
# petal-fold each face: the lifted point is the bottom of the face's top layer (the midpoint of
# an edge of the square); its kite lines lay that layer's lower edges on the centre line
x0, y0, x1, y1 = fp.state.bbox()
TIP = fp.state.vertex_near((CTR[0], (CTR[1] + B[1]) / 2 - (CTR[1] - B[1]) * 0.21), 0.01 * S)
r2 = 1.0 / math.sqrt(2.0)
KL = meet(TIP, (-r2, r2), CTR, (x0 - CTR[0], TIP[1] - CTR[1]))
KR = meet(TIP, (r2, r2), CTR, (x1 - CTR[0], TIP[1] - CTR[1]))
SEED = (CTR[0] + 0.02 * S, (KL[1] + TIP[1]) / 2)
fp.petal("petal-1", T["petal"], (KL, KR), TIP, at=SEED)
fp.turn_over()
fp.petal("petal-2", T["petal"], (KL, KR), TIP, at=SEED)
fp.fold("page-3", T["page"], (CTR, B), "valley", at=(CTR[0] + 0.04 * S, TIP[1] + 0.067 * S),
        layers=3)
fp.petal("petal-3", T["petal"], (KL, KR), TIP, at=SEED)
fp.fold("page-4", T["page"], (CTR, B), "valley", at=(CTR[0] - 0.04 * S, TIP[1] + 0.067 * S),
        layers=7)
fp.petal("petal-4", T["petal"], (KL, KR), TIP, at=SEED)
frog_base = fp.state

built = fp.build("square")
arr = built.state.unfold("check", folded_only=True).build()
reports, issues = pliego.flatfold.check(arr)
errors = [i["detail"] for i in issues if i["level"] == "error"]
if errors:
    raise ValueError("the frog base's crease pattern is not flat-foldable: " + "; ".join(errors))
full = built.arr
pts = [(round(v.x - H, 3) + 0.0, round(v.y - H, 3) + 0.0) for v in full.vertices]
lines = {tuple(sorted((pts[a], pts[b]))) for a, b in full.edges}
turned = {tuple(sorted(((-pts[a][1], pts[a][0]), (-pts[b][1], pts[b][0])))) for a, b in full.edges}
if lines != turned:
    raise ValueError("the frog base's crease pattern lost its four-fold symmetry")
print(built.summary())
print(f"flatfold: vertices={len(reports)} maekawa=ok kawasaki=ok big_little_big=ok "
      f"faces={len(frog_base.faces)} four_fold_symmetric=yes")

result = pliego.Assembly(
    [built.sheet],
    controls=[pliego.sequence_control(label=L4(
        "Fold program", "Secuencia de pliegues", "Séquence de pliage", "Sequência de dobras"))],
    sequence=built.sequence,
    targets={"flat-folded": built.target()},
    title="Frog base",
)
