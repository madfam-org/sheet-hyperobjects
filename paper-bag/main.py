"""Paper bag — sheet-hyperobjects cartridge (Pliego).

The flat-bottomed paper bag with side gussets (the SOS style), made from one sheet of kraft:

* the sheet is a row of panels: front (`width`), gusset (`gusset`), back (`width`), gusset, and a
  glue flap that closes the tube against the inside of the front; each gusset is scored down its
  centre so the made bag can pleat in;
* below the bottom score every panel continues by an extension `e` = `gusset`/2 + overlap/2 that
  becomes the bottom: the gusset extensions fold in first and lie flat; the back and front
  extensions fold over them, overlap by `overlap` mm in the middle and are glued;
* where a front or back extension meets a gusset extension, a 45° crease from the bag's corner
  lets the corner of the flap fold back on itself (an ear tucked between the gusset extension and
  the flap), so the bottom closes from a sheet that is not cut at the corners. Seen from below,
  each gusset extension shows as a triangle between the two flaps.

The fold program is kinematic and every in-between state is an exact rigid state, expanded by
`pliego.Sequence.kinematic_path` from three key poses: the tube folds on its four corners, the
gusset flaps fold in halfway while the front and back flaps rise and their corners fold into
ears, then the bottom is pressed flat (0.4° short of flat, so its layers do not coincide). The
bottom corners are degree-5 vertices with two branches from the singular tube state; `branch()`
solves the branch that tucks the ears inside on one corner and every corner is driven along it.
The script checks the erected bag: the tube closes on the glue flap, the flaps lie on the bottom
and overlap by `overlap`, and every crease closes (`kinematics.closure_residual`).
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


width = float(PARAM(lambda: width, 180.0))                   # noqa: F821
gusset = float(PARAM(lambda: gusset, 100.0))                 # noqa: F821
height = float(PARAM(lambda: height, 260.0))                 # noqa: F821
overlap = float(PARAM(lambda: overlap, 20.0))                # noqa: F821
stock = str(PARAM(lambda: stock, "kraft-120"))               # noqa: F821

STOCKS = ("kraft-120", "copy-80", "cardstock-160")
if stock not in STOCKS:
    raise ValueError(f"paper-bag: stock must be one of {STOCKS}, got {stock!r}")
w = pliego.clamp(width, 80.0, 320.0)
g = pliego.clamp(gusset, 40.0, 200.0)
h = pliego.clamp(height, 100.0, 460.0)
ov = pliego.clamp(overlap, 8.0, 40.0)
e = g / 2 + ov / 2                    # bottom extension of every panel
SEAM = 15.0                           # glue flap width
DELTA = 1.0                           # the front's extension starts 1 mm in from the seam corner
TOL = 1e-4
if e > w / 2 - 2.0:
    raise ValueError(f"paper-bag: a {g:g} mm gusset needs a front wider than {2 * e + 4:.0f} mm "
                     "(the gusset extensions would collide on the bottom)")
if h < g:
    raise ValueError("paper-bag: the bag must be at least as tall as its gusset")

X1, X2, X3, X4 = w, w + g, 2 * w + g, 2 * w + 2 * g      # panel edges along the sheet
ring = [(0.0, 0.0), (DELTA, 0.0), (DELTA + e, -e), (X4, -e), (X4, 0.0), (X4 + SEAM, 4.0),
        (X4 + SEAM, h - 4.0), (X4, h), (0.0, h)]
bag = pliego.Sheet("bag", ring, stock=stock, grain_deg=90.0,
                   placement=pliego.Placement(origin=(0.0, 0.0, g),
                                              rotation=(math.sqrt(0.5), 0.0, 0.0, math.sqrt(0.5))),
                   label=L4("Bag blank", "Plantilla de la bolsa", "Patron du sac",
                            "Molde do saco"))


def crease(a, b, en, es, fr, pt, kind="mountain", ang=90.0, name=None):
    return bag.crease(a, b, kind, ang, treatment="score", label=L4(en, es, fr, pt), name=name)


corners = [crease((x, 0.0), (x, h), "Corner of the bag", "Esquina de la bolsa", "Arête du sac",
                  "Aresta do saco") for x in (X1, X2, X3)]
seam = crease((X4, 0.0), (X4, h), "Glue flap", "Pestaña de pegado", "Patte de collage",
              "Aba de colagem", ang=89.0, name="seam")
centres = [bag.score((x, 0.0), (x, h), "flat", 0.0, L4("Gusset centre", "Centro del fuelle",
                                                         "Milieu du soufflet", "Centro do fole"),
                     name="gusset-centre") for x in (X1 + g / 2, X3 + g / 2)]
f_bot = crease((DELTA, 0.0), (X1, 0.0), "Front flap", "Solapa delantera", "Rabat avant",
               "Aba da frente", ang=89.8, name="front-flap")
s_bot = [crease((a, 0.0), (b, 0.0), "Gusset flap", "Solapa del fuelle", "Rabat du soufflet",
                "Aba do fole", ang=89.6) for a, b in ((X1, X2), (X3, X4))]
b_bot = crease((X2, 0.0), (X3, 0.0), "Back flap", "Solapa trasera", "Rabat arrière",
               "Aba de trás", ang=89.8, name="back-flap")
ext = [crease((x, -e), (x, 0.0), "Corner of the bottom", "Esquina del fondo", "Coin du fond",
              "Canto do fundo") for x in (X1, X2, X3)]
ears = [crease((X1, 0.0), (X1 - e, -e), "Ear", "Oreja", "Oreille", "Orelha", kind="valley",
               ang=180.0),
        crease((X2, 0.0), (X2 + e, -e), "Ear", "Oreja", "Oreille", "Orelha", kind="valley",
               ang=180.0),
        crease((X3, 0.0), (X3 - e, -e), "Ear", "Oreja", "Oreille", "Orelha", kind="valley",
               ang=180.0)]
bag.label_edge("bottom-overlap", (DELTA + e, -e), (X1, -e))

def branch(s_deg):
    """Flap, corner-line and ear angles on the rigid branch of a bag corner (gusset flap s_deg).

    The bottom corners are degree-5 vertices (sectors 90°, 90°, 90°, 45°, 45°): with the bag's
    corner held at 90° they keep 2 degrees of freedom, and from the tube state (a singular,
    straight-folded start) the motion solver may take either branch. Every corner of the bag is
    driven along the branch that tucks the ear inside, solved here once on a single corner (the
    angles do not depend on the bag's dimensions)."""
    v = pliego.Sheet("corner", [(-60.0, -30.0), (60.0, -30.0), (60.0, 60.0), (-60.0, 60.0)])
    c = v.crease((0, 0), (0, 60), "mountain", 90.0)
    f = v.crease((-60, 0), (0, 0), "mountain", 90.0)
    sg = v.crease((0, 0), (60, 0), "mountain", 90.0)
    x = v.crease((0, -30), (0, 0), "mountain", 90.0)
    r = v.crease((0, 0), (-30, -30), "valley", 180.0)
    path = kinematics.solve(v, {c: -90.0, x: -90.0}, {sg: s_deg}, fixed=[c], steps=24,
                            along="chord")
    return {m: path[-1][k.edges()[0]] for m, k in (("flap", f), ("ext", x), ("ear", r))}


S_HALF, S_DOWN = -50.0, -89.6          # gusset flaps: halfway, then 0.4° short of flat
HALF, DOWN = branch(S_HALF), branch(S_DOWN)
F_DOWN = DOWN["flap"]


def bottom_pose(s_deg, b):
    return ([(m, s_deg) for m in s_bot] + [(f_bot, b["flap"]), (b_bot, b["flap"])]
            + [(m, b["ext"]) for m in ext] + [(m, b["ear"]) for m in ears])


TUBE = [(m, -90.0) for m in corners + ext] + [(seam, -89.0)]
steps = [
    pliego.Step("tube", L4("Fold the four corners and glue the flap inside the front: a tube",
                           "Dobla las cuatro esquinas y pega la pestaña por dentro del frente: "
                           "un tubo", "Pliez les quatre arêtes et collez la patte derrière "
                           "l'avant : un tube", "Dobre as quatro arestas e cole a aba por dentro "
                           "da frente: um tubo"), TUBE, duration_ms=2500),
    pliego.Step("gussets-in", L4("Push the gusset flaps in: the front and back flaps rise and "
                                 "their corners fold back into ears",
                                 "Mete las solapas de los fuelles: las solapas delantera y "
                                 "trasera se levantan y sus esquinas se doblan en orejas",
                                 "Rentrez les rabats des soufflets : les rabats avant et arrière "
                                 "se relèvent et leurs coins se replient en oreilles",
                                 "Empurre as abas dos foles para dentro: as abas da frente e de "
                                 "trás sobem e os seus cantos dobram-se em orelhas"),
                bottom_pose(S_HALF, HALF), duration_ms=2500),
    pliego.Step("bottom", L4("Press the bottom flat: gusset flaps under, the front flap over the "
                             "back flap; glue the overlap",
                             "Aplana el fondo: las solapas de los fuelles debajo y la solapa "
                             "delantera sobre la trasera; pega la parte que se superpone",
                             "Aplatissez le fond : rabats des soufflets dessous, rabat avant sur "
                             "le rabat arrière ; collez le recouvrement",
                             "Alise o fundo: as abas dos foles por baixo e a aba da frente sobre "
                             "a de trás; cole a sobreposição"),
                bottom_pose(S_DOWN, DOWN), duration_ms=2500),
]
program = pliego.Sequence.kinematic_path(bag, steps, substeps={"tube": 6, "gussets-in": 10,
                                                                "bottom": 10})

# ── self-checks: the erected bag (the program's last state) ──
arr = bag.build()
final = {}
for st in program.steps:
    for t, a in st.targets:
        final[t.edge] = a
res = kinematics.closure_residual(arr, final, pliego.P(w / 2, h / 2))
pose = kinematics.pose_arrangement(arr, final, pliego.P(w / 2, h / 2))


def world(u, v):
    for i, p in enumerate(arr.vertices):
        if abs(p.x - u) < 1e-6 and abs(p.y - v) < 1e-6:
            x, y, z = pose[i]
            return (x, -z, y + g)    # the stand rotation: (x, y, z) → (x, −z, y), then + g on z
    raise ValueError(f"paper-bag: no vertex at ({u}, {v})")


checks = {
    "tube closes": math.dist(world(X4, h), (0.0, h, g)),
    "back panel": math.dist(world(X3, 0.0), (0.0, 0.0, 0.0)),
    "gusset": math.dist(world(X2, h), (w, h, 0.0)),
}
front_tip = world(DELTA + e, -e)
back_tip = world(X2 + e, -e)
worst = max(checks.values())
if worst > TOL or res > 1e-6:
    raise ValueError(f"paper-bag: the erected bag does not close ({checks}, residual {res:.3g})")
lift = -e * math.sin(math.radians(90.0 + F_DOWN))  # the flaps stop just short of flat
if abs(front_tip[1] - lift) > TOL or abs(front_tip[2] - (g - e * math.cos(math.radians(
        90.0 + F_DOWN)))) > TOL:
    raise ValueError(f"paper-bag: the front flap does not lie on the bottom: {front_tip}")
reach = back_tip[2] - front_tip[2]
if reach < ov - 1.0:
    raise ValueError(f"paper-bag: the flaps overlap by {reach:.2f} mm, not {ov:g} mm")
ear_y = max(world(*p)[1] for p in ((X1 - e, -e), (X2 + e, -e), (X3 - e, -e)))
print(f"paper-bag: bag={w:g}x{g:g}x{h:g}mm extension={e:.1f}mm overlap={ov:g}mm "
      f"blank={X4 + SEAM:.0f}x{h + e:.0f}mm tube={worst:.1e}mm residual={res:.1e}mm "
      f"flaps={F_DOWN:.3f}deg reach={reach:.1f}mm "
      f"ears_y<={ear_y:.2f}mm program={len(program.steps)} substeps "
      f"dof={program.report['dof']} max_residual={program.report['max_residual_rad']:.1e}rad")

result = pliego.Assembly(
    [bag],
    controls=[pliego.sequence_control(label=L4("Make the bag", "Armar la bolsa",
                                               "Former le sac", "Montar o saco"))],
    sequence=program,
    targets={"erected": {"angles": dict(final), "root": (w / 2, h / 2)}},
    title="Paper bag",
)
