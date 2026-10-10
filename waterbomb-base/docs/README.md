# Waterbomb base

| | Title | Summary |
|---|---|---|
| en | Waterbomb base | The triangle base: both diagonals and one book fold collapse the square into a right isosceles triangle, the preliminary base turned inside out. One vertex of degree 6, folded along an exact rigid path. |
| es | Base de bomba de agua | La base triangular: las dos diagonales y un pliegue de libro convierten el cuadrado en un triángulo rectángulo isósceles, la base preliminar vuelta del revés. Un vértice de grado 6, doblado por una trayectoria rígida exacta. |
| fr | Base de la bombe à eau | La base triangulaire : les deux diagonales et un pli livre replient le carré en triangle rectangle isocèle, la base préliminaire retournée. Un sommet de degré 6, plié le long d'une trajectoire rigide exacte. |
| pt | Base da bomba d'água | A base triangular: as duas diagonais e uma dobra de livro transformam o quadrado num triângulo retângulo isósceles, a base preliminar virada do avesso. Um vértice de grau 6, dobrado por uma trajetória rígida exata. |

The waterbomb base, or triangle base, is named after the traditional waterbomb (the inflatable
paper balloon) that is folded from it. The square is precreased along both diagonals and one book
fold. Pushing the side midpoints in collapses it into a right isosceles triangle: the centre of
the paper becomes the apex, and the four corners meet in pairs at the two base corners. It is the
preliminary base turned inside out (see `preliminary-base`). The tulip blossom (see `tulip`) and
many boxes start from it.

## Geometry

The sheet is a square of side `size` with centre O. Every crease meets O. Seen from the coloured
side, with the coloured side ending up outside:

| Crease | Rays from O | Assignment |
|---|---|---|
| both diagonals | 45°, 135°, 225°, 315° | mountain |
| one book fold (E and W halves) | 0°, 180° | valley |

The other book fold is not creased: it runs down the middle of the front and back triangles, which
stay flat. The base is one vertex of degree 6 with sectors 45°, 45°, 90°, 45°, 45°, 90°,
counter-clockwise from the east ray:

- **Kawasaki:** alternate sectors sum to 45° + 90° + 45° = 180°. The slopes are 0 and ±1, so the
  kernel checks it exactly in rational arithmetic.
- **Maekawa:** four mountains and two valleys, |M − V| = 2.
- **Big-little-big:** the 45° sectors are never strictly smaller than both neighbours.

`pliego.flatfold.check` runs these tests on the folded creases every time the cartridge runs, and
the cartridge fails if any of them fails. The folded triangle has a hypotenuse of `size` and a
height of `size`/2.

## The fold program

The program has 33 kinematic steps, written as seven key poses:

1. Mountain-fold the first diagonal (4 steps) and unfold it (3 steps).
2. Mountain-fold the second diagonal (4 steps) and unfold it (3 steps).
3. Valley-fold the book fold (4 steps) and unfold it (3 steps).
4. Collapse (12 steps): all six creases at once.

`pliego.Sequence.kinematic_path` expands each key pose into exact rigid in-between states with
the kernel's motion solver. Each precrease is one straight crease through O, a plain hinge. The
collapse is a degree-6 vertex with three rigid degrees of freedom (`dof=3`). The solver follows
the symmetric path to the flat-folded triangle, with every loop closed to about 10⁻¹⁴ rad. The
southern triangle stays on the table. The flat-folded state is written as the
`target:flat-folded` frame, and its loop-closure residual is checked before the document is
written.

What the program does **not** model:

- **No layer contact.** The side triangles fold inside between the front and back faces. Rigid
  kinematics does not check that they pass cleanly; contact belongs to the physics engine.
- **No crease memory.** In kinematic mode an unfolded precrease is exactly flat again. Real paper
  keeps a rest angle there (see `crease-and-unfold`).

## Making one

1. Start with a square, coloured side up.
2. Turn it over, valley-fold both diagonals and unfold. Seen from the coloured side, these are
   mountain folds.
3. Turn it back. Valley-fold it in half edge to edge and unfold.
4. Hold the paper by the ends of the book fold and push those two midpoints toward each other. The
   sides fold inside along the book fold, and the square flattens into a triangle.

## Parameters

| Parameter | Meaning | Default |
|---|---|---|
| `size` | side of the square (mm) | 150 |
| `stock` | `kami`, `copy-80`, `washi-kozo-30` | `kami` |

Presets: `large-24cm` (a 240 mm square), `copy-paper` (a 200 mm square of 80 g/m² copy paper).

## History and sources

The waterbomb base is a traditional base, named after the waterbomb balloon folded from it. Its
crease pattern and its relation to the preliminary base are described in Robert J. Lang,
*Origami Design Secrets: Mathematical Methods for an Ancient Art*, 2nd ed., CRC Press, 2011. The
flat-foldability conditions checked here are Kawasaki's and Maekawa's theorems, as presented in
Thomas C. Hull, *Origametry: Mathematical Methods in Paper Folding*, Cambridge University Press,
2020. No diagram is reproduced; the geometry is computed by this cartridge.

## Provenance and licence

Traditional base (public domain); original geometry and program by Innovaciones MADFAM. Published
under CERN-OHL-W-2.0, like every object in the commons (see the commons root `LICENSE`).
