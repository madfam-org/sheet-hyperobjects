"""Paper circuit card — sheet-hyperobjects cartridge (Pliego).

A card that lights an LED from a coin cell through copper tape (or conductive ink), with a fold
switch: a tab at the card's edge carries one contact; folding the tab over presses it onto the
other contact and closes the circuit. Mode `card` is a flat card; mode `popup` is a folded card
whose spread holds a box pop-up (one parallel fold, cut and scored in the same sheet) with the LED
on its riser.

The conductors are `pliego.press.trace` finishes (spec §5.30): each exports on its own layers
(outline, centre line, contact pads) for a cutter or plotter. Before building, the script checks
the circuit with `pliego.press.circuit` (rule 30): open with the switch up, closed with the
switch folded, the LED forward-biased; and the switch geometry with
`pliego.press.fold_switch_closes`: the tab folded flat brings its contact onto the other one.
The switch's steps carry that report in their notes.

Kinematics (Tier R, exact). Every pop-up fold is parallel to the gutter, so the card moves in
its cross-section: the box is a parallelogram four-bar (foot fold at `tread` from the gutter on
the left page, head fold at `riser` on the right page, nose fold between), and every fold turns
by the gutter angle. The tab's fold is a branch of its own. The fold program is
`Sequence.kinematic_path` (exact rigid substeps). Every line is computed here; the layout is an
original design.
"""

import pliego


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


def L4(en, es, fr, pt):
    return {"en": en, "es": es, "fr": fr, "pt": pt}


run = PARAM(lambda: mode, "card")  # noqa: F821
material = PARAM(lambda: material, "copper-tape")  # noqa: F821
width = pliego.clamp(float(PARAM(lambda: width, 5.0)), 2.0, 6.0)  # noqa: F821
stock = PARAM(lambda: stock, "cardstock-250")  # noqa: F821
angle = pliego.clamp(float(PARAM(lambda: angle, 90.0)), 60.0, 150.0)  # noqa: F821
if run not in ("card", "popup"):
    raise ValueError(f"unknown mode {run!r}")
if material not in ("copper-tape", "conductive-ink"):
    raise ValueError(f"unknown material {material!r}")

W, H = 105.0, 148.0                 # one page (A6 portrait); the pop-up spread is 2W × H
TAB_W, TAB_Y = 35.0, (15.0, 50.0)   # the switch tab on the left page's fore-edge (u = 0)
TREAD, RISER = 30.0, 40.0           # the box: foot fold at W − TREAD, head fold at W + RISER
STRIP = (49.0, 99.0)                # the box's width across the gutter (between the two slits)
CELL, PAD, LEG = 20.0, 10.0, 6.0    # coin-cell pad (a 20 mm cell), switch pads, LED pads (mm)

# ── the circuit (an original layout): cell → LED → switch → cell ─────────────
tr = pliego.press


def traces():
    return [
        tr.trace("plus", "card", [(65.0, 115.0), (65.0, 86.0), (100.0, 86.0)], width,
                 material=material, pads=[
                     tr.pad("cell-plus", (65.0, 115.0), PAD, part="cell", pin="plus"),
                     tr.pad("led-anode", (100.0, 86.0), LEG, part="led", pin="anode")]),
        tr.trace("return", "card", [(100.0, 62.0), (40.0, 62.0), (40.0, 30.0), (20.0, 30.0)],
                 width, material=material, pads=[
                     tr.pad("led-cathode", (100.0, 62.0), LEG, part="led", pin="cathode"),
                     tr.pad("switch-a", (20.0, 30.0), PAD, part="switch", pin="contact")]),
        tr.trace("tab", "card", [(-20.0, 30.0), (-20.0, 42.0), (6.0, 42.0), (6.0, 115.0),
                                 (30.0, 115.0)], width, material=material, pads=[
                     tr.pad("switch-b", (-20.0, 30.0), PAD, part="switch", pin="contact"),
                     tr.pad("cell-minus", (40.0, 115.0), CELL, part="cell", pin="minus")]),
    ]


TRACES = traces()
TAB_LINE = ((0.0, TAB_Y[0]), (0.0, TAB_Y[1]))
problems = tr.fold_switch_closes(TRACES, "switch", TAB_LINE, "valley")
if problems:
    raise ValueError("fold switch: " + "; ".join(problems))
OFF, ON = tr.circuit(TRACES), tr.circuit(TRACES, closed=["switch"])
errors = [i["detail"] for r in (OFF, ON) for i in r["issues"] if i["level"] == "error"]
if errors or OFF["closed"] or not ON["closed"] or ON["lit"] != ["led"]:
    raise ValueError(f"circuit: open={OFF['closed']} closed={ON['closed']} lit={ON['lit']} "
                     f"{errors}")

# ── the sheet: the page (and the pop-up's right page), with the switch tab ───
right = 2.0 * W if run == "popup" else W
outline = [(0.0, 0.0), (right, 0.0), (right, H), (0.0, H), (0.0, TAB_Y[1]),
           (-TAB_W, TAB_Y[1]), (-TAB_W, TAB_Y[0]), (0.0, TAB_Y[0])]
sheet = pliego.Sheet("card", outline, stock=stock, grain_deg=90.0,
                     label=L4("Circuit card", "Tarjeta de circuito", "Carte à circuit",
                              "Cartão de circuito"))
tab = sheet.valley(TAB_LINE[0], TAB_LINE[1], treatment="score", name="switch-fold", label=L4(
    "Fold switch", "Interruptor de pliegue", "Interrupteur à pli", "Interruptor de dobra"))
sheet.label_edge("switch-tab", (-TAB_W, TAB_Y[0]), (-TAB_W, TAB_Y[1]))

pop = []                             # (mark, sign): every pop-up fold turns by ±γ
if run == "popup":
    xa, xf, xb = W - TREAD, W - TREAD + RISER, W + RISER
    y0, y1 = STRIP
    for y in (y0, y1):
        sheet.cut([(xa, y), (xb, y)], name="box-slit")
    gl = L4("Gutter (the card's spine)", "Pliegue central (lomo de la tarjeta)",
            "Pliure centrale (dos de la carte)", "Dobra central (lombada do cartão)")
    for ya, yb in ((0.0, y0), (y1, H)):
        pop.append((sheet.valley((W, ya), (W, yb), treatment="score", name="gutter", label=gl), 1))
    pop.append((sheet.valley((xa, y0), (xa, y1), treatment="score", name="box-foot", label=L4(
        "Box: foot fold", "Caja: pliegue de base", "Boîte : pli de pied", "Caixa: dobra da base")),
        1))
    pop.append((sheet.valley((xb, y0), (xb, y1), treatment="score", name="box-head", label=L4(
        "Box: head fold", "Caja: pliegue superior", "Boîte : pli de tête", "Caixa: dobra do topo")),
        1))
    pop.append((sheet.mountain((xf, y0), (xf, y1), treatment="score", name="box-nose", label=L4(
        "Box: front edge", "Caja: arista delantera", "Boîte : arête avant",
        "Caixa: aresta da frente")), -1))
    for t in TRACES:                 # the traces must not cross the slits
        for (ax, ay), (bx, by) in zip(t["path"], t["path"][1:], strict=False):
            for y in (y0, y1):
                if min(ay, by) < y < max(ay, by) and xa <= ax <= xb:
                    raise ValueError(f"trace '{t['id']}' crosses a slit of the box")

cut = pliego.papercut.analyze(sheet, min_feature_mm=width)
if any(i["level"] == "error" for i in cut.issues):
    raise ValueError("papercut: " + "; ".join(i["detail"] for i in cut.issues))


def note(r, on):
    loop = " → ".join(["cell +"] + [f"LED '{p}'" for p in r["loop"]] + ["switch", "cell −"])
    if on:
        return L4(f"Circuit closed ({loop}): the LED lights. Checked by pliego.press.circuit.",
                  f"Circuito cerrado ({loop}): el LED se enciende. Comprobado con "
                  "pliego.press.circuit.",
                  f"Circuit fermé ({loop}) : la LED s'allume. Vérifié par pliego.press.circuit.",
                  f"Circuito fechado ({loop}): o LED acende. Verificado por "
                  "pliego.press.circuit.")
    return L4("Circuit open: the switch is up and the LED is off.",
              "Circuito abierto: el interruptor está levantado y el LED, apagado.",
              "Circuit ouvert : l'interrupteur est relevé et la LED éteinte.",
              "Circuito aberto: o interruptor está levantado e o LED apagado.")


steps = []
if run == "popup":
    gamma = 180.0 - angle
    steps += [
        pliego.Step("close", L4("Fold the card shut: the box folds inside",
                                "Cierra la tarjeta: la caja se pliega dentro",
                                "Fermez la carte : la boîte se replie à l'intérieur",
                                "Feche o cartão: a caixa dobra-se para dentro"),
                    [(m, s * 180.0) for m, s in pop], duration_ms=2600),
        pliego.Step("open", L4(f"Open the card to {angle:g}°: the box stands up with the LED",
                               f"Abre la tarjeta a {angle:g}°: la caja se levanta con el LED",
                               f"Ouvrez la carte à {angle:g}° : la boîte se dresse avec la LED",
                               f"Abra o cartão a {angle:g}°: a caixa ergue-se com o LED"),
                    [(m, s * gamma) for m, s in pop], duration_ms=2200),
    ]
steps += [
    pliego.Step("switch-on", L4("Fold the switch tab over: the contacts meet",
                                "Dobla la pestaña del interruptor: los contactos se tocan",
                                "Rabattez la languette de l'interrupteur : les contacts se "
                                "touchent", "Dobre a aba do interruptor: os contactos tocam-se"),
                [(tab, 180.0)], duration_ms=1400, note=note(ON, True)),
    pliego.Step("switch-off", L4("Lift the tab: the circuit opens",
                                 "Levanta la pestaña: el circuito se abre",
                                 "Relevez la languette : le circuit s'ouvre",
                                 "Levante a aba: o circuito abre-se"),
                [(tab, 0.0)], duration_ms=1200, note=note(OFF, False)),
    pliego.Step("switch-on-again", L4("Fold it over again: the LED lights",
                                      "Vuelve a doblarla: el LED se enciende",
                                      "Rabattez-la à nouveau : la LED s'allume",
                                      "Dobre-a outra vez: o LED acende"),
                [(tab, 180.0)], duration_ms=1400, note=note(ON, True)),
]
program = pliego.Sequence.kinematic_path(sheet, steps, substeps=6)
print(f"circuit: material={material} width_mm={width:g} nets_open={OFF['nets']} "
      f"nets_closed={ON['nets']} open=off closed=on lit={','.join(ON['lit'])} "
      f"switch_fold=ok papercut_issues={len(cut.issues)}")
print(f"kinematics: mode={run} steps={len(program.steps)} "
      f"max_residual_rad={program.report.get('max_residual_rad', 0.0):.3e}")

result = pliego.Assembly(
    [sheet],
    controls=[pliego.sequence_control("switch", label=L4(
        "Fold switch (and the card)", "Interruptor de pliegue (y la tarjeta)",
        "Interrupteur à pli (et la carte)", "Interruptor de dobra (e o cartão)"))],
    sequence=program, finishes=TRACES, title="Paper circuit card")
