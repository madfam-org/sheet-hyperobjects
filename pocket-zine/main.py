"""Pocket zine — sheet-hyperobjects cartridge (Pliego).

The eight-page booklet folded from one sheet with one cut. A landscape sheet is divided into a
4 × 2 grid of pages; one slit runs along the middle line through the two centre columns. The
fold program is kinematic and exact:

1. fold the sheet in half lengthwise, the top half going behind (the `head-fold`);
2. push the ends together: the slit opens into a diamond and then a cross of four wings
   (`spine` creases to 90°, `fore-edge` creases shut);
3. wrap the wings round the spine into a booklet.

The slit makes the eight pages a closed ring of faces around a hole, so the sheet has no interior
vertex and the kernel's vertex closure does not apply; this script checks the loop itself with
`pliego.kinematics.closure_residual` at every state of the program (fail loud).

The imposition is not hard-coded: the script poses the folded booklet, orders the wings along
the stack, takes the cover from the binding side and numbers every face from the stack order,
then checks the result against the classic template (front cover top left) and checks that
every page's head points the same way. The page numbers are written into the step notes and
printed on the read-proof line.
"""

import math

import pliego


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


sheet_width = float(PARAM(lambda: sheet_width, 297.0))      # noqa: F821
sheet_height = float(PARAM(lambda: sheet_height, 210.0))    # noqa: F821
stock = PARAM(lambda: stock, "copy-80")                     # noqa: F821
binding = PARAM(lambda: binding, "left")                    # noqa: F821

STOCKS = ("copy-80", "kraft-120")
if stock not in STOCKS:
    raise ValueError(f"pocket-zine: stock must be one of {STOCKS}, got {stock!r}")
if binding not in ("left", "right"):
    raise ValueError(f"pocket-zine: binding must be left or right, got {binding!r}")

W = pliego.clamp(sheet_width, 180.0, 600.0)
H = pliego.clamp(sheet_height, 120.0, 450.0)
if H > W:
    raise ValueError("pocket-zine: the sheet is laid landscape (width ≥ height)")
w, h = W / 4.0, H / 2.0          # one page
GAP = 2.0                        # wrapped wings are left this many degrees apart (paper thickness)
SUB = 4                          # exact substeps per key step


def L4(en, es, fr, pt):
    return {"en": en, "es": es, "fr": fr, "pt": pt}


sheet = pliego.Sheet("zine", [(0, 0), (W, 0), (W, H), (0, H)], stock=stock, grain_deg=0.0,
                     label=L4("Zine sheet", "Hoja del fanzine", "Feuille du fanzine",
                              "Folha do fanzine"))
# The head fold: the outer columns' middle line, the top half going behind (mountain).
head = [sheet.mountain((0, h), (w, h), name="head-fold"),
        sheet.mountain((3 * w, h), (W, h), name="head-fold")]
slit = sheet.cut([(w, h), (3 * w, h)], name="slit")
# Vertical folds, one mark per row (the rows move differently once the slit opens).
spine_lb = sheet.valley((w, 0), (w, h), name="spine")
spine_lt = sheet.valley((w, h), (w, H), name="spine")
fore_b = sheet.mountain((2 * w, 0), (2 * w, h), name="fore-edge")
fore_t = sheet.mountain((2 * w, h), (2 * w, H), name="fore-edge")
spine_rb = sheet.valley((3 * w, 0), (3 * w, h), name="spine")
spine_rt = sheet.valley((3 * w, h), (3 * w, H), name="spine")

# Key poses. After step 2 the four wings stand as a cross around the spine (90° apart): left
# (column 1, both rows), front (columns 2–3 of the bottom row), right (column 4, both rows) and
# back (columns 2–3 of the top row). Step 3 lays front, then left, onto the right wing and the
# back wing under it, GAP degrees apart; the hinge between back and left wraps round the stack
# (−(180 − 3·GAP)) so the ring of faces stays closed.
STEP = {
    "half": (L4("Fold in half lengthwise, top half behind",
                "Dobla a lo largo por la mitad, la mitad de arriba hacia atrás",
                "Pliez en deux dans la longueur, la moitié du haut derrière",
                "Dobre ao meio no comprimento, a metade de cima para trás"),
             [(m, -180.0) for m in head]),
    "push": (L4("Push the ends together: the slit opens into a cross",
                "Empuja los extremos hacia el centro: la ranura se abre en cruz",
                "Poussez les extrémités l'une vers l'autre : la fente s'ouvre en croix",
                "Empurre as pontas uma contra a outra: a fenda abre-se em cruz"),
             [(spine_lb, 90.0), (spine_lt, 90.0), (spine_rb, 90.0), (spine_rt, 90.0),
              (fore_b, -180.0), (fore_t, -180.0)]),
    "wrap": (L4("Wrap the wings round the spine into a booklet",
                "Envuelve las alas alrededor del lomo para formar el cuadernillo",
                "Rabattez les ailes autour du dos pour former le livret",
                "Envolva as asas em volta da lombada para formar o livrinho"),
             [(spine_lb, 180.0 - GAP), (spine_rb, 180.0 - GAP), (spine_rt, 180.0 - GAP),
              (spine_lt, -(180.0 - 3 * GAP))]),
}

arr = sheet.build()


def angles_of(pairs):
    out = {}
    for mark, ang in pairs:
        for e in mark.edges():
            out[e] = ang
    return out


# ── the imposition, computed from the folded booklet ─────────────────────────


def mat_vec(m, v):
    return tuple(m[i][0] * v[0] + m[i][1] * v[1] + m[i][2] * v[2] for i in range(3))


def world(tr, u, v):
    p = mat_vec(tr[0], (u, 0.0, -v))
    return (p[0] + tr[1][0], p[1] + tr[1][1], p[2] + tr[1][2])


def sub3(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def dot3(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def cross3(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


cells = {}                       # face index → (column, row)
for fi, f in enumerate(arr.faces):
    cx = math.fsum(arr.vertices[v].x for v in f) / len(f)
    cy = math.fsum(arr.vertices[v].y for v in f) / len(f)
    cells[fi] = (int(cx // w), int(cy // h))
if sorted(cells.values()) != [(c, r) for c in range(4) for r in range(2)]:
    raise ValueError("pocket-zine: the sheet did not divide into a 4 × 2 grid of pages")

half = angles_of(STEP["half"][1])
cross = {**half, **angles_of(STEP["push"][1])}
done = {**cross, **angles_of(STEP["wrap"][1])}
done_tr = pliego.kinematics.face_transforms(arr, done, 0)
normal = {fi: mat_vec(done_tr[fi][0], (0.0, 1.0, 0.0)) for fi in cells}
spine_a = world(done_tr[0], w, 0.0)
# The wrapped wings lie GAP degrees apart round the spine, so their centres are apart along the
# stack normal; the two layers of one wing coincide (their fore-edge fold is shut).
centre = {fi: world(done_tr[fi], (cells[fi][0] + 0.5) * w, (cells[fi][1] + 0.5) * h)
          for fi in cells}
ref = normal[0]
level = {fi: dot3(centre[fi], ref) for fi in cells}
order = sorted(cells, key=lambda fi: (round(level[fi], 6), dot3(normal[fi], ref)))
# Faces with the same level are the two layers of one wing; the higher level is the top.
stack = list(reversed(order))    # top (largest level along ref) first
for k in range(0, 8, 2):
    a, b = stack[k], stack[k + 1]
    if abs(level[a] - level[b]) > 1e-6 or dot3(normal[a], ref) < dot3(normal[b], ref):
        raise ValueError("pocket-zine: the wings did not stack as double layers")


def head_dir(fi):
    col, row = cells[fi]
    toward = (0.0, 1.0) if row == 0 else (0.0, -1.0)    # every page's head is the head fold
    a = world(done_tr[fi], (col + 0.5) * w, (row + 0.5) * h)
    b = world(done_tr[fi], (col + 0.5) * w + toward[0], (row + 0.5) * h + toward[1])
    return sub3(b, a)


up = head_dir(stack[0])
for fi in cells:
    if dot3(head_dir(fi), up) < 1.0 - 1e-9:
        raise ValueError("pocket-zine: the pages' heads do not all point the same way")


def spine_side(fi, outward):
    right = cross3(up, outward)
    c = world(done_tr[fi], (cells[fi][0] + 0.5) * w, (cells[fi][1] + 0.5) * h)
    return "left" if dot3(sub3(spine_a, c), right) < 0 else "right"


outer = {"top": (stack[0], ref), "bottom": (stack[-1], tuple(-x for x in ref))}
cover_end = next(k for k, (fi, out) in outer.items() if spine_side(fi, out) == binding)
pages_in_order = stack if cover_end == "top" else list(reversed(stack))
page = {fi: k + 1 for k, fi in enumerate(pages_in_order)}
grid = {cells[fi]: page[fi] for fi in cells}
bottom_row = [grid[(c, 0)] for c in range(4)]
top_row = [grid[(c, 1)] for c in range(4)]
EXPECTED = {"left": ([2, 3, 4, 5], [1, 8, 7, 6]), "right": ([7, 6, 5, 4], [8, 1, 2, 3])}
if (bottom_row, top_row) != EXPECTED[binding]:
    raise ValueError(f"pocket-zine: imposition {bottom_row}/{top_row} is not the classic "
                     f"template {EXPECTED[binding]}")

# ── the fold program ─────────────────────────────────────────────────────────

b_txt = " ".join(str(p) for p in bottom_row)
t_txt = " ".join(str(p) for p in top_row)
NOTES = {
    "half": L4(f"The slit is cut first. Print the pages on the front: bottom row {b_txt}, top "
               f"row upside down {t_txt} (left to right).",
               f"La ranura se corta primero. Imprime las páginas en el anverso: fila de abajo "
               f"{b_txt}; fila de arriba, de cabeza, {t_txt} (de izquierda a derecha).",
               f"La fente se coupe d'abord. Imprimez les pages au recto : rangée du bas "
               f"{b_txt} ; rangée du haut, tête en bas, {t_txt} (de gauche à droite).",
               f"A fenda corta-se primeiro. Imprima as páginas na frente: fila de baixo "
               f"{b_txt}; fila de cima, de cabeça para baixo, {t_txt} (da esquerda para a "
               "direita)."),
    "wrap": L4("Pages now read 1 to 8 in order; the head fold is the top edge.",
               "Ahora las páginas se leen en orden del 1 al 8; el doblez de cabeza es el canto "
               "superior.",
               "Les pages se lisent maintenant dans l'ordre de 1 à 8 ; le pli de tête est le "
               "bord supérieur.",
               "Agora as páginas leem-se em ordem de 1 a 8; a dobra de cabeça é a borda de "
               "cima."),
}
key_steps = [pliego.Step(sid, STEP[sid][0], STEP[sid][1], duration_ms=2400,
                         note=NOTES.get(sid)) for sid in ("half", "push", "wrap")]
program = pliego.Sequence.kinematic_path(sheet, key_steps, substeps=SUB)

# Loop closure round the slit at every state of the program (the kernel checks vertex loops only).
state = {}
worst = 0.0
for st in program.steps:
    for t, ang in st.targets:
        state[t.edge] = ang          # kinematic_path targets are EdgeRefs
    worst = max(worst, pliego.kinematics.closure_residual(arr, state))
if worst > 1e-6:
    raise ValueError(f"pocket-zine: the ring of pages does not close ({worst:.3g} mm)")

print(f"zine: sheet={W:g}x{H:g}mm page={w:g}x{h:g}mm binding={binding} "
      f"imposition=bottom[{b_txt}] top-inverted[{t_txt}] closure={worst:.1e}mm "
      f"steps={len(program.steps)}")

result = pliego.Assembly(
    [sheet],
    controls=[pliego.sequence_control(label=L4("Fold the zine", "Doblar el fanzine",
                                               "Plier le fanzine", "Dobrar o fanzine"))],
    sequence=program,
    title="Pocket zine",
)
