# Paper weaving

| | Title | Summary |
|---|---|---|
| en | Paper weaving | Strips of paper woven over and under: a mat in plain, twill or basket weave, and the Danish and Scandinavian woven heart basket. Every crossing is a contact, one strip above the other. |
| es | Tejido de papel | Tiras de papel tejidas por encima y por debajo: una esterilla en tafetán, sarga o panamá, y el corazón tejido de Dinamarca y Escandinavia. Cada cruce es un contacto, una tira sobre la otra. |
| fr | Tissage de papier | Des bandes de papier tissées dessus-dessous : une natte en toile, sergé ou natté, et le cœur tressé du Danemark et de Scandinavie. Chaque croisement est un contact, une bande au-dessus de l'autre. |
| pt | Tecelagem de papel | Tiras de papel tecidas por cima e por baixo: uma esteira em tafetá, sarja ou panamá, e o coração trançado da Dinamarca e da Escandinávia. Cada cruzamento é um contato, uma tira sobre a outra. |

## What it is

Paper weaving interlaces strips over and under each other, as a loom interlaces threads. This
cartridge makes two woven objects:

- **`mat`**: a woven mat, the classic classroom exercise. A loom sheet is slit into parallel bands
  (the warp) that stay joined by an uncut border at both ends, and separate weft strips are threaded
  through it, one row at a time. The `pattern` decides where a weft strip passes over or under:
  `plain` (over one, under one, shifting by one each row), `twill` (over two, under two, stepping
  by one each row, which draws diagonals) or `basket` (pairs of strips woven as one).
- **`heart`**: the woven heart basket of the Danish and Scandinavian Christmas tradition. Two
  pieces of different colours are each folded in half, with slits from the fold, so every strip is
  a loop. The loops are woven through each other: a loop of one piece goes through a loop of the
  other, then round the next one, alternately. The woven square, turned point down between the two
  round lobes, is the heart, and it opens as a pocket.

## Geometry

**Over and under as contact.** At every crossing the strip on top sits higher than the one
beneath. Each strip bends through the crossings as a chain of flat panels, a triangle wave in
section: in the mat the weft rises to +*a* where it crosses over a band and drops to −*a* where it
passes under, and the band does the opposite, so the two are 2*a* apart at the crossing
(*a* = 0.6 × the thicker stock's caliper); in the heart the four layers of a cell (each loop is two
layers) sit at four levels one gap *g* apart, *g* ≥ 1.2 × the thicker caliper. Between crossings
the strips meet only at the cells' corners, so nothing passes through anything. The bend lines are
flat lines (`F`) with treatment `none`: plain paper that the program bends, never drawn on a cut
file. The cartridge builds the document itself to set that treatment, because the authoring API
offers only creases and scores for a foldable line.

**Mat.** The loom is `warps` × `pitch` wide and `rows` × `pitch` plus two 15 mm borders tall; the
slits are 1 mm channels, so the two sides of a slit never share a vertex and each band can take its
own crimp. Weft strips are `pitch` − 1 mm wide with 10 mm tails beyond the loom. A weft strip's
tails rest 2*a* above the loom when it starts over the first band and 2*a* below when it starts
under, so an unwoven strip never touches the warp. The script checks the finished mat: at every
crossing the right strip is on top, with at least 0.14 mm between them at the default size.

**Heart.** Each piece is a stadium (a rectangle `heart_size` wide with a half-disc lobe at each
end), folded across its middle; `fingers` − 1 slits, 1 mm wide, run through the fold from lobe to
lobe. The fold is a pair of valley creases with a narrow spine between them, so the two layers of a
loop lie one or three gaps apart. The red piece's loops run along one side of the square from its
fold, the white piece's along the other; the bottom point of the heart is where the two folds meet.

## The fold program

- **`mat`**: one step per weft strip. Each step lays the strip into its row (it waits raised at the
  loom's edge, 75° up) and gives it its crimp, and re-bends the warp bands where that row now
  crosses them.
- **`heart`**: fold the red piece in half, fold the white piece in half, then weave: every loop
  takes its crimp and the layers settle into the woven order.

Threading a strip under a band, or a loop through a loop, is a topological move that a rigid fold
program cannot play: in the preview a strip passes through the warp on its way into place. The
geometry at the end of each step is exact, and a `target:woven` frame records the finished object.

**Preview and engine.** The studio preview plays every step. The physics engine adds what the
preview leaves out: real paper bending smoothly through each crossing instead of in flat panels,
friction holding the weave together, and the heart's pocket opening when it is squeezed.

## Making one by hand

- **Mat.** Fold the loom sheet in half and cut slits from the fold, stopping short of the edges;
  open it. Cut the weft strips. Weave the first strip over and under, the next one under and over
  (or following the twill or basket pattern), pushing each strip up against the last.
- **Heart.** Fold each piece in half and cut the slits from the fold through both layers, stopping
  where the lobe begins. Hold the pieces at a right angle with the folds at the bottom point. Take
  the first loop of one piece and push it through the first loop of the other, then open it and
  pass the next loop through it, alternately inside and around, to the end of the row; work the
  next loop in the opposite order. Add a handle and the heart becomes a basket.

## Parameters

| id | meaning | default | range |
|---|---|---|---|
| `pattern` | `plain`, `twill` (2/2) or `basket` (2 × 2) (mode `mat`) | `plain` | |
| `warps` | warp bands | 8 | 3–16 |
| `rows` | weft strips (one step each) | 8 | 2–16 |
| `pitch` | strip width | 15 mm | 10–30 mm |
| `heart_size` | side of the woven square (mode `heart`) | 70 mm | 40–140 mm |
| `fingers` | loops per piece | 4 | 2–8 (loops at least 8 mm wide) |

Presets: `twill-mat`, `basket-mat`, `three-loop-heart`.

## History and sources

- Woven (pleated) Christmas hearts are a Danish, Norwegian and north German craft. English
  Wikipedia dates the oldest known one to 1860, made by Hans Christian Andersen and kept at the
  Hans Christian Andersen Museum in Odense, without citing a source for it (Wikipedia, «Pleated
  Christmas hearts», https://en.wikipedia.org/wiki/Pleated_Christmas_hearts).
- Danish Wikipedia dates the oldest preserved heart, of glossy paper and cut by H.C. Andersen, to
  the 1850s, yellow and green rather than red and white, at H.C. Andersen's House in Odense, and
  gives the oldest instructions for woven two-strip hearts as Nordisk Husflidstidende, 1871, citing
  Odense City Museums (Wikipedia, «Julehjerte», https://da.wikipedia.org/wiki/Julehjerte).

The sources disagree on the decade; this article claims no more than that. The heart's tradition
belongs to the Danish and Nordic households and schools that keep it. Strip weaving in paper is a
common classroom craft and is credited to no one.

## Provenance and licence

Original MADFAM geometry: the loom, the strips, the crimp, the heart's pieces and the layer order
are computed by `main.py`; no published pattern is copied. The woven heart is credited to the
Danish and Scandinavian Christmas tradition. Published under CERN-OHL-W-2.0 like every object in
the commons (see the commons root `LICENSE`).
