"""Fox puppet — sheet-hyperobjects cartridge (Pliego): the talking fox from one square.

The traditional fox puppet starts from the organ base (the square folded in half, the sides to
the middle and both flaps squashed). This cartridge folds that base exactly, then shapes the head
with its own folds: the lower jaw's side folded in and its corner turned under, the ear flap
opened out and its corners folded into a pointed ear, and two creases from the middle of the
closed edge that make the mouth's pleat. In 3-D the pleat folds and the jaws close about the
mouth's corner as rigid paper (`FoldProgram.kinematic`, loop closure solved on the whole
pattern), so the studio preview can open and close the mouth.

Every flat fold is a `pliego.FoldProgram` operation on a layer-ordered flat state, checked for a
consistent layer order and for Kawasaki and Maekawa at every vertex; the crease pattern is the
final state unfolded. No published diagram or crease pattern is copied: every line is computed
here. The face art (eyes and nose) is an original drawing made by this script.
"""

import math

import pliego


def L4(en, es, fr, pt):
    return {"en": en, "es": es, "fr": fr, "pt": pt}


# ── parameters ───────────────────────────────────────────────────────────────
P, C = pliego.param, pliego.clamp
size = C(float(P(lambda: size, 200.0)), 120.0, 400.0)  # noqa: F821
gape = C(float(P(lambda: gape, 22.0)), 6.0, 26.0)  # noqa: F821
face = P(lambda: face, "drawn")  # noqa: F821
stock = P(lambda: stock, "kami")  # noqa: F821
run = P(lambda: mode, "fold")  # noqa: F821
if face not in ("drawn", "plain"):
    raise ValueError(f"unknown face {face!r}")
if run not in ("fold", "talk"):
    raise ValueError(f"unknown mode {run!r}")

S = size
h, q = S / 2.0, S / 4.0
M = (h, h)                                  # the middle of the closed edge: the mouth's corner
NOSE = (q, 0.0)                             # the upper jaw's tip (the nose crease ends here)
XB = h - h * math.tan(math.atan(0.5) / 2.0)
PLEAT = (XB, 0.0)                           # the pleat crease halves the gusset
HALF = math.atan(0.5) / 2.0                 # each pleat wedge's angle at the mouth's corner


def pleat(gap):
    """The pleat's fold angle (deg) for a mouth opened `gap` degrees: the two wedges meet the
    jaws at angle HALF each, so cos(gap) = cos²(HALF) + sin²(HALF)·cos(180° − fold)."""
    c = (math.cos(math.radians(gap)) - math.cos(HALF) ** 2) / math.sin(HALF) ** 2
    return 180.0 - math.degrees(math.acos(max(-1.0, min(1.0, c))))


SHUT, OPEN = pleat(2.0), pleat(gape)        # nearly closed, and as wide as asked
OUTSIDE, INSIDE = "#d9611f", "#f6e3d3"       # back of the sheet (the fox), front (the mouth)

T = {
    "half": L4("Fold the square in half, top edge to bottom edge, coloured side inside",
               "Dobla el cuadrado por la mitad, el borde de arriba sobre el de abajo, con el "
               "color hacia dentro",
               "Pliez le carré en deux, bord du haut sur bord du bas, couleur à l'intérieur",
               "Dobre o quadrado ao meio, a aresta de cima sobre a de baixo, com a cor para "
               "dentro"),
    "mid": L4("Fold in half side to side and unfold: a crease down the middle",
              "Dobla por la mitad de lado a lado y desdobla: un pliegue marcado en el centro",
              "Pliez en deux d'un côté à l'autre et dépliez : un pli marqué au milieu",
              "Dobre ao meio de lado a lado e desdobre: um vinco marcado no meio"),
    "sides": L4("Fold both sides to the middle crease", "Dobla los dos lados hasta el pliegue "
                "central", "Rabattez les deux côtés sur le pli du milieu",
                "Dobre os dois lados até ao vinco do meio"),
    "squash": L4("Lift the flap, open its two layers and squash it flat: a roof-shaped point",
                 "Levanta la solapa, abre sus dos capas y aplástala: queda una punta en forma de "
                 "tejado",
                 "Soulevez le rabat, ouvrez ses deux couches et aplatissez-le : une pointe en "
                 "forme de toit",
                 "Levante a aba, abra as duas camadas e espalme-a: fica uma ponta em forma de "
                 "telhado"),
    "chin": L4("Fold the lower jaw's side behind, to the middle",
               "Dobla hacia atrás el costado de la mandíbula, hasta el centro",
               "Rabattez derrière le côté de la mâchoire, jusqu'au milieu",
               "Dobre para trás o lado da mandíbula, até ao meio"),
    "taper": L4("Turn the jaw's outer corner under",
                "Dobla hacia atrás la esquina exterior de la mandíbula",
                "Rentrez derrière le coin extérieur de la mâchoire",
                "Dobre para trás o canto de fora da mandíbula"),
    "ear-open": L4("Open the other flap out flat: it lies on the point behind it",
                   "Abre la otra solapa hasta dejarla plana: queda sobre la punta de detrás",
                   "Dépliez l'autre rabat à plat : il se pose sur la pointe de derrière",
                   "Abra a outra aba até ficar plana: fica sobre a ponta de trás"),
    "ear-tip": L4("Fold the bottom corner of both layers up along the diagonal",
                  "Dobla hacia arriba la esquina de abajo de las dos capas, por la diagonal",
                  "Remontez le coin du bas des deux couches le long de la diagonale",
                  "Dobre para cima o canto de baixo das duas camadas, pela diagonal"),
    "ear": L4("Fold the front edge behind: a pointed ear",
              "Dobla hacia atrás el borde delantero: una oreja puntiaguda",
              "Rabattez derrière le bord avant : une oreille pointue",
              "Dobre para trás a aresta da frente: uma orelha pontiaguda"),
    "creases": L4("Crease two lines from the middle of the folded edge: the mouth's pleat",
                  "Marca dos líneas desde el centro del borde doblado: el pliegue de la boca",
                  "Marquez deux lignes depuis le milieu du bord plié : le pli de la bouche",
                  "Vinque duas linhas a partir do meio da aresta dobrada: a prega da boca"),
    "shut": L4("Push the pleat in: the jaws close", "Empuja el pliegue hacia dentro: las "
               "mandíbulas se cierran", "Poussez le pli vers l'intérieur : les mâchoires se "
               "ferment", "Empurre a prega para dentro: as mandíbulas fecham-se"),
    "open": L4("Open the mouth", "Abre la boca", "Ouvrez la bouche", "Abra a boca"),
    "close": L4("Close the mouth", "Cierra la boca", "Fermez la bouche", "Feche a boca"),
}
NOTE = L4(
    "Kinematic stand-in: the jaws turn about the mouth's corner as rigid paper while the pleat "
    "folds. In the hand, fingers in the pockets work the mouth and the paper bends; that is the "
    "physics engine's part.",
    "Sustituto cinemático: las mandíbulas giran sobre la comisura como papel rígido mientras el "
    "pliegue se dobla. En la mano, los dedos en los bolsillos mueven la boca y el papel se curva; "
    "eso le toca al motor físico.",
    "Substitut cinématique : les mâchoires tournent autour de la commissure comme du papier "
    "rigide pendant que le pli se ferme. Dans la main, les doigts dans les poches font bouger la "
    "bouche et le papier se courbe ; c'est le rôle du moteur physique.",
    "Substituto cinemático: as mandíbulas giram sobre o canto da boca como papel rígido enquanto "
    "a prega dobra. Na mão, os dedos nos bolsos mexem a boca e o papel curva-se; isso cabe ao "
    "motor físico.")


# ── the face art (original): one eye on each cheek, a nose dot on each side ──
def face_art():
    """Back-side art over the sheet's bounding box (image y down): the eyes sit on the upper
    jaw near the mouth's corner, the nose at the jaw's tip, mirrored onto both halves."""
    r, k = 0.035 * S, 0.012 * S
    marks = []
    for y in (0.44 * S, 0.56 * S):          # the two cheeks (the folded halves)
        ey = S - y
        marks.append(f"<ellipse cx='{0.34 * S:.2f}' cy='{ey:.2f}' rx='{r:.2f}' "
                     f"ry='{0.7 * r:.2f}' fill='#1d1a17'/>")
        marks.append(f"<circle cx='{0.33 * S:.2f}' cy='{ey - 0.25 * r:.2f}' r='{0.25 * r:.2f}' "
                     "fill='#ffffff'/>")
    for y in (0.025 * S, 0.975 * S):        # the nose, at the upper jaw's tip on each half
        marks.append(f"<circle cx='{0.262 * S:.2f}' cy='{S - y:.2f}' r='{k:.2f}' "
                     "fill='#1d1a17'/>")
    svg = (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {S:.2f} {S:.2f}'>"
           f"<rect width='{S:.2f}' height='{S:.2f}' fill='{OUTSIDE}'/>" + "".join(marks)
           + "</svg>")
    for a, b in (("%", "%25"), ("#", "%23"), ("<", "%3C"), (">", "%3E"), (" ", "%20"),
                 ("'", "%27")):
        svg = svg.replace(a, b)
    return "data:image/svg+xml;charset=utf-8," + svg


back = pliego.Face(OUTSIDE, face_art()) if face == "drawn" else OUTSIDE

# ── the organ base (traditional) ─────────────────────────────────────────────
fp = pliego.FoldProgram([(0.0, 0.0), (S, 0.0), (S, S), (0.0, S)], stock=stock,
                        label=L4("Square", "Cuadrado", "Carré", "Quadrado"),
                        front=INSIDE, back=back)
fp.fold("half", T["half"], ((-1.0, h), (S + 1.0, h)), "valley", at=(h, 0.9 * S))
fp.crease_and_unfold("mid", T["mid"], ((h, -1.0), (h, S + 1.0)), "valley", at=(0.9 * S, 0.3 * S))
fp.fold("sides", T["sides"], ((3 * q, -1.0), (3 * q, h + 1.0)), "valley", at=(0.95 * S, 0.3 * S))
fp.fold("sides-2", T["sides"], ((q, h + 1.0), (q, -1.0)), "valley", at=(0.05 * S, 0.3 * S))
fp.squash("squash", T["squash"], ((3 * q, -1.0), (3 * q, h + 1.0)), at=(0.6 * S, 0.4 * S))
fp.squash("squash-2", T["squash"], ((q, h + 1.0), (q, -1.0)), at=(0.4 * S, 0.4 * S))
organ_base = fp.state

# ── the head (this cartridge's folds) ────────────────────────────────────────
fp.fold("chin", T["chin"], ((3 * q, -1.0), (3 * q, h + 1.0)), "mountain", at=(0.9 * S, 0.1 * S))
fp.fold("taper", T["taper"], ((h, 0.0), (3 * q, q)), "mountain", at=(0.73 * S, 0.02 * S))
fp.fold("ear-open", T["ear-open"], ((q, -1.0), (q, h + 1.0)), "valley", at=(0.4 * S, 0.1 * S),
        layers=1)
fp.fold("ear-tip", T["ear-tip"], ((q, 0.0), (0.0, q)), "valley", at=(0.02 * S, 0.02 * S))
fp.fold("ear", T["ear"], ((q, 0.0), (q / 2.0, (q + h) / 2.0)), "mountain", at=(0.05 * S, 0.3 * S))
fp.crease("nose", T["creases"], (M, NOSE), "valley", at=(0.3 * S, 0.45 * S))
fp.crease("pleat", T["creases"], (M, PLEAT), "valley", at=(0.3 * S, 0.45 * S))

# ── 3-D: the pleat folds and the jaws close; then the mouth talks ────────────
UPPER = (0.3 * S, 0.9 * S)                  # a sheet point on the upper jaw, which holds still
FREE = [(M, NOSE), (M, (h, 0.0))]


def mouth(sid, label, deg, note=None):
    fp.kinematic(sid, label, drive=[((M, PLEAT), deg)], free=FREE, fixed=UPPER, ms=900,
                 note=note)


mouth("shut", T["shut"], SHUT, note=NOTE)
for k in (1, 2):
    mouth(f"open-{k}", T["open"], OPEN)
    mouth(f"close-{k}", T["close"], SHUT)

built = fp.build("square", start_after="shut" if run == "talk" else None)
reports, issues = pliego.flatfold.check(built.state.unfold("check", folded_only=True).build())
errors = [i["detail"] for i in issues if i["level"] == "error"]
if errors:
    raise ValueError("the fox's crease pattern is not flat-foldable: " + "; ".join(errors))
print(built.summary())
print(f"flatfold: vertices={len(reports)} maekawa=ok kawasaki=ok big_little_big=ok "
      f"organ_base_faces={len(organ_base.faces)} fox_faces={len(built.state.faces)} "
      f"mouth_deg=2/{gape:g} pleat_deg={SHUT:.1f}/{OPEN:.1f}")

if run == "talk":
    built.sheet.placement = pliego.Placement((0.0, 0.0, 0.0), (math.sqrt(0.5), 0.0, 0.0,
                                                               math.sqrt(0.5)))
    result = pliego.Assembly(
        [built.sheet],
        controls=[pliego.sequence_control("mouth", label=L4(
            "Mouth (open and close)", "Boca (abrir y cerrar)", "Bouche (ouvrir et fermer)",
            "Boca (abrir e fechar)"))],
        sequence=built.sequence, initial=built.initial("square"),
        targets={"flat-folded": built.target()}, title="Fox puppet")
else:
    result = pliego.Assembly(
        [built.sheet],
        controls=[pliego.sequence_control(label=L4(
            "Fold program", "Secuencia de pliegues", "Séquence de pliage", "Sequência de dobras"))],
        sequence=built.sequence, targets={"flat-folded": built.target()}, title="Fox puppet")
