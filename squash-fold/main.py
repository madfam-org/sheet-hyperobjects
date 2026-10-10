"""Squash fold — sheet-hyperobjects cartridge (Pliego).

The classic first squash: a square is folded in half along a diagonal, then in half again, and the
top flap is lifted, opened and squashed flat into a square — half a preliminary base.

Every crease meets the centre O, so the move is one vertex of degree 6: the diagonal O–NE / O–SW,
the half-diagonals O–NW and O–SE, and the half book folds O–W and O–S that the squash adds. A
degree-6 vertex has three rigid degrees of freedom. The program holds the first diagonal flat-folded
(O–NE at 180°), turns the two-layer flap about the hinge O–SE, then follows the mirror-symmetric
path in which the flap's spine O–SW slides down the symmetry plane while O–W and O–S spread
apart. Each state is built as ray directions on the unit sphere around O (spherical-linkage
construction, every sector angle kept exact), the fold angles are read off as signed dihedrals,
and every state is checked with `pliego.kinematics` (closure residual, edge lengths).

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


size = float(PARAM(lambda: size, 150.0))
stock = PARAM(lambda: stock, "kami")
size = max(80.0, min(300.0, size))
SQUASH_STEPS = 8
TOL_MM = 1e-5  # mm; vertex coordinates are grid-snapped by the arrangement


def L4(en, es, fr, pt):
    return {"en": en, "es": es, "fr": fr, "pt": pt}


# ── small vector helpers (world frame: sheet (u, v) ↦ (u, 0, −v), front normal +Y) ──

def vadd(*vs):
    return tuple(sum(c) for c in zip(*vs))


def vmul(k, a):
    return (k * a[0], k * a[1], k * a[2])


def vdot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def vcross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def vunit(a):
    n = math.sqrt(vdot(a, a))
    return vmul(1.0 / n, a)


def sheet_dir(deg):
    """Un-placed world direction of a sheet direction `deg`."""
    return (math.cos(math.radians(deg)), 0.0, -math.sin(math.radians(deg)))


def vertex_folds(rays, previous):
    """Signed fold angles (deg) at each ray of a single vertex.

    `rays` are the world directions of the creases in counter-clockwise sheet order; face i spans
    rays i → i+1 and its front normal is rays[i] × rays[i+1]. The fold at ray i is the signed
    angle from face i−1's normal to face i's about the ray (valley > 0, as in pliego.kinematics).
    Flat-folded creases (normals antiparallel) take the sign nearest the previous state.
    """
    n = len(rays)
    normals = [vunit(vcross(rays[i], rays[(i + 1) % n])) for i in range(n)]
    out = []
    for i in range(n):
        a, b = normals[i - 1], normals[i]
        rho = math.degrees(math.atan2(vdot(rays[i], vcross(a, b)), vdot(a, b)))
        if abs(abs(rho) - 180.0) < 1e-6:
            rho = 180.0 if previous[i] >= 0 else -180.0
        out.append(rho)
    return tuple(out)


# ── the sheet: a square, every crease from the centre ────────────────────────

h = size / 2.0
O = (h, h)
sheet = pliego.Sheet(
    "square", pliego.square(size), stock=stock,
    label=L4("Square", "Cuadrado", "Carré", "Quadrado"),
    front="#f4efe6", back="#2f8f6b",
)
# counter-clockwise from NE: 45°, 135°, 180°, 225°, 270°, 315°
diag_ne = sheet.valley(O, (size, size), label=L4("Diagonal, NE half", "Diagonal, mitad NE",
                                                 "Diagonale, moitié NE", "Diagonal, metade NE"))
half_nw = sheet.mountain(O, (0.0, size), label=L4("Hinge, top layer", "Bisagra, capa superior",
                                                   "Charnière, couche du dessus",
                                                   "Dobradiça, camada de cima"))
book_w = sheet.valley(O, (0.0, h), label=L4("Book fold, W half", "Pliegue de libro, mitad O",
                                            "Pli livre, moitié O", "Dobra de livro, metade O"))
diag_sw = sheet.valley(O, (0.0, 0.0), label=L4("Flap spine (diagonal, SW half)",
                                               "Lomo de la solapa (diagonal, mitad SO)",
                                               "Dos du rabat (diagonale, moitié SO)",
                                               "Lombada da aba (diagonal, metade SO)"))
book_s = sheet.valley(O, (h, 0.0), label=L4("Book fold, S half", "Pliegue de libro, mitad S",
                                            "Pli livre, moitié S", "Dobra de livro, metade S"))
half_se = sheet.valley(O, (size, 0.0), label=L4("Hinge, bottom layer", "Bisagra, capa inferior",
                                                "Charnière, couche du dessous",
                                                "Dobradiça, camada de baixo"))
CREASES = (diag_ne, half_nw, book_w, diag_sw, book_s, half_se)
arr = sheet.build()
EDGE = [m.edges()[0] for m in CREASES]
ROOT = pliego.P(size * 0.85, h)  # the E quarter stays on the table

D = sheet_dir(315.0)  # the hinge O–SE
P_SIDE = sheet_dir(45.0)  # in-plane, perpendicular to the hinge, over the E quarter
UP = (0.0, 1.0, 0.0)
C45 = math.cos(math.radians(45.0))


def rays_turn(psi):
    """The two-layer flap turned about the hinge: ψ = 180° unfolded, 0° folded over, 90° upright."""
    spine = vadd(vmul(math.cos(math.radians(psi)), P_SIDE), vmul(math.sin(math.radians(psi)), UP))
    mid = vadd(vmul(C45, D), vmul(C45, spine))
    return (P_SIDE, D, mid, spine, mid, D)


def rays_squash(phi):
    """Mirror-symmetric squash: the spine at elevation φ in the plane (hinge, up); 90° → 0°."""
    spine = vadd(vmul(math.cos(math.radians(phi)), D), vmul(math.sin(math.radians(phi)), UP))
    c = C45 * math.tan(math.radians(phi) / 2.0)
    b = math.sqrt(max(0.0, 0.5 - c * c))
    west = vadd(vmul(C45, D), vmul(b, P_SIDE), vmul(c, UP))
    south = vadd(vmul(C45, D), vmul(-b, P_SIDE), vmul(c, UP))
    return (P_SIDE, D, west, spine, south, D)


def residuals(rho):
    ang = dict(zip(EDGE, rho))
    closure = kinematics.closure_residual(arr, ang, ROOT)
    pose = kinematics.pose_arrangement(arr, ang, ROOT)
    worst = 0.0
    for a, b in arr.edges:
        flat = arr.vertices[a].distance(arr.vertices[b])
        worst = max(worst, abs(math.dist(pose[a], pose[b]) - flat))
    return closure, worst


# ── the fold program ─────────────────────────────────────────────────────────

FLAT = (0.0,) * 6
DIAGONAL = (180.0, 0.0, 0.0, 180.0, 0.0, 0.0)
HALVED = vertex_folds(rays_turn(0.0), (180.0, -180.0, 0.0, 180.0, 0.0, 180.0))
UPRIGHT = vertex_folds(rays_turn(90.0), HALVED)
program = [
    ("fold-diagonal", L4("Valley-fold the square in half along the diagonal",
                         "Dobla el cuadrado por la mitad en valle, por la diagonal",
                         "Pliez le carré en deux en vallée selon la diagonale",
                         "Dobre o quadrado ao meio em vale, pela diagonal"), DIAGONAL, 1500),
    ("fold-in-half", L4("Fold the triangle in half: the top flap is two layers",
                        "Dobla el triángulo por la mitad: la solapa de arriba tiene dos capas",
                        "Pliez le triangle en deux : le rabat du dessus a deux couches",
                        "Dobre o triângulo ao meio: a aba de cima tem duas camadas"), HALVED, 1500),
    ("lift-flap", L4("Lift the flap upright along its hinge",
                     "Levanta la solapa hasta dejarla vertical sobre su bisagra",
                     "Relevez le rabat à la verticale sur sa charnière",
                     "Levante a aba até ficar vertical sobre a dobradiça"), UPRIGHT, 1200),
]
prev = UPRIGHT
for k in range(1, SQUASH_STEPS + 1):
    phi = 90.0 * (1.0 - k / SQUASH_STEPS)
    rho = vertex_folds(rays_squash(phi), prev)
    program.append((f"squash-{k}", L4(
        f"Open the flap and press its spine down onto the hinge, squashing it into a square "
        f"({k}/{SQUASH_STEPS})",
        f"Abre la solapa y baja su lomo sobre la bisagra, aplastándola en un cuadrado "
        f"({k}/{SQUASH_STEPS})",
        f"Ouvrez le rabat et rabattez son dos sur la charnière en l'écrasant en carré "
        f"({k}/{SQUASH_STEPS})",
        f"Abra a aba e baixe a lombada sobre a dobradiça, esmagando-a num quadrado "
        f"({k}/{SQUASH_STEPS})"), rho, 450))
    prev = rho
FINAL = prev

worst_closure = worst_edge = worst_mid = 0.0
last = FLAT
for _, _, rho, _ in program:
    c, e = residuals(rho)
    worst_closure, worst_edge = max(worst_closure, c), max(worst_edge, e)
    worst_mid = max(worst_mid, residuals(tuple((a + b) / 2.0 for a, b in zip(last, rho)))[0])
    last = rho
if worst_closure > TOL_MM or worst_edge > TOL_MM:
    raise ValueError(f"inconsistent rigid fold state: closure {worst_closure:.3g} mm, "
                     f"edge {worst_edge:.3g} mm")
dof = kinematics.dof(arr, dict(zip(EDGE, vertex_folds(rays_squash(45.0), UPRIGHT))))
print(f"kinematics: steps={len(program)} dof={dof} max_closure_mm={worst_closure:.3e} "
      f"max_edge_error_mm={worst_edge:.3e} max_linear_midpoint_closure_mm={worst_mid:.3e}")

steps = [pliego.Step(sid, label, [(m, a) for m, a in zip(CREASES, rho)], duration_ms=ms)
         for sid, label, rho, ms in program]

result = pliego.Assembly(
    [sheet],
    controls=[pliego.sequence_control(label=L4(
        "Fold program", "Secuencia de pliegues", "Séquence de pliage", "Sequência de dobras"))],
    sequence=pliego.Sequence(steps, mode="kinematic"),
    targets={"squashed": {"angles": dict(zip(CREASES, FINAL)), "root": (ROOT.x, ROOT.y)}},
    title="Squash fold",
)
