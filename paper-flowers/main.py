"""Paper flowers (flores de papel) — sheet-hyperobjects cartridge (Pliego).

One family, two ways of making a tissue flower, each on a rolled paper stem.

- `carnation`: a pleated-tissue flower. A small stack of tissue sheets is pleated together like a
  fan, its ends trimmed pointed (pinked) or round, and tied at the centre onto the stem; then the
  layers are pulled up into a bloom. It is the pom-pom's technique made small, on a stem.
- `cut-petal`: a petal strip. A strip of tissue cut into a row of petals along one edge is curled
  petal by petal, wound round the top of the stem and its petals opened outward.

Stems. Each stem is a strip of kraft rolled straight into a tube: `F` lines parallel to the stem's
axis, folded by the exterior angles of a polygonal spiral (side c, radius growing by the paper's
thickness and a little air per turn), so the roll is an exact isometry and several layers thick.

Petals. The petal strip's base band is wound round the stem the same way (F lines across the
strip). Each petal sits on one base panel, hinged along that panel's top edge (an F line), with
two more F lines across it that curl it outward. Notches between the petals keep them separate, so
every line ends on the outline or on another line's end: no interior vertex, and every fold is free.
The petals open more on the outer turns than on the inner ones.

The carnation's stack. Each tissue sheet carries pleat lines (valley/mountain, `crease`) and a
tie line along its middle (F). Pleating is rigid; the bloom is not (fanning a pleated stack bends
and crushes the tissue at the tie, see tissue-pom-pom), so the program ends with the pleated stick
tied on its stem (`target:pleated`) and `target:bloom` is the closest exact state: pleats
flat-folded and each sheet folded at the tie so its two halves lift upward, the bottom sheet least.

Everything is a kinematic program: the lines never cross, so every step is an exact rigid motion.
The `initial` frame holds each sheet flat where its first face (the face the studio preview keeps
still) sits in the finished flower, so the preview ends exactly on the target: the flower stands
upright on its stem. Every F line is plain paper (treatment `none`), off the cut file.
There is no crepe-paper stock card, so the tissue is papel de china; crepe's stretch is not
modelled.
"""

import math

import pliego


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


def L4(en, es, fr, pt):
    return {"en": en, "es": es, "fr": fr, "pt": pt}


SLUG = "paper-flowers"
TISSUE = "papel-de-china"
MIN_TISSUE = 1.5            # mm, papel de china min feature
TISSUE_T = 0.04             # mm, papel de china caliper (stock card estimate)
STEM_STOCKS = {"kraft-120": (1.0, 0.16), "cardstock-160": (1.5, 0.20)}   # min feature, caliper
CLOSED = 178.0              # deg, carnation pleats in the program
NOTCH = 1.6                 # mm gap between petals (≥ the 1.5 mm cutter minimum)
BASE = 14.0                 # mm, the petal strip's base band (wound round the stem)
AIR = 1.0                   # mm per turn, petal strip (the tissue gathers loosely)
STEM_AIR = 0.1              # mm of air per turn, stem
STEM_CORE = 2.0             # mm, radius of the skewer or wire the stem is rolled on
STEM_FACET = 1.8            # mm, stem panel width
COLOURS = {"marigold": "#f28c28", "yellow": "#f6c445", "pink": "#e8336d", "red": "#c81d25",
           "white": "#f4f1ea", "purple": "#7a3e9d"}

mode = str(PARAM(lambda: mode, "carnation"))                               # noqa: F821
colour = str(PARAM(lambda: colour, "pink"))                                # noqa: F821
stem_length = pliego.clamp(PARAM(lambda: stem_length, 180.0), 80.0, 300.0)      # noqa: F821
stem_stock = str(PARAM(lambda: stem_stock, "kraft-120"))                   # noqa: F821
n_sheets = int(pliego.clamp(PARAM(lambda: sheets, 4), 3, 6))              # noqa: F821
sheet_length = pliego.clamp(PARAM(lambda: sheet_length, 200.0), 120.0, 300.0)   # noqa: F821
sheet_width = pliego.clamp(PARAM(lambda: sheet_width, 120.0), 80.0, 200.0)      # noqa: F821
pleat = pliego.clamp(PARAM(lambda: pleat, 12.0), 8.0, 25.0)                # noqa: F821
ends = str(PARAM(lambda: ends, "pointed"))                                 # noqa: F821
petal_height = pliego.clamp(PARAM(lambda: petal_height, 35.0), 20.0, 60.0)      # noqa: F821
petal_width = pliego.clamp(PARAM(lambda: petal_width, 4.5), 3.5, 10.0)    # noqa: F821
turns = pliego.clamp(PARAM(lambda: turns, 4.0), 2.0, 6.0)                 # noqa: F821
tip = str(PARAM(lambda: tip, "round"))                                     # noqa: F821
for name, val, ok in (("mode", mode, ("carnation", "cut-petal")), ("colour", colour, COLOURS),
                      ("stem_stock", stem_stock, STEM_STOCKS), ("ends", ends, ("round", "pointed")),
                      ("tip", tip, ("round", "pointed"))):
    if val not in ok:
        raise ValueError(f"paper-flowers: {name} must be one of {tuple(ok)}, got {val!r}")
TINT = COLOURS[colour]


# ── small 3-D helpers ────────────────────────────────────────────────────────
def sub(a, b):
    return tuple(a[i] - b[i] for i in range(3))


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def unit(a):
    r = math.sqrt(sum(x * x for x in a))
    return tuple(x / r for x in a)


def frame(a, b, c):
    """Orthonormal frame (rows e1, e2, e3) and origin from three points."""
    e1 = unit(sub(b, a))
    e3 = unit(cross(e1, sub(c, a)))
    return (e1, cross(e3, e1), e3), a


def newell(pts):
    n = [0.0, 0.0, 0.0]
    for i, p in enumerate(pts):
        q = pts[(i + 1) % len(pts)]
        n[0] += (p[1] - q[1]) * (p[2] + q[2])
        n[1] += (p[2] - q[2]) * (p[0] + q[0])
        n[2] += (p[0] - q[0]) * (p[1] + q[1])
    return unit(n)


def fold_angles(pose, sheet_id, arr):
    """Signed fold angle (FOLD convention, deg) of every interior F/M/V edge in `pose`."""
    pts = [pose(sheet_id, (v.x, v.y)) for v in arr.vertices]
    left = {}
    for fi, f in enumerate(arr.faces):
        for i in range(len(f)):
            left[(f[i], f[(i + 1) % len(f)])] = fi
    normals = [newell([pts[v] for v in f]) for f in arr.faces]
    out = {}
    for e, (a, b) in enumerate(arr.edges):
        if arr.assignment[e] in ("F", "M", "V") and (a, b) in left and (b, a) in left:
            out[e] = pliego.tessellate.signed_fold_angle(normals[left[(a, b)]],
                                                         normals[left[(b, a)]], sub(pts[b], pts[a]))
    return out


def check_isometric(pose, sheet_id, arr, what):
    for a, b in arr.edges:
        pa, pb = arr.vertices[a], arr.vertices[b]
        d0 = math.dist((pa.x, pa.y), (pb.x, pb.y))
        d1 = math.dist(pose(sheet_id, (pa.x, pa.y)), pose(sheet_id, (pb.x, pb.y)))
        if abs(d1 - d0) > 1e-5 * max(1.0, d0):
            raise ValueError(f"paper-flowers: the {what} pose stretches an edge ({d0} → {d1})")


def root_aligned(pose, sheet_id, arr):
    """The flat sheet, moved rigidly so that its first face lies where `pose` puts it (the studio
    preview keeps that face still, so its program then ends exactly on `pose`)."""
    f, V = arr.faces[0], arr.vertices

    def area(t):
        (ax, ay), (bx, by), (cx, cy) = [(V[i].x, V[i].y) for i in t]
        return abs((bx - ax) * (cy - ay) - (by - ay) * (cx - ax))
    best = max(((f[0], f[i], f[i + 1]) for i in range(1, len(f) - 1)), key=area)
    (A, oa) = frame(*[(V[i].x, 0.0, -V[i].y) for i in best])
    (B, ob) = frame(*[pose(sheet_id, (V[i].x, V[i].y)) for i in best])

    def place(uv):
        d = sub((uv[0], 0.0, -uv[1]), oa)
        loc = [sum(A[r][i] * d[i] for i in range(3)) for r in range(3)]
        return tuple(ob[i] + sum(loc[r] * B[r][i] for r in range(3)) for i in range(3))
    return place


def spiral(n, c, r0, dr):
    """Vertices of a polygonal spiral with n sides of length c, starting on a circle of radius r0
    and growing by dr per turn; returns (points, centre of the first turn, turning angles)."""
    pts, psi, r, turnings = [(0.0, 0.0)], 0.0, r0, []
    for _ in range(n):
        x, y = pts[-1]
        pts.append((x + c * math.cos(psi), y + c * math.sin(psi)))
        th = 2.0 * math.asin(min(1.0, c / (2.0 * r)))
        turnings.append(th)
        psi += th
        r += dr * th / (2.0 * math.pi)
    return pts, (0.0, r0 * math.cos(math.asin(min(1.0, c / (2.0 * r0))))), turnings


def on_spiral(pts, c, u):
    i = min(max(int(u / c), 0), len(pts) - 2)
    t = u / c - i
    (x0, y0), (x1, y1) = pts[i], pts[i + 1]
    return (x0 + t * (x1 - x0), y0 + t * (y1 - y0))


# ── the stem: kraft rolled straight on a thin core ───────────────────────────
stem_min, stem_t = STEM_STOCKS[stem_stock]
STEM_TURNS = 2.5
stem_n = max(8, round(STEM_TURNS * 2.0 * math.pi * (STEM_CORE + 0.6) / STEM_FACET))
stem_w = stem_n * STEM_FACET
stem = pliego.Sheet("stem", [(0.0, 0.0), (stem_w, 0.0), (stem_w, stem_length),
                             (0.0, stem_length)], stock=stem_stock, grain_deg=90.0,
                    label=L4("Stem", "Tallo", "Tige", "Caule"), back="#5b8c3a")
for i in range(1, stem_n):
    stem.bend((i * STEM_FACET, 0.0), (i * STEM_FACET, stem_length))
stem_pts, stem_c0, _ = spiral(stem_n, STEM_FACET, STEM_CORE + stem_t, stem_t + STEM_AIR)
stem_arr = stem.build()
STEM_TOP = stem_length                       # the stem stands on the table, top at this height
STEM_R = STEM_CORE + (STEM_TURNS + 0.5) * (stem_t + STEM_AIR)    # outer radius, about
MIRROR = {"stem": 1.0, "petals": 1.0}


def stem_pose_at(axis):
    def pose(sheet_id, uv):
        q = on_spiral(stem_pts, STEM_FACET, uv[0])
        return (axis[0] + q[0] - stem_c0[0], uv[1],
                axis[1] + MIRROR["stem"] * (q[1] - stem_c0[1]))
    return pose


def stem_angles(pose):
    a = fold_angles(pose, "stem", stem_arr)
    if min(a.values()) < 0.0:
        MIRROR["stem"] = -1.0
        a = fold_angles(pose, "stem", stem_arr)
    if min(a.values()) <= 0.0:
        raise ValueError("paper-flowers: the stem is not a valley roll")
    check_isometric(pose, "stem", stem_arr, "stem")
    return a


# ── carnation ────────────────────────────────────────────────────────────────
def build_carnation():
    n = max(6, round(sheet_length / pleat))
    p = sheet_length / n
    Hy = sheet_width
    mid = Hy / 2.0
    depth = 1.0 + (0.5 * p if ends == "round" else 0.9 * p)
    if Hy < 4.0 * depth:
        raise ValueError("paper-flowers: the tissue sheets are too short for these pleats")

    def profile(y_edge, sign):
        pts = [(0.0, y_edge + sign * depth)]
        for j in range(n):
            if ends == "round":
                for i in range(1, 4):
                    th = math.pi * i / 4.0
                    pts.append((j * p + 0.5 * p * (1.0 - math.cos(th)),
                                y_edge + sign * (depth - (depth - 1.0) * math.sin(th))))
            else:
                pts.append((j * p + 0.5 * p, y_edge + sign * 1.0))
            pts.append(((j + 1) * p, y_edge + sign * depth))
        return pts

    outline = profile(0.0, 1.0) + list(reversed(profile(Hy, -1.0)))
    H = STEM_TOP + 0.5
    sheets = []
    for k in range(n_sheets):
        sh = pliego.Sheet(f"layer-{k + 1}", outline, stock=TISSUE, grain_deg=90.0,
                          label=L4(f"Tissue layer {k + 1}", f"Capa de papel de china {k + 1}",
                                   f"Couche de papier de soie {k + 1}",
                                   f"Camada de papel de seda {k + 1}"), front=TINT, back=TINT)
        for j in range(1, n):
            sh.crease((j * p, depth), (j * p, Hy - depth), "valley" if j % 2 else "mountain",
                      180.0, treatment="crease")
        sh.bend((0.0, mid), (sheet_length, mid), name="tie-line")
        sheets.append(sh)
    rep = pliego.papercut.analyze(sheets[0], min_feature_mm=MIN_TISSUE)
    if not rep.ok:
        raise ValueError(f"paper-flowers: a layer fails the papercut check: {rep.issues}")
    arr = sheets[0].build()
    V = arr.vertices
    pleat_e = [e for e in range(len(arr.edges)) if arr.assignment[e] in ("M", "V")]
    sign = {e: (1.0 if round(V[arr.edges[e][0]].x / p) % 2 else -1.0) for e in pleat_e}
    pleated = {e: sign[e] * CLOSED for e in pleat_e}
    half = {e: sign[e] * 90.0 for e in pleat_e}
    tree = pliego.kinematics.pose_arrangement(arr, pleated)
    look = {(round(v.x, 5), round(v.y, 5)): tree[i] for i, v in enumerate(V)}
    tie_x = [tree[i][0] for i, v in enumerate(V) if abs(v.y - mid) < 1e-6]
    axis = (0.5 * (min(tie_x) + max(tie_x)), -mid)
    stem_pose = stem_pose_at(axis)

    def lift(k):                     # both halves of layer k (bottom → top) lift by this much
        return (k + 0.5) * 90.0 / n_sheets

    def layer_k(sheet_id):
        return int(sheet_id.split("-")[1]) - 1

    def initial(sheet_id, uv):
        if sheet_id == "stem":
            return stem_init(uv)
        return (uv[0], H + layer_k(sheet_id) * TISSUE_T, -uv[1])

    def end(sheet_id, uv):
        if sheet_id == "stem":
            return stem_pose(sheet_id, uv)
        q = look[(round(uv[0], 5), round(uv[1], 5))]
        return (q[0], q[1] + H + layer_k(sheet_id) * TISSUE_T, q[2])

    def bloom(sheet_id, uv):
        if sheet_id == "stem":
            return stem_pose(sheet_id, uv)
        k = layer_k(sheet_id)
        x, y = uv
        j = min(max(int(x / p), 0), n - 1)
        xf = (x - j * p) if j % 2 == 0 else (p - (x - j * p))
        yc, g = y - mid, math.radians(lift(k))
        return (xf, H + k * TISSUE_T + abs(yc) * math.sin(g), -mid - yc * math.cos(g))

    s_ang = stem_angles(stem_pose)
    stem_init = root_aligned(stem_pose, "stem", stem_arr)
    for sh in sheets:
        check_isometric(bloom, sh.id, arr, "bloom")
    steps = [
        stem_step(s_ang),
        pliego.Step("pleat", L4("Pleat the stack of tissue like a fan",
                                "Dobla la pila de papel de china en acordeón",
                                "Pliez la pile de papier de soie en accordéon",
                                "Dobre a pilha de papel de seda em sanfona"),
                    [(pliego.assembly.EdgeRef(sh, e), a) for sh in sheets for e, a in
                     half.items()], duration_ms=2500,
                    note=L4("The ends are already trimmed; in practice you trim the folded "
                            "stick.", "Las puntas ya están recortadas; en la práctica se recorta "
                            "la tira ya doblada.", "Les extrémités sont déjà taillées ; en "
                            "pratique, on taille le bâton plié.", "As pontas já estão aparadas; "
                            "na prática, apara-se o bastão dobrado.")),
        pliego.Step("close-up", L4("Press it into a narrow stick on top of the stem",
                                   "Apriétala en una tira angosta sobre el tallo",
                                   "Serrez-la en un bâton étroit sur la tige",
                                   "Aperte-a num bastão estreito sobre o caule"),
                    [(pliego.assembly.EdgeRef(sh, e), a) for sh in sheets for e, a in
                     pleated.items()], duration_ms=2500,
                    note=L4("Wind wire round the middle and onto the stem, then pull the layers "
                            "up one by one (the frame target:bloom).",
                            "Enreda alambre en el centro y bájalo al tallo; luego jala las capas "
                            "hacia arriba una por una (el marco target:bloom).",
                            "Enroulez du fil de fer au milieu et jusqu'à la tige, puis relevez "
                            "les couches une à une (le cadre target:bloom).",
                            "Enrole arame no meio e desça-o pelo caule; depois puxe as camadas "
                            "para cima uma a uma (o quadro target:bloom).")),
    ]
    info = {"pleats": n, "pleat_mm": round(p, 3), "lifts_deg": [round(lift(k), 2)
                                                               for k in range(n_sheets)]}
    return sheets + [stem], steps, initial, {"pleated": end, "bloom": bloom}, info


def stem_step(angles):
    return pliego.Step("roll-stem", L4("Roll a strip of kraft tightly into a stem",
                                       "Enrolla bien apretada una tira de kraft para hacer el "
                                       "tallo", "Roulez serré une bande de kraft pour faire la "
                                       "tige", "Enrole bem apertada uma tira de kraft para fazer "
                                       "o caule"),
                       [(pliego.assembly.EdgeRef(stem, e), a) for e, a in angles.items()],
                       duration_ms=2500,
                       note=L4("Roll it on a skewer or a wire and glue the last edge.",
                               "Enróllala sobre un palito o un alambre y pega la última orilla.",
                               "Roulez-la sur une pique ou un fil de fer et collez le dernier "
                               "bord.", "Enrole-a num palito ou num arame e cole a última "
                               "borda."))


# ── cut-petal flower: a strip of petals wound round the top of the stem ──────
def build_cut_petal():
    c = petal_width
    w = c - NOTCH
    tip_depth = 0.5 * w if tip == "round" else 1.0 * w
    hs = petal_height - tip_depth
    y1, y2 = BASE + 0.35 * hs, BASE + 0.7 * hs
    r0 = STEM_R + 0.3
    n, total = 0, 0.0
    while total < 2.0 * math.pi * turns:            # how many panels make `turns` turns
        r = r0 + AIR * total / (2.0 * math.pi)
        total += 2.0 * math.asin(min(1.0, c / (2.0 * r)))
        n += 1
    length = n * c
    prof = []
    for j in range(n):
        a, b = j * c + NOTCH / 2.0, (j + 1) * c - NOTCH / 2.0
        prof += [(a, BASE), (a, BASE + hs)]
        if tip == "round":
            prof += [(0.5 * (a + b) - 0.5 * w * math.cos(math.pi * i / 4.0),
                      BASE + hs + tip_depth * math.sin(math.pi * i / 4.0)) for i in range(1, 4)]
        else:
            prof.append((0.5 * (a + b), BASE + hs + tip_depth))
        prof += [(b, BASE + hs), (b, BASE)]
    outline = [(0.0, 0.0), (length, 0.0), (length, BASE)] + list(reversed(prof)) + [(0.0, BASE)]
    strip = pliego.Sheet("petals", outline, stock=TISSUE, grain_deg=0.0,
                         label=L4("Petal strip", "Tira de pétalos", "Bande de pétales",
                                  "Tira de pétalas"), front=TINT, back=TINT)
    for j in range(1, n):
        strip.bend((j * c, 0.0), (j * c, BASE))
    for j in range(n):
        a, b = j * c + NOTCH / 2.0, (j + 1) * c - NOTCH / 2.0
        for y in (BASE, y1, y2):
            strip.bend((a, y), (b, y))
    rep = pliego.papercut.analyze(strip, min_feature_mm=MIN_TISSUE)
    if not rep.ok:
        raise ValueError(f"paper-flowers: the petal strip fails the papercut check: {rep.issues}")
    arr = strip.build()
    pts, ctr, turnings = spiral(n, c, r0, AIR)
    cum = [0.0]
    for th in turnings:
        cum.append(cum[-1] + th)
    H = STEM_TOP - BASE + 2.0                      # the band wraps the top of the stem

    def frac(j):
        return cum[j] / cum[-1]

    def flat2(q):            # spiral plane → centred on the stem, mirrored if needed, and
        # turned half a turn so that the flat strip starts on the far side from the stem's strip
        return (ctr[0] - q[0], -MIRROR["petals"] * (q[1] - ctr[1]))

    def flower(sheet_id, uv):
        if sheet_id == "stem":
            return stem_pose(sheet_id, uv)
        u, v = uv
        if v <= BASE + 1e-9:
            q = flat2(on_spiral(pts, c, u))
            return (q[0], H + v, q[1])
        j = min(int(u / c), n - 1)
        p0, p1 = flat2(pts[j]), flat2(pts[j + 1])
        s = (u - j * c) / c
        cx, cz = p0[0] + s * (p1[0] - p0[0]), p0[1] + s * (p1[1] - p0[1])
        nx, nz = (p1[1] - p0[1]) / c, -(p1[0] - p0[0]) / c
        if nx * (cx + p0[0]) / 2 + nz * (cz + p0[1]) / 2 < 0.0:   # point the normal outward
            nx, nz = -nx, -nz
        lift = 8.0 + 52.0 * frac(j)
        curl = 8.0 + 12.0 * frac(j)
        x, y, z = cx, H + BASE, cz
        for lo, hi, ang in ((BASE, y1, lift), (y1, y2, lift + curl), (y2, 1e9, lift + 2 * curl)):
            d = max(0.0, min(v, hi) - lo)
            g = math.radians(ang)
            x, y, z = x + d * math.sin(g) * nx, y + d * math.cos(g), z + d * math.sin(g) * nz
        return (x, y, z)

    stem_pose = stem_pose_at((0.0, 0.0))
    s_ang = stem_angles(stem_pose)
    ang = fold_angles(flower, "petals", arr)
    V = arr.vertices
    roll_e = [e for e in ang if abs(V[arr.edges[e][0]].x - V[arr.edges[e][1]].x) < 1e-6]
    if min(ang[e] for e in roll_e) < 0.0:
        MIRROR["petals"] = -1.0
        ang = fold_angles(flower, "petals", arr)
    if min(ang[e] for e in roll_e) <= 0.0:
        raise ValueError("paper-flowers: the petal strip is not a valley roll round the stem")
    check_isometric(flower, "petals", arr, "flower")
    hinge_e = [e for e in ang if e not in roll_e and abs(V[arr.edges[e][0]].y - BASE) < 1e-6]
    curl_e = [e for e in ang if e not in roll_e and e not in hinge_e]
    for j in range(n):                             # petals open outward: tip farther out than base
        mid_u = (j + 0.5) * c
        base_p, tip_p = flower("petals", (mid_u, BASE)), flower("petals", (mid_u, y2))
        if math.hypot(tip_p[0], tip_p[2]) <= math.hypot(base_p[0], base_p[2]):
            raise ValueError(f"paper-flowers: petal {j} does not open outward")
    petal_init = root_aligned(flower, "petals", arr)
    stem_init = root_aligned(stem_pose, "stem", stem_arr)

    def initial(sheet_id, uv):
        return stem_init(uv) if sheet_id == "stem" else petal_init(uv)

    def refs(edges):
        return [(pliego.assembly.EdgeRef(strip, e), ang[e]) for e in edges]
    steps = [
        stem_step(s_ang),
        pliego.Step("curl-petals", L4("Curl each petal outward between your fingers",
                                      "Riza cada pétalo hacia afuera entre los dedos",
                                      "Recourbez chaque pétale vers l'extérieur entre les doigts",
                                      "Curve cada pétala para fora entre os dedos"),
                    refs(curl_e), duration_ms=2000),
        pliego.Step("wind", L4("Wind the strip round the top of the stem, petals up",
                               "Enrolla la tira alrededor de la punta del tallo, pétalos arriba",
                               "Enroulez la bande autour du haut de la tige, pétales en haut",
                               "Enrole a tira em volta da ponta do caule, pétalas para cima"),
                    refs(roll_e), duration_ms=3000,
                    note=L4("Glue the first end to the stem and the last end to the strip.",
                            "Pega la primera punta al tallo y la última a la tira.",
                            "Collez le premier bout à la tige et le dernier à la bande.",
                            "Cole a primeira ponta no caule e a última na tira.")),
        pliego.Step("open", L4("Open the petals outward, the outer ones most",
                               "Abre los pétalos hacia afuera, más los de fuera",
                               "Ouvrez les pétales vers l'extérieur, surtout ceux du bord",
                               "Abra as pétalas para fora, mais as de fora"),
                    refs(hinge_e), duration_ms=2500),
    ]
    info = {"petals": n, "turns": round(cum[-1] / (2.0 * math.pi), 3),
            "strip_mm": [round(length, 1), round(BASE + petal_height, 1)],
            "petal_mm": [round(w, 2), round(petal_height, 2)]}
    return [strip, stem], steps, initial, {"flower": flower}, info


sheets, steps, initial, frames, info = (build_carnation() if mode == "carnation"
                                        else build_cut_petal())
rep_stem = pliego.papercut.analyze(stem, min_feature_mm=stem_min)
if not rep_stem.ok:
    raise ValueError(f"paper-flowers: the stem fails the papercut check: {rep_stem.issues}")
end_name = "pleated" if mode == "carnation" else "flower"
render_vertices = sum(len(f) for sh in sheets for f in sh.build().faces)
info.update({"stem_mm": [round(stem_w, 1), stem_length], "stem_diameter_mm": round(2 * STEM_R, 2),
             "render_vertices": render_vertices})
print(f"paper-flowers: {mode} {info}")
params = {"colour": colour, "stem_length": stem_length, "stem_stock": stem_stock}
if mode == "carnation":
    params.update({"sheets": n_sheets, "sheet_length": sheet_length, "sheet_width": sheet_width,
                   "pleat": pleat, "ends": ends})
else:
    params.update({"petal_height": petal_height, "petal_width": petal_width, "turns": turns,
                   "tip": tip})
LABEL = {"carnation": L4("Make the carnation", "Hacer el clavel", "Faire l'œillet",
                         "Fazer o cravo"),
         "cut-petal": L4("Make the flower", "Hacer la flor", "Faire la fleur", "Fazer a flor")}
assembly = pliego.Assembly(
    sheets, controls=[pliego.sequence_control(label=LABEL[mode])],
    sequence=pliego.Sequence(steps, mode="kinematic"), initial=initial, targets=frames,
    title="Paper flowers")
doc = assembly.build(cartridge=SLUG, mode=mode, params=params)
result = doc.stamp()
