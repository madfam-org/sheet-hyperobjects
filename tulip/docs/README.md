# Tulip

| | Title | Summary |
|---|---|---|
| en | Tulip | The traditional flat tulip as a two-sheet assembly: a blossom with two petals and a stem with a leaf, each folded from its own square by simple folds solved as exact rigid motions, then slid together. |
| es | Tulipán | El tulipán plano tradicional como ensamble de dos hojas: una flor con dos pétalos y un tallo con hoja, cada uno doblado de su propio cuadrado con pliegues simples resueltos como movimientos rígidos exactos, y luego unidos deslizándolos. |
| fr | Tulipe | La tulipe plate traditionnelle en assemblage de deux feuilles : une fleur à deux pétales et une tige avec sa feuille, chacune pliée dans son propre carré par des plis simples résolus en mouvements rigides exacts, puis glissées l'une dans l'autre. |
| pt | Tulipa | A tulipa plana tradicional como montagem de duas folhas: uma flor com duas pétalas e um caule com folha, cada um dobrado do seu próprio quadrado com dobras simples resolvidas como movimentos rígidos exatos, e depois encaixados. |

The flat tulip is one of the first models children fold. The blossom is a square folded into a
triangle with its side corners folded up as petals. The stem is a second square, folded into a
kite, narrowed, folded in half, with its wide end folded out as a leaf. The stem's point goes into
the bottom of the blossom. This cartridge folds both pieces and then puts them together.

## Geometry

Both pieces start as squares held as diamonds, one diagonal vertical. The blossom's square has
half-diagonal d = `blossom_size`/√2; the stem's has e = `stem_size`/√2.

**Blossom.**

1. The horizontal diagonal folds the top corner down to the bottom: a triangle, point down.
2. Each petal fold runs from the top edge, at `petal`·d from the centre, to a point 0.1·d beside the
   bottom point. The side corner swings up across it and rises above the top edge. The default
   (`petal` = 0.7) lifts each petal tip about 0.28·d above the edge. The parameter is limited to
   0.62 to 0.8 so that the fold stays clear of the bottom point and the corner always rises.

**Stem and leaf.**

1. The kite: the two edges at the top corner P fold onto the vertical diagonal along lines from P
   at 22.5° to it.
2. Narrowing: the new edges fold onto the diagonal again, along lines from P at 11.25°, each
   through two layers.
3. The stem folds in half along the diagonal, through every layer.
4. The leaf: everything below a slanted line from the axis at 0.45·e below the centre folds up and
   out.

Each step is a simple fold of a flat stack. `pliego.simplefold` folds the stack and records, in
every layer the fold line crosses, the crease it leaves, with its sense: valley on a layer that
faces up, mountain on one that is turned over. A crease through three layers is three crease
segments in the pattern. The cartridge authors those segments as the sheet's creases, so the
crease pattern is computed, not drawn. Every interior vertex has degree four (three on the stem,
two on the blossom). Each is a place where a later fold crosses an earlier crease that is already
folded flat, so both layers turn together.

`pliego.flatfold.check` tests Maekawa, Kawasaki and big-little-big on both folded patterns every
time the cartridge runs. Where the leaf fold crosses the right kite crease, the two small sectors
are equal in exact geometry (39.2894°), and grid snapping can make them differ by about 10⁻⁵°.
The lemma applies to a strictly smallest sector, so the cartridge counts such a vertex
(`blb_equal_sectors`) rather than failing on it, and fails on any other error. With the kernel
this cartridge was last checked against, no vertex needs that allowance (`blb_equal_sectors=0`).

## The fold program

The program has 54 kinematic steps: 36 for the stem (six folds of six steps) and 18 for the
blossom (three folds of six). While it runs, the blossom comes down the stem, and the last fold
ends with the stem's point inside the blossom.

Each fold is a key pose, and the kernel's motion solver (`pliego.kinematics.solve`) expands it into
exact rigid states, holding every other crease. A simple fold of a flat stack is a rotation of part
of the stack about one line, so it is rigid. The cartridge tries chord continuation first. Where the
solver's branch analysis does not settle, as in the leaf fold, it drives the crease angles
linearly, which is the exact motion of a simple fold. The worst loop residual is about 10⁻⁷ rad.
That floor comes from the grid-snapped crease crossings at irrational positions on the 22.5° kite
lines. The folded state of each piece is checked for closure: the stem to about 2·10⁻⁵ mm, the
blossom to about 10⁻¹³ mm. The document carries `target:folded` with both pieces folded.

The slide is the blossom sheet's presentation (spec §5.16): a rigid end transform that a viewer
blends in over the program, from none at step 0 to all of it at step 54. The studio preview and
the engine's render both apply it; it moves no physics. The cartridge computes it from the
folded geometry. The blossom starts on the stem's axis, with its bottom point 0.5·d beyond the
stem's point (twice the insertion), and slides 0.75·d down the stem, until the stem's point is
0.25·d inside the blossom. Because the blend is linear in the step position, the bottom point
reaches the stem's point at step 36, just as the stem's last fold ends, so the flat blossom never
lies over the stem while the stem is folding. Each sheet's presentation also names its root face,
the face the preview holds still while that sheet folds: the stem's base layer beside its point
and the blossom's body. The engine's kinematic program does not read the root face yet; it holds
each sheet's first face, so its render of the folded pieces, and of where the blossom lands, is
not the preview's until it does.

Earlier versions moved the blossom with a `translate` mechanism and an `assemble` control. A
mechanism may move only a rigid (kinematic) sheet (spec §8, rule 15), and a rigid sheet cannot
fold, so the engine refused the document; the presentation slide replaces it.

What the program does **not** model:

- **No contact.** The stem's point slides between the blossom's layers in the real model. Here the
  blossom is placed half a millimetre above the stem: zero-thickness geometry cannot hold one piece
  inside the other.
- **No inflation.** Some versions blow the blossom open into a 3-D bloom. This flat tulip stays
  flat.

## Making one

1. **Blossom:** fold a square in half along a diagonal, point down. Fold each side corner up from
   just beside the bottom point so that it stands above the top edge.
2. **Stem:** with the green side down, fold the two edges at one corner onto the diagonal. Fold the
   new edges onto the diagonal again, then fold the stem in half lengthwise.
3. **Leaf:** fold the wide end up and out at a slant.
4. Slide the stem's point into the bottom of the blossom.

## Parameters

| Parameter | Meaning | Default |
|---|---|---|
| `blossom_size` | side of the blossom's square (mm) | 150 |
| `stem_size` | side of the stem's square (mm) | 150 |
| `petal` | where each petal fold meets the top edge, as a fraction of the half-diagonal (0.62 to 0.8) | 0.7 |
| `stock` | `kami`, `copy-80`, `washi-kozo-30` | `kami` |

The stem is coloured green on its front (its sheet's own face colour) whatever the stock. Presets:
`small-stem` (a 110 mm stem square), `tall-petals` (`petal` = 0.78).

## History and sources

The flat tulip with a stem is a traditional first-lesson model, credited here to that tradition.
The easy blossom, a triangle with its side corners folded up as petals, is published for beginners
in many places, for example Instructables, «Origami Tulip (Easy)»,
https://www.instructables.com/Origami-Tulip-Easy. The stem's first fold is the kite base, described
among the classic bases in Robert J. Lang, *Origami Design Secrets: Mathematical Methods for an
Ancient Art*, 2nd ed., CRC Press, 2011. No diagram is reproduced; the folds and their angles are
chosen and computed by this cartridge.

## Provenance and licence

Traditional model (public domain); original geometry and program by Innovaciones MADFAM. Published
under CERN-OHL-W-2.0, like every object in the commons (see the commons root `LICENSE`).
