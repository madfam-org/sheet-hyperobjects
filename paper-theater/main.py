"""Paper theatre — sheet-hyperobjects cartridge (Pliego).

A toy theatre in card: a stage platform, a proscenium with a curtain and valance, pairs of wings,
a ground row and a backdrop, all standing on the stage floor by tabs pushed through slits and
folded under, and a flat that slides in from the right wing.

* The **stage** is one scored sheet: the floor, and a band of four skirts hinged to its front edge
  that wraps round under the floor's edges (flaps on the band's top edge are glued under the floor,
  a tab closes the band at the front-left corner). The floor carries one slit per tab.
* The **pieces** (proscenium, `wings` pairs of wings, ground row, backdrop) are cards whose bottom
  edges carry tabs; each tab goes through its slit and folds back flat under the floor.
* The **flat** stands on a folded foot whose long handle runs out past the right side of the stage,
  as on the slides of nineteenth-century toy theatres. It is a rigid (kinematic) sheet moved by a
  `translate` mechanism: the `slide-in` control brings it from behind the right wing to the
  centre of the stage, and the studio preview plays it.

The fold program folds the stage band and locks the tabs. The studio roots each sheet's face tree
on the face holding its lowest-left vertex; for the stage that is the floor, which therefore stays
in place while the band wraps round it. Scenes (`forest`, `street`, `seaside`) are original shapes
generated here; every piece is checked with `pliego.papercut.analyze`, and the folded band is
checked closed under the floor.
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


scene = str(PARAM(lambda: scene, "forest"))                  # noqa: F821
width = float(PARAM(lambda: width, 240.0))                   # noqa: F821
depth = float(PARAM(lambda: depth, 150.0))                   # noqa: F821
wings = round(float(PARAM(lambda: wings, 3)))                # noqa: F821
stock = str(PARAM(lambda: stock, "cardstock-300"))           # noqa: F821

SCENES = ("forest", "street", "seaside")
if scene not in SCENES:
    raise ValueError(f"paper-theater: scene must be one of {SCENES}, got {scene!r}")
if stock not in ("cardstock-250", "cardstock-300"):
    raise ValueError(f"paper-theater: stock must be cardstock-250 or cardstock-300, got {stock!r}")
if not 2 <= wings <= 4:
    raise ValueError(f"paper-theater: wings must be an integer in [2, 4], got {wings}")

W = pliego.clamp(width, 180.0, 360.0)
D = pliego.clamp(depth, 110.0, 240.0)
SH = 30.0                              # stage platform height
HP = round(0.72 * W, 1)                # proscenium height
PW = 0.13 * W                          # proscenium posts
HT = 0.2 * HP                          # proscenium header
SILL = 8.0
WW = 0.25 * W                          # wing width
HW = HP - HT + 6.0                     # wings reach just behind the header
MINF = 2.0                             # papercut minimum feature of 250/300 g/m² card
NECK = 1.6 * MINF
TW, TD = 14.0, 0.6 * SH                # tab width and depth
FLAP = 10.0                            # band flaps glued under the floor
GLUE = 12.0                            # band closing tab
DELTA = 0.5                            # the band starts 0.5 mm in from the floor's left corner
IN = 89.0
TOL = 1e-4
SEED = {"forest": 1.0, "street": 2.0, "seaside": 3.0}[scene]


def rnd(i):
    v = math.sin(i * 12.9898 + SEED * 78.233) * 43758.5453
    return v - math.floor(v)


def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def arc(cx, cy, r, a0, a1, n=12):
    return [(cx + r * math.cos(a0 + (a1 - a0) * i / n), cy + r * math.sin(a0 + (a1 - a0) * i / n))
            for i in range(n + 1)]


def clean(ring):
    out = []
    for p in ring:
        if not out or math.dist(p, out[-1]) > 0.05:
            out.append(p)
    if len(out) > 3 and math.dist(out[0], out[-1]) <= 0.05:
        out.pop()
    return out


def mirror(ring, w):
    """The same outline flipped left ↔ right (still counter-clockwise)."""
    return [(w - x, y) for x, y in reversed(ring)]


def with_tabs(bottom_right, centres):
    """Bottom edge from (0, 0) to (bottom_right, 0) with a tab under each centre."""
    pts = [(0.0, 0.0)]
    for xc in sorted(centres):
        pts += [(xc - TW / 2, 0.0), (xc - TW / 2 + 2.0, -TD), (xc + TW / 2 - 2.0, -TD),
                (xc + TW / 2, 0.0)]
    return pts + [(bottom_right, 0.0)]


# ── pieces: (id, label, outline, holes, tab centres, x, z); local y is up from the floor ──
pieces = []
WO = W - 2 * PW
yo_top = HP - HT


def curtain(y):                        # curtain width at height y: drawn back to a tie-back
    tie = SILL + 0.42 * (yo_top - SILL)
    if y >= tie:
        t = (y - tie) / (yo_top - tie)
        return 0.035 * WO + (0.12 * WO - 0.035 * WO) * t ** 0.8
    t = (tie - y) / (tie - SILL)
    return 0.035 * WO + (0.075 * WO - 0.035 * WO) * t ** 1.5


vd = 0.1 * (yo_top - SILL)
ys = [SILL + (yo_top - 0.4 * vd - SILL) * i / 16 for i in range(17)]
opening = [(PW + curtain(SILL), SILL), (W - PW - curtain(SILL), SILL)]
opening += [(W - PW - curtain(y), y) for y in ys[1:]]
xv0, xv1 = PW + curtain(ys[-1]), W - PW - curtain(ys[-1])
for k in range(5, 0, -1):
    xa = xv0 + (xv1 - xv0) * k / 5
    opening += [(xa - (xv1 - xv0) / 5 * i / 8,
                 yo_top - vd * (0.4 + 0.6 * math.sin(math.pi * i / 8))) for i in range(1, 9)]
opening += [(PW + curtain(y), y) for y in reversed(ys[:-1])]
cr = 0.12 * W
prosc = with_tabs(W, [PW / 2, W - PW / 2]) + [(W, HP), (W / 2 + cr, HP)]
prosc += arc(W / 2, HP, cr, 0.0, math.pi, 16)[1:-1] + [(W / 2 - cr, HP), (0.0, HP)]
pieces.append(("proscenium", L4("Proscenium", "Proscenio", "Cadre de scène", "Proscênio"),
               clean(prosc), [clean(opening)], [PW / 2, W - PW / 2], 0.0, D - 6.0))


def wing_edge(k):
    """Inner edge of a left wing, bottom → top, and its holes (x = WW is the stage side)."""
    h = HW
    if scene == "forest":
        xt = 0.45 * WW
        r = 0.55 * h / 6
        pts = [(xt, 0.0), (xt, 0.45 * h)]
        for b in range(3):
            pts += arc(WW - r, 0.45 * h + (2 * b + 1) * r, r, -math.pi / 2, math.pi / 2, 10)
        return pts + [(WW - r, h)], []
    if scene == "street":
        xw, y0 = 0.82 * WW, 0.6 * h
        dx, dy = 0.17 * WW, 0.1 * h
        pts = [(xw, 0.0), (xw, y0)]
        for i in range(3):
            pts += [(xw - i * dx, y0 + (i + 1) * dy), (xw - (i + 1) * dx, y0 + (i + 1) * dy)]
        holes = []
        for r_ in range(3):
            for c_ in range(2):
                wx, wy = 0.14 * WW + c_ * 0.34 * WW, 0.12 * h + r_ * 0.16 * h
                holes.append(rect(wx, wy, wx + 0.2 * WW, wy + 0.1 * h))
        return pts + [(xw - 3 * dx, h)], holes
    pts = [(0.78 * WW, 0.0)]
    n = 7
    for i in range(1, n):
        pts.append((WW * (0.55 + 0.4 * rnd(13 * k + i)), h * i / n))
    return pts + [(0.4 * WW, h)], []


passages = []
for k in range(1, wings + 1):
    z = D - 6.0 - (D - 32.0) * k / (wings + 0.6)
    edge, holes = wing_edge(k)
    left = clean(with_tabs(edge[0][0], [edge[0][0] / 2]) + edge + [(0.0, HW)])
    lab = L4(f"Wing {k}", f"Bastidor {k}", f"Coulisse {k}", f"Bastidor {k}")
    tc = edge[0][0] / 2
    pieces.append((f"wing-{k}-left", lab, left, holes, [tc], 0.0, z))
    pieces.append((f"wing-{k}-right", lab, mirror(left, WW), [mirror(h, WW) for h in holes],
                   [WW - tc], W - WW, z))
    passages.append(z)

GW, GH = W - 30.0, 0.22 * HP
if scene == "forest":
    top = []
    for i in range(9, -1, -1):
        x = GW * i / 9
        y = GH * (0.55 + 0.15 * math.sin(i * 1.3 + SEED))
        top.append((x, y))
        if 0 < i < 9 and i % 2 == 1:
            top = top[:-1] + [(x + 6.0, y), (x, min(GH * 1.0, y + 0.4 * GH)), (x - 6.0, y)]
elif scene == "street":
    top, x, i = [], GW, 0
    while x > 0:
        bw = min(x, GW * (0.1 + 0.06 * rnd(20 + i)))
        h = GH * (0.45 + 0.35 * rnd(30 + i))
        top += [(x, h), (x - bw / 2, h + 0.4 * bw), (x - bw, h)]
        x, i = x - bw, i + 1
else:
    top = [(GW - GW * i / 48, GH * (0.45 + 0.18 * (1 - abs(math.sin(math.pi * i / 8))) ** 1.6))
           for i in range(49)]
ground_row = clean(with_tabs(GW, [0.25 * GW, 0.75 * GW]) + top)
pieces.append(("ground-row", L4("Ground row", "Rompimiento bajo", "Ferme basse",
                                  "Praticável baixo"),
               ground_row, [], [0.25 * GW, 0.75 * GW], 15.0, 20.0))
BW, BH = W - 10.0, HP - HT + 12.0
pieces.append(("backdrop", L4("Backdrop", "Telón de fondo", "Toile de fond", "Pano de fundo"),
               clean(with_tabs(BW, [0.2 * BW, 0.5 * BW, 0.8 * BW]) + [(BW, BH), (0.0, BH)]), [],
               [0.2 * BW, 0.5 * BW, 0.8 * BW], 5.0, 8.0))

# ── the flat: a scene piece on a base strip, a folded foot and a long handle ──
WF, HFL, BS = WW - 6.0, 0.36 * HP, 5.0
if scene == "forest":                                  # a cottage with a chimney, door, window
    ew, ey = 0.06 * WF, BS + 0.5 * HFL

    def roof(x):
        return HFL - (x - WF / 2) / (WF / 2) * (HFL - ey)

    ct = roof(0.62 * WF) + 0.1 * HFL
    shape = [(WF, BS), (WF - ew, BS), (WF - ew, ey), (WF, ey), (0.72 * WF, roof(0.72 * WF)),
             (0.72 * WF, ct), (0.62 * WF, ct), (0.62 * WF, roof(0.62 * WF)), (WF / 2, HFL),
             (0.0, ey), (ew, ey), (ew, BS)]
    holes = [rect(0.2 * WF, BS + 2.0, 0.36 * WF, BS + 0.36 * HFL),
             rect(0.55 * WF, BS + 0.18 * HFL, 0.78 * WF, BS + 0.36 * HFL)]
elif scene == "street":                                # a coach: body, roof, two wheels
    rw = 0.16 * HFL
    yb = BS + 1.4 * rw
    cf, cr_ = (0.74 * WF, BS + 0.8 * rw), (0.26 * WF, BS + 0.8 * rw)

    def wheel(c, a0, a1):
        return arc(c[0], c[1], rw, a0, a1, 10)

    lo = math.asin((BS - cf[1]) / rw)
    hi = math.asin((yb - cf[1]) / rw)
    shape = [(WF, BS)] + wheel(cf, lo, hi) + [(0.9 * WF, yb), (0.9 * WF, yb + 0.4 * HFL)]
    shape += arc(WF / 2, yb + 0.4 * HFL, 0.4 * WF, 0.0, math.pi, 12)[1:-1]
    shape += [(0.1 * WF, yb + 0.4 * HFL), (0.1 * WF, yb)]
    shape += wheel(cr_, math.pi - hi, math.pi - lo)
    gap = wheel(cr_, lo, hi) + wheel(cf, math.pi - hi, math.pi - lo)
    holes = [clean(gap), rect(0.38 * WF, yb + 0.12 * HFL, 0.62 * WF, yb + 0.32 * HFL)]
else:                                                  # a sailboat on a wave
    hb, deck = 0.4 * WF, BS + 0.14 * HFL
    mast, mw = HFL, NECK
    shape = [(WF, BS), (0.5 * WF + hb, BS + 3.0), (0.5 * WF + 1.15 * hb, deck),
             (0.5 * WF + mw / 2, deck), (0.5 * WF + mw / 2, deck + 6.0),
             (0.5 * WF + 0.95 * hb, deck + 6.0), (0.5 * WF + mw / 2, mast),
             (0.5 * WF - mw / 2, mast), (0.5 * WF - mw / 2, deck), (0.5 * WF - 1.15 * hb, deck),
             (0.5 * WF - hb, BS + 3.0)]
    holes = []
FD = min(14.0, 0.4 * (passages[0] - passages[1]))   # foot depth (it lies on the floor)
C = 1.0
X_START = W - WW + 3.0                                 # hidden behind the right wing of row 1
TRAVEL = X_START - (W / 2 - WF / 2)
HANDLE = TRAVEL + 40.0
flat_ring = clean([(0.0, 0.0), (C, 0.0), (C, -FD), (WF + HANDLE, -FD), (WF + HANDLE, -FD + 8.0),
                   (WF - C, -FD + 8.0), (WF - C, 0.0), (WF, 0.0)] + shape + [(0.0, BS)])
Z_FLAT = 0.5 * (passages[0] + passages[1])

# ── self-checks of every piece (papercut) and build the sheets ──
STAND = (math.sqrt(0.5), 0.0, 0.0, math.sqrt(0.5))   # (u, v) → world (x = u, y = v), front +Z
sheets, tabs, slits, bridges, roots = [], [], [], [], {}
for pid, label, ring, holes, centres, x0, z in pieces + [("flat", None, flat_ring, holes, [],
                                                           X_START, Z_FLAT)]:
    probe = pliego.Sheet(f"probe-{pid}", ring, stock=stock)
    for h in holes:
        probe.hole(h)
    rep = pliego.papercut.analyze(probe, min_feature_mm=MINF)
    if not rep.ok or rep.components != 1:
        raise ValueError(f"paper-theater: {pid} fails the papercut check: " + "; ".join(
            i["detail"] for i in rep.issues if i["level"] == "error"))
    bridges.append(rep.min_bridge_mm)
    roots[pid] = next((x, 1.0) for x in [0.5 + i for i in range(int(W))]
                      if probe.region_contains((x, 1.0)))
    if pid == "flat":
        continue
    sh = pliego.Sheet(pid, ring, stock=stock, grain_deg=90.0, label=label,
                      placement=pliego.Placement(origin=(x0, SH, z), rotation=STAND))
    for h in holes:
        sh.hole(h)
    for xc in centres:
        tabs.append(sh.crease((xc - TW / 2, 0.0), (xc + TW / 2, 0.0), "mountain", IN,
                              treatment="score", name="tab"))
        slits.append(((x0 + xc - TW / 2 - 0.5, z), (x0 + xc + TW / 2 + 0.5, z)))
    sheets.append(sh)

flat = pliego.Sheet("flat", flat_ring, stock=stock, grain_deg=90.0, kinematic="slide-in",
                    label=L4("Flat on its slide", "Figura con su corredera",
                             "Figurine sur sa coulisse", "Figura na sua corrediça"),
                    placement=pliego.Placement(origin=(X_START, SH, Z_FLAT), rotation=STAND))
for h in holes:
    flat.hole(h)
foot = flat.crease((C, 0.0), (WF - C, 0.0), "mountain", 90.0, treatment="score", name="foot")
flat.label_edge("handle", (WF + HANDLE, -FD), (WF + HANDLE, -FD + 8.0))

# ── the stage: floor (root) and a band of skirts hinged to its front edge ──
band = [W - DELTA, D, W, D]            # front, right, back, left skirt lengths
ub = [DELTA]
for L_ in band:
    ub.append(ub[-1] + L_)


outline = [(0.0, 0.0), (DELTA, 0.0), (DELTA, -SH), (ub[4], -SH), (ub[4] + GLUE, -SH + 3.0),
           (ub[4] + GLUE, -3.0), (ub[4], 0.0)]
for i in (3, 2, 1):
    a, b = ub[i], ub[i + 1]
    outline += [(b - C, 0.0), (b - C - FLAP, FLAP), (a + C + FLAP, FLAP), (a + C, 0.0)]
outline += [(W, 0.0), (W, D), (0.0, D)]
stage = pliego.Sheet("stage", outline, stock="cardstock-300", grain_deg=0.0,
                     placement=pliego.Placement(origin=(0.0, SH, D)),
                     label=L4("Stage (one scored sheet)", "Escenario (una hoja hendida)",
                              "Scène (une feuille rainée)", "Palco (uma folha vincada)"))
for (xa, za), (xb, zb) in slits:
    stage.cut([(xa, D - za), (xb, D - zb)], name="slot")


def mscore(sheet, a, b, ang, en, es, fr, pt, name=None):
    return sheet.crease(a, b, "mountain", ang, treatment="score", label=L4(en, es, fr, pt),
                        name=name)


front = mscore(stage, (DELTA, 0.0), (W, 0.0), 90.0, "Fold the front skirt down",
               "Dobla hacia abajo el faldón delantero", "Rabattre la jupe avant",
               "Dobre para baixo a saia da frente")
corners = [mscore(stage, (ub[i], 0.0), (ub[i], -SH), 90.0, "Corner", "Esquina", "Coin", "Canto")
           for i in (1, 2, 3)]
closing = mscore(stage, (ub[4], -SH + 0.0), (ub[4], 0.0), IN, "Closing tab", "Pestaña de cierre",
                 "Patte de fermeture", "Aba de fecho", name="glue-tab")
flaps = [mscore(stage, (ub[i] + C, 0.0), (ub[i + 1] - C, 0.0), IN, "Flap under the floor",
                "Solapa bajo el piso", "Rabat sous le plancher", "Aba sob o piso",
                name="glue-flap") for i in (1, 2, 3)]
stage.label_edge("floor-front", (DELTA, 0.0), (W, 0.0))

# ── self-check: the band closes round the floor and the flaps lie under it ──
ANG = {front: -90.0, closing: -IN}
ANG.update({m: -90.0 for m in corners})
ANG.update({m: -IN for m in flaps})
arr = stage.build()
pose = kinematics.pose_arrangement(arr, {e: a for m, a in ANG.items() for e in m.edges()},
                                   pliego.P(W / 2, D / 2))


def at(u, v):
    for i, p in enumerate(arr.vertices):
        if abs(p.x - u) < 1e-6 and abs(p.y - v) < 1e-6:
            x, y, z = pose[i]
            return (x, y + SH, z + D)
    raise ValueError(f"paper-theater: no stage vertex at ({u}, {v})")


expect = {(ub[1], 0.0): (W, SH, D), (ub[2], 0.0): (W, SH, 0.0), (ub[3], 0.0): (0.0, SH, 0.0),
          (ub[4], 0.0): (0.0, SH, D), (ub[4], -SH): (0.0, 0.0, D), (ub[2], -SH): (W, 0.0, 0.0)}
worst = max(math.dist(at(*uv), xyz) for uv, xyz in expect.items())
if worst > TOL:
    raise ValueError(f"paper-theater: the stage band does not close: {worst:.3g} mm")
print(f"paper-theater: scene={scene} stage={W:g}x{D:g}x{SH:g}mm proscenium={W:g}x{HP:g}mm "
      f"opening={WO:.0f}mm wings={wings} pieces={len(sheets)} tabs={len(tabs)} "
      f"band_closed={worst:.1e}mm flat_travel={TRAVEL:.1f}mm "
      f"bridges>={min(b for b in bridges if b is not None):.1f}mm (min {MINF:g})")

steps = [
    pliego.Step("band-flaps", L4("Fold in the flaps on the band's top edge",
                                 "Dobla hacia dentro las solapas del borde de la banda",
                                 "Repliez les rabats du bord de la bande",
                                 "Dobre para dentro as abas da borda da faixa"),
                [(m, -IN) for m in flaps], duration_ms=1200),
    pliego.Step("front-skirt", L4("Fold the front skirt down under the floor's front edge",
                                  "Dobla el faldón delantero bajo el borde del piso",
                                  "Rabattez la jupe avant sous le bord du plancher",
                                  "Dobre a saia da frente sob a borda do piso"),
                [(front, -90.0)], duration_ms=1500),
    pliego.Step("right-skirt", L4("Fold the right skirt back", "Dobla hacia atrás el faldón "
                                  "derecho", "Rabattez la jupe droite", "Dobre para trás a saia "
                                  "direita"), [(corners[0], -90.0)], duration_ms=1300),
    pliego.Step("back-skirt", L4("Fold the back skirt across", "Dobla el faldón trasero",
                                 "Rabattez la jupe arrière", "Dobre a saia de trás"),
                [(corners[1], -90.0)], duration_ms=1300),
    pliego.Step("left-skirt", L4("Fold the left skirt and glue the closing tab inside the front",
                                 "Dobla el faldón izquierdo y pega la pestaña de cierre por "
                                 "dentro del frente", "Rabattez la jupe gauche et collez la patte "
                                 "de fermeture derrière l'avant", "Dobre a saia esquerda e cole a "
                                 "aba de fecho por dentro da frente"),
                [(corners[2], -90.0), (closing, -IN)], duration_ms=1500,
                note=L4("Glue the band's flaps under the floor.",
                        "Pega las solapas de la banda bajo el piso.",
                        "Collez les rabats de la bande sous le plancher.",
                        "Cole as abas da faixa sob o piso.")),
    pliego.Step("lock-tabs", L4("Push every tab through its slit and fold it back under the floor",
                                "Pasa cada pestaña por su ranura y dóblala hacia atrás bajo el "
                                "piso", "Passez chaque patte dans sa fente et repliez-la sous le "
                                "plancher", "Passe cada aba pela sua fenda e dobre-a para trás "
                                "sob o piso"),
                [(m, -IN) for m in tabs], duration_ms=2000),
]
done = {"stage": {"angles": dict(ANG), "root": (W / 2, D / 2)}}
for sh in sheets:
    done[sh.id] = {"angles": {m: -IN for m in tabs if m.sheet is sh}, "root": roots[sh.id]}
done["flat"] = {"angles": {foot: -90.0}, "root": (WF / 2, BS / 2)}
result = pliego.Assembly(
    [stage] + sheets + [flat],
    mechanisms=[pliego.translate("slide-in", "slide-in", (-1.0, 0.0, 0.0), TRAVEL, [flat])],
    controls=[pliego.sequence_control(label=L4("Build the theatre", "Armar el teatro",
                                               "Monter le théâtre", "Montar o teatro")),
              pliego.control("slide-in", "distance", L4(
                  "Slide the flat in", "Deslizar la figura", "Faire glisser la figurine",
                  "Deslizar a figura"), default=TRAVEL, min=0.0, max=TRAVEL, unit="mm")],
    sequence=pliego.Sequence(steps, mode="kinematic"),
    initial={"flat": {"angles": {foot: -90.0}, "root": (WF / 2, BS / 2)}},
    targets={"assembled": done},
    title="Paper theatre",
)
