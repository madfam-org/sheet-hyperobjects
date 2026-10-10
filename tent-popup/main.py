"""Tent pop-up — sheet-hyperobjects cartridge (Pliego).

A strip of card folded in the middle (the ridge) and glued across the gutter of a card, its two
tabs at the same distance `glue_distance` from the gutter on each page. Its sides are longer than
the glue distance, so it stands as a tent (a roof) when the card lies open flat, and folds flat
inside when the card closes. It is the 180° mechanism of paper engineering.

Kinematics (Tier R, exact). In the card's cross-section the piece is a kite four-bar G–A–F–B:
G the gutter, A and B the tab hinges at distance p from it on each page (lifted by the piece's
offset above the card), F the ridge with |AF| = |FB| = s > p, on the far side of AB from G:
F = M + √(s² − |AM|²)·n, M the midpoint of AB and n the unit normal pointing away from G. The kite
never locks (s > p) and never passes through the card. The three creases' angles are the signed
turns between consecutive links; the script poses the piece with `pliego.kinematics` and checks,
at every state, that its right tab lies on the right page exactly where it is glued.

The card is one scored sheet whose gutter is folded by the same kinematic program, so the studio
preview animates both: the piece is posed from its left tab, glued to the card's fixed page.
"""

import math

import pliego
from pliego import kinematics


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


page_width = float(PARAM(lambda: page_width, 150.0))        # noqa: F821
page_height = float(PARAM(lambda: page_height, 150.0))      # noqa: F821
glue_distance = float(PARAM(lambda: glue_distance, 35.0))   # noqa: F821
side = float(PARAM(lambda: side, 55.0))                     # noqa: F821
tent_width = float(PARAM(lambda: tent_width, 80.0))         # noqa: F821
tab_width = float(PARAM(lambda: tab_width, 12.0))           # noqa: F821
tent_offset = float(PARAM(lambda: tent_offset, 0.5))        # noqa: F821

W = pliego.clamp(page_width, 90.0, 220.0)
H = pliego.clamp(page_height, 90.0, 260.0)
p = pliego.clamp(glue_distance, 10.0, 90.0)
s = pliego.clamp(side, 15.0, 120.0)
pw = pliego.clamp(tent_width, 20.0, 200.0)
t = pliego.clamp(tab_width, 8.0, 20.0)
pos = pliego.clamp(tent_offset, 0.0, 1.0)

CARD_STOCK, PIECE_STOCK = "cardstock-300", "cardstock-250"
LIFT = 0.2           # the piece lies this far above the card (< the stocks' collision thickness)
INSET = 0.5          # glue regions stop this short of the tab's edges
SHUT = 170.0         # zero-thickness sheets cannot nest fully shut: the preview stops here
MARGIN = 6.0
TOL = 1e-6


def L4(en, es, fr, pt):
    return {"en": en, "es": es, "fr": fr, "pt": pt}


if s < p + 2.0:
    raise ValueError(f"tent-popup: the sides ({s:g} mm) must be longer than the glue distance "
                     f"({p:g} mm) by at least 2 mm, or the tent does not stand")
if p + s > W - MARGIN:
    raise ValueError(f"tent-popup: shut, the tent reaches {p + s:g} mm from the gutter; keep "
                     f"glue_distance + side ≤ page_width − {MARGIN:g}")
if p + t > W - MARGIN:
    raise ValueError("tent-popup: the tabs run off the page")
if pw > H - 2 * MARGIN:
    raise ValueError(f"tent-popup: a {pw:g} mm wide tent does not fit a {H:g} mm card")
at = MARGIN + pos * (H - 2 * MARGIN - pw)        # the piece's distance from the bottom edge

# ── sheets ───────────────────────────────────────────────────────────────────

card = pliego.Sheet("card", [(0, 0), (2 * W, 0), (2 * W, H), (0, H)], stock=CARD_STOCK,
                    grain_deg=90.0, label=L4("Card", "Tarjeta", "Carte", "Cartão"))
gutter = card.valley((W, 0), (W, H), treatment="score", name="gutter", label=L4(
    "Gutter (the card's spine)", "Pliegue central (lomo de la tarjeta)",
    "Pliure centrale (dos de la carte)", "Dobra central (lombada do cartão)"))

total = 2 * t + 2 * s
piece = pliego.Sheet(
    "tent", [(0, 0), (total, 0), (total, pw), (0, pw)], stock=PIECE_STOCK, grain_deg=90.0,
    label=L4("Tent piece", "Pieza en tienda", "Pièce en tente", "Peça em tenda"),
    placement=pliego.Placement(origin=(W - p - t, LIFT, -at)),
)
c_a = piece.valley((t, 0), (t, pw), treatment="score", label=L4(
    "Left glue fold", "Doblez de pegado izquierdo", "Pli de collage gauche",
    "Dobra de colagem esquerda"))
c_f = piece.mountain((t + s, 0), (t + s, pw), treatment="score", name="ridge", label=L4(
    "Ridge of the tent", "Cumbrera de la tienda", "Faîte de la tente", "Cumeeira da tenda"))
c_b = piece.valley((t + 2 * s, 0), (t + 2 * s, pw), treatment="score", label=L4(
    "Right glue fold", "Doblez de pegado derecho", "Pli de collage droit",
    "Dobra de colagem direita"))
piece.label_edge("glue-left", (0, 0), (0, pw))
piece.label_edge("glue-right", (total, 0), (total, pw))

# ── the kite four-bar in the cross-section (world x, y; the gutter at x = W) ──


def frame(gamma):
    """Page directions and normals at gutter angle γ (the right page turned up by γ)."""
    g = math.radians(gamma)
    return (-1.0, 0.0), (0.0, 1.0), (math.cos(g), math.sin(g)), (-math.sin(g), math.cos(g))


def kite(gamma):
    e_l, n_l, e_r, n_r = frame(gamma)
    a = (W + p * e_l[0] + LIFT * n_l[0], p * e_l[1] + LIFT * n_l[1])
    b = (W + p * e_r[0] + LIFT * n_r[0], p * e_r[1] + LIFT * n_r[1])
    m = ((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0)
    half = math.dist(a, m)
    nrm = (-math.sin(math.radians(gamma) / 2.0), math.cos(math.radians(gamma) / 2.0))
    h = math.sqrt(s * s - half * half)
    f = (m[0] + h * nrm[0], m[1] + h * nrm[1])
    return a, f, b, e_r


def turn(d0, d1):
    """Signed turn (degrees) from direction d0 to d1: positive = toward the front (valley)."""
    return math.degrees(math.atan2(d0[0] * d1[1] - d0[1] * d1[0], d0[0] * d1[0] + d0[1] * d1[1]))


def unit(v):
    n = math.hypot(*v)
    return (v[0] / n, v[1] / n)


def angles(gamma):
    a, f, b, e_r = kite(gamma)
    d1, d2 = unit((f[0] - a[0], f[1] - a[1])), unit((b[0] - f[0], b[1] - f[1]))
    return {gutter: gamma, c_a: turn((1.0, 0.0), d1), c_f: turn(d1, d2), c_b: turn(d2, e_r)}


def piece_world(gamma, u, v):
    """Where piece point (u, v) is at gutter angle γ (exact kite pose)."""
    a, f, b, e_r = kite(gamma)
    if u <= t:
        x = (a[0] - (t - u), a[1])
    elif u <= t + s:
        d = unit((f[0] - a[0], f[1] - a[1]))
        x = (a[0] + d[0] * (u - t), a[1] + d[1] * (u - t))
    elif u <= t + 2 * s:
        d = unit((b[0] - f[0], b[1] - f[1]))
        x = (f[0] + d[0] * (u - t - s), f[1] + d[1] * (u - t - s))
    else:
        x = (b[0] + e_r[0] * (u - t - 2 * s), b[1] + e_r[1] * (u - t - 2 * s))
    return (x[0], x[1], -(at + v))


def initial(sheet_id, uv):
    u, v = uv
    if sheet_id == "card":
        return (u, 0.0, -v)
    return piece_world(0.0, u, v)


# ── check: the piece posed from its left tab by the crease angles lands on its glue zone ──

parr = piece.build()


def pose_error(gamma):
    ang = {e: a for m, a in angles(gamma).items() if m is not gutter for e in m.edges()}
    tr = kinematics.face_transforms(parr, ang, kinematics.root_face(parr, pliego.P(t / 2, 1.0)))
    # the root tab's world placement: kernel un-placed (u, 0, −v) → its kite pose
    worst = 0.0
    off = (W - p - t, LIFT, -at)
    for fi, fv in enumerate(parr.faces):
        rot, tv = tr[fi]
        for vi in fv:
            q = parr.vertices[vi]
            loc = [sum(rot[i][j] * (q.x, 0.0, -q.y)[j] for j in range(3)) + tv[i]
                   for i in range(3)]
            got = (loc[0] + off[0], loc[1] + off[1], loc[2] + off[2])
            worst = max(worst, math.dist(got, piece_world(gamma, q.x, q.y)))
    return worst


SUB = 10
gam = ([SHUT * k / SUB for k in range(1, SUB + 1)]
       + [SHUT * (SUB - k) / SUB for k in range(1, SUB + 1)])
worst = max(pose_error(g) for g in [0.0] + gam)
if worst > 1e-6:
    raise ValueError(f"tent-popup: the posed piece misses its glue zone by {worst:.3g} mm")
for g in gam:
    a, f, b, _ = kite(g)
    if f[1] < 0.0 or math.dist(a, b) > 2 * s:
        raise ValueError("tent-popup: the tent would pass through the card")

steps = []
for k, g in enumerate(gam, 1):
    closing = k <= SUB
    n = k if closing else k - SUB
    lab = (L4("Close the card: the tent folds flat inside", "Cierra la tarjeta: la tienda se "
              "aplana por dentro", "Fermez la carte : la tente se range à plat",
              "Feche o cartão: a tenda fica plana por dentro") if closing else
           L4("Open the card flat: the tent stands", "Abre la tarjeta del todo: la tienda se "
              "levanta", "Ouvrez la carte à plat : la tente se dresse",
              "Abra o cartão por completo: a tenda se ergue"))
    steps.append(pliego.Step(f"{'close' if closing else 'open'}-{n}",
                             {lang: f"{txt} ({n}/{SUB})" for lang, txt in lab.items()},
                             [(m, a) for m, a in angles(g).items()], duration_ms=300))

region_l = [(INSET, INSET), (t - INSET, INSET), (t - INSET, pw - INSET), (INSET, pw - INSET)]
u0 = t + 2 * s
region_r = [(u0 + INSET, INSET), (total - INSET, INSET), (total - INSET, pw - INSET),
            (u0 + INSET, pw - INSET)]
joins = [
    pliego.glue("tent-left", piece, region_l, card, (1, 0, 0, 1, W - p - t, at), "front"),
    pliego.glue("tent-right", piece, region_r, card, (1, 0, 0, 1, W + p - u0, at), "front"),
]
print(f"kinematics: kite p={p:g} s={s:g} ridge_height_open={kite(0.0)[1][1] - LIFT:.2f}mm "
      f"program_steps={len(steps)} max_pose_error_mm={worst:.3e}")

result = pliego.Assembly(
    [card, piece], joins=joins,
    controls=[pliego.sequence_control(
        label=L4("Close and open", "Cerrar y abrir", "Fermer et ouvrir", "Fechar e abrir"),
        default=float(len(steps)))],
    sequence=pliego.Sequence(steps, mode="kinematic"),
    initial=initial,
    title="Tent pop-up",
)
