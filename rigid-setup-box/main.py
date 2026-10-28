"""Rigid set-up box — sheet-hyperobjects cartridge (Pliego).

The wrapped greyboard box of luxury packaging, generated from inside dimensions: a board tray
whose walls are raised and stayed at the corners, covered by a printed wrap that is glued under
the base, raised up the walls with ears wrapped round the corners, and turned in over the rim.

Three modes:
- ``tray``: one wrapped tray (a base, or a presentation tray);
- ``telescope``: a wrapped base and a wrapped lid that slides over it; the lid's board is the
  base's outside (board and wrap) plus the lid's own turn-in plus the clearance on every side, so
  the clearance is the air gap the lid slides on;
- ``shoulder``: a wrapped base, a wrapped neck glued inside it and standing above its rim, and a
  lid that slides over the neck and sits on the base's rim (the shoulder).

Geometry, all computed here from the stock cards' calipers (board t, wrap w). Panels are laid on
the mid-surface, as every Pliego dieline is: the board base is L + t by W + t, the long walls run
past the base by t/2 at each end and the end walls are butted between them (W long), so the inside
is exactly L × W × D. The wrap's base is the board's outside plus w; its walls rise D + t + w to
the rim, cross the rim in t + w and turn in by ``turn_in``; the long sides carry the corner ears.
Every blank is a face tree (flaps parted by slots and slits), so the fold program is kinematic.

What this does not model: board thickness in the 3-D preview (folds turn on the mid-surface; the
inside dimensions are compensated, the pose is not), the glue's physics, the corner stay tape as
its own sheet (its zones are marked on the board), and the slow, air-cushioned fall of a lid,
which depends on the clearance and is the reason it is a parameter.
"""

import pliego


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


def L4(en, es, fr, pt):
    return {"en": en, "es": es, "fr": fr, "pt": pt}


run_mode = str(PARAM(lambda: mode, "telescope"))                                 # noqa: F821
L = pliego.clamp(float(PARAM(lambda: length, 160.0)), 40.0, 500.0)               # noqa: F821
W = pliego.clamp(float(PARAM(lambda: width, 120.0)), 30.0, 400.0)                # noqa: F821
D = pliego.clamp(float(PARAM(lambda: depth, 60.0)), 15.0, 250.0)                 # noqa: F821
lid_d = float(PARAM(lambda: lid_depth, 25.0))                                    # noqa: F821
neck_h = pliego.clamp(float(PARAM(lambda: neck_height, 20.0)), 8.0, 80.0)        # noqa: F821
gap = pliego.clamp(float(PARAM(lambda: clearance, 0.3)), 0.1, 1.5)               # noqa: F821
board_slug = str(PARAM(lambda: board, "greyboard-1500"))                         # noqa: F821
wrap_slug = str(PARAM(lambda: wrap, "elephant-hide-110"))                        # noqa: F821
turn = float(PARAM(lambda: turn_in, 15.0))                                       # noqa: F821
ear_w = float(PARAM(lambda: ear, 12.0))                                          # noqa: F821

BOARDS = ("greyboard-1500", "folding-boxboard-300")
WRAPS = ("elephant-hide-110", "kraft-120", "foil-paper", "washi-kozo-30")
if run_mode not in ("tray", "telescope", "shoulder"):
    raise ValueError(f"rigid-setup-box: unknown mode {run_mode!r}")
if board_slug not in BOARDS:
    raise ValueError(f"rigid-setup-box: board must be one of {BOARDS}, got {board_slug!r}")
if wrap_slug not in WRAPS:
    raise ValueError(f"rigid-setup-box: wrap must be one of {WRAPS}, got {wrap_slug!r}")
W = min(W, L)                                     # long sides carry the ears: W ≤ L

t = pliego.stock.snapshot(board_slug)["caliper_mm"]
w = pliego.stock.snapshot(wrap_slug)["caliper_mm"]
PRINT_DOWN = (1.0, 0.0, 0.0, 0.0)                 # 180° about world X: walls fold up
PRINT_UP = (0.0, 0.0, 0.0, 1.0)                   # identity: walls fold down (a lid)
UPRIGHT = (0.7071067811865476, 0.0, 0.0, 0.7071067811865476)   # +90° about X: sheet stands

NAMES = {
    "base": L4("Base", "Base", "Fond", "Base"),
    "front": L4("Front wall", "Pared frontal", "Paroi avant", "Parede frontal"),
    "back": L4("Back wall", "Pared trasera", "Paroi arrière", "Parede traseira"),
    "left": L4("Left end", "Cabecera izquierda", "Côté gauche", "Cabeceira esquerda"),
    "right": L4("Right end", "Cabecera derecha", "Côté droit", "Cabeceira direita"),
    "ear": L4("Corner ear", "Oreja de esquina", "Oreille d'angle", "Orelha de canto"),
    "rim": L4("Rim", "Borde", "Chant", "Borda"),
    "turn": L4("Turn-in", "Doblez interior", "Rempli", "Dobra interna"),
    "glue": L4("Glue flap", "Pestaña de pegado", "Patte de collage", "Aba de colagem"),
}


def tag(key, side):
    return {k: f"{v} · {side}" for k, v in NAMES[key].items()}


def tray_board(sid, label, il, iw, depth):
    """Greyboard tray: base (il + t) × (iw + t), long walls over the full outside length, end
    walls butted between them; walls raised 90°, corner stays marked on the long walls."""
    d = pliego.dieline.Dieline(sid, "rigid set-up tray (board)", "rigid",
                               {"length": il, "width": iw, "depth": depth}, board_slug, t,
                               label=label, grain_deg=90.0)
    pl, pw, h = il + t, iw + t, depth + t / 2.0
    d.rect("base", 0.0, 0.0, pl, pw, "bottom", NAMES["base"], print_area=False)
    d.rect("front", -t / 2.0, -h, pl + t / 2.0, 0.0, "panel", NAMES["front"], print_area=False)
    d.rect("back", -t / 2.0, pw, pl + t / 2.0, pw + h, "panel", NAMES["back"], print_area=False)
    d.rect("left", -h, t / 2.0, 0.0, pw - t / 2.0, "panel", NAMES["left"], print_area=False)
    d.rect("right", pl, t / 2.0, pl + h, pw - t / 2.0, "panel", NAMES["right"],
           print_area=False)
    for side in ("front", "back", "left", "right"):
        d.hinge("base", side, -90.0, name=f"{side}-raise")
    stay = min(20.0, il / 4.0)
    for side, y0, y1 in (("front", -h + 2.0, -2.0), ("back", pw + 2.0, pw + h - 2.0)):
        d.glue_zone(f"{side}-stay-left", [(-t / 2.0, y0), (stay, y0), (stay, y1), (-t / 2.0, y1)],
                    "tape", on=side)
        d.glue_zone(f"{side}-stay-right", [(pl - stay, y0), (pl + t / 2.0, y0),
                                           (pl + t / 2.0, y1), (pl - stay, y1)], "tape", on=side)
    d.dimension((0.0, 0.0), (pl, 0.0), f"L {il:g} (inside)", -6.0)
    d.dimension((0.0, 0.0), (0.0, pw), f"W {iw:g} (inside)", 8.0)
    d.step("raise-walls", L4("Raise the walls and stay the corners",
                             "Levanta las paredes y refuerza las esquinas con cinta",
                             "Relevez les parois et renforcez les angles",
                             "Levante as paredes e reforce os cantos"),
           ["front-raise", "back-raise", "left-raise", "right-raise"], 1400)
    return d.build(rest_on="base")


def tray_wrap(sid, label, il, iw, depth, turn_in, ear):
    """Wrap for a tray of inside il × iw × depth: base glued under the board, walls up to the
    rim with corner ears on the long sides, rims over the wall tops, turn-ins down inside."""
    d = pliego.dieline.Dieline(sid, "rigid set-up tray (wrap)", "rigid",
                               {"length": il, "width": iw, "depth": depth}, wrap_slug, w,
                               label=label, grain_deg=0.0)
    pl, pw = il + 2.0 * t + w, iw + 2.0 * t + w
    h, r = depth + t + w, t + w
    ti = max(5.0, min(turn_in, depth - 3.0))
    e = max(6.0, min(ear, iw / 2.0 - 2.0))
    d.rect("base", 0.0, 0.0, pl, pw, "bottom", NAMES["base"])
    d.glue_zone("base-glue", [(2.0, 2.0), (pl - 2.0, 2.0), (pl - 2.0, pw - 2.0), (2.0, pw - 2.0)],
                on="base")
    long_rim, long_turn = il + 2.0 * t, il - 1.0
    end_rim, end_turn = iw, iw - 2.0 * w - 1.0
    for side, sign in (("front", -1.0), ("back", 1.0)):
        y0 = 0.0 if sign < 0 else pw
        ys = (lambda a, b, y0=y0, s=sign: (min(y0 + s * a, y0 + s * b), max(y0 + s * a, y0 + s * b)))
        wy0, wy1 = ys(0.0, h)
        d.rect(side, 0.0, wy0, pl, wy1, "panel", NAMES[side])
        d.hinge("base", side, -90.0, name=f"{side}-raise")
        d.glue_zone(f"{side}-glue", [(2.0, wy0 + 1.0), (pl - 2.0, wy0 + 1.0),
                                     (pl - 2.0, wy1 - 1.0), (2.0, wy1 - 1.0)], on=side)
        for end, x0, x1 in (("left", -e, 0.0), ("right", pl, pl + e)):
            ear_name = f"{side}-ear-{end}"
            d.rect(ear_name, x0, wy0, x1, wy1, "flap", tag("ear", f"{side} {end}"))
            d.hinge(side, ear_name, -90.0, name=f"{ear_name}-wrap")
        ry0, ry1 = ys(h, h + r)
        m = (pl - long_rim) / 2.0
        d.rect(f"{side}-rim", m, ry0, pl - m, ry1, "flap", tag("rim", side))
        d.hinge(side, f"{side}-rim", -90.0, name=f"{side}-rim-fold")
        ty0, ty1 = ys(h + r, h + r + ti)
        m = (pl - long_turn) / 2.0
        d.rect(f"{side}-turn-in", m, ty0, pl - m, ty1, "flap", tag("turn", side))
        d.hinge(f"{side}-rim", f"{side}-turn-in", -90.0, name=f"{side}-turn-in-fold")
    for side, sign in (("left", -1.0), ("right", 1.0)):
        x0 = 0.0 if sign < 0 else pl
        xs = (lambda a, b, x0=x0, s=sign: (min(x0 + s * a, x0 + s * b), max(x0 + s * a, x0 + s * b)))
        wx0, wx1 = xs(0.0, h)
        d.rect(side, wx0, 0.0, wx1, pw, "panel", NAMES[side])
        d.hinge("base", side, -90.0, name=f"{side}-raise")
        d.glue_zone(f"{side}-glue", [(wx0 + 1.0, 2.0), (wx1 - 1.0, 2.0), (wx1 - 1.0, pw - 2.0),
                                     (wx0 + 1.0, pw - 2.0)], on=side)
        rx0, rx1 = xs(h, h + r)
        m = (pw - end_rim) / 2.0
        d.rect(f"{side}-rim", rx0, m, rx1, pw - m, "flap", tag("rim", side))
        d.hinge(side, f"{side}-rim", -90.0, name=f"{side}-rim-fold")
        tx0, tx1 = xs(h + r, h + r + ti)
        m = (pw - end_turn) / 2.0
        d.rect(f"{side}-turn-in", tx0, m, tx1, pw - m, "flap", tag("turn", side))
        d.hinge(f"{side}-rim", f"{side}-turn-in", -90.0, name=f"{side}-turn-in-fold")
    d.dimension((0.0, 0.0), (pl, 0.0), f"{pl:.1f} (board outside + wrap)", -6.0)
    d.step("wrap-long-sides", L4("Raise the long sides and wrap the ears round the corners",
                                 "Sube los lados largos y envuelve las orejas en las esquinas",
                                 "Relevez les grands côtés et rabattez les oreilles aux angles",
                                 "Suba os lados longos e dobre as orelhas nos cantos"),
           ["front-raise", "back-raise", "front-ear-left-wrap", "front-ear-right-wrap",
            "back-ear-left-wrap", "back-ear-right-wrap"], 1400)
    d.step("wrap-ends", L4("Raise the ends over the ears", "Sube las cabeceras sobre las orejas",
                           "Relevez les petits côtés sur les oreilles",
                           "Suba as cabeceiras sobre as orelhas"),
           ["left-raise", "right-raise"], 1000)
    d.step("turn-in", L4("Turn the wrap in over the rim", "Dobla el forro hacia dentro sobre el borde",
                         "Rentrez le rempli sur le chant", "Dobre o forro para dentro sobre a borda"),
           [f"{s}-{k}" for s in ("front", "back", "left", "right")
            for k in ("rim-fold", "turn-in-fold")], 1600)
    return d.build(rest_on="base")


def tube(sid, label, ol, ow, height, slug, cal, rim_turn=None):
    """A four-sided band folded into a tube of outside ol × ow (mid-surface panels ol − cal and
    ow − cal), closed by a glue flap; with `rim_turn` = (rim, turn) each panel carries a rim and
    a turn-in at its top edge (the neck's wrap)."""
    d = pliego.dieline.Dieline(sid, "rigid set-up neck", "rigid",
                               {"length": ol, "width": ow, "height": height}, slug, cal,
                               label=label, grain_deg=90.0)
    a, b = ol - cal, ow - cal
    widths = [("front", a), ("left", b), ("back", a), ("right", b)]
    x = 0.0
    for name, span in widths:
        d.rect(name, x, 0.0, x + span, height, "panel", NAMES[name], print_area=rim_turn is not None)
        if rim_turn:
            rim, ti = rim_turn
            d.rect(f"{name}-rim", x + 0.5, height, x + span - 0.5, height + rim, "flap",
                   tag("rim", name))
            d.hinge(name, f"{name}-rim", -90.0, name=f"{name}-rim-fold")
            d.rect(f"{name}-turn-in", x + 1.0, height + rim, x + span - 1.0, height + rim + ti,
                   "flap", tag("turn", name))
            d.hinge(f"{name}-rim", f"{name}-turn-in", -90.0, name=f"{name}-turn-in-fold")
        x += span
    g = min(15.0, b / 2.0)
    d.panel("glue-flap", [(x, 2.0), (x + g, 2.0 + g / 3.0), (x + g, height - 2.0 - g / 3.0),
                          (x, height - 2.0)], "glue-flap", NAMES["glue"], print_area=False)
    for p, q in (("front", "left"), ("left", "back"), ("back", "right"), ("right", "glue-flap")):
        d.hinge(p, q, -90.0, name=f"{p}-{q}-fold")
    d.glue_zone("tube-joint", [(x + 1.0, 4.0), (x + g - 1.0, 4.0 + g / 3.0),
                               (x + g - 1.0, height - 4.0 - g / 3.0), (x + 1.0, height - 4.0)],
                on="glue-flap")
    d.step("form-tube", L4("Fold the band into a tube and glue the joint",
                           "Dobla la banda en un tubo y pega la unión",
                           "Pliez la bande en tube et collez la patte",
                           "Dobre a faixa num tubo e cole a junta"),
           ["front-left-fold", "left-back-fold", "back-right-fold", "right-glue-flap-fold"], 1400)
    if rim_turn:
        d.step("turn-in", L4("Turn the wrap in over the neck", "Dobla el forro sobre el cuello",
                             "Rentrez le rempli sur la hausse", "Dobre o forro sobre o colarinho"),
               [f"{s}-{k}" for s, _ in widths for k in ("rim-fold", "turn-in-fold")], 1400)
    return d.build(rest_on="front")


def place(pack, rotation, origin):
    pack.sheet.placement = pliego.Placement(origin=origin, rotation=rotation)


def wrapped_tray(prefix, label, il, iw, depth, y_mid, flipped=False):
    """Board and wrap of one tray, centred on the base board's centre (cx, cz), base board
    mid-plane at y_mid; `flipped` turns it open side down (a lid)."""
    board = tray_board(f"{prefix}-board", tag_label(label, "board"), il, iw, depth)
    wrap = tray_wrap(f"{prefix}-wrap", tag_label(label, "wrap"), il, iw, depth, turn, ear_w)
    bl, bw = il + t, iw + t
    wl, ww = il + 2.0 * t + w, iw + 2.0 * t + w
    off = (t + w) / 2.0
    if flipped:   # identity placement: world = (u, 0, −v) + origin, walls fold down
        place(board, PRINT_UP, (CX - bl / 2.0, y_mid, CZ + bw / 2.0))
        place(wrap, PRINT_UP, (CX - wl / 2.0, y_mid + off, CZ + ww / 2.0))
    else:         # print side down: world = (u, 0, v) + origin, walls fold up
        place(board, PRINT_DOWN, (CX - bl / 2.0, y_mid, CZ - bw / 2.0))
        place(wrap, PRINT_DOWN, (CX - wl / 2.0, y_mid - off, CZ - ww / 2.0))
    return [board, wrap]


def tag_label(label, part):
    words = {"board": L4("board", "cartón", "carton", "cartão"),
             "wrap": L4("wrap", "forro", "habillage", "forro")}[part]
    return {k: f"{v} ({words[k]})" for k, v in label.items()}


CX, CZ = (L + t) / 2.0, (W + t) / 2.0      # the base board's centre in world x, z
BASE = L4("Base", "Base", "Fond", "Base")
LID = L4("Lid", "Tapa", "Couvercle", "Tampa")
rim_top = D + t / 2.0 + w                  # the base's rim, over the wrap's rim strip
packs = wrapped_tray("base", BASE, L, W, D, 0.0)
lid_inside = None
if run_mode == "telescope":
    # the base's outside (board + wrap) + the lid's own turn-in + the air gap, per side
    lid_inside = (L + 2.0 * (t + 2.0 * w + gap), W + 2.0 * (t + 2.0 * w + gap))
    depth_lid = pliego.clamp(lid_d, 10.0, D)
elif run_mode == "shoulder":
    nl, nw = L - 2.0 * w - 2.0 * 0.1, W - 2.0 * w - 2.0 * 0.1   # the neck's outside, snug
    neck_total = D - 0.5 + neck_h
    neck = tube("neck-board", L4("Neck (board)", "Cuello (cartón)", "Hausse (carton)",
                                 "Colarinho (cartão)"), nl, nw, neck_total, board_slug, t)
    neck_wrap = tube("neck-wrap", L4("Neck (wrap)", "Cuello (forro)", "Hausse (habillage)",
                                     "Colarinho (forro)"), nl + 2.0 * w, nw + 2.0 * w,
                     neck_h - 0.5 - w / 2.0, wrap_slug, w,
                     rim_turn=(t + w, min(turn, neck_total - 5.0)))
    # stood upright (+90° about X: world = (u, v, 0) + origin), front panel against the back wall
    zb = CZ + W / 2.0 - w - 0.1
    place(neck, UPRIGHT, (CX - (nl - t) / 2.0, t / 2.0 + 0.5, zb - t / 2.0))
    place(neck_wrap, UPRIGHT, (CX - (nl + w) / 2.0, rim_top + 0.5, zb + w / 2.0))
    packs += [neck, neck_wrap]
    lid_inside = (nl + 4.0 * w + 2.0 * gap, nw + 4.0 * w + 2.0 * gap)   # neck wrap + lid turn-in
    depth_lid = neck_h
if lid_inside:
    # closed: a telescope lid's top rests on the base's rim; a shoulder lid's walls stand on it
    li, wi = lid_inside
    lid_mid = rim_top + t / 2.0 + (depth_lid if run_mode == "shoulder" else 0.0)
    packs += wrapped_tray("lid", LID, li, wi, depth_lid, lid_mid, flipped=True)

result = pliego.dieline.assemble(
    packs, title=f"Rigid set-up box ({run_mode})",
    label=L4("Fold program", "Secuencia de armado", "Séquence de montage", "Sequência de montagem"),
    meta={"cartridge": "rigid-setup-box",
          "params": {"mode": run_mode, "length": L, "width": W, "depth": D, "lid_depth": lid_d,
                     "neck_height": neck_h, "clearance": gap, "board": board_slug,
                     "wrap": wrap_slug, "turn_in": turn, "ear": ear_w}})
