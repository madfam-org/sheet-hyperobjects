"""Paper doily — sheet-hyperobjects cartridge (Pliego).

Radial lace by fold-and-cut. A square is folded through its centre into a wedge of 180°/n with 2n
layers (`pliego.simplefold`; n = 4, 6 or 8, as for a snowflake), and one cut through every layer
(`pliego.foldcut`) unfolds into a round doily with n-fold rotation and n mirror lines. The lace is
generated from the `density` parameter: a scalloped edge with a picot hole in every scallop, then
density + 2 concentric rings of small holes — circles, radial diamonds and petals in turn — with as
many holes per ring as its circumference allows at a fixed bridge, and a petal rosette at the
centre. All motifs are original generic geometry. `pliego.papercut.analyze` checks one connected
piece and the stock's minimum feature, and the script refuses to build otherwise.

The fold program re-folds the cut sheet in the original order, then opens it and presses it flat.
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


MIN_FEATURE = {"copy-80": 1.0, "kami": 1.0, "washi-kozo-30": 1.0, "papel-de-china": 1.5}
FOLDS = {
    4: [(0.0, "valley"), (270.0, "valley"), (225.0, "valley")],
    6: [(225.0, "valley"), (165.0, "valley"), (285.0, "mountain"), (315.0, "valley")],
    8: [(0.0, "valley"), (270.0, "valley"), (225.0, "valley"), (202.5, "valley")],
}

folds = int(PARAM(lambda: folds, 8))
density = int(clamp(PARAM(lambda: density, 3), 1, 5))
size = clamp(PARAM(lambda: size, 200.0), 120.0, 300.0)
stock = str(PARAM(lambda: stock, "copy-80"))
if folds not in FOLDS:
    raise ValueError("folds must be 4, 6 or 8")
if stock not in MIN_FEATURE:
    raise ValueError(f"stock {stock!r} is not one this cartridge offers")
mf = MIN_FEATURE[stock]
n = folds
alpha = math.pi / n

cx = cy = size / 2.0
state = pliego.simplefold.FoldedState(pliego.square(size))
crease_counts = []
for angle, kind in FOLDS[n]:
    a = math.radians(angle)
    state.fold(((cx, cy), (cx + math.cos(a), cy + math.sin(a))), kind)
    crease_counts.append(len(state.creases))
if len(state.layers) != 2 * n:
    raise ValueError(f"expected {2 * n} layers, the folds made {len(state.layers)}")
image = state.layers[-1].image()
angles = sorted(math.atan2(p.y - cy, p.x - cx) % (2 * math.pi) for p in image
                if math.hypot(p.x - cx, p.y - cy) > 1e-6)
if max(angles) - min(angles) > math.pi:  # the wedge straddles angle 0
    angles = sorted((t + math.pi) % (2 * math.pi) - math.pi for t in angles)
theta0 = min(angles)
if abs((max(angles) - theta0) - alpha) > 1e-6:
    raise ValueError("the folds did not make the expected wedge")


def P(r, phi):
    return (cx + r * math.cos(theta0 + phi), cy + r * math.sin(theta0 + phi))


def disc(r, phi, rad, k=10):
    c = P(r, phi)
    return [(c[0] + rad * math.cos(2 * math.pi * i / k), c[1] + rad * math.sin(2 * math.pi * i / k))
            for i in range(k)]


def diamond(r, phi, half_len, half_wid):
    return [P(r - half_len, phi), P(r, phi + half_wid / r), P(r + half_len, phi),
            P(r, phi - half_wid / r)]


def petal(r_a, r_b, phi, half_width):
    pts = []
    for i in range(9):
        t = i / 8
        r = r_a + (r_b - r_a) * t
        pts.append((r, phi + half_width * math.sin(math.pi * t) ** 0.8 / r))
    pts += [(r, 2 * phi - p) for r, p in reversed(pts[1:-1])]
    return [P(r, p) for r, p in pts]


R = 0.47 * size
regions = []
# edge: scallops (up to density + 1 per wedge, as many as fit), a picot hole in each
picot = 1.2 * mf
q = max(1, min(density + 1, int(0.9 * R * alpha // (2.0 * picot + 3.0 * mf))))
depth = min(0.06 * R, 0.5 * R * alpha / q)
edge = [(R - depth * (1 - abs(math.sin(math.pi * i / 8))), alpha * i / (8 * q))
        for i in range(8 * q + 1)]
pad = math.radians(3.0)
regions.append([P(r, p) for r, p in edge] + [P(size, alpha + pad), P(size, -pad)])


def lace(scale, inset):
    """Picots, lace rings and rosette, holes scaled by `scale`, picots `inset` minimum features
    in from the scallops; returns (regions, holes)."""
    out, holes = [], 0
    r_picot = R - depth - picot - inset * mf
    for k in range(q):
        out.append(disc(r_picot, alpha * (k + 0.5) / q, picot, 8))
    # rings of lace between the rosette and the scallops
    r_in, r_out = 0.2 * R, r_picot - picot - 2.5 * mf
    rings = max(1, min(density + 2, int((r_out - r_in) // (4.0 * mf))))
    pitch = (r_out - r_in) / rings
    for k in range(rings):
        r = r_in + (k + 0.5) * pitch
        hole = 0.55 * pitch * scale        # radial extent of each hole
        across = min(hole, 0.6 * pitch)    # tangential extent
        arc = (r - hole / 2.0) * alpha     # the wedge's width at the hole's inner end
        count = max(1, int(arc // (across + 2.5 * mf)))
        across = min(across, arc / count - 2.5 * mf)
        if across < 2.0 * mf:
            continue                       # too narrow here for a hole and its bridges
        for j in range(count):
            phi = (j + 0.5) * alpha / count
            shape = k % 3
            if shape == 0:
                out.append(disc(r, phi, min(hole, across) / 2.0))
            elif shape == 1:
                out.append(diamond(r, phi, hole / 2.0, across / 2.5))
            else:
                out.append(petal(r - hole / 2.0, r + hole / 2.0, phi, across / 2.5))
            holes += 1
    # centre rosette: one petal per wedge on its axis, a round hole in the middle
    rosette = min(0.035 * R, 0.11 * R * math.sin(alpha / 2) - mf)
    if rosette >= mf:
        out.append(petal(0.05 * R, 0.17 * R, alpha / 2, rosette))
    out.append([P(0.03 * R, 2 * math.pi * i / 12 - theta0) for i in range(12)])
    return out, holes


LABEL = L4("Paper doily", "Carpeta de papel", "Napperon en papier", "Toalhinha de papel")


def simple_faces(sheet):
    arr = sheet.build()
    return all(pliego.geometry.is_simple_polygon([arr.vertices[v] for v in f]) for f in arr.faces)


# The kernel's hole bridging occasionally leaves a self-touching face for some lace layouts (a
# kernel 0.2.0 issue, reported). Try the layout as designed, then with the picots moved further in
# and the holes shrunk in 3 % steps, until every face is simple.
for inset, scale in [(i, 1.0 - 0.03 * k) for i in (1.5, 4.0) for k in range(4)]:
    lace_regions, holes = lace(scale, inset)
    cut = pliego.foldcut.cut(state, regions + lace_regions, id="doily", stock=stock,
                             grain_deg=90.0, label=LABEL, front="#fbf8f1", back="#fbf8f1")
    if simple_faces(cut.sheet):
        break
else:
    raise ValueError("the lace layout leaves a face the kernel cannot bridge: change the size "
                     "or the density")
regions = regions + lace_regions
if not cut.connected:
    raise ValueError(f"the cut leaves {len(cut.islands)} loose pieces")
report = pliego.papercut.analyze(cut.sheet, min_feature_mm=mf)
if not report.ok:
    raise ValueError("paper-doily papercut check failed: "
                     + "; ".join(i["detail"] for i in report.issues if i["level"] == "error"))

sheet = cut.sheet
creases = [m for m in sheet.marks if m.assignment in ("M", "V") and m.edges()]
groups, start = [], 0
for end in crease_counts:
    groups.append([m for m in sheet.marks[start:end] if m.assignment in ("M", "V") and m.edges()])
    start = end
fold_word = L4("Fold through the centre", "Dobla por el centro", "Plier par le centre",
               "Dobre pelo centro")
steps = [pliego.Step(f"fold-{k + 1}", {lang: f"{text} ({k + 1}/{len(groups)})"
                                       for lang, text in fold_word.items()},
                     [(m, None) for m in group]) for k, group in enumerate(groups)]
steps.append(pliego.Step("cut-and-open", L4("Cut the lace through every layer, then unfold and "
                                            "press flat",
                                            "Corta el encaje a través de todas las capas, "
                                            "desdobla y alisa",
                                            "Découper la dentelle à travers toutes les couches, "
                                            "déplier et aplatir",
                                            "Corte a renda através de todas as camadas, desdobre "
                                            "e alise"),
                         [(m, 0.0) for m in creases], duration_ms=3000))
result = pliego.Assembly(
    [sheet],
    controls=[pliego.sequence_control()],
    sequence=pliego.Sequence(steps, mode="physical"),
    title="Paper doily",
    meta={"min_feature_mm": mf},
)
print(f"paper-doily: folds={n} density={density} holes_per_wedge={holes} hole_scale={scale:.2f} "
      f"picot_inset={inset} "
      f"min_bridge={report.min_bridge_mm}")
