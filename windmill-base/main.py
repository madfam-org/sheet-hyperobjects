"""Windmill base — sheet-hyperobjects cartridge (Pliego).

The windmill (pinwheel) base: a square precreased along its quarter lines, both diagonals and a
blintz, then collapsed so that four triangular flaps stand round a central square in four-fold
rotational symmetry. The central square is half the paper's side; each flap is a corner square
folded in half along its diagonal and swivelled out the same way round.

In the folded state each corner of the central square is a degree-4 vertex: two sides of the
central square (mountains), the outer half of a diagonal (the flap's spine, mountain) and one half
of a blintz line (the swivel, valley), with sectors 90°, 135°, 90°, 45° (Kawasaki holds exactly;
three mountains and one valley satisfy Maekawa). The quarter lines' outer parts, the diagonals'
inner parts and the other blintz halves are precreases, open in the base. This assignment was
found by this cartridge's author as the four-fold symmetric flat-folded state of those creases;
`pliego.flatfold.check` and `pliego.kinematics` verify it on every run.

The collapse swivels paper round the corners; the kernel's motion solver finds no rigid path to it
from the precreased sheet (the swivels need the paper to bend), so the program is physical: key
poses for the engine's paper physics, with the exact flat-folded state as the target frame. All
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


def program_physical(sheet, root):
    """A physical program (spec §5.6): the same key poses, driven by the paper physics. Used
    where no rigid path exists; the flat-folded target is still checked for closure."""
    steps = [pliego.Step(sid, label, [(MARK[k], a) for k, a in moving.items()], duration_ms=ms)
             for sid, label, moving, ms, _ in KEYS]
    arr = sheet.build()
    final = {e: a for k, a in STATE.items() for e in MARK[k].edges()}
    closure = kinematics.closure_residual(arr, final, pliego.P(*root))
    if closure > CLOSURE_TOL_MM:
        raise ValueError(f"the flat-folded target does not close: {closure:.3g} mm")
    return (pliego.Sequence(steps, mode="physical"),
            f"kinematics: physical program steps={len(steps)} target_closure_mm={closure:.2e}")


size = float(PARAM(lambda: size, 150.0))  # noqa: F821
stock = PARAM(lambda: stock, "kami")  # noqa: F821
size = max(80.0, min(300.0, size))

s, q = size, size / 4.0
C = (2 * q, 2 * q)
sheet = pliego.Sheet("square", pliego.square(s), stock=stock,
                     label=L4("Square", "Cuadrado", "Carré", "Quadrado"))


def rot(p, k):
    """Rotate a point k quarter turns counter-clockwise about the centre."""
    x, y = p
    for _ in range(k):
        x, y = 4 * q - y, x
    return (x, y)


# one corner of the inner square, A = (3q, 3q), and its rays; the other three corners are the
# same pattern turned by quarter turns (the base has four-fold rotational symmetry)
A = (3 * q, 3 * q)
SEGS = {  # name: (other end, kind, label)
    "side-a": ((3 * q, q), "mountain", L4(
        "Quarter line, side of the centre square", "Línea de cuarto, lado del cuadrado central",
        "Ligne du quart, côté du carré central", "Linha do quarto, lado do quadrado central")),
    "out-up": ((3 * q, s), "mountain", L4(
        "Quarter line, outer part (precrease)", "Línea de cuarto, parte exterior (premarcado)",
        "Ligne du quart, partie extérieure (prémarquage)",
        "Linha do quarto, parte exterior (pré-vinco)")),
    "out-right": ((s, 3 * q), "mountain", L4(
        "Quarter line, outer part (precrease)", "Línea de cuarto, parte exterior (premarcado)",
        "Ligne du quart, partie extérieure (prémarquage)",
        "Linha do quarto, parte exterior (pré-vinco)")),
    "diag-out": ((s, s), "mountain", L4(
        "Diagonal, outer part (the flap's spine)", "Diagonal, parte exterior (lomo de la solapa)",
        "Diagonale, partie extérieure (dos du rabat)", "Diagonal, parte exterior (lombada da aba)")),
    "diag-in": (C, "mountain", L4(
        "Diagonal, inner part (precrease)", "Diagonal, parte interior (premarcado)",
        "Diagonale, partie intérieure (prémarquage)", "Diagonal, parte interior (pré-vinco)")),
    "blintz-swivel": ((s, 2 * q), "valley", L4(
        "Blintz line, swivel half", "Línea de blintz, mitad del giro",
        "Ligne du blintz, moitié du pivot", "Linha do blintz, metade do giro")),
    "blintz-flat": ((2 * q, s), "valley", L4(
        "Blintz line, other half (precrease)", "Línea de blintz, otra mitad (premarcado)",
        "Ligne du blintz, autre moitié (prémarquage)", "Linha do blintz, outra metade (pré-vinco)")),
}
CORNER = (L4("top right", "superior derecha", "en haut à droite", "superior direita"),
          L4("top left", "superior izquierda", "en haut à gauche", "superior esquerda"),
          L4("bottom left", "inferior izquierda", "en bas à gauche", "inferior esquerda"),
          L4("bottom right", "inferior derecha", "en bas à droite", "inferior direita"))
for k in range(4):
    for nm, (end, kind, lab) in SEGS.items():
        crease(sheet, f"{nm}-{k}", rot(A, k), rot(end, k), kind,
               {g: f"{lab[g]} ({CORNER[k][g]})" for g in lab})
ROOT = (2.15 * q, 1.7 * q)  # a triangle of the centre square stays on the table
UNFOLD = L4("Unfold", "Desdobla", "Dépliez", "Desdobre")


def line(*names):
    return {f"{n}-{k}": None for n in names for k in range(4)}


def group(ks, names, a):
    return {f"{n}-{k}": a for n in names for k in ks}


# cupboard folds: x = q and x = 3q are carried by corners 0 and 2 (side, upper part) and 1 and 3
# (lower part); y = q and y = 3q by the others
VERT = dict(group((0, 2), ("side-a", "out-up"), -180.0), **group((1, 3), ("out-right",), -180.0))
HORZ = dict(group((1, 3), ("side-a", "out-up"), -180.0), **group((0, 2), ("out-right",), -180.0))
DIAG1 = group((0, 2), ("diag-out", "diag-in"), -180.0)
DIAG2 = group((1, 3), ("diag-out", "diag-in"), -180.0)
BLINTZ = group((0, 1, 2, 3), ("blintz-swivel", "blintz-flat"), 180.0)
FINAL = dict(group((0, 1, 2, 3), ("side-a", "diag-out"), -180.0),
             **group((0, 1, 2, 3), ("blintz-swivel",), 180.0))

key("cupboard-vertical", L4(
    "Mountain-fold the left and right edges to the centre line (behind), then unfold",
    "Dobla en monte los bordes izquierdo y derecho hasta la línea central (hacia atrás) y "
    "desdobla",
    "Pliez en montagne les bords gauche et droit sur la ligne médiane (vers l'arrière), puis "
    "dépliez",
    "Dobre em montanha as arestas esquerda e direita até à linha central (para trás) e "
    "desdobre"), VERT, 1200)
key("unfold-vertical", UNFOLD, {n: 0.0 for n in VERT}, 900)
key("cupboard-horizontal", L4(
    "Mountain-fold the top and bottom edges to the centre line, then unfold",
    "Dobla en monte los bordes de arriba y de abajo hasta la línea central y desdobla",
    "Pliez en montagne les bords du haut et du bas sur la ligne médiane, puis dépliez",
    "Dobre em montanha as arestas de cima e de baixo até à linha central e desdobre"),
    HORZ, 1200)
key("unfold-horizontal", UNFOLD, {n: 0.0 for n in HORZ}, 900)
key("fold-diagonal-1", L4(
    "Mountain-fold along a diagonal", "Dobla en monte por una diagonal",
    "Pliez en montagne selon une diagonale", "Dobre em montanha por uma diagonal"), DIAG1, 1200)
key("unfold-diagonal-1", UNFOLD, {n: 0.0 for n in DIAG1}, 900)
key("fold-diagonal-2", L4(
    "Mountain-fold along the other diagonal", "Dobla en monte por la otra diagonal",
    "Pliez en montagne selon l'autre diagonale", "Dobre em montanha pela outra diagonal"),
    DIAG2, 1200)
key("unfold-diagonal-2", UNFOLD, {n: 0.0 for n in DIAG2}, 900)
key("blintz", L4(
    "Fold the four corners to the centre (a blintz)", "Lleva las cuatro esquinas al centro "
    "(un blintz)", "Rabattez les quatre coins au centre (un blintz)",
    "Leve os quatro cantos ao centro (um blintz)"), BLINTZ, 1500)
key("unfold-blintz", UNFOLD, {n: 0.0 for n in BLINTZ}, 900)
key("collapse", L4(
    "Refold the quarter lines all round and swivel each corner out the same way round: the "
    "windmill",
    "Vuelve a doblar las líneas de cuarto alrededor y gira cada esquina hacia fuera en el mismo "
    "sentido: el molinete",
    "Repliez les lignes des quarts tout autour et faites pivoter chaque coin vers l'extérieur "
    "dans le même sens : le moulin",
    "Volte a dobrar as linhas dos quartos à volta e gire cada canto para fora no mesmo sentido: "
    "o cata-vento"), FINAL, 4000)

flat_line = flat_check(sheet)
seq, kin_line = program_physical(sheet, ROOT)
print(flat_line)
print(kin_line)

result = pliego.Assembly(
    [sheet],
    controls=[pliego.sequence_control(label=L4(
        "Fold program", "Secuencia de pliegues", "Séquence de pliage", "Sequência de dobras"))],
    sequence=seq,
    targets={"flat-folded": target(ROOT)},
    title="Windmill base",
)
