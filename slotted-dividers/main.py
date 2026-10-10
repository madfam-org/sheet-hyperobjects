"""Slotted dividers — sheet-hyperobjects cartridge (Pliego).

Interlocking partitions: board strips with half-height slots that cross-lock into a grid of
cells, the insert that keeps bottles, jars or parts apart inside a shipping case. Generated from
the cell grid (``columns`` × ``rows`` cells of ``cell_length`` × ``cell_width`` inside, ``height``
tall) in greyboard or corrugated board.

- **Strips.** ``rows − 1`` long partitions run the box's length and ``columns − 1`` cross
  partitions run its width; the outside walls are the case's own. A long strip is
  ``columns·cell_length + (columns − 1)·t`` long, a cross strip ``rows·cell_width + (rows − 1)·t``
  (t = the board caliper: every partition between two cells takes t of the length).
- **Slots.** Long strips are slotted from the top and cross strips from the bottom, each slot
  **half the height deep** and **one caliper wide**, centred on the crossing partition's
  centre line, so the two halves meet flush. The script checks the slot geometry against the
  caliper and the strips with ``pliego.papercut.analyze``.
- **Assembled cells form the initial frame**: every strip is a rigid board standing in its
  plane, the long strips fixed, the cross strips on a ``translate`` mechanism; the ``lift``
  control raises the cross strips straight out of their slots (half the height plus a margin)
  and lowers them back — the preview drives it.

**Limits.** The strips' contact in the slots is edge-to-edge contact, which the engine does not
model in v0.1: nothing stops a strip from passing through another, and the grid's stiffness,
friction and the slots' fit (exactly one caliper here; makers often add a fraction of a
millimetre) need the physics engine. Corrugated strips are cut with the flutes running up the
height (grain along the strip's length), the stiffer way for a partition.
"""

import math

import pliego


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


def L4(en, es, fr, pt):
    return {"en": en, "es": es, "fr": fr, "pt": pt}


columns = round(float(PARAM(lambda: columns, 4)))        # noqa: F821 - cells along the length
rows = round(float(PARAM(lambda: rows, 3)))              # noqa: F821 - cells across
cell_length = float(PARAM(lambda: cell_length, 70.0))    # noqa: F821
cell_width = float(PARAM(lambda: cell_width, 70.0))      # noqa: F821
height = float(PARAM(lambda: height, 120.0))             # noqa: F821
stock = str(PARAM(lambda: stock, "corrugated-e-flute"))  # noqa: F821

STOCKS = ("corrugated-e-flute", "corrugated-b-flute", "corrugated-c-flute", "greyboard-1500")
if stock not in STOCKS:
    raise ValueError(f"slotted-dividers: stock must be one of {STOCKS}, got {stock!r}")
columns = int(pliego.clamp(columns, 2, 8))
rows = int(pliego.clamp(rows, 2, 8))
cell_length = pliego.clamp(cell_length, 25.0, 250.0)
cell_width = pliego.clamp(cell_width, 25.0, 250.0)
height = pliego.clamp(height, 30.0, 400.0)

t = pliego.board.caliper(stock)
family = "corrugated" if stock.startswith("corrugated") else "board"
Lb = columns * cell_length + (columns - 1) * t       # long strips (box inside length)
Wb = rows * cell_width + (rows - 1) * t              # cross strips (box inside width)
H = height
slot_w, slot_d = t, H / 2.0
xs = [j * (cell_length + t) - t / 2.0 for j in range(1, columns)]   # cross partitions' centres
zs = [i * (cell_width + t) - t / 2.0 for i in range(1, rows)]       # long partitions' centres

# slot geometry against the caliper (fail loud)
checks = [("slot width = caliper", abs(slot_w - t) < 1e-9),
          ("slot depth = half the height", abs(2 * slot_d - H) < 1e-9),
          ("slots clear of the strip ends", xs[0] - slot_w / 2 > 0 and zs[0] - slot_w / 2 > 0),
          ("material between slots ≥ 3 caliper", min(cell_length, cell_width) >= 3 * t)]
bad = [name for name, ok in checks if not ok]
if bad:
    raise ValueError("slotted-dividers: slot check failed: " + ", ".join(bad))


def strip_outline(length, centres, from_top):
    """A strip's outline with slot_w-wide, slot_d-deep slots at the given centres."""
    pts = [(0.0, 0.0)]
    if not from_top:
        for c in centres:
            pts += [(c - slot_w / 2, 0.0), (c - slot_w / 2, slot_d), (c + slot_w / 2, slot_d),
                    (c + slot_w / 2, 0.0)]
    pts += [(length, 0.0), (length, H)]
    if from_top:
        for c in reversed(centres):
            pts += [(c + slot_w / 2, H), (c + slot_w / 2, H - slot_d), (c - slot_w / 2, H - slot_d),
                    (c - slot_w / 2, H)]
    return pts + [(0.0, H)]


S = math.sqrt(0.5)
STAND_X = (S, 0.0, 0.0, S)                 # +90° about X: sheet (u, v) → world (u, v, 0)
STAND_Z = (0.5, -0.5, 0.5, 0.5)            # then −90° about Y: sheet (u, v) → world (0, v, u)
LONG = L4("Long partition", "Separador largo", "Croisillon long", "Divisória longa")
CROSS = L4("Cross partition", "Separador transversal", "Croisillon transversal",
           "Divisória transversal")
packs, report = [], []
for kind, count, length, centres, from_top, label in (
        ("long", rows - 1, Lb, xs, True, LONG), ("cross", columns - 1, Wb, zs, False, CROSS)):
    for k in range(count):
        sid = f"{kind}-{k + 1}"
        d = pliego.dieline.Dieline(
            sid, f"slotted partition ({'slots from the top' if from_top else 'slots from the bottom'})",
            family, {"length": cell_length, "width": cell_width, "depth": H}, stock, t,
            label={g: f"{v} {k + 1}" for g, v in label.items()}, grain_deg=0.0)
        d.panel("strip", strip_outline(length, centres, from_top), "panel",
                {g: f"{v} {k + 1}" for g, v in label.items()}, print_area=False)
        d.dimension((0.0, 0.0), (length, 0.0), f"{length:.1f}", -8.0)
        d.dimension((0.0, 0.0), (0.0, H), f"{H:g}", 8.0)
        pack = d.build(rest_on="strip")
        sheet = pack.sheet
        if kind == "long":
            sheet.placement = pliego.Placement(origin=(0.0, 0.0, zs[k]), rotation=STAND_X)
        else:
            sheet.placement = pliego.Placement(origin=(xs[k], 0.0, 0.0), rotation=STAND_Z)
        sheet.kinematic = "lift-cross"
        rep = pliego.papercut.analyze(sheet, min_feature_mm=max(1.0, t))
        errors = [i["detail"] for i in rep.issues if i["level"] == "error"]
        if errors:
            raise ValueError(f"slotted-dividers: {sid}: " + "; ".join(errors))
        report.append(rep.min_bridge_mm)
        packs.append(pack)

travel = round(0.5 * H + max(10.0, 0.2 * H), 1)
cross_sheets = [p.sheet for p in packs if p.sheet.id.startswith("cross")]
area = (rows - 1) * Lb * H + (columns - 1) * Wb * H
print(f"slotted-dividers: {columns}x{rows} cells, {rows - 1} long + {columns - 1} cross strips, "
      f"slots {slot_w:.2f} x {slot_d:.1f} mm, board {area / 1e6:.3f} m², papercut ok "
      f"({len(report)} strips), lift {travel} mm")
result = pliego.Assembly(
    [p.sheet for p in packs],
    mechanisms=[pliego.translate("lift-cross", "lift", (0.0, 1.0, 0.0), travel, cross_sheets)],
    controls=[pliego.control("lift", "distance",
                             L4("Lift the cross partitions out", "Saca los separadores "
                                "transversales", "Soulever les croisillons transversaux",
                                "Levante as divisórias transversais"), 0.0, 0.0, travel, "mm")],
    dielines=[p.block for p in packs], title=f"Slotted dividers ({columns} × {rows} cells)",
    meta={"cartridge": "slotted-dividers",
          "params": {"columns": columns, "rows": rows, "cell_length": cell_length,
                     "cell_width": cell_width, "height": height, "stock": stock}})
