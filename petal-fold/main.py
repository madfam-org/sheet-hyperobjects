"""Petal fold — sheet-hyperobjects cartridge (Pliego).

A square collapses into a preliminary base, the front flap's lower edges are precreased to the
centre line, and the front layer's bottom corner is lifted up along a horizontal crease while the
sides swing in: the petal fold, the move that turns a preliminary base into (half) a bird base.

Three interior vertices move:

- the centre O, degree 6 (four book-fold rays, one diagonal; the other diagonal stays flat). The
  collapse follows the symmetric one-parameter family: front and back quadrants rise at τ, the
  diagonal rays at σ = 2·atan(sin τ), so every sector stays exact (spherical construction);
- K1 and K2, degree 5, where the horizontal crease meets the book folds. With O frozen in the
  preliminary base, the faces round K1 form a spherical rhombus (sectors 67.5°): the petal turns
  about the horizontal crease by λ and the side ray K1–L is placed at 67.5° from both of its
  neighbours. One parameter, λ, drives both vertices (they are mirror images).

States are built as ray directions, fold angles are read off as signed dihedrals, and every state
is checked with `pliego.kinematics` (closure residual, edge lengths) before the document is
written. All geometry is computed here; the move is traditional (no designer's diagram is used).
"""

import math

import pliego
from pliego import kinematics


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


size = float(PARAM(lambda: size, 200.0))
stock = PARAM(lambda: stock, "kami")
size = max(100.0, min(300.0, size))
COLLAPSE_STEPS = 6
PETAL_STEPS = 8
TOL_MM = 1e-5  # mm; vertex coordinates are grid-snapped by the arrangement


def L4(en, es, fr, pt):
    return {"en": en, "es": es, "fr": fr, "pt": pt}


# ── small vector helpers (world frame: sheet (u, v) ↦ (u, 0, −v), front normal +Y) ──

def vadd(*vs):
    return tuple(sum(c) for c in zip(*vs))


def vsub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def vmul(k, a):
    return (k * a[0], k * a[1], k * a[2])


def vdot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def vcross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def vunit(a):
    return vmul(1.0 / math.sqrt(vdot(a, a)), a)


def rotate(axis, deg, v):
    """Rodrigues rotation of v about the unit axis by deg."""
    a = math.radians(deg)
    return vadd(vmul(math.cos(a), v), vmul(math.sin(a), vcross(axis, v)),
                vmul(vdot(axis, v) * (1.0 - math.cos(a)), axis))


def sheet_dir(deg):
    return (math.cos(math.radians(deg)), 0.0, -math.sin(math.radians(deg)))


def vertex_folds(rays, previous):
    """Signed fold angles (deg) at each ray of one vertex; rays in CCW sheet order, face i spans
    rays i → i+1 with front normal rays[i] × rays[i+1]; the fold at ray i is the signed angle from
    face i−1's normal to face i's about the ray (valley > 0). Flat-folded creases take the sign
    nearest the previous state."""
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


# ── the sheet ────────────────────────────────────────────────────────────────

h = size / 2.0
k = h * (2.0 - math.sqrt(2.0))  # K1 = O + (k, 0): where the kite crease from B meets O–L
O, B, L, R = (h, h), (size, size), (size, h), (h, size)
K1, K2, C1, C2 = (h + k, h), (h, h + k), (size, 0.0), (0.0, size)
sheet = pliego.Sheet(
    "square", pliego.square(size), stock=stock,
    label=L4("Square", "Cuadrado", "Carré", "Quadrado"),
    front="#c8553d", back="#f4efe6",
)
M = {}
M["o-k1"] = sheet.mountain(O, K1, label=L4("Book fold (E, inner)", "Pliegue de libro (E, interior)",
                                           "Pli livre (E, intérieur)", "Dobra de livro (E, interior)"))
M["o-k2"] = sheet.mountain(O, K2, label=L4("Book fold (N, inner)", "Pliegue de libro (N, interior)",
                                           "Pli livre (N, intérieur)", "Dobra de livro (N, interior)"))
M["o-nw"] = sheet.valley(O, C2, label=L4("Diagonal (NW half)", "Diagonal (mitad NO)",
                                         "Diagonale (moitié NO)", "Diagonal (metade NO)"))
M["o-w"] = sheet.mountain(O, (0.0, h), label=L4("Book fold (W)", "Pliegue de libro (O)",
                                                "Pli livre (O)", "Dobra de livro (O)"))
M["o-s"] = sheet.mountain(O, (h, 0.0), label=L4("Book fold (S)", "Pliegue de libro (S)",
                                                "Pli livre (S)", "Dobra de livro (S)"))
M["o-se"] = sheet.valley(O, C1, label=L4("Diagonal (SE half)", "Diagonal (mitad SE)",
                                         "Diagonale (moitié SE)", "Diagonal (metade SE)"))
M["k1-l"] = sheet.mountain(K1, L, label=L4("Book fold (E, outer)", "Pliegue de libro (E, exterior)",
                                           "Pli livre (E, extérieur)", "Dobra de livro (E, exterior)"))
M["k2-r"] = sheet.mountain(K2, R, label=L4("Book fold (N, outer)", "Pliegue de libro (N, exterior)",
                                           "Pli livre (N, extérieur)", "Dobra de livro (N, exterior)"))
M["kite1"] = sheet.mountain(K1, B, label=L4("Kite crease, front layer", "Pliegue de cometa, capa delantera",
                                            "Pli cerf-volant, couche avant", "Vinco de pipa, camada da frente"))
M["kite2"] = sheet.mountain(K2, B, label=L4("Kite crease, front layer", "Pliegue de cometa, capa delantera",
                                            "Pli cerf-volant, couche avant", "Vinco de pipa, camada da frente"))
M["hinge"] = sheet.valley(K1, K2, label=L4("Petal hinge", "Bisagra del pétalo", "Charnière du pétale",
                                           "Dobradiça da pétala"))
M["kite1-in"] = sheet.mountain(K1, C1, label=L4("Kite crease, inner layer", "Pliegue de cometa, capa interior",
                                                "Pli cerf-volant, couche intérieure",
                                                "Vinco de pipa, camada interior"))
M["kite2-in"] = sheet.mountain(K2, C2, label=L4("Kite crease, inner layer", "Pliegue de cometa, capa interior",
                                                "Pli cerf-volant, couche intérieure",
                                                "Vinco de pipa, camada interior"))
NAMES = list(M)
arr = sheet.build()
EDGE = {n: M[n].edges()[0] for n in NAMES}
ROOT = pliego.P(h / 2.0, h / 2.0)  # the back quadrant
E45, E135, UP = sheet_dir(45.0), sheet_dir(135.0), (0.0, 1.0, 0.0)
C45 = math.cos(math.radians(45.0))


def angles(d):
    return {EDGE[n]: d.get(n, 0.0) for n in NAMES}


def collapse(tau, previous):
    """Preliminary-base family at O (front side out): rays 0°, 90°, 135°, 180°, 270°, 315°."""
    t = math.radians(tau)
    sg = 2.0 * math.atan(math.sin(t))
    m1 = vadd(vmul(math.cos(t), E45), vmul(-math.sin(t), UP))
    m3 = vadd(vmul(-math.cos(t), E45), vmul(-math.sin(t), UP))
    d135 = vadd(vmul(math.cos(sg), E135), vmul(-math.sin(sg), UP))
    d315 = vadd(vmul(-math.cos(sg), E135), vmul(-math.sin(sg), UP))
    rays = (vadd(vmul(C45, m1), vmul(-C45, E135)), vadd(vmul(C45, m1), vmul(C45, E135)), d135,
            vadd(vmul(C45, m3), vmul(C45, E135)), vadd(vmul(C45, m3), vmul(-C45, E135)), d315)
    f = vertex_folds(rays, previous)
    d = dict(zip(("o-k1", "o-k2", "o-nw", "o-w", "o-s", "o-se"), f))
    d["k1-l"], d["k2-r"] = d["o-k1"], d["o-k2"]
    return d


def residuals(d):
    ang = angles(d)
    closure = kinematics.closure_residual(arr, ang, ROOT)
    pose = kinematics.pose_arrangement(arr, ang, ROOT)
    worst = 0.0
    for a, b in arr.edges:
        flat = arr.vertices[a].distance(arr.vertices[b])
        worst = max(worst, abs(math.dist(pose[a], pose[b]) - flat))
    return closure, worst


# ── the preliminary base, and the rays round K1 in it ────────────────────────

previous = (-1.0, -1.0, 1.0, -1.0, -1.0, 1.0)
collapse_states = []
for i in range(1, COLLAPSE_STEPS + 1):
    st = collapse(90.0 * i / COLLAPSE_STEPS, previous)
    previous = (st["o-k1"], st["o-k2"], st["o-nw"], st["o-w"], st["o-s"], st["o-se"])
    collapse_states.append(st)
PRELIM = collapse_states[-1]
pose0 = kinematics.pose_arrangement(arr, angles(PRELIM), ROOT)


def world(pt):
    i = min(range(len(arr.vertices)), key=lambda j: arr.vertices[j].distance(pliego.P(*pt)))
    return pose0[i]


def ray(a, b):
    return vunit(vsub(world(b), world(a)))


K_TO_K2, K_TO_O, K_TO_C, K_TO_L, K_TO_B = (ray(K1, K2), ray(K1, O), ray(K1, C1), ray(K1, L),
                                         ray(K1, B))
OUT = vunit(vcross(K_TO_L, K_TO_B))  # the front face's front normal points out of the base
SIDE = math.degrees(math.atan2(size - h, size - (h + k)))  # sector L–K1–B (67.5° nominally)
if vdot(rotate(K_TO_K2, -10.0, K_TO_B), OUT) <= 0:  # the petal must lift away from the base
    raise ValueError("petal hinge orientation check failed")


def petal(lam, l_prev, f_prev):
    """The rhombus at K1 with the petal turned by λ about K1–K2 (mirrored at K2)."""
    b = rotate(K_TO_K2, -lam, K_TO_B)
    half = math.acos(max(-1.0, min(1.0, vdot(b, K_TO_C)))) / 2.0
    x = min(1.0, math.cos(math.radians(SIDE)) / math.cos(half))
    u, w = vunit(vadd(b, K_TO_C)), vunit(vcross(b, K_TO_C))
    z = math.sqrt(max(0.0, 1.0 - x * x))
    cands = (vadd(vmul(x, u), vmul(z, w)), vadd(vmul(x, u), vmul(-z, w)))
    lvec = max(cands, key=lambda c: vdot(c, l_prev))
    f = vertex_folds((lvec, b, K_TO_K2, K_TO_O, K_TO_C), f_prev)
    d = dict(PRELIM)
    d["k1-l"] = d["k2-r"] = f[0]
    d["kite1"] = d["kite2"] = f[1]
    d["hinge"] = f[2]
    d["kite1-in"] = d["kite2-in"] = f[4]
    return d, lvec, f


# ── the fold program ─────────────────────────────────────────────────────────

program = []
for i, st in enumerate(collapse_states, 1):
    program.append((f"collapse-{i}", L4(
        f"Collapse the square into a preliminary base, coloured side out ({i}/{COLLAPSE_STEPS})",
        f"Pliega el cuadrado en una base preliminar, con el color por fuera ({i}/{COLLAPSE_STEPS})",
        f"Repliez le carré en base préliminaire, couleur à l'extérieur ({i}/{COLLAPSE_STEPS})",
        f"Dobre o quadrado numa base preliminar, com a cor por fora ({i}/{COLLAPSE_STEPS})"),
        st, 600))
kites = dict(PRELIM)
kites.update({"kite1": 180.0, "kite2": 180.0, "kite1-in": -180.0, "kite2-in": -180.0})
program.append(("kite-folds", L4(
    "Valley-fold the lower edges of the front flap to the centre line, through both layers",
    "Dobla en valle los bordes inferiores de la solapa delantera hasta la línea central, "
    "a través de las dos capas",
    "Pliez en vallée les bords inférieurs du rabat avant sur la ligne médiane, à travers les "
    "deux couches",
    "Dobre em vale as arestas inferiores da aba da frente até à linha central, através das "
    "duas camadas"), kites, 1500))
program.append(("unfold-kites", L4("Unfold the kite folds", "Desdobla los pliegues de cometa",
                                   "Dépliez les plis cerf-volant", "Desdobre os vincos de pipa"),
                dict(PRELIM), 1000))
l_prev, f_prev = K_TO_L, (PRELIM["k1-l"], 0.0, 0.0, PRELIM["o-k1"], 0.0)
for i in range(1, PETAL_STEPS + 1):
    st, l_prev, f_prev = petal(180.0 * i / PETAL_STEPS, l_prev, f_prev)
    program.append((f"petal-{i}", L4(
        f"Lift the front corner up along the hinge; the sides swing in to the centre "
        f"({i}/{PETAL_STEPS})",
        f"Levanta la esquina delantera sobre la bisagra; los lados se cierran hacia el centro "
        f"({i}/{PETAL_STEPS})",
        f"Relevez le coin avant sur la charnière ; les côtés se rabattent vers le centre "
        f"({i}/{PETAL_STEPS})",
        f"Levante o canto da frente sobre a dobradiça; os lados fecham-se para o centro "
        f"({i}/{PETAL_STEPS})"), st, 450))
FINAL = program[-1][2]

worst_closure = worst_edge = worst_mid = 0.0
last = {}
for _, _, st, _ in program:
    c, e = residuals(st)
    worst_closure, worst_edge = max(worst_closure, c), max(worst_edge, e)
    mid = {n: (last.get(n, 0.0) + st.get(n, 0.0)) / 2.0 for n in NAMES}
    worst_mid = max(worst_mid, residuals(mid)[0])
    last = st
if worst_closure > TOL_MM or worst_edge > TOL_MM:
    raise ValueError(f"inconsistent rigid fold state: closure {worst_closure:.3g} mm, "
                     f"edge {worst_edge:.3g} mm")
dof = kinematics.dof(arr, angles(collapse(40.0, (-1.0, -1.0, 1.0, -1.0, -1.0, 1.0))))
print(f"kinematics: steps={len(program)} dof={dof} max_closure_mm={worst_closure:.3e} "
      f"max_edge_error_mm={worst_edge:.3e} max_linear_midpoint_closure_mm={worst_mid:.3e}")

steps = [pliego.Step(sid, label, [(M[n], st.get(n, 0.0)) for n in NAMES], duration_ms=ms)
         for sid, label, st, ms in program]

result = pliego.Assembly(
    [sheet],
    controls=[pliego.sequence_control(label=L4(
        "Fold program", "Secuencia de pliegues", "Séquence de pliage", "Sequência de dobras"))],
    sequence=pliego.Sequence(steps, mode="kinematic"),
    targets={
        "preliminary-base": {"angles": {M[n]: PRELIM.get(n, 0.0) for n in NAMES},
                             "root": (ROOT.x, ROOT.y)},
        "petal-folded": {"angles": {M[n]: FINAL.get(n, 0.0) for n in NAMES},
                         "root": (ROOT.x, ROOT.y)},
    },
    title="Petal fold",
)
