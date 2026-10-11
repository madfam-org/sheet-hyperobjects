# Curved-crease sculpture

| | Title | Summary |
|---|---|---|
| en | Curved-crease sculpture | Paper folded along curves, concentric arcs or interleaved spirals, alternately mountain and valley. The panels bend as the creases close, and the sheet takes a curved shape that holds itself up. |
| es | Escultura de pliegues curvos | Papel plegado a lo largo de curvas, arcos concéntricos o espirales entrelazadas, alternando monte y valle. Los paneles se curvan al cerrarse los pliegues y la hoja toma una forma curva que se sostiene sola. |
| fr | Sculpture à plis courbes | Du papier plié le long de courbes, arcs concentriques ou spirales entrelacées, en montagne et vallée alternées. Les panneaux se courbent quand les plis se referment, et la feuille prend une forme courbe qui tient toute seule. |
| pt | Escultura de dobras curvas | Papel dobrado ao longo de curvas, arcos concêntricos ou espirais entrelaçadas, alternando montanha e vale. Os painéis curvam-se quando as dobras fecham, e a folha toma uma forma curva que se sustenta sozinha. |

## What it is

Fold paper along a straight line and the two sides stay flat. Fold it along a curve and they
cannot: as the crease closes, the paper on both sides has to bend. The bending and the crease
balance each other, and the sheet takes a curved, self-supporting shape. This cartridge carries
two generic curved-crease patterns:

| Mode | Sheet | Creases |
|---|---|---|
| `arcs` | a rectangle (height 0.6 × width) | `arcs` concentric semicircles centred on the middle of the bottom edge, each from the bottom edge back to it |
| `spiral` | a disc with a central hole | `spirals` interleaved logarithmic spirals, each from the hole to the rim, sweeping `turns` of a turn |

In both modes the curves alternate mountain and valley; the outermost is a valley.

## Geometry

**Arcs.** The semicircles are spaced evenly, out to 0.9 × the smaller of the half-width and the
height, so every arc stays inside the sheet and ends on its bottom edge.

**Spirals.** Spiral i is `r(θ) = r₀ · e^(kθ)`, started at angle `2πi/spirals` on the hole, with k
chosen so that it reaches the rim after its sweep. Spirals with the same k are rotations of each
other, so they never cross. Each meets every circle round the centre at the same angle, which the
script prints as `angle_to_radius`. The sweep is rounded so that every spiral ends exactly on a
vertex of the rim.

**Segmentation.** The kernel has no curved crease, so every curve is written as a polyline whose
vertices lie on the true curve. The script chooses the number of segments so that no chord
strays from its curve by more than `tolerance`: the sagitta `r · (1 − cos(Δθ/2))` stays below it.
The rim and the hole of the disc are regular polygons, with sides that are a multiple of the
spiral count, so that the spirals start and end on their vertices. The script prints the counts
and the worst deviation, and the first step's note states them in four languages (cartridge data
stays out of `pliego:meta`, which carries only the spec's own keys):

    segmentation: arcs=7 segments_per_arc=10..25 max_deviation_mm=0.1989 (tolerance 0.2)
    segmentation: spirals=8 segments_per_spiral=28 rim_sides=56 sweep=180.0° angle_to_radius=58.87° max_deviation_mm=0.1852 (tolerance 0.2)

## The fold program

A curved crease has no rigid folding motion: its panels must bend. The program is therefore
`physical`, with three steps:

1. **Fold along every curve.** Every crease goes to ±30°. The step's note says that the panels
   bend.
2. **Press the curved pleats further.** Every crease goes to ±75°, and the sheet arches.
3. **Let go.** Every crease is released.

**Release does not unfold** (spec §5.6). A released crease springs back only by about the stock's
yield angle. The bent panels and the remembered creases then settle into the sculpture.

**What the preview shows and what needs the physics engine.** The studio preview poses rigid faces
along a spanning tree. Here every band between two curves is a single face, joined to its
neighbour along one segment of the polyline. The preview therefore shows each band tilting about
that segment, as a rough picture of the creases closing, not the curved shape. The curved shape is
bending, and the physics engine (tier C) computes it.

## Making one by hand

1. Plot the pattern (SVG, DXF or HPGL) and score every curve. A blunt stylus or a plotter's
   scoring tool works; on cardstock score with a ball tool along a template. Scoring is essential
   for curves, which a bone folder cannot follow.
2. Pinch each curve into its fold direction along its whole length, a little at a time,
   alternating mountains and valleys.
3. Work across the sheet repeatedly, deepening every fold. The sheet arches (arcs) or twists into
   a coiled cone (spiral).
4. Let go and let it settle; adjust by pinching.

Copy paper and 160 g/m² cardstock hold curved creases well; kami is very soft.

## Parameters

| Parameter | Modes | Meaning |
|---|---|---|
| `arcs` | `arcs` | number of concentric arcs (3–16) |
| `width` | `arcs` | sheet width, mm (height 0.6 × width) |
| `spirals` | `spiral` | number of spirals (even, 4–16) |
| `turns` | `spiral` | sweep of each spiral, in turns (0.2–1) |
| `diameter` | `spiral` | disc diameter, mm |
| `hole` | `spiral` | centre hole as a fraction of the radius |
| `tolerance` | both | largest chord-to-curve gap of the polylines, mm |
| `stock` | both | copy paper, kami, tant or 160 g/m² cardstock |

Presets: `few-curves` (4 arcs, 4 spirals) and `full-turn` (12 arcs, 12 spirals of 0.9 turn).

## History and sources

Curved-crease folding appears in the paper studies of the Bauhaus preliminary course in the late
1920s, the concentric circles among them. The computer scientist David Huffman later studied it
systematically, and in the 2000s Erik and Martin Demaine and Duks Koschitz reconstructed his
work. The two patterns here are generic geometric families, arcs of circles and logarithmic
spirals, and are not reproductions of any artist's piece.

- D. A. Huffman, "Curvature and creases: a primer on paper", *IEEE Transactions on Computers*
  C-25 (1976) 1010–1019.
- E. D. Demaine, M. L. Demaine, D. Koschitz and T. Tachi, "Curved crease folding: a review on art,
  design and mathematics", IABSE-IASS Symposium, London, 2011.
- E. D. Demaine, M. L. Demaine and D. Koschitz, "Reconstructing David Huffman's legacy in
  curved-crease folding", in *Origami⁵* (CRC Press, 2011).

## Provenance and licence

Original MADFAM work. The arcs and spirals and their segmentation are generated by this cartridge's
`main.py`. No artist's curved-crease design is copied. Licence: CERN-OHL-W-2.0 (the commons' root
licence).
