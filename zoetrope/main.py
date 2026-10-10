"""Zoetrope — sheet-hyperobjects cartridge (Pliego).

A slotted drum on a base disc, with a strip of pictures inside. Spun, and watched through the slits,
the pictures run as a short animation: each slit shows one frame for an instant, the next slit the
next frame, seen from the same place.

* The drum is one strip of `frames` panels with a slit in the upper part of each, a glue tab at
  its end and a small tab under each panel. It is rolled into a `frames`-sided drum: the panel
  lines are scored, each turning 360°/frames, so it rolls into an even polygon, and the initial
  frame poses it exactly. The end tab is glued inside the first panel, and the
  bottom tabs fold inwards and are glued onto the base disc.
* The picture strip has as many panels, a little narrower so that it fits inside, and carries
  `frames` original drawings of one motion cycle (`animation`: a bouncing ball or a flapping
  bird). It is slipped inside, below the slits.

Mode `spin` is the assembled zoetrope (glue joins and the initial frame) with a `rotate` mechanism
about the base's centre on the `spin` control. Mode `make` rolls the flat sheets into shape. The
apparent motion appears in the eye at a few turns a second.
"""

import math

import pliego


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


mode = PARAM(lambda: mode, "spin")                       # noqa: F821
frames = int(round(float(PARAM(lambda: frames, 12))))   # noqa: F821
diameter = float(PARAM(lambda: diameter, 150.0))         # noqa: F821
height = float(PARAM(lambda: height, 80.0))              # noqa: F821
animation = PARAM(lambda: animation, "ball")             # noqa: F821

if mode not in ("spin", "make"):
    raise ValueError(f"zoetrope: unknown mode {mode!r}")
if animation not in ("ball", "bird"):
    raise ValueError(f"zoetrope: unknown animation {animation!r}")
N = int(pliego.clamp(frames, 8, 16))
DIA = pliego.clamp(diameter, 100.0, 300.0)
HD = pliego.clamp(height, 0.35 * DIA, 0.8 * DIA)
RP = DIA / 2.0                                   # the drum polygon's circumradius
PW = 2 * RP * math.sin(math.pi / N)              # drum panel width
INSET = 0.8                                      # the picture strip sits this far inside
RS = RP - INSET / math.cos(math.pi / N)          # its polygon's circumradius
PWS = 2 * RS * math.sin(math.pi / N)             # its panel width
HP = 0.45 * HD                                   # picture strip height
SLIT_W = pliego.clamp(0.08 * PW, 2.5, 5.0)
SLIT_Y0, SLIT_Y1 = HP + 0.08 * HD, 0.92 * HD
GLUE_W, TAB_M = 12.0, 0.12 * PW                  # end tab; side margin of the bottom tabs
TAB_H = min(8.0, 0.25 * PW)                      # bottom tab depth
RB = RP + 12.0                                   # base disc radius
TURN = 360.0 / N
GAP = 0.2                                        # the drum stands this far above the base


def L4(en, es, fr, pt):
    return {"en": en, "es": es, "fr": fr, "pt": pt}


def rolled(u, v, r, pw, sense, lift):
    """World point (y up) of sheet point (u, v) on a strip rolled into the N-gon of circumradius
    r, its panels running one way round (sense +1: front outwards) or the other (−1: inwards).
    Past the last panel (the glue tab) it runs on along the first; below v = 0 (a bottom tab) it is
    folded flat towards the axis."""
    k = int(u // pw) if u < N * pw else N
    k, s = (0, u - N * pw) if k >= N else (max(k, 0), u - max(k, 0) * pw)
    a0, a1 = sense * 2 * math.pi * k / N, sense * 2 * math.pi * (k + 1) / N
    x0, z0, x1, z1 = r * math.cos(a0), r * math.sin(a0), r * math.cos(a1), r * math.sin(a1)
    x, z = x0 + s * (x1 - x0) / pw, z0 + s * (z1 - z0) / pw
    if v < 0:
        m = math.hypot((x0 + x1) / 2, (z0 + z1) / 2)
        x, z, v = x + (x0 + x1) / 2 / m * v, z + (z0 + z1) / 2 / m * v, 0.0
    return (x, v + lift, -z)


for r_, pw_, sense, outwards in ((RP, PW, 1, True), (RS, PWS, -1, False)):
    p0, p1, p2 = (rolled(0.3 * pw_, 0.0, r_, pw_, sense, 0.0), rolled(0.6 * pw_, 0.0, r_, pw_, sense, 0.0),
                  rolled(0.3 * pw_, 10.0, r_, pw_, sense, 0.0))
    e1 = [p1[i] - p0[i] for i in range(3)]
    e2 = [p2[i] - p0[i] for i in range(3)]
    nrm = (e1[1] * e2[2] - e1[2] * e2[1], e1[2] * e2[0] - e1[0] * e2[2], e1[0] * e2[1] - e1[1] * e2[0])
    if (nrm[0] * p0[0] + nrm[2] * p0[2] > 0) != outwards:
        raise ValueError("zoetrope: a rolled strip faces the wrong way")

# ── the drum: panels, slits, end tab, bottom tabs ─────────────────────────────
ring = []
for k in range(N):
    x0, x1 = k * PW, (k + 1) * PW
    ring += [(x0, 0.0), (x0 + TAB_M, 0.0), (x0 + TAB_M + TAB_H, -TAB_H),
             (x1 - TAB_M - TAB_H, -TAB_H), (x1 - TAB_M, 0.0)]
ring += [(N * PW, 0.0), (N * PW + GLUE_W, 0.25 * GLUE_W), (N * PW + GLUE_W, HD - 0.25 * GLUE_W),
         (N * PW, HD), (0.0, HD)]
drum = pliego.Sheet("drum", ring, stock="cardstock-250", grain_deg=90.0,
                    label=L4("Slotted drum", "Tambor ranurado", "Tambour à fentes",
                             "Tambor com fendas"),
                    front="#3d405b", back="#1d1d1f", kinematic="spin" if mode == "spin" else None,
                    placement=pliego.Placement(rotation=(1.0, 0.0, 0.0, 0.0))
                    if mode == "make" else None)
panels = [drum.mountain((k * PW, 0.0), (k * PW, HD), TURN, treatment="score", name="panel")
          for k in range(1, N + 1)]
tabs = [drum.mountain((k * PW + TAB_M, 0.0), ((k + 1) * PW - TAB_M, 0.0), 90.0,
                      treatment="score", name="base-tab") for k in range(N)]
for k in range(N):
    cx = (k + 0.5) * PW
    drum.hole([(cx - SLIT_W / 2, SLIT_Y0), (cx + SLIT_W / 2, SLIT_Y0),
               (cx + SLIT_W / 2, SLIT_Y1), (cx - SLIT_W / 2, SLIT_Y1)])
rep = pliego.papercut.analyze(drum, min_feature_mm=3.0)
if [i for i in rep.issues if i["level"] == "error"]:
    raise ValueError(f"zoetrope: the drum fails the papercut check: {rep.issues}")

# ── the picture strip: one motion cycle, one frame per panel ─────────────────


def frame_svg(k):
    """Frame k of the cycle, drawn in panel k (image coordinates: y down, panel origin top-left)."""
    t, w, ink = k / N, PWS, "#1d1d1f"
    if animation == "ball":
        r = 0.16 * min(w, HP)
        ground = HP - 0.12 * HP
        up = abs(math.cos(math.pi * t))              # 1 at the top, 0 on the ground
        squash = max(0.0, 1.0 - up / 0.18)           # squashed only near the ground
        rx, ry = r * (1 + 0.3 * squash), r * (1 - 0.3 * squash)
        cy = ground - ry - up * (ground - 2.2 * r - 0.08 * HP)
        return (f"<ellipse cx='{w / 2:.2f}' cy='{ground:.2f}' rx='{r * (1.2 - 0.6 * up):.2f}' "
                f"ry='{r * 0.25:.2f}' fill='#00000033'/>"
                f"<line x1='0' y1='{ground:.2f}' x2='{w:.2f}' y2='{ground:.2f}' stroke='{ink}' "
                f"stroke-width='0.6'/><ellipse cx='{w / 2:.2f}' cy='{cy:.2f}' rx='{rx:.2f}' "
                f"ry='{ry:.2f}' fill='#e4572e' stroke='{ink}' stroke-width='0.6'/>")
    s = 0.36 * min(w, HP)                             # bird: wings beat once per cycle
    cx, cy = w / 2, HP / 2 + 0.06 * HP * math.cos(2 * math.pi * t)
    lift = 0.9 * s * math.cos(2 * math.pi * t)
    wing = (f"M{cx - 0.1 * s:.2f},{cy:.2f} Q{cx - 0.7 * s:.2f},{cy - lift:.2f} "
            f"{cx - 1.3 * s:.2f},{cy - 0.6 * lift:.2f} M{cx + 0.1 * s:.2f},{cy:.2f} "
            f"Q{cx + 0.7 * s:.2f},{cy - lift:.2f} {cx + 1.3 * s:.2f},{cy - 0.6 * lift:.2f}")
    return (f"<ellipse cx='{cx:.2f}' cy='{cy:.2f}' rx='{0.45 * s:.2f}' ry='{0.22 * s:.2f}' "
            f"fill='#2e86ab' stroke='{ink}' stroke-width='0.6'/><path d='{wing}' fill='none' "
            f"stroke='{ink}' stroke-width='{0.12 * s:.2f}' stroke-linecap='round'/>")


svg = [f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {N * PWS:.2f} {HP:.2f}'>"
       f"<rect width='{N * PWS:.2f}' height='{HP:.2f}' fill='#fdfaf3'/>"]
svg += [f"<g transform='translate({k * PWS:.2f},0)'>{frame_svg(k)}</g>" for k in range(N)]
art = "".join(svg) + "</svg>"
for a, b in (("%", "%25"), ("#", "%23"), ("<", "%3C"), (">", "%3E"), (" ", "%20"), ("'", "%27")):
    art = art.replace(a, b)
strip = pliego.Sheet("pictures", pliego.rectangle(N * PWS, HP), stock="copy-80", grain_deg=0.0,
                     label=L4("Picture strip", "Tira de dibujos", "Bande d'images",
                              "Tira de desenhos"),
                     front=pliego.Face(None, "data:image/svg+xml;charset=utf-8," + art),
                     back="#f6f3ec", kinematic="spin" if mode == "spin" else None)
strip_panels = [strip.valley((k * PWS, 0.0), (k * PWS, HP), TURN, treatment="score",
                             name="frame") for k in range(1, N)]

base = pliego.Sheet("base", pliego.circle((RB, RB), RB, 96), stock="cardstock-300",
                    grain_deg=90.0, label=L4("Base disc", "Disco de base", "Disque de base",
                                             "Disco de base"), front="#f3a712", kinematic="spin" if mode == "spin" else None,
                    placement=pliego.Placement(origin=(-RB, 0.0, RB)) if mode == "spin" else None)
for a, b in (((RB - 3, RB), (RB + 3, RB)), ((RB, RB - 3), (RB, RB + 3))):
    base.halfcut([a, b], name="spindle-mark")

# ── programs ──────────────────────────────────────────────────────────────────
SPIN = L4("Spin the drum", "Girar el tambor", "Faire tourner le tambour", "Girar o tambor")
if mode == "make":
    steps = [
        pliego.Step("tabs", L4("Fold the base tabs back", "Dobla hacia atrás las pestañas de la base",
                               "Replier les languettes du bas", "Dobre para trás as abas da base"),
                    [(m, -90.0) for m in tabs], duration_ms=1200),
        pliego.Step("roll-drum", L4("Roll the drum and glue the end tab inside",
                                    "Enrolla el tambor y pega la pestaña del extremo por dentro",
                                    "Rouler le tambour et coller la languette à l'intérieur",
                                    "Enrole o tambor e cole a aba da ponta por dentro"),
                    [(m, -TURN) for m in panels], duration_ms=2500),
        pliego.Step("roll-pictures", L4("Roll the picture strip, pictures inside",
                                        "Enrolla la tira de dibujos, con los dibujos hacia dentro",
                                        "Rouler la bande d'images, images à l'intérieur",
                                        "Enrole a tira de desenhos, com os desenhos para dentro"),
                    [(m, TURN) for m in strip_panels], duration_ms=2500)]
    result = pliego.Assembly([drum, strip, base], controls=[pliego.sequence_control(
        label=L4("Make it", "Armarlo", "Le fabriquer", "Montá-lo"))],
        sequence=pliego.Sequence(steps, mode="kinematic"), title="Zoetrope")
else:
    def to_base(w):
        return (w[0] + RB, RB - w[2])

    joins = [pliego.glue("end-tab", drum, [(N * PW + 1.0, 0.25 * GLUE_W + 1.0),
                                          (N * PW + GLUE_W - 1.0, 0.25 * GLUE_W + 1.0),
                                          (N * PW + GLUE_W - 1.0, HD - 0.25 * GLUE_W - 1.0),
                                          (N * PW + 1.0, HD - 0.25 * GLUE_W - 1.0)],
                         drum, (1.0, 0.0, 0.0, 1.0, -N * PW, 0.0), side="back")]
    for k in range(N):
        x0, x1 = k * PW + TAB_M + TAB_H, (k + 1) * PW - TAB_M - TAB_H
        reg = [(x0, -1.0), (x1, -1.0), (x1, -TAB_H + 1.0), (x0, -TAB_H + 1.0)]
        src = [(x0, -1.0), (x1, -1.0), (x0, -TAB_H + 1.0)]
        dst = [to_base(rolled(p[0], p[1], RP, PW, 1, GAP)) for p in src]
        (sx0, sy0), (sx1, sy1), (sx2, sy2) = src
        det = (sx1 - sx0) * (sy2 - sy0) - (sx2 - sx0) * (sy1 - sy0)
        row = []
        for q0, q1, q2 in ((dst[0][0], dst[1][0], dst[2][0]), (dst[0][1], dst[1][1], dst[2][1])):
            a = ((q1 - q0) * (sy2 - sy0) - (q2 - q0) * (sy1 - sy0)) / det
            b = ((sx1 - sx0) * (q2 - q0) - (sx2 - sx0) * (q1 - q0)) / det
            row.append((a, b, q0 - a * sx0 - b * sy0))
        joins.append(pliego.glue(f"base-tab-{k + 1}", drum, reg, base,
                                 (row[0][0], row[0][1], row[1][0], row[1][1], row[0][2],
                                  row[1][2]), side="front"))

    def initial(sheet_id, uv):
        if sheet_id == "drum":
            return rolled(uv[0], uv[1], RP, PW, 1, GAP)
        if sheet_id == "pictures":
            return rolled(uv[0], uv[1], RS, PWS, -1, GAP + 0.3)
        return (uv[0] - RB, 0.0, RB - uv[1])

    result = pliego.Assembly(
        [drum, strip, base], joins=joins, initial=initial,
        mechanisms=[pliego.rotate("spin", (base, (RB, RB)), "spin", [base, drum, strip])],
        controls=[pliego.angle_control("spin", SPIN, default=0.0, min=0.0, max=360.0)],
        title="Zoetrope")
print(f"zoetrope: mode={mode} frames={N} diameter={DIA:g}mm height={HD:g}mm panel={PW:.1f}mm "
      f"slit={SLIT_W:.1f}x{SLIT_Y1 - SLIT_Y0:.1f}mm animation={animation}")
