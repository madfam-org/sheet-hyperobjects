# Waterbomb balloon · Bomba de agua

| | Title | Summary |
|---|---|---|
| en | Waterbomb balloon | The traditional water bomb: a waterbomb base collapsed as one rigid vertex, each face folded and tucked, ready to be blown up. |
| es | Bomba de agua | La bomba de agua tradicional: una base de bomba de agua colapsada como un único vértice rígido, cada cara doblada y metida, lista para inflarse. |
| fr | Bombe à eau | La bombe à eau traditionnelle : une base de la bombe à eau affaissée comme un seul sommet rigide, chaque face pliée et rentrée, prête à être gonflée. |
| pt | Bomba de água | A bomba de água tradicional: uma base da bomba de água colapsada como um único vértice rígido, cada face dobrada e metida, pronta a encher. |

## What it is

The paper balloon you blow into through a small hole until it puffs up into a rough cube; filled with
water it becomes the water bomb. The cartridge folds it from a square to the flat folded state.
**Inflation needs the engine's air model** and is not shown; no puffed approximation is offered.

## Geometry

The sheet is a square of side `s`, centre `O`.

- **The waterbomb base.** Both diagonals are valley-folded and unfolded, the horizontal midline
  mountain-folded and unfolded. Six creases meet at `O` with sectors 45°, 90°, 45°, 45°, 90°, 45°.
  The collapse is one degree-6 vertex: the midline's two rays fold mountain and the four diagonal
  rays valley, all at once (`pliego.flatvertex.collapse`). The kernel solves the layer order from
  the side each sector arrives from and checks every ray ends with its sign. The base lies flat as
  a triangle of base `s` and height `s/2`, apex at `O`.
- **Each face.** The two bottom corners are folded up to the apex (a diamond), the diamond's side
  points are folded in to the centre line (vertical folds at 3s/8 and 5s/8), and the two top points
  are folded down along the line at height 3s/8 and tucked into the pockets of those side folds:
  each lands under the top layer of the side flap. The back face repeats the three steps as
  mountain folds seen from the front.

## The fold program

The program is `kinematic`, 12 steps: the collapse in six rigid states, then three steps for each
face (corners, sides, tuck).

- **The square starts creased.** The diagonals and the midline are folded and unfolded before the
  program starts, so its first frame is a creased square, not a fresh one. Each of those creases
  remembers the sense it was folded in: the document gives it a signed rest angle
  (`pliego:edges_restAngle`) of the stock's crease yield, 35°, valley on the diagonals and mountain
  on the midline, which is how far a crease folded flat springs back when it is let go. The
  physics engine starts from those angles; the preview starts flat.
- **The operations.** Every fold is an operation of `pliego.FoldProgram` on a layer-ordered flat
  state. After each one the kernel checks the layer order (taco and tortilla conditions,
  transitivity) and Kawasaki and Maekawa at every vertex. The crease pattern is the final flat
  state unfolded. The six collapse states are even steps along the kernel's rigid path, which
  follows the straight line from start to end in fold-angle space, projected onto the states that
  close.
- **The tucks are real.** `FoldProgram.tuck` folds each top point into its pocket, under the top
  layer of the side flap. With paper of no thickness, the point travels on the simple fold's path
  and crosses that layer at the end (the kernel reports one pocket crossing per point; no other
  paper is crossed). Because each point ends inside the pocket rather than on top, the two layers
  of the point swap valley and mountain on its crease, compared with a point folded on top. The
  preview blends each crease's angle from open to its final value, so it turns the point down
  the other way round, away from the viewer; the fold program's end state, the target and the
  pattern agree.
- **Closure.** Every state closes to about 10⁻⁶ mm (the step angles are written to six decimals).
  A straight blend between two states of the collapse misses closure by up to 2.2 mm on the
  default square; the cartridge prints the figure.

## Making one by hand

1. Fold a square along both diagonals; unfold. Fold it in half (top behind); unfold.
2. Push the ends of the midline in and bring the top down: a triangle with two flaps on each side.
3. On the front, fold the two bottom corners up to the top point.
4. Fold the two side points in to the centre line.
5. Fold the two loose top points down and tuck them into the pockets of the side folds.
6. Turn over and repeat 3 to 5.
7. Blow hard into the hole at the bottom.

## Parameters

| Parameter | Meaning |
|---|---|
| `size` | side of the square, mm |
| `stock` | kami or copy paper 80 g/m² |

## History and sources

The Public Paperfolding History Project finds the waterbomb first in Elise van Calcar's Dutch
folding book of 1863, as "De teerling" (the die). In Japan it appears as "Temari" (ball) in the
children's magazine *Shokokumin* in 1894, and as the "Balloon" in Sano Shozo's *Origami zusetsu*
(1908) and Isao Honda's *Origami (Part 1)* (1931). The project describes it as a Western European
design that reached Japan with the kindergarten system. Its first steps form the waterbomb base,
one of origami's fundamental bases.

- The Public Paperfolding History Project, "The waterbomb":
  https://origamiheaven.com/historyofthewaterbomb.htm

## Provenance and licence

Geometry generated by this cartridge with the Pliego kernel; credited to tradition. Licence
CERN-OHL-W-2.0 (both manifest fields).
