"""Pleated hypar — sheet-hyperobjects cartridge (Pliego).

The pleated hyperbolic paraboloid of the Bauhaus preliminary course: a square pleated in
concentric squares, alternately mountain and valley, with both diagonals creased, collapsed into a
flat bundle and let go — it springs open into a saddle. The circular variant pleats concentric
circles round a central hole and twists into a saddle by itself. Two modes:

- `square`: `rings` concentric squares (spacing `size / (2·rings + 2)`), alternating; the two
  diagonals run corner to corner, cut into segments by the squares. The classic instruction folds
  both diagonals as valleys and lets half the segments reverse as the bundle collapses; this
  cartridge assigns the reversed segments directly, so that every vertex is flat-foldable. At a
  square's corner the sectors are 45°, 45°, 135°, 135° (Kawasaki); the two square edges share an
  assignment and the two diagonal segments differ (three of one kind: Maekawa); so the diagonal
  segments alternate along each half-diagonal. At the centre, where four 90° sectors meet, three
  halves start as valleys and one as a mountain. The script runs `pliego.flatfold.check`.
- `circular`: `rings` concentric circles, alternating, round a central hole; each circle is a
  regular polygon of `segments` sides (the kernel has no curved crease; this is the
  segmentation, recorded in `pliego:meta`), inscribed in its true circle.

Neither folds into its saddle with rigid flat panels: Demaine, Demaine, Hart, Price and Tachi
(2011) proved that the square hypar cannot take that shape with flat faces and only its own
creases (the paper twists between the creases, or needs extra ones), and the circular pleat needs
curved, bending panels. Both programs are physical. The square's flat bundle is exact as far as
local flat-foldability goes (every vertex passes; the layer order of the whole stack is not
checked); the saddle is what the paper does after `release`, which (spec §5.6) only lets each
crease spring back by about the stock's yield angle — computing the saddle is the physics
engine's job.
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


run_mode = PARAM(lambda: mode, "square")  # noqa: F821 - injected by the runner
rings = int(clamp(PARAM(lambda: rings, 8), 3, 16))
size = clamp(PARAM(lambda: size, 200.0), 100.0, 400.0)
hole = clamp(PARAM(lambda: hole, 0.12), 0.06, 0.4)
segments = int(clamp(PARAM(lambda: segments, 48), 24, 96))
stock = str(PARAM(lambda: stock, "kami"))
if run_mode not in ("square", "circular"):
    raise ValueError(f"mode {run_mode!r} must be 'square' or 'circular'")
if stock not in ("kami", "copy-80", "washi-kozo-30", "tant"):
    raise ValueError(f"stock {stock!r} is not one this cartridge offers")
flip = {"valley": "mountain", "mountain": "valley"}
LABEL = L4("Fold program", "Secuencia de pliegues", "Séquence de pliage", "Sequência de dobras")
LET_GO = L4("Let go: the bundle springs open into a saddle",
            "Suelta: el paquete se abre de golpe en una silla de montar",
            "Lâcher : le paquet s'ouvre d'un coup en selle de cheval",
            "Solte: o pacote abre-se de repente numa sela")
LET_GO_NOTE = L4("Released, each crease springs back only by about the paper's yield angle; the "
                 "pleats stay mostly closed and the sheet twists into a hyperbolic paraboloid. "
                 "That shape comes from the physics engine.",
                 "Al soltarlos, cada pliegue se abre solo lo que permite el ángulo de cedencia "
                 "del papel; los pliegues siguen casi cerrados y la hoja se tuerce en un "
                 "paraboloide hiperbólico. Esa forma la calcula el motor físico.",
                 "Relâché, chaque pli ne se rouvre que d'environ l'angle de plastification du "
                 "papier ; les plis restent presque fermés et la feuille se tord en paraboloïde "
                 "hyperbolique. Cette forme vient du moteur physique.",
                 "Solto, cada vinco abre apenas cerca do ângulo de cedência do papel; as pregas "
                 "ficam quase fechadas e a folha torce-se num paraboloide hiperbólico. Essa "
                 "forma vem do motor físico.")


def signed(m, magnitude):
    return magnitude if m.assignment == "V" else -magnitude


if run_mode == "square":
    sheet = pliego.Sheet("hypar", pliego.square(size), stock=stock, grain_deg=90.0,
                         label=L4("Square sheet", "Hoja cuadrada", "Feuille carrée",
                                  "Folha quadrada"))
    c, step = size / 2.0, size / (2.0 * rings + 2.0)
    squares, diagonals = [], []
    for k in range(1, rings + 1):
        a = k * step
        kind = "valley" if (rings - k) % 2 == 0 else "mountain"      # outermost square: valley
        ring = [(c + a, c + a), (c - a, c + a), (c - a, c - a), (c + a, c - a)]
        for i in range(4):
            squares.append(sheet.crease(ring[i], ring[(i + 1) % 4], kind))
    starts = {(1, 1): "valley", (-1, 1): "valley", (-1, -1): "valley", (1, -1): "mountain"}
    for (sx, sy), kind in starts.items():
        for k in range(rings + 1):
            r0 = k * step
            r1 = c if k == rings else (k + 1) * step
            diagonals.append(sheet.crease((c + sx * r0, c + sy * r0), (c + sx * r1, c + sy * r1),
                                          kind))
            kind = flip[kind]
    creases = squares + diagonals
    arr = sheet.build()
    reports, issues = pliego.flatfold.check(arr)
    errors = [i for i in issues if i["level"] == "error"]
    if errors:
        raise ValueError(f"pleated-hypar: not flat-foldable: {errors[0]['detail']}")
    print(f"flatfold: square hypar rings={rings} vertices={len(reports)} maekawa=ok kawasaki=ok "
          f"big_little_big=ok exact={sum(1 for r in reports if r.kawasaki_exact)}/{len(reports)}")
    steps = [
        pliego.Step("pleat-squares",
                    L4("Pleat the concentric squares, mountain and valley in turn",
                       "Pliega los cuadrados concéntricos, monte y valle alternados",
                       "Plisser les carrés concentriques, montagne et vallée tour à tour",
                       "Pregue os quadrados concêntricos, montanha e vale alternados"),
                    [(m, signed(m, 90.0)) for m in squares]
                    + [(m, signed(m, 45.0)) for m in diagonals], duration_ms=3000),
        pliego.Step("collapse",
                    L4("Collapse along the diagonals into a flat bundle",
                       "Cierra a lo largo de las diagonales hasta formar un paquete plano",
                       "Refermer le long des diagonales en un paquet plat",
                       "Feche ao longo das diagonais num pacote plano"),
                    [(m, signed(m, 180.0)) for m in creases], duration_ms=3000,
                    note=L4("Exact flat-folded bundle: every crease at 180°.",
                            "Paquete plegado en plano exacto: todos los pliegues a 180°.",
                            "Paquet replié à plat exact : tous les plis à 180°.",
                            "Pacote dobrado rente exato: todas as dobras a 180°.")),
        pliego.Step("let-go", LET_GO, release=list(creases), duration_ms=3000,
                    note=LET_GO_NOTE),
    ]
    targets = {"flat-folded": {"angles": {m: signed(m, 180.0) for m in creases}}}
    title = "Pleated hypar"
else:
    R = size / 2.0
    c = (R, R)
    r_hole = hole * R
    sheet = pliego.Sheet("hypar", pliego.circle(c, R, segments), stock=stock, grain_deg=90.0,
                         label=L4("Round sheet", "Hoja redonda", "Feuille ronde",
                                  "Folha redonda"))
    sheet.hole(pliego.circle(c, r_hole, segments))
    gap = (R - r_hole) / (rings + 1)
    circles = []
    for k in range(1, rings + 1):
        r = r_hole + k * gap
        kind = "valley" if (rings - k) % 2 == 0 else "mountain"
        pts = pliego.circle(c, r, segments)
        circles.append(sheet.path(list(pts) + [pts[0]], kind))
    arr = sheet.build()
    chord = 2.0 * R * math.sin(math.pi / segments)
    sagitta = R * (1.0 - math.cos(math.pi / segments))
    print(f"segmentation: circles={rings} segments={segments} outer_chord_mm={chord:.2f} "
          f"max_sagitta_mm={sagitta:.3f} hole_mm={2 * r_hole:.1f}")
    steps = [
        pliego.Step("pleat-circles",
                    L4("Pleat the concentric circles, mountain and valley in turn",
                       "Pliega los círculos concéntricos, monte y valle alternados",
                       "Plisser les cercles concentriques, montagne et vallée tour à tour",
                       "Pregue os círculos concêntricos, montanha e vale alternados"),
                    [(m, signed(m, 30.0)) for m in circles], duration_ms=3000,
                    note=L4("A pleated ring cannot stay flat: the panels bend and the disc "
                            "starts to twist.",
                            "Un anillo plisado no puede quedarse plano: los paneles se curvan y "
                            "el disco empieza a torcerse.",
                            "Un anneau plissé ne peut pas rester plan : les panneaux se courbent "
                            "et le disque commence à se tordre.",
                            "Um anel plissado não pode ficar plano: os painéis curvam-se e o "
                            "disco começa a torcer-se.")),
        pliego.Step("press-pleats",
                    L4("Press the pleats together all round",
                       "Junta los pliegues a todo alrededor",
                       "Resserrer les plis tout autour",
                       "Junte as pregas a toda a volta"),
                    [(m, signed(m, 60.0)) for m in circles], duration_ms=3000),
        pliego.Step("let-go", LET_GO, release=list(circles), duration_ms=3000,
                    note=LET_GO_NOTE),
    ]
    targets = {}
    title = "Pleated circular hypar"

result = pliego.Assembly(
    [sheet],
    controls=[pliego.sequence_control(label=LABEL)],
    sequence=pliego.Sequence(steps, mode="physical"),
    targets=targets,
    title=title,
    meta={"segmentation": {"circle_segments": segments}} if run_mode == "circular" else {},
)
