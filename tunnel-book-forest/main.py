"""Tunnel book forest — sheet-hyperobjects cartridge (Pliego).

A tunnel book whose layers are a forest: `frames` cut frames of trees stand one behind the other
between two accordion (leporello) walls, in front of a solid back scene, and pulling the cover
opens the tunnel. A path runs through a clearing in the middle of every layer; the trees grow
larger and the ground lower toward the cover, whose canopy hangs from the top.

Construction (kernel builder `pliego.book.pleated_tunnel`, no cartridge's script is copied): each
wall is one leporello strip — a foot glued to the back scene's side tab, then for every frame an
accordion V (two panels, the peak outward) and a box pleat that folds half the frame out of the
wall: in to the middle, across a 1 mm strip, back out. Each frame is therefore two double
half-frames, one from each wall, meeting at the middle seam; the forest's window is cut through
both layers of both halves (one window per frame, crossing the seam in the clearing). The two
cover halves are tied at the seam.

Kinematics (Tier R, exact). Every crease of a wall is vertical, so each wall is a planar chain;
every crease angle is affine in the walls' half-angle φ, so the opening — φ from shut to 30° —
is one linear program, exact at every point of the blend. The script checks the angle law against
the face-tree pose, the papercut minimum feature of both walls (in the builder) and the frames'
spacing and parallelism (fail loud).

The trees are original silhouettes generated here (round-crowned trees, poplars, firs with
branching sides, shrubs); no published tunnel book is reproduced.
"""

import math

import pliego


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


frames = round(float(PARAM(lambda: frames, 4)))                    # noqa: F821
frame_width = float(PARAM(lambda: frame_width, 120.0))             # noqa: F821
frame_height = float(PARAM(lambda: frame_height, 90.0))            # noqa: F821
depth = float(PARAM(lambda: depth, 18.0))                          # noqa: F821
forest = str(PARAM(lambda: forest, "mixed"))                       # noqa: F821
stock = str(PARAM(lambda: stock, "cardstock-160"))                 # noqa: F821

MIN_FEATURE = {"cardstock-160": 1.5, "cardstock-250": 2.0}
FORESTS = {"mixed": ("round", "fir", "poplar"), "conifers": ("fir",),
           "grove": ("round", "poplar")}
if stock not in MIN_FEATURE:
    raise ValueError(f"tunnel-book-forest: stock must be one of {tuple(MIN_FEATURE)}, got "
                     f"{stock!r}")
if forest not in FORESTS:
    raise ValueError(f"tunnel-book-forest: forest must be one of {tuple(FORESTS)}, got {forest!r}")
if not 3 <= frames <= 6:
    raise ValueError(f"tunnel-book-forest: frames must be an integer in [3, 6], got {frames}")

N = frames
W = pliego.clamp(frame_width, 90.0, 180.0)
H = pliego.clamp(frame_height, 70.0, 140.0)
D = pliego.clamp(depth, 12.0, 30.0)
MINF = MIN_FEATURE[stock]
MARGIN = 4.0 + (MINF - 1.5) * 2.0            # border of every frame (mm)
OPEN = 30.0                                  # the walls' half-angle when displayed
PITCH_SHUT = 3.0                             # frame pitch of the shut book (mm)
PLEAT = 1.0
TOL = 1e-6
GOLD = 0.6180339887


def L4(en, es, fr, pt):
    return {"en": en, "es": es, "fr": fr, "pt": pt}


def frac(x):
    return x - math.floor(x)


# ── tree silhouettes: skyline pieces from the left foot to the right foot ─────

TW = max(2.0 * MINF + 1.0, 0.045 * H)          # trunk width
TIP = 0.9 * MINF                               # half-width of a blunt tree top


def round_tree(xc, g, h):
    rc = 0.27 * h
    yc = g + h - rc
    dy = math.sqrt(rc * rc - (TW / 2) ** 2)
    pts = [(xc - TW / 2, g), (xc - TW / 2, yc - dy)]
    th0 = math.atan2(-dy, -TW / 2)                      # bottom-left of the crown
    th1 = math.atan2(-dy, TW / 2) - 2 * math.pi         # round over the top, clockwise
    for i in range(1, 24):
        t = th0 + (th1 - th0) * i / 24
        pts.append((xc + rc * math.cos(t), yc + rc * math.sin(t)))
    return pts + [(xc + TW / 2, yc - dy), (xc + TW / 2, g)], rc


def poplar(xc, g, h):
    a, y0 = 0.15 * h, g + 0.16 * h
    left = [(xc - TW / 2, g)]
    for i in range(0, 13):
        t = i / 12
        half = max(TIP, a * math.sin(math.pi * (0.15 + 0.85 * t)) ** 0.8)
        left.append((xc - half, y0 + t * (g + h - y0)))
    right = [(2 * xc - x, y) for x, y in reversed(left[1:])]
    return left + right + [(xc + TW / 2, g)], a


def fir(xc, g, h):
    b, y0 = 0.25 * h, g + 0.12 * h
    teeth = max(3, min(7, int((h - 0.12 * h) / max(6.0, 3.2 * MINF))))
    left = [(xc - TW / 2, g), (xc - TW / 2, y0)]
    for i in range(teeth):
        ya = y0 + (g + h - y0) * i / teeth
        yb = y0 + (g + h - y0) * (i + 1) / teeth
        wa = b * (1 - i / teeth)
        wb = b * (1 - (i + 1) / teeth)
        left += [(xc - max(wa, TIP + 0.8), ya),
                 (xc - max(0.75 * (0.55 * wa + 0.45 * wb), TIP), ya + 0.3 * (yb - ya))]
    left.append((xc - TIP, g + h))                   # a blunt tip keeps the paper wide
    right = [(2 * xc - x, y) for x, y in reversed(left)]
    return left + right, b


def shrub(xc, g, w):
    pts = [(xc - w / 2 + w * i / 10, g + 0.42 * w * math.sin(math.pi * i / 10) ** 0.7)
           for i in range(11)]
    return pts, w / 2


TREES = {"round": round_tree, "poplar": poplar, "fir": fir}


def ground(k, q):
    """Ground line of frame k: low and gently rolling at the cover, higher behind."""
    base = MARGIN + H * (0.05 + 0.20 * q)
    amp = 0.02 * H
    return lambda x: base + amp * math.sin(2.1 * x / W * math.pi + 1.3 * k)


def window(k):
    """Trees of frame k (0 = the cover): (x0, x1, top, ground, [(x, half, height, kind)])."""
    q = k / (N - 1)
    x0, x1 = -W / 2 + MARGIN, W / 2 - MARGIN
    top = H - MARGIN
    g = ground(k, q)
    kinds = FORESTS[forest]
    clearing = W * (0.09 + 0.03 * q)                 # half-width of the path's clearing
    room = top - MARGIN - g(0.0) - (0.16 * H if k == 0 else 0.0)
    tall = room * (0.96 if k == 0 else 0.95 - 0.22 * q)
    placed = []
    for side in (-1, 1):                             # from the outer edge in to the clearing
        pos, j = (x1 - x0) / 2 - 1.0, 0
        while True:
            kind = kinds[(k + j + (side > 0)) % len(kinds)]
            hh = tall * ((1.0 - 0.10 * j) if k == 0 else
                         0.72 + 0.28 * frac(GOLD * (11 * k + 5 * j + 3 * (side > 0))))
            _, half = TREES[kind](0.0, 0.0, hh)
            xc = pos - half
            if xc - half < clearing:
                break
            placed.append((side * xc, half, hh, kind))
            pos = xc - half - (2.0 + 3.0 * frac(GOLD * (3 * k + 7 * j + 1)))
            j += 1
    return x0, x1, top, g, sorted(placed)


windows = []
for k in range(N):
    x0, x1, top, g, items = window(k)
    sky = [(x0, g(x0))]
    for xc, _half, hh, kind in items:
        pts, half = TREES[kind](xc, 0.0, hh)
        gx = min(g(xc - half), g(xc + half), g(xc))       # trees stand on the lowest ground
        piece = [(x, y + gx) for x, y in pts]
        sky += [(x, g(x)) for x in (sky[-1][0] + (piece[0][0] - sky[-1][0]) * i / 6
                                    for i in range(1, 6))]
        sky += [(piece[0][0], g(piece[0][0]))] + piece[1:-1] + [(piece[-1][0], g(piece[-1][0]))]
    for i in range(1, 13):
        x = sky[-1][0] + (x1 - sky[-1][0]) * i / 12
        sky.append((x, g(x)))
    if k == 0:                                         # hanging leaves along the top
        drop = 0.14 * H
        n = max(4, round((x1 - x0) / 16.0))
        roof = []
        for i in range(n * 8, -1, -1):
            x = x0 + (x1 - x0) * i / (n * 8)
            ph = (i % 8) / 8.0
            roof.append((x, top - 0.25 * drop - 0.75 * drop * math.sin(math.pi * ph) ** 0.6))
    else:
        roof = [(x1, top), (x0, top)]
    ring = []
    for p in sky + roof:
        if not ring or math.dist(p, ring[-1]) > 0.05:
            ring.append(p)
    if math.dist(ring[0], ring[-1]) <= 0.05:
        ring.pop()
    for x, y in ring:
        if y > top + 1e-9 or y < MARGIN - 1e-9:
            raise ValueError(f"tunnel-book-forest: a tree of frame {k + 1} leaves the window")
    windows.append(([ring], len(items)))

# ── the tunnel ───────────────────────────────────────────────────────────────

tun = pliego.book.pleated_tunnel(
    N, W, H, D, foot=12.0, pleat=PLEAT, open_phi=OPEN, windows=[w for w, _ in windows],
    stock=stock, min_feature=MINF, margin=MARGIN - 0.5, colors=("#2f6b3a", "#cfe3ef"))
shut = math.degrees(math.acos((PITCH_SHUT - PLEAT) / (2.0 * D)))
for phi in (shut, (shut + OPEN) / 2.0, OPEN):
    err = tun.pose_error(phi)
    if err > TOL:
        raise ValueError(f"tunnel-book-forest: the walls do not follow the angle law ({err:.3g} mm)")
z = [tun.world("wall-left", tun.frame_u(k)[1] - 1.0, H / 2, OPEN)[2] for k in range(N)]
zr = [tun.world("wall-right", tun.frame_u(k)[1] - 1.0, H / 2, OPEN)[2] for k in range(N)]
for k in range(N - 1):
    if abs(z[k] - z[k + 1] - tun.spacing(OPEN)) > TOL or abs(z[k] - zr[k]) > TOL:
        raise ValueError("tunnel-book-forest: the frames do not stand parallel and evenly spaced")
u_seam = tun.frame_u(0)[0] + W / 2 + PLEAT
ties = [pliego.string(f"cover-tie-{name}", (tun.sheets[1], (u_seam, y)),
                      (tun.sheets[2], (u_seam, y)), 1.0)
        for name, y in (("top", H - MARGIN / 2), ("bottom", MARGIN / 2))]

ang_open, ang_shut = tun.angles(OPEN), tun.angles(shut)
step = pliego.Step(
    "open", L4("Pull the cover: the forest opens", "Tira de la portada: el bosque se abre",
               "Tirez la couverture : la forêt s'ouvre", "Puxe a capa: a floresta se abre"),
    [(m, a) for m, a in ang_open.items()], duration_ms=4000,
    note=L4(f"Hold the back scene and pull: the frames go from {PITCH_SHUT:g} mm to "
            f"{tun.spacing(OPEN):.1f} mm apart, and the path through the clearing appears.",
            f"Sujeta la escena del fondo y tira: los marcos pasan de {PITCH_SHUT:g} mm a "
            f"{tun.spacing(OPEN):.1f} mm de separación, y aparece el sendero del claro.",
            f"Tenez la scène du fond et tirez : les cadres passent de {PITCH_SHUT:g} mm à "
            f"{tun.spacing(OPEN):.1f} mm d'écart, et le chemin de la clairière apparaît.",
            f"Segure a cena do fundo e puxe: as molduras passam de {PITCH_SHUT:g} mm a "
            f"{tun.spacing(OPEN):.1f} mm de distância, e aparece a trilha da clareira."))
initial = tun.initial(shut)                   # exact world pose of the shut book
trees = [n for _, n in windows]
print(f"forest: frames={N} forest={forest} frame={W:g}x{H:g}mm wall_panel={D:g}mm "
      f"spacing={tun.spacing(OPEN):.2f}mm shut={shut:.2f}deg trees={trees} "
      f"strip={sum(tun.lengths):.0f}mm faces={sum(len(s.build().faces) for s in tun.sheets)}")

result = pliego.Assembly(
    tun.sheets, joins=tun.joins + ties,
    controls=[pliego.sequence_control(label=L4("Open the tunnel", "Abrir el túnel",
                                               "Ouvrir le tunnel", "Abrir o túnel"),
                                      default=1.0)],
    sequence=pliego.Sequence([step], mode="kinematic"),
    initial=initial,
    title="Tunnel book forest",
    min_feature_mm=MINF,
)
