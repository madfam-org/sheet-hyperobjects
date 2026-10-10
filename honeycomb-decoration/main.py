"""Honeycomb decoration — sheet-hyperobjects cartridge (Pliego).

A stack of N tissue sheets, each glued to the next along straight stripes that run from the spine
to the edge, perpendicular to it. Consecutive pairs use alternate stripes (pair k uses stripes
j ≡ k mod 2), so when the stack is opened like a book the tissue between the glue lines spreads
into cells: honeycomb paper. Two card covers close the stack; the bottom one stays put and the
top one turns about the spine.

Shapes (`shape`): `ball` — half-disc pages opened all the way round (360°) into a sphere;
`fan` — the same half-disc opened halfway (180°) into a half ball that sits flat against a wall;
`bell` — half-bell pages (the spine is the bell's axis) opened 360° into a bell.

Physical (tier C): the cells only exist because tissue bends and stretches between the welds, so
the opening needs the physics engine. Every weld is a `glue` join, the stack is laid out with the
sheets 0.03 mm apart (within tissue's collision thickness, so every weld holds in the initial
frame), the covers are kinematic boards, and the `open` control turns the top cover about the spine
with a `hinge`. The studio preview cannot drive a hinge whose moving board is glued to paper, so it
keeps the stack closed.
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


TISSUE, COVER = "papel-de-china", "cardstock-300"
GAP = 0.03          # mm between stacked sheets (tissue collision thickness is 0.04 mm)
GLUE_W = 4.0        # width of a glue stripe, mm
INSET = 3.0         # stripes stop this far from the spine and the edge, mm
COLOURS = {"coral": "#f0705a", "gold": "#f2c14e", "teal": "#2a9d8f", "white": "#f7f4ee"}

shape = str(PARAM(lambda: shape, "ball"))
size = clamp(PARAM(lambda: size, 120.0), 60.0, 300.0)
sheets = int(clamp(PARAM(lambda: sheets, 16), 6, 40))
spacing = clamp(PARAM(lambda: spacing, 15.0), 8.0, 40.0)
colour = str(PARAM(lambda: colour, "coral"))
if shape not in ("ball", "fan", "bell"):
    raise ValueError(f"shape {shape!r} must be ball, fan or bell")
if colour not in COLOURS:
    raise ValueError(f"colour {colour!r} is not offered")

# The page outline: the spine runs along v = 0 from u = 0 to u = L; height(u) is the page's reach.
if shape in ("ball", "fan"):
    R = size / 2.0
    L = 2.0 * R

    def height(u):
        return math.sqrt(max(0.0, R * R - (u - R) ** 2))

    outline = [(R + R * math.cos(math.pi * k / 48), R * math.sin(math.pi * k / 48))
               for k in range(49)]
    outline[0], outline[-1] = (L, 0.0), (0.0, 0.0)
else:
    L = size
    top, mouth = 0.18 * size, 0.42 * size

    def height(u):
        t = u / L
        return top + (mouth - top) * t ** 2.2 + 0.05 * size * max(0.0, (t - 0.85) / 0.15) ** 2

    outline = [(0.0, 0.0), (L, 0.0)] + [(L * (1 - k / 40), height(L * (1 - k / 40)))
                                         for k in range(41)]
open_to = 180.0 if shape == "fan" else 360.0

stripes = [INSET + GLUE_W / 2 + j * spacing for j in range(int((L - 2 * INSET - GLUE_W) // spacing)
                                                           + 1)]
if len(stripes) < 4:
    raise ValueError("fewer than four glue stripes fit the page: lower the spacing")

hex_ = COLOURS[colour]
pages = []
for k in range(sheets):
    pages.append(pliego.Sheet(
        f"tissue-{k + 1}", outline, stock=TISSUE, grain_deg=90.0, front=hex_, back=hex_,
        label=L4(f"Tissue sheet {k + 1}", f"Hoja de papel de china {k + 1}",
                 f"Feuille de papier de soie {k + 1}", f"Folha de papel de seda {k + 1}"),
        placement=pliego.Placement(origin=(0.0, (k + 1) * GAP, 0.0))))
covers = []
for name, y, lab in (("cover-bottom", 0.0, ("Bottom cover", "Tapa de abajo", "Couverture du bas",
                                            "Capa de baixo")),
                     ("cover-top", (sheets + 1) * GAP, ("Top cover", "Tapa de arriba",
                                                         "Couverture du haut", "Capa de cima"))):
    covers.append(pliego.Sheet(name, outline, stock=COVER, grain_deg=0.0, kinematic="open-book",
                               label=L4(*lab), placement=pliego.Placement(origin=(0.0, y, 0.0))))


def stripe(x):
    """Glue region around the stripe x, from the spine inset to below the page edge."""
    lo, hi = x - GLUE_W / 2, x + GLUE_W / 2
    reach = min(height(lo), height(hi), height(x)) - INSET
    if reach <= INSET + 2.0:
        return None
    return [(lo, INSET), (hi, INSET), (hi, reach), (lo, reach)]


joins = []
for k in range(sheets - 1):
    for j, x in enumerate(stripes):
        if j % 2 != k % 2:
            continue
        region = stripe(x)
        if region is not None:
            joins.append(pliego.glue(f"weld-{k + 1}-{j + 1}", pages[k], region, pages[k + 1],
                                     side="back"))
inner = [(u, max(INSET, 0.8 * height(u))) for u in
         [INSET + (L - 2 * INSET) * i / 24 for i in range(25)]]
face = [(INSET, INSET), (L - INSET, INSET)] + inner[::-1]
joins.append(pliego.glue("cover-bottom-weld", covers[0], face, pages[0], side="back"))
joins.append(pliego.glue("cover-top-weld", pages[-1], face, covers[1], side="back"))

opening = pliego.angle_control("open", L4("Open", "Abrir", "Ouvrir", "Abrir"), default=0.0,
                               min=0.0, max=open_to)
spine = pliego.hinge("open-book", (0.0, (sheets + 1) * GAP, 0.0), (1.0, 0.0, 0.0), "open",
                     ["cover-top"], rest=0.0)
result = pliego.Assembly(
    [covers[0]] + pages + [covers[1]],
    joins=joins,
    mechanisms=[spine],
    controls=[opening],
    title="Honeycomb decoration",
    meta={"min_feature_mm": 1.5},
)
print(f"honeycomb: shape={shape} sheets={sheets} stripes={len(stripes)} welds={len(joins)} "
      f"opens_to={open_to:.0f}deg")
