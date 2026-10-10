"""Fastener joins — sheet-hyperobjects cartridge (Pliego).

Mechanical joins in card: two cards held together by hardware or thread instead of glue. One mode
per fastener:

* `brad`, `eyelet`, `rivet` — pivoting fasteners. An arm (a strip with round ends) turns on a
  base card about a fastener through a hole in both. The arm is a kinematic sheet moved by a
  `rotate` mechanism about the hole's centre (the `swing` angle control). As in the volvelle, the
  hardware is the mechanism's centre, not a `pivot` join: a join between the turning arm and the
  fixed base would leave the control to the physics engine.
* `staple`, `stitch` — fixed fasteners along an edge. A cover lies on a base; two staples, or a
  running stitch through pierced stations, hold the cover's margin to the base, and the cover
  opens on a score line just inside the fastening, the way a stapled or side-sewn booklet opens.
  Every staple leg and every stitch station is a `pivot` join (its two points coincide; two or more
  of them hold the margin rigidly), and the opening is a fold program on the cover's score line.

The hardware itself (brads, eyelets, rivets, staples, thread) is not paper and is not modelled as
a sheet; its holes and piercing marks are.
"""

import math

import pliego


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


mode = PARAM(lambda: mode, "brad")                             # noqa: F821
card_width = float(PARAM(lambda: card_width, 120.0))           # noqa: F821
card_height = float(PARAM(lambda: card_height, 80.0))          # noqa: F821
arm_length = float(PARAM(lambda: arm_length, 95.0))            # noqa: F821
arm_width = float(PARAM(lambda: arm_width, 18.0))              # noqa: F821
brad_hole = float(PARAM(lambda: brad_hole, 3.0))               # noqa: F821
eyelet_hole = float(PARAM(lambda: eyelet_hole, 3.2))           # noqa: F821
rivet_hole = float(PARAM(lambda: rivet_hole, 4.0))             # noqa: F821
margin = float(PARAM(lambda: margin, 14.0))                    # noqa: F821
stations = int(round(float(PARAM(lambda: stations, 5))))       # noqa: F821
open_angle = float(PARAM(lambda: open_angle, 150.0))           # noqa: F821

PIVOTING = ("brad", "eyelet", "rivet")
if mode not in PIVOTING + ("staple", "stitch"):
    raise ValueError(f"fastener-joins: unknown mode {mode!r}")

W = pliego.clamp(card_width, 60.0, 250.0)
H = pliego.clamp(card_height, 50.0, 250.0)
AL = pliego.clamp(arm_length, 40.0, 220.0)
AW = pliego.clamp(arm_width, 10.0, 40.0)
M = pliego.clamp(margin, 8.0, 30.0)
N_ST = int(pliego.clamp(stations, 3, 11))
OPEN = pliego.clamp(open_angle, 30.0, 178.0)
BASE_STOCK, MOVER_STOCK = "cardstock-300", "cardstock-250"
STACK = 0.36            # the upper card's height above the base (the base's caliper)
SEG = 48

# Hole diameter and the head (or flange) footprint each fastener needs round its hole, as multiples
# of the hole: a brad's domed head, an eyelet's rolled flange, a two-part rivet's cap. Common craft
# sizes; check the hardware in hand.
HOLE = {"brad": pliego.clamp(brad_hole, 2.0, 5.0), "eyelet": pliego.clamp(eyelet_hole, 2.5, 6.0),
        "rivet": pliego.clamp(rivet_hole, 3.0, 6.0)}
HEAD_FACTOR = {"brad": 2.6, "eyelet": 2.0, "rivet": 2.4}
STAPLE_CROWN = 12.0     # a standard office staple's crown, mm
MARK = 1.2              # half-size of a piercing mark (kiss-cut cross)


def L4(en, es, fr, pt):
    return {"en": en, "es": es, "fr": fr, "pt": pt}


def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def pierce(sheet, at, name):
    """A kiss-cut cross where an awl or a staple leg pierces the card (no hole is cut)."""
    x, y = at
    sheet.halfcut([(x - MARK, y), (x + MARK, y)], name=name)
    sheet.halfcut([(x, y - MARK), (x, y + MARK)], name=name)


NAMES = {
    "brad": L4("Brad (split pin)", "Broche (encuadernador)", "Attache parisienne",
               "Colchete (bailarina)"),
    "eyelet": L4("Eyelet", "Ojillo", "Œillet", "Ilhós"),
    "rivet": L4("Rivet", "Remache", "Rivet", "Rebite"),
    "staple": L4("Staples", "Grapas", "Agrafes", "Grampos"),
    "stitch": L4("Running stitch", "Puntada corrida", "Point avant", "Ponto corrido"),
}

base = pliego.Sheet("base", rect(0.0, 0.0, W, H), stock=BASE_STOCK, grain_deg=90.0,
                    label=L4("Base card", "Tarjeta base", "Carte de base", "Cartão base"))
sheets, joins, mechanisms, controls, sequence = [base], [], [], [], None

if mode in PIVOTING:
    d = HOLE[mode]
    head = HEAD_FACTOR[mode] * d
    if AW < head + 2.0:
        raise ValueError(f"fastener-joins: a {mode} with a {d:g} mm hole has a head of about "
                         f"{head:.1f} mm; the arm must be at least {head + 2.0:.1f} mm wide")
    r = AW / 2.0
    px, py = r + 4.0, H / 2.0            # the pivot on the base, near its left edge
    if AL - r > W - px - 2.0 + 30.0:
        raise ValueError("fastener-joins: the arm is far longer than the card")
    # the arm, in its own frame: centre line along u at v = r; round ends; the pivot at (r, r)
    ring = []
    for k in range(SEG // 2 + 1):        # right end, −90° → 90°
        a = math.radians(-90.0 + 180.0 * k / (SEG // 2))
        ring.append((AL - r + r * math.cos(a), r + r * math.sin(a)))
    for k in range(SEG // 2 + 1):        # left end, 90° → 270°
        a = math.radians(90.0 + 180.0 * k / (SEG // 2))
        ring.append((r + r * math.cos(a), r + r * math.sin(a)))
    arm = pliego.Sheet("arm", ring, stock=MOVER_STOCK, grain_deg=0.0,
                       label=L4("Arm", "Brazo", "Bras", "Braço"), kinematic="swing-arm",
                       placement=pliego.Placement(origin=(px - r, STACK, -(py - r))))
    arm.hole(pliego.circle((r, r), d / 2.0, 24))
    # The base's hole is a closed cut: its slug stays in the document (it drops out when the card
    # is cut), so the mechanism's centre still lies on the base's material.
    base.cut(pliego.circle((px, py), d / 2.0, 24), closed=True, name="fastener-hole")
    for sh in (arm, base):
        rep = pliego.papercut.analyze(sh, min_feature_mm=2.0)
        bad = [i for i in rep.issues if i["level"] == "error" and i["kind"] != "islands"]
        if bad or rep.components > (2 if sh is base else 1):
            raise ValueError(f"fastener-joins: {sh.id} fails the papercut check: {rep.issues}")
    sheets.append(arm)
    mechanisms.append(pliego.rotate("swing-arm", (base, (px, py)), "swing", [arm]))
    controls.append(pliego.angle_control("swing", L4("Swing the arm", "Girar el brazo",
                                                     "Faire pivoter le bras", "Girar o braço"),
                                         default=35.0, min=0.0, max=360.0))
    summary = f"hole={d:g}mm head~{head:.1f}mm arm={AL:g}x{AW:g}mm pivot=({px:g}, {py:g})"
else:
    if W - M < 30.0:
        raise ValueError("fastener-joins: the margin leaves too little cover to open")
    cover = pliego.Sheet("cover", rect(0.0, 0.0, W, H), stock=MOVER_STOCK, grain_deg=90.0,
                         label=L4("Cover", "Tapa", "Couverture", "Capa"),
                         placement=pliego.Placement(origin=(0.0, STACK, 0.0)))
    hinge_line = cover.score((M, 0.0), (M, H), kind="valley", angle=OPEN, name="hinge",
                             label=L4("Opens here", "Abre aquí", "S'ouvre ici", "Abre aqui"))
    xf = M / 2.0                          # the fastening runs down the middle of the margin
    points = []
    if mode == "staple":
        if H < 2.0 * STAPLE_CROWN + 16.0:
            raise ValueError("fastener-joins: the card is too short for two staples")
        for k, yc in enumerate((H / 4.0, 3.0 * H / 4.0)):
            legs = [(xf, yc - STAPLE_CROWN / 2.0), (xf, yc + STAPLE_CROWN / 2.0)]
            for sh in (cover, base):      # the crown on the cover, the clinch on the base
                sh.halfcut(legs, name="staple")
            points += legs
    else:
        n_fit = int((H - 2.0 * 8.0) // 6.0) + 1      # stations at least 6 mm apart
        if N_ST > n_fit:
            print(f"fastener-joins: {N_ST} stations do not fit {H:g} mm at 6 mm; using {n_fit}")
            N_ST = n_fit
        pitch = (H - 2.0 * 8.0) / (N_ST - 1)
        for k in range(N_ST):
            at = (xf, 8.0 + pitch * k)
            for sh in (cover, base):
                pierce(sh, at, "station")
            points.append(at)
    for k, at in enumerate(points):
        joins.append(pliego.pivot(f"{mode}-{k + 1}", (cover, at), (base, at)))
    sheets.append(cover)
    sequence = pliego.Sequence([
        pliego.Step("open", L4("Open the cover", "Abre la tapa", "Ouvrir la couverture",
                               "Abra a capa"), [(hinge_line, OPEN)], duration_ms=1600,
                    note=L4("The fastened margin stays put; the cover turns on the score.",
                            "El margen sujeto no se mueve; la tapa gira sobre el marcado.",
                            "La marge fixée ne bouge pas ; la couverture tourne sur le rainage.",
                            "A margem presa não se move; a capa gira sobre o vinco.")),
        pliego.Step("close", L4("Close it", "Ciérrala", "La refermer", "Feche"),
                    [(hinge_line, 0.0)], duration_ms=1400),
    ])
    controls.append(pliego.sequence_control(label=L4("Open and close", "Abrir y cerrar",
                                                     "Ouvrir et fermer", "Abrir e fechar")))
    summary = f"margin={M:g}mm joins={len(points)} open={OPEN:g}deg"

print(f"fastener-joins: mode={mode} card={W:g}x{H:g}mm {summary}")

result = pliego.Assembly(sheets, joins=joins, mechanisms=mechanisms, controls=controls,
                         sequence=sequence, title="Fastener joins")
