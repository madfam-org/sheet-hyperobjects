"""Ofrenda pop-up — sheet-hyperobjects cartridge (Pliego).

A Día de Muertos ofrenda as a 90° pop-up card: a back page (the wall) and a floor page meet at the
gutter, and opening the card raises an altar of `levels` tiers out of the card itself, dressed
with candles, a pan de muerto and a photo-frame space; kirigami cempasúchil (marigold) flowers
open on the wall in an arch, and a papel picado banner of tissue flags hangs across the top.

The ofrenda is a living tradition; this is an original paper design that credits it as tradition
(sources in the article). Every element is a generic shape: tiers, candles with flames, a round
loaf, an empty frame for a photograph, flowers and cut-paper flags. No skulls, no characters.

Composition of kernel builders (no cartridge's script is copied):

* `pliego.popup.cut_fold` — the altar: tier k + 1 is a box standing in the corner where tier k's
  top meets the wall (nested at its A fold), so the tiers rise as a stepped altar against the
  wall; candles stand in the corners at the foot of each riser (B folds) and against the wall on
  the top tier, the loaf at the foot of the top tier, the frame on top. A candle's flame and the
  loaf's dome are crests that continue the front face past its top fold. All from the card.
* `pliego.foldcut.papel_picado` — each flag: folded in half, cut through both layers, checked,
  ironed flat, its hem folded over the string and glued; the flags are pinned along one line.
* kirigami marigolds (here): two orange discs per flower, petals cut on three sides and scored
  at their base, glued at the centre to the wall; the petals fold out, the inner disc further.

Kinematics (Tier R, exact). Every fold of the altar turns by the gutter angle γ (A and B folds
with the gutter, F folds against it), so every state is rigid and a linear blend is exact; the
petals are free hinges on discs glued to the wall, which the preview holds still. The script
checks closure, the papercut minimum feature (card, flowers, flags), that every flower is glued
on uncut wall clear of the altar, and that the banner and the flowers fit (fail loud).
"""

import math

import pliego


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


levels = round(float(PARAM(lambda: levels, 3)))                     # noqa: F821
card_width = float(PARAM(lambda: card_width, 180.0))                # noqa: F821
page_height = float(PARAM(lambda: page_height, 170.0))              # noqa: F821
tier_height = float(PARAM(lambda: tier_height, 22.0))               # noqa: F821
depth = float(PARAM(lambda: depth, 72.0))                           # noqa: F821
flowers = round(float(PARAM(lambda: flowers, 7)))                   # noqa: F821
flags = round(float(PARAM(lambda: flags, 5)))                       # noqa: F821
picado = str(PARAM(lambda: picado, "alternate"))                    # noqa: F821
stock = str(PARAM(lambda: stock, "cardstock-160"))                  # noqa: F821

MIN_FEATURE = {"cardstock-160": 1.5, "cardstock-250": 2.0}
if stock not in MIN_FEATURE:
    raise ValueError(f"ofrenda-popup: stock must be one of {tuple(MIN_FEATURE)}, got {stock!r}")
if picado not in ("alternate", "flower", "lattice"):
    raise ValueError(f"ofrenda-popup: picado must be alternate, flower or lattice, got {picado!r}")
if not 2 <= levels <= 7:
    raise ValueError(f"ofrenda-popup: levels must be an integer in [2, 7], got {levels}")
if not 0 <= flowers <= 11 or not 3 <= flags <= 6:
    raise ValueError("ofrenda-popup: flowers must be in [0, 11] and flags in [3, 6]")

N = levels
WD = pliego.clamp(card_width, 140.0, 240.0)
HP = pliego.clamp(page_height, 140.0, 240.0)
R = pliego.clamp(tier_height, 10.0, 30.0)
D1 = pliego.clamp(depth, 36.0, 120.0)
MINF = MIN_FEATURE[stock]
M = MINF + 0.6                       # uncut fold ends, clearance between cut features (mm)
FMINF = 1.5                          # the flowers' card (160 g/m²) minimum feature
OPEN, SHUT = 90.0, 176.0             # displayed gutter turn; closed (zero-thickness card)
BLOOM = (50.0, 75.0)                 # outer and inner petal discs
LIFT = 0.1                           # flowers sit this far in front of the wall
BAND = 0.25 * HP                     # the banner's band at the top of the wall
TOL = 1e-6
FLAG_COLOURS = ["#e8336d", "#f28c28", "#8e44ad", "#33a852", "#f6d32d", "#2a7de1"]
PETAL_COLOURS = ("#f08c00", "#f7b500")
STAND = (0.0, math.sqrt(0.5), math.sqrt(0.5), 0.0)     # wall page upright, front toward +z
UPRIGHT = (math.sqrt(0.5), 0.0, 0.0, math.sqrt(0.5))   # a loose sheet standing, front to +z


def L4(en, es, fr, pt):
    return {"en": en, "es": es, "fr": fr, "pt": pt}


if N * R > HP - BAND - 0.24 * HP:
    raise ValueError(f"ofrenda-popup: {N} tiers of {R:g} mm leave no wall for the flowers and the "
                     "banner; lower tier_height or levels, or raise page_height")
if D1 > HP - 12.0:
    raise ValueError("ofrenda-popup: the bottom tier is deeper than the floor page")

# ── the altar: a cut-fold tree on the card ───────────────────────────────────

card = pliego.Sheet("card", [(0, 0), (WD, 0), (WD, 2 * HP), (0, 2 * HP)], stock=stock,
                    grain_deg=0.0, front="#f3e7cf", back="#6b3f8f",
                    placement=pliego.Placement(origin=(WD / 2.0, HP, 0.0), rotation=STAND),
                    label=L4("Ofrenda card: wall and floor", "Tarjeta de la ofrenda: pared y "
                             "piso", "Carte de l'ofrenda : mur et sol",
                             "Cartão da oferenda: parede e chão"))
widths = [0.82 * WD * (1.0 - 0.5 * k / max(1, N - 1)) for k in range(N)]
depths = [D1 * (N - k) / N for k in range(N)]
tread = D1 / N                                       # what each tier leaves in front of the next
tiers = []
for k in range(N):
    lo, hi = WD / 2.0 - widths[k] / 2.0, WD / 2.0 + widths[k] / 2.0
    tiers.append(pliego.popup.Block(
        a=R, b=depths[k], lo=lo, hi=hi, at="a", name=f"tier-{k + 1}",
        label=L4(f"Tier {k + 1}", f"Nivel {k + 1}", f"Gradin {k + 1}", f"Nível {k + 1}")))
for k in range(N - 1):
    tiers[k].children.append(tiers[k + 1])
ornaments = {"candle": 0, "bread": 0, "frame": 0}


def flame(lo, hi, h):
    """A candle flame (crest past F, from the front panel into the top), centred on [lo, hi]."""
    c, w = (lo + hi) / 2.0, min(0.5 * (hi - lo - 2 * M), max(2.2, (MINF + 0.3) / 0.9))
    return [(c - w, 0.0), (c - 0.95 * w, 0.4 * h), (c - 0.8 * w, 0.68 * h), (c, h),
            (c + 0.8 * w, 0.68 * h), (c + 0.95 * w, 0.4 * h), (c + w, 0.0)]


def candle(y, w, tall, deep, at):
    """A candle: a box in a corner, its flame a crest; None when it cannot fit."""
    h = min(deep - M, 0.55 * tall, 7.0)
    if tall < 6.0 or deep < 5.0 or w < 2 * M + 2 * MINF or h < 2.5:
        return None
    ornaments["candle"] += 1
    return pliego.popup.Block(a=tall, b=deep, lo=y, hi=y + w, at=at, crest_side="fold",
                              crest_panel=2, crest=flame(y, y + w, h),
                              name=f"candle-{ornaments['candle']}",
                              label=L4("Candle", "Vela", "Bougie", "Vela"))


cw = pliego.clamp(0.05 * WD, 7.0, 10.0) + 2.0 * (MINF - 1.5)       # candle width
for k in range(N):
    host = tiers[k]
    room_tall = R - M - 0.5                                     # under the riser above
    room_deep = (tread if k > 0 else HP - D1) - M - 0.5         # the tread (or floor) in front
    if k == 0:
        tall, deep = min(1.3 * room_tall, R - M - 0.5), min(12.0, room_deep)
    else:
        tall, deep = min(0.8 * room_tall, room_tall), min(9.0, room_deep)
    for y in (host.lo + M + 2.0, host.hi - M - 2.0 - cw):
        c = candle(y, cw, tall, deep, "b")
        if c is not None:
            host.children.append(c)
top = tiers[-1]
fw = min(0.36 * widths[-1], 42.0)
fh = min(0.20 * HP, 0.9 * fw + 6.0)
fd = min(5.0, depths[-1] - M - 0.5)
if fd >= 3.0:
    top.children.append(pliego.popup.Block(a=fh, b=fd, lo=WD / 2 - fw / 2, hi=WD / 2 + fw / 2,
                                           at="a", name="photo-frame",
                                           label=L4("Photo frame", "Marco para la foto",
                                                    "Cadre pour la photo",
                                                    "Moldura para a foto")))
    ornaments["frame"] = 1
    for y in (WD / 2 - fw / 2 - M - 2.0 - cw, WD / 2 + fw / 2 + M + 2.0):
        c = candle(y, cw, min(0.6 * fh, 18.0), fd, "a")
        if c is not None and y > top.lo + M and y + cw < top.hi - M:
            top.children.append(c)
if N >= 2:                                   # the loaf, on the tread in front of the top tier
    bw = min(0.28 * widths[-1], 30.0)
    ba, bb = min(0.55 * R, R - M - 1.0), tread - M - 0.5
    dome = min(bb - M, 0.45 * bw, 9.0)
    if bb >= 5.0 and dome >= 2.5:
        c0, c1 = WD / 2 - bw / 2, WD / 2 + bw / 2
        pts = [(c0 + M, 0.0)]
        for j in range(1, 12):
            th = math.pi * j / 12
            pts.append((WD / 2 - (bw / 2 - M) * math.cos(th), 0.78 * dome * math.sin(th)))
        pts[6] = (WD / 2, dome)                                    # the little round top
        pts += [(c1 - M, 0.0)]
        top.children.append(pliego.popup.Block(a=ba, b=bb, lo=c0, hi=c1, at="b",
                                               crest_side="fold", crest_panel=2, crest=pts,
                                               name="pan-de-muerto",
                                               label=L4("Pan de muerto", "Pan de muerto",
                                                        "Pain des morts", "Pão dos mortos")))
        ornaments["bread"] = 1
cf = pliego.popup.cut_fold(card, (0.0, HP), (1.0, 0.0), (0.0, 1.0), [tiers[0]],
                           reach=(HP, HP), span=(0.0, WD), angle=OPEN, margin=M,
                           gutter_label=L4("Gutter (wall meets floor)", "Pliegue central (la "
                                           "pared se une al piso)", "Pliure (le mur rejoint "
                                           "le sol)", "Dobra central (a parede encontra o chão)"))
for p in cf.blocks:
    if p.block.name == "photo-frame":                    # the photo space: a window in front
        t0, t1 = 2.5, p.block.a - 2.5
        card.hole([cf.panel_point(p.index, 2, t, y) for t, y in
                   ((t0, p.block.lo + 2.5), (t1, p.block.lo + 2.5), (t1, p.block.hi - 2.5),
                    (t0, p.block.hi - 2.5))])
card.label_edge("wall-top", (0.0, 0.0), (WD, 0.0))
arr = card.build()
WALL = pliego.P(1.0, 1.0)                                # the wall: the preview's still face
rep = pliego.papercut.analyze(card, min_feature_mm=MINF)
if not rep.ok or rep.components != 1:
    raise ValueError("ofrenda-popup: card fails the papercut check: "
                     + "; ".join(i["detail"] for i in rep.issues if i["level"] == "error"))
foot = [[(q.x, q.y) for q in poly] for poly in cf.footprints()]

# ── kirigami marigolds: two discs per flower, glued to the wall ──────────────


def wall_xy(u, v):
    """World (x, y) of a wall point (sheet u, v); the wall stands in the plane z = 0."""
    return (WD / 2.0 - u, HP - v)


def marigold_disc(sid, radius, petals, rot, colour, label):
    """A disc with `petals` round-tipped petals cut on three sides, scored at their base."""
    rim = max(1.6, FMINF + 0.2)
    half = math.pi / petals
    gap = FMINF + 0.3                                     # card left between two petal bases
    rh, rt = max(0.36 * radius, (1.6 + gap) / (2.0 * math.sin(half))), radius - rim
    sheet = pliego.Sheet(sid, pliego.circle((radius, radius), radius, 32), stock="cardstock-160",
                         grain_deg=90.0, front=colour, back=colour, label=label)
    for k in range(petals):
        th = math.radians(rot) + 2 * half * k
        u, v = (math.cos(th), math.sin(th)), (-math.sin(th), math.cos(th))

        def P(r, t, u=u, v=v):
            return (radius + r * u[0] + t * v[0], radius + r * u[1] + t * v[1])
        wb = rh * math.sin(half) - gap / 2.0                         # half width at the base
        wm = max(wb, min((rt - 0.3 * (rt - rh)) * math.sin(half) - gap / 2.0, 0.3 * (rt - rh)))
        rm = rt - wm                                                  # rounded tip
        pts = [P(rh, -wb), P(rm, -wm)]
        pts += [P(rm + wm * math.sin(math.pi * j / 8), -wm * math.cos(math.pi * j / 8))
                for j in range(1, 8)]
        pts += [P(rm, wm), P(rh, wb)]
        sheet.cut(pts, name="petal-edge")
        sheet.crease(P(rh, -wb), P(rh, wb), "valley", BLOOM[0], treatment="score", name="petal")
    rp = pliego.papercut.analyze(sheet, min_feature_mm=FMINF, search_mm=3.0 * FMINF)
    if not rp.ok:
        raise ValueError(f"ofrenda-popup: {sid} fails the papercut check: "
                         + "; ".join(i["detail"] for i in rp.issues if i["level"] == "error"))
    return sheet


RF = pliego.clamp(0.07 * WD, 10.0, 15.0)
h_top = N * R + (fh if ornaments["frame"] else 0.0)            # top of the altar on the wall


def clear(cu, cv, rad):
    """True when a disc (sheet u, v, radius) lies on uncut wall, clear of the altar."""
    if not (rad + 3.0 <= cu <= WD - rad - 3.0 and BAND + rad <= cv <= HP - rad - 3.0):
        return False
    for poly in foot:
        xs, ys = [q[0] for q in poly], [q[1] for q in poly]
        dx = max(min(xs) - cu, 0.0, cu - max(xs))
        dy = max(min(ys) - cv, 0.0, cv - max(ys))
        if math.hypot(dx, dy) < rad + 3.0:
            return False
    return True


def arch(rf):
    """Flower centres evenly spaced along a half ellipse over the altar, or None."""
    base_h = N * R
    rx, ry = WD / 2.0 - rf - 4.0, h_top - base_h + rf + 3.0
    while HP - base_h - ry - rf > BAND:
        arc = [(WD / 2.0 - rx * math.cos(math.radians(8.0 + 164.0 * i / 400)),
                HP - base_h - ry * math.sin(math.radians(8.0 + 164.0 * i / 400)))
               for i in range(401)]
        run = [0.0]
        for p0, p1 in zip(arc, arc[1:], strict=False):
            run.append(run[-1] + math.dist(p0, p1))
        want = ([run[-1] * j / (flowers - 1) for j in range(flowers)] if flowers > 1
                else [run[-1] / 2.0])
        pts = [arc[min(range(401), key=lambda i, w=w: abs(run[i] - w))] for w in want]
        if all(clear(u, v, rf) for u, v in pts) and all(
                math.dist(p, q) >= 2 * rf + 1.0 for i, p in enumerate(pts) for q in pts[i + 1:]):
            return pts
        ry += 1.0
    return None


centres = []
while flowers and not centres:               # shrink the flowers until the arch fits
    centres = arch(RF) or []
    if not centres:
        RF -= 0.5
        if RF < 8.0:
            raise ValueError(f"ofrenda-popup: {flowers} flowers do not fit in an arch over the "
                             "altar; use fewer flowers or a taller card")
flower_sheets, petal_hinges, joins, initial = [], [], [], {}
RI = 0.70 * RF                               # inner disc; petal counts that cut cleanly
LAYERS = ((RF, 10 if RF >= 9.0 else 8, 0.0), (RI, 7 if RI >= 7.0 else (6 if RI >= 6.3 else 5),
                                               18.0))
templates = [marigold_disc(f"marigold-{layer}", rad, n, rot, PETAL_COLOURS[layer], None)
             for layer, (rad, n, rot) in enumerate(LAYERS)] if centres else []
if len(templates) == 2 and \
        pliego.foldcut.material_min_area(templates[1].build()) < 1.1 * FMINF ** 2:
    templates, LAYERS = templates[:1], LAYERS[:1]   # inner petals below the face-area floor
for j, (cu, cv) in enumerate(centres):
    x, y = wall_xy(cu, cv)
    for layer, (rad, _n, _rot) in enumerate(LAYERS):
        sid = f"marigold-{j + 1}-{'outer' if layer == 0 else 'inner'}"
        lab = L4(f"Marigold {j + 1}, {'outer' if layer == 0 else 'inner'} petals",
                 f"Cempasúchil {j + 1}, pétalos {'exteriores' if layer == 0 else 'interiores'}",
                 f"Rose d'Inde {j + 1}, pétales {'extérieurs' if layer == 0 else 'intérieurs'}",
                 f"Cravo-de-defunto {j + 1}, pétalas {'externas' if layer == 0 else 'internas'}")
        sheet = templates[layer].copy(sid, label=lab)
        hinges = [m for m in sheet.marks if m.name == "petal"]
        z = LIFT * (layer + 1)
        sheet.placement = pliego.Placement(origin=(x - rad, y - rad, z), rotation=UPRIGHT)
        c = 0.20 * rad                                         # glue at the centre
        region = [(rad - c, rad - c), (rad + c, rad - c), (rad + c, rad + c), (rad - c, rad + c)]
        if layer == 0:                                         # disc → card (u = WD/2 − x)
            mp = (-1.0, 0.0, 0.0, -1.0, WD / 2.0 - (x - rad), HP - (y - rad))
            joins.append(pliego.glue(f"{sid}-glue", sheet, region, card, mp, "front"))
        else:                                                  # inner disc → outer disc
            mp = (1.0, 0.0, 0.0, 1.0, RF - rad, RF - rad)        # same centre
            joins.append(pliego.glue(f"{sid}-glue", sheet, region,
                                     flower_sheets[-1], mp, "front"))
        flower_sheets.append(sheet)
        petal_hinges += [(m, BLOOM[layer]) for m in hinges]
        initial[sid] = {"angles": {m: BLOOM[layer] for m in hinges}, "root": (rad, rad)}

# ── the papel picado banner ──────────────────────────────────────────────────

edge, gap = 8.0, 4.0
pw = (WD - 2 * edge - (flags - 1) * gap) / flags
ph = min(BAND - 6.0, 1.35 * pw)
hem = pliego.clamp(0.12 * ph, 4.0, 7.0)
if pw < 22.0 or ph < 30.0:
    raise ValueError("ofrenda-popup: the flags would be too small to cut; use fewer flags")
cx = pw / 2.0
field = ph - 2 * hem - 1.5


def motif(kind):
    """Original motifs in the folded half (x ≥ pw/2): regions to cut out."""
    pc = pliego.papercut
    y0 = 3.0 + 2.2                             # above the picos fringe
    span = field - y0
    cy = y0 + 0.5 * span
    out = []
    if kind == "flower":                       # a rosette with a diamond at each top corner
        r = min(0.30 * pw, 0.42 * span)
        for a in (-90.0, -45.0, 0.0, 45.0, 90.0):
            out.append([(q.x, q.y) for q in pc.petal((cx, cy), r, 0.42 * r, a, segments=6)])
        out.append([(q.x, q.y) for q in pc.disc((cx, cy), 0.16 * r, 10)])
        d = min(0.12 * pw, 0.18 * span)
        if d >= 3.5:                           # room for a corner diamond
            out.append([(q.x, q.y) for q in pc.diamond(
                (pw - 2.0 - d / 2 - 1.6, field - 0.6 * d - 0.2), d, 1.2 * d)])
    else:                                      # three diamonds beside a central lozenge
        out.append([(cx - 0.1, cy - 0.42 * span), (cx + 0.16 * pw, cy),
                    (cx - 0.1, cy + 0.42 * span)])
        dh = min(0.22 * span, 0.16 * pw * 1.3)
        for f in (0.17, 0.5, 0.83):
            out.append([(q.x, q.y) for q in pc.diamond((cx + 0.32 * pw, y0 + f * span),
                                                       0.13 * pw, dh)])
    teeth = max(2, round(pw / 2 / 5.0))        # picos: zigzag fringe along the bottom edge
    step = (pw / 2) / teeth
    fringe = [(cx - 0.5, -1.0), (cx - 0.5, 0.0)]
    for t in range(teeth):
        fringe += [(cx + t * step + step / 2, 3.0), (cx + (t + 1) * step, 0.0)]
    fringe += [(pw + 1.0, 0.0), (pw + 1.0, -1.0)]
    out.append(fringe)
    return out


kinds = {"alternate": ["flower", "lattice"], "flower": ["flower"], "lattice": ["lattice"]}[picado]
string_y = HP - 6.0                                   # world height of the string
flag_sheets = []
for k in range(flags):
    kind = kinds[k % len(kinds)]
    x0 = -WD / 2.0 + edge + k * (pw + gap)
    pp = pliego.foldcut.papel_picado(
        f"flag-{k + 1}", pw, ph, motif(kind), hem=hem, symmetry=1, min_feature=1.5,
        front=FLAG_COLOURS[k % len(FLAG_COLOURS)],
        label=L4(f"Papel picado flag {k + 1}", f"Banderita de papel picado {k + 1}",
                 f"Fanion de papel picado {k + 1}", f"Bandeirinha de papel picado {k + 1}"),
        placement=pliego.Placement(origin=(x0, string_y - (ph - hem), 0.4), rotation=UPRIGHT))
    flag_sheets.append(pp.sheet)
    joins.append(pp.hem_glue(f"flag-{k + 1}-hem"))
    joins.append(pliego.pin(f"flag-{k + 1}-string", along=(pp.sheet, [(0.0, ph - hem),
                                                                      (pw, ph - hem)])))
    initial[pp.sheet.id] = {"angles": {pp.hem: -180.0}, "root": (pw / 2.0, 2.0)}
joins.append(pliego.pin("wall-hold", along=(card, [(0.0, 0.0), (WD, 0.0)])))

# ── self-checks and the program ──────────────────────────────────────────────

initial["card"] = {"angles": cf.angles(OPEN), "root": (WALL.x, WALL.y)}
worst = max(cf.residual([0.0, OPEN, (OPEN + SHUT) / 2.0, SHUT], root=WALL), 0.0)
if worst > TOL:
    raise ValueError(f"ofrenda-popup: the altar is not a rigid state ({worst:.3g} mm)")
if h_top > HP - BAND - (2 * RF if flowers else 0.0):
    raise ValueError("ofrenda-popup: the altar reaches the banner; lower the tiers")

petal_marks = [m for m, _ in petal_hinges]
steps = []
if petal_marks:
    steps.append(pliego.Step("press-flowers", L4("Press the marigolds flat",
                                                 "Aplana las flores de cempasúchil",
                                                 "Aplatir les roses d'Inde",
                                                 "Achate as flores de cravo-de-defunto"),
                             [(m, 0.0) for m in petal_marks], duration_ms=1500))
steps += [
    pliego.Step("close", L4("Close the card: the altar folds flat inside",
                            "Cierra la tarjeta: el altar se pliega por dentro",
                            "Fermez la carte : l'autel se replie à l'intérieur",
                            "Feche o cartão: o altar se dobra por dentro"),
                [(m, sg * SHUT) for m, sg in cf.marks], duration_ms=3000),
    pliego.Step("open", L4(f"Open the card to 90°: the {N} levels of the ofrenda rise",
                           f"Abre la tarjeta a 90°: se levantan los {N} niveles de la ofrenda",
                           f"Ouvrez la carte à 90° : les {N} gradins de l'ofrenda se dressent",
                           f"Abra o cartão a 90°: erguem-se os {N} níveis da oferenda"),
                [(m, sg * OPEN) for m, sg in cf.marks], duration_ms=3500,
                note=L4("Every level is a box cut into the corner of the one below; candles, "
                        "the loaf and the frame are smaller boxes in the corners.",
                        "Cada nivel es una caja cortada en la esquina del de abajo; las velas, "
                        "el pan y el marco son cajas más pequeñas en las esquinas.",
                        "Chaque gradin est une boîte découpée dans l'angle de celui du dessous ; "
                        "les bougies, le pain et le cadre sont de plus petites boîtes dans les "
                        "angles.",
                        "Cada nível é uma caixa cortada no canto do de baixo; as velas, o pão e "
                        "a moldura são caixas menores nos cantos.")),
]
if petal_marks:
    steps.append(pliego.Step("bloom", L4("The marigolds open", "Se abren las flores de "
                                         "cempasúchil", "Les roses d'Inde s'ouvrent",
                                         "As flores de cravo-de-defunto se abrem"),
                             [(m, a) for m, a in petal_hinges], duration_ms=1800))

print(f"ofrenda: levels={N} card={WD:g}x{HP:g}x2mm tier={R:g}mm depth={D1:g}mm "
      f"candles={ornaments['candle']} bread={ornaments['bread']} frame={ornaments['frame']} "
      f"flowers={len(centres)} flags={flags}x{pw:.1f}x{ph:.1f}mm picado={picado} "
      f"closure={worst:.1e}mm bridge={rep.min_bridge_mm:.2f}mm>={MINF:g} faces={len(arr.faces)}")

result = pliego.Assembly(
    [card] + flower_sheets + flag_sheets,
    joins=joins,
    controls=[pliego.sequence_control(label=L4("Close and open", "Cerrar y abrir",
                                               "Fermer et ouvrir", "Fechar e abrir"),
                                      default=float(len(steps)))],
    sequence=pliego.Sequence(steps, mode="kinematic"),
    initial=initial,
    title="Ofrenda pop-up",
    min_feature_mm=min(MINF, FMINF),            # the smallest intended feature: flowers, flags
)
