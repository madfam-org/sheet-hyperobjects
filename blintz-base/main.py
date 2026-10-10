"""Blintz base — sheet-hyperobjects cartridge (Pliego).

The blintzed square: the four corners of a square folded to its centre (a single blintz), and,
with `blintz = "double"`, the four new corners folded to the centre again. The name comes from the
pastry folded the same way.

A single blintz is four creases joining the edge midpoints. They meet only on the boundary, so
every corner fold is an independent hinge. The double blintz folds the half-size square again, now
through two layers: each new fold line crosses the base and two folded corners, so its crease
pattern is a valley segment on the base and two mountain segments on the flipped corner flaps. The
segments line up into the four quarter lines of the square. Where they meet the first blintz the
pattern has four degree-6 vertices with sectors 90°, 45°, 45°, 90°, 45°, 45° (Kawasaki holds
exactly; four valleys and two mountains satisfy Maekawa).

Every key pose is a flat-folded state; `pliego.Sequence.kinematic_path` (the kernel's motion
solver) turns each into exact rigid in-between states. `pliego.flatfold.check` verifies the folded
crease pattern and `pliego.kinematics` the closure of the flat-folded target. All geometry is
computed here; the fold is traditional (no designer's diagram is used).
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
blintz = PARAM(lambda: blintz, "single")  # noqa: F821
size = max(80.0, min(300.0, size))
if blintz not in ("single", "double"):
    raise ValueError(f"blintz must be 'single' or 'double', not {blintz!r}")

s, h, q = size, size / 2.0, size / 4.0
E, N, W, S = (s, h), (h, s), (0.0, h), (h, 0.0)
sheet = pliego.Sheet("square", pliego.square(s), stock=stock,
                     label=L4("Square", "Cuadrado", "Carré", "Quadrado"))
crease(sheet, "book-ew", W, E, "valley", L4(
    "Book fold, side to side (precrease, finds the centre)",
    "Pliegue de libro, de lado a lado (premarcado, marca el centro)",
    "Pli livre, d'un côté à l'autre (prémarquage, trouve le centre)",
    "Dobra de livro, de lado a lado (pré-vinco, marca o centro)"))
crease(sheet, "book-ns", S, N, "valley", L4(
    "Book fold, top to bottom (precrease)", "Pliegue de libro, de arriba abajo (premarcado)",
    "Pli livre, de haut en bas (prémarquage)", "Dobra de livro, de cima para baixo (pré-vinco)"))
CORNERS = (("ne", E, N, L4("top right", "superior derecha", "en haut à droite",
                          "superior direito")),
           ("nw", N, W, L4("top left", "superior izquierda", "en haut à gauche",
                           "superior esquerdo")),
           ("sw", W, S, L4("bottom left", "inferior izquierda", "en bas à gauche",
                           "inferior esquerdo")),
           ("se", S, E, L4("bottom right", "inferior derecha", "en bas à droite",
                           "inferior direito")))
for c, a, b, where in CORNERS:
    crease(sheet, f"blintz-{c}", a, b, "valley", {
        "en": f"First blintz, {where['en']} corner", "es": f"Primer blintz, esquina {where['es']}",
        "fr": f"Premier blintz, coin {where['fr']}", "pt": f"Primeiro blintz, canto {where['pt']}"})

# double blintz: each new corner (an edge midpoint) folds to the centre along a quarter line;
# (base segment, flap segment, flap segment) — the flaps are the first blintz's corners
SECOND = {
    "n": (((q, 3 * q), (3 * q, 3 * q)), ((3 * q, 3 * q), (3 * q, s)), ((q, 3 * q), (q, s))),
    "e": (((3 * q, q), (3 * q, 3 * q)), ((3 * q, 3 * q), (s, 3 * q)), ((3 * q, q), (s, q))),
    "s": (((q, q), (3 * q, q)), ((3 * q, q), (3 * q, 0.0)), ((q, q), (q, 0.0))),
    "w": (((q, q), (q, 3 * q)), ((q, 3 * q), (0.0, 3 * q)), ((q, q), (0.0, q))),
}
SIDE2 = {"n": L4("top", "de arriba", "du haut", "de cima"),
         "e": L4("right", "derecha", "de droite", "direita"),
         "s": L4("bottom", "de abajo", "du bas", "de baixo"),
         "w": L4("left", "izquierda", "de gauche", "esquerda")}
if blintz == "double":
    for c, (base, f1, f2) in SECOND.items():
        w = SIDE2[c]
        crease(sheet, f"second-{c}", *base, "valley", {
            "en": f"Second blintz, {w['en']} corner (base layer)",
            "es": f"Segundo blintz, esquina {w['es']} (capa de base)",
            "fr": f"Second blintz, coin {w['fr']} (couche de base)",
            "pt": f"Segundo blintz, canto {w['pt']} (camada de base)"})
        for i, seg in enumerate((f1, f2), 1):
            crease(sheet, f"second-{c}-flap{i}", *seg, "mountain", {
                "en": f"Second blintz, {w['en']} corner (through a folded corner)",
                "es": f"Segundo blintz, esquina {w['es']} (a través de una esquina doblada)",
                "fr": f"Second blintz, coin {w['fr']} (à travers un coin replié)",
                "pt": f"Segundo blintz, canto {w['pt']} (através de um canto dobrado)"})
ROOT = (0.45 * s, 0.45 * s)  # the middle of the base layer never moves
UNFOLD = L4("Unfold", "Desdobla", "Dépliez", "Desdobre")

key("fold-book-ew", L4(
    "Valley-fold in half, side to side", "Dobla en valle a la mitad, de lado a lado",
    "Pliez en vallée en deux, d'un côté à l'autre", "Dobre em vale ao meio, de lado a lado"),
    {"book-ew": 180.0}, 1200, 4)
key("unfold-book-ew", UNFOLD, {"book-ew": 0.0}, 900, 3)
key("fold-book-ns", L4(
    "Valley-fold in half, top to bottom", "Dobla en valle a la mitad, de arriba abajo",
    "Pliez en vallée en deux, de haut en bas", "Dobre em vale ao meio, de cima para baixo"),
    {"book-ns": 180.0}, 1200, 4)
key("unfold-book-ns", UNFOLD, {"book-ns": 0.0}, 900, 3)
for c, _, _, where in CORNERS:
    key(f"corner-{c}", {
        "en": f"Fold the {where['en']} corner to the centre",
        "es": f"Lleva la esquina {where['es']} al centro",
        "fr": f"Rabattez le coin {where['fr']} au centre",
        "pt": f"Leve o canto {where['pt']} ao centro"}, {f"blintz-{c}": 180.0}, 1200, 5)
SINGLE = dict(STATE)
if blintz == "double":
    for c in SECOND:
        w = SIDE2[c]
        key(f"second-corner-{c}", {
            "en": f"Fold the new {w['en']} corner to the centre, through both layers",
            "es": f"Lleva la nueva esquina {w['es']} al centro, a través de las dos capas",
            "fr": f"Rabattez le nouveau coin {w['fr']} au centre, à travers les deux couches",
            "pt": f"Leve o novo canto {w['pt']} ao centro, através das duas camadas"},
            {f"second-{c}": 180.0, f"second-{c}-flap1": -180.0, f"second-{c}-flap2": -180.0},
            1500, 6)

flat_line = flat_check(sheet)
seq, kin_line = program(sheet, ROOT)
print(flat_line)
print(kin_line)

targets = {"flat-folded": target(ROOT)}
if blintz == "double":
    targets["single-blintz"] = target(ROOT, SINGLE)
result = pliego.Assembly(
    [sheet],
    controls=[pliego.sequence_control(label=L4(
        "Fold program", "Secuencia de pliegues", "Séquence de pliage", "Sequência de dobras"))],
    sequence=seq,
    targets=targets,
    title="Blintz base",
)
