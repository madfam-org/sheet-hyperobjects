"""Saddle stitch — sheet-hyperobjects cartridge (Pliego).

The stapled booklet: `pages / 4` sheets, each a spread folded once at its centre, nested one
inside the other (the outer sheet is the cover) and stapled through the spine fold.

* **Creep (shingling).** Every sheet wraps round all the sheets inside it, so the inner sheets
  push out at the fore-edge. The fold of sheet k (counted from the outside, cover = 0) sits
  D_k = Σ_{j<k} (t_j + t_{j+1}) / 2 inside the cover's fold (t = caliper of each sheet, from its
  stock card). The fore-edge push-out is shift_k = f · D_k with f = 1 for a pressed fold (the
  trade rule: one caliper per sheet) or f = π/2 for a round fold (concentric half-circles). This
  cartridge pre-trims: sheet k is cut 2 · shift_k narrower, centred on its fold, so the
  fore-edges line up once folded and no guillotine trim is needed. Self-check (fail loud): the
  nest is folded in 3-D with thickness (one auxiliary sheet per spread, its fold a band of m
  facets on the half-circle of its radius: m = 1 is the pressed fold, m = 60 the round one;
  placement + fold angles through `pliego.kinematics.face_transforms`) and every trimmed
  fore-edge must land on the cover's.
* **Imposition.** The page numbers on each sheet face are computed from the shut booklet (layer
  order along the stack, front cover from the binding side) and checked against the classic
  rule (outer sheet: N and 1 outside, 2 and N − 1 inside). The studio renders no text, so they
  are written into the step notes and printed on the read-proof line.
* **Staples.** `string` joins (physics engine) chain the spine folds of consecutive sheets at
  each staple point; the length is the sheets' fold spacing, so the nest cannot part there.
  Staples sit at (2i + 1) / (2m) of the spine for m staples (¼ and ¾ for two).
* **Preview.** Zero-thickness rigid sheets cannot stack at exactly 180°, so the creases are
  nested a fold spacing apart (each sheet's fold one caliper outside the fold it wraps) and the
  sheets fan by DELTA degrees per layer. Every key state keeps each inner sheet inside the wedge
  of the sheet that wraps it, and the fold program moves all creases linearly with the same
  sweep, so in-between states stay ordered too (checked).
"""

import math

import pliego


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


pages = int(PARAM(lambda: pages, 16))                       # noqa: F821
page_width = float(PARAM(lambda: page_width, 148.0))        # noqa: F821
page_height = float(PARAM(lambda: page_height, 210.0))      # noqa: F821
stock = PARAM(lambda: stock, "copy-80")                     # noqa: F821
cover_stock = PARAM(lambda: cover_stock, "self")            # noqa: F821
creep_rule = PARAM(lambda: creep_rule, "pressed")           # noqa: F821
staples = int(PARAM(lambda: staples, 2))                    # noqa: F821
binding = PARAM(lambda: binding, "left")                    # noqa: F821

STOCKS = ("copy-80", "kraft-120", "washi-kozo-30")
COVERS = ("self", "cardstock-160", "cardstock-250", "kraft-120")
if stock not in STOCKS:
    raise ValueError(f"saddle-stitch: stock must be one of {STOCKS}, got {stock!r}")
if cover_stock not in COVERS:
    raise ValueError(f"saddle-stitch: cover_stock must be one of {COVERS}, got {cover_stock!r}")
if creep_rule not in ("pressed", "round"):
    raise ValueError(f"saddle-stitch: creep_rule must be pressed or round, got {creep_rule!r}")
if binding not in ("left", "right"):
    raise ValueError(f"saddle-stitch: binding must be left or right, got {binding!r}")
if pages % 4 or not 8 <= pages <= 64:
    raise ValueError(f"saddle-stitch: pages must be a multiple of 4 in 8…64, got {pages}")
if staples not in (2, 3):
    raise ValueError(f"saddle-stitch: staples must be 2 or 3, got {staples}")

N = pages
n = N // 4                                    # sheets (spreads)
w = pliego.clamp(page_width, 70.0, 300.0)     # finished page
H = pliego.clamp(page_height, 70.0, 420.0)
F = 1.0 if creep_rule == "pressed" else math.pi / 2.0
DELTA = 0.2          # preview fan per layer (degrees)
GAP_IN = 0.5         # the innermost sheet shuts to 179.5° (the preview's flat limit)
M_BAND = 1 if creep_rule == "pressed" else 60      # facets of the thick fold in the self-check
TOL = 0.005          # mm, fore-edge coincidence


def L4(en, es, fr, pt):
    return {"en": en, "es": es, "fr": fr, "pt": pt}


def caliper(slug):
    return float(pliego.resolve_stock(slug, None)["caliper_mm"])


sheet_stock = [stock if (k or cover_stock == "self") else cover_stock for k in range(n)]
t = [caliper(s) for s in sheet_stock]
d = [(t[k] + t[k + 1]) / 2.0 for k in range(n - 1)]          # fold spacing, sheet k → k + 1
D = [sum(d[:k]) for k in range(n)]                             # fold k inside the cover's fold
shift = [F * D[k] for k in range(n)]                           # fore-edge push-out = trim
half = [w - shift[k] for k in range(n)]                        # trimmed half width
if half[-1] < 0.9 * w:
    raise ValueError("saddle-stitch: the creep eats more than a tenth of the page; use fewer "
                     "pages or thinner paper")

# ── the preview pose: nested creases, fanned layers ──────────────────────────
LAM = [k * DELTA for k in range(n)]                            # elevation of the fixed half
GAM = [GAP_IN + 2.0 * (n - 1 - k) * DELTA for k in range(n)]   # opening left when shut
OPEN = [2.0 * k * DELTA for k in range(n)]                     # open flat (cover exactly flat)
SHUT = [180.0 - GAM[k] for k in range(n)]
SWEEP = SHUT[0] - OPEN[0]
SADDLE = [OPEN[k] + 0.5 * SWEEP for k in range(n)]             # half shut, as on the saddle
P = [(0.0, 0.0)]
for k in range(n - 1):
    beta = math.radians(180.0 - LAM[k] - GAM[k] / 2.0)         # into the wedge it wraps
    P.append((P[k][0] + d[k] * math.cos(beta), P[k][1] + d[k] * math.sin(beta)))

SPINE = L4("Spine fold", "Doblez del lomo", "Pli du dos", "Dobra da lombada")
sheets, spines = [], []
for k in range(n):
    a = half[k]
    lam = math.radians(LAM[k])
    rot = (0.0, 0.0, math.sin(-lam / 2.0), math.cos(-lam / 2.0))
    origin = (P[k][0] - a * math.cos(lam), P[k][1] + a * math.sin(lam), 0.0)
    label = (L4("Cover sheet", "Pliego de cubierta", "Feuille de couverture", "Folha da capa")
             if k == 0 else L4(f"Sheet {k + 1}", f"Pliego {k + 1}", f"Feuille {k + 1}",
                               f"Folha {k + 1}"))
    s = pliego.Sheet(f"sheet-{k + 1}", [(0, 0), (2 * a, 0), (2 * a, H), (0, H)],
                     stock=sheet_stock[k], grain_deg=90.0, label=label,
                     placement=pliego.Placement(origin=origin, rotation=rot))
    treat = "score" if sheet_stock[k].startswith("cardstock") else "crease"
    spines.append(s.valley((a, 0), (a, H), treatment=treat, name="spine", label=SPINE))
    s.label_edge("fore-edge", (0, 0), (0, H))
    s.label_edge("fore-edge", (2 * a, 0), (2 * a, H))
    sheets.append(s)
arrs = [s.build() for s in sheets]


def mat_vec(m, v):
    return tuple(m[i][0] * v[0] + m[i][1] * v[1] + m[i][2] * v[2] for i in range(3))


def placed(k, tr, u, v):
    """World point of sheet k's local (u, v) on a face with transform tr (placement applied)."""
    p = mat_vec(tr[0], (u, 0.0, -v))
    p = (p[0] + tr[1][0], p[1] + tr[1][1], p[2] + tr[1][2])
    lam = math.radians(LAM[k])
    c, sn = math.cos(-lam), math.sin(-lam)
    o = sheets[k].placement.origin
    return (c * p[0] - sn * p[1] + o[0], sn * p[0] + c * p[1] + o[1], p[2] + o[2])


def halves(k, angles):
    """Posed sheet k: [(face index, which half 'L'/'R', transform)]."""
    arr = arrs[k]
    tr = pliego.kinematics.face_transforms(arr, {e: angles[k] for e in spines[k].edges()}, 0)
    out = []
    for fi, f in enumerate(arr.faces):
        cx = sum(arr.vertices[v].x for v in f) / len(f)
        out.append((fi, "L" if cx < half[k] else "R", tr[fi]))
    if sorted(h for _, h, _ in out) != ["L", "R"]:
        raise ValueError(f"saddle-stitch: sheet {k + 1} did not split into two halves")
    return out


def arm_dirs(k, angles):
    """Section directions (deg) of the two halves of sheet k, from its posed fore-edges."""
    res = {}
    for _, hh, tr in halves(k, angles):
        u = 0.0 if hh == "L" else 2 * half[k]
        q = placed(k, tr, u, H / 2.0)
        res[hh] = math.degrees(math.atan2(q[1] - P[k][1], q[0] - P[k][0])) % 360.0
    return res


def nested_ok(angles):
    """Each inner sheet lies inside the wedge of the sheet that wraps it (worst margin, deg)."""
    worst = 180.0
    for k in range(n - 1):
        o, i = arm_dirs(k, angles), arm_dirs(k + 1, angles)
        lo, hi = o["R"], o["L"]                      # the wedge runs CCW from R to L
        span = (hi - lo) % 360.0
        apex = math.degrees(math.atan2(P[k + 1][1] - P[k][1], P[k + 1][0] - P[k][0]))
        for ang in (apex, i["R"], i["L"]):
            rel = (ang - lo) % 360.0
            worst = min(worst, rel, span - rel)
    return worst


for frac in (0.0, 0.25, 0.5, 0.75, 1.0):
    state = [OPEN[k] + frac * (SHUT[k] - OPEN[k]) for k in range(n)]
    if n > 1 and nested_ok(state) < 1e-6:
        raise ValueError(f"saddle-stitch: preview layers cross at {frac:.0%} of the fold")

# ── creep self-check: the nest folded in 3-D with thickness ──────────────────
T_STACK = 2.0 * sum(t)
Y_L = [sum(t[:k]) + t[k] / 2.0 for k in range(n)]             # mid-plane of each left half
Y_C = T_STACK / 2.0                                            # spine centre (stack middle)
fore = []
for k in range(n):
    r = Y_C - Y_L[k]
    b = 2.0 * r * math.sin(math.radians(90.0 / M_BAND))       # chord of the fold band
    a = half[k]
    u0 = a - M_BAND * b / 2.0
    aux = pliego.Sheet(f"thick-{k + 1}", [(0, 0), (2 * a, 0), (2 * a, H), (0, H)],
                       stock=sheet_stock[k])
    band = [aux.valley((u0 + i * b, 0), (u0 + i * b, H), name="fold-band")
            for i in range(M_BAND + 1)]
    ang = {}
    for i, mk in enumerate(band):
        for e in mk.edges():
            ang[e] = 90.0 / M_BAND if i in (0, M_BAND) else 180.0 / M_BAND
    aarr = aux.build()
    atr = pliego.kinematics.face_transforms(aarr, ang, 0)
    lift = (-u0, Y_L[k])                                       # band start onto x = 0
    xs = []
    for fi, f in enumerate(aarr.faces):
        us = [aarr.vertices[v].x for v in f]
        for u in (0.0, 2 * a):
            if min(abs(x - u) for x in us) < 1e-5:
                q = mat_vec(atr[fi][0], (u, 0.0, -H / 2.0))
                q = (q[0] + atr[fi][1][0] + lift[0], q[1] + atr[fi][1][1] + lift[1])
                xs.append(q)
    if len(xs) != 2:
        raise ValueError(f"saddle-stitch: thick fold of sheet {k + 1} lost a fore-edge")
    lo_q, hi_q = sorted(xs, key=lambda q: q[1])
    if abs(hi_q[1] - (T_STACK - Y_L[k])) > 1e-6:
        raise ValueError(f"saddle-stitch: sheet {k + 1} did not wrap to its layer")
    fore.extend([lo_q[0], hi_q[0]])
spread = max(fore) - min(fore)
if spread > TOL:
    raise ValueError(f"saddle-stitch: trimmed fore-edges miss by {spread:.4f} mm (> {TOL})")
untrimmed = F * D[-1]                    # what the innermost sheet would stick out uncorrected

# ── imposition, from the shut preview pose ───────────────────────────────────
layers = []                              # (height at mid-page, sheet, half, front-up?)
for k in range(n):
    for fi, hh, tr in halves(k, SHUT):
        u = 0.0 if hh == "L" else 2 * half[k]
        q0, q1 = placed(k, tr, half[k], H / 2.0), placed(k, tr, u, H / 2.0)
        x = -0.5 * half[-1]
        y = q0[1] + (q1[1] - q0[1]) * (x - q0[0]) / (q1[0] - q0[0])
        nrm = mat_vec(tr[0], (0.0, 1.0, 0.0))
        lam = math.radians(LAM[k])
        ny = math.sin(-lam) * nrm[0] + math.cos(-lam) * nrm[1]
        layers.append((y, k, hh, ny > 0))
layers.sort()
expect = [(k, "L") for k in range(n)] + [(k, "R") for k in reversed(range(n))]
if [(k, hh) for _, k, hh, _ in layers] != expect:
    raise ValueError("saddle-stitch: the shut layers are not nested cover-outside")
# The bottom layer seen from outside (below), head up (sheet +v → world −z): is its spine on
# the binding side? Then it is the front cover; otherwise the top layer is.
up, outward = (0.0, 0.0, -1.0), (0.0, -1.0, 0.0)
right = (up[1] * outward[2] - up[2] * outward[1], up[2] * outward[0] - up[0] * outward[2],
         up[0] * outward[1] - up[1] * outward[0])
centre_x = P[0][0] - half[0] / 2.0       # middle of the cover's fixed half (λ = 0)
spine_side = "left" if (P[0][0] - centre_x) * right[0] < 0 else "right"
front_cover_bottom = spine_side == binding
order = layers if front_cover_bottom else list(reversed(layers))
page = {}                                # (sheet, half, 'front'|'back') → page number
for ell, (_, k, hh, front_up) in enumerate(order):
    toward_front = "down" if front_cover_bottom else "up"
    side_toward_front = ("front" if front_up else "back") if toward_front == "up" else \
                        ("back" if front_up else "front")
    other = "back" if side_toward_front == "front" else "front"
    page[(k, hh, side_toward_front)] = 2 * ell + 1
    page[(k, hh, other)] = 2 * ell + 2
imposition = []
for k in range(n):
    outside = (page[(k, "R", "back")], page[(k, "L", "back")])     # sheet turned over
    inside = (page[(k, "L", "front")], page[(k, "R", "front")])
    if binding == "left":
        want = ((N - 2 * k, 2 * k + 1), (2 * k + 2, N - 2 * k - 1))
    else:
        want = ((2 * k + 1, N - 2 * k), (N - 2 * k - 1, 2 * k + 2))
    if (outside, inside) != want:
        raise ValueError(f"saddle-stitch: sheet {k + 1} imposes {outside}/{inside}, "
                         f"not the classic {want}")
    imposition.append((outside, inside))

# ── staples: string joins chaining the spine folds ───────────────────────────
STAPLE_V = [H * (2 * i + 1) / (2 * staples) for i in range(staples)]
joins = []
for i, v in enumerate(STAPLE_V):
    for k in range(n - 1):
        pa = placed(k, halves(k, OPEN)[0][2], half[k], v)
        pb = placed(k + 1, halves(k + 1, OPEN)[0][2], half[k + 1], v)
        gap = math.sqrt(sum((pa[c] - pb[c]) ** 2 for c in range(3)))
        if gap > d[k] + 1e-9:
            raise ValueError(f"saddle-stitch: staple {i + 1} cannot reach sheet {k + 2}")
        joins.append(pliego.string(f"staple-{i + 1}-{k + 1}", (sheets[k], (half[k], v)),
                                   (sheets[k + 1], (half[k + 1], v)), d[k]))

# ── the fold program ─────────────────────────────────────────────────────────


def pp(pair):
    return f"{pair[0]}|{pair[1]}"


WORDS = {"en": ("sheet", "outside", "inside", "cover"),
         "es": ("pliego", "cara exterior", "cara interior", "cubierta"),
         "fr": ("feuille", "extérieur", "intérieur", "couverture"),
         "pt": ("folha", "lado de fora", "lado de dentro", "capa")}


def imposition_text(lang):
    sh, out, ins, cov = WORDS[lang]
    rows = []
    for k, (o, i) in enumerate(imposition):
        name = f"{sh} {k + 1}" + (f" ({cov})" if k == 0 else "")
        rows.append(f"{name}: {out} {pp(o)}, {ins} {pp(i)}")
    return "; ".join(rows)


shift_txt = " ".join(f"{s:.2f}" for s in shift)
stap_txt = ", ".join(f"{v:.1f}" for v in STAPLE_V)
INTRO = L4("Pages per sheet, left|right as you look at each face: ",
           "Páginas de cada pliego, izquierda|derecha mirando cada cara: ",
           "Pages de chaque feuille, gauche|droite en regardant chaque face : ",
           "Páginas de cada folha, esquerda|direita olhando cada face: ")
NOTES = {
    "saddle": {lang: INTRO[lang] + imposition_text(lang) + "." for lang in WORDS},
    "stitch": L4(f"{staples} staples through the fold, driven from outside and clinched in the "
                 f"centre spread, at {stap_txt} mm from the head.",
                 f"{staples} grapas a través del doblez, clavadas desde fuera y remachadas en el "
                 f"pliego central, a {stap_txt} mm de la cabeza.",
                 f"{staples} agrafes à travers le pli, enfoncées de l'extérieur et rabattues au "
                 f"cahier central, à {stap_txt} mm de la tête.",
                 f"{staples} grampos pela dobra, cravados por fora e rebatidos na folha central, "
                 f"a {stap_txt} mm da cabeça."),
    "shut": L4(f"Each sheet was cut narrower by twice its creep, outside in (mm per side): "
               f"{shift_txt}. Shut, the fore-edges line up.",
               f"Cada pliego se cortó más angosto el doble de su corrimiento, de fuera hacia "
               f"dentro (mm por lado): {shift_txt}. Cerrado, los cantos delanteros coinciden.",
               f"Chaque feuille a été coupée plus étroite de deux fois sa chasse, de l'extérieur "
               f"vers l'intérieur (mm par côté) : {shift_txt}. Fermé, les gouttières "
               "s'alignent.",
               f"Cada folha foi cortada mais estreita o dobro do seu deslocamento, de fora para "
               f"dentro (mm por lado): {shift_txt}. Fechado, as bordas da frente coincidem."),
}
STEP = {
    "saddle": L4("Nest the sheets and fold them over the saddle",
                 "Encaja los pliegos y dóblalos sobre el caballete",
                 "Emboîtez les feuilles et pliez-les sur la selle",
                 "Encaixe as folhas e dobre-as sobre o cavalete"),
    "stitch": L4("Staple through the spine fold", "Grapa a través del doblez del lomo",
                 "Agrafez à travers le pli du dos", "Grampeie pela dobra da lombada"),
    "shut": L4("Fold the booklet shut", "Cierra el cuadernillo", "Fermez le livret",
               "Feche o livrinho"),
}
TARGET = {"saddle": SADDLE, "stitch": SADDLE, "shut": SHUT}
program = pliego.Sequence([
    pliego.Step(sid, STEP[sid], [(spines[k], TARGET[sid][k]) for k in range(n)],
                duration_ms=2400 if sid != "stitch" else 1200, note=NOTES[sid])
    for sid in ("saddle", "stitch", "shut")], mode="kinematic")

o0, i0 = imposition[0]
print(f"saddle: pages={N} sheets={n} page={w:g}x{H:g}mm calipers={t[0]:g}/{t[-1]:g}mm "
      f"rule={creep_rule} shifts=[{shift_txt}]mm uncorrected={untrimmed:.3f}mm "
      f"fore-edge-spread={spread:.1e}mm cover={pp(o0)}/{pp(i0)} staples=[{stap_txt}]mm "
      f"joins={len(joins)} steps={len(program.steps)}")

result = pliego.Assembly(
    sheets, joins=joins,
    controls=[pliego.sequence_control(label=L4("Stitch the booklet", "Engrapar el cuadernillo",
                                               "Piquer le livret", "Grampear o livrinho"))],
    sequence=program,
    initial={s.id: {"angles": {spines[k]: OPEN[k]}, "root": (half[k] / 2.0, H / 2.0)}
             for k, s in enumerate(sheets)},
    title="Saddle stitch",
)
