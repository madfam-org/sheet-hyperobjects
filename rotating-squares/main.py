"""Rotating squares — sheet-hyperobjects cartridge (Pliego).

An auxetic kirigami sheet: an n × n lattice of square units of side L, joined at small corner
ligaments by straight through cuts (`C`). Every interior lattice vertex carries one slit of length
2L − 2w centred on it, horizontal where i + j is even and vertical where it is odd; boundary
vertices carry the half slit that reaches the outline. Each unit edge then keeps exactly one
ligament of width w at one end, which is the rotating-squares mechanism (Grima & Evans 2000):
neighbouring squares counter-rotate by ±φ and the lattice expands equally in both directions
(ideal-hinge Poisson ratio ν = −1).

Physical mode: the sheet starts flat on the table (v1 frames cannot separate the two sides of a
cut, so the opening happens in simulation — the engine splits cut vertices at mesh time). The centre
of the left-middle square is pinned (`pin`), the centre of the right-middle square is pinned to a
`translate` driver and pulled by the `pull` control. Pinning single points, not whole edges, leaves
the squares free to rotate: clamping a full edge would hold one square's rotation at zero and, in
the ideal mechanism, lock the whole lattice.
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


MIN_FEATURE = {"cardstock-160": 1.5, "copy-80": 1.0, "kraft-120": 1.0, "pp-300": 1.5}

units = int(clamp(PARAM(lambda: units, 8), 3, 12))
unit = clamp(PARAM(lambda: unit, 20.0), 10.0, 40.0)
ligament = clamp(PARAM(lambda: ligament, 2.0), 1.0, 6.0)
open_angle = clamp(PARAM(lambda: open_angle, 30.0), 5.0, 40.0)
stock = str(PARAM(lambda: stock, "cardstock-160"))
if stock not in MIN_FEATURE:
    raise ValueError(f"stock {stock!r} is not one this cartridge offers")
if ligament < MIN_FEATURE[stock]:
    raise ValueError(f"ligament {ligament} mm is narrower than {stock}'s minimum feature "
                     f"{MIN_FEATURE[stock]} mm")
if ligament > unit / 4:
    raise ValueError(f"ligament {ligament} mm is wider than a quarter of the {unit} mm unit")

n, L, w = units, unit, ligament
size = n * L
LABEL = {"en": "Rotating squares", "es": "Cuadrados rotatorios", "fr": "Carrés rotatifs",
         "pt": "Quadrados rotativos"}
sheet = pliego.Sheet("rotating-squares", pliego.square(size), stock=stock, grain_deg=90.0,
                     label=LABEL)

slits = 0
for i in range(n + 1):
    for j in range(n + 1):
        x, y = i * L, j * L
        horizontal = (i + j) % 2 == 0
        on_x_border, on_y_border = i in (0, n), j in (0, n)
        if on_x_border and on_y_border:
            continue  # sheet corners: only the outline meets there
        if horizontal:
            if on_y_border:
                continue  # a horizontal slit on the top/bottom outline would cut nothing
            x0, x1 = max(0.0, x - L + w), min(size, x + L - w)
            sheet.cut([(x0, y), (x1, y)])
        else:
            if on_x_border:
                continue  # a vertical slit on the left/right outline would cut nothing
            y0, y1 = max(0.0, y - L + w), min(size, y + L - w)
            sheet.cut([(x, y0), (x, y1)])
        slits += 1

report = pliego.papercut.analyze(sheet, min_feature_mm=MIN_FEATURE[stock])
if not report.ok:
    raise ValueError("rotating-squares papercut check failed: "
                     + "; ".join(i["detail"] for i in report.issues if i["level"] == "error"))

# Opening kinematics (ideal hinges): centre spacing L → L·(cos φ + sin φ).
phi = math.radians(open_angle)
mid = (n // 2 + 0.5) * L
left_centre, right_centre = (0.5 * L, mid), (size - 0.5 * L, mid)
travel = (n - 1) * L * (math.cos(phi) + math.sin(phi) - 1.0)

pull = pliego.control("pull", "distance",
                      {"en": "Pull", "es": "Jalar", "fr": "Tirer", "pt": "Puxar"},
                      0.0, 0.0, round(travel, 3), "mm")
result = pliego.Assembly(
    [sheet],
    joins=[
        pliego.pin("anchor", (sheet, left_centre)),
        pliego.pin("handle", (sheet, right_centre), mechanism="pull-apart"),
    ],
    mechanisms=[pliego.translate("pull-apart", "pull", (1.0, 0.0, 0.0), round(travel, 3))],
    controls=[pull],
    title="Rotating squares",
    meta={"min_feature_mm": MIN_FEATURE[stock]},
)
