"""Kresling tower — sheet-hyperobjects cartridge (Pliego).

A strip of sheared triangles rolled into a polygonal tube: each storey is a ring of `sides`
parallelograms split by their long diagonals. Pushed down and twisted, the tower snaps from tall
to flat; pulled and untwisted, it snaps back. It is bistable, and it is not a mechanism.

The crease pattern comes from the kernel (`pliego.tessellate.kresling`); this script chooses its
proportions so that the tower has two stable states with every panel exactly flat and every
crease at its flat length — a tall one and one folded completely flat — and computes both in
closed form.

**The two states.** Model a storey as two rigid regular n-gons (side `width`, circumradius
R = width / (2 sin(π/n))) turned by φ and stacked at height H. The side crease (length a) joins
vertex k of one ring to vertex k of the next, the diagonal (length b) joins vertex k to vertex
k + 1:

    a² = 2R²(1 − cos φ) + H²,        b² = 2R²(1 − cos(φ + 2π/n)) + H²

Subtracting gives sin(φ + π/n) = const, whose two roots are φ and π − 2π/n − φ. Choosing the
flat state (H = 0) at φ₀ = π − 2π/n − φ₁ fixes a and b, and then the tall state at the deployed
twist φ₁ has H₁² = 2R²(cos φ₁ − cos φ₀). The flat strip follows from a, b and width.

**Why tier R reports 0 DOF.** Those two roots are the only states of the symmetric tower in
which no panel or crease line is strained. They are isolated points, not ends of a path, so
the rigid-origami solver has no motion to follow: zero rigid degrees of freedom. Between them,
holding the rings and side creases at their lengths, the diagonals must change length; the
script prints the largest strain on the way. Snapping through that strain barrier is the
bistability, and simulating it needs the compliant (tier C) engine, so the program is physical.
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


sides = int(clamp(PARAM(lambda: sides, 6), 4, 10))
storeys = int(clamp(PARAM(lambda: storeys, 3), 1, 6))
width = clamp(PARAM(lambda: width, 30.0), 15.0, 50.0)
# The tall state needs φ₁ < φ₀ (twist below 90° − 180°/n); the kernel's strip needs a shear below
# the panel width, which works out to sin(π/n + φ₁) < 3·sin(π/n) (binding only for n = 10).
max_twist = 90.0 - 180.0 / sides
if 3.0 * math.sin(math.pi / sides) < 1.0:
    max_twist = min(max_twist, math.degrees(math.asin(3.0 * math.sin(math.pi / sides)))
                    - 180.0 / sides)
twist = clamp(PARAM(lambda: twist, 40.0), 5.0, max_twist - 5.0)
stock = str(PARAM(lambda: stock, "kami"))
if stock not in ("kami", "copy-80", "washi-kozo-30", "tant"):
    raise ValueError(f"stock {stock!r} is not one this cartridge offers")

n = sides
R = width / (2.0 * math.sin(math.pi / n))
phi1 = math.radians(twist)                       # deployed (tall) twist per storey
phi0 = math.pi - 2.0 * math.pi / n - phi1        # folded (flat) twist per storey
H1 = math.sqrt(2.0 * R * R * (math.cos(phi1) - math.cos(phi0)))
a2 = 2.0 * R * R * (1.0 - math.cos(phi0))
b2 = 2.0 * R * R * (1.0 - math.cos(phi0 + 2.0 * math.pi / n))
shear = (b2 - a2 - width * width) / (2.0 * width)
height = math.sqrt(a2 - shear * shear)
if not 0.0 <= shear < width:
    raise ValueError(f"kresling-tower: twist {twist:.1f}° gives a shear of {shear:.1f} mm, outside "
                     f"[0, {width:.1f})")

tess = pliego.tessellate.kresling(n, storeys, width, height, shear, stock,
                                  sheet_id="kresling")
sheet = tess.sheet
sheet.label = L4("Kresling strip", "Tira Kresling", "Bande de Kresling", "Tira Kresling")
groups = tess.groups
arr = sheet.build()


def sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def newell(pts):
    nx = ny = nz = 0.0
    for i, p in enumerate(pts):
        q = pts[(i + 1) % len(pts)]
        nx += (p[1] - q[1]) * (p[2] + q[2])
        ny += (p[2] - q[2]) * (p[0] + q[0])
        nz += (p[0] - q[0]) * (p[1] + q[1])
    m = math.sqrt(nx * nx + ny * ny + nz * nz)
    return (nx / m, ny / m, nz / m)


def fold_angles(world):
    """Signed fold angle (deg, valley > 0) of every M/V edge in a 3-D state of the sheet; a crease
    folded flat (±180°) takes the sign of its assignment."""
    verts = arr.vertices
    half = {}
    for fi, f in enumerate(arr.faces):
        for i in range(len(f)):
            half[(f[i], f[(i + 1) % len(f)])] = fi
    normals = []
    for f in arr.faces:
        flat = newell([(verts[v].x, 0.0, -verts[v].y) for v in f])
        nrm = newell([world[v] for v in f])
        normals.append(nrm if flat[1] > 0 else (-nrm[0], -nrm[1], -nrm[2]))
    out = {}
    for e, (a, b) in enumerate(arr.edges):
        if arr.assignment[e] in ("M", "V"):
            rho = pliego.tessellate.signed_fold_angle(normals[half[(a, b)]], normals[half[(b, a)]],
                                                      sub(world[b], world[a]))
            if abs(abs(rho) - 180.0) < 1e-4:
                rho = 180.0 if arr.assignment[e] == "V" else -180.0
            out[e] = rho
    return out


def tower(phi, H, mirror):
    """(sheet_id, (u, v)) → world point of the rolled tower; strip vertex (k, j) sits at
    (k·width + j·shear, j·height) and goes to ring j's vertex k, turned by j·φ, at height j·H."""
    def at(_sid, uv):
        j = round(uv[1] / height)
        k = round((uv[0] - j * shear) / width)
        theta = 2.0 * math.pi * k / n + j * phi
        return (R * math.cos(theta), j * H, mirror * R * math.sin(theta))
    return at


for mirror in (1.0, -1.0):
    tall = fold_angles([tower(phi1, H1, mirror)("", (p.x, p.y)) for p in arr.vertices])
    if all((tall[e] > 0) == (arr.assignment[e] == "V") for e in tall):
        break
else:
    raise ValueError("kresling-tower: the rolled tower disagrees with the assignment")
flat = fold_angles([tower(phi0, 0.0, mirror)("", (p.x, p.y)) for p in arr.vertices])
worst = max(pliego.kinematics.closure_residual(arr, tall),
            pliego.kinematics.closure_residual(arr, flat))
if worst > 1e-5:
    raise ValueError(f"kresling-tower: a stable state does not close ({worst:.3g} mm)")

# The strain barrier: rings and side creases rigid, diagonals free to change length.
b = math.sqrt(b2)
barrier = 0.0
for i in range(1, 200):
    H = H1 * i / 200.0
    c = 1.0 - (a2 - H * H) / (2.0 * R * R)
    phi = math.acos(max(-1.0, min(1.0, c)))
    bh = math.sqrt(2.0 * R * R * (1.0 - math.cos(phi + 2.0 * math.pi / n)) + H * H)
    barrier = max(barrier, abs(bh / b - 1.0))


def rho(state, group):
    return sorted({round(state[e], 3) for m in groups[group] for e in m.edges()})


print(f"kinematics: kresling n={n} storeys={storeys} R={R:.3f}mm deployed twist={twist:.2f}° "
      f"H={H1:.3f}mm folded twist={math.degrees(phi0):.2f}° H=0 rigid_states=2 (isolated) "
      f"tier_R_dof=0 truss_model_peak_diagonal_strain={100 * barrier:.2f}% "
      f"max_closure_mm={worst:.1e}")
print(f"kinematics: deployed rings={rho(tall, 'rings')} sides={rho(tall, 'sides')} "
      f"diagonals={rho(tall, 'diagonals')}")


def state(angles, f=1.0):
    return [(pliego.assembly.EdgeRef(sheet, e), angles[e] * f) for e in sorted(angles)]


SNAP = L4(f"Between the two states the diagonals must stretch by up to {100 * barrier:.1f}%: "
          "the paper resists, then snaps through.",
          f"Entre los dos estados las diagonales tienen que estirarse hasta un "
          f"{100 * barrier:.1f} %: el papel se resiste y luego salta.",
          f"Entre les deux états, les diagonales doivent s'allonger jusqu'à "
          f"{100 * barrier:.1f} % : le papier résiste, puis bascule d'un coup.",
          f"Entre os dois estados as diagonais precisam esticar até {100 * barrier:.1f}%: o "
          "papel resiste e depois salta.")
TALL = L4(f"Tall stable state: twist {twist:.1f}° and height {H1:.1f} mm per storey.",
          f"Estado estable alto: giro de {twist:.1f}° y altura de {H1:.1f} mm por piso.",
          f"État stable haut : rotation de {twist:.1f}° et hauteur de {H1:.1f} mm par étage.",
          f"Estado estável alto: giro de {twist:.1f}° e altura de {H1:.1f} mm por andar.")
steps = [
    pliego.Step("fold-strip",
                L4("Fold the strip: diagonals as valleys, sides and rings as mountains",
                   "Pliega la tira: diagonales en valle, lados y anillos en monte",
                   "Plier la bande : diagonales en vallée, côtés et anneaux en montagne",
                   "Dobre a tira: diagonais em vale, lados e anéis em montanha"),
                state(tall, 0.5), duration_ms=2500),
    pliego.Step("close-tower",
                L4("Roll it into a tube and close the seam: the tall tower",
                   "Enróllala en un tubo y cierra la costura: la torre alta",
                   "La rouler en tube et fermer la jointure : la tour haute",
                   "Enrole-a num tubo e feche a emenda: a torre alta"),
                state(tall), duration_ms=2500, note=TALL),
    pliego.Step("twist-down",
                L4("Push down and twist: the tower snaps flat",
                   "Empuja hacia abajo y gira: la torre se aplana de golpe",
                   "Pousser et tourner : la tour s'aplatit d'un coup",
                   "Empurre para baixo e gire: a torre achata-se de repente"),
                state(flat), duration_ms=2000, note=SNAP),
    pliego.Step("pull-up",
                L4("Pull up and untwist: it snaps back to the tall state",
                   "Tira hacia arriba y gira al revés: vuelve de golpe al estado alto",
                   "Tirer et détourner : elle revient d'un coup à l'état haut",
                   "Puxe para cima e gire ao contrário: volta de repente ao estado alto"),
                state(tall), duration_ms=2000, note=TALL),
]

result = pliego.Assembly(
    [sheet],
    controls=[pliego.sequence_control(label=L4("Fold program", "Secuencia de pliegues",
                                               "Séquence de pliage", "Sequência de dobras"))],
    sequence=pliego.Sequence(steps, mode="physical"),
    targets={"deployed": tower(phi1, H1, mirror), "flat-folded": tower(phi0, 0.0, mirror)},
    title="Kresling tower",
)
