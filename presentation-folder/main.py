"""Presentation folder — sheet-hyperobjects cartridge (Pliego).

A pocket folder cut from one sheet of board: two covers joined by a **capacity spine** (two
parallel scores ``capacity`` + t apart), a **glued pocket** inside each cover (folded up from
the cover's bottom edge, its side tabs folded under and glued to the cover) and optional
**business-card slits** in the front pocket. Sized for A4 or US Letter content (presets), or
any content size.

Layout (print side = the folder's outside): back cover · spine · front cover, pockets below the
covers. Covers are the content size plus a margin; a pocket stops a tab's width plus 1 mm short
of its cover's outer edge, so its outer tab folds under it without showing, and its top corner
at the spine is cut away at 45° for an easy grip. Card slits are diagonal knife cuts that hold
the corners of a business card (85 × 55 mm or 3.5 × 2 in); they are placed in the folded
pocket's frame and mapped back through the 180° pocket fold.

Every fold is straight and no hinge meets another inside the sheet, so the blank is a face tree
and the program is kinematic and exact: tabs under, pockets up, then the folder closes about
its two spine scores. The tabs' glue zones are fabrication data; welding them, and the papers
inside pushing the spine open, are the physics engine's part.
"""

import math

import pliego


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


def L4(en, es, fr, pt):
    return {"en": en, "es": es, "fr": fr, "pt": pt}


size = str(PARAM(lambda: size, "a4"))                    # noqa: F821
capacity = float(PARAM(lambda: capacity, 6.0))           # noqa: F821 - spine capacity (mm)
pocket = float(PARAM(lambda: pocket, 100.0))             # noqa: F821 - pocket height (mm)
cards = str(PARAM(lambda: cards, "four"))                # noqa: F821 - none | two | four
card_size = str(PARAM(lambda: card_size, "iso"))         # noqa: F821 - iso | us
stock = str(PARAM(lambda: stock, "sbs-board-350"))       # noqa: F821
branding = bool(PARAM(lambda: branding, True))           # noqa: F821

SIZES = {"a4": (210.0, 297.0), "letter": (215.9, 279.4), "a5": (148.0, 210.0)}
COVERS = {"a4": (222.0, 310.0), "letter": (228.6, 304.8), "a5": (158.0, 222.0)}   # [E]
CARDS = {"iso": (85.0, 55.0), "us": (88.9, 50.8)}
STOCKS = ("sbs-board-350", "folding-boxboard-300", "cardstock-300", "cardstock-250")
if size not in SIZES or stock not in STOCKS or cards not in ("none", "two", "four") \
        or card_size not in CARDS:
    raise ValueError("presentation-folder: unknown size, stock, cards or card_size")
t = pliego.board.caliper(stock)
capacity = pliego.clamp(capacity, 0.0, 25.0)
Wc, Hc = COVERS[size]
pocket = pliego.clamp(pocket, 60.0, 0.45 * Hc)
spine = capacity + t                     # two scores, capacity + caliper apart (centre line)
TAB = 12.0                               # pocket glue tab
inset = TAB + 1.0                        # pocket inset at the cover's outer edge
slope = min(25.0, 0.25 * pocket)         # the pocket's spine-side corner is cut away
cs = max(2.0 + t, 3.5 - spine / 2.0)     # pocket clearance at the spine (room for tabs)
y0 = pocket + 2.0                        # covers' bottom edge (pockets below)
y1 = y0 + Hc
xb = (0.0, Wc)                           # back cover
xf = (Wc + spine, 2 * Wc + spine)        # front cover

d = pliego.dieline.Dieline(
    "folder", f"pocket folder ({size}, capacity {capacity:g} mm)", "board",
    {"width": SIZES[size][0], "height": SIZES[size][1], "depth": capacity}, stock, t,
    label=L4("Folder blank", "Suaje de la carpeta", "Flan de la chemise", "Corte da pasta"),
    grain_deg=90.0)
d.rect("back-cover", xb[0], y0, xb[1], y1, "panel",
       L4("Back cover", "Contraportada", "Quatrième de couverture", "Contracapa"))
d.rect("spine", xb[1], y0, xf[0], y1, "panel", L4("Spine", "Lomo", "Dos", "Lombada"))
d.rect("front-cover", xf[0], y0, xf[1], y1, "panel",
       L4("Front cover", "Portada", "Première de couverture", "Capa"))
d.hinge("back-cover", "spine", -90.0, name="spine-score-1")
d.hinge("spine", "front-cover", -90.0, name="spine-score-2")

POCKET = L4("pocket", "bolsillo", "pochette", "bolso")
TABL = L4("pocket glue tab", "pestaña de pegado del bolsillo", "patte de collage de la pochette",
          "aba de colagem do bolso")
tabs, pockets = [], []
geom = {}
for cover, (xa, xb_), outer in (("back-cover", xb, -1.0), ("front-cover", xf, 1.0)):
    po = xb_ - inset if outer > 0 else xa + inset          # the pocket's outer edge
    pi = xa + cs if outer > 0 else xb_ - cs                # its spine-side edge
    lo_x, hi_x = sorted((po, pi))
    h_out, h_in = pocket, pocket - slope
    name = f"{cover.split('-')[0]}-pocket"
    pts = [(lo_x, y0), (hi_x, y0)]
    pts += ([(hi_x, y0 - pocket), (lo_x + slope, y0 - pocket), (lo_x, y0 - h_in)] if outer > 0
            else [(hi_x, y0 - h_in), (hi_x - slope, y0 - pocket), (lo_x, y0 - pocket)])
    lab = {g: f"{d.panels[cover].label[g]}: {POCKET[g]}" for g in POCKET}
    d.panel(name, pts, "pocket", lab, print_area=True)
    d.hinge(cover, name, -180.0, name=f"{name}-fold")
    pockets.append(f"{name}-fold")
    geom[name] = (lo_x, hi_x, outer, po, pi)
    # glue tabs on both side edges, folded under the pocket (180°) and glued to the cover
    for side_x, h, dirn, width_ in ((po, h_out, outer, TAB),
                                    (pi, h_in, -outer, min(TAB, 0.5 * spine + cs - 0.5))):
        a0, a1 = y0 - 2.0, y0 - h + 3.0
        ch = min(width_, 0.4 * (a0 - a1))
        tab = [(side_x, a0), (side_x + dirn * width_, a0 - ch),
               (side_x + dirn * width_, a1 + ch), (side_x, a1)]
        tname = f"{name}-tab-{'outer' if side_x == po else 'inner'}"
        d.panel(tname, tab, "glue-flap", {g: f"{lab[g]}: {TABL[g]}" for g in TABL},
                print_area=False)
        d.hinge(name, tname, -180.0, name=f"{tname}-fold")
        tabs.append(f"{tname}-fold")
        lo_t, hi_t = sorted((side_x, side_x + dirn * width_))
        d.glue_zone(f"{tname}-glue", [(lo_t + 1.0, a0 - ch), (hi_t - 1.0, a0 - ch),
                                      (hi_t - 1.0, a1 + ch), (lo_t + 1.0, a1 + ch)], on=tname)

d.dimension((xb[0], y1), (xb[1], y1), f"cover {Wc:g}", 8.0)
d.dimension((xb[1], y1), (xf[0], y1), f"spine {spine:.2f} (capacity {capacity:g})", 16.0)
d.dimension((xb[0], y0), (xb[0], y1), f"{Hc:g}", 8.0)
d.dimension((xf[1], y0), (xf[1], y0 - pocket), f"pocket {pocket:g}", -8.0)
d.step("tabs-under", L4("Fold the pocket tabs under", "Dobla hacia atrás las pestañas de los "
                        "bolsillos", "Repliez les pattes des pochettes",
                        "Dobre para trás as abas dos bolsos"), tabs, 1000)
d.step("pockets-up", L4("Fold the pockets up and glue their tabs to the covers",
                        "Sube los bolsillos y pega sus pestañas a las tapas",
                        "Relevez les pochettes et collez leurs pattes aux couvertures",
                        "Suba os bolsos e cole as abas às capas"), pockets, 1400)
d.step("close", L4("Close the folder about its spine", "Cierra la carpeta por el lomo",
                   "Fermez la chemise sur son dos", "Feche a pasta pela lombada"),
       ["spine-score-1", "spine-score-2"], 1600)
pack = d.build(rest_on="back-cover")

# ── business-card slits in the front pocket: placed folded, mapped back through the fold ─────
slits = []
if cards != "none":
    lo_x, hi_x, outer, po, pi = geom["front-pocket"]
    cw, chh = CARDS[card_size]
    cx = (lo_x + hi_x) / 2.0 + 0.1 * (hi_x - lo_x)     # a little toward the outer edge
    cy = y0 + 0.5 * pocket                             # folded frame: above the hinge
    corners = [(cx - cw / 2, cy - chh / 2, (1, 1)), (cx + cw / 2, cy - chh / 2, (-1, 1)),
               (cx + cw / 2, cy + chh / 2, (-1, -1)), (cx - cw / 2, cy + chh / 2, (1, -1))]
    use = corners if cards == "four" else [corners[3], corners[1]]
    ell = 14.0
    for k, (px, py, (ix, iy)) in enumerate(use):
        # a cut across the corner, perpendicular to the card's diagonal, 4 mm in from the corner
        mx, my = px + ix * 4.0 / math.sqrt(2), py + iy * 4.0 / math.sqrt(2)
        ux, uy = -iy / math.sqrt(2), ix / math.sqrt(2)
        a = (mx - ux * ell / 2, my - uy * ell / 2)
        b = (mx + ux * ell / 2, my + uy * ell / 2)
        # through the 180° pocket fold about y = y0: (x, y0 + d) ↦ (x, y0 − d)
        a, b = (a[0], 2 * y0 - a[1]), (b[0], 2 * y0 - b[1])
        pack.sheet.cut([a, b], name=f"card-slit-{k + 1}")
        slits.append((a, b))
    print(f"presentation-folder: {len(slits)} card slits ({card_size} card {cw} x {chh} mm)")

artwork = []
if branding:
    side_len = 0.35 * min(Wc, Hc)
    cx_, cy_ = (xf[0] + xf[1]) / 2.0, y0 + 0.62 * Hc
    artwork.append(pliego.press.artwork(
        "brand-mark", pack.sheet, "assets/brand-mark.svg", (cx_ - side_len / 2, cy_ - side_len / 2),
        (side_len, side_len), side="front", panel="front-cover", clip="panel"))

result = pliego.dieline.assemble(
    [pack], title=f"Presentation folder ({size})", artwork=artwork,
    label=L4("Fold program", "Secuencia de armado", "Séquence de montage",
             "Sequência de montagem"),
    meta={"cartridge": "presentation-folder",
          "params": {"size": size, "capacity": capacity, "pocket": pocket, "cards": cards,
                     "card_size": card_size, "stock": stock, "branding": branding}})
