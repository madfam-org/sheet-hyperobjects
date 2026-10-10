# Preliminary base

| | Title | Summary |
|---|---|---|
| en | Preliminary base | The square base: one diagonal and both book folds collapse so the four corners meet at the bottom. One vertex of degree 6, folded along an exact rigid path, coloured side out or in. |
| es | Base preliminar | La base cuadrada: una diagonal y los dos pliegues de libro se pliegan juntos y las cuatro esquinas se encuentran abajo. Un vértice de grado 6, doblado por una trayectoria rígida exacta, con el color por fuera o por dentro. |
| fr | Base préliminaire | La base carrée : une diagonale et les deux plis livre s'effondrent ensemble et les quatre coins se rejoignent en bas. Un sommet de degré 6, plié le long d'une trajectoire rigide exacte, couleur à l'extérieur ou à l'intérieur. |
| pt | Base preliminar | A base quadrada: uma diagonal e as duas dobras de livro colapsam juntas e os quatro cantos encontram-se em baixo. Um vértice de grau 6, dobrado por uma trajetória rígida exata, com a cor por fora ou por dentro. |

The preliminary base, also called the square base, is the first base most folders learn. A
square is creased along one diagonal and both book folds, and then the creases are pushed together
so that the four corners meet at the bottom and the centre of the paper becomes the closed top
point. The result is a small square, a quarter of the paper's area, with two flaps on each side.
The bird base, the frog base and the crane all start here (see `bird-base`, `frog-base` and
`petal-fold`).

## Geometry

The sheet is a square of side `size` with centre O. Every crease meets O:

| Crease | Ray from O | Coloured side out | Coloured side in |
|---|---|---|---|
| book fold, E and W halves | 0°, 180° | mountain | valley |
| book fold, N and S halves | 90°, 270° | mountain | valley |
| diagonal, NW and SE halves | 135°, 315° | valley | mountain |

The other diagonal is not creased. It runs down the middle of the front and back flaps, which
stay flat. So the base is a single vertex of degree 6 with sectors 90°, 45°, 45°, 90°, 45°, 45°,
counter-clockwise from the east ray:

- **Kawasaki:** alternate sectors sum to 90° + 45° + 45° = 180°. All slopes are 0, ∞ or −1, so the
  kernel checks it exactly in rational arithmetic.
- **Maekawa:** four creases of one kind against two of the other, |M − V| = 2.
- **Big-little-big:** the 45° sectors are never strictly smaller than both neighbours.

`pliego.flatfold.check` runs these tests on the folded creases every time the cartridge runs, and
the cartridge fails if any of them fails.

`colour` chooses which side of the paper ends up outside. Folding with the coloured side in is the
same base made from the other side of the sheet: seen from the coloured side, every mountain
becomes a valley and every valley a mountain.

## The fold program

The program has 33 kinematic steps, written as seven key poses:

1. Fold the diagonal (4 steps) and unfold it (3 steps).
2. Fold the book fold top to bottom (4 steps) and unfold it (3 steps).
3. Fold the book fold side to side (4 steps) and unfold it (3 steps).
4. Collapse (12 steps): all six creases at once.

`pliego.Sequence.kinematic_path` expands each key pose into exact rigid in-between states with
the kernel's motion solver. Each precrease is a single straight crease through O, so it folds and
unfolds as a hinge. The collapse is a degree-6 vertex with three rigid degrees of freedom (the
kernel reports `dof=3`). The solver follows the symmetric path toward the flat-folded state, with
every loop closed to about 10⁻¹³ rad. The flat-folded state is also written as the
`target:flat-folded` frame. Its loop-closure residual is checked before the document is written.

What the program does **not** model:

- **No layer contact.** Zero-thickness rigid kinematics places every face exactly, but it does not
  stop layers from passing through each other. Contact belongs to the physics engine.
- **No crease memory between the precreases and the collapse.** In kinematic mode an unfolded
  precrease is exactly flat again. Real paper keeps a rest angle there (see `crease-and-unfold`),
  and that memory is what makes the collapse easy by hand.

## Making one

1. Start with a square, coloured side up for the coloured-out base.
2. Valley-fold it in half along the diagonal and unfold.
3. Turn it over. Valley-fold it in half edge to edge, unfold, and repeat in the other direction.
   These are the mountain folds of the program, seen from the other side.
4. Turn it back over. Push the centre down slightly and bring all four corners together at the
   bottom. Flatten so that two flaps lie on each side.

For the coloured-in base, start with the white side up.

## Parameters

| Parameter | Meaning | Default |
|---|---|---|
| `size` | side of the square (mm) | 150 |
| `stock` | `kami`, `copy-80`, `washi-kozo-30` | `kami` |
| `colour` | `out` (coloured side outside) or `in` | `out` |

Presets: `coloured-in`, `large-24cm` (a 240 mm square).

## History and sources

The preliminary base is a traditional base of Japanese and Western paper folding, the common
starting point of the crane, the lily and the frog. Its crease pattern and its use as a base are
described in Robert J. Lang, *Origami Design Secrets: Mathematical Methods for an Ancient Art*,
2nd ed., CRC Press, 2011. The flat-foldability conditions checked here are Kawasaki's and
Maekawa's theorems, as presented in Thomas C. Hull, *Origametry: Mathematical Methods in Paper
Folding*, Cambridge University Press, 2020. No diagram is reproduced; the geometry is computed by
this cartridge.

## Provenance and licence

Traditional base (public domain); original geometry and program by Innovaciones MADFAM. Published
under CERN-OHL-W-2.0, like every object in the commons (see the commons root `LICENSE`).
