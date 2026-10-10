# Windmill base

| | Title | Summary |
|---|---|---|
| en | Windmill base | Quarter lines, diagonals and a blintz collapse into four flaps swivelled round a central square, in four-fold rotational symmetry. Flat-folded state verified exactly; the swivel collapse runs as a physical program. |
| es | Base de molinete | Las líneas de cuarto, las diagonales y un blintz se pliegan en cuatro solapas giradas alrededor de un cuadrado central, con simetría de rotación de orden cuatro. El estado doblado se verifica de forma exacta; el colapso con giros se ejecuta como secuencia física. |
| fr | Base du moulin à vent | Les lignes des quarts, les diagonales et un blintz s'effondrent en quatre rabats pivotés autour d'un carré central, avec une symétrie de rotation d'ordre quatre. L'état plié est vérifié exactement ; l'effondrement par pivots est une séquence physique. |
| pt | Base do cata-vento | As linhas dos quartos, as diagonais e um blintz colapsam em quatro abas giradas em volta de um quadrado central, com simetria de rotação de ordem quatro. O estado dobrado é verificado de forma exata; o colapso com giros corre como sequência física. |

The windmill base is the paper windmill, or pinwheel, of traditional folding. It also starts the
double-boat family of models. A square is precreased along its quarter lines, both diagonals and
a blintz. Then the edges are refolded to the centre one corner at a time, and the paper that has
nowhere to go at each corner is swivelled out as a flap. The result is a central square with four
triangular flaps standing round it, all turned the same way.

## Geometry

The sheet is a square of side `size`, with q = `size`/4 and centre C. The central square has
corners (q, q), (3q, q), (3q, 3q) and (q, 3q). The pattern has four-fold rotational symmetry. Every
corner of the central square carries the same creases, turned by a quarter turn. At the corner
A = (3q, 3q):

| Crease at A | Ray | In the base |
|---|---|---|
| sides of the central square | down and left | mountain |
| outer half of the diagonal, to the paper corner | 45° | mountain (the flap's spine) |
| blintz line, half toward the right edge's midpoint | 315° | valley (the swivel) |
| blintz line, other half | 135° | precrease, open |
| quarter lines, outer parts | right and up | precrease, open |
| diagonal, inner half to C | 225° | precrease, open |

So each corner of the central square is a degree-4 vertex with sectors 90°, 135°, 90° and 45°:

- **Kawasaki:** 90° + 90° = 180°, exact in rational arithmetic (slopes 0, ∞ and ±1);
- **Maekawa:** three mountains and one valley;
- **Big-little-big:** the 45° sector lies between a mountain and the valley.

Each corner square of the paper folds in half along its diagonal and becomes a flap. Its two
halves stay attached to neighbouring sides through the swivel valley and the open quarter lines.

This mountain-and-valley assignment was found by the cartridge's author. Among the flat-folded
states of these creases, it is the one with four-fold rotational symmetry and four flaps standing
out. `pliego.flatfold.check` verifies it on every run, and so does the loop-closure residual of
`target:flat-folded` (about 10⁻¹³ mm). The mirror-image windmill, which turns the other way,
swivels on the other blintz halves; this cartridge folds one handedness.

## The fold program

The program has 11 physical steps:

1. Cupboard folds, vertical and horizontal: the quarter lines, folded and unfolded.
2. Both diagonals, folded and unfolded.
3. A blintz, folded and unfolded.
4. The collapse into the windmill.

The precreases are plain hinges. The collapse is the honest limit of this cartridge. The kernel's
motion solver (`pliego.kinematics.solve`, along a chord in angle space) finds no rigid path from the
precreased sheet to the windmill. That holds for the whole collapse at once and for the first
corner on its own. The swivels need the paper to bend. So the sequence is `physical`: the key poses
are the targets the engine's paper physics drives toward, and the exact flat-folded windmill is the
`target:flat-folded` frame. The studio's preview, which has no physics, blends the fold angles
between key poses. Its in-between frames show the order of the moves, not an exact motion, and its
last frame is the exact windmill.

## Making one

1. Fold the left and right edges to the centre line and unfold; do the same with the top and bottom
   edges.
2. Fold both diagonals and unfold. Fold the four corners to the centre (a blintz) and unfold.
3. Refold the bottom and right quarter creases together. The corner between them pops up; swivel it
   out to the right and flatten.
4. Turn the paper a quarter turn and refold the next quarter crease, swivelling the next corner the
   same way. Repeat until all four flaps stand round the centre.

## Parameters

| Parameter | Meaning | Default |
|---|---|---|
| `size` | side of the square (mm) | 150 |
| `stock` | `kami`, `copy-80`, `washi-kozo-30` | `kami` |

Presets: `large-24cm` (a 240 mm square).

## History and sources

The windmill (pinwheel) is a traditional model and base. The order of the precreases and the
corner-by-corner swivel collapse follow the folding sequence described by the Origami Resource
Center («Origami Windmill Base», https://origami-resource-center.com/windmill-base/). Its geometry
is computed here, not copied. Traditional bases are surveyed in Robert J. Lang, *Origami Design
Secrets: Mathematical Methods for an Ancient Art*, 2nd ed., CRC Press, 2011. The flat-foldability
conditions are Kawasaki's and Maekawa's theorems, as presented in Thomas C. Hull, *Origametry:
Mathematical Methods in Paper Folding*, Cambridge University Press, 2020.

## Provenance and licence

Traditional base (public domain); original geometry and program by Innovaciones MADFAM. Published
under CERN-OHL-W-2.0, like every object in the commons (see the commons root `LICENSE`).
