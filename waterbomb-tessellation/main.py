"""Waterbomb tessellation — sheet-hyperobjects cartridge (Pliego).

A grid of the generic waterbomb cell: a square with both diagonals as mountains and the line
through its centre as a valley (the kernel's `pliego.tessellate.waterbomb`, rows in register).
Every interior vertex — cell corners and cell centres alike — is a waterbomb base: degree six,
sectors 45°, 90°, 45°, 45°, 90°, 45°.

**The rigid motion.** Every vertex can fold the same way. With τ the angle the two valley rays
drop out of the sheet's plane, the vertex's rays are

    H± = (±cos τ, −sin τ, 0),   D = (±1/√2, −tan(τ/2)/√2, ±√(1/2 − tan²(τ/2)/2))

(each diagonal stays 45° from its valley rays and 90° from its neighbour diagonal), and the fold
angles follow with `pliego.kinematics.vertex_folds`. Each valley line turns by 2τ at every
vertex, so the grid curls as it folds. The loop closure of the whole sheet is checked at every
state, and the kernel's motion solver is run on one cell as a cross-check.

`tube` mode: the curl closes into a tube when the valley lines become regular polygons of
`columns` sides, at τ = 180°/columns. The program is kinematic and exact from the flat sheet to
the closed tube. With rows in register this grid is the Yoshimura pattern with right-angled
triangles (base `size`, height `size/2`), so the tube also has the Yoshimura closed form, which
the script checks against: radius size/(2 sin(π/n)), ring spacing (size/2)·√(1 − tan²(π/(2n))).

`flat` mode: the flat-foldable grid pressed flat. Every vertex passes Kawasaki and Maekawa, so the
flat-folded state exists; but the symmetric rigid motion curls the sheet a full turn and more
before it gets there (it would pass through itself), so a real grid is collapsed row by row,
with the paper bending. The program is physical: one exact rigid step (the grid half curled),
then the exact flat-folded state.

Only the generic waterbomb cell is used. The offset-row arrangement behind some well-known
waterbomb balls is not modelled.
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


run_mode = PARAM(lambda: mode, "flat")  # noqa: F821 - injected by the runner
columns = int(clamp(PARAM(lambda: columns, 6), 3, 12))
rows = int(clamp(PARAM(lambda: rows, 3), 1, 8))
size = clamp(PARAM(lambda: size, 30.0), 20.0, 80.0)
stock = str(PARAM(lambda: stock, "kami"))
if run_mode not in ("flat", "tube"):
    raise ValueError(f"mode {run_mode!r} must be 'flat' or 'tube'")
if stock not in ("kami", "copy-80", "washi-kozo-30", "tant"):
    raise ValueError(f"stock {stock!r} is not one this cartridge offers")
if columns < 3:
    raise ValueError("waterbomb-tessellation: the grid needs at least 3 cells round")

tess = pliego.tessellate.waterbomb(columns, rows, size, stock, sheet_id="waterbomb")
sheet = tess.sheet
sheet.label = L4("Waterbomb grid", "Cuadrícula de bombas de agua", "Grille de bombes à eau",
                 "Grade de bombas d'água")
lines, diagonals = tess.groups["lines"], tess.groups["diagonals"]
arr = sheet.build()
EdgeRef = pliego.assembly.EdgeRef
LABEL = L4("Fold program", "Secuencia de pliegues", "Séquence de pliage", "Sequência de dobras")


def vertex(tau):
    """(valley, diagonal) fold angles of the symmetric waterbomb vertex at drop angle τ (deg)."""
    t = math.radians(tau)
    a = 1.0 / math.sqrt(2.0)
    b = -math.tan(t / 2.0) / math.sqrt(2.0)
    c = math.sqrt(max(0.0, 0.5 - b * b))
    rays = [(math.cos(t), -math.sin(t), 0.0), (a, b, -c), (-a, b, -c),
            (-math.cos(t), -math.sin(t), 0.0), (-a, b, c), (a, b, c)]
    f = pliego.kinematics.vertex_folds(rays, previous=(1, -1, -1, 1, -1, -1))
    if abs(f[0] - f[3]) > 1e-9 or max(f[1:3] + f[4:]) - min(f[1:3] + f[4:]) > 1e-9:
        raise ValueError("waterbomb-tessellation: the symmetric vertex is not symmetric")
    return f[0], f[1]


def uniform(rho_v, rho_d):
    out = {e: rho_v for m in lines for e in m.edges()}
    out.update({e: rho_d for m in diagonals for e in m.edges()})
    return out


# ── the rigid states, and a solver cross-check on one cell ───────────────────

def rigid(tau):
    rv, rd = vertex(tau)
    ang = uniform(rv, rd)
    res = pliego.kinematics.closure_residual(arr, ang)
    if res > 1e-6:
        raise ValueError(f"waterbomb-tessellation: uniform state does not close ({res:.3g} mm)")
    return rv, rd, ang, res


cell = pliego.tessellate.waterbomb(1, 1, size, stock, sheet_id="cell")
probe_rv = vertex(20.0)
probe = pliego.kinematics.solve(cell.sheet, {}, {m: probe_rv[0] for m in cell.groups["lines"]},
                                steps=8)
solved = probe[-1][cell.groups["diagonals"][0].edges()[0]]
if abs(solved - probe_rv[1]) > 1e-6:
    raise ValueError(f"waterbomb-tessellation: solver gives {solved:.6f}° for the diagonal, closed "
                     f"form {probe_rv[1]:.6f}°")
CHECK = f"solver_cross_check_deg={abs(solved - probe_rv[1]):.1e} cell_dof={probe.dof}"


def edge_targets(ang):
    return [(EdgeRef(sheet, e), a) for e, a in sorted(ang.items())]


# ── flat: half curled, then pressed flat ─────────────────────────────────────

if run_mode == "flat":
    tau1 = 90.0 / columns
    rv, rd, ang, res = rigid(tau1)
    flat_folded = uniform(180.0, -180.0)
    print(f"kinematics: waterbomb grid {columns}x{rows} rigid step tau={tau1:.2f}° (rings half "
          f"curled) rho_valley={rv:.4f} rho_diagonal={rd:.4f} max_closure_mm={res:.2e} {CHECK}; "
          "flat-folded state exact, path to it physical")
    vals = f"τ = {tau1:.1f}°, ρ_valley = {rv:.1f}°, ρ_diagonal = {rd:.1f}°"
    steps = [
        pliego.Step("fold-cells",
                    L4("Fold every cell a little: the grid curls half a turn",
                       "Pliega un poco cada celda: la cuadrícula se enrolla media vuelta",
                       "Plier un peu chaque cellule : la grille s'enroule d'un demi-tour",
                       "Dobre um pouco cada célula: a grade enrola-se meia volta"),
                    edge_targets(ang), duration_ms=2500,
                    note=L4(f"Exact rigid state: {vals}.", f"Estado rígido exacto: {vals}.",
                            f"État rigide exact : {vals}.", f"Estado rígido exato: {vals}.")),
        pliego.Step("press-flat",
                    L4("Collapse the grid row by row and press it flat",
                       "Cierra la cuadrícula fila por fila y aplánala",
                       "Refermer la grille rangée par rangée et l'aplatir",
                       "Feche a grade fileira por fileira e achate-a"),
                    edge_targets(flat_folded), duration_ms=3000,
                    note=L4("Every cell is now a flat waterbomb base. The symmetric rigid motion "
                            "would make the sheet pass through itself on the way, so the paper "
                            "bends instead.",
                            "Cada celda es ahora una base de bomba de agua plana. El movimiento "
                            "rígido simétrico haría que la hoja se atravesara a sí misma por el "
                            "camino, así que el papel se curva.",
                            "Chaque cellule est maintenant une base de la bombe à eau à plat. Le "
                            "mouvement rigide symétrique ferait traverser la feuille par "
                            "elle-même en chemin ; le papier se courbe donc.",
                            "Cada célula é agora uma base da bomba d'água plana. O movimento "
                            "rígido simétrico faria a folha atravessar-se a si mesma pelo "
                            "caminho, por isso o papel curva-se.")),
    ]
    result = pliego.Assembly(
        [sheet], controls=[pliego.sequence_control(label=LABEL)],
        sequence=pliego.Sequence(steps, mode="physical"),
        targets={"flat-folded": {"angles": {**{m: 180.0 for m in lines},
                                            **{m: -180.0 for m in diagonals}}}},
        title="Waterbomb tessellation")

# ── tube: the grid rolled up ─────────────────────────────────────────────────

else:
    n, w, h = columns, size, size / 2.0
    R = w / (2.0 * math.sin(math.pi / n))
    dz = h * math.sqrt(1.0 - math.tan(math.pi / (2 * n)) ** 2)

    def tube(mirror):
        def at(_sid, uv):
            j = round(uv[1] / h)
            x = uv[0] / w - 0.5 * (j % 2)
            k = math.floor(x + 1e-9)
            t = x - k
            p = [(R * math.cos(2 * math.pi * (kk + 0.5 * (j % 2)) / n), j * dz,
                  mirror * R * math.sin(2 * math.pi * (kk + 0.5 * (j % 2)) / n))
                 for kk in (k, k + 1)]
            return tuple(p[0][i] + (p[1][i] - p[0][i]) * t for i in range(3))
        return at

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
                d = tuple(world[b][i] - world[a][i] for i in range(3))
                out[e] = pliego.tessellate.signed_fold_angle(normals[half[(a, b)]],
                                                             normals[half[(b, a)]], d)
        return out

    for mirror in (1.0, -1.0):
        angles = fold_angles([tube(mirror)("", (p.x, p.y)) for p in arr.vertices])
        if all((angles[e] > 0) == (arr.assignment[e] == "V") for e in angles):
            break
    else:
        raise ValueError("waterbomb-tessellation: the rolled tube disagrees with the assignment")
    residual = pliego.kinematics.closure_residual(arr, angles)
    pose = pliego.kinematics.pose_arrangement(arr, angles)
    seam = max((math.dist(pose[i], pose[min(range(len(arr.vertices)), key=lambda q: abs(
        arr.vertices[q].x - n * w) + abs(arr.vertices[q].y - p.y))]))
               for i, p in enumerate(arr.vertices) if abs(p.x) < 1e-6)
    if residual > 1e-6 or seam > 1e-6:
        raise ValueError(f"waterbomb-tessellation: tube does not close ({residual:.3g} mm, seam "
                         f"{seam:.3g} mm)")
    STEPS = 6
    path = [(180.0 / columns * i / STEPS,) + rigid(180.0 / columns * i / STEPS)[:3]
            for i in range(1, STEPS + 1)]
    gap = max(abs(path[-1][3][e] - angles[e]) for e in angles)
    if gap > 1e-6:
        raise ValueError(f"waterbomb-tessellation: the rigid curl misses the closed-form tube by "
                         f"{gap:.3g}°")
    print(f"kinematics: waterbomb tube n={n} R={R:.3f}mm dz={dz:.3f}mm "
          f"rho_valley={path[-1][1]:.4f} rho_diagonal={path[-1][2]:.4f} "
          f"max_closure_mm={residual:.2e} seam_gap_mm={seam:.2e} "
          f"rigid_curl_steps={STEPS} gap_to_closed_form_deg={gap:.1e} {CHECK}")
    vals = f"R = {R:.1f} mm, Δz = {dz:.1f} mm"
    steps = []
    for i, (tau, _rv, _rd, ang) in enumerate(path, 1):
        if i < STEPS:
            label = L4(f"Fold every cell: the grid curls ({i}/{STEPS})",
                       f"Pliega cada celda: la cuadrícula se enrolla ({i}/{STEPS})",
                       f"Plier chaque cellule : la grille s'enroule ({i}/{STEPS})",
                       f"Dobre cada célula: a grade enrola-se ({i}/{STEPS})")
            note = L4(f"Rigid state: τ = {tau:.1f}°, each valley line has turned through "
                      f"{2 * n * tau:.0f}°.",
                      f"Estado rígido: τ = {tau:.1f}°, cada línea de valle ha girado "
                      f"{2 * n * tau:.0f}°.",
                      f"État rigide : τ = {tau:.1f}°, chaque ligne de vallée a tourné de "
                      f"{2 * n * tau:.0f}°.",
                      f"Estado rígido: τ = {tau:.1f}°, cada linha de vale já girou "
                      f"{2 * n * tau:.0f}°.")
        else:
            label = L4("The valley lines close into polygons: the tube",
                       "Las líneas de valle se cierran en polígonos: el tubo",
                       "Les lignes de vallée se ferment en polygones : le tube",
                       "As linhas de vale fecham-se em polígonos: o tubo")
            note = L4(f"Exact rigid tube: {vals}; close the seam.",
                      f"Tubo rígido exacto: {vals}; cierra la costura.",
                      f"Tube rigide exact : {vals} ; fermer la jointure.",
                      f"Tubo rígido exato: {vals}; feche a emenda.")
        steps.append(pliego.Step(f"curl-{i}", label, edge_targets(ang), duration_ms=900,
                                 note=note))
    result = pliego.Assembly(
        [sheet], controls=[pliego.sequence_control(label=LABEL)],
        sequence=pliego.Sequence(steps, mode="kinematic"),
        targets={"tube": tube(mirror)}, title="Waterbomb tube")
