# Lily and iris

| | Title | Summary |
|---|---|---|
| en | Lily and iris | Two traditional flowers from the frog base: its four faces are narrowed and the flower opens about its stem, the lily with eight even petals, the iris with four at right angles. Every flat move is a checked layer-aware operation; the opening is a rigid hinge pose the preview plays. |
| es | Lirio e iris | Dos flores tradicionales desde la base de rana: se estrechan sus cuatro caras y la flor se abre alrededor del tallo, el lirio con ocho pétalos regulares, el iris con cuatro en ángulo recto. Cada paso plano es una operación por capas comprobada; la apertura es una pose rígida de bisagras que reproduce la vista previa. |
| fr | Lys et iris | Deux fleurs traditionnelles depuis la base de la grenouille : ses quatre faces sont affinées et la fleur s'ouvre autour de sa tige, le lys avec huit pétales réguliers, l'iris avec quatre à angle droit. Chaque geste à plat est une opération par couches vérifiée ; l'ouverture est une pose rigide de charnières que l'aperçu joue. |
| pt | Lírio e íris | Duas flores tradicionais a partir da base do sapo: as suas quatro faces são afinadas e a flor abre-se à volta do caule, o lírio com oito pétalas regulares, a íris com quatro em ângulo reto. Cada passo plano é uma operação por camadas verificada; a abertura é uma pose rígida de dobradiças que a pré-visualização reproduz. |

The lily and the iris are traditional flowers folded from the frog base (see `frog-base`). The
frog base is made slender by folding the lower edges of each of its four faces to the centre line,
and the flower is opened around its central axis, the stem. The two flowers share these steps; one
`flower` parameter chooses how the petals open.

## Geometry

The sheet is a square of side `size`. As in `paper-crane` and `frog-base`, nothing is drawn from a
crease pattern: every flat move is a `pliego.flatops` operation on a layer-ordered flat state, each
result is checked by `pliego.flatcheck` (a complete, consistent layer order; taco–taco,
taco–tortilla and tortilla–tortilla conditions; Kawasaki, Maekawa and big–little–big at every
vertex), and the crease pattern is the flower unfolded. The cartridge also checks that the
unfolded pattern is unchanged by a quarter turn, which shows that all four faces were narrowed
alike.

At the defaults the flat flower has 80 faces; the pattern has 72 crease lines, 38 valley,
24 mountain and 10 left flat, meeting at 35 interior vertices. The narrowing creases run from the
open end of the frog base and lay each lower edge of a face on the centre line.

The flat flower is a stack of eight half-faces, the leaves of a book whose spine is the centre
line: they meet only along it. Opening the flower turns each leaf about the spine:

- **lily**: the eight leaves at even 45° steps all the way round;
- **iris**: the leaves in pairs, four petals at right angles.

`bloom` scales every opening angle (1 opens fully, 0.5 half way).

## The fold program

The program has 27 operations, 124 steps at the defaults:

1. The preliminary base and the frog base (see `frog-base`): two folds and two squashes, four
   squashes with page turns, four petal folds with page turns.
2. Narrow each face: fold its two lower edges to the centre line. Front, then back, then turn a
   page for each of the other two faces.
3. Open the flower: every leaf turns about the spine at once, in six sub-steps.

**What the preview shows.** Every step is a rigid motion: page turns and narrowing folds are
single rotations, squashes and petal folds follow their spherical linkages, sampled until the blend
between two samples tears less than 0.5 mm (0.53 mm at one sample of the program), and the opening
turns the leaves about one axis. The opening step carries a note: it is a rigid stand-in. By hand
the petals are curled, which bends the paper; that is the physics engine's part. The document
carries the reference frames `target:flat-folded` and `target:open`.

**What differs from the hand.** Published diagrams of the lily and of the iris differ in their
later steps: which flaps are folded down before narrowing, how often the petals are narrowed, how
they are curled. This cartridge folds the steps the flowers share (the frog base and narrowed
faces) and opens the flower as rigid leaves. It does not claim to follow any one diagram.

## Making one

1. Fold a frog base, open end toward you.
2. On each face in turn, fold the two lower edges of the top layer to the centre line, turning
   pages to reach each face.
3. Hold the stem and spread the petals around it: eight for the lily, in pairs for the iris. Curl
   the petals over a pencil if you like.

## Parameters

| Parameter | Meaning | Default |
|---|---|---|
| `size` | side of the square (mm), 80–300 | 150 |
| `flower` | `lily` (eight even petals) or `iris` (four petals at right angles) | `lily` |
| `bloom` | how far the flower opens, 0.2–1 | 1 |
| `stock` | `kami`, `washi-kozo-30`, `copy-80` | `kami` |

Presets: `iris`, `half-open` (`bloom` 0.5), `large-24cm` (240 mm).

## History and sources

The lily and the iris are traditional models folded from the frog base. The frog base and its
derivation from the preliminary base are described in Robert J. Lang, *Origami Design Secrets:
Mathematical Methods for an Ancient Art*, 2nd ed., CRC Press, 2011. The layer conditions checked
here come from Marshall Bern and Barry Hayes, "The complexity of flat origami", *Proceedings of the
7th ACM-SIAM Symposium on Discrete Algorithms* (1996); Kawasaki's and Maekawa's theorems are as
presented in Thomas C. Hull, *Origametry: Mathematical Methods in Paper Folding*, Cambridge
University Press, 2020. No diagram is reproduced; the geometry, the program and the opening are
computed by this cartridge.

## Provenance and licence

Traditional models (public domain); original geometry, program and opening by Innovaciones MADFAM.
Published under CERN-OHL-W-2.0, like every object in the commons (see the commons root `LICENSE`).
