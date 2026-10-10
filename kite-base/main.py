"""Kite base — sheet-hyperobjects cartridge (Pliego).

The simplest base: a square is creased along a diagonal and unfolded, and the two edges at one
corner are folded onto that diagonal. Each kite crease bisects the 45° angle between an edge and
the diagonal, so it leaves the corner at 22.5° to its edge and meets the opposite edge at
size·(√2 − 1) from the far corner. The creases meet only at the corner, on the boundary, so the
pattern has no interior vertex: every crease folds on its own, and the base is a set of plain
hinges.

The precrease and the two kite folds are key poses; `pliego.Sequence.kinematic_path` (the
kernel's motion solver) turns each into exact rigid in-between states, and
`pliego.kinematics` checks the closure of the flat-folded target. All geometry is computed here;
the base is traditional (no designer's diagram is used).
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
t = s * math.tan(math.radians(22.5))  # = s·(√2 − 1)
P0, Q = (0.0, 0.0), (s, s)
sheet = pliego.Sheet("square", pliego.square(s), stock=stock,
                     label=L4("Square", "Cuadrado", "Carré", "Quadrado"))
crease(sheet, "diagonal", P0, Q, "valley", L4(
    "Diagonal (precrease, the kite's axis)", "Diagonal (premarcado, el eje de la cometa)",
    "Diagonale (prémarquage, l'axe du cerf-volant)", "Diagonal (pré-vinco, o eixo da pipa)"))
crease(sheet, "kite-lower", P0, (s, t), "valley", L4(
    "Kite fold (lower edge to the diagonal)", "Pliegue de cometa (borde inferior a la diagonal)",
    "Pli cerf-volant (bord inférieur sur la diagonale)",
    "Dobra de pipa (aresta inferior até à diagonal)"))
crease(sheet, "kite-left", P0, (t, s), "valley", L4(
    "Kite fold (left edge to the diagonal)", "Pliegue de cometa (borde izquierdo a la diagonal)",
    "Pli cerf-volant (bord gauche sur la diagonale)",
    "Dobra de pipa (aresta esquerda até à diagonal)"))
ROOT = (0.62 * s, 0.5 * s)  # the kite's body below the diagonal stays on the table

key("fold-diagonal", L4(
    "Coloured side up, valley-fold in half along the diagonal",
    "Con el color hacia arriba, dobla en valle a la mitad por la diagonal",
    "Couleur dessus, pliez en vallée en deux selon la diagonale",
    "Com a cor para cima, dobre em vale ao meio pela diagonal"),
    {"diagonal": 180.0}, 1200, 4)
key("unfold-diagonal", L4("Unfold", "Desdobla", "Dépliez", "Desdobre"),
    {"diagonal": 0.0}, 900, 3)
key("fold-lower-edge", L4(
    "Fold the lower edge onto the diagonal", "Lleva el borde inferior a la diagonal",
    "Rabattez le bord inférieur sur la diagonale", "Leve a aresta inferior até à diagonal"),
    {"kite-lower": 180.0}, 1500, 6)
key("fold-left-edge", L4(
    "Fold the left edge onto the diagonal: the kite", "Lleva el borde izquierdo a la diagonal: la "
    "cometa", "Rabattez le bord gauche sur la diagonale : le cerf-volant",
    "Leve a aresta esquerda até à diagonal: a pipa"),
    {"kite-left": 180.0}, 1500, 6)

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
    title="Kite base",
)
