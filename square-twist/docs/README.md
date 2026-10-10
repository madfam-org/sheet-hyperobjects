# Square twist

| | Title | Summary |
|---|---|---|
| en | Square twist | A central square ringed by four pleats; folded flat, the square turns as the pleats close round it. One twist, or a grid of twists of alternating hand. |
| es | Torsión cuadrada | Un cuadrado central rodeado por cuatro pliegues; al plegarlo en plano, el cuadrado gira mientras los pliegues se cierran a su alrededor. Una torsión sola o una cuadrícula de torsiones que alternan el sentido de giro. |
| fr | Twist carré | Un carré central entouré de quatre plis ; replié à plat, le carré tourne pendant que les plis se referment autour de lui. Un twist seul, ou une grille de twists qui alternent le sens de rotation. |
| pt | Torção quadrada | Um quadrado central rodeado por quatro pregas; dobrado rente, o quadrado gira enquanto as pregas se fecham à sua volta. Uma torção única, ou uma grade de torções que alternam o sentido de giro. |

## What it is

A twist fold is the basic cell of most origami tessellations. A small polygon in the middle of the
sheet is outlined with valley creases, and from each of its edges a pleat (one mountain line, one
valley line) runs outward. When the pleats are folded flat they cannot stay where they are: they
slide round the polygon, which turns on the spot. This cartridge carries the square case in two
modes:

| Mode | Sheet | What you get |
|---|---|---|
| `single` | a square sheet | one square twist in the middle (kernel generator `pliego.tessellate.twist`, n = 4) |
| `tiled` | a square of `cells × cells` cells | a grid of square twists joined by their pleats |

## Geometry

**One twist.** Call the twist angle `α`. At each corner of the central square the four creases sit
at 0° and 90° (the square's two edges) and at 180° + α and 270° + α (the two pleat lines),
measured from one edge. The sectors between them are therefore

    90°, 90° + α, 90°, 90° − α

The alternate sums are 180° each, so **Kawasaki's theorem** holds for any `α`. The assignment is
three valleys and one mountain, so **Maekawa's theorem** (|M − V| = 2) holds as well, and the
smallest sector (90° − α) is bounded by one mountain and one valley, so the big-little-big rule
holds. The pleat width is `inner · cos α`. The script runs `pliego.flatfold.check` on every
vertex before it returns and fails loud if any test fails.

**The tiled grid.** In the `tiled` mode the script writes the grid itself. Every centre square is
turned by −α, which makes its pleats run parallel to the sheet's edges. Neighbouring twists are
**mirror images** of each other (alternating hand, as on a chessboard). With that choice the
pleat leaving a corner of one twist arrives exactly at a corner of the next one, and it has the
same assignment at both ends. The script checks three things and fails loud if any is false:

- every pleat meets its partner corner;
- no two pleats cross;
- every vertex passes the flat-foldability tests above.

Pleats of the outer twists run to the edge of the sheet. A pleat that enters a twist on one side
leaves it on the other side shifted sideways by `inner · sin α`. That offset is what lets the
squares turn.

**Rigid folding.** A square twist with this assignment cannot be folded with flat, rigid panels.
The paper has to bend between the flat sheet and the flat-folded twist. In the `single` mode the
script checks this with the kernel's motion solver. It drives one centre valley 10° away from
flat and lets `pliego.kinematics.solve` find the rigid motion. The only branch it finds folds
three creases against their assignment, so it does not lead to the twist. The script prints:

    kinematics: rigid branch from flat dof=1 creases_against_assignment=3 -> program is physical (the paper bends on the way)

## The fold program

The program is `physical`, with three steps:

1. **Pre-fold the pleats halfway.** Pleats go to ±90°, the centre edges to 20°.
2. **Twist the centre.** Pleats go to ±150°, the centre edges to 120°. The step's note says that
   no rigid path exists.
3. **Press the twist flat.** Every crease goes to ±180°.

The document also carries a `target:flat-folded` frame, the exact flat-folded state.

**What the preview shows and what needs the physics engine.** The studio's preview poses the faces
along a spanning tree of the crease pattern. It shows the last step, the flat-folded twist,
exactly: every crease is at 180° and Kawasaki holds everywhere, so the faces meet. In between,
the rigid face tree cannot follow the bending paper, and seams open between faces that the tree
does not join. The physics engine (tier C) is what bends the panels and closes those seams.

## Making one by hand

1. Print or plot the crease pattern (SVG, PDF, DXF or HPGL) and score every line. Kami and
   80 g/m² copy paper take a bone-folder score; score tant with a plotter blade at low pressure.
2. Precrease every line in its own direction: fold it, press it, open it again.
3. Pre-fold all the pleats a little.
4. Push the centre square down from the front and turn it while the pleats close round it.
5. Press it flat.

For the grid, fold one twist at a time, starting in a corner. Each finished twist sets the pleats
of its neighbours. Twists that alternate in hand turn in opposite directions.

## Parameters

| Parameter | Modes | Meaning |
|---|---|---|
| `alpha` | both | twist angle α, degrees (10–40) |
| `inner` | both | side of each centre square, mm |
| `sheet_size` | `single` | side of the square sheet, mm |
| `cells` | `tiled` | twists per side of the grid |
| `pitch` | `tiled` | distance between neighbouring twist centres, mm |
| `stock` | both | kami, copy paper, kozo washi or tant |

Presets: `gentle` (α = 15°) and `steep` (α = 35°, centre square 24 mm). In the tiled grid the turned
squares need room. The script refuses a pitch below `inner · (cos α + sin α) + 2 mm` and names the
smallest pitch that works.

## History and sources

Twist folds were explored systematically by Shuzo Fujimoto in the 1970s. They are now studied as a
mathematical family of flat-foldable crease patterns.

- S. Fujimoto, *Sōzōsei o kaihatsu suru rittai origami* ("Creative invention by 3-D origami"),
  self-published, 1976. An early collection of twist folds and tessellations.
- R. J. Lang, *Twists, Tilings, and Tessellations: Mathematical Methods for Geometric Origami*,
  CRC Press, 2018. The general theory of twist folds and their tilings.
- T. A. Evans, R. J. Lang, S. P. Magleby and L. L. Howell, "Rigidly foldable origami twists", in
  *Origami⁶* (American Mathematical Society, 2015). Which twists fold with rigid panels.
- T. C. Hull, *Origametry: Mathematical Methods in Paper Folding*, Cambridge University Press,
  2020. The Kawasaki and Maekawa theorems.

## Provenance and licence

Original MADFAM work. The single twist comes from the Pliego kernel's generator; the tiled grid
is computed by this cartridge's `main.py`. Both are built from the generic, mathematically defined
twist fold, and no published crease pattern or designer's tessellation is copied. Licence:
CERN-OHL-W-2.0 (the commons' root licence).
