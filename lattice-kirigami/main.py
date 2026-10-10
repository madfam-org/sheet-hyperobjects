"""Lattice kirigami — sheet-hyperobjects cartridge (Pliego).

Rows of straight slits, staggered by half a pitch from row to row, turn a sheet into a mesh that
stretches far beyond what plain paper allows. Along a row the slits have length Ls and are
separated by ligaments of width g (pitch P = Ls + g); rows are h apart. Odd rows are shifted by
P/2, so the ligaments of one row sit at the middle of the slits of the next, and every other row
starts and ends with a half slit that runs off the side edge. Two uncut grip bands (top and
bottom) hold the pins.

Mode `fold-and-cut` builds the sheet the way it is made by hand: an accordion of pleats every
P/2, with the slits cut from alternate folds through both layers of each pleat (a slit centred on
a fold line is one cut from the fold). The pleat creases stay in the document, and the fold
program pleats the sheet, opens it and lets go (the creases keep their memory, spec §5.6).

Mode `stretch` is the same pattern cut flat (knife, plotter, laser) and pulled open, a physical
operation (tier C): the bottom grip band is pinned and the top band is pinned to a `translate`
driver pulled by the `pull` control. Version 1 frames cannot separate the two lips of a cut, so
the opening happens in the engine; the studio's preview keeps the sheet flat. The pull range is a
geometric estimate (every slit row opened by a quarter of the slit length); the paper decides how
far it really goes. The two modes are separate because pinned grip bands would fight the pleats.
"""

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


MIN_FEATURE = {"copy-80": 1.0, "kraft-120": 1.0, "cardstock-160": 1.5, "pp-300": 1.5}
BAND = 15.0  # mm, the uncut grip band at the top and bottom

width = clamp(PARAM(lambda: width, 180.0), 100.0, 300.0)
height = clamp(PARAM(lambda: height, 120.0), 80.0, 250.0)
slit_length = clamp(PARAM(lambda: slit_length, 30.0), 10.0, 60.0)
ligament = clamp(PARAM(lambda: ligament, 4.0), 1.0, 10.0)
spacing = clamp(PARAM(lambda: spacing, 6.0), 2.0, 20.0)
mode = str(PARAM(lambda: mode, "fold-and-cut"))
stock = str(PARAM(lambda: stock, "copy-80"))
if stock not in MIN_FEATURE:
    raise ValueError(f"stock {stock!r} is not one this cartridge offers")
if mode not in ("fold-and-cut", "stretch"):
    raise ValueError(f"mode {mode!r} must be fold-and-cut or stretch")
mf = MIN_FEATURE[stock]
if ligament < mf or spacing < mf:
    raise ValueError(f"ligament {ligament} mm and spacing {spacing} mm must both reach {stock}'s "
                     f"minimum feature {mf} mm")

if ligament / 2.0 < mf:
    raise ValueError(f"the edge ligaments are half a ligament wide: {ligament / 2.0} mm is below "
                     f"{stock}'s minimum feature {mf} mm; widen the ligament")
Ls, g, h = slit_length, ligament, spacing
P = Ls + g
half = P / 2.0
k = int(width // half)  # whole half-pitches across: every fold line falls on the pattern
if k < 4:
    raise ValueError("the sheet is narrower than two slit pitches: widen it or shorten the slits")
W = k * half
rows = int((height - 2.0 * BAND) // h) + 1
if rows < 3:
    raise ValueError("the sheet leaves fewer than three slit rows: make it taller")
H = height
y0 = (H - (rows - 1) * h) / 2.0  # centre the rows between the grip bands

sheet = pliego.Sheet("lattice", pliego.rectangle(W, H), stock=stock, grain_deg=90.0,
                     label=L4("Lattice kirigami", "Kirigami de retícula", "Kirigami en treillis",
                              "Kirigami em treliça"))
slits = 0
for j in range(rows):
    y = y0 + j * h
    for m in range(j % 2, k + 1, 2):  # slits centred on every other fold line, alternating
        x = m * half
        x_a, x_b = max(0.0, x - (P - g) / 2.0), min(W, x + (P - g) / 2.0)
        sheet.cut([(x_a, y), (x_b, y)])
        slits += 1

pleats = []
if mode == "fold-and-cut":
    for m in range(1, k):
        kind = "valley" if m % 2 else "mountain"
        pleats.append(sheet.crease(
            (m * half, 0.0), (m * half, H), kind, 180.0,
            label=L4(f"Pleat {m}", f"Pliegue {m} del acordeón", f"Pli {m} de l'accordéon",
                     f"Prega {m} da sanfona")))

report = pliego.papercut.analyze(sheet, min_feature_mm=mf)
if not report.ok:
    raise ValueError("lattice-kirigami papercut check failed: "
                     + "; ".join(i["detail"] for i in report.issues if i["level"] == "error"))

joins, mechanisms, controls, sequence = [], [], [], None
if mode == "stretch":
    # Pull range: every slit row opening by a quarter of the slit length (a geometric estimate).
    travel = round(rows * 0.25 * Ls, 3)
    controls.append(pliego.control("pull", "distance", L4("Pull", "Jalar", "Tirer", "Puxar"),
                                   0.0, 0.0, travel, "mm"))
    joins = [
        pliego.pin("grip-bottom", along=(sheet, [(0.0, BAND / 2.0), (W, BAND / 2.0)])),
        pliego.pin("grip-top", along=(sheet, [(0.0, H - BAND / 2.0), (W, H - BAND / 2.0)]),
                   mechanism="pull-apart"),
    ]
    mechanisms = [pliego.translate("pull-apart", "pull", (0.0, 0.0, -1.0), travel)]
else:
    edges = [p for p in pleats if p.edges()]
    steps = [
        pliego.Step("pleat", L4("Pleat the sheet into an accordion, one fold every half pitch",
                                "Pliega la hoja en acordeón, un doblez cada medio paso",
                                "Plier la feuille en accordéon, un pli tous les demi-pas",
                                "Dobre a folha em sanfona, uma dobra a cada meio passo"),
                    [(p, None) for p in edges], duration_ms=3000),
        pliego.Step("cut-and-open", L4("Cut the slits from alternate folds, then open the "
                                       "accordion",
                                       "Corta las ranuras desde dobleces alternos y abre el "
                                       "acordeón",
                                       "Découper les fentes depuis un pli sur deux, puis ouvrir "
                                       "l'accordéon",
                                       "Corte as fendas a partir de dobras alternadas e abra a "
                                       "sanfona"),
                    [(p, 0.0) for p in edges], duration_ms=3000),
        pliego.Step("let-go", L4("Let go: the pleats keep a little of their fold",
                                 "Suelta: los pliegues conservan un poco del doblez",
                                 "Lâcher : les plis gardent un peu de leur pliure",
                                 "Solte: as pregas guardam um pouco da dobra"),
                    release=edges, duration_ms=1500),
    ]
    sequence = pliego.Sequence(steps, mode="physical")
    controls.append(pliego.sequence_control(label=L4("Make it", "Hacerlo", "Le fabriquer",
                                                     "Fazer")))

result = pliego.Assembly(
    [sheet],
    joins=joins,
    mechanisms=mechanisms,
    controls=controls,
    sequence=sequence,
    title="Lattice kirigami",
    meta={"min_feature_mm": mf},
)
print(f"lattice: slits={slits} rows={rows} pitch={P:.2f}mm width={W:.2f}mm pleats={len(pleats)} "
      f"min_bridge={report.min_bridge_mm}")
