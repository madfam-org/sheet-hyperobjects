"""Step pop-up — sheet-hyperobjects cartridge (Pliego).

A staircase that rises out of one cut-and-scored card. The card is a spread of two pages
(`page_width` × `page_height` each) with the gutter at u = page_width. Pairs of slits cross the
gutter and three scored folds between each pair make a step; every further step is cut, narrower,
into the corner of the step before it ("nested" step folds), so `steps` levels make a staircase of
`steps` risers.

Kinematics (Tier R, exact). Every fold is parallel to the gutter, so the card moves in its
cross-section. Each level is a parallelogram four-bar nested in the corner of its parent: corner
C, attachment points A and B on the two panels that meet at C, at distances a and b, and the new
fold F = A + B − C. Because opposite sides are equal, the angle at F equals the angle at C, so
every level sees the same opening and **every fold of the card turns by the same magnitude γ, the
gutter angle**: A and B with the sign of their corner, F with the opposite sign. Level k of an
n-step staircase uses (m = n − k + 1): a = m·tread, b = m·riser on odd levels, a = m·riser,
b = m·tread on even levels. Flat at γ = 0, folded flat at γ = 180°, never locked.

The fold program is kinematic: the flat card is folded shut (the steps fold inward) and opened to
90°, where the stairs stand. Closure is checked in this script with
`pliego.kinematics.closure_residual` at every state and midpoint (fail loud); the slits make the
solver's vertex loops vacuous (every vertex touches a cut), so the residual over every crease,
including the loop through each step, is the check.
"""

import pliego
from pliego import kinematics


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


page_width = float(PARAM(lambda: page_width, 150.0))       # noqa: F821
page_height = float(PARAM(lambda: page_height, 150.0))     # noqa: F821
steps = int(round(float(PARAM(lambda: steps, 3))))         # noqa: F821
riser = float(PARAM(lambda: riser, 18.0))                  # noqa: F821
tread = float(PARAM(lambda: tread, 18.0))                  # noqa: F821
step_width = float(PARAM(lambda: step_width, 90.0))        # noqa: F821
inset = float(PARAM(lambda: inset, 10.0))                  # noqa: F821
open_angle = float(PARAM(lambda: open_angle, 90.0))        # noqa: F821
stock = PARAM(lambda: stock, "cardstock-160")              # noqa: F821

W = pliego.clamp(page_width, 90.0, 220.0)
H = pliego.clamp(page_height, 90.0, 260.0)
n = int(pliego.clamp(steps, 1, 5))
r = pliego.clamp(riser, 6.0, 40.0)
t = pliego.clamp(tread, 6.0, 40.0)
w1 = pliego.clamp(step_width, 30.0, 200.0)
s_in = pliego.clamp(inset, 3.0, 25.0)
phi_end = pliego.clamp(open_angle, 30.0, 150.0)
if stock not in ("cardstock-160", "cardstock-250", "kraft-120", "copy-80"):
    raise ValueError(f"step-popup: unsupported stock {stock!r}")

MARGIN = 6.0
MIN_WIDTH = 10.0
TOL_MM = 1e-6
SUBSTEPS = {"close": 10, "open": 8}


def L4(en, es, fr, pt):
    return {"en": en, "es": es, "fr": fr, "pt": pt}


# ── fit checks (fail loud) ───────────────────────────────────────────────────

if n * (t + r) > W - MARGIN:
    raise ValueError(f"step-popup: {n} steps of {t:g} + {r:g} mm reach {n * (t + r):g} mm from the "
                     f"gutter when the card is shut; the page is {W:g} mm (keep "
                     f"steps·(tread + riser) ≤ page_width − {MARGIN:g})")
widths = [w1 - 2.0 * s_in * k for k in range(n)]
if widths[-1] < MIN_WIDTH:
    raise ValueError(f"step-popup: the top step would be {widths[-1]:g} mm wide; reduce the inset "
                     f"or the number of steps (minimum {MIN_WIDTH:g} mm)")
if w1 > H - 2 * MARGIN:
    raise ValueError(f"step-popup: step_width {w1:g} mm does not fit a {H:g} mm page")

# ── levels: corner position c, distances a/b, fold signs (material coordinate s = u − W) ──

yc = H / 2.0
levels = []
corner, sign = 0.0, 1           # the gutter: a valley at s = 0
for k in range(n):
    m = n - k
    a, b = (m * t, m * r) if k % 2 == 0 else (m * r, m * t)
    levels.append({"c": corner, "a": a, "b": b, "sign": sign, "w": widths[k]})
    corner, sign = corner - a + b, -sign

sheet = pliego.Sheet(
    "card", [(0, 0), (2 * W, 0), (2 * W, H), (0, H)], stock=stock, grain_deg=90.0,
    label=L4("Card with step folds", "Tarjeta con escalones", "Carte à marches",
             "Cartão com degraus"),
)
sheet.label_edge("fore-edge-left", (0, 0), (0, H))
sheet.label_edge("fore-edge-right", (2 * W, 0), (2 * W, H))

KIND = {1: "valley", -1: "mountain"}
creases = []                    # (mark, sign)

gutter_lab = L4("Gutter (the card's spine)", "Pliegue central (lomo de la tarjeta)",
                "Pliure centrale (dos de la carte)", "Dobra central (lombada do cartão)")
lo, hi = yc - w1 / 2.0, yc + w1 / 2.0
for y0, y1 in ((0.0, lo), (hi, H)):
    creases.append((sheet.valley((W, y0), (W, y1), treatment="score", label=gutter_lab,
                                 name="gutter"), 1))

for k, lv in enumerate(levels):
    c, a, b, sg, w = lv["c"], lv["a"], lv["b"], lv["sign"], lv["w"]
    y0, y1 = yc - w / 2.0, yc + w / 2.0
    xa, xf, xb = W + c - a, W + c - a + b, W + c + b
    sheet.cut([(xa, y0), (xb, y0)], name=f"slit-{k + 1}")
    sheet.cut([(xa, y1), (xb, y1)], name=f"slit-{k + 1}")
    num = k + 1
    creases.append((sheet.crease((xa, y0), (xa, y1), KIND[sg], treatment="score", label=L4(
        f"Step {num}: foot fold", f"Escalón {num}: pliegue de base",
        f"Marche {num} : pli de pied", f"Degrau {num}: dobra da base")), sg))
    creases.append((sheet.crease((xb, y0), (xb, y1), KIND[sg], treatment="score", label=L4(
        f"Step {num}: head fold", f"Escalón {num}: pliegue de remate",
        f"Marche {num} : pli de tête", f"Degrau {num}: dobra do topo")), sg))
    edge_lab = L4(f"Step {num}: nose (the edge that comes forward)",
                  f"Escalón {num}: arista (el borde que avanza)",
                  f"Marche {num} : nez (l'arête qui avance)",
                  f"Degrau {num}: quina (a aresta que avança)")
    if k + 1 < n:               # the next level is cut into this fold: keep its two ends
        w_next = levels[k + 1]["w"]
        for ya, yb in ((y0, yc - w_next / 2.0), (yc + w_next / 2.0, y1)):
            creases.append((sheet.crease((xf, ya), (xf, yb), KIND[-sg], treatment="score",
                                         label=edge_lab), -sg))
    else:
        creases.append((sheet.crease((xf, y0), (xf, y1), KIND[-sg], treatment="score",
                                     label=edge_lab), -sg))

arr = sheet.build()
ROOT = pliego.P(MARGIN, MARGIN)            # the left page stays down


def state(gamma):
    """{mark: deg} of the card at gutter angle γ (every fold turns by ±γ)."""
    return {m: sg * gamma for m, sg in creases}


def edge_angles(gamma):
    out = {}
    for m, sg in creases:
        for e in m.edges():
            out[e] = sg * gamma
    return out


def extent(gamma):
    """World bounding box of every face of the card at gutter angle γ."""
    tr = kinematics.face_transforms(arr, edge_angles(gamma), kinematics.root_face(arr, ROOT))
    pts = []
    for fi, f in enumerate(arr.faces):
        rot, off = tr[fi]
        for v in f:
            p = (arr.vertices[v].x, 0.0, -arr.vertices[v].y)
            pts.append(tuple(sum(rot[i][j] * p[j] for j in range(3)) + off[i] for i in range(3)))
    return ([min(p[i] for p in pts) for i in range(3)], [max(p[i] for p in pts) for i in range(3)])


# ── the fold program: shut, then open to the display angle ───────────────────

gamma_end = 180.0 - phi_end
key_steps = [
    pliego.Step("close", L4("Fold the card shut: every step folds inward",
                            "Cierra la tarjeta: cada escalón se dobla hacia dentro",
                            "Fermez la carte : chaque marche se replie vers l'intérieur",
                            "Feche o cartão: cada degrau se dobra para dentro"),
                [(m, a) for m, a in state(180.0).items()], duration_ms=3000),
    pliego.Step("open", L4(f"Open the card to {phi_end:g}°: the stairs stand up",
                           f"Abre la tarjeta a {phi_end:g}°: la escalera se levanta",
                           f"Ouvrez la carte à {phi_end:g}° : l'escalier se dresse",
                           f"Abra o cartão a {phi_end:g}°: a escada se ergue"),
                [(m, a) for m, a in state(gamma_end).items()], duration_ms=2400),
]
program = pliego.Sequence.kinematic_path(sheet, key_steps, substeps=SUBSTEPS)

# closure at every program state and at every midpoint (the preview blends between states)
worst = 0.0
prev = {e: 0.0 for m, _ in creases for e in m.edges()}
for st in program.steps:
    cur = dict(prev)
    for ref, ang in st.targets:
        cur[ref.edge] = ang
    mid = {e: (prev[e] + cur[e]) / 2.0 for e in cur}
    worst = max(worst, kinematics.closure_residual(arr, cur, ROOT),
                kinematics.closure_residual(arr, mid, ROOT))
    prev = cur
if worst > 1e-6:
    raise ValueError(f"step-popup: inconsistent rigid state (closure residual {worst:.3g} mm)")

# containment: shut, everything lies in the closed page; at 180° it is the flat card
lo3, hi3 = extent(180.0)
if lo3[0] < -TOL_MM or hi3[0] > W + TOL_MM or abs(hi3[1]) > TOL_MM + 1e-6 or \
        abs(lo3[1]) > TOL_MM + 1e-6:
    raise ValueError(f"step-popup: the shut card is not flat or something sticks out "
                     f"({lo3}, {hi3})")
print(f"kinematics: levels={n} program_steps={len(program.steps)} "
      f"max_closure_mm={worst:.3e} shut_extent_mm={hi3[0]:.3f} of {W:g}")

result = pliego.Assembly(
    [sheet],
    controls=[pliego.sequence_control(
        label=L4("Close and open", "Cerrar y abrir", "Fermer et ouvrir", "Fechar e abrir"),
        default=float(len(program.steps)))],
    sequence=program,
    title="Step pop-up",
)
