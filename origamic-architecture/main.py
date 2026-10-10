"""Origamic architecture — sheet-hyperobjects cartridge (Pliego).

90° cut-and-fold cards from one sheet. The sheet (two pages of width w, height H) folds along the
gutter u = w. Every element is a strip between two slits, perpendicular to the gutter, folded into
a zigzag whose segments are alternately parallel to the right page (risers) and to the left page
(treads): it leaves the floor at distance D from the gutter and meets the wall at height Σr, with
Σt = D. On the flat sheet the strip runs from u = w − D to u = w + Σr, with valley creases at both
ends and mountain/valley creases in turn between. Because each segment stays parallel to one page,
every crease turns by the same angle as the gutter, ρ = 180° − φ (φ the angle between the pages),
so the card closes flat at φ = 0 and lies flat at φ = 180: a generalised parallelogram linkage.

Designs (all original MADFAM geometry):
- `stairs`: one block whose profile is a staircase of n equal steps climbing to the wall;
- `arch`: a gateway with a round-arched opening between two lower wall blocks;
- `facade`: a building front of five blocks of different heights and depths, with windows and a
  door.

The fold program is `kinematic`: the angles of every crease are ±ρ, so the plain angle blend between
key poses is the exact rigid motion. No vertex is interior (creases end on slits or the outline),
so there is no vertex closure to solve; the loops around the slits close by the parallelogram
property, which the script checks with `pliego.kinematics.pose_arrangement` at 90°.
"""

import math

import pliego
from pliego import kinematics


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


def clamp(value, lo, hi):
    return max(lo, min(hi, float(value)))


def L4(en, es, fr, pt):
    return {"en": en, "es": es, "fr": fr, "pt": pt}


MIN_FEATURE = {"cardstock-160": 1.5, "cardstock-250": 2.0, "kraft-120": 1.0}
MARGIN = 10.0  # mm of plain page kept around every element

design = str(PARAM(lambda: design, "stairs"))
page_width = clamp(PARAM(lambda: page_width, 120.0), 80.0, 200.0)
page_height = clamp(PARAM(lambda: page_height, 160.0), 100.0, 250.0)
depth = clamp(PARAM(lambda: depth, 50.0), 20.0, 150.0)
rise = clamp(PARAM(lambda: rise, 60.0), 20.0, 150.0)
steps = int(clamp(PARAM(lambda: steps, 4), 2, 6))
stock = str(PARAM(lambda: stock, "cardstock-160"))
if design not in ("stairs", "arch", "facade"):
    raise ValueError(f"design {design!r} must be stairs, arch or facade")
if stock not in MIN_FEATURE:
    raise ValueError(f"stock {stock!r} is not one this cartridge offers")
mf = MIN_FEATURE[stock]
w, H = page_width, page_height
if depth > w - MARGIN or rise > w - MARGIN:
    raise ValueError(f"depth and rise must leave {MARGIN} mm of each {w} mm page")

# A block: (v_a, v_b, profile [r1, t1, r2, t2, ...], holes as lists of (riser index, polygon in
# riser coordinates (x along the riser from its bottom crease, y across it from v_a))).
blocks = []
if design == "stairs":
    half = 0.32 * H
    prof = []
    for _ in range(steps):
        prof += [rise / steps, depth / steps]
    blocks.append((H / 2 - half, H / 2 + half, prof, []))
elif design == "arch":
    gate = 0.3 * H
    v0, v1 = H / 2 - gate / 2, H / 2 + gate / 2
    side = min(0.25 * H, v0 - MARGIN)
    aw = 0.62 * gate                       # opening width
    sill = max(2.0 * mf, 3.0)
    spring = 0.62 * rise - aw / 2          # where the round top begins
    if spring <= sill + 5.0 or spring + aw / 2 > rise - max(4.0 * mf, 6.0):
        raise ValueError("the arch does not fit the gate: raise the rise or lower the depth")
    opening = [(sill, gate / 2 - aw / 2), (spring, gate / 2 - aw / 2)]
    opening += [(spring + aw / 2 * math.sin(math.pi * k / 16),
                 gate / 2 - aw / 2 * math.cos(math.pi * k / 16)) for k in range(1, 16)]
    opening += [(spring, gate / 2 + aw / 2), (sill, gate / 2 + aw / 2)]
    blocks += [(v0 - side, v0, [0.6 * rise, depth], []),
               (v0, v1, [rise, depth], [(0, opening)]),
               (v1, v1 + side, [0.6 * rise, depth], [])]
else:  # facade
    widths = [0.14, 0.16, 0.2, 0.16, 0.14]
    heights = [0.55, 0.8, 1.0, 0.7, 0.45]
    depths = [0.7, 0.85, 1.0, 0.85, 0.7]
    v = (H - sum(widths) * H) / 2
    for k, (bw, bh, bd) in enumerate(zip(widths, heights, depths)):
        bw, r, d = bw * H, bh * rise, bd * depth
        holes = []
        win, gap = 0.2 * bw, 0.2 * bw
        floors = int((r - 8.0) // (win * 1.6 + gap))
        for i in range(floors):
            x0 = r - gap - i * (win * 1.6 + gap) - win * 1.6
            if k == 2 and x0 < 0.45 * r:
                break
            for y0 in (gap, bw - gap - win):
                holes.append((0, [(x0, y0), (x0 + 1.6 * win, y0), (x0 + 1.6 * win, y0 + win),
                                  (x0, y0 + win)]))
        if k == 2:  # the door: a tall opening above a sill
            dw, sill = 0.34 * bw, max(2.0 * mf, 3.0)
            holes.append((0, [(sill, bw / 2 - dw / 2), (0.38 * r, bw / 2 - dw / 2),
                              (0.38 * r, bw / 2 + dw / 2), (sill, bw / 2 + dw / 2)]))
        blocks.append((v, v + bw, [r, d], holes))
        v += bw
if blocks[0][0] < MARGIN or blocks[-1][1] > H - MARGIN:
    raise ValueError("the design does not fit the page height")

LABEL = L4("Origamic architecture card", "Tarjeta de arquitectura origámica",
           "Carte d'architecture origamique", "Cartão de arquitetura origâmica")
sheet = pliego.Sheet("card", pliego.rectangle(2 * w, H), stock=stock, grain_deg=90.0,
                     label=LABEL)
valleys, mountains = [], []


def span(block):
    prof = block[2]
    d = sum(prof[1::2])
    return w - d, w + sum(prof[0::2])


# slits: at each block boundary, across the union of the strips that meet there
edges_v = sorted({b[0] for b in blocks} | {b[1] for b in blocks})
for v in edges_v:
    touching = [span(b) for b in blocks if b[0] == v or b[1] == v]
    sheet.cut([(min(a for a, _ in touching), v), (max(b for _, b in touching), v)])

for v_a, v_b, prof, holes in blocks:
    u = w - sum(prof[1::2])
    risers = []
    valleys.append(sheet.crease((u, v_a), (u, v_b), "valley", 90.0, treatment="score"))
    for i, seg in enumerate(prof):
        if i % 2 == 0:
            risers.append(u)
        u += seg
        kind = "mountain" if i % 2 == 0 else "valley"
        made = sheet.crease((u, v_a), (u, v_b), kind, 90.0, treatment="score")
        (mountains if kind == "mountain" else valleys).append(made)
    for riser, poly in holes:
        u0, r = risers[riser], prof[2 * riser]
        if any(x < mf or x > r - mf or y < mf or y > (v_b - v_a) - mf for x, y in poly):
            raise ValueError("an opening comes closer than the minimum feature to a fold or slit")
        sheet.hole([(u0 + x, v_a + y) for x, y in poly])

# the gutter crease runs wherever no element crosses it
covered = sorted((b[0], b[1]) for b in blocks)
v = 0.0
for v_a, v_b in covered + [(H, H)]:
    if v_a > v + 1e-9:
        valleys.append(sheet.crease((w, v), (w, v_a), "valley", 90.0, treatment="score"))
    v = max(v, v_b)

report = pliego.papercut.analyze(sheet, min_feature_mm=mf)
if not report.ok:
    raise ValueError("origamic-architecture papercut check failed: "
                     + "; ".join(i["detail"] for i in report.issues if i["level"] == "error"))

# ── check: the loops around the slits close at every opening (closure residual over all
# creases, including those the face tree does not cross), and at 90° the pages are floor and wall ──
arr = sheet.build()
ROOT = pliego.P(w / 4.0, 4.0)


def angles_at(rho):
    return {**{e: rho for m in valleys for e in m.edges()},
            **{e: -rho for m in mountains for e in m.edges()}}


loop = max(kinematics.closure_residual(arr, angles_at(rho), ROOT)
           for rho in (30.0, 60.0, 90.0, 120.0, 150.0, 180.0))
pose = kinematics.pose_arrangement(arr, angles_at(90.0), ROOT)
worst = 0.0
for i, p in enumerate(arr.vertices):
    x, y, z = pose[i]
    if p.x <= w - depth - 1e-6:          # left page (floor): y = 0
        worst = max(worst, abs(y))
    elif p.x >= w + rise + 1e-6:         # right page (wall): x = w
        worst = max(worst, abs(x - w))
if loop > 1e-6 or worst > 1e-6:
    raise ValueError(f"the pop-up does not close: loop residual {loop:.3g} mm, page offset "
                     f"{worst:.3g} mm")
print(f"origamic-architecture: design={design} blocks={len(blocks)} creases="
      f"{len(valleys) + len(mountains)} holes={sum(len(b[3]) for b in blocks)} "
      f"loop_residual={loop:.1e}mm pages_at_90={worst:.1e}mm")


def pose_at(rho):
    return [(m, rho) for m in valleys] + [(m, -rho) for m in mountains]


program = [
    pliego.Step("open-90", L4("Fold the card to a right angle: the design stands up",
                              "Dobla la tarjeta en ángulo recto: el diseño se levanta",
                              "Plier la carte à angle droit : le décor se dresse",
                              "Dobre o cartão em ângulo reto: o desenho levanta-se"),
                pose_at(90.0), duration_ms=2500),
    pliego.Step("close", L4("Close the card: every piece folds flat between the pages",
                            "Cierra la tarjeta: cada pieza queda plana entre las páginas",
                            "Fermer la carte : chaque pièce se range à plat entre les pages",
                            "Feche o cartão: cada peça fica plana entre as páginas"),
                pose_at(180.0), duration_ms=2500),
    pliego.Step("reopen", L4("Open it again to 90°", "Vuelve a abrirla a 90°",
                             "La rouvrir à 90°", "Abra-o de novo a 90°"),
                pose_at(90.0), duration_ms=2500),
]
result = pliego.Assembly(
    [sheet],
    controls=[pliego.sequence_control(label=L4("Open and close", "Abrir y cerrar",
                                               "Ouvrir et fermer", "Abrir e fechar"))],
    sequence=pliego.Sequence(program, mode="kinematic"),
    targets={"open-90": {"angles": dict(pose_at(90.0)), "root": (ROOT.x, ROOT.y)}},
    title="Origamic architecture",
    meta={"min_feature_mm": mf},
)
