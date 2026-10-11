"""Carousel village — sheet-hyperobjects cartridge (Pliego).

A carousel (star) book whose chambers are a village street: one strip of card opens 360° into
`chambers` chambers, and every chamber holds a house that stands up out of the card itself when
the book opens. Composition of two kernel builders, no glue for the houses:

* `pliego.book.carousel_strip` — the strip: front and back covers lined (a panel folded and glued
  behind each cover), double walls made by fore-edge folds, two ribbons that tie the covers;
* `pliego.popup.cut_fold` — at every chamber's spine fold, one parallel (box) fold cut from the
  two walls that meet there: two slits, three folds, a facade parallel to one wall and a side wall
  parallel to the other. The roof, belfry or parapet is a crest: it continues the facade past the
  upper slit and leaves its own shape as a window in the wall behind.

Kinematics (Tier R, exact). Every spine fold turns about the book's axis, and every fold of a box
turns by the same angle as the spine fold it is cut across (A and B with it, F against it), so
every state of the program is rigid and a linear blend of the angles is exact. Doors are flaps cut
in the facades, hinged on one side: free hinges. The script checks closure at every program state,
the papercut minimum feature over the whole strip, that no roof window looks through a double wall
into the next chamber's house, and that open doors stay inside their chamber (fail loud).

House shapes are original, generic village forms generated here (cottage, chapel with a bell
gable, two-storey house, tower, flat-roofed house, granary); no published pop-up is reproduced.
"""

import math

import pliego


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


chambers = round(float(PARAM(lambda: chambers, 6)))               # noqa: F821
page_width = float(PARAM(lambda: page_width, 110.0))              # noqa: F821
page_height = float(PARAM(lambda: page_height, 150.0))            # noqa: F821
village = str(PARAM(lambda: village, "mixed"))                    # noqa: F821
doors = str(PARAM(lambda: doors, "opening"))                      # noqa: F821
stock = str(PARAM(lambda: stock, "cardstock-250"))                # noqa: F821

MIN_FEATURE = {"cardstock-250": 2.0, "cardstock-160": 1.5}
VILLAGES = {
    "mixed": ("granary", "flat-roof", "cottage", "chapel", "townhouse", "tower"),
    "cottages": ("cottage",),
    "flat-roofs": ("flat-roof",),
}
if stock not in MIN_FEATURE:
    raise ValueError(f"carousel-village: stock must be one of {tuple(MIN_FEATURE)}, got {stock!r}")
if village not in VILLAGES:
    raise ValueError(f"carousel-village: village must be one of {tuple(VILLAGES)}, got "
                     f"{village!r}")
if doors not in ("opening", "none"):
    raise ValueError(f"carousel-village: doors must be opening or none, got {doors!r}")
if not 4 <= chambers <= 8:
    raise ValueError(f"carousel-village: chambers must be an integer in [4, 8], got {chambers}")

N = chambers
W = pliego.clamp(page_width, 80.0, 180.0)
H = pliego.clamp(page_height, 110.0, 260.0)
MINF = MIN_FEATURE[stock]
MARGIN = 3.0                      # uncut fold ends, clearance between features (mm)
GROUND = MARGIN                   # houses start this far above the table
SHUT = 178.0                      # closed: every spine fold stops 2° short of flat
DOOR_OPEN = 70.0
UPRIGHT = (math.sqrt(0.5), 0.0, 0.0, math.sqrt(0.5))   # +90° about X: sheet v → world up
TOL = 1e-6


def L4(en, es, fr, pt):
    return {"en": en, "es": es, "fr": fr, "pt": pt}


NAMES = {
    "cottage": L4("Cottage", "Casita", "Maisonnette", "Casinha"),
    "chapel": L4("Chapel", "Capilla", "Chapelle", "Capela"),
    "townhouse": L4("Two-storey house", "Casa de dos pisos", "Maison à étage", "Sobrado"),
    "tower": L4("Tower", "Torre", "Tour", "Torre"),
    "flat-roof": L4("Flat-roofed house", "Casa de azotea", "Maison à toit plat",
                    "Casa de terraço"),
    "granary": L4("Granary", "Granero", "Grange", "Celeiro"),
}


# ── house styles: proportions of the page, crest outline over the facade ──────


def rect(t0, y0, t1, y1):
    return [(t0, y0), (t1, y0), (t1, y1), (t0, y1)]


def arch(tc, y0, w, h, n=8):
    """An arched opening: straight sides, a half-round top (panel-local t, y)."""
    r = w / 2.0
    pts = [(tc - r, y0), (tc + r, y0), (tc + r, y0 + h - r)]
    pts += [(tc + r * math.cos(math.pi * k / n), y0 + h - r + r * math.sin(math.pi * k / n))
            for k in range(1, n)]
    return pts + [(tc - r, y0 + h - r)]


def disc(tc, yc, r, n=12):
    return [(tc + r * math.cos(2 * math.pi * k / n), yc + r * math.sin(2 * math.pi * k / n))
            for k in range(n)]


def style(name):
    """{a, b, wall, crest [(t, h)], facade/side/crest holes, doors} for one house style."""
    if name == "cottage":
        a, b, wall, roof = 0.44 * W, 0.27 * W, 0.30 * H, 0.15 * H
        x0, x1 = 0.66 * b, 0.80 * b
        slope = lambda t: roof * (b - t) / (b / 2.0)                    # noqa: E731
        crest = [(0, 0), (b / 2, roof), (x0, slope(x0)), (x0, 1.05 * roof),
                 (x1, 1.05 * roof), (x1, slope(x1)), (b, 0)]
        gable = [disc(b / 2, 0.42 * roof, 0.11 * b)]
        side = [rect(0.22 * a, 0.42 * wall, 0.40 * a, 0.68 * wall),
                rect(0.60 * a, 0.42 * wall, 0.78 * a, 0.68 * wall)]
        dr = [(0.5 * b, 0.28 * b, 0.48 * wall, "rect")]
        return a, b, wall, crest, [], side, gable, dr
    if name == "chapel":
        a, b, wall = 0.38 * W, 0.24 * W, 0.36 * H
        s, t = 0.06 * H, 0.17 * H
        crest = [(0, 0), (0.16 * b, s), (0.30 * b, s), (0.30 * b, t), (0.5 * b, 0.23 * H),
                 (0.70 * b, t), (0.70 * b, s), (0.84 * b, s), (b, 0)]
        bell = [arch(0.5 * b, 0.085 * H, 0.22 * b, 0.075 * H)]
        side = [arch(0.30 * a, 0.40 * wall, 0.10 * a, 0.36 * wall),
                arch(0.62 * a, 0.40 * wall, 0.10 * a, 0.36 * wall)]
        facade = [disc(0.5 * b, 0.80 * wall, 0.10 * b)]
        dr = [(0.5 * b, 0.32 * b, 0.50 * wall, "arch")]
        return a, b, wall, crest, facade, side, bell, dr
    if name == "townhouse":
        a, b, wall = 0.36 * W, 0.30 * W, 0.42 * H
        c1, c2 = 0.035 * H, 0.06 * H
        crest = [(0, 0), (0.06 * b, c1), (0.35 * b, c1), (0.35 * b, c2), (0.65 * b, c2),
                 (0.65 * b, c1), (0.94 * b, c1), (b, 0)]
        facade = [rect(0.14 * b, 0.62 * wall, 0.38 * b, 0.84 * wall),
                  rect(0.62 * b, 0.62 * wall, 0.86 * b, 0.84 * wall)]
        side = [rect(r0 * a, h0 * wall, (r0 + 0.2) * a, (h0 + 0.18) * wall)
                for r0 in (0.2, 0.6) for h0 in (0.20, 0.62)]
        dr = [(0.5 * b, 0.26 * b, 0.42 * wall, "rect")]
        return a, b, wall, crest, facade, side, [], dr
    if name == "tower":
        a, b, wall = 0.28 * W, 0.14 * W, 0.52 * H
        crest = [(0, 0), (0.5 * b, 0.20 * H), (b, 0)]
        facade = [disc(0.5 * b, 0.82 * wall, 0.22 * b),
                  rect(0.40 * b, 0.40 * wall, 0.60 * b, 0.58 * wall)]
        side = [rect(0.44 * a, 0.30 * wall, 0.56 * a, 0.46 * wall),
                rect(0.44 * a, 0.62 * wall, 0.56 * a, 0.78 * wall)]
        dr = [(0.5 * b, 0.40 * b, 0.26 * wall, "arch")]
        return a, b, wall, crest, facade, side, [], dr
    if name == "flat-roof":
        a, b, wall = 0.44 * W, 0.30 * W, 0.26 * H
        p1, p2 = 0.04 * H, 0.07 * H
        crest = [(0, 0), (0.08 * b, p1), (0.28 * b, p1), (0.36 * b, p2), (0.64 * b, p2),
                 (0.72 * b, p1), (0.92 * b, p1), (b, 0)]
        facade = [rect(0.62 * b, 0.40 * wall, 0.86 * b, 0.70 * wall)]
        side = [rect(0.30 * a, 0.40 * wall, 0.50 * a, 0.70 * wall)]
        dr = [(0.30 * b, 0.26 * b, 0.58 * wall, "rect")]
        return a, b, wall, crest, facade, side, [], dr
    a, b, wall, roof = 0.48 * W, 0.32 * W, 0.24 * H, 0.10 * H          # granary
    crest = [(0, 0), (0.5 * b, roof), (b, 0)]
    vent = [disc(0.5 * b, 0.40 * roof, 0.08 * b)]
    side = [rect(0.40 * a, 0.55 * wall, 0.60 * a, 0.75 * wall)]
    dr = [(0.36 * b, 0.22 * b, 0.62 * wall, "left"), (0.64 * b, 0.22 * b, 0.62 * wall, "right")]
    return a, b, wall, crest, [], side, vent, dr


# ── the strip and the houses ─────────────────────────────────────────────────

strip = pliego.book.carousel_strip(
    N, W, H, stock=stock, spines=False, lined=True, placement=pliego.Placement(rotation=UPRIGHT),
    front="#f1e4c8", back="#b5523b",
    label=L4("Carousel village strip", "Tira de la aldea carrusel",
             "Bande du village carrousel", "Tira da aldeia carrossel"))
sheet = strip.sheet
cycle = VILLAGES[village]
houses = []
for k in range(N):
    kind = cycle[k % len(cycle)]
    a, b, wall, crest, facade, side, crest_holes, door_specs = style(kind)
    lo, hi = GROUND, GROUND + wall
    name = NAMES[kind]
    blk = pliego.popup.Block(a=a, b=b, lo=lo, hi=hi, crest=crest, crest_panel=1,
                             crest_side="hi", name=f"house-{k + 1}",
                             label={g: f"{name[g]} {k + 1}" for g in name})
    cf = pliego.popup.cut_fold(sheet, **strip.spine_frame(k), blocks=[blk],
                               angle=strip.open_angle, margin=MARGIN, gutter_name="spine",
                               gutter_label=L4("Spine", "Lomo", "Dos", "Lombada"),
                               prefix=f"house-{k + 1}")
    for poly in facade:
        sheet.hole([cf.panel_point(0, 1, t, lo + y) for t, y in poly])
    for poly in side:
        sheet.hole([cf.panel_point(0, 2, t, lo + y) for t, y in poly])
    for poly in crest_holes:
        sheet.hole([cf.panel_point(0, 1, t, hi + y) for t, y in poly])
    flaps = []
    for tc, dw, dh, shape in door_specs if doors == "opening" else ():
        y0, y1 = lo + 0.02 * wall + MARGIN, lo + 0.02 * wall + MARGIN + dh
        t0, t1 = tc - dw / 2.0, tc + dw / 2.0
        if shape == "left":                            # double doors: each hinged outside
            hinge_t, free_t = t0, t1
        else:
            hinge_t, free_t = t1, t0                   # hinged on the house's corner side
        if shape == "arch":
            top = [(free_t + (hinge_t - free_t) * (1 - math.cos(math.pi * j / 8)) / 2.0,
                    y1 - dw / 2.0 + dw / 2.0 * math.sin(math.pi * j / 8)) for j in range(9)]
            path = [(hinge_t, y0), (free_t, y0), (free_t, y1 - dw / 2.0)] + top[1:]
            y_top = y1 - dw / 2.0
        else:
            path = [(hinge_t, y0), (free_t, y0), (free_t, y1), (hinge_t, y1)]
            y_top = y1
        sheet.cut([cf.panel_point(0, 1, t, y) for t, y in path], name="door-edge")
        m = sheet.crease(cf.panel_point(0, 1, hinge_t, y0), cf.panel_point(0, 1, hinge_t, y_top),
                         "valley", DOOR_OPEN, treatment="score", name="door",
                         label=L4(f"Door hinge, house {k + 1}", f"Bisagra de la puerta, casa "
                                  f"{k + 1}", f"Charnière de la porte, maison {k + 1}",
                                  f"Dobradiça da porta, casa {k + 1}"))
        inward = 1.0 if hinge_t > free_t else -1.0      # a point just inside the flap
        flaps.append((m, cf.panel_point(0, 1, free_t + inward * 1.0, (y0 + y_top) / 2.0)))
    houses.append({"kind": kind, "cf": cf, "a": a, "b": b, "lo": lo, "hi": hi,
                   "roof": max(h for _, h in crest), "crest": crest, "doors": flaps})

arr = sheet.build()


def edge_angles(spine, door):
    out = {e: ang for m, ang in strip.angles(spine).items() for e in m.edges()}
    for hs in houses:
        out.update(hs["cf"].edge_angles(spine))
        for m, _ in hs["doors"]:
            for e in m.edges():
                out[e] = door
    return out


# ── self-checks (fail loud) ──────────────────────────────────────────────────

ROOT = pliego.P(W / 2.0, H / 2.0)                 # on the front lining (the preview's root)
worst = max(pliego.kinematics.closure_residual(arr, edge_angles(g, d), ROOT)
            for g in (0.0, strip.open_angle, (strip.open_angle + SHUT) / 2.0, SHUT)
            for d in (0.0, DOOR_OPEN))
if worst > TOL:
    raise ValueError(f"carousel-village: inconsistent rigid state ({worst:.3g} mm)")

rep = pliego.papercut.analyze(sheet, min_feature_mm=MINF)
if not rep.ok or rep.components != 1:
    raise ValueError("carousel-village: papercut check failed: "
                     + "; ".join(i["detail"] for i in rep.issues if i["level"] == "error"))

# A roof leaves a window in its chamber's left wall, back to back with the previous chamber's
# right wall; that wall has an opening where the previous house came from. They must not overlap
# (the two layers are glued back to back, so touching is fine).
for k in range(1, N):
    cur, prev = houses[k], houses[k - 1]
    d0, d1 = cur["a"] - cur["b"], cur["a"]                 # distance from the spine
    if prev["hi"] > cur["hi"] + TOL and prev["b"] > d0 + TOL:
        raise ValueError(f"carousel-village: the roof of house {k + 1} would look through the "
                         f"wall into house {k} (taller and wider); reorder the street")

tr = pliego.kinematics.face_transforms(arr, edge_angles(strip.open_angle, DOOR_OPEN),
                                       pliego.kinematics.root_face(arr, ROOT))


def world(p):
    rot, t = tr[pliego.kinematics.root_face(arr, p)]
    q = (p.x, 0.0, -p.y)
    return [sum(rot[i][j] * q[j] for j in range(3)) + t[i] for i in range(3)]


def heading(p, spine):
    """Angle of a point round the spine axis (degrees, unplaced frame: the axis is along z)."""
    w, o = world(p), world(spine)
    return math.degrees(math.atan2(w[1] - o[1], w[0] - o[0]))


for k, hs in enumerate(houses):
    su = strip.spine_u(k)
    axis = pliego.P(su, H - 1.0)                       # on the spine fold, above the house
    right = heading(pliego.P(su + 0.9 * W, H - 1.0), axis)
    for _m, tip in hs["doors"]:
        rel = (heading(tip, axis) - right) % 360.0
        if not 0.0 < rel < strip.alpha:
            raise ValueError(f"carousel-village: an open door of house {k + 1} leaves its chamber")

# ── the program ──────────────────────────────────────────────────────────────

door_marks = [m for hs in houses for m, _ in hs["doors"]]
# spec §5.20: the ribbons tied in the displayed state come undone as the book closes; a second
# pair, active from the `tie` step (§5.19), ties it again once open


def lining_glue(margin=2.0, inset=0.5):
    """Each lining glued behind its cover, clear of the house cut through that cover: the cover's
    first and last chambers' houses are cut across the covers, and a weld over them would land in
    a window hole (the engine refuses it) or pin the pop-up flat. An L-shaped region per lining."""
    out, end = [], strip.offset + 2 * N * W
    for name, c0, axis in (("front", strip.offset, strip.offset), ("back", end - W, end)):
        cut = [arr.vertices[v] for e, (a, b) in enumerate(arr.edges)
               if arr.assignment[e] == "C" or (arr.assignment[e] == "B" and 0.0 < min(
                   arr.vertices[a].y, arr.vertices[b].y) and max(
                   arr.vertices[a].y, arr.vertices[b].y) < H) for v in (a, b)
               if c0 + 1e-6 < arr.vertices[v].x < c0 + W - 1e-6]
        top = min(H - inset, max(p.y for p in cut) + margin)
        u0 = 2.0 * axis - (c0 + W) if name == "front" else end   # the lining's left edge
        if name == "front":                  # the house is near the spine: the lining's left
            a = 2.0 * axis - min(p.x for p in cut) + margin
            ring = [(u0 + inset, top), (a, top), (a, inset), (u0 + W - inset, inset),
                    (u0 + W - inset, H - inset), (u0 + inset, H - inset)]
        else:                                # the house is near the spine: the lining's right
            a = 2.0 * axis - max(p.x for p in cut) - margin
            ring = [(u0 + inset, inset), (a, inset), (a, top), (u0 + W - inset, top),
                    (u0 + W - inset, H - inset), (u0 + inset, H - inset)]
        out.append(pliego.glue(f"lining-{name}", sheet, ring, sheet,
                               (-1.0, 0.0, 0.0, 1.0, 2.0 * axis, 0.0), "back"))
    return out


tied = strip.ribbons()
ribbons = tied + [dict(j, id=f"{j['id']}-again", active_from="tie") for j in tied]


def targets(spine):
    return [(m, sg * spine) for hs in houses for m, sg in hs["cf"].marks]


steps = []
if door_marks:
    steps.append(pliego.Step("close-doors", L4("Close the doors", "Cierra las puertas",
                                               "Fermer les portes", "Feche as portas"),
                             [(m, 0.0) for m in door_marks], duration_ms=1200))
steps += [
    pliego.Step("close", L4("Untie the ribbons and close the book: the houses fold flat",
                            "Desata los listones y cierra el libro: las casas se aplanan",
                            "Dénouez les rubans et fermez le livre : les maisons se replient",
                            "Desamarre as fitas e feche o livro: as casas se dobram"),
                targets(SHUT), duration_ms=3000, release_joins=[j["id"] for j in tied]),
    pliego.Step("open", L4(f"Open it all the way round: {N} chambers, {N} houses",
                           f"Ábrelo por completo: {N} cámaras, {N} casas",
                           f"Ouvrez-le jusqu'au bout : {N} chambres, {N} maisons",
                           f"Abra-o por inteiro: {N} câmaras, {N} casas"),
                targets(strip.open_angle), duration_ms=3500,
                note=L4("Each house is two slits and three folds across a spine fold; it stands "
                        "up because its walls open.",
                        "Cada casa son dos cortes y tres dobleces a través de un doblez del lomo; "
                        "se levanta porque sus paredes se abren.",
                        "Chaque maison n'est que deux fentes et trois plis en travers d'un pli du "
                        "dos ; elle se dresse parce que ses parois s'ouvrent.",
                        "Cada casa são dois cortes e três dobras através de uma dobra da "
                        "lombada; ela se ergue porque suas paredes se abrem.")),
    pliego.Step("tie", L4("Tie the ribbons at top and bottom", "Ata los listones arriba y abajo",
                          "Nouez les rubans en haut et en bas",
                          "Amarre as fitas em cima e em baixo"), [], duration_ms=800),
]
if door_marks:
    steps.append(pliego.Step("open-doors", L4("Open the doors", "Abre las puertas",
                                              "Ouvrir les portes", "Abra as portas"),
                             [(m, DOOR_OPEN) for m in door_marks], duration_ms=1200))

initial = {m: ang for m, ang in strip.angles(strip.open_angle).items()}
for hs in houses:
    initial.update(hs["cf"].angles(strip.open_angle))
    initial.update({m: DOOR_OPEN for m, _ in hs["doors"]})

print(f"village: chambers={N} street={village} page={W:g}x{H:g}mm alpha={strip.alpha:.3f}deg "
      f"houses=[{','.join(h['kind'] for h in houses)}] doors={len(door_marks)} "
      f"closure={worst:.1e}mm bridge={rep.min_bridge_mm:.2f}mm>={MINF:g} faces={len(arr.faces)}")

result = pliego.Assembly(
    [sheet],
    joins=ribbons + lining_glue(),
    controls=[pliego.sequence_control(label=L4("Close and open", "Cerrar y abrir",
                                               "Fermer et ouvrir", "Fechar e abrir"),
                                      default=float(len(steps)))],
    sequence=pliego.Sequence(steps, mode="kinematic"),
    initial={"angles": initial, "root": (ROOT.x, ROOT.y)},
    title="Carousel village",
    min_feature_mm=MINF,
)
