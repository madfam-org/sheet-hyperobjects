"""Fish base — sheet-hyperobjects cartridge (Pliego).

Two rabbit ears on one diagonal. A square is creased along the diagonal PQ, kite-folded from P and
from Q (and unfolded each time), and then each side corner is rabbit-eared: in the triangle P–R–Q
(R a side corner, the right angle) the bisectors from P and Q meet at the incentre V, the
bisector from R is the flap's ridge, and a swivel runs from V perpendicular to the side RQ. Both
flaps then point toward Q.

Each incentre V is a degree-4 vertex with sectors 67.5°, 135°, 112.5°, 45°: Kawasaki holds
(67.5° + 112.5° = 180°) and three valleys against the mountain ridge satisfy Maekawa. The kite
precreases cross V as well and stay flat in the base. The two vertices share no crease (the
diagonal stays open), so each rabbit ear is one rigid degree of freedom.

The precreases and the two rabbit ears are key poses; `pliego.Sequence.kinematic_path` (the
kernel's motion solver) turns each into exact rigid in-between states. `pliego.flatfold.check`
verifies the folded crease pattern and `pliego.kinematics` the closure of the flat-folded target.
All geometry is computed here; the base is traditional (no designer's diagram is used).
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

s = size
c, sn = math.cos(math.radians(22.5)), math.sin(math.radians(22.5))
r = s / (c + sn)                       # P to the incentre, along the 22.5° bisector
t = s * math.tan(math.radians(22.5))  # where a full kite crease meets the far edge
P0, Q, R1, R2 = (0.0, 0.0), (s, s), (s, 0.0), (0.0, s)
V1, V2 = (r * c, r * sn), (r * sn, r * c)   # incentres of P–R1–Q and P–R2–Q
E1, E2 = (s, V1[1]), (V2[0], s)            # swivel feet on R1–Q and R2–Q
sheet = pliego.Sheet("square", pliego.square(s), stock=stock,
                     label=L4("Square", "Cuadrado", "Carré", "Quadrado"))


SIDE = {"r": L4("right corner", "esquina derecha", "coin de droite", "canto direito"),
        "t": L4("top corner", "esquina superior", "coin du haut", "canto de cima")}


def side_label(en, es, fr, pt, which):
    text = L4(en, es, fr, pt)
    return {k: f"{text[k]} ({SIDE[which][k]})" for k in text}


crease(sheet, "diagonal", P0, Q, "valley", L4(
    "Diagonal (precrease, the axis)", "Diagonal (premarcado, el eje)",
    "Diagonale (prémarquage, l'axe)", "Diagonal (pré-vinco, o eixo)"))
for w, V, R, E, far_p, far_q in (("r", V1, R1, E1, (s, t), (s - t, 0.0)),
                                 ("t", V2, R2, E2, (t, s), (0.0, s - t))):
    crease(sheet, f"bis-p-{w}", P0, V, "valley", side_label(
        "Kite crease from P, to the incentre", "Pliegue de cometa desde P, hasta el incentro",
        "Pli cerf-volant depuis P, jusqu'au centre inscrit",
        "Vinco de pipa desde P, até ao incentro", w))
    crease(sheet, f"ext-p-{w}", V, far_p, "valley", side_label(
        "Kite crease from P, beyond the incentre (precrease)",
        "Pliegue de cometa desde P, más allá del incentro (premarcado)",
        "Pli cerf-volant depuis P, au-delà du centre inscrit (prémarquage)",
        "Vinco de pipa desde P, além do incentro (pré-vinco)", w))
    crease(sheet, f"bis-q-{w}", Q, V, "valley", side_label(
        "Kite crease from Q, to the incentre", "Pliegue de cometa desde Q, hasta el incentro",
        "Pli cerf-volant depuis Q, jusqu'au centre inscrit",
        "Vinco de pipa desde Q, até ao incentro", w))
    crease(sheet, f"ext-q-{w}", V, far_q, "valley", side_label(
        "Kite crease from Q, beyond the incentre (precrease)",
        "Pliegue de cometa desde Q, más allá del incentro (premarcado)",
        "Pli cerf-volant depuis Q, au-delà du centre inscrit (prémarquage)",
        "Vinco de pipa desde Q, além do incentro (pré-vinco)", w))
    crease(sheet, f"ridge-{w}", R, V, "mountain", side_label(
        "Ridge of the flap (bisector of the corner)",
        "Cresta de la solapa (bisectriz de la esquina)",
        "Arête du rabat (bissectrice du coin)", "Crista da aba (bissetriz do canto)", w))
    crease(sheet, f"swivel-{w}", V, E, "valley", side_label(
        "Swivel (perpendicular to the edge)", "Giro (perpendicular al borde)",
        "Pivot (perpendiculaire au bord)", "Giro (perpendicular à aresta)", w))
ROOT = (0.3 * s, 0.2 * s)  # the body between the P kite crease and the diagonal stays down
UNFOLD = L4("Unfold", "Desdobla", "Dépliez", "Desdobre")
KITE_P = {f"{k}-{w}": 180.0 for k in ("bis-p", "ext-p") for w in "rt"}
KITE_Q = {f"{k}-{w}": 180.0 for k in ("bis-q", "ext-q") for w in "rt"}


def rabbit(w):
    return {f"bis-p-{w}": 180.0, f"bis-q-{w}": 180.0, f"swivel-{w}": 180.0,
            f"ridge-{w}": -180.0}


key("fold-diagonal", L4(
    "Coloured side up, valley-fold in half along the diagonal PQ",
    "Con el color hacia arriba, dobla en valle a la mitad por la diagonal PQ",
    "Couleur dessus, pliez en vallée en deux selon la diagonale PQ",
    "Com a cor para cima, dobre em vale ao meio pela diagonal PQ"),
    {"diagonal": 180.0}, 1200, 4)
key("unfold-diagonal", UNFOLD, {"diagonal": 0.0}, 900, 3)
key("kite-from-p", L4(
    "Fold both edges at P onto the diagonal (a kite)",
    "Lleva los dos bordes de P a la diagonal (una cometa)",
    "Rabattez les deux bords de P sur la diagonale (un cerf-volant)",
    "Leve as duas arestas de P até à diagonal (uma pipa)"), KITE_P, 1500, 5)
key("unfold-kite-p", UNFOLD, {k: 0.0 for k in KITE_P}, 900, 3)
key("kite-from-q", L4(
    "Fold both edges at Q onto the diagonal", "Lleva los dos bordes de Q a la diagonal",
    "Rabattez les deux bords de Q sur la diagonale", "Leve as duas arestas de Q até à diagonal"),
    KITE_Q, 1500, 5)
key("unfold-kite-q", UNFOLD, {k: 0.0 for k in KITE_Q}, 900, 3)
key("rabbit-ear-right", L4(
    "Rabbit-ear the right corner: both edges come down onto the diagonal and the corner rises "
    "as a flap, laid toward Q",
    "Haz una oreja de conejo en la esquina derecha: los dos bordes bajan a la diagonal y la "
    "esquina se levanta como una solapa que se acuesta hacia Q",
    "Faites une oreille de lapin au coin de droite : les deux bords descendent sur la diagonale "
    "et le coin se dresse en rabat, couché vers Q",
    "Faça uma orelha de coelho no canto direito: as duas arestas descem até à diagonal e o "
    "canto ergue-se como uma aba, deitada em direção a Q"), rabbit("r"), 2000, 8)
key("rabbit-ear-top", L4(
    "Rabbit-ear the top corner the same way: the fish base",
    "Haz lo mismo con la esquina superior: la base de pez",
    "Faites de même au coin du haut : la base du poisson",
    "Faça o mesmo com o canto de cima: a base do peixe"), rabbit("t"), 2000, 8)

flat_line = flat_check(sheet)
seq, kin_line = program(sheet, ROOT)
print(flat_line)
print(kin_line)

result = pliego.Assembly(
    [sheet],
    controls=[pliego.sequence_control(label=L4(
        "Fold program", "Secuencia de pliegues", "Séquence de pliage", "Sequência de dobras"))],
    sequence=seq,
    targets={"flat-folded": target(ROOT)},
    title="Fish base",
)
