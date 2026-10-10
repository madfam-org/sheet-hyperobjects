# Yoshimura pattern

| | Title | Summary |
|---|---|---|
| en | Yoshimura pattern | The diamond pattern a crushed thin cylinder buckles into, folded on purpose. The sheet curls rigidly until its rings close into regular polygons, an exact tube; squashing the closed tube needs the paper to bend. |
| es | Patrón Yoshimura | El patrón de rombos en el que se pandea un cilindro delgado al aplastarlo, plegado a propósito. La hoja se enrolla de forma rígida hasta que sus anillos se cierran en polígonos regulares, un tubo exacto; para aplastar el tubo cerrado, el papel tiene que curvarse. |
| fr | Motif de Yoshimura | Le motif de losanges que prend un cylindre mince écrasé, plié volontairement. La feuille s'enroule de façon rigide jusqu'à ce que ses anneaux se referment en polygones réguliers, un tube exact ; pour écraser le tube fermé, le papier doit se courber. |
| pt | Padrão Yoshimura | O padrão de losangos em que um cilindro fino esmagado flamba, dobrado de propósito. A folha enrola-se de forma rígida até os anéis se fecharem em polígonos regulares, um tubo exato; para esmagar o tubo fechado, o papel precisa curvar-se. |

## What it is

Press a thin-walled cylinder along its axis, an aluminium can or a paper tube, and it
collapses into a ring of diamonds. Yoshimaru Yoshimura analysed this pattern in 1951, and the
crease pattern that produces it on purpose carries his name. The sheet is a strip of triangles:

- horizontal **valley rings** run along the strip;
- **mountain diagonals** zigzag between the rings;
- every interior vertex has degree six (two ring segments and four diagonals).

Rolled into a tube, each ring becomes a polygon and each band of triangles a ring of diamonds.
The `sides` parameter sets how many diamonds go round the tube and `rings` how many bands go up
it. The crease pattern comes from the kernel's generator `pliego.tessellate.yoshimura`.

## Geometry

**The flat sheet.** The strip is `sides × width` long and `rings × height` tall. Each band holds
triangles with base `width` and height `height`; the diagonals have length
`L = √((width/2)² + height²)`. Neighbouring rings are offset by half a triangle. At every vertex
the sectors are β, 180° − 2β, β, β, 180° − 2β, β, where β is the angle between a diagonal and
the ring. The alternate sums are 180°, so the pattern is flat-foldable at every vertex.

**The rolled tube.** The cartridge computes the tube in closed form:

- ring `j` becomes a planar regular polygon with `n = sides` edges of length `width`, so its
  circumradius is `R = width / (2 sin(π/n))`;
- consecutive rings are turned by `π/n` against each other, so each diagonal joins a vertex of
  one ring to the nearest vertex of the next;
- the rings are stacked at the spacing that keeps every diagonal at its flat length `L`:

      Δz² = L² − 2R²(1 − cos(π/n)) = height² − (width/2)² · tan²(π/(2n))

The tube therefore exists only when `height > (width/2) · tan(π/(2n))`; the script refuses
shorter bands and names the limit.

**The rigid path to the tube.** The open sheet gets there without bending a single panel. Every
vertex can fold the same way. Let β be the angle between a diagonal and its ring
(`tan β = 2·height/width`), and τ the angle by which the two ring rays drop out of the sheet's
plane. The six rays of a vertex are then

    H± = (±cos τ, −sin τ, 0)
    D  = (±cos β, −cos β · tan(τ/2), ±√(sin²β − cos²β · tan²(τ/2)))

Each diagonal keeps its sectors β and 180° − 2β, so every state is rigid. Each ring turns by 2τ
at every vertex, which is why the sheet **curls as it folds**. The rings close into n-gons at
`τ = 180°/n`, and that state is exactly the closed-form tube above. The script checks the loop
closure of the whole sheet at every step and checks that the last step equals the closed form.

**Why squashing the tube needs bending.** Once the seam is closed, the rings must stay closed
n-gons, so τ is fixed at 180°/n. The tube is then the only uniform rigid state left: an isolated
rigid state, not a mechanism. Pushing it shorter means bending the panels, which is why the
pattern is the post-buckling shape of a crushed cylinder.

The script reads every fold angle off the closed-form vertices as a signed dihedral. It then
checks five things and fails loud if one is false:

- the angles agree with the assignment (rings valley, diagonals mountain, front face outside);
- every ring crease shares one angle and every diagonal another;
- the loops close (`pliego.kinematics.closure_residual`);
- the two ends of the strip meet at the seam;
- the rigid path arrives at the closed form.

With the defaults it prints:

    kinematics: tube n=6 rings=4 R=30.000mm dz=19.592mm rho_ring=23.1864 rho_diag=37.7523 max_closure_mm=1.19e-13 seam_gap_mm=8.13e-14 (the only closed uniform state: squashing further needs bending)
    kinematics: rigid path flat->tube steps=6 tau_end=30.000° max_closure_mm=1.21e-13 gap_to_closed_form_deg=8.2e-14

## The fold program

The program is `kinematic`, with six exact rigid steps along the path above, from τ = 0 to
τ = 180°/n:

1. **Steps 1–5: fold the diamonds.** The sheet curls; each step's note gives τ and how far each
   ring has turned.
2. **Step 6: the rings close.** This is the exact tube. The note prints `R`, `Δz` and the two
   fold angles.

The document also carries a `target:tube` frame, the closed-form tube itself.

**What the preview shows and what needs the physics engine.** The studio preview poses the faces
along a spanning tree, and every step is a rigid state. The preview therefore shows the true
motion: the flat strip curls up, and at the last step the seam meets and every ring is a regular
polygon. Two things need the physics engine (tier C): squashing the closed tube below its rigid
height, and the snap-through of a real cylinder buckling into this pattern.

## Making one by hand

1. Plot or print the strip (SVG, PDF, DXF or HPGL). Add a 10 mm glue tab on one short end, or
   plan to close the seam with tape; the tab is not modelled.
2. Score every line.
3. Fold every ring as a valley and every diagonal as a mountain, and press each one firmly.
4. Fold all the creases further together, a little at a time. The strip curls by itself, as in
   the program. Bring the two ends together so that their half-triangles meet, then glue or tape
   the seam.
5. Push the tube gently along its axis. The diamonds pop in together, and the tube settles at the
   height computed above.

Thin paper (kami, kozo washi) makes it easiest to watch the diamonds snap through.

## Parameters

| Parameter | Meaning |
|---|---|
| `sides` | diamonds round the tube, n (4–12) |
| `rings` | bands of triangles up the tube (2–10) |
| `width` | triangle base = ring polygon side, mm |
| `height` | band height on the flat sheet, mm |
| `stock` | kami, copy paper, kozo washi or tant |

Presets: `square-tube` (4 sides, 5 rings, 40 × 25 mm) and `fine` (12 sides, 8 rings,
20 × 12 mm).

## History and sources

Yoshimura studied the post-buckling pattern of thin cylinders under axial load. It also appears
in folded engineering structures and in collapsible tubes, where it is contrasted with the
twisting (Kresling) pattern.

- Y. Yoshimura, *On the mechanism of buckling of a circular cylindrical shell under axial
  compression*, NACA Technical Memorandum 1390 (1955); translated from a 1951 report of the
  Institute of Science and Technology, University of Tokyo.
- G. W. Hunt and I. Ario, "Twist buckling and the foldable cylinder: an exercise in origami",
  *International Journal of Non-Linear Mechanics* 40 (2005) 833–843. The diamond (Yoshimura) and
  twist (Kresling) modes of a foldable cylinder.

## Provenance and licence

Original MADFAM work. The crease pattern is generated by the Pliego kernel; the rolled tube and
its fold angles are computed in closed form by this cartridge's `main.py`. No published crease
pattern is copied. Licence: CERN-OHL-W-2.0 (the commons' root licence).
