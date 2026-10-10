"""Paper bag — sheet-hyperobjects cartridge (Pliego).

The flat-bottomed paper bag with side gussets (the SOS style), made from one sheet of kraft:

* the sheet is a row of panels: front (`width`), gusset (`gusset`), back (`width`), gusset, and a
  glue flap that closes the tube against the inside of the front; each gusset is scored down its
  centre so the made bag can pleat in;
* below the bottom score the front and back panels continue by an extension `e` =
  `gusset`/2 + `overlap`/2 and each gusset by `gusset`/2: the bottom. Each gusset extension
  carries two 45° creases from the bag's corners to its middle; folding in, it becomes a triangle
  lying flat on the bottom, and its two corners (the ears) fold back over it. The back and front
  extensions fold over the triangles and the ears, overlap by `overlap` mm in the middle and are
  glued, so the ears end tucked between the gusset triangles and the flaps; the sheet is not cut
  at the corners. From inside, each gusset shows as a triangle (the diamond fold).

The fold program is kinematic and every in-between state is an exact rigid state, expanded by
`pliego.Sequence.kinematic_path` from three key poses: the tube folds on its four corners, the
gusset flaps fold in halfway while the front and back flaps rise and the ears fold, then the
bottom is pressed flat (0.4° short of flat, so its layers do not coincide). The bottom corners are
degree-5 vertices with two branches from the singular tube state; `branch()` solves, on one
corner, the branch on which the ear ends between the gusset triangle and the flap, and every
corner is driven along it. The script checks the erected bag: the tube closes on the glue flap,
the flaps lie on the bottom and overlap by `overlap`, the ears lie between the gusset triangles
and the flaps, and every crease closes (`kinematics.closure_residual`).
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
e = g / 2 + ov / 2                    # bottom extension of the front and the back
eg = g / 2                            # bottom extension of the gussets (to the triangles' tips)
SEAM = 15.0                           # glue flap width
DELTA = 1.0                           # the front's extension starts 1 mm in from the seam corner
TOL = 1e-4
if g > w - 2.0:
    raise ValueError(f"paper-bag: a {g:g} mm gusset needs a front at least {g + 2:.0f} mm wide "
                     "(the gusset triangles would meet in the middle of the bottom)")
if ov > g - 4.0:
    raise ValueError(f"paper-bag: the overlap must stay under the gusset minus 4 mm ({g - 4:g})")
if h < g:
    raise ValueError("paper-bag: the bag must be at least as tall as its gusset")

X1, X2, X3, X4 = w, w + g, 2 * w + g, 2 * w + 2 * g      # panel edges along the sheet
ring = [(0.0, 0.0), (DELTA, 0.0), (DELTA, -e), (X1, -e), (X1, -eg), (X2, -eg), (X2, -e),
        (X3, -e), (X3, -eg), (X4, -eg), (X4, 0.0), (X4 + SEAM, 4.0), (X4 + SEAM, h - 4.0),
        (X4, h), (0.0, h)]
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
ext = [crease((x, -eg), (x, 0.0), "Corner of the bottom", "Esquina del fondo", "Coin du fond",
              "Canto do fundo") for x in (X1, X2, X3)]
ears = [crease((x, 0.0), (x + sgn * eg, -eg), "Ear", "Oreja", "Oreille", "Orelha",
               kind="valley", ang=180.0)
        for x, sgn in ((X1, 1.0), (X2, -1.0), (X3, 1.0), (X4, -1.0))]
bag.label_edge("bottom-overlap", (DELTA, -e), (X1, -e))

def branch(s_deg):
    """Front-flap, corner-line and ear angles on the rigid branch of a bag corner (gusset flap at
    s_deg).

    A bottom corner is a degree-5 vertex: the gusset and the front (90° each), the front flap
    (90°), the ear and the gusset triangle (45° each). With the bag's corner held at 90° it keeps
    2 degrees of freedom, and from the tube state (a singular, straight-folded start) the motion
    solver may take either of two branches. Every corner is driven along the one on which the
    front flap folds in and the ear ends between the gusset triangle and the flap, solved here on
    a single corner (the angles do not depend on the bag's dimensions)."""
    v = pliego.Sheet("corner", [(-60.0, -40.0), (0.0, -40.0), (0.0, -30.0), (30.0, -30.0),
                                (60.0, 0.0), (60.0, 60.0), (-60.0, 60.0)])
    c = v.crease((0, 0), (0, 60), "mountain", 90.0)
    f = v.crease((-60, 0), (0, 0), "mountain", 90.0)
    sg = v.crease((0, 0), (60, 0), "mountain", 90.0)
    x = v.crease((0, -30), (0, 0), "mountain", 90.0)
    r = v.crease((0, 0), (30, -30), "valley", 180.0)
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
front_tip = world(DELTA, -e)
back_tip = world(X2, -e)
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
tr = kinematics.face_transforms(arr, final, kinematics.root_face(arr, pliego.P(w / 2, h / 2)))


def height(u, v, x, z):
    """Height (world y) of the face holding paper point (u, v), at world (x, z)."""
    rm, t = tr[kinematics.root_face(arr, pliego.P(u, v))]
    q = []
    for p_ in ((u, v), (u + 1.0, v), (u, v + 1.0)):
        a_ = (p_[0], 0.0, -p_[1])
        loc = [sum(rm[i][j] * a_[j] for j in range(3)) + t[i] for i in range(3)]
        q.append((loc[0], -loc[2], loc[1] + g))
    n_ = [(q[1][(i + 1) % 3] - q[0][(i + 1) % 3]) * (q[2][(i + 2) % 3] - q[0][(i + 2) % 3])
          - (q[1][(i + 2) % 3] - q[0][(i + 2) % 3]) * (q[2][(i + 1) % 3] - q[0][(i + 1) % 3])
          for i in range(3)]
    return q[0][1] - (n_[0] * (x - q[0][0]) + n_[2] * (z - q[0][2])) / n_[1]


# the ear must lie between the gusset triangle (inside) and the front flap (outside)
ear_uv = (X1 + eg / 3, -2 * eg / 3)
c_ = kinematics.pose_arrangement(arr, final, pliego.P(w / 2, h / 2))
eu = [c_[i] for i, p_ in enumerate(arr.vertices)
      if (abs(p_.x - X1) < 1e-6 and abs(p_.y + eg) < 1e-6) or
      (abs(p_.x - X1 - eg) < 1e-6 and abs(p_.y + eg) < 1e-6) or
      (abs(p_.x - X1) < 1e-6 and abs(p_.y) < 1e-6)]
px = sum(q[0] for q in eu) / 3
pz = sum(q[1] for q in eu) / 3 + g
layers = (height(X1 + 0.6 * eg, -0.2 * eg, px, pz), height(*ear_uv, px, pz),
          height(DELTA + 1.0, -1.0, px, pz))
if not layers[0] > layers[1] > layers[2]:
    raise ValueError(f"paper-bag: the ear is not between the gusset and the flap: {layers}")
ear_y = layers[1]
print(f"paper-bag: bag={w:g}x{g:g}x{h:g}mm extension={e:.1f}mm overlap={ov:g}mm "
      f"blank={X4 + SEAM:.0f}x{h + e:.0f}mm tube={worst:.1e}mm residual={res:.1e}mm "
      f"flaps={F_DOWN:.3f}deg reach={reach:.1f}mm "
      f"ear_height={ear_y:.2f}mm program={len(program.steps)} substeps "
      f"dof={program.report['dof']} max_residual={program.report['max_residual_rad']:.1e}rad")

result = pliego.Assembly(
    [bag],
    controls=[pliego.sequence_control(label=L4("Make the bag", "Armar la bolsa",
                                               "Former le sac", "Montar o saco"))],
    sequence=program,
    targets={"erected": {"angles": dict(final), "root": (w / 2, h / 2)}},
    title="Paper bag",
)
