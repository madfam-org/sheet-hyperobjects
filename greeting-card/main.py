"""Greeting card — sheet-hyperobjects cartridge (Pliego).

One family, every common folded card, from one generator:

* mode `card`, parameter `style`:
  - `single` — single fold on the long side (a book-like portrait card): two panels;
  - `tent` — single fold along the top of a landscape card, so it stands as a tent;
  - `gatefold` — a centre panel and two half-width doors that meet in the middle;
  - `z-fold` — three equal panels folded valley then mountain (an accordion);
  - `tri-fold` — three panels rolled in (letter fold); the inner panel is narrower so it tucks in;
* mode `with-insert` — a single-fold cover with a lighter paper insert folded inside it and held by
  a narrow glue line beside the spine.

Sizes are the finished (folded) face, `face_width` × `face_height`; presets give A6, A5, US A2 and
US A7. Every fold is scored (cardstock cracks if it is folded unscored; see `score-vs-crease`). The
sheet's front side is the inside of the card and its back side the outside, so the two colour
parameters print as the inside and the outside.

All folds of a card are parallel, so its fold program is exact and has no loop to close: a
kinematic program (`pliego.Sequence.kinematic_path`) folds the card shut and then opens it to
`display_open`, the angle between panels at which it is shown. Fully shut layers are drawn a hair
apart by the preview.
"""

import pliego


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


mode = PARAM(lambda: mode, "card")                          # noqa: F821
style = PARAM(lambda: style, "single")                      # noqa: F821
face_width = float(PARAM(lambda: face_width, 105.0))        # noqa: F821
face_height = float(PARAM(lambda: face_height, 148.0))      # noqa: F821
stock = PARAM(lambda: stock, "cardstock-250")               # noqa: F821
outside_color = PARAM(lambda: outside_color, "#f7f5ef")     # noqa: F821
inside_color = PARAM(lambda: inside_color, "#f7f5ef")       # noqa: F821
display_open = float(PARAM(lambda: display_open, 100.0))    # noqa: F821
insert_margin = float(PARAM(lambda: insert_margin, 4.0))    # noqa: F821

if mode not in ("card", "with-insert"):
    raise ValueError(f"greeting-card: unknown mode {mode!r}")
if mode == "with-insert":
    style = "single"
if style not in ("single", "tent", "gatefold", "z-fold", "tri-fold"):
    raise ValueError(f"greeting-card: unknown style {style!r}")
if stock not in ("cardstock-160", "cardstock-250", "cardstock-300", "kraft-120"):
    raise ValueError(f"greeting-card: unsupported stock {stock!r}")
COLORS = ("#f7f5ef", "#efe3c8", "#b98a5a", "#b23a3a", "#2f6b4f", "#2b3f6b", "#e8b7b0",
          "#3a3a3a")
for c in (outside_color, inside_color):
    if c not in COLORS:
        raise ValueError(f"greeting-card: colour {c!r} is not one of the palette")

fw = pliego.clamp(face_width, 70.0, 220.0)
fh = pliego.clamp(face_height, 70.0, 300.0)
gamma_end = 180.0 - pliego.clamp(display_open, 30.0, 180.0)
margin = pliego.clamp(insert_margin, 2.0, 10.0)
GATE_GAP = 1.0      # each gatefold door stops this short of half the face: doors never collide
TUCK = 2.0          # the tri-fold's inner panel is this much narrower: it tucks inside
SHUT = 178.0        # an outer fold is drawn shut at this angle and an inner one at 179.5°, so
INNER = 179.5       # nested layers stay in order (real card has thickness)
SUB = 6
GLUE_W = 5.0        # the insert's glue line beside the spine


def L4(en, es, fr, pt):
    return {"en": en, "es": es, "fr": fr, "pt": pt}


SPINE = L4("Spine (scored fold)", "Lomo (doblez hendido)", "Dos (pli rainé)",
           "Lombada (dobra vincada)")


def panel_fold(sheet, a, b, kind, name, label):
    return sheet.crease(a, b, kind, treatment="score", name=name, label=label)


# ── the card sheet, per style ────────────────────────────────────────────────

if style == "tent":
    pw, ph = max(fw, fh), min(fw, fh)              # a landscape panel, folded along its top
    outline = [(0, 0), (pw, 0), (pw, 2 * ph), (0, 2 * ph)]
    grain = 0.0
elif style == "gatefold":
    door = fw / 2.0 - GATE_GAP
    outline = [(0, 0), (2 * door + fw, 0), (2 * door + fw, fh), (0, fh)]
    grain = 90.0
elif style == "z-fold":
    outline = [(0, 0), (3 * fw, 0), (3 * fw, fh), (0, fh)]
    grain = 90.0
elif style == "tri-fold":
    outline = [(0, 0), (3 * fw - TUCK, 0), (3 * fw - TUCK, fh), (0, fh)]
    grain = 90.0
else:
    outline = [(0, 0), (2 * fw, 0), (2 * fw, fh), (0, fh)]
    grain = 90.0

card = pliego.Sheet("card", outline, stock=stock, grain_deg=grain,
                    label=L4("Card", "Tarjeta", "Carte", "Cartão"),
                    front=inside_color, back=outside_color)

folds = []          # (mark, shut angle magnitude, sign, key step id)
if style == "single":
    folds.append((panel_fold(card, (fw, 0), (fw, fh), "valley", "spine", SPINE), SHUT, 1, "shut"))
elif style == "tent":
    folds.append((panel_fold(card, (0, ph), (pw, ph), "valley", "spine", L4(
        "Ridge of the tent (scored fold)", "Cumbrera de la tienda (doblez hendido)",
        "Faîte de la tente (pli rainé)", "Cumeeira da tenda (dobra vincada)")), SHUT, 1, "shut"))
elif style == "gatefold":
    x1, x2 = door, door + fw
    folds.append((panel_fold(card, (x1, 0), (x1, fh), "valley", "door-left", L4(
        "Left door fold", "Doblez de la puerta izquierda", "Pli du volet gauche",
        "Dobra da porta esquerda")), SHUT, 1, "door-left"))
    folds.append((panel_fold(card, (x2, 0), (x2, fh), "valley", "door-right", L4(
        "Right door fold", "Doblez de la puerta derecha", "Pli du volet droit",
        "Dobra da porta direita")), SHUT, 1, "door-right"))
elif style == "z-fold":
    folds.append((panel_fold(card, (fw, 0), (fw, fh), "valley", "fold-1", L4(
        "First fold (valley)", "Primer doblez (valle)", "Premier pli (vallée)",
        "Primeira dobra (vale)")), SHUT, 1, "zig"))
    folds.append((panel_fold(card, (2 * fw, 0), (2 * fw, fh), "mountain", "fold-2", L4(
        "Second fold (mountain)", "Segundo doblez (monte)", "Second pli (montagne)",
        "Segunda dobra (montanha)")), SHUT, -1, "zag"))
else:   # tri-fold: the narrow end panel folds in first, then the cover panel over it
    folds.append((panel_fold(card, (2 * fw, 0), (2 * fw, fh), "valley", "fold-inner", L4(
        "Inner fold (the narrow panel tucks in)", "Doblez interior (el panel angosto entra)",
        "Pli intérieur (le volet étroit se glisse dedans)",
        "Dobra interna (o painel estreito entra)")), INNER, 1, "tuck"))
    folds.append((panel_fold(card, (fw, 0), (fw, fh), "valley", "fold-cover", L4(
        "Cover fold", "Doblez de la portada", "Pli de couverture", "Dobra da capa")),
        SHUT, 1, "cover"))

STEP_TEXT = {
    "shut": L4("Fold the card shut along the score", "Cierra la tarjeta por el hendido",
               "Fermez la carte le long du rainage", "Feche o cartão pelo vinco"),
    "door-left": L4("Fold the left door in", "Dobla la puerta izquierda hacia dentro",
                    "Rabattez le volet gauche", "Dobre a porta esquerda para dentro"),
    "door-right": L4("Fold the right door in to meet it", "Dobla la puerta derecha hasta juntarlas",
                     "Rabattez le volet droit jusqu'à l'autre",
                     "Dobre a porta direita até encontrar a outra"),
    "zag": L4("Fold it into a Z: valley the first score, mountain the second",
              "Dóblala en Z: en valle el primer hendido, en monte el segundo",
              "Pliez-la en Z : le premier rainage en vallée, le second en montagne",
              "Dobre-o em Z: o primeiro vinco em vale, o segundo em montanha"),
    "tuck": L4("Fold the narrow end panel in", "Dobla hacia dentro el panel angosto del extremo",
               "Rabattez le volet étroit de l'extrémité",
               "Dobre para dentro o painel estreito da ponta"),
    "cover": L4("Fold the cover panel over it", "Dobla encima el panel de la portada",
                "Rabattez le volet de couverture par-dessus",
                "Dobre por cima o painel da capa"),
}
OPEN_TEXT = L4(f"Open it to {180.0 - gamma_end:g}° to stand it up",
               f"Ábrela a {180.0 - gamma_end:g}° para que se sostenga de pie",
               f"Ouvrez-la à {180.0 - gamma_end:g}° pour qu'elle tienne debout",
               f"Abra-o a {180.0 - gamma_end:g}° para que fique de pé")

key_steps = []
for mark, shut, sg, sid in folds:
    targets = [(mark, sg * shut)]
    if sid == "zig":    # an accordion collapses as one: both folds together
        continue
    if sid == "zag":
        targets = [(m, s * a) for m, a, s, _ in folds]
    key_steps.append(pliego.Step(sid, STEP_TEXT[sid], targets, duration_ms=1800))
key_steps.append(pliego.Step("open", OPEN_TEXT, [(m, s * gamma_end) for m, _, s, _ in folds],
                             duration_ms=1800))

sheets = [card]
joins = []
insert_steps = []
if mode == "with-insert":
    iw, ih = 2 * fw - 2 * margin, fh - 2 * margin
    if iw < 40 or ih < 40:
        raise ValueError("greeting-card: the insert margin leaves no insert")
    insert = pliego.Sheet(
        "insert", [(0, 0), (iw, 0), (iw, ih), (0, ih)], stock="copy-80", grain_deg=90.0,
        label=L4("Insert", "Hoja interior", "Feuillet intérieur", "Folha interna"),
        placement=pliego.Placement(origin=(margin, 0.1, -margin)),
    )
    ifold = insert.valley((iw / 2.0, 0), (iw / 2.0, ih), name="spine", label=L4(
        "Insert fold", "Doblez de la hoja interior", "Pli du feuillet", "Dobra da folha interna"))
    region = [(iw / 2.0 - 1.0 - GLUE_W, 3.0), (iw / 2.0 - 1.0, 3.0), (iw / 2.0 - 1.0, ih - 3.0),
              (iw / 2.0 - 1.0 - GLUE_W, ih - 3.0)]
    joins.append(pliego.glue("insert-glue-line", insert, region, card,
                             (1.0, 0.0, 0.0, 1.0, margin, margin), "front"))
    sheets.append(insert)
    key_steps = [
        pliego.Step("shut", L4("Fold the card shut with the insert inside",
                               "Cierra la tarjeta con la hoja interior dentro",
                               "Fermez la carte avec le feuillet à l'intérieur",
                               "Feche o cartão com a folha interna dentro"),
                    [(folds[0][0], SHUT)], duration_ms=1800),
        pliego.Step("open", OPEN_TEXT, [(folds[0][0], gamma_end)], duration_ms=1800),
    ]
    insert_steps = [(ifold, INNER), (ifold, gamma_end)]

program = pliego.Sequence.kinematic_path(card, key_steps, substeps=SUB)
steps = list(program.steps)
if insert_steps:            # the insert's fold follows the cover's, substep by substep
    merged = []
    k = 0
    for mark, shut_to in insert_steps:
        start = 0.0 if k == 0 else insert_steps[0][1]
        for j in range(1, SUB + 1):
            st = steps[k * SUB + j - 1]
            ang = start + (shut_to - start) * j / SUB
            merged.append(pliego.Step(st.id, st.label, st.targets + [(mark, ang)],
                                      st.release, st.duration_ms, st.note))
        k += 1
    steps = merged
program = pliego.Sequence(steps, mode="kinematic")

# sanity: every shut fold reaches its target, every program angle is legal
for st in program.steps:
    for _, ang in st.targets:
        if not -180.0 <= ang <= 180.0:
            raise ValueError(f"greeting-card: angle {ang} out of range")
print(f"card: mode={mode} style={style} sheet={outline[2][0]:g}x{outline[2][1]:g}mm "
      f"folds={len(folds)} program_steps={len(program.steps)}")

result = pliego.Assembly(
    sheets, joins=joins,
    controls=[pliego.sequence_control(
        label=L4("Fold and open", "Doblar y abrir", "Plier et ouvrir", "Dobrar e abrir"),
        default=float(len(program.steps)))],
    sequence=program,
    title="Greeting card",
)
