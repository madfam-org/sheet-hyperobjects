"""Modular origami — sheet-hyperobjects cartridge (Pliego).

Interlocking-unit assemblies built only from generic units: every unit's fold sequence is derived
here, and none is a named designer's unit. Three modes, each with one unit folded by the program
beside the assembled object (the assembled units stand folded in the initial frame):

* `cube` — six sleeve units: a 3:1 strip folded into a two-layer square face, open at two opposite
  edges (the pockets), with a tab on each of the other two edges. Each tab slides into the
  neighbouring face's pocket; the tabs run so that every face gives two tabs and takes two.
* `wreath` — a flat ring of triangular units in the folk "3-D origami" idiom: each unit's point
  slides into the next unit's pocket.
* `crown` — the same units standing up round the ring: each unit tilts about its own pocket edge,
  which keeps every point in its pocket.

The triangular unit is folded with simple folds (`pliego.simplefold`): fold a 2:3 rectangle in
half, fold the corners of the folded edge down to the centre line, turn over, fold the flap's
corners in and the flap down, turn over and repeat, then fold the triangle in half. The result is
a right triangle whose two layers part along its long leg: two points at one corner and a pocket
between them. The sleeve unit's tabs fold square, so it is authored directly.
"""

import math

import pliego


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


mode = PARAM(lambda: mode, "cube")                            # noqa: F821
unit_size = float(PARAM(lambda: unit_size, 40.0))             # noqa: F821
units = int(round(float(PARAM(lambda: units, 12))))           # noqa: F821
tilt = float(PARAM(lambda: tilt, 70.0))                       # noqa: F821
depth = float(PARAM(lambda: depth, 0.55))                     # noqa: F821

if mode not in ("cube", "wreath", "crown"):
    raise ValueError(f"modular-origami: unknown mode {mode!r}")

U = pliego.clamp(unit_size, 24.0, 90.0)
N = int(pliego.clamp(units, 6, 24))
TILT = pliego.clamp(tilt, 20.0, 85.0)
DEPTH = pliego.clamp(depth, 0.3, 0.75)
STOCKS = ("kami", "tant", "elephant-hide-110")   # red, blue, tan
GAP = 0.15                                   # neighbours sit this far apart off-plane


def L4(en, es, fr, pt):
    return {"en": en, "es": es, "fr": fr, "pt": pt}


def quat_from_matrix(m):
    """[x, y, z, w] of a proper rotation given as rows m[i][j]."""
    tr = m[0][0] + m[1][1] + m[2][2]
    if tr > 0.0:
        s = math.sqrt(tr + 1.0) * 2.0
        return ((m[2][1] - m[1][2]) / s, (m[0][2] - m[2][0]) / s, (m[1][0] - m[0][1]) / s,
                0.25 * s)
    if m[0][0] > m[1][1] and m[0][0] > m[2][2]:
        s = math.sqrt(1.0 + m[0][0] - m[1][1] - m[2][2]) * 2.0
        return (0.25 * s, (m[0][1] + m[1][0]) / s, (m[0][2] + m[2][0]) / s,
                (m[2][1] - m[1][2]) / s)
    if m[1][1] > m[2][2]:
        s = math.sqrt(1.0 + m[1][1] - m[0][0] - m[2][2]) * 2.0
        return ((m[0][1] + m[1][0]) / s, 0.25 * s, (m[1][2] + m[2][1]) / s,
                (m[0][2] - m[2][0]) / s)
    s = math.sqrt(1.0 + m[2][2] - m[0][0] - m[1][1]) * 2.0
    return ((m[0][2] + m[2][0]) / s, (m[1][2] + m[2][1]) / s, 0.25 * s, (m[1][0] - m[0][1]) / s)


def mat_mul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]


def mat_vec(a, v):
    return tuple(sum(a[i][k] * v[k] for k in range(3)) for i in range(3))


def axis_matrix(axis, deg):
    x, y, z = axis
    n = math.sqrt(x * x + y * y + z * z)
    x, y, z = x / n, y / n, z / n
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    k = 1.0 - c
    return [[c + x * x * k, x * y * k - z * s, x * z * k + y * s],
            [y * x * k + z * s, c + y * y * k, y * z * k - x * s],
            [z * x * k - y * s, z * y * k + x * s, c + z * z * k]]


# ── the triangular unit (folk idiom), folded with simple folds ────────────────────────────────

def triangle_unit():
    """Fold program of the triangular unit. Returns (outline, creases [(a, b, 'V'|'M')], steps
    [(label, crease index range)], the root face's affine map into the folded frame, and the
    folded triangle's corners (right angle R, point P, apex A) in the folded frame)."""
    w, h_full = U, 1.5 * U
    h, f = h_full / 2.0, h_full / 2.0 - U / 2.0
    sf = pliego.simplefold
    st = sf.FoldedState([(0.0, 0.0), (w, 0.0), (w, h_full), (0.0, h_full)])
    marks = []

    def mark(label):
        start = marks[-1][1][1] if marks else 0
        marks.append((label, (start, len(st.creases))))

    def turn():
        r = sf.reflection(pliego.Line((w / 2.0, 0.0), (w / 2.0, 1.0)))
        st.layers = [sf.Layer(lay.poly, sf.compose(r, lay.xf)) for lay in reversed(st.layers)]

    def top_to(x, y):
        """How many layers, from the top, down to the first one covering (x, y)."""
        for i in range(len(st.layers) - 1, -1, -1):
            if pliego.geometry.point_in_polygon(pliego.Vec2(x, y), st.layers[i].image()) == 1:
                return len(st.layers) - i
        raise ValueError("modular-origami: no layer under the fold")

    st.fold(((w, h), (0.0, h)), "valley")
    mark(L4("Fold the rectangle in half", "Dobla el rectángulo por la mitad",
            "Plier le rectangle en deux", "Dobre o retângulo ao meio"))
    st.fold(((w / 2.0, h), (0.0, h + w / 2.0)), "valley")
    st.fold(((w, h + w / 2.0), (w / 2.0, h)), "valley")
    mark(L4("Fold the corners of the folded edge to the centre",
            "Dobla las esquinas del borde doblado hacia el centro",
            "Rabattre les coins du bord plié vers le centre",
            "Dobre os cantos da borda dobrada para o centro"))
    for side in range(2):
        turn()
        st.fold(((0.0, h_full - f), (f, h_full)), "valley", layers=top_to(1.0, h_full - 1.0))
        st.fold(((w - f, h_full), (w, h_full - f)), "valley",
                layers=top_to(w - 1.0, h_full - 1.0))
        mark(L4("Turn over; fold the flap's corners in", "Voltea; dobla hacia dentro las "
                "esquinas de la solapa", "Retourner ; rentrer les coins du rabat",
                "Vire; dobre para dentro os cantos da aba") if side == 0 else
             L4("Turn over; fold the other flap's corners in", "Voltea; dobla hacia dentro las "
                "esquinas de la otra solapa", "Retourner ; rentrer les coins de l'autre rabat",
                "Vire; dobre para dentro os cantos da outra aba"))
        st.fold(((0.0, h_full - f), (w, h_full - f)), "valley",
                layers=top_to(w / 2.0, h_full - 1.0))
        mark(L4("Fold the flap down over the triangle", "Dobla la solapa sobre el triángulo",
                "Rabattre le rabat sur le triangle", "Dobre a aba sobre o triângulo"))
    turn()
    st.fold(((w / 2.0, 0.0), (w / 2.0, h_full)), "valley")
    mark(L4("Fold the triangle in half: two points, one pocket",
            "Dobla el triángulo por la mitad: dos puntas, un bolsillo",
            "Plier le triangle en deux : deux pointes, une poche",
            "Dobre o triângulo ao meio: duas pontas, um bolso"))
    root_pt = (w / 2.0 + 1.0, h_full - f - 1.0)          # a point of the first layer kept
    lay = st.layer_at(root_pt)
    corners = {"R": (w / 2.0, h_full - f), "P": (w, h_full - f), "A": (w / 2.0, h)}
    return (st.outline, list(st.creases), marks, lay.xf, root_pt, corners)


# ── the sleeve unit (cube), authored directly ─────────────────────────────────────────────────

def sleeve_unit_marks(sh, f, t):
    """Creases of the sleeve unit on a (2f + 3t) × f strip: back face [0, f], double tab
    [f, f + 2t] (folded flat at f + t), front face [f + 2t, 2f + 2t], single tab beyond."""
    x1, x2, x3, x4 = f, f + t, f + 2.0 * t, 2.0 * f + 2.0 * t
    m_tab_out = sh.mountain((x1, 0.0), (x1, f), angle=90.0, name="tab-hinge")
    m_sleeve = sh.valley((x2, 0.0), (x2, f), angle=180.0, name="sleeve")
    m_tab_in = sh.valley((x3, 0.0), (x3, f), angle=90.0, name="tab-hinge")
    m_tab_end = sh.valley((x4, 0.0), (x4, f), angle=90.0, name="tab-hinge")
    return m_tab_out, m_sleeve, m_tab_in, m_tab_end


sheets, steps, initial = [], [], {}

if mode == "cube":
    f = U
    t = f / 3.0
    strip_len = 2.0 * f + 3.0 * t

    def sleeve(sid, stock, label, placement=None):
        sh = pliego.Sheet(sid, [(0.0, 0.0), (strip_len, 0.0), (strip_len, f), (0.0, f)],
                          stock=stock, grain_deg=0.0, label=label, placement=placement)
        return sh, sleeve_unit_marks(sh, f, t)

    demo, (mo, ms, mi, me) = sleeve("unit", STOCKS[0],
                                     L4("Unit (folding)", "Unidad (en plegado)",
                                        "Module (en pliage)", "Unidade (dobrando)"),
                                     # face down, so its tabs fold up off the table
                                     pliego.Placement(origin=(-1.4 * f - strip_len, 0.5, f),
                                                      rotation=(1.0, 0.0, 0.0, 0.0)))
    sheets.append(demo)
    # assembled: tabs 1.5° past square, so that without paper thickness each tab sits just inside
    # its pocket instead of in the pocket's own plane
    final = {"o": -91.5, "s": 180.0, "i": 91.5, "e": 91.5}
    steps += [
        pliego.Step("sleeve", L4("Fold the strip into a sleeve", "Dobla la tira en una funda",
                                 "Plier la bande en fourreau", "Dobre a tira numa luva"),
                    [(ms, 180.0)], duration_ms=1600,
                    note=L4("The top and bottom edges stay open: those are the pockets.",
                            "Los bordes de arriba y de abajo quedan abiertos: son los bolsillos.",
                            "Les bords du haut et du bas restent ouverts : ce sont les poches.",
                            "As bordas de cima e de baixo ficam abertas: são os bolsos.")),
        pliego.Step("double-tab", L4("Fold the double tab square", "Dobla la pestaña doble a "
                                     "escuadra", "Plier la double languette d'équerre",
                                     "Dobre a aba dupla em esquadro"),
                    [(mo, -90.0), (mi, 90.0)], duration_ms=1200),
        pliego.Step("single-tab", L4("Fold the single tab square", "Dobla la pestaña sencilla a "
                                     "escuadra", "Plier la languette simple d'équerre",
                                     "Dobre a aba simples em esquadro"),
                    [(me, 90.0)], duration_ms=1200),
    ]
    # Every face gives tabs along one axis and takes them along another: z faces → x,
    # x faces → y, y faces → z (each face gives two and takes two).
    faces = [((0, 0, 1), (1, 0, 0)), ((0, 0, -1), (1, 0, 0)), ((1, 0, 0), (0, 1, 0)),
             ((-1, 0, 0), (0, 1, 0)), ((0, 1, 0), (0, 0, 1)), ((0, -1, 0), (0, 0, 1))]
    for k, (n, a) in enumerate(faces):
        axn = (a[1] * n[2] - a[2] * n[1], a[2] * n[0] - a[0] * n[2], a[0] * n[1] - a[1] * n[0])
        # columns: unplaced x → a (along the tabs), y → n (outward), z → a × n
        rot = [[a[i], n[i], axn[i]] for i in range(3)]
        nxa = (-axn[0], -axn[1], -axn[2])
        centre = (n[0] * f / 2.0, f / 2.0 + n[1] * f / 2.0 + 0.5, n[2] * f / 2.0)
        origin = tuple(centre[i] - a[i] * f / 2.0 - nxa[i] * f / 2.0 for i in range(3))
        sh, (o2, s2, i2, e2) = sleeve(f"face-{k + 1}", STOCKS[k // 2],    # opposite faces match
                                      L4(f"Cube face {k + 1}", f"Cara del cubo {k + 1}",
                                         f"Face du cube {k + 1}", f"Face do cubo {k + 1}"),
                                      pliego.Placement(origin=origin,
                                                       rotation=quat_from_matrix(rot)))
        initial[sh.id] = {"angles": {o2: final["o"], s2: final["s"], i2: final["i"],
                                     e2: final["e"]}, "root": (f / 2.0, f / 2.0)}
        sheets.append(sh)
    clock = L4("Fold a unit", "Doblar una unidad", "Plier un module", "Dobrar uma unidade")
    summary = f"face={f:g}mm strip={strip_len:g}x{f:g}mm units=6"
else:
    outline, creases, marks, xf_root, root_pt, corners = triangle_unit()

    def tri_sheet(sid, stock, label, placement=None):
        sh = pliego.Sheet(sid, outline, stock=stock, grain_deg=90.0, label=label,
                          placement=placement)
        ms = [sh.crease(a, b, "valley" if asg == "V" else "mountain", 180.0)
              for a, b, asg in creases]
        return sh, ms

    # ring geometry in the folded frame: R (right angle), P (the points), A (apex)
    R, P = corners["R"], corners["P"]
    leg = P[0] - R[0]
    alpha = 360.0 / N
    # rotating unit k by α about the ring's centre C carries the point P onto the next unit's
    # pocket edge at Q, DEPTH of the leg in from its point: C solves Rot_α(Q − C) + C = P
    q = (P[0] - DEPTH * leg, P[1])
    ca, sa = math.cos(math.radians(alpha)), math.sin(math.radians(alpha))
    rq = (ca * q[0] - sa * q[1], sa * q[0] + ca * q[1])
    bx, by = P[0] - rq[0], P[1] - rq[1]
    # (I − Rot_α) C = P − Rot_α Q
    m00, m01, m10, m11 = 1.0 - ca, sa, -sa, 1.0 - ca
    det = m00 * m11 - m01 * m10
    C = ((m11 * bx - m01 * by) / det, (-m10 * bx + m00 * by) / det)
    radius = math.hypot(R[0] - C[0], R[1] - C[1])

    def placed(k, lift):
        """Placement of unit k: its folded frame → plan, turned k·α about C (plan (X, Y) is world
        (X, y, −Y)); a reflected root face is flipped over."""
        c, s = math.cos(math.radians(k * alpha)), math.sin(math.radians(k * alpha))
        a, b, cc, d, tx, ty = xf_root
        # plan = Rot_k(xf(u, v) − C) + C
        la, lb = c * a - s * cc, c * b - s * d
        lc, ld = s * a + c * cc, s * b + c * d
        ox, oy = c * (tx - C[0]) - s * (ty - C[1]) + C[0], s * (tx - C[0]) + c * (ty - C[1]) + C[1]
        sgn = 1.0 if (a * d - b * cc) > 0 else -1.0
        rot = [[la, 0.0, -lb], [0.0, sgn, 0.0], [-lc, 0.0, ld]]
        org = (ox, lift, -oy)
        if mode == "crown":     # stand the unit up about its pocket edge (the line R–P)
            r_w = (c * (R[0] - C[0]) - s * (R[1] - C[1]) + C[0], lift,
                   -(s * (R[0] - C[0]) + c * (R[1] - C[1]) + C[1]))
            axis = (c, 0.0, -s)
            apex = corners["A"]
            a_w = (c * (apex[0] - C[0]) - s * (apex[1] - C[1]) + C[0], lift,
                   -(s * (apex[0] - C[0]) + c * (apex[1] - C[1]) + C[1]))
            rel_a = (a_w[0] - r_w[0], 0.0, a_w[2] - r_w[2])
            t_rot = axis_matrix(axis, TILT)
            if mat_vec(t_rot, rel_a)[1] < 0.0:        # the apex must rise, not sink
                t_rot = axis_matrix(axis, -TILT)
            rot = mat_mul(t_rot, rot)
            rel = (org[0] - r_w[0], org[1] - r_w[1], org[2] - r_w[2])
            rr = mat_vec(t_rot, rel)
            org = (r_w[0] + rr[0], r_w[1] + rr[1], r_w[2] + rr[2])
        return pliego.Placement(origin=org, rotation=quat_from_matrix(rot))

    demo, demo_marks = tri_sheet("unit", STOCKS[0],
                                 L4("Unit (folding)", "Unidad (en plegado)",
                                    "Module (en pliage)", "Unidade (dobrando)"),
                                 pliego.Placement(origin=(C[0] - radius - 2.2 * U, 0.0, 0.0)))
    sheets.append(demo)
    for k, (label, (i0, i1)) in enumerate(marks):
        steps.append(pliego.Step(f"step-{k + 1}", label,
                                 [(m, m.fold_angle) for m in demo_marks[i0:i1]],
                                 duration_ms=1400))
    base = 2.0 if mode == "wreath" else 1.0
    for k in range(N):
        sh, ms = tri_sheet(f"unit-{k + 1}", STOCKS[k % 2],
                           L4(f"Unit {k + 1}", f"Unidad {k + 1}", f"Module {k + 1}",
                              f"Unidade {k + 1}"), placed(k, base + GAP * (k % 2)))
        initial[sh.id] = {"angles": {m: m.fold_angle for m in ms}, "root": root_pt}
        sheets.append(sh)
    residual = pliego.kinematics.closure_residual(
        demo.build(), {e: demo_marks[mk.index].fold_angle for mk in demo_marks
                       for e in demo.build().edges_of_tag(mk.index)})
    if residual > 1e-6:
        raise ValueError(f"modular-origami: the folded unit does not close ({residual:.2e} mm)")
    clock = L4("Fold a unit", "Doblar una unidad", "Plier un module", "Dobrar uma unidade")
    summary = (f"paper={U:g}x{1.5 * U:g}mm unit_leg={leg:.1f}mm units={N} "
               f"ring_radius={radius:.1f}mm insertion={DEPTH * leg:.1f}mm "
               f"fold_residual={residual:.1e}mm")

print(f"modular-origami: mode={mode} {summary} steps={len(steps)}")

result = pliego.Assembly(sheets, controls=[pliego.sequence_control(label=clock)],
                         sequence=pliego.Sequence(steps, mode="physical"),
                         initial=initial, title="Modular origami")
