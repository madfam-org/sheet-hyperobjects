"""Sleeve and tray — sheet-hyperobjects cartridge (Pliego).

The matchbox-style pack: an open tray that slides in and out of a glued sleeve, both cut from
paperboard and generated from the tray's inside dimensions. Two modes:

- ``fold`` — the two blanks and their fold programs. The tray folds with **locking ends**: the
  long walls rise, ears on their ends fold in, the end walls rise and roll over the ears (each
  end wall is a double leaf), and lock tabs on the inner leaves drop into slots at the base folds
  (no glue). The sleeve is four panels and a glue flap folded into a tube (a glued tube).
- ``slide`` — the assembled pack: both erected in the initial frame, the sleeve a fixed rigid
  board and the tray a rigid board moved by a ``translate`` mechanism; the ``slide`` control
  pushes the tray out of the sleeve and back (spec §5.4: mechanisms move rigid sheets only).

**Thickness compensation** (caliper t, tray inside L × W × D): tray panels are inside + t, the
inner leaf of a rolled end is t shorter than its outer leaf, the lock slots are 2t wide through
the fold and the tabs drop 1.5t (the inner leaf ends t above the base's centre plane, so the
tabs end flush with its underside): nothing hangs below the base to catch on the sleeve. The
sleeve fits the tray's outside (W + 2t across, D + t high, plus ``clearance``) and is as long
as the tray's outside (L + 2t); its panels are inside + t. Every fold is straight and no hinge
meets another inside a sheet, so both blanks are face trees and the fold programs are kinematic
and exact. The sleeve's glued joint is a glue zone; welding it, the tabs' snap and the friction
of the slide are the physics engine's part.
"""

import pliego


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


def L4(en, es, fr, pt):
    return {"en": en, "es": es, "fr": fr, "pt": pt}


run_mode = str(PARAM(lambda: mode, "slide"))          # noqa: F821 - injected by the runner
length = float(PARAM(lambda: length, 110.0))          # noqa: F821 - tray inside, slide axis
width = float(PARAM(lambda: width, 70.0))             # noqa: F821 - tray inside, across
depth = float(PARAM(lambda: depth, 25.0))             # noqa: F821 - tray inside height
clearance = float(PARAM(lambda: clearance, 1.0))      # noqa: F821 - sleeve over tray
stock = str(PARAM(lambda: stock, "folding-boxboard-300"))   # noqa: F821
branding = bool(PARAM(lambda: branding, True))        # noqa: F821

STOCKS = ("folding-boxboard-300", "sbs-board-350", "cardstock-300", "greyboard-1500")
if stock not in STOCKS:
    raise ValueError(f"sleeve-and-tray: stock must be one of {STOCKS}, got {stock!r}")
if run_mode not in ("fold", "slide"):
    raise ValueError("sleeve-and-tray: mode must be fold or slide")
length = pliego.clamp(length, 40.0, 300.0)
width = pliego.clamp(width, 30.0, min(length, 200.0))
depth = pliego.clamp(depth, 12.0, min(width, 80.0))
clearance = pliego.clamp(clearance, 0.3, 3.0)

t = pliego.board.caliper(stock)
Lp, Wp, Dp = length + t, width + t, depth + t
s = max(2.0 * t, 1.5)                     # ear inset (knife clearance)
tab = 1.5 * t                             # lock tab: ends flush with the base's underside
inner = Dp - t                            # rolled end: inner leaf


def notched(x0, y0, x1, y1, edge, spans, dep):
    """A rectangle with rectangular notches `dep` deep in its bottom or top edge."""
    pts = [(x0, y0)]
    if edge == "bottom":
        for a, b in sorted(spans):
            pts += [(a, y0), (a, y0 + dep), (b, y0 + dep), (b, y0)]
    pts += [(x1, y0), (x1, y1)]
    if edge == "top":
        for a, b in sorted(spans, reverse=True):
            pts += [(b, y1), (b, y1 - dep), (a, y1 - dep), (a, y1)]
    return pts + [(x0, y1)]


# ── tray: base (long axis along y), long walls left and right, rolled ends below and above ────
TRAY = {"base": L4("Tray base", "Fondo de la charola", "Fond du tiroir", "Fundo da gaveta"),
        "side": L4("Tray long wall", "Pared larga de la charola", "Paroi longue du tiroir",
                   "Parede longa da gaveta"),
        "ear": L4("Ear", "Oreja", "Oreille", "Orelha"),
        "end": L4("Tray end wall", "Cabecera de la charola", "Paroi d'extrémité du tiroir",
                  "Cabeceira da gaveta"),
        "inner": L4("Rolled end, inner leaf", "Cabecera enrollada, hoja interior",
                    "Extrémité roulée, feuillet intérieur", "Cabeceira enrolada, folha interna")}


def numbered(label, k):
    return {g: f"{v} {k}" for g, v in label.items()}


x0, y0 = Dp, 2 * Dp - t + tab            # base origin: room for the walls and the rolled end
x1, y1 = x0 + Wp, y0 + Lp
q = Wp / 4.0
spans = [(x0 + q - q / 4.0, x0 + q + q / 4.0), (x0 + 3 * q - q / 4.0, x0 + 3 * q + q / 4.0)]
slots = [(a - 0.5, b + 0.5) for a, b in spans]
tray = pliego.dieline.Dieline(
    "tray", "matchbox tray with rolled locking ends", "folding-carton",
    {"length": length, "width": width, "depth": depth}, stock, t,
    label=L4("Tray blank", "Suaje de la charola", "Flan du tiroir", "Corte da gaveta"),
    grain_deg=90.0)
base = [(x0, y0)]
for a, b in sorted(slots):
    base += [(a, y0), (a, y0 + t), (b, y0 + t), (b, y0)]
base += [(x1, y0), (x1, y1)]
for a, b in sorted(slots, reverse=True):
    base += [(b, y1), (b, y1 - t), (a, y1 - t), (a, y1)]
base.append((x0, y1))
tray.panel("base", base, "bottom", TRAY["base"])
walls, ears, ends, rolls = [], [], [], []
ear_w = Wp / 2.0 - t
for k, (xa, xb) in ((1, (x0 - Dp, x0)), (2, (x1, x1 + Dp))):
    tray.rect(f"side-{k}", xa, y0, xb, y1, "panel", numbered(TRAY["side"], k))
    tray.hinge("base", f"side-{k}", -90.0, name=f"side-{k}-fold")
    walls.append(f"side-{k}-fold")
    free, hing = (xa, xb) if k == 1 else (xb, xa)      # the wall's free edge and its base edge
    sgn = 1.0 if k == 1 else -1.0
    for j, (ye, dirn) in enumerate(((y0, -1.0), (y1, 1.0))):
        ear = f"side-{k}-ear-{j + 1}"
        e0, e1 = free + sgn * s, hing - sgn * s / 2.0
        ch = min(0.3 * ear_w, 0.4 * Dp)
        tray.panel(ear, [(e0, ye), (e1, ye), (e1, ye + dirn * ear_w),
                         (e0 + sgn * ch, ye + dirn * ear_w)], "dust-flap",
                   numbered(TRAY["ear"], 2 * (k - 1) + j + 1))
        tray.hinge(f"side-{k}", ear, -90.0, name=f"{ear}-fold")
        ears.append(f"{ear}-fold")
for k, (ya, dirn) in ((1, (y0, -1.0)), (2, (y1, 1.0))):
    yb = ya + dirn * Dp
    lo, hi = sorted((ya, yb))
    tray.panel(f"end-{k}", notched(x0, lo, x1, hi, "top" if k == 1 else "bottom", slots, t),
               "panel", numbered(TRAY["end"], k))
    tray.hinge("base", f"end-{k}", -90.0, name=f"end-{k}-fold")
    yc = yb + dirn * inner
    leaf = [(x0 + t, yb), (x1 - t, yb), (x1 - t, yc)]
    for a, b in sorted(spans, reverse=True):
        leaf += [(b, yc), (b - 0.5, yc + dirn * tab), (a + 0.5, yc + dirn * tab), (a, yc)]
    leaf.append((x0 + t, yc))
    tray.panel(f"end-{k}-inner", leaf, "lock", numbered(TRAY["inner"], k))
    tray.hinge(f"end-{k}", f"end-{k}-inner", -180.0, name=f"roll-{k}-fold")
    ends.append(f"end-{k}-fold")
    rolls.append(f"roll-{k}-fold")
tray.dimension((x0, y0), (x1, y0), f"W {width:g} (inside)", -6.0)
tray.dimension((x0 - Dp, y0), (x0 - Dp, y1), f"L {length:g} (inside)", 8.0)
tray.step("walls-up", L4("Raise the long walls", "Levanta las paredes largas",
                         "Relevez les parois longues", "Levante as paredes longas"), walls, 1100)
tray.step("ears-in", L4("Fold the ears in", "Dobla las orejas hacia dentro",
                        "Rabattez les oreilles", "Dobre as orelhas para dentro"), ears, 900)
tray.step("ends-up", L4("Raise the end walls over the ears",
                        "Levanta las cabeceras sobre las orejas",
                        "Relevez les extrémités sur les oreilles",
                        "Levante as cabeceiras sobre as orelhas"), ends, 1000)
tray.step("roll-ends", L4("Roll the ends in and drop the tabs into the slots",
                          "Enrolla las cabeceras y mete las pestañas en las ranuras",
                          "Roulez les extrémités et engagez les pattes dans les fentes",
                          "Enrole as cabeceiras e encaixe as abas nas fendas"), rolls, 1400)
tray_pack = tray.build(rest_on="base")

# ── sleeve: bottom, side, top, side and glue flap; the tube's axis runs along the tray ────────
Ws, Hs = width + 2 * t + clearance, depth + t + clearance      # inside, over the tray
Wsp, Hsp, Ls = Ws + t, Hs + t, length + 2 * t
G = min(max(0.2 * Hsp, 8.0), 15.0)
SLEEVE = {"bottom": L4("Sleeve bottom", "Base de la funda", "Dessous du fourreau",
                       "Base da luva"),
          "side": L4("Sleeve side", "Costado de la funda", "Côté du fourreau", "Lateral da luva"),
          "top": L4("Sleeve top", "Cara superior de la funda", "Dessus du fourreau",
                    "Topo da luva")}
sleeve = pliego.dieline.Dieline(
    "sleeve", "matchbox sleeve (glued tube)", "folding-carton",
    {"length": length + 2 * t, "width": Ws, "depth": Hs}, stock, t,
    label=L4("Sleeve blank", "Suaje de la funda", "Flan du fourreau", "Corte da luva"),
    grain_deg=0.0)
xs = [0.0, Wsp, Wsp + Hsp, 2 * Wsp + Hsp, 2 * Wsp + 2 * Hsp]
names = ["bottom", "side-1", "top", "side-2"]
for k, nm in enumerate(names):
    lab = SLEEVE[nm.split("-")[0]]
    sleeve.rect(nm, xs[k], 0.0, xs[k + 1], Ls, "panel",
                numbered(lab, nm[-1]) if nm.startswith("side") else lab)
xe = xs[-1]
sleeve.panel("glue-flap", [(xe, G * 0.5), (xe + G, G), (xe + G, Ls - G), (xe, Ls - G * 0.5)],
             "glue-flap", L4("Glue flap", "Pestaña de pegado", "Patte de collage",
                             "Aba de colagem"), print_area=False)
sleeve.glue_zone("manufacturers-joint", [(xe + 1.0, G), (xe + G - 1.0, G + 0.6),
                                         (xe + G - 1.0, Ls - G - 0.6), (xe + 1.0, Ls - G)],
                 on="glue-flap")
folds = []
for a_, b_ in zip(names, names[1:] + ["glue-flap"]):
    sleeve.hinge(a_, b_, -90.0, name=f"{a_}-{b_}-fold")
    folds.append(f"{a_}-{b_}-fold")
sleeve.dimension((0.0, 0.0), (Wsp, 0.0), f"{Ws:.1f} (inside)", -6.0)
sleeve.dimension((0.0, 0.0), (0.0, Ls), f"{Ls:.1f}", 8.0)
sleeve.step("form-sleeve", L4("Fold the sleeve into a tube and glue the joint",
                              "Dobla la funda en un tubo y pega la unión",
                              "Pliez le fourreau en tube et collez la patte",
                              "Dobre a luva num tubo e cole a junta"), folds, 1600)
sleeve_pack = sleeve.build(rest_on="bottom")

artwork = []
if branding:
    side_len = 0.5 * min(Wsp, Ls)
    cx, cy = xs[2] + Wsp / 2.0, Ls / 2.0
    artwork.append(pliego.press.artwork(
        "brand-mark", sleeve_pack.sheet, "assets/brand-mark.svg",
        (cx - side_len / 2, cy - side_len / 2), (side_len, side_len), side="front", panel="top",
        clip="panel"))
params = {"length": length, "width": width, "depth": depth, "clearance": clearance,
          "stock": stock, "branding": branding}
ROT = (1.0, 0.0, 0.0, 0.0)               # print side down: sheet (u, v) → world (u, 0, v)
# the sleeve's bottom under the tray's base, centred on it (world x across, z along the tray)
origin = (x0 + Wp / 2.0 - Wsp / 2.0, -(t + clearance / 2.0), y0 + Lp / 2.0 - Ls / 2.0)

if run_mode == "fold":
    tray_box = max(p[0] for pn in tray.panels.values() for p in pn.polygon)
    sleeve_pack.sheet.placement = pliego.Placement(origin=(tray_box + 40.0, 0.0, 0.0),
                                                   rotation=ROT)
    result = pliego.dieline.assemble(
        [tray_pack, sleeve_pack], title="Sleeve and tray (blanks)", artwork=artwork,
        label=L4("Fold program", "Secuencia de armado", "Séquence de montage",
                 "Sequência de montagem"),
        meta={"cartridge": "sleeve-and-tray", "mode": "fold", "params": params})
else:
    travel = round(0.8 * Ls, 1)
    tray_pack.sheet.kinematic = "slide-tray"
    sleeve_pack.sheet.kinematic = "slide-tray"          # not moved by it: a fixed board
    sleeve_pack.sheet.placement = pliego.Placement(origin=origin, rotation=ROT)
    initial = dict(tray_pack.closed)
    initial.update(sleeve_pack.closed)
    result = pliego.Assembly(
        [tray_pack.sheet, sleeve_pack.sheet],
        mechanisms=[pliego.translate("slide-tray", "slide", (0.0, 0.0, 1.0), travel,
                                     [tray_pack.sheet])],
        controls=[pliego.control("slide", "distance",
                                 L4("Slide the tray out", "Desliza la charola hacia fuera",
                                    "Faire glisser le tiroir", "Deslize a gaveta para fora"),
                                 0.0, 0.0, travel, "mm")],
        initial=initial, dielines=[tray_pack.block, sleeve_pack.block], artwork=artwork,
        title="Sleeve and tray",
        meta={"cartridge": "sleeve-and-tray", "mode": "slide", "params": params})
