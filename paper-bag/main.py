"""Paper bag — sheet-hyperobjects cartridge (Pliego).

The flat-bottomed paper bag with side gussets (the SOS style), made from one sheet of kraft:

* the sheet is a row of panels: front (`width`), gusset (`gusset`), back (`width`), gusset, and a
  glue flap that closes the tube against the inside of the front; each gusset is scored down its
  centre so the made bag can pleat in;
* below the bottom score the front and back panels continue by an extension `e` =
  `gusset`/2 + `overlap`/2 and each gusset by `gusset`/2: the bottom. Each gusset extension
  carries two 45° creases from the bag's corners to its middle; folding in, it becomes a triangle
  lying flat on the bottom, and its two corners (the ears) fold back over it. The back and front
  extensions fold over the triangles and the ears, overlap by `overlap` mm in the middle and are
  glued, so the ears end tucked between the gusset triangles and the flaps; the sheet is not cut
  at the corners. From inside, each gusset shows as a triangle (the diamond fold).

The fold program is kinematic and every in-between state is an exact rigid state, expanded by
`pliego.Sequence.kinematic_path` from three key poses: the tube folds on its four corners, the
gusset flaps fold in halfway while the front and back flaps rise and the ears fold, then the
bottom is pressed flat (0.4° short of flat, so its layers do not coincide). The bottom corners are
degree-5 vertices with two branches from the singular tube state; `branch()` solves, on one
corner, the branch on which the ear ends between the gusset triangle and the flap, and every
corner is driven along it. The script checks the erected bag: the tube closes on the glue flap,
the flaps lie on the bottom and overlap by `overlap`, the ears lie between the gusset triangles
and the flaps, and every crease closes (`kinematics.closure_residual`).
"""

import math

import pliego
from pliego import kinematics


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


def L4(en, es, fr, pt):
    return {"en": en, "es": es, "fr": fr, "pt": pt}


width = float(PARAM(lambda: width, 180.0))                   # noqa: F821
gusset = float(PARAM(lambda: gusset, 100.0))                 # noqa: F821
height = float(PARAM(lambda: height, 260.0))                 # noqa: F821
overlap = float(PARAM(lambda: overlap, 20.0))                # noqa: F821
stock = str(PARAM(lambda: stock, "kraft-120"))               # noqa: F821

STOCKS = ("kraft-120", "copy-80", "cardstock-160")
if stock not in STOCKS:
    raise ValueError(f"paper-bag: stock must be one of {STOCKS}, got {stock!r}")
w = pliego.clamp(width, 80.0, 320.0)
g = pliego.clamp(gusset, 40.0, 200.0)
h = pliego.clamp(height, 100.0, 460.0)
ov = pliego.clamp(overlap, 8.0, 40.0)
e = g / 2 + ov / 2                    # bottom extension of the front and the back
eg = g / 2                            # bottom extension of the gussets (to the triangles' tips)
SEAM = 15.0                           # glue flap width
DELTA = 1.0                           # the front's extension starts 1 mm in from the seam corner
TOL = 1e-4
if g > w - 2.0:
    raise ValueError(f"paper-bag: a {g:g} mm gusset needs a front at least {g + 2:.0f} mm wide "
                     "(the gusset triangles would meet in the middle of the bottom)")
if ov > g - 4.0:
    raise ValueError(f"paper-bag: the overlap must stay under the gusset minus 4 mm ({g - 4:g})")
if h < g:
    raise ValueError("paper-bag: the bag must be at least as tall as its gusset")

X1, X2, X3, X4 = w, w + g, 2 * w + g, 2 * w + 2 * g      # panel edges along the sheet
ring = [(0.0, 0.0), (DELTA, 0.0), (DELTA, -e), (X1, -e), (X1, -eg), (X2, -eg), (X2, -e),
        (X3, -e), (X3, -eg), (X4, -eg), (X4, 0.0), (X4 + SEAM, 4.0), (X4 + SEAM, h - 4.0),
        (X4, h), (0.0, h)]
bag = pliego.Sheet("bag", ring, stock=stock, grain_deg=90.0,
                   placement=pliego.Placement(origin=(0.0, 0.0, g),
                                              rotation=(math.sqrt(0.5), 0.0, 0.0, math.sqrt(0.5))),
                   label=L4("Bag blank", "Plantilla de la bolsa", "Patron du sac",
                            "Molde do saco"))


def crease(a, b, en, es, fr, pt, kind="mountain", ang=90.0, name=None):
    return bag.crease(a, b, kind, ang, treatment="score", label=L4(en, es, fr, pt), name=name)


corners = [crease((x, 0.0), (x, h), "Corner of the bag", "Esquina de la bolsa", "Arête du sac",
                  "Aresta do saco") for x in (X1, X2, X3)]
seam = crease((X4, 0.0), (X4, h), "Glue flap", "Pestaña de pegado", "Patte de collage",
              "Aba de colagem", ang=89.0, name="seam")
centres = [bag.score((x, 0.0), (x, h), "flat", 0.0, L4("Gusset centre", "Centro del fuelle",
                                                         "Milieu du soufflet", "Centro do fole"),
                     name="gusset-centre") for x in (X1 + g / 2, X3 + g / 2)]
f_bot = crease((DELTA, 0.0), (X1, 0.0), "Front flap", "Solapa delantera", "Rabat avant",
               "Aba da frente", ang=89.8, name="front-flap")
s_bot = [crease((a, 0.0), (b, 0.0), "Gusset flap", "Solapa del fuelle", "Rabat du soufflet",
                "Aba do fole", ang=89.6) for a, b in ((X1, X2), (X3, X4))]
b_bot = crease((X2, 0.0), (X3, 0.0), "Back flap", "Solapa trasera", "Rabat arrière",
               "Aba de trás", ang=89.8, name="back-flap")
ext = [crease((x, -eg), (x, 0.0), "Corner of the bottom", "Esquina del fondo", "Coin du fond",
              "Canto do fundo") for x in (X1, X2, X3)]
ears = [crease((x, 0.0), (x + sgn * eg, -eg), "Ear", "Oreja", "Oreille", "Orelha",
               kind="valley", ang=180.0)
        for x, sgn in ((X1, 1.0), (X2, -1.0), (X3, 1.0), (X4, -1.0))]
bag.label_edge("bottom-overlap", (DELTA, -e), (X1, -e))

def branch(s_deg):
    """Front-flap, corner-line and ear angles on the rigid branch of a bag corner (gusset flap at
    s_deg).

    A bottom corner is a degree-5 vertex: the gusset and the front (90° each), the front flap
    (90°), the ear and the gusset triangle (45° each). With the bag's corner held at 90° it keeps
    2 degrees of freedom, and from the tube state (a singular, straight-folded start) the motion
    solver may take either of two branches. Every corner is driven along the one on which the
    front flap folds in and the ear ends between the gusset triangle and the flap, solved here on
    a single corner (the angles do not depend on the bag's dimensions)."""
    v = pliego.Sheet("corner", [(-60.0, -40.0), (0.0, -40.0), (0.0, -30.0), (30.0, -30.0),
                                (60.0, 0.0), (60.0, 60.0), (-60.0, 60.0)])
    c = v.crease((0, 0), (0, 60), "mountain", 90.0)
    f = v.crease((-60, 0), (0, 0), "mountain", 90.0)
    sg = v.crease((0, 0), (60, 0), "mountain", 90.0)
    x = v.crease((0, -30), (0, 0), "mountain", 90.0)
    r = v.crease((0, 0), (30, -30), "valley", 180.0)
    path = kinematics.solve(v, {c: -90.0, x: -90.0}, {sg: s_deg}, fixed=[c], steps=24,
                            along="chord")
    return {m: path[-1][k.edges()[0]] for m, k in (("flap", f), ("ext", x), ("ear", r))}


S_HALF, S_DOWN = -50.0, -89.6          # gusset flaps: halfway, then 0.4° short of flat
HALF, DOWN = branch(S_HALF), branch(S_DOWN)
F_DOWN = DOWN["flap"]


def bottom_pose(s_deg, b):
    return ([(m, s_deg) for m in s_bot] + [(f_bot, b["flap"]), (b_bot, b["flap"])]
            + [(m, b["ext"]) for m in ext] + [(m, b["ear"]) for m in ears])


TUBE = [(m, -90.0) for m in corners + ext] + [(seam, -89.0)]
steps = [
    pliego.Step("tube", L4("Fold the four corners and glue the flap inside the front: a tube",
                           "Dobla las cuatro esquinas y pega la pestaña por dentro del frente: "
                           "un tubo", "Pliez les quatre arêtes et collez la patte derrière "
                           "l'avant : un tube", "Dobre as quatro arestas e cole a aba por dentro "
                           "da frente: um tubo"), TUBE, duration_ms=2500),
    pliego.Step("gussets-in", L4("Push the gusset flaps in: the front and back flaps rise and "
                                 "their corners fold back into ears",
                                 "Mete las solapas de los fuelles: las solapas delantera y "
                                 "trasera se levantan y sus esquinas se doblan en orejas",
                                 "Rentrez les rabats des soufflets : les rabats avant et arrière "
                                 "se relèvent et leurs coins se replient en oreilles",
                                 "Empurre as abas dos foles para dentro: as abas da frente e de "
                                 "trás sobem e os seus cantos dobram-se em orelhas"),
                bottom_pose(S_HALF, HALF), duration_ms=2500),
    pliego.Step("bottom", L4("Press the bottom flat: gusset flaps under, the front flap over the "
                             "back flap; glue the overlap",
                             "Aplana el fondo: las solapas de los fuelles debajo y la solapa "
                             "delantera sobre la trasera; pega la parte que se superpone",
                             "Aplatissez le fond : rabats des soufflets dessous, rabat avant sur "
                             "le rabat arrière ; collez le recouvrement",
                             "Alise o fundo: as abas dos foles por baixo e a aba da frente sobre "
                             "a de trás; cole a sobreposição"),
                bottom_pose(S_DOWN, DOWN), duration_ms=2500),
]
program = pliego.Sequence.kinematic_path(bag, steps, substeps={"tube": 6, "gussets-in": 10,
                                                                "bottom": 10})

# ── self-checks: the erected bag (the program's last state) ──
arr = bag.build()
final = {}
for st in program.steps:
    for t, a in st.targets:
        final[t.edge] = a
res = kinematics.closure_residual(arr, final, pliego.P(w / 2, h / 2))
pose = kinematics.pose_arrangement(arr, final, pliego.P(w / 2, h / 2))


def world(u, v):
    for i, p in enumerate(arr.vertices):
        if abs(p.x - u) < 1e-6 and abs(p.y - v) < 1e-6:
            x, y, z = pose[i]
            return (x, -z, y + g)    # the stand rotation: (x, y, z) → (x, −z, y), then + g on z
    raise ValueError(f"paper-bag: no vertex at ({u}, {v})")


checks = {
    "tube closes": math.dist(world(X4, h), (0.0, h, g)),
    "back panel": math.dist(world(X3, 0.0), (0.0, 0.0, 0.0)),
    "gusset": math.dist(world(X2, h), (w, h, 0.0)),
}
front_tip = world(DELTA, -e)
back_tip = world(X2, -e)
worst = max(checks.values())
if worst > TOL or res > 1e-6:
    raise ValueError(f"paper-bag: the erected bag does not close ({checks}, residual {res:.3g})")
lift = -e * math.sin(math.radians(90.0 + F_DOWN))  # the flaps stop just short of flat
if abs(front_tip[1] - lift) > TOL or abs(front_tip[2] - (g - e * math.cos(math.radians(
        90.0 + F_DOWN)))) > TOL:
    raise ValueError(f"paper-bag: the front flap does not lie on the bottom: {front_tip}")
reach = back_tip[2] - front_tip[2]
if reach < ov - 1.0:
    raise ValueError(f"paper-bag: the flaps overlap by {reach:.2f} mm, not {ov:g} mm")
tr = kinematics.face_transforms(arr, final, kinematics.root_face(arr, pliego.P(w / 2, h / 2)))


def height(u, v, x, z):
    """Height (world y) of the face holding paper point (u, v), at world (x, z)."""
    rm, t = tr[kinematics.root_face(arr, pliego.P(u, v))]
    q = []
    for p_ in ((u, v), (u + 1.0, v), (u, v + 1.0)):
        a_ = (p_[0], 0.0, -p_[1])
        loc = [sum(rm[i][j] * a_[j] for j in range(3)) + t[i] for i in range(3)]
        q.append((loc[0], -loc[2], loc[1] + g))
    n_ = [(q[1][(i + 1) % 3] - q[0][(i + 1) % 3]) * (q[2][(i + 2) % 3] - q[0][(i + 2) % 3])
          - (q[1][(i + 2) % 3] - q[0][(i + 2) % 3]) * (q[2][(i + 1) % 3] - q[0][(i + 1) % 3])
          for i in range(3)]
    return q[0][1] - (n_[0] * (x - q[0][0]) + n_[2] * (z - q[0][2])) / n_[1]


# the ear must lie between the gusset triangle (inside) and the front flap (outside)
ear_uv = (X1 + eg / 3, -2 * eg / 3)
c_ = kinematics.pose_arrangement(arr, final, pliego.P(w / 2, h / 2))
eu = [c_[i] for i, p_ in enumerate(arr.vertices)
      if (abs(p_.x - X1) < 1e-6 and abs(p_.y + eg) < 1e-6) or
      (abs(p_.x - X1 - eg) < 1e-6 and abs(p_.y + eg) < 1e-6) or
      (abs(p_.x - X1) < 1e-6 and abs(p_.y) < 1e-6)]
px = sum(q[0] for q in eu) / 3
pz = sum(q[1] for q in eu) / 3 + g
layers = (height(X1 + 0.6 * eg, -0.2 * eg, px, pz), height(*ear_uv, px, pz),
          height(DELTA + 1.0, -1.0, px, pz))
if not layers[0] > layers[1] > layers[2]:
    raise ValueError(f"paper-bag: the ear is not between the gusset and the flap: {layers}")
ear_y = layers[1]
print(f"paper-bag: bag={w:g}x{g:g}x{h:g}mm extension={e:.1f}mm overlap={ov:g}mm "
      f"blank={X4 + SEAM:.0f}x{h + e:.0f}mm tube={worst:.1e}mm residual={res:.1e}mm "
      f"flaps={F_DOWN:.3f}deg reach={reach:.1f}mm "
      f"ear_height={ear_y:.2f}mm program={len(program.steps)} substeps "
      f"dof={program.report['dof']} max_residual={program.report['max_residual_rad']:.1e}rad")

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


result = pliego.Assembly(
    [bag],
    controls=[pliego.sequence_control(label=L4("Make the bag", "Armar la bolsa",
                                               "Former le sac", "Montar o saco"))],
    sequence=program,
    targets={"erected": {"angles": dict(final), "root": (w / 2, h / 2)}},
    title="Paper bag",
)
# the seam and the bottom overlap glued at their steps (spec §5.19): flat blank, glued bag
ZONES = [{"id": "seam", "polygon": [(X4 + 1.0, 5.0), (X4 + SEAM - 1.0, 5.0),
                                    (X4 + SEAM - 1.0, h - 5.0), (X4 + 1.0, h - 5.0)]},
         {"id": "bottom-overlap", "polygon": [(DELTA + ov / 2 + 2.0, -e + 1.0),
                                              (X1 - ov / 2 - 2.0, -e + 1.0),
                                              (X1 - ov / 2 - 2.0, -e + ov - 1.0),
                                              (DELTA + ov / 2 + 2.0, -e + ov - 1.0)]}]
# the front flap wraps under the back flap: it lies on the back flap's outside (its front)
made, flat = glue_at_steps(result, [(bag, ZONES)], frame="target:erected",
                           sides={"seam": "back", "bottom-overlap": "front"})
if flat:
    raise ValueError(f"paper-bag: glue zones {flat} land on no face of the erected bag")
print("paper-bag: glue=" + " ".join(f"{j['id']}@{j['active_from']}" for j in made))
