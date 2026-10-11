"""Gift wrap — sheet-hyperobjects cartridge (Pliego).

Wrapping a box in a sheet of paper. The box is a rigid reference: a box net folded shut and posed
on the table, held folded by the fold program itself (its first step targets every box crease at
the angle it already has, so the kinematic program poses the box rigidly in place). The wrapping
sheet folds round it.

Mode `standard` (the everyday wrap): the paper goes round the box's girth and overlaps on top. At
each end the side flaps are pushed in first: each carries two 45° creases from the box's corners
and folds in as a triangle, its two corners (the ears) folding back over it. The top and bottom
flaps then fold over the triangles and the ears, overlap and are taped, so the paper is never cut
at the corners. Every corner of an end is a degree-5 vertex (sectors 90°, 90°, 90°, 45°, 45°) with
two branches from its straight-folded start; `branch()` solves, once on a single corner, the
branch on which the ear ends tucked between the triangle and the flap, and every corner is driven
along it (the same corner as the bottom of the flat-bottomed paper bag).

Mode `diagonal`: the box sits at 45° in the middle of a square sheet whose side is
(length + width + 2 × height)/√2. The four corners of the sheet come up over the four sides and
onto the top, where the short sides' corners reach the middle and the long sides' corners overlap.
At each corner of the box the paper between two flaps folds in half into a 45° pleat that lies
under the long side's flap: the same degree-5 corner, with the short flap folded first.

The fold program is kinematic (`pliego.Sequence.kinematic_path`), so every in-between state is an
exact rigid state. Real paper bends a little round the box's edges and the overlapping layers have
thickness: that is the physics engine's job. The paper's panels are sized for the box plus the
paper's own thickness, and the overlapping flaps stop just short of flat so their layers do not
coincide.

The script computes the **minimum paper** for the box (standard: girth + 10 mm by length + height
+ 8 mm; diagonal: the square above), checks that the given paper is at least that, trims the
excess the wrap does not use, and checks the wrapped state: the paper closes round the box, the
flaps overlap, the ears and pleats lie under their flaps, and every crease closes
(`kinematics.closure_residual`).
"""

import math

import pliego
from pliego import kinematics


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


def L4(en, es, fr, pt):
    return {"en": en, "es": es, "fr": fr, "pt": pt}


mode = str(PARAM(lambda: mode, "standard"))                  # noqa: F821
box_length = float(PARAM(lambda: box_length, 240.0))         # noqa: F821
box_width = float(PARAM(lambda: box_width, 160.0))           # noqa: F821
box_height = float(PARAM(lambda: box_height, 60.0))          # noqa: F821
paper_width = float(PARAM(lambda: paper_width, 500.0))       # noqa: F821
paper_length = float(PARAM(lambda: paper_length, 500.0))     # noqa: F821
overlap = float(PARAM(lambda: overlap, 20.0))                # noqa: F821
stock = str(PARAM(lambda: stock, "copy-80"))                 # noqa: F821

STOCKS = {"copy-80": 0.10, "kraft-120": 0.16, "kami": 0.08, "washi-kozo-30": 0.08}
if mode not in ("standard", "diagonal"):
    raise ValueError(f"gift-wrap: unknown mode {mode!r}")
if stock not in STOCKS:
    raise ValueError(f"gift-wrap: stock must be one of {tuple(STOCKS)}, got {stock!r}")
BL = pliego.clamp(box_length, 30.0, 500.0)
BW = pliego.clamp(box_width, 30.0, 500.0)
BL, BW = max(BL, BW), min(BL, BW)        # the length is the longer side of the footprint
BH = pliego.clamp(box_height, 10.0, 300.0)
PW = pliego.clamp(paper_width, 100.0, 2000.0)
PL = pliego.clamp(paper_length, 100.0, 2000.0)
OV = pliego.clamp(overlap, 10.0, 80.0)
T = STOCKS[stock] + 0.36                 # paper + box card: the paper's panels clear the box
TOL = 1e-4
PAPER_FRONT = "#b8324a"                  # the printed side of the gift paper (preview colour)
H2 = math.sqrt(0.5)
DOWN_ROT = (0.0, -H2, 0.0, H2)           # sheet-local (u, v) → world (x = v, z = u), front up


def crease_box_net():
    """The rigid box: a net (base, front, top, back; end panels on the front) folded shut."""
    net = [(0.0, 0.0), (2 * BW + 2 * BH, 0.0), (2 * BW + 2 * BH, BL), (BW + BH, BL),
           (BW + BH, BL + BW), (BW, BL + BW), (BW, BL), (0.0, BL)]
    net = net[:1] + [(BW, 0.0), (BW, -BW), (BW + BH, -BW), (BW + BH, 0.0)] + net[1:]
    box = pliego.Sheet("box", net, stock="cardstock-300", grain_deg=0.0,
                       placement=pliego.Placement(rotation=DOWN_ROT),
                       front=pliego.Face("#d8c6a0"), back=pliego.Face("#8a5a35"),
                       label=L4("Box (rigid reference)", "Caja (referencia rígida)",
                                "Boîte (référence rigide)", "Caixa (referência rígida)"))
    marks = [box.crease((u, 0.0), (u, BL), "valley", 90.0, treatment="score")
             for u in (BW, BW + BH, 2 * BW + BH)]
    marks += [box.crease((BW, v), (BW + BH, v), "valley", 90.0, treatment="score")
              for v in (0.0, BL)]
    return box, {m: 90.0 for m in marks}


def branch(s_deg):
    """Flap, corner-line and ear angles on the branch of a wrapped corner on which the ear tucks
    under the flap, when the triangle flap (the one carrying the 45° crease) is at s_deg.

    The corner is a degree-5 vertex: two faces of the box (90° each), the flap that covers the
    end (90°), the ear and the triangle (45° each). Held at 90° on its box edge it keeps 2
    degrees of freedom and, from a straight-folded start, two branches: on one the flap folds in
    and the ear ends between the triangle and the flap. Solved here once on a single corner; the
    angles do not depend on the box's size."""
    v = pliego.Sheet("corner", [(-60.0, -40.0), (0.0, -40.0), (0.0, -30.0), (30.0, -30.0),
                                (60.0, 0.0), (60.0, 60.0), (-60.0, 60.0)])
    c = v.crease((0, 0), (0, 60), "mountain", 90.0)
    f = v.crease((-60, 0), (0, 0), "mountain", 90.0)
    sg = v.crease((0, 0), (60, 0), "mountain", 90.0)
    x = v.crease((0, -30), (0, 0), "mountain", 90.0)
    r = v.crease((0, 0), (30, -30), "valley", 180.0)
    path = kinematics.solve(v, {c: -90.0, x: -90.0}, {sg: s_deg}, fixed=[c], steps=24,
                            along="chord")
    return {m: path[-1][k.edges()[0]] for m, k in (("flap", f), ("ext", x), ("ear", r))}


def layer_depths(arr, angles, root, to_world, samples, axis, at):
    """World coordinate `axis` (0 x, 1 y, 2 z) of the plane of each face holding a paper sample
    point, evaluated at the world point `at`: the order of stacked layers."""
    tr = kinematics.face_transforms(arr, angles, kinematics.root_face(arr, root))
    out = []
    for u, v in samples:
        rm, t = tr[kinematics.root_face(arr, pliego.P(u, v))]
        q = [to_world([sum(rm[i][j] * a_[j] for j in range(3)) + t[i] for i in range(3)])
             for a_ in ((u, 0.0, -v), (u + 1.0, 0.0, -v), (u, 0.0, -v - 1.0))]
        d1 = [q[1][k] - q[0][k] for k in range(3)]
        d2 = [q[2][k] - q[0][k] for k in range(3)]
        n = [d1[1] * d2[2] - d1[2] * d2[1], d1[2] * d2[0] - d1[0] * d2[2],
             d1[0] * d2[1] - d1[1] * d2[0]]
        others = [k for k in range(3) if k != axis]
        out.append(q[0][axis] - sum(n[k] * (at[k] - q[0][k]) for k in others) / n[axis])
    return out


ON_SIDE = mode == "standard" and BH > BW    # the standard wrap lays a tall box on its side
if ON_SIDE:
    BW, BH = BH, BW
box, BOX_ANG = crease_box_net()


def standard():
    """The everyday wrap: girth round the box, overlap on top, folded ends."""
    w, h = BW + 2 * T, BH + 2 * T        # paper panels: the box plus the layers' thickness
    girth = 2 * (w + h)
    seam = PW - girth                    # girth overlap (the strip that goes over the top)
    e_min = h / 2 + 4.0                  # top and bottom flaps overlap by at least 8 mm
    e = (PL - BL) / 2                    # end extension the paper allows
    e_max = h / 2 + min(OV, h - 4.0) / 2   # end overlap at most `overlap`, and inside the end
    need_w, need_l = girth + 10.0, BL + 2 * e_min
    if seam < 10.0 or e < e_min:
        raise ValueError(f"gift-wrap: the paper ({PW:g} x {PL:g} mm) is too small: this box needs "
                         f"at least {need_w:.0f} x {need_l:.0f} mm")
    seam_used, e_used = min(seam, OV), min(e, e_max)
    et = h / 2                           # the side flaps end in triangles h/2 deep
    X1, X2, X3, X4 = w, w + h, 2 * w + h, girth
    D = 1.0                              # the top's end flaps start 1 mm in from the seam corner
    low = [(0.0, 0.0), (D, 0.0), (D, -e_used), (X1, -e_used), (X1, -et), (X2, -et),
           (X2, -e_used), (X3, -e_used), (X3, -et), (X4, -et), (X4, 0.0)]
    ring = low + [(X4 + seam_used, 0.0), (X4 + seam_used, BL)] + [
        (u, BL - v) for u, v in reversed(low)]
    paper = pliego.Sheet("paper", ring, stock=stock, grain_deg=0.0,
                         placement=pliego.Placement(origin=(0.0, BH + T, -T), rotation=DOWN_ROT),
                         front=pliego.Face(PAPER_FRONT),
                         label=L4("Wrapping paper", "Papel de envolver", "Papier cadeau",
                                  "Papel de embrulho"))

    def mc(a, b, ang=90.0, kind="mountain", name=None):
        return paper.crease(a, b, kind, ang, treatment="crease", name=name)

    girth_m = [mc((u, 0.0), (u, BL)) for u in (X1, X2, X3)]
    seam_m = mc((X4, 0.0), (X4, BL), 89.0, name="seam")
    ends = []
    for v0, sgn in ((0.0, -1.0), (BL, 1.0)):
        end = {"ext": [mc((u, v0), (u, v0 + sgn * et)) for u in (X1, X2, X3)],
               "top": mc((D, v0), (X1, v0), name="end-flap"),
               "sides": [mc((a, v0), (b, v0), name="side-flap") for a, b in ((X1, X2), (X3, X4))],
               "bottom": mc((X2, v0), (X3, v0), name="end-flap"),
               "ears": [mc((u, v0), (u + d * et, v0 + sgn * et), 180.0, "valley")
                        for u, d in ((X1, 1.0), (X2, -1.0), (X3, 1.0), (X4, -1.0))]}
        ends.append(end)

    def end_pose(end, s_deg, b):
        return ([(m, s_deg) for m in end["sides"]] + [(end["top"], b["flap"]),
                                                      (end["bottom"], b["flap"])]
                + [(m, b["ext"]) for m in end["ext"]] + [(m, b["ear"]) for m in end["ears"]])

    half, down = branch(-50.0), branch(-89.6)
    steps = [
        pliego.Step("front-bottom", L4("Bring the paper down the front and under the box",
                                       "Baja el papel por el frente y pásalo bajo la caja",
                                       "Rabattez le papier sur l'avant et sous la boîte",
                                       "Desça o papel pela frente e passe-o sob a caixa"),
                    [(girth_m[0], -90.0), (girth_m[1], -90.0)]
                    + [(m, -90.0) for end in ends for m in end["ext"][:2]], duration_ms=2500),
        pliego.Step("back-seam", L4("Bring it up the back and over the top; tape the overlap",
                                    "Súbelo por detrás y sobre la tapa; pega con cinta el "
                                    "traslape", "Remontez-le à l'arrière et sur le dessus ; "
                                    "scotchez le recouvrement", "Suba-o por trás e sobre a "
                                    "tampa; cole com fita a sobreposição"),
                    [(girth_m[2], -90.0), (seam_m, -89.0)]
                    + [(end["ext"][2], -90.0) for end in ends], duration_ms=2500),
    ]
    for k, end in enumerate(ends, 1):
        steps += [
            pliego.Step(f"end-{k}-sides", L4(f"End {k}: push the side flaps in; they fold into "
                                             "triangles and the top and bottom flaps come down",
                                             f"Extremo {k}: mete las solapas laterales; se "
                                             "doblan en triángulos y bajan las solapas de "
                                             "arriba y de abajo",
                                             f"Bout {k} : rentrez les rabats latéraux ; ils se "
                                             "replient en triangles et les rabats du haut et du "
                                             "bas s'abaissent",
                                             f"Ponta {k}: empurre as abas laterais para dentro; "
                                             "dobram-se em triângulos e as abas de cima e de "
                                             "baixo descem"),
                        end_pose(end, -50.0, half), duration_ms=2200),
            pliego.Step(f"end-{k}-flaps", L4(f"End {k}: fold the top flap down and the bottom "
                                             "flap up over it; tape",
                                             f"Extremo {k}: baja la solapa de arriba y sube "
                                             "sobre ella la de abajo; pega con cinta",
                                             f"Bout {k} : rabattez le rabat du haut puis "
                                             "relevez celui du bas par-dessus ; scotchez",
                                             f"Ponta {k}: baixe a aba de cima e suba a de "
                                             "baixo por cima dela; cole com fita"),
                        end_pose(end, -89.6, down), duration_ms=2200),
        ]
    program = pliego.Sequence.kinematic_path(paper, steps, substeps=6)
    final = {}
    for st in program.steps:
        for t, a in st.targets:
            final[t.edge] = a
    arr = paper.build()
    res = kinematics.closure_residual(arr, final, pliego.P(w / 2, BL / 2))
    pose = kinematics.pose_arrangement(arr, final, pliego.P(w / 2, BL / 2))

    def world(u, v):                     # paper-local → world (DOWN_ROT, then the origin)
        for i, p in enumerate(arr.vertices):
            if abs(p.x - u) < 1e-6 and abs(p.y - v) < 1e-6:
                x, y, z = pose[i]
                return (-z, y + BH + T, x - T)
        raise ValueError(f"gift-wrap: no paper vertex at ({u}, {v})")

    seam_gap = math.dist(world(X4, BL), (BL, BH + T, -T))
    corner = math.dist(world(X2, 0.0), (0.0, -T, BW + T))
    tip_top, tip_bottom = world(D, -e_used), world(X2, -e_used)
    reach = tip_top[1] - tip_bottom[1]
    if max(seam_gap, corner) > TOL or res > 1e-6:
        raise ValueError(f"gift-wrap: the wrap does not close ({seam_gap:.3g}, {corner:.3g} mm, "
                         f"residual {res:.3g})")
    if abs(tip_top[0] + e_used * math.sin(math.radians(90 + down["flap"]))) > 1.0 \
            or reach > -(2 * e_used - h) + 0.5:
        raise ValueError(f"gift-wrap: the end flaps do not overlap on the end ({reach:.2f} mm)")
    # at end 1 (outside is −x): side triangle inside, ear, top flap outside
    ear = [world(X1, 0.0), world(X1, -et), world(X1 + et, -et)]
    at = [sum(p[k] for p in ear) / 3 for k in range(3)]
    depth = layer_depths(arr, final, pliego.P(w / 2, BL / 2),
                         lambda q: (-q[2], q[1] + BH + T, q[0] - T),
                         [(X1 + 0.6 * et, -0.2 * et), (X1 + et / 3, -2 * et / 3), (D + 1.0, -1.0)],
                         0, at)
    if not depth[0] > depth[1] > depth[2]:
        raise ValueError(f"gift-wrap: the ears are not tucked under the end flaps: {depth}")
    report = (f"min_paper={need_w:.0f}x{need_l:.0f}mm paper={PW:g}x{PL:g}mm "
              f"used={X4 + seam_used:.0f}x{BL + 2 * e_used:.0f}mm "
              f"trimmed={'yes' if seam > OV or e > e_max else 'no'} seam={seam_used:.1f}mm "
              f"end_overlap={2 * e_used - h:.1f}mm ears_tucked={depth[0] - depth[2]:.2f}mm "
              f"closure={res:.1e}mm")
    targets = {"paper": {"angles": dict(final), "root": (w / 2, BL / 2)}}
    return paper, program, targets, report


def diagonal():
    """The diagonal wrap: the box set at 45° in the middle of a square sheet; the four corners of
    the sheet come up over the four sides and onto the top."""
    L, W, H = BL + 2 * T, BW + 2 * T, BH + 2 * T
    R = (L + W) / 2 + H                  # centre of the box to a corner of the sheet
    side = R * math.sqrt(2.0)            # the sheet is a square of this side, turned 45°
    if min(PW, PL) < side:
        raise ValueError(f"gift-wrap: the diagonal wrap of this box needs a square of paper at "
                         f"least {side:.0f} mm on a side; the paper is {PW:g} x {PL:g} mm")
    ring = [(-R, 0.0), (0.0, -R), (R, 0.0), (0.0, R)]
    paper = pliego.Sheet("paper", ring, stock=stock, grain_deg=45.0,
                         placement=pliego.Placement(origin=(-(L + H) + 0.0, BH + T, 0.0),
                                                    rotation=(0.0, 1.0, 0.0, 0.0)),
                         front=pliego.Face(PAPER_FRONT),
                         label=L4("Wrapping paper (a square, the box set diagonally on it)",
                                  "Papel de envolver (un cuadrado, con la caja en diagonal)",
                                  "Papier cadeau (un carré, la boîte posée en diagonale)",
                                  "Papel de embrulho (um quadrado, com a caixa na diagonal)"))

    def mc(a, b, ang=90.0, kind="mountain", name=None):
        return paper.crease(a, b, kind, ang, treatment="crease", name=name)

    hl, hw = L / 2, W / 2
    edge = {"left": mc((-hl, -hw), (-hl, hw)), "right": mc((hl, -hw), (hl, hw)),
            "front": mc((-hl, -hw), (hl, -hw)), "back": mc((-hl, hw), (hl, hw))}
    top = {"left": mc((-hl - H, -hw), (-hl - H, hw), name="top-fold"),
           "right": mc((hl + H, -hw), (hl + H, hw), name="top-fold"),
           "front": mc((-hl, -hw - H), (hl, -hw - H), name="top-fold"),
           "back": mc((-hl, hw + H), (hl, hw + H), name="top-fold")}
    corners = []
    for su in (-1.0, 1.0):
        for sv in (-1.0, 1.0):
            v0 = (su * hl, sv * hw)
            corners.append({
                "short": "left" if su < 0 else "right",
                "long": "front" if sv < 0 else "back",
                # the extension of the short edge: between the wedge and the long flap
                "ext": mc(v0, (su * hl, sv * (hw + H))),
                # the extension of the long edge: between the short flap and the wedge
                "flap": mc(v0, (su * (hl + H), sv * hw)),
                "ear": mc(v0, (su * (hl + H / 2), sv * (hw + H / 2)), 180.0, "valley")})

    def short_fold(name):
        return [(edge[name], -90.0)] + [(c["ext"], -90.0) for c in corners if c["short"] == name]

    sb = branch(-89.6)
    steps = [
        pliego.Step("left", L4("Bring the left corner of the sheet over the short side and under "
                               "the box", "Lleva la esquina izquierda de la hoja sobre el lado "
                               "corto y bajo la caja", "Amenez le coin gauche de la feuille sur "
                               "le petit côté et sous la boîte", "Leve o canto esquerdo da folha "
                               "sobre o lado curto e sob a caixa"),
                    [(top["left"], -90.0)] + short_fold("left"), duration_ms=2500),
        pliego.Step("right", L4("Raise the right corner against the other short side",
                                "Levanta la esquina derecha contra el otro lado corto",
                                "Relevez le coin droit contre l'autre petit côté",
                                "Levante o canto direito contra o outro lado curto"),
                    short_fold("right"), duration_ms=2000),
        pliego.Step("long-sides", L4("Raise the front and back corners: the paper at each corner "
                                     "of the box folds into a 45° pleat against the long side",
                                     "Levanta las esquinas de delante y de atrás: en cada esquina "
                                     "de la caja el papel se dobla en un pliegue a 45° contra el "
                                     "lado largo", "Relevez les coins avant et arrière : à chaque "
                                     "coin de la boîte le papier forme un pli à 45° contre le "
                                     "grand côté", "Levante os cantos da frente e de trás: em "
                                     "cada canto da caixa o papel dobra-se numa prega a 45° "
                                     "contra o lado comprido"),
                    [(edge["front"], sb["flap"]), (edge["back"], sb["flap"])]
                    + [(c["flap"], -89.6) for c in corners]
                    + [(c["ext"], sb["ext"]) for c in corners]
                    + [(c["ear"], sb["ear"]) for c in corners], duration_ms=3000),
        pliego.Step("right-top", L4("Fold the right corner over the top",
                                    "Dobla la esquina derecha sobre la tapa",
                                    "Rabattez le coin droit sur le dessus",
                                    "Dobre o canto direito sobre a tampa"),
                    [(top["right"], -90.0)], duration_ms=1500),
        pliego.Step("long-tops", L4("Fold the front corner over, then the back corner on top of "
                                    "it; tape where they meet", "Dobla la esquina de delante y "
                                    "encima la de atrás; pega con cinta donde se juntan",
                                    "Rabattez le coin avant, puis le coin arrière par-dessus ; "
                                    "scotchez là où ils se rejoignent", "Dobre o canto da frente "
                                    "e por cima o de trás; cole com fita onde se encontram"),
                    [(top["front"], -90.0), (top["back"], -89.5)], duration_ms=2000),
    ]
    program = pliego.Sequence.kinematic_path(paper, steps, substeps={
        "left": 6, "right": 6, "long-sides": 10, "right-top": 4, "long-tops": 6})
    final = {}
    for st in program.steps:
        for t, a in st.targets:
            final[t.edge] = a
    arr = paper.build()
    root = pliego.P(-R + 1.0, 0.0)
    res = kinematics.closure_residual(arr, final, root)
    pose = kinematics.pose_arrangement(arr, final, root)

    def world(u, v):                     # paper-local → world (a half turn about Y, then origin)
        for i, p in enumerate(arr.vertices):
            if abs(p.x - u) < 1e-6 and abs(p.y - v) < 1e-6:
                x, y, z = pose[i]
                return (-x - (L + H), y + BH + T, -z)
        raise ValueError(f"gift-wrap: no paper vertex at ({u}, {v})")

    checks = [math.dist(world(-hl, -hw), (-hl, -T, -hw)), math.dist(world(hl, hw), (hl, -T, hw)),
              math.dist(world(-hl - H, -hw), (-hl, BH + T, -hw))]
    worst = max(checks)
    if worst > 0.5 or res > 1e-6:
        raise ValueError(f"gift-wrap: the diagonal wrap does not close ({checks}, residual "
                         f"{res:.3g})")
    # left-front corner, on the front side (outside is −z): the wedge half by the short flap
    # inside, the other half, then the front flap outside
    tip = (-hl - H / 2, -hw - H / 2)
    at = [sum(world(*p)[k] for p in ((-hl, -hw), (-hl, -hw - H), tip)) / 3 for k in range(3)]
    depth = layer_depths(arr, final, root, lambda q: (-q[0] - (L + H), q[1] + BH + T, -q[2]),
                         [(-hl - 0.6 * H, -hw - 0.15 * H), (-hl - 0.15 * H, -hw - 0.6 * H),
                          (-hl + 2.0, -hw - 2.0)], 2, at)
    if not depth[0] > depth[1] > depth[2]:
        raise ValueError(f"gift-wrap: the corner pleats are not under the long flaps: {depth}")
    report = (f"min_paper={side:.0f}x{side:.0f}mm (square, box at 45°) paper={PW:g}x{PL:g}mm "
              f"trim_to={side:.0f}x{side:.0f}mm long_overlap_on_top={L - W:.1f}mm "
              f"corners={worst:.2f}mm pleats_tucked={depth[0] - depth[2]:.2f}mm "
              f"closure={res:.1e}mm")
    targets = {"paper": {"angles": dict(final), "root": (-R + 1.0, 0.0)}}
    return paper, program, targets, report


if mode == "standard":
    paper, program, wrapped, report = standard()
    box_origin = (0.0, 0.0, 0.0)
    box_rot = DOWN_ROT
else:
    paper, program, wrapped, report = diagonal()
    box_origin = (-BL / 2, 0.0, -BW / 2)
    box_rot = DOWN_ROT
box.placement = pliego.Placement(origin=box_origin, rotation=box_rot)
side_note = " (laid on its side)" if ON_SIDE else ""
print(f"gift-wrap: mode={mode} box={BL:g}x{BW:g}x{BH:g}mm{side_note} "
      f"{report} steps={len(program.steps)}")
BOX_POSE = {"angles": dict(BOX_ANG), "root": (BW / 2, BL / 2)}
# The box is held by the fold program: its first step targets every box crease at the angle the
# `initial` frame already gives it, so a kinematic program owns the box and poses it rigidly where
# it stands (spec §5.6: a crease holds its angle between steps). No mechanism is needed, and the
# box keeps its folded shape in the engine too (a kinematic board would be posed flat).
program.steps[0].targets.extend((m, a) for m, a in BOX_ANG.items())
result = pliego.Assembly(
    [box, paper],
    controls=[pliego.sequence_control(label=L4("Wrap the box", "Envolver la caja",
                                               "Emballer la boîte", "Embrulhar a caixa"))],
    sequence=program,
    initial={"box": BOX_POSE},
    targets={"wrapped": dict(wrapped, box=BOX_POSE)},
    title="Gift wrap",
)
