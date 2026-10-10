"""Kaleidocycle — sheet-hyperobjects cartridge (Pliego).

A ring of `links` (6, 8 or 10) congruent tetrahedra, each joined to the next along an edge, that
turns through its own centre without end. Each tetrahedron has two opposite edges as hinges, AB to
the previous link and CD to the next: perpendicular, of length `hinge`, `height` apart. Its four
faces are isosceles triangles (base `hinge`, legs √(hinge²/2 + height²)).

The net is one band of `links` rows. A row is a strip of four triangles that folds into one
tetrahedron (its seam BC closes with a glue tab), and the rows meet along the hinges: alternately
along both edges of the hinge (shift left) and along one (shift right), so the attachments
alternate A→D and A→C around the ring. The last row closes the ring with a glue tab on the first.

The motion. Each hinge i is a revolute joint; with the alternating attachments the ring closes
(the product of the N link transforms is the identity) on a one-parameter loop of hinge angles
(a, b) alternating around the ring, a = r(θ)·cos θ, b = r(θ)·sin θ, which this script solves by
Newton on r for each θ; one turn of θ is one full cycle of the ring (every hinge swings between
±720°/N). The 0.2 motion solver closes vertex loops but not loops through glue seams, so the ring
closure is solved here; `Sequence.kinematic_path` then expands the key states into rigid substeps
on the net's own vertex loops (the interior vertices where two rows meet along both hinge edges),
and every state is checked: the vertex loops close, and each glue seam stays shut within a fraction
of a millimetre. A hinge angle beyond 180° minus the tetrahedron's dihedral at the hinge would
push neighbours into each other, and non-neighbours are checked point by point; the script refuses
a slim-ness that collides. The colour patterns are original (no M. C. Escher art).
"""

import math

import pliego
from pliego import kinematics


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


mode = PARAM(lambda: mode, "turn")                       # noqa: F821
links = int(round(float(PARAM(lambda: links, 6))))      # noqa: F821
hinge = float(PARAM(lambda: hinge, 40.0))                # noqa: F821
height = float(PARAM(lambda: height, 40.0))              # noqa: F821
palette = PARAM(lambda: palette, "bright")               # noqa: F821
stock = PARAM(lambda: stock, "cardstock-160")            # noqa: F821

if mode not in ("make", "turn"):
    raise ValueError(f"kaleidocycle: unknown mode {mode!r}")
if links not in (6, 8, 10):
    raise ValueError(f"kaleidocycle: links must be 6, 8 or 10, got {links}")
if stock not in ("cardstock-160", "copy-80", "kraft-120"):
    raise ValueError(f"kaleidocycle: unknown stock {stock!r}")
N = links
L = pliego.clamp(hinge, 20.0, 80.0)
Hh = pliego.clamp(height, 0.3 * L, 2.0 * L)
LEG = math.sqrt(L * L / 2 + Hh * Hh)
HT = math.sqrt(LEG * LEG - L * L / 4)          # height of a net triangle
KEYS = 72                                      # key states per turn (5° of the loop)
SEAM_TOL = 0.5                                 # mm: a glue seam may open this much mid-step
SUBS = 1                                       # the key states are exact; no chord substeps


def L4(en, es, fr, pt):
    return {"en": en, "es": es, "fr": fr, "pt": pt}


# ── the swing limit: neighbours must not pass into each other ─────────────────
DIHEDRAL = math.degrees(2 * math.atan(L / (2 * Hh)))       # the tetrahedron's angle at a hinge
SWING = 720.0 / N                                          # the loop's largest hinge angle
if SWING > 180.0 - DIHEDRAL - 2.0:
    raise ValueError(f"kaleidocycle: with {N} links each hinge swings to {SWING:.0f}°, but "
                     f"links {L:g} × {Hh:g} mm allow {180 - DIHEDRAL:.1f}°; raise the height")

# ── rigid transforms (4 × 4, row-major) and the ring's closure loop ──────────


def mat(r, t=(0.0, 0.0, 0.0)):
    return [list(r[0]) + [t[0]], list(r[1]) + [t[1]], list(r[2]) + [t[2]], [0.0, 0.0, 0.0, 1.0]]


def mmul(A, B):
    return [[sum(A[i][k] * B[k][j] for k in range(4)) for j in range(4)] for i in range(4)]


def apply(M, p):
    return tuple(M[i][0] * p[0] + M[i][1] * p[1] + M[i][2] * p[2] + M[i][3] for i in range(3))


def link(phi, sg):
    """Next tetrahedron's frame: up h/2, turn sg·90° about z (A lands on D or C), swing phi about
    the hinge line (the y-axis), up h/2."""
    c, s = math.cos(phi), math.sin(phi)
    up = mat(((1, 0, 0), (0, 1, 0), (0, 0, 1)), (0.0, 0.0, Hh / 2))
    return mmul(mmul(mmul(up, mat(((c, 0, s), (0, 1, 0), (-s, 0, c)))),
                     mat(((0, -sg, 0), (sg, 0, 0), (0, 0, 1)))), up)


def frames(a, b):
    out = [mat(((1, 0, 0), (0, 1, 0), (0, 0, 1)))]
    for k in range(N):
        out.append(mmul(out[-1], link(a if k % 2 == 0 else b, -1 if k % 2 == 0 else 1)))
    return out


def gap(a, b):
    M = frames(a, b)[-1]
    return [M[i][j] - (1.0 if i == j else 0.0) for i in range(3) for j in range(4)]


def loop_radius(theta, r):
    """Newton on r: the ring closes at hinge angles (r cos θ, r sin θ)."""
    for _ in range(60):
        f = gap(r * math.cos(theta), r * math.sin(theta))
        g = gap((r + 1e-7) * math.cos(theta), (r + 1e-7) * math.sin(theta))
        J = [(x - y) / 1e-7 for x, y in zip(g, f)]
        dr = sum(x * y for x, y in zip(J, f)) / sum(x * x for x in J)
        r -= dr
        if abs(dr) < 1e-14:
            break
    if max(abs(x) for x in gap(r * math.cos(theta), r * math.sin(theta))) > 1e-9:
        raise ValueError(f"kaleidocycle: the ring does not close at θ = {math.degrees(theta)}°")
    return r


STATES, r = [], math.radians(SWING)
for j in range(KEYS + 1):
    th = 2 * math.pi * j / KEYS
    r = loop_radius(th, r)
    STATES.append((r * math.cos(th), r * math.sin(th)))

# ── the tetrahedron and the net ───────────────────────────────────────────────
TET = {"A": (-L / 2, 0.0, -Hh / 2), "B": (L / 2, 0.0, -Hh / 2),
       "C": (0.0, -L / 2, Hh / 2), "D": (0.0, L / 2, Hh / 2)}
ROW = {"Bp": (-L, 0.0), "A": (0.0, 0.0), "B": (L, 0.0),
       "Cp": (-1.5 * L, HT), "D": (-0.5 * L, HT), "C": (0.5 * L, HT)}
TRIS = [("A", "B", "C"), ("A", "C", "D"), ("Bp", "A", "D"), ("Bp", "D", "Cp")]
xoff = [0.0]
for k in range(N - 1):
    xoff.append(xoff[-1] + (-L / 2 if k % 2 == 0 else L / 2))


def npt(k, name):
    x, y = ROW[name]
    return (round(x + xoff[k] + 1.5 * L + 1.0, 6), round(y + k * HT, 6))


FACES = []            # (row, triangle index, sheet points, tetrahedron labels)
for k in range(N):
    for t, tri in enumerate(TRIS):
        FACES.append((k, t, [npt(k, n) for n in tri], [n.rstrip("p") for n in tri]))


# glue tabs: (row, triangle with the tab, edge names, target triangle, target edge names)
TABS = [(k, 0, ("B", "C"), (k, 3), ("Bp", "Cp")) if k % 2 == 0 else
        (k, 3, ("Cp", "Bp"), (k, 0), ("C", "B")) for k in range(N)]
TABS.append((N - 1, 1, ("D", "C"), (0, 2), ("Bp", "A")))

# ── the net's outline: triangle edges used once ─────────────────────────────────
fidx = {}
for f, (k, t, pts, _) in enumerate(FACES):
    for i in range(3):
        fidx.setdefault(frozenset((pts[i], pts[(i + 1) % 3])), []).append(f)
outline_next = {pts[i]: pts[(i + 1) % 3] for k, t, pts, _ in FACES for i in range(3)
                if len(fidx[frozenset((pts[i], pts[(i + 1) % 3]))]) == 1}
ring_pts = [min(outline_next)]
while outline_next[ring_pts[-1]] != ring_pts[0]:
    ring_pts.append(outline_next[ring_pts[-1]])
if len(ring_pts) != len(outline_next):
    raise ValueError("kaleidocycle: the net's outline is not one loop")

# ── 3-D: the ring's frame, faces, tabs and crease angles ────────────────────────


def sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def unit(a):
    n = math.sqrt(dot(a, a))
    return (a[0] / n, a[1] / n, a[2] / n)


M0 = frames(*STATES[0])
mids = [apply(M0[k], (0.0, 0.0, -Hh / 2)) for k in range(N)]
cen = tuple(sum(m[i] for m in mids) / N for i in range(3))
ey = unit(tuple(sum(cross(sub(mids[k], cen), sub(mids[(k + 1) % N], cen))[i] for k in range(N))
                for i in range(3)))
ex = sub(mids[0], cen)
ex = unit(sub(ex, tuple(dot(ex, ey) * c for c in ey)))
ez = cross(ex, ey)
G = mat((ex, ey, ez), tuple(-dot(e, cen) for e in (ex, ey, ez)))
lift = -min(apply(mmul(G, M), TET[n])[1] for M in M0[:N] for n in "ABCD")
G[1][3] += lift


def affine3(src, dst):
    """Sheet point → world point for the triangle src (sheet) ↦ dst (world)."""
    (x0, y0), (x1, y1), (x2, y2) = src
    det = (x1 - x0) * (y2 - y0) - (x2 - x0) * (y1 - y0)

    def f(p):
        a = ((p[0] - x0) * (y2 - y0) - (x2 - x0) * (p[1] - y0)) / det
        b = ((x1 - x0) * (p[1] - y0) - (p[0] - x0) * (y1 - y0)) / det
        return tuple(dst[0][i] + a * (dst[1][i] - dst[0][i]) + b * (dst[2][i] - dst[0][i])
                     for i in range(3))
    return f


def world(state):
    Ms = [mmul(G, M) for M in frames(*state)]
    return [[apply(Ms[k], TET[n]) for n in lab] for k, _, _, lab in FACES]


def fold(P, Q, a, b):
    """Signed fold (deg, valley > 0) between faces P and Q (world points, sheet-CCW order) at
    the edge a→b of P's CCW order."""
    nP = unit(cross(sub(P[1], P[0]), sub(P[2], P[0])))
    nQ = unit(cross(sub(Q[1], Q[0]), sub(Q[2], Q[0])))
    return math.degrees(math.atan2(dot(cross(nP, nQ), unit(sub(a, b))), dot(nP, nQ)))


W0 = world(STATES[0])
for (k, t, pts, lab), P in zip(FACES, W0):
    c = apply(mmul(G, M0[k]), (0.0, 0.0, 0.0))
    if dot(cross(sub(P[1], P[0]), sub(P[2], P[0])), sub(P[0], c)) <= 0:
        raise ValueError("kaleidocycle: a face of the net folds with its print inside")
CREASES = []              # (face f, face g, i: f's CCW edge index)
for e, fs in fidx.items():
    if len(fs) == 2:
        f, g = fs
        pts = FACES[f][2]
        i = [j for j in range(3) if frozenset((pts[j], pts[(j + 1) % 3])) == e][0]
        CREASES.append((f, g, i))


def crease_angles(W):
    out = []
    for f, g, i in CREASES:
        out.append(fold(W[f], W[g], W[f][i], W[f][(i + 1) % 3]))
    return out


def rigid2(p, q, p2, q2, flip):
    """2-D rigid map sending p→p2, q→q2 (a reflection when flip)."""
    a1 = math.atan2(q[1] - p[1], q[0] - p[0])
    a2 = math.atan2(q2[1] - p2[1], q2[0] - p2[0])

    def f(x):
        dx, dy = x[0] - p[0], x[1] - p[1]
        if flip:
            ca, sa = math.cos(2 * a1), math.sin(2 * a1)
            dx, dy = ca * dx + sa * dy, sa * dx - ca * dy
        c, s = math.cos(a2 - a1), math.sin(a2 - a1)
        return (p2[0] + c * dx - s * dy, p2[1] + s * dx + c * dy)
    return f


def inside(pt, tri, slack=1e-6):
    return all((tri[(i + 1) % 3][0] - tri[i][0]) * (pt[1] - tri[i][1])
               - (tri[(i + 1) % 3][1] - tri[i][1]) * (pt[0] - tri[i][0]) >= -slack
               for i in range(3))


def reflect(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    t = ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / (dx * dx + dy * dy)
    return (2 * (a[0] + t * dx) - p[0], 2 * (a[1] + t * dy) - p[1])


TABDEF = []               # (face with the tab fx, glue face fy, hinge (p, q), map, probe triangle)
for (k, t, (p, q), (k2, t2), (p2, q2)) in TABS:
    fx = [n for n, F in enumerate(FACES) if F[0] == k and F[1] == t][0]
    fy = [n for n, F in enumerate(FACES) if F[0] == k2 and F[1] == t2][0]
    a, b, c = npt(k, p), npt(k, q), npt(k2, p2)
    other = [v for v in FACES[fx][2] if v not in (a, b)][0]
    probe = [a, b, reflect(other, a, b)]
    if (b[0] - a[0]) * (probe[2][1] - a[1]) - (b[1] - a[1]) * (probe[2][0] - a[0]) < 0:
        probe = [b, a, probe[2]]
    cen2 = tuple(sum(v[i] for v in probe) / 3 for i in (0, 1))
    maps = [m for m in (rigid2(a, b, c, npt(k2, q2), fl) for fl in (False, True))
            if inside(m(cen2), FACES[fy][2])]
    if len(maps) != 1:
        raise ValueError("kaleidocycle: a glue tab has no unique place on its glue face")
    TABDEF.append((fx, fy, (a, b), maps[0], probe))


def tab_angles(W):
    out = []
    for fx, fy, (a, b), m, probe in TABDEF:
        to_w = affine3(FACES[fy][2], W[fy])
        pts = FACES[fx][2]
        i = [j for j in range(3) if {pts[j], pts[(j + 1) % 3]} == {a, b}][0]
        T = [to_w(m(v)) for v in probe]
        out.append(fold(W[fx], T, W[fx][i], W[fx][(i + 1) % 3]))
    return out


# ── the swing check for non-neighbours (points of one link inside another) ───────
for st in STATES:
    W = world(st)
    tets = [[W[4 * k][0], W[4 * k][1], W[4 * k][2], W[4 * k + 1][2]] for k in range(N)]
    for i in range(N):
        A0, A1, A2, A3 = tets[i]
        vol = dot(sub(A1, A0), cross(sub(A2, A0), sub(A3, A0)))
        for j in range(N):
            if (i - j) % N in (0, 1, N - 1):
                continue
            pts = tets[j] + [tuple((x[c] + y[c]) / 2 for c in range(3))
                             for x in tets[j] for y in tets[j] if x < y]
            for q in pts:
                lam = [dot(sub(A1, q), cross(sub(A2, q), sub(A3, q))) / vol,
                       dot(sub(q, A0), cross(sub(A2, A0), sub(A3, A0))) / vol,
                       dot(sub(A1, A0), cross(sub(q, A0), sub(A3, A0))) / vol,
                       dot(sub(A1, A0), cross(sub(A2, A0), sub(q, A0))) / vol]
                if min(lam) > 0.02:
                    raise ValueError(f"kaleidocycle: links {i + 1} and {j + 1} collide while "
                                     "turning; raise the height")

for st in STATES:                      # the folded net is one piece: shared edges meet
    W = world(st)
    for f, g, i in CREASES:
        a, b = FACES[f][2][i], FACES[f][2][(i + 1) % 3]
        for v in (a, b):
            if max(abs(x - y) for x, y in zip(W[f][FACES[f][2].index(v)],
                                               W[g][FACES[g][2].index(v)])) > 1e-6:
                raise ValueError("kaleidocycle: the net does not fold onto the ring")

# ── the sheet: creases, tabs, glue seams, printed patterns ─────────────────────
A0, T0 = crease_angles(W0), tab_angles(W0)
PALETTES = {"bright": ["#e4572e", "#f3a712", "#2e86ab", "#4c9f70"],
            "earth": ["#b5651d", "#d9b44a", "#5b7c99", "#6b8f71"]}
if palette not in PALETTES:
    raise ValueError(f"kaleidocycle: unknown palette {palette!r}")


def f2(x):
    return f"{x:.2f}"


def art(tab_regions):
    """Original patterns: each of the four faces of a link in its own colour and motif."""
    xs = [p[0] for p in ring_pts] + [v[0] for r in tab_regions for v in r]
    ys = [p[1] for p in ring_pts] + [v[1] for r in tab_regions for v in r]
    u0, v1 = min(xs), max(ys)

    def img(p):
        return (p[0] - u0, v1 - p[1])
    out = [f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {f2(max(xs) - u0)} "
           f"{f2(v1 - min(ys))}'>"]
    for n, (k, t, pts, _) in enumerate(FACES):
        q = [img(p) for p in pts]
        cx, cy = sum(p[0] for p in q) / 3, sum(p[1] for p in q) / 3
        poly = " ".join(f"{f2(x)},{f2(y)}" for x, y in q)
        out.append(f"<clipPath id='c{n}'><polygon points='{poly}'/></clipPath><g clip-path="
                   f"'url(#c{n})'><polygon points='{poly}' fill='{PALETTES[palette][t]}'/>")
        ink = "stroke='#fdfaf3' fill='none' stroke-width='" + f2(L / 40) + "'"
        if t == 0:      # nested triangles
            out += [f"<polygon points='" + " ".join(f"{f2(cx + (x - cx) * s / 5)},"
                                                    f"{f2(cy + (y - cy) * s / 5)}" for x, y in q)
                    + f"' {ink}/>" for s in range(1, 5)]
        elif t == 1:    # stripes along the hinge
            out += [f"<line x1='{f2(q[1][0] - L)}' y1='{f2(q[1][1] + j * L / 8)}' "
                    f"x2='{f2(q[1][0] + 2 * L)}' y2='{f2(q[1][1] + j * L / 8)}' {ink}/>"
                    for j in range(-10, 11)]
        elif t == 2:    # dots
            out += [f"<circle cx='{f2(cx + (x - cx) * 0.45)}' cy='{f2(cy + (y - cy) * 0.45)}' "
                    f"r='{f2(L / 14)}' fill='#fdfaf3'/>" for x, y in q]
            out.append(f"<circle cx='{f2(cx)}' cy='{f2(cy)}' r='{f2(L / 9)}' fill='#fdfaf3'/>")
        else:           # rays from the centre
            out += [f"<line x1='{f2(cx)}' y1='{f2(cy)}' x2='{f2(cx + 2 * L * math.cos(j * math.pi / 6))}' "
                    f"y2='{f2(cy + 2 * L * math.sin(j * math.pi / 6))}' {ink}/>" for j in range(12)]
        out.append("</g>")
    for r in tab_regions:
        out.append("<polygon points='" + " ".join(f"{f2(x)},{f2(y)}" for x, y in map(img, r))
                   + "' fill='#d8d3c8'/>")
    svg = "".join(out) + "</svg>"
    for a, b in (("%", "%25"), ("#", "%23"), ("<", "%3C"), (">", "%3E"), (" ", "%20"),
                 ("'", "%27")):
        svg = svg.replace(a, b)
    return "data:image/svg+xml;charset=utf-8," + svg


sheet = pliego.Sheet("net", ring_pts, stock=stock, grain_deg=90.0,
                     label=L4("Ring of tetrahedra", "Anillo de tetraedros",
                              "Anneau de tétraèdres", "Anel de tetraedros"))
MARKS = [sheet.crease(FACES[f][2][i], FACES[f][2][(i + 1) % 3],
                      "valley" if a > 0 else "mountain", abs(a), name=f"hinge-{FACES[f][0] + 1}"
                      if FACES[f][0] != FACES[g][0] else None)
         for (f, g, i), a in zip(CREASES, A0)]
TAB_W = min(8.0, 0.2 * L)
tabs, joins = [], []
for n, ((fx, fy, (a, b), m, probe), ang) in enumerate(zip(TABDEF, T0)):
    tab = sheet.tab((a, b), width=TAB_W, taper=45.0, kind="valley" if ang > 0 else "mountain",
                    angle=abs(ang), treatment="score",
                    name="ring-tab" if n == N else f"seam-tab-{n + 1}")
    cx = sum(v.x for v in tab.region) / len(tab.region)
    cy = sum(v.y for v in tab.region) / len(tab.region)
    region = [(cx + (v.x - cx) * 0.8, cy + (v.y - cy) * 0.8) for v in tab.region]
    if not all(inside(m(p), FACES[fy][2]) for p in region):
        raise ValueError(f"kaleidocycle: glue tab {n + 1} overhangs its glue face")
    o, e1, e2 = m((0.0, 0.0)), m((1.0, 0.0)), m((0.0, 1.0))
    joins.append(pliego.glue(f"seam-{n + 1}", sheet, region, sheet,
                             (e1[0] - o[0], e2[0] - o[0], e1[1] - o[1], e2[1] - o[1], o[0], o[1]),
                             side="back"))
    tabs.append(tab)
sheet.front = pliego.Face(None, art([[(v.x, v.y) for v in t.region] for t in tabs]))
ALL = MARKS + [t.mark for t in tabs]


def targets(state):
    W = world(state)
    return list(zip(ALL, crease_angles(W) + tab_angles(W)))


TURN = L4("Turn the ring", "Girar el anillo", "Tourner l'anneau", "Girar o anel")
if mode == "make":
    key = [pliego.Step("assemble", L4(
        "Fold each row into a tetrahedron and close the ring; glue the tabs",
        "Dobla cada fila en un tetraedro y cierra el anillo; pega las pestañas",
        "Plier chaque rangée en tétraèdre et fermer l'anneau ; coller les languettes",
        "Dobre cada fileira num tetraedro e feche o anel; cole as abas"),
        targets(STATES[0]), duration_ms=6000)]
    seq = pliego.Sequence.kinematic_path(sheet, key, substeps=16)
    result = pliego.Assembly([sheet], controls=[pliego.sequence_control(
        label=L4("Fold", "Doblar", "Plier", "Dobrar"))], sequence=seq, title="Kaleidocycle")
else:
    key = [pliego.Step(f"turn-{j}", {lang: f"{txt} ({j}/{KEYS})" for lang, txt in TURN.items()},
                       targets(STATES[j]), duration_ms=500) for j in range(1, KEYS + 1)]
    seq = pliego.Sequence.kinematic_path(sheet, key, start=dict(targets(STATES[0])), substeps=SUBS)

    def initial(_sheet_id, uv):
        for f, (k, t, pts, _) in enumerate(FACES):
            if inside(uv, pts, 1e-3):
                return affine3(pts, W0[f])(uv)
        for (fx, fy, _, m, _), tab in zip(TABDEF, tabs):
            ring = [(v.x, v.y) for v in tab.region]
            if any(inside(uv, [ring[0], ring[i], ring[i + 1]], 1e-3) for i in (1, 2)):
                return affine3(FACES[fy][2], W0[fy])(m(uv))
        raise ValueError(f"kaleidocycle: point {uv} is on no face")
    result = pliego.Assembly([sheet], joins=joins, initial=initial, sequence=seq,
                             controls=[pliego.sequence_control(label=TURN)], title="Kaleidocycle")

# ── read-proof: the vertex loops close along the program and the seams stay shut ──
arr = sheet.build()
cur = {e: a for mk, a in targets(STATES[0]) for e in mk.edges()} if mode == "turn" else {}
worst_v = worst_seam = 0.0
for stp in seq.steps:
    for ref, a in stp.targets:
        cur[ref.edge] = a
    worst_v = max([worst_v] + list(kinematics.vertex_residuals(arr, cur).values()))
    if mode == "turn":
        P = kinematics.pose_arrangement(arr, cur)
        for (fx, fy, _, m, _), tab in zip(TABDEF, tabs):
            ys = FACES[fy][2]
            iy = [min(range(len(arr.vertices)), key=lambda v: (arr.vertices[v].x - p[0]) ** 2
                      + (arr.vertices[v].y - p[1]) ** 2) for p in ys]
            for v in tab.region[2:]:
                vi = min(range(len(arr.vertices)), key=lambda w: (arr.vertices[w].x - v.x) ** 2
                         + (arr.vertices[w].y - v.y) ** 2)
                want = affine3(ys, [P[i] for i in iy])(m((v.x, v.y)))
                worst_seam = max(worst_seam, math.dist(P[vi], want))
if worst_v > 1e-6 or worst_seam > SEAM_TOL:
    raise ValueError(f"kaleidocycle: the program leaves the ring (vertex {worst_v:.2g} rad, "
                     f"seam {worst_seam:.3g} mm)")
print(f"kaleidocycle: mode={mode} links={N} hinge={L:g}mm height={Hh:g}mm "
      f"dihedral={DIHEDRAL:.1f}deg swing={SWING:.0f}deg steps={len(seq.steps)} "
      f"vertex_residual_rad={worst_v:.2g} seam_gap_mm={worst_seam:.3f}")
