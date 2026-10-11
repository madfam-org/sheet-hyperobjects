"""Display stand — sheet-hyperobjects cartridge (Pliego).

A counter display cut from one sheet of board: a tray for the products, a header card rising
behind it, and an easel back that props the header up — all one blank, no glue needed to stand.

- **Print side.** The sheet's front faces the shopper: the blank is placed print side *up* and
  the tray's walls rise as valley folds, so the tray's inside and the header's front show the
  print. The front lip is a double wall rolled to the outside, so its outer leaf shows the print
  to the shopper too; the side walls' front ears are trapped between the lip's two leaves, and
  lock tabs on the outer leaf drop into slots at the base's front fold.
- **Header and easel.** The back panel leans back by ``lean`` and rises ``header`` above the
  base. A narrower strut hangs from the header's top edge down behind it to the table, a floor
  panel runs from the strut's foot back under to the base's back edge, and lock tabs on the
  floor drop into slots at the base's back fold: a closed triangle (back panel, strut, floor)
  that stands rigid once locked. The header's top corners outside the strut are rounded.
- **Side walls** follow the leaning back panel (their back edges are slanted by ``lean``); ears
  on those edges fold in 90° against the back panel (the panel contains the stand's width
  direction, so it is perpendicular to the side walls) and carry glue zones.

The triangle's angles come from its geometry: base–back fold 90° − lean (valley), header–strut
and strut–floor folds from the triangle's angles (mountain: the easel goes behind the print
side); the floor's tabs slide flat into the slots. Every fold is straight and the blank is a
face tree, so the program is kinematic and exact; the triangle closes exactly at the end (the
floor's tabs land on the back fold). Panels are inside + t (t = the board caliper); slots are 2t
wide through their folds and the lip's tabs drop 1.5t. Glue welds, the tabs' snap and the
stand's stability under load need the physics engine; no load rating is claimed.
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


width = float(PARAM(lambda: width, 220.0))          # noqa: F821 - tray inside width
depth = float(PARAM(lambda: depth, 150.0))          # noqa: F821 - tray inside, front to back
lip = float(PARAM(lambda: lip, 50.0))               # noqa: F821 - front lip height
side = float(PARAM(lambda: side, 70.0))             # noqa: F821 - side wall height
header = float(PARAM(lambda: header, 320.0))        # noqa: F821 - back panel height
lean = float(PARAM(lambda: lean, 10.0))             # noqa: F821 - back panel lean (deg)
foot = float(PARAM(lambda: foot, 140.0))            # noqa: F821 - easel floor length
stock = str(PARAM(lambda: stock, "corrugated-e-flute"))     # noqa: F821
branding = bool(PARAM(lambda: branding, True))      # noqa: F821

STOCKS = ("corrugated-e-flute", "corrugated-b-flute", "sbs-board-350", "folding-boxboard-300")
if stock not in STOCKS:
    raise ValueError(f"display-stand: stock must be one of {STOCKS}, got {stock!r}")
width = pliego.clamp(width, 80.0, 500.0)
depth = pliego.clamp(depth, 50.0, 400.0)
lip = pliego.clamp(lip, 15.0, 0.5 * depth)
side = pliego.clamp(side, lip, 1.5 * depth)
header = pliego.clamp(header, side + 60.0, 800.0)
lean = pliego.clamp(lean, 0.0, 25.0)
foot = pliego.clamp(foot, 0.25 * header, 0.8 * header)

t = pliego.board.caliper(stock)
family = "corrugated" if stock.startswith("corrugated") else "board"
Wp, Dp = width + t, depth + t
hf, hs, Hb = lip + t, side + t, header + t
phi = math.radians(lean)
s = max(2.0 * t, 2.0)                    # ear inset (knife clearance)
tab = 1.5 * t                            # lock tabs end flush with the base's underside
strut_w = 0.6 * Wp
xs0, xs1 = (Wp - strut_w) / 2.0, (Wp + strut_w) / 2.0
q = strut_w / 4.0
# triangle in the side view: B = base back edge, T = header top, E = easel foot
T = (Hb * math.sin(phi), Hb * math.cos(phi))
E = (foot, 0.0)
S = math.hypot(E[0] - T[0], E[1] - T[1])


def turn(d1, d2):
    """Signed turning angle (deg) from direction d1 to d2 in the side view (CCW > 0)."""
    return math.degrees(math.atan2(d1[0] * d2[1] - d1[1] * d2[0], d1[0] * d2[0] + d1[1] * d2[1]))


dirs = [(1.0, 0.0), (math.sin(phi), math.cos(phi)), ((E[0] - T[0]) / S, (E[1] - T[1]) / S),
        (-1.0, 0.0)]
a_back, a_strut, a_floor = (turn(dirs[k], dirs[k + 1]) for k in range(3))
# walking +y on a print-up sheet, CCW in (y, z) turns toward the print side: valley > 0

# ── the blank (flat y runs from the front lip back to the floor) ──────────────────────────────
y_base0 = (hf - t) + tab + hf            # room for the rolled lip below the base
y_base1 = y_base0 + Dp
y_top = y_base1 + Hb
d = pliego.dieline.Dieline(
    "stand", "counter display with header card and easel back", family,
    {"length": width, "width": depth, "depth": side}, stock, t,
    label=L4("Display stand blank", "Suaje del exhibidor", "Flan du présentoir",
             "Corte do expositor"), grain_deg=0.0)
NM = {"base": L4("Tray base", "Base de la charola", "Fond du plateau", "Base da bandeja"),
      "lip": L4("Front lip, inner leaf", "Frente, hoja interior", "Bord avant, feuillet intérieur",
                "Frente, folha interna"),
      "lip-outer": L4("Front lip, outer leaf", "Frente, hoja exterior",
                      "Bord avant, feuillet extérieur", "Frente, folha externa"),
      "header": L4("Header card", "Cabecera", "Fronton", "Cabeceira"),
      "strut": L4("Easel strut", "Pata del atril", "Béquille", "Pé do cavalete"),
      "floor": L4("Easel floor", "Piso del atril", "Semelle de la béquille", "Base do cavalete"),
      "side": L4("Side wall", "Pared lateral", "Paroi latérale", "Parede lateral"),
      "ear": L4("ear", "oreja", "oreille", "orelha")}
slot_back = [(xs0 + q - q / 4.0 - 0.5, xs0 + q + q / 4.0 + 0.5),
             (xs0 + 3 * q - q / 4.0 - 0.5, xs0 + 3 * q + q / 4.0 + 0.5)]
slot_front = [(Wp * 0.25 - Wp / 16.0 - 0.5, Wp * 0.25 + Wp / 16.0 + 0.5),
              (Wp * 0.75 - Wp / 16.0 - 0.5, Wp * 0.75 + Wp / 16.0 + 0.5)]


def notch(edge_y, spans, depth_, up):
    """Points along a horizontal edge at edge_y with notches `depth_` deep (up: into +y)."""
    out = []
    for a, b in spans:
        dd = depth_ if up else -depth_
        out += [(a, edge_y), (a, edge_y + dd), (b, edge_y + dd), (b, edge_y)]
    return out


base = ([(0.0, y_base0)] + notch(y_base0, slot_front, t, True) + [(Wp, y_base0), (Wp, y_base1)]
        + list(reversed(notch(y_base1, slot_back, t, False))) + [(0.0, y_base1)])
d.panel("base", base, "bottom", NM["base"])
lip_in = ([(0.0, y_base0 - hf)] + [(Wp, y_base0 - hf), (Wp, y_base0)]
          + list(reversed(notch(y_base0, slot_front, t, False))) + [(0.0, y_base0)])
d.panel("lip", lip_in, "panel", NM["lip"])
yo0, yo1 = y_base0 - hf, y_base0 - hf - (hf - t)
outer = [(t, yo0), (t, yo1)]
for a, b in slot_front:
    a_, b_ = a + 0.5, b - 0.5
    outer += [(a_, yo1), (a_ + 0.5, yo1 - tab), (b_ - 0.5, yo1 - tab), (b_, yo1)]
outer += [(Wp - t, yo1), (Wp - t, yo0)]
d.panel("lip-outer", outer, "lock", NM["lip-outer"])
# header: straight sides, rounded top corners outside the strut's hinge
rc = min(0.9 * xs0, 0.15 * Hb)
hdr = ([(0.0, y_base1)] + notch(y_base1, slot_back, t, True) + [(Wp, y_base1), (Wp, y_top - rc)])
for k in range(1, 9):
    ang = math.radians(90.0 * k / 8)
    hdr.append((Wp - rc + rc * math.cos(ang), y_top - rc + rc * math.sin(ang)))
hdr += [(xs1, y_top), (xs0, y_top)]
for k in range(0, 8):
    ang = math.radians(90.0 + 90.0 * k / 8)
    hdr.append((rc + rc * math.cos(ang), y_top - rc + rc * math.sin(ang)))
hdr.append((0.0, y_top - rc))
d.panel("header", hdr, "panel", NM["header"])
d.rect("strut", xs0, y_top, xs1, y_top + S, "panel", NM["strut"])
yf1 = y_top + S + foot
floor = [(xs0, y_top + S), (xs1, y_top + S), (xs1, yf1)]
for a, b in reversed(slot_back):
    a_, b_ = a + 0.5, b - 0.5
    floor += [(b_, yf1), (b_ - 0.5, yf1 + tab), (a_ + 0.5, yf1 + tab), (a_, yf1)]
floor.append((xs0, yf1))
d.panel("floor", floor, "lock", NM["floor"])
d.hinge("base", "lip", 90.0, name="lip-fold")
d.hinge("lip", "lip-outer", -180.0, name="lip-roll")
d.hinge("base", "header", a_back, name="header-fold")
d.hinge("header", "strut", a_strut, name="strut-fold")
d.hinge("strut", "floor", a_floor, name="floor-fold")
glue_back = []
ears_front, ears_back, sides = [], [], []
for k, sgn in ((1, -1.0), (2, 1.0)):
    edge = 0.0 if sgn < 0 else Wp
    out = edge + sgn * hs
    yb = y_base1 + hs * math.tan(phi)
    poly = [(edge, y_base0), (edge, y_base1), (out, yb), (out, y_base0)]
    d.panel(f"side-{k}", poly, "panel", {g: f"{v} {k}" for g, v in NM["side"].items()})
    d.hinge("base", f"side-{k}", 90.0, name=f"side-{k}-fold")
    sides.append(f"side-{k}-fold")
    # front ear: trapped between the lip's leaves
    eh = hf - 2.0 * s
    ew = min(0.3 * Wp, 0.8 * (hf - t))
    xa, xb = sorted((edge + sgn * s / 2.0, edge + sgn * (s / 2.0 + eh)))
    d.panel(f"side-{k}-front-ear", [(xa, y_base0), (xb, y_base0), (xb, y_base0 - ew),
                                    (xa, y_base0 - ew)], "dust-flap",
            {g: f"{NM['side'][g]} {k}: {NM['ear'][g]}" for g in NM["ear"]})
    d.hinge(f"side-{k}", f"side-{k}-front-ear", 90.0, name=f"side-{k}-front-ear-fold")
    ears_front.append(f"side-{k}-front-ear-fold")
    # back ear on the slanted edge, folded 90° in against the header
    ux, uy = (out - edge) / math.hypot(out - edge, yb - y_base1), \
        (yb - y_base1) / math.hypot(out - edge, yb - y_base1)
    nx, ny = (uy, -ux) if sgn < 0 else (-uy, ux)
    if ny < 0:
        nx, ny = -nx, -ny
    ln = math.hypot(out - edge, yb - y_base1)
    bw = min(15.0, 0.25 * ln)
    p0 = (edge + ux * (s + 1.0), y_base1 + uy * (s + 1.0))
    p1 = (edge + ux * (0.75 * ln), y_base1 + uy * (0.75 * ln))
    ear = [p0, p1, (p1[0] + nx * bw - ux * bw * 0.5, p1[1] + ny * bw - uy * bw * 0.5),
           (p0[0] + nx * bw + ux * bw * 0.5, p0[1] + ny * bw + uy * bw * 0.5)]
    d.panel(f"side-{k}-back-ear", ear, "glue-flap",
            {g: f"{NM['side'][g]} {k}: {NM['ear'][g]}" for g in NM["ear"]}, print_area=False)
    d.hinge(f"side-{k}", f"side-{k}-back-ear", 90.0, name=f"side-{k}-back-ear-fold")
    ears_back.append(f"side-{k}-back-ear-fold")
    cx_, cy_ = sum(p[0] for p in ear) / 4.0, sum(p[1] for p in ear) / 4.0
    d.glue_zone(f"side-{k}-back-ear-glue", [((x - cx_) * 0.7 + cx_, (y - cy_) * 0.7 + cy_)
                                            for x, y in ear], on=f"side-{k}-back-ear")
d.dimension((0.0, y_base0), (Wp, y_base0), f"W {width:g} (inside)", -6.0)
d.dimension((Wp, y_base0), (Wp, y_base1), f"D {depth:g} (inside)", -8.0 - hs)
d.dimension((Wp, y_base1), (Wp, y_top), f"header {header:g}", -8.0)
d.step("lip-up", L4("Raise the front lip's inner leaf", "Levanta la hoja interior del frente",
                    "Relevez le feuillet intérieur du bord avant",
                    "Levante a folha interna da frente"), ["lip-fold"], 900)
d.step("sides-up", L4("Raise the side walls and fold their ears in",
                      "Levanta las paredes laterales y dobla sus orejas hacia dentro",
                      "Relevez les parois latérales et rabattez leurs oreilles",
                      "Levante as paredes laterais e dobre as orelhas para dentro"),
       sides + ears_front + ears_back, 1200)
d.step("lip-roll", L4("Roll the lip's outer leaf over the ears and lock its tabs",
                      "Enrolla la hoja exterior del frente sobre las orejas y traba sus pestañas",
                      "Roulez le feuillet extérieur sur les oreilles et verrouillez ses pattes",
                      "Enrole a folha externa sobre as orelhas e trave as abas"),
       ["lip-roll"], 1200)
d.step("header-up", L4("Raise the header card, leaning back",
                       "Levanta la cabecera, inclinada hacia atrás",
                       "Relevez le fronton, incliné vers l'arrière",
                       "Levante a cabeceira, inclinada para trás"), ["header-fold"], 1300)
d.step("easel", L4("Fold the easel down behind, run its floor under and lock the tabs",
                   "Baja el atril por detrás, mete su piso por debajo y traba las pestañas",
                   "Rabattez la béquille derrière, glissez sa semelle et verrouillez les pattes",
                   "Baixe o cavalete por trás, passe a base por baixo e trave as abas"),
       ["strut-fold", "floor-fold"], 1600)
pack = d.build(rest_on="base")
pack.sheet.placement = pliego.Placement()          # print side up: the shopper sees the front
# the floor lies on the table: its tabs, part of the floor panel, slide flat into the slots
print(f"display-stand: back {a_back:.1f} strut {a_strut:.1f} floor {a_floor:.1f} deg; "
      f"strut {S:.1f} mm; triangle closes on the back fold")

artwork = []
if branding:
    side_len = 0.5 * min(Wp, Hb - hs)
    cx, cy = Wp / 2.0, y_base1 + hs + 0.55 * (Hb - hs)
    artwork.append(pliego.press.artwork(
        "brand-mark", pack.sheet, "assets/brand-mark.svg", (cx - side_len / 2, cy - side_len / 2),
        (side_len, side_len), side="front", panel="header", clip="panel"))

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


def closed_glue(assembly, sheet_id, zones, frame="target:closed", after=None):
    """Welds for glue zones ({id, polygon} on sheet `sheet_id`), read from a closed pose: {zone id:
    (region, map, side, k)} — the zone inset by INSET and clipped clear of cut edges, the map
    onto the face it lands on, the side of that face the tab lies on, and k, the last step that
    folds a crease on the face-tree path from tab to zone (or `after[zone id]`). Zones that land
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
        q0, q1, q2 = [to2(faces[ib], to3(faces[ia], p))[0] for p in ((0, 0), (1, 0), (0, 1))]
        m = [q1[0] - q0[0], q2[0] - q0[0], q1[1] - q0[1], q2[1] - q0[1], q0[0], q0[1]]
        # the tab comes from the side of the zone where its hinge neighbour stands
        lean = [to2(faces[ib], to3(f, centre([lay[v] for v in f])))[1]
                for i, f in enumerate(faces) if i != ia and rims[i] & rims[ia]]
        side = "front" if max(lean, key=abs, default=1.0) > 0 else "back"
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


def glue_at_steps(assembly, groups, frame="target:closed", after=None):
    """A glue join for every glue zone of `groups` ([(sheet, zones)]), active from the step after
    the one that closes it (a short final press step when that is the last one). Returns the
    joins made and the zones left as fabrication data."""
    welds = {(sh.id, z): (sh, w) for sh, zones in groups
             for z, w in closed_glue(assembly, sh.id, zones, frame, after).items()}
    steps = assembly.sequence.steps
    if any(w[3] == len(steps) - 1 for _, w in welds.values()):
        steps.append(pliego.Step("press", PRESS, [], duration_ms=600))
    made = [dict(pliego.glue(zid, sh, w[0], sh, w[1], w[2]), active_from=steps[w[3] + 1].id)
            for (_, zid), (sh, w) in welds.items()]
    assembly.joins.extend(made)
    return made, [z["id"] for sh, zones in groups for z in zones if (sh.id, z["id"]) not in welds]


result = pliego.dieline.assemble(
    [pack], title="Counter display stand", artwork=artwork,
    label=L4("Fold program", "Secuencia de armado", "Séquence de montage",
             "Sequência de montagem"),
    meta={"cartridge": "display-stand",
          "params": {"width": width, "depth": depth, "lip": lip, "side": side, "header": header,
                     "lean": lean, "foot": foot, "stock": stock, "branding": branding}})

# glue joins that take hold at their step (spec §5.19): the program starts flat and ends glued
made, flat = glue_at_steps(result, [(pack.sheet, pack.block["glue"])])
print("display-stand: glue=" + " ".join(f"{j['id']}@{j['active_from']}" for j in made)
      + (f" flat-glued={flat}" if flat else ""))
