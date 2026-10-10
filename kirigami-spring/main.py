"""Kirigami spring — sheet-hyperobjects cartridge (Pliego).

An Archimedean spiral cut, r(θ) = r_hub + b·θ/(2π·arms), turns a disc into a spiral strip of width
b that joins a central hub to an outer rim. Lift the hub while the rim is held and the strip rises
into a conical helix: a spring cut from one flat sheet. With two arms the disc carries two
interleaved cuts half a turn apart, so two strips of the same width hold the hub from opposite
sides and it rises level.

Physical (tier C): the rim is pinned at points around its middle circle and three points of the
hub are pinned to a `translate` driver that lifts them along world +Y (the `lift` control). Version
1 frames cannot separate the two lips of a cut, and the strip bends and twists as it rises, which no
rigid model of this sheet can show, so the extension happens in the engine; the studio's preview
shows the flat sheet. The lift range is the disc's radius, an estimate: the paper decides.
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


def L4(en, es, fr, pt):
    return {"en": en, "es": es, "fr": fr, "pt": pt}


MIN_FEATURE = {"copy-80": 1.0, "kraft-120": 1.0, "cardstock-160": 1.5, "pp-300": 1.5}
SEG_DEG = 6.0  # polyline step of the spiral, degrees

diameter = clamp(PARAM(lambda: diameter, 160.0), 80.0, 300.0)
turns = clamp(PARAM(lambda: turns, 4.0), 1.0, 10.0)
width = clamp(PARAM(lambda: width, 8.0), 3.0, 30.0)
arms = int(clamp(PARAM(lambda: arms, 1), 1, 2))
stock = str(PARAM(lambda: stock, "cardstock-160"))
if stock not in MIN_FEATURE:
    raise ValueError(f"stock {stock!r} is not one this cartridge offers")
mf = MIN_FEATURE[stock]
if width < mf:
    raise ValueError(f"strip width {width} mm is below {stock}'s minimum feature {mf} mm")

R = diameter / 2.0
b = width
rim = max(2.0 * b, 8.0)            # the uncut outer ring that the hands (or pins) hold
r_hub = max(2.0 * b, 0.12 * R)     # the uncut centre that is lifted
span = turns * arms * b            # radial growth of one cut: `turns` turns, pitch arms·b
if r_hub + span > R - rim:
    raise ValueError(f"{turns} turns of a {b} mm strip do not fit a {diameter} mm disc: lower the "
                     "turns or the width, or enlarge the disc")

sheet = pliego.Sheet("spring", pliego.circle((R, R), R, segments=96), stock=stock,
                     grain_deg=90.0,
                     label=L4("Kirigami spring", "Resorte de kirigami", "Ressort en kirigami",
                              "Mola de kirigami"))
steps = int(math.ceil(turns * 360.0 / SEG_DEG))
for a in range(arms):
    phase = 2.0 * math.pi * a / arms
    pts = []
    for i in range(steps + 1):
        t = turns * 2.0 * math.pi * i / steps          # angle travelled along the cut
        r = r_hub + arms * b * t / (2.0 * math.pi)
        pts.append((R + r * math.cos(t + phase), R + r * math.sin(t + phase)))
    sheet.cut(pts)

report = pliego.papercut.analyze(sheet, min_feature_mm=mf)
if not report.ok:
    raise ValueError("kirigami-spring papercut check failed: "
                     + "; ".join(i["detail"] for i in report.issues if i["level"] == "error"))

ring = R - rim / 2.0
rim_pins = [pliego.pin(f"rim-{k + 1}", (sheet, (R + ring * math.cos(math.pi * k / 4),
                                                R + ring * math.sin(math.pi * k / 4))))
            for k in range(8)]
hub_pins = [pliego.pin(f"hub-{k + 1}",
                       (sheet, (R + 0.5 * r_hub * math.cos(2 * math.pi * k / 3 + math.pi / 2),
                                R + 0.5 * r_hub * math.sin(2 * math.pi * k / 3 + math.pi / 2))),
                       mechanism="lift-hub")
            for k in range(3)]
travel = round(R, 3)
lift = pliego.control("lift", "distance", L4("Lift the centre", "Levantar el centro",
                                             "Soulever le centre", "Levantar o centro"),
                      0.0, 0.0, travel, "mm")
result = pliego.Assembly(
    [sheet],
    joins=rim_pins + hub_pins,
    mechanisms=[pliego.translate("lift-hub", "lift", (0.0, 1.0, 0.0), travel)],
    controls=[lift],
    title="Kirigami spring",
    meta={"min_feature_mm": mf},
)
strip_length = turns * math.pi * (2.0 * r_hub + span)  # per arm: turns × 2π × mean radius
print(f"spring: arms={arms} turns={turns} strip={b}mm hub={r_hub:.1f}mm rim={rim:.1f}mm "
      f"strip_length~{strip_length:.0f}mm min_bridge={report.min_bridge_mm}")
