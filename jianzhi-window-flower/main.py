"""Jianzhi window flower — sheet-hyperobjects cartridge (Pliego).

Radial fold-and-cut in the idiom of Chinese paper-cut window flowers (chuanghua). A square of red
paper is folded through its centre into a wedge of 180°/n with 2n layers (`pliego.simplefold`):

- 4-fold: in half, in half again, then along the diagonal (a 45° wedge, 8 layers);
- 6-fold: along the diagonal, into thirds, then in half (a 30° wedge, 12 layers);
- 8-fold: the 4-fold wedge folded in half once more (22.5°, 16 layers).

One cut through every layer (`pliego.foldcut`) then unfolds into a design with n-fold rotation
and n mirror lines (dihedral symmetry Dn). The motifs are ORIGINAL geometric shapes generated
here — a scalloped round edge with a small hole in each scallop, rings of petals, crescents and
diamonds, a round centre — in a generic radial idiom; no traditional artwork is reproduced.
`pliego.papercut.analyze` checks one connected piece and the stock's minimum feature, and the
script refuses to build otherwise.

The fold program re-folds the cut sheet along its creases in the original order, then opens it and
presses it flat (targets back to 0°: the hand unfolds and holds it, as a window flower is pasted
flat). It does not let go: a release would leave each crease standing at its yield angle (spec
§5.6), which is the paper's memory but not how the finished piece is shown.
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


MIN_FEATURE = {"papel-de-china": 1.5, "kami": 1.0, "washi-kozo-30": 1.0, "copy-80": 1.0}
COLOURS = {"papel-de-china": "#c8102e", "kami": "#c8102e", "washi-kozo-30": "#b5121b",
           "copy-80": "#d0202e"}
# directed fold lines through the centre (degrees) and their direction; the stack ends in a wedge
FOLDS = {
    4: [(0.0, "valley"), (270.0, "valley"), (225.0, "valley")],
    6: [(225.0, "valley"), (165.0, "valley"), (285.0, "mountain"), (315.0, "valley")],
    8: [(0.0, "valley"), (270.0, "valley"), (225.0, "valley"), (202.5, "valley")],
}

folds = int(PARAM(lambda: folds, 6))
size = clamp(PARAM(lambda: size, 180.0), 120.0, 300.0)
style = str(PARAM(lambda: style, "blossom"))
stock = str(PARAM(lambda: stock, "papel-de-china"))
if folds not in FOLDS:
    raise ValueError("folds must be 4, 6 or 8")
if style not in ("blossom", "lantern"):
    raise ValueError(f"style {style!r} must be blossom or lantern")
if stock not in MIN_FEATURE:
    raise ValueError(f"stock {stock!r} is not one this cartridge offers")
mf = MIN_FEATURE[stock]
n = folds
alpha = math.pi / n                       # wedge angle

# ── fold ──
cx = cy = size / 2.0
state = pliego.simplefold.FoldedState(pliego.square(size))
crease_counts = []
for angle, kind in FOLDS[n]:
    a = math.radians(angle)
    state.fold(((cx, cy), (cx + math.cos(a), cy + math.sin(a))), kind)
    crease_counts.append(len(state.creases))
if len(state.layers) != 2 * n:
    raise ValueError(f"expected {2 * n} layers, the folds made {len(state.layers)}")
# the wedge: the angular range of the stack's image around the centre
image = state.layers[-1].image()
angles = sorted(math.atan2(p.y - cy, p.x - cx) % (2 * math.pi) for p in image
                if math.hypot(p.x - cx, p.y - cy) > 1e-6)
spread = max(angles) - min(angles)
if spread > math.pi:  # the wedge straddles angle 0
    angles = sorted((t + math.pi) % (2 * math.pi) - math.pi for t in angles)
theta0 = min(angles)
if abs((max(angles) - theta0) - alpha) > 1e-6:
    raise ValueError("the folds did not make the expected wedge")


def P(r, phi):
    """Point at radius r and angle phi inside the wedge (phi from 0 to alpha)."""
    return (cx + r * math.cos(theta0 + phi), cy + r * math.sin(theta0 + phi))


def petal(r_a, r_b, phi, half_width):
    """A pointed petal along the ray phi, from r_a to r_b, half-width at its widest."""
    pts = []
    for i in range(13):
        t = i / 12
        r = r_a + (r_b - r_a) * t
        wdt = half_width * math.sin(math.pi * t) ** 0.8
        pts.append((r, phi + wdt / r))
    pts += [(r, phi - (p - phi)) for r, p in reversed(pts[1:-1])]
    return [P(r, p) for r, p in pts]


def disc(r, phi, rad, k=16):
    c = P(r, phi)
    return [(c[0] + rad * math.cos(2 * math.pi * i / k), c[1] + rad * math.sin(2 * math.pi * i / k))
            for i in range(k)]


def diamond(r, phi, half_len, half_wid):
    return [P(r - half_len, phi), P(r, phi + half_wid / r), P(r + half_len, phi),
            P(r, phi - half_wid / r)]


def local(r0, phi, pts):
    """Map local points (x along the ray at angle phi, y across it) placed at radius r0."""
    c, u = P(r0, phi), (math.cos(theta0 + phi), math.sin(theta0 + phi))
    return [(c[0] + x * u[0] - y * u[1], c[1] + x * u[1] + y * u[0]) for x, y in pts]


def crescent(r0, phi, rad, shift):
    """A crescent opening outward: a disc of radius rad minus the same disc moved out by shift."""
    h = math.sqrt(rad * rad - (shift / 2) ** 2)
    g = math.atan2(h, shift / 2)
    pts = [(rad * math.cos(g + (2 * math.pi - 2 * g) * i / 24),
            rad * math.sin(g + (2 * math.pi - 2 * g) * i / 24)) for i in range(25)]
    pts += [(shift + rad * math.cos(math.pi + g - 2 * g * i / 12),
             rad * math.sin(math.pi + g - 2 * g * i / 12)) for i in range(1, 12)]
    return local(r0, phi, pts)


def arch(r_a, r_b, phi, half_width):
    """An arched window along the ray phi: straight sides from r_a, a round top reaching r_b."""
    top = r_b - r_a - half_width
    pts = [(0.0, -half_width), (top, -half_width)]
    pts += [(top + half_width * math.sin(math.pi * i / 12),
             -half_width * math.cos(math.pi * i / 12)) for i in range(1, 12)]
    pts += [(top, half_width), (0.0, half_width)]
    return local(r_a, phi, pts)


R = 0.47 * size
regions = []
# outer edge: scallops (two per wedge), each with a small round hole
q = 2
edge = [(R - 0.07 * R * (1 - abs(math.sin(math.pi * q * (alpha * i / 16) / alpha))), alpha * i / 16)
        for i in range(17)]
big = size
pad = math.radians(3.0)
regions.append([P(r, p) for r, p in edge] + [P(big, alpha + pad), P(big, -pad)])
for k in range(q):
    regions.append(disc(0.885 * R, alpha * (k + 0.5) / q, max(0.022 * R, 1.5 * mf)))
# centre: a round hole inside a solid hub
regions.append([P(0.06 * R, 2 * math.pi * i / 24 - theta0) for i in range(24)])
# band A: petals between the hub and the first ring
r1, r2 = 0.17 * R, 0.46 * R
mid = alpha / 2
regions.append(petal(r1 + 2 * mf, r2 - 2 * mf, mid,
                     min(0.32 * (r1 + r2) / 2 * mid, (r1 + r2) / 2 * mid - 1.5 * mf)))
if style == "blossom":
    # small diamonds on the mirror lines, between the petals
    regions.append(diamond((r1 + r2) / 2 + 0.06 * R, 0.0, 0.08 * R, 0.022 * R))
    regions.append(diamond((r1 + r2) / 2 + 0.06 * R, alpha, 0.08 * R, 0.022 * R))
    # band B: a crescent on the wedge axis and a round hole on each mirror line
    r3, r4 = 0.53 * R, 0.78 * R
    avail = (r3 + r4) / 2 * math.sin(mid)   # half the wedge's width across band B
    rad = min(0.105 * R, 0.5 * avail)
    regions.append(crescent((r3 + r4) / 2, mid, rad, 0.67 * rad))
    for phi in (0.0, alpha):
        regions.append(disc((r3 + r4) / 2, phi, min(0.045 * R, 0.3 * avail)))
else:  # lantern: a ring of arched windows, diamonds between them
    r3, r4 = 0.53 * R, 0.78 * R
    half = min(0.5 * r3 * mid, r3 * mid - 2.0 * mf)
    regions.append(arch(r3 + mf, r4 - mf, mid, half))
    for phi in (0.0, alpha):
        regions.append(diamond((r3 + r4) / 2, phi, 0.09 * R, 0.03 * R))
        regions.append(diamond((r1 + r2) / 2 + 0.05 * R, phi, 0.07 * R, 0.02 * R))

LABEL = L4("Window flower", "Flor de ventana", "Fleur de fenêtre", "Flor de janela")
colour = COLOURS[stock]
cut = pliego.foldcut.cut(state, regions, id="window-flower", stock=stock, grain_deg=90.0,
                         label=LABEL, front=colour, back=colour)
if not cut.connected:
    raise ValueError(f"the cut leaves {len(cut.islands)} loose pieces")
report = pliego.papercut.analyze(cut.sheet, min_feature_mm=mf)
if not report.ok:
    raise ValueError("jianzhi-window-flower papercut check failed: "
                     + "; ".join(i["detail"] for i in report.issues if i["level"] == "error"))

sheet = cut.sheet
creases = [m for m in sheet.marks if m.assignment in ("M", "V") and m.edges()]
groups, start = [], 0
for end in crease_counts:
    groups.append([m for m in sheet.marks[start:end] if m.assignment in ("M", "V") and m.edges()])
    start = end
WORDS = {
    4: [L4("Fold the square in half", "Dobla el cuadrado por la mitad", "Plier le carré en deux",
           "Dobre o quadrado ao meio"),
        L4("Fold it in half again", "Dóblalo otra vez por la mitad", "Le plier encore en deux",
           "Dobre-o de novo ao meio"),
        L4("Fold along the diagonal into a 45° wedge", "Dobla por la diagonal en una cuña de 45°",
           "Plier selon la diagonale en un coin de 45°",
           "Dobre pela diagonal numa cunha de 45°")],
    6: [L4("Fold the square along its diagonal", "Dobla el cuadrado por la diagonal",
           "Plier le carré selon sa diagonale", "Dobre o quadrado pela diagonal"),
        L4("Fold one third over the middle", "Dobla un tercio sobre el centro",
           "Rabattre un tiers sur le milieu", "Dobre um terço sobre o meio"),
        L4("Fold the other third behind", "Dobla el otro tercio por detrás",
           "Rabattre l'autre tiers derrière", "Dobre o outro terço por trás"),
        L4("Fold the wedge in half into 30°", "Dobla la cuña por la mitad, a 30°",
           "Plier le coin en deux, à 30°", "Dobre a cunha ao meio, a 30°")],
}
WORDS[8] = WORDS[4] + [L4("Fold the wedge in half once more, to 22.5°",
                          "Dobla la cuña por la mitad una vez más, a 22.5°",
                          "Plier le coin en deux encore une fois, à 22,5°",
                          "Dobre a cunha ao meio mais uma vez, a 22,5°")]
steps = [pliego.Step(f"fold-{k + 1}", WORDS[n][k], [(m, None) for m in group])
         for k, group in enumerate(groups)]
steps.append(pliego.Step("cut-and-open", L4("Cut through every layer, then unfold and press it "
                                            "flat",
                                            "Corta todas las capas, desdobla y alísala",
                                            "Découper toutes les couches, déplier et aplatir",
                                            "Corte todas as camadas, desdobre e alise"),
                         [(m, 0.0) for m in creases], duration_ms=3000))
result = pliego.Assembly(
    [sheet],
    controls=[pliego.sequence_control()],
    sequence=pliego.Sequence(steps, mode="physical"),
    title="Jianzhi window flower",
    meta={"min_feature_mm": mf},
)
print(f"jianzhi: folds={n} layers={len(state.layers)} wedge={math.degrees(alpha):.1f}deg "
      f"regions={len(regions)} min_bridge={report.min_bridge_mm}")
