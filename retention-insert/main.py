"""An open media pocket from the content envelope, clearance and board caliper.

Original MADFAM geometry; the rolled locking ends adapt sleeve-and-tray's construction.
No game artwork, commercial die line or measured box is reproduced. The kinematic program
shows erection; friction, lock strength and shock retention require a physical specimen.
"""
import pliego


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


def L4(en, es, fr, pt):
    return {"en": en, "es": es, "fr": fr, "pt": pt}


pocket_w = float(PARAM(lambda: pocket_w, 85.0))
pocket_h = float(PARAM(lambda: pocket_h, 100.0))
pocket_d = float(PARAM(lambda: pocket_d, 25.0))
clearance = float(PARAM(lambda: clearance, 1.0))
wall_folds = bool(PARAM(lambda: wall_folds, True))
lock_tabs = bool(PARAM(lambda: lock_tabs, True))
stock = str(PARAM(lambda: stock, "folding-boxboard-300"))
STOCKS = ("folding-boxboard-300", "sbs-board-350", "cardstock-300")
if stock not in STOCKS:
    raise ValueError(f"retention-insert: stock must be one of {STOCKS}")
if not (30 <= pocket_w <= 240 and 30 <= pocket_h <= 300 and 3 <= pocket_d <= 80):
    raise ValueError("retention-insert: content envelope is outside the supported range")
if not 0.5 <= clearance <= 5:
    raise ValueError("retention-insert: clearance must be 0.5 to 5 mm per side")

# The family owns allowances; reference presets supply only the content envelope.
width = pocket_w + 2.0 * clearance
length = pocket_h + 2.0 * clearance
depth = pocket_d + clearance
t = pliego.board.caliper(stock)
Wp, Lp, Dp = width + t, length + t, depth + t
inset = max(2.0 * t, 1.5)
tab = 1.5 * t if lock_tabs else 0.0
inner = Dp - t
ANGLE = -90.0 if wall_folds else 0.0
ROLL = -180.0 if wall_folds else 0.0


def notched(x0, y0, x1, y1, edge, spans, dep):
    pts = [(x0, y0)]
    if edge == "bottom":
        for a, b in sorted(spans):
            pts += [(a, y0), (a, y0 + dep), (b, y0 + dep), (b, y0)]
    pts += [(x1, y0), (x1, y1)]
    if edge == "top":
        for a, b in sorted(spans, reverse=True):
            pts += [(b, y1), (b, y1 - dep), (a, y1 - dep), (a, y1)]
    return pts + [(x0, y1)]


LABEL = {
    "base": L4("Pocket floor", "Fondo del alojamiento", "Fond du logement", "Fundo do encaixe"),
    "side": L4("Side wall", "Pared lateral", "Paroi latérale", "Parede lateral"),
    "ear": L4("Ear", "Oreja", "Oreille", "Orelha"),
    "end": L4("End wall", "Cabecera", "Paroi d'extrémité", "Cabeceira"),
    "inner": L4("Rolled locking leaf", "Hoja de cierre enrollada", "Feuillet de verrouillage",
                "Aba interna de trava"),
}


def numbered(key, n):
    return {lang: f"{value} {n}" for lang, value in LABEL[key].items()}


x0, y0 = Dp, (2 * Dp - t + tab if lock_tabs else Dp)
x1, y1 = x0 + Wp, y0 + Lp
q = Wp / 4.0
spans = [(x0 + q - q / 4.0, x0 + q + q / 4.0),
         (x0 + 3 * q - q / 4.0, x0 + 3 * q + q / 4.0)] if lock_tabs else []
slots = [(a - 0.5, b + 0.5) for a, b in spans]
tray = pliego.dieline.Dieline(
    "insert", "retention pocket", "folding-carton",
    {"length": length, "width": width, "depth": depth}, stock, t,
    label=L4("Retention insert blank", "Suaje del inserto de retención",
             "Flan de l'insert de maintien", "Corte do inserto de retenção"), grain_deg=90.0)
base = [(x0, y0)]
for a, b in sorted(slots):
    base += [(a, y0), (a, y0 + t), (b, y0 + t), (b, y0)]
base += [(x1, y0), (x1, y1)]
for a, b in sorted(slots, reverse=True):
    base += [(b, y1), (b, y1 - t), (a, y1 - t), (a, y1)]
base.append((x0, y1))
tray.panel("base", base, "pocket", LABEL["base"])
walls, ears, ends, rolls = [], [], [], []
ear_w = Wp / 2.0 - t
for k, (xa, xb) in ((1, (x0 - Dp, x0)), (2, (x1, x1 + Dp))):
    tray.rect(f"side-{k}", xa, y0, xb, y1, "panel", numbered("side", k))
    name = f"side-{k}-fold"
    tray.hinge("base", f"side-{k}", ANGLE, name=name)
    walls.append(name)
    free, hing = (xa, xb) if k == 1 else (xb, xa)
    sgn = 1.0 if k == 1 else -1.0
    for j, (ye, direction) in enumerate(((y0, -1.0), (y1, 1.0)), 1):
        name = f"side-{k}-ear-{j}"
        e0, e1 = free + sgn * inset, hing - sgn * inset / 2.0
        chamfer = min(0.3 * ear_w, 0.4 * Dp)
        tray.panel(name, [(e0, ye), (e1, ye), (e1, ye + direction * ear_w),
                          (e0 + sgn * chamfer, ye + direction * ear_w)],
                   "dust-flap", numbered("ear", 2 * (k - 1) + j))
        tray.hinge(f"side-{k}", name, ANGLE, name=f"{name}-fold")
        ears.append(f"{name}-fold")
for k, (ya, direction) in ((1, (y0, -1.0)), (2, (y1, 1.0))):
    yb = ya + direction * Dp
    lo, hi = sorted((ya, yb))
    name = f"end-{k}"
    tray.panel(name, notched(x0, lo, x1, hi, "top" if k == 1 else "bottom", slots, t),
               "panel", numbered("end", k))
    tray.hinge("base", name, ANGLE, name=f"{name}-fold")
    ends.append(f"{name}-fold")
    if lock_tabs:
        yc = yb + direction * inner
        leaf = [(x0 + t, yb), (x1 - t, yb), (x1 - t, yc)]
        for a, b in sorted(spans, reverse=True):
            leaf += [(b, yc), (b - 0.5, yc + direction * tab),
                     (a + 0.5, yc + direction * tab), (a, yc)]
        leaf.append((x0 + t, yc))
        tray.panel(f"{name}-inner", leaf, "lock", numbered("inner", k))
        tray.hinge(name, f"{name}-inner", ROLL, name=f"roll-{k}-fold")
        rolls.append(f"roll-{k}-fold")
tray.dimension((x0, y0), (x1, y0), f"W {width:g} inside", -6.0)
tray.dimension((x0 - Dp, y0), (x0 - Dp, y1), f"H {length:g} inside", 8.0)
for name, label, hinges in [
    ("walls-up", L4("Raise the side walls", "Levanta las paredes laterales",
                    "Relevez les parois latérales", "Levante as paredes laterais"), walls),
    ("ears-in", L4("Fold the corner ears in", "Dobla las orejas hacia dentro",
                   "Rabattez les oreilles", "Dobre as orelhas para dentro"), ears),
    ("ends-up", L4("Raise the end walls", "Levanta las cabeceras",
                   "Relevez les extrémités", "Levante as cabeceiras"), ends),
]:
    tray.step(name, label, hinges, 1000)
if rolls:
    tray.step("lock-ends", L4("Roll the ends and engage the tabs", "Enrolla las cabeceras y encaja las pestañas",
                              "Roulez les extrémités et engagez les pattes",
                              "Enrole as cabeceiras e encaixe as abas"), rolls, 1400)
pack = tray.build(rest_on="base")
result = pliego.dieline.assemble(
    [pack], title="Retention insert",
    label=L4("Erect the insert", "Arma el inserto", "Monter l'insert", "Monte o inserto"),
    meta={"cartridge": "retention-insert", "params": {
        "pocket_w": pocket_w, "pocket_h": pocket_h, "pocket_d": pocket_d,
        "clearance": clearance, "stock": stock, "wall_folds": wall_folds,
        "lock_tabs": lock_tabs}})
print(f"retention-insert: content={pocket_w:g}x{pocket_h:g}x{pocket_d:g}mm "
      f"inside={width:g}x{length:g}x{depth:g}mm caliper={t:g}mm "
      f"walls={wall_folds} lock-tabs={lock_tabs}")
