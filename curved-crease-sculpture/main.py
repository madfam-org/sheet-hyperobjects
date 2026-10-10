"""Curved-crease sculpture — sheet-hyperobjects cartridge (Pliego).

Paper folded along curves instead of straight lines: the panels between the creases must bend,
and the sheet takes a curved, self-supporting shape. Two modes:

- `arcs`: concentric semicircular arcs on a rectangle, centred on the middle of its bottom edge,
  alternately mountain and valley, each running from the bottom edge back to the bottom edge.
- `spiral`: `spirals` interleaved logarithmic spirals on a disc with a central hole,
  alternately mountain and valley, each running from the hole to the rim. Spirals of one growth
  rate are rotations of each other, so they never cross; each sweeps `turns` of a turn.

**Segmentation.** The kernel has no curved crease, so every curve is a polyline whose vertices
lie on the true curve. The number of segments is chosen so that no chord departs from its arc by
more than `tolerance` (the sagitta r·(1 − cos(Δθ/2)) ≤ tolerance); the script prints the counts
and the worst deviation, and records them in `pliego:meta`. The disc's rim and hole are regular
polygons whose vertices are the spirals' end points.

**Physics.** A curved crease cannot fold with flat panels: the paper on both sides bends along
rulings as the crease closes. There is no rigid motion to follow, so the fold program is physical:
fold the curves partway, press them further, then `release` — which (spec §5.6) lets each crease
spring back only by about the stock's yield angle, so the sheet settles into its sculpture. The
curved shape itself is computed by the physics engine.
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


run_mode = PARAM(lambda: mode, "arcs")  # noqa: F821 - injected by the runner
arcs = int(clamp(PARAM(lambda: arcs, 7), 3, 16))
width = clamp(PARAM(lambda: width, 240.0), 120.0, 400.0)
spirals = 2 * int(clamp(PARAM(lambda: spirals, 8), 4, 16) // 2)
turns = clamp(PARAM(lambda: turns, 0.5), 0.2, 1.0)
diameter = clamp(PARAM(lambda: diameter, 220.0), 120.0, 400.0)
hole = clamp(PARAM(lambda: hole, 0.15), 0.08, 0.4)
tolerance = clamp(PARAM(lambda: tolerance, 0.2), 0.05, 1.0)
stock = str(PARAM(lambda: stock, "copy-80"))
if run_mode not in ("arcs", "spiral"):
    raise ValueError(f"mode {run_mode!r} must be 'arcs' or 'spiral'")
if stock not in ("copy-80", "kami", "tant", "cardstock-160"):
    raise ValueError(f"stock {stock!r} is not one this cartridge offers")


def kinds(n):
    return ["valley" if (n - 1 - k) % 2 == 0 else "mountain" for k in range(n)]


def sagitta(r, dtheta):
    return r * (1.0 - math.cos(dtheta / 2.0))


if run_mode == "arcs":
    height = 0.6 * width
    centre = (width / 2.0, 0.0)
    r_max = 0.9 * min(width / 2.0, height)
    gap = r_max / (arcs + 0.5)
    sheet = pliego.Sheet("sculpture", pliego.rectangle(width, height), stock=stock,
                         grain_deg=90.0, label=L4("Sheet", "Hoja", "Feuille", "Folha"))
    creases, worst, counts = [], 0.0, []
    for k, kind in enumerate(kinds(arcs)):
        r = (k + 1) * gap
        n = max(8, math.ceil(math.pi / (2.0 * math.acos(max(-1.0, 1.0 - tolerance / r)))))
        pts = [(centre[0] + r * math.cos(math.pi * i / n), r * math.sin(math.pi * i / n))
               for i in range(n + 1)]
        creases.append(sheet.path(pts, kind))
        worst = max(worst, sagitta(r, math.pi / n))
        counts.append(n)
    seg = {"curves": arcs, "segments": counts, "max_deviation_mm": round(worst, 6)}
    print(f"segmentation: arcs={arcs} segments_per_arc={counts[0]}..{counts[-1]} "
          f"max_deviation_mm={worst:.4f} (tolerance {tolerance:g})")
    title = "Concentric arcs"
else:
    R, r0 = diameter / 2.0, diameter / 2.0 * hole
    c = (R, R)
    # rim/hole polygon: enough sides for the tolerance, a multiple of the spiral count
    sides = max(spirals * 4, math.ceil(math.pi / math.acos(1.0 - tolerance / R)))
    sides = spirals * math.ceil(sides / spirals)
    sweep_steps = max(1, round(turns * sides))
    sweep = 2.0 * math.pi * sweep_steps / sides       # each spiral ends on a rim vertex
    growth = math.log(R / r0) / sweep
    sheet = pliego.Sheet("sculpture", pliego.circle(c, R, sides), stock=stock, grain_deg=90.0,
                         label=L4("Disc", "Disco", "Disque", "Disco"))
    sheet.hole(pliego.circle(c, r0, sides))
    creases, worst = [], sagitta(R, 2.0 * math.pi / sides)
    # spiral samples: an angular step whose chord stays within tolerance at the outer radius
    steps_n = max(sweep_steps, math.ceil(sweep / (2.0 * math.acos(max(-1.0, 1.0 - tolerance
                                                                      / R)))))
    dth = sweep / steps_n
    for i, kind in enumerate(kinds(spirals)):
        th0 = 2.0 * math.pi * i / spirals
        pts = []
        for s in range(steps_n + 1):
            th = s * dth
            r = R if s == steps_n else r0 * math.exp(growth * th)
            pts.append((c[0] + r * math.cos(th0 + th), c[1] + r * math.sin(th0 + th)))
        creases.append(sheet.path(pts, kind))
    # a log spiral's chord deviation is bounded by the circle of the larger radius
    worst = max(worst, sagitta(R * math.exp(growth * dth), dth))
    crossing = math.degrees(math.atan(1.0 / growth))
    seg = {"curves": spirals, "segments": [steps_n] * spirals, "rim_sides": sides,
           "max_deviation_mm": round(worst, 6)}
    print(f"segmentation: spirals={spirals} segments_per_spiral={steps_n} rim_sides={sides} "
          f"sweep={math.degrees(sweep):.1f}° angle_to_radius={crossing:.2f}° "
          f"max_deviation_mm={worst:.4f} (tolerance {tolerance:g})")
    title = "Spiral curved-crease sculpture"


def signed(m, magnitude):
    return magnitude if m.assignment == "V" else -magnitude


BENDS = L4("A curved crease cannot close with flat panels: the paper bends along its rulings.",
           "Un pliegue curvo no puede cerrarse con paneles planos: el papel se curva a lo largo "
           "de sus generatrices.",
           "Un pli courbe ne peut pas se refermer avec des panneaux plans : le papier se courbe "
           "le long de ses génératrices.",
           "Uma dobra curva não pode fechar com painéis planos: o papel curva-se ao longo das "
           "suas geratrizes.")
steps = [
    pliego.Step("fold-curves",
                L4("Fold along every curve, mountain and valley in turn",
                   "Pliega a lo largo de cada curva, monte y valle alternados",
                   "Plier le long de chaque courbe, montagne et vallée tour à tour",
                   "Dobre ao longo de cada curva, montanha e vale alternados"),
                [(m, signed(m, 30.0)) for m in creases], duration_ms=3000, note=BENDS),
    pliego.Step("press-curves",
                L4("Press the curved pleats further: the sheet arches",
                   "Junta más los pliegues curvos: la hoja se arquea",
                   "Resserrer davantage les plis courbes : la feuille se cambre",
                   "Junte mais as pregas curvas: a folha arqueia-se"),
                [(m, signed(m, 75.0)) for m in creases], duration_ms=3000),
    pliego.Step("let-go",
                L4("Let go: the sculpture settles", "Suelta: la escultura se asienta",
                   "Lâcher : la sculpture trouve son équilibre", "Solte: a escultura assenta"),
                release=list(creases), duration_ms=3000,
                note=L4("Released, each crease springs back only by about the yield angle; the "
                        "bent panels and the creases balance in a curved shape that the physics "
                        "engine computes.",
                        "Al soltarlo, cada pliegue se abre solo cerca del ángulo de cedencia; "
                        "los paneles curvados y los pliegues se equilibran en una forma curva "
                        "que calcula el motor físico.",
                        "Relâché, chaque pli ne se rouvre que d'environ l'angle de "
                        "plastification ; les panneaux courbés et les plis s'équilibrent en une "
                        "forme courbe que calcule le moteur physique.",
                        "Solto, cada vinco abre apenas cerca do ângulo de cedência; os painéis "
                        "curvados e os vincos equilibram-se numa forma curva que o motor físico "
                        "calcula.")),
]

result = pliego.Assembly(
    [sheet],
    controls=[pliego.sequence_control(label=L4("Fold program", "Secuencia de pliegues",
                                               "Séquence de pliage", "Sequência de dobras"))],
    sequence=pliego.Sequence(steps, mode="physical"),
    title=title,
    meta={"segmentation": seg},
)
