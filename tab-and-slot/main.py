"""Tab and slot — sheet-hyperobjects cartridge (Pliego).

Two cards that interlock through complementary slits. Card A has a slit cut from the middle of
its top edge down to the meeting point; card B has a slit cut from the middle of its bottom edge
up to the same height. Turned 90° to each other and pushed together, each card's solid half runs
through the other's slit, and the pair stands on its edges as a cross. Nothing is glued: contact
between the cards holds them.

The script builds both cards with their slits (`C` cuts from an edge to the meeting point) and
places them rigidly in the world (card A in the plane z = 0, card B in the plane x = 0, both
standing on the ground), so the slits engage in the initial frame. The two slits together span
the full card height: `slit_ratio` of it on card A, the rest on card B, and their ends meet.
"""

import math

import pliego


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


card_width = float(PARAM(lambda: card_width, 100.0))
card_height = float(PARAM(lambda: card_height, 120.0))
slit_ratio = float(PARAM(lambda: slit_ratio, 0.5))
stock = str(PARAM(lambda: stock, "cardstock-250"))

STOCKS = ("cardstock-160", "cardstock-250", "cardstock-300")
if stock not in STOCKS:
    raise ValueError(f"tab-and-slot: stock must be one of {STOCKS}, got {stock!r}")
if not 0.2 <= slit_ratio <= 0.8:
    raise ValueError(f"tab-and-slot: slit_ratio must be in [0.2, 0.8], got {slit_ratio}")

half = card_width / 2.0
meet = card_height * (1.0 - slit_ratio)        # height at which the two slits meet
s45 = math.sqrt(0.5)

# Card A: slit from the top edge down to the meeting point. Placement: +90° about x, so the
# card stands in the plane z = 0, centred on x = 0: (u, v) -> (u - W/2, v, 0).
card_a = pliego.Sheet(
    "card-a", pliego.rectangle(card_width, card_height), stock=stock, grain_deg=90.0,
    label={"en": "Card A (slot from the top)", "es": "Tarjeta A (ranura desde arriba)",
           "fr": "Carte A (fente par le haut)", "pt": "Cartão A (fenda por cima)"},
    placement=pliego.Placement(origin=(-half, 0.0, 0.0), rotation=(s45, 0.0, 0.0, s45)))
slot = card_a.cut([(half, card_height), (half, meet)],
                  label={"en": "Slot", "es": "Ranura", "fr": "Fente", "pt": "Fenda"})

# Card B: slit from the bottom edge up to the meeting point. Placement: the rotation taking
# (u, 0, -v) to (0, v, -u), then +W/2 on z, so the card stands in the plane x = 0 with its
# slit on z = 0: (u, v) -> (0, v, W/2 - u).
card_b = pliego.Sheet(
    "card-b", pliego.rectangle(card_width, card_height), stock=stock, grain_deg=90.0,
    label={"en": "Card B (slot from the bottom)", "es": "Tarjeta B (ranura desde abajo)",
           "fr": "Carte B (fente par le bas)", "pt": "Cartão B (fenda por baixo)"},
    placement=pliego.Placement(origin=(0.0, 0.0, half), rotation=(0.5, 0.5, -0.5, 0.5)))
tab = card_b.cut([(half, 0.0), (half, meet)],
                 label={"en": "Slot", "es": "Ranura", "fr": "Fente", "pt": "Fenda"})


def placed(sheet, u, v):
    """World point of sheet-local (u, v): the un-placed (u, 0, -v), rotated, then moved."""
    x, y, z, w = sheet.placement.rotation
    p = (u, 0.0, -v)
    # q · p · q*, expanded (unit quaternion [x, y, z, w])
    tx = 2.0 * (y * p[2] - z * p[1])
    ty = 2.0 * (z * p[0] - x * p[2])
    tz = 2.0 * (x * p[1] - y * p[0])
    r = (p[0] + w * tx + (y * tz - z * ty), p[1] + w * ty + (z * tx - x * tz),
         p[2] + w * tz + (x * ty - y * tx))
    o = sheet.placement.origin
    return (r[0] + o[0], r[1] + o[1], r[2] + o[2])


# Self-check (fail loud): both slits lie on the cards' common line x = z = 0, they meet at
# the same height, and together they span the card from the ground to the top edge.
ends = [placed(card_a, half, card_height), placed(card_a, half, meet),
        placed(card_b, half, 0.0), placed(card_b, half, meet)]
for x, _y, z in ends:
    if abs(x) > 1e-9 or abs(z) > 1e-9:
        raise ValueError("tab-and-slot: the slits do not lie on the cards' common line")
if abs(ends[1][1] - ends[3][1]) > 1e-9 or abs(ends[0][1] - card_height) > 1e-9 \
        or abs(ends[2][1]) > 1e-9:
    raise ValueError("tab-and-slot: the slits do not meet or do not span the card")

result = pliego.Assembly(
    [card_a, card_b], title="Tab and slot",
    meta={"cartridge": "tab-and-slot",
          "params": {"card_width": card_width, "card_height": card_height,
                     "slit_ratio": slit_ratio, "stock": stock}})
