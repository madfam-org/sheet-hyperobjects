"""Paper house — sheet-hyperobjects cartridge (Pliego).

An original cut-out house model, chosen by `design`: a cottage with a gable roof and a chimney,
a narrow townhouse with its gable to the street, a barn with a gambrel roof and double doors,
and a house with a hip roof. Each is built here as a polygon mesh (walls, roof planes and a
chimney straddling the ridge, one closed surface with an open bottom) at a real-world size in
metres, scaled to the model scale, and unfolded by the kernel (`pliego.unfold.net`) into tabbed,
numbered pieces on A4 or Letter pages. Windows and doors are then drawn onto the pieces: cut out
(the doors hinge open), scored only, or left off.

How the mesh is built (metres; x along the ridge, y up, z toward the front):
- the end-wall profile (z, y) runs from the front eave over the roof to the back eave: a
  triangle for a gable, two slopes a side for a gambrel; the walls, the roof planes and the end
  walls are that profile carried along x. A hip roof instead has a short ridge, with a trapezoid
  roof plane front and back and a triangle at each end;
- the chimney is a box straddling the ridge: the two roof planes beside the ridge are notched
  around its footprint, and its two side walls come down to a peak on the ridge, so roof and
  chimney are one surface with no hole and no overlap;
- the bottom is open (the walls' bottom edges are plain cut edges), so the doors reach the
  ground and the model sits flat on a base board;
- faces are oriented consistently by a walk across shared edges, outward by the volume's sign.
"""

import math

import pliego


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


design = str(PARAM(lambda: design, "cottage"))                      # noqa: F821
scale = str(PARAM(lambda: scale, "87"))                             # noqa: F821
openings = str(PARAM(lambda: openings, "cut"))                      # noqa: F821
chimney = bool(PARAM(lambda: chimney, True))                        # noqa: F821
page = str(PARAM(lambda: page, "a4"))                               # noqa: F821
method = str(PARAM(lambda: method, "min-perimeter"))                # noqa: F821
tab_style = str(PARAM(lambda: tab_style, "trapezoid"))              # noqa: F821
tab_height = float(PARAM(lambda: tab_height, 5.0))                  # noqa: F821
stock = str(PARAM(lambda: stock, "cardstock-250"))                  # noqa: F821
mode = str(PARAM(lambda: mode, "fold"))                             # noqa: F821

M = pliego.mesh
STOCKS = ("cardstock-160", "cardstock-250", "cardstock-300")
MIN_FEATURE = {"cardstock-160": 1.5, "cardstock-250": 2.0, "cardstock-300": 2.0}
SCALES = {"100": 100.0, "87": 87.0, "50": 50.0}
if scale not in SCALES:
    raise ValueError(f"paper-house: scale must be one of {sorted(SCALES)}, got {scale!r}")
if openings not in ("cut", "scored", "none"):
    raise ValueError(f"paper-house: openings must be cut, scored or none, got {openings!r}")
if stock not in STOCKS:
    raise ValueError(f"paper-house: stock must be one of {STOCKS}, got {stock!r}")
if mode not in ("fold", "glued"):
    raise ValueError(f"paper-house: mode must be fold or glued, got {mode!r}")
tab_height = pliego.clamp(tab_height, 3.0, 6.0)
MM = 1000.0 / SCALES[scale]          # millimetres of card per metre of house
DOOR_OPEN_DEG = 70.0

# ── the designs (metres) ─────────────────────────────────────────────────────
# Openings: (wall, kind, u, v, width, height); u runs left to right along the wall seen from
# outside, v up from the ground. Walls: front (z+), back (z−), right (x+), left (x−).
# Kinds: window, door (hinged on its left), door-r (hinged on its right), double (two leaves).
DESIGNS = {
    "cottage": {
        "roof": "gable", "w": 8.0, "d": 5.5, "h": 2.7, "pitch": 45.0,
        "chimney": (2.2, 0.8, 0.8, 1.1), "colour": "#e9c46a",
        "openings": [
            ("front", "door", 2.4, 0.0, 1.0, 2.0), ("front", "window", 0.9, 0.9, 1.0, 1.1),
            ("front", "window", 4.6, 0.9, 1.1, 1.1), ("front", "window", 6.1, 0.9, 1.0, 1.1),
            ("back", "window", 1.3, 0.9, 1.1, 1.1), ("back", "window", 5.6, 0.9, 1.1, 1.1),
            ("right", "window", 2.2, 0.9, 1.1, 1.1), ("right", "window", 2.35, 3.2, 0.8, 0.7),
            ("left", "window", 2.2, 0.9, 1.1, 1.1), ("left", "window", 2.35, 3.2, 0.8, 0.7),
        ],
    },
    "townhouse": {
        "roof": "gable", "w": 9.0, "d": 5.0, "h": 8.4, "pitch": 55.0,
        "chimney": (-2.4, 0.7, 0.8, 1.0), "colour": "#d08c60",
        "openings": [("right", "door-r", 3.0, 0.0, 1.2, 2.3),
                     ("right", "window", 0.9, 0.9, 1.2, 1.4)]
        + [("right", "window", u, v, 1.2, 1.5) for v in (3.5, 6.2) for u in (0.9, 2.9)]
        + [("right", "window", 2.0, 8.9, 1.0, 1.0)]
        + [("left", "window", u, v, 1.2, 1.4) for v in (0.9, 3.5, 6.2) for u in (0.9, 2.9)],
    },
    "barn": {
        "roof": "gambrel", "w": 11.0, "d": 8.0, "h": 3.4, "pitch": 62.0, "upper_pitch": 26.0,
        "knee": 0.62, "chimney": None, "colour": "#a4161a",
        "openings": [
            ("right", "double", 2.3, 0.0, 3.4, 3.0), ("right", "window", 3.2, 4.8, 1.6, 1.4),
            ("left", "door", 3.4, 0.0, 1.2, 2.2),
        ] + [(w, "window", u, 1.4, 1.2, 1.0) for w in ("front", "back") for u in (1.3, 4.9, 8.5)],
    },
    "hip-house": {
        "roof": "hip", "w": 10.0, "d": 7.0, "h": 3.0, "pitch": 30.0,
        "chimney": (0.0, 0.8, 0.8, 1.2), "colour": "#90be6d",
        "openings": [
            ("front", "door", 4.5, 0.0, 1.0, 2.1), ("front", "window", 1.2, 0.9, 1.4, 1.3),
            ("front", "window", 7.4, 0.9, 1.4, 1.3), ("back", "window", 1.6, 0.9, 1.3, 1.3),
            ("back", "window", 4.4, 0.9, 1.3, 1.3), ("back", "window", 7.1, 0.9, 1.3, 1.3),
            ("right", "window", 2.8, 0.9, 1.4, 1.3), ("left", "window", 2.8, 0.9, 1.4, 1.3),
        ],
    },
}
if design not in DESIGNS:
    raise ValueError(f"paper-house: design must be one of {sorted(DESIGNS)}, got {design!r}")
D = DESIGNS[design]
W, DEP, H = D["w"], D["d"], D["h"]

# ── the mesh ────────────────────────────────────────────────────────────────

verts, index = [], {}


def V(x, y, z):
    key = (round(x, 9), round(y, 9), round(z, 9))
    if key not in index:
        index[key] = len(verts)
        verts.append((x, y, z))
    return index[key]


def profile():
    """End-wall outline (z, y) from the front ground corner over the roof to the back one."""
    rise = DEP / 2.0 * math.tan(math.radians(D["pitch"]))
    if D["roof"] == "gambrel":
        zk = DEP / 2.0 * D["knee"]
        yk = H + (DEP / 2.0 - zk) * math.tan(math.radians(D["pitch"]))
        ridge = yk + zk * math.tan(math.radians(D["upper_pitch"]))
        return [(DEP / 2, 0.0), (DEP / 2, H), (zk, yk), (0.0, ridge), (-zk, yk), (-DEP / 2, H),
                (-DEP / 2, 0.0)]
    return [(DEP / 2, 0.0), (DEP / 2, H), (0.0, H + rise), (-DEP / 2, H), (-DEP / 2, 0.0)]


def ridge_height():
    if D["roof"] == "hip":
        return H + DEP / 2.0 * math.tan(math.radians(D["pitch"]))
    return max(y for _z, y in profile())


faces, named = [], {}
R = ridge_height()
if D["roof"] == "hip":
    r = W / 2.0 - DEP / 2.0                       # equal pitch on all four sides
    x0, x1, z0, z1 = -W / 2, W / 2, -DEP / 2, DEP / 2
    named["front"] = len(faces)
    faces.append([V(x0, 0, z1), V(x1, 0, z1), V(x1, H, z1), V(x0, H, z1)])
    named["back"] = len(faces)
    faces.append([V(x1, 0, z0), V(x0, 0, z0), V(x0, H, z0), V(x1, H, z0)])
    named["right"] = len(faces)
    faces.append([V(x1, 0, z1), V(x1, 0, z0), V(x1, H, z0), V(x1, H, z1)])
    named["left"] = len(faces)
    faces.append([V(x0, 0, z0), V(x0, 0, z1), V(x0, H, z1), V(x0, H, z0)])
    faces.append([V(x0, H, z1), V(x1, H, z1), V(r, R, 0), V(-r, R, 0)])
    faces.append([V(x1, H, z0), V(x0, H, z0), V(-r, R, 0), V(r, R, 0)])
    faces.append([V(x1, H, z1), V(x1, H, z0), V(r, R, 0)])
    faces.append([V(x0, H, z0), V(x0, H, z1), V(-r, R, 0)])
    ridge_x = (-r, r)
else:
    prof = profile()
    named["right"] = len(faces)
    faces.append([V(W / 2, y, z) for z, y in reversed(prof)])
    named["left"] = len(faces)
    faces.append([V(-W / 2, y, z) for z, y in prof])
    for k in range(len(prof) - 1):
        (za, ya), (zb, yb) = prof[k], prof[k + 1]
        if k == 0:
            named["front"] = len(faces)
        if k == len(prof) - 2:
            named["back"] = len(faces)
        faces.append([V(-W / 2, ya, za), V(-W / 2, yb, zb), V(W / 2, yb, zb), V(W / 2, ya, za)])
    ridge_x = (-W / 2, W / 2)

if chimney and D["chimney"] is not None:
    cx, cw, cd, ch = D["chimney"]
    c0, c1, hz = cx - cw / 2, cx + cw / 2, cd / 2
    if not ridge_x[0] + 0.3 < c0 < c1 < ridge_x[1] - 0.3:
        raise ValueError("paper-house: the chimney must sit on the ridge, clear of its ends")

    def roof_y(z):
        """Height of the ridge-side roof planes at |z| (they meet at the ridge, z = 0)."""
        for f in faces:
            pts = [verts[i] for i in f]
            if sum(1 for p in pts if abs(p[1] - R) < 1e-9 and abs(p[2]) < 1e-9) == 2:
                lo = [p for p in pts if abs(p[1] - R) > 1e-9][0]
                return R - (R - lo[1]) * abs(z) / abs(lo[2])
        raise ValueError("paper-house: no roof plane meets the ridge")

    yq, top = roof_y(hz), R + ch
    for fi, f in enumerate(faces):
        on_ridge = [k for k, i in enumerate(f) if abs(verts[i][1] - R) < 1e-9
                    and abs(verts[i][2]) < 1e-9]
        if len(on_ridge) != 2:
            continue
        side = 1.0 if sum(verts[i][2] for i in f) > 0 else -1.0
        k = on_ridge[0] if (on_ridge[0] + 1) % len(f) == on_ridge[1] else on_ridge[1]
        going_down = verts[f[k]][0] > verts[f[(k + 1) % len(f)]][0]
        notch = [V(c1, R, 0), V(c1, yq, side * hz), V(c0, yq, side * hz), V(c0, R, 0)]
        faces[fi] = f[:k + 1] + (notch if going_down else notch[::-1]) + f[k + 1:]
    for s in (1.0, -1.0):
        faces.append([V(c0, yq, s * hz), V(c1, yq, s * hz), V(c1, top, s * hz),
                      V(c0, top, s * hz)])
    for x in (c0, c1):
        faces.append([V(x, yq, -hz), V(x, R, 0), V(x, yq, hz), V(x, top, hz), V(x, top, -hz)])
    faces.append([V(c0, top, -hz), V(c1, top, -hz), V(c1, top, hz), V(c0, top, hz)])


def oriented(fs):
    """Faces turned so neighbours run opposite ways across shared edges, then outward."""
    owner = {}
    for fi, f in enumerate(fs):
        for k in range(len(f)):
            owner.setdefault((min(f[k], f[k - 1]), max(f[k], f[k - 1])), []).append(fi)
    out, done, todo = [list(f) for f in fs], {0}, [0]
    while todo:
        fi = todo.pop()
        f = out[fi]
        directed = {(f[k - 1], f[k]) for k in range(len(f))}
        for k in range(len(f)):
            for g in owner[(min(f[k], f[k - 1]), max(f[k], f[k - 1]))]:
                if g in done:
                    continue
                gd = {(out[g][j - 1], out[g][j]) for j in range(len(out[g]))}
                if gd & directed:
                    out[g].reverse()
                done.add(g)
                todo.append(g)
    m = M.Mesh(verts, out)
    # Volume about the origin, which lies in the open floor's plane: the missing floor adds 0.
    if m.signed_volume() < 0:
        m = M.Mesh(verts, [list(reversed(f)) for f in out])
    return m.check()


house = oriented(faces).scaled(MM)
lo, hi = house.bounds()
extent = max(hi[i] - lo[i] for i in range(3))
net = pliego.unfold.net(house, size=extent, page=page, method=method, tabs=tab_style,
                        tab_height=tab_height)
result = net.assembly(mode, stock=stock, front=D["colour"], title=f"Paper house: {design}")

# ── windows and doors on the pieces ─────────────────────────────────────────


def wall_point(wall, u, v):
    if wall == "front":
        return (-W / 2 + u, v, DEP / 2)
    if wall == "back":
        return (W / 2 - u, v, -DEP / 2)
    if wall == "right":
        return (W / 2, v, DEP / 2 - u)
    return (-W / 2, v, -DEP / 2 + u)


def frame(f):
    """Face f's own 2-D frame, as `pliego.unfold.face_frame` builds it."""
    pts = net.mesh.face_points(f)
    n = M.newell(pts)
    ln = math.sqrt(sum(c * c for c in n))
    n = (n[0] / ln, n[1] / ln, n[2] / ln)
    e = [pts[1][i] - pts[0][i] for i in range(3)]
    le = math.sqrt(sum(c * c for c in e))
    e1 = (e[0] / le, e[1] / le, e[2] / le)
    e2 = (n[1] * e1[2] - n[2] * e1[1], n[2] * e1[0] - n[0] * e1[2], n[0] * e1[1] - n[1] * e1[0])

    def local(p):
        d = [p[i] - pts[0][i] for i in range(3)]
        return (sum(d[i] * e1[i] for i in range(3)), sum(d[i] * e2[i] for i in range(3)))
    return local


def rigid(qa, qb, pa, pb):
    ang = (math.atan2(pb[1] - pa[1], pb[0] - pa[0]) - math.atan2(qb[1] - qa[1], qb[0] - qa[0]))
    c, s = math.cos(ang), math.sin(ang)
    return (c, s, pa[0] - (c * qa[0] - s * qa[1]), pa[1] - (s * qa[0] + c * qa[1]))


def apply(t, p):
    return (t[0] * p[0] - t[1] * p[1] + t[2], t[1] * p[0] + t[0] * p[1] + t[3])


def to_sheet(f):
    """Model point (mm) on face f → (sheet, sheet-local point function)."""
    isl = next(i for i in net.islands if f in i.pos)
    local = frame(f)
    loc = [local(p) for p in net.mesh.face_points(f)]
    t = rigid(loc[0], loc[1], isl.pos[f][0], isl.pos[f][1])
    for a, b in zip(loc, isl.pos[f], strict=True):
        q = apply(t, a)
        if math.dist(q, b) > 1e-6:
            raise ValueError("paper-house: the face map does not match the net")
    return result.sheets[isl.index], lambda p: apply(isl.sheet_map, apply(t, local(p))), loc


def clearance(f, loc, pts, skip_ground):
    """Least distance from points to face f's edges (mm); the ground edge may be skipped."""
    p3 = net.mesh.face_points(f)
    best = math.inf
    for k in range(len(loc)):
        if skip_ground and abs(p3[k - 1][1]) < 1e-6 and abs(p3[k][1]) < 1e-6:
            continue
        a, b = loc[k - 1], loc[k]
        ab = (b[0] - a[0], b[1] - a[1])
        for p in pts:
            t = max(0.0, min(1.0, ((p[0] - a[0]) * ab[0] + (p[1] - a[1]) * ab[1])
                             / (ab[0] ** 2 + ab[1] ** 2)))
            best = min(best, math.dist(p, (a[0] + t * ab[0], a[1] + t * ab[1])))
    return best


doors, holes, clear_min = [], 0, math.inf
# The kernel bridges each window (a hole inside a face) to the face's boundary with J edges.
# A bridge laid almost along another window's edge (windows in one row or column, on a piece
# turned by the page layout) can come out as a sliver face that is not simple. Every opening on
# a wall is therefore shifted by its own multiple of 0.1 mm (on the card), right and down, so
# no two openings share an edge line; under 1 mm in all, invisible at these scales.
NUDGE_MM = 0.1
count = {}
for wall, kind, u, v, w, h in (D["openings"] if openings != "none" else []):
    k = count[wall] = count.get(wall, -1) + 1
    u += k * NUDGE_MM / MM
    v -= 0.0 if kind != "window" else k * NUDGE_MM / MM
    f = named[wall]
    sheet, put, loc = to_sheet(f)
    corners3 = [tuple(c * MM for c in wall_point(wall, uu, vv))
                for uu, vv in ((u, v), (u + w, v), (u + w, v + h), (u, v + h))]
    local = frame(f)
    need = tab_height + 1.0
    gap = clearance(f, loc, [local(p) for p in corners3], kind != "window")
    clear_min = min(clear_min, gap)
    if gap < need - 1e-6:
        raise ValueError(f"paper-house: a {kind} on the {wall} wall comes {gap:.1f} mm from an "
                         f"edge, closer than the {need:.1f} mm the glue tabs need; use a "
                         "larger scale or lower tabs")
    bl, br, tr, tl = (put(p) for p in corners3)
    if openings == "scored":
        sheet.halfcut([bl, br, tr, tl, bl] if kind == "window" else [bl, tl, tr, br])
        continue
    if kind == "window":
        sheet.hole([bl, br, tr, tl])
        holes += 1
        continue
    hinge = {"door": [(bl, tl)], "door-r": [(br, tr)]}.get(kind, [(bl, tl), (br, tr)])
    if kind == "door":
        sheet.cut([br, tr, tl])
    elif kind == "door-r":
        sheet.cut([bl, tl, tr])
    else:
        mid_b = ((bl[0] + br[0]) / 2, (bl[1] + br[1]) / 2)
        mid_t = ((tl[0] + tr[0]) / 2, (tl[1] + tr[1]) / 2)
        sheet.cut([tl, tr])
        sheet.cut([mid_b, mid_t])
    for a, b in hinge:
        doors.append(sheet.crease(a, b, "mountain", DOOR_OPEN_DEG, "score"))

OPEN = ({"en": "Open the door", "es": "Abre la puerta", "fr": "Ouvrez la porte",
         "pt": "Abra a porta"} if len(doors) == 1 else
        {"en": "Open the doors", "es": "Abre las puertas", "fr": "Ouvrez les portes",
         "pt": "Abra as portas"})
OPEN_NOTE = {"en": "Doors are cut on three sides and hinge on a scored fold; they open inward.",
             "es": "Las puertas van cortadas por tres lados y giran sobre un doblez marcado; "
                   "abren hacia dentro.",
             "fr": "Les portes sont découpées sur trois côtés et pivotent sur un pli rainé ; "
                   "elles s'ouvrent vers l'intérieur.",
             "pt": "As portas são cortadas em três lados e giram numa dobra vincada; abrem para "
                   "dentro."}
if mode == "fold" and doors:
    steps = list(result.sequence.steps)
    steps.append(pliego.Step("open-doors", OPEN, [(m, None) for m in doors], duration_ms=1500,
                             note=OPEN_NOTE))
    result.sequence = pliego.Sequence(steps, mode="kinematic")

# ── papercut check: every piece whole, no bridge thinner than the card allows ───────────────
bridges = []
for sheet in result.sheets:
    rep = pliego.papercut.analyze(sheet, min_feature_mm=MIN_FEATURE[stock])
    if rep.components != 1:
        raise ValueError(f"paper-house: {sheet.id} falls apart into {rep.components} parts")
    thin = [i for i in rep.issues if i["kind"] == "bridge_too_thin"]
    if thin:
        raise ValueError(f"paper-house: {sheet.id}: {thin[0]['detail']}")
    if rep.min_bridge_mm is not None:
        bridges.append(rep.min_bridge_mm)
print(f"paper-house: {design} at 1:{scale}, {len(net.mesh.faces)} faces, openings={openings} "
      f"holes={holes} doors={len(doors)} clearance={clear_min:.1f}mm")
print(net.summary())
print(f"papercut: pieces={len(result.sheets)} min_bridge="
      f"{round(min(bridges), 2) if bridges else 'none'} min_feature={MIN_FEATURE[stock]}")
