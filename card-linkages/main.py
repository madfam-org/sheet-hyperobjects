"""Card linkages — sheet-hyperobjects cartridge (Pliego).

Levers and linkages in card. Three modes:

* `four-bar` — a four-bar linkage (a double rocker) folded from one strip of card standing on a
  base: a post, the input link, the coupler, the output link and a second post, joined by score
  lines (living hinges, axes vertical). The posts' feet are glued to the base, which is the fixed
  link. The program swings the input link through its range; every key pose is solved in closed
  form (circle–circle intersection), so the strip closes on the second post at every key.
* `extender` — a scissor (lazy-tongs) extender folded as a rhombus chain from one strip: a top
  zig-zag and a bottom zig-zag that meet tip to tip at the crossing points, stapled there (`pivot`
  joins). Every hinge angle is a linear function of the cells' half-angle, so the program's
  interpolation keeps the chain closed at every instant, not only at the keys.
* `crank-rocker` — a crank that turns all the way round driving a rocker, with flat card links
  joined by brads (`pivot` joins), the classic movable-book linkage. Its crank is a kinematic sheet
  on a `rotate` mechanism (the `crank` control); the coupler and the rocker follow through their
  pivots, which only the physics engine can solve, so the studio preview leaves the control
  disabled. `target:crank-…` frames hold the exact solved poses every 30°.

Why not drive the brad linkages from one control in the preview: a mechanism moves its sheet
linearly in its control (a rotation by the control value, or a translation proportional to it),
and a kinematic sheet follows one mechanism. A coupler's motion is not linear in the crank angle,
so no set of mechanisms on one control can carry it exactly. The folded versions avoid that: their
links are faces of one sheet posed by the fold program.
"""

import math

import pliego


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


mode = PARAM(lambda: mode, "four-bar")                         # noqa: F821
scale = float(PARAM(lambda: scale, 1.0))                       # noqa: F821
wall = float(PARAM(lambda: wall, 30.0))                        # noqa: F821
cells = int(round(float(PARAM(lambda: cells, 4))))             # noqa: F821
link_width = float(PARAM(lambda: link_width, 14.0))            # noqa: F821

if mode not in ("four-bar", "extender", "crank-rocker"):
    raise ValueError(f"card-linkages: unknown mode {mode!r}")

K = pliego.clamp(scale, 0.6, 2.0)
HW = pliego.clamp(wall, 15.0, 60.0)          # height of a standing (folded) link
N_CELLS = int(pliego.clamp(cells, 2, 8))
LW = pliego.clamp(link_width, 10.0, 24.0)
POST, FOOT = 8.0, 10.0                       # post width, foot depth (folded modes)
STRIP, BASE = "cardstock-250", "cardstock-300"
T_BASE = 0.36                                # the base's caliper: the feet stand on it
MAX_GAP = 0.25                               # mm: the worst mid-step closure gap allowed
HOLE = 3.0                                   # brad hole


def L4(en, es, fr, pt):
    return {"en": en, "es": es, "fr": fr, "pt": pt}


def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def wrap(a):
    while a <= -180.0:
        a += 360.0
    while a > 180.0:
        a -= 360.0
    return a


def heading(p, q):
    return math.degrees(math.atan2(q[1] - p[1], q[0] - p[0]))


def circle_meet(b, rb, d, rd, prev):
    """The point at distance rb from b and rd from d nearest `prev` (None if out of reach)."""
    dx, dz = d[0] - b[0], d[1] - b[1]
    dist = math.hypot(dx, dz)
    if dist > rb + rd - 1e-9 or dist < abs(rb - rd) + 1e-9:
        return None
    a = (rb * rb - rd * rd + dist * dist) / (2.0 * dist)
    h = math.sqrt(max(0.0, rb * rb - a * a))
    mx, mz = b[0] + a * dx / dist, b[1] + a * dz / dist
    c1 = (mx - h * dz / dist, mz + h * dx / dist)
    c2 = (mx + h * dz / dist, mz - h * dx / dist)
    return min((c1, c2), key=lambda c: (c[0] - prev[0]) ** 2 + (c[1] - prev[1]) ** 2)


def chain_end(lengths, turns):
    """Walk a chain of links from (0, 0) heading +x: (end point, final heading)."""
    x = z = 0.0
    hd = 0.0
    for length, t in zip(lengths, turns, strict=True):
        hd += math.radians(t)
        x += length * math.cos(hd)
        z += length * math.sin(hd)
    return (x, z), hd


sheets, joins, mechanisms, controls, sequence, initial, targets = [], [], [], [], None, None, {}

# ── folded modes: one strip standing on a base ────────────────────────────────────────────────
# Plan chart (x, z): the strip's first post runs along +x into the first pivot at (0, 0); its
# walls' fronts face the chart's left of travel, so a valley score turns the chain
# counter-clockwise (turning angle = fold angle).


def build_strip(lengths, label, closing):
    """A strip: foot+post, the links (`lengths`), then a foot+post (`closing` = "post") or a tab
    glued back onto the first post ("tab"). Returns the sheet, the vertical scores (one per joint)
    and the u of each joint."""
    u_joint = [POST]
    for length in lengths:
        u_joint.append(u_joint[-1] + length)
    ltot = u_joint[-1] + POST
    ring = [(0.0, -FOOT), (POST, -FOOT), (POST, 0.0)]
    if closing == "post":
        ring += [(ltot - POST, 0.0), (ltot - POST, -FOOT), (ltot, -FOOT)]
    else:
        ring += [(ltot, 0.0)]
    ring += [(ltot, HW), (0.0, HW)]
    sh = pliego.Sheet("strip", ring, stock=STRIP, grain_deg=90.0, label=label,
                      placement=pliego.Placement(origin=(-POST, T_BASE, 0.0)))
    feet = [sh.valley((0.0, 0.0), (POST, 0.0), angle=90.0, treatment="score", name="foot")]
    if closing == "post":
        feet.append(sh.valley((ltot - POST, 0.0), (ltot, 0.0), angle=90.0, treatment="score",
                              name="foot"))
    scores = [sh.score((u, 0.0), (u, HW), kind="flat", name="hinge") for u in u_joint]
    return sh, scores, feet, u_joint, ltot


def base_sheet(xs, zs):
    x0, x1 = min(xs) - 12.0, max(xs) + 12.0
    z0, z1 = min(zs) - 12.0, max(zs) + 12.0
    b = pliego.Sheet("base", rect(0.0, 0.0, x1 - x0, z1 - z0), stock=BASE, grain_deg=90.0,
                     label=L4("Base", "Base", "Base", "Base"),
                     placement=pliego.Placement(origin=(x0, 0.0, z1)))
    return b, x0, z1       # plan (x, z) ↦ base (x − x0, z1 − z)


def foot_glue(jid, strip, u0, plan_x0, bx0, bz1, base):
    """Glue a foot (strip u ∈ [u0, u0 + POST], v ∈ [−FOOT, 0]) whose post starts at plan
    (plan_x0, 0) heading +x: foot point (u, v) lies at plan (plan_x0 + u − u0, −v)."""
    region = rect(u0 + 0.5, -FOOT + 0.5, u0 + POST - 0.5, -0.5)
    return pliego.glue(jid, strip, region, base, (1.0, 0.0, 0.0, 1.0, plan_x0 - u0 - bx0, bz1),
                       side="front")


def keyframe_steps(scores, keys, labels, durations):
    steps = []
    for k, (angles, label) in enumerate(zip(keys, labels, strict=True)):
        steps.append(pliego.Step(f"pose-{k + 1}", label,
                                 [(mk, ang) for mk, ang in zip(scores, angles, strict=True)],
                                 duration_ms=durations))
    return steps


if mode == "four-bar":
    G, A_, C_, B_ = 64.0 * K, 50.0 * K, 22.0 * K, 46.0 * K   # ground, input, coupler, output
    D = (G, 0.0)
    s, l_ = sorted((G, A_, C_, B_))[0], sorted((G, A_, C_, B_))[-1]
    grashof = s + l_ <= G + A_ + C_ + B_ - s - l_
    # the input's reach: the coupler and output must close; walk outward from 90° both ways
    prev = None

    def pose(phi, prev):
        b = (A_ * math.cos(math.radians(phi)), A_ * math.sin(math.radians(phi)))
        c = circle_meet(b, C_, D, B_, prev if prev else (b[0] + C_, b[1] + 10.0))
        return b, c

    def turns(b, c):
        phi = heading((0.0, 0.0), b)
        t = [phi, wrap(heading(b, c) - phi), wrap(heading(c, D) - heading(b, c)),
             wrap(0.0 - heading(c, D))]
        return t

    def ok(b, c):
        if c is None:
            return False
        return all(abs(t) < 170.0 for t in turns(b, c)) and c[1] > 2.0 and b[1] > 2.0

    # start where the input puts the coupler's far pivot mid-reach of the output
    m_mid = (abs(B_ - C_) + B_ + C_) / 2.0
    phi0 = round(math.degrees(math.acos(pliego.clamp((A_ * A_ + G * G - m_mid * m_mid)
                                                     / (2.0 * A_ * G), -1.0, 1.0))))
    lo = hi = phi0
    b, c = pose(phi0, None)
    if not ok(b, c):
        raise ValueError(f"card-linkages: the four-bar does not close at {phi0}°")
    cl = ch = c
    while True:
        b2, c2 = pose(lo - 1.0, cl)
        if lo < -170.0:
            break
        if not ok(b2, c2):
            break
        lo, cl = lo - 1.0, c2
    while True:
        b2, c2 = pose(hi + 1.0, ch)
        if hi > 170.0:
            break
        if not ok(b2, c2):
            break
        hi, ch = hi + 1.0, c2
    lo, hi = lo + 3.0, hi - 3.0                 # keep clear of the reach's edge
    # key poses: from the middle out to hi, back to lo, and back to the middle
    n_half = 6
    while True:
        phis = ([lo + (hi - lo) * (0.5 + 0.5 * k / n_half) for k in range(n_half + 1)]
                + [hi - (hi - lo) * k / (2 * n_half) for k in range(1, 2 * n_half + 1)]
                + [lo + (hi - lo) * 0.5 * k / n_half for k in range(1, n_half + 1)])
        keys, prev = [], None
        for phi in phis:
            b, c = pose(phi, prev)
            prev = c
            keys.append([-t for t in turns(b, c)])   # mirrored: the walls stand behind the feet
        gap = 0.0
        for k0, k1 in zip(keys, keys[1:]):
            for t in (0.25, 0.5, 0.75):
                mid = [x + (y - x) * t for x, y in zip(k0, k1, strict=True)]
                end, hd = chain_end([A_, C_, B_], mid[:3])
                gap = max(gap, math.hypot(end[0] - D[0], end[1] - D[1]),
                          POST * abs(math.radians(wrap(math.degrees(hd) + mid[3]))))
        if gap <= MAX_GAP or n_half >= 24:
            break
        n_half += 3
    if gap > MAX_GAP:
        raise ValueError(f"card-linkages: mid-step closure gap {gap:.2f} mm")
    strip, scores, feet, u_joint, ltot = build_strip(
        [A_, C_, B_], L4("Linkage strip", "Tira del mecanismo", "Bande du mécanisme",
                         "Tira do mecanismo"), "post")
    xs = [-POST, G + POST]
    zs = [0.0, FOOT]
    prev = None
    for phi in [lo + (hi - lo) * k / 40.0 for k in range(41)]:
        b, c = pose(phi, prev)
        prev = c
        xs += [b[0], c[0]]
        zs += [-b[1], -c[1]]
    base, bx0, bz1 = base_sheet(xs, zs)
    joins += [foot_glue("foot-input", strip, 0.0, -POST, bx0, bz1, base),
              foot_glue("foot-output", strip, ltot - POST, G, bx0, bz1, base)]
    start = keys[0]
    initial = {"strip": {"angles": {**{f: 90.0 for f in feet},
                                    **dict(zip(scores, start, strict=True))},
                         "root": (POST / 2.0, -FOOT / 2.0)}}
    labels = [L4(f"Input link at {phi:.0f}°", f"Eslabón de entrada a {phi:.0f}°",
                 f"Biellette d'entrée à {phi:.0f}°", f"Elo de entrada a {phi:.0f}°")
              for phi in phis[1:]]
    sequence = pliego.Sequence(keyframe_steps(scores, keys[1:], labels, 450), mode="physical")
    controls.append(pliego.sequence_control(label=L4("Swing the input link",
                                                     "Mover el eslabón de entrada",
                                                     "Balancer la biellette d'entrée",
                                                     "Balançar o elo de entrada")))
    sheets += [base, strip]
    summary = (f"ground={G:.1f} input={A_:.1f} coupler={C_:.1f} output={B_:.1f}mm "
               f"grashof={grashof} input_range=[{lo:.0f}, {hi:.0f}]deg keys={len(keys)} "
               f"max_mid_step_gap={gap:.3f}mm")

elif mode == "extender":
    HL = 22.0 * K                                    # half-bar length (rhombus side)
    a_open, a_shut = 18.0, 70.0                      # the cells' half-angle range (deg)
    n = N_CELLS

    def ext_turns(alpha):
        t = [alpha]                                  # post → first top panel
        for k in range(n):                           # top zig-zag: J (−2α), C (+2α) …
            t.append(-2.0 * alpha)
            if k < n - 1:
                t.append(2.0 * alpha)
        t.append(-(180.0 - 2.0 * alpha))             # the tip: round onto the bottom zig-zag
        for k in range(n):
            t.append(-2.0 * alpha)
            if k < n - 1:
                t.append(2.0 * alpha)
        t.append(alpha)                              # back at the first crossing: the tab
        return t

    lengths = [HL] * (4 * n)
    strip, scores, feet, u_joint, ltot = build_strip(
        lengths, L4("Extender strip", "Tira del extensor", "Bande de l'extenseur",
                    "Tira do extensor"), "tab")
    # closure check (exact at every α: every angle is linear in α)
    gap = 0.0
    for alpha in (a_shut, (a_open + a_shut) / 2.0, a_open):
        end, hd = chain_end(lengths, ext_turns(alpha)[:-1])
        gap = max(gap, math.hypot(*end))
    if gap > 1e-6:
        raise ValueError(f"card-linkages: the extender does not close ({gap:.2e} mm)")
    reach = 2.0 * n * HL * math.cos(math.radians(a_open))
    xs, zs = [-POST, reach], [-HL, HL, FOOT]
    base, bx0, bz1 = base_sheet(xs, zs)
    joins.append(foot_glue("foot", strip, 0.0, -POST, bx0, bz1, base))
    # the closing tab lies back on the first post (mirrored along u)
    joins.append(pliego.glue("tab-to-post", strip, rect(ltot - POST + 0.5, 0.5, ltot - 0.5,
                                                         HW - 0.5),
                             strip, (-1.0, 0.0, 0.0, 1.0, ltot, 0.0), side="back"))
    # staples at the crossings: top zig-zag joint ↔ bottom zig-zag joint
    for k in range(1, n):
        u_top = u_joint[2 * k]                       # C_k on the top zig-zag
        u_bot = u_joint[4 * n - 2 * k]               # C_k on the bottom zig-zag
        joins.append(pliego.pivot(f"crossing-{k}", (strip, (u_top, HW / 2.0)),
                                  (strip, (u_bot, HW / 2.0))))
    joints = scores
    initial = {"strip": {"angles": {**{f: 90.0 for f in feet},
                                    **dict(zip(joints, ext_turns(a_shut), strict=True))},
                         "root": (POST / 2.0, -FOOT / 2.0)}}
    steps = [
        pliego.Step("extend", L4("Pull the tip: the extender opens",
                                 "Jala la punta: el extensor se abre",
                                 "Tirer sur la pointe : l'extenseur se déploie",
                                 "Puxe a ponta: o extensor se abre"),
                    list(zip(joints, ext_turns(a_open), strict=True)), duration_ms=2000),
        pliego.Step("retract", L4("Push it back: it closes", "Empújala: se cierra",
                                  "La repousser : il se replie", "Empurre: ele se fecha"),
                    list(zip(joints, ext_turns(a_shut), strict=True)), duration_ms=2000),
    ]
    sequence = pliego.Sequence(steps, mode="physical")
    controls.append(pliego.sequence_control(label=L4("Extend and retract", "Extender y retraer",
                                                     "Déployer et replier",
                                                     "Estender e recolher")))
    sheets += [base, strip]
    summary = (f"cells={n} half_bar={HL:.1f}mm reach={2 * n * HL * math.cos(math.radians(a_shut)):.1f}"
               f"→{reach:.1f}mm closure_gap={gap:.1e}mm")

else:   # crank-rocker with brads
    G, A_, C_, B_ = 80.0 * K, 24.0 * K, 76.0 * K, 56.0 * K
    if not (min(G, C_, B_) > A_ and A_ + max(G, C_, B_) <= G + C_ + B_ - max(G, C_, B_)):
        raise ValueError("card-linkages: these lengths are not a crank-rocker")
    r = LW / 2.0
    STEP_Y = 0.32                                    # layer pitch of the stacked links
    D = (G, 0.0)                                     # plan (X, Y); A at the origin

    def solve(theta, prev):
        b = (A_ * math.cos(math.radians(theta)), A_ * math.sin(math.radians(theta)))
        c = circle_meet(b, C_, D, B_, prev)
        if c is None:
            raise ValueError(f"card-linkages: no closure at crank {theta:g}°")
        return b, c

    def brad_mark(sh, at):
        """A kiss-cut cross where the brad hole is punched (the join point stays on material)."""
        x, y = at
        sh.halfcut([(x - HOLE / 2.0, y), (x + HOLE / 2.0, y)], name="brad")
        sh.halfcut([(x, y - HOLE / 2.0), (x, y + HOLE / 2.0)], name="brad")

    def link(sid, length, label, level, kin=None):
        ring = []
        for k in range(17):
            t = math.radians(-90.0 + 180.0 * k / 16)
            ring.append((r + length + r * math.cos(t), r + r * math.sin(t)))
        for k in range(17):
            t = math.radians(90.0 + 180.0 * k / 16)
            ring.append((r + r * math.cos(t), r + r * math.sin(t)))
        sh = pliego.Sheet(sid, ring, stock=STRIP, grain_deg=0.0, label=label, kinematic=kin)
        for x in (r, r + length):
            brad_mark(sh, (x, r))
        return sh, level

    def place(sh, level, p, q):
        """Put a link (pivots at local (r, r) and (r + L, r)) from plan p to plan q."""
        psi = heading(p, q)
        c, s = math.cos(math.radians(psi)), math.sin(math.radians(psi))
        ox, oy = p[0] - (r * c - r * s), p[1] - (r * s + r * c)
        h = math.radians(psi) / 2.0
        sh.placement = pliego.Placement(origin=(ox, T_BASE + STEP_Y * level, -oy),
                                        rotation=(0.0, math.sin(h), 0.0, math.cos(h)))

    def world_of(level, p, q, uv):
        psi = math.radians(heading(p, q))
        c, s = math.cos(psi), math.sin(psi)
        u, v = uv[0] - r, uv[1] - r
        return (p[0] + u * c - v * s, T_BASE + STEP_Y * level, -(p[1] + u * s + v * c))

    theta0 = 60.0
    b0, c0 = solve(theta0, (A_ + C_ * 0.6, 40.0 * K))
    rocker, lr = link("rocker", B_, L4("Rocker", "Balancín", "Balancier", "Balancim"), 1)
    coupler, lc = link("coupler", C_, L4("Coupler", "Biela", "Bielle", "Biela"), 2)
    crank, lk = link("crank", A_, L4("Crank", "Manivela", "Manivelle", "Manivela"), 3,
                     kin="turn-crank")
    place(rocker, lr, D, c0)
    place(coupler, lc, c0, b0)
    place(crank, lk, (0.0, 0.0), b0)
    # the base: pivots A and D; plan bounds over a full turn
    xs, ys, prev = [0.0, G], [0.0], c0
    poses = {}
    for k in range(0, 361, 5):
        b, c = solve(theta0 + k, prev)
        prev = c
        poses[k] = (b, c)
        xs += [b[0], c[0]]
        ys += [b[1], c[1]]
    x0, x1 = min(xs) - LW - 6.0, max(xs) + LW + 6.0
    y0, y1 = min(ys) - LW - 6.0, max(ys) + LW + 6.0
    base = pliego.Sheet("base", rect(0.0, 0.0, x1 - x0, y1 - y0), stock=BASE, grain_deg=90.0,
                        label=L4("Base", "Base", "Base", "Base"),
                        placement=pliego.Placement(origin=(x0, 0.0, -y0)))
    for x, y in ((0.0, 0.0), (G, 0.0)):
        brad_mark(base, (x - x0, y - y0))
    joins += [pliego.pivot("brad-b", (crank, (r + A_, r)), (coupler, (r + C_, r))),
              pliego.pivot("brad-c", (coupler, (r, r)), (rocker, (r + B_, r))),
              pliego.pivot("brad-d", (rocker, (r, r)), (base, (G - x0, -y0)))]
    mechanisms.append(pliego.rotate("turn-crank", (base, (-x0, -y0)), "crank", [crank]))
    controls.append(pliego.angle_control("crank", L4("Turn the crank", "Girar la manivela",
                                                     "Tourner la manivelle", "Girar a manivela"),
                                         default=0.0, min=0.0, max=360.0))
    swing = [math.degrees(math.atan2(c[1], c[0] - G)) for b, c in poses.values()]

    for k in range(0, 360, 30):
        b, c = poses[k]

        def frame(sid, uv, b=b, c=c):
            if sid == "base":
                return (uv[0] + x0, 0.0, -(uv[1] + y0))
            if sid == "crank":
                return world_of(lk, (0.0, 0.0), b, uv)
            if sid == "coupler":
                return world_of(lc, c, b, uv)
            return world_of(lr, D, c, uv)
        targets[f"crank-{k:03d}"] = frame
    sheets += [base, rocker, coupler, crank]
    summary = (f"ground={G:.1f} crank={A_:.1f} coupler={C_:.1f} rocker={B_:.1f}mm "
               f"rocker_swing={max(swing) - min(swing):.1f}deg targets={len(targets)}")

print(f"card-linkages: mode={mode} {summary}")

result = pliego.Assembly(sheets, joins=joins, mechanisms=mechanisms, controls=controls,
                         sequence=sequence, initial=initial, targets=targets,
                         title="Card linkages")
