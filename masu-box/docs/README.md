# Masu box · Caja masu

| | Title | Summary |
|---|---|---|
| en | Masu box | The traditional masu box and its lid, folded from one square each; the end walls rise while their corners fold in, an exact rigid motion. |
| es | Caja masu | La caja masu tradicional y su tapa, cada una doblada con un cuadrado; las paredes de los extremos se levantan mientras sus esquinas se doblan hacia dentro, en un movimiento rígido exacto. |
| fr | Boîte masu | La boîte masu traditionnelle et son couvercle, chacun plié dans un carré ; les parois d'extrémité se relèvent tandis que leurs coins se replient, en un mouvement rigide exact. |
| pt | Caixa masu | A caixa masu tradicional e a sua tampa, cada uma dobrada de um quadrado; as paredes das pontas levantam-se enquanto os cantos se dobram para dentro, num movimento rígido exato. |

## What it is

A square box with no glue, named after the wooden *masu* once used in Japan to measure rice. Two
modes:

- **`box`**: the box, folded from a square of side `size`;
- **`lid`**: the lid, folded from a square of side `size + 4√2 · gap`. Its floor is `2 · gap` wider
  than the box's, so it fits over the box with `gap` to spare on each side.

## Geometry

The square is turned 45°: `Lh = size/√2` is half its diagonal, and the blintzed square is
`[−Lh/2, Lh/2]²`. With `q = Lh/4`:

- the **floor** is the square `|x|, |y| ≤ q`, 2q wide (70.7 mm for a 200 mm square);
- the **walls** are `q` high (35.4 mm);
- each **corner square** `q ≤ |x|, |y| ≤ 2q` folds along its diagonal into a gusset.

The sheet starts creased along its two midlines, which are the diagonals of the corner squares.
The program blintzes the square, creases the four edges to the centre lines and unfolds the top
and bottom corners.

**The side walls** rise 90° about the lines `x = ±q`. Everything beyond each line rises with it:
the wall strip, the blintz flap folded inside it, and the corner squares.

**The end walls.** At the floor corner `V`, five creases meet: the floor's two edges, the end wall's
side edge, the side wall's edge (now upright) and the corner square's diagonal. With the side wall
already standing, raising the end wall by φ about the floor edge is a motion with one degree of
freedom. The end wall's side edge points along `n(φ) = cos φ · north + sin φ · up`. The diagonal ray
`r₂` must stay 45° from the upright edge (`up`) and 45° from `n(φ)`, which gives

    r₂(φ) = (up + n(φ)) / (√2 · (1 + sin φ)) + √(sin φ / (1 + sin φ)) · (∓x̂).

The sign is the one that folds the gusset inwards, over the end wall. The kernel does not use this
formula: it solves the motion on the whole crease pattern (below), and its states agree with it. At φ = 90° the gusset lies folded flat against the inside
of the end wall, and the triangle above it (the corner of the end flap) lies along the wall's top
edge.

**The end flaps** fold over the wall top into the box. The band below the wall top is `q` deep, so it
covers the inside of the wall, and the tip turns 90° along the crease at `3q` to lie on the floor.

## The fold program

The program is `kinematic`, 23 steps: the blintz, four edge creases (fold and unfold), unfolding
the end corners, raising the side walls, then for each end five rigid steps of the end wall rising
and one step for the flap.

- **The square starts creased.** Its two midlines are folded and unfolded before the program
  starts. Each remembers the sense it was folded in: the document gives it a signed rest angle
  (`pliego:edges_restAngle`) of the stock's crease yield, 35° valley, which is how far a crease
  folded flat springs back when it is let go. The physics engine starts from those angles; the
  preview starts flat.
- **Flat operations.** The blintz, the edge creases and the opened corners are operations of
  `pliego.FoldProgram` on a layer-ordered flat state. After each one the kernel checks the layer
  order (taco and tortilla conditions, transitivity) and Kawasaki and Maekawa at every vertex.
- **3-D steps.** The side walls are a hinge pose (`hinges`). Each end wall is a rigid step on the
  whole crease pattern (`kinematic`): the floor edge turns to its angle, the three creases at each
  floor corner follow, and every other crease holds. The first 18° is its own step, so each gusset
  leaves the flat sheet folding inwards; the rest, to 90°, is one step that the program shows as
  four steps of 18°. Each flap is a flat fold inside the wall's plane, with its tip turning 90°
  onto the floor at the same time. At every sampled state the kernel checks that no moving face
  passes through paper that stays (none does).
- **The crease pattern.** The pattern is the flat state unfolded. A crease opened again, or
  folded only in 3-D (the walls, the gussets, the flaps), is drawn flat (`F`, a scored line); the
  sequence and the `folded` target drive each one to its angle. Only the side blintz folds, which
  stay folded throughout, keep their valley.
- **Closure.** Every state is an exact rigid state (closure about 10⁻⁶ mm; the step angles are
  written to six decimals). The finished box keeps all of its paper inside the box volume
  `[−q, q] × [0, q] × [−q, q]`; the cartridge checks this while it is written. The end-wall
  motion is not linear in the fold angles: a straight blend between two of its steps misses
  closure by up to 8 mm on the default square. The cartridge prints the figure.
- **The lid's square** is rounded to a multiple of 8 µm (at most 4 µm off `size + 4√2 · gap`),
  so every vertex of its pattern lies on the kernel's 10⁻⁶ mm grid.

## Making one by hand

1. Fold a square in half both ways and unfold.
2. Fold the four corners to the centre.
3. Fold the top and bottom edges to the centre line and unfold; do the same with the left and right
   edges.
4. Unfold the top and bottom corners.
5. Raise the left and right sides as walls.
6. Lift the top end: push its corners in along the creases so they fold inside, and the end
   stands as a wall.
7. Fold the top flap over the wall and down onto the floor. Repeat 6 and 7 at the bottom end.
8. For the lid, fold a square that is `4√2 · gap` larger (for 1.5 mm, about 8.5 mm larger) the same
   way.

## Parameters

| Parameter | Meaning |
|---|---|
| `size` | side of the box's square, mm |
| `gap` | lid clearance per side, mm (lid mode) |
| `stock` | kami, copy paper 80 g/m² or card 160 g/m² |

## History and sources

The Public Paperfolding History Project records the masu under its other name, the blintz box. In
Japan it first appears in Isao Honda's *Origami (Part 1)* (1931) and *Origami Shuko* (1944), and
in English as the "Treasure Box" with lid in Florence Sakade's *Origami: Book Three* (1959). The
project notes that European references are older: David Mitchell traces the model to 1864, when
Elise van Calcar described it as an ashtray ("Het aschbakje").

- The Public Paperfolding History Project, "The blintz box":
  https://www.origamiheaven.com/historyoftheblintzbox.htm

## Provenance and licence

Geometry generated by this cartridge with the Pliego kernel; credited to tradition. Licence
CERN-OHL-W-2.0 (both manifest fields).
