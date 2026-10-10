# Blintz base

| | Title | Summary |
|---|---|---|
| en | Blintz base | The four corners folded to the centre, once (single blintz) or twice (double blintz). The second blintz folds through two layers, so its creases line up into the quarter lines and meet the first at four exact degree-6 vertices. |
| es | Base blintz | Las cuatro esquinas dobladas al centro, una vez (blintz sencillo) o dos (blintz doble). El segundo blintz dobla a través de dos capas, así que sus pliegues se alinean en las líneas de los cuartos y se encuentran con los primeros en cuatro vértices exactos de grado 6. |
| fr | Base blintz | Les quatre coins rabattus au centre, une fois (blintz simple) ou deux (blintz double). Le second blintz plie à travers deux couches, si bien que ses plis s'alignent sur les lignes des quarts et rencontrent les premiers en quatre sommets exacts de degré 6. |
| pt | Base blintz | Os quatro cantos dobrados ao centro, uma vez (blintz simples) ou duas (blintz duplo). O segundo blintz dobra através de duas camadas, por isso os seus vincos alinham-se nas linhas dos quartos e encontram os primeiros em quatro vértices exatos de grau 6. |

To blintz a square is to fold its four corners to the centre. The result is a square of half the
area, with the four corners meeting in the middle. The name comes from the blintz, a pastry folded
the same way. Blintzing is a step in many traditional models, and blintzing a square before
folding a base (a blintzed bird base, for example) gives every flap an extra point. A double blintz
folds the four new corners to the centre again, leaving a square of a quarter of the area.

## Geometry

The sheet is a square of side `size`, with edge midpoints E, N, W and S and q = `size`/4.

**Single blintz.** Four valley creases join consecutive edge midpoints: E–N, N–W, W–S, S–E. Each
is the perpendicular bisector of the segment from a corner to the centre, so the corner lands
exactly on the centre. The creases meet only at the midpoints, which are on the boundary, so the
folded pattern has no interior vertex. Every corner fold is an independent hinge. Two book folds
are precreased to find the centre; they are open in the base.

**Double blintz.** The half-size square has its corners at E, N, W and S. Each of these folds to the
centre along a line that crosses three layers: the base and two of the folded corners. Its crease
pattern therefore has three segments:

- a **valley** on the base, a side of the inner square of side `size`/2;
- two **mountains** on the folded corners, which lie back side up. Reflected back through the
  first blintz, each runs from a corner of the inner square straight out to the paper's edge.

The segments line up into the four quarter lines x = q, x = 3q, y = q and y = 3q. Each corner of the
inner square, for example (3q, 3q), is a degree-6 vertex: two first-blintz rays, two valleys on the
base and two mountains on the flaps. Its sectors are 90°, 45°, 45°, 90°, 45°, 45°:

- **Kawasaki:** 90° + 45° + 45° = 180°, exact in rational arithmetic (slopes 0, ∞, ±1);
- **Maekawa:** four valleys and two mountains;
- **Big-little-big:** each 45° sector lies between creases of opposite kinds.

`pliego.flatfold.check` runs these tests on the folded creases every time the cartridge runs.

## The fold program

**Single blintz:** 34 kinematic steps. Fold and unfold each book fold (14 steps), then fold the four
corners to the centre one by one (5 steps each).

**Double blintz:** the same 34 steps, then the four new corners folded to the centre one by one, 6
steps each, for 58 steps in all.

`pliego.Sequence.kinematic_path` expands each key pose into exact rigid in-between states. A
second-blintz fold turns three coincident layers about one line in the folded state. In the crease
pattern that is three creases rotating together, with opposite signs on the base and on the
flipped flaps. The kernel solves it as a rigid motion with the first blintz held flat, and every
loop closes to rounding error. The finished base is the `target:flat-folded` frame; the double
blintz also carries `target:single-blintz`.

What the program does **not** model:

- **No layer contact or thickness.** Four layers meet at the centre of a double blintz. Rigid
  kinematics stacks them at zero thickness; real paper needs a little room at each fold, and thick
  stock rounds the corners off.
- **No crease memory.** The precreased book folds are exactly flat again in kinematic mode.

## Making one

1. Fold the square in half both ways and unfold, to mark the centre.
2. Fold each corner to the centre. That is a single blintz.
3. For a double blintz, fold each of the four new corners to the centre as well, through both
   layers. Crease firmly: there are four layers at the centre.

## Parameters

| Parameter | Meaning | Default |
|---|---|---|
| `size` | side of the square (mm) | 150 |
| `stock` | `kami`, `copy-80`, `washi-kozo-30` | `kami` |
| `blintz` | `single` or `double` | `single` |

Presets: `double`, `double-large` (a double blintz from a 240 mm square).

## History and sources

The blintz fold is a traditional technique, named in English after the blintz pastry. Blintzing a
base is described in Robert J. Lang, *Origami Design Secrets: Mathematical Methods for an Ancient
Art*, 2nd ed., CRC Press, 2011. The flat-foldability conditions checked here are Kawasaki's and
Maekawa's theorems, as presented in Thomas C. Hull, *Origametry: Mathematical Methods in Paper
Folding*, Cambridge University Press, 2020. No diagram is reproduced; the geometry is computed by
this cartridge.

## Provenance and licence

Traditional technique (public domain); original geometry and program by Innovaciones MADFAM.
Published under CERN-OHL-W-2.0, like every object in the commons (see the commons root
`LICENSE`).
