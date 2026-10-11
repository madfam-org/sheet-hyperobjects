"""Kusudama — sheet-hyperobjects cartridge (Pliego).

The traditional glued flower ball: identical petals, each folded from a square, five petals glued
side by side into a flower, twelve flowers glued into a ball (one flower per face of a
dodecahedron). The petal is the traditional glued-petal construction, derived here (no designer's
modular unit, no copied diagram):

1. fold the square on its diagonal A–C (D lands on B);
2. bring the two base corners A and C up to the apex B: a diamond of a quarter of the square, its
   90° corner at the centre O of the square (creases: the two midlines through O);
3. roll the diamond into a cone around O, coloured side out, the flaps inside, and glue the seam
   where the two edges of the diamond overlap by `OVERLAP_DEG`.

Geometry. Every crease passes through O, so the folded petal is a single-vertex fold: each sheet
sector maps onto the diamond by a rotation or reflection about O (the flat fold), and the diamond
wraps onto a cone whose development angle is Ψ = 90° − overlap. Rolled paper is segmented (the
commons convention): the cone is a pyramid of planar facets whose edges are rulings from O, `F`
lines handed to the document untreated (`none`). Its cross-section is designed for the flower:
an inner facet (holding the glued seam), two contact facets lying in the planes ±36° about the
flower axis (each petal is glued face to face to its neighbours there) and `n_o` outer facets
whose profile flares by `flare`; the contact width is solved so the facets add up to Ψ. Every
layer of the flat-folded stack carries the rulings at the same diamond angles, so the stack rolls
as one: the loop around O closes for any roll (checked with `pliego.kinematics.closure_residual`).

On the sheet (turned by TURN) the outer corner B is the lower-left corner, A the upper-left, C
the lower-right and D the upper-right; the diagonal fold is A–C.

Modes.
- `petal`: one square; a kinematic program (diagonal, corners up, curl, close) that ends exactly
  in the petal, also written as `target:petal`.
- `flower`: five petal sheets; `initial` = the glued flower; glue joins (five seams, five
  petal-to-petal welds, exact in the closed form); a physical program squeezes the flower in the
  hand and eases it back (the end state is the glued flower again).
- `ball`: twelve flowers (60 petal sheets) with one outer facet per petal (the render budget),
  each flower on a face of a dodecahedron with its petals pointing at the face's edge midpoints,
  at the radius where neighbouring flowers just touch. Seams and petal welds are glue; touching
  petals of neighbouring flowers meet along a rim chord and are joined at both ends by short
  strings (a dab of glue at a line contact cannot be an area weld). Its physical program presses
  one petal and eases it back.
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


SLUG = "kusudama"
STOCKS = ("kami", "washi-kozo-30", "copy-80")
OVERLAP_DEG = 10.0     # how far the two edges of the diamond overlap at the seam (glue zone)
INNER_HALF = 15.0      # half width of the inner (seam) facet, deg of development
SQUEEZE = 0.6          # flower and ball programs: a press opens the rolls to 60 % of angle
FLOWER_OUTER = 4       # outer facets per petal (flower and petal modes)
BALL_OUTER = 1         # outer facets per petal in the ball (60 sheets: render budget)

mode = str(PARAM(lambda: mode, "petal"))                              # noqa: F821
size = pliego.clamp(PARAM(lambda: size, 75.0), 50.0, 150.0)           # noqa: F821
flare = pliego.clamp(PARAM(lambda: flare, 4.0), 0.0, 8.0)             # noqa: F821
stock = str(PARAM(lambda: stock, "kami"))                             # noqa: F821
colour = str(PARAM(lambda: colour, "#d9382b"))                        # noqa: F821
if mode not in ("petal", "flower", "ball"):
    raise ValueError(f"kusudama: mode must be petal, flower or ball, got {mode!r}")
if stock not in STOCKS:
    raise ValueError(f"kusudama: stock must be one of {STOCKS}, got {stock!r}")

A_ = size
H = A_ / 2.0
CTR = (H, H)                       # the centre of the square (the petal tip)
DELTA = OVERLAP_DEG
PSI = 90.0 - DELTA                 # development angle of the rolled cone
N_OUT = BALL_OUTER if mode == "ball" else FLOWER_OUTER
R = math.radians


def v_add(p, q, k=1.0):
    return tuple(p[i] + k * q[i] for i in range(3))


def v_dot(p, q):
    return p[0] * q[0] + p[1] * q[1] + p[2] * q[2]


def v_cross(p, q):
    return (p[1] * q[2] - p[2] * q[1], p[2] * q[0] - p[0] * q[2], p[0] * q[1] - p[1] * q[0])


def v_unit(p):
    n = math.sqrt(v_dot(p, p))
    return tuple(x / n for x in p)


def ang(p, q):
    return math.degrees(math.atan2(math.sqrt(v_dot(v_cross(p, q), v_cross(p, q))), v_dot(p, q)))


def ray(az, polar):
    """Unit ray in the petal frame: x radial (the petal's own azimuth), y tangential, z = the
    flower axis; az measured about z, polar from z (deg)."""
    return (math.sin(R(polar)) * math.cos(R(az)), math.sin(R(polar)) * math.sin(R(az)),
            math.cos(R(polar)))


def mirror(p):
    return (p[0], -p[1], p[2])


# ── the petal's cross-section (the pyramid of the rolled cone) ──
SPIN = -1.0                        # which side ψ grows towards (fixed by the valley-roll check)
theta_i = math.degrees(math.asin(math.sin(R(INNER_HALF)) / math.sin(R(36.0))))


def chain(w_c, n_o, fl):
    """Rays of one cross-section: contact edge R+ → outer facets → R−, profile flared by fl."""
    th_r = theta_i + w_c
    out = []
    for j in range(n_o + 1):
        az = 36.0 * SPIN * (1.0 - 2.0 * j / n_o)
        out.append(ray(az, th_r + fl * (1.0 - (az / 36.0) ** 2)))
    return out


def total(w_c, n_o, fl):
    c = chain(w_c, n_o, fl)
    return 2.0 * INNER_HALF + 2.0 * w_c + sum(ang(c[j], c[j + 1]) for j in range(n_o))


lo_w, hi_w = 0.5, 40.0
if not (total(lo_w, N_OUT, flare) < PSI < total(hi_w, N_OUT, flare)):
    raise ValueError("kusudama: no petal cross-section closes for this flare")
for _ in range(200):
    mid = 0.5 * (lo_w + hi_w)
    lo_w, hi_w = (mid, hi_w) if total(mid, N_OUT, flare) < PSI else (lo_w, mid)
W_C = 0.5 * (lo_w + hi_w)
if W_C < 2.0:
    raise ValueError(f"kusudama: the contact facet is only {W_C:.2f}° wide; lower the flare")
I_IN = ray(36.0 * SPIN, theta_i)                 # inner ray on the R+ side
OUT = chain(W_C, N_OUT, flare)
RAYS = [mirror(I_IN), I_IN] + OUT + [mirror(I_IN)]
PSIS = [DELTA / 2.0 - INNER_HALF]
for k in range(len(RAYS) - 1):
    PSIS.append(PSIS[-1] + ang(RAYS[k], RAYS[k + 1]))
if abs(PSIS[-1] - (PSIS[0] + PSI)) > 1e-9:
    raise ValueError(f"kusudama: the facets do not close ({PSIS[-1] - PSIS[0] - PSI:.3g}°)")
PSIS[-1] = PSIS[0] + PSI


def cone_point(rays, psis, phi, r):
    """Diamond point (angle phi ∈ [270, 360], radius r) → petal frame (the rolled cone)."""
    if r < 1e-12:
        return (0.0, 0.0, 0.0)
    psi = phi - 270.0
    if psi > psis[-1] + 1e-9:
        psi -= PSI
    k = 0
    while k < len(psis) - 2 and psi > psis[k + 1]:
        k += 1
    a, b = rays[k], rays[k + 1]
    w = R(psis[k + 1] - psis[k])
    wv = tuple((b[i] - math.cos(w) * a[i]) / math.sin(w) for i in range(3))
    t = R(psi - psis[k])
    return tuple(r * (math.cos(t) * a[i] + math.sin(t) * wv[i]) for i in range(3))


# Each sheet sector around O lands on the diamond (sheet angles 270–360) by a rotation or a
# reflection about O: (upper sheet angle, matrix) acting on (x, y) − O.
DMAP = ((45.0, (1, 0, 0, -1)), (90.0, (0, 1, -1, 0)), (180.0, (0, 1, 1, 0)),
        (225.0, (0, -1, 1, 0)), (270.0, (-1, 0, 0, 1)), (360.0, (1, 0, 0, 1)))


# The design is written with the outer quarter at sheet angles 270–360 and turned by TURN on the
# sheet, so the preview's root face (the one at the lower-left corner) lies in the outer quarter
# and the petal rolls up off the table.
TURN = 270.0


def diamond(uv):
    c, s = math.cos(R(TURN)), math.sin(R(TURN))
    x0, y0 = uv[0] - CTR[0], uv[1] - CTR[1]
    x, y = c * x0 + s * y0, -s * x0 + c * y0
    th = math.degrees(math.atan2(y, x)) % 360.0
    m = next(mm for hi, mm in DMAP if th < hi + 1e-9)
    dx, dy = m[0] * x + m[1] * y, m[2] * x + m[3] * y
    phi = math.degrees(math.atan2(dy, dx)) % 360.0
    if phi < 180.0:
        phi += 360.0
    return phi, math.hypot(dx, dy)


def petal_pose(rays=RAYS, psis=PSIS):
    def pose(sheet_id, uv):
        phi, r = diamond(uv)
        return cone_point(rays, psis, phi, r)
    return pose


# ── the sheet: square, creases through O, rulings at the facet edges ──
base = pliego.Sheet(
    "petal", [(0.0, 0.0), (A_, 0.0), (A_, A_), (0.0, A_)], stock=stock, grain_deg=90.0,
    label=L4("Petal square", "Cuadrado del pétalo", "Carré du pétale", "Quadrado da pétala"),
    front="#f6f3ec", back=colour)


def rim(th):
    """Point where the ray from O at sheet angle th (deg) leaves the square."""
    c, s = math.cos(R(th + TURN)), math.sin(R(th + TURN))
    t = min(H / abs(c) if abs(c) > 1e-12 else 1e18, H / abs(s) if abs(s) > 1e-12 else 1e18)
    return (CTR[0] + t * c, CTR[1] + t * s)


CREASES = ((45.0, "valley"), (225.0, "valley"), (270.0, "valley"), (0.0, "valley"),
           (90.0, "mountain"), (180.0, "mountain"))
for th, kind in CREASES:
    base.crease(CTR, rim(th), kind, 180.0)
RULE_PHI = [270.0 + p for p in PSIS[1:]]
ruling_th = []
for phi in RULE_PHI:
    ruling_th += [phi % 360.0, (450.0 - phi) % 360.0]                    # B and D quarters
    if phi < 315.0 - 1e-9:
        ruling_th += [540.0 - phi, phi - 90.0]                           # the A flap
    elif phi > 315.0 + 1e-9:
        ruling_th += [360.0 - phi, phi - 270.0]                          # the C flap
for th in ruling_th:
    base.crease(CTR, rim(th), "flat", 0.0, treatment="crease")
cut_check = pliego.papercut.analyze(base, min_feature_mm=1.0)
if not cut_check.ok:
    raise ValueError(f"kusudama: the square fails the papercut check: {cut_check.issues}")
arr = base.build()


def newell(pts):
    n = [0.0, 0.0, 0.0]
    for i, p in enumerate(pts):
        q = pts[(i + 1) % len(pts)]
        n[0] += (p[1] - q[1]) * (p[2] + q[2])
        n[1] += (p[2] - q[2]) * (p[0] + q[0])
        n[2] += (p[0] - q[0]) * (p[1] + q[1])
    return v_unit(n)


def to_world(p):
    """Petal frame (z = flower axis) → world (Y up), a proper rotation."""
    return (p[0], p[2], -p[1])


def fold_angles(pose):
    """Signed fold angle (FOLD convention, deg) of every interior F/M/V edge in `pose`."""
    pts = [to_world(pose("petal", (v.x, v.y))) for v in arr.vertices]
    left = {}
    for fi, f in enumerate(arr.faces):
        for k in range(len(f)):
            left[(f[k], f[(k + 1) % len(f)])] = fi
    normals = [newell([pts[v] for v in f]) for f in arr.faces]
    out = {}
    for e, (a, b) in enumerate(arr.edges):
        if arr.assignment[e] in ("F", "M", "V") and (a, b) in left and (b, a) in left:
            edge = tuple(pts[b][i] - pts[a][i] for i in range(3))
            out[e] = pliego.tessellate.signed_fold_angle(normals[left[(a, b)]],
                                                         normals[left[(b, a)]], edge)
    return out


def edge_theta(e):
    a, b = arr.edges[e]
    far = arr.vertices[a] if math.hypot(arr.vertices[a].x - H, arr.vertices[a].y - H) > \
        math.hypot(arr.vertices[b].x - H, arr.vertices[b].y - H) else arr.vertices[b]
    return (math.degrees(math.atan2(far.y - H, far.x - H)) - TURN) % 360.0


def near(th, target):
    return abs((th - target + 180.0) % 360.0 - 180.0) < 1e-6


diag_e = [e for e in range(len(arr.edges)) if arr.assignment[e] in ("M", "V")
          and (near(edge_theta(e), 45.0) or near(edge_theta(e), 225.0))]
mid_e = [e for e in range(len(arr.edges)) if arr.assignment[e] in ("M", "V") and e not in diag_e]
rule_e = [e for e in range(len(arr.edges)) if arr.assignment[e] == "F"]
CREASE_ANGLE = {e: (180.0 if arr.assignment[e] == "V" else -180.0) for e in diag_e + mid_e}
if len(diag_e) != 2 or len(mid_e) != 4:
    raise ValueError(f"kusudama: crease bookkeeping failed ({len(diag_e)}, {len(mid_e)})")


def petal_angles(pose):
    ang_ = fold_angles(pose)
    for e in CREASE_ANGLE:                       # coincident layers: |angle| = 180 exactly
        if abs(abs(ang_[e]) - 180.0) > 1e-3:
            raise ValueError(f"kusudama: crease {e} is not folded flat ({ang_[e]:.4f}°)")
    out = {e: ang_[e] for e in rule_e}
    out.update(CREASE_ANGLE)
    return out


angles = petal_angles(petal_pose())
b_rules = [e for e in rule_e if 270.0 < edge_theta(e) < 360.0]
if min(angles[e] for e in b_rules) <= 0.0:
    raise ValueError("kusudama: the petal is not a valley roll of the outer layer (SPIN)")
worst = 0.0
for t in (0.25, 0.5, 0.75, 1.0):                 # the roll, blended linearly, stays rigid
    st = {e: (a if e in CREASE_ANGLE else t * a) for e, a in angles.items()}
    worst = max(worst, pliego.kinematics.closure_residual(arr, st))
for t in (0.5, 1.0):                             # diagonal, then corners up
    worst = max(worst, pliego.kinematics.closure_residual(
        arr, {**{e: t * CREASE_ANGLE[e] for e in diag_e}}),
        pliego.kinematics.closure_residual(
            arr, {**{e: CREASE_ANGLE[e] for e in diag_e},
                  **{e: t * CREASE_ANGLE[e] for e in mid_e}}))
if worst > 1e-6:
    raise ValueError(f"kusudama: inconsistent rigid state (closure residual {worst:.3g} mm)")


# ── glue: the seam (overlap) and the petal-to-petal welds, in sheet-local coordinates ──
def at(phi, r):
    return (CTR[0] + r * math.cos(R(phi + TURN)), CTR[1] + r * math.sin(R(phi + TURN)))


def rim_r(phi):
    return H / math.cos(R(phi - 270.0 if phi <= 315.0 else 360.0 - phi))


def reflect_map(line_deg):
    c, s = math.cos(R(2.0 * (line_deg + TURN))), math.sin(R(2.0 * (line_deg + TURN)))
    return (c, s, s, -c, CTR[0] - (c * CTR[0] + s * CTR[1]), CTR[1] - (s * CTR[0] - c * CTR[1]))


def apply(m, p):
    return (m[0] * p[0] + m[1] * p[1] + m[4], m[2] * p[0] + m[3] * p[1] + m[5])


def quad(phi0, phi1):
    return [at(phi0, 0.25 * H), at(phi1, 0.25 * H), at(phi1, 0.9 * rim_r(phi1)),
            at(phi0, 0.9 * rim_r(phi0))]


SEAM = quad(270.0 + 0.15 * DELTA, 270.0 + 0.85 * DELTA)      # outer layer, left overlap zone
SEAM_MAP = reflect_map(135.0 + DELTA / 2.0)                  # → the C flap's inner layer
CONTACT = quad(270.0 + 0.85 * PSIS[1] + 0.15 * PSIS[2],      # outer layer on a contact facet
               270.0 + 0.15 * PSIS[1] + 0.85 * PSIS[2])
CONTACT_MAP = reflect_map(135.0)                              # → the neighbour's mirror facet
NEXT = 1 if SPIN * 36.0 > 0 else -1                           # that facet's neighbour (k ± 1)
pose0 = petal_pose()
for p in SEAM:
    gap = math.dist(pose0("petal", p), pose0("petal", apply(SEAM_MAP, p)))
    if gap > 1e-6:
        raise ValueError(f"kusudama: seam weld point {p} misses by {gap} mm")


def rot_z(p, deg):
    c, s = math.cos(R(deg)), math.sin(R(deg))
    return (c * p[0] - s * p[1], s * p[0] + c * p[1], p[2])


for p in CONTACT:                                 # petal k's facet onto petal k+NEXT's
    q = apply(CONTACT_MAP, p)
    gap = math.dist(rot_z(pose0("petal", p), 0.0), rot_z(pose0("petal", q), 72.0 * NEXT))
    if gap > 1e-6:
        raise ValueError(f"kusudama: petal weld point {p} misses its neighbour by {gap} mm")

PETAL_LABEL = ("Petal", "Pétalo", "Pétale", "Pétala")


def petals(prefix, n, lab=""):
    return [base.copy(f"{prefix}{k + 1}", label=L4(*[f"{w} {lab}{k + 1}" for w in PETAL_LABEL]))
            for k in range(n)]


def flower_joins(sheets, tag=""):
    n = len(sheets)
    out = []
    for k, sh in enumerate(sheets):
        out.append(pliego.glue(f"{tag}seam-{k + 1}", sh, SEAM, sh, SEAM_MAP, side="back"))
        out.append(pliego.glue(f"{tag}petal-{k + 1}-{(k + NEXT) % n + 1}", sh, CONTACT,
                               sheets[(k + NEXT) % n], CONTACT_MAP, side="back"))
    return out


def ruling_steps(sheets, target, sid, label, ms=2500, note=None):
    tg = [(pliego.assembly.EdgeRef(sh, e), target[e]) for sh in sheets for e in rule_e]
    return pliego.Step(sid, label, tg, duration_ms=ms, note=note)


params = {"size": size, "flare": flare, "stock": stock, "colour": colour}
render_v = sum(len(f) for f in arr.faces)
info = {"cone_deg": PSI, "contact_facet_deg": round(W_C, 3), "facets": len(RAYS) - 1,
        "faces_per_petal": len(arr.faces), "render_vertices_per_petal": render_v}
SEQ_LABEL = L4("Fold program", "Secuencia de pliegues", "Séquence de pliage",
               "Sequência de dobras")

if mode == "petal":
    print(f"kusudama: {info} max_closure_mm={worst:.2e}")
    half = {e: 0.5 * a for e, a in angles.items()}
    steps = [
        pliego.Step("diagonal", L4("Coloured side down, fold the square in half on the diagonal",
                                   "Con el lado de color hacia abajo, dobla el cuadrado por la "
                                   "diagonal", "Face colorée dessous, pliez le carré en deux sur "
                                   "la diagonale", "Com o lado colorido para baixo, dobre o "
                                   "quadrado ao meio pela diagonal"),
                    [(pliego.assembly.EdgeRef(base, e), CREASE_ANGLE[e]) for e in diag_e],
                    duration_ms=2000),
        pliego.Step("corners-up", L4("Bring the two base corners up to the top corner: a diamond",
                                     "Sube las dos esquinas de la base hasta la punta: queda un "
                                     "rombo", "Remontez les deux coins de la base jusqu'à la "
                                     "pointe : un losange", "Leve os dois cantos da base até a "
                                     "ponta: forma-se um losango"),
                    [(pliego.assembly.EdgeRef(base, e), CREASE_ANGLE[e]) for e in mid_e],
                    duration_ms=2000),
        ruling_steps([base], half, "curl", L4(
            "Curl the diamond around its bottom point, flaps inside",
            "Curva el rombo alrededor de su punta inferior, con las solapas adentro",
            "Enroulez le losange autour de sa pointe inférieure, rabats à l'intérieur",
            "Curve o losango em torno da ponta inferior, com as abas para dentro")),
        ruling_steps([base], angles, "close", L4(
            "Overlap the two edges and glue them: the petal is a cone",
            "Encima un borde sobre el otro y pégalos: el pétalo queda en cono",
            "Faites chevaucher les deux bords et collez-les : le pétale est un cône",
            "Sobreponha as duas bordas e cole-as: a pétala vira um cone"), note=L4(
            f"The edges overlap by {DELTA:g}° around the point; glue only that strip.",
            f"Los bordes se enciman {DELTA:g}° alrededor de la punta; pon pegamento solo en esa "
            "franja.", f"Les bords se chevauchent de {DELTA:g}° autour de la pointe ; ne collez "
            "que cette bande.", f"As bordas se sobrepõem {DELTA:g}° em torno da ponta; passe "
            "cola só nessa faixa.")),
    ]
    steps.append(pliego.Step("press", L4("Hold the seam until the glue sets",
                                         "Sostén la unión hasta que el pegamento agarre",
                                         "Tenez la jointure jusqu'à ce que la colle prenne",
                                         "Segure a junta até a cola pegar"), [], duration_ms=800))
    seam = pliego.glue("seam", base, SEAM, base, SEAM_MAP, side="back")
    seam["active_from"] = "press"          # spec §5.19: the cone's seam glued at its step
    assembly = pliego.Assembly(
        [base], joins=[seam], controls=[pliego.sequence_control(label=SEQ_LABEL)],
        sequence=pliego.Sequence(steps, mode="kinematic"),
        targets={"petal": {"angles": dict(angles)}}, title="Kusudama petal")

elif mode == "flower":
    sheets = petals("petal-", 5)

    def placed(sheet_id, uv):
        k = int(sheet_id.split("-")[1]) - 1
        return to_world(rot_z(pose0("petal", uv), 72.0 * k))

    squeeze = {e: SQUEEZE * a for e, a in angles.items()}
    print(f"kusudama: {info} render_vertices={5 * render_v}")
    steps = [ruling_steps(sheets, squeeze, "press", L4(
        "Press the flower gently against your palm",
        "Presiona la flor con suavidad contra la palma de la mano",
        "Pressez doucement la fleur contre la paume de la main",
        "Pressione a flor com delicadeza contra a palma da mão")),
             ruling_steps(sheets, angles, "let-go", L4(
                 "Ease the petals back into shape: the glue holds",
                 "Devuelve los pétalos a su forma: el pegamento aguanta",
                 "Redonnez leur forme aux pétales : la colle tient",
                 "Devolva a forma às pétalas: a cola segura"))]
    assembly = pliego.Assembly(
        sheets, joins=flower_joins(sheets), initial=placed,
        controls=[pliego.sequence_control(label=L4("Press the flower", "Presionar la flor",
                                                   "Presser la fleur", "Pressionar a flor"))],
        sequence=pliego.Sequence(steps, mode="physical"), targets={"flower": placed},
        layout={s.id: (k * (A_ + 10.0), 0.0) for k, s in enumerate(sheets)},
        title="Kusudama flower")

else:
    # dodecahedron: face normals = icosahedron vertices, face corners = dodecahedron vertices
    G = (1.0 + math.sqrt(5.0)) / 2.0
    normals = [v_unit(p) for s1 in (1, -1) for s2 in (1, -1)
               for p in ((0, s1, s2 * G), (s1, s2 * G, 0), (s2 * G, 0, s1))]
    dverts = [v_unit((x, y, z)) for x in (1, -1) for y in (1, -1) for z in (1, -1)]
    dverts += [v_unit(p) for s1 in (1, -1) for s2 in (1, -1)
               for p in ((0, s1 / G, s2 * G), (s1 / G, s2 * G, 0), (s2 * G, 0, s1 / G))]
    def rot_axis(p, n, deg):
        c, s_ = math.cos(R(deg)), math.sin(R(deg))
        return tuple(c * p[i] + s_ * v_cross(n, p)[i] + (1 - c) * v_dot(n, p) * n[i]
                     for i in range(3))

    frames = []
    for n in normals:
        top = max(v_dot(v, n) for v in dverts)
        v0 = next(v for v in dverts if v_dot(v, n) > top - 1e-9)
        x = v_unit(v_add(v0, n, -v_dot(v0, n)))
        x = rot_axis(x, n, 36.0)               # petal 1 points at an edge midpoint
        frames.append((x, v_cross(n, x), n))

    def in_ball(f, k, p, r0):
        q = rot_z(p, 72.0 * k)
        x, y, z = frames[f]
        return tuple(r0 * z[i] + q[0] * x[i] + q[1] * y[i] + q[2] * z[i] for i in range(3))

    nb = next(m for m in range(1, 12) if abs(v_dot(normals[0], normals[m]) - 1 / math.sqrt(5))
              < 1e-9)
    mvec = v_unit(v_add(normals[nb], normals[0], -1.0))
    outer = [v for v in range(len(arr.vertices))
             if math.hypot(arr.vertices[v].x - H, arr.vertices[v].y - H) > 1e-6
             and (math.degrees(math.atan2(arr.vertices[v].y - H, arr.vertices[v].x - H))
                  - TURN) % 360.0 >= 270.0 - 1e-9]       # vertices of the outer layer (B quarter)
    best = None
    for k in range(5):
        for v in outer:
            p = in_ball(0, k, pose0("petal", (arr.vertices[v].x, arr.vertices[v].y)), 0.0)
            if best is None or v_dot(mvec, p) > best[0] + 1e-9:
                best = (v_dot(mvec, p), k, v)
    R0 = best[0] / -v_dot(mvec, normals[0])
    if R0 <= 0.0:
        raise ValueError("kusudama: the flowers cannot touch on this ball")
    pts = [in_ball(f, k, pose0("petal", (vx.x, vx.y)), R0)
           for f in range(12) for k in range(5) for vx in arr.vertices]
    lift = -min(p[1] for p in pts)
    radius = max(math.sqrt(v_dot(p, p)) for p in pts)

    def ball_pose(sheet_id, uv):
        f, k = int(sheet_id[1:3]) - 1, int(sheet_id[5:]) - 1
        q = in_ball(f, k, pose0("petal", uv), R0)
        return (q[0], q[1] + lift, q[2])

    sheets = []
    joins = []
    for f in range(12):
        fl = petals(f"f{f + 1:02d}-p", 5, f"{f + 1}.")
        sheets += fl
        joins += flower_joins(fl, f"f{f + 1:02d}-")
    # a dab of glue where neighbouring flowers touch: the touching rim vertex, 0.5 mm inside
    vt = arr.vertices[best[2]]
    tip = (vt.x + 0.5 * (H - vt.x) / math.hypot(H - vt.x, H - vt.y),
           vt.y + 0.5 * (H - vt.y) / math.hypot(H - vt.x, H - vt.y))
    tip_m = apply(CONTACT_MAP, tip)
    seen = set()
    for fa in range(12):
        for kb in range(5):
            xa = ball_pose(f"f{fa + 1:02d}-p{kb + 1}", tip)
            for fb in range(12):
                for kc in range(5):
                    if fb == fa or (fb, kc, fa, kb) in seen:
                        continue
                    xb = ball_pose(f"f{fb + 1:02d}-p{kc + 1}", tip_m)
                    if math.dist(xa, xb) < 2.0:
                        seen.add((fa, kb, fb, kc))
                        joins.append(pliego.string(
                            f"dab-{fa + 1}-{kb + 1}-{fb + 1}-{kc + 1}",
                            (sheets[5 * fa + kb], tip), (sheets[5 * fb + kc], tip_m),
                            round(math.dist(xa, xb) + 0.2, 3)))
    if len(seen) != 60:
        raise ValueError(f"kusudama: expected 60 flower-to-flower contacts, found {len(seen)}")
    print(f"kusudama: {info} flower_radius_mm={R0:.3f} ball_diameter_mm={2 * radius:.1f} "
          f"render_vertices={60 * render_v}")
    press = {e: SQUEEZE * a for e, a in angles.items()}
    steps = [ruling_steps([sheets[0]], press, "press-petal", L4(
        "Press one petal gently with a fingertip", "Presiona un pétalo con suavidad con la yema "
        "del dedo", "Appuyez doucement sur un pétale du bout du doigt", "Pressione uma pétala "
        "com delicadeza com a ponta do dedo")),
             ruling_steps([sheets[0]], angles, "ease-back", L4(
                 "Ease it back into shape: the glue holds", "Devuélvele su forma: el pegamento "
                 "aguanta", "Redonnez-lui sa forme : la colle tient", "Devolva-lhe a forma: a "
                 "cola segura"))]
    assembly = pliego.Assembly(
        sheets, joins=joins, initial=ball_pose,
        controls=[pliego.sequence_control(label=L4(
            "Press a petal", "Presionar un pétalo", "Appuyer sur un pétale",
            "Pressionar uma pétala"))],
        sequence=pliego.Sequence(steps, mode="physical"), targets={"ball": ball_pose},
        layout={s.id: ((k % 10) * (A_ + 10.0), (k // 10) * (A_ + 10.0))
                for k, s in enumerate(sheets)}, title="Kusudama ball")

doc = assembly.build(cartridge=SLUG, mode=mode, params=params)
# The rulings are plain paper (spec §4: F + `none`): exporters must not score a rolled surface.
tr = doc.data["pliego:edges_treatment"]
for e, a in enumerate(doc.data["edges_assignment"]):
    if a == "F" and tr[e] == "crease":
        tr[e] = "none"
result = doc.stamp()
