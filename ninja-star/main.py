"""Ninja star (shuriken) — sheet-hyperobjects cartridge (Pliego): the traditional two-unit star.
Two half-square units, mirror images, are folded by simple folds; unit B is turned over, crossed
under unit A, and each unit's halves are folded across the other to lock them together.
"""

import math

import pliego

# ── fold engine: convex facets with rigid transforms (sheet (u, v) -> world (u, 0, -v), front +Y).
# A move rotates the facets the paper connects on one side of a line; each kernel edge's fold angle
# is measured between its two faces, so every program state is rigid and closes by construction.
TOL = 1e-6
IDT = ((1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0), (0.0, 0.0, 0.0))

def L4(en, es, fr, pt):
    return {"en": en, "es": es, "fr": fr, "pt": pt}

def S(fd, sid, en, es, fr, pt, ms=1500):
    step(fd, sid, L4(en, es, fr, pt), ms)

def vsub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])

def vdot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]

def vcross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])

def vunit(a):
    n = math.sqrt(vdot(a, a))
    return (a[0] / n, a[1] / n, a[2] / n)

def mvec(m, v):
    return tuple(m[3 * i] * v[0] + m[3 * i + 1] * v[1] + m[3 * i + 2] * v[2] for i in range(3))

def tapply(t, p):
    q = mvec(t[0], p)
    return (q[0] + t[1][0], q[1] + t[1][1], q[2] + t[1][2])

def tcomp(a, b):
    r = tuple(sum(a[0][3 * i + k] * b[0][3 * k + j] for k in range(3)) for i in range(3)
              for j in range(3))
    return (r, tapply(a, b[1]))

def about(o, r):
    q = mvec(r, o)
    return (r, (o[0] - q[0], o[1] - q[1], o[2] - q[2]))

def rot_line(o, d, ang):
    x, y, z = vunit(d)
    c, s = math.cos(ang), math.sin(ang)
    k = 1.0 - c
    return about(o, (c + x * x * k, x * y * k - z * s, x * z * k + y * s, y * x * k + z * s,
                     c + y * y * k, y * z * k - x * s, z * x * k - y * s, z * y * k + x * s,
                     c + z * z * k))

def unp(p):
    return (p[0], 0.0, -p[1])

def area2(poly):
    return 0.5 * sum(poly[i - 1][0] * poly[i][1] - poly[i][0] * poly[i - 1][1]
                     for i in range(len(poly)))

def inside(p, poly, tol=1e-7):
    return all((b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0]) >= -tol
               for a, b in zip(poly, poly[1:] + poly[:1]))

def on_seg(p, a, b, tol=1e-6):
    dx, dy = b[0] - a[0], b[1] - a[1]
    ln2 = dx * dx + dy * dy
    t = ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / ln2
    return -tol <= t <= 1 + tol and abs(dx * (p[1] - a[1]) - dy * (p[0] - a[0])) <= tol * ln2 ** .5

def split_poly(poly, s):
    left, right, chord = [], [], []
    for i, a in enumerate(poly):
        b, sa, sb = poly[(i + 1) % len(poly)], s[i], s[(i + 1) % len(poly)]
        for lst, ok in ((left, sa >= -TOL), (right, sa <= TOL), (chord, abs(sa) <= TOL)):
            if ok:
                lst.append(a)
        if sa * sb < 0 and abs(sa) > TOL and abs(sb) > TOL:
            t = sa / (sa - sb)
            q = (a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1]))
            left.append(q), right.append(q), chord.append(q)
    return left, right, chord

def facet(fid, poly, t):
    return {"id": fid, "poly": poly, "T": t}

def folder(outline, t0=IDT):
    # snaps: every state and each move's half-way state (it signs flat folds), {facet id: T}
    ring = [tuple(map(float, p)) for p in outline]
    ring = ring if area2(ring) > 0 else ring[::-1]
    fd = {"outline": ring, "f": [facet(0, ring, t0)], "parent": {0: -1}, "nid": 1, "ops": 0,
          "creases": [], "flats": [], "cuts": [], "snaps": [], "steps": []}
    snap(fd)
    return fd

def snap(fd, override=None):
    fd["snaps"].append({**{f["id"]: f["T"] for f in fd["f"]}, **(override or {})})

def step(fd, sid, label, ms=1500, note=None):
    fd["steps"].append((len(fd["snaps"]) - 1, sid, label, ms, note))

def lookup(fd, fid, snap):
    while fid not in snap:
        fid = fd["parent"][fid]
    return snap[fid]

def at(fd, p, tol=1e-7):
    for f in fd["f"]:
        if inside(p, f["poly"], tol):
            return f
    raise ValueError(f"no facet at sheet point ({p[0]:.3f}, {p[1]:.3f})")

def deepest(fd, p):
    def depth(f):
        return min(((b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0]))
                   / math.hypot(b[0] - a[0], b[1] - a[1])
                   for a, b in zip(f["poly"], f["poly"][1:] + f["poly"][:1]))
    return max(fd["f"], key=depth)

def world(fd, p):
    return tapply(at(fd, p)["T"], unp(p))

def image(fd, f):
    return [(w[0], -w[2]) for w in (tapply(f["T"], unp(p)) for p in f["poly"])]

def adjacency(fd, facets):
    buckets, out, seen = {}, {i: [] for i in range(len(facets))}, set()
    for i, f in enumerate(facets):
        for a, b in zip(f["poly"], f["poly"][1:] + f["poly"][:1]):
            ln = math.hypot(b[0] - a[0], b[1] - a[1])
            ux, uy = (b[0] - a[0]) / ln, (b[1] - a[1]) / ln
            if ux < -1e-9 or (abs(ux) <= 1e-9 and uy < 0):
                ux, uy = -ux, -uy
            key = (round(math.atan2(uy, ux) * 1e3), round((ux * a[1] - uy * a[0]) * 10))
            buckets.setdefault(key, []).append((i, a, b, ux, uy))
    for (ka, kc), items in buckets.items():
        near = [x for da in (-1, 0, 1) for dc in (-1, 0, 1)
                for x in buckets.get((ka + da, kc + dc), ())]
        for i, a, b, ux, uy in items:
            for j, c, d, _, _ in near:
                if j <= i or (i, j, a, c) in seen or max(
                        abs(ux * (q[1] - a[1]) - uy * (q[0] - a[0])) for q in (c, d)) > 1e-6:
                    continue
                seen.add((i, j, a, c))
                tb = ux * (b[0] - a[0]) + uy * (b[1] - a[1])
                tc, td = (ux * (q[0] - a[0]) + uy * (q[1] - a[1]) for q in (c, d))
                lo, hi = max(min(0.0, tb), min(tc, td)), min(max(0.0, tb), max(tc, td))
                if hi - lo < 1e-6:
                    continue
                p, q = (a[0] + ux * lo, a[1] + uy * lo), (a[0] + ux * hi, a[1] + uy * hi)
                if not any(on_seg(p, *ct) and on_seg(q, *ct) for ct in fd["cuts"]):
                    out[i].append((j, p, q)), out[j].append((i, p, q))
    return out

def flood(fd, facets, seeds, blocked):
    adj = adjacency(fd, facets)
    moving, stack = set(seeds), list(seeds)
    while stack:
        i = stack.pop()
        for j, p, q in adj[i]:
            if j not in moving and not blocked(facets[i], p, q):
                moving.add(j), stack.append(j)
    return moving

def fold(fd, p0, p1, kind="valley", seeds=None, angle=180.0, cut=False):
    # fold (flat state) the paper left of the folded-frame line p0 -> p1 (valley: towards +Y);
    # seeds (sheet points) pick the flap, else every layer moves; kind="flat": split only
    y0 = fd["f"][0]["T"][1][1]  # the height of the flat stack (0 unless the sheet was placed)
    if any(abs(abs(f["T"][0][4]) - 1.0) > 1e-7 or abs(f["T"][1][1] - y0) > 1e-4 for f in fd["f"]):
        raise ValueError("a line fold needs a flat-folded state")
    ln = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
    dx, dy = (p1[0] - p0[0]) / ln, (p1[1] - p0[1]) / ln
    pieces = []
    for f in fd["f"]:
        im = image(fd, f)
        s = [dx * (q[1] - p0[1]) - dy * (q[0] - p0[0]) for q in im]
        al = [dx * (q[0] - p0[0]) + dy * (q[1] - p0[1]) for q in im]
        if min(s) >= -TOL or max(s) <= TOL or (cut and (max(al) < TOL or min(al) > ln - TOL)):
            pieces.append([f["poly"], f, min(s) >= -TOL, None])
        else:
            a, b, ch = split_poly(f["poly"], s)
            pieces += [[a, f, True, ch], [b, f, False, ch]]
    if cut:
        return cutting(fd, pieces, p0, dx, dy, ln)
    lp = [pc for pc in pieces if pc[2]]
    left = [facet(-1, pc[0], pc[1]["T"]) for pc in lp]

    def on_line(fc, p, q):
        return all(abs(dx * (-w[2] - p0[1]) - dy * (w[0] - p0[0])) <= 1e-5
                   for w in (tapply(fc["T"], unp(p)), tapply(fc["T"], unp(q))))
    sd = set(range(len(left)))
    if seeds is not None:
        sd = {i for p in seeds for i, fc in enumerate(left) if inside(p, fc["poly"], -1e-6)}
        if len(sd) < len(seeds):
            raise ValueError(f"a seed of {seeds} is not on the moving side")
    mv = flood(fd, left, sd, on_line)
    sign = {"flat": 0.0, "valley": 1.0, "mountain": -1.0}[kind] * math.radians(angle)
    o, d = (p0[0], y0, -p0[1]), (dx, 0.0, -dy)
    return commit(fd, pieces, {id(lp[i]) for i in mv}, rot_line(o, d, sign),
                        rot_line(o, d, sign / 2.0), "flat" if kind == "flat" else True)

def commit(fd, pieces, moving, w, wh, record):
    new, half, moved, made, byf = [], {}, set(), [], {}
    for pc in pieces:
        byf.setdefault(id(pc[1]), []).append(pc)
    for f in fd["f"]:
        pcs = byf[id(f)]
        if len(pcs) == 1 or id(pcs[0] if pcs[0][2] else pcs[1]) not in moving:
            if len(pcs) == 1 and id(pcs[0]) in moving:
                moved.add(f["id"])
                half[f["id"]], f["T"] = tcomp(wh, f["T"]), tcomp(w, f["T"])
            new.append(f)
            continue
        lp, rp = pcs if pcs[0][2] else pcs[::-1]
        fl, fr = facet(fd["nid"], lp[0], tcomp(w, f["T"])), facet(fd["nid"] + 1, rp[0], f["T"])
        fd["parent"][fl["id"]] = fd["parent"][fr["id"]] = f["id"]
        fd["nid"] += 2
        half[fl["id"]] = tcomp(wh, f["T"])
        moved.add(fl["id"])
        new += [fl, fr]
        if record and math.dist(lp[3][0], lp[3][-1]) > 1e-6:
            made.append((lp[3][0], lp[3][-1]))
    fd["ops"] += 1
    (fd["flats"] if record == "flat" else fd["creases"]).extend((a, b, fd["ops"]) for a, b in made)
    fd["f"] = new
    if record:
        snap(fd, half)
        snap(fd)
    return moved, made

def series(fd, fa, fb, a, b):
    # fold angle (deg, valley > 0) between facet ids fa (left of a -> b) and fb, per state
    out, prev, d = [], 0.0, vunit(vsub(unp(b), unp(a)))
    for s in fd["snaps"]:
        ta, tb = lookup(fd, fa, s)[0], lookup(fd, fb, s)[0]
        n1 = tuple(sum(ta[3 * k + i] * tb[3 * k + 1] for k in range(3)) for i in range(3))
        v = -math.degrees(math.atan2(vdot(d, vcross((0.0, 1.0, 0.0), n1)), n1[1]))
        prev = max(-180.0, min(180.0, v + 360.0 * round((prev - v) / 360.0)))
        out.append(prev)
    return out

def pair(fd, a, b, eps=1e-3):
    ln = math.hypot(b[0] - a[0], b[1] - a[1])
    m, n = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2), ((a[1] - b[1]) / ln, (b[0] - a[0]) / ln)
    return (at(fd, (m[0] + eps * n[0], m[1] + eps * n[1])),
            at(fd, (m[0] - eps * n[0], m[1] - eps * n[1])))

def turn(fd, a, b, target, seed, keep_sign=True):
    # set the crease through sheet points a, b to `target` (keep_sign: its current sign)
    fa, fb = pair(fd, a, b)
    cur = series(fd, fa["id"], fb["id"], a, b)[-1]
    if keep_sign:
        target = math.copysign(abs(target), cur if abs(cur) > 1e-9 else target)
    o, d = tapply(fa["T"], unp(a)), mvec(fa["T"][0], vunit(vsub(unp(b), unp(a))))
    allc = fd["creases"] + fd["flats"]
    op = [c[2] for c in allc if (on_seg(a, c[0], c[1]) and on_seg(b, c[0], c[1]))
          or (on_seg(c[0], a, b) and on_seg(c[1], a, b))]
    if not op:
        raise ValueError("turn: no crease through those points")
    grp = [c for c in allc if c[2] == op[0]]
    mv = flood(fd, fd["f"], [fd["f"].index(at(fd, seed, -1e-6))], lambda fc, p, q: any(
        on_seg(p, c0, c1) and on_seg(q, c0, c1) for c0, c1, _ in grp))
    ia, ib = fd["f"].index(fa), fd["f"].index(fb)
    if (ia in mv) == (ib in mv):
        raise ValueError("turn: the crease does not separate the seed's side")
    delta = math.radians((cur - target) if ib in mv else (target - cur))
    move(fd, {fd["f"][i]["id"] for i in mv}, rot_line(o, d, delta), rot_line(o, d, delta / 2))
    return target

def move(fd, ids, w, wh):
    half = {}
    for f in fd["f"]:
        if f["id"] in ids:
            half[f["id"]], f["T"] = tcomp(wh, f["T"]), tcomp(w, f["T"])
    snap(fd, half)
    snap(fd)

# ── the kernel sheet, the fold program and the presentation ──────────────────
def interior_point(poly):
    ring = [pliego.P(*q) for q in poly]
    for k in range(len(poly)):
        for a, b, c in [(poly[k], poly[(k + m) % len(poly)], poly[(k + m + 1) % len(poly)])
                        for m in range(1, len(poly) - 1)]:
            q = ((a[0] + b[0] + c[0]) / 3.0, (a[1] + b[1] + c[1]) / 3.0)
            if pliego.geometry.point_in_polygon(pliego.P(*q), ring) == 1:
                return q
    raise ValueError("face without an interior point")

def build_sheet(fd, sid, label, stock, front, back):
    sheet = pliego.Sheet(sid, [pliego.P(*p) for p in fd["outline"]], stock=stock, label=label,
                         front=front, back=back)
    for a, b, _ in fd["creases"]:
        fa, fb = pair(fd, a, b)
        ser = series(fd, fa["id"], fb["id"], a, b)
        ref = ser[-1] if abs(ser[-1]) > 0.5 else max(ser, key=abs)
        if abs(ref) < 1e-3:
            raise ValueError("a crease that never folds")
        sheet.crease(a, b, "valley" if ref > 0 else "mountain", abs(ref))
    for a, b, _ in fd["flats"]:
        sheet.crease(a, b, "flat")
    for a, b in fd["cuts"]:
        sheet.cut([a, b])
    arr = sheet.build()
    vs = [(v.x, v.y) for v in arr.vertices]
    fmap = [deepest(fd, interior_point([vs[v] for v in face]))["id"] for face in arr.faces]
    info = {}
    for fi, lst in pliego.kinematics.face_adjacency(arr).items():
        for g, e, a, b in lst:
            if e not in info and arr.assignment[e] in ("M", "V", "F"):
                info[e] = series(fd, fmap[fi], fmap[g], vs[a], vs[b])
    return {"sheet": sheet, "arr": arr, "info": info, "fd": fd, "f0": fmap[0],
            "root": pliego.P(*interior_point([vs[v] for v in arr.faces[0]]))}

def make_steps(entries):
    # (built, snap, id, label, ms, note) -> Steps listing only the edges they move (spec §5.6)
    out, prev = [], {}
    for b, si, sid, label, ms, note in entries:
        p = prev.get(id(b), 0)
        tg = [(pliego.assembly.EdgeRef(b["sheet"], e), ser[si])
              for e, ser in sorted(b["info"].items()) if abs(ser[si] - ser[p]) > 1e-6]
        if not tg and "slit" not in sid:
            raise ValueError(f"step '{sid}' moves no crease")
        out.append(pliego.Step(sid, label, tg, duration_ms=ms, note=note))
        prev[id(b)] = si
    return out

def check_closure(b, sis, tol=1e-3):
    worst = mid = 0.0
    last = {e: 0.0 for e in b["info"]}
    for si in sis:
        ang = {e: ser[si] for e, ser in b["info"].items()}
        worst = max(worst, pliego.kinematics.closure_residual(b["arr"], ang, b["root"]))
        mid = max(mid, pliego.kinematics.closure_residual(
            b["arr"], {e: (ang[e] + last[e]) / 2.0 for e in ang}, b["root"]))
        last = ang
    if worst > tol:
        raise ValueError(f"inconsistent fold state: closure {worst:.3g} mm")
    return worst, mid

def final_angles(b):
    return {e: ser[-1] for e, ser in b["info"].items()}

def quat(r):
    i = max(range(4), key=lambda k: r[0] + r[4] + r[8] if k == 3 else r[4 * k])
    if i == 3:
        w = math.sqrt(1.0 + r[0] + r[4] + r[8]) / 2.0
        return ((r[7] - r[5]) / (4 * w), (r[2] - r[6]) / (4 * w), (r[3] - r[1]) / (4 * w), w)
    j, k = (i + 1) % 3, (i + 2) % 3
    s = math.sqrt(max(1e-30, 1.0 + r[4 * i] - r[4 * j] - r[4 * k])) * 2.0
    q = [0.0] * 4
    q[i], q[j], q[k] = s / 4, (r[3 * j + i] + r[3 * i + j]) / s, (r[3 * k + i] + r[3 * i + k]) / s
    q[3] = (r[3 * k + j] - r[3 * j + k]) / s
    return tuple(q)

def present(bs, fwd, up, lift=0.0):
    # show the finished model up -> +Y, fwd -> -Z (the studio roots each sheet at its face 0)
    bs = bs if isinstance(bs, list) else [bs]
    lat = vcross(up, fwd)
    rd = (-lat[0], -lat[1], -lat[2], up[0], up[1], up[2], -fwd[0], -fwd[1], -fwd[2])
    ps = [tcomp((rd, (0.0, 0.0, 0.0)), next(f for f in b["fd"]["f"] if f["id"] == b["f0"])["T"])
          for b in bs]
    low = min(min(tapply(p, unp(q))[1] for q in b["fd"]["outline"]) for p, b in zip(ps, bs))
    low = min([low] + [mvec(rd, tapply(f["T"], unp(q)))[1] for b in bs for f in b["fd"]["f"]
                       for q in f["poly"]])
    for (r, t), b in zip(ps, bs):
        b["sheet"].placement = pliego.Placement((t[0], t[1] - low + lift, t[2]), quat(r))

def program(entries, sheets, title, meta=None, physical=False):
    tg = {b["sheet"].id: {"angles": final_angles(b), "root": (b["root"].x, b["root"].y)}
          for b in sheets}
    return pliego.Assembly(
        [b["sheet"] for b in sheets],
        controls=[pliego.sequence_control(label=L4(
            "Fold program", "Secuencia de pliegues", "Séquence de pliage", "Sequência de dobras"))],
        sequence=pliego.Sequence(make_steps(entries), mode="physical" if physical else "kinematic"),
        targets={} if any(b["fd"]["cuts"] for b in sheets) else {  # kernel poses share cut vertices
            "folded": tg if len(sheets) > 1 else tg[sheets[0]["sheet"].id]},
        title=title, meta=meta or {})


P, C = pliego.param, pliego.clamp
size = C(float(P(lambda: size, 150.0)), 100.0, 300.0)  # noqa: F821
stock = P(lambda: stock, "kami")  # noqa: F821
u = size / 4.0  # each unit is half a square: 4u by 2u
RECT = [(0.0, 0.0), (4.0 * u, 0.0), (4.0 * u, 2.0 * u), (0.0, 2.0 * u)]
ctr = (2.0 * u, u / 2.0)  # the unit's centre once folded
# unit B: turned over, a quarter turn, its centre on unit A's, one paper thickness below
flip = rot_line((ctr[0], 0.0, -ctr[1]), (1.0, 0.0, 0.0), math.pi)
quarter = rot_line((ctr[0], 0.0, -ctr[1]), (0.0, 1.0, 0.0), math.pi / 2.0)
tB = tcomp((IDT[0], (0.0, -0.4, 0.0)), tcomp(quarter, flip))
A = folder(RECT)
B = folder(RECT, tB)
prog = []


def F(fd, t0, p0, p1, kind, mirror=False, seeds=None):
    """A fold given in the unit's own frame (mirrored for unit B), carried by its placement."""
    if mirror:
        p0, p1 = (4.0 * u - p1[0], p1[1]), (4.0 * u - p0[0], p0[1])
        seeds = None if seeds is None else [(4.0 * u - q[0], q[1]) for q in seeds]

    def g(p):
        w = tapply(t0, (p[0], 0.0, -p[1]))
        return (w[0], -w[2])
    if t0[0][4] < 0:  # turned over: the same paper moves from the other side of the line
        return fold(fd, g(p1), g(p0), {"valley": "mountain", "mountain": "valley"}[kind], seeds=seeds)
    return fold(fd, g(p0), g(p1), kind, seeds=seeds)


def unit(fd, t0, mir, name):
    m = 4.0 * u if mir else 0.0
    F(fd, t0, (2.0 * u, -1.0), (2.0 * u, 2.0 * u + 1.0), "valley", mir)
    step(fd, f"{name.lower()}-crease", L4(f"Unit {name}: fold in half crosswise", f"Pieza {name}: dobla por la mitad a lo ancho",
                                  f"Module {name} : pliez en deux dans la largeur", f"Peça {name}: dobre ao meio na largura"), 900)
    turn(fd, (2.0 * u, 0.0), (2.0 * u, 2.0 * u), 0.0, (abs(m - u), u), keep_sign=False)
    step(fd, f"{name.lower()}-unfold", L4("Unfold", "Desdobla", "Dépliez", "Desdobre"), 700)
    F(fd, t0, (-1.0, u), (4.0 * u + 1.0, u), "valley", mir)
    step(fd, f"{name.lower()}-half", L4(f"Unit {name}: fold in half lengthwise", f"Pieza {name}: dobla por la mitad a lo largo",
                                f"Module {name} : pliez en deux dans la longueur", f"Peça {name}: dobre ao meio no comprimento"))
    F(fd, t0, (u + 1.0, -1.0), (-1.0, u + 1.0), "valley", mir)
    F(fd, t0, (3.0 * u - 1.0, u + 1.0), (4.0 * u + 1.0, -1.0), "valley", mir)
    step(fd, f"{name.lower()}-corners", L4(
        f"Unit {name}: fold opposite corners in, one up and one down",
        f"Pieza {name}: dobla esquinas opuestas, una hacia arriba y otra hacia abajo",
        f"Module {name} : rabattez deux coins opposés, l'un vers le haut, l'autre vers le bas",
        f"Peça {name}: dobre cantos opostos, um para cima e outro para baixo"))


def arms(fd, t0, mir, name):
    F(fd, t0, (u - 1.0, -1.0), (2.0 * u + 1.0, u + 1.0), "valley", mir, [(0.3 * u, 0.9 * u)])
    F(fd, t0, (3.0 * u + 1.0, u + 1.0), (2.0 * u - 1.0, -1.0), "valley", mir, [(3.7 * u, 0.1 * u)])
    step(fd, f"{name.lower()}-arms", L4(
        f"Fold unit {name}'s two halves across the other unit, one each way, and tuck them in",
        f"Dobla las dos mitades de la pieza {name} sobre la otra pieza, una hacia cada lado, y mételas",
        f"Rabattez les deux moitiés du module {name} sur l'autre module, une de chaque côté, et rentrez-les",
        f"Dobre as duas metades da peça {name} sobre a outra peça, uma para cada lado, e encaixe-as"))


unit(A, IDT, False, "A")
unit(B, tB, True, "B")
arms(B, tB, True, "B")
arms(A, IDT, False, "A")
lab = {"A": L4("Unit A", "Pieza A", "Module A", "Peça A"), "B": L4("Unit B", "Pieza B", "Module B", "Peça B")}
bA = build_sheet(A, "unit-a", lab["A"], stock, "#264653", "#e9c46a")
bB = build_sheet(B, "unit-b", lab["B"], stock, "#e76f51", "#e9c46a")
present([bA, bB], (0.0, 0.0, -1.0), (0.0, 1.0, 0.0))
order = {sid: (bb, si, sid, l, ms, nt) for bb, fd in ((bA, A), (bB, B)) for si, sid, l, ms, nt in fd["steps"]}
seq = [k for k in order if k.startswith("a-") and not k.endswith("arms")] + \
      [k for k in order if k.startswith("b-") and not k.endswith("arms")] + ["b-arms", "a-arms"]
entries = [order[k] for k in seq]
worst = max(check_closure(bb, [e[1] for e in entries if e[0] is bb])[0] for bb in (bA, bB))
print(f"kinematics: steps={len(entries)} max_closure_mm={worst:.3e}")
result = program(entries, [bA, bB], "Ninja star")
