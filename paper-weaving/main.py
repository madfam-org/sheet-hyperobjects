"""Paper weaving — sheet-hyperobjects cartridge (Pliego).

Strips of paper interlaced over and under each other. Two modes:

* `mat` — a woven mat: a loom sheet with parallel slits (the warp: bands joined by an uncut border
  at both ends) and separate weft strips threaded through it, in a `plain`, `twill` (2/2) or
  `basket` (2 × 2) pattern. The program weaves one weft strip per step.
* `heart` — the woven heart basket of the Danish and Scandinavian Christmas tradition: two pieces,
  each folded in half with slits from the fold, whose loops are woven through each other into a
  checkerboard; the finished heart is a pocket.

Over and under is geometry, not a label. Every crossing is a contact: at a crossing the strip on
top sits higher than the one beneath by a gap of at least one caliper. Strips bend through the
crossings as a chain of flat panels (a triangle wave in section, the crimp of a woven mat). The
bend lines are flat lines (`F`) with treatment `none` — plain paper the program bends, never drawn
by the exporters — authored with `Sheet.bend`. The heart's
fold is a real crease. Weaving itself (threading a strip under a band) is a topological move a
rigid fold program cannot play: the program sets each strip's crimp so the layer order appears, and
a `target:woven` frame records the finished state.
"""

import math

import pliego


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


mode = PARAM(lambda: mode, "mat")                             # noqa: F821
pattern = PARAM(lambda: pattern, "plain")                     # noqa: F821
warps = int(round(float(PARAM(lambda: warps, 8))))            # noqa: F821
rows = int(round(float(PARAM(lambda: rows, 8))))              # noqa: F821
pitch = float(PARAM(lambda: pitch, 15.0))                     # noqa: F821
heart_size = float(PARAM(lambda: heart_size, 70.0))           # noqa: F821
fingers = int(round(float(PARAM(lambda: fingers, 4))))        # noqa: F821

if mode not in ("mat", "heart"):
    raise ValueError(f"paper-weaving: unknown mode {mode!r}")
if pattern not in ("plain", "twill", "basket"):
    raise ValueError(f"paper-weaving: unknown pattern {pattern!r}")

CALIPER = {"cardstock-160": 0.2, "kraft-120": 0.16, "kami": 0.072, "copy-80": 0.1}
H0 = 2.0                         # the woven plane's height above the ground (mm)
SLIT = 1.0                       # slits are 1 mm channels: the two sides never share a vertex


def L4(en, es, fr, pt):
    return {"en": en, "es": es, "fr": fr, "pt": pt}


def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def turn_angles(path):
    """Signed turning angles (deg, counter-clockwise positive) at the interior points of a
    cross-section path [(s, h), …]."""
    out = []
    for k in range(1, len(path) - 1):
        (s0, h0), (s1, h1), (s2, h2) = path[k - 1], path[k], path[k + 1]
        d1, d2 = (s1 - s0, h1 - h0), (s2 - s1, h2 - h1)
        out.append(math.degrees(math.atan2(d1[0] * d2[1] - d1[1] * d2[0],
                                           d1[0] * d2[0] + d1[1] * d2[1])))
    return out


def y_quat(deg):
    """Rotation about the world Y axis (up), as [x, y, z, w]."""
    h = math.radians(deg) / 2.0
    return (0.0, math.sin(h), 0.0, math.cos(h))


def q_mul(a, b):
    ax, ay, az, aw = a
    bx, by, bz, bw = b
    return (aw * bx + ax * bw + ay * bz - az * by, aw * by - ax * bz + ay * bw + az * bx,
            aw * bz + ax * by - ay * bx + az * bw, aw * bw - ax * bx - ay * by - az * bz)


def rot_y(deg, p):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return (p[0] * c + p[2] * s, p[1], -p[0] * s + p[2] * c)


bends = []          # every crimp mark: an untreated bend line (`Sheet.bend`, F + `none`)
steps, sheets, targets_woven, initial = [], [], {}, {}
LIFT = 75.0                      # an unwoven weft strip stands raised at the loom's edge

if mode == "mat":
    n = int(pliego.clamp(warps, 3, 16))
    m = int(pliego.clamp(rows, 2, 16))
    p = pliego.clamp(pitch, 10.0, 30.0)
    BORDER, TAIL, GAP = 15.0, 10.0, SLIT
    LOOM, WEFT = "cardstock-160", "kraft-120"
    a = 0.6 * max(CALIPER[LOOM], CALIPER[WEFT])      # crimp: ±a, so the gap is 2a ≥ a caliper
    WL, HL = n * p, m * p + 2.0 * BORDER

    def over(i, j):
        """True where weft row i passes over warp band j."""
        if pattern == "plain":
            return (i + j) % 2 == 0
        if pattern == "twill":
            return (j - i) % 4 < 2
        return (i // 2 + j // 2) % 2 == 0

    loom = pliego.Sheet("loom", rect(0.0, 0.0, WL, HL), stock=LOOM, grain_deg=90.0,
                        label=L4("Loom (warp)", "Telar (urdimbre)", "Métier (chaîne)",
                                 "Tear (urdidura)"),
                        placement=pliego.Placement(origin=(0.0, H0, 0.0)))
    for k in range(1, n):
        loom.hole(rect(k * p - SLIT / 2.0, BORDER, k * p + SLIT / 2.0, BORDER + m * p))
    loom.label_edge("slit", (p - SLIT / 2.0, BORDER), (p - SLIT / 2.0, BORDER + m * p))
    sheets.append(loom)
    # warp band j: nodes along v at the border lines and the row centres
    v_nodes = [BORDER] + [BORDER + (i + 0.5) * p for i in range(m)] + [BORDER + m * p]

    def warp_heights(j, woven):
        return [0.0] + [(-a if over(i, j) else a) if i < woven else 0.0 for i in range(m)] + [0.0]

    def warp_angles(j, woven):
        path = [(0.0, 0.0)] + list(zip(v_nodes, warp_heights(j, woven))) + [(HL, 0.0)]
        return turn_angles(path)          # front up, travelling +v: valley = CCW

    warp_marks = {}
    for j in range(n):
        states = [warp_angles(j, k) for k in range(m + 1)]
        for q, v in enumerate(v_nodes):
            if any(abs(st[q]) > 1e-9 for st in states):
                x0 = j * p + (SLIT / 2.0 if j > 0 else 0.0)
                x1 = (j + 1) * p - (SLIT / 2.0 if j < n - 1 else 0.0)
                mk = loom.bend((x0, v), (x1, v))
                bends.append(mk)
                warp_marks[(j, q)] = (mk, [st[q] for st in states])

    woven_angles = {}
    for i in range(m):
        w = p - GAP
        h_in = 2.0 * a if over(i, 0) else -2.0 * a          # tails rest clear of the warp
        h_out = 2.0 * a if over(i, n - 1) else -2.0 * a
        weft = pliego.Sheet(f"weft-{i + 1}", rect(0.0, 0.0, WL + 2.0 * TAIL, w), stock=WEFT,
                            grain_deg=0.0,
                            label=L4(f"Weft strip {i + 1}", f"Tira de trama {i + 1}",
                                     f"Bande de trame {i + 1}", f"Tira de trama {i + 1}"),
                            placement=pliego.Placement(origin=(-TAIL, H0 + h_in,
                                                               -(BORDER + i * p + GAP / 2.0))))
        u_nodes = [TAIL] + [TAIL + (j + 0.5) * p for j in range(n)] + [TAIL + WL]
        hs = [h_in] + [a if over(i, j) else -a for j in range(n)] + [h_out]
        path = [(0.0, h_in)] + list(zip(u_nodes, hs)) + [(WL + 2.0 * TAIL, h_out)]
        ang = turn_angles(path)
        targets = []
        weft_woven = {}
        lift = None
        for u, rho in zip(u_nodes, ang, strict=True):
            if abs(rho) > 1e-9:
                mk = weft.bend((u, 0.0), (u, w))
                bends.append(mk)
                targets.append((mk, rho))
                weft_woven[mk] = rho
                if lift is None:          # the bend at the loom's edge: the strip waits, raised
                    lift = mk
        # the warp bends that change once this row is woven (state i → i + 1)
        for (j, q), (mk, st) in warp_marks.items():
            if abs(st[i + 1] - st[i]) > 1e-12:
                targets.append((mk, st[i + 1]))
        sheets.append(weft)
        targets_woven[weft.id] = {"angles": weft_woven, "root": (TAIL / 2.0, w / 2.0)}
        initial[weft.id] = {"angles": {lift: LIFT}, "root": (TAIL / 2.0, w / 2.0)}
        first = (L4("It starts over the first band.", "Empieza por encima de la primera banda.",
                    "Elle commence par-dessus la première bande.",
                    "Começa por cima da primeira faixa.") if over(i, 0) else
                 L4("It starts under the first band.", "Empieza por debajo de la primera banda.",
                    "Elle commence par-dessous la première bande.",
                    "Começa por baixo da primeira faixa."))
        steps.append(pliego.Step(
            f"weave-row-{i + 1}",
            L4(f"Weave weft strip {i + 1}", f"Teje la tira de trama {i + 1}",
               f"Tisser la bande de trame {i + 1}", f"Teça a tira de trama {i + 1}"),
            targets, duration_ms=1300, note=first))
    for (j, q), (mk, st) in warp_marks.items():
        woven_angles[mk] = st[m]
    targets_woven["loom"] = {"angles": woven_angles, "root": (1.0, 1.0)}
    clock = L4("Weave", "Tejer", "Tisser", "Tecer")
    summary = (f"pattern={pattern} warps={n} rows={m} pitch={p:g}mm loom={WL:g}x{HL:g}mm "
               f"crimp=±{a:.3f}mm")
else:
    S = pliego.clamp(heart_size, 40.0, 140.0)
    n = int(pliego.clamp(fingers, 2, 8))
    fw = S / n
    if fw < 8.0:
        raise ValueError(f"paper-weaving: {n} loops in a {S:g} mm heart are narrower than 8 mm")
    R = S / 2.0
    STOCK_A, STOCK_B = "kami", "copy-80"
    g = max(1.2 * max(CALIPER[STOCK_A], CALIPER[STOCK_B]), 1.6 / fw)   # layer gap
    # four levels in a cell: A rests on the inner pair, B on the outer pair; weaving swaps them
    # where A's loop goes round B's (A outer)
    LEV = {"A": (-0.5 * g, 0.5 * g), "B": (-1.5 * g, 1.5 * g)}
    SPIN = 45.0                       # the heart turned point-down in plan

    def a_outer(r, c):
        """Plan cell (row r along A's loops, column c along B's loops): A's loop outside."""
        return (r + c) % 2 == 0

    def piece(pid, stock, rest, colour_label):
        lo, hi = rest
        w_sp = hi - lo
        ltot = 2.0 * (R + S) + w_sp
        ring = []
        for k in range(25):          # lobe at u = 0 … R (the bottom layer's end)
            t = math.radians(90.0 + 180.0 * k / 24)
            ring.append((R + R * math.cos(t), R + R * math.sin(t)))
        for k in range(25):          # lobe at the far end (the top layer's end)
            t = math.radians(-90.0 + 180.0 * k / 24)
            ring.append((ltot - R + R * math.cos(t), R + R * math.sin(t)))
        sh = pliego.Sheet(pid, ring, stock=stock, grain_deg=0.0, label=colour_label)
        for k in range(1, n):
            sh.hole(rect(R, k * fw - SLIT / 2.0, ltot - R, k * fw + SLIT / 2.0))
        return sh, ltot, w_sp

    def finger_path(devs, rest):
        """Cross-section of one loop from the bottom lobe's end, round the fold, to the top
        lobe's end: [(s, h)] with s the distance from the fold."""
        lo, hi = rest
        centres = [(c + 0.5) * fw for c in range(n)]
        bottom = [(S + R, lo), (S, lo)] + [(s, lo - d) for s, d in
                                           reversed(list(zip(centres, devs)))] + [(0.0, lo)]
        top = [(0.0, hi)] + [(s, hi + d) for s, d in zip(centres, devs)] + [(S, hi), (S + R, hi)]
        return bottom + top

    def finger_angles(devs, rest):
        # front up on the bottom layer while travelling −s: front = clockwise of travel, so a
        # valley (toward the front) is a clockwise turn
        return [-t for t in turn_angles(finger_path(devs, rest))]

    info = {}
    for key, pid, stock, lab in (
            ("A", "piece-a", STOCK_A, L4("Red piece", "Pieza roja", "Pièce rouge", "Peça vermelha")),
            ("B", "piece-b", STOCK_B, L4("White piece", "Pieza blanca", "Pièce blanche",
                                         "Peça branca"))):
        sh, ltot, w_sp = piece(pid, stock, LEV[key], lab)
        base_u = R + S                  # the fold starts here (bottom layer ends)
        loops = []
        for i in range(n):              # loop i spans local v ∈ [i·fw, (i+1)·fw]
            if key == "A":
                r = n - 1 - i           # plan row (A's v runs against plan Y)
                devs = [g if a_outer(r, c) else 0.0 for c in range(n)]
            else:
                c = i                   # plan column
                devs = [-g if a_outer(r, c) else 0.0 for r in range(n)]
            path = finger_path(devs, LEV[key])
            folded = finger_angles([0.0] * n, LEV[key])
            woven = finger_angles(devs, LEV[key])
            nb = n + 2                  # bottom interior nodes before the spine
            u_of = ([base_u - s for s, _ in path[1:nb + 1]]
                    + [base_u + w_sp + s for s, _ in path[nb + 1:-1]])
            marks = []
            v0 = i * fw + (SLIT / 2.0 if i > 0 else 0.0)
            v1 = (i + 1) * fw - (SLIT / 2.0 if i < n - 1 else 0.0)
            for k, u in enumerate(u_of):
                spine = k in (nb - 1, nb)
                if spine:
                    mk = sh.crease((u, v0), (u, v1), kind="valley", angle=90.0,
                                   name="fold")
                elif abs(woven[k]) > 1e-9:
                    mk = sh.bend((u, v0), (u, v1))
                    bends.append(mk)
                else:
                    continue
                marks.append((mk, folded[k], woven[k], spine))
            loops.append(marks)
        info[key] = (sh, ltot, w_sp, loops)
        sheets.append(sh)
    # placements: A's loops run along plan +X from its fold at X = 0, B's along plan +Y; the
    # bottom layers lie on their lower rest level; then the whole heart turns point-down.
    for key, rot, origin in (("A", 180.0, (R + S, H0 + LEV["A"][0], -S)),
                             ("B", -90.0, (0.0, H0 + LEV["B"][0], -(R + S)))):
        sh = info[key][0]
        sh.placement = pliego.Placement(origin=rot_y(SPIN, origin),
                                        rotation=q_mul(y_quat(SPIN), y_quat(rot)))
    for key in ("A", "B"):
        sh, ltot, w_sp, loops = info[key]
        targets_woven[sh.id] = {"angles": {mk: wv for lp in loops for mk, _, wv, _ in lp},
                                "root": (R / 2.0, S / 2.0)}
    fold_label = {"A": L4("Fold the red piece in half", "Dobla la pieza roja por la mitad",
                          "Plier la pièce rouge en deux", "Dobre a peça vermelha ao meio"),
                  "B": L4("Fold the white piece in half", "Dobla la pieza blanca por la mitad",
                          "Plier la pièce blanche en deux", "Dobre a peça branca ao meio")}
    for key in ("A", "B"):
        steps.append(pliego.Step(f"fold-{key.lower()}", fold_label[key],
                                 [(mk, fd) for lp in info[key][3] for mk, fd, _, sp in lp if sp],
                                 duration_ms=1500,
                                 note=L4("The slits run from the fold; each strip becomes a loop.",
                                         "Los cortes salen del doblez; cada tira se vuelve un lazo.",
                                         "Les fentes partent du pli ; chaque bande devient une "
                                         "boucle.",
                                         "Os cortes saem da dobra; cada tira vira uma alça.")))
    steps.append(pliego.Step(
        "weave", L4("Weave the loops through each other", "Entreteje los lazos",
                    "Entrelacer les boucles", "Entrelace as alças"),
        [(mk, wv) for key in ("A", "B") for lp in info[key][3] for mk, _, wv, _ in lp],
        duration_ms=2600,
        note=L4("Each loop goes through the next loop, then round the one after, alternately; "
                "the heart opens as a pocket.",
                "Cada lazo pasa por dentro del siguiente y luego por fuera del otro, alternando; "
                "el corazón se abre como un bolsillo.",
                "Chaque boucle passe dans la suivante puis autour de l'autre, en alternance ; le "
                "cœur s'ouvre comme une poche.",
                "Cada alça passa por dentro da seguinte e depois por fora da outra, alternando; o "
                "coração se abre como um bolso.")))
    clock = L4("Fold and weave", "Doblar y tejer", "Plier et tisser", "Dobrar e tecer")
    summary = f"heart={S:g}mm loops={n} loop_width={fw:.1f}mm gap={g:.3f}mm"

print(f"paper-weaving: mode={mode} {summary} bends={len(bends)} steps={len(steps)}")

assembly = pliego.Assembly(sheets, controls=[pliego.sequence_control(label=clock)],
                           sequence=pliego.Sequence(steps, mode="physical"),
                           initial=initial or None, targets={"woven": targets_woven},
                           title="Paper weaving")
doc = assembly.build()
result = doc.stamp()
