"""Paper automaton — sheet-hyperobjects cartridge (Pliego).

A cam-and-crank automaton box made of card (an original MADFAM design). Turning the handle turns a
shaft; a cam on the shaft lifts a follower that rises through a slot in the box's lid, and a bird
on top of the follower bobs. Two modes:

* `automaton` — the assembled box. The cam, the shaft and the handle are kinematic sheets turned by
  the `crank` control (two `rotate` mechanisms and a `hinge` about the shaft's axis). The follower's
  height is computed from the cam profile as a function of the crank angle, for a pointed
  (knife-edge) follower straight above the shaft.
* `nets` — every part flat as a cut-and-score net (the box, three cam layers, two handle layers,
  two follower layers, two shaft collars), and a fold program that folds the box.

Cam profiles (`profile`): `snail` (an Archimedean spiral with a drop: the follower rises steadily
for a whole turn, then falls), `eccentric` (an off-centre disc: a smooth rise and fall) and `egg`
(a round cam with one lobe: a long rest and a quick bob). With the snail the follower's height is
linear in the crank angle, so a `translate` mechanism on the same control carries it exactly in
the preview. The eccentric and egg lifts are periodic in the crank angle, and a preview mechanism
moves its sheet linearly in its control, so no mechanism can carry those followers exactly: they
are physical sheets that ride the cam under gravity in the physics engine, start at the top of the
stroke (where the cam holds them at crank 0), and `target:crank-…` frames record the exact lift.
"""

import math

import pliego


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


mode = PARAM(lambda: mode, "automaton")                        # noqa: F821
profile = PARAM(lambda: profile, "snail")                      # noqa: F821
lift = float(PARAM(lambda: lift, 12.0))                        # noqa: F821
handle_length = float(PARAM(lambda: handle_length, 30.0))      # noqa: F821
box_height = float(PARAM(lambda: box_height, 85.0))            # noqa: F821

if mode not in ("automaton", "nets"):
    raise ValueError(f"paper-automaton: unknown mode {mode!r}")
if profile not in ("snail", "eccentric", "egg"):
    raise ValueError(f"paper-automaton: unknown profile {profile!r}")

LIFT = pliego.clamp(lift, 6.0, 14.0)
HL = pliego.clamp(handle_length, 20.0, 45.0)
WB, DB = 90.0, 70.0                         # box width (x) and depth (z)
HB = pliego.clamp(box_height, 70.0, 120.0)  # box height (y)
YS = 32.0                                   # the shaft's height in the box
R_BASE = 14.0                               # the cam's smallest radius
WF = 8.0                                    # follower width
MARGIN = 10.0                               # window frame
TAB = 10.0                                  # glue tab
TUCK = 15.0                                 # lid's tuck flap
SHAFT_D = 4.0                               # bamboo skewer (hardware): holes are a little wider
SEG = 144
BOX, CARD = "cardstock-300", "cardstock-250"
FLAT_UP = (math.sin(math.pi / 4.0), 0.0, 0.0, math.cos(math.pi / 4.0))   # local (u, v) → (x, y)


def L4(en, es, fr, pt):
    return {"en": en, "es": es, "fr": fr, "pt": pt}


def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def circle(c, r, n=32):
    return pliego.circle(c, r, n)


def pierce(sheet, at, size=2.0, name="pierce"):
    x, y = at
    sheet.halfcut([(x - size, y), (x + size, y)], name=name)
    sheet.halfcut([(x, y - size), (x, y + size)], name=name)


# ── the cam: radius along local direction φ (deg); +v (φ = 90°) points up at crank 0 ───────────

def cam_radius(phi):
    if profile == "snail":     # rises with the crank: r grows as φ falls from 90°
        return R_BASE + LIFT * ((90.0 - phi) % 360.0) / 360.0
    if profile == "eccentric":
        e, rc = LIFT / 2.0, R_BASE + LIFT / 2.0
        s, c = math.sin(math.radians(phi)), math.cos(math.radians(phi))
        return e * s + math.sqrt(rc * rc - (e * c) ** 2)
    lobe = (1.0 + math.cos(math.radians(phi - 90.0))) / 2.0     # egg: one end longer
    return R_BASE + LIFT * lobe ** 3


def lift_at(theta):
    """Follower height above the shaft at crank angle θ (the cam turns counter-clockwise seen
    from the front, so the point under the follower is at φ = 90° − θ)."""
    if profile == "snail":
        return R_BASE + LIFT * (theta % 360.0) / 360.0
    return cam_radius(90.0 - theta)


def cam_outline():
    if profile == "snail":     # from just past the drop, round to the drop
        pts = []
        for k in range(SEG + 1):
            phi = 90.0 - 360.0 * k / SEG
            r = R_BASE + LIFT * k / SEG
            pts.append((r * math.cos(math.radians(phi)), r * math.sin(math.radians(phi))))
        return pts[::-1]       # counter-clockwise
    return [(cam_radius(360.0 * k / SEG) * math.cos(math.radians(360.0 * k / SEG)),
             cam_radius(360.0 * k / SEG) * math.sin(math.radians(360.0 * k / SEG)))
            for k in range(SEG)]


lifts = [lift_at(t) for t in range(360)]
H_MIN, H_MAX = min(lifts), max(lifts)
if R_BASE + LIFT > YS - 4.0:
    raise ValueError("paper-automaton: the cam does not fit under the shaft")
pressure = 0.0
for t in range(0, 359):        # pressure angle of a knife-edge follower: tan α = (dh/dθ) / r
    if profile == "snail" and t == 359:
        continue
    dh = (lifts[t + 1] - lifts[t]) / math.radians(1.0)
    pressure = max(pressure, math.degrees(math.atan2(abs(dh), lifts[t])))
if pressure > 35.0:
    raise ValueError(f"paper-automaton: the cam's pressure angle reaches {pressure:.0f}°; "
                     "lower the lift")

# ── the follower: a strip with a pointed foot and an original bird on top ──────────────────────

L_ROD = (HB + 12.0) - (YS + H_MIN)         # the rod clears the lid by 12 mm at its lowest


def bird_outline():
    """Original silhouette: an elliptical body, a round head with a beak, a tail; star-shaped
    about the body's centre (radial maximum of the parts). Returns points in rod-top coordinates
    from the right of the neck round to the left of it (counter-clockwise)."""
    bw, bh = 15.0, 9.0                     # body semi-axes
    cx, cy = 0.0, bh                       # body centre (the body sits on the rod)
    head_c, head_r = (-12.0, bh + 9.0), 6.0
    beak = [(-17.5, bh + 10.5), (-25.0, bh + 8.5), (-17.5, bh + 6.5)]
    tail = [(12.0, bh + 3.0), (24.0, bh + 12.0), (22.0, bh + 4.0), (13.0, bh - 3.0)]

    def ray_poly(dx, dy, poly):
        best = 0.0
        for (x0, y0), (x1, y1) in zip(poly, poly[1:] + poly[:1]):
            ex, ey = x1 - x0, y1 - y0
            den = dx * ey - dy * ex
            if abs(den) < 1e-12:
                continue
            t = ((x0 - cx) * ey - (y0 - cy) * ex) / den
            s = ((x0 - cx) * dy - (y0 - cy) * dx) / den
            if t > 0 and 0.0 <= s <= 1.0:
                best = max(best, t)
        return best

    def radius(a):
        dx, dy = math.cos(a), math.sin(a)
        r = 1.0 / math.sqrt((dx / bw) ** 2 + (dy / bh) ** 2)
        hx, hy = head_c[0] - cx, head_c[1] - cy
        b = dx * hx + dy * hy
        disc = b * b - (hx * hx + hy * hy - head_r * head_r)
        if disc >= 0.0 and b + math.sqrt(disc) > 0.0:
            r = max(r, b + math.sqrt(disc))
        return max(r, ray_poly(dx, dy, beak), ray_poly(dx, dy, tail))

    # where the outline crosses the neck's edges (x = ±WF/2) at the bottom
    def cross(sign):
        lo, hi = -math.pi / 2.0, -math.pi / 2.0 + sign * 1.2
        for _ in range(60):
            mid = (lo + hi) / 2.0
            if abs(radius(mid) * math.cos(mid)) < WF / 2.0:
                lo = mid
            else:
                hi = mid
        return lo
    a0, a1 = cross(1.0), cross(-1.0) + 2.0 * math.pi
    n = 180
    return [(cx + radius(a0 + (a1 - a0) * k / n) * math.cos(a0 + (a1 - a0) * k / n),
             cy + radius(a0 + (a1 - a0) * k / n) * math.sin(a0 + (a1 - a0) * k / n))
            for k in range(n + 1)]


def follower_sheet(sid, label, kinematic=None):
    top = bird_outline()
    ring = [(0.0, -L_ROD), (WF / 2.0, -L_ROD + 4.0)] + top + [(-WF / 2.0, -L_ROD + 4.0)]
    return pliego.Sheet(sid, ring, stock=CARD, grain_deg=90.0, label=label, kinematic=kinematic)


# ── the box: front, right, back, left walls and a glue tab in a row; the lid on the back wall ──

def box_sheet(placement):
    u_r, u_b, u_l, u_t = WB, WB + DB, 2.0 * WB + DB, 2.0 * WB + 2.0 * DB
    ring = [(0.0, 0.0), (u_t, 0.0), (u_t + TAB, 3.0), (u_t + TAB, HB - 3.0), (u_t, HB),
            (u_l, HB), (u_l, HB + DB), (u_l - 3.0, HB + DB + TUCK), (u_b + 3.0, HB + DB + TUCK),
            (u_b, HB + DB), (u_b, HB), (0.0, HB)]
    sh = pliego.Sheet("box", ring, stock=BOX, grain_deg=90.0,
                      label=L4("Box", "Caja", "Boîte", "Caixa"), placement=placement)
    walls = [sh.mountain((u, 0.0), (u, HB), angle=90.0, treatment="score", name="corner",
                         rest=90.0) for u in (u_r, u_b, u_l)]
    tab = sh.mountain((u_t, 0.0), (u_t, HB), angle=90.0, treatment="score", name="glue-tab",
                      rest=90.0)
    lid = sh.mountain((u_b, HB), (u_l, HB), angle=90.0, treatment="score", name="lid",
                      rest=90.0)
    tuck = sh.mountain((u_b, HB + DB), (u_l, HB + DB), angle=90.0, treatment="score",
                       name="tuck", rest=90.0)
    hole = SHAFT_D / 2.0 + 0.5
    sh.hole(circle((WB / 2.0, YS), hole))                    # front wall: the shaft
    sh.hole(circle((u_b + WB / 2.0, YS), hole))              # back wall
    for u0 in (u_r, u_l):                                    # side windows: the cam shows
        sh.hole(rect(u0 + MARGIN, MARGIN, u0 + DB - MARGIN, HB - MARGIN))
    uc = u_b + WB / 2.0                                      # the lid's slot for the follower
    sh.hole(rect(uc - WF / 2.0 - 0.5, HB + DB / 2.0 - 0.8, uc + WF / 2.0 + 0.5,
                 HB + DB / 2.0 + 0.8))
    return sh, walls, tab, lid, tuck, u_t


def disc_with_pierce(sid, outline, label, kinematic=None, placement=None):
    sh = pliego.Sheet(sid, outline, stock=CARD, grain_deg=90.0, label=label,
                      kinematic=kinematic, placement=placement)
    pierce(sh, (0.0, 0.0), name="shaft")
    return sh


def handle_outline():
    r = 6.0
    pts = []
    for k in range(17):
        t = math.radians(-90.0 + 180.0 * k / 16)
        pts.append((HL + r * math.cos(t), r * math.sin(t)))
    for k in range(17):
        t = math.radians(90.0 + 180.0 * k / 16)
        pts.append((r * math.cos(t), r * math.sin(t)))
    return pts


CAM_L = L4("Cam", "Leva", "Came", "Came")
HANDLE_L = L4("Handle", "Manivela", "Manivelle", "Manivela")
FOLLOWER_L = L4("Follower with bird", "Seguidor con pájaro", "Poussoir et oiseau",
                "Seguidor com pássaro")
sheets, joins, mechanisms, controls, sequence, initial, targets = [], [], [], [], None, None, {}

if mode == "automaton":
    box, walls, tab, lid, tuck, u_t = box_sheet(
        pliego.Placement(origin=(-WB / 2.0, 0.0, DB / 2.0), rotation=FLAT_UP))
    joins.append(pliego.glue("box-tab", box, rect(u_t + 0.5, 3.5, u_t + TAB - 0.5, HB - 3.5),
                             box, (1.0, 0.0, 0.0, 1.0, -u_t, 0.0), side="back"))
    box_pose = {"angles": {m: -90.0 for m in walls + [tab, lid, tuck]}, "root": (5.0, 5.0)}
    initial = {"box": box_pose}
    cam = disc_with_pierce("cam", cam_outline(), CAM_L, "turn-cam",
                           pliego.Placement(origin=(0.0, YS, 0.0), rotation=FLAT_UP))
    handle = disc_with_pierce("handle", handle_outline(), HANDLE_L, "turn-handle",
                              pliego.Placement(origin=(0.0, YS, DB / 2.0 + 6.0),
                                               rotation=FLAT_UP))
    pierce(handle, (HL, 0.0), name="knob")
    shaft_len = DB + 22.0
    shaft = pliego.Sheet("shaft", rect(0.0, 0.0, SHAFT_D, shaft_len), stock=CARD, grain_deg=90.0,
                         label=L4("Shaft (skewer)", "Eje (brocheta)", "Axe (pique)",
                                  "Eixo (espeto)"), kinematic="turn-shaft",
                         placement=pliego.Placement(origin=(-SHAFT_D / 2.0, YS,
                                                            DB / 2.0 + 10.0)))
    follower = follower_sheet("follower", FOLLOWER_L,
                              "lift-follower" if profile == "snail" else None)
    y_top = H_MIN if profile == "snail" else H_MAX      # where the follower starts
    follower.placement = pliego.Placement(origin=(0.0, YS + y_top + L_ROD, 0.0),
                                          rotation=FLAT_UP)
    mechanisms += [pliego.rotate("turn-cam", (cam, (0.0, 0.0)), "crank", [cam]),
                   pliego.rotate("turn-handle", (handle, (0.0, 0.0)), "crank", [handle]),
                   pliego.hinge("turn-shaft", (0.0, YS, 0.0), (0.0, 0.0, 1.0), "crank",
                                [shaft])]
    if profile == "snail":
        mechanisms.append(pliego.translate("lift-follower", "crank", (0.0, 1.0, 0.0), LIFT,
                                           [follower]))
    controls.append(pliego.angle_control("crank", L4("Turn the handle", "Gira la manivela",
                                                     "Tourner la manivelle", "Gire a manivela"),
                                         default=0.0, min=0.0, max=360.0))
    sheets += [box, shaft, cam, handle, follower]

    def turned(theta, z0, uv):
        c, s = math.cos(math.radians(theta)), math.sin(math.radians(theta))
        return (uv[0] * c - uv[1] * s, YS + uv[0] * s + uv[1] * c, z0)

    for k in range(0, 360, 30):
        h = lift_at(k)

        def fn_cam(sid, uv, k=k):
            return turned(k, 0.0, uv)

        def fn_handle(sid, uv, k=k):
            return turned(k, DB / 2.0 + 6.0, uv)

        def fn_shaft(sid, uv, k=k):
            x, z = uv[0] - SHAFT_D / 2.0, -uv[1] + DB / 2.0 + 10.0
            c, s = math.cos(math.radians(k)), math.sin(math.radians(k))
            return (x * c, YS + x * s, z)

        def fn_follower(sid, uv, h=h):
            return (uv[0], YS + h + L_ROD + uv[1], 0.0)

        targets[f"crank-{k:03d}"] = {"box": box_pose, "cam": fn_cam, "handle": fn_handle,
                                     "shaft": fn_shaft, "follower": fn_follower}
    summary = (f"lift={H_MIN - R_BASE:.1f}..{H_MAX - R_BASE:.1f}mm over the base circle "
               f"pressure_max={pressure:.1f}deg follower="
               f"{'translate (exact)' if profile == 'snail' else 'physical (rides the cam)'}")
else:
    box, walls, tab, lid, tuck, u_t = box_sheet(
        pliego.Placement(rotation=(1.0, 0.0, 0.0, 0.0)))       # face down: folds come up
    sheets.append(box)
    for k in range(3):
        sheets.append(disc_with_pierce(f"cam-{k + 1}", cam_outline(),
                                       L4(f"Cam, layer {k + 1}", f"Leva, capa {k + 1}",
                                          f"Came, couche {k + 1}", f"Came, camada {k + 1}")))
    for k in range(2):
        h = disc_with_pierce(f"handle-{k + 1}", handle_outline(),
                             L4(f"Handle, layer {k + 1}", f"Manivela, capa {k + 1}",
                                f"Manivelle, couche {k + 1}", f"Manivela, camada {k + 1}"))
        pierce(h, (HL, 0.0), name="knob")
        sheets.append(h)
    for k in range(2):
        sheets.append(follower_sheet(f"follower-{k + 1}",
                                     L4(f"Follower, layer {k + 1}", f"Seguidor, capa {k + 1}",
                                        f"Poussoir, couche {k + 1}",
                                        f"Seguidor, camada {k + 1}")))
    for k in range(2):
        sheets.append(disc_with_pierce(f"collar-{k + 1}", circle((0.0, 0.0), 7.0),
                                       L4(f"Shaft collar {k + 1}", f"Tope del eje {k + 1}",
                                          f"Bague d'arrêt {k + 1}", f"Batente do eixo {k + 1}")))
    steps = [
        pliego.Step("fold-walls", L4("Fold the four walls into a ring",
                                     "Dobla las cuatro paredes en un anillo",
                                     "Plier les quatre parois en anneau",
                                     "Dobre as quatro paredes num anel"),
                    [(m, -90.0) for m in walls], duration_ms=2000),
        pliego.Step("glue-tab", L4("Fold the tab inside and glue it",
                                   "Dobla la pestaña hacia dentro y pégala",
                                   "Rabattre la languette à l'intérieur et la coller",
                                   "Dobre a aba para dentro e cole-a"),
                    [(tab, -90.0)], duration_ms=1200),
        pliego.Step("close-lid", L4("Close the lid and tuck its flap",
                                    "Cierra la tapa y mete la solapa",
                                    "Fermer le couvercle et rentrer le rabat",
                                    "Feche a tampa e encaixe a aba"),
                    [(lid, -90.0), (tuck, -90.0)], duration_ms=1800),
    ]
    # lay the parts out side by side on the table, after the box net
    cursor = 2.0 * WB + 2.0 * DB + TAB + 15.0
    for sh in sheets[1:]:
        xs = [p.x for p in sh.outline]
        ys = [p.y for p in sh.outline]
        sh.placement = pliego.Placement(origin=(cursor - min(xs), 0.0, -15.0 + max(ys)))
        cursor += max(xs) - min(xs) + 10.0
    sequence = pliego.Sequence(steps, mode="physical")
    controls.append(pliego.sequence_control(label=L4("Fold the box", "Doblar la caja",
                                                     "Plier la boîte", "Dobrar a caixa")))
    summary = f"parts={len(sheets)}"

print(f"paper-automaton: mode={mode} profile={profile} box={WB:g}x{DB:g}x{HB:g}mm "
      f"shaft_y={YS:g}mm rod={L_ROD:.1f}mm {summary}")

result = pliego.Assembly(sheets, joins=joins, mechanisms=mechanisms, controls=controls,
                         sequence=sequence, initial=initial, targets=targets,
                         title="Paper automaton")
