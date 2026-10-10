"""Stencil — sheet-hyperobjects cartridge (Pliego).

A cut stencil plate: letters and digits cut out of a sheet so that paint or ink can be pushed
through. A letter with a closed counter (A, B, D, O, P, Q, R, 0, 4, 6, 8, 9) would lose its
middle — the island would fall out — so a stencil letter is built from separate strokes with
bridges of paper between them, and every island stays tied to the plate.

The glyphs are generated here, not read from a font file: each is a few stroke centrelines
(straight segments and elliptic arcs) in a unit box of cap height 1, swept to stroke width T with
mitred joins (at a corner sharper than 120°, bevelled outside) and square ends. Strokes never touch:
`fit()` trims the flagged ends of strokes that meet, in small steps, until every pair of strokes is
at least `bridge` apart, and that gap is the bridge. Closed bowls are cut as two halves with a
bridge at the top and the bottom. The glyph set is A–Z, 0–9 and the space; anything else is
refused. `pliego.papercut.analyze` then checks the plate: one connected piece (no island) and
every bridge at least the stock's minimum feature (the bridge is never set below it).

A scored grip strip runs along the top of the plate: the program folds it up (a handle to lift the
plate off wet paint without smudging) and back down flat.
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


MIN_FEATURE = {"pet-125": 1.0, "cardstock-250": 2.0, "cardstock-160": 1.5, "pp-300": 1.5}

text = str(PARAM(lambda: text, "ABOPR"))
height = clamp(PARAM(lambda: height, 40.0), 15.0, 120.0)
bridge = clamp(PARAM(lambda: bridge, 3.0), 1.0, 10.0)
stock = str(PARAM(lambda: stock, "pet-125"))
if stock not in MIN_FEATURE:
    raise ValueError(f"stock {stock!r} is not one this cartridge offers")
mf = MIN_FEATURE[stock]
bridge = max(bridge, mf)
text = text.upper()
if not 1 <= len(text) <= 16:
    raise ValueError("the text must have 1 to 16 characters")

T = 0.16                             # stroke width (unit cap height)
UNIT = (1.0 + T) / height            # mm → unit (the cap height includes the stroke overhang)
G = bridge * UNIT                    # bridge, unit
if G > 0.12:
    raise ValueError("the bridge is too wide for this letter height: lower it or enlarge the text")


def arc(cx, cy, rx, ry, a0, a1, n=None):
    n = n or max(4, int(abs(a1 - a0) / 8))
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def S(pts, start=False, end=False):
    """A stroke: centreline points and which ends may be trimmed back to open a bridge."""
    return (list(pts), start, end)


def ring(cx, cy, rx, ry):
    """A closed bowl as two halves, left and right, trimmed apart at the top and the bottom."""
    return [S(arc(cx, cy, rx, ry, 90, 270), True, True), S(arc(cx, cy, rx, ry, -90, 90), True, True)]


def rot180(strokes, w):
    return [S([(w - x, 1.0 - y) for x, y in reversed(p)], te, ts) for p, ts, te in strokes]


def glyph(ch):
    """(width, strokes) of one character in the unit box (cap height 1). Ends flagged True are
    trimmed back until the stroke clears every other stroke by a bridge."""
    if ch == " ":
        return 0.4, []
    six = [S(arc(0.3, 0.5, 0.3, 0.5, 70, 270)[:-1] + arc(0.3, 0.3, 0.3, 0.3, 270, 455))]
    table = {
        "A": (0.8, [S([(0.0, 0.0), (0.4, 1.0)], False, True),
                    S([(0.8, 0.0), (0.4, 1.0)], False, True),
                    S([(0.0, 0.3), (0.8, 0.3)], True, True)]),
        "B": (0.6, [S([(0.0, 0.0), (0.0, 1.0)]),
                    S([(0.0, 1.0), (0.26, 1.0)] + arc(0.26, 0.81, 0.3, 0.19, 90, -90)
                      + [(0.0, 0.62)], True, True),
                    S([(0.0, 0.38), (0.28, 0.38)] + arc(0.28, 0.19, 0.32, 0.19, 90, -90)
                      + [(0.0, 0.0)], True, True)]),
        "C": (0.6, [S(arc(0.32, 0.5, 0.32, 0.5, 45, 315))]),
        "D": (0.62, [S([(0.0, 0.0), (0.0, 1.0)]),
                     S([(0.0, 1.0), (0.22, 1.0)] + arc(0.22, 0.5, 0.4, 0.5, 90, -90)
                       + [(0.0, 0.0)], True, True)]),
        "E": (0.55, [S([(0.55, 1.0), (0.0, 1.0), (0.0, 0.0), (0.55, 0.0)]),
                     S([(0.0, 0.5), (0.45, 0.5)], True)]),
        "F": (0.55, [S([(0.55, 1.0), (0.0, 1.0), (0.0, 0.0)]), S([(0.0, 0.5), (0.42, 0.5)], True)]),
        "G": (0.64, [S(arc(0.32, 0.5, 0.32, 0.5, 40, 320) + [(0.62, 0.42), (0.36, 0.42)])]),
        "H": (0.6, [S([(0.0, 0.0), (0.0, 1.0)]), S([(0.6, 0.0), (0.6, 1.0)]),
                    S([(0.0, 0.5), (0.6, 0.5)], True, True)]),
        "I": (0.0, [S([(0.0, 0.0), (0.0, 1.0)])]),
        "J": (0.5, [S([(0.5, 1.0), (0.5, 0.28)] + arc(0.25, 0.28, 0.25, 0.28, 0, -180)[1:])]),
        "K": (0.66, [S([(0.0, 0.0), (0.0, 1.0)]), S([(0.62, 1.0), (0.32, 0.5), (0.66, 0.0)])]),
        "L": (0.55, [S([(0.0, 1.0), (0.0, 0.0), (0.55, 0.0)])]),
        "M": (0.8, [S([(0.0, 0.0), (0.0, 1.0), (0.4, 0.3), (0.8, 1.0), (0.8, 0.0)])]),
        "N": (0.66, [S([(0.0, 0.0), (0.0, 1.0), (0.66, 0.0), (0.66, 1.0)])]),
        "O": (0.6, ring(0.3, 0.5, 0.3, 0.5)),
        "P": (0.6, [S([(0.0, 0.0), (0.0, 1.0)]),
                    S([(0.0, 1.0), (0.26, 1.0)] + arc(0.26, 0.74, 0.32, 0.26, 90, -90)
                      + [(0.0, 0.48)], True, True)]),
        "Q": (0.66, ring(0.32, 0.52, 0.32, 0.48) + [S([(0.54, 0.12), (0.8, -0.16)], True)]),
        "R": (0.64, [S([(0.0, 0.0), (0.0, 1.0)]),
                     S([(0.0, 1.0), (0.26, 1.0)] + arc(0.26, 0.74, 0.32, 0.26, 90, -90)
                       + [(0.0, 0.48)], True, True),
                     S([(0.26, 0.48), (0.64, 0.0)], True)]),
        "S": (0.6, [S(arc(0.3, 0.75, 0.3, 0.25, 15, 270)[:-1] + arc(0.3, 0.25, 0.3, 0.25, 90, -165))]),
        "T": (0.6, [S([(0.0, 1.0), (0.6, 1.0)]), S([(0.3, 1.0), (0.3, 0.0)], True)]),
        "U": (0.6, [S([(0.0, 1.0), (0.0, 0.3)] + arc(0.3, 0.3, 0.3, 0.3, 180, 360)[1:-1]
                      + [(0.6, 0.3), (0.6, 1.0)])]),
        "V": (0.64, [S([(0.0, 1.0), (0.32, 0.0), (0.64, 1.0)])]),
        "W": (0.92, [S([(0.0, 1.0), (0.23, 0.0), (0.46, 0.72), (0.69, 0.0), (0.92, 1.0)])]),
        "X": (0.6, [S([(0.0, 0.0), (0.6, 1.0)]), S([(0.0, 1.0), (0.3, 0.5)], False, True),
                    S([(0.3, 0.5), (0.6, 0.0)], True)]),
        "Y": (0.64, [S([(0.0, 1.0), (0.32, 0.5), (0.64, 1.0)]), S([(0.32, 0.5), (0.32, 0.0)], True)]),
        "Z": (0.6, [S([(0.0, 1.0), (0.6, 1.0), (0.0, 0.0), (0.6, 0.0)])]),
        "0": (0.52, ring(0.26, 0.5, 0.26, 0.5)),
        "1": (0.3, [S([(0.0, 0.8), (0.3, 1.0), (0.3, 0.0)])]),
        "2": (0.6, [S(arc(0.3, 0.7, 0.3, 0.3, 160, -10) + [(0.0, 0.0), (0.6, 0.0)])]),
        "3": (0.6, [S(arc(0.28, 0.75, 0.3, 0.25, 150, -90)[:-1] + [(0.12, 0.5)]),
                    S([(0.12, 0.5)] + arc(0.28, 0.25, 0.3, 0.25, 90, -150), True)]),
        "4": (0.6, [S([(0.36, 1.0), (0.0, 0.32), (0.56, 0.32)], False, True),
                    S([(0.56, 0.72), (0.56, 0.0)])]),
        "5": (0.6, [S([(0.56, 1.0), (0.05, 1.0), (0.05, 0.56)] + arc(0.28, 0.32, 0.31, 0.32, 100, -155))]),
        "6": (0.6, six),
        "7": (0.6, [S([(0.0, 1.0), (0.6, 1.0), (0.2, 0.0)])]),
        "8": (0.6, ring(0.3, 0.81, 0.25, 0.19) + ring(0.3, 0.19, 0.3, 0.19)),
        "9": (0.6, rot180(six, 0.6)),
    }
    if ch not in table:
        raise ValueError(f"character {ch!r} is not in the stencil's glyph set (A–Z, 0–9, space)")
    return table[ch]


def sweep(line, t):
    """Polygon of a stroke of width t along a centreline: square ends, mitred joins, and at a
    corner sharper than 120° a bevel on the outer side and the offset-line crossing inside."""
    pts = [p for i, p in enumerate(line) if i == 0 or math.dist(p, line[i - 1]) > 1e-9]
    left, right = [], []
    n = len(pts)
    for i in range(n):
        if i in (0, n - 1):
            a, b = (pts[0], pts[1]) if i == 0 else (pts[-2], pts[-1])
            d = math.dist(a, b)
            nx, ny = -(b[1] - a[1]) / d, (b[0] - a[0]) / d
            left.append((pts[i][0] + nx * t / 2, pts[i][1] + ny * t / 2))
            right.append((pts[i][0] - nx * t / 2, pts[i][1] - ny * t / 2))
            continue
        p0, p1, p2 = pts[i - 1], pts[i], pts[i + 1]
        d1, d2 = math.dist(p0, p1), math.dist(p1, p2)
        n1 = (-(p1[1] - p0[1]) / d1, (p1[0] - p0[0]) / d1)
        n2 = (-(p2[1] - p1[1]) / d2, (p2[0] - p1[0]) / d2)
        bx, by = n1[0] + n2[0], n1[1] + n2[1]
        bl = math.hypot(bx, by)
        cosh = bl / 2.0                                   # cos of half the turn
        mx, my = bx / bl * (t / 2) / cosh, by / bl * (t / 2) / cosh
        if cosh >= 0.5:
            left.append((p1[0] + mx, p1[1] + my))
            right.append((p1[0] - mx, p1[1] - my))
            continue
        turn = (p1[0] - p0[0]) * (p2[1] - p1[1]) - (p1[1] - p0[1]) * (p2[0] - p1[0])
        outer, inner, sign = (right, left, -1) if turn > 0 else (left, right, 1)
        inner.append((p1[0] - sign * mx, p1[1] - sign * my))
        outer.append((p1[0] + sign * n1[0] * t / 2, p1[1] + sign * n1[1] * t / 2))
        outer.append((p1[0] + sign * n2[0] * t / 2, p1[1] + sign * n2[1] * t / 2))
    return left + right[::-1]


def seg_dist(p, a, b):
    abx, aby = b[0] - a[0], b[1] - a[1]
    dd = abx * abx + aby * aby
    k = 0.0 if dd == 0 else max(0.0, min(1.0, ((p[0] - a[0]) * abx + (p[1] - a[1]) * aby) / dd))
    return math.hypot(p[0] - a[0] - k * abx, p[1] - a[1] - k * aby)


def inside(p, poly):
    hit = False
    for i in range(len(poly)):
        (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % len(poly)]
        if (y1 > p[1]) != (y2 > p[1]) and p[0] < x1 + (p[1] - y1) * (x2 - x1) / (y2 - y1):
            hit = not hit
    return hit


def clearance(pa, pb):
    """Smallest distance between two polygons (0 when one reaches into the other)."""
    if any(inside(p, pb) for p in pa) or any(inside(p, pa) for p in pb):
        return 0.0
    best = float("inf")
    for P1, P2 in ((pa, pb), (pb, pa)):
        for p in P1:
            for i in range(len(P2)):
                best = min(best, seg_dist(p, P2[i], P2[(i + 1) % len(P2)]))
    return best


def trim(line, length, at_start):
    pts = list(line) if at_start else list(reversed(line))
    while length > 1e-12 and len(pts) >= 2:
        d = math.dist(pts[0], pts[1])
        if d > length + 1e-9:
            k = length / d
            pts[0] = (pts[0][0] + (pts[1][0] - pts[0][0]) * k, pts[0][1] + (pts[1][1] - pts[0][1]) * k)
            length = 0.0
        else:
            length -= d
            pts.pop(0)
    if len(pts) < 2:
        raise ValueError("a stroke was trimmed away entirely")
    return pts if at_start else list(reversed(pts))


def fit(strokes):
    """Trim flagged ends in small steps until every pair of strokes is a bridge apart. For each
    pair still too close, the flagged end nearest the other stroke is trimmed (both, on a tie)."""
    strokes = [list(s) for s in strokes]
    step = 0.004

    def tip_gap(i, at_start, poly):
        tip = strokes[i][0][0] if at_start else strokes[i][0][-1]
        return min(seg_dist(tip, poly[k], poly[(k + 1) % len(poly)]) for k in range(len(poly)))

    for _ in range(500):
        polys = [sweep(s[0], T) for s in strokes]
        cuts = set()
        for i in range(len(strokes)):
            for j in range(i + 1, len(strokes)):
                if clearance(polys[i], polys[j]) >= G * 1.02:
                    continue
                cand = [(tip_gap(a, end, polys[b]), a, end)
                        for a, b in ((i, j), (j, i))
                        for end, flag in ((True, strokes[a][1]), (False, strokes[a][2])) if flag]
                cand = [c for c in cand if c[0] < T + 2 * G]
                if cand:
                    low = min(c[0] for c in cand)
                    cuts.update((a, end) for d, a, end in cand if d <= low + 1e-6)
        if not cuts:
            break
        for a, end in cuts:
            strokes[a][0] = trim(strokes[a][0], step, end)
    polys = [sweep(s[0], T) for s in strokes]
    for i in range(len(polys)):
        for j in range(i + 1, len(polys)):
            if clearance(polys[i], polys[j]) < G:
                raise ValueError("two strokes of a glyph cannot be separated by a bridge")
    return polys


glyphs = [glyph(ch) for ch in text]
H = height
scale = 1.0 / UNIT
margin = max(12.0, 0.5 * H)
track = 0.28                                  # space between glyphs, unit
x = margin * UNIT + T / 2
polys = []
for wdt, strokes in glyphs:
    for poly in fit([S([(x + px, py) for px, py in p], ts, te) for p, ts, te in strokes]):
        polys.append([(px * scale, margin + (py + T / 2) * scale) for px, py in poly])
    x += wdt + T + track
plate_w = (x - track - T / 2) * scale + margin
plate_h = H + 2 * margin
sheet = pliego.Sheet("stencil", pliego.rectangle(plate_w, plate_h + 25.0), stock=stock,
                     grain_deg=0.0, label=L4("Stencil plate", "Plantilla de estarcido",
                                             "Plaque de pochoir", "Placa de estêncil"))
for poly in polys:
    sheet.hole(poly)
grip = sheet.crease((0.0, plate_h), (plate_w, plate_h), "mountain", 90.0, treatment="score",
                    label=L4("Grip tab", "Pestaña para sujetar", "Languette de prise",
                             "Aba para segurar"))
report = pliego.papercut.analyze(sheet, min_feature_mm=mf)
if not report.ok:
    raise ValueError("stencil papercut check failed: "
                     + "; ".join(i["detail"] for i in report.issues if i["level"] == "error"))

steps = [
    pliego.Step("fold-grip", L4("Fold the grip tab up along its score",
                                "Dobla hacia arriba la pestaña por su marca",
                                "Relever la languette le long de sa rainure",
                                "Dobre a aba para cima pelo vinco"),
                [(grip, -90.0)], duration_ms=1500),
    pliego.Step("lay-flat", L4("Fold it back down: the plate lies flat to stencil",
                               "Vuelve a bajarla: la plantilla queda plana para estarcir",
                               "La rabattre : la plaque est à plat pour pochoir",
                               "Baixe-a de novo: a placa fica plana para estampar"),
                [(grip, 0.0)], duration_ms=1500),
]
result = pliego.Assembly(
    [sheet],
    controls=[pliego.sequence_control(label=L4("Handle", "Manejar", "Manipuler", "Manusear"))],
    sequence=pliego.Sequence(steps, mode="physical"),
    title="Stencil",
    meta={"min_feature_mm": mf},
)
print(f"stencil: text={text!r} glyphs={len(glyphs)} strokes={len(polys)} bridge={bridge}mm "
      f"plate={plate_w:.0f}x{plate_h + 25:.0f}mm min_bridge={report.min_bridge_mm}")
