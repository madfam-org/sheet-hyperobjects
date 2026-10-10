"""Glue flap — sheet-hyperobjects cartridge (Pliego).

A strip of `sides` equal panels with a tapered glue tab on its last edge is folded into a
closed tube (square by default) and the tab is glued inside the first panel. The technique
the object teaches: a glue flap is a tab hinged on a fold, and the glue joint is a weld from
the tab's region onto a glue zone, here on the same sheet.

The script builds the strip, its `sides` scored valley folds (each turning 360°/sides) and the
tab, writes one `glue` join (tab region -> first panel, map = translation by -sides·side_width)
and computes the initial frame in the folded state in closed form, so the weld holds exactly:
panel k lies along direction k·360°/sides in the tube's cross-section and the tab, turned a
full 360°, lands back on panel 0.
"""

import math

import pliego


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


sides = round(float(PARAM(lambda: sides, 4)))
side_width = float(PARAM(lambda: side_width, 50.0))
tube_length = float(PARAM(lambda: tube_length, 120.0))
tab_width = float(PARAM(lambda: tab_width, 12.0))
tab_taper = float(PARAM(lambda: tab_taper, 45.0))
stock = str(PARAM(lambda: stock, "cardstock-250"))

STOCKS = ("cardstock-160", "cardstock-250", "cardstock-300", "kraft-120")
GLUE_MARGIN_MM = 0.5
if stock not in STOCKS:
    raise ValueError(f"glue-flap: stock must be one of {STOCKS}, got {stock!r}")
if not 3 <= sides <= 8:
    raise ValueError(f"glue-flap: sides must be an integer in [3, 8], got {sides}")
if not tab_width + GLUE_MARGIN_MM < side_width:
    raise ValueError("glue-flap: the tab must be narrower than a panel (it lies on panel 1)")

turn = 360.0 / sides                       # fold angle of every crease, valley
length = sides * side_width                # the strip without its tab

strip = pliego.Sheet(
    "strip", pliego.rectangle(length, tube_length), stock=stock, grain_deg=90.0,
    label={"en": "Tube strip", "es": "Tira del tubo", "fr": "Bande du tube",
           "pt": "Tira do tubo"})
folds = [strip.crease((k * side_width, 0.0), (k * side_width, tube_length), "valley", turn,
                      treatment="score")
         for k in range(1, sides)]
tab = strip.tab(((length, 0.0), (length, tube_length)), width=tab_width, taper=tab_taper,
                kind="valley", angle=turn, treatment="score")

# Glue region: the tab inset by a margin from its hinge, its free edge and its tapered sides.
inset = tab_width / math.tan(math.radians(tab_taper))
slope = inset / tab_width
pad = GLUE_MARGIN_MM * math.hypot(1.0, slope)


def tab_span(u):
    """Glue-region v-range on the tab at sheet-local u (a margin inside both tapered sides)."""
    d = u - length
    return d * slope + pad, tube_length - d * slope - pad


u0, u1 = length + GLUE_MARGIN_MM, length + tab_width - GLUE_MARGIN_MM
(lo0, hi0), (lo1, hi1) = tab_span(u0), tab_span(u1)
region = [(u0, lo0), (u1, lo1), (u1, hi1), (u0, hi0)]
join = pliego.glue("tab-to-panel-1", strip, region, strip,
                   (1.0, 0.0, 0.0, 1.0, -length, 0.0), side="front")

# Folded state: the cross-section polygon in the world x–y plane (y up), the tube's axis
# along −z (sheet v). Panel 0 lies on the ground with its front face up, i.e. inside the tube.
corners = [(0.0, 0.0)]
for k in range(sides):
    t = math.radians(k * turn)
    cx, cy = corners[-1]
    corners.append((cx + side_width * math.cos(t), cy + side_width * math.sin(t)))


def folded(sheet_id, uv):
    u, v = uv
    k = min(max(int(u // side_width), 0), sides)     # panel index; k = sides is the tab
    s = u - k * side_width
    t = math.radians(k * turn)
    cx, cy = corners[k] if k < sides else corners[0]
    return (cx + s * math.cos(t), cy + s * math.sin(t), -v)


# Self-check (fail loud): the polygon closes and every weld point lands on its glue zone.
if math.dist(corners[-1], corners[0]) > 1e-9:
    raise ValueError("glue-flap: the cross-section does not close")
for p in region:
    gap = math.dist(folded("strip", p), folded("strip", (p[0] - length, p[1])))
    if gap > 1e-9:
        raise ValueError(f"glue-flap: weld point {p} misses its glue zone by {gap} mm")

result = pliego.Assembly(
    [strip], joins=[join], initial=folded, title="Glue flap",
    meta={"cartridge": "glue-flap",
          "params": {"sides": sides, "side_width": side_width, "tube_length": tube_length,
                     "tab_width": tab_width, "tab_taper": tab_taper, "stock": stock}})
