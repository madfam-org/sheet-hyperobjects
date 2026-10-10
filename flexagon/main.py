"""Flexagon — sheet-hyperobjects cartridge (Pliego).

One family, three styles, each a strip of cells whose last cell is glued onto the first:
`trihexa` (9 triangles + glue, faces 1-2-3), `hexahexa` (18 triangles + glue, coiled first, six
faces in a Tuckerman traverse of 12 flexes) and `tetra` (8 squares in a staircase + glue, faces
1-2-3-4). Mode `make` folds the flat strip into its flat state; mode `flex` is the glued flexagon
(a `glue` join and an exact initial frame) flexed through every face and back.

A flat state is a polygon of N sectors (6 triangles or 4 squares) around a centre C, each holding a
stack of cells (a pat). A flex is a rigid motion in two phases. Phase 1 folds the centre vertex:
every other radius (the spines) closes to 180° and the pats pair into fins — the pinch of the
hexaflexagons, the book fold of the tetraflexagon. It is solved with `pliego.kinematics.solve` on
the degree-N vertex and each solved state is matched to the symmetric closed form. Phase 2 opens
the far vertex T: each fin splits into two contiguous blocks of layers that unfold into a new flat
state around T. Which cells go where follows from the hinges (a fold on a spine radius never splits,
one on the far edge may) and the fin's layer order; every flat state passes local layer checks.
The strip's fold angles are the signed dihedrals of the posed cells, so the preview's face tree
reproduces every pose, and the glue cell stays on cell 1 throughout (checked at every step).

The faces are printed with original colours and patterns, each drawn in the frame of the flat state
where the face first shows, plus its number. History: A. H. Stone (1939), M. Gardner (1956); the
strips, layer orders and motions are computed here.
"""

import math

import pliego
from pliego import kinematics


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


mode = PARAM(lambda: mode, "flex")                     # noqa: F821
style = PARAM(lambda: style, "trihexa")                # noqa: F821
side = float(PARAM(lambda: side, 40.0))                # noqa: F821
palette = PARAM(lambda: palette, "bright")             # noqa: F821
stock = PARAM(lambda: stock, "copy-80")                # noqa: F821

if mode not in ("make", "flex"):
    raise ValueError(f"flexagon: unknown mode {mode!r}")
if stock not in ("copy-80", "kami", "cardstock-160"):
    raise ValueError(f"flexagon: unknown stock {stock!r}")
S = pliego.clamp(side, 20.0, 80.0)
EPS_DEG = 0.0005          # initial frame: flat folds stop this short of 180° (layer order)
TOL = 1e-6
H = math.sqrt(3.0) / 2.0


def L4(en, es, fr, pt):
    return {"en": en, "es": es, "fr": fr, "pt": pt}


# ── styles: cells, the folds of the flat state, its layer order (bottom → top per sector) ──

def tri_cell(i):
    x = i // 2
    if i % 2 == 0:
        return [(x * S, 0.0), ((x + 1) * S, 0.0), ((x + 0.5) * S, H * S)]
    return [((x + 1) * S, 0.0), ((x + 1.5) * S, H * S), ((x + 0.5) * S, H * S)]


def square_cells(dirs):
    step, at, out = [(1, 0), (0, 1), (-1, 0), (0, -1)], (0, 0), []
    for d in [None] + dirs:
        if d is not None:
            at = (at[0] + step[d][0], at[1] + step[d][1])
        x, y = at[0] * S, at[1] * S
        out.append([(x, y), (x + S, y), (x + S, y + S), (x, y + S)])
    return out


STYLES = {
    "trihexa": dict(N=6, cells=[tri_cell(i) for i in range(10)], folds=[2, 5, 8], faces=3,
                    stacks={0: [3, 2], 1: [1], 2: [9, 0, 8], 3: [7], 4: [6, 5], 5: [4]}),
    "hexahexa": dict(N=6, cells=[tri_cell(i) for i in range(19)], faces=6,
                     folds=[0, 2, 4, 6, 8, 10, 12, 14, 16, 5, 11, 17],
                     stacks={0: [11, 10, 13, 12], 1: [14, 15], 2: [17, 16, 1, 18, 0],
                             3: [2, 3], 4: [5, 4, 7, 6], 5: [8, 9]}),
    "tetra": dict(N=4, cells=square_cells([0, 0, 1, 1, 0, 0, 1, 1]), folds=[1, 3, 5, 7], faces=4,
                  stacks={0: [4, 3], 1: [5, 6], 2: [0, 8, 7], 3: [1, 2]}),
}
if style not in STYLES:
    raise ValueError(f"flexagon: unknown style {style!r}")
ST = STYLES[style]
N, CELLS = ST["N"], ST["cells"]
NC = len(CELLS)
GLUE = NC - 1
SUB = 4 if style == "hexahexa" else 6

# ── vectors (engine frame: sheet (u, v) ↦ (u, v, 0), front +z) ─────────────────

def add(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def mul(k, a):
    return (k * a[0], k * a[1], k * a[2])


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def unit(a):
    return mul(1.0 / math.sqrt(dot(a, a)), a)


def dist(a, b):
    return math.sqrt(dot(sub(a, b), sub(a, b)))


def normal(P):
    return unit(cross(sub(P[1], P[0]), sub(P[2], P[0])))


def affine(src, dst):
    """2-D affine map taking three src points to three dst points, as the SVG matrix
    (a, b, c, d, e, f): x' = a·x + c·y + e, y' = b·x + d·y + f."""
    (x0, y0), (x1, y1), (x2, y2) = src
    det = (x1 - x0) * (y2 - y0) - (x2 - x0) * (y1 - y0)
    rows = []
    for q0, q1, q2 in ((dst[0][0], dst[1][0], dst[2][0]), (dst[0][1], dst[1][1], dst[2][1])):
        a = ((q1 - q0) * (y2 - y0) - (q2 - q0) * (y1 - y0)) / det
        c = ((x1 - x0) * (q2 - q0) - (x2 - x0) * (q1 - q0)) / det
        rows.append((a, c, q0 - a * x0 - c * y0))
    return rows[0][0], rows[1][0], rows[0][1], rows[1][1], rows[0][2], rows[1][2]


# ── the strip: hinges (shared edges, in each cell's CCW order) and its face-tree pose ──

HINGE = []
for i in range(NC - 1):
    a, b = CELLS[i], CELLS[i + 1]
    ka = [k for k, p in enumerate(a) if any(math.dist(p, q) < TOL for q in b)]
    k0, k1 = (ka[0], ka[1]) if (ka[0] + 1) % len(a) == ka[1] else (ka[1], ka[0])
    kb = [[k for k, q in enumerate(b) if math.dist(q, a[j]) < TOL][0] for j in (k0, k1)]
    HINGE.append((k0, k1, kb[0], kb[1]))


def chain_pose(ang, clamp=180.0):
    """3-D cells from hinge angles (deg), cell 0 flat (the preview's face tree)."""
    rots, out = [], []
    for i in range(NC):
        if i:
            a, b = CELLS[i - 1][HINGE[i - 1][0]], CELLS[i - 1][HINGE[i - 1][1]]
            rots.append(((a[0], a[1], 0.0), unit((a[0] - b[0], a[1] - b[1], 0.0)),
                         math.radians(max(-clamp, min(clamp, ang[i - 1])))))
        pts = [(p[0], p[1], 0.0) for p in CELLS[i]]
        for o, d, t in reversed(rots):
            c, s = math.cos(t), math.sin(t)
            pts = [add(o, tuple(x[j] * c + cross(d, x)[j] * s + d[j] * dot(d, x) * (1 - c)
                                for j in range(3))) for x in (sub(q, o) for q in pts)]
        out.append(pts)
    return out


def hinge_angles(P, prev):
    """Signed dihedral of each hinge (valley > 0, the kernel's convention); a flat fold keeps the
    sign of the previous state."""
    out = []
    for i, (k0, k1, _, _) in enumerate(HINGE):
        na, nb = normal(P[i]), normal(P[i + 1])
        a = math.degrees(math.atan2(dot(cross(na, nb), unit(sub(P[i][k0], P[i][k1]))),
                                    dot(na, nb)))
        if abs(abs(a) - 180.0) < 1e-6:
            a = 180.0 if prev[i] >= 0 else -180.0
        out.append(0.0 if abs(a) < 1e-9 else a)
    return out


def check_rigid(P):
    for i, (k0, k1, j0, j1) in enumerate(HINGE):
        if dist(P[i][k0], P[i + 1][j0]) > TOL or dist(P[i][k1], P[i + 1][j1]) > TOL:
            raise ValueError(f"flexagon: hinge {i} tears")
    if sorted(tuple(round(c, 5) for c in p) for p in P[0]) != \
            sorted(tuple(round(c, 5) for c in p) for p in P[GLUE]):
        raise ValueError("flexagon: the glue cell leaves cell 1")


# ── flat states and the two phases of a flex ─────────────────────────────────

def rays(p, e, sg):
    """Radii of the centre vertex: the spines (parity p) and the others at elevation e, fins
    toward sg. For 60° sectors the spines follow at the elevation that keeps 60° between radii."""
    out = []
    for j in range(N):
        el = e
        if j % 2 == p:
            r = math.sqrt(math.cos(e) ** 2 + 4 * math.sin(e) ** 2)
            el = (math.atan2(2 * math.sin(e), math.cos(e)) - math.acos(min(1.0, 1.0 / r))
                  if N == 6 else 0.0)
        az, el = 2 * math.pi * j / N, sg * el
        out.append((math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el)))
    return out


def place(O, R, k, roles):
    a, b = R[k], R[(k + 1) % N]
    at = {"c": O, "l": add(O, mul(S, a)), "h": add(O, mul(S, b)), "f": add(O, mul(S, add(a, b)))}
    return [at[r] for r in roles]


def roles_at(P, O, R, k):
    ref = place(O, R, k, "clhf")
    out = [[r for r, x in zip("clhf", ref) if dist(q, x) < TOL] for q in P]
    return None if [] in out else [m[0] for m in out]


def layers_ok(secs, roles, stacks):
    """Local flat-fold layer checks: folds on one edge nest, nothing passes through a fold,
    strands crossing a radius keep their order, the glue cell lies on cell 1."""
    lvl = {c: (k, n) for k, o in stacks.items() for n, c in enumerate(o)}
    folded, flat, pairs = {}, {}, {}
    for i, (k0, k1, j0, j1) in enumerate(HINGE):
        ea = frozenset((roles[i][k0], roles[i][k1]))
        eb = frozenset((roles[i + 1][j0], roles[i + 1][j1]))
        (ka, la), (kb, lb) = lvl[i], lvl[i + 1]
        if ka == kb:
            folded.setdefault((ka, ea), []).append((min(la, lb), max(la, lb)))
            continue
        flat.setdefault((ka, ea), []).append(la)
        flat.setdefault((kb, eb), []).append(lb)
        key = (ka, ea, kb, eb) if ka < kb else (kb, eb, ka, ea)
        pairs.setdefault(key, []).append((la, lb) if ka < kb else (lb, la))
    for key, iv in folded.items():
        if any(p < r < q < s for p, q in iv for r, s in iv) or \
                any(p < m < q for m in flat.get(key, []) for p, q in iv):
            return False
    if any((x[0] < y[0]) != (x[1] < y[1]) for pl in pairs.values() for x in pl for y in pl):
        return False
    return any(abs(o.index(0) - o.index(GLUE)) == 1 for o in stacks.values() if 0 in o)


def State(O, secs, roles, stacks):
    return {"O": O, "secs": secs, "roles": roles, "stacks": stacks}


def cells_of(st, R):
    return [place(st["O"], R, st["secs"][i], st["roles"][i]) for i in range(NC)]


def key_of(st):
    """The state up to a turn of the whole polygon."""
    return min((tuple((s - r) % N for s in st["secs"]), tuple(map(tuple, st["roles"])),
                tuple(tuple(st["stacks"][(k + r) % N]) for k in range(N))) for r in range(N))


def flex(state, p, sg):
    """The flex at spine parity p, fins toward sg (±z): the new flat state, or None."""
    fins = []
    for sp in range(p, N, 2):
        j, a, b = (sp - 1) % N, state["stacks"][(sp - 1) % N], state["stacks"][sp]
        fins.append((j, sp, a + b[::-1] if sg > 0 else a[::-1] + b))
    O, T = state["O"], add(state["O"], (0.0, 0.0, S * sg))
    Pc = cells_of(state, rays(p, math.pi / 2, sg))
    kind = []
    for i, (k0, k1, _, _) in enumerate(HINGE):
        lab = {"C" if dist(q, O) < TOL else "T" if dist(q, T) < TOL else "o"
               for q in (Pc[i][k0], Pc[i][k1])}
        kind.append("axis" if lab >= {"C", "T"} else "c" if "C" in lab else
                    "t" if "T" in lab else "far")
    fin_of = {c: n for n, f in enumerate(fins) for c in f[2]}
    splits, found = [[]], []
    for f in fins:
        splits = [s + [m] for s in splits for m in range(1, len(f[2]))]
    for split in splits:
        h = {}
        for (j, j1, order), m in zip(fins, split):
            h.update({c: j for c in order[:m]} | {c: j1 for c in order[m:]})
        ok = h[0] == h[GLUE]
        for i, t in enumerate(kind):
            a, b, same = h[i], h[i + 1], fin_of[i] == fin_of[i + 1]
            if t == "t":
                ok = ok and same
            elif t in ("c", "far") or same:
                ok = ok and a == b
            else:
                ok = ok and (((b - a) % N == 1 and b % 2 == 1 - p)
                             or ((a - b) % N == 1 and a % 2 == 1 - p))
        if not ok:
            continue
        stacks = {}
        for (j, j1, order), m in zip(fins, split):
            pre, suf = order[:m], order[m:]
            stacks[j], stacks[j1] = (pre[::-1], suf) if sg > 0 else (pre, suf[::-1])
        secs = [h[i] for i in range(NC)]
        roles = [roles_at(Pc[i], T, rays(p, math.pi / 2, -sg), secs[i]) for i in range(NC)]
        if None not in roles and layers_ok(secs, roles, stacks):
            found.append(State(T, secs, roles, stacks))
    return found[0] if len(found) == 1 else None


# ── the motion solver: the pinch (or book fold) of the centre vertex ──────────────

A = 50.0                    # the vertex path is scale-free: solve it on a 50 mm vertex
aux = pliego.Sheet("vertex", pliego.regular_polygon(N, A, (A, A), start_deg=0.0)
                   if N == 6 else pliego.square(2 * A))
spokes = [aux.crease((A, A), (A + A * math.cos(2 * math.pi * k / N),
                              A + A * math.sin(2 * math.pi * k / N)),
                     "valley" if k % 2 == 0 else "mountain", 180.0 if k % 2 == 0 else 60.0)
          for k in range(N)]
vpath = kinematics.solve(aux, {}, {m: (180.0 if k % 2 == 0 else (-60.0 if N == 6 else 0.0))
                                   for k, m in enumerate(spokes)}, steps=SUB, along="chord")
E_PATH, worst = [], 0.0
for state_k in vpath:
    vals = [state_k[m.edges()[0]] for m in spokes]
    e = math.radians(sum(vals[0::2]) / (N // 2) / 2.0)      # the spines fold to 2e
    cf = kinematics.vertex_folds([(r[0], r[2], -r[1]) for r in rays(0, e, 1)])
    worst = max(worst, max(abs(a - b) for a, b in zip(cf, vals)))
    E_PATH.append(e)
if worst > 0.05 or abs(E_PATH[-1] - math.pi / 2) > 1e-6:
    raise ValueError(f"flexagon: the solved vertex path leaves the symmetric pinch ({worst}°)")
E_PATH[-1] = math.pi / 2

# ── the flat state the strip folds into, its fold signs, and the full traverse ──

folded = set(ST["folds"])
P0 = chain_pose([180.0 if i in folded else 0.0 for i in range(NC - 1)])
O0 = set.intersection(*[{(round(p[0], 6), round(p[1], 6)) for p in c} for c in P0])
if len(O0) != 1:
    raise ValueError("flexagon: the strip does not fold around one centre")
O0 = tuple(O0.pop()) + (0.0,)
flat = rays(0, 0.0, 1)
secs0 = [int((math.degrees(math.atan2(sum(p[1] for p in c) / len(c) - O0[1],
                                      sum(p[0] for p in c) / len(c) - O0[0])) % 360.0)
             // (360.0 / N)) for c in P0]
roles0 = [roles_at(P0[i], O0, flat, secs0[i]) for i in range(NC)]
stacks0 = {k: list(v) for k, v in ST["stacks"].items()}
if sorted(sum(stacks0.values(), [])) != list(range(NC)) or None in roles0 or \
        any(secs0[c] != k for k, o in stacks0.items() for c in o) or \
        not layers_ok(secs0, roles0, stacks0):
    raise ValueError("flexagon: the layer order of the flat state is invalid")
# a folded hinge is a valley when the next cell lies on this cell's front side
ANG0 = [(180.0 if (stacks0[secs0[i]].index(i + 1) > stacks0[secs0[i]].index(i))
         == (normal(P0[i])[2] > 0) else -180.0) if i in folded else 0.0 for i in range(NC - 1)]
check_rigid(chain_pose(ANG0))
faces, first = {}, {}       # (cell, side) → face number; face → (state, sign of view)


def record(st):
    """Number the faces in order of appearance; returns (top face, bottom face)."""
    P, shown = cells_of(st, flat), []
    for top in (True, False):
        grp = [(c, "F" if (normal(P[c])[2] > 0) == top else "B")
               for c in (st["stacks"][k][-1 if top else 0] for k in range(N))]
        got = {faces.get(x) for x in grp}
        if got == {None}:
            first[len(first) + 1] = (st, 1 if top else -1)
            faces.update({x: len(first) for x in grp})
        elif None in got or len(got) != 1:
            raise ValueError("flexagon: a face mixes cells of two faces")
        shown.append(faces[grp[0]])
    return tuple(shown)


state = State(O0, secs0, roles0, stacks0)
history, start, frames, ang, p = [record(state)], key_of(state), [], list(ANG0), 0
for n_flex in range(1, 17):
    nxt = None
    for pp in (p, 1 - p):           # flex at the same vertex until it will not, then turn
        nxt = flex(state, pp, 1)
        if nxt:
            p = pp
            break
    if nxt is None:
        raise ValueError(f"flexagon: stuck after {n_flex - 1} flexes")
    for kind_, st, es, sg in (("pinch", state, E_PATH, 1),
                              ("open", nxt, list(reversed(E_PATH))[1:] + [0.0], -1)):
        for e in es:
            P = cells_of(st, rays(p, e, sg))
            check_rigid(P)
            ang = hinge_angles(P, ang)
            frames.append((kind_, n_flex, ang))
    state = nxt
    history.append(record(state))
    if key_of(state) == start and len(first) == ST["faces"]:
        break
if key_of(state) != start or len(first) != ST["faces"]:
    raise ValueError(f"flexagon: the traverse shows {len(first)} faces and does not close")

# ── printed art: a colour and an original pattern per face ─────────────────────

PALETTES = {"bright": ["#e4572e", "#f3a712", "#2e86ab", "#4c9f70", "#a23b72", "#3d405b"],
            "earth": ["#b5651d", "#d9b44a", "#5b7c99", "#6b8f71", "#8e5572", "#4a4e69"]}
if palette not in PALETTES:
    raise ValueError(f"flexagon: unknown palette {palette!r}")
INK, DARK = "#fdfaf3", "#1d1d1f"


def f2(x):
    return f"{x:.2f}"


def motif(face):
    """The pattern of a face in face coordinates (centre 0, unit one cell side)."""
    r, k, w = 1.5 * S, (face - 1) % 6, f2(S / 20)
    if k == 0:      # concentric rings
        return "".join(f"<circle r='{f2(S * j / 5)}' fill='none' stroke='{INK}' "
                       f"stroke-width='{w}'/>" for j in range(1, 8))
    if k == 1:      # a sunburst of 12 rays
        return "".join(f"<polygon points='0,0 {f2(r)},{f2(-r * 0.13)} {f2(r)},{f2(r * 0.13)}' "
                       f"fill='{INK}' fill-opacity='0.55' transform='rotate({30 * j})'/>"
                       for j in range(12))
    if k == 2:      # dots on a triangular lattice
        d = S / 4.0
        return "".join(f"<circle cx='{f2((a + b / 2.0) * d)}' cy='{f2(b * d * H)}' "
                       f"r='{f2(d / 4)}' fill='{INK}'/>" for a in range(-7, 8)
                       for b in range(-7, 8) if (a + b / 2.0) ** 2 + (b * H) ** 2 < 36)
    if k == 3:      # nested polygons
        return "".join("<polygon points='" + " ".join(
            f"{f2(S * j / 5 * math.cos((2 * m + 1) * math.pi / N))},"
            f"{f2(S * j / 5 * math.sin((2 * m + 1) * math.pi / N))}" for m in range(N))
            + f"' fill='none' stroke='{INK}' stroke-width='{w}'/>" for j in range(1, 7))
    if k == 4:      # petals
        return "".join(f"<ellipse cx='{f2(0.55 * S)}' rx='{f2(0.5 * S)}' ry='{f2(0.12 * S)}' "
                       f"fill='{INK}' fill-opacity='0.5' transform='rotate({30 * j})'/>"
                       for j in range(12))
    return "".join(f"<line x1='{f2(j * S / 8)}' y1='{f2(-r)}' x2='{f2(j * S / 8)}' y2='{f2(r)}' "
                   f"stroke='{INK}' stroke-width='{f2(S / 40)}' transform='rotate(30)'/>"
                   for j in range(-12, 13))      # cross-hatch


U0, U1 = min(p[0] for c in CELLS for p in c), max(p[0] for c in CELLS for p in c)
V0, V1 = min(p[1] for c in CELLS for p in c), max(p[1] for c in CELLS for p in c)


def art(side_):
    """SVG of one side over the sheet's bounding box (the back as seen from the back)."""
    img_of = (lambda p: (p[0] - U0, V1 - p[1])) if side_ == "F" else \
        (lambda p: (U1 - p[0], V1 - p[1]))
    body = [f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {f2(U1 - U0)} "
            f"{f2(V1 - V0)}'><defs>"]
    imgs = [[img_of(p) for p in c] for c in CELLS]
    pts = [" ".join(f"{f2(x)},{f2(y)}" for x, y in img) for img in imgs]
    body += [f"<clipPath id='c{i}'><polygon points='{q}'/></clipPath>" for i, q in enumerate(pts)]
    body.append("</defs>")
    for i, img in enumerate(imgs):
        face = faces.get((i, side_))
        if face is None:        # a glued side: hatching where the glue goes
            body.append(f"<g clip-path='url(#c{i})'><polygon points='{pts[i]}' fill='#d8d3c8'/>"
                        + "".join(f"<line x1='{f2(img[0][0] + j * S / 6 - S)}' "
                                  f"y1='{f2(img[0][1] - S)}' x2='{f2(img[0][0] + j * S / 6 + S)}' "
                                  f"y2='{f2(img[0][1] + S)}' stroke='#9a9488' "
                                  f"stroke-width='{f2(S / 30)}'/>" for j in range(-12, 13))
                        + "</g>")
            continue
        st, view = first[face]
        fc = [(q[0] - st["O"][0], view * (q[1] - st["O"][1])) for q in cells_of(st, flat)[i]]
        m = affine(fc[:3], img[:3])
        if m[0] * m[3] - m[1] * m[2] > 0:
            raise ValueError("flexagon: a face would print mirrored")
        cx, cy = sum(q[0] for q in fc) / len(fc), sum(q[1] for q in fc) / len(fc)
        tx, ty = m[0] * cx + m[2] * cy + m[4], m[1] * cx + m[3] * cy + m[5]
        body.append(f"<g clip-path='url(#c{i})'><polygon points='{pts[i]}' fill='"
                    f"{PALETTES[palette][(face - 1) % 6]}'/><g transform='matrix("
                    + ",".join(f"{v:.5f}" for v in m) + f")'>{motif(face)}</g></g>"
                    f"<text transform='translate({f2(tx)},{f2(ty)}) rotate("
                    f"{f2(math.degrees(math.atan2(m[1], m[0])))})' font-family='sans-serif' "
                    f"font-weight='700' font-size='{f2(0.3 * S)}' text-anchor='middle' "
                    f"dominant-baseline='central' fill='{DARK}' stroke='{INK}' "
                    f"stroke-width='{f2(S / 60)}'>{face}</text>")
        if side_ == "F":        # the cell number, for the making
            body.append(f"<text x='{f2((2 * img[0][0] + tx) / 3)}' y='{f2((2 * img[0][1] + ty) / 3)}'"
                        f" font-family='sans-serif' font-size='{f2(0.11 * S)}' text-anchor="
                        f"'middle' dominant-baseline='central' fill='{DARK}'>{i + 1}</text>")
    svg = "".join(body) + "</svg>"
    for a, b in (("%", "%25"), ("#", "%23"), ("<", "%3C"), (">", "%3E"), (" ", "%20"),
                 ("'", "%27")):
        svg = svg.replace(a, b)
    return "data:image/svg+xml;charset=utf-8," + svg


# ── the sheet: the strip's outline (edges of one cell only) and its hinges ────────

def rk(p):
    return (round(p[0], 6), round(p[1], 6))


cell_edges = [(rk(c[k]), rk(c[(k + 1) % len(c)])) for c in CELLS for k in range(len(c))]
undirected = [frozenset(e) for e in cell_edges]
nxt_pt = {a: b for (a, b), u in zip(cell_edges, undirected) if undirected.count(u) == 1}
ring = [min(nxt_pt)]
while nxt_pt[ring[-1]] != ring[0]:
    ring.append(nxt_pt[ring[-1]])
if len(ring) != len(nxt_pt):
    raise ValueError("flexagon: the strip's outline is not one loop")
NAMES = {"trihexa": L4("Trihexaflexagon strip", "Tira del trihexaflexágono",
                       "Bande du trihexaflexagone", "Tira do triexaflexágono"),
         "hexahexa": L4("Hexahexaflexagon strip", "Tira del hexahexaflexágono",
                        "Bande de l'hexahexaflexagone", "Tira do hexaexaflexágono"),
         "tetra": L4("Tetraflexagon strip", "Tira del tetraflexágono",
                     "Bande du tétraflexagone", "Tira do tetraflexágono")}
sheet = pliego.Sheet("strip", ring, stock=stock, grain_deg=0.0, label=NAMES[style],
                     front=pliego.Face(None, art("F")), back=pliego.Face(None, art("B")))
MK = [sheet.crease(CELLS[i][k0], CELLS[i][k1],
                   ("valley" if ANG0[i] > 0 else "mountain") if i in folded else "flat",
                   180.0 if i in folded else 0.0, name="glue-hinge" if i == GLUE - 1 else None)
      for i, (k0, k1, _, _) in enumerate(HINGE)]

# ── the programs ──────────────────────────────────────────────────────────────

if mode == "make":
    steps = []
    for n, i in enumerate(ST["folds"], 1):
        a, b = i + 1, i + 2
        lab = (L4(f"Valley-fold between cells {a} and {b}",
                  f"Dobla en valle entre las celdas {a} y {b}",
                  f"Pli vallée entre les cases {a} et {b}",
                  f"Dobre em vale entre as células {a} e {b}") if ANG0[i] > 0 else
               L4(f"Mountain-fold between cells {a} and {b}",
                  f"Dobla en monte entre las celdas {a} y {b}",
                  f"Pli montagne entre les cases {a} et {b}",
                  f"Dobre em montanha entre as células {a} e {b}"))
        if i == GLUE - 1:
            lab = L4(f"Fold the glue cell {b} onto cell 1 and glue it",
                     f"Dobla la celda de pegado {b} sobre la celda 1 y pégala",
                     f"Plier la case à coller {b} sur la case 1 et la coller",
                     f"Dobre a célula de colagem {b} sobre a célula 1 e cole-a")
        steps.append(pliego.Step(f"fold-{n}", lab, [(MK[i], ANG0[i])], duration_ms=1200))
    result = pliego.Assembly(
        [sheet], controls=[pliego.sequence_control(label=L4("Fold", "Doblar", "Plier", "Dobrar"))],
        sequence=pliego.Sequence(steps, mode="kinematic"), title="Flexagon")
else:
    Pg, Pe = chain_pose(ANG0), chain_pose(ANG0, clamp=180.0 - EPS_DEG)
    m = affine([p[:2] for p in CELLS[GLUE][:3]], [q[:2] for q in Pg[GLUE][:3]])
    cx = sum(p[0] for p in CELLS[GLUE]) / len(CELLS[GLUE])
    cy = sum(p[1] for p in CELLS[GLUE]) / len(CELLS[GLUE])
    o = stacks0[secs0[0]]
    join = pliego.glue("glue-cell", sheet,
                       [(cx + (p[0] - cx) * 0.85, cy + (p[1] - cy) * 0.85) for p in CELLS[GLUE]],
                       sheet, (m[0], m[2], m[1], m[3], m[4], m[5]),
                       side="front" if o.index(GLUE) > o.index(0) else "back")

    def initial(_sheet_id, uv):
        """The flat state, its flat folds a hair short of 180° so the layer order reads."""
        for c, q in zip(CELLS, Pe):
            if all((c[(k + 1) % len(c)][0] - c[k][0]) * (uv[1] - c[k][1])
                   - (c[(k + 1) % len(c)][1] - c[k][1]) * (uv[0] - c[k][0]) >= -1e-3
                   for k in range(len(c))):
                t = affine(c[:3], [(0.0, 0.0), (1.0, 0.0), (0.0, 1.0)])
                a, b = t[0] * uv[0] + t[2] * uv[1] + t[4], t[1] * uv[0] + t[3] * uv[1] + t[5]
                w = add(q[0], add(mul(a, sub(q[1], q[0])), mul(b, sub(q[2], q[0]))))
                return (w[0], w[2], -w[1])
        raise ValueError(f"flexagon: point {uv} is on no cell")

    steps, prev, count = [], list(ANG0), {}
    for kind_, n_flex, a in frames:
        k = count[(kind_, n_flex)] = count.get((kind_, n_flex), 0) + 1
        top = history[n_flex][0]
        if kind_ == "open":
            lab = L4(f"Flex {n_flex}: open from the centre, face {top} shows ({k}/{SUB})",
                     f"Flexión {n_flex}: ábrelo desde el centro, aparece la cara {top} ({k}/{SUB})",
                     f"Flexion {n_flex} : ouvrir par le centre, la face {top} apparaît ({k}/{SUB})",
                     f"Flexão {n_flex}: abra pelo centro, aparece a face {top} ({k}/{SUB})")
        elif N == 6:
            lab = L4(f"Flex {n_flex}: pinch into a three-pointed star ({k}/{SUB})",
                     f"Flexión {n_flex}: pellizca hasta formar una estrella de tres puntas ({k}/{SUB})",
                     f"Flexion {n_flex} : pincer en étoile à trois branches ({k}/{SUB})",
                     f"Flexão {n_flex}: aperte até formar uma estrela de três pontas ({k}/{SUB})")
        else:
            lab = L4(f"Flex {n_flex}: close it like a book ({k}/{SUB})",
                     f"Flexión {n_flex}: ciérralo como un libro ({k}/{SUB})",
                     f"Flexion {n_flex} : le fermer comme un livre ({k}/{SUB})",
                     f"Flexão {n_flex}: feche-o como um livro ({k}/{SUB})")
        moved = [(MK[i], a[i]) for i in range(NC - 1) if abs(a[i] - prev[i]) > 1e-7]
        steps.append(pliego.Step(f"flex-{n_flex}-{kind_}-{k}", lab, moved, duration_ms=300))
        prev = a
    result = pliego.Assembly(
        [sheet], joins=[join], initial=initial,
        controls=[pliego.sequence_control(label=L4("Flex", "Flexionar", "Flexer", "Flexionar"))],
        sequence=pliego.Sequence(steps, mode="kinematic"), title="Flexagon")

print(f"flexagon: style={style} mode={mode} cells={NC} side={S:g}mm faces={len(first)} "
      f"flexes={len(history) - 1} shows={'-'.join(str(h[0]) for h in history)} "
      f"vertex_residual_deg={worst:.2g}")
