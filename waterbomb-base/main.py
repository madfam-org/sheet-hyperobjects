"""Waterbomb base — sheet-hyperobjects cartridge (Pliego).

The triangle base of origami, the preliminary base turned inside out. Both diagonals and one book
fold are precreased, and the square collapses into a right isosceles triangle: the centre O is
the apex and the corners meet in pairs at the two base corners. Every crease meets O, so the base
is one vertex of degree 6: the four diagonal rays and the two halves of one book fold, with
sectors 45°, 45°, 90°, 45°, 45°, 90°. Kawasaki's condition holds exactly (axis-parallel and ±45°
slopes), and four mountains against two valleys satisfy Maekawa's.

The precreases and the collapse are key poses; `pliego.Sequence.kinematic_path` (the kernel's
motion solver) turns each into exact rigid in-between states. `pliego.flatfold.check` verifies
the folded crease pattern and `pliego.kinematics` the closure of the flat-folded target. All
geometry is computed here; the base is traditional (no designer's diagram is used).
"""

import math  # noqa: F401 - the sandbox provides it; kept for parity with sibling cartridges

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
O = (h, h)
sheet = pliego.Sheet("square", pliego.square(s), stock=stock,
                     label=L4("Square", "Cuadrado", "Carré", "Quadrado"))
# coloured side out: seen from the coloured side the diagonals are mountains, the book fold a valley
crease(sheet, "book-e", O, (s, h), "valley", L4(
    "Book fold (E half)", "Pliegue de libro (mitad E)", "Pli livre (moitié E)",
    "Dobra de livro (metade E)"))
crease(sheet, "diag-ne", O, (s, s), "mountain", L4(
    "Diagonal (NE half)", "Diagonal (mitad NE)", "Diagonale (moitié NE)", "Diagonal (metade NE)"))
crease(sheet, "diag-nw", O, (0.0, s), "mountain", L4(
    "Diagonal (NW half)", "Diagonal (mitad NO)", "Diagonale (moitié NO)", "Diagonal (metade NO)"))
crease(sheet, "book-w", O, (0.0, h), "valley", L4(
    "Book fold (W half)", "Pliegue de libro (mitad O)", "Pli livre (moitié O)",
    "Dobra de livro (metade O)"))
crease(sheet, "diag-sw", O, (0.0, 0.0), "mountain", L4(
    "Diagonal (SW half)", "Diagonal (mitad SO)", "Diagonale (moitié SO)", "Diagonal (metade SO)"))
crease(sheet, "diag-se", O, (s, 0.0), "mountain", L4(
    "Diagonal (SE half)", "Diagonal (mitad SE)", "Diagonale (moitié SE)", "Diagonal (metade SE)"))
ROOT = (h, 0.2 * s)  # the front triangle (the S quarter) stays on the table
UNFOLD = L4("Unfold", "Desdobla", "Dépliez", "Desdobre")

key("fold-diagonal-1", L4(
    "Mountain-fold along a diagonal (fold it behind)",
    "Dobla en monte por una diagonal (hacia atrás)",
    "Pliez en montagne selon une diagonale (vers l'arrière)",
    "Dobre em montanha por uma diagonal (para trás)"),
    {"diag-ne": -180.0, "diag-sw": -180.0}, 1200, 4)
key("unfold-diagonal-1", UNFOLD, {"diag-ne": 0.0, "diag-sw": 0.0}, 900, 3)
key("fold-diagonal-2", L4(
    "Mountain-fold along the other diagonal", "Dobla en monte por la otra diagonal",
    "Pliez en montagne selon l'autre diagonale", "Dobre em montanha pela outra diagonal"),
    {"diag-nw": -180.0, "diag-se": -180.0}, 1200, 4)
key("unfold-diagonal-2", UNFOLD, {"diag-nw": 0.0, "diag-se": 0.0}, 900, 3)
key("fold-book", L4(
    "Valley-fold in half, top edge to bottom edge",
    "Dobla en valle a la mitad, del borde de arriba al de abajo",
    "Pliez en vallée en deux, bord du haut sur bord du bas",
    "Dobre em vale ao meio, da aresta de cima para a de baixo"),
    {"book-e": 180.0, "book-w": 180.0}, 1200, 4)
key("unfold-book", UNFOLD, {"book-e": 0.0, "book-w": 0.0}, 900, 3)
key("collapse", L4(
    "Push the side midpoints in: the sides fold inside and the square becomes a triangle",
    "Empuja hacia dentro los puntos medios de los lados: los costados se meten y el cuadrado se "
    "vuelve un triángulo",
    "Rentrez les milieux des côtés : les côtés se replient à l'intérieur et le carré devient un "
    "triangle",
    "Empurre para dentro os pontos médios dos lados: as laterais entram e o quadrado vira um "
    "triângulo"),
    {"book-e": 180.0, "book-w": 180.0, "diag-ne": -180.0, "diag-nw": -180.0,
     "diag-sw": -180.0, "diag-se": -180.0}, 2400, 12)

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
    title="Waterbomb base",
)
