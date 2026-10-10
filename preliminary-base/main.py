"""Preliminary base — sheet-hyperobjects cartridge (Pliego).

The square base of origami: a square is precreased along one diagonal and both book folds, then
collapsed so that all four corners meet at the bottom and the centre becomes the closed top
point. Every crease meets the centre O, so the base is one vertex of degree 6: the four
book-fold rays and the two halves of one diagonal. The other diagonal stays flat; it runs down
the middle of the front and back flaps. Sectors 90°, 45°, 45°, 90°, 45°, 45° satisfy Kawasaki's
condition, and four creases of one kind against two of the other satisfy Maekawa's.

`colour` chooses which side ends up outside. With the coloured side out the book folds are
mountains and the diagonal a valley, seen from the coloured side; with it in, every assignment
flips (the same base, folded from the other side of the paper).

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
colour = PARAM(lambda: colour, "out")  # noqa: F821
size = max(80.0, min(300.0, size))
if colour not in ("out", "in"):
    raise ValueError(f"colour must be 'out' or 'in', not {colour!r}")
BOOK, DIAG = ("mountain", "valley") if colour == "out" else ("valley", "mountain")
SB, SD = (-180.0, 180.0) if colour == "out" else (180.0, -180.0)

s, h = size, size / 2.0
O = (h, h)
sheet = pliego.Sheet("square", pliego.square(s), stock=stock,
                     label=L4("Square", "Cuadrado", "Carré", "Quadrado"))

crease(sheet, "book-e", O, (s, h), BOOK, L4("Book fold (E half)", "Pliegue de libro (mitad E)",
                                       "Pli livre (moitié E)", "Dobra de livro (metade E)"))
crease(sheet, "book-n", O, (h, s), BOOK, L4("Book fold (N half)", "Pliegue de libro (mitad N)",
                                       "Pli livre (moitié N)", "Dobra de livro (metade N)"))
crease(sheet, "diag-nw", O, (0.0, s), DIAG, L4("Diagonal (NW half)", "Diagonal (mitad NO)",
                                          "Diagonale (moitié NO)", "Diagonal (metade NO)"))
crease(sheet, "book-w", O, (0.0, h), BOOK, L4("Book fold (W half)", "Pliegue de libro (mitad O)",
                                         "Pli livre (moitié O)", "Dobra de livro (metade O)"))
crease(sheet, "book-s", O, (h, 0.0), BOOK, L4("Book fold (S half)", "Pliegue de libro (mitad S)",
                                         "Pli livre (moitié S)", "Dobra de livro (metade S)"))
crease(sheet, "diag-se", O, (s, 0.0), DIAG, L4("Diagonal (SE half)", "Diagonal (mitad SE)",
                                          "Diagonale (moitié SE)", "Diagonal (metade SE)"))
ROOT = (0.25 * s, 0.25 * s)  # the back flap (SW quadrant) stays on the table

side = (L4("coloured side up", "con el color hacia arriba", "couleur dessus",
           "com a cor para cima") if colour == "out" else
        L4("white side up", "con el lado blanco hacia arriba", "côté blanc dessus",
           "com o lado branco para cima"))
VERB = {"valley": L4("Valley-fold", "Dobla en valle", "Pliez en vallée", "Dobre em vale"),
        "mountain": L4("Mountain-fold", "Dobla en monte", "Pliez en montagne",
                       "Dobre em montanha")}


def says(verb, what):
    return {k: f"{verb[k]} {what[k]}" for k in verb}


key("fold-diagonal", says(VERB[DIAG], L4(
    f"along the diagonal, {side['en']}", f"por la diagonal, {side['es']}",
    f"selon la diagonale, {side['fr']}", f"pela diagonal, {side['pt']}")),
    {"diag-nw": SD, "diag-se": SD}, 1200, 4)
key("unfold-diagonal", L4("Unfold", "Desdobla", "Dépliez", "Desdobre"),
      {"diag-nw": 0.0, "diag-se": 0.0}, 900, 3)
key("fold-book-ew", says(VERB[BOOK], L4("in half, top to bottom",
                                          "a la mitad, de arriba abajo",
                                          "en deux, de haut en bas", "ao meio, de cima para baixo")),
      {"book-e": SB, "book-w": SB}, 1200, 4)
key("unfold-book-ew", L4("Unfold", "Desdobla", "Dépliez", "Desdobre"),
      {"book-e": 0.0, "book-w": 0.0}, 900, 3)
key("fold-book-ns", says(VERB[BOOK], L4("in half, side to side",
                                          "a la mitad, de lado a lado",
                                          "en deux, d'un côté à l'autre", "ao meio, de lado a lado")),
      {"book-n": SB, "book-s": SB}, 1200, 4)
key("unfold-book-ns", L4("Unfold", "Desdobla", "Dépliez", "Desdobre"),
      {"book-n": 0.0, "book-s": 0.0}, 900, 3)
key("collapse", L4(
    "Bring the four corners down together: the centre rises to the closed top point",
    "Junta las cuatro esquinas abajo: el centro sube y forma la punta cerrada",
    "Réunissez les quatre coins en bas : le centre devient la pointe fermée du haut",
    "Junte os quatro cantos em baixo: o centro sobe e forma a ponta fechada"),
    {"book-e": SB, "book-n": SB, "book-w": SB, "book-s": SB, "diag-nw": SD, "diag-se": SD},
    2400, 12)

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
    title="Preliminary base",
)
