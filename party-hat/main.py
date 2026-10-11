"""Party hat — sheet-hyperobjects cartridge (Pliego).

A cone hat rolled from a flat sector of card, closed with a glue tab, worn with an elastic chin
strap. The user gives the hat's height h and base diameter d; the script derives the slant
L = √(h² + (d/2)²) and the sector angle θ = 360° · (d/2) / L (the development of a cone).

Segmentation (how a rolled shape is modelled). The kernel's sheets fold along edges, so the curved
cone is approximated by a pyramid of `panels` narrow triangles: rulings from the apex to the rim,
authored as `F` (flat) lines and handed to the document as plain paper (treatment `none`: never
scored or cut, the engine treats them as panel hinges). The rim between rulings is a chord, so the
sheet outline is a polygon and the folded state is an exact isometry of it (a right pyramid on a
regular N-gon, circumradius R' = L·sin(Δ/2)/sin(π/N), Δ = θ/N). The glue tab is a continuation of
the sector over `m` more panels, trimmed short of the apex and chamfered at the rim; it is
segmented by the same rulings, so in the closed hat it lies exactly on the first m panels (inside
the cone) and a `glue` join welds it there (map = rotation by −θ about the apex).

Modes.
- `make`: the making as a kinematic program on the rulings (curl, close, tuck the tab): the studio
  preview plays it and it ends in the cone, which is also written as the frame `target:cone`.
- `worn`: the finished hat for the physics engine: glue weld, an elastic as a `string` join between
  two points 8 mm above the rim on opposite sides (a string is inextensible, so its length is the
  elastic's stretched limit — an approximation), the `initial` frame upright on the table, and a
  physical program that presses the hat flat for storage and opens it again (flat: two layers, folds
  at the seam and at the opposite ruling; the weld holds in both states).
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


SLUG = "party-hat"
STOCKS = ("cardstock-160", "cardstock-250", "kraft-120", "foil-paper", "copy-80")
TAB_RIM_MM = 12.0          # glue tab width at the rim (rounded up to whole panels)
TAB_INNER = 0.3            # the tab stops at 0.3 L from the apex
CHAMFER = 4.0              # mm, the tab's rim corner
ELASTIC_ABOVE_RIM = 8.0    # mm, where the elastic is stapled

mode = str(PARAM(lambda: mode, "make"))                     # noqa: F821
height = pliego.clamp(PARAM(lambda: height, 180.0), 80.0, 400.0)       # noqa: F821
diameter = pliego.clamp(PARAM(lambda: diameter, 150.0), 80.0, 260.0)   # noqa: F821
panels = int(pliego.clamp(PARAM(lambda: panels, 48), 24, 96))          # noqa: F821
elastic = pliego.clamp(PARAM(lambda: elastic, 300.0), 0.0, 600.0)      # noqa: F821
stock = str(PARAM(lambda: stock, "cardstock-160"))                     # noqa: F821
colour = str(PARAM(lambda: colour, "#e94f37"))                         # noqa: F821
if mode not in ("make", "worn"):
    raise ValueError(f"party-hat: mode must be make or worn, got {mode!r}")
if stock not in STOCKS:
    raise ValueError(f"party-hat: stock must be one of {STOCKS}, got {stock!r}")
panels += panels % 2       # even: the flattened hat folds at the seam and at ruling N/2

r = diameter / 2.0
L = math.hypot(height, r)                 # slant height = sector radius
theta = 2.0 * math.pi * r / L             # sector angle (rad)
N = panels
D = theta / N                             # angle of one panel
m = max(1, math.ceil(TAB_RIM_MM / (2.0 * L * math.sin(D / 2.0))))
total = theta + m * D
if math.degrees(total) > 330.0:
    raise ValueError(f"party-hat: a {height:g} mm hat on a {diameter:g} mm base needs a "
                     f"{math.degrees(total):.0f}° sector with its tab; make it taller")
if elastic and elastic < 1.05 * diameter:
    raise ValueError("party-hat: the elastic must be longer than the base diameter (or 0)")

# ── the flat sector, apex at the origin of a polar frame, opening upward ──
a0 = math.pi / 2.0 - total / 2.0


def polar(rho, phi):
    return (rho * math.cos(a0 + phi), rho * math.sin(a0 + phi))


rho0 = TAB_INNER * L
ring = [(0.0, 0.0)] + [polar(L, k * D) for k in range(N + m)]
ring += [polar(L - CHAMFER, total), polar(rho0 + CHAMFER, total), polar(rho0, theta)]
xs, ys = [p[0] for p in ring], [p[1] for p in ring]
ox, oy = -min(xs), -min(ys)
APEX = (ox, oy)


def local(p):
    return (p[0] + ox, p[1] + oy)


hat = pliego.Sheet(
    "hat", [local(p) for p in ring], stock=stock, grain_deg=90.0,
    label=L4("Hat sector", "Sector del gorro", "Secteur du chapeau", "Setor do chapéu"),
    front="#f6f1e7", back=colour)


def ruling(a, b, name=None):
    hat.crease(local(a), local(b), "flat", 0.0, treatment="crease", name=name)


for k in range(1, N):
    ruling((0.0, 0.0), polar(L, k * D))
ruling(polar(rho0, theta), polar(L, theta), "glue-tab")         # the tab's hinge
ix0, iy0 = polar(rho0, theta)
ix1, iy1 = polar(rho0 + CHAMFER, total)
for j in range(1, m):                                           # rulings across the tab
    ux, uy = math.cos(a0 + theta + j * D), math.sin(a0 + theta + j * D)
    # ray from the apex along (ux, uy) meets the tab's inner edge (ix0,iy0)→(ix1,iy1)
    ex, ey = ix1 - ix0, iy1 - iy0
    det = ux * (-ey) - uy * (-ex)
    s = (ix0 * (-ey) - iy0 * (-ex)) / det
    ruling((s * ux, s * uy), polar(L, theta + j * D))

MIN_FEATURE = {"copy-80": 1.0, "kraft-120": 1.0, "cardstock-160": 1.5, "foil-paper": 1.5,
               "cardstock-250": 2.0}[stock]
cut_check = pliego.papercut.analyze(hat, min_feature_mm=MIN_FEATURE)
if not cut_check.ok:
    raise ValueError(f"party-hat: the sector fails the papercut check: {cut_check.issues}")

# ── the closed hat: a right pyramid on a regular N-gon ──
Rb = L * math.sin(D / 2.0) / math.sin(math.pi / N)
Hp = math.sqrt(L * L - Rb * Rb)
SPIN = 1.0                     # base polygon orientation: front (inside of the hat) faces inward


def base(k):
    a = 2.0 * math.pi * k / N
    return (Rb * math.cos(a), 0.0, SPIN * Rb * math.sin(a))


def cone(sheet_id, uv):
    px, py = uv[0] - ox, uv[1] - oy
    phi = math.atan2(py, px) - a0
    while phi < -0.2:          # the sector never reaches 330°+: wrap only real negatives
        phi += 2.0 * math.pi
    k = min(max(int(phi / D + 1e-12), 0), N + m - 1)
    p0, p1 = polar(L, k * D), polar(L, (k + 1) * D)
    det = p0[0] * p1[1] - p0[1] * p1[0]
    s = (px * p1[1] - py * p1[0]) / det
    t = (p0[0] * py - p0[1] * px) / det
    b0, b1 = base(k % N), base((k + 1) % N)
    return tuple(s * b0[i] + t * b1[i] + (1.0 - s - t) * (0.0, Hp, 0.0)[i] for i in range(3))


arr = hat.build()


def newell(pts):
    n = [0.0, 0.0, 0.0]
    for i, p in enumerate(pts):
        q = pts[(i + 1) % len(pts)]
        n[0] += (p[1] - q[1]) * (p[2] + q[2])
        n[1] += (p[2] - q[2]) * (p[0] + q[0])
        n[2] += (p[0] - q[0]) * (p[1] + q[1])
    s = math.sqrt(n[0] ** 2 + n[1] ** 2 + n[2] ** 2)
    return (n[0] / s, n[1] / s, n[2] / s)


def fold_angles(pose):
    """Signed fold angle (FOLD convention, deg) of every interior F/M/V edge in `pose`."""
    pts = [pose("hat", (v.x, v.y)) for v in arr.vertices]
    left = {}
    for fi, f in enumerate(arr.faces):
        for k in range(len(f)):
            left[(f[k], f[(k + 1) % len(f)])] = fi
    normals = [newell([pts[v] for v in f]) for f in arr.faces]
    out = {}
    for e, (a, b) in enumerate(arr.edges):
        if arr.assignment[e] in ("F", "M", "V") and (a, b) in left and (b, a) in left:
            edge = tuple(pts[b][i] - pts[a][i] for i in range(3))
            out[e] = pliego.tessellate.signed_fold_angle(normals[left[(a, b)]],
                                                         normals[left[(b, a)]], edge)
    return out


angles = fold_angles(cone)
if min(angles.values()) <= 0.0:
    raise ValueError("party-hat: the cone pose is not a valley roll (orientation error)")

# which rulings are which: sector rulings, the tab hinge and the tab's own rulings
verts = arr.vertices


def edge_phi(e):
    a, b = arr.edges[e]
    mx = (verts[a].x + verts[b].x) / 2.0 - ox
    my = (verts[a].y + verts[b].y) / 2.0 - oy
    phi = math.atan2(my, mx) - a0
    return phi + 2.0 * math.pi if phi < -0.2 else phi


sector_e = [e for e in angles if edge_phi(e) < theta - D / 2.0]
tab_e = [e for e in angles if e not in sector_e]
hinge_e = min(tab_e, key=lambda e: abs(edge_phi(e) - theta))
opposite_e = min(sector_e, key=lambda e: abs(edge_phi(e) - theta / 2.0))

# ── glue: the tab, inset from its edges, welded onto the first m panels ──
inset = 1.5
gl = [polar(rho0 + CHAMFER + inset, theta + 0.04 * D), polar(L - inset, theta + 0.04 * D),
      polar(L - CHAMFER - inset, total - 0.04 * D), polar(rho0 + CHAMFER + inset,
                                                           total - 0.04 * D)]
region = [local(p) for p in gl]
for p in region:
    if not hat.region_contains(p):
        raise ValueError(f"party-hat: glue point {p} is off the tab")
c, s_ = math.cos(-theta), math.sin(-theta)
glue_map = (c, -s_, s_, c, APEX[0] - (c * APEX[0] - s_ * APEX[1]),
            APEX[1] - (s_ * APEX[0] + c * APEX[1]))
for p in region:                                 # fail loud: every weld point lands on its zone
    q = (glue_map[0] * p[0] + glue_map[1] * p[1] + glue_map[4],
         glue_map[2] * p[0] + glue_map[3] * p[1] + glue_map[5])
    gap = math.dist(cone("hat", p), cone("hat", q))
    if gap > 1e-6:
        raise ValueError(f"party-hat: weld point {p} misses its glue zone by {gap} mm")

params = {"height": height, "diameter": diameter, "panels": N, "elastic": elastic,
          "stock": stock, "colour": colour}
info = {"slant_mm": round(L, 3), "sector_deg": round(math.degrees(theta), 3),
        "tab_panels": m, "min_bridge_mm": cut_check.min_bridge_mm, "pyramid_base_radius_mm": round(Rb, 3),
        "pyramid_height_mm": round(Hp, 3),
        "sheet_mm": [round(max(xs) - min(xs), 1), round(max(ys) - min(ys), 1)]}
print(f"party-hat: {info}")


def steps_make():
    half = [(pliego.assembly.EdgeRef(hat, e), 0.5 * angles[e]) for e in sector_e]
    full = [(pliego.assembly.EdgeRef(hat, e), angles[e]) for e in sector_e]
    tab = [(pliego.assembly.EdgeRef(hat, e), angles[e]) for e in tab_e]
    return [
        pliego.Step("curl", L4("Curl the sector into a loose cone, coloured side out",
                               "Curva el sector en un cono holgado, con el lado de color hacia "
                               "fuera", "Courbez le secteur en un cône lâche, face colorée à "
                               "l'extérieur", "Curve o setor num cone folgado, com o lado colorido "
                               "para fora"), half, duration_ms=2500),
        pliego.Step("close", L4("Bring the straight edges together: the cone closes",
                                "Junta los bordes rectos: el cono se cierra",
                                "Rapprochez les bords droits : le cône se ferme",
                                "Junte as bordas retas: o cone se fecha"), full, duration_ms=2500),
        pliego.Step("tuck-tab", L4("Tuck the glue tab inside and glue it under the other edge",
                                   "Mete la pestaña adentro y pégala bajo el otro borde",
                                   "Rentrez la languette et collez-la sous l'autre bord",
                                   "Dobre a aba para dentro e cole-a sob a outra borda"), tab,
                    duration_ms=2000,
                    note=L4("Optional: staple an elastic 8 mm above the rim on opposite sides.",
                            "Opcional: engrapa un elástico 8 mm arriba del borde, en lados "
                            "opuestos.", "En option : agrafez un élastique à 8 mm du bord, de "
                            "part et d'autre.", "Opcional: grampeie um elástico 8 mm acima da "
                            "borda, em lados opostos.")),
    ]


if mode == "make":
    steps = steps_make() + [pliego.Step(
        "press", L4("Hold the tab until the glue sets",
                    "Sostén la pestaña hasta que el pegamento agarre",
                    "Tenez la languette jusqu'à ce que la colle prenne",
                    "Segure a aba até a cola pegar"), [], duration_ms=800)]
    # the tab's glue takes hold once it lies under the other edge (spec §5.19)
    glue = pliego.glue("tab-to-panels", hat, region, hat, glue_map, side="front")
    glue["active_from"] = "press"
    assembly = pliego.Assembly(
        [hat], joins=[glue], controls=[pliego.sequence_control(label=L4("Roll the hat", "Enrollar el gorro",
                                                          "Rouler le chapeau", "Enrolar o "
                                                          "chapéu"))],
        sequence=pliego.Sequence(steps, mode="kinematic"),
        targets={"cone": {"angles": dict(angles)}}, title="Party hat")
else:
    joins = [pliego.glue("tab-to-panels", hat, region, hat, glue_map, side="front")]
    if elastic:
        p_left = local(polar(L - ELASTIC_ABOVE_RIM * L / Hp, (math.floor(N / 4) + 0.5) * D))
        p_right = local(polar(L - ELASTIC_ABOVE_RIM * L / Hp, (math.floor(3 * N / 4) + 0.5) * D))
        joins.append(pliego.string("elastic", (hat, p_left), (hat, p_right), elastic))
    flat = {e: 0.0 for e in angles}
    flat[opposite_e] = 180.0
    flat[hinge_e] = 180.0
    steps = [
        pliego.Step("press-flat", L4("Press the hat flat to store it", "Aplana el gorro para "
                                     "guardarlo", "Aplatissez le chapeau pour le ranger",
                                     "Achate o chapéu para guardá-lo"),
                    [(pliego.assembly.EdgeRef(hat, e), a) for e, a in flat.items()],
                    duration_ms=2500),
        pliego.Step("open", L4("Open it into a cone again", "Ábrelo de nuevo en cono",
                               "Rouvrez-le en cône", "Abra-o de novo em cone"),
                    [(pliego.assembly.EdgeRef(hat, e), a) for e, a in angles.items()],
                    duration_ms=2500),
    ]
    assembly = pliego.Assembly(
        [hat], joins=joins, initial=cone,
        controls=[pliego.sequence_control(label=L4("Flatten and open", "Aplanar y abrir",
                                                   "Aplatir et ouvrir", "Achatar e abrir"))],
        sequence=pliego.Sequence(steps, mode="physical"), targets={"cone": cone, "flat": {"angles": flat}},
        title="Party hat")

doc = assembly.build(cartridge=SLUG, mode=mode, params=params)
# The rulings are plain paper (spec §4: F + `none`); the Sheet API authors F lines with a
# treatment, so they are marked untreated here: exporters must not score a curved surface.
tr = doc.data["pliego:edges_treatment"]
for e, a in enumerate(doc.data["edges_assignment"]):
    if a == "F" and tr[e] == "crease":
        tr[e] = "none"
result = doc.stamp()
