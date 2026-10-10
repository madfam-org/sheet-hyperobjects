"""Paper snowflake — sheet-hyperobjects cartridge (Pliego).

Six-fold fold-and-cut: a square is folded along its diagonal, into thirds (a 60° wedge, six layers)
and in half again (a 30° wedge, twelve layers) with simple folds (`pliego.simplefold`); the cut is
made once through every layer (`pliego.foldcut`) and the sheet is unfolded. Each cut appears twelve
times: six rotations and their mirror images (dihedral symmetry D6), the symmetry of a snow crystal.
The kept material is checked with `pliego.papercut.analyze` (one connected piece, every bridge at
least the stock's minimum feature) and the cartridge refuses to build otherwise.

The motif (a hexagonal hub with a centre hole and six diamonds, six pointed arms, branches that join
neighbouring arms into a ring, and a spike pair near each tip) is an original generic design.
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


MIN_FEATURE = {"copy-80": 1.0, "kami": 1.0, "washi-kozo-30": 1.0, "papel-de-china": 1.5}

size = clamp(PARAM(lambda: size, 150.0), 100.0, 250.0)
arm_width = clamp(PARAM(lambda: arm_width, 6.0), 3.0, 14.0)
hub = clamp(PARAM(lambda: hub, 0.3), 0.2, 0.45)
branch = clamp(PARAM(lambda: branch, 0.55), 0.4, 0.75)
spikes = bool(PARAM(lambda: spikes, True))
stock = str(PARAM(lambda: stock, "copy-80"))
if stock not in MIN_FEATURE:
    raise ValueError(f"stock {stock!r} is not one this cartridge offers")
min_feature = MIN_FEATURE[stock]

# ── fold: diagonal, thirds, half — the stack ends in the 30° wedge between 135° and 165° ──
cx = cy = size / 2.0
FOLDS = [(225.0, "valley"), (165.0, "valley"), (285.0, "mountain"), (315.0, "valley")]
state = pliego.simplefold.FoldedState(pliego.square(size))
crease_counts = []
for angle, kind in FOLDS:
    a = math.radians(angle)
    state.fold(((cx, cy), (cx + math.cos(a), cy + math.sin(a))), kind)
    crease_counts.append(len(state.creases))

# wedge-local frame: x' along the 135° fold edge, y' towards the 165° fold edge
U = (math.cos(math.radians(135.0)), math.sin(math.radians(135.0)))
V = (math.cos(math.radians(225.0)), math.sin(math.radians(225.0)))
T30 = math.tan(math.radians(30.0))


def P(x, y):
    return (cx + x * U[0] + y * V[0], cy + x * U[1] + y * V[1])


def meet(p, d, k):
    """Where the line p + s·d meets the line y' = k·x' (the 30° mirror for k = tan 30°)."""
    s = (k * p[0] - p[1]) / (d[1] - k * d[0])
    return (p[0] + s * d[0], p[1] + s * d[1])


def meet_y(p, d, y):
    s = (y - p[1]) / d[1]
    return (p[0] + s * d[0], y)


radius = 0.47 * size          # tip radius (the paper reaches at least size/2 in every direction)
h = arm_width / 2.0           # half arm (the fold mirrors it to the full width)
tip = 2.5 * h
R = radius - tip              # where the arm's straight sides end
R0 = hub * R                  # hub edge (a hexagon after unfolding)
if R0 * T30 <= h + min_feature:
    raise ValueError("the hub is too small for this arm width")

# branches leave the arm at 60° and run into the 30° mirror, where they meet the twin branch of
# the neighbouring arm (so the outer ring holds the arms together)
xb = branch * R
d60 = (math.cos(math.radians(60.0)), math.sin(math.radians(60.0)))
hb = 0.8 * h
left = (xb - hb * d60[1], hb * d60[0])
right = (xb + hb * d60[1], -hb * d60[0])
L1, R1 = meet_y(left, d60, h), meet_y(right, d60, h)
L2, R2 = meet(left, d60, T30), meet(right, d60, T30)
L2x, R2x = (L2[0] + 3 * d60[0], L2[1] + 3 * d60[1]), (R2[0] + 3 * d60[0], R2[1] + 3 * d60[1])
if L1[0] <= R0 + min_feature:
    raise ValueError("the branches start inside the hub: raise the branch position")
if R1[0] >= R - min_feature:
    raise ValueError("the branches start beyond the arm: lower the branch position")

inner = [(R0, h), L1, L2x, (R0, R0 * T30 + 3.0)]
outer = [R1]
if spikes:
    xs = (R1[0] + R) / 2.0
    ws = min(0.6 * h, (R - R1[0]) / 6.0)
    length = min(0.5 * (R - R1[0]), 0.8 * ((xs + ws) * T30 - h) / (d60[1] - T30 * d60[0]))
    if length > 2.0 * ws:
        apex = (xs + length * d60[0], h + length * d60[1])
        outer += [(xs - ws, h), apex, (xs + ws, h)]
big = 2.0 * size
outer += [(R, h), (R + tip, 0.0), (R + tip + 1.0, -1.0), (big, -1.0), (big, big * T30 + 5.0),
          R2x]
hole_r = 0.18 * R0
centre = [(hole_r * math.cos(2 * math.pi * k / 24), hole_r * math.sin(2 * math.pi * k / 24))
          for k in range(24)]
diamond = [(0.4 * R0, 0.0), (0.6 * R0, -0.12 * R0), (0.8 * R0, 0.0), (0.6 * R0, 0.12 * R0)]
regions = [[P(*q) for q in poly] for poly in (inner, outer, centre, diamond)]

LABEL = {"en": "Paper snowflake", "es": "Copo de nieve de papel", "fr": "Flocon de neige en papier",
         "pt": "Floco de neve de papel"}
cut = pliego.foldcut.cut(state, regions, id="snowflake", stock=stock, grain_deg=90.0,
                         label=LABEL)
if not cut.connected:
    raise ValueError(f"the cut leaves {len(cut.islands)} loose pieces")
report = pliego.papercut.analyze(cut.sheet, min_feature_mm=min_feature)
if not report.ok:
    raise ValueError("paper-snowflake papercut check failed: "
                     + "; ".join(i["detail"] for i in report.issues if i["level"] == "error"))

# ── fold program: re-fold along the creases in order, then release them all (unfold) ──
sheet = cut.sheet
creases = [m for m in sheet.marks if m.assignment in ("M", "V")]
groups, start = [], 0
for end in crease_counts:
    groups.append(creases[start:end])
    start = end
STEP_LABELS = [
    {"en": "Fold the square along its diagonal", "es": "Dobla el cuadrado por la diagonal",
     "fr": "Plier le carré selon sa diagonale", "pt": "Dobre o quadrado pela diagonal"},
    {"en": "Fold one third over the middle", "es": "Dobla un tercio sobre el centro",
     "fr": "Rabattre un tiers sur le milieu", "pt": "Dobre um terço sobre o meio"},
    {"en": "Fold the other third behind", "es": "Dobla el otro tercio por detrás",
     "fr": "Rabattre l'autre tiers derrière", "pt": "Dobre o outro terço por trás"},
    {"en": "Fold the wedge in half", "es": "Dobla la cuña por la mitad",
     "fr": "Plier le coin en deux", "pt": "Dobre a cunha ao meio"},
]
steps = [pliego.Step(f"fold-{k + 1}", STEP_LABELS[k], [(m, None) for m in group if m.edges()])
         for k, group in enumerate(groups)]
steps.append(pliego.Step(
    "unfold", {"en": "Cut through every layer, then unfold", "es": "Corta todas las capas y desdobla",
               "fr": "Découper toutes les couches, puis déplier",
               "pt": "Corte todas as camadas e desdobre"},
    release=[m for m in creases if m.edges()], duration_ms=3000))

result = pliego.Assembly(
    [sheet],
    controls=[pliego.sequence_control()],
    sequence=pliego.Sequence(steps, mode="physical"),
    title="Paper snowflake",
    meta={"min_feature_mm": min_feature},
)
