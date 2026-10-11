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
INSET = 0.75                     # mm: weld region inset from the glue zone's outline
PRESS = {"en": "Press the glued flaps until the glue holds",
         "es": "Presiona las solapas pegadas hasta que el pegamento agarre",
         "fr": "Presser les rabats collés jusqu'à ce que la colle prenne",
         "pt": "Pressione as abas coladas até a cola pegar"}


def _dot(a, b):
    return sum(x * y for x, y in zip(a, b, strict=True))


def _side(p, a, b):
    return (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])


def _clip(poly, a, b, off):
    """The part of the convex `poly` left of a→b moved `off` further left."""
    n_ = math.hypot(b[0] - a[0], b[1] - a[1])
    sh = (-(b[1] - a[1]) / n_ * off, (b[0] - a[0]) / n_ * off)
    a, b = (a[0] + sh[0], a[1] + sh[1]), (b[0] + sh[0], b[1] + sh[1])
    out = []
    for p, q in zip(poly, poly[1:] + poly[:1], strict=True):
        sp, sq = _side(p, a, b), _side(q, a, b)
        if sp >= 0:
            out.append(p)
        if sp * sq < 0:
            t = sp / (sp - sq)
            out.append((p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])))
    return out


def closed_glue(assembly, sheet_id, zones, frame="target:closed", after=None, sides=None):
    """Welds for glue zones ({id, polygon} on sheet `sheet_id`), read from a closed pose: {zone id:
    (region, map, side, k)} — the zone inset by INSET and clipped clear of cut edges, the map
    onto the face it lands on, the side of that face the tab lies on, and k, the last step that
    folds a crease on the face-tree path from tab to zone (`after` and `sides` override k and the
    side by zone id, for a flap that wraps round its zone's edge). Zones that land
    on no face are left out (fabrication data only)."""
    d = assembly.build().data
    X = next(f for f in d["file_frames"] if f.get("frame_title") == frame)
    X = X["vertices_coords"]
    si = [s["id"] for s in d["pliego:sheets"]].index(sheet_id)
    off = d["pliego:sheets"][si]["offset"]
    lay = [(x - off[0], y - off[1]) for x, y in d["vertices_coords"]]
    faces = [f for f, s in zip(d["faces_vertices"], d["pliego:faces_sheet"], strict=True)
             if s == si]
    rims = [{frozenset((f[i], f[i - 1])) for i in range(len(f))} for f in faces]
    fold = {frozenset(uv): e for e, uv in enumerate(d["edges_vertices"])
            if d["edges_assignment"][e] not in ("B", "C")}
    steps = d["pliego:sequence"]["steps"]

    def frame(f):        # the face's widest corner, in the layout and in the closed pose
        o, i, j = max(((f[0], f[k], f[m]) for k in range(1, len(f))
                       for m in range(k + 1, len(f))),
                      key=lambda t: abs(_side(lay[t[2]], lay[t[0]], lay[t[1]])))
        a = _side(lay[j], lay[o], lay[i])
        e1, e2 = [(lay[v][0] - lay[o][0], lay[v][1] - lay[o][1]) for v in (i, j)]
        E1, E2 = [[X[v][c] - X[o][c] for c in range(3)] for v in (i, j)]
        n = [E1[1] * E2[2] - E1[2] * E2[1], E1[2] * E2[0] - E1[0] * E2[2],
             E1[0] * E2[1] - E1[1] * E2[0]]
        s = math.sqrt(_dot(n, n)) * (1.0 if a > 0 else -1.0)
        return o, a, e1, e2, E1, E2, [c / s for c in n]

    def to3(f, p):
        o, a, e1, e2, E1, E2, _ = frame(f)
        px, py = p[0] - lay[o][0], p[1] - lay[o][1]
        s, t = (px * e2[1] - py * e2[0]) / a, (e1[0] * py - e1[1] * px) / a
        return [X[o][c] + s * E1[c] + t * E2[c] for c in range(3)]

    def to2(f, P):       # (layout point, height above the face's front)
        o, a, e1, e2, E1, E2, n = frame(f)
        r = [P[c] - X[o][c] for c in range(3)]
        g11, g12, g22, b1, b2 = _dot(E1, E1), _dot(E1, E2), _dot(E2, E2), _dot(r, E1), _dot(r, E2)
        det = g11 * g22 - g12 ** 2
        s, t = (b1 * g22 - b2 * g12) / det, (g11 * b2 - g12 * b1) / det
        return (lay[o][0] + s * e1[0] + t * e2[0], lay[o][1] + s * e1[1] + t * e2[1]), _dot(r, n)

    def inside(p, f):
        return sum(1 for a, b in zip(f, f[1:] + f[:1], strict=True)
                   if (lay[a][1] > p[1]) != (lay[b][1] > p[1]) and p[0] < lay[a][0] + (
                       p[1] - lay[a][1]) * (lay[b][0] - lay[a][0]) / (lay[b][1] - lay[a][1])) % 2

    def centre(pts):
        return (sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts))

    out = {}
    for z in zones:
        c = centre(z["polygon"])
        ia = next(i for i, f in enumerate(faces) if inside(c, f))
        C3 = to3(faces[ia], c)
        hits = [(abs(h), i) for i, f in enumerate(faces) if i != ia
                for q, h in [to2(f, C3)] if abs(h) < 1.0 and inside(q, f)]
        if not hits:
            continue
        ib = min(hits)[1]
        off = to2(faces[ib], C3)[1]            # the tab's height over the zone's front
        q0, q1, q2 = [to2(faces[ib], to3(faces[ia], p))[0] for p in ((0, 0), (1, 0), (0, 1))]
        m = [q1[0] - q0[0], q2[0] - q0[0], q1[1] - q0[1], q2[1] - q0[1], q0[0], q0[1]]
        # the side: where the tab lies off the zone's plane, else where its hinge neighbour stands
        lean = [to2(faces[ib], to3(f, centre([lay[v] for v in f])))[1]
                for i, f in enumerate(faces) if i != ia and rims[i] & rims[ia]]
        side = "front" if (off if abs(off) > 0.5 else max(lean, key=abs, default=1.0)) > 0 \
            else "back"
        side = (sides or {}).get(z["id"], side)
        prev, todo = {ia: None}, [ia]          # the face-tree path closes the loop
        while todo:
            i = todo.pop(0)
            for g in range(len(faces)):
                e = next((fold[x] for x in rims[i] & rims[g] if x in fold), None)
                if g not in prev and e is not None:
                    prev[g], todo = (i, e), todo + [g]
        path, i = set(), ib
        while prev.get(i):
            i, e = prev[i]
            path.add(e)
        k = max((i for i, st in enumerate(steps) if any(t[0] in path for t in st["targets"])),
                default=-1)
        if after and z["id"] in after:
            k = [st["id"] for st in steps].index(after[z["id"]])
        ring = [pliego.Vec2(*p) for p in z["polygon"]]
        ring = ring if pliego.polygon_area(ring) > 0 else ring[::-1]
        img = [(m[0] * p.x + m[1] * p.y + m[4], m[2] * p.x + m[3] * p.y + m[5])
               for p in pliego.offset_ring(ring, [-INSET] * len(ring))]
        for f in faces:                      # keep the image on the card (a window too near)
            for a, b in zip(f, f[1:] + f[:1], strict=True):
                if frozenset((a, b)) not in fold and any(
                        _side(p, lay[a], lay[b]) * _side(q, lay[a], lay[b]) < 0
                        and _side(lay[a], p, q) * _side(lay[b], p, q) < 0
                        for p, q in zip(img, img[1:] + img[:1], strict=True)):
                    img = _clip(img, lay[a], lay[b], INSET)
        det = m[0] * m[3] - m[1] * m[2]
        region = [((m[3] * (x - m[4]) - m[1] * (y - m[5])) / det,
                   (m[0] * (y - m[5]) - m[2] * (x - m[4])) / det) for x, y in img]
        out[z["id"]] = (region, tuple(round(x, 9) for x in m), side, k)
    return out


def glue_at_steps(assembly, groups, frame="target:closed", after=None, sides=None):
    """A glue join for every glue zone of `groups` ([(sheet, zones)]), active from the step after
    the one that closes it (a short final press step when that is the last one). Returns the
    joins made and the zones left as fabrication data."""
    welds = {(sh.id, z): (sh, w) for sh, zones in groups
             for z, w in closed_glue(assembly, sh.id, zones, frame, after, sides).items()}
    steps = assembly.sequence.steps
    if any(w[3] == len(steps) - 1 for _, w in welds.values()):
        steps.append(pliego.Step("press", PRESS, [], duration_ms=600))
    made = [dict(pliego.glue(zid, sh, w[0], sh, w[1], w[2]), active_from=steps[w[3] + 1].id)
            for (_, zid), (sh, w) in welds.items()]
    assembly.joins.extend(made)
    return made, [z["id"] for sh, zones in groups for z in zones if (sh.id, z["id"]) not in welds]


result = pliego.dieline.assemble(
    [pack], title=f"Folding carton ({style})", artwork=artwork,
    label={"en": "Fold program", "es": "Secuencia de armado", "fr": "Séquence de montage",
           "pt": "Sequência de montagem"},
    meta={"cartridge": "folding-carton",
          "params": {"style": style, "length": length, "width": width, "depth": depth,
                     "stock": stock, "window": window, "branding": branding}})

# glue joins that take hold at their step (spec §5.19): the program starts flat and ends glued
made, flat = glue_at_steps(result, [(pack.sheet, pack.block["glue"])])
print(f"folding-carton: style={style} glue=" + " ".join(f"{j['id']}@{j['active_from']}"
                                                         for j in made)
      + (f" flat-glued={flat}" if flat else ""))
