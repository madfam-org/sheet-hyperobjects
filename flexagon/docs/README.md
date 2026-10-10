# Flexagon

| | Title | Summary |
|---|---|---|
| en | Flexagon | A folded paper band that shows a new face each time you flex it: trihexa-, hexahexa- and tetraflexagon from one generator, flexed through every face as an exact rigid motion. |
| es | Flexágono | Una banda de papel doblada que muestra una cara nueva cada vez que se flexiona: trihexa-, hexahexa- y tetraflexágono de un mismo generador, flexionados por todas sus caras como un movimiento rígido exacto. |
| fr | Flexagone | Une bande de papier pliée qui montre une nouvelle face à chaque flexion : trihexa-, hexahexa- et tétraflexagone issus d'un même générateur, flexés à travers toutes leurs faces selon un mouvement rigide exact. |
| pt | Flexágono | Uma faixa de papel dobrada que mostra uma face nova cada vez que é flexionada: triexa-, hexaexa- e tetraflexágono de um mesmo gerador, flexionados por todas as faces como um movimento rígido exato. |

## What it is

A flexagon is a strip of paper folded flat into a polygon and glued into a band. Pinching it (or
closing it like a book) and opening it from the other side turns faces that were hidden inside the
layers outward. This cartridge is one family with three styles:

- **`trihexa`**: a strip of 9 equilateral triangles plus a glue triangle, folded into a hexagon.
  Three faces show in the cycle 1 → 2 → 3 → 1.
- **`hexahexa`**: 18 triangles plus a glue triangle. The strip is first coiled (every other cell
  folded onto its neighbour) and then folded like the trihexaflexagon. Six faces; the program
  follows a Tuckerman traverse (flex at the same corner until it will not open, then move one
  corner over): 1-2-3-1-2-4-5-2-4-1-6-4-1, twelve flexes.
- **`tetra`**: a staircase strip of 8 squares plus a glue square, folded into a 2 × 2 square. It
  flexes by the book flex (close it in half, open it from the back) through four faces,
  1 → 2 → 3 → 4 → 1.

Two modes: **`make`** folds the flat strip into its flat state, one fold per step, and ends by
gluing the last cell onto the first; **`flex`** is the glued flexagon, flexed through every face
and back to the start.

## Geometry

The strip is a chain of cells (triangles of side `side`, or squares), each hinged to the next along
a shared edge, so it is printed and cut as one piece; the last cell is the glue cell. The script
folds the chosen hinges flat and checks that every cell lands around one centre, then reads the
**flat state**: N sectors (6 or 4) around the centre, each holding a stack of cells (a pat), and a
role for each cell corner (centre, one radius, the other radius, far corner).

The layer order of each pat is part of the design. It is stored per style and verified: folds on
one edge nest, nothing passes through a fold, strands that cross a radius keep their order, and the
glue cell lies directly on cell 1. A folded hinge is a valley when the next cell lies on the front
side of the cell before it, so the fold signs follow from the layers.

Each face gets an original colour and pattern (rings, a sunburst, a dot lattice, nested polygons,
petals, cross-hatching) and its number. The pattern is drawn in the frame of the flat state where
the face first shows, so it reads whole there; in the hexahexaflexagon some faces later come back
with their cells rearranged, which is the toy's famous trick. The back of each cell is printed as
seen from the back, and the two glued sides carry a hatching.

## The flex

A flex is a rigid motion of the cells in two phases.

1. **Close the centre.** Every other radius (the spines) folds to 180° while the pats pair into
   fins: a three-pointed star for the hexaflexagons, a closed book for the tetraflexagon. This is
   a single vertex of degree 6 (or 4). Its path is solved with `pliego.kinematics.solve` on that
   vertex, and each solved state is matched to the symmetric closed form, in which the spines fold
   to 2e while the other radii rise to elevation e (the largest mismatch is printed,
   about 0.004°).
2. **Open the far vertex.** In the closed state all the fins meet at a second vertex T. Each fin
   splits into two contiguous blocks of layers, which unfold around T into the next flat state.
   The split follows from the hinges: a fold on a spine radius or on a far edge never splits, a
   fold on the radius between two fins joins the right pair of new sectors, and a fold on the edge
   through T may open. The new layer order passes the same checks as the first one.

The fold angle of every hinge is the signed dihedral between its two posed cells (valley > 0, the
kernel's convention, with the sign of a 180° fold carried over from the previous state). Every
state is checked: no hinge tears and the glue cell stays on cell 1. The program flexes until the
flexagon comes back to its first state with every face shown.

**Preview and engine.** The whole program plays in the studio preview, which rebuilds each pose
from the hinge angles. The physics engine adds what paper does beyond the rigid model: the slack
of real hinges, the slight bending that lets a flexagon open, and friction between layers.

## Making one by hand

1. Export the strip (`svg`, `pdf`, `dxf` or `hpgl`). The `svg` carries the printed front; print
   the back (stored in the document's sheet art, drawn as seen from the back) on the reverse,
   or colour the faces by hand using the numbers.
2. Cut the outline, then crease every line both ways: flexagons need hinges that turn freely.
3. Follow the `make` program: fold at the lines it names (the small numbers are the cells), and
   for the hexahexaflexagon coil the strip first. Glue the last cell onto cell 1.
4. Flex: pinch two neighbouring triangles together so the hexagon closes into a star, then open
   it from the centre; if it will not open, try the next corner. For the tetraflexagon, close it
   in half like a book and open it from the back.

## Parameters

| id | meaning | default | range |
|---|---|---|---|
| `style` | `trihexa`, `hexahexa` or `tetra` | `trihexa` | |
| `side` | side of each triangle or square | 40 mm | 20–80 mm |
| `palette` | colours of the printed faces: `bright` or `earth` | `bright` | |
| `stock` | `copy-80`, `kami` or `cardstock-160` | `copy-80` | |

Presets: `hexahexa` (30 mm cells), `tetra`, `large-earth` (60 mm, earth colours).

## History and sources

Arthur H. Stone found the trihexaflexagon in 1939 as a graduate student at Princeton: his
American paper did not fit his English binder, so he cut off the ends and folded the strips. With
his colleagues Bryant Tuckerman, Richard Feynman and John Tukey he formed the Princeton Flexagon
Committee; Tuckerman worked out the traverse that reveals every face. Martin Gardner introduced
flexagons to the public in *Scientific American* in December 1956, in an article that launched his
Mathematical Games column; square flexagons (tetraflexagons) belong to the same family. Sources: M. Gardner, "Flexagons", *Scientific American* 195 (6), December 1956;
M. Gardner, *Hexaflexagons and Other Mathematical Diversions* (1959); Wikipedia, «Flexagon»,
https://en.wikipedia.org/wiki/Flexagon. The staircase strip of the tetraflexagon was found by this
cartridge's own search for a strip of squares that flexes through four faces; no claim is made that
it matches a published net.

## Provenance and licence

Original MADFAM geometry, layer orders, motions and artwork, generated by `main.py`; the toy is
credited to its history above. Published under CERN-OHL-W-2.0 like every object in the commons
(see the commons root `LICENSE`).
