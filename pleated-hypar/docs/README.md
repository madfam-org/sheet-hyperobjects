# Pleated hypar

| | Title | Summary |
|---|---|---|
| en | Pleated hypar | Concentric squares and both diagonals collapsed into a flat bundle that springs open into a saddle when let go, and the circular variant in concentric circles. A Bauhaus exercise; the saddle is the paper bending. |
| es | Paraboloide hiperbólico plisado | Cuadrados concéntricos y las dos diagonales cerrados en un paquete plano que se abre en una silla de montar al soltarlo, y la variante circular en círculos concéntricos. Un ejercicio de la Bauhaus; la silla es el papel que se curva. |
| fr | Paraboloïde hyperbolique plissé | Des carrés concentriques et les deux diagonales refermés en un paquet plat qui s'ouvre en selle de cheval quand on le lâche, et la variante circulaire en cercles concentriques. Un exercice du Bauhaus ; la selle, c'est le papier qui se courbe. |
| pt | Paraboloide hiperbólico plissado | Quadrados concêntricos e as duas diagonais fechados num pacote plano que se abre numa sela ao ser solto, e a variante circular em círculos concêntricos. Um exercício da Bauhaus; a sela é o papel a curvar-se. |

## What it is

Pleat a square in concentric squares, crease both diagonals, collapse it along the diagonals into a
narrow bundle and let go. It opens by itself into a saddle, a hyperbolic paraboloid or **hypar**.
Pleat a disc in concentric circles round a hole and it twists into a saddle in the same way. Both
were paper exercises in the preliminary course (*Vorkurs*) that Josef Albers taught at the
Bauhaus in 1927–28.

| Mode | Sheet | Creases |
|---|---|---|
| `square` | a square | `rings` concentric squares, alternating mountain and valley, plus both diagonals |
| `circular` | a disc with a central hole | `rings` concentric circles, alternating |

## Geometry

**Square.** The squares are spaced `size / (2·rings + 2)` apart; the outermost is a valley. The
diagonals run from corner to corner, cut into segments by the squares.

At every corner of a square the four creases leave at 45°, 45°, 135° and 135° to each other, so
**Kawasaki** holds. The two edges of the square share one assignment, so the two diagonal segments
must differ for **Maekawa** (three of one kind) to hold. The diagonal segments therefore
**alternate** along each half-diagonal. The classic instruction creases both diagonals as valleys
and lets every other segment reverse as the bundle collapses; this cartridge assigns the reversed
segments directly. At the centre four 90° sectors meet; three half-diagonals start as valleys and
one as a mountain, which makes that vertex flat-foldable too. The script runs
`pliego.flatfold.check` on every vertex:

    flatfold: square hypar rings=8 vertices=33 maekawa=ok kawasaki=ok big_little_big=ok exact=33/33

The flat bundle is therefore exact as far as local flat-foldability goes. The layer order of the
whole stack is not checked.

**Circular.** The circles are spaced evenly between the hole (`hole` × the radius) and the rim.
The kernel has no curved crease, so each circle is a regular polygon of `segments` sides inscribed
in its true circle. The sheet's outline and the hole use the same polygon. The script prints the
segmentation (the default outer chord is 13.1 mm, and the polygon departs from the circle by at
most 0.21 mm), and the first step's note states the side count and that deviation in four
languages. (Cartridge data stays out of `pliego:meta`, which carries only the spec's own keys.)

**Why neither folds rigidly.** Demaine, Demaine, Hart, Price and Tachi proved in 2011 that the
square hypar cannot take its saddle shape with flat faces and only its own creases. The paper
twists between the creases, or the pattern needs extra triangulating creases. A pleated circle
cannot stay flat either: its panels have to curve. The saddle is the bending, so it belongs to the
physics engine.

## The fold program

Both programs are `physical`, with three steps.

**Square.**

1. **Pleat the concentric squares.** Squares go to ±90°, diagonal segments to ±45°.
2. **Collapse along the diagonals.** Every crease goes to ±180°: the exact flat bundle, also stored
   as a `target:flat-folded` frame.
3. **Let go.** Every crease is released.

**Circular.**

1. **Pleat the circles.** Circles go to ±30°.
2. **Press the pleats together.** Circles go to ±60°.
3. **Let go.** Every circle is released.

**Release does not unfold** (spec §5.6). A released crease springs back only by about the stock's
yield angle and stays mostly folded. That partial springing, pulling against the pleats, is what
twists the sheet into a saddle.

**What the preview shows and what needs the physics engine.** The studio preview poses the faces
along a spanning tree. In the square mode the flat bundle (step 2) is exact. In step 1 and after
the release no rigid state exists, so the face tree opens seams. The preview applies the stock's
yield on release, so the bundle does open a little, but it cannot bend the panels into the saddle.
In the circular mode each ring is a single face hinged to its neighbour along one segment of the
polygon, so the preview shows rings tilting as flaps rather than a saddle. The saddle in both
modes comes from the physics engine (tier C).

## Making one by hand

**Square.**

1. Plot or print the pattern (SVG, PDF, DXF or HPGL) on kami or copy paper and score every line.
2. Fold the squares alternately, from the outside in, and crease both diagonals.
3. Collapse the sheet along the diagonals into a narrow X-shaped bundle and press it hard.
4. Let go. It opens into a saddle; tease the corners apart to even it out.

**Circular.**

1. Cut out the disc and its hole, and score every circle.
2. Fold the circles alternately, a little at a time all round.
3. As the pleats tighten, the disc twists into a saddle by itself.

## Parameters

| Parameter | Modes | Meaning |
|---|---|---|
| `rings` | both | number of concentric squares or circles (3–16) |
| `size` | both | sheet side (square) or diameter (circular), mm |
| `hole` | `circular` | radius of the centre hole as a fraction of the sheet's radius |
| `segments` | `circular` | sides of each circle's polygon (the segmentation) |
| `stock` | both | kami, copy paper, kozo washi or tant |

Presets: `few-rings` (4 rings) and `fine` (12 rings, 300 mm, 64 segments).

## History and sources

The pleated hypar and the concentric-circle pleat come from the paper studies of the Bauhaus
preliminary course taught by Josef Albers in 1927–28. They are among the earliest documented
pleated and curved-crease forms. Whether the hypar folds with flat faces was answered only in
2011: it does not.

- E. D. Demaine, M. L. Demaine, V. Hart, G. N. Price and T. Tachi, "(Non)existence of pleated
  folds: how paper folds between creases", *Graphs and Combinatorics* 27 (2011) 377–397. The Bauhaus
  origin, and the proof that the hypar does not fold with flat faces.
- E. D. Demaine, M. L. Demaine, D. Koschitz and T. Tachi, "Curved crease folding: a review on art,
  design and mathematics", IABSE-IASS Symposium, London, 2011. The concentric circles at the
  Bauhaus.
- H. M. Wingler, *The Bauhaus: Weimar, Dessau, Berlin, Chicago*, MIT Press, 1969. The preliminary
  course and its paper exercises.

## Provenance and licence

The two forms are credited to the Bauhaus preliminary course. The geometry is generated by this
cartridge's `main.py`, and no published crease pattern is copied. Licence: CERN-OHL-W-2.0 (the
commons' root licence).
