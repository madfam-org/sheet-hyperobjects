"""Paper lantern — sheet-hyperobjects cartridge (Pliego).

The slit lantern: a sheet of length W + g and height H is folded in half along its length
(y = H/2, printed side out), cut from the fold with n slits that stop short of the edges, unfolded,
rolled into a cylinder and glued along the strip g at one end. Pushed down from the top, the strips
between the slits bow outward.

Mode `make` is the making: fold in half, cut through both layers from the fold, open, let go. The
crease keeps its memory (spec §5.6); the program is physical and the preview plays it.

Mode `lantern` is the finished lantern. This lantern is scored: score lines (assignment `F`)
continue each slit through the top and bottom bands, and two more cross the strips at the slit
ends. So the rolled form is a crisp regular n-sided prism whose facet edges run through the slits,
and the `initial` frame is an exact isometric pose: every facet is one strip wide and the glue strip
lies on the first half facet, which a `glue` join welds. The bow is a rigid two-panel model: each
strip's lower half tilts outward by γ about the bottom line, folds by −2γ at the real middle crease
and the upper half tilts back by γ, so the top ring moves straight down by (yt − yb)(1 − cos γ).
Every strip does the same, so the loops around the slits close; the script checks it with
`pliego.kinematics.closure_residual`. The bowed state is not written as a frame: where a slit
crosses the middle crease, the two strips share one vertex in a v1 document, and bowed strips
would need two positions for it (the cut-separation gap of v1 frames). Paper between the scores still bends a little (the strips
bow in a curve rather than as two flat panels), which needs the physics engine; the preview shows
the rigid model.
"""

import math

import pliego
from pliego import kinematics


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


def clamp(value, lo, hi):
    return max(lo, min(hi, float(value)))


def L4(en, es, fr, pt):
    return {"en": en, "es": es, "fr": fr, "pt": pt}


MIN_FEATURE = {"cardstock-160": 1.5, "kraft-120": 1.0, "copy-80": 1.0, "foil-paper": 1.5}

mode = str(PARAM(lambda: mode, "lantern"))
circumference = clamp(PARAM(lambda: circumference, 240.0), 150.0, 420.0)
height = clamp(PARAM(lambda: height, 150.0), 80.0, 300.0)
slits = int(clamp(PARAM(lambda: slits, 14), 8, 32))
band = clamp(PARAM(lambda: band, 25.0), 12.0, 60.0)
bow = clamp(PARAM(lambda: bow, 50.0), 10.0, 70.0)
stock = str(PARAM(lambda: stock, "cardstock-160"))
if mode not in ("make", "lantern"):
    raise ValueError(f"mode {mode!r} must be make or lantern")
if stock not in MIN_FEATURE:
    raise ValueError(f"stock {stock!r} is not one this cartridge offers")
mf = MIN_FEATURE[stock]

W, H, n = circumference, height, slits
s = W / n                          # strip width = prism facet width
g = min(12.0, 0.45 * s)            # glue strip at the right end
yb, yt = band, H - band
if yt - yb < 20.0:
    raise ValueError("the bands leave less than 20 mm of slit: lower the band or raise the height")
if s < 4.0 * mf:
    raise ValueError(f"{n} slits leave strips of {s:.1f} mm: use fewer slits or a longer sheet")
xs = [(i + 0.5) * s for i in range(n)]

sheet = pliego.Sheet("lantern", pliego.rectangle(W + g, H), stock=stock, grain_deg=90.0,
                     label=L4("Paper lantern", "Farol de papel", "Lanterne en papier",
                              "Lanterna de papel"))
for x in xs:
    sheet.cut([(x, yb), (x, yt)])
middle = sheet.mountain((0.0, H / 2), (W + g, H / 2), 180.0,
                        label=L4("Middle fold", "Doblez central", "Pli du milieu",
                                 "Dobra do meio"))

# scored lines (assignment F): the facet edges of the rim, continuing each slit through the top and
# bottom bands, and one line across every strip at each slit end. They make the rolled lantern a
# crisp n-sided prism and let each strip fold at its ends and at the middle crease.
facets = []
for x in xs:
    facets.append(sheet.score((x, 0.0), (x, yb)))
    facets.append(sheet.score((x, yt), (x, H)))
low = sheet.score((0.0, yb), (W + g, yb), label=L4("Lower strip ends", "Base de las tiras",
                                                  "Pied des bandes", "Base das tiras"))
high = sheet.score((0.0, yt), (W + g, yt), label=L4("Upper strip ends", "Remate de las tiras",
                                                   "Haut des bandes", "Topo das tiras"))

report = pliego.papercut.analyze(sheet, min_feature_mm=mf)
if not report.ok:
    raise ValueError("paper-lantern papercut check failed: "
                     + "; ".join(i["detail"] for i in report.issues if i["level"] == "error"))

if mode == "make":
    steps = [
        pliego.Step("fold-in-half", L4("Fold the sheet in half along its length, printed side out",
                                       "Dobla la hoja a lo largo por la mitad, con la cara impresa "
                                       "hacia fuera",
                                       "Plier la feuille en deux dans sa longueur, face imprimée "
                                       "à l'extérieur",
                                       "Dobre a folha ao meio no comprimento, com o lado impresso "
                                       "para fora"),
                    [(middle, None)], duration_ms=2000),
        pliego.Step("cut-and-open", L4("Cut the slits from the fold through both layers, then open "
                                       "the sheet",
                                       "Corta las ranuras desde el doblez a través de las dos "
                                       "capas y abre la hoja",
                                       "Découper les fentes depuis le pli à travers les deux "
                                       "couches, puis ouvrir la feuille",
                                       "Corte as fendas a partir da dobra através das duas camadas "
                                       "e abra a folha"),
                    [(middle, 0.0)], duration_ms=2000),
        pliego.Step("let-go", L4("Let go: the middle fold keeps a little of its crease",
                                 "Suelta: el doblez central conserva un poco de su marca",
                                 "Lâcher : le pli du milieu garde un peu de sa marque",
                                 "Solte: a dobra do meio guarda um pouco do vinco"),
                    release=[middle], duration_ms=1500),
    ]
    result = pliego.Assembly(
        [sheet],
        controls=[pliego.sequence_control(label=L4("Make it", "Hacerlo", "Le fabriquer",
                                                   "Fazer"))],
        sequence=pliego.Sequence(steps, mode="physical"),
        title="Paper lantern",
        meta={"min_feature_mm": mf},
    )
else:
    turn = -360.0 / n                       # printed side out: each facet edge turns away
    rolled = {m: turn for m in facets}
    ROOT = (s / 4.0, yb / 2.0)
    arr = sheet.build()

    def residual(gamma):
        ang = {e: a for m, a in rolled.items() for e in m.edges()}
        ang.update({e: gamma for m in (low, high) for e in m.edges()})
        ang.update({e: -2.0 * gamma for e in middle.edges()})
        return kinematics.closure_residual(arr, ang, pliego.P(*ROOT))

    loop = max(residual(gam) for gam in (0.0, bow / 2.0, bow))
    if loop > 1e-6:
        raise ValueError(f"the lantern does not close: loop residual {loop:.3g} mm")
    drop = (yt - yb) * (1.0 - math.cos(math.radians(bow)))
    radius = s / (2.0 * math.sin(math.pi / n))
    print(f"paper-lantern: facets={n} facet={s:.2f}mm radius={radius:.1f}mm glue={g:.1f}mm "
          f"bow={bow}deg drop={drop:.1f}mm loop_residual={loop:.1e}mm")
    # stand it up: +90° about world X maps the sheet's height (−Z) to +Y, the rolled prism (which
    # curls below the sheet) to −Z; shift it so its axis passes near the origin
    q = math.sqrt(0.5)
    sheet.placement = pliego.Placement(origin=(0.0, 0.0, round(radius, 6)),
                                       rotation=(q, 0.0, 0.0, q))
    seam = pliego.glue("seam", sheet, [(W + 0.5, 0.5), (W + g - 0.5, 0.5), (W + g - 0.5, H - 0.5),
                                       (W + 0.5, H - 0.5)], sheet, (1.0, 0.0, 0.0, 1.0, -W, 0.0),
                       "back")  # tucked inside: the printed side is out
    steps = [pliego.Step("bow-out", L4("Push the top down: the strips bow outward",
                                       "Empuja la parte de arriba: las tiras se arquean hacia "
                                       "fuera",
                                       "Appuyer sur le haut : les bandes se bombent vers "
                                       "l'extérieur",
                                       "Empurre o topo para baixo: as tiras arqueiam para fora"),
                         [(low, bow), (middle, -2.0 * bow), (high, bow)], duration_ms=2500)]
    result = pliego.Assembly(
        [sheet],
        joins=[seam],
        controls=[pliego.sequence_control(label=L4("Shape it", "Darle forma", "Le former",
                                                   "Dar forma"))],
        sequence=pliego.Sequence(steps, mode="kinematic"),
        initial={"angles": dict(rolled), "root": ROOT},
        title="Paper lantern",
        meta={"min_feature_mm": mf},
    )
