"""Paper mobile — sheet-hyperobjects cartridge (Pliego).

A balanced hanging mobile: card arms on threads, card shapes hanging from their ends. Every arm
hangs from its balance point, computed from the areas and centroids of everything below it.

Structure (`structure`, `tiers`):
- `cascade`: one arm per tier; each arm carries a shape on its left end and the next tier's arm on
  its right end; the last arm carries two shapes (the classic cascading mobile);
- `tree`: every arm carries two arms of the next tier, the last tier carries shapes (a binary tree
  of 2^tiers − 1 arms).

Balance (statics, computed here, never guessed). A shape is a card polygon of area A and centroid
c; it hangs from a thread attached on the vertical through c, so it hangs level. Its mass is
A · gsm. An arm is a card strip of length ℓ and mass m_arm (centroid at ℓ/2) carrying loads W_L
and W_R at its end points e_L and e_R (5 mm from each end); its thread is tied at

    x_b = (m_arm · ℓ/2 + W_L · e_L + W_R · e_R) / (m_arm + W_L + W_R)

from its left end, so the moments about the thread cancel. An arm's load on its parent is the total
mass hanging from it. The script prints every balance point and writes it into the note of the
step that creases that arm. (The sheet document's `pliego:meta` takes no extra keys, so the
numbers live in the step notes, the printout and the article.)

Arms are strips of card scored along their length: the program creases each arm to 90° into an L
beam, which keeps it straight (the score lies on the thread line, so the balance along the arm does
not change; the small sideways shift of the arm's own centroid is left to the engine). Shapes are
original simple polygons (disc, leaf, drop, star). Threads are `string` joins of fixed length; the
`initial` frame is the balanced mobile at rest, every thread taut and vertical. Dynamics (the slow
turning of the arms, the air) are the physics engine's job: the `wind` control needs it.
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


SLUG = "paper-mobile"
GSM = {"cardstock-160": 160.0, "cardstock-250": 250.0, "cardstock-300": 300.0,
       "kraft-120": 120.0}
PALETTES = {
    "primary": ["#d7263d", "#f4c430", "#1b4f9c", "#111111", "#f6f1e7"],
    "pastel": ["#f4a6a6", "#a6d8f4", "#b8e0a6", "#f4dca6", "#d0b8f4"],
    "kraft": ["#b98a5a", "#f4efe6", "#5a3e2b"],
}
ARM_WIDTH = 12.0          # two 6 mm halves of the scored arm
END_INSET = 5.0           # where the threads are tied, from each end of an arm
SHAPE_DROP = 30.0         # thread from an arm end to a shape
CLEAR = 15.0              # extra drop so a sub-arm hangs below its sibling shape
TOP_THREAD = 120.0

structure = str(PARAM(lambda: structure, "cascade"))                    # noqa: F821
tiers = int(pliego.clamp(PARAM(lambda: tiers, 4), 1, 5))                # noqa: F821
arm_length = pliego.clamp(PARAM(lambda: arm_length, 300.0), 150.0, 500.0)    # noqa: F821
shape_size = pliego.clamp(PARAM(lambda: shape_size, 80.0), 40.0, 150.0)      # noqa: F821
shapes = str(PARAM(lambda: shapes, "mixed"))                            # noqa: F821
palette = str(PARAM(lambda: palette, "primary"))                        # noqa: F821
shape_stock = str(PARAM(lambda: shape_stock, "cardstock-160"))          # noqa: F821
arm_stock = str(PARAM(lambda: arm_stock, "cardstock-300"))              # noqa: F821
if structure not in ("cascade", "tree"):
    raise ValueError(f"paper-mobile: structure must be cascade or tree, got {structure!r}")
if structure == "tree" and tiers > 3:
    raise ValueError("paper-mobile: a tree mobile has at most 3 tiers (7 arms, 8 shapes)")
if shapes not in ("mixed", "disc", "leaf", "drop", "star"):
    raise ValueError(f"paper-mobile: unknown shapes {shapes!r}")
if palette not in PALETTES or shape_stock not in GSM or arm_stock not in GSM:
    raise ValueError("paper-mobile: unknown palette or stock")


# ── original shapes, as polygons in mm (any position; they are normalised below) ──
def disc(s):
    return [(s / 2 * math.cos(2 * math.pi * k / 20), s / 2 * math.sin(2 * math.pi * k / 20))
            for k in range(20)]


def leaf(s):
    right = [(0.3 * s * (1 - t * t), t * s / 2) for t in (k / 8 - 1 for k in range(1, 16))]
    return [(0.0, -s / 2)] + right + [(0.0, s / 2)] + [(-x, y) for x, y in reversed(right)]


def drop(s):
    r = 0.32 * s                      # a round bottom and a point at the top
    arc = [(r * math.cos(math.radians(a)), -s / 2 + r + r * math.sin(math.radians(a)))
           for a in range(120, 421, 15)]
    return arc + [(0.0, s / 2)]


def star(s):
    return [((s / 2 if k % 2 == 0 else 0.21 * s) * math.cos(math.pi / 2 + math.pi * k / 5),
             (s / 2 if k % 2 == 0 else 0.21 * s) * math.sin(math.pi / 2 + math.pi * k / 5))
            for k in range(10)]


MAKERS = {"disc": disc, "leaf": leaf, "drop": drop, "star": star}
CYCLE = ["disc", "leaf", "star", "drop"]


def area_centroid(poly):
    a = cx = cy = 0.0
    for i, (x0, y0) in enumerate(poly):
        x1, y1 = poly[(i + 1) % len(poly)]
        cr = x0 * y1 - x1 * y0
        a += cr
        cx += (x0 + x1) * cr
        cy += (y0 + y1) * cr
    return a / 2.0, (cx / (3.0 * a), cy / (3.0 * a))


# ── the tree of arms and shapes ──
nodes = []        # dicts: kind, id, children, ...


def new_shape():
    i = sum(1 for n in nodes if n["kind"] == "shape")
    kind = CYCLE[i % 4] if shapes == "mixed" else shapes
    size = shape_size * (0.7 + 0.45 * ((i * 0.618034) % 1.0))     # varied, deterministic
    poly = MAKERS[kind](size)
    lo_x, lo_y = min(p[0] for p in poly), min(p[1] for p in poly)
    poly = [(x - lo_x, y - lo_y) for x, y in poly]
    area, c = area_centroid(poly)
    if area < 0:
        poly.reverse()
        area, c = area_centroid(poly)
    # the thread is tied on the vertical through the centroid, 4 mm below the top edge
    tops = []
    for k, (x0, y0) in enumerate(poly):
        x1, y1 = poly[(k + 1) % len(poly)]
        if (x0 - c[0]) * (x1 - c[0]) <= 0 and abs(x1 - x0) > 1e-12:
            tops.append(y0 + (y1 - y0) * (c[0] - x0) / (x1 - x0))
    node = {"kind": "shape", "id": f"shape-{i + 1}", "poly": poly, "shape": kind,
            "area": area, "centroid": c, "attach": (c[0], max(tops) - 4.0),
            "mass": area * GSM[shape_stock] * 1e-6, "height": max(p[1] for p in poly)}
    nodes.append(node)
    return node


def new_arm(depth):
    i = sum(1 for n in nodes if n["kind"] == "arm")
    node = {"kind": "arm", "id": f"arm-{i + 1}", "depth": depth,
            "length": arm_length * 0.8 ** (depth - 1)}
    nodes.append(node)
    if structure == "cascade":
        node["children"] = [new_shape(), new_arm(depth + 1) if depth < tiers else new_shape()]
    else:
        node["children"] = ([new_arm(depth + 1), new_arm(depth + 1)] if depth < tiers
                            else [new_shape(), new_shape()])
    ell = node["length"]
    node["mass_own"] = ell * ARM_WIDTH * GSM[arm_stock] * 1e-6
    wl, wr = node["children"][0]["mass"], node["children"][1]["mass"]
    el, er = END_INSET, ell - END_INSET
    node["mass"] = node["mass_own"] + wl + wr
    node["balance"] = (node["mass_own"] * ell / 2.0 + wl * el + wr * er) / node["mass"]
    node["ends"] = (el, er)
    return node


root = new_arm(1)
colours = PALETTES[palette]


def rot_y(deg):
    h = math.radians(deg) / 2.0
    return (0.0, math.sin(h), 0.0, math.cos(h))


def qmul(a, b):
    ax, ay, az, aw = a
    bx, by, bz, bw = b
    return (aw * bx + ax * bw + ay * bz - az * by, aw * by - ax * bz + ay * bw + az * bx,
            aw * bz + ax * by - ay * bx + az * bw, aw * bw - ax * bx - ay * by - az * bz)


def rot(q, v):
    x, y, z, s = q
    tx, ty, tz = 2 * (y * v[2] - z * v[1]), 2 * (z * v[0] - x * v[2]), 2 * (x * v[1] - y * v[0])
    return (v[0] + s * tx + (y * tz - z * ty), v[1] + s * ty + (z * tx - x * tz),
            v[2] + s * tz + (x * ty - y * tx))


Q_UPRIGHT = (math.sqrt(0.5), 0.0, 0.0, math.sqrt(0.5))     # +90° about x: a sheet stands up

# ── hang everything: every thread vertical and taut ──
sheets, joins, poses = [], [], {}


def depth_span(node):
    """Vertical extent below a node's attachment point."""
    if node["kind"] == "shape":
        return node["attach"][1]
    return max(SHAPE_DROP + depth_span(c) if c["kind"] == "shape" else drop_for(node) +
               depth_span(c) for c in node["children"])


def drop_for(arm):
    """Thread length from an arm end to a child arm: below the sibling shapes."""
    sib = [c for c in arm["children"] if c["kind"] == "shape"]
    return max([SHAPE_DROP + s["attach"][1] + CLEAR for s in sib] + [SHAPE_DROP + 60.0])


def hang(node, point, yaw):
    """Place `node` with its attachment point at world `point`; arms turn by `yaw`."""
    if node["kind"] == "shape":
        q = qmul(rot_y(yaw), Q_UPRIGHT)
        ax, ay = node["attach"]
        ra = rot(q, (ax, 0.0, -ay))
        origin = tuple(point[k] - ra[k] for k in range(3))
        k = int(node["id"].split("-")[1]) - 1
        s = pliego.Sheet(node["id"], node["poly"], stock=shape_stock, grain_deg=90.0,
                         label=L4(f"Shape {k + 1}", f"Figura {k + 1}", f"Forme {k + 1}",
                                  f"Forma {k + 1}"),
                         front=colours[k % len(colours)], back=colours[k % len(colours)],
                         placement=pliego.Placement(origin=origin, rotation=q))
        sheets.append(s)
        node["sheet"] = s
        return
    ell, xb = node["length"], node["balance"]
    q = rot_y(yaw)
    rb = rot(q, (xb, 0.0, -ARM_WIDTH / 2.0))
    origin = tuple(point[k] - rb[k] for k in range(3))
    k = int(node["id"].split("-")[1]) - 1
    s = pliego.Sheet(node["id"], pliego.rectangle(ell, ARM_WIDTH), stock=arm_stock,
                     grain_deg=0.0,
                     label=L4(f"Arm {k + 1}", f"Brazo {k + 1}", f"Bras {k + 1}",
                              f"Braço {k + 1}"),
                     front="#1a1a1a", back="#1a1a1a",
                     placement=pliego.Placement(origin=origin, rotation=q))
    node["score"] = s.mountain((0.0, ARM_WIDTH / 2.0), (ell, ARM_WIDTH / 2.0), 90.0,
                               treatment="score", name="spine")
    sheets.append(s)
    node["sheet"] = s
    for end, child in zip(node["ends"], node["children"], strict=True):
        we = rot(q, (end, 0.0, -ARM_WIDTH / 2.0))
        end_w = tuple(origin[j] + we[j] for j in range(3))
        d = SHAPE_DROP if child["kind"] == "shape" else drop_for(node)
        child_pt = (end_w[0], end_w[1] - d, end_w[2])
        hang(child, child_pt, yaw + 90.0)
        attach = child["attach"] if child["kind"] == "shape" else (child["balance"],
                                                                   ARM_WIDTH / 2.0)
        joins.append(pliego.string(f"thread-{node['id']}-{child['id']}",
                                   (s, (end, ARM_WIDTH / 2.0)), (child["sheet"], attach), d))


height = TOP_THREAD + depth_span(root) + 50.0
ceiling = (0.0, height, 0.0)
hang(root, (0.0, height - TOP_THREAD, 0.0), 0.0)
joins.insert(0, pliego.string("hang", (root["sheet"], (root["balance"], ARM_WIDTH / 2.0)),
                              ceiling, TOP_THREAD))

# fail loud: the statics close (zero moment about every thread) and nothing collides
for n in nodes:
    if n["kind"] != "arm":
        continue
    (el, er), (cl, cr) = n["ends"], n["children"]
    moment = (n["mass_own"] * (n["length"] / 2.0 - n["balance"]) + cl["mass"] * (el - n["balance"])
              + cr["mass"] * (er - n["balance"]))
    if abs(moment) > 1e-9:
        raise ValueError(f"paper-mobile: {n['id']} does not balance ({moment} g·mm)")
    if not END_INSET < n["balance"] < n["length"] - END_INSET:
        raise ValueError(f"paper-mobile: {n['id']} balances outside its ends; change the sizes")


def world_box(s):
    q, o = s.placement.rotation, s.placement.origin
    pts = [rot(q, (p.x, 0.0, -p.y)) for p in s.outline]
    return [min(p[k] + o[k] for p in pts) for k in range(3)], [max(p[k] + o[k] for p in pts)
                                                               for k in range(3)]


boxes = [(s.id, world_box(s)) for s in sheets if s.id.startswith("shape")]
for i, (ia, (alo, ahi)) in enumerate(boxes):
    for ib, (blo, bhi) in boxes[i + 1:]:
        if all(alo[k] < bhi[k] and blo[k] < ahi[k] for k in range(3)):
            raise ValueError(f"paper-mobile: {ia} and {ib} would touch; use longer arms or "
                             "smaller shapes")


def mm(x):
    return f"{x:.1f}"


report = []
steps = []
for t in range(1, tiers + 1):
    arms = [n for n in nodes if n["kind"] == "arm" and n["depth"] == t]
    for n in arms:
        report.append(f"{n['id']}: length {mm(n['length'])} mm, carries "
                      f"{n['mass'] - n['mass_own']:.3f} g, balance {mm(n['balance'])} mm from "
                      "its left end")
    bal = ", ".join(f"{n['id']} {mm(n['balance'])}" for n in arms)
    steps.append(pliego.Step(
        f"crease-tier-{t}",
        L4(f"Crease the tier-{t} arm{'s' if len(arms) > 1 else ''} into an L beam",
           f"Dobla por el marcado {'los brazos' if len(arms) > 1 else 'el brazo'} del nivel {t} "
           "en ángulo", f"Pliez sur le rainage {'les bras' if len(arms) > 1 else 'le bras'} du "
           f"niveau {t} en cornière", f"Dobre no vinco {'os braços' if len(arms) > 1 else 'o '
                                                         'braço'} do nível {t} em cantoneira"),
        [(n["score"], -90.0) for n in arms], duration_ms=1500,
        note=L4(f"Threads tied at the balance point, mm from the left end: {bal}.",
                f"El hilo va en el punto de equilibrio, en mm desde el extremo izquierdo: {bal}.",
                f"Le fil est noué au point d'équilibre, en mm depuis l'extrémité gauche : {bal}.",
                f"O fio vai no ponto de equilíbrio, em mm a partir da ponta esquerda: {bal}.")))
for line in report:
    print(f"paper-mobile: {line}")
print(f"paper-mobile: structure={structure} tiers={tiers} arms="
      f"{sum(1 for n in nodes if n['kind'] == 'arm')} shapes="
      f"{sum(1 for n in nodes if n['kind'] == 'shape')} height={mm(height)}mm "
      f"total_mass={root['mass']:.3f}g")

wind = pliego.control("wind", "wind", L4("Air", "Aire", "Air", "Ar"), 0.0, 0.0, 3.0, "m/s")
result = pliego.Assembly(
    sheets, joins=joins, initial="flat",
    controls=[pliego.sequence_control(label=L4("Crease the arms", "Doblar los brazos",
                                               "Plier les bras", "Dobrar os braços")), wind],
    sequence=pliego.Sequence(steps, mode="physical"),
    title="Paper mobile")
