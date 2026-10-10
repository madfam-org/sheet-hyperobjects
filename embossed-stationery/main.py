"""Embossed stationery — sheet-hyperobjects cartridge (Pliego).

Sheet pressing and heat branding on a folded card. One family; ``style`` selects the finish
applied to the card's cover (``pliego.press``, spec ``pliego:finishes``):

- blind emboss (raised, no ink), registered emboss (raised over printed art), deboss (pressed
  in), hot foil (metallic foil stamped flat), letterpress (inked impression);
- heat branding: laser burn (engraved char, vector + raster) or branding iron (a hot die).

The motif is original geometry computed here — an n-point star inside a ring. The card is a
single scored fold; the program folds it closed with the cover's print side up. The dieline
export profile writes each finish as its own plates (die and counter, foil plate, letterpress
plate, branding-iron face, engrave layers). The engine does not yet change local stiffness or
thickness from the finish, and the studio does not yet render relief: documented limits.
"""

import math

import pliego


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


style = str(PARAM(lambda: style, "blind-emboss"))     # noqa: F821
size = str(PARAM(lambda: size, "a6"))                 # noqa: F821
points = round(float(PARAM(lambda: points, 8)))       # noqa: F821
motif = float(PARAM(lambda: motif, 0.55))             # noqa: F821
stock = str(PARAM(lambda: stock, "cardstock-300"))    # noqa: F821

SIZES = {"a6": (105.0, 148.0), "a7": (74.0, 105.0), "us-5x7": (127.0, 177.8),
         "square-150": (150.0, 150.0)}
STOCKS = ("cardstock-250", "cardstock-300", "sbs-board-350", "folding-boxboard-300",
          "greyboard-1500")
STYLES = ("blind-emboss", "registered-emboss", "deboss", "hot-foil", "letterpress",
          "laser-burn", "branding-iron")
if size not in SIZES or stock not in STOCKS or style not in STYLES:
    raise ValueError("embossed-stationery: unknown size, stock or style")
points = int(pliego.clamp(points, 5, 12))
motif = pliego.clamp(motif, 0.3, 0.8)


def L4(en, es, fr, pt):
    return {"en": en, "es": es, "fr": fr, "pt": pt}


w, h = SIZES[size]                 # one panel (the folded card's size)
card = pliego.Sheet(
    "card", pliego.rectangle(2 * w, h), stock=stock, grain_deg=90.0,
    label=L4("Folded card", "Tarjeta doblada", "Carte pliée", "Cartão dobrado"),
    placement=pliego.Placement(rotation=(1.0, 0.0, 0.0, 0.0)))     # print side down
fold = card.mountain((w, 0.0), (w, h), 180.0, treatment="score", name="spine")
card.label_edge("cover-edge", (2 * w, 0.0), (2 * w, h))

# motif on the cover (right panel): an n-point star inside a ring, centred
cx, cy = 1.5 * w, h / 2.0
R = motif * min(w, h) / 2.0


def circle(r, n=96):
    return [(cx + r * math.cos(2 * math.pi * k / n), cy + r * math.sin(2 * math.pi * k / n))
            for k in range(n)]


def star(n, r_out, r_in):
    return [(cx + (r_out if k % 2 == 0 else r_in) * math.cos(math.radians(90 + 180.0 * k / n)),
             cy + (r_out if k % 2 == 0 else r_in) * math.sin(math.radians(90 + 180.0 * k / n)))
            for k in range(2 * n)]


ring = [circle(R), circle(0.88 * R)]           # even-odd: the inner circle is a hole
mark = [star(points, 0.76 * R, 0.34 * R)]
press = pliego.press
finishes, artwork = [], []
if style == "blind-emboss":
    finishes = [press.emboss("ring", card, ring, 0.35, profile="bevel"),
                press.emboss("star", card, mark, 0.45, profile="dome")]
elif style == "registered-emboss":
    finishes = [press.emboss("ring", card, ring, 0.35, profile="bevel", registered=True),
                press.emboss("star", card, mark, 0.45, profile="dome", registered=True)]
    artwork = [press.artwork("motif-print", card, "assets/motif-print.svg", (cx - R, cy - R),
                             (2 * R, 2 * R), side="front", clip="none")]
elif style == "deboss":
    finishes = [press.deboss("ring", card, ring, 0.3), press.deboss("star", card, mark, 0.3)]
elif style == "hot-foil":
    finishes = [press.foil("ring", card, ring, "#c9a227"),
                press.foil("star", card, mark, "#c9a227")]
elif style == "letterpress":
    finishes = [press.letterpress("ring", card, ring, 0.15, color="#1d2a44"),
                press.letterpress("star", card, mark, 0.15, color="#9b2335")]
elif style == "laser-burn":
    finishes = [press.burn("ring", card, ring, 0.1, process="laser", char=0.6),
                press.burn("star", card, mark, 0.15, process="laser", char=0.8)]
else:
    finishes = [press.burn("mark", card, ring + mark, 0.4, process="iron", char=0.9)]

step = pliego.Step("fold-card", L4("Fold the card closed along its score",
                                   "Cierra la tarjeta doblándola por el marcado",
                                   "Fermez la carte en la pliant sur le rainage",
                                   "Feche o cartão dobrando-o pelo vinco"), [(fold, -180.0)],
                   duration_ms=1600)
result = pliego.Assembly(
    [card], controls=[pliego.sequence_control(label=L4("Fold", "Doblar", "Plier", "Dobrar"))],
    sequence=pliego.Sequence([step], mode="kinematic"), finishes=finishes, artwork=artwork,
    title=f"Embossed stationery ({style})",
    meta={"cartridge": "embossed-stationery",
          "params": {"style": style, "size": size, "points": points, "motif": motif,
                     "stock": stock}})
