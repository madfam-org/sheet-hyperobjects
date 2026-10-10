# Bird base

| | Title | Summary |
|---|---|---|
| en | Bird base | The base of the crane: a preliminary base petal-folded front and back. Five interior vertices; the collapse and both petal folds run along exact rigid paths from the kernel's motion solver. |
| es | Base de pájaro | La base de la grulla: una base preliminar con pliegue pétalo delante y detrás. Cinco vértices interiores; el colapso y los dos pliegues pétalo siguen trayectorias rígidas exactas del solucionador de movimiento del núcleo. |
| fr | Base de l'oiseau | La base de la grue : une base préliminaire pliée en pétale devant et derrière. Cinq sommets intérieurs ; l'effondrement et les deux plis pétale suivent des trajectoires rigides exactes du solveur de mouvement du noyau. |
| pt | Base do pássaro | A base do grou: uma base preliminar com dobra pétala na frente e atrás. Cinco vértices interiores; o colapso e as duas dobras pétala seguem trajetórias rígidas exatas do solucionador de movimento do núcleo. |

The bird base, or crane base, is the base of the traditional crane and the flapping bird (see
`paper-crane` and `flapping-bird`). Fold a preliminary base (see `preliminary-base`), and then
petal-fold its front flap and its back flap (see `petal-fold`). What remains is a long diamond with
four flaps: two narrow upper flaps, the petals, which become a crane's wings, and two lower flaps
split down the middle, which become the neck and the tail.

## Geometry

The sheet is a square of side `size` with centre O; h = `size`/2 and k = h·(2 − √2) ≈ 0.586·h. The
corners are B (front petal), D (back petal), C₁ and C₂ (the lower flaps). The edge midpoints are
E, N, W, S.

| Crease | Where | Assignment in the base |
|---|---|---|
| book folds, inner part | O to K on each ray, \|OK\| = k | mountain |
| book folds, outer part | K to the edge midpoint | precrease, open in the base |
| diagonal C₂–C₁ | through O | valley |
| petal kite creases | B to K₁ and K₂; D to K₃ and K₄ | mountain |
| inner-layer kite creases | K₁–C₁, K₂–C₂, K₃–C₂, K₄–C₁ | mountain |
| petal hinges | K₁–K₂ (front), K₃–K₄ (back) | valley |

Each K is where a line from the petal corner, at 22.5° to the diagonal, meets the book fold. That
is the line that lays the flap's lower edge on the centre line. The diagonal B–D is not creased.

The folded pattern has five interior vertices:

- **O**, degree 6: the preliminary base's vertex, with sectors 90°, 45°, 45°, 90°, 45°, 45°.
  Kawasaki holds exactly (slopes 0, ∞ and −1).
- **K₁ to K₄**, degree 4 in the base: inner book fold, petal kite crease, hinge and inner-layer kite
  crease, with sectors 135°, 67.5°, 45° and 112.5°. Kawasaki holds (135° + 45° = 180°); the 22.5°
  slopes are irrational, so the kernel checks it in floating point within the bound set by its
  coordinate grid. Maekawa holds with three mountains and one valley.

During the program each K is a degree-5 vertex, because the outer book fold is still folded. It
opens flat as the petal rises, exactly as in `petal-fold`. `pliego.flatfold.check` tests Maekawa,
Kawasaki and big-little-big on the folded creases every time the cartridge runs.

## The fold program

The program has 65 kinematic steps, written as 13 key poses:

1. Precreases: the diagonal, then each book fold, folded and unfolded (21 steps).
2. Collapse into a preliminary base (10 steps).
3. Front flap: kite precreases through both layers (4 steps), unfold (3 steps), petal fold (10
   steps).
4. Back flap: the same (17 steps).

`pliego.Sequence.kinematic_path` expands each key pose into exact rigid in-between states with
the kernel's motion solver. In each petal fold three vertices move at once (O holds, K₁ and K₂ or
K₃ and K₄ move). The solver finds the rigid branch in which the corner rises over the hinge while
the outer book folds open from 180° to 0°. The worst loop residual is about 10⁻⁸ rad, the floor set
by the grid-snapped positions of the K points. The document carries two reference frames,
`target:preliminary-base` and `target:flat-folded` (the bird base).

What the program does **not** model:

- **The stretched bird base.** The catalogue lists it as a variant. It is not included: this
  cartridge could not derive its crease pattern from geometry it can verify (a flat-folded state
  with the two lower flaps pulled apart that also passes the checks above), and it does not copy a
  published one.
- **No layer contact.** The kite flaps fold in as the petal rises. Zero-thickness kinematics does
  not check that they pass cleanly; contact belongs to the physics engine.
- **No crease memory.** In kinematic mode the unfolded precreases are exactly flat again.

## Making one

1. Fold a preliminary base, coloured side out, open end toward you.
2. Fold the lower edges of the front flap to the centre line, through both layers on each side.
   Crease firmly and unfold.
3. Lift the bottom corner of the front layer along the horizontal crease. The sides fold in along
   the kite creases and meet in the middle. Flatten the long diamond.
4. Turn over and repeat on the back flap.

## Parameters

| Parameter | Meaning | Default |
|---|---|---|
| `size` | side of the square (mm) | 150 |
| `stock` | `kami`, `copy-80`, `washi-kozo-30` | `kami` |

Presets: `large-24cm` (a 240 mm square).

## History and sources

The bird base is the traditional base of the Japanese crane (orizuru) and of the flapping bird.
Its crease pattern and its derivation from the preliminary base by two petal folds are described
in Robert J. Lang, *Origami Design Secrets: Mathematical Methods for an Ancient Art*, 2nd ed., CRC
Press, 2011. The flat-foldability conditions checked here are Kawasaki's and Maekawa's theorems,
as presented in Thomas C. Hull, *Origametry: Mathematical Methods in Paper Folding*, Cambridge
University Press, 2020. No diagram is reproduced; the geometry is computed by this cartridge.

## Provenance and licence

Traditional base (public domain); original geometry and program by Innovaciones MADFAM. Published
under CERN-OHL-W-2.0, like every object in the commons (see the commons root `LICENSE`).
