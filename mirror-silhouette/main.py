"""Mirror silhouette — sheet-hyperobjects cartridge (Pliego).

Bilateral fold-and-cut: a rectangle is folded in half along its vertical centre line
(`pliego.simplefold`), half a motif is cut through both layers (`pliego.foldcut`), and the sheet
unfolds into a shape with one mirror line. Motifs (ORIGINAL geometric designs generated here): an
urn, a tree and a butterfly. As a `silhouette` the shape is kept and everything around it is cut
away; as a `window` the shape is cut out of a framed card. The kept paper is checked with
`pliego.papercut.analyze` (one piece, every bridge at least the stock's minimum feature).

Each motif is a half outline in a unit box (x from the fold outward, y up), from a point on the
fold at the top to a point on the fold at the bottom, plus detail holes inside the silhouette.
Cut regions cross the fold by 1 mm so no region edge lies on the fold line itself.
"""

import math

import pliego


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


def clamp(value, lo, hi):
    return max(lo, min(hi, float(value)))


def L4(en, es, fr, pt):
    return {"en": en, "es": es, "fr": fr, "pt": pt}


MIN_FEATURE = {"cardstock-160": 1.5, "copy-80": 1.0, "kami": 1.0, "elephant-hide-110": 1.0}
COLOURS = {"cardstock-160": "#1d1d1f", "copy-80": "#1d1d1f", "kami": "#1d1d1f",
           "elephant-hide-110": "#3b2f2a"}

motif = str(PARAM(lambda: motif, "urn"))
cutout = str(PARAM(lambda: cutout, "silhouette"))
width = clamp(PARAM(lambda: width, 150.0), 120.0, 300.0)
height = clamp(PARAM(lambda: height, 200.0), 120.0, 400.0)
stock = str(PARAM(lambda: stock, "cardstock-160"))
if motif not in ("urn", "tree", "butterfly"):
    raise ValueError(f"motif {motif!r} must be urn, tree or butterfly")
if cutout not in ("silhouette", "window"):
    raise ValueError(f"cutout {cutout!r} must be silhouette or window")
if stock not in MIN_FEATURE:
    raise ValueError(f"stock {stock!r} is not one this cartridge offers")
mf = MIN_FEATURE[stock]


def arc(cx, cy, rx, ry, a0, a1, k=10):
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / k)),
             cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / k))) for i in range(k + 1)]


def blob(cx, cy, rx, ry, k=14):
    return arc(cx, cy, rx, ry, 0.0, 360.0 * (k - 1) / k, k - 1)


# half outlines in the unit box: x ∈ [0, 1] from the fold, y ∈ [0, 1] up; top point first
if motif == "urn":
    half = [(0.0, 1.0), (0.42, 1.0), (0.46, 0.96), (0.30, 0.93), (0.24, 0.86)]
    half += arc(0.24, 0.60, 0.70, 0.26, 90.0, -90.0, 14)[1:]        # the body's swelling
    half += [(0.18, 0.30), (0.12, 0.22), (0.12, 0.12), (0.36, 0.06), (0.40, 0.0), (0.0, 0.0)]
    holes = [[(0.0, 0.48), (0.10, 0.60), (0.0, 0.72), (-0.05, 0.60)],     # diamond on the fold
             blob(0.42, 0.60, 0.07, 0.10), blob(0.20, 0.80, 0.04, 0.03)]
elif motif == "tree":
    half = [(0.0, 1.0), (0.30, 0.78), (0.16, 0.78), (0.50, 0.60), (0.27, 0.60), (0.70, 0.42),
            (0.38, 0.42), (0.92, 0.24), (0.10, 0.24), (0.10, 0.06), (0.30, 0.0), (0.0, 0.0)]
    holes = [blob(0.16, 0.68, 0.045, 0.03), blob(0.30, 0.50, 0.05, 0.03),
             blob(0.45, 0.30, 0.05, 0.03), blob(0.0, 0.40, 0.05, 0.03)]
else:  # butterfly
    half = [(0.0, 0.80), (0.05, 0.84), (0.10, 0.86)]
    half += arc(0.50, 0.66, 0.46, 0.30, 110.0, -40.0, 18)[1:]       # forewing
    half += arc(0.36, 0.32, 0.34, 0.28, 30.0, -110.0, 14)[1:]       # hindwing
    half += [(0.06, 0.08), (0.05, 0.0), (0.0, 0.0)]
    holes = [blob(0.54, 0.70, 0.13, 0.09), blob(0.30, 0.30, 0.09, 0.07),
             blob(0.80, 0.78, 0.04, 0.035)]

W, H = width, height
AX = W / 2.0
box_h = 0.86 * H
box_w = 0.44 * W
y_base = (H - box_h) / 2.0


def to_sheet(p):
    return (AX + p[0] * box_w, y_base + p[1] * box_h)


outline = [to_sheet(p) for p in half]
detail = [[to_sheet(p) for p in h] for h in holes]
if min(box_w, box_h) * 0.03 < mf:
    raise ValueError("the sheet is too small for this motif's finest parts: enlarge it")

state = pliego.simplefold.FoldedState(pliego.rectangle(W, H))
state.fold(((AX, 0.0), (AX, H)), "valley")
y_top, y_bottom = outline[0][1], outline[-1][1]
if cutout == "silhouette":
    # everything on the folded half outside the half outline goes; details are holes inside it
    regions = [[(AX - 1.0, -1.0), (W + 1.0, -1.0), (W + 1.0, H + 1.0), (AX - 1.0, H + 1.0),
                (AX - 1.0, y_top)] + outline[1:-1] + [(AX - 1.0, y_bottom)]]
    regions += detail
else:
    # the shape is cut out of a framed card (inner details would fall out, so none are cut)
    regions = [[(AX - 1.0, y_top)] + outline[1:-1] + [(AX - 1.0, y_bottom)]]
LABEL = L4("Mirror silhouette", "Silueta en espejo", "Silhouette en miroir", "Silhueta espelhada")
colour = COLOURS[stock]
cut = pliego.foldcut.cut(state, regions, id="silhouette", stock=stock, grain_deg=90.0,
                         label=LABEL, front=colour, back=colour)
if not cut.connected:
    raise ValueError(f"the cut leaves {len(cut.islands)} loose pieces")
report = pliego.papercut.analyze(cut.sheet, min_feature_mm=mf)
if not report.ok:
    raise ValueError("mirror-silhouette papercut check failed: "
                     + "; ".join(i["detail"] for i in report.issues if i["level"] == "error"))

sheet = cut.sheet
fold = [m for m in sheet.marks if m.assignment in ("M", "V") and m.edges()]
steps = [
    pliego.Step("fold-in-half", L4("Fold the sheet in half along its centre line",
                                   "Dobla la hoja por la mitad sobre su eje central",
                                   "Plier la feuille en deux selon son axe",
                                   "Dobre a folha ao meio pelo eixo central"),
                [(m, None) for m in fold], duration_ms=2000),
    pliego.Step("cut-and-open", L4("Cut the half motif through both layers, then unfold and press "
                                   "flat",
                                   "Corta medio motivo a través de las dos capas, desdobla y "
                                   "alisa",
                                   "Découper le demi-motif à travers les deux couches, déplier et "
                                   "aplatir",
                                   "Corte meio motivo através das duas camadas, desdobre e alise"),
                [(m, 0.0) for m in fold], duration_ms=2500),
]
result = pliego.Assembly(
    [sheet],
    controls=[pliego.sequence_control()],
    sequence=pliego.Sequence(steps, mode="physical"),
    title="Mirror silhouette",
    meta={"min_feature_mm": mf},
)
print(f"mirror-silhouette: motif={motif} cutout={cutout} regions={len(regions)} "
      f"min_bridge={report.min_bridge_mm}")
