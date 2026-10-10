"""Paper spring (witch's ladder) — sheet-hyperobjects cartridge (Pliego).

Two strips glued crosswise at one end and folded over each other in turn, A over B, B over A,
until both are used up: the stack is a spring. Let go and it stretches by itself; squash it and
it closes. Two modes, by cross-section:

- `square`: two strips of square panels (side `width`), crossed at 90°. Strip A folds across
  its panels' left and right edges, strip B across their top and bottom edges.
- `triangular`: two strips of equilateral triangles (side `width`), the second turned by 120°
  about the first triangle. A strip of triangles folded at every edge stacks every triangle on
  the first, the fold line moving round its three edges; the two strips take turns at the edges.

Each strip is two sheets' worth of geometry written here: a straight strip with a crease at every
panel boundary, alternately valley and mountain (every fold takes the strip's tail over the top
of the stack, and the panel underneath is face-down every other time). No crease ends inside a
strip, so every folded state of a strip is consistent; folded flat, every panel of both strips
lies on the glued first panel. The strips are glued at their first panels (a glue join, satisfied
in the initial frame); the sheets are placed crosswise with `placement`.

The fold program is physical: the making, one fold per step in turn, then `release`. A released
crease (spec §5.6) springs back only by about the stock's yield angle — that partial springing
of every crease at once is what stretches the spring. Two more steps stretch it by hand and
squash it shut, and a last release lets it spring again. Layers, contact and the strips locking
each other are the physics engine's work.
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
folds = int(clamp(PARAM(lambda: folds, 12), 4, 24))
width = clamp(PARAM(lambda: width, 25.0), 12.0, 50.0)
stretch = clamp(PARAM(lambda: stretch, 120.0), 60.0, 170.0)
stock = str(PARAM(lambda: stock, "copy-80"))
if run_mode not in ("square", "triangular"):
    raise ValueError(f"mode {run_mode!r} must be 'square' or 'triangular'")
if stock not in ("copy-80", "kraft-120", "kami", "cardstock-160"):
    raise ValueError(f"stock {stock!r} is not one this cartridge offers")
GLUE_INSET = 1.5
STRIP = {"A": L4("Strip A", "Tira A", "Bande A", "Tira A"),
         "B": L4("Strip B", "Tira B", "Bande B", "Tira B")}


def strip(name):
    """One strip in its own sheet frame: outline, crease segments, first panel, its centroid."""
    w = width
    if run_mode == "square":
        outline = pliego.rectangle((folds + 1) * w, w)
        lines = [((k * w, 0.0), (k * w, w)) for k in range(1, folds + 1)]
        first = [(0.0, 0.0), (w, 0.0), (w, w), (0.0, w)]
        turn = 90.0
    else:
        h = w * math.sqrt(3.0) / 2.0
        b = [(k * w, 0.0) for k in range(folds + 2)]
        t = [((k + 0.5) * w, h) for k in range(folds + 2)]
        lines = []
        for j in range(folds):                 # crease between triangle j and j + 1
            i = j // 2
            lines.append((b[i + 1], t[i]) if j % 2 == 0 else (b[i + 1], t[i + 1]))
        p = folds // 2                         # last triangle is number `folds`
        if folds % 2 == 0:
            outline = b[:p + 2] + t[:p + 1][::-1]
        else:
            outline = b[:p + 2] + t[:p + 2][::-1]
        first = [b[0], b[1], t[0]]
        turn = 120.0
    sheet = pliego.Sheet(f"strip-{name.lower()}", outline, stock=stock, grain_deg=0.0,
                         label=STRIP[name])
    marks = [sheet.crease(a, c, "valley" if k % 2 == 0 else "mountain")
             for k, (a, c) in enumerate(lines)]
    g = (sum(x for x, _ in first) / len(first), sum(y for _, y in first) / len(first))
    return sheet, marks, first, g, turn


sheet_a, marks_a, first, g, turn = strip("A")
sheet_b, marks_b, _, _, _ = strip("B")

# B is A turned by `turn` about the first panel's centre, lying on top of it.
th = math.radians(turn)
c, s = math.cos(th), math.sin(th)
tx, ty = g[0] - (c * g[0] - s * g[1]), g[1] - (s * g[0] + c * g[1])
caliper = {"copy-80": 0.1, "kraft-120": 0.16, "kami": 0.072, "cardstock-160": 0.2}[stock]
# world: sheet (u, v) ↦ (u, 0, −v); turning by θ in the sheet is turning by θ about +Y
sheet_b.placement = pliego.Placement(origin=(tx, 0.9 * caliper, -ty),
                                     rotation=(0.0, math.sin(th / 2.0), 0.0, math.cos(th / 2.0)))
inset = []
for x, y in first:
    dx, dy = g[0] - x, g[1] - y
    d = math.hypot(dx, dy)
    inset.append((x + dx / d * GLUE_INSET, y + dy / d * GLUE_INSET))
glue = pliego.glue("glue-first-panels", sheet_b, inset, sheet_a, (c, -s, s, c, tx, ty),
                   side="front")

for sheet in (sheet_a, sheet_b):
    arr = sheet.build()
    if pliego.kinematics.interior_vertices(arr):
        raise ValueError("paper-spring: a crease ends inside a strip")
print(f"spring: section={run_mode} folds_per_strip={folds} panel={width:g}mm "
      f"strip_length={max(p.x for p in sheet_a.build().vertices):.1f}mm "
      f"interior_vertices=0 glue=first panels (inset {GLUE_INSET} mm)")


def signed(m, magnitude):
    return magnitude if m.assignment == "V" else -magnitude


steps = []
for k in range(folds):
    for name, marks in (("A", marks_a), ("B", marks_b)):
        other = "B" if name == "A" else "A"
        steps.append(pliego.Step(
            f"fold-{name.lower()}-{k + 1}",
            L4(f"Fold strip {name} over strip {other} ({k + 1}/{folds})",
               f"Dobla la tira {name} sobre la tira {other} ({k + 1}/{folds})",
               f"Replier la bande {name} sur la bande {other} ({k + 1}/{folds})",
               f"Dobre a tira {name} sobre a tira {other} ({k + 1}/{folds})"),
            [(marks[k], signed(marks[k], 180.0))], duration_ms=600))
every = marks_a + marks_b
LET_GO_NOTE = L4("Released, every crease springs back by about the paper's yield angle at once: "
                 "the spring stretches by itself.",
                 "Al soltarlos, todos los pliegues se abren a la vez cerca del ángulo de cedencia "
                 "del papel: el resorte se estira solo.",
                 "Relâchés, tous les plis se rouvrent à la fois d'environ l'angle de "
                 "plastification du papier : le ressort s'allonge tout seul.",
                 "Soltos, todos os vincos abrem ao mesmo tempo cerca do ângulo de cedência do "
                 "papel: a mola estica sozinha.")
steps += [
    pliego.Step("let-go", L4("Let go", "Suelta", "Lâcher", "Solte"), release=list(every),
                duration_ms=2000, note=LET_GO_NOTE),
    pliego.Step("stretch",
                L4("Pull the ends apart: the spring stretches",
                   "Separa los extremos: el resorte se estira",
                   "Écarter les extrémités : le ressort s'allonge",
                   "Afaste as pontas: a mola estica"),
                [(m, signed(m, stretch)) for m in every], duration_ms=2000,
                note=L4(f"Every crease opened to {stretch:.0f}°.",
                        f"Todos los pliegues abiertos a {stretch:.0f}°.",
                        f"Tous les plis ouverts à {stretch:.0f}°.",
                        f"Todos os vincos abertos a {stretch:.0f}°.")),
    pliego.Step("squash",
                L4("Squash it shut", "Aplástalo hasta cerrarlo", "L'écraser jusqu'à le fermer",
                   "Esmague-a até fechar"),
                [(m, signed(m, 180.0)) for m in every], duration_ms=1500),
    pliego.Step("let-go-again", L4("Let go again", "Suelta otra vez", "Lâcher à nouveau",
                                   "Solte outra vez"),
                release=list(every), duration_ms=2000, note=LET_GO_NOTE),
]

result = pliego.Assembly(
    [sheet_a, sheet_b], joins=[glue],
    controls=[pliego.sequence_control(label=L4("Fold program", "Secuencia de pliegues",
                                               "Séquence de pliage", "Sequência de dobras"))],
    sequence=pliego.Sequence(steps, mode="physical"),
    title="Paper spring",
)
