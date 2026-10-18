"""Case binding — sheet-hyperobjects cartridge (Pliego): a hardcover book from three commons.

The paper parts are Pliego's: greyboard boards, a card spine strip, kraft endpapers and the text
block's signatures. The cover cloth is Fashion Cabinet's fabric (``manta-cruda`` or
``popelina-algodon``), used by ``material_ref`` and backed with kraft paper as a **laminate**
stock (``pliego.laminate``, spec §5.40): the kernel reads the fabric's ``sheet_behaviour`` from
its vendored keystone snapshot and never copies the fabric card. The optional magnetic clasp is
Yantra4D's ``magnetic-clasp``, named by the manifest's ``hardware_ref`` and checked name-level
(§5.42); Pliego cuts only the recesses its two halves sit in.

Two modes:
- ``case``: the cover cloth as one sheet. The joints are creased where the boards and the spine
  strip are laid, the head and tail are turned in, then the fore-edges with their mitred corners
  tucked, and the case closes round the text block's thickness (a ``pliego.FoldProgram``: rigid,
  layer-ordered, previewable);
- ``book``: the cased-in book. Covered boards and spine (laminate stocks), the endpapers (paste-
  downs on the boards, flyleaves hinged at the spine) and the signatures of the text block, each
  turning on its spine; the front cover opens and closes on a hinge, and with the clasp a cloth
  flap wraps the fore-edge onto the front cover (two keyed hinges, one control).

Geometry, all computed here: text block thickness = leaves × the text paper's caliper (from its
stock card); spine strip = text block + 2 × board; board = page + square at head, tail and
fore-edge, set back from the spine by the joint.
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


run_mode = PARAM(lambda: mode, "case")  # noqa: F821
page_w = pliego.clamp(float(PARAM(lambda: page_width, 148.0)), 80.0, 300.0)  # noqa: F821
page_h = pliego.clamp(float(PARAM(lambda: page_height, 210.0)), 100.0, 320.0)  # noqa: F821
n_sig = int(pliego.clamp(round(float(PARAM(lambda: signatures, 6))), 1, 12))  # noqa: F821
per_sig = int(pliego.clamp(round(float(PARAM(lambda: sheets_per_signature, 4))), 2, 8))  # noqa: F821
text_stock = str(PARAM(lambda: text_paper, "copy-80"))  # noqa: F821
b = pliego.clamp(float(PARAM(lambda: board_caliper, 1.5)), 1.0, 3.0)  # noqa: F821
joint_w = pliego.clamp(float(PARAM(lambda: joint, 7.0)), 4.0, 12.0)  # noqa: F821
sq = pliego.clamp(float(PARAM(lambda: square, 3.0)), 2.0, 5.0)  # noqa: F821
ti = pliego.clamp(float(PARAM(lambda: turn_in, 15.0)), 12.0, 20.0)  # noqa: F821
cloth_slug = str(PARAM(lambda: cloth, "manta-cruda"))  # noqa: F821
with_clasp = bool(PARAM(lambda: clasp, False))  # noqa: F821
magnet_d = pliego.clamp(float(PARAM(lambda: clasp_magnet, 12.0)), 6.0, 20.0)  # noqa: F821

TEXT_PAPERS = ("copy-80", "kraft-120", "cardstock-160")
CLOTHS = {"manta-cruda": ("#e9dfc8", "#d9c9a3"), "popelina-algodon": ("#2f4a6d", "#25384f")}
if text_stock not in TEXT_PAPERS:
    raise ValueError(f"text_paper must be one of {TEXT_PAPERS}, got {text_stock!r}")
if cloth_slug not in CLOTHS:
    raise ValueError(f"cloth must be one of {tuple(CLOTHS)}, got {cloth_slug!r}")
if run_mode not in ("case", "book"):
    raise ValueError(f"unknown mode {run_mode!r}")

# ── the book's numbers ───────────────────────────────────────────────────────
caliper = pliego.stock.snapshot(text_stock)["caliper_mm"]  # the text paper's card
pages = 4 * per_sig * n_sig            # each sheet of a signature is folded once: 4 pages
leaves = pages // 2
T = leaves * caliper                   # text block thickness
S = T + 2.0 * b                        # spine strip: the block between the two boards
x_tb = b                               # the text block's spine edge sits inside the spine strip
bw = page_w + sq + x_tb - joint_w      # board width: to the square at the fore-edge
bh = page_h + 2.0 * sq                 # board height: a square at head and tail
t_sig = 2 * per_sig * caliper          # one signature's thickness
ENDPAPER = "kraft-120"
PAD = 0.3                              # a pastedown's offset from its board (display only)

# ── the laminate stocks (spec §5.40) ────────────────────────────────────────
LAM = pliego.laminate
CLOTH_REF = {"platform": "fashion-cabinet", "material_slug": cloth_slug, "behaviour": "sheet"}
front_hex, back_hex = CLOTHS[cloth_slug]
BOARD = LAM.layer(stock="greyboard-1500", thickness_mm=b)
KRAFT = LAM.layer(stock="kraft-120")
CLOTH = LAM.layer(material_ref=CLOTH_REF)
STOCKS = {
    "case-cloth": LAM.stock(L4("Book cloth on kraft", "Tela de encuadernar sobre kraft",
                               "Toile de reliure sur kraft", "Tecido de encadernação sobre kraft"),
                            [KRAFT, CLOTH], appearance={"front": "#b08d5b", "back": front_hex}),
}
if run_mode == "book":
    COVERED = L4("Covered board", "Cartón forrado", "Carton couvert", "Cartão forrado")
    STOCKS["covered-board"] = LAM.stock(COVERED, [BOARD, KRAFT, CLOTH],
                                        appearance={"front": front_hex, "back": "#8a8580"})
    STOCKS["covered-board-back"] = LAM.stock(COVERED, [CLOTH, KRAFT, BOARD],
                                             appearance={"front": "#8a8580", "back": front_hex})
    STOCKS["covered-spine"] = LAM.stock(
        L4("Covered spine strip", "Lomera forrada", "Carte de dos couverte", "Lombada forrada"),
        [LAM.layer(stock="cardstock-300"), KRAFT, CLOTH],
        appearance={"front": front_hex, "back": "#d8d2c4"})


def rect(w, h):
    return [(0.0, 0.0), (w, 0.0), (w, h), (0.0, h)]


# ── mode `case`: the cover cloth, turned in and closed (a fold program) ──────
def build_case():
    x1 = ti
    x2 = x1 + bw            # back board | joint
    x3 = x2 + joint_w       # joint | spine strip
    x4 = x3 + S             # spine strip | joint
    x5 = x4 + joint_w       # joint | front board
    x6 = x5 + bw
    cw, ch = x6 + ti, bh + 2.0 * ti
    y1, y2 = ti, ti + bh
    # mitred corners: cut at 45° one and a half board thicknesses off each board corner, so the
    # turned-in corner covers the board's edge (the binder's "library corner" is not modelled)
    c = 2.0 * ti - 1.5 * b * math.sqrt(2.0)
    outline = [(c, 0.0), (cw - c, 0.0), (cw, c), (cw, ch - c), (cw - c, ch), (c, ch),
               (0.0, ch - c), (0.0, c)]
    fp = pliego.FoldProgram(outline, stock="case-cloth", grain_deg=90.0,
                            label=L4("Cover cloth", "Tela de la cubierta", "Toile de couverture",
                                     "Tecido da capa"), front="#b08d5b", back=front_hex)
    lay = L4("Lay the boards and the spine strip on the glued cloth: crease the joints",
             "Coloca los cartones y la lomera sobre la tela encolada: marca las cajas",
             "Posez les cartons et la carte de dos sur la toile encollée : marquez les mors",
             "Coloque os cartões e a lombada sobre o tecido colado: vinque os encaixes")
    for k, x in enumerate((x2, x3, x4, x5)):
        fp.crease(f"joint-{k + 1}", lay, ((x, 0.0), (x, ch)), "valley")
    fp.fold("turn-in-head", L4("Turn in the head", "Remete la cabeza", "Rempliez la tête",
                               "Dobre a cabeça para dentro"), ((cw, y1), (0.0, y1)), "valley")
    fp.fold("turn-in-tail", L4("Turn in the tail", "Remete el pie", "Rempliez la queue",
                               "Dobre o pé para dentro"), ((0.0, y2), (cw, y2)), "valley")
    fore = L4("Turn in the fore-edge: the mitred corner tucks under",
              "Remete el canal: la esquina en inglete queda debajo",
              "Rempliez la gouttière : le coin en onglet passe dessous",
              "Dobre o corte da frente para dentro: o canto em meia-esquadria fica por baixo")
    fp.fold("turn-in-fore-edge-back", fore, ((x1, 0.0), (x1, ch)), "valley")
    fp.fold("turn-in-fore-edge-front", fore, ((x6, ch), (x6, 0.0)), "valley")
    close = L4("Case in: the spine stands up round the text block",
               "Encaja el libro: el lomo se levanta alrededor del bloque de texto",
               "Emboîtez : le dos se dresse autour du corps d'ouvrage",
               "Encaixe o miolo: a lombada levanta-se em volta do miolo")
    fp.hinges("case-in", close, [{"line": ((x3, 0.0), (x3, ch)), "turn": 90.0,
                                  "at": ((x3 + x4) / 2.0, ch / 2.0)}])
    fp.hinges("close", L4("Close the book", "Cierra el libro", "Fermez le livre",
                          "Feche o livro"),
              [{"line": ((x4, 0.0), (x4, ch)), "turn": 90.0, "at": ((x5 + x6) / 2.0, ch / 2.0)}])
    built = fp.build("cover-cloth")
    print(built.summary())
    print(f"case-binding: mode=case pages={pages} block_mm={T:.2f} spine_mm={S:.2f} "
          f"board_mm={bw:.1f}x{bh:.1f} cloth_mm={cw:.1f}x{ch:.1f}")
    return pliego.Assembly(
        [built.sheet], controls=[pliego.sequence_control(label=L4(
            "Cover and case in", "Forrar y encajar", "Couvrir et emboîter", "Forrar e encaixar"))],
        sequence=built.sequence, initial=built.initial("cover-cloth"), stocks=STOCKS,
        title="Case binding — the case")


# ── mode `book`: the cased-in book (mechanisms) ──────────────────────────────
Q_UP = (0.0, 0.0, math.sqrt(0.5), math.sqrt(0.5))   # 90° about +Z: sheet u → world +Y


def kin(sid, label, w, h, stock, origin, mech, rotation=(0.0, 0.0, 0.0, 1.0), **kw):
    return pliego.Sheet(sid, rect(w, h), stock=stock, grain_deg=90.0, label=label,
                        placement=pliego.Placement(origin, rotation), kinematic=mech, **kw)


def circle_at(cx, cy, r, n=24):
    return [(cx + r * math.cos(2 * math.pi * k / n), cy + r * math.sin(2 * math.pi * k / n))
            for k in range(n)]


def build_book():
    sheets, mechs, ctrls, joins = [], [], [], []
    xf = joint_w + bw                       # the boards' fore-edge
    disc = magnet_d + 6.0                   # the printed housing's diameter (params_map)
    tab_w = max(30.0, disc + 16.0)
    back = kin("board-back", L4("Back board", "Tapa trasera", "Plat inférieur",
                                "Pasta de trás"), bw, bh, "covered-board-back",
               (joint_w, 0.0, 0.0), "cover")
    spine = kin("spine", L4("Spine", "Lomo", "Dos", "Lombada"), S, bh, "covered-spine",
                (0.0, 0.0, 0.0), "cover", Q_UP)
    front = kin("board-front", L4("Front board", "Tapa delantera", "Plat supérieur",
                                  "Pasta da frente"), bw, bh, "covered-board",
                (joint_w, S, 0.0), "cover")
    paste_b = kin("pastedown-back", L4("Back pastedown", "Guarda trasera pegada",
                                       "Contregarde inférieure", "Guarda de trás colada"),
                  page_w + x_tb - joint_w, page_h, ENDPAPER, (joint_w, PAD, -sq), "cover")
    paste_f = kin("pastedown-front", L4("Front pastedown", "Guarda delantera pegada",
                                        "Contregarde supérieure", "Guarda da frente colada"),
                  page_w + x_tb - joint_w, page_h, ENDPAPER, (joint_w, S - PAD, -sq), "cover")
    fly_b = kin("flyleaf-back", L4("Back flyleaf", "Guarda volante trasera",
                                   "Garde volante inférieure", "Guarda volante de trás"),
                page_w, page_h, ENDPAPER, (x_tb, b - PAD, -sq), "cover")
    if with_clasp:
        cx, cy = xf - joint_w - tab_w / 2.0, bh / 2.0
        front.hole(circle_at(cx, cy, disc / 2.0))
    sheets += [back, spine, paste_b, fly_b]
    turn = L4("Turn the signature", "Pasa el cuadernillo", "Tournez le cahier", "Vire o caderno")
    for k in range(1, n_sig + 1):
        y = b + T - (k - 0.5) * t_sig       # signature 1 on top
        leaf = pliego.Sheet(f"signature-{k}", rect(page_w, page_h), stock=text_stock,
                            grain_deg=90.0,
                            label=L4(f"Signature {k}", f"Cuadernillo {k}", f"Cahier {k}",
                                     f"Caderno {k}"),
                            placement=pliego.Placement((x_tb, y, -sq)))
        sheets.append(leaf)
        spine_line = ((0.0, 0.0), (0.0, page_h))
        mechs.append(pliego.leaf(f"signature-{k}-turn", leaf, spine_line, f"turn-{k}"))
        ctrls.append(pliego.angle_control(f"turn-{k}", turn, default=0.0))
        joins.append(pliego.pin(f"signature-{k}-sewn", along=(leaf, spine_line)))
    fly_f = pliego.Sheet("flyleaf-front", rect(page_w, page_h), stock=ENDPAPER, grain_deg=90.0,
                         label=L4("Front flyleaf", "Guarda volante delantera",
                                  "Garde volante supérieure", "Guarda volante da frente"),
                         placement=pliego.Placement((x_tb, S - b + PAD, -sq)))
    sheets += [fly_f, paste_f, front]
    fl = ((0.0, 0.0), (0.0, page_h))
    mechs.append(pliego.leaf("flyleaf-front-turn", fly_f, fl, "flyleaf"))
    ctrls.append(pliego.angle_control("flyleaf", L4("Turn the flyleaf", "Pasa la guarda",
                                                    "Tournez la garde", "Vire a guarda"),
                                      default=0.0))
    joins.append(pliego.pin("flyleaf-front-tipped", along=(fly_f, fl)))
    mechs.append(pliego.hinge("cover", (0.0, S, 0.0), (0.0, 0.0, 1.0), "open",
                              [front, paste_f]))
    ctrls.insert(0, pliego.angle_control("open", L4("Open the cover", "Abre la tapa",
                                                    "Ouvrez la couverture", "Abra a capa"),
                                         default=0.0))
    if with_clasp:
        wrap = S + 1.0
        side = kin("clasp-flap", L4("Clasp flap", "Solapa del cierre", "Rabat du fermoir",
                                    "Aba do fecho"), wrap, bh, "case-cloth", (xf, 0.0, 0.0),
                   "clasp-up")
        tab = kin("clasp-tab", L4("Clasp tab", "Lengüeta del cierre", "Patte du fermoir",
                                  "Lingueta do fecho"), tab_w, bh, "covered-board-back",
                  (xf + wrap, 0.0, 0.0), "clasp-over")
        tab.hole(circle_at(tab_w / 2.0, bh / 2.0, disc / 2.0))
        sheets += [side, tab]
        up = pliego.hinge("clasp-up", (xf, 0.0, 0.0), (0.0, 0.0, 1.0), "clasp", [side])
        up["keys"] = [[0.0, 0.0], [90.0, 90.0], [180.0, 90.0]]
        over = pliego.hinge("clasp-over", (xf + wrap, 0.0, 0.0), (0.0, 0.0, 1.0), "clasp",
                            [tab])
        over["keys"] = [[0.0, 0.0], [90.0, 0.0], [180.0, 90.0]]
        over["ride"] = "clasp-up"          # the tab turns on the flap, the flap on the board
        mechs += [up, over]
        ctrls.append(pliego.angle_control("clasp", L4(
            "Close the magnetic clasp", "Cierra el broche magnético", "Fermez le fermoir aimanté",
            "Feche o fecho magnético"), default=0.0))
    print(f"case-binding: mode=book pages={pages} signatures={n_sig} block_mm={T:.2f} "
          f"spine_mm={S:.2f} board_mm={bw:.1f}x{bh:.1f} clasp={'yes' if with_clasp else 'no'}"
          + (f" recess_mm={disc:.1f}" if with_clasp else ""))
    for sid, snap in sorted(STOCKS.items()):
        lam = snap["laminate"]
        print(f"laminate: {sid} layers={len(lam['layers'])} caliper_mm={snap['caliper_mm']} "
              f"coupled={'yes' if lam['coupled'] else 'no'} "
              f"coupling_ratio={lam['coupling_ratio']}")
    return pliego.Assembly(sheets, joins=joins, mechanisms=mechs, controls=ctrls, stocks=STOCKS,
                           title="Case binding — the book")


result = build_case() if run_mode == "case" else build_book()
