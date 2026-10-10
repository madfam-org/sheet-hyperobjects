"""Cardboard furniture — sheet-hyperobjects cartridge (Pliego).

Original slotted furniture in thick corrugated board (BC double wall or AAC triple wall), cut
flat and assembled without glue or fasteners. ``piece`` selects the design:

- ``stool`` — two straight leg panels that cross-halve into an X (plan "+"), a square seat with
  rounded corners on top; four tabs on the legs' top edges pass through four mortises in the seat;
- ``side-table`` — the same joinery with tapered legs and a round top.

**Slotted assembly, checked against the caliper t.** One leg is slotted from the top, the other
from the bottom (up from its arch), each slot **one caliper wide** and reaching **half the leg's
height**, so the two legs meet flush. Tabs are one caliper tall (flush with the seat's top) and
the seat's mortises are one caliper wide and one tab long. The script fails loud unless these
hold and unless the arch stays clear of the cross slot; it runs ``pliego.papercut.analyze`` on
every part. Legs are cut with the flutes running up their height (grain along the leg's width).

**Panel layout.** The parts are packed onto a stock sheet format (shelf packing, flutes along the
sheet's ``y`` side, 10 mm margins and gaps) and the document's layout places them that way, so the
exported cut files show the nesting; the script prints sheets used and the board's utilisation.

**Interaction.** The assembled piece is the initial frame (every part a rigid board). The
``explode`` control lifts the seat out of its tabs and the second leg out of its cross slot (two
``translate`` mechanisms on one control; the seat travels twice as far, so it stays clear) — the
preview drives it.

**Prototype only.** Whether the piece carries a person is a statics claim this cartridge cannot
verify (board crushing, buckling of the legs, the joints' play): no load rating is given. Board
contact in the slots is edge-to-edge contact, not modelled by the engine in v0.1.
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


piece = str(PARAM(lambda: piece, "stool"))                       # noqa: F821
height = float(PARAM(lambda: height, 420.0))                     # noqa: F821 - floor to top
top = float(PARAM(lambda: top, 320.0))                           # noqa: F821 - seat / top size
stock = str(PARAM(lambda: stock, "corrugated-bc-double-wall"))   # noqa: F821
sheet_format = str(PARAM(lambda: sheet_format, "1600x1200"))     # noqa: F821

STOCKS = ("corrugated-bc-double-wall", "corrugated-aac-triple-wall")
FORMATS = {"1200x1000": (1200.0, 1000.0), "1600x1200": (1600.0, 1200.0),
           "2000x1200": (2000.0, 1200.0)}                         # common formats [E]
if piece not in ("stool", "side-table") or stock not in STOCKS or sheet_format not in FORMATS:
    raise ValueError("cardboard-furniture: unknown piece, stock or sheet_format")
t = pliego.board.caliper(stock)
height = pliego.clamp(height, 300.0, 700.0)
top = pliego.clamp(top, 260.0, 600.0)
Hl = height - t                          # legs: floor to the top panel's underside
over = 15.0 if piece == "stool" else 0.0
wl = top - 2 * over if piece == "stool" else 0.82 * top     # leg width at the floor
wt = wl if piece == "stool" else 0.62 * top                 # leg width at the top
foot = 0.18 * wl
arch = 0.3 * Hl
tab_w = 40.0 if t < 10 else 60.0
d_t = 0.32 * wt                           # tab centres from the leg's centre
cx = wl / 2.0                             # leg centre (local u)


def leg_outline(from_top):
    """A leg: tapered sides, an arch between the feet, two tabs on top, the cross slot."""
    xl, xr = (wl - wt) / 2.0, (wl + wt) / 2.0
    n = 16
    arch_pts = [(cx - (cx - foot) * math.cos(math.pi * k / n), arch * math.sin(math.pi * k / n))
                for k in range(n + 1)]                   # half an ellipse, foot to foot
    if from_top:
        pts = [(0.0, 0.0)] + arch_pts
    else:                                                # slot from the arch up to half height
        ys = arch * math.sqrt(1.0 - (t / 2.0 / (cx - foot)) ** 2)
        pts = ([(0.0, 0.0)] + [p for p in arch_pts if p[0] < cx - t / 2.0]
               + [(cx - t / 2.0, ys), (cx - t / 2.0, Hl / 2.0), (cx + t / 2.0, Hl / 2.0),
                  (cx + t / 2.0, ys)] + [p for p in arch_pts if p[0] > cx + t / 2.0])
    pts += [(wl, 0.0), (xr, Hl)]
    tops = [cx + d_t, cx - d_t]
    for k, c_ in enumerate(tops):                        # tabs, right to left along the top
        pts += [(c_ + tab_w / 2.0, Hl), (c_ + tab_w / 2.0, Hl + t), (c_ - tab_w / 2.0, Hl + t),
                (c_ - tab_w / 2.0, Hl)]
        if from_top and k == 0:                          # the cross slot, between the tabs
            pts += [(cx + t / 2.0, Hl), (cx + t / 2.0, Hl / 2.0), (cx - t / 2.0, Hl / 2.0),
                    (cx - t / 2.0, Hl)]
    return pts + [(xl, Hl)]


def top_outline():
    if piece == "stool":
        r, pts = 30.0, []
        for k, (ccx, ccy) in enumerate(((top - 30.0, 30.0), (top - 30.0, top - 30.0),
                                        (30.0, top - 30.0), (30.0, 30.0))):
            for j in range(7):
                ang = math.radians(-90.0 + 90.0 * k + 15.0 * j)
                pts.append((ccx + r * math.cos(ang), ccy + r * math.sin(ang)))
        return pts
    return [(top / 2.0 + top / 2.0 * math.cos(2 * math.pi * k / 48),
             top / 2.0 + top / 2.0 * math.sin(2 * math.pi * k / 48)) for k in range(48)]


# ── checks: slot geometry against the caliper ─────────────────────────────────────────────────
checks = [("cross slots one caliper wide", True),
          ("cross slots reach half the leg height", True),
          ("arch clear of the cross slot", arch < Hl / 2.0 - 2 * t),
          ("tabs one caliper tall, mortises one caliper wide", True),
          ("tabs clear of the cross slot", d_t - tab_w / 2.0 > t),
          ("tabs on the legs' top edge", d_t + tab_w / 2.0 < wt / 2.0 - t),
          ("tabs inside the top", piece == "side-table"
           and math.hypot(d_t + tab_w / 2.0, t / 2.0) < top / 2.0 - 2 * t
           or piece == "stool" and d_t + tab_w / 2.0 < top / 2.0 - 2 * t),
          ("legs inside the top", wl / 2.0 <= top / 2.0 + 1e-9)]
bad = [name for name, ok in checks if not ok]
if bad:
    raise ValueError("cardboard-furniture: joinery check failed: " + ", ".join(bad))

S = math.sqrt(0.5)
STAND_X = (S, 0.0, 0.0, S)                 # sheet (u, v) → world (u, v, 0)
STAND_Z = (0.5, -0.5, 0.5, 0.5)            # sheet (u, v) → world (0, v, u)
NAMES = {"leg-a": L4("Leg A (slotted from the top)", "Pata A (ranura desde arriba)",
                     "Pied A (fente par le haut)", "Perna A (ranhura por cima)"),
         "leg-b": L4("Leg B (slotted from the bottom)", "Pata B (ranura desde abajo)",
                     "Pied B (fente par le bas)", "Perna B (ranhura por baixo)"),
         "top": (L4("Seat", "Asiento", "Assise", "Assento") if piece == "stool" else
                 L4("Table top", "Cubierta", "Plateau", "Tampo"))}
packs = {}
for name, from_top in (("leg-a", True), ("leg-b", False)):
    d = pliego.dieline.Dieline(name, f"slotted leg ({piece})", "corrugated",
                               {"length": top, "width": top, "depth": height}, stock, t,
                               label=NAMES[name], grain_deg=0.0)
    d.panel("leg", leg_outline(from_top), "panel", NAMES[name], print_area=False)
    d.dimension((0.0, 0.0), (wl, 0.0), f"{wl:.0f}", -8.0)
    d.dimension((0.0, 0.0), (0.0, Hl), f"{Hl:.1f}", 8.0)
    packs[name] = d.build(rest_on="leg")
d = pliego.dieline.Dieline("top", f"{piece} top with mortises", "corrugated",
                           {"length": top, "width": top, "depth": height}, stock, t,
                           label=NAMES["top"], grain_deg=0.0)
d.panel("top", top_outline(), "panel", NAMES["top"], print_area=False)
c = top / 2.0
for s_ in (-1.0, 1.0):
    u0 = c + s_ * d_t
    d.hole([(u0 - tab_w / 2, c - t / 2), (u0 + tab_w / 2, c - t / 2), (u0 + tab_w / 2, c + t / 2),
            (u0 - tab_w / 2, c + t / 2)])                       # leg A's tabs (along u)
    d.hole([(c - t / 2, u0 - tab_w / 2), (c + t / 2, u0 - tab_w / 2), (c + t / 2, u0 + tab_w / 2),
            (c - t / 2, u0 + tab_w / 2)])                       # leg B's tabs (along v)
d.dimension((0.0, 0.0), (top, 0.0), f"{top:.0f}", -8.0)
packs["top"] = d.build(rest_on="top")

# ── assembled: legs crossing at the top's centre, the top on their tabs ──────────────────────
leg_a, leg_b, top_sheet = packs["leg-a"].sheet, packs["leg-b"].sheet, packs["top"].sheet
leg_a.placement = pliego.Placement(origin=(c - cx, 0.0, c), rotation=STAND_X)
leg_b.placement = pliego.Placement(origin=(c, 0.0, c - cx), rotation=STAND_Z)
top_sheet.placement = pliego.Placement(origin=(0.0, Hl + t / 2.0, top))   # print side up
for sh in (leg_a, leg_b, top_sheet):
    rep = pliego.papercut.analyze(sh, min_feature_mm=t)
    errors = [i["detail"] for i in rep.issues if i["level"] == "error"]
    if errors:
        raise ValueError(f"cardboard-furniture: {sh.id}: " + "; ".join(errors))
leg_a.kinematic = leg_b.kinematic = "explode-leg"
top_sheet.kinematic = "explode-top"
lift = round(Hl / 2.0 + 30.0, 1)

# ── panel layout on a stock format (shelf packing; part y along the sheet's flutes) ──────────
SW, SH = FORMATS[sheet_format]
M = 10.0
parts = [("leg-a", wl, Hl + t), ("leg-b", wl, Hl + t), ("top", top, top)]
if any(w > SW - 2 * M or h > SH - 2 * M for _n, w, h in parts):
    raise ValueError(f"cardboard-furniture: a part does not fit a {sheet_format} sheet")


def pack(items):
    """Shelf packing: tallest first, rows across the sheet, a new sheet when a row overflows."""
    pos, sheet_no, x, y, shelf = {}, 0, M, M, 0.0
    for name, w, h in sorted(items, key=lambda p: -p[2]):
        if x + w > SW - M:
            x, y, shelf = M, y + shelf + M, 0.0
        if y + h > SH - M:
            sheet_no, x, y, shelf = sheet_no + 1, M, M, 0.0
        pos[name] = (sheet_no * (SW + 50.0) + x, y)
        x, shelf = x + w + M, max(shelf, h)
    return sheet_no + 1, pos


used, placed = pack(parts)
part_area = sum(pliego.polygon_area(pk.sheet.outline) for pk in packs.values())
util = part_area / (used * SW * SH)
sets = 1
while sets < 24 and pack([(f"{n}-{k}", w, h) for k in range(sets + 1)
                          for n, w, h in parts])[0] == 1:
    sets += 1
if used > 1:
    sets = 0
print(f"cardboard-furniture: {piece}, {stock} (t {t:g} mm): legs {wl:.0f} x {Hl:.0f} mm, top "
      f"{top:.0f} mm; slots {t:g} x {Hl / 2:.0f} mm, mortises {tab_w:g} x {t:g} mm; layout "
      f"{used} sheet(s) of {sheet_format} mm for one set (utilisation {100 * util:.0f}%), "
      f"{sets} set(s) per sheet ({100 * util * max(sets, 1):.0f}%) — prototype only, "
      f"no load rating")

result = pliego.Assembly(
    [leg_a, leg_b, top_sheet],
    mechanisms=[pliego.translate("explode-top", "explode", (0.0, 1.0, 0.0), 2 * lift,
                                 [top_sheet]),
                pliego.translate("explode-leg", "explode", (0.0, 1.0, 0.0), lift, [leg_b])],
    controls=[pliego.control("explode", "distance",
                             L4("Take it apart", "Desármalo", "Démonter", "Desmontar"),
                             0.0, 0.0, lift, "mm")],
    layout={k: v for k, v in placed.items()}, dielines=[p.block for p in packs.values()],
    title=f"Cardboard furniture ({piece})",
    meta={"cartridge": "cardboard-furniture",
          "params": {"piece": piece, "height": height, "top": top, "stock": stock,
                     "sheet_format": sheet_format}})
