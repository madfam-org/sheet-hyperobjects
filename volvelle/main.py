"""Volvelle (wheel chart) — sheet-hyperobjects cartridge (Pliego).

Paper discs turning on a pivot through a base. Two modes:

* `windows` — a base, a wheel and a cover. The wheel (larger than the square base and cover, so its
  rim shows at the four sides for the thumb) turns between them; the cover has `windows` openings in
  a ring, through which the wheel's printing shows one sector at a time.
* `rings` — a base and `rings` stacked discs of decreasing radius. Each disc turns on its own and
  leaves a band of the disc below it visible; a small notch in each rim points at the band below.

Every turning disc is a kinematic sheet moved by a `rotate` mechanism about the pivot (the normal of
the base at its centre), each with its own angle control. The pivot hardware (a paper brad, a split
pin or a binding post) is the mechanism's centre and not a join: a `pivot` join between a turning
disc and the fixed base would leave the control to the physics engine. The discs and the cover have
a pivot hole; the base is marked with a kiss-cut cross where the pivot pierces it.
"""

import math

import pliego


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


mode = PARAM(lambda: mode, "windows")                        # noqa: F821
size = float(PARAM(lambda: size, 150.0))                     # noqa: F821
wheel_ratio = float(PARAM(lambda: wheel_ratio, 1.2))         # noqa: F821
windows = int(round(float(PARAM(lambda: windows, 2))))       # noqa: F821
window_shape = PARAM(lambda: window_shape, "sector")         # noqa: F821
window_angle = float(PARAM(lambda: window_angle, 40.0))      # noqa: F821
band_inner = float(PARAM(lambda: band_inner, 0.35))          # noqa: F821
band_outer = float(PARAM(lambda: band_outer, 0.8))           # noqa: F821
rings = int(round(float(PARAM(lambda: rings, 3))))           # noqa: F821
ring_band = float(PARAM(lambda: ring_band, 16.0))            # noqa: F821
pivot_hole = float(PARAM(lambda: pivot_hole, 3.0))           # noqa: F821

if mode not in ("windows", "rings"):
    raise ValueError(f"volvelle: unknown mode {mode!r}")
if window_shape not in ("sector", "round"):
    raise ValueError(f"volvelle: unknown window shape {window_shape!r}")

S = pliego.clamp(size, 80.0, 300.0)
k_wheel = pliego.clamp(wheel_ratio, 1.05, 1.35)
n_win = int(pliego.clamp(windows, 1, 8))
w_deg = pliego.clamp(window_angle, 8.0, 120.0)
b_in = pliego.clamp(band_inner, 0.15, 0.85)
b_out = pliego.clamp(band_outer, 0.25, 0.95)
n_rings = int(pliego.clamp(rings, 2, 5))
band = pliego.clamp(ring_band, 8.0, 40.0)
hole_d = pliego.clamp(pivot_hole, 2.0, 6.0)
BASE_STOCK, DISC_STOCK = "cardstock-300", "cardstock-250"
STACK = 0.25            # each layer this far above the one below (< collision thickness)
SEG = 96                # segments of a disc outline
MIN_BRIDGE = 3.0


def L4(en, es, fr, pt):
    return {"en": en, "es": es, "fr": fr, "pt": pt}


C = (S / 2.0, S / 2.0)          # the pivot, in base coordinates


def disc_sheet(sid, radius, label, level, notch=False):
    """A disc of `radius` with a pivot hole, placed concentric with the base `level` layers up.
    Its local frame is centred on (radius, radius) so the outline stays in the positive quadrant."""
    cx = cy = radius
    ring = pliego.circle((cx, cy), radius, SEG)
    if notch:   # a V notch at angle 0 on the rim: the pointer at the band below
        ring = _notched(cx, cy, radius, min(4.0, radius * 0.08))
    sh = pliego.Sheet(sid, ring, stock=DISC_STOCK, grain_deg=90.0, label=label,
                      kinematic="spin-" + sid,
                      placement=pliego.Placement(origin=(C[0] - cx, STACK * level, -(C[1] - cy))))
    sh.hole(pliego.circle((cx, cy), hole_d / 2.0, 24))
    return sh


def _notched(cx, cy, r, d):
    """A disc outline with a V notch (depth 1.6·d, half-width d) at angle 0."""
    half = math.degrees(math.asin(d / r))
    pts = [pliego.P(cx + r - 1.6 * d, cy)]
    for i in range(SEG + 1):
        a = half + (360.0 - 2 * half) * i / SEG
        pts.append(pliego.P(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))))
    return pts


def mark_pivot(sheet, at):
    """A kiss-cut cross where the pivot pierces a sheet without a hole."""
    x, y = at
    a = hole_d / 2.0
    sheet.halfcut([(x - a, y), (x + a, y)], name="pivot-mark")
    sheet.halfcut([(x, y - a), (x, y + a)], name="pivot-mark")


base = pliego.Sheet("base", [(0, 0), (S, 0), (S, S), (0, S)], stock=BASE_STOCK, grain_deg=90.0,
                    label=L4("Base", "Base", "Base", "Base"))
mark_pivot(base, C)
sheets, mechanisms, controls = [base], [], []

if mode == "windows":
    R = S * k_wheel / 2.0
    r_in, r_out = b_in * S / 2.0, b_out * S / 2.0
    if r_out - r_in < 8.0:
        raise ValueError("volvelle: the window band must be at least 8 mm wide")
    if r_in < hole_d + 4.0:
        raise ValueError("volvelle: the window band starts too close to the pivot")
    if n_win * w_deg > 360.0 - n_win * math.degrees(MIN_BRIDGE / r_in):
        raise ValueError(f"volvelle: {n_win} windows of {w_deg:g}° leave bridges under "
                         f"{MIN_BRIDGE:g} mm at the inner edge of the band")
    wheel = disc_sheet("wheel", R, L4("Wheel", "Rueda", "Roue", "Roda"), 1)
    cover = pliego.Sheet("cover", [(0, 0), (S, 0), (S, S), (0, S)], stock=DISC_STOCK,
                         grain_deg=90.0, label=L4("Cover with windows", "Tapa con ventanas",
                                                  "Couvercle à fenêtres", "Tampa com janelas"),
                         placement=pliego.Placement(origin=(0.0, 2 * STACK, 0.0)))
    cover.hole(pliego.circle(C, hole_d / 2.0, 24))
    for k in range(n_win):
        mid = 90.0 + 360.0 * k / n_win
        if window_shape == "sector":
            a0, a1 = mid - w_deg / 2.0, mid + w_deg / 2.0
            m = max(4, int(w_deg / 4))
            outer = [(C[0] + r_out * math.cos(math.radians(a0 + (a1 - a0) * i / m)),
                      C[1] + r_out * math.sin(math.radians(a0 + (a1 - a0) * i / m)))
                     for i in range(m + 1)]
            inner = [(C[0] + r_in * math.cos(math.radians(a1 - (a1 - a0) * i / m)),
                      C[1] + r_in * math.sin(math.radians(a1 - (a1 - a0) * i / m)))
                     for i in range(m + 1)]
            cover.hole(outer + inner)
        else:
            rr = (r_out - r_in) / 2.0
            rc = (r_out + r_in) / 2.0
            cover.hole(pliego.circle((C[0] + rc * math.cos(math.radians(mid)),
                                      C[1] + rc * math.sin(math.radians(mid))), rr, 32))
    rep = pliego.papercut.analyze(cover, min_feature_mm=MIN_BRIDGE)
    bad = [i for i in rep.issues if i["level"] == "error"]
    if bad:
        raise ValueError(f"volvelle: the cover fails the papercut check: {bad}")
    sheets += [wheel, cover]
    mechanisms.append(pliego.rotate("spin-wheel", (base, C), "turn", [wheel]))
    controls.append(pliego.angle_control("turn", L4("Turn the wheel", "Girar la rueda",
                                                     "Tourner la roue", "Girar a roda"),
                                         default=30.0, min=0.0, max=360.0))
    summary = f"wheel_d={2 * R:.1f}mm windows={n_win} bridge_mm={rep.min_bridge_mm}"
else:
    R0 = S / 2.0 - 4.0
    radii = [R0 - band * k for k in range(n_rings)]
    if radii[-1] < hole_d + 8.0:
        raise ValueError(f"volvelle: {n_rings} rings of {band:g} mm leave a top disc of "
                         f"{radii[-1]:.1f} mm radius; use fewer rings or narrower bands")
    for k, rad in enumerate(radii):
        sid = f"ring-{k + 1}"
        sh = disc_sheet(sid, rad, L4(f"Disc {k + 1}", f"Disco {k + 1}", f"Disque {k + 1}",
                                     f"Disco {k + 1}"), k + 1, notch=k > 0)
        sheets.append(sh)
        mechanisms.append(pliego.rotate("spin-" + sid, (base, C), sid, [sh]))
        controls.append(pliego.angle_control(sid, L4(f"Turn disc {k + 1}",
                                                      f"Girar el disco {k + 1}",
                                                      f"Tourner le disque {k + 1}",
                                                      f"Girar o disco {k + 1}"),
                                             default=25.0 * k, min=0.0, max=360.0))
    summary = f"rings={n_rings} radii_mm={[round(r, 1) for r in radii]}"

print(f"volvelle: mode={mode} base={S:g}mm {summary}")

result = pliego.Assembly(sheets, mechanisms=mechanisms, controls=controls, title="Volvelle")
