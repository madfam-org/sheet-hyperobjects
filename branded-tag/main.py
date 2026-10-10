"""Branded tag — sheet-hyperobjects cartridge (Pliego).

A folded board hang tag that demonstrates the four ways a brand goes onto board, chosen with
``style`` (one generator; ``pliego.press``, spec §5.10–§5.11):

- ``artwork`` — printed brand artwork, a ``pliego:artwork`` record placing ``assets/mark.svg``
  inside the cover's safe area;
- ``emboss`` / ``deboss`` — the brand mark pressed up or in (die and counter plates);
- ``iron-burn`` — the mark charred by a hot branding iron (one iron face, deep char);
- ``laser-burn`` — the mark engraved by a laser (vector outline plus a raster fill hatch).

The mark is an original, brand-neutral motif computed here: a rounded square ring around a
folded-corner triangle and a dot (a sheet with its corner turned over), drawn identically in the
SVG asset so the pressed, burned and printed versions match. The tag is two panels joined by a
scored spine; the top corners are clipped at 45° and an **eyelet hole** goes through both panels
(mirrored about the spine, so the holes align when the tag is folded). A ``string`` join hangs the
cover from a point above the hole.

The tag hangs upright (rigid placement, the cover's print side facing the viewer); the program
folds the back panel behind the cover along the spine (kinematic, exact), so both printed faces
end outward. **Limits.** The string, the tag swinging on it and the finishes' local stiffening
(emboss) or thinning (burn) are the physics engine's part; the studio does not yet render relief,
sheen or char. A metal eyelet can be set in the hole; it is not modelled.
"""

import math

import pliego


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


def L4(en, es, fr, pt):
    return {"en": en, "es": es, "fr": fr, "pt": pt}


style = str(PARAM(lambda: style, "emboss"))           # noqa: F821
size = str(PARAM(lambda: size, "medium"))             # noqa: F821
mark_scale = float(PARAM(lambda: mark_scale, 0.62))   # noqa: F821 - mark width / tag width
hole = float(PARAM(lambda: hole, 5.0))                # noqa: F821 - eyelet hole diameter
string_length = float(PARAM(lambda: string_length, 90.0))   # noqa: F821
stock = str(PARAM(lambda: stock, "greyboard-1500"))   # noqa: F821

STYLES = ("artwork", "emboss", "deboss", "iron-burn", "laser-burn")
SIZES = {"small": (40.0, 70.0), "medium": (55.0, 90.0), "large": (70.0, 120.0)}
STOCKS = ("greyboard-1500", "sbs-board-350", "folding-boxboard-300", "cardstock-300")
if style not in STYLES or size not in SIZES or stock not in STOCKS:
    raise ValueError("branded-tag: unknown style, size or stock")
W, H = SIZES[size]
mark_scale = pliego.clamp(mark_scale, 0.35, 0.8)
hole = pliego.clamp(hole, 3.0, 8.0)
string_length = pliego.clamp(string_length, 30.0, 300.0)
t = pliego.board.caliper(stock)
clip = 0.22 * W                          # 45° clipped top corners
hy = H - clip                            # hole centre height: level with the clips
r = hole / 2.0

d = pliego.dieline.Dieline(
    "tag", f"folded hang tag ({style})", "board", {"width": W, "height": H}, stock, t,
    label=L4("Hang tag", "Etiqueta colgante", "Étiquette suspendue", "Etiqueta pendente"),
    grain_deg=90.0, bleed=2.0, safe=3.0)
d.panel("cover", [(0.0, 0.0), (W, 0.0), (W, H - clip), (W - clip, H), (clip, H), (0.0, H - clip)],
        "panel", L4("Cover", "Portada", "Recto", "Frente"))
d.panel("back", [(W, 0.0), (2 * W, 0.0), (2 * W, H - clip), (2 * W - clip, H), (W + clip, H),
                 (W, H - clip)], "panel", L4("Back", "Reverso", "Verso", "Verso"))
d.hinge("cover", "back", -180.0, name="spine")


def circle(cx, cy, rr, n=24):
    return [(cx + rr * math.cos(2 * math.pi * k / n), cy + rr * math.sin(2 * math.pi * k / n))
            for k in range(n)]


d.hole(circle(W / 2.0, hy, r))
d.hole(circle(2 * W - W / 2.0, hy, r))                 # mirrored about the spine
d.dimension((0.0, 0.0), (W, 0.0), f"{W:g}", -6.0)
d.dimension((0.0, 0.0), (0.0, H), f"{H:g}", 6.0)
d.step("fold", L4("Fold the back behind the cover along the spine",
                  "Dobla el reverso detrás de la portada por el lomo",
                  "Repliez le verso derrière le recto le long du dos",
                  "Dobre o verso atrás da frente pela lombada"), ["spine"], 1400)
pack = d.build(rest_on="cover")
sheet = pack.sheet
S = math.sqrt(0.5)
sheet.placement = pliego.Placement(origin=(0.0, 40.0, 0.0), rotation=(S, 0.0, 0.0, S))
rep = pliego.papercut.analyze(sheet, min_feature_mm=max(1.0, t))
errors = [i["detail"] for i in rep.issues if i["level"] == "error"]
if errors:
    raise ValueError("branded-tag: papercut check failed: " + "; ".join(errors))
if clip - r < max(2.0 * t, 2.0):           # board left between the eyelet and the top edge
    raise ValueError("branded-tag: the eyelet hole is too close to the top edge")

# ── the brand mark: a rounded-square ring, a folded-corner triangle and a dot ─────────────────
M = mark_scale * W                      # mark width
mx, my = W / 2.0, 0.42 * H              # its centre on the cover


def rounded_square(cx, cy, half, rad, n=6):
    pts = []
    for k, (sx, sy) in enumerate(((1, -1), (1, 1), (-1, 1), (-1, -1))):
        ccx, ccy = cx + sx * (half - rad), cy + sy * (half - rad)
        for j in range(n + 1):
            ang = math.radians(-90.0 + 90.0 * k + 90.0 * j / n)
            pts.append((ccx + rad * math.cos(ang), ccy + rad * math.sin(ang)))
    return pts


outer = rounded_square(mx, my, M / 2.0, 0.18 * M)
inner = rounded_square(mx, my, 0.40 * M, 0.12 * M)
fold_tri = [(mx + 0.32 * M, my + 0.04 * M), (mx + 0.32 * M, my + 0.32 * M),
            (mx + 0.04 * M, my + 0.32 * M)]
dot = circle(mx - 0.12 * M, my - 0.12 * M, 0.11 * M, 20)
ring = [outer, inner]                   # even-odd: the inner square is a hole
mark = ring + [fold_tri, dot]
press = pliego.press
finishes, artwork = [], []
if style == "artwork":
    artwork = [press.artwork("brand-mark", sheet, "assets/mark.svg", (mx - M / 2, my - M / 2),
                             (M, M), side="front", panel="cover", clip="panel")]
elif style == "emboss":
    finishes = [press.emboss("ring", sheet, ring, 0.4, profile="bevel"),
                press.emboss("corner", sheet, [fold_tri], 0.5, profile="flat"),
                press.emboss("dot", sheet, [dot], 0.5, profile="dome")]
elif style == "deboss":
    finishes = [press.deboss("ring", sheet, ring, 0.35, profile="flat"),
                press.deboss("corner", sheet, [fold_tri], 0.35, profile="flat"),
                press.deboss("dot", sheet, [dot], 0.35, profile="flat")]
elif style == "iron-burn":                # a burn never chars more than half the board [E]
    finishes = [press.burn("mark", sheet, mark, min(0.4, 0.5 * t), process="iron", char=0.9)]
else:
    finishes = [press.burn("mark", sheet, mark, min(0.15, 0.5 * t), process="laser",
                           char=0.75)]

anchor = (W / 2.0, hy + r)              # the top of the cover's eyelet hole
hang = pliego.string("hang-string", (sheet, anchor),
                     (anchor[0], 40.0 + anchor[1] + string_length, 0.0), string_length)
print(f"branded-tag: {style} on {stock} ({t} mm), {W:g} x {H:g} mm, mark {M:.1f} mm, eyelet "
      f"{hole:g} mm, narrowest bridge "
      f"{'n/a' if rep.min_bridge_mm is None else round(rep.min_bridge_mm, 1)} mm")
result = pliego.dieline.assemble(
    [pack], title=f"Branded tag ({style})", finishes=finishes, artwork=artwork,
    label=L4("Fold", "Doblar", "Plier", "Dobrar"),
    meta={"cartridge": "branded-tag",
          "params": {"style": style, "size": size, "mark_scale": mark_scale, "hole": hole,
                     "string_length": string_length, "stock": stock}})
result.joins = [hang]
