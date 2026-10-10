"""Lucky star — sheet-hyperobjects cartridge (Pliego).

The strip-folded puffy star. A long, narrow strip is tied in a loose knot near one end; flattened,
the knot is a regular pentagon. The long end is then wrapped round and round the pentagon, folding
over each side in turn, and its last bit is tucked under a layer. Pinching each side in at its
middle puffs the pentagon into a small five-pointed star.

The geometry. A knot in a strip of width w flattens into a regular pentagon of side
s = w / sin 72°: the strip runs across the pentagon covering it from one side to the diagonal
parallel to that side, so each pass covers an isosceles trapezoid (bases s and φ·s, φ the golden
ratio, height w), and folding over the side that ends the pass lays the strip across the next
trapezoid, turned round the pentagon. Unfolded, the fold lines zig-zag along the strip at 72° and
108° to its edges, so the strip is a row of trapezoids alternately short side down and short side
up. The script checks the claim by folding: every trapezoid, reflected across the fold lines before
it, lands with its four corners on the pentagon's corners.

The fold program ties the knot (the first three folds), wraps the strip (one fold per step) and
tucks the end, all kinematic: the strip is a chain of rigid trapezoids. The knot's threading of the
strip through its own loop is not modelled (the preview folds the layers in order). The final
puffing bends the paper and needs the physics engine; it is the program's last step, with no
target in the preview.
"""

import math

import pliego


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


width = float(PARAM(lambda: width, 12.0))              # noqa: F821
wraps = int(round(float(PARAM(lambda: wraps, 3))))     # noqa: F821
colour = PARAM(lambda: colour, "#f3a712")              # noqa: F821
stock = PARAM(lambda: stock, "copy-80")                # noqa: F821

if stock not in ("copy-80", "kami", "papel-de-china"):
    raise ValueError(f"lucky-star: unknown stock {stock!r}")
if not (isinstance(colour, str) and len(colour) == 7 and colour[0] == "#"):
    raise ValueError(f"lucky-star: colour must be #rrggbb, got {colour!r}")
W = pliego.clamp(width, 6.0, 30.0)
NW = int(pliego.clamp(wraps, 2, 5))
PHI = (1 + math.sqrt(5.0)) / 2
S = W / math.sin(math.radians(72.0))     # the pentagon's side
SLANT = (PHI - 1) / 2 * S                # how far a fold line leans across the strip
N = 5 * NW + 1                           # trapezoids: the knot's three and the wraps' rest


def L4(en, es, fr, pt):
    return {"en": en, "es": es, "fr": fr, "pt": pt}


# fold lines (bottom x, top x) along the strip; leg 0 is the strip's slanted start
legs = [(SLANT, 0.0)]
for k in range(N):
    b, t = legs[-1]
    legs.append((b + S, t + PHI * S) if k % 2 == 0 else (b + PHI * S, t + S))
ring = [(legs[0][0], 0.0), (legs[-1][0], 0.0), (legs[-1][1], W), (legs[0][1], W)]


def reflect(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    t = ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / (dx * dx + dy * dy)
    return (2 * (a[0] + t * dx) - p[0], 2 * (a[1] + t * dy) - p[1])


# the check: fold every trapezoid onto the pentagon of the first one
PENT = [(SLANT, 0.0), (SLANT + S, 0.0), (PHI * S, W), (PHI * S / 2, W + S * math.sin(math.radians(36.0))),
        (0.0, W)]
for k in range(N):
    corners = [(legs[k][0], 0.0), (legs[k + 1][0], 0.0), (legs[k + 1][1], W), (legs[k][1], W)]
    for j in range(k, 0, -1):          # fold k first, then k − 1 … 1 (the composition R1∘…∘Rk)
        a, b = (legs[j][0], 0.0), (legs[j][1], W)
        corners = [reflect(p, a, b) for p in corners]
    if not all(min(math.dist(p, q) for q in PENT) < 1e-6 for p in corners):
        raise ValueError(f"lucky-star: trapezoid {k + 1} does not fold onto the pentagon")

strip = pliego.Sheet("strip", ring, stock=stock, grain_deg=0.0,
                     label=L4("Star strip", "Tira de la estrella", "Bande de l'étoile",
                              "Tira da estrela"), front=colour, back="#fdfaf3")
folds = [strip.mountain((legs[k][0], 0.0), (legs[k][1], W), 180.0, name="wrap")
         for k in range(1, N)]

steps = []
for k, m in enumerate(folds, 1):
    if k <= 3:
        lab = L4(f"Tie a loose knot: fold {k} of 3", f"Haz un nudo flojo: pliegue {k} de 3",
                 f"Faire un nœud lâche : pli {k} sur 3", f"Dê um nó frouxo: dobra {k} de 3")
    elif k < len(folds):
        lab = L4(f"Wrap the strip round the pentagon ({k - 3}/{len(folds) - 4})",
                 f"Enrolla la tira alrededor del pentágono ({k - 3}/{len(folds) - 4})",
                 f"Enrouler la bande autour du pentagone ({k - 3}/{len(folds) - 4})",
                 f"Enrole a tira em volta do pentágono ({k - 3}/{len(folds) - 4})")
    else:
        lab = L4("Fold the end over and tuck it under a layer",
                 "Dobla el extremo y mételo bajo una capa",
                 "Replier le bout et le glisser sous une couche",
                 "Dobre a ponta e enfie-a sob uma camada")
    steps.append(pliego.Step(f"fold-{k}", lab, [(m, -180.0)], duration_ms=900))
steps.append(pliego.Step(
    "puff", L4("Pinch each side in at its middle to puff the star",
               "Pellizca cada lado por la mitad para inflar la estrella",
               "Pincer chaque côté en son milieu pour gonfler l'étoile",
               "Aperte cada lado no meio para inflar a estrela"), [], duration_ms=1500,
    note=L4("Puffing bends the paper: the physics engine does it; the preview stops at the flat "
            "pentagon.", "Inflarla curva el papel: lo hace el motor de física; la vista previa se "
            "detiene en el pentágono plano.", "Gonfler l'étoile courbe le papier : c'est le "
            "moteur physique qui le fait ; l'aperçu s'arrête au pentagone plat.",
            "Inflar a estrela curva o papel: é o motor de física que o faz; a pré-visualização "
            "para no pentágono plano.")))
print(f"lucky-star: width={W:g}mm pentagon_side={S:.2f}mm wraps={NW} folds={len(folds)} "
      f"strip={legs[-1][0] - legs[0][1]:.0f}mm")
result = pliego.Assembly([strip], controls=[pliego.sequence_control(
    label=L4("Fold", "Doblar", "Plier", "Dobrar"))],
    sequence=pliego.Sequence(steps, mode="kinematic"), title="Lucky star")
