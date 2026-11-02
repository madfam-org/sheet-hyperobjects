"""Blank paper inserts: a case wrap, two-spine tray inlay, or front panel.

Original parameter geometry. Dimensions are inside the selected case's paper channel, not
outside case dimensions. No game artwork, scan or unmeasured product trim is reproduced.
"""
import pliego


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


def L4(en, es, fr, pt):
    return {"en": en, "es": es, "fr": fr, "pt": pt}


style = str(PARAM(lambda: style, "wrap"))
panel_w = float(PARAM(lambda: panel_w, 120.0))
panel_h = float(PARAM(lambda: panel_h, 180.0))
spine_w = float(PARAM(lambda: spine_w, 15.0))
bleed = float(PARAM(lambda: bleed, 3.0))
flap = float(PARAM(lambda: flap, 0.0))
fold_angle = float(PARAM(lambda: fold_angle, 90.0))
stock = str(PARAM(lambda: stock, "copy-80"))
if style not in ("wrap", "tray-inlay", "front"):
    raise ValueError("case-insert: style must be wrap, tray-inlay or front")
if stock not in ("copy-80", "elephant-hide-110", "cardstock-160"):
    raise ValueError("case-insert: unsupported stock")
if not (50 <= panel_w <= 250 and 50 <= panel_h <= 300 and 2 <= spine_w <= 40):
    raise ValueError("case-insert: panel or spine is outside the supported range")
if not (0 <= bleed <= 6 and 0 <= flap <= 30 and 0 <= fold_angle <= 90):
    raise ValueError("case-insert: bleed, flap or fold angle is outside the supported range")
t = pliego.stock.snapshot(stock)["caliper_mm"]
treatment = "score" if t >= 0.2 else "crease"
blank = pliego.dieline.Dieline(
    "insert", f"case {style}", "folding-carton",
    {"length": panel_h, "width": panel_w, "depth": spine_w if style != "front" else t},
    stock, t, bleed=bleed, safe=3,
    label=L4("Paper insert", "Inserto de papel", "Insert en papier", "Inserto de papel"))
blank.rect("panel", 0, 0, panel_w, panel_h, "panel",
           L4("Panel", "Panel", "Panneau", "Painel"))
folds = []
if style == "wrap":
    blank.rect("spine", panel_w, 0, panel_w + spine_w, panel_h, "panel",
               L4("Spine", "Lomo", "Dos", "Lombada"))
    blank.rect("back", panel_w + spine_w, 0, 2 * panel_w + spine_w, panel_h, "panel",
               L4("Back panel", "Panel trasero", "Panneau arrière", "Painel traseiro"))
    for a, b in (("panel", "spine"), ("spine", "back")):
        name = f"{a}-{b}-fold"
        blank.hinge(a, b, -fold_angle, name=name, treatment=treatment)
        folds.append(name)
    last, edge = "back", 2 * panel_w + spine_w
elif style == "tray-inlay":
    for name, xa, xb in (("left-spine", -spine_w, 0),
                         ("right-spine", panel_w, panel_w + spine_w)):
        blank.rect(name, xa, 0, xb, panel_h, "flap",
                   L4("Spine strip", "Tira de lomo", "Bande de dos", "Tira da lombada"))
        blank.hinge("panel", name, -fold_angle, name=name + "-fold", treatment=treatment)
        folds.append(name + "-fold")
    last, edge = "right-spine", panel_w + spine_w
else:
    last, edge = "panel", panel_w
if flap > 0:
    blank.rect("flap", edge, 0, edge + flap, panel_h, "flap",
               L4("Extra flap", "Solapa adicional", "Rabat supplémentaire", "Aba adicional"))
    blank.hinge(last, "flap", -fold_angle, name="flap-fold", treatment=treatment)
    folds.append("flap-fold")
blank.dimension((0, 0), (panel_w, 0), f"W {panel_w:g}", -7)
blank.dimension((0, 0), (0, panel_h), f"H {panel_h:g}", 7)
if folds:
    blank.step("wrap-insert", L4("Fold the blank insert", "Dobla el inserto sin arte",
                                  "Pliez l'insert vierge", "Dobre o inserto sem arte"), folds)
pack = blank.build(rest_on="panel")
metadata = {"cartridge": "case-insert", "params": {
    "style": style, "panel_w": panel_w, "panel_h": panel_h, "spine_w": spine_w,
    "bleed": bleed, "flap": flap, "fold_angle": fold_angle, "stock": stock}}
result = pliego.dieline.assemble(
    [pack], title="Case insert",
    label=L4("Wrap the insert", "Doblar el inserto", "Plier l'insert", "Dobrar o inserto"),
    meta=metadata) if folds else pliego.Assembly(
        [pack.sheet], dielines=[pack.block], title="Case insert", meta=metadata)
print(f"case-insert: style={style} panel={panel_w:g}x{panel_h:g}mm spine={spine_w:g}mm "
      f"flap={flap:g}mm bleed={bleed:g}mm folds={len(folds)}")
