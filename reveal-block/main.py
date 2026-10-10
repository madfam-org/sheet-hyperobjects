"""Reveal block — sheet-hyperobjects cartridge (Pliego).

A memo-block sculpture: a pad of paper whose every sheet is pre-cut along that layer's
cross-section of a 3-D scene. Tear the sheets away from the top and the cut-out middle of each one
stays behind; the scene appears as a stepped relief inside the block. One family, five ORIGINAL
MADFAM scenes (a `scene` select): a stepped pyramid, a volcano, a landscape, a sphere on a
pedestal and a city skyline. Every scene is a field computed here — heightfields and a small
constructive geometry of spheres, boxes, cylinders and cones — and sliced by the kernel's
`pliego.reveal.slice_block`:

* the cross-section of each layer is traced (marching squares) after thin features below the
  minimum feature are removed, and cut through the sheet (or perforated, or kiss-cut);
* a perforated tear grid splits the excess of each sheet into chunks, so a chunk can slide out
  even from under an overhang (the sphere's lower half);
* every separable region of a sheet is a `keep` or `excess` piece, the sheets form a stack, and
  the fold program removes the excess layer by layer from the top (spec §5.8).

The preview lets each document sheet stand for several real sheets (`represents`); the
fabrication setting slices every real sheet of the pad (block height ÷ paper caliper).
"""

import math

import pliego


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


def clamp(value, lo, hi):
    return max(lo, min(hi, float(value)))


# A reveal block's floor for kept bridges and removed slits: the stock card's
# fabrication.min_feature_mm, but never under 2 mm — a column of separate sheets is far weaker
# than one sheet, and a chunk narrower than that tears unpredictably.
STOCK_MIN_FEATURE = {"copy-80": 1.0, "kraft-120": 1.0, "cardstock-160": 1.5,
                     "cardstock-250": 2.0}
BLOCK_MIN_FEATURE = 2.0
SCENES = ("stepped-pyramid", "volcano", "landscape", "sphere", "city-skyline")
CONTOURS = ("cut", "perforation", "halfcut")

scene_id = str(PARAM(lambda: scene, "stepped-pyramid"))  # noqa: F821
size = clamp(PARAM(lambda: size, 70.0), 50.0, 100.0)  # noqa: F821
height = clamp(PARAM(lambda: height, 50.0), 30.0, 90.0)  # noqa: F821
layers = int(clamp(PARAM(lambda: layers, 40), 12, 120))  # noqa: F821
fabrication = bool(PARAM(lambda: fabrication, False))  # noqa: F821
tear_grid = int(clamp(PARAM(lambda: tear_grid, 2), 1, 4))  # noqa: F821
contour = str(PARAM(lambda: contour, "cut"))  # noqa: F821
stock = str(PARAM(lambda: stock, "copy-80"))  # noqa: F821
if scene_id not in SCENES:
    raise ValueError(f"scene {scene_id!r} is not one of {SCENES}")
if contour not in CONTOURS:
    raise ValueError(f"contour {contour!r} is not one of {CONTOURS}")
if stock not in STOCK_MIN_FEATURE:
    raise ValueError(f"stock {stock!r} is not offered (choose {sorted(STOCK_MIN_FEATURE)})")
min_feature = max(BLOCK_MIN_FEATURE, STOCK_MIN_FEATURE[stock])

R = pliego.reveal
W = D = size
H = height
CX, CY = W / 2.0, D / 2.0


def smoothstep(e0, e1, x):
    t = min(1.0, max(0.0, (x - e0) / (e1 - e0)))
    return t * t * (3.0 - 2.0 * t)


# ── stepped pyramid: battered terraces, a front stairway and a shrine on top ─────────────────

def pyramid_height(x, y):
    tiers = 6
    base, top = 0.42 * W, 0.13 * W          # half-widths of the lowest and the top terrace
    tier_w = (base - top) / tiers
    tier_h = 0.78 * H / tiers
    r = max(abs(x - CX), abs(y - CY))       # square terraces (Chebyshev distance)
    if r >= base:
        h = 0.0
    else:
        k = min(tiers - 1, int((base - r) / tier_w))
        inner = base - (k + 1) * tier_w      # the terrace's inner edge
        batter = smoothstep(inner + 0.55 * tier_w, inner + tier_w, r)
        h = (k + 1) * tier_h - 0.45 * tier_h * batter
    # the stairway climbs the front face (low y) straight to the top terrace
    if abs(x - CX) < 0.065 * W and y < CY:
        t = (y - (CY - base)) / (base - top)
        if 0.0 <= t <= 1.0:
            h = max(h, t * 0.78 * H)
    # a shrine with a flat roof on the top terrace
    if abs(x - CX) < 0.085 * W and abs(y - CY) < 0.085 * W:
        h = max(h, 0.95 * H)
    return h


# ── volcano: a concave cone with gullies, a crater and a parasitic side cone ─────────────────

def volcano_height(x, y):
    ox, oy, radius = 0.49 * W, 0.51 * D, 0.44 * W
    rho = math.hypot(x - ox, y - oy) / radius
    theta = math.atan2(y - oy, x - ox)
    plain = 0.06 * H
    if rho < 1.0:
        cone = 0.92 * H * (1.0 - rho) ** 1.5 * (1.0 + 0.07 * math.sin(7.0 * theta) * rho)
    else:
        cone = 0.0
    crater_r = 0.17
    if rho < crater_r:
        rim = 0.92 * H * (1.0 - crater_r) ** 1.5
        cone = rim - 0.28 * H * (1.0 - (rho / crater_r) ** 2)
    side = math.hypot(x - 0.72 * W, y - 0.30 * D) / (0.13 * W)
    vent = 0.32 * H * (1.0 - side) ** 1.2 if side < 1.0 else 0.0
    return max(plain, cone, vent)


# ── landscape: rolling hills, a mountain, a river valley and a mesa ──────────────────────────

def landscape_height(x, y):
    u, v = x / W, y / D
    hills = 0.5 + 0.5 * math.sin(2 * math.pi * 1.3 * u + 0.6) * math.cos(2 * math.pi * 0.9 * v + 0.3)
    mountain = math.exp(-((u - 0.70) ** 2 + (v - 0.64) ** 2) / 0.022)
    h = H * (0.16 + 0.22 * hills + 0.55 * mountain)
    river_v = 0.30 + 0.10 * math.sin(2 * math.pi * 0.8 * u + 0.4)
    h -= 0.16 * H * math.exp(-((v - river_v) ** 2) / 0.0035)
    mesa = math.hypot(u - 0.24, v - 0.72) / 0.11
    if mesa < 1.0:                           # a flat-topped mesa with a steep rim
        h = max(h, H * (0.40 + 0.10 * (1.0 - smoothstep(0.85, 1.0, mesa))))
    return max(0.08 * H, h)


# ── sphere on a pedestal: the overhang case ───────────────────────────────────────────────────

def sphere_scene():
    r = min(0.30 * W, 0.31 * H)
    return R.union(R.cylinder((CX, CY), 0.30 * W, 0.0, 0.10 * H),
                   R.cylinder((CX, CY), 0.075 * W, 0.0, 0.42 * H),
                   R.sphere((CX, CY, H - r - 0.02 * H), r))


# ── city skyline: a street grid of towers with setbacks, a round tower and a spire ───────────

def city_scene():
    n = 4
    lo, hi = 0.09 * W, 0.91 * W
    cell = (hi - lo) / n
    street = 0.055 * W
    parts = [R.box((lo, lo, 0.0), (hi, hi, 0.06 * H))]
    for i in range(n):
        for j in range(n):
            x0, y0 = lo + i * cell + street / 2.0, lo + j * cell + street / 2.0
            x1, y1 = x0 + cell - street, y0 + cell - street
            # a fixed, deterministic height pattern: taller towards the back-right corner
            frac = (math.sin(12.9898 * (i + 1) + 78.233 * (j + 1)) * 43758.5453) % 1.0
            top = H * (0.25 + 0.30 * frac + 0.10 * (i + j) / (2 * (n - 1)))
            if (i, j) == (1, 2):                 # the round tower with a spire
                cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
                parts.append(R.cylinder((cx, cy), (x1 - x0) / 2.0, 0.0, 0.70 * H))
                parts.append(R.cone((cx, cy), (x1 - x0) / 2.0, 0.70 * H, 0.97 * H))
            elif (i + 2 * j) % 3 == 0:           # a stepped tower: a setback halfway up
                inset = 0.22 * (x1 - x0)
                parts.append(R.box((x0, y0, 0.0), (x1, y1, 0.55 * top)))
                parts.append(R.box((x0 + inset, y0 + inset, 0.0), (x1 - inset, y1 - inset, top)))
            else:
                parts.append(R.box((x0, y0, 0.0), (x1, y1, top)))
    return R.union(*parts)


SCENE_BUILDERS = {
    "stepped-pyramid": lambda: R.heightfield(pyramid_height),
    "volcano": lambda: R.heightfield(volcano_height),
    "landscape": lambda: R.heightfield(landscape_height),
    "sphere": sphere_scene,
    "city-skyline": city_scene,
}
TITLES = {
    "stepped-pyramid": "Reveal block — stepped pyramid",
    "volcano": "Reveal block — volcano",
    "landscape": "Reveal block — landscape",
    "sphere": "Reveal block — sphere on a pedestal",
    "city-skyline": "Reveal block — city skyline",
}

block = R.slice_block(SCENE_BUILDERS[scene_id](), size=(W, D), height=H, layers=layers,
                      stock=stock, fabrication=fabrication, min_feature=min_feature,
                      tear_grid=tear_grid, contour=contour, tear="perforation", spine=True,
                      title=TITLES[scene_id])
report = block.report
if report["keep_pieces"] == 0:
    raise ValueError("the scene left nothing to reveal at this size and height")
if tear_grid == 1 and report["overhang_layers"] > 0:
    raise ValueError(f"{report['overhang_layers']} layers sit under an overhang: their excess "
                     "frame cannot lift off whole — use 2 or more tear chunks per side")
result = block.assembly
