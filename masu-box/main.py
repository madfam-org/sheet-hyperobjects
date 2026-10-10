"""Masu box — sheet-hyperobjects cartridge (Pliego): the traditional box and its lid (two modes).
Folded from a square by simple folds; each end wall then rises while its corners fold in, an exact
one-degree-of-freedom rigid motion, and the end flaps fold over into the box.
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

def frame_map(c0, c1, w0, w1, o):
    def fr(a, b):
        e1, e3 = vunit(a), vunit(vcross(a, b))
        return e1, vcross(e3, e1), e3
    cf, wf = fr(c0, c1), fr(w0, w1)
    return about(o, tuple(sum(wf[k][i] * cf[k][j] for k in range(3)) for i in range(3)
                          for j in range(3)))

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

def preimage(fd, ids, q):
    # the sheet point that lies at folded-frame point q on the first facet in `ids` covering q
    for f in fd["f"]:
        im, fid = image(fd, f), f["id"]
        while ids is not None and fid not in ids and fid != -1:
            fid = fd["parent"][fid]
        if fid != -1 and inside(q, im if area2(im) > 0 else im[::-1], -1e-6):
            r, t = f["T"]
            w = (q[0] - t[0], 0.0, -q[1] - t[2])
            x = tuple(r[i] * w[0] + r[3 + i] * w[1] + r[6 + i] * w[2] for i in range(3))
            return (x[0], -x[2])
    raise ValueError(f"no facet of the set covers ({q[0]:.2f}, {q[1]:.2f})")

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
size = C(float(P(lambda: size, 200.0)), 120.0, 400.0)  # noqa: F821
gap = C(float(P(lambda: gap, 1.5)), 0.5, 5.0)  # noqa: F821
stock = P(lambda: stock, "kami")  # noqa: F821
run_mode = P(lambda: mode, "box")  # noqa: F821
S0 = size + (4.0 * math.sqrt(2.0) * gap if run_mode == "lid" else 0.0)  # lid floor 2·gap wider
h, Lh = S0 / 2.0, S0 / math.sqrt(2.0)  # Lh: half the diagonal = the blintzed square's side
q = Lh / 4.0  # the floor is the square |x|, |y| <= q; the walls are q high
SQ = [(0.0, 0.0), (S0, 0.0), (S0, S0), (0.0, S0)]
t0 = tcomp((IDT[0], (-h, 0.0, h)), rot_line((h, 0.0, -h), (0.0, 1.0, 0.0), math.pi / 4.0))
fd = folder(SQ, t0)
corner = {}
for p in SQ:  # sheet corners by where they sit on the diamond: top, right, bottom, left
    w = tapply(t0, unp(p))
    corner[(round(w[0] / Lh), round(-w[2] / Lh))] = (p[0] + 0.02 * (h - p[0]), p[1] + 0.02 * (h - p[1]))
CT, CB = corner[(0, 1)], corner[(0, -1)]


def pre(x, y):
    return preimage(fd, None, (x, y))


def crease(p0, p1, sid, label, ms=900):
    """Fold and unfold through every layer (the seed is taken on the moving side first)."""
    ln = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
    n = ((p0[1] - p1[1]) / ln, (p1[0] - p0[0]) / ln)
    m = ((p0[0] + p1[0]) / 2.0 + 0.3 * q * n[0] + 0.17 * q * n[1],
         (p0[1] + p1[1]) / 2.0 + 0.3 * q * n[1] - 0.17 * q * n[0])  # off every other line
    seed = pre(*m)
    _, made = fold(fd, p0, p1, "valley")
    step(fd, sid, label, ms)
    turn(fd, made[0][0], made[0][1], 0.0, seed, keep_sign=False)
    step(fd, sid + "-open", L4("Unfold", "Desdobla", "Dépliez", "Desdobre"), 600)
    return made


HALF = L4("Fold in half and unfold", "Dobla por la mitad y desdobla", "Pliez en deux et dépliez",
          "Dobre ao meio e desdobre")
crease((-Lh, -Lh), (Lh, Lh), "half-1", HALF)
crease((Lh, -Lh), (-Lh, Lh), "half-2", HALF)
_, mt = fold(fd, (-Lh, 2 * q), (Lh, 2 * q), "valley")
fold(fd, (2 * q, Lh), (2 * q, -Lh), "valley")
_, mb = fold(fd, (Lh, -2 * q), (-Lh, -2 * q), "valley")
fold(fd, (-2 * q, -Lh), (-2 * q, Lh), "valley")
S(fd, "blintz", "Fold the four corners to the centre", "Dobla las cuatro esquinas hasta el centro",
  "Rabattez les quatre coins au centre", "Dobre os quatro cantos até ao centro")
EDGE = L4("Fold the edge to the centre line and unfold", "Dobla el borde hasta la línea central y desdobla",
          "Rabattez le bord sur la ligne centrale et dépliez", "Dobre a aresta até à linha central e desdobre")
ct = crease((-Lh, q), (Lh, q), "edge-top", EDGE)
cb = crease((Lh, -q), (-Lh, -q), "edge-bottom", EDGE)
cr = crease((q, Lh), (q, -Lh), "edge-right", EDGE)
cl = crease((-q, -Lh), (-q, Lh), "edge-left", EDGE)
turn(fd, mt[0][0], mt[0][1], 0.0, CT, keep_sign=False)
turn(fd, mb[0][0], mb[0][1], 0.0, CB, keep_sign=False)
S(fd, "open-ends", "Unfold the top and bottom corners", "Desdobla las esquinas de arriba y de abajo",
  "Dépliez les coins du haut et du bas", "Desdobre os cantos de cima e de baixo", 1200)

# seeds, taken while flat: the walls, the end walls and the corner gussets (each side, each end)
sw = {sx: pre(sx * 1.6 * q, 0.0) for sx in (1, -1)}
ew = {sy: pre(0.0, sy * 1.5 * q) for sy in (1, -1)}
ga = {(sx, sy): pre(sx * 1.85 * q, sy * 1.25 * q) for sx in (1, -1) for sy in (1, -1)}
gb = {(sx, sy): pre(sx * 1.25 * q, sy * 1.85 * q) for sx in (1, -1) for sy in (1, -1)}
tip = {1: [c for c in ct if abs(tapply(t0, unp(((c[0][0] + c[1][0]) / 2, (c[0][1] + c[1][1]) / 2)))[2]
                                  + 3 * q) < 1e-6][0],
       -1: [c for c in cb if abs(tapply(t0, unp(((c[0][0] + c[1][0]) / 2, (c[0][1] + c[1][1]) / 2)))[2]
                                   - 3 * q) < 1e-6][0]}
for c, sx in ((cr, 1), (cl, -1)):  # raise towards +Y (the chord may lie in a turned-over layer)
    t = turn(fd, c[0][0], c[0][1], 90.0, sw[sx])
    if world(fd, sw[sx])[1] < 0.0:
        turn(fd, c[0][0], c[0][1], -t, sw[sx], keep_sign=False)
S(fd, "walls", "Raise the two side walls", "Levanta las dos paredes laterales",
  "Relevez les deux parois latérales", "Levante as duas paredes laterais", 1500)
UP, X, s2 = (0.0, 1.0, 0.0), (1.0, 0.0, 0.0), math.sqrt(0.5)


def end_wall(sy, n=5):
    """Raise one end wall; at each floor corner the gusset folds in along its diagonal. One rigid
    degree of freedom per corner: the diagonal ray stays 45° from the upright corner edge and 45°
    from the end wall's side edge, r2 = (up + n)/(√2 (1 + sin φ)) + √(sin φ / (1 + sin φ)) (∓x)."""
    north = (0.0, 0.0, -float(sy))

    def rays(phi, sx):
        sp, cp = math.sin(math.radians(phi)), math.cos(math.radians(phi))
        nphi = tuple(cp * north[i] + sp * UP[i] for i in range(3))
        r2 = tuple(s2 / (1.0 + sp) * (UP[i] + nphi[i]) - sx * math.sqrt(sp / (1.0 + sp)) * X[i]
                   for i in range(3))
        return nphi, r2
    groups = {}
    for key, seed in [(("end",), ew[sy])] + [(("a", sx), ga[(sx, sy)]) for sx in (1, -1)] + \
            [(("b", sx), gb[(sx, sy)]) for sx in (1, -1)]:
        V = {sx: (sx * q, 0.0, -sy * q) for sx in (1, -1)}
        dirs = [(V[sx], d) for sx in (1, -1) for d in (UP, rays(0.0, sx)[1], north, (-sx, 0.0, 0.0))]

        def blocked(fc, p0, p1):  # both ends of the shared edge on one ray
            ws = (tapply(fc["T"], unp(p0)), tapply(fc["T"], unp(p1)))
            return any(all(vdot(vcross(vsub(wpt, o), d), vcross(vsub(wpt, o), d)) < 1e-9
                           and vdot(vsub(wpt, o), d) > -1e-6 for wpt in ws) for o, d in dirs)
        g = flood(fd, fd["f"], [fd["f"].index(at(fd, seed, -1e-6))], blocked)
        groups[key] = {fd["f"][i]["id"]: fd["f"][i]["T"] for i in g}
    for k in range(1, n + 1):
        half = {}
        for phi, store in ((90.0 * (k - 0.5) / n, half), (90.0 * k / n, None)):
            moves = {("end",): rot_line((0.0, 0.0, -sy * q), X, sy * math.radians(phi))}
            for sx in (1, -1):
                o = (sx * q, 0.0, -sy * q)
                n0, r0 = rays(0.0, sx)
                n1, r1 = rays(phi, sx)
                moves[("a", sx)] = frame_map(UP, r0, UP, r1, o)
                moves[("b", sx)] = frame_map(r0, n0, r1, n1, o)
            for key, ids in groups.items():
                for f in fd["f"]:
                    if f["id"] in ids:
                        if store is None:
                            f["T"] = tcomp(moves[key], ids[f["id"]])
                        else:
                            store[f["id"]] = tcomp(moves[key], ids[f["id"]])
        snap(fd, half)
        snap(fd)
        end = L4("Raise the end wall: its corners fold in", "Levanta la pared del extremo: sus esquinas se doblan hacia dentro",
                 "Relevez la paroi du bout : ses coins se replient vers l'intérieur",
                 "Levante a parede da ponta: os cantos dobram-se para dentro")
        step(fd, f"end-{'top' if sy > 0 else 'bottom'}-{k}", {g_: f"{t} ({k}/{n})" for g_, t in end.items()}, 450)
    flap = mt if sy > 0 else mb
    cpt = CT if sy > 0 else CB
    inside = lambda: abs(world(fd, cpt)[2]) < q - 1e-6  # noqa: E731 - over or on the floor
    t = turn(fd, flap[0][0], flap[0][1], 90.0, cpt, keep_sign=False)
    t = t if inside() else turn(fd, flap[0][0], flap[0][1], -t, cpt, keep_sign=False)
    turn(fd, flap[0][0], flap[0][1], math.copysign(180.0, t), cpt, keep_sign=False)
    a0, b0 = tip[sy]
    t = turn(fd, a0, b0, 90.0, cpt, keep_sign=False)
    if not inside():
        turn(fd, a0, b0, -t, cpt, keep_sign=False)
    S(fd, f"flap-{'top' if sy > 0 else 'bottom'}", "Fold the flap over the wall and down onto the floor",
      "Dobla la solapa por encima de la pared y hasta el fondo", "Rabattez le rabat par-dessus la paroi jusqu'au fond",
      "Dobre a aba por cima da parede até ao fundo")


end_wall(1)
end_wall(-1)
box = [tapply(f["T"], unp(p)) for f in fd["f"] for p in f["poly"]]  # all paper inside the box
if max(max(abs(w[0]), abs(w[2]), abs(w[1] - q / 2.0) + q / 2.0) for w in box) > q + 1e-6:
    raise ValueError("the finished box has paper outside its walls")
b = build_sheet(fd, "square", L4("Square", "Cuadrado", "Carré", "Quadrado"), stock, "#f4efe6", "#c1121f")
present(b, (0.0, 0.0, -1.0), UP)
entries = [(b, *st) for st in fd["steps"]]
worst, mid = check_closure(b, [x[1] for x in entries])
print(f"kinematics: mode={run_mode} side={S0:.1f}mm floor={2 * q:.1f}mm wall={q:.1f}mm "
      f"steps={len(entries)} max_closure_mm={worst:.3e} max_linear_midpoint_closure_mm={mid:.3e}")
result = program(entries, [b], "Masu box" if run_mode == "box" else "Masu box lid")
