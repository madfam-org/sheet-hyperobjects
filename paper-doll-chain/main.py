"""Paper doll chain — sheet-hyperobjects cartridge (Pliego).

Accordion fold-and-cut: a strip of N panels is pleated into an accordion one panel wide
(`pliego.simplefold`, alternate valley and mountain folds), one figure is cut through all N
layers (`pliego.foldcut`), and the strip opens into a chain of N figures. Each figure is
symmetric about its panel's centre line and reaches both folds (the hands, and for some figures
the hem or the lobes), so the figures stay joined: the parts of the figure that touch a fold are
never cut. Figures (ORIGINAL geometric designs): a person, a figure in a dress, a heart.

A figure is a half outline in the panel's unit box (s from the centre line, 0…0.5 at the fold; v
up, 0…1), from the top of the centre line to the bottom of it, with touch segments at s = 0.5.
The removed regions are the gaps between the figure and the folds: above the first touch, below
the last, and between touches on each side. They cross the folds by 1 mm so no region edge lies on
a fold line. `pliego.papercut.analyze` checks one connected chain and the stock's minimum feature.
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


MIN_FEATURE = {"copy-80": 1.0, "kraft-120": 1.0, "kami": 1.0, "cardstock-160": 1.5}

figure = str(PARAM(lambda: figure, "person"))
panels = int(clamp(PARAM(lambda: panels, 6), 3, 10))
panel_width = clamp(PARAM(lambda: panel_width, 40.0), 25.0, 80.0)
height = clamp(PARAM(lambda: height, 90.0), 50.0, 200.0)
stock = str(PARAM(lambda: stock, "copy-80"))
if figure not in ("person", "dress", "heart"):
    raise ValueError(f"figure {figure!r} must be person, dress or heart")
if stock not in MIN_FEATURE:
    raise ValueError(f"stock {stock!r} is not one this cartridge offers")
mf = MIN_FEATURE[stock]


def head(v_c, r):
    """The head, from the top of the centre line round to the neck (right half)."""
    return [(r * math.sin(math.pi * k / 10) * 0.9, v_c + r * math.cos(math.pi * k / 10))
            for k in range(9)]


if figure == "person":
    half = head(0.86, 0.09) + [(0.045, 0.765), (0.14, 0.735), (0.5, 0.70), (0.5, 0.64),
                               (0.17, 0.645), (0.14, 0.60), (0.15, 0.40), (0.17, 0.05),
                               (0.23, 0.02), (0.23, 0.0), (0.06, 0.0), (0.05, 0.30), (0.0, 0.33)]
elif figure == "dress":
    half = head(0.86, 0.09) + [(0.045, 0.765), (0.14, 0.735), (0.5, 0.70), (0.5, 0.64),
                               (0.17, 0.645), (0.13, 0.60), (0.09, 0.50), (0.5, 0.22),
                               (0.5, 0.15), (0.12, 0.15), (0.11, 0.03), (0.16, 0.0),
                               (0.04, 0.0), (0.04, 0.14), (0.0, 0.14)]
else:  # heart
    half = [(0.25 - 0.25 * math.cos(math.pi * k / 12), 0.68 + 0.25 * math.sin(math.pi * k / 12))
            for k in range(13)]
    half += [(0.5, 0.60)]
    half += [(0.5 - 0.5 * (k / 8) ** 1.25 * 1.0, 0.60 - 0.50 * (k / 8)) for k in range(1, 9)]
    half[-1] = (0.0, 0.10)

W, H, pw = panels * panel_width, height, panel_width

# ── fold the accordion: from the right end, each fold takes everything right of the line under or
# over, so the stack ends on the first panel [0, pw] ──
state = pliego.simplefold.FoldedState(pliego.rectangle(W, H))
for k in range(panels - 1, 0, -1):
    x = k * pw
    state.fold(((x, H), (x, 0.0)), "valley" if k % 2 else "mountain")
if len(state.layers) != panels:
    raise ValueError(f"expected {panels} layers, the accordion made {len(state.layers)}")


def R(p):
    return (pw * (0.5 + p[0]), H * p[1])


def Lm(p):
    return (pw * (0.5 - p[0]), H * p[1])


touch = [i for i in range(len(half) - 1) if half[i][0] == 0.5 and half[i + 1][0] == 0.5]
if not touch:
    raise ValueError("the figure never reaches the fold: the chain would fall apart")
for i in touch:
    if (half[i][1] - half[i + 1][1]) * H < 2.0 * mf:
        raise ValueError("a joint between figures is narrower than twice the minimum feature")
pieces, start = [], 0
for i in touch:
    pieces.append(half[start:i + 1])
    start = i + 1
pieces.append(half[start:])
top, bottom = pieces[0], pieces[-1]
yt, yb = H * top[-1][1], H * bottom[0][1]
regions = [[(-1.0, yt)] + [Lm(p) for p in reversed(top)] + [R(p) for p in top[1:]]
           + [(pw + 1.0, yt), (pw + 1.0, H + 1.0), (-1.0, H + 1.0)]]
regions.append([R(p) for p in bottom] + [Lm(p) for p in reversed(bottom[:-1])]
               + [(-1.0, yb), (-1.0, -1.0), (pw + 1.0, -1.0), (pw + 1.0, yb)])
for piece in pieces[1:-1]:
    y0, y1 = H * piece[0][1], H * piece[-1][1]
    regions.append([R(p) for p in piece] + [(pw + 1.0, y1), (pw + 1.0, y0)])
    regions.append([Lm(p) for p in piece] + [(-1.0, y1), (-1.0, y0)])

LABEL = L4("Paper doll chain", "Cadena de muñecos de papel", "Farandole de papier",
           "Corrente de bonecos de papel")
cut = pliego.foldcut.cut(state, regions, id="doll-chain", stock=stock, grain_deg=0.0,
                         label=LABEL)
if not cut.connected:
    raise ValueError(f"the cut leaves {len(cut.islands)} loose pieces")
report = pliego.papercut.analyze(cut.sheet, min_feature_mm=mf)
if not report.ok:
    raise ValueError("paper-doll-chain papercut check failed: "
                     + "; ".join(i["detail"] for i in report.issues if i["level"] == "error"))

sheet = cut.sheet
pleats = [m for m in sheet.marks if m.assignment in ("M", "V") and m.edges()]
steps = [
    pliego.Step("pleat", L4("Pleat the strip into an accordion, one panel wide",
                            "Pliega la tira en acordeón, de un panel de ancho",
                            "Plier la bande en accordéon, large d'un panneau",
                            "Dobre a tira em sanfona, com um painel de largura"),
                [(m, None) for m in pleats], duration_ms=3000),
    pliego.Step("cut-and-open", L4("Cut one figure through every layer, then open the chain and "
                                   "press it flat",
                                   "Corta una figura a través de todas las capas, abre la cadena y "
                                   "alísala",
                                   "Découper une figure à travers toutes les couches, ouvrir la "
                                   "farandole et l'aplatir",
                                   "Corte uma figura através de todas as camadas, abra a corrente "
                                   "e alise-a"),
                [(m, 0.0) for m in pleats], duration_ms=3000),
]
result = pliego.Assembly(
    [sheet],
    controls=[pliego.sequence_control()],
    sequence=pliego.Sequence(steps, mode="physical"),
    title="Paper doll chain",
    meta={"min_feature_mm": mf},
)
print(f"paper-doll-chain: figure={figure} panels={panels} layers={len(state.layers)} "
      f"joints={len(touch)} min_bridge={report.min_bridge_mm}")
