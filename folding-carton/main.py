"""Folding carton — sheet-hyperobjects cartridge (Pliego).

One family: the folding cartons cut from one sheet of paperboard, from inside dimensions.
``style`` selects the closures (one generator, ``pliego.dieline.carton``):

- straight tuck end — tuck lids top and bottom, both on the back panel;
- reverse tuck end — top tuck on the back panel, bottom tuck on the front panel;
- seal end — four flaps at each end, the outer flap glued over the inner one;
- crash-lock (auto) bottom with a tuck top — the minor bottom flaps carry a diagonal crease
  whose glue triangle is glued to the neighbouring major flap;
- 1-2-3 (snap-lock) bottom with a tuck top.

Panels are inside + the board caliper; the fold program is kinematic (a face tree). Optional:
a die-cut window in the front panel, and brand artwork (``assets/brand-mark.svg``, original
placeholder art) placed inside the front panel's safe area (``pliego:artwork``).
"""

import math

import pliego


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


style = str(PARAM(lambda: style, "reverse-tuck"))      # noqa: F821
length = float(PARAM(lambda: length, 80.0))            # noqa: F821
width = float(PARAM(lambda: width, 40.0))              # noqa: F821
depth = float(PARAM(lambda: depth, 120.0))             # noqa: F821
stock = str(PARAM(lambda: stock, "folding-boxboard-300"))   # noqa: F821
window = bool(PARAM(lambda: window, False))            # noqa: F821
branding = bool(PARAM(lambda: branding, True))         # noqa: F821

STOCKS = ("folding-boxboard-300", "sbs-board-350", "cardstock-300", "kraftliner-150")
if stock not in STOCKS:
    raise ValueError(f"folding-carton: stock must be one of {STOCKS}, got {stock!r}")
width = min(width, length)

pack = pliego.dieline.carton(length, width, depth, stock, style=style, window=window)

artwork = []
if branding:
    xs = [p[0] for p in pack.panels["front"].polygon]
    ys = [p[1] for p in pack.panels["front"].polygon]
    safe = pack.block["safe_mm"]
    side = 0.5 * min(max(xs) - min(xs), max(ys) - min(ys))
    cx = (min(xs) + max(xs)) / 2.0
    top = max(ys) - safe - side * 0.25
    artwork.append(pliego.press.artwork(
        "brand-mark", pack.sheet, "assets/brand-mark.svg", (cx - side / 2.0, top - side),
        (side, side), side="front", panel="front", clip="panel"))

# ── glue that takes hold at its step (spec §5.19) ─────────────────────────────────────────────

def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


INSET = 0.75                     # mm: weld region inset from the glue zone's outline


def _side(p, a, b):
    return (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])


def _crosses(poly, a, b):
    """Does segment a–b reach into the convex polygon `poly`?"""
    n = len(poly)
    for i in range(n):
        p, q = poly[i], poly[(i + 1) % n]
        if (_side(p, a, b) * _side(q, a, b) < 0) and (_side(a, p, q) * _side(b, p, q) < 0):
            return True
    return False


def _clip(poly, a, b, off):
    """Keep the part of `poly` left of a→b, moved `off` further left."""
    L = math.hypot(b[0] - a[0], b[1] - a[1])
    nx, ny = -(b[1] - a[1]) / L, (b[0] - a[0]) / L
    a2 = (a[0] + nx * off, a[1] + ny * off)
    b2 = (b[0] + nx * off, b[1] + ny * off)
    out = []
    for i in range(len(poly)):
        p, q = poly[i], poly[(i + 1) % len(poly)]
        sp, sq = _side(p, a2, b2), _side(q, a2, b2)
        if sp >= 0:
            out.append(p)
        if sp * sq < 0:
            t = sp / (sp - sq)
            out.append((p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])))
    return out


def closed_glue(assembly, block, frame="target:closed"):
    """Weld maps for a dieline's glue zones, read from the closed pose: for each zone, the face
    it lands on there and the sheet-local map onto it. Returns {zone id: (region, map, side, k)}:
    the zone inset by `INSET` (its image stays clear of the zone's edges), the weld map, the face
    of the zone the tab lies on, and k, the last program step that folds a crease on the
    face-tree path from tab to zone (the glue takes hold after it). A zone that lands on no face
    is left out."""
    d = assembly.build().data
    pose = next(f for f in d["file_frames"] if f.get("frame_title") == frame)["vertices_coords"]
    si = [s["id"] for s in d["pliego:sheets"]].index(block["sheet"])
    off = d["pliego:sheets"][si]["offset"]
    lay = [(x - off[0], y - off[1]) for x, y in d["vertices_coords"]]
    faces = [f for f, s in zip(d["faces_vertices"], d["pliego:faces_sheet"], strict=True)
             if s == si]

    def basis(f):        # the face's widest corner: 2-D and 3-D frames of the same three points
        best, area = None, 0.0
        for k in range(1, len(f) - 1):
            e1 = (lay[f[k]][0] - lay[f[0]][0], lay[f[k]][1] - lay[f[0]][1])
            for j in range(k + 1, len(f)):
                e2 = (lay[f[j]][0] - lay[f[0]][0], lay[f[j]][1] - lay[f[0]][1])
                a = e1[0] * e2[1] - e1[1] * e2[0]
                if abs(a) > area:
                    best, area = (f[0], f[k], f[j], a), abs(a)
        o, i, j, a = best
        E1 = tuple(pose[i][c] - pose[o][c] for c in range(3))
        E2 = tuple(pose[j][c] - pose[o][c] for c in range(3))
        n = _cross(E1, E2)
        s = math.sqrt(_dot(n, n)) * (1.0 if a > 0 else -1.0)
        return o, i, j, a, E1, E2, (n[0] / s, n[1] / s, n[2] / s)

    def to3(f, p):
        o, i, j, a, E1, E2, _ = basis(f)
        e1 = (lay[i][0] - lay[o][0], lay[i][1] - lay[o][1])
        e2 = (lay[j][0] - lay[o][0], lay[j][1] - lay[o][1])
        px, py = p[0] - lay[o][0], p[1] - lay[o][1]
        s, t = (px * e2[1] - py * e2[0]) / a, (e1[0] * py - e1[1] * px) / a
        return tuple(pose[o][c] + s * E1[c] + t * E2[c] for c in range(3))

    def to2(f, P):
        o, i, j, a, E1, E2, n = basis(f)
        r = tuple(P[c] - pose[o][c] for c in range(3))
        g11, g12, g22 = _dot(E1, E1), _dot(E1, E2), _dot(E2, E2)
        b1, b2 = _dot(r, E1), _dot(r, E2)
        det = g11 * g22 - g12 * g12
        s, t = (b1 * g22 - b2 * g12) / det, (g11 * b2 - g12 * b1) / det
        e1 = (lay[i][0] - lay[o][0], lay[i][1] - lay[o][1])
        e2 = (lay[j][0] - lay[o][0], lay[j][1] - lay[o][1])
        return ((lay[o][0] + s * e1[0] + t * e2[0], lay[o][1] + s * e1[1] + t * e2[1]),
                _dot(r, n))

    def inside(p, f):
        hit = False
        for k in range(len(f)):
            (x0, y0), (x1, y1) = lay[f[k]], lay[f[(k + 1) % len(f)]]
            if (y0 > p[1]) != (y1 > p[1]) and p[0] < x0 + (p[1] - y0) * (x1 - x0) / (y1 - y0):
                hit = not hit
        return hit

    def centre(pts):
        return (sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts))

    out = {}
    for z in block["glue"]:
        c = centre(z["polygon"])
        fa = next(f for f in faces if inside(c, f))
        C3 = to3(fa, c)
        hits = []
        for fb in faces:
            if fb is not fa:
                q, h = to2(fb, C3)
                if abs(h) < 1.0 and inside(q, fb):
                    hits.append((abs(h), fb))
        if not hits:
            continue
        fb = min(hits, key=lambda x: x[0])[1]
        q0 = to2(fb, to3(fa, (0.0, 0.0)))[0]
        q1 = to2(fb, to3(fa, (1.0, 0.0)))[0]
        q2 = to2(fb, to3(fa, (0.0, 1.0)))[0]
        m = (q1[0] - q0[0], q2[0] - q0[0], q1[1] - q0[1], q2[1] - q0[1], q0[0], q0[1])
        # the tab comes from the side of fb where its hinge neighbour stands
        nb = [f for f in faces if f is not fa and len(set(f) & set(fa)) >= 2]
        lean = [_dot(tuple(to3(f, centre([lay[v] for v in f]))[k] - C3[k] for k in range(3)),
                     basis(fb)[6]) for f in nb]
        side = "front" if max(lean, key=abs, default=1.0) > 0 else "back"
        # the creases on the face-tree path from the tab to its zone close the loop; the glue
        # takes hold after the last step that folds one of them
        fold = {frozenset(uv): e for e, uv in enumerate(d["edges_vertices"])
                if d["edges_assignment"][e] not in ("B", "C")}
        prev, todo = {id(fa): None}, [fa]
        while todo and id(fb) not in prev:
            f = todo.pop(0)
            for g in faces:
                if id(g) in prev:
                    continue
                for e in ({frozenset((f[i], f[(i + 1) % len(f)])) for i in range(len(f))}
                          & {frozenset((g[i], g[(i + 1) % len(g)])) for i in range(len(g))}):
                    if e in fold:
                        prev[id(g)] = (f, fold[e])
                        todo.append(g)
                        break
        path, f = set(), fb
        while prev.get(id(f)):
            f, e = prev[id(f)]
            path.add(e)
        k = max((i for i, st in enumerate(d["pliego:sequence"]["steps"])
                 if any(t[0] in path for t in st["targets"])), default=-1)
        ring = [pliego.Vec2(*p) for p in z["polygon"]]
        if pliego.polygon_area(ring) < 0:
            ring = ring[::-1]
        region = [(p.x, p.y) for p in pliego.offset_ring(ring, [-INSET] * len(ring))]
        # keep the weld's image on the card: clip it inside every outline edge of the zone's
        # sheet that it crosses (a window cut too close to the joint)
        img = [(m[0] * x + m[1] * y + m[4], m[2] * x + m[3] * y + m[5]) for x, y in region]
        for f in faces:
            for i in range(len(f)):
                a, b = f[i], f[(i + 1) % len(f)]
                if frozenset((a, b)) not in fold and _crosses(img, lay[a], lay[b]):
                    img = _clip(img, lay[a], lay[b], INSET)
        det = m[0] * m[3] - m[1] * m[2]
        region = [((m[3] * (x - m[4]) - m[1] * (y - m[5])) / det,
                   (m[0] * (y - m[5]) - m[2] * (x - m[4])) / det) for x, y in img]
        out[z["id"]] = (region, tuple(round(x, 9) for x in m), side, k)
    return out


result = pliego.dieline.assemble(
    [pack], title=f"Folding carton ({style})", artwork=artwork,
    label={"en": "Fold program", "es": "Secuencia de armado", "fr": "Séquence de montage",
           "pt": "Sequência de montagem"},
    meta={"cartridge": "folding-carton",
          "params": {"style": style, "length": length, "width": width, "depth": depth,
                     "stock": stock, "window": window, "branding": branding}})

# glue joins that take hold at their step (spec §5.19): the program starts flat and ends glued
steps = result.sequence.steps
welds = closed_glue(result, pack.block)
if any(k == len(steps) - 1 for _, _, _, k in welds.values()):
    steps.append(pliego.Step("press", {
        "en": "Press the glued flaps until the glue holds",
        "es": "Presiona las solapas pegadas hasta que el pegamento agarre",
        "fr": "Presser les rabats collés jusqu'à ce que la colle prenne",
        "pt": "Pressione as abas coladas até a cola pegar"}, [], duration_ms=600))
for z in pack.block["glue"]:
    if z["id"] not in welds:
        continue
    region, weld_map, side, k = welds[z["id"]]
    j = pliego.glue(z["id"], pack.sheet, region, pack.sheet, weld_map, side)
    j["active_from"] = steps[k + 1].id
    result.joins.append(j)
print(f"folding-carton: style={style} glue={len(result.joins)} "
      + " ".join(f"{j['id']}@{j['active_from']}" for j in result.joins)
      + (f" flat-glued={[z['id'] for z in pack.block['glue'] if z['id'] not in welds]}"
         if len(welds) < len(pack.block["glue"]) else ""))
