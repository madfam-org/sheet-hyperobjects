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
wide through their folds and the lip's tabs drop 1.5t. Glue welds, the tabs' snap and the stand's stability under load need the
physics engine; no load rating is claimed.
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

result = pliego.dieline.assemble(
    [pack], title="Counter display stand", artwork=artwork,
    label=L4("Fold program", "Secuencia de armado", "Séquence de montage",
             "Sequência de montagem"),
    meta={"cartridge": "display-stand",
          "params": {"width": width, "depth": depth, "lip": lip, "side": side, "header": header,
                     "lean": lean, "foot": foot, "stock": stock, "branding": branding}})
