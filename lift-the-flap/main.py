"""Lift-the-flap — sheet-hyperobjects cartridge (Pliego).

A flap over a page: lift it and what was under it shows. Two modes, one geometry:

* `hinged` — the flap is a rigid board turned by a `hinge` mechanism about its hinge edge (the
  `lift` angle control, 0–180°). The attachment itself (in a board book, a strip of tape or cloth)
  is the mechanism's axis and is not a sheet of the document, so the preview can drive it.
* `glued-tab` — the paper construction: the flap and a glue tab are one piece with a scored hinge
  between them, and the tab is glued to the page (`glue` join). The fold program lifts the flap and
  lowers it again. The piece is posed from its tab, so the preview animates it too.

Styles: `rectangle`, `rounded` (rounded free corners), `arch` (a round-ended flap) and `doors` (two
flaps hinged on opposite sides that meet in the middle). A single flap is hinged along its `top` or
its `left` edge. Every flap is laid out in its own frame (u from the hinge to the free edge, v
across it) and placed on the page by a rotation, so the hinge is always the same line in the
flap's frame.
"""

import math

import pliego


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


mode = PARAM(lambda: mode, "hinged")                        # noqa: F821
style = PARAM(lambda: style, "rounded")                     # noqa: F821
hinge_side = PARAM(lambda: hinge_side, "top")               # noqa: F821
page_width = float(PARAM(lambda: page_width, 200.0))        # noqa: F821
page_height = float(PARAM(lambda: page_height, 200.0))      # noqa: F821
flap_width = float(PARAM(lambda: flap_width, 90.0))         # noqa: F821
flap_height = float(PARAM(lambda: flap_height, 70.0))       # noqa: F821
flap_x = float(PARAM(lambda: flap_x, 0.5))                  # noqa: F821
flap_y = float(PARAM(lambda: flap_y, 0.5))                  # noqa: F821
tab_width = float(PARAM(lambda: tab_width, 10.0))           # noqa: F821
lift_to = float(PARAM(lambda: lift_to, 150.0))              # noqa: F821

if mode not in ("hinged", "glued-tab"):
    raise ValueError(f"lift-the-flap: unknown mode {mode!r}")
if style not in ("rectangle", "rounded", "arch", "doors"):
    raise ValueError(f"lift-the-flap: unknown style {style!r}")
if hinge_side not in ("top", "left"):
    raise ValueError(f"lift-the-flap: unknown hinge side {hinge_side!r}")

W = pliego.clamp(page_width, 100.0, 300.0)
H = pliego.clamp(page_height, 100.0, 300.0)
fw = pliego.clamp(flap_width, 20.0, 260.0)
fh = pliego.clamp(flap_height, 20.0, 260.0)
t = pliego.clamp(tab_width, 6.0, 20.0) if mode == "glued-tab" else 0.0
lift = pliego.clamp(lift_to, 30.0, 175.0)
PAGE_STOCK, FLAP_STOCK = "cardstock-300", "cardstock-250"
LIFT = 0.2           # the flap lies this far above the page (< collision thickness)
DOOR_GAP = 1.0       # the two doors stop this far apart
MARGIN = 6.0
INSET = 0.5


def L4(en, es, fr, pt):
    return {"en": en, "es": es, "fr": fr, "pt": pt}


if fw + 2 * (MARGIN + t) > W or fh + 2 * (MARGIN + t) > H:
    raise ValueError(f"lift-the-flap: a {fw:g} × {fh:g} mm flap with its tabs does not fit the "
                     f"{W:g} × {H:g} mm page")
x0 = MARGIN + t + flap_x * (W - fw - 2 * (MARGIN + t))      # the covered window, page frame
y0 = MARGIN + t + flap_y * (H - fh - 2 * (MARGIN + t))

# ── flaps: (id, length u, width v, page map) — page point = (a·u + b·v + tx, c·u + d·v + ty) ──
# u runs from the hinge to the free edge (the tab, in glued-tab mode, is u ∈ [−t, 0]).

if style == "doors":
    half = fw / 2.0 - DOOR_GAP / 2.0
    flaps = [
        ("door-left", half, fh, (1.0, 0.0, 0.0, 1.0, x0, y0), "left"),
        ("door-right", half, fh, (-1.0, 0.0, 0.0, -1.0, x0 + fw, y0 + fh), "right"),
    ]
elif hinge_side == "top":
    flaps = [("flap", fh, fw, (0.0, 1.0, -1.0, 0.0, x0, y0 + fh), "top")]
else:
    flaps = [("flap", fw, fh, (1.0, 0.0, 0.0, 1.0, x0, y0), "left")]


def flap_outline(length, width):
    """The flap in its own frame: hinge on u = 0 (from v = 0 to width), free edge at u = length."""
    if style == "arch":
        r = width / 2.0
        if length < r + 5.0:
            raise ValueError("lift-the-flap: an arch flap must be longer than half its width "
                             "+ 5 mm")
        arc = [(length - r + r * math.sin(math.pi * k / 24), r - r * math.cos(math.pi * k / 24))
               for k in range(25)]
        return [(0.0, 0.0)] + arc + [(0.0, width)]
    if style == "rounded":
        r = min(10.0, width / 4.0, length / 4.0)
        q = [math.pi / 2 * k / 8 for k in range(9)]
        c1 = [(length - r + r * math.sin(a), r - r * math.cos(a)) for a in q]
        c2 = [(length - r + r * math.cos(a), width - r + r * math.sin(a)) for a in q]
        return [(0.0, 0.0)] + c1 + c2 + [(0.0, width)]
    return [(0.0, 0.0), (length, 0.0), (length, width), (0.0, width)]


def quat_y(deg):
    h = math.radians(deg) / 2.0
    return (0.0, math.sin(h), 0.0, math.cos(h))


def placement_of(m):
    """The placement mapping the flap frame (u, v) onto its page position, LIFT above the page:
    sheet-local (u, v) → un-placed (u, 0, −v) → rotation about +Y → + origin."""
    a, b, c, d, tx, ty = m
    # un-placed (u, 0, -v) must go to world (a·u + b·v + tx, LIFT, −(c·u + d·v + ty)),
    # a rotation about +Y by θ with cos θ = a, sin θ = c (the maps used here are rotations)
    theta = math.degrees(math.atan2(c, a))
    return pliego.Placement(origin=(tx, LIFT, -ty), rotation=quat_y(theta))


page = pliego.Sheet("page", [(0, 0), (W, 0), (W, H), (0, H)], stock=PAGE_STOCK, grain_deg=90.0,
                    label=L4("Page", "Página", "Page", "Página"))
page.label_edge("page-edge", (0, 0), (W, 0))

sheets, joins, mechanisms, hinges = [page], [], [], []
for fid, length, width, m, _side in flaps:
    ring = [(u + t, v) for u, v in flap_outline(length, width)]
    if t > 0:
        ring = [(0.0, 0.0)] + ring + [(0.0, width)]
    a, b, c, d, tx, ty = m
    # with a tab the sheet's frame starts t before the hinge: shift the map by −t along u
    tm = (a, b, c, d, tx - a * t, ty - c * t)
    label = {"flap": L4("Flap", "Solapa", "Rabat", "Aba"),
             "door-left": L4("Left door", "Puerta izquierda", "Volet gauche", "Porta esquerda"),
             "door-right": L4("Right door", "Puerta derecha", "Volet droit", "Porta direita")}[fid]
    sh = pliego.Sheet(fid, ring, stock=FLAP_STOCK, grain_deg=0.0, label=label,
                      placement=placement_of(tm),
                      kinematic="lift-" + fid if mode == "hinged" else None)
    sh.label_edge("hinge", (t, 0.0), (t, width))
    if mode == "glued-tab":
        crease = sh.valley((t, 0.0), (t, width), treatment="score", name="hinge", label=L4(
            "Hinge (scored)", "Bisagra (hendida)", "Charnière (rainée)", "Dobradiça (vincada)"))
        region = [(INSET, INSET), (t - INSET, INSET), (t - INSET, width - INSET),
                  (INSET, width - INSET)]
        joins.append(pliego.glue(f"{fid}-tab", sh, region, page, tm, "front"))
        sh.label_edge("glue-tab", (0.0, 0.0), (0.0, width))
        hinges.append(crease)
    else:
        # the hinge axis on the page: from the hinge's v = 0 end to its v = width end
        p0 = (tx, LIFT, -ty)
        p1 = (tx + b * width, LIFT, -(ty + d * width))
        # right-hand rule: turning about p1 → p0 lifts the flap off the page (+Y)
        direction = (p0[0] - p1[0], 0.0, p0[2] - p1[2])
        mechanisms.append(pliego.hinge("lift-" + fid, p0, direction, "lift", [fid], rest=0.0))
    sheets.append(sh)

controls = []
sequence = None
if mode == "hinged":
    controls.append(pliego.angle_control("lift", L4("Lift the flap", "Levantar la solapa",
                                                     "Soulever le rabat", "Levantar a aba"),
                                         default=110.0, min=0.0, max=180.0))
else:
    n = 8
    steps = []
    for k in range(1, n + 1):
        steps.append(pliego.Step(f"lift-{k}", L4(f"Lift the flap ({k}/{n})",
                                                 f"Levanta la solapa ({k}/{n})",
                                                 f"Soulevez le rabat ({k}/{n})",
                                                 f"Levante a aba ({k}/{n})"),
                                 [(cr, lift * k / n) for cr in hinges], duration_ms=250))
    for k in range(1, n + 1):
        steps.append(pliego.Step(f"lower-{k}", L4(f"Let it down again ({k}/{n})",
                                                  f"Bájala otra vez ({k}/{n})",
                                                  f"Rabattez-le ({k}/{n})",
                                                  f"Abaixe-a de novo ({k}/{n})"),
                                 [(cr, lift * (n - k) / n) for cr in hinges], duration_ms=250))
    sequence = pliego.Sequence(steps, mode="kinematic")
    controls.append(pliego.sequence_control(
        label=L4("Lift and lower", "Levantar y bajar", "Soulever et rabattre",
                 "Levantar e abaixar"), default=float(n)))

print(f"flap: mode={mode} style={style} hinge={'both sides' if style == 'doors' else hinge_side} "
      f"flaps={len(flaps)} window={fw:g}x{fh:g}mm at ({x0:.1f}, {y0:.1f})")

result = pliego.Assembly(sheets, joins=joins, mechanisms=mechanisms, controls=controls,
                         sequence=sequence, title="Lift-the-flap")
