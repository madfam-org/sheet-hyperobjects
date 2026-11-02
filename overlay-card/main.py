"""A blank cut overlay from an outline and explicit cutout geometry.

All examples are archetypes. No artwork, legends, photographed contours or proprietary
control-panel dimensions are included. A PET stock is PET, not an acetate substitute claim.
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


outline = str(PARAM(lambda: outline, "rounded"))
pattern = str(PARAM(lambda: pattern, "keypad"))
panel_w = float(PARAM(lambda: panel_w, 80.0))
panel_h = float(PARAM(lambda: panel_h, 120.0))
corner_radius = float(PARAM(lambda: corner_radius, 4.0))
rows = int(PARAM(lambda: rows, 4))
columns = int(PARAM(lambda: columns, 3))
pitch_x = float(PARAM(lambda: pitch_x, 20.0))
pitch_y = float(PARAM(lambda: pitch_y, 22.0))
cutout_w = float(PARAM(lambda: cutout_w, 12.0))
cutout_h = float(PARAM(lambda: cutout_h, 12.0))
cutouts = str(PARAM(lambda: cutouts, "20,30,12,10;50,60,14,14"))
stock = str(PARAM(lambda: stock, "cardstock-250"))
if stock not in ("cardstock-250", "pet-125"):
    raise ValueError("overlay-card: stock must be cardstock-250 or pet-125")
if outline not in ("rectangle", "rounded") or pattern not in ("keypad", "window", "custom"):
    raise ValueError("overlay-card: unsupported outline or opening pattern")
if not (40 <= panel_w <= 300 and 40 <= panel_h <= 300 and 0 <= corner_radius <= 15):
    raise ValueError("overlay-card: outline dimensions are outside the supported range")
if not (1 <= rows <= 8 and 1 <= columns <= 6 and 5 <= pitch_x <= 60 and 5 <= pitch_y <= 60):
    raise ValueError("overlay-card: keypad grid is outside the supported range")
if not (3 <= cutout_w <= 250 and 3 <= cutout_h <= 250):
    raise ValueError("overlay-card: opening dimensions are outside the supported range")

if outline == "rectangle" or corner_radius == 0:
    ring = [(0, 0), (panel_w, 0), (panel_w, panel_h), (0, panel_h)]
else:
    r = min(corner_radius, panel_w / 2, panel_h / 2)
    ring = []
    for cx, cy, start in [(panel_w-r, r, -90), (panel_w-r, panel_h-r, 0),
                           (r, panel_h-r, 90), (r, r, 180)]:
        for k in range(9):
            a = math.radians(start + 90 * k / 8)
            ring.append((round(cx + r * math.cos(a), 6), round(cy + r * math.sin(a), 6)))

if pattern == "keypad":
    boxes = [(panel_w/2 + (c-(columns-1)/2)*pitch_x,
              panel_h/2 + (r-(rows-1)/2)*pitch_y, cutout_w, cutout_h)
             for r in range(rows) for c in range(columns)]
elif pattern == "window":
    boxes = [(panel_w/2, panel_h/2, cutout_w, cutout_h)]
else:
    chunks = [p.strip() for p in cutouts.split(";") if p.strip()]
    if not 1 <= len(chunks) <= 32:
        raise ValueError("overlay-card: enter 1 to 32 custom openings")
    boxes = []
    for item in chunks:
        values = item.split(",")
        if len(values) != 4:
            raise ValueError("overlay-card: each opening needs centre x, centre y, width, height")
        box = tuple(float(v.strip()) for v in values)
        if not all(math.isfinite(v) for v in box) or box[2] < 3 or box[3] < 3:
            raise ValueError("overlay-card: openings need finite coordinates and spans at least 3 mm")
        boxes.append(box)

# Conservative authored boundary allowance; the native cut analyzer also judges bridges.
minimum = float(pliego.stock.load_card(stock)["fabrication"]["min_feature_mm"])
boundary = minimum + (corner_radius if outline == "rounded" else 0)
rects = []
for x, y, w, h in boxes:
    a, b, c, d = x-w/2, y-h/2, x+w/2, y+h/2
    if min(a, b, panel_w-c, panel_h-d) < boundary:
        raise ValueError("overlay-card: an opening leaves too little border; enlarge the outline")
    for e, f, g, j in rects:
        gap = math.hypot(max(a-g, e-c, 0), max(b-j, f-d, 0))
        if gap < minimum:
            raise ValueError("overlay-card: openings overlap or leave too little material between them")
    rects.append((a, b, c, d))

sheet = pliego.Sheet("overlay", ring, stock=stock, grain_deg=90,
                     label=L4("Blank overlay", "Plantilla sin arte", "Plaque vierge", "Sobreposição sem arte"))
for a, b in zip(ring, ring[1:] + ring[:1]):
    sheet.label_edge("outline", a, b)
for a, b, c, d in rects:
    sheet.hole([(a, b), (c, b), (c, d), (a, d)])
report = pliego.papercut.analyze(sheet, min_feature_mm=minimum)
if not report.ok:
    raise ValueError("overlay-card: " + "; ".join(i["detail"] for i in report.issues
                                                if i["level"] == "error"))
result = pliego.Assembly([sheet], title="Overlay card", meta={"cartridge":"overlay-card", "params":{
    "outline":outline, "pattern":pattern, "panel_w":panel_w, "panel_h":panel_h,
    "corner_radius":corner_radius, "rows":rows, "columns":columns, "pitch_x":pitch_x,
    "pitch_y":pitch_y, "cutout_w":cutout_w, "cutout_h":cutout_h, "cutouts":cutouts, "stock":stock}})
print(f"overlay-card: pattern={pattern} outline={panel_w:g}x{panel_h:g}mm "
      f"openings={len(boxes)} connected={report.components} "
      f"minimum-feature={minimum:g}mm measured-min-bridge={report.min_bridge_mm} stock={stock}")
