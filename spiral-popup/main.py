"""Spiral pop-up — sheet-hyperobjects cartridge (Pliego).

A spiral cut from a disc, lying flat inside a closed card: its outer end is glued to the left page
beside the gutter and its centre to the right page. Open the card and the right page lifts the
centre, so the spiral springs out of the gutter as a helix-like spring between the two pages; close
it and the spiral lies flat again.

This is a compliant (tier C) object: the spiral's rise is bending and twisting of a long strip, not
a rigid fold, so no kinematic program can describe it. The fold program is `physical`: it opens the
card's scored gutter to 90° and closes it again, and the physics engine bends the spiral through its
two `glue` joins. The card is one scored sheet; the spiral is a disc with an Archimedean spiral
strip (`turns` turns, 1 mm kerf between coils), checked with `pliego.papercut.analyze`.

Initial frame: the card shut to 180° − δ, where δ opens the right page just enough to meet the top
of the spiral at its centre (two layers of the piece's offset), so both glue welds hold within the
stocks' collision thickness and the gutter's start angle is unambiguous.
"""

import math

import pliego


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


page_width = float(PARAM(lambda: page_width, 150.0))       # noqa: F821
page_height = float(PARAM(lambda: page_height, 150.0))     # noqa: F821
diameter = float(PARAM(lambda: diameter, 100.0))           # noqa: F821
turns = float(PARAM(lambda: turns, 3.0))                   # noqa: F821
centre = float(PARAM(lambda: centre, 12.0))                # noqa: F821
gutter_gap = float(PARAM(lambda: gutter_gap, 6.0))         # noqa: F821
stock = PARAM(lambda: stock, "cardstock-160")              # noqa: F821

W = pliego.clamp(page_width, 90.0, 220.0)
H = pliego.clamp(page_height, 90.0, 260.0)
D = pliego.clamp(diameter, 50.0, 200.0)
N = pliego.clamp(turns, 1.5, 6.0)
rc = pliego.clamp(centre, 8.0, 30.0)
gg = pliego.clamp(gutter_gap, 3.0, 20.0)
if stock not in ("cardstock-160", "kraft-120", "copy-80"):
    raise ValueError(f"spiral-popup: unsupported stock {stock!r}")

CARD_STOCK = "cardstock-300"
KERF = 1.0            # removed between coils
LIFT = 0.25           # the spiral lies this far above the left page
INSET = 0.5
MARGIN = 6.0
STEP_DEG = 4.0        # outline resolution along the spiral


def L4(en, es, fr, pt):
    return {"en": en, "es": es, "fr": fr, "pt": pt}


R = D / 2.0
p = (R - rc) / N                      # coil pitch
w = p - KERF                          # strip width
if w < 4.0:
    raise ValueError(f"spiral-popup: {N:g} turns between radius {rc:g} and {R:g} mm leave a "
                     f"{w:.2f} mm strip; use fewer turns or a bigger disc (minimum 4 mm)")
c = R + gg                            # spiral centre, distance from the gutter
if c + R > W - MARGIN:
    raise ValueError(f"spiral-popup: the spiral needs pages at least {c + R + MARGIN:g} mm wide")
if D > H - 2 * MARGIN:
    raise ValueError(f"spiral-popup: a {D:g} mm spiral does not fit a {H:g} mm card")

# ── the spiral piece, in its own frame centred at (R, R) ─────────────────────
# centreline r(θ) = rc − w/2 + p·θ/2π; outer edge r + w/2 (θ from 0 to 2πN), inner edge r − w/2
# (θ from 2π to 2πN): the first turn of the outer edge bounds the centre disc.
r_s = rc - w / 2.0
theta_end = 2.0 * math.pi * N
CTR = (R, R)


PHASE = -theta_end      # turn the spiral so that its outer end points at the gutter (+u)


def at(radius, th):
    return (CTR[0] + radius * math.cos(th + PHASE), CTR[1] + radius * math.sin(th + PHASE))


def samples(t0, t1):
    k = max(2, int(math.degrees(t1 - t0) / STEP_DEG))
    return [t0 + (t1 - t0) * i / k for i in range(k + 1)]


outer = [at(r_s + p * th / (2 * math.pi) + w / 2.0, th) for th in samples(0.0, theta_end)]
inner = [at(r_s + p * th / (2 * math.pi) - w / 2.0, th)
         for th in reversed(samples(2 * math.pi, theta_end))]
spiral = pliego.Sheet("spiral", outer + inner, stock=stock, grain_deg=90.0,
                      label=L4("Spiral", "Espiral", "Spirale", "Espiral"),
                      placement=pliego.Placement(origin=(W - c - R, LIFT, -(H / 2.0 - R))))
rep = pliego.papercut.analyze(spiral, min_feature_mm=3.0, cutter_min_mm=0.5)
bad = [i for i in rep.issues if i["level"] == "error"]
if bad:
    raise ValueError(f"spiral-popup: the spiral fails the papercut check: {bad}")

# glue regions: the centre disc, and the last 40° of the strip (the end beside the gutter)
centre_region = [(CTR[0] + 0.6 * rc * math.cos(math.radians(a)),
                  CTR[1] + 0.6 * rc * math.sin(math.radians(a))) for a in range(0, 360, 20)]
d_end = min(math.radians(40.0), theta_end - 2 * math.pi - 0.1)
end_t = samples(theta_end - d_end, theta_end - 0.02)
end_region = ([at(r_s + p * th / (2 * math.pi) + w / 2.0 - INSET, th) for th in end_t] +
              [at(r_s + p * th / (2 * math.pi) - w / 2.0 + INSET, th) for th in reversed(end_t)])
# ── the card ─────────────────────────────────────────────────────────────────
card = pliego.Sheet("card", [(0, 0), (2 * W, 0), (2 * W, H), (0, H)], stock=CARD_STOCK,
                    grain_deg=90.0, label=L4("Card", "Tarjeta", "Carte", "Cartão"))
gutter = card.valley((W, 0), (W, H), treatment="score", name="gutter", label=L4(
    "Gutter (the card's spine)", "Pliegue central (lomo de la tarjeta)",
    "Pliure centrale (dos de la carte)", "Dobra central (lombada do cartão)"))

ox, oy = W - c - R, H / 2.0 - R      # spiral frame origin on the card (left page)
joins = [
    pliego.glue("spiral-end", spiral, end_region, card, (1, 0, 0, 1, ox, oy), "front"),
    # shut, the right page lies mirrored across the gutter: card x = 2W − (ox + u)
    pliego.glue("spiral-centre", spiral, centre_region, card, (-1, 0, 0, 1, 2 * W - ox, oy),
                "front"),
]

# initial frame: the right page tilted down to touch the spiral's top at its centre
delta = math.degrees(math.asin(2 * LIFT / c))
shut = 180.0 - delta


def initial(sheet_id, uv):
    u, v = uv
    if sheet_id == "spiral":
        return (ox + u, LIFT, -(oy + v))
    if u <= W:
        return (u, 0.0, -v)
    g = math.radians(shut)
    d = u - W
    return (W + d * math.cos(g), d * math.sin(g), -v)


steps = [
    pliego.Step("open", L4("Open the card to 90°: the spiral springs up from the gutter",
                           "Abre la tarjeta a 90°: la espiral salta desde el pliegue",
                           "Ouvrez la carte à 90° : la spirale jaillit de la pliure",
                           "Abra o cartão a 90°: a espiral salta da dobra"),
                [(gutter, 90.0)], duration_ms=3000),
    pliego.Step("close", L4("Close it again: the spiral lies flat", "Ciérrala de nuevo: la "
                            "espiral queda plana", "Refermez-la : la spirale se couche à plat",
                            "Feche-o de novo: a espiral fica plana"),
                [(gutter, shut)], duration_ms=3000),
]
strip_len = math.pi * N * (2 * r_s + p * N)       # centreline length ≈ ∫ r dθ
print(f"spiral: turns={N:g} pitch={p:.2f}mm strip={w:.2f}mm length~{strip_len:.0f}mm "
      f"centre_from_gutter={c:g}mm initial_gutter={shut:.3f}deg "
      f"papercut_bridge_mm={rep.min_bridge_mm}")

result = pliego.Assembly(
    [card, spiral], joins=joins, initial=initial,
    controls=[pliego.sequence_control(
        label=L4("Open and close", "Abrir y cerrar", "Ouvrir et fermer", "Abrir e fechar"),
        default=1.0)],
    sequence=pliego.Sequence(steps, mode="physical"),
    title="Spiral pop-up",
)
