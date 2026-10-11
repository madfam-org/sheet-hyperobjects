"""Rolled paper rose — sheet-hyperobjects cartridge (Pliego).

A spiral strip cut into a disc of paper, leaving an uncut circle in the middle; the strip is rolled
from its outer end inward into a tight bud, let loosen and glued onto the centre circle, which
becomes the rose's base. `edge`: `plain` or `scalloped` (a wavy spiral cut: rounded petal edges).

The spiral. An involute of a circle of radius b = w/2π (w = the strip's width) rather than an
Archimedean spiral: the involute's turns are parallel curves exactly w apart, and every tangent line
of the base circle crosses every turn at right angles. `F` lines lie on those tangent lines
(`panels` stations per turn, the same angles every turn, fewer if the 400-panel render budget
binds), so each is normal to the strip's centreline and every panel is a flat quadrilateral (plain
paper, treatment `none`). The cut removes a 1 mm kerf: the kernel keeps one vertex per point, so a
zero-width slit could not open, and the turns must separate. A scalloped edge offsets the cut along
the F lines by a(t) = A·|sin(n·(t − t0)/2)| (n = 8 scallops per turn, nodes on F lines).

The rolled poses (an approximation; the article explains it). In the flat sheet the strip is
curved: a panel's two F lines meet near the centre at the station step Δt. Rolled onto a coil of
radius ρ, a panel at development distance ℓ (its centreline point to the base circle along its F
line) lies on a cone of half-angle α with sin α = ρ/ℓ, the development of a cone. Each F line gets
the fold angle between two facets of apex angle Δt of a pyramid inscribed in its own cone:
cos Δψ = (cos Δt − cos²α)/sin²α, angle = ∠(g(−Δψ)×g(0), g(0)×g(Δψ)), g = the generators. α changes
slowly along the strip, so the coil is a stack of cones: upright at the core (small ρ, large ℓ),
opening toward flat at the outside: the rose. A curved strip cannot follow a turn wider than its own
curvature radius (ρ ≤ ℓ), so ρ/ℓ is clamped softly at 1 (a parabolic blend over 1 ± 0.15 keeps the
coil's torsion finite): those panels stay flat and lie round the centre circle as in the sheet.
Coil radius ρ(s) = √(ρ0² + g·s/π) along the strip from its outer end, two poses:
- `bud` (rolled tight): g = max(caliper, 1.5 × the core panel's sagitta), a display spacing so the
  panel chords never cut through the turn beneath;
- `rose` (loosened): g puts ρ at (1 + 0.15)·ℓ at the circle's hinge (the last turn settles
  flat), and is at least 1.5 × the bud's.
The fold angle at the circle's hinge is chosen (forward kinematics from the core panel) so the
circle's front faces the coil along its axis; the script fails loud if the loosened rose does not
stand on the circle's front within 15°.

The sheet is turned so the strip's outer end is its leftmost point: the studio preview keeps that
panel (the core of the rose) on the table, so the rose lies on its side in the preview. Valley
rolls: the front ends up inside each turn, and it is the side you see from above.
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


SLUG = "paper-rose"
EDGES = ("plain", "scalloped")
CALIPER = {"copy-80": 0.100, "kraft-120": 0.160, "kami": 0.072, "elephant-hide-110": 0.120}
MIN_FEATURE = {"copy-80": 1.0, "kraft-120": 1.0, "kami": 1.0, "elephant-hide-110": 1.0}
SCALLOPS = 8               # scallops per turn (scalloped edge)
SCALLOP_DEPTH = 0.22       # × strip width
KERF = 1.0                 # mm removed along the spiral cut (see the docstring)
MAX_PANELS = 400           # render budget: about 4 vertices per panel
SOFT = 0.15                # width of the soft clamp of sin α = ρ/ℓ at 1 (flat)

mode = str(PARAM(lambda: mode, "make"))                                 # noqa: F821
edge = str(PARAM(lambda: edge, "plain"))                                # noqa: F821
diameter = pliego.clamp(PARAM(lambda: diameter, 120.0), 80.0, 200.0)   # noqa: F821
width = pliego.clamp(PARAM(lambda: width, 12.0), 8.0, 20.0)            # noqa: F821
base = pliego.clamp(PARAM(lambda: base, 30.0), 20.0, 50.0)             # noqa: F821
panels = int(pliego.clamp(PARAM(lambda: panels, 96), 48, 144))         # noqa: F821
stock = str(PARAM(lambda: stock, "copy-80"))                            # noqa: F821
colour = str(PARAM(lambda: colour, "#c8102e"))                          # noqa: F821
if mode != "make":
    raise ValueError(f"paper-rose: mode must be make, got {mode!r}")
if edge not in EDGES:
    raise ValueError(f"paper-rose: edge must be one of {EDGES}, got {edge!r}")
if stock not in CALIPER:
    raise ValueError(f"paper-rose: stock must be one of {tuple(CALIPER)}, got {stock!r}")
N = panels - panels % SCALLOPS                 # stations per turn, a multiple of the scallops
R, w, rb = diameter / 2.0, width, base / 2.0
b = w / (2.0 * math.pi)
turns_needed = (R - w - rb) / w
if turns_needed < 1.5:
    raise ValueError(f"paper-rose: a {diameter:g} mm disc with a {base:g} mm centre leaves only "
                     f"{turns_needed:.1f} turns of a {w:g} mm strip; use a bigger disc, a narrower "
                     f"strip or a smaller centre")
N = min(N, int(MAX_PANELS / turns_needed) // SCALLOPS * SCALLOPS)   # render budget
if N < 48:
    raise ValueError(f"paper-rose: {turns_needed:.1f} turns are too many to model; use a wider "
                     f"strip or a bigger centre circle")
dt = 2.0 * math.pi / N
t_end = (R - w) / b
M = int(round((t_end - rb / b) / dt))          # panels along the strip
t0 = t_end - M * dt
ts = [t0 + k * dt for k in range(M + 1)]
amp = SCALLOP_DEPTH * w if edge == "scalloped" else 0.0


def scallop(t):
    return amp * abs(math.sin(SCALLOPS * (t - t0) / 2.0))


def X(t, ell):
    """Point at distance ell along the tangent line touching the base circle at angle t."""
    return (b * math.cos(t) + ell * math.sin(t), b * math.sin(t) - ell * math.cos(t))


# the strip at station t spans ell ∈ [b·t + a + KERF/2, b·t + w + a − KERF/2] on its tangent line;
# the outer-edge curve, followed past t0 for one more turn, is the centre circle's boundary
lo_edge = [X(t, b * t + scallop(t) + KERF / 2.0) for t in ts]                    # k = 0..M
hi_ts = [t0 + k * dt for k in range(M, -N - 1, -1)]                             # t_end → t0 − 2π
hi_edge = [X(t, b * t + w + scallop(t) - KERF / 2.0) for t in hi_ts]
# ── turn the piece so the strip's outer end is its leftmost point, then make coords positive ──
ex, ey = hi_edge[0]
rot = math.pi - math.atan2(ey, ex)
cr, sr = math.cos(rot), math.sin(rot)
pts_all = [(cr * x - sr * y, sr * x + cr * y) for x, y in lo_edge + hi_edge]
ox, oy = -min(p[0] for p in pts_all) + 2.0, -min(p[1] for p in pts_all) + 2.0


def S(p):
    return (cr * p[0] - sr * p[1] + ox, sr * p[0] + cr * p[1] + oy)


ring = [S(p) for p in hi_edge] + [S(p) for p in lo_edge]
fl = [(S(lo_edge[k]), S(hi_edge[M - k])) for k in range(M + 1)]
area = sum(ring[i][0] * ring[(i + 1) % len(ring)][1] - ring[(i + 1) % len(ring)][0] * ring[i][1]
           for i in range(len(ring)))
if area < 0:
    ring.reverse()
FRONT = colour
BACK = "#" + "".join(f"{int(int(colour[i:i + 2], 16) * 0.72):02x}" for i in (1, 3, 5))
disc = pliego.Sheet(
    "disc", ring, stock=stock, grain_deg=0.0,
    label=L4("Spiral disc", "Disco en espiral", "Disque en spirale", "Disco em espiral"),
    front=FRONT, back=BACK)
for k in range(M):
    disc.bend(fl[k][0], fl[k][1], name="base-hinge" if k == 0 else None)
cut_check = pliego.papercut.analyze(disc, min_feature_mm=MIN_FEATURE[stock], cutter_min_mm=0.5)
if not cut_check.ok:
    raise ValueError(f"paper-rose: the spiral fails the papercut check: {cut_check.issues}")
arr = disc.build()

# ── fold angles from the cone model ──
t_cal = CALIPER[stock]
ell = [b * t + w / 2.0 + scallop(t) for t in ts]                     # development distance
s_at = [0.0] * (M + 1)                                               # arclength from outer end
for k in range(M - 1, -1, -1):
    s_at[k] = s_at[k + 1] + 0.5 * (ell[k] + ell[k + 1]) * dt
L = s_at[0]
core_chord = ell[M] * dt
rho0 = max(4.0, 0.9 * core_chord)
g_bud = max(t_cal, 1.5 * core_chord * core_chord / (8.0 * rho0))
# loosened: the turns next to the centre circle settle flat (ρ reaches (1 + SOFT)·ℓ at the hinge),
# and never tighter than 1.5 × the bud's spacing (then more inner turns lie flat round the circle)
g_rose = max(math.pi * (((1.0 + SOFT) * ell[0]) ** 2 - rho0 ** 2) / L, 1.5 * g_bud)


def vsub(p, q):
    return (p[0] - q[0], p[1] - q[1], p[2] - q[2])


def vdot(p, q):
    return p[0] * q[0] + p[1] * q[1] + p[2] * q[2]


def vcross(p, q):
    return (p[1] * q[2] - p[2] * q[1], p[2] * q[0] - p[0] * q[2], p[0] * q[1] - p[1] * q[0])


def vunit(p):
    n = math.sqrt(vdot(p, p))
    return (p[0] / n, p[1] / n, p[2] / n)


def vrot(v, u, ang):
    """Rodrigues: v rotated by ang (rad) about the unit axis u."""
    c, s_ = math.cos(ang), math.sin(ang)
    k = vcross(u, v)
    d = vdot(u, v) * (1.0 - c)
    return tuple(v[i] * c + k[i] * s_ + u[i] * d for i in range(3))


def facet_fold(sin_a):
    """Fold angle (deg) between two facets of apex angle dt of a pyramid of half-angle α."""
    sin_a = min(sin_a, 1.0)
    cos_a = math.sqrt(max(0.0, 1.0 - sin_a * sin_a))
    if sin_a > 1.0 - 1e-12:
        return 0.0
    cdp = min(1.0, max(-1.0, (math.cos(dt) - cos_a * cos_a) / (sin_a * sin_a)))
    dpsi = math.acos(cdp)

    def g(psi):
        return (sin_a * math.cos(psi), sin_a * math.sin(psi), -cos_a)

    n1, n2 = vunit(vcross(g(-dpsi), g(0.0))), vunit(vcross(g(0.0), g(dpsi)))
    return math.degrees(math.acos(min(1.0, max(-1.0, vdot(n1, n2)))))


def soft_clamp(x):
    """min(x, 1) with a parabolic blend over 1 ± SOFT: 1 − result ∝ (x* − x)² near the clamp,
    so the coil's torsion stays finite where its turns settle flat."""
    if x <= 1.0 - SOFT:
        return x
    if x >= 1.0 + SOFT:
        return 1.0
    return x - (x - 1.0 + SOFT) ** 2 / (4.0 * SOFT)


def pose_angles(g):
    """Fold angles of the coil with spacing g (sin α = ρ/ℓ, softly clamped at flat)."""
    return [facet_fold(soft_clamp(math.sqrt(rho0 * rho0 + g * s_at[k] / math.pi) / ell[k]))
            for k in range(M)]


# which arrangement edge is F line k: match by midpoint
f_edges = {}
for e, (a, c) in enumerate(arr.edges):
    if arr.assignment[e] != "F":
        continue
    mx = 0.5 * (arr.vertices[a].x + arr.vertices[c].x)
    my = 0.5 * (arr.vertices[a].y + arr.vertices[c].y)
    k = min(range(M), key=lambda j: (0.5 * (fl[j][0][0] + fl[j][1][0]) - mx) ** 2
            + (0.5 * (fl[j][0][1] + fl[j][1][1]) - my) ** 2)
    f_edges[k] = e
if sorted(f_edges) != list(range(M)):
    raise ValueError(f"paper-rose: expected {M} F lines, found {len(f_edges)}")


def apply(T, p):
    cols, o = T
    return tuple(p[0] * cols[0][i] + p[1] * cols[1][i] + o[i] for i in range(3))


def fold_about(T_parent, a, b_, child_pt, deg):
    """The child's transform: the parent's, turned about the shared line a→b by `deg` (valley =
    toward the parent's front normal)."""
    A, B_ = apply(T_parent, a), apply(T_parent, b_)
    u = vunit(vsub(B_, A))
    if vdot(vcross(u, vsub(apply(T_parent, child_pt), A)), T_parent[0][2]) < 0.0:
        u = (-u[0], -u[1], -u[2])
    ang = math.radians(deg)
    cols = [vrot(c, u, ang) for c in T_parent[0]]
    o = vsub(T_parent[1], A)
    o = vrot(o, u, ang)
    return (cols, (o[0] + A[0], o[1] + A[1], o[2] + A[2]))


def mid2(k):
    return (0.5 * (fl[k][0][0] + fl[k][1][0]), 0.5 * (fl[k][0][1] + fl[k][1][1]))


CTR = S((0.0, 0.0))                                   # the centre circle's centre
IDENT = (((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)), (0.0, 0.0, 0.0))


def chain(angles_k):
    """Panel transforms from the core panel (M − 1, fixed) to panel 0; centreline points; the
    coil's mean binormal (its axis direction)."""
    T = {M - 1: IDENT}
    for k in range(M - 2, -1, -1):
        cpt = ((mid2(k)[0] + mid2(k + 1)[0]) / 2.0, (mid2(k)[1] + mid2(k + 1)[1]) / 2.0)
        T[k] = fold_about(T[k + 1], fl[k + 1][0], fl[k + 1][1], cpt, angles_k[k + 1])
    mids = [apply(T[min(k, M - 1)], mid2(k)) for k in range(M)]
    binorm = (0.0, 0.0, 0.0)
    for k in range(1, M - 1):
        c_ = vcross(vsub(mids[k], mids[k - 1]), vsub(mids[k + 1], mids[k]))
        binorm = (binorm[0] + c_[0], binorm[1] + c_[1], binorm[2] + c_[2])
    return T, mids, vunit(binorm)


def disc_pose(T, deg):
    return fold_about(T[0], fl[0][0], fl[0][1], CTR, deg)


def best_hinge(T, axis):
    """The hinge angle that turns the centre circle's front to face the coil along its axis."""
    best = max((vdot(disc_pose(T, d)[0][2], axis), d) for d in range(-179, 181))
    lo, hi = best[1] - 1.0, best[1] + 1.0
    for _ in range(40):
        m1, m2 = lo + (hi - lo) / 3.0, hi - (hi - lo) / 3.0
        if vdot(disc_pose(T, m1)[0][2], axis) < vdot(disc_pose(T, m2)[0][2], axis):
            lo = m1
        else:
            hi = m2
    return 0.5 * (lo + hi)


poses = {}
for name, g in (("bud", g_bud), ("rose", g_rose)):
    ang = pose_angles(g)
    T, mids, axis0 = chain(ang)
    cbar = tuple(sum(m[i] for m in mids) / M for i in range(3))
    options = []
    for sgn in (1.0, -1.0):                       # the coil must stand on the circle's front
        axis = (sgn * axis0[0], sgn * axis0[1], sgn * axis0[2])
        hinge = best_hinge(T, axis)
        Td = disc_pose(T, hinge)
        off = vsub(cbar, apply(Td, CTR))
        if vdot(off, Td[0][2]) > 0.0:
            options.append((vdot(Td[0][2], axis), hinge, axis, Td, off))
    if not options:
        raise ValueError(f"paper-rose: no hinge angle puts the {name} on the centre circle")
    _, ang[0], axis, Td, off = max(options, key=lambda o: o[0])
    tilt = math.degrees(math.acos(min(1.0, vdot(Td[0][2], axis))))
    along = vdot(off, axis)
    radial = math.sqrt(max(0.0, vdot(off, off) - along * along))
    poses[name] = {"angles": ang, "tilt_deg": round(tilt, 1), "base_offset_mm": round(radial, 1),
                   "base_below_mm": round(along, 1)}
bud, rose = poses["bud"]["angles"], poses["rose"]["angles"]
# angle [0] is the centre circle's hinge: either sign
if min(bud[1:]) < 0.0 or min(rose[1:]) < 0.0 or max(bud) <= 0.0:
    raise ValueError("paper-rose: the coil is not a valley roll")
if poses["rose"]["base_below_mm"] <= 0.0 or poses["rose"]["tilt_deg"] > 15.0:
    raise ValueError(f"paper-rose: the centre circle does not end up under the rose: {poses}")
bud_a = {f_edges[k]: bud[k] for k in range(M)}
rose_a = {f_edges[k]: rose[k] for k in range(M)}

# ── the program: roll from the outer end (k = M−1 down to 0), then loosen onto the base ──
order = list(range(M - 1, -1, -1))
cuts = [N, int(M * 0.45), int(M * 0.8), M]
chunks, start = [], 0
for c in cuts:
    c = min(max(c, start + 1), M)
    if c > start:
        chunks.append(order[start:c])
        start = c
LABELS = [
    L4("Roll the outer end into a tight core", "Enrolla la punta exterior en un centro apretado",
       "Roulez le bout extérieur en un cœur serré", "Enrole a ponta externa num miolo apertado"),
    L4("Keep rolling along the spiral, the inner edge down",
       "Sigue enrollando a lo largo de la espiral, con el borde interior hacia abajo",
       "Continuez à rouler le long de la spirale, bord intérieur en bas",
       "Continue enrolando ao longo da espiral, com a borda interna para baixo"),
    L4("Roll on: the turns begin to flare", "Sigue enrollando: las vueltas empiezan a abrirse",
       "Roulez encore : les tours commencent à s'évaser",
       "Continue enrolando: as voltas começam a se abrir"),
    L4("Roll up to the centre circle: a tight bud", "Enrolla hasta el círculo del centro: un "
       "capullo apretado", "Roulez jusqu'au cercle central : un bouton serré",
       "Enrole até o círculo do centro: um botão apertado"),
]
LABELS = LABELS[:len(chunks) - 1] + [LABELS[-1]]
steps = []
for i, (lab, ch) in enumerate(zip(LABELS, chunks)):
    steps.append(pliego.Step(["core", "roll", "roll-on", "bud"][i if i < len(chunks) - 1 else 3],
                             lab, [(pliego.assembly.EdgeRef(disc, f_edges[k]), bud[k])
                                   for k in ch], duration_ms=2000))
steps.append(pliego.Step(
    "loosen", L4("Let it loosen and glue it down onto the centre circle: a rose",
                 "Déjalo aflojarse y pégalo sobre el círculo del centro: una rosa",
                 "Laissez-le se desserrer et collez-le sur le cercle central : une rose",
                 "Deixe-o afrouxar e cole-o sobre o círculo do centro: uma rosa"),
    [(pliego.assembly.EdgeRef(disc, e), a) for e, a in rose_a.items()], duration_ms=2500,
    note=L4("Pinch and curl the petal edges outward if you like.",
            "Si quieres, pellizca y riza hacia fuera los bordes de los pétalos.",
            "Si vous voulez, pincez et recourbez les bords des pétales vers l'extérieur.",
            "Se quiser, belisque e curve as bordas das pétalas para fora.")))

params = {"edge": edge, "diameter": diameter, "width": w, "base": base, "panels": N,
          "stock": stock, "colour": colour}
assembly = pliego.Assembly(
    [disc], controls=[pliego.sequence_control(label=L4("Roll the rose", "Enrollar la rosa",
                                                       "Rouler la rose", "Enrolar a rosa"))],
    sequence=pliego.Sequence(steps, mode="kinematic"),
    targets={"bud": {"angles": bud_a}, "rose": {"angles": rose_a}}, title="Rolled paper rose")
doc = assembly.build(cartridge=SLUG, mode=mode, params=params)

info = {"turns": round(M / N, 2), "panels": M, "per_turn": N, "strip_mm": round(L, 1),
        "core_mm": round(2 * rho0, 1),
        "bud_spacing_mm": round(g_bud, 3), "rose_spacing_mm": round(g_rose, 3),
        "rose": {k: v for k, v in poses["rose"].items() if k != "angles"},
        "bud": {k: v for k, v in poses["bud"].items() if k != "angles"},
        "min_bridge_mm": cut_check.min_bridge_mm}
print(f"paper-rose: {info}")
result = doc.stamp()
