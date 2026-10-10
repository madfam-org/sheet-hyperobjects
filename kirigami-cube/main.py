"""Kirigami cube — sheet-hyperobjects cartridge (Pliego).

A closed cube from one cut and scored sheet, held shut by tucked flaps instead of glue. The net is
the 1-4-1 cross: a row of four squares that wraps the cube top to bottom (base, back, lid, front)
and two side walls hinged to the back. Seven flaps close the seams: two on the base and two on the
lid fold inside the side walls, two on the front fold inside the side walls, and the tuck flap on
the front's free edge slides in along the base.

Every crease is a score folded to 90°, and the net is a tree of faces, so the fold program is an
exact rigid motion: `kinematic` steps whose in-between states are plain angle blends (no vertex
of the net is interior, so there is no closure to solve). Flaps that lie against a wall stop at
88°, so the preview shows them just inside it instead of in the wall's plane. The script poses
the closed cube with `pliego.kinematics.pose_arrangement` and checks that the front meets the base
edge and the tuck flap lies on the base before it writes the document; the closed state is also
written as the `target:closed` frame.

The base square holds the sheet's lowest-left vertex, so it is the first face of the canonical
arrangement and the root of the studio's face tree: it stays on the table while the walls rise.
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


FLAPS_IN = 88.0  # a flap pressed against a wall, drawn just inside it
TOL_MM = 1e-4

side = clamp(PARAM(lambda: side, 60.0), 25.0, 120.0)
flap = clamp(PARAM(lambda: flap, 0.3), 0.15, 0.4)
stock = str(PARAM(lambda: stock, "cardstock-250"))
if stock not in ("cardstock-160", "cardstock-250", "cardstock-300", "kraft-120"):
    raise ValueError(f"stock {stock!r} is not one this cartridge offers")

s = side
f = flap * s          # flap depth
t = flap * s          # tuck depth
c = 1.0               # flaps start 1 mm in from each corner, so no two flaps share a vertex
if s - 2 * c - 2 * f < 5.0:
    raise ValueError("the flaps leave less than 5 mm of straight edge: make them shallower")


def bottom_flap(x0):
    return [(x0 + c, 0.0), (x0 + c + f, -f), (x0 + s - c - f, -f), (x0 + s - c, 0.0)]


def top_flap(x0):
    return [(x0 + s - c, s), (x0 + s - c - f, s + f), (x0 + c + f, s + f), (x0 + c, s)]


outline = [(0.0, 0.0)] + bottom_flap(0.0) + [(s, 0.0), (s, -s), (2 * s, -s), (2 * s, 0.0)]
outline += bottom_flap(2 * s) + [(3 * s, 0.0)] + bottom_flap(3 * s) + [(4 * s, 0.0)]
outline += [(4 * s, c), (4 * s + t, c + t), (4 * s + t, s - c - t), (4 * s, s - c), (4 * s, s)]
outline += top_flap(3 * s) + [(3 * s, s)] + top_flap(2 * s) + [(2 * s, s), (2 * s, 2 * s),
                                                             (s, 2 * s), (s, s)]
outline += top_flap(0.0) + [(0.0, s)]

sheet = pliego.Sheet("cube-net", outline, stock=stock, grain_deg=90.0,
                     label=L4("Cube net", "Desarrollo del cubo", "Patron du cube",
                              "Planificação do cubo"))


def score(a, b, en, es, fr, pt):
    return sheet.crease(a, b, "valley", 90.0, treatment="score", label=L4(en, es, fr, pt))


back = score((s, 0), (s, s), "Base to back wall", "Base con pared trasera",
             "Base et paroi arrière", "Base com parede traseira")
lid = score((2 * s, 0), (2 * s, s), "Back wall to lid", "Pared trasera con tapa",
            "Paroi arrière et couvercle", "Parede traseira com tampa")
front = score((3 * s, 0), (3 * s, s), "Lid to front wall", "Tapa con pared frontal",
              "Couvercle et paroi avant", "Tampa com parede frontal")
right = score((s, s), (2 * s, s), "Back wall to side wall", "Pared trasera con lateral",
              "Paroi arrière et côté", "Parede traseira com lateral")
left = score((s, 0), (2 * s, 0), "Back wall to other side wall",
             "Pared trasera con el otro lateral", "Paroi arrière et l'autre côté",
             "Parede traseira com a outra lateral")
base_flaps = [score((c, y), (s - c, y), "Base flap", "Solapa de la base", "Rabat de la base",
                    "Aba da base") for y in (0.0, s)]
lid_flaps = [score((2 * s + c, y), (3 * s - c, y), "Lid flap", "Solapa de la tapa",
                   "Rabat du couvercle", "Aba da tampa") for y in (0.0, s)]
front_flaps = [score((3 * s + c, y), (4 * s - c, y), "Front flap", "Solapa frontal",
                     "Rabat avant", "Aba frontal") for y in (0.0, s)]
tuck = score((4 * s, c), (4 * s, s - c), "Tuck flap", "Lengüeta de cierre", "Rabat à glisser",
             "Lingueta de fecho")

ANG = {back: 90.0, lid: 90.0, front: 90.0, right: 90.0, left: 90.0, tuck: FLAPS_IN}
ANG.update({m: FLAPS_IN for m in base_flaps + lid_flaps + front_flaps})
ROOT = (s / 2.0, s / 2.0)

# ── closure check: pose the closed cube and compare the seams it must close ──
arr = sheet.build()
angles = {e: ANG[m] for m in ANG for e in m.edges()}
pose = kinematics.pose_arrangement(arr, angles, pliego.P(*ROOT))


def where(x, y):
    for i, v in enumerate(arr.vertices):
        if abs(v.x - x) < 1e-6 and abs(v.y - y) < 1e-6:
            return pose[i]
    raise ValueError(f"no vertex at ({x}, {y})")


worst = 0.0
for (xa, ya), (xb, yb) in (((4 * s, 0.0), (0.0, 0.0)), ((4 * s, s), (0.0, s)),
                           ((2 * s, 2 * s), (3 * s, s)), ((s, 2 * s), (0.0, s)),
                           ((2 * s, -s), (3 * s, 0.0)), ((s, -s), (0.0, 0.0))):
    worst = max(worst, math.dist(where(xa, ya), where(xb, yb)))
if worst > TOL_MM:
    raise ValueError(f"the folded net does not close: a seam is {worst:.3g} mm open")
print(f"kirigami-cube: side={s}mm flap={f:.1f}mm seams_closed_within={worst:.2e}mm")

steps = [
    pliego.Step("base-flaps", L4("Fold the two base flaps up", "Dobla hacia arriba las dos "
                                 "solapas de la base", "Relever les deux rabats de la base",
                                 "Dobre para cima as duas abas da base"),
                [(m, FLAPS_IN) for m in base_flaps], duration_ms=1500),
    pliego.Step("walls", L4("Raise the back wall; the side walls swing in beside the base",
                            "Levanta la pared trasera; los laterales giran hasta quedar junto a "
                            "la base",
                            "Relever la paroi arrière ; les côtés pivotent contre la base",
                            "Levante a parede traseira; as laterais giram até ficar junto à base"),
                [(back, 90.0), (right, 90.0), (left, 90.0)], duration_ms=2500),
    pliego.Step("lid-flaps", L4("Fold in the flaps of the lid and the front, and the tuck flap",
                                "Dobla hacia dentro las solapas de la tapa y del frente, y la "
                                "lengüeta",
                                "Rabattre vers l'intérieur les rabats du couvercle, de l'avant et "
                                "le rabat à glisser",
                                "Dobre para dentro as abas da tampa e da frente, e a lingueta"),
                [(m, FLAPS_IN) for m in lid_flaps + front_flaps] + [(tuck, FLAPS_IN)],
                duration_ms=2000),
    pliego.Step("close", L4("Close the lid and slide the tuck flap in along the base",
                            "Cierra la tapa y mete la lengüeta a lo largo de la base",
                            "Fermer le couvercle et glisser le rabat le long de la base",
                            "Feche a tampa e enfie a lingueta ao longo da base"),
                [(lid, 90.0), (front, 90.0)], duration_ms=2500),
]
result = pliego.Assembly(
    [sheet],
    controls=[pliego.sequence_control(label=L4("Fold program", "Secuencia de pliegues",
                                               "Séquence de pliage", "Sequência de dobras"))],
    sequence=pliego.Sequence(steps, mode="kinematic"),
    targets={"closed": {"angles": dict(ANG), "root": ROOT}},
    title="Kirigami cube",
)
