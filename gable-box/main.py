"""Gable box — sheet-hyperobjects cartridge (Pliego).

A gable-top carry box with a handle, cut from one sheet of paperboard and generated from inside
dimensions (length × width × wall height, roof rise, handle height). Panels run front · side ·
back · side with the glue flap on the last side.

- **Body and bottom.** Walls are inside + t (centre-line rule, t = the board caliper). The
  bottom is a tuck end (two dust flaps and a tuck lid) or a 1-2-3 snap-lock bottom (minor,
  major, minor, then the front flap's tongue under them), chosen with ``bottom``.
- **Gable.** The front and back walls carry roof panels that tilt in by β = atan(W/2 / h) and
  handle panels that turn back to vertical, so the two handles meet back to back at the middle
  (each t/2 off the centre plane: roof run = (W + t)/2 − t/2 = W/2, roof slant √(h² + (W/2)²)).
  The side walls end in triangular gable ends whose slanted edges run parallel to the roof and
  t inside it (the base corner moves in by t·r/h); a support flap on each slanted edge folds in
  90° — the roof plane contains the box's length direction, so it is perpendicular to the gable —
  and the roof rests on it. The gable ends are slit free of the roofs.
- **Handle.** Both handle panels carry the same stadium-shaped hand hole, so the holes align
  when the handles close; a peel-and-seal strip on the front handle holds them together.

Every fold is straight and no hinge meets another inside the sheet (flaps are separated by
slits), so the blank is a face tree and the fold program is kinematic and exact. The glued
joint and the peel-and-seal strip are fabrication data (glue zones); welding them, and the
handle carrying a load, need the physics engine.
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


length = float(PARAM(lambda: length, 100.0))        # noqa: F821 - inside, front panel
width = float(PARAM(lambda: width, 60.0))           # noqa: F821 - inside, front to back
depth = float(PARAM(lambda: depth, 90.0))           # noqa: F821 - inside wall height
rise = float(PARAM(lambda: rise, 45.0))             # noqa: F821 - roof rise above the walls
handle = float(PARAM(lambda: handle, 45.0))         # noqa: F821 - handle panel height
bottom = str(PARAM(lambda: bottom, "snap-lock"))    # noqa: F821
stock = str(PARAM(lambda: stock, "folding-boxboard-300"))   # noqa: F821
branding = bool(PARAM(lambda: branding, True))      # noqa: F821

STOCKS = ("folding-boxboard-300", "sbs-board-350", "cardstock-300", "kraftliner-150")
if stock not in STOCKS:
    raise ValueError(f"gable-box: stock must be one of {STOCKS}, got {stock!r}")
if bottom not in ("tuck", "snap-lock"):
    raise ValueError("gable-box: bottom must be tuck or snap-lock")
length = pliego.clamp(length, 40.0, 300.0)
width = pliego.clamp(width, 30.0, min(length, 200.0))
depth = pliego.clamp(depth, 30.0, 300.0)
rise = pliego.clamp(rise, 0.3 * width, 1.5 * width)
handle = pliego.clamp(handle, 30.0, 120.0)

t = pliego.board.caliper(stock)
Lp, Wp, Dp = length + t, width + t, depth + t
run = width / 2.0                              # roof run: (W + t)/2 − t/2
slant = math.hypot(rise, run)
beta = math.degrees(math.atan2(run, rise))     # roof tilt from vertical
c = max(t, 0.5)                                # clearance trim at the glue joint
G = min(max(0.18 * Wp, 10.0), 18.0)            # glue flap
xs = {"front": (0.0, Lp), "side-1": (Lp, Lp + Wp), "back": (Lp + Wp, 2 * Lp + Wp),
      "side-2": (2 * Lp + Wp, 2 * Lp + 2 * Wp)}
tongue = min(max(0.3 * Wp, 12.0), 25.0)
bottom_h = Wp + tongue if bottom == "tuck" else 0.82 * Wp
y0 = bottom_h
y1 = y0 + Dp
PANELS = {"front": L4("Front", "Frente", "Face avant", "Frente"),
          "side-1": L4("Side 1", "Costado 1", "Côté 1", "Lateral 1"),
          "back": L4("Back", "Parte trasera", "Face arrière", "Traseira"),
          "side-2": L4("Side 2", "Costado 2", "Côté 2", "Lateral 2")}


def part(panel, what):
    return {g: f"{PANELS[panel][g]}: {what[g]}" for g in what}


d = pliego.dieline.Dieline(
    "gable", "gable-top box with handle", "folding-carton",
    {"length": length, "width": width, "depth": depth}, stock, t,
    label=L4("Gable box blank", "Suaje de la caja gable", "Flan de la boîte à pignon",
             "Corte da caixa gable"), grain_deg=90.0)

# ── walls; the side walls end in gable triangles (one panel each) ─────────────────────────────
s_c = t * slant / rise                         # gable base corner, moved in (support plane)
apex_h = (Wp / 2.0 - s_c) * rise / run         # gable apex above the wall top
for name, (xa, xb) in xs.items():
    if name.startswith("side"):
        d.panel(name, [(xa, y0), (xb, y0), (xb, y1), (xb - s_c, y1),
                       ((xa + xb) / 2.0, y1 + apex_h), (xa + s_c, y1), (xa, y1)], "panel",
                PANELS[name])
    else:
        d.rect(name, xa, y0, xb, y1, "panel", PANELS[name])
xe = xs["side-2"][1]
d.panel("glue-flap", [(xe, y0 + G * 0.5), (xe + G, y0 + G), (xe + G, y1 - G),
                      (xe, y1 - G * 0.5)], "glue-flap",
        L4("Glue flap", "Pestaña de pegado", "Patte de collage", "Aba de colagem"),
        print_area=False)
d.glue_zone("manufacturers-joint", [(xe + 1.0, y0 + G), (xe + G - 1.0, y0 + G + 0.6),
                                    (xe + G - 1.0, y1 - G - 0.6), (xe + 1.0, y1 - G)],
            on="glue-flap")
for a_, b_ in (("front", "side-1"), ("side-1", "back"), ("back", "side-2")):
    d.hinge(a_, b_, -90.0, name=f"{a_}-{b_}-fold")
d.hinge("side-2", "glue-flap", -90.0, name="glue-flap-fold")

# ── roofs and handles (front and back), with the hand hole ────────────────────────────────────
hole_w = min(0.55 * Lp, 95.0)
hole_h = min(24.0, 0.45 * handle, 0.8 * hole_w)
roof_lab = L4("roof", "techo", "toit", "telhado")
hand_lab = L4("handle", "asa", "poignée", "alça")
for name in ("front", "back"):
    xa, xb = xs[name]
    if name == "front":
        xa += c                                  # clearance against the glue flap
    d.rect(f"{name}-roof", xa, y1, xb, y1 + slant, "lid", part(name, roof_lab))
    d.rect(f"{name}-handle", xa, y1 + slant, xb, y1 + slant + handle, "panel",
           part(name, hand_lab))
    d.hinge(name, f"{name}-roof", -beta, name=f"{name}-roof-fold")
    d.hinge(f"{name}-roof", f"{name}-handle", beta, name=f"{name}-handle-fold")
    cx, cy = (xs[name][0] + xs[name][1]) / 2.0, y1 + slant + 0.5 * handle
    r = hole_h / 2.0
    hole = []                                    # a stadium: two half circles, CCW
    for x0, a0 in ((cx + hole_w / 2.0 - r, -90.0), (cx - hole_w / 2.0 + r, 90.0)):
        for k in range(13):
            ang = math.radians(a0 + 180.0 * k / 12)
            hole.append((x0 + r * math.cos(ang), cy + r * math.sin(ang)))
    d.hole(hole)
fx0, fx1 = xs["front"][0] + c + 3.0, xs["front"][1] - 3.0
top = y1 + slant + handle
d.glue_zone("handle-seal", [(fx0, top - 3.0 - 0.15 * handle), (fx1, top - 3.0 - 0.15 * handle),
                            (fx1, top - 3.0), (fx0, top - 3.0)], kind="peel-and-seal",
            on="front-handle")

# ── roof support flaps on the gable ends' slanted edges ───────────────────────────────────────
F = min(12.0, 0.25 * slant)
sup_lab = L4("roof support flap", "solapa de apoyo del techo", "rabat d'appui du toit",
             "aba de apoio do telhado")
supports = []
for name in ("side-1", "side-2"):
    xa, xb = xs[name]
    apex = ((xa + xb) / 2.0, y1 + apex_h)
    for k, (base, sgn) in enumerate((((xa + s_c, y1), -1.0), ((xb - s_c, y1), 1.0))):
        dx, dy = apex[0] - base[0], apex[1] - base[1]
        ln = math.hypot(dx, dy)
        ux, uy = dx / ln, dy / ln
        nx, ny = (-uy, ux) if sgn < 0 else (uy, -ux)   # outward normal of the slanted edge
        if ny < 0:
            nx, ny = -nx, -ny
        ax_, nx_ = abs(ux), abs(nx)
        f_ = min(F, (ln - 6.0) * ax_ / (nx_ + 2.0 * ax_))  # room for both chamfers
        if f_ < 3.0:
            raise ValueError("gable-box: the gable is too small for its roof supports")
        s0 = max(1.0, (1.0 + f_ * (nx_ - 0.5 * ax_)) / ax_)   # clear of the roof column
        s1 = ln - f_ - 1.0
        p0 = (base[0] + ux * s0, base[1] + uy * s0)
        p1 = (base[0] + ux * s1, base[1] + uy * s1)
        q0 = (p0[0] + nx * f_ + ux * f_ * 0.5, p0[1] + ny * f_ + uy * f_ * 0.5)
        q1 = (p1[0] + nx * f_ - ux * f_ * 0.5, p1[1] + ny * f_ - uy * f_ * 0.5)
        flap = f"{name}-support-{k + 1}"
        d.panel(flap, [p0, p1, q1, q0], "flap", part(name, sup_lab), print_area=False)
        d.hinge(name, flap, -90.0, name=f"{flap}-fold")
        supports.append(f"{flap}-fold")

# ── bottom ─────────────────────────────────────────────────────────────────────────────────────
dust_lab = L4("dust flap", "guardapolvo", "rabat anti-poussière", "aba guarda-pó")
bottom_steps = []
if bottom == "tuck":
    dusts = []
    for name in ("side-1", "side-2"):
        xa, xb = xs[name]
        dh = min(0.6 * Wp, Lp / 2.0 - t)
        ch = min(dh * 0.5, Wp * 0.25)
        d.panel(f"{name}-dust", [(xa, y0), (xb, y0), (xb - ch * 0.4, y0 - dh), (xa + ch, y0 - dh)],
                "dust-flap", part(name, dust_lab))
        d.hinge(name, f"{name}-dust", -90.0, name=f"{name}-dust-fold")
        dusts.append(f"{name}-dust-fold")
    xa, xb = xs["back"]
    d.rect("bottom-lid", xa, y0 - Wp, xb, y0, "lid",
           L4("Bottom lid", "Tapa del fondo", "Couvercle du fond", "Tampa do fundo"))
    ch = min(tongue * 0.6, (xb - xa) * 0.15)
    d.panel("bottom-tuck", [(xa, y0 - Wp), (xa + ch, y0 - Wp - tongue),
                            (xb - ch, y0 - Wp - tongue), (xb, y0 - Wp)], "tuck",
            L4("Bottom tuck flap", "Lengüeta del fondo", "Patte rentrante du fond",
               "Aba de encaixe do fundo"))
    d.hinge("back", "bottom-lid", -90.0, name="bottom-lid-fold")
    d.hinge("bottom-lid", "bottom-tuck", -90.0, name="bottom-tuck-fold")
    bottom_steps = [("bottom-dust", L4("Fold in the bottom dust flaps",
                                       "Dobla hacia dentro los guardapolvos del fondo",
                                       "Rabattez les rabats anti-poussière du fond",
                                       "Dobre para dentro as abas guarda-pó do fundo"), dusts),
                    ("bottom-close", L4("Close the bottom and tuck it in",
                                        "Cierra el fondo y mete la lengüeta",
                                        "Fermez le fond et rentrez la patte",
                                        "Feche o fundo e encaixe a aba"),
                     ["bottom-lid-fold", "bottom-tuck-fold"])]
else:
    h_minor, h_major = Wp / 2.0, 0.7 * Wp
    flap_lab = L4("bottom flap", "solapa de fondo", "rabat de fond", "aba do fundo")
    order = []
    for k, (name, h) in enumerate((("side-1", h_minor), ("back", h_major), ("side-2", h_minor))):
        xa, xb = xs[name]
        ch = min(h * 0.5, (xb - xa) * 0.2)
        fl = f"bottom-{k + 1}"
        d.panel(fl, [(xa, y0), (xb, y0), (xb - ch, y0 - h), (xa + ch, y0 - h)], "bottom",
                part(name, flap_lab))
        d.hinge(name, fl, -90.0, name=f"{fl}-fold")
        order.append(f"{fl}-fold")
    xa, xb = xs["front"][0] + c, xs["front"][1]
    tw = (xb - xa) / 3.0
    d.panel("bottom-4", [(xa, y0), (xb, y0), (xb, y0 - h_major), (xa + 2 * tw, y0 - h_major),
                         (xa + 2 * tw - 2.0, y0 - h_major - 0.12 * Wp),
                         (xa + tw + 2.0, y0 - h_major - 0.12 * Wp), (xa + tw, y0 - h_major),
                         (xa, y0 - h_major)], "lock", part("front", flap_lab))
    d.hinge("front", "bottom-4", -90.0, name="bottom-4-fold")
    for k, h_ in enumerate(order):
        bottom_steps.append((f"bottom-{k + 1}", L4(f"Fold bottom flap {k + 1}",
                                                    f"Dobla la solapa de fondo {k + 1}",
                                                    f"Rabattez le rabat de fond {k + 1}",
                                                    f"Dobre a aba do fundo {k + 1}"), [h_]))
    bottom_steps.append(("bottom-lock", L4("Lock the front flap's tongue under the others",
                                           "Traba la lengüeta de la solapa frontal bajo las demás",
                                           "Glissez la languette du rabat avant sous les autres",
                                           "Trave a lingueta da aba frontal sob as outras"),
                         ["bottom-4-fold"]))

d.dimension((0.0, y0), (Lp, y0), f"L {length:g} (inside)", -6.0)
d.dimension((Lp, y0), (Lp + Wp, y0), f"W {width:g} (inside)", -6.0)
d.dimension((0.0, y0), (0.0, y1), f"D {depth:g} (inside)", 8.0)
d.dimension((0.0, y1), (0.0, y1 + slant), f"roof {slant:.1f} (rise {rise:g})", 8.0)

d.step("form-tube", L4("Fold the body into a tube and glue the joint",
                       "Dobla el cuerpo en un tubo y pega la unión",
                       "Pliez le corps en tube et collez la patte",
                       "Dobre o corpo num tubo e cole a junta"),
       ["front-side-1-fold", "side-1-back-fold", "back-side-2-fold", "glue-flap-fold"], 1500)
for sid, label, hinges in bottom_steps:
    d.step(sid, label, hinges, 900)
d.step("supports-in", L4("Fold the roof supports in on the gable ends",
                         "Dobla hacia dentro los apoyos del techo en los frontones",
                         "Rabattez les appuis du toit sur les pignons",
                         "Dobre para dentro os apoios do telhado nos frontões"), supports, 900)
d.step("close-gable", L4("Bring the roofs together and raise the handles back to back",
                         "Junta los techos y levanta las asas espalda con espalda",
                         "Rapprochez les toits et dressez les poignées dos à dos",
                         "Junte os telhados e levante as alças costas com costas"),
       ["front-roof-fold", "back-roof-fold", "front-handle-fold", "back-handle-fold"], 1800)
pack = d.build(rest_on="front")

artwork = []
if branding:
    side_len = 0.45 * min(Lp, Dp)
    cx, cy = Lp / 2.0, (y0 + y1) / 2.0
    artwork.append(pliego.press.artwork(
        "brand-mark", pack.sheet, "assets/brand-mark.svg", (cx - side_len / 2, cy - side_len / 2),
        (side_len, side_len), side="front", panel="front", clip="panel"))

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
    [pack], title="Gable box with handle", artwork=artwork,
    label=L4("Fold program", "Secuencia de armado", "Séquence de montage",
             "Sequência de montagem"),
    meta={"cartridge": "gable-box",
          "params": {"length": length, "width": width, "depth": depth, "rise": rise,
                     "handle": handle, "bottom": bottom, "stock": stock, "branding": branding}})

# glue joins that take hold at their step (spec §5.19): the program starts flat and ends glued
made, flat = glue_at_steps(result, [(pack.sheet, pack.block["glue"])])
print("gable-box: glue=" + " ".join(f"{j['id']}@{j['active_from']}" for j in made)
      + (f" flat-glued={flat}" if flat else ""))
