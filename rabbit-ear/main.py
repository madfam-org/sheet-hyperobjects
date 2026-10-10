"""Rabbit ear — sheet-hyperobjects cartridge (Pliego).

A triangle ABC (base AC) is rabbit-eared: the angle bisectors from A, B and C meet at the incentre
I, and a fourth crease — the swivel — runs from I perpendicular to side BC, to the incircle's
touch point E. Edges AB and CB come down onto the base, the corner B rises as a flap pinched along
IB, and the flap swings over towards C.

The four creases at I make a flat-foldable degree-4 vertex. With the bisector angles of a
triangle the sectors are (90° − B/2, 90° + C/2, 90° + B/2, 90° − C/2) counter-clockwise from IE,
so opposite sectors add to 180° (Kawasaki). The rabbit ear is mode 1 of the Foschi–Hull–Ku closed
forms in `pliego.kinematics` (IE = IA, IB = −IC): three valleys and a mountain on IB. For IB to
come out a mountain the apex angle B must exceed C (otherwise the same mode lays the flap the
other way), which the script enforces.

All geometry is computed here; the move is traditional (no designer's diagram is used).
"""

import math

import pliego
from pliego import kinematics


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


base = float(PARAM(lambda: base, 200.0))
angle_a = float(PARAM(lambda: angle_a, 45.0))
angle_c = float(PARAM(lambda: angle_c, 45.0))
stock = PARAM(lambda: stock, "kami")

base = max(100.0, min(300.0, base))
angle_a = max(30.0, min(75.0, angle_a))
angle_c = max(25.0, min(60.0, angle_c))
if 180.0 - angle_a - angle_c <= angle_c + 2.0:
    raise ValueError(f"rabbit ear needs the apex angle B = {180.0 - angle_a - angle_c:.1f}° to "
                     f"exceed C = {angle_c:.1f}° by at least 2° (constraint angle_a + 2·angle_c "
                     "≤ 178)")
COLLAPSE_STEPS = 8
TOL_MM = 1e-5  # mm; vertex coordinates are grid-snapped by the arrangement


def L4(en, es, fr, pt):
    return {"en": en, "es": es, "fr": fr, "pt": pt}


# ── geometry: triangle, incentre, touch point on BC ──────────────────────────

ta, tc = math.tan(math.radians(angle_a)), math.tan(math.radians(angle_c))
apex_x = base * tc / (ta + tc)
A, C, B = (0.0, 0.0), (base, 0.0), (apex_x, apex_x * ta)
side_a, side_b, side_c = math.dist(B, C), math.dist(A, C), math.dist(A, B)
per = side_a + side_b + side_c
I = ((side_a * A[0] + side_b * B[0] + side_c * C[0]) / per,
     (side_a * A[1] + side_b * B[1] + side_c * C[1]) / per)
bc = (C[0] - B[0], C[1] - B[1])
t = ((I[0] - B[0]) * bc[0] + (I[1] - B[1]) * bc[1]) / (bc[0] ** 2 + bc[1] ** 2)
E = (B[0] + t * bc[0], B[1] + t * bc[1])
angle_b = 180.0 - angle_a - angle_c

sheet = pliego.Sheet(
    "triangle", [A, C, B], stock=stock,
    label=L4("Triangle", "Triángulo", "Triangle", "Triângulo"),
    front="#f4efe6", back="#3d7ac8",
)
# CCW around I starting at the swivel: e1 IE, e2 IB, e3 IA, e4 IC
swivel = sheet.valley(I, E, label=L4("Swivel (to the incircle's touch point)",
                                     "Giro (hasta el punto de tangencia del incírculo)",
                                     "Pivot (jusqu'au point de contact du cercle inscrit)",
                                     "Giro (até ao ponto de tangência do incírculo)"))
pinch = sheet.mountain(I, B, label=L4("Bisector of B (the flap's ridge)",
                                      "Bisectriz de B (la cresta de la solapa)",
                                      "Bissectrice de B (l'arête du rabat)",
                                      "Bissetriz de B (a crista da aba)"))
fold_a = sheet.valley(I, A, label=L4("Bisector of A", "Bisectriz de A", "Bissectrice de A",
                                     "Bissetriz de A"))
fold_c = sheet.valley(I, C, label=L4("Bisector of C", "Bisectriz de C", "Bissectrice de C",
                                     "Bissetriz de C"))
CREASES = (swivel, pinch, fold_a, fold_c)
arr = sheet.build()
EDGE = [m.edges()[0] for m in CREASES]
ROOT = pliego.P((A[0] + C[0] + I[0]) / 3.0, I[1] / 3.0)  # the base face A–I–C stays down

ALPHA1, ALPHA2 = 90.0 - angle_b / 2.0, 90.0 + angle_c / 2.0  # sectors E→B and B→A


def mode1(drive):
    return kinematics.degree4_mode1(ALPHA1, ALPHA2, drive)


def residuals(rho):
    ang = dict(zip(EDGE, rho))
    closure = kinematics.closure_residual(arr, ang, ROOT)
    pose = kinematics.pose_arrangement(arr, ang, ROOT)
    worst = 0.0
    for a, b in arr.edges:
        flat = arr.vertices[a].distance(arr.vertices[b])
        worst = max(worst, abs(math.dist(pose[a], pose[b]) - flat))
    return closure, worst


def arc_samples(curve, n):
    """n states along curve(t), t ∈ (0, 1], evenly spaced in fold-angle arc length."""
    fine = [curve(i / 400.0) for i in range(401)]
    cum = [0.0]
    for i in range(400):
        cum.append(cum[-1] + math.dist(fine[i], fine[i + 1]))
    out, j = [], 0
    for k in range(1, n + 1):
        goal = cum[-1] * k / n
        while j < 400 and cum[j + 1] < goal:
            j += 1
        out.append(curve(min(1.0, (j + 1) / 400.0)) if k < n else curve(1.0))
    return out


# ── the fold program: one degree of freedom, sampled ─────────────────────────

FLAT = (0.0, 0.0, 0.0, 0.0)
FINAL = mode1(180.0)  # (180, −180, 180, 180)
program = []
for k, rho in enumerate(arc_samples(lambda s: mode1(180.0 * s), COLLAPSE_STEPS), 1):
    if 2 * k <= COLLAPSE_STEPS:
        label = L4(f"Bring edges AB and CB down towards the base; B rises as a flap "
                   f"({k}/{COLLAPSE_STEPS})",
                   f"Baja los bordes AB y CB hacia la base; B se levanta como una solapa "
                   f"({k}/{COLLAPSE_STEPS})",
                   f"Rabattez les bords AB et CB vers la base ; B se dresse en rabat "
                   f"({k}/{COLLAPSE_STEPS})",
                   f"Baixe as arestas AB e CB em direção à base; B ergue-se como uma aba "
                   f"({k}/{COLLAPSE_STEPS})")
    else:
        label = L4(f"Pinch the flap along IB and swing it over towards C ({k}/{COLLAPSE_STEPS})",
                   f"Pellizca la solapa por IB y abátela hacia C ({k}/{COLLAPSE_STEPS})",
                   f"Pincez le rabat le long de IB et couchez-le vers C ({k}/{COLLAPSE_STEPS})",
                   f"Belisque a aba ao longo de IB e deite-a em direção a C "
                   f"({k}/{COLLAPSE_STEPS})")
    program.append((f"rabbit-ear-{k}", label, rho, 500))

worst_closure = worst_edge = worst_mid = 0.0
prev = FLAT
for _, _, rho, _ in program:
    c, e = residuals(rho)
    worst_closure, worst_edge = max(worst_closure, c), max(worst_edge, e)
    worst_mid = max(worst_mid, residuals(tuple((a + b) / 2.0 for a, b in zip(prev, rho)))[0])
    prev = rho
if worst_closure > TOL_MM or worst_edge > TOL_MM:
    raise ValueError(f"inconsistent rigid fold state: closure {worst_closure:.3g} mm, "
                     f"edge {worst_edge:.3g} mm")
dof = kinematics.dof(arr, dict(zip(EDGE, mode1(60.0))))
print(f"kinematics: steps={len(program)} dof={dof} max_closure_mm={worst_closure:.3e} "
      f"max_edge_error_mm={worst_edge:.3e} max_linear_midpoint_closure_mm={worst_mid:.3e}")

steps = [pliego.Step(sid, label, [(m, a) for m, a in zip(CREASES, rho)], duration_ms=ms)
         for sid, label, rho, ms in program]

result = pliego.Assembly(
    [sheet],
    controls=[pliego.sequence_control(label=L4(
        "Fold program", "Secuencia de pliegues", "Séquence de pliage", "Sequência de dobras"))],
    sequence=pliego.Sequence(steps, mode="kinematic"),
    targets={"rabbit-eared": {"angles": dict(zip(CREASES, FINAL)), "root": (ROOT.x, ROOT.y)}},
    title="Rabbit ear",
)
