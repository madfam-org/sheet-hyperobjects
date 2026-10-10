"""Shadow box — sheet-hyperobjects cartridge (Pliego).

A layered papercut diorama: `layers` cut frames stand one behind the other inside a card box
with a window in its front, kept apart by folded spacers. Everything is cut from flat card:

* the **box** is one scored sheet: a row of four panels (base, front with the window, top, back)
  with the two side walls hinged to the front panel, three pairs of side flaps (glued inside the
  side walls; the back panel's pair only tucks) and a tuck flap on the back panel's free edge;
* each **frame** is a card with a scene window cut in it: a silhouette that grows from its bottom
  margin (and, on the front frame, hangs from its top margin); deeper frames have a higher ground
  line and smaller shapes, so the layers read as depth;
* each **spacer** is a strip of four panels and a tab, folded into a square tube (a box-section
  strip) and glued along a frame's side margin; two spacers fill every gap, from the front panel
  to the back panel, so the stack is held at `spacing` mm pitch.

The fold program folds the spacer tubes and the box around the frames, which stand in their final
places throughout. Every crease is a score folded to 90° and every sheet is a tree of panels, so
each step is an exact rigid motion. Flaps that lie against a wall stop at 89°, just inside it.
The assembled box is also written as the `target:assembled` frame. Before it writes the document
the script checks every frame with `pliego.papercut.analyze` against the stock's minimum feature,
checks that every seam of the folded box closes, and that every folded spacer spans its gap.
Scenes are original shapes generated here: forest, sea, night city and garden.
"""

import math

import pliego
from pliego import kinematics


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


def L4(en, es, fr, pt):
    return {"en": en, "es": es, "fr": fr, "pt": pt}


scene = str(PARAM(lambda: scene, "forest"))                  # noqa: F821
layers = round(float(PARAM(lambda: layers, 5)))              # noqa: F821
width = float(PARAM(lambda: width, 160.0))                   # noqa: F821
height = float(PARAM(lambda: height, 120.0))                 # noqa: F821
spacing = float(PARAM(lambda: spacing, 10.0))                # noqa: F821
stock = str(PARAM(lambda: stock, "cardstock-250"))           # noqa: F821

SCENES = ("forest", "sea", "night-city", "garden")
MIN_FEATURE = {"cardstock-160": 1.5, "cardstock-250": 2.0, "cardstock-300": 2.0}
CALIPER = {"cardstock-160": 0.2, "cardstock-250": 0.3, "cardstock-300": 0.36}
if scene not in SCENES:
    raise ValueError(f"shadow-box: scene must be one of {SCENES}, got {scene!r}")
if stock not in MIN_FEATURE:
    raise ValueError(f"shadow-box: stock must be one of {tuple(MIN_FEATURE)}, got {stock!r}")
if not 3 <= layers <= 8:
    raise ValueError(f"shadow-box: layers must be an integer in [3, 8], got {layers}")

N = layers
W = pliego.clamp(width, 100.0, 240.0)
H = pliego.clamp(height, 80.0, 200.0)
S = pliego.clamp(spacing, 6.0, 25.0)
MINF = MIN_FEATURE[stock]
BOX, ROD = "cardstock-300", "cardstock-250"
TB, TF, TR = CALIPER[BOX], CALIPER[stock], CALIPER[ROD]
D = TB + (N + 1) * S + N * TF          # inside depth: front panel to back panel, mid-planes
WF, HF = W - 2.0, H - 1.0              # frames: 1 mm side clearance, 0.5 mm top and bottom
MX = 2.0                               # spacer band starts 2 mm in from the frame edge
RM = 4.0                               # spacers stop 4 mm short of the frame's top and bottom
MW = max(14.0, MX + S + 5.0)           # window side margin hides the spacers
MV = max(12.0, 0.1 * H)                # window top and bottom margins
F = min(15.0, 0.3 * min(D, H))         # side flap depth
TUCK = min(F, S - 1.0)                 # the back's tuck flap must clear the last frame
C = 1.0                                # flaps start 1 mm in from each corner
IN = 89.0                              # a flap against a wall, drawn just inside it
TOL = 1e-4
if W - 2 * MW < 40.0 or H - 2 * MV < 40.0:
    raise ValueError("shadow-box: the window would be under 40 mm: make the box larger or the "
                     "spacing smaller")
SEED = {"forest": 1.0, "sea": 2.0, "night-city": 3.0, "garden": 4.0}[scene]


def rnd(i):
    v = math.sin(i * 12.9898 + SEED * 78.233) * 43758.5453
    return v - math.floor(v)


def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


# ── scenes: frame-local window [X0, X1] × [Y0, Y1]; skylines run left → right ──
X0, X1 = MW - 1.0, W - MW - 1.0
Y0, Y1 = MV - 0.5, H - MV - 0.5
WW, WH = X1 - X0, Y1 - Y0
NECK = 1.6 * MINF                       # the narrowest stem, trunk or mast a scene draws


def sample(f, xa, xb, step=4.0):
    n = max(1, int(math.ceil((xb - xa) / step)))
    return [(xa + (xb - xa) * i / n, f(xa + (xb - xa) * i / n)) for i in range(n + 1)]


def ground(q, j, amp=0.03):
    base = Y0 + WH * (0.05 + 0.28 * q)
    return lambda x: base + WH * amp * math.sin(2 * math.pi * (x - X0) / WW * 1.2 + 1.7 * j)


def fir(xc, g, h):
    """A fir of three overhanging tiers, standing on the ground line g (left → right)."""
    tw, th = max(NECK, 0.08 * h), max(3.0, 0.14 * h)
    hw = [0.26 * h, 0.2 * h, 0.14 * h]
    yb = [th, th + 0.3 * (h - th), th + 0.56 * (h - th)]
    base = g(xc)
    left = [(xc - tw / 2, g(xc - tw / 2)), (xc - tw / 2, base + th)]
    for i in range(3):
        left.append((xc - hw[i], base + yb[i]))
        left.append((xc - 0.42 * hw[i], base + (yb[i + 1] if i < 2 else 0.0)) if i < 2
                    else (xc, base + h))
    left = left[:-1]
    right = [(2 * xc - x, y) for x, y in reversed(left[2:])]
    return left + [(xc, base + h)] + right + [(xc + tw / 2, base + th),
                                              (xc + tw / 2, g(xc + tw / 2))]


def round_tree(xc, g, h):
    tw = max(NECK, 0.07 * h)
    r = 0.34 * h
    cy = g(xc) + h - r
    a0 = math.asin(min(0.95, (tw / 2) / r))
    arc = [(xc + r * math.cos(t), cy + r * math.sin(t)) for t in
           [-math.pi / 2 - a0 - (math.pi * 2 - 2 * a0) * (i / 24) for i in range(25)]]
    return [(xc - tw / 2, g(xc - tw / 2))] + arc + [(xc + tw / 2, g(xc + tw / 2))]


def tulip(xc, g, h):
    sw, cw = NECK, max(3.2 * MINF, 0.32 * h)
    base, cup = g(xc), g(xc) + 0.62 * h
    return [(xc - sw / 2, g(xc - sw / 2)), (xc - sw / 2, cup), (xc - cw / 2, cup + 0.12 * h),
            (xc - cw / 2, base + h), (xc - cw / 6, base + 0.86 * h), (xc, base + h * 1.02),
            (xc + cw / 6, base + 0.86 * h), (xc + cw / 2, base + h),
            (xc + cw / 2, cup + 0.12 * h), (xc + sw / 2, cup), (xc + sw / 2, g(xc + sw / 2))]


def hedge(g, hb, r):
    """A clipped hedge across the window: a band with round bumps on top (left → right)."""
    xa, xb = X0 + 3.0, X1 - 3.0
    n = max(2, round((xb - xa) / (2 * r)))
    r = (xb - xa) / (2 * n)
    yb = max(g(xa), g(xb), max(g(xa + (xb - xa) * i / 16) for i in range(17))) + hb
    pts = [(xa, g(xa)), (xa, yb)]
    for k in range(n):
        cx = xa + (2 * k + 1) * r
        pts += [(cx - r * math.cos(math.pi * i / 10), yb + r * math.sin(math.pi * i / 10))
                for i in range(1, 10)]
        pts.append((cx + r, yb))
    return pts + [(xb, g(xb))]


def building(x, bw, g, top, k):
    pts = [(x, g(x)), (x, top)]
    roof = int(rnd(60 + k) * 4)
    if roof == 1 and bw > 10.0:
        pts.append((x + bw / 2, min(top + 0.4 * bw, Y1 - 6.0)))
    elif roof == 2 and top + 12.0 < Y1 - 6.0:
        aw = max(NECK, 2.0)
        pts += [(x + bw / 2 - aw / 2, top), (x + bw / 2 - aw / 2, top + 10.0),
                (x + bw / 2 + aw / 2, top + 10.0), (x + bw / 2 + aw / 2, top)]
    elif roof == 3 and bw > 9.0:
        st = min(5.0, Y1 - 6.0 - top)
        pts += [(x + 0.25 * bw, top), (x + 0.25 * bw, top + st), (x + 0.75 * bw, top + st),
                (x + 0.75 * bw, top)]
    return pts + [(x + bw, top), (x + bw, g(x + bw))]


def place(n, width_each, j):
    """n feature centres spread over the window without overlaps (deterministic jitter)."""
    out = []
    for k in range(n):
        xc = X0 + (k + 0.5) * WW / n + 0.25 * (rnd(10 * j + k) - 0.5) * WW / n
        xc = pliego.clamp(xc, X0 + width_each / 2 + 3.0, X1 - width_each / 2 - 3.0)
        if all(abs(xc - o) >= width_each + 3.0 for o in out):
            out.append(xc)
    return sorted(out)


def skyline(shapes, g, step=4.0):
    """Ground line between shapes (each a left → right polyline standing on g)."""
    pts, xa = [], X0
    for shp in sorted(shapes, key=lambda s: s[0][0]):
        pts += sample(g, xa, shp[0][0], step)[:-1] + shp
        xa = shp[-1][0]
    return pts + sample(g, xa, X1, step)


def drape(depth, count):
    """A hanging scalloped edge (right → left, kept above): canopy, cloud bank or vine."""
    pts, step = [], WW / count
    for k in range(count, 0, -1):
        xa = X0 + k * step
        for i in range(8):
            t = i / 8.0
            pts.append((xa - t * step, Y1 - depth * (0.35 + 0.65 * math.sin(math.pi * t))))
    return pts + [(X0, Y1 - 0.35 * depth)]


def scene_frame(k):
    """(bottom skyline, top line or None, extra holes) of frame k (1 = front, N = back)."""
    q = (k - 1) / (N - 1)
    j = k + 3 * SEED
    g = ground(q, j)
    room = Y1 - 8.0 - g(X0) - WH * 0.03
    holes = []
    top = None
    if scene == "forest":
        h = min(room, WH * (0.82 - 0.4 * q))
        if k == 1:
            h = min(h, room - 0.12 * WH)
            xs = [X0 + 0.36 * h + 3.0, X1 - 0.36 * h - 3.0]
            shapes = [round_tree(x, g, h) for x in xs]
            top = drape(0.14 * WH, 5)
        else:
            n = 2 + k
            shapes = [fir(x, g, h * (0.8 + 0.2 * rnd(30 * j + i)))
                      for i, x in enumerate(place(n, 0.52 * h, j))]
    elif scene == "sea":
        lam = WW / max(2, round(WW / (34.0 - 16.0 * q)))
        amp = min(WH * (0.09 - 0.04 * q), 0.28 * lam)
        base = g(X0)
        ph = rnd(5 * j)

        def wave(x):
            u = (x - X0) / lam + ph
            return base + amp * (1.0 - abs(math.sin(math.pi * u))) ** 1.6

        shapes = []
        if k == (N + 1) // 2 or (k == N - 1 and N >= 6):          # sailboats mid-depth
            xb = X0 + (0.36 if k == (N + 1) // 2 else 0.2) * WW
            hw = (0.13 if k == (N + 1) // 2 else 0.08) * WW
            deck = base + amp + 0.25 * hw
            mast = min(Y1 - 8.0, deck + 3.2 * hw)
            mw, boom = max(NECK, 2.0), deck + max(4.0, 0.25 * hw)
            shapes = [[(xb - 0.75 * hw, wave(xb - 0.75 * hw)), (xb - hw, deck),
                       (xb - mw / 2, deck), (xb - mw / 2, mast), (xb + mw / 2, mast),
                       (xb + 0.85 * hw, boom), (xb + mw / 2, boom), (xb + mw / 2, deck),
                       (xb + hw, deck), (xb + 0.75 * hw, wave(xb + 0.75 * hw))]]
        elif k == 2:                                              # a rock with a gull's perch
            xr, rw = X0 + 0.8 * WW, 0.12 * WW
            shapes = [[(xr - rw, wave(xr - rw)), (xr - 0.6 * rw, base + amp + 0.5 * rw),
                       (xr - 0.1 * rw, base + amp + 0.75 * rw),
                       (xr + 0.5 * rw, base + amp + 0.4 * rw),
                       (xr + rw, wave(xr + rw))]]
        elif k == N:                                              # an island with a lighthouse
            xi = X0 + 0.7 * WW
            lw, lh = max(NECK + 1.0, 4.0), min(0.3 * WH, Y1 - 8.0 - base - 10.0)
            shapes = [[(xi - 0.16 * WW, wave(xi - 0.16 * WW)), (xi - 0.06 * WW, base + 8.0),
                       (xi - lw / 2, base + 9.0), (xi - lw / 2, base + 9.0 + lh),
                       (xi, base + 12.0 + lh), (xi + lw / 2, base + 9.0 + lh),
                       (xi + lw / 2, base + 9.0), (xi + 0.08 * WW, base + 7.0),
                       (xi + 0.18 * WW, wave(xi + 0.18 * WW))]]
        if k == 1:
            top = drape(0.12 * WH, 3)
        bottom = skyline(shapes, wave, lam / 10.0)
        return bottom, top, holes
    elif scene == "night-city":
        tall = room * (0.5 + 0.45 * q)
        shapes, x, i = [], X0 + 3.0, 0
        while True:
            bw = WW * (0.08 + 0.07 * rnd(40 * j + i))
            if x + bw > X1 - 3.0:
                break
            u = (x + bw / 2 - X0) / WW
            if k == 1 and 0.25 < u < 0.75:
                x, i = x + bw, i + 1
                continue
            top_y = g(x) + max(10.0, tall * (0.5 + 0.5 * rnd(50 * j + i)))
            shapes.append(building(x, bw, g, top_y, 7 * j + i))
            if k >= N - 1 and bw > 3 * MINF + 8.0:               # lit windows on the far blocks
                ww, wh = 3.0, 4.0
                cols = int((bw - 2 * MINF - 1.0) // (ww + MINF + 1.0))
                rows = int((top_y - g(x) - 8.0) // (wh + MINF + 2.0))
                for r in range(rows):
                    for c in range(cols):
                        if rnd(100 * j + 10 * i + 3 * r + c) < 0.45:
                            continue
                        wx = x + MINF + 1.0 + c * (ww + MINF + 1.0)
                        wy = max(g(x), g(x + bw)) + 5.0 + r * (wh + MINF + 2.0)
                        holes.append(rect(wx, wy, wx + ww, wy + wh))
            x, i = x + bw + (2.5 if rnd(70 * j + i) < 0.3 else 0.0), i + 1
    else:                                                         # garden
        if k == 1:
            h = min(room, WH * 0.42)
            shapes = [tulip(x, g, h * (0.75 + 0.25 * rnd(20 * j + i)))
                      for i, x in enumerate(place(7, max(3.4 * MINF, 0.34 * h), j))]
            top = drape(0.13 * WH, 4)
        elif k == 2:
            ph, pw, gap = min(room, WH * 0.32), max(5.0, 2.5 * MINF), max(4.0, 2.0 * MINF)
            shapes, x = [], X0 + 4.0
            while x + pw < X1 - 4.0:
                gy = g(x + pw / 2)
                shapes.append([(x, g(x)), (x, gy + ph), (x + pw / 2, gy + ph + pw * 0.7),
                               (x + pw, gy + ph), (x + pw, g(x + pw))])
                x += pw + gap
        elif k % 2 == 1 and k < N:
            shapes = [hedge(g, min(room, WH * (0.2 - 0.06 * q)), max(5.0, 0.05 * WW))]
        else:
            h = min(room, WH * (0.7 - 0.3 * q))
            shapes = [round_tree(x, g, h * (0.7 + 0.3 * rnd(30 * j + i)))
                      for i, x in enumerate(place(1 + k // 2, 0.7 * h, j))]
    return skyline(shapes, g), top, holes


def clean(ring):
    """Drop repeated points, collinear midpoints and zero-width spikes (adjacent buildings)."""
    out = []
    for p in ring:
        if not out or math.dist(p, out[-1]) > 0.05:
            out.append(p)
    changed = True
    while changed and len(out) > 3:
        changed = False
        for i in range(len(out)):
            a, p, b = out[i - 1], out[i], out[(i + 1) % len(out)]
            cr = (p[0] - a[0]) * (b[1] - p[1]) - (p[1] - a[1]) * (b[0] - p[0])
            if math.dist(a, p) <= 0.05 or abs(cr) < 1e-9:
                del out[i]
                changed = True
                break
    return out


def scene_hole(k):
    bottom, top, holes = scene_frame(k)
    out = clean(bottom + (top or [(X1, Y1), (X0, Y1)]))
    for x, y in out:
        if not (X0 - 1e-9 <= x <= X1 + 1e-9 and Y0 - 1e-9 <= y <= Y1 + 1e-9):
            raise ValueError(f"shadow-box: scene point ({x:.2f}, {y:.2f}) leaves the window")
    return out, holes


# ── world (Y up, viewer at +Z): the base on the table, the front panel at z = D ──
H2 = math.sqrt(0.5)
BOX_ROT = (0.0, -H2, 0.0, H2)        # box-local (u, v) → world (x = v, z = u), front face up
STAND = (H2, 0.0, 0.0, H2)           # sheet-local (u, v) → world (x = u, y = v), front face +Z
MIRROR = (0.0, H2, -H2, 0.0)         # (u, v) → (x = −u, y = v), front face −Z


def frame_front(k):                  # the front face of frame k (k = 1 front … N back)
    return D - TB / 2 - k * S - (k - 1) * TF


# ── the box: base | front | top | back | tuck along u; side walls on the front panel ──
def flap(u0, u1, v, out):            # a trapezoid flap hinged on v between u0 and u1
    return [(u0 + C, v), (u0 + C + F, v + out * F), (u1 - C - F, v + out * F), (u1 - C, v)]


U1, U2, U3, U4 = D, D + H, 2 * D + H, 2 * D + 2 * H
low = [(0.0, 0.0)] + flap(0.0, U1, 0.0, -1) + [(U1, 0.0), (U1, -D), (U2, -D), (U2, 0.0)]
low += flap(U2, U3, 0.0, -1) + [(U3, 0.0)] + flap(U3, U4, 0.0, -1) + [(U4, 0.0)]
tuck = [(U4, 0.0), (U4, C), (U4 + TUCK, C + TUCK), (U4 + TUCK, W - C - TUCK), (U4, W - C),
        (U4, W)]
high = [(u, W - v) for u, v in reversed(low)]
box = pliego.Sheet("box", low + tuck[1:-1] + high, stock=BOX, grain_deg=0.0,
                   placement=pliego.Placement(rotation=BOX_ROT),
                   label=L4("Box (one scored sheet)", "Caja (una hoja hendida)",
                            "Boîte (une feuille rainée)", "Caixa (uma folha vincada)"))
box.hole(rect(U1 + MV, MW, U2 - MV, W - MW))
box.label_edge("window", (U1 + MV, MW), (U1 + MV, W - MW))
if scene == "night-city":            # moon and stars pierced in the back panel (back-light)
    def at(x, y):                    # world (x, y) on the back panel → box-local
        return (U4 - y, x)
    mx_, my_, mr = 0.74 * W, H - MV - 0.18 * H, 0.08 * min(W, H)
    box.hole([at(mx_ + mr * math.cos(math.pi * i / 14), my_ + mr * math.sin(math.pi * i / 14))
              for i in range(28)])
    for i in range(9):
        sx = MW + 4.0 + (W - 2 * MW - 8.0) * rnd(200 + i)
        sy = H - MV - 4.0 - 0.32 * H * rnd(300 + i)
        if math.hypot(sx - mx_, sy - my_) < mr + 6.0:
            continue
        r = 1.6 + 0.6 * rnd(400 + i)
        box.hole([at(sx + r, sy), at(sx, sy + r), at(sx - r, sy), at(sx, sy - r)])


def score(sheet, a, b, ang, en, es, fr, pt, name=None):
    return sheet.crease(a, b, "valley", ang, treatment="score", label=L4(en, es, fr, pt), name=name)


front = score(box, (U1, 0), (U1, W), 90.0, "Front panel up", "Frente hacia arriba",
              "Relever la face avant", "Frente para cima")
sides = [score(box, (U1, v), (U2, v), 90.0, "Side wall back", "Lateral hacia atrás",
               "Rabattre la paroi latérale", "Lateral para trás", name="side-wall")
         for v in (0.0, W)]
top = score(box, (U2, 0), (U2, W), 90.0, "Top back", "Techo hacia atrás",
            "Rabattre le dessus", "Topo para trás")
back = score(box, (U3, 0), (U3, W), 90.0, "Close the back", "Cerrar el fondo",
             "Fermer le fond", "Fechar o fundo")
tuck_m = score(box, (U4, C), (U4, W - C), IN, "Tuck flap", "Lengüeta de cierre",
               "Rabat à glisser", "Lingueta de fecho", name="tuck")
flaps = {}
for key, (u0, u1) in (("base", (0.0, U1)), ("top", (U2, U3)), ("back", (U3, U4))):
    flaps[key] = [score(box, (u0 + C, v), (u1 - C, v), IN, "Side flap", "Solapa lateral",
                        "Rabat latéral", "Aba lateral", name=f"{key}-flap") for v in (0.0, W)]

# ── frames ──
frames, bridges = [], []
for k in range(1, N + 1):
    ring, extra = scene_hole(k)
    probe = pliego.Sheet(f"probe-{k}", rect(0, 0, WF, HF), stock=stock)
    probe.hole(ring)
    for h in extra:
        probe.hole(h)
    rep = pliego.papercut.analyze(probe, min_feature_mm=MINF)
    if not rep.ok or rep.components != 1:
        raise ValueError(f"shadow-box: frame {k} fails the papercut check: " + "; ".join(
            i["detail"] for i in rep.issues if i["level"] == "error"))
    bridges.append(rep.min_bridge_mm)
    fr = pliego.Sheet(f"frame-{k}", rect(0, 0, WF, HF), stock=stock, grain_deg=90.0,
                      placement=pliego.Placement(origin=(1.0, 0.5, frame_front(k) - TF / 2),
                                                 rotation=STAND),
                      label=L4(f"Frame {k}", f"Marco {k}", f"Cadre {k}", f"Moldura {k}"))
    fr.hole(ring)
    for h in extra:
        fr.hole(h)
    fr.label_edge("spacer-zone", (0, 0), (0, HF)).label_edge("spacer-zone", (WF, 0), (WF, HF))
    frames.append(fr)

# ── spacers: two square tubes per gap, rooted on a frame face, folded toward the gap ──
A = S - TR                            # tube panel width (mid-planes), so the tube spans S
LR = HF - 2 * RM
TAB = 0.8 * A
rod_ring = [(0, 0), (4 * A, 0), (4 * A + TAB, 2.0), (4 * A + TAB, LR - 2.0), (4 * A, LR),
            (0, LR)]
rods, rod_marks, rod_checks = [], [], []
for g in range(N + 1):
    on_front = g < N                  # glued on frame g+1's front face, else frame N's back
    k = g + 1 if on_front else N
    face = frame_front(k) if on_front else frame_front(k) - TF
    zs = face + (TR / 2 if on_front else -TR / 2)
    toward = 1.0 if on_front else -1.0
    for side in ("left", "right"):
        rot = MIRROR if side == "left" else STAND
        x0 = 1.0 + MX + A if side == "left" else 1.0 + WF - MX - A
        normal_z = -1.0 if side == "left" else 1.0
        kind = "valley" if normal_z * toward > 0 else "mountain"
        lt = side == "left"
        rod = pliego.Sheet(f"spacer-{g}-{side}", rod_ring, stock=ROD, grain_deg=90.0,
                           placement=pliego.Placement(origin=(x0, 0.5 + RM, zs), rotation=rot),
                           label=L4(f"Spacer {g} ({side})",
                                    f"Separador {g} ({'izquierdo' if lt else 'derecho'})",
                                    f"Entretoise {g} ({'gauche' if lt else 'droite'})",
                                    f"Espaçador {g} ({'esquerdo' if lt else 'direito'})"))
        rod.label_edge("glue-face", (0, 0), (0, LR))
        ms = [rod.crease((A * i, 0), (A * i, LR), kind, 90.0, treatment="score")
              for i in (1, 2, 3)]
        ms.append(rod.crease((4 * A, 0), (4 * A, LR), kind, 88.0, treatment="score"))
        rods.append(rod)
        rod_marks.append(ms)
        rod_checks.append((rod, ms, toward))



def rod_angles(ms):                   # signed: a spacer that folds toward its back is mountain
    sg = 1.0 if ms[0].assignment == "V" else -1.0
    return {ms[0]: 90.0 * sg, ms[1]: 90.0 * sg, ms[2]: 90.0 * sg, ms[3]: 88.0 * sg}


# ── self-checks (fail loud) ──
ANG = {front: 90.0, top: 90.0, back: 90.0, tuck_m: IN}
ANG.update({m: 90.0 for m in sides})
ANG.update({m: IN for ms in flaps.values() for m in ms})
ROOT = (D / 2, W / 2)
arr = box.build()
pose = kinematics.pose_arrangement(arr, {e: a for m, a in ANG.items() for e in m.edges()},
                                   pliego.P(*ROOT))


def box_world(u, v):
    for i, p in enumerate(arr.vertices):
        if abs(p.x - u) < 1e-6 and abs(p.y - v) < 1e-6:
            x, y, z = pose[i]
            return (-z, y, x)        # BOX_ROT applied to the un-placed pose
    raise ValueError(f"shadow-box: no box vertex at ({u}, {v})")


expect = {(0.0, 0.0): (0, 0, 0), (0.0, W): (W, 0, 0), (U1, -D): (0, 0, 0), (U1, W + D): (W, 0, 0),
          (U2, -D): (0, H, 0), (U3, 0.0): (0, H, 0), (U4, 0.0): (0, 0, 0), (U4, W): (W, 0, 0),
          (U2, 0.0): (0, H, D), (U1, 0.0): (0, 0, D)}
worst = max(math.dist(box_world(*uv), xyz) for uv, xyz in expect.items())
if worst > TOL:
    raise ValueError(f"shadow-box: the folded box does not close: a seam is {worst:.3g} mm open")
span = 0.0
for rod, ms, toward in rod_checks:
    rarr = rod.build()
    rp = kinematics.pose_arrangement(rarr, {e: a for m, a in rod_angles(ms).items()
                                            for e in m.edges()}, pliego.P(A / 2, LR / 2))
    far = [rp[i] for i, p in enumerate(rarr.vertices) if 2 * A - 1e-6 <= p.x <= 3 * A + 1e-6]
    # un-placed: the sheet normal is +Y; the far panel must sit A above or below, by the fold
    lift = sum(p[1] for p in far) / len(far)
    sign = 1.0 if ms[0].assignment == "V" else -1.0
    span = max(span, abs(abs(lift) - A), 0.0 if lift * sign > 0 else 1.0)
if span > TOL:
    raise ValueError(f"shadow-box: a folded spacer does not span its gap ({span:.3g} mm)")
print(f"shadow-box: scene={scene} layers={N} box={W:g}x{H:g}x{D:.2f}mm spacing={S:g}mm "
      f"window={W - 2 * MW:.0f}x{H - 2 * MV:.0f}mm seams={worst:.1e}mm "
      f"bridges=[{' '.join('-' if b is None else f'{b:.1f}' for b in bridges)}]mm>={MINF:g} "
      f"spacers={len(rods)} sheets={1 + N + len(rods)}")

# ── the fold program ──
rod_steps = [(m, a) for ms in rod_marks for m, a in rod_angles(ms).items()]
steps = [
    pliego.Step("spacers", L4("Fold each spacer strip into a square tube and glue its tab",
                              "Dobla cada tira separadora en un tubo cuadrado y pega su pestaña",
                              "Pliez chaque bande d'entretoise en tube carré et collez sa patte",
                              "Dobre cada tira espaçadora num tubo quadrado e cole a aba"),
                rod_steps, duration_ms=2500,
                note=L4("Glue one face of each tube along a frame's side margin and the opposite "
                        "face to the next layer: front panel, frames, back panel.",
                        "Pega una cara de cada tubo en el margen lateral de un marco y la cara "
                        "opuesta a la capa siguiente: frente, marcos, fondo.",
                        "Collez une face de chaque tube sur la marge latérale d'un cadre et la "
                        "face opposée sur la couche suivante : façade, cadres, fond.",
                        "Cole uma face de cada tubo na margem lateral de uma moldura e a face "
                        "oposta na camada seguinte: frente, molduras, fundo.")),
    pliego.Step("base-flaps", L4("Fold up the base's side flaps", "Levanta las solapas laterales "
                                 "de la base", "Relevez les rabats latéraux de la base",
                                 "Levante as abas laterais da base"),
                [(m, IN) for m in flaps["base"]], duration_ms=1200),
    pliego.Step("front", L4("Raise the front panel with its window",
                            "Levanta el frente con su ventana",
                            "Relevez la façade et sa fenêtre", "Levante a frente com a janela"),
                [(front, 90.0)], duration_ms=1800),
    pliego.Step("sides", L4("Swing the side walls back over the base flaps and glue them",
                            "Gira los laterales hacia atrás sobre las solapas de la base y "
                            "pégalos", "Rabattez les parois latérales sur les rabats de la base "
                            "et collez-les", "Gire as laterais para trás sobre as abas da base e "
                            "cole-as"), [(m, 90.0) for m in sides], duration_ms=1800),
    pliego.Step("top", L4("Fold the top's flaps down, then fold the top back and glue its flaps",
                          "Dobla hacia abajo las solapas del techo; luego dobla el techo hacia "
                          "atrás y pega sus solapas",
                          "Rabattez les rabats du dessus, puis rabattez le dessus et collez-les",
                          "Dobre para baixo as abas do topo; depois dobre o topo para trás e "
                          "cole as abas"),
                [(m, IN) for m in flaps["top"]] + [(top, 90.0)], duration_ms=2000),
    pliego.Step("close", L4("Close the back: tuck its side flaps inside and slide the tuck flap "
                            "along the base", "Cierra el fondo: mete sus solapas laterales y "
                            "desliza la lengüeta sobre la base", "Fermez le fond : rentrez ses "
                            "rabats latéraux et glissez le rabat le long de la base",
                            "Feche o fundo: enfie as abas laterais e deslize a lingueta sobre a "
                            "base"),
                [(m, IN) for m in flaps["back"]] + [(tuck_m, IN), (back, 90.0)],
                duration_ms=2200),
]
assembled = {"box": {"angles": dict(ANG), "root": ROOT}}
for rod, ms in zip(rods, rod_marks, strict=True):
    assembled[rod.id] = {"angles": rod_angles(ms), "root": (A / 2, LR / 2)}
result = pliego.Assembly(
    [box] + frames + rods,
    controls=[pliego.sequence_control(label=L4("Build the box", "Armar la caja",
                                               "Monter la boîte", "Montar a caixa"))],
    sequence=pliego.Sequence(steps, mode="kinematic"),
    targets={"assembled": assembled},
    title="Shadow box",
    meta={"min_feature_mm": MINF},
)
