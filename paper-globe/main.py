"""Paper globe — sheet-hyperobjects cartridge (Pliego).

A sphere made of gores: `gores` (12 or 24) lens-shaped strips, each covering 360°/G of longitude
from pole to pole, cut flat and bent along their length until neighbours meet edge to edge.

Geometry. A gore is not exactly developable (a sphere has double curvature), so each one is a
developable approximation: the sphere is replaced by the polyhedron whose vertices lie on the
sphere at every `band` degrees of latitude and every 360°/G of longitude (a "UV sphere"). One gore
of it is a chain of isosceles trapezoids (two triangles at the poles), each sharing a latitude
chord with the next, so the chain unrolls flat exactly: a trapezoid between latitudes φᵢ and φᵢ₊₁
has parallel sides cᵢ = 2ρ·cos φᵢ·sin(π/G) and slant sides s = 2ρ·sin(Δφ/2). The flat gore is
the classic lens whose width follows cos φ. Its panel lines (the latitude chords) are `F` lines,
treatment `none`: plain paper, never scored. The assembled globe is an exact isometry of every
gore: each panel is mapped rigidly onto its trapezoid of the polyhedron.

The surface pattern is original and simple: gores in alternating colours (a beach-ball look), a
two-tone graticule (the seams are meridians every 360°/G, the panel lines parallels every `band`
degrees) or plain paper. No map artwork is used.

Program. Each gore sheet is placed so that its south-pole triangle (the sheet's first face) sits
where it belongs on the globe; the flat gores start radiating from the south pole like petals and a
kinematic program bends them along their meridians until they close into the sphere
(`target:globe`). Gores are pasted onto a ball or, here, simply meet: the core is not modelled
(solids belong to Yantra4D), so nothing holds the shape but the program's rigid state.
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


SLUG = "paper-globe"
STOCKS = {"copy-80": 1.0, "kraft-120": 1.0, "cardstock-160": 1.5, "washi-kozo-30": 1.0}
PATTERNS = {
    "beach-ball": ["#e94f37", "#f6f1e7", "#2e86ab", "#f2b134", "#3bb273", "#f6f1e7"],
    "graticule": ["#3a7ca5", "#81c3d7"],
    "plain": ["#f6f1e7"],
}

gores = int(PARAM(lambda: gores, 12))                                   # noqa: F821
diameter = pliego.clamp(PARAM(lambda: diameter, 150.0), 60.0, 400.0)    # noqa: F821
band = float(PARAM(lambda: band, 10.0))                                 # noqa: F821
pattern = str(PARAM(lambda: pattern, "beach-ball"))                     # noqa: F821
stock = str(PARAM(lambda: stock, "copy-80"))                            # noqa: F821
if gores not in (12, 24):
    raise ValueError(f"paper-globe: gores must be 12 or 24, got {gores}")
if band not in (6.0, 7.5, 9.0, 10.0, 12.0, 15.0):
    raise ValueError(f"paper-globe: band must divide 180° evenly (6, 7.5, 9, 10, 12 or 15), "
                     f"got {band:g}")
if pattern not in PATTERNS:
    raise ValueError(f"paper-globe: pattern must be one of {tuple(PATTERNS)}, got {pattern!r}")
if stock not in STOCKS:
    raise ValueError(f"paper-globe: stock must be one of {tuple(STOCKS)}, got {stock!r}")

rho = diameter / 2.0
G = gores
K = int(round(180.0 / band))                     # latitude bands per gore
lat = [math.radians(-90.0 + i * band) for i in range(K + 1)]
chord = [2.0 * rho * math.cos(p) * math.sin(math.pi / G) for p in lat]
chord[0] = chord[-1] = 0.0                       # the poles
slant = 2.0 * rho * math.sin(math.radians(band) / 2.0)
xs = [0.0]
for i in range(K):
    half = (chord[i + 1] - chord[i]) / 2.0
    xs.append(xs[-1] + math.sqrt(slant * slant - half * half))
H = max(chord)                                    # the gore's widest chord (at the equator)
render_vertices = G * (2 * 3 + 4 * (K - 2))
if render_vertices > 2400:
    raise ValueError(f"paper-globe: {G} gores × {K} bands make {render_vertices} render "
                     "vertices; use wider bands")

# flat gore, lying along +u: south pole at u = 0, north pole at u = xs[K], centreline v = H/2
upper = [(xs[i], H / 2.0 + chord[i] / 2.0) for i in range(1, K)]
lower = [(xs[i], H / 2.0 - chord[i] / 2.0) for i in range(1, K)]
outline = [(0.0, H / 2.0)] + lower + [(xs[K], H / 2.0)] + list(reversed(upper))


def gore_sheet(g):
    colours = PATTERNS[pattern]
    s = pliego.Sheet(f"gore-{g + 1}", outline, stock=stock, grain_deg=0.0,
                     label=L4(f"Gore {g + 1}", f"Huso {g + 1}", f"Fuseau {g + 1}",
                              f"Fuso {g + 1}"),
                     front=colours[g % len(colours)], back="#f6f1e7")
    for i in range(1, K):
        s.bend(lower[i - 1], upper[i - 1], name="equator" if 2 * i == K else None)
    return s


# ── the polyhedral globe: corner (band i, side ±) of gore g, centre at height rho ──
def corner(g, i, side):
    lon = -2.0 * math.pi * (g + 0.5 * (1 + side)) / G     # side −1: west edge, +1: east edge
    phi = lat[i]
    return (rho * math.cos(phi) * math.cos(lon), rho + rho * math.sin(phi),
            rho * math.cos(phi) * math.sin(lon))


def sub3(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def unit(a):
    n = math.sqrt(a[0] ** 2 + a[1] ** 2 + a[2] ** 2)
    return (a[0] / n, a[1] / n, a[2] / n)


def frame(a, b, c):
    e1 = unit(sub3(b, a))
    e3 = unit(cross(e1, sub3(c, a)))
    return a, e1, cross(e3, e1), e3


def panel_corners(i):
    """Flat (u, v) and the matching 3-D corner keys of panel i (a triangle at the poles)."""
    if i == 0:
        return [(0.0, H / 2.0), lower[0], upper[0]], [(0, 0), (1, 1), (1, -1)]
    if i == K - 1:
        return [lower[K - 2], (xs[K], H / 2.0), upper[K - 2]], [(K - 1, 1), (K, 0), (K - 1, -1)]
    return [lower[i - 1], lower[i], upper[i]], [(i, 1), (i + 1, 1), (i + 1, -1)]


def globe(sheet_id, uv):
    g = int(sheet_id.split("-")[1]) - 1
    u, v = uv
    i = min(max(int(sum(1 for x in xs[1:K] if u > x + 1e-9)), 0), K - 1)
    flat, keys = panel_corners(i)
    pts = [corner(g, k, s) if s else corner(g, k, 1) for k, s in keys]
    fo, f1, f2, _ = frame(*[(p[0], p[1], 0.0) for p in flat])
    wo, w1, w2, w3 = frame(*pts)
    d = (u - fo[0], v - fo[1], 0.0)
    a_, b_ = d[0] * f1[0] + d[1] * f1[1], d[0] * f2[0] + d[1] * f2[1]
    return tuple(wo[k] + a_ * w1[k] + b_ * w2[k] for k in range(3))


sheets = [gore_sheet(g) for g in range(G)]
cut_check = pliego.papercut.analyze(sheets[0], min_feature_mm=STOCKS[stock])
if not cut_check.ok:
    raise ValueError(f"paper-globe: the gore fails the papercut check: {cut_check.issues}")
arr = sheets[0].build()


def newell(pts):
    n = [0.0, 0.0, 0.0]
    for k, p in enumerate(pts):
        q = pts[(k + 1) % len(pts)]
        n[0] += (p[1] - q[1]) * (p[2] + q[2])
        n[1] += (p[2] - q[2]) * (p[0] + q[0])
        n[2] += (p[0] - q[0]) * (p[1] + q[1])
    return unit(n)


def fold_angles(sheet_id):
    """Signed fold angle (FOLD convention, deg) of every interior F/M/V edge of one gore."""
    pts = [globe(sheet_id, (vx.x, vx.y)) for vx in arr.vertices]
    left = {}
    for fi, f in enumerate(arr.faces):
        for k in range(len(f)):
            left[(f[k], f[(k + 1) % len(f)])] = fi
    normals = [newell([pts[v] for v in f]) for f in arr.faces]
    out = {}
    for e, (a, b) in enumerate(arr.edges):
        if arr.assignment[e] in ("F", "M", "V") and (a, b) in left and (b, a) in left:
            out[e] = pliego.tessellate.signed_fold_angle(normals[left[(a, b)]],
                                                         normals[left[(b, a)]], sub3(pts[b],
                                                                                     pts[a]))
    return out


angles = fold_angles("gore-1")      # every gore bends alike (the globe is symmetric)
if max(angles.values()) >= 0.0:
    raise ValueError("paper-globe: the gores must bend printed side out (mountain)")

# self-checks: the pose is an isometry, and the east edge (v < H/2) of gore g meets the west
# edge (v > H/2) of gore g + 1
for e, (a, b) in enumerate(arr.edges):
    pa, pb = arr.vertices[a], arr.vertices[b]
    d3 = math.dist(globe("gore-1", (pa.x, pa.y)), globe("gore-1", (pb.x, pb.y)))
    if abs(d3 - math.dist((pa.x, pa.y), (pb.x, pb.y))) > 1e-6:
        raise ValueError(f"paper-globe: edge {e} stretches in the assembled globe")
seam = max(math.dist(globe("gore-1", lower[i - 1]), globe("gore-2", upper[i - 1]))
           for i in range(1, K))
if seam > 1e-6:
    raise ValueError(f"paper-globe: neighbouring gores miss each other by {seam} mm")


def quaternion(c1, c2, c3):
    """Unit quaternion (x, y, z, w) of the rotation whose matrix columns are c1, c2, c3."""
    m00, m11, m22 = c1[0], c2[1], c3[2]
    tr = m00 + m11 + m22
    if tr > 0.0:
        s = 2.0 * math.sqrt(tr + 1.0)
        return ((c2[2] - c3[1]) / s, (c3[0] - c1[2]) / s, (c1[1] - c2[0]) / s, s / 4.0)
    if m00 >= m11 and m00 >= m22:
        s = 2.0 * math.sqrt(1.0 + m00 - m11 - m22)
        return (s / 4.0, (c2[0] + c1[1]) / s, (c3[0] + c1[2]) / s, (c2[2] - c3[1]) / s)
    if m11 >= m22:
        s = 2.0 * math.sqrt(1.0 + m11 - m00 - m22)
        return ((c2[0] + c1[1]) / s, s / 4.0, (c3[1] + c2[2]) / s, (c3[0] - c1[2]) / s)
    s = 2.0 * math.sqrt(1.0 + m22 - m00 - m11)
    return ((c3[0] + c1[2]) / s, (c3[1] + c2[2]) / s, s / 4.0, (c1[1] - c2[0]) / s)


# place each gore so its south-pole triangle (face 0) is where the globe needs it
f0 = [arr.vertices[v] for v in arr.faces[0]]
for g, s in enumerate(sheets):
    flat3 = [(p.x, 0.0, -p.y) for p in f0]                      # un-placed sheet frame
    world = [globe(s.id, (p.x, p.y)) for p in f0]
    ao, a1, a2, a3 = frame(*flat3)
    bo, b1, b2, b3 = frame(*world)
    # rotation R = B · Aᵀ (columns), then origin = bo − R·ao
    cols = []
    for k in range(3):
        ek = [1.0 if j == k else 0.0 for j in range(3)]
        local = (ek[0] * a1[0] + ek[1] * a1[1] + ek[2] * a1[2],
                 ek[0] * a2[0] + ek[1] * a2[1] + ek[2] * a2[2],
                 ek[0] * a3[0] + ek[1] * a3[1] + ek[2] * a3[2])
        cols.append(tuple(local[0] * b1[j] + local[1] * b2[j] + local[2] * b3[j]
                          for j in range(3)))
    ra = tuple(sum(cols[k][j] * ao[k] for k in range(3)) for j in range(3))
    s.placement = pliego.Placement(origin=tuple(bo[j] - ra[j] for j in range(3)),
                                   rotation=quaternion(*cols))

params = {"gores": G, "diameter": diameter, "band": band, "pattern": pattern, "stock": stock}
print(f"paper-globe: gores={G} bands={K} gore={xs[K]:.1f}x{H:.1f}mm (sphere meridian "
      f"{math.pi * rho:.1f}mm) render_vertices={render_vertices} "
      f"polyhedron_vs_sphere_equator={G * chord[K // 2] / (math.pi * diameter):.4f}")


def ref(s, e):
    return pliego.assembly.EdgeRef(s, e)


steps = [
    pliego.Step("bend", L4("Bend every gore along its length, printed side out",
                           "Curva cada huso a lo largo, con el lado impreso hacia fuera",
                           "Courbez chaque fuseau sur sa longueur, face imprimée à l'extérieur",
                           "Curve cada fuso ao longo do comprimento, com o lado impresso para "
                           "fora"),
                [(ref(s, e), 0.5 * a) for s in sheets for e, a in angles.items()],
                duration_ms=3000),
    pliego.Step("close", L4("Close the globe: each gore meets its neighbours edge to edge",
                            "Cierra el globo: cada huso se junta con sus vecinos orilla con "
                            "orilla", "Fermez le globe : chaque fuseau rejoint ses voisins bord "
                            "à bord", "Feche o globo: cada fuso encontra os vizinhos borda com "
                            "borda"),
                [(ref(s, e), a) for s in sheets for e, a in angles.items()], duration_ms=3000,
                note=L4("On a real globe the gores are pasted onto a ball.",
                        "En un globo de verdad los husos se pegan sobre una esfera.",
                        "Sur un vrai globe, les fuseaux sont collés sur une sphère.",
                        "Num globo de verdade, os fusos são colados sobre uma esfera.")),
]
assembly = pliego.Assembly(
    sheets, controls=[pliego.sequence_control(label=L4("Close the globe", "Cerrar el globo",
                                                       "Fermer le globe", "Fechar o globo"))],
    sequence=pliego.Sequence(steps, mode="kinematic"),
    targets={"globe": {s.id: {"angles": dict(angles)} for s in sheets}}, title="Paper globe")

doc = assembly.build(cartridge=SLUG, mode=str(PARAM(lambda: mode, "globe")),  # noqa: F821
                     params=params)
result = doc.stamp()
