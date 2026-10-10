"""Print folds — sheet-hyperobjects cartridge (Pliego).

One family, every commercial print fold, from one generator (parameter `style`):

* parallel folds — `letter` (tri-fold rolled in), `z-fold`, `gatefold`, `roll` (4–8 panels rolled
  in), `double-parallel`, `accordion` (4–8 panels);
* cross folds (the second fold runs across the first, through stacked layers) — `french`
  (right-angle fold: in half, then in half across), `cross` (in half, then a letter fold across),
  `map` (an accordion, then folded across in two or three).

The fold lines are not typed in. `main.py` folds the sheet with the kernel's simple-fold model
(`pliego.simplefold.FoldedState`), in the order a finisher folds it, one fold line through every
layer it meets. Each fold records its crease segments in the sheet frame with their M/V
assignment, so a fold that goes through stacked layers alternates valley and mountain across the
earlier folds by construction. Those segments become the sheet's creases (scored on card stock).

Finishing allowances come from the geometry: a panel that folds inside another stops short by the
`allowance` parameter or, when it is larger, by the thickness the wrapping fold has to go round,
(k + 1) × caliper for k layers inside the wrap. Gate doors stop short of the centre line.

The fold program is kinematic and exact: each fold turns from 0 to ±180° while every earlier fold
is held shut at exactly ±180°, so all layers it meets are coplanar and every crease of the fold
turns by the same angle (valley +, mountain −): the motion is linear in the angles and the
studio's interpolation is exact. A last step opens the outermost fold to `display_open`. The
script checks loop closure (`pliego.kinematics.closure_residual`) at every state, the finished
size against the expected panel and the panel widths against the minimum; it fails loud.
"""

import pliego


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


style = PARAM(lambda: style, "letter")                      # noqa: F821
sheet_width = float(PARAM(lambda: sheet_width, 297.0))      # noqa: F821
sheet_height = float(PARAM(lambda: sheet_height, 210.0))    # noqa: F821
stock = PARAM(lambda: stock, "copy-80")                     # noqa: F821
panels = int(PARAM(lambda: panels, 4))                      # noqa: F821
cross_panels = int(PARAM(lambda: cross_panels, 2))          # noqa: F821
allowance = float(PARAM(lambda: allowance, 1.6))            # noqa: F821
display_open = float(PARAM(lambda: display_open, 60.0))     # noqa: F821

STYLES = ("letter", "z-fold", "gatefold", "french", "roll", "double-parallel", "accordion",
          "cross", "map")
if style not in STYLES:
    raise ValueError(f"print-folds: unknown style {style!r}")
# gsm and caliper (mm) from the stock cards in materials/<slug>/stock.json
STOCKS = {"copy-80": (80, 0.10), "kraft-120": (120, 0.16), "cardstock-160": (160, 0.20),
          "cardstock-250": (250, 0.30), "cardstock-300": (300, 0.36)}
if stock not in STOCKS:
    raise ValueError(f"print-folds: unsupported stock {stock!r}")
GSM, CAL = STOCKS[stock]
# Text paper folds cleanly with a plain crease; card stock (160 g/m² and up here) cracks along the
# fold unless it is scored first (see the score-vs-crease object).
TREATMENT = "score" if GSM >= 160 else "crease"

W = pliego.clamp(sheet_width, 150.0, 900.0)
H = pliego.clamp(sheet_height, 100.0, 700.0)
n = int(pliego.clamp(panels, 4, 8))
m = int(pliego.clamp(cross_panels, 2, 3))
A = pliego.clamp(allowance, 0.5, 4.0)
OPEN = pliego.clamp(display_open, 0.0, 180.0)
MIN_PANEL = 25.0      # mm: below this a folding machine cannot hold the panel
SUB = 4               # exact substeps per fold


def L4(en, es, fr, pt):
    return {"en": en, "es": es, "fr": fr, "pt": pt}


def need(layers_inside):
    """The allowance for a panel tucked inside a fold that wraps `layers_inside` layers."""
    return max(A, (layers_inside + 1) * CAL)


def fmt(v):
    return f"{v:.1f}"


# ── the fold plan, per style: (directed line, valley|mountain, edge name, role) ──────────────
# FoldedState folds the part LEFT of the directed line over to the right; a line pointing down
# (−y) moves the part right of it, one pointing up moves the part left of it.


def up(x):
    return ((x, 0.0), (x, H))


def down(x):
    return ((x, H), (x, 0.0))


def east(y):
    return ((0.0, y), (W, y))        # moves the part above y


def west(y):
    return ((W, y), (0.0, y))        # moves the part below y


plan = []
xs = []                  # panel boundaries along x (sheet frame), for the read-proof line
ys = []
display = 1              # how many of the last folds the display step re-opens
allow_used = []
if style in ("letter", "roll"):
    k = 3 if style == "letter" else n
    steps_a = [need(k - i) for i in range(2, k)]           # a_i for panels 2 … k−1
    allow_used = steps_a
    w = (W + sum(sum(steps_a[:j]) for j in range(1, len(steps_a) + 1))) / k
    widths = [w, w]
    for a in steps_a:
        widths.append(widths[-1] - a)
    xs = [sum(widths[:i]) for i in range(1, k)]
    for i in range(k - 1, 1, -1):
        plan.append((down(xs[i - 1]), "valley", "tuck-fold" if i == k - 1 else "roll-fold",
                     "tuck" if i == k - 1 else "roll"))
    plan.append((up(xs[0]), "valley", "cover-fold", "cover"))
    finished = (w, H)
elif style == "z-fold":
    xs = [W / 3.0, 2.0 * W / 3.0]
    widths = [W / 3.0] * 3
    plan = [(down(xs[1]), "mountain", "panel-fold", "z-back"),
            (up(xs[0]), "valley", "panel-fold", "z-front")]
    finished = (W / 3.0, H)
elif style == "gatefold":
    a = max(A, CAL)                      # each door stops this short of the centre line
    allow_used = [a]
    c = W / 2.0 + a
    d = c / 2.0 - a
    xs = [d, d + c]
    widths = [d, c, d]
    plan = [(up(d), "valley", "door-fold", "door-left"),
            (down(d + c), "valley", "door-fold", "door-right")]
    finished = (c, H)
    display = 2
elif style == "french":
    xs, ys = [W / 2.0], [H / 2.0]
    widths = [W / 2.0, W / 2.0]
    plan = [(up(W / 2.0), "valley", "half-fold", "half"),
            (east(H / 2.0), "valley", "cross-fold", "cross")]
    finished = (W / 2.0, H / 2.0)
elif style == "double-parallel":
    a = need(2)                          # the folded-in half is two layers thick
    allow_used = [a]
    s_in = (W / 2.0 - a) / 2.0
    xs = [W / 2.0 - s_in, W / 2.0, W / 2.0 + s_in]
    widths = [W / 2.0 - s_in, s_in, s_in, W / 2.0 - s_in]
    plan = [(up(W / 2.0), "valley", "half-fold", "half"),
            (up(W / 2.0 + s_in), "valley", "parallel-fold", "parallel")]
    finished = (W / 2.0 - s_in, H)
elif style == "accordion":
    xs = [W * i / n for i in range(1, n)]
    widths = [W / n] * n
    for i in range(n - 1, 0, -1):
        kind = "valley" if i % 2 == 1 else "mountain"
        plan.append((down(xs[i - 1]), kind, "panel-fold", "acc-v" if kind == "valley"
                     else "acc-m"))
    finished = (W / n, H)
elif style == "cross":
    a = need(2)                          # the tucked end is two layers (the sheet is halved)
    allow_used = [a]
    p = (H + a) / 3.0
    xs, ys = [W / 2.0], [p, 2.0 * p]
    widths = [W / 2.0, W / 2.0]
    plan = [(up(W / 2.0), "valley", "half-fold", "half"),
            (east(2.0 * p), "valley", "cross-fold", "cross-tuck"),
            (west(p), "valley", "cross-fold", "cross-cover")]
    finished = (W / 2.0, p)
else:   # map: an accordion of n panels, then folded across in m (alternating)
    xs = [W * i / n for i in range(1, n)]
    widths = [W / n] * n
    ys = [H * j / m for j in range(1, m)]
    for i in range(n - 1, 0, -1):
        kind = "valley" if i % 2 == 1 else "mountain"
        plan.append((down(xs[i - 1]), kind, "panel-fold", "acc-v" if kind == "valley"
                     else "acc-m"))
    if m == 2:
        plan.append((east(H / 2.0), "valley", "cross-fold", "cross"))
    else:
        plan.append((east(2.0 * H / 3.0), "mountain", "cross-fold", "map-back"))
        plan.append((west(H / 3.0), "valley", "cross-fold", "map-front"))
    finished = (W / n, H / m)

heights = [b - a for a, b in zip([0.0] + ys, ys + [H])]
if min(widths + heights) < MIN_PANEL:
    raise ValueError(f"print-folds: a {style} panel would be {min(widths + heights):.1f} mm, "
                     f"under {MIN_PANEL:g} mm: use a larger sheet or fewer panels")

# ── fold it with the simple-fold model; collect each fold's crease segments ────────────────

state = pliego.simplefold.FoldedState([(0.0, 0.0), (W, 0.0), (W, H), (0.0, H)])
segments = []                         # per fold: [(a, b, "V" | "M"), …] in the sheet frame
for line, kind, _, _ in plan:
    before = len(state.creases)
    state.fold(line, kind)
    segments.append(state.creases[before:])

# finished size and layer count, read off the folded stack
pts = [q for lay in state.layers for q in lay.image()]
fw = max(q.x for q in pts) - min(q.x for q in pts)
fh = max(q.y for q in pts) - min(q.y for q in pts)
if abs(fw - finished[0]) > 1e-6 or abs(fh - finished[1]) > 1e-6:
    raise ValueError(f"print-folds: {style} folded to {fw:.3f}x{fh:.3f} mm, expected "
                     f"{finished[0]:.3f}x{finished[1]:.3f}")
n_panels = len(widths) * len(heights)
if len(state.layers) != n_panels:
    raise ValueError(f"print-folds: {len(state.layers)} layers for {n_panels} panels")

# ── the sheet and its creases ────────────────────────────────────────────────

ROLE = {
    "tuck": (L4("Tuck-in fold (the narrow panel goes inside)",
                "Doblez interior (el panel angosto queda dentro)",
                "Pli rentrant (le volet étroit passe dedans)",
                "Dobra interna (o painel estreito fica dentro)"),
             L4("Fold the narrow end panel in", "Dobla hacia dentro el panel angosto del extremo",
                "Rabattez le volet étroit de l'extrémité",
                "Dobre para dentro o painel estreito da ponta")),
    "roll": (L4("Roll fold", "Doblez enrollado", "Pli roulé", "Dobra enrolada"),
             L4("Roll the folded panels in over the next panel",
                "Enrolla los paneles ya doblados sobre el panel siguiente",
                "Roulez les volets déjà pliés sur le volet suivant",
                "Enrole os painéis já dobrados sobre o painel seguinte")),
    "cover": (L4("Cover fold", "Doblez de la portada", "Pli de couverture", "Dobra da capa"),
              L4("Fold the cover panel over to close it",
                 "Dobla encima el panel de la portada para cerrarlo",
                 "Rabattez le volet de couverture pour le fermer",
                 "Dobre por cima o painel da capa para fechar")),
    "z-back": (L4("Panel fold (mountain)", "Doblez de panel (monte)", "Pli de volet (montagne)",
                  "Dobra de painel (montanha)"),
               L4("Fold the right panel back", "Dobla hacia atrás el panel derecho",
                  "Rabattez le volet droit en arrière", "Dobre para trás o painel direito")),
    "z-front": (L4("Panel fold (valley)", "Doblez de panel (valle)", "Pli de volet (vallée)",
                   "Dobra de painel (vale)"),
                L4("Fold the left panel over the front: a Z",
                   "Dobla el panel izquierdo por delante: queda una Z",
                   "Rabattez le volet gauche par-devant : un Z",
                   "Dobre o painel esquerdo pela frente: fica um Z")),
    "acc-v": (L4("Accordion fold (valley)", "Doblez de acordeón (valle)",
                 "Pli accordéon (vallée)", "Dobra sanfona (vale)"),
              L4("Fold the end forward onto the next panel",
                 "Dobla el extremo hacia delante sobre el panel siguiente",
                 "Rabattez l'extrémité vers l'avant sur le volet suivant",
                 "Dobre a ponta para a frente sobre o painel seguinte")),
    "acc-m": (L4("Accordion fold (mountain)", "Doblez de acordeón (monte)",
                 "Pli accordéon (montagne)", "Dobra sanfona (montanha)"),
              L4("Fold the end back behind the next panel",
                 "Dobla el extremo hacia atrás, detrás del panel siguiente",
                 "Rabattez l'extrémité en arrière, derrière le volet suivant",
                 "Dobre a ponta para trás, atrás do painel seguinte")),
    "door-left": (L4("Gate door fold", "Doblez de puerta", "Pli de volet de fenêtre",
                     "Dobra de porta"),
                  L4("Fold the left door in", "Dobla la puerta izquierda hacia dentro",
                     "Rabattez le volet gauche", "Dobre a porta esquerda para dentro")),
    "door-right": (L4("Gate door fold", "Doblez de puerta", "Pli de volet de fenêtre",
                      "Dobra de porta"),
                   L4("Fold the right door in: the doors stop short of the centre",
                      "Dobla la puerta derecha: las puertas no llegan al centro",
                      "Rabattez le volet droit : les volets s'arrêtent avant le milieu",
                      "Dobre a porta direita: as portas param antes do centro")),
    "half": (L4("Half fold", "Doblez a la mitad", "Pli en deux", "Dobra ao meio"),
             L4("Fold the sheet in half", "Dobla la hoja a la mitad", "Pliez la feuille en deux",
                "Dobre a folha ao meio")),
    "parallel": (L4("Second parallel fold", "Segundo doblez paralelo", "Second pli parallèle",
                    "Segunda dobra paralela"),
                 L4("Fold in half again, parallel, the folded edge inside",
                    "Dobla otra vez a la mitad, en paralelo, con el lomo hacia dentro",
                    "Repliez en deux, parallèlement, le pli à l'intérieur",
                    "Dobre de novo ao meio, em paralelo, com a dobra para dentro")),
    "cross": (L4("Cross fold (through the stacked layers)",
                 "Doblez cruzado (atraviesa las capas)", "Pli croisé (à travers les épaisseurs)",
                 "Dobra cruzada (atravessa as camadas)"),
              L4("Turn it a quarter turn and fold across, through every layer",
                 "Gírala un cuarto de vuelta y dóblala en cruz, a través de todas las capas",
                 "Tournez d'un quart de tour et pliez en travers, à travers toutes les épaisseurs",
                 "Gire um quarto de volta e dobre em cruz, através de todas as camadas")),
    "cross-tuck": (L4("Cross tuck-in fold", "Doblez cruzado interior", "Pli croisé rentrant",
                      "Dobra cruzada interna"),
                   L4("Turn it and fold the narrow end across and in, through both layers",
                      "Gírala y dobla el extremo angosto en cruz hacia dentro, por las dos capas",
                      "Tournez et rabattez en travers l'extrémité étroite, sur les deux épaisseurs",
                      "Gire e dobre a ponta estreita em cruz para dentro, pelas duas camadas")),
    "cross-cover": (L4("Cross cover fold", "Doblez cruzado de portada", "Pli croisé de couverture",
                       "Dobra cruzada da capa"),
                    L4("Fold the other end across over it", "Dobla encima el otro extremo en cruz",
                       "Rabattez l'autre extrémité en travers par-dessus",
                       "Dobre por cima a outra ponta em cruz")),
    "map-back": (L4("Cross fold (mountain)", "Doblez cruzado (monte)", "Pli croisé (montagne)",
                    "Dobra cruzada (montanha)"),
                 L4("Fold the top third across and behind, through every layer",
                    "Dobla en cruz el tercio de arriba hacia atrás, por todas las capas",
                    "Rabattez en travers le tiers du haut derrière, à travers toutes les épaisseurs",
                    "Dobre em cruz o terço de cima para trás, por todas as camadas")),
    "map-front": (L4("Cross fold (valley)", "Doblez cruzado (valle)", "Pli croisé (vallée)",
                     "Dobra cruzada (vale)"),
                  L4("Fold the bottom third across and in front",
                     "Dobla en cruz el tercio de abajo hacia delante",
                     "Rabattez en travers le tiers du bas par-devant",
                     "Dobre em cruz o terço de baixo para a frente")),
}

sheet = pliego.Sheet("leaflet", [(0, 0), (W, 0), (W, H), (0, H)], stock=stock, grain_deg=90.0,
                     label=L4("Printed sheet", "Pliego impreso", "Feuille imprimée",
                              "Folha impressa"))


def r6(p):
    return (round(p.x, 6), round(p.y, 6))


fold_marks = []                    # per fold: [(mark, ±1), …]
for (line, kind, name, role), segs in zip(plan, segments):
    if not segs:
        raise ValueError(f"print-folds: fold {name} made no crease")
    row = []
    for a, b, asg in segs:
        mk = sheet.crease(r6(a), r6(b), "valley" if asg == "V" else "mountain",
                          treatment=TREATMENT, name=name, label=ROLE[role][0])
        row.append((mk, 1.0 if asg == "V" else -1.0))
    fold_marks.append(row)
arr = sheet.build()

# ── the fold program (exact, linear in the angles) and its closure check ────────────────────

pw_txt = " / ".join(fmt(v) for v in widths)
ph_txt = " / ".join(fmt(v) for v in heights)
al_txt = ", ".join(fmt(v) for v in allow_used) if allow_used else "0"
tr = {"score": L4("scored", "hendidos", "rainés", "vincados"),
      "crease": L4("plain creases", "marcados a mano", "marqués à la main", "marcados à mão")}[
    TREATMENT]
NOTE = L4(f"Panels across {pw_txt} mm, down {ph_txt} mm; allowance {al_txt} mm; folds "
          f"{tr['en']}. Finished size {fmt(fw)} × {fmt(fh)} mm.",
          f"Paneles a lo ancho {pw_txt} mm, a lo alto {ph_txt} mm; holgura {al_txt} mm; "
          f"dobleces {tr['es']}. Tamaño terminado {fmt(fw)} × {fmt(fh)} mm.",
          f"Volets en largeur {pw_txt} mm, en hauteur {ph_txt} mm ; jeu {al_txt} mm ; plis "
          f"{tr['fr']}. Format fini {fmt(fw)} × {fmt(fh)} mm.",
          f"Painéis na largura {pw_txt} mm, na altura {ph_txt} mm; folga {al_txt} mm; dobras "
          f"{tr['pt']}. Tamanho final {fmt(fw)} × {fmt(fh)} mm.")

steps = []
angles = {}
worst = 0.0


def pose(row, value):
    for mk, sg in row:
        for e in mk.edges():
            angles[e] = sg * value


for k, row in enumerate(fold_marks):
    role = plan[k][3]
    for j in range(1, SUB + 1):
        th = 180.0 * j / SUB
        pose(row, th)
        worst = max(worst, pliego.kinematics.closure_residual(arr, angles))
        steps.append(pliego.Step(f"fold-{k + 1}-{j}", ROLE[role][1],
                                 [(mk, sg * th) for mk, sg in row], duration_ms=500,
                                 note=NOTE if (k == 0 and j == 1) else None))
OPEN_TEXT = L4(f"Open the last fold to {OPEN:g}° to display it",
               f"Abre el último doblez a {OPEN:g}° para exhibirlo",
               f"Ouvrez le dernier pli à {OPEN:g}° pour le présenter",
               f"Abra a última dobra a {OPEN:g}° para expor")
last = [pair for row in fold_marks[-display:] for pair in row]
for j in range(1, SUB + 1):
    th = 180.0 - OPEN * j / SUB
    pose(last, th)
    worst = max(worst, pliego.kinematics.closure_residual(arr, angles))
    steps.append(pliego.Step(f"open-{j}", OPEN_TEXT, [(mk, sg * th) for mk, sg in last],
                             duration_ms=500))
if worst > 1e-6:
    raise ValueError(f"print-folds: the {style} fold program does not close ({worst:.3g} mm)")
program = pliego.Sequence(steps, mode="kinematic")

print(f"print-folds: style={style} sheet={W:g}x{H:g}mm stock={stock} treatment={TREATMENT} "
      f"panels_x=[{pw_txt}] panels_y=[{ph_txt}] allowance=[{al_txt}] "
      f"finished={fw:.2f}x{fh:.2f}mm layers={len(state.layers)} creases={len(sheet.marks)} "
      f"closure={worst:.1e}mm steps={len(steps)}")

result = pliego.Assembly(
    [sheet],
    controls=[pliego.sequence_control(label=L4("Fold and display", "Doblar y exhibir",
                                               "Plier et présenter", "Dobrar e expor"))],
    sequence=program,
    title="Print folds",
)
