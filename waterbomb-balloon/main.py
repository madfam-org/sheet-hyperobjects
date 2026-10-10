"""Waterbomb balloon — sheet-hyperobjects cartridge (Pliego): the traditional water bomb.
The base collapses as one rigid degree-6 vertex; each face is then folded by simple folds. The
program ends in the folded, flat state: inflation needs the engine's air model.
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
        while fid not in ids and fid != -1:
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

def sectors(fd, p, ray_degs, r=0.5):
    """Rigid facet groups around the folded-frame point p between rays (CCW degrees) of
    a flat state, and the rays' world directions."""
    dirs = [(math.cos(math.radians(a)), math.sin(math.radians(a))) for a in ray_degs]

    def on_ray(fc, q0, q1):
        for x in (tapply(fc["T"], unp(q0)), tapply(fc["T"], unp(q1))):
            w = (x[0] - p[0], -x[2] - p[1])
            if math.hypot(*w) > 1e-6 and not any(abs(e[0] * w[1] - e[1] * w[0]) <= 1e-5
                                                 and vdot(e + (0,), w + (0,)) > 0 for e in dirs):
                return False
        return True
    groups, taken = [], set()
    for k, a0 in enumerate(ray_degs):
        a1 = ray_degs[(k + 1) % len(ray_degs)] + (360.0 if k == len(ray_degs) - 1 else 0.0)
        m = math.radians((a0 + a1) / 2.0)
        q = (p[0] + r * math.cos(m), p[1] + r * math.sin(m))
        sd = [i for i, f in enumerate(fd["f"]) for im in [image(fd, f)]
              if inside(q, im if area2(im) > 0 else im[::-1], -1e-9)]
        g = flood(fd, fd["f"], sd, on_ray)
        if g & taken:
            raise ValueError("sectors: the rays do not separate the paper")
        taken |= g
        groups.append({fd["f"][i]["id"] for i in g})
    if len(taken) != len(fd["f"]):
        raise ValueError("sectors: some facets belong to no sector")
    return groups, [(e[0], 0.0, -e[1]) for e in dirs]

def move_vertex(fd, p, groups, cur, new, half):
    """Rotate each sector group about the world point p from rays `cur` to rays `new`."""
    o, n, hv = (p[0], 0.0, -p[1]), len(groups), {}
    for k, g in enumerate(groups):
        k1 = (k + 1) % n
        w = frame_map(cur[k], cur[k1], new[k], new[k1], o)
        wh = frame_map(cur[k], cur[k1], half[k], half[k1], o)
        for f in fd["f"]:
            if f["id"] in g:
                hv[f["id"]], f["T"] = tcomp(wh, f["T"]), tcomp(w, f["T"])
    snap(fd, hv)
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
S0, h = size, size / 2.0
O = (h, h)
FRONT, BACK = "#3a86ff", "#f4efe6"
fd = folder([(0.0, 0.0), (S0, 0.0), (S0, S0), (0.0, S0)])

# ── 1. the waterbomb base: two diagonals, one midline, one rigid degree-6 vertex ──
for p0, p1, seed, sid, lab in (
        ((0.0, S0), (S0, 0.0), (S0 - 1.0, S0 - 6.0), "diagonal-1",
         L4("Valley-fold along a diagonal", "Dobla en valle por una diagonal",
            "Pliez en vallée selon une diagonale", "Dobre em vale por uma diagonal")),
        ((0.0, 0.0), (S0, S0), (1.0, S0 - 6.0), "diagonal-2",
         L4("Valley-fold along the other diagonal", "Dobla en valle por la otra diagonal",
            "Pliez en vallée selon l'autre diagonale", "Dobre em vale pela outra diagonal"))):
    fold(fd, p0, p1, "valley")
    step(fd, sid, lab, 1100)
    turn(fd, p0, p1, 0.0, seed, keep_sign=False)
    step(fd, sid + "-open", L4("Unfold", "Desdobla", "Dépliez", "Desdobre"), 700)
fold(fd, (-1.0, h), (S0 + 1.0, h), "mountain")
S(fd, "midline", "Mountain-fold in half, top behind", "Dobla en monte por la mitad, la parte de arriba hacia atrás",
  "Pliez en deux en montagne, le haut vers l'arrière", "Dobre em montanha ao meio, a parte de cima para trás", 1100)
turn(fd, (0.0, h), (S0, h), 0.0, (h, S0 - 2.0), keep_sign=False)
S(fd, "midline-open", "Unfold", "Desdobla", "Dépliez", "Desdobre", 700)
s2 = math.sqrt(0.5)
groups, flat = sectors(fd, O, [0.0, 45.0, 135.0, 180.0, 225.0, 315.0])


def rays(psi):
    """Sector rays at O when the lower-left triangle has turned psi degrees about O-D."""
    if psi < 1e-9:
        return list(flat)
    r3 = mvec(rot_line((0.0, 0.0, 0.0), flat[4], -math.radians(psi))[0], (-1.0, 0.0, 0.0))
    a, b, c = r3
    k, hh = (1.0 + a) * s2, math.hypot(b, c)
    off = math.sqrt(max(0.0, 0.5 - (k / hh) ** 2))
    y, z = max((k / hh / hh * b + sg * off * -c / hh, k / hh / hh * c + sg * off * b / hh)
               for sg in (1.0, -1.0))
    return [(-r3[0], r3[1], r3[2]), (s2, y, z), (-s2, y, z), r3, flat[4], flat[5]]


N = 6
cur = rays(0.0)
for i in range(1, N + 1):
    new = rays(180.0 * i / N)
    move_vertex(fd, O, groups, cur, new, rays(180.0 * (i - 0.5) / N))
    cur = new
    S(fd, f"collapse-{i}", f"Collapse into the waterbomb base: sides in, top down ({i}/{N})",
      f"Colapsa en la base de bomba de agua: lados hacia dentro, arriba hacia abajo ({i}/{N})",
      f"Affaissez en base de la bombe à eau : côtés dedans, haut en bas ({i}/{N})",
      f"Colapse na base da bomba de água: lados para dentro, cima para baixo ({i}/{N})", 450)


# ── 2. each face: corners up, sides in, top points tucked into the pockets ────
def face(layer, kind, side):
    q, Q, e = S0 / 4.0, 3.0 * S0 / 4.0, 3.0 * S0 / 8.0
    ml, _ = fold(fd, (h, 0.0), (q, q), kind, seeds=[preimage(fd, layer, (3.0, 1.5))])
    mr, _ = fold(fd, (Q, q), (h, 0.0), kind, seeds=[preimage(fd, layer, (S0 - 3.0, 1.5))])
    S(fd, f"{side}-corners", f"{side.capitalize()}: fold the bottom corners up to the top point",
      f"{'Delante' if side == 'front' else 'Detrás'}: dobla las esquinas de abajo hasta la punta de arriba",
      f"{'Devant' if side == 'front' else 'Derrière'} : rabattez les coins du bas jusqu'à la pointe du haut",
      f"{'Frente' if side == 'front' else 'Trás'}: dobre os cantos de baixo até à ponta de cima")
    sl, sr = preimage(fd, ml, (q + 2.0, q)), preimage(fd, mr, (Q - 2.0, q))
    tl, tr = preimage(fd, ml, (h - 1.0, h - 4.0)), preimage(fd, mr, (h + 1.0, h - 4.0))
    fold(fd, (e, -1.0), (e, S0), kind, seeds=[sl])
    fold(fd, (S0 - e, S0), (S0 - e, -1.0), kind, seeds=[sr])
    S(fd, f"{side}-sides", "Fold the side points in to the centre line",
      "Dobla las puntas laterales hasta la línea central",
      "Rabattez les pointes latérales sur la ligne centrale",
      "Dobre as pontas laterais até à linha central")
    fold(fd, (-1.0, e), (S0 + 1.0, e), kind, seeds=[tl])
    fold(fd, (-1.0, e), (S0 + 1.0, e), kind, seeds=[tr])
    S(fd, f"{side}-tuck", "Fold the two top points down and tuck them into the side pockets",
      "Dobla hacia abajo las dos puntas de arriba y mételas en los bolsillos laterales",
      "Rabattez les deux pointes du haut et glissez-les dans les poches latérales",
      "Dobre para baixo as duas pontas de cima e meta-as nos bolsos laterais")


face(groups[1], "valley", "front")
face(groups[4], "mountain", "back")
b = build_sheet(fd, "square", L4("Square", "Cuadrado", "Carré", "Quadrado"), stock, FRONT, BACK)
f0 = at(fd, (h, 2.0))
present(b, vunit(vsub(world(fd, (h, h - 4.0)), world(fd, (h, 2.0)))), mvec(f0["T"][0], (0.0, 1.0, 0.0)))
entries = [(b, *st) for st in fd["steps"]]
worst, mid = check_closure(b, [x[1] for x in entries])
print(f"kinematics: steps={len(entries)} max_closure_mm={worst:.3e} "
      f"max_linear_midpoint_closure_mm={mid:.3e}")
result = program(entries, [b], "Waterbomb balloon")
