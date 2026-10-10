"""Yoshimura pattern — sheet-hyperobjects cartridge (Pliego).

The diamond pattern that thin cylinders buckle into under axial compression, folded on purpose:
horizontal valley rings and zigzag mountain diagonals, every interior vertex of degree six. The
crease pattern comes from the kernel (`pliego.tessellate.yoshimura`): `sides` diamonds round the
tube, `rings` bands of triangles up it, triangles of base `width` and height `height`.

Rolled into a tube, the pattern has an exact rigid-panel form, computed here in closed form. Ring
j becomes a planar regular polygon with `sides` edges of length `width` (circumradius
R = width / (2 sin(π/n))); consecutive rings are turned by π/n against each other and stacked at
the height that keeps the diagonals at their flat length L = √((width/2)² + height²):

    Δz² = L² − 2R²(1 − cos(π/n)) = height² − (width/2)² · tan²(π/(2n))

so the form exists only when height > (width/2) · tan(π/(2n)). The open sheet reaches it along
a rigid path: every vertex folds the same way, the rings turn by 2τ at each vertex, and they close
into n-gons at τ = 180°/n (derived below; the program is kinematic and exact all the way). Once
the seam is closed the tube is the only uniform state left — an isolated rigid state, which is
why squashing a Yoshimura tube further needs the paper to bend (it is the post-buckling pattern
of a cylinder). Fold angles are read off the closed-form vertices as signed dihedrals, checked
against the assignment and loop closure, the seam is checked to close, and the rigid path is
checked to arrive at the closed form.
"""

import math

import pliego


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


def clamp(value, lo, hi):
    return max(lo, min(hi, float(value)))


def L4(en, es, fr, pt):
    return {"en": en, "es": es, "fr": fr, "pt": pt}


sides = int(clamp(PARAM(lambda: sides, 6), 4, 12))
rings = int(clamp(PARAM(lambda: rings, 4), 2, 10))
width = clamp(PARAM(lambda: width, 30.0), 15.0, 60.0)
height = clamp(PARAM(lambda: height, 20.0), 8.0, 60.0)
stock = str(PARAM(lambda: stock, "kami"))
if stock not in ("kami", "copy-80", "washi-kozo-30", "tant"):
    raise ValueError(f"stock {stock!r} is not one this cartridge offers")
TOL_MM = 1e-6

n = sides
half_turn = math.pi / n
dz2 = height ** 2 - (width / 2.0) ** 2 * math.tan(half_turn / 2.0) ** 2
if dz2 <= (0.05 * height) ** 2:
    raise ValueError(f"yoshimura: bands of height {height:.1f} mm are too short for {n} sides of "
                     f"{width:.1f} mm — the tube needs height > "
                     f"{width / 2.0 * math.tan(half_turn / 2.0) / math.sqrt(1 - 0.05 ** 2):.1f}"
                     " mm")
dz = math.sqrt(dz2)
R = width / (2.0 * math.sin(half_turn))

tess = pliego.tessellate.yoshimura(n, rings, width, height, stock, sheet_id="yoshimura")
sheet = tess.sheet
sheet.label = L4("Yoshimura sheet", "Hoja Yoshimura", "Feuille Yoshimura", "Folha Yoshimura")
ring_marks, diagonals = tess.groups["rings"], tess.groups["diagonals"]
arr = sheet.build()


def ring_vertex(j, k, mirror):
    """Ring j's k-th polygon vertex (k may run past n: the tube wraps)."""
    theta = 2.0 * math.pi * (k + 0.5 * (j % 2)) / n
    return (R * math.cos(theta), j * dz, mirror * R * math.sin(theta))


def tube(mirror):
    """(sheet_id, (u, v)) → world point of the rolled tube; every vertex of the sheet lies on a
    ring line v = j·height (seam points are mid-edge points, interpolated on the chord)."""
    def at(_sid, uv):
        u, v = uv
        j = round(v / height)
        x = u / width - 0.5 * (j % 2)
        k = math.floor(x + 1e-9)
        t = x - k
        a, b = ring_vertex(j, k, mirror), ring_vertex(j, k + 1, mirror)
        return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))
    return at


def sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def newell(pts):
    nx = ny = nz = 0.0
    for i, p in enumerate(pts):
        q = pts[(i + 1) % len(pts)]
        nx += (p[1] - q[1]) * (p[2] + q[2])
        ny += (p[2] - q[2]) * (p[0] + q[0])
        nz += (p[0] - q[0]) * (p[1] + q[1])
    m = math.sqrt(nx * nx + ny * ny + nz * nz)
    return (nx / m, ny / m, nz / m)


def fold_angles(world):
    """Signed fold angle (deg, valley > 0) of every M/V edge, read off a 3-D state of the sheet
    (the convention of pliego.kinematics.face_transforms)."""
    verts = arr.vertices
    half = {}
    for fi, f in enumerate(arr.faces):
        for i in range(len(f)):
            half[(f[i], f[(i + 1) % len(f)])] = fi
    normals = []
    for f in arr.faces:
        flat = newell([(verts[v].x, 0.0, -verts[v].y) for v in f])
        nrm = newell([world[v] for v in f])
        normals.append(nrm if flat[1] > 0 else (-nrm[0], -nrm[1], -nrm[2]))
    out = {}
    for e, (a, b) in enumerate(arr.edges):
        if arr.assignment[e] in ("M", "V"):
            fl, fr = half[(a, b)], half[(b, a)]
            out[e] = pliego.tessellate.signed_fold_angle(normals[fl], normals[fr],
                                                         sub(world[b], world[a]))
    return out


# Roll the sheet one way, read the angles; if the front ends up inside, roll it the other way.
for mirror in (1.0, -1.0):
    world = [tube(mirror)("yoshimura", (p.x, p.y)) for p in arr.vertices]
    angles = fold_angles(world)
    if all((angles[e] > 0) == (arr.assignment[e] == "V") for e in angles):
        break
else:
    raise ValueError("yoshimura: the rolled tube does not agree with the mountain/valley "
                     "assignment in either direction")

rho_ring = sorted({round(abs(angles[e]), 6) for m in ring_marks for e in m.edges()})
rho_diag = sorted({round(abs(angles[e]), 6) for m in diagonals for e in m.edges()})
if len(rho_ring) != 1 or len(rho_diag) != 1:
    raise ValueError(f"yoshimura: the tube is not uniform (rings {rho_ring}, diagonals {rho_diag})")
residual = pliego.kinematics.closure_residual(arr, angles)
pose = pliego.kinematics.pose_arrangement(arr, angles)
seam = 0.0
for i, p in enumerate(arr.vertices):
    if abs(p.x) < TOL_MM:
        mate = min(range(len(arr.vertices)), key=lambda q: abs(arr.vertices[q].x - n * width)
                   + abs(arr.vertices[q].y - p.y))
        seam = max(seam, math.dist(pose[i], pose[mate]))
if residual > 1e-6 or seam > 1e-6:
    raise ValueError(f"yoshimura: tube state does not close (loops {residual:.3g} mm, seam "
                     f"{seam:.3g} mm)")
print(f"kinematics: tube n={n} rings={rings} R={R:.3f}mm dz={dz:.3f}mm rho_ring={rho_ring[0]:.4f} "
      f"rho_diag={rho_diag[0]:.4f} max_closure_mm={residual:.2e} seam_gap_mm={seam:.2e} "
      f"(the only closed uniform state: squashing further needs bending)")


# ── the rigid path from the flat sheet to the tube ───────────────────────────
# Every vertex of the open sheet can fold the same way. With β the angle between a diagonal and
# its ring (tan β = 2·height/width) and τ the angle the two ring rays drop out of the sheet's
# plane, the vertex's rays are H± = (±cos τ, −sin τ, 0) and D = (±cos β, −cos β·tan(τ/2),
# ±√(sin²β − cos²β·tan²(τ/2))): each diagonal keeps its sectors β and 180° − 2β. Each ring then
# turns by 2τ at every vertex, so the sheet curls as it folds, and the rings close into n-gons at
# τ = 180°/n: exactly the tube above. Every state on the way is rigid.

beta = math.atan2(2.0 * height, width)


def vertex(tau):
    t = math.radians(tau)
    a, b = math.cos(beta), -math.cos(beta) * math.tan(t / 2.0)
    c = math.sqrt(max(0.0, math.sin(beta) ** 2 - b * b))
    rays = [(math.cos(t), -math.sin(t), 0.0), (a, b, -c), (-a, b, -c),
            (-math.cos(t), -math.sin(t), 0.0), (-a, b, c), (a, b, c)]
    f = pliego.kinematics.vertex_folds(rays, previous=(1, -1, -1, 1, -1, -1))
    return f[0], f[1]


STEPS = 6
path, worst_path = [], 0.0
for i in range(1, STEPS + 1):
    tau = 180.0 / n * i / STEPS
    rv, rd = vertex(tau)
    ang = {e: rv for m in ring_marks for e in m.edges()}
    ang.update({e: rd for m in diagonals for e in m.edges()})
    worst_path = max(worst_path, pliego.kinematics.closure_residual(arr, ang))
    path.append((tau, rv, rd, ang))
gap = max(abs(path[-1][3][e] - angles[e]) for e in angles)
if worst_path > 1e-6 or gap > 1e-6:
    raise ValueError(f"yoshimura: rigid path does not reach the tube (closure {worst_path:.3g} mm, "
                     f"angle gap {gap:.3g}°)")
print(f"kinematics: rigid path flat->tube steps={STEPS} tau_end={180.0 / n:.3f}° "
      f"max_closure_mm={worst_path:.2e} gap_to_closed_form_deg={gap:.1e}")

vals = (f"R = {R:.1f} mm, Δz = {dz:.1f} mm, ρ_ring = {rho_ring[0]:.1f}°, "
        f"ρ_diagonal = {rho_diag[0]:.1f}°")
steps = []
for i, (tau, _rv, _rd, ang) in enumerate(path, 1):
    curl = 2.0 * n * tau
    if i < STEPS:
        label = L4(f"Fold the diamonds: the sheet curls ({i}/{STEPS})",
                   f"Pliega los rombos: la hoja se enrolla ({i}/{STEPS})",
                   f"Plier les losanges : la feuille s'enroule ({i}/{STEPS})",
                   f"Dobre os losangos: a folha enrola-se ({i}/{STEPS})")
        note = L4(f"Rigid state: τ = {tau:.1f}°, each ring has turned through {curl:.0f}°.",
                  f"Estado rígido: τ = {tau:.1f}°, cada anillo ha girado {curl:.0f}°.",
                  f"État rigide : τ = {tau:.1f}°, chaque anneau a tourné de {curl:.0f}°.",
                  f"Estado rígido: τ = {tau:.1f}°, cada anel já girou {curl:.0f}°.")
    else:
        label = L4("The rings close: every ring a regular polygon, the seam meets",
                   "Los anillos se cierran: cada uno es un polígono regular y la costura se une",
                   "Les anneaux se ferment : chacun est un polygone régulier, la jointure se "
                   "rejoint",
                   "Os anéis fecham-se: cada um é um polígono regular e a emenda encontra-se")
        note = L4(f"Exact rigid tube: {vals}.", f"Tubo rígido exacto: {vals}.",
                  f"Tube rigide exact : {vals}.", f"Tubo rígido exato: {vals}.")
    steps.append(pliego.Step(f"curl-{i}", label,
                             [(pliego.assembly.EdgeRef(sheet, e), a)
                              for e, a in sorted(ang.items())],
                             duration_ms=900, note=note))

result = pliego.Assembly(
    [sheet],
    controls=[pliego.sequence_control(label=L4("Fold program", "Secuencia de pliegues",
                                               "Séquence de pliage", "Sequência de dobras"))],
    sequence=pliego.Sequence(steps, mode="kinematic"),
    targets={"tube": tube(mirror)},
    title="Yoshimura pattern",
)
