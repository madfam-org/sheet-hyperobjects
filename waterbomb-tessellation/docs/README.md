# Waterbomb tessellation

| | Title | Summary |
|---|---|---|
| en | Waterbomb tessellation | A grid of the generic waterbomb cell in which every vertex is a waterbomb base. Folded symmetrically it curls rigidly and closes into an exact tube; pressed flat, every cell becomes a flat waterbomb base. |
| es | Teselado de bomba de agua | Una cuadrícula de la celda genérica de bomba de agua en la que cada vértice es una base de bomba de agua. Plegada de forma simétrica se enrolla rígidamente y se cierra en un tubo exacto; aplanada, cada celda se vuelve una base de bomba de agua plana. |
| fr | Pavage de la bombe à eau | Une grille de la cellule générique de la bombe à eau dont chaque sommet est une base de la bombe à eau. Pliée symétriquement, elle s'enroule de façon rigide et se ferme en un tube exact ; aplatie, chaque cellule devient une base de la bombe à eau à plat. |
| pt | Tesselação da bomba d'água | Uma grade da célula genérica da bomba d'água em que cada vértice é uma base da bomba d'água. Dobrada de forma simétrica, enrola-se rigidamente e fecha-se num tubo exato; achatada, cada célula torna-se uma base da bomba d'água plana. |

## What it is

The waterbomb base is one of the traditional origami bases: a square with both diagonals folded
one way and the line through its centre folded the other. Repeat that cell on a grid and you get
a sheet in which **every** vertex, at cell corners and at cell centres alike, is a waterbomb
base. Folded, the grid curls up on its own. This cartridge has two modes:

| Mode | What you get | Program |
|---|---|---|
| `tube` | the grid curls rigidly and closes into a tube, `columns` cells round | kinematic, exact at every step |
| `flat` | the grid pressed flat, every cell a flat waterbomb base | physical; one exact rigid step, then the exact flat-folded state |

The grid comes from the kernel's generator `pliego.tessellate.waterbomb`: diagonals are mountains,
centre lines are valleys, and rows are in register. **Only the generic waterbomb cell is used.**
The offset-row arrangement behind some well-known waterbomb balls is not modelled.

## Geometry

**One vertex.** Every interior vertex has degree six: two valley rays along the horizontal line
and four mountain diagonals, with sectors 45°, 90°, 45°, 45°, 90°, 45°. Kawasaki holds (the
alternate sums are 180°) and so does Maekawa (four mountains, two valleys).

**The rigid motion.** Every vertex can fold the same way. Let τ be the angle by which the two
valley rays drop out of the sheet's plane. The six rays are then

    H± = (±cos τ, −sin τ, 0)
    D  = (±1/√2, −tan(τ/2)/√2, ±√(1/2 − tan²(τ/2)/2))

Each diagonal stays 45° from its valley ray and 90° from its neighbouring diagonal, so every face
stays rigid. τ = 0 is flat and τ = 90° is folded flat. The fold angles come from
`pliego.kinematics.vertex_folds`, and the script checks the loop closure of the whole sheet in
every state it uses. As a cross-check it drives one cell's valleys with the kernel's motion solver
and compares the diagonal it finds with the closed form (they agree to about 1e-13°).

**Why the grid curls.** At every vertex the two valley rays are no longer opposite: the valley
line turns by 2τ there. Every vertex turns it the same way, so each valley line becomes a regular
polygon and the sheet rolls up.

**The tube.** The polygons close when they have `columns` sides, at `τ = 180°/columns`. With rows
in register this grid is the Yoshimura pattern with right-angled triangles (base `size`, height
`size/2`), so the tube also has the Yoshimura closed form:

- radius `size / (2 sin(π/n))`;
- consecutive valley lines turned by `π/n`;
- spacing `(size/2) · √(1 − tan²(π/(2n)))`.

The script builds that tube independently and checks four things: the assignment, the loop
closure, that the seam meets, and that the last rigid step equals it:

    kinematics: waterbomb tube n=6 R=30.000mm dz=14.451mm rho_valley=31.0845 rho_diagonal=-42.9414 max_closure_mm=1.34e-13 seam_gap_mm=1.18e-13 rigid_curl_steps=6 gap_to_closed_form_deg=1.1e-13 solver_cross_check_deg=4.6e-14 cell_dof=3

**Pressed flat.** Every vertex is flat-foldable, so the flat-folded state exists: all valleys at
+180° and all diagonals at −180°. The symmetric rigid motion does not reach it, though. Each
valley line would have to turn through far more than a full circle on the way, and the sheet
would pass through itself. A real grid is collapsed row by row instead, and the paper bends while
that happens. The flat-folded geometry is exact. That its layers can be stacked without crossing
is not checked; the kernel orders layers only locally.

## The fold program

**`tube` (kinematic).** Six exact rigid steps, from τ = 0 to τ = 180°/columns. In steps 1–5 the
grid curls, and each note gives τ and how far each valley line has turned. In step 6 the lines
close and the tube is complete. A `target:tube` frame carries the closed-form tube.

**`flat` (physical).** Two steps:

1. **Fold every cell a little.** An exact rigid state at τ = 90°/columns: the grid curls half a
   turn.
2. **Collapse the grid row by row and press it flat.** The exact flat-folded state.

A `target:flat-folded` frame carries the flat-folded state.

**What the preview shows and what needs the physics engine.** In `tube` every step is rigid, so
the preview shows the real motion: the sheet curls up and the seam meets. In `flat` both step
ends are exact. Between them the preview blends the fold angles along the face tree, which no
rigid state matches, so faces separate and cross where real paper bends. That row-by-row collapse
needs the physics engine (tier C).

## Making one by hand

1. Plot or print the grid (SVG, PDF, DXF or HPGL) and score every line.
2. Precrease every line in its own direction: diagonals as mountains, horizontal lines as valleys.
3. For the tube, fold all cells together, a little at a time. The sheet rolls up by itself; join
   the two side edges with tape or a glue tab (not modelled).
4. For the flat grid, collapse one row of waterbomb bases at a time, then press the whole stack.

## Parameters

| Parameter | Meaning |
|---|---|
| `columns` | cells across, which is cells round the tube (3–12) |
| `rows` | cells up (1–8) |
| `size` | side of one cell, mm |
| `stock` | kami, copy paper, kozo washi or tant |

Presets: `square-tube` (4 × 3 cells of 40 mm) and `long-tube` (8 × 6 cells of 25 mm).

## History and sources

The waterbomb base is a traditional origami base, named after the traditional inflatable paper
waterbomb folded from it. As a mechanism it is a symmetric degree-six vertex, and grids of it
fold into deployable tubes that engineers have studied.

- T. C. Hull, *Origametry: Mathematical Methods in Paper Folding*, Cambridge University Press,
  2020. Flat-foldable vertices, Kawasaki and Maekawa.
- B. H. Hanna, J. M. Lund, R. J. Lang, S. P. Magleby and L. L. Howell, "Waterbomb base: a
  symmetric single-vertex bistable origami mechanism", *Smart Materials and Structures* 23 (2014)
  094009.
- Y. Chen, H. Feng, J. Ma, R. Peng and Z. You, "Symmetric waterbomb origami", *Proceedings of the
  Royal Society A* 472 (2016) 20150846. Rigid motions of waterbomb tubes.
- Y. Yoshimura, *On the mechanism of buckling of a circular cylindrical shell under axial
  compression*, NACA Technical Memorandum 1390 (1955). The diamond pattern this grid
  specialises.

## Provenance and licence

Original MADFAM work. The grid is generated by the Pliego kernel from the generic waterbomb cell.
The rigid motion and the tube are computed in closed form by this cartridge's `main.py`. No
designer's waterbomb model or crease pattern is copied. Licence: CERN-OHL-W-2.0 (the commons'
root licence).
