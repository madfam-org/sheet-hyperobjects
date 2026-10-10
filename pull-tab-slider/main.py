"""Pull-tab slider — sheet-hyperobjects cartridge (Pliego).

A pull tab that moves a part. Two modes:

* `straight` — a picture strip slides in a channel behind a page; pulling its tab, which sticks out
  of the page's edge, brings the strip's second picture into a window cut in the page. The channel
  is two rails glued between the page and a backing; a wider head on the strip's inner end stops at
  the narrowed mouth of the channel (full travel), and the wider grip stops against the page edge
  (pushed home). The strip is moved by a `translate` mechanism (the `pull` distance control).
* `pivoting` — a lever on a pivot in front of the page: moving the tab at one end along the page
  edge swings the part at the other end (a paddle) the other way through an arc. The lever is
  moved by a `rotate` mechanism about the pivot (the `swing` angle control); the pivot is a brad
  through a hole in the lever and a kiss-cut mark on the page.

Both moving parts are kinematic sheets with no joins of their own, so the preview drives them; the
rails, the backing and the page are glued to each other (fixed to fixed, which the preview does not
need either). Layers are stacked 0.3 mm apart, inside the stocks' collision thickness, so every glue
weld holds in the initial frame.
"""

import math

import pliego


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


mode = PARAM(lambda: mode, "straight")                       # noqa: F821
page_width = float(PARAM(lambda: page_width, 200.0))         # noqa: F821
page_height = float(PARAM(lambda: page_height, 150.0))       # noqa: F821
window_width = float(PARAM(lambda: window_width, 50.0))      # noqa: F821
window_height = float(PARAM(lambda: window_height, 34.0))    # noqa: F821
strip_width = float(PARAM(lambda: strip_width, 44.0))        # noqa: F821
grip = float(PARAM(lambda: grip, 18.0))                      # noqa: F821
lever_length = float(PARAM(lambda: lever_length, 120.0))     # noqa: F821
lever_width = float(PARAM(lambda: lever_width, 14.0))        # noqa: F821
paddle = float(PARAM(lambda: paddle, 30.0))                  # noqa: F821
swing = float(PARAM(lambda: swing, 40.0))                    # noqa: F821

if mode not in ("straight", "pivoting"):
    raise ValueError(f"pull-tab-slider: unknown mode {mode!r}")
W = pliego.clamp(page_width, 120.0, 300.0)
H = pliego.clamp(page_height, 100.0, 300.0)
ww = pliego.clamp(window_width, 15.0, 120.0)
wh = pliego.clamp(window_height, 10.0, 100.0)
sw = pliego.clamp(strip_width, 15.0, 110.0)
g = pliego.clamp(grip, 10.0, 40.0)
ll = pliego.clamp(lever_length, 60.0, 260.0)
lw = pliego.clamp(lever_width, 8.0, 30.0)
pad = pliego.clamp(paddle, 10.0, 60.0)
sw_deg = pliego.clamp(swing, 10.0, 70.0)

STOCK = "cardstock-300"           # page, backing, rails
MOVER = "cardstock-250"           # strip, lever
GAP = 0.3                         # layer spacing (< 0.36 mm collision thickness of the page stock)
CLEAR = 1.0                       # clearance each side of the strip in the channel
STOP = 3.0                        # the head is this much wider than the strip, each side
HEAD = 6.0                        # length of the head
RAIL = 10.0                       # rail width
MARGIN = 8.0
INSET = 0.5
HOLE = 3.0                        # pivot hole diameter


def L4(en, es, fr, pt):
    return {"en": en, "es": es, "fr": fr, "pt": pt}


def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def shrink(poly, d):
    """Inset an axis-aligned rectangle given as rect() (for glue regions)."""
    (x0, y0), _, (x1, y1), _ = poly
    return rect(x0 + d, y0 + d, x1 - d, y1 - d)


sheets, joins, mechanisms, controls = [], [], [], []

if mode == "straight":
    if wh > sw - 4.0:
        raise ValueError("pull-tab-slider: the window must be at least 4 mm lower than the strip, "
                         "so the strip's edges stay hidden")
    yc = H / 2.0
    travel = ww + 6.0                               # the second picture replaces the first
    wx0 = W - MARGIN - RAIL - ww - 20.0             # window, page frame
    xs0 = wx0 - travel - HEAD                       # strip's inner end at rest
    if xs0 < MARGIN + 4.0:
        raise ValueError(f"pull-tab-slider: a {ww:g} mm window needs a page wider than "
                         f"{W - xs0 + MARGIN + 4.0:.0f} mm")
    if sw + 2 * (CLEAR + STOP) + 2 * RAIL > H - 2 * MARGIN:
        raise ValueError("pull-tab-slider: the channel does not fit the page height")
    xm = xs0 + HEAD + travel                        # the mouth narrows here: the head stops
    half_in, half_mouth = sw / 2.0 + STOP + CLEAR, sw / 2.0 + CLEAR

    page = pliego.Sheet("page", rect(0, 0, W, H), stock=STOCK, grain_deg=90.0,
                        label=L4("Page with a window", "Página con ventana", "Page à fenêtre",
                                 "Página com janela"),
                        placement=pliego.Placement(origin=(0.0, 2 * GAP, 0.0)))
    page.hole(rect(wx0, yc - wh / 2.0, wx0 + ww, yc + wh / 2.0))
    backing = pliego.Sheet("backing", rect(0, 0, W, H), stock=STOCK, grain_deg=90.0,
                           label=L4("Backing", "Respaldo", "Contre-page", "Contracapa"))
    rails = []
    for side, sgn in (("rail-low", -1.0), ("rail-high", 1.0)):
        # an L: wide channel from the inner end to the mouth, narrower channel from there out
        x_in = xs0 - 4.0
        a_in, a_m = yc + sgn * half_in, yc + sgn * half_mouth
        b = yc + sgn * (half_in + RAIL)
        ring = [(x_in, a_in), (xm, a_in), (xm, a_m), (W, a_m), (W, b), (x_in, b)]
        if sgn < 0:
            ring = ring[::-1]
        lo_x, lo_y = min(p[0] for p in ring), min(p[1] for p in ring)
        local = [(x - lo_x, y - lo_y) for x, y in ring]
        r = pliego.Sheet(side, local, stock=STOCK, grain_deg=0.0,
                         label=L4("Rail" + (" (lower)" if sgn < 0 else " (upper)"),
                                  "Riel" + (" inferior" if sgn < 0 else " superior"),
                                  "Glissière" + (" inférieure" if sgn < 0 else " supérieure"),
                                  "Trilho" + (" inferior" if sgn < 0 else " superior")),
                         placement=pliego.Placement(origin=(lo_x, GAP, -lo_y)))
        # glue the outer, full-length band of the rail to the backing and to the page
        band = rect(0.0, 0.0, W - x_in, RAIL) if sgn < 0 else \
            rect(0.0, half_in - half_mouth, W - x_in, half_in - half_mouth + RAIL)
        band = shrink(band, INSET)
        joins.append(pliego.glue(f"{side}-to-backing", r, band, backing,
                                 (1, 0, 0, 1, lo_x, lo_y), "front"))
        page_band = [(x + lo_x, y + lo_y) for x, y in band]
        joins.append(pliego.glue(f"page-to-{side}", page, page_band, r,
                                 (1, 0, 0, 1, -lo_x, -lo_y), "front"))
        rails.append(r)
    # the strip: head (wider) at the inner end, body, and the grip (wider) outside the page
    x_end = W + g
    hs, hb = sw / 2.0 + STOP, sw / 2.0
    hg = half_mouth + 4.0
    ring = [(0, -hs), (HEAD, -hs), (HEAD, -hb), (W + 2.0 - xs0, -hb), (W + 2.0 - xs0, -hg),
            (x_end - xs0, -hg), (x_end - xs0, hg), (W + 2.0 - xs0, hg), (W + 2.0 - xs0, hb),
            (HEAD, hb), (HEAD, hs), (0, hs)]
    strip = pliego.Sheet("strip", [(x, y + hg) for x, y in ring], stock=MOVER, grain_deg=0.0,
                         label=L4("Picture strip with pull tab", "Tira de imágenes con lengüeta",
                                  "Bande d'images à tirette", "Tira de imagens com puxador"),
                         kinematic="pull-strip",
                         placement=pliego.Placement(origin=(xs0, GAP, -(yc - hg))))
    strip.label_edge("pull-tab", (x_end - xs0, 0.0), (x_end - xs0, 2 * hg))
    sheets = [backing] + rails + [strip, page]
    mechanisms.append(pliego.translate("pull-strip", "pull", (1.0, 0.0, 0.0), travel, [strip]))
    controls.append(pliego.control("pull", "distance", L4(
        "Pull the tab", "Jalar la lengüeta", "Tirer la tirette", "Puxar o puxador"),
        default=travel, min=0.0, max=travel, unit="mm"))
    summary = f"travel={travel:g}mm window={ww:g}x{wh:g} head_stop_at_x={xm:.1f}"
else:
    # the lever: pivot P on the page, tab end past the right edge, paddle end inside the page
    yc = H / 2.0
    tab_out = g
    px = W - (ll - pad - tab_out)                   # pivot so that the lever reaches W + tab_out
    if px < MARGIN + pad:
        raise ValueError("pull-tab-slider: the lever is too long for the page")
    reach_r = ll - pad                              # pivot to tab end
    # the lever in its own frame: a round paddle (centre (pad/2, cy)), a neck of width lw from
    # the paddle to the tab, the pivot at u = pad, and a wider grip at the far end
    if pad < lw + 2.0:
        raise ValueError("pull-tab-slider: the paddle must be at least 2 mm wider than the lever")
    cy = pad / 2.0
    piv_u = pad
    tab_u = pad + reach_r
    neck_lo, neck_hi = cy - lw / 2.0, cy + lw / 2.0
    j = math.degrees(math.asin(min(1.0, (lw / 2.0) / (pad / 2.0))))
    paddle_arc = [(pad / 2.0 + pad / 2.0 * math.cos(math.radians(a)),
                   cy + pad / 2.0 * math.sin(math.radians(a)))
                  for a in [j + (360.0 - 2 * j) * i / 32 for i in range(33)]]
    tab_hi = cy + lw / 2.0 + 4.0
    tab_lo = cy - lw / 2.0 - 4.0
    ring = paddle_arc + [(tab_u - tab_out, neck_lo), (tab_u - tab_out, tab_lo), (tab_u, tab_lo),
                         (tab_u, tab_hi), (tab_u - tab_out, tab_hi), (tab_u - tab_out, neck_hi)]
    ring = [(x, y - tab_lo) for x, y in ring]
    cy -= tab_lo
    page = pliego.Sheet("page", rect(0, 0, W, H), stock=STOCK, grain_deg=90.0,
                        label=L4("Page", "Página", "Page", "Página"))
    page.halfcut([(px - 2.0, yc), (px + 2.0, yc)], name="pivot-mark")
    page.halfcut([(px, yc - 2.0), (px, yc + 2.0)], name="pivot-mark")
    lever = pliego.Sheet("lever", ring, stock=MOVER, grain_deg=0.0,
                         label=L4("Lever with pull tab", "Palanca con lengüeta",
                                  "Levier à tirette", "Alavanca com puxador"),
                         kinematic="swing-lever",
                         placement=pliego.Placement(origin=(px - piv_u, GAP, -(yc - cy))))
    lever.hole(pliego.circle((piv_u, cy), HOLE / 2.0, 20))
    lever.label_edge("pull-tab", (tab_u, 0.0), (tab_u, tab_hi - tab_lo))
    sheets = [page, lever]
    mechanisms.append(pliego.rotate("swing-lever", (page, (px, yc)), "swing", [lever]))
    controls.append(pliego.angle_control("swing", L4(
        "Move the tab: the paddle swings", "Mueve la lengüeta: la paleta gira",
        "Déplacez la tirette : la palette pivote", "Mova o puxador: a paleta gira"),
        default=sw_deg, min=0.0, max=sw_deg))
    summary = (f"pivot=({px:.1f}, {yc:.1f}) swing={sw_deg:g}deg "
               f"arc_at_tab={math.radians(sw_deg) * reach_r:.1f}mm")

print(f"pull-tab: mode={mode} page={W:g}x{H:g}mm {summary}")

result = pliego.Assembly(sheets, joins=joins, mechanisms=mechanisms, controls=controls,
                         title="Pull-tab slider")
