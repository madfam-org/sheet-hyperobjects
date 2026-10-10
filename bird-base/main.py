"""Bird base — sheet-hyperobjects cartridge (Pliego).

The base of the crane and the flapping bird: a preliminary base whose front and back flaps are
petal-folded. The pattern has five interior vertices. The centre O keeps the preliminary base's
degree-6 vertex (four book-fold rays and one diagonal); each book fold is split at K, at
size·(2 − √2)/2 from O, where the 22.5° kite creases from the petal corner meet it. Each K is a
degree-5 vertex during the program (inner and outer book fold, kite crease, kite crease of the
inner layer, petal hinge); the outer book fold opens flat as the petal rises, so in the bird base
K is a degree-4 vertex with sectors 135°, 67.5°, 45°, 112.5° (Kawasaki: 135° + 45° = 180°).

The program follows the hand: precreases, the collapse into a preliminary base, the kite
precreases of each flap, and the two petal folds. Every key pose is a flat-folded state;
`pliego.Sequence.kinematic_path` (the kernel's motion solver) turns each into exact rigid
in-between states, including the petal folds, where three vertices move together.
`pliego.flatfold.check` verifies the folded crease pattern and `pliego.kinematics` the closure of
the flat-folded target. All geometry is computed here; the base is traditional (no designer's
diagram is used).
"""

import math

import pliego
from pliego import flatfold, kinematics


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


def L4(en, es, fr, pt):
    return {"en": en, "es": es, "fr": fr, "pt": pt}


FLAT_TOL_DEG = 1e-6     # a crease within this of ±180° counts as folded flat
CLOSURE_TOL_MM = 1e-5   # loop closure of the target frame (grid-snapped vertices)

# ── the pattern: named creases on one sheet, flat-folded key poses, the kernel's checks ──
# Key poses list only what changes (spec §5.6: unlisted creases hold). The kernel's motion
# solver (`pliego.Sequence.kinematic_path`) turns them into exact rigid in-between states.
MARK, ENDS, STATE, KEYS = {}, {}, {}, []


def crease(sheet, name, a, b, kind, label):
    MARK[name] = sheet.crease(a, b, kind, label=label)
    ENDS[name] = (a, b)
    STATE[name] = 0.0


def key(sid, label, angles, ms=1500, n=8):
    moving = {k: float(v) for k, v in angles.items() if abs(v - STATE[k]) > 1e-9}
    if not moving:
        raise ValueError(f"key pose '{sid}' moves nothing")
    STATE.update(moving)
    KEYS.append((sid, label, moving, ms, n))


def flat_check(sheet, state=None):
    """Maekawa, Kawasaki and big-little-big at every interior vertex of the creases folded flat
    in the final pose (`pliego.flatfold.check`); fail loud on any error."""
    st = STATE if state is None else state
    check = pliego.Sheet("check", list(sheet.outline))
    folded = 0
    for name, a in st.items():
        if abs(abs(a) - 180.0) <= FLAT_TOL_DEG:
            check.crease(*ENDS[name], "valley" if a > 0 else "mountain")
            folded += 1
        elif abs(a) > FLAT_TOL_DEG:
            raise ValueError(f"crease '{name}' ends at {a:.4f}°, neither flat nor folded")
    reports, issues = flatfold.check(check.build())
    errors = [i["detail"] for i in issues if i["level"] == "error"]
    if errors:
        raise ValueError("not flat-foldable: " + "; ".join(errors))
    exact = sum(1 for r in reports if r.kawasaki_exact)
    return (f"flatfold: folded_creases={folded} vertices={len(reports)} maekawa=ok "
            f"kawasaki=ok(exact={exact} float={len(reports) - exact}) big_little_big=ok")


def program(sheet, root):
    steps = [pliego.Step(sid, label, [(MARK[k], a) for k, a in moving.items()], duration_ms=ms)
             for sid, label, moving, ms, _ in KEYS]
    seq = pliego.Sequence.kinematic_path(sheet, steps,
                                         substeps={sid: n for sid, _, _, _, n in KEYS})
    arr = sheet.build()
    final = {e: a for k, a in STATE.items() for e in MARK[k].edges()}
    closure = kinematics.closure_residual(arr, final, pliego.P(*root))
    if closure > CLOSURE_TOL_MM:
        raise ValueError(f"the flat-folded target does not close: {closure:.3g} mm")
    rep = seq.report
    line = (f"kinematics: steps={rep['steps']} dof={rep['dof']} "
            f"max_residual_rad={rep['max_residual_rad']:.2e} target_closure_mm={closure:.2e}")
    return seq, line


def target(root, state=None):
    st = STATE if state is None else state
    return {"angles": {MARK[k]: a for k, a in st.items()}, "root": root}


size = float(PARAM(lambda: size, 150.0))  # noqa: F821
stock = PARAM(lambda: stock, "kami")  # noqa: F821
size = max(80.0, min(300.0, size))

s, h = size, size / 2.0
k = h * (2.0 - math.sqrt(2.0))  # O to K along a book fold: where a 22.5° kite crease meets it
O = (h, h)
K1, K2, K3, K4 = (h + k, h), (h, h + k), (h - k, h), (h, h - k)
E, N, W, S = (s, h), (h, s), (0.0, h), (h, 0.0)          # edge midpoints
B, C1, C2, D = (s, s), (s, 0.0), (0.0, s), (0.0, 0.0)    # front petal, legs, back petal
sheet = pliego.Sheet("square", pliego.square(s), stock=stock,
                     label=L4("Square", "Cuadrado", "Carré", "Quadrado"))
DIRS = {"e": L4("E", "E", "E", "E"), "n": L4("N", "N", "N", "N"),
        "w": L4("W", "O", "O", "O"), "s": L4("S", "S", "S", "S")}


def lab(text, d):
    return {k_: f"{text[k_]} ({DIRS[d][k_]})" for k_ in text}


INNER = L4("Book fold, inner part", "Pliegue de libro, parte interior",
           "Pli livre, partie intérieure", "Dobra de livro, parte interior")
OUTER = L4("Book fold, outer part", "Pliegue de libro, parte exterior",
           "Pli livre, partie extérieure", "Dobra de livro, parte exterior")
for d, Kp, M_ in (("e", K1, E), ("n", K2, N), ("w", K3, W), ("s", K4, S)):
    crease(sheet, f"in-{d}", O, Kp, "mountain", lab(INNER, d))
    crease(sheet, f"out-{d}", Kp, M_, "mountain", lab(OUTER, d))
crease(sheet, "diag-nw", O, C2, "valley", L4(
    "Diagonal (NW half)", "Diagonal (mitad NO)", "Diagonale (moitié NO)", "Diagonal (metade NO)"))
crease(sheet, "diag-se", O, C1, "valley", L4(
    "Diagonal (SE half)", "Diagonal (mitad SE)", "Diagonale (moitié SE)", "Diagonal (metade SE)"))
KITE = L4("Kite crease, petal layer", "Pliegue de cometa, capa del pétalo",
          "Pli cerf-volant, couche du pétale", "Vinco de pipa, camada da pétala")
KITE_IN = L4("Kite crease, inner layer", "Pliegue de cometa, capa interior",
             "Pli cerf-volant, couche intérieure", "Vinco de pipa, camada interior")
HINGE = L4("Petal hinge", "Bisagra del pétalo", "Charnière du pétale", "Dobradiça da pétala")
FRONT, BACK = (L4("front", "delante", "devant", "frente"), L4("back", "detrás", "derrière",
                                                                  "trás"))


def side(text, which):
    return {k_: f"{text[k_]} ({which[k_]})" for k_ in text}


# front petal (corner B, hinge K1–K2); back petal (corner D, hinge K3–K4)
crease(sheet, "kite-e", K1, B, "mountain", side(KITE, FRONT))
crease(sheet, "kite-n", K2, B, "mountain", side(KITE, FRONT))
crease(sheet, "hinge-f", K1, K2, "valley", side(HINGE, FRONT))
crease(sheet, "kin-e", K1, C1, "mountain", side(KITE_IN, FRONT))
crease(sheet, "kin-n", K2, C2, "mountain", side(KITE_IN, FRONT))
crease(sheet, "kite-w", K3, D, "mountain", side(KITE, BACK))
crease(sheet, "kite-s", K4, D, "mountain", side(KITE, BACK))
crease(sheet, "hinge-b", K3, K4, "valley", side(HINGE, BACK))
crease(sheet, "kin-w", K3, C2, "mountain", side(KITE_IN, BACK))
crease(sheet, "kin-s", K4, C1, "mountain", side(KITE_IN, BACK))
ROOT = (0.45 * s, 0.3 * s)  # a face of the back quadrant, inside the back petal's body
UNFOLD = L4("Unfold", "Desdobla", "Dépliez", "Desdobre")
BOOK_EW = {"in-e": -180.0, "out-e": -180.0, "in-w": -180.0, "out-w": -180.0}
BOOK_NS = {"in-n": -180.0, "out-n": -180.0, "in-s": -180.0, "out-s": -180.0}
PRELIM = dict(BOOK_EW, **BOOK_NS, **{"diag-nw": 180.0, "diag-se": 180.0})
PRE_F = {"kite-e": 180.0, "kite-n": 180.0, "kin-e": -180.0, "kin-n": -180.0}
KITES_F = {"kite-e": -180.0, "kite-n": -180.0, "kin-e": -180.0, "kin-n": -180.0}
PRE_B = {"kite-w": 180.0, "kite-s": 180.0, "kin-w": -180.0, "kin-s": -180.0}
KITES_B = {"kite-w": -180.0, "kite-s": -180.0, "kin-w": -180.0, "kin-s": -180.0}
PETAL_F = dict(KITES_F, **{"hinge-f": 180.0, "out-e": 0.0, "out-n": 0.0})
PETAL_B = dict(KITES_B, **{"hinge-b": 180.0, "out-w": 0.0, "out-s": 0.0})

key("fold-diagonal", L4(
    "Coloured side up, valley-fold along the diagonal",
    "Con el color hacia arriba, dobla en valle por la diagonal",
    "Couleur dessus, pliez en vallée selon la diagonale",
    "Com a cor para cima, dobre em vale pela diagonal"),
    {"diag-nw": 180.0, "diag-se": 180.0}, 1200, 4)
key("unfold-diagonal", UNFOLD, {"diag-nw": 0.0, "diag-se": 0.0}, 900, 3)
key("fold-book-ew", L4(
    "Mountain-fold in half, top to bottom", "Dobla en monte a la mitad, de arriba abajo",
    "Pliez en montagne en deux, de haut en bas", "Dobre em montanha ao meio, de cima para baixo"),
    BOOK_EW, 1200, 4)
key("unfold-book-ew", UNFOLD, {n: 0.0 for n in BOOK_EW}, 900, 3)
key("fold-book-ns", L4(
    "Mountain-fold in half, side to side", "Dobla en monte a la mitad, de lado a lado",
    "Pliez en montagne en deux, d'un côté à l'autre", "Dobre em montanha ao meio, de lado a lado"),
    BOOK_NS, 1200, 4)
key("unfold-book-ns", UNFOLD, {n: 0.0 for n in BOOK_NS}, 900, 3)
key("collapse", L4(
    "Collapse into a preliminary base, open end down",
    "Pliega en una base preliminar, con la abertura hacia abajo",
    "Repliez en base préliminaire, ouverture en bas",
    "Dobre numa base preliminar, com a abertura para baixo"), PRELIM, 2000, 10)
PRELIM_STATE = dict(STATE)
key("kites-front", L4(
    "Fold the lower edges of the front flap to the centre line, through both layers",
    "Lleva los bordes inferiores de la solapa delantera a la línea central, por las dos capas",
    "Rabattez les bords inférieurs du rabat avant sur la ligne médiane, à travers les deux "
    "couches",
    "Leve as arestas inferiores da aba da frente até à linha central, pelas duas camadas"),
    PRE_F, 1200, 4)
key("unfold-kites-front", UNFOLD, {n: 0.0 for n in PRE_F}, 900, 3)
key("petal-front", L4(
    "Petal fold: lift the front corner up along the hinge while the sides swing in",
    "Pliegue pétalo: levanta la esquina delantera sobre la bisagra mientras los lados se "
    "cierran",
    "Pli pétale : relevez le coin avant sur la charnière tandis que les côtés se rabattent",
    "Dobra pétala: levante o canto da frente sobre a dobradiça enquanto os lados se fecham"),
    PETAL_F, 2400, 10)
key("kites-back", L4(
    "Turn over; fold the lower edges of the back flap to the centre line",
    "Da la vuelta; lleva los bordes inferiores de la solapa trasera a la línea central",
    "Retournez ; rabattez les bords inférieurs du rabat arrière sur la ligne médiane",
    "Vire; leve as arestas inferiores da aba de trás até à linha central"),
    PRE_B, 1200, 4)
key("unfold-kites-back", UNFOLD, {n: 0.0 for n in PRE_B}, 900, 3)
key("petal-back", L4(
    "Petal fold the back: the bird base", "Haz el pliegue pétalo atrás: la base de pájaro",
    "Pli pétale à l'arrière : la base de l'oiseau",
    "Dobra pétala atrás: a base do pássaro"), PETAL_B, 2400, 10)

flat_line = flat_check(sheet)
seq, kin_line = program(sheet, ROOT)
print(flat_line)
print(kin_line)

result = pliego.Assembly(
    [sheet],
    controls=[pliego.sequence_control(label=L4(
        "Fold program", "Secuencia de pliegues", "Séquence de pliage", "Sequência de dobras"))],
    sequence=seq,
    targets={"preliminary-base": target(ROOT, PRELIM_STATE), "flat-folded": target(ROOT)},
    title="Bird base",
)
