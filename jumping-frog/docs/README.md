# Jumping frog · Rana saltarina

| | Title | Summary |
|---|---|---|
| en | Jumping frog | The index-card frog: a waterbomb half-base head, front legs, folded sides and a Z-pleat spring that stores the jump. |
| es | Rana saltarina | La rana de ficha: una cabeza de media base de bomba de agua, patas delanteras, lados doblados y un resorte en Z que guarda el salto. |
| fr | Grenouille sauteuse | La grenouille en fiche bristol : une tête en demi-base de la bombe à eau, des pattes avant, des côtés repliés et un ressort en Z qui emmagasine le saut. |
| pt | Rã saltadora | A rã de ficha: uma cabeça em meia base da bomba de água, patas da frente, lados dobrados e uma mola em Z que guarda o salto. |

## What it is

A paper frog folded from an index card (or a business card). You press its back end down and let
your finger slip off; the Z-shaped pleat under the body springs open and the frog hops. The
cartridge folds it from the flat card to the finished frog sitting on its spring, then shows the
pleat pressed flat, the way a finger loads the jump.

## Geometry

The card is `W × H` (3 × 5 in by default). Its top `W × W` square carries the head.

- **The X and the line.** Each top corner is folded to the opposite long edge and unfolded, so two
  45° creases cross at `O = (W/2, H − W/2)`. A mountain fold through `O`, parallel to the short
  edge, completes a waterbomb half-base: six creases meet at `O`.
- **The head is one rigid vertex.** The collapse is a single degree-6 vertex with sector angles
  45°, 90°, 45°, 45°, 90°, 45°. With the body held still and mirror symmetry left to right, it has
  one degree of freedom. The cartridge drives the lower-left triangle round its crease by ψ and
  solves the remaining rays on the unit sphere. The upper-left ray must make 45° with its
  neighbours and 90° with its mirror image, which fixes it as the intersection of a line and a
  circle. Each sector then turns rigidly from its flat rays to the solved rays.
- **Front legs, body, spring.** The two bottom corners of the head triangle are folded up to its
  apex, the long sides are folded in to the centre line, the bottom is folded up to the base of the
  head and folded back down in half. Those last two folds are the Z pleat.

## The fold program

The program is `kinematic`, 18 steps: crease the X (fold and unfold, twice), crease the line
through `O` (fold and unfold), collapse the head in six rigid states, fold the front legs, the
sides, the bottom up and the pleat back down. Then the pleat opens by `spring` degrees so the frog
sits on it, and finally it is pressed nearly flat. With `spring` at 0 the pleat has nothing to
open, so that step is left out.

- **Flat folds.** Every fold is an operation of `pliego.FoldProgram` on a layer-ordered flat state.
  After each one the kernel checks the layer order (taco and tortilla conditions, transitivity) and
  Kawasaki and Maekawa at every vertex. The crease pattern is the final flat state unfolded.
- **The head is one vertex collapse** (`pliego.flatvertex.collapse`). The two diagonals fold
  valley and the line through `O` mountain, all at once; the kernel solves the layer order and
  checks every ray ends with its sign. The six states the program shows are even steps along the
  kernel's rigid path, which follows the straight line from start to end in fold-angle space,
  projected onto the states that close.
- **The spring and the press are 3-D hinge poses.** The bottom flap turns about the bottom-up
  crease and the pleat's flap about the pleat's crease (`FoldProgram.hinge`), with every layer
  of each flap.
- **Closure.** Every state is an exact rigid state: the worst loop-closure residual over the program
  is below 10⁻⁶ mm (the step angles are written to six decimals). The collapse is not linear
  in the fold angles: a straight blend between two of its states misses closure by up to
  1.1 mm on the default card. The cartridge prints both figures.
- **The pattern.** Each crease's fold angle in the pattern is the flat-folded one (±180°); the
  sequence and the `folded` target carry the pleat's open and pressed angles.

**The jump needs physics.** Pressing stores elastic energy in the pleat's creases, and the hop is
that energy released against the frog's weight and the table. The studio's preview is kinematic
and shows the pleat's positions only; the bounce waits for the physics engine.

## Making one by hand

1. Hold an index card upright. Fold the top right corner to the left edge, crease, unfold. Do the
   same with the top left corner.
2. Fold the top down along the line through the centre of the X, crease, unfold.
3. Push the two ends of that line in: the top collapses into a triangle on the front.
4. Fold the triangle's two bottom corners up to its top point: the front legs.
5. Fold the long sides in to meet at the centre line.
6. Fold the bottom up to the base of the head, then fold that flap back down in half.
7. Turn the frog over. Press its back and slide your finger off.

## Parameters

| Parameter | Meaning |
|---|---|
| `card` | 3 × 5 in or 4 × 6 in index card, or a business card |
| `spring` | how far each fold of the pleat opens when the frog rests on it, 0–80° |
| `stock` | card 160 g/m² (default), copy paper 80 g/m², card 250 g/m² |

## History and sources

The jumping frog folded from a card first appears in *Folding Paper Toys* by Shari Lewis and
Lillian Oppenheimer (Stein and Day, New York, 1963), and in *The Australian Women's Weekly* of
12 May 1963, which reprinted it. *The Origamian* (spring 1964) speaks of it in terms that suggest it
may have begun with Oppenheimer and Lewis; its earlier origin is not documented. It is folded today
as a traditional model, and this cartridge credits it to tradition.

- The Public Paperfolding History Project, "The jumping frog":
  https://www.origamiheaven.com/historyofthejumpingfrog.htm

## Provenance and licence

Geometry generated by this cartridge with the Pliego kernel; no published diagram is copied.
Licence CERN-OHL-W-2.0 (both manifest fields).
