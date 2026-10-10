# Kresling tower

| | Title | Summary |
|---|---|---|
| en | Kresling tower | A strip of sheared triangles rolled into a polygonal tower that snaps between two stable states, tall and folded flat. Both are exact; between them the paper must stretch, so the tower has no rigid motion. |
| es | Torre Kresling | Una tira de triángulos sesgados enrollada en una torre poligonal que salta entre dos estados estables, alta y plegada en plano. Los dos son exactos; entre ellos el papel tiene que estirarse, así que la torre no tiene movimiento rígido. |
| fr | Tour de Kresling | Une bande de triangles cisaillés roulée en une tour polygonale qui bascule entre deux états stables, haute et repliée à plat. Les deux sont exacts ; entre eux, le papier doit s'étirer, si bien que la tour n'a aucun mouvement rigide. |
| pt | Torre Kresling | Uma tira de triângulos inclinados enrolada numa torre poligonal que salta entre dois estados estáveis, alta e dobrada rente. Os dois são exatos; entre eles o papel precisa esticar, por isso a torre não tem movimento rígido. |

## What it is

Twist a thin paper cylinder while you crush it and it buckles into a spiral of triangles instead
of the diamonds of the Yoshimura pattern. Biruta Kresling studied this twist-buckling pattern
and showed how to fold it on purpose. The result is a tower that you push down and twist until
it **snaps flat**, then pull and untwist until it **snaps back up**. In between it pushes back:
the tower is bistable.

The sheet is a strip of `sides × storeys` parallelograms, each split along its long diagonal:

- the diagonals are **valleys**;
- the short sides and the storey lines are **mountains**.

The strip comes from the kernel's generator `pliego.tessellate.kresling`. This cartridge chooses
its proportions so that the tower has exactly two strain-free states, and computes both.

## Geometry

**The tower model.** Each storey is two rigid regular polygons, with `n = sides` edges of length
`width` and circumradius `R = width / (2 sin(π/n))`. The upper polygon is turned by φ against the
lower one and sits at height H above it. The side crease (length `a`) joins vertex k of one ring
to vertex k of the next; the diagonal (length `b`) joins vertex k to vertex k + 1:

    a² = 2R²(1 − cos φ) + H²
    b² = 2R²(1 − cos(φ + 2π/n)) + H²

**Two states.** Subtracting the two equations eliminates H and leaves `sin(φ + π/n)` equal to a
constant. That equation has two roots, φ and π − 2π/n − φ. The cartridge puts one root at
H = 0, the **flat-folded** state, with twist `φ₀ = π − 2π/n − φ₁`. The other root is the **tall**
state at the twist you choose, `φ₁` (the `twist` parameter). Its height follows as

    H₁² = 2R²(cos φ₁ − cos φ₀)

so φ₁ must stay below 90° − 180°/n. The lengths `a` and `b` come from the flat state, and the
strip's shear and panel height follow from `a`, `b` and `width`. The kernel needs the shear to
stay below the panel width, which caps the twist for ten-sided towers.

**Why tier R reports 0 DOF.** In those two states every triangle is flat and every crease line
has its flat length. They are the *only* such states of the symmetric tower, and they are
isolated points: no path of strain-free states joins them. A rigid-origami solver (tier R)
therefore has nothing to follow, and the tower has zero rigid degrees of freedom. To get from one
state to the other, something must change length. Hold the rings and the side creases rigid and
let the diagonals give, and the diagonals must stretch on the way. The script prints the largest
such strain:

    kinematics: kresling n=6 storeys=3 R=30.000mm deployed twist=40.00° H=32.654mm folded twist=80.00° H=0 rigid_states=2 (isolated) tier_R_dof=0 truss_model_peak_diagonal_strain=1.69% max_closure_mm=3.0e-06

That strain barrier is the bistability: the paper resists, then snaps through. Real paper also
bends its triangular panels a little, which lowers the barrier. The truss figure is
therefore an upper estimate of how hard the snap is. A smaller twist gives a taller tower and a
harder snap.

The kernel's motion solver closes loops round interior vertices only. The loop round the tube
appears only once the seam is glued, so it cannot be posed to the solver directly. That is why
the cartridge derives the 0-DOF result in closed form for the closed, symmetric tower, rather than
asking the solver.

Both states are read off as signed fold angles; creases folded flat take their assignment's sign.
The script checks them against the assignment and checks loop closure. Both states also ship as
target frames, `target:deployed` and `target:flat-folded`.

## The fold program

The program is `physical`, with four steps:

1. **Fold the strip.** Every crease goes to half its tall-state angle.
2. **Roll it into a tube and close the seam.** Every crease goes to its exact tall-state angle.
3. **Push down and twist.** The tower goes to the exact flat-folded state. The note gives the
   strain barrier.
4. **Pull up and untwist.** The tower returns to the tall state.

**What the preview shows and what needs the physics engine.** The studio preview poses the faces
along a spanning tree. Steps 2, 3 and 4 end in exact states, so the tall tower closes, the
flat-folded tower closes and the seam meets. Between those states the face tree simply blends the
fold angles, which no strain-free state matches, so seams open. The snap itself is the stretching
of the paper and its sudden release. The physics engine (tier C) simulates it, together with the
force you feel.

## Making one by hand

1. Plot or print the strip (SVG, PDF, DXF or HPGL). Leave a 10 mm glue tab past the last
   parallelogram, or close the seam with tape; the tab is not modelled.
2. Score every line. Fold the diagonals as valleys and the sides and storey lines as mountains.
   Press each crease hard.
3. Roll the strip so that its two slanted ends meet, and glue or tape the seam.
4. Hold the tower between your palms. Push down and twist in the direction the triangles lean,
   and it collapses flat with a click. Pull and untwist, and it springs back up.

Thin paper (kami, kozo washi) snaps easily. With copy paper, crease harder and expect a stiffer
snap.

## Parameters

| Parameter | Meaning |
|---|---|
| `sides` | sides of the ring polygon, n (4–10) |
| `storeys` | storeys of the tower (1–6) |
| `width` | polygon side, mm |
| `twist` | twist per storey in the tall state, degrees; clamped below 90° − 180°/n − 5° (and lower for n = 10) |
| `stock` | kami, copy paper, kozo washi or tant |

Presets: `square-tower` (4 sides, 4 storeys, twist 25°) and `octagonal-tower` (8 sides,
4 storeys, twist 48°, a gentle snap).

## History and sources

- B. Kresling, "Natural twist buckling in shells: from the hawkmoth's bellies to the deployable
  Kresling-pattern and cylindrical Miura-ori", *Proceedings of the 6th International Conference
  on Computation of Shell and Spatial Structures* (IASS-IACM, 2008).
- S. D. Guest and S. Pellegrino, "The folding of triangulated cylinders, Part I: geometric
  considerations", *Journal of Applied Mechanics* 61 (1994) 773–777. The geometry of
  twist-folding triangulated tubes.
- G. W. Hunt and I. Ario, "Twist buckling and the foldable cylinder: an exercise in origami",
  *International Journal of Non-Linear Mechanics* 40 (2005) 833–843.
- J. Cai, X. Deng, Y. Zhou, J. Feng and Y. Tu, "Bistable behavior of the cylindrical origami
  structure with Kresling pattern", *Journal of Mechanical Design* 137 (2015) 061406. The truss
  model of the snap used above.

## Provenance and licence

Original MADFAM work. The crease pattern is generated by the Pliego kernel; the proportions and
both stable states are computed in closed form by this cartridge's `main.py`. No published crease
pattern is copied. Licence: CERN-OHL-W-2.0 (the commons' root licence).
