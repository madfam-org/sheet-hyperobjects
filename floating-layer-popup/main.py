"""Floating-layer pop-up — sheet-hyperobjects cartridge (Pliego).

A layer that floats on two supports, cut and scored from one card. The supports are two narrow
step folds at the sides; the layer is the panel between them, cut free of the card everywhere
except along its sides, where it continues into the supports. A gap cut under the layer lifts it
off the base page, and its top can rise above the supports with a shaped outline (straight, arch,
gable or scallops). Opened to 90°, the layer stands parallel to one page and clear of both.

Kinematics (Tier R, exact). The supports are a parallelogram four-bar: corner G (the gutter),
attachment folds A and B at `layer_distance` (p) and `support_height` (q) from it, fold F = A + B −
G. The layer is rigid with the supports' A–F panels, so it moves with them: every fold turns by the
gutter angle γ (A and B valleys, F a mountain). `orientation` chooses which page the layer is
parallel to: `upright` (parallel to the back page, standing p in front of it) or `level` (parallel
to the base page, a platform p above it); the second is the mirror image of the first across the
gutter.

The program is kinematic: fold the card shut, open it to 90°. `kinematics.closure_residual` is
checked at every state (fail loud), the cuts are checked with `pliego.papercut.analyze`, and the
shut card must be flat and inside its page.
"""

import math

import pliego
from pliego import kinematics


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


page_width = float(PARAM(lambda: page_width, 150.0))          # noqa: F821
page_height = float(PARAM(lambda: page_height, 150.0))        # noqa: F821
orientation = PARAM(lambda: orientation, "upright")           # noqa: F821
layer_distance = float(PARAM(lambda: layer_distance, 35.0))   # noqa: F821
support_height = float(PARAM(lambda: support_height, 40.0))   # noqa: F821
gap = float(PARAM(lambda: gap, 10.0))                         # noqa: F821
rise = float(PARAM(lambda: rise, 12.0))                       # noqa: F821
layer_width = float(PARAM(lambda: layer_width, 70.0))         # noqa: F821
support_width = float(PARAM(lambda: support_width, 10.0))     # noqa: F821
outline = PARAM(lambda: outline, "arch")                      # noqa: F821
peak = float(PARAM(lambda: peak, 12.0))                       # noqa: F821
stock = PARAM(lambda: stock, "cardstock-160")                 # noqa: F821

W = pliego.clamp(page_width, 90.0, 220.0)
H = pliego.clamp(page_height, 90.0, 260.0)
p = pliego.clamp(layer_distance, 8.0, 80.0)
q = pliego.clamp(support_height, 15.0, 100.0)
g = pliego.clamp(gap, 2.0, 40.0)
e = pliego.clamp(rise, 0.0, 60.0)
lw = pliego.clamp(layer_width, 20.0, 200.0)
ws = pliego.clamp(support_width, 5.0, 30.0)
pk = pliego.clamp(peak, 0.0, 40.0)
if orientation not in ("upright", "level"):
    raise ValueError(f"floating-layer-popup: unknown orientation {orientation!r}")
if outline not in ("straight", "arch", "gable", "scallops"):
    raise ValueError(f"floating-layer-popup: unknown outline {outline!r}")
if stock not in ("cardstock-160", "cardstock-250", "kraft-120"):
    raise ValueError(f"floating-layer-popup: unsupported stock {stock!r}")
if outline == "straight":
    pk = 0.0

MARGIN = 6.0
MIN_FEATURE = 2.0
TOL_MM = 1e-6
SIGN = 1.0 if orientation == "upright" else -1.0     # the mirror across the gutter


def L4(en, es, fr, pt):
    return {"en": en, "es": es, "fr": fr, "pt": pt}


# ── fit checks (fail loud) ───────────────────────────────────────────────────

s_a, s_f, s_b = -p, -p + q, q          # canonical material coordinate s = ±(u − W)
s_top = s_f + e                        # the layer's top edge at its sides
if g > q - 8.0:
    raise ValueError("floating-layer-popup: the gap leaves less than 8 mm of support under the "
                     "layer")
if s_top + pk > s_b - MIN_FEATURE * 2:
    raise ValueError(f"floating-layer-popup: the layer rises {e + pk:g} mm above its supports; "
                     f"it is cut from the {p:g} mm between the supports' shoulders and the far "
                     f"page, so keep rise + peak ≤ layer_distance − {2 * MIN_FEATURE:g} mm")
if p + q + e + pk > W - MARGIN or max(p, q) > W - MARGIN:
    raise ValueError(f"floating-layer-popup: shut, the layer reaches {p + q + e + pk:g} mm "
                     f"from the gutter; the page is {W:g} mm")
total_w = lw + 2 * ws
if total_w > H - 2 * MARGIN:
    raise ValueError(f"floating-layer-popup: layer and supports ({total_w:g} mm) do not fit a "
                     f"{H:g} mm card")

y0 = (H - total_w) / 2.0
ya, yb, y1 = y0 + ws, y0 + ws + lw, y0 + total_w


def X(s):
    return W + SIGN * s


def pt(s, y):
    return (X(s), y)


def contour():
    """The layer's top edge from (s_top, ya) to (s_top, yb), shaped by `outline`."""
    if outline == "straight" or pk <= 0:
        return [pt(s_top, ya), pt(s_top, yb)]
    n = 24 if outline != "gable" else 2
    out = []
    for i in range(n + 1):
        tt = i / n
        if outline == "arch":
            h = pk * math.sin(math.pi * tt)
        elif outline == "gable":
            h = pk * (1.0 - abs(2.0 * tt - 1.0))
        else:
            h = pk * abs(math.sin(3.0 * math.pi * tt))
        out.append(pt(s_top + h, ya + (yb - ya) * tt))
    return out


card = pliego.Sheet(
    "card", [(0, 0), (2 * W, 0), (2 * W, H), (0, H)], stock=stock, grain_deg=90.0,
    label=L4("Card with a floating layer", "Tarjeta con capa flotante",
             "Carte à couche flottante", "Cartão com camada flutuante"))
card.cut([pt(s_a, y0), pt(s_b, y0)], name="slit")
card.cut([pt(s_a, y1), pt(s_b, y1)], name="slit")
card.hole([pt(s_a, ya), pt(s_a + g, ya), pt(s_a + g, yb), pt(s_a, yb)])
top = contour()
card.hole(top + [pt(s_b, yb), pt(s_b, ya)])
if e > 0:
    card.cut([pt(s_f, ya), pt(s_top, ya)], name="layer-side")
    card.cut([pt(s_f, yb), pt(s_top, yb)], name="layer-side")

creases = []
gut = L4("Gutter (the card's spine)", "Pliegue central (lomo de la tarjeta)",
         "Pliure centrale (dos de la carte)", "Dobra central (lombada do cartão)")
for ys, ye in ((0.0, y0), (y1, H)):
    creases.append((card.valley((W, ys), (W, ye), treatment="score", label=gut, name="gutter"), 1))
for ys, ye in ((y0, ya), (yb, y1)):
    creases.append((card.valley(pt(s_a, ys), pt(s_a, ye), treatment="score", label=L4(
        "Support: foot fold", "Soporte: pliegue de base", "Support : pli de pied",
        "Suporte: dobra da base")), 1))
    creases.append((card.mountain(pt(s_f, ys), pt(s_f, ye), treatment="score", label=L4(
        "Support: shoulder fold", "Soporte: pliegue del hombro", "Support : pli d'épaule",
        "Suporte: dobra do ombro")), -1))
    creases.append((card.valley(pt(s_b, ys), pt(s_b, ye), treatment="score", label=L4(
        "Support: head fold", "Soporte: pliegue de remate", "Support : pli de tête",
        "Suporte: dobra do topo")), 1))

report = pliego.papercut.analyze(card, min_feature_mm=MIN_FEATURE)
bad = [i for i in report.issues if i["level"] == "error"]
if bad:
    raise ValueError(f"floating-layer-popup: papercut check failed: {bad}")

arr = card.build()
ROOT = pliego.P(MARGIN / 2.0, MARGIN / 2.0)


def edge_angles(gamma):
    return {e_: sg * gamma for m, sg in creases for e_ in m.edges()}


def extent(gamma):
    tr = kinematics.face_transforms(arr, edge_angles(gamma), kinematics.root_face(arr, ROOT))
    pts = []
    for fi, f in enumerate(arr.faces):
        rot, off = tr[fi]
        for v in f:
            p3 = (arr.vertices[v].x, 0.0, -arr.vertices[v].y)
            pts.append([sum(rot[i][j] * p3[j] for j in range(3)) + off[i] for i in range(3)])
    return ([min(c[i] for c in pts) for i in range(3)], [max(c[i] for c in pts) for i in range(3)])


steps_key = [
    pliego.Step("close", L4("Fold the card shut: the layer folds down with its supports",
                            "Cierra la tarjeta: la capa se pliega con sus soportes",
                            "Fermez la carte : la couche se replie avec ses supports",
                            "Feche o cartão: a camada se dobra com seus suportes"),
                [(m, sg * 180.0) for m, sg in creases], duration_ms=3000),
    pliego.Step("open", L4("Open it to 90°: the layer floats", "Ábrela a 90°: la capa flota",
                           "Ouvrez-la à 90° : la couche flotte", "Abra-o a 90°: a camada flutua"),
                [(m, sg * 90.0) for m, sg in creases], duration_ms=2400),
]
program = pliego.Sequence.kinematic_path(card, steps_key, substeps={"close": 10, "open": 8})
worst = 0.0
prev = edge_angles(0.0)
for st in program.steps:
    cur = dict(prev)
    for ref, ang in st.targets:
        cur[ref.edge] = ang
    worst = max(worst, kinematics.closure_residual(arr, cur, ROOT),
                kinematics.closure_residual(arr, {k: (prev[k] + cur[k]) / 2 for k in cur}, ROOT))
    prev = cur
if worst > 1e-6:
    raise ValueError(f"floating-layer-popup: inconsistent rigid state ({worst:.3g} mm)")
lo3, hi3 = extent(180.0)
if lo3[0] < -TOL_MM or hi3[0] > W + TOL_MM or max(abs(lo3[1]), abs(hi3[1])) > 1e-6:
    raise ValueError(f"floating-layer-popup: the shut card is not flat or the layer sticks out "
                     f"({lo3}, {hi3})")
print(f"kinematics: orientation={orientation} program_steps={len(program.steps)} "
      f"max_closure_mm={worst:.3e} papercut_bridge_mm={report.min_bridge_mm} "
      f"layer_clearance_mm={g:g}")

result = pliego.Assembly(
    [card],
    controls=[pliego.sequence_control(
        label=L4("Close and open", "Cerrar y abrir", "Fermer et ouvrir", "Fechar e abrir"),
        default=float(len(program.steps)))],
    sequence=program,
    title="Floating-layer pop-up",
)
