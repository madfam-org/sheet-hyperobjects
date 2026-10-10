# Kaleidocycle

| | Title | Summary |
|---|---|---|
| en | Kaleidocycle | A ring of 6, 8 or 10 tetrahedra hinged edge to edge that turns through its own centre without end, folded from one band and turned along its exact closed-loop motion. |
| es | Caleidociclo | Un anillo de 6, 8 o 10 tetraedros unidos arista con arista que gira a través de su propio centro sin fin, doblado a partir de una sola banda y girado según su movimiento exacto de lazo cerrado. |
| fr | Kaléidocycle | Un anneau de 6, 8 ou 10 tétraèdres articulés arête contre arête qui tourne sans fin à travers son propre centre, plié dans une seule bande et tourné selon son mouvement exact en boucle fermée. |
| pt | Caleidociclo | Um anel de 6, 8 ou 10 tetraedros articulados aresta com aresta que gira através do próprio centro sem fim, dobrado a partir de uma única faixa e girado segundo o seu movimento exato de laço fechado. |

## What it is

A kaleidocycle is a ring of congruent tetrahedra. Each one is joined to the next along an edge, and
the joints act as hinges, so the whole ring can be turned inside out through its centre, over and
over. Turning it brings different sets of faces to the outside. The classic ring has six links;
rings of eight and ten also turn, and leave a hole in the middle.

Two modes: **`turn`** is the glued ring (glue joins and an exact initial frame) turning through a
full cycle; **`make`** folds the flat band into the ring.

## Geometry

Each tetrahedron has two opposite edges as hinges: AB to the previous link, CD to the next. They
are perpendicular, both `hinge` long, and `height` apart along their common perpendicular, which
passes through both midpoints. The four faces are equal isosceles triangles with base `hinge` and
legs √(`hinge`²/2 + `height`²).

**The net** is one band of `links` rows. A row is a strip of four triangles (ABC, ACD, ABD, BCD)
that folds into one tetrahedron; its seam BC closes with a glue tab. Rows meet along the hinges,
alternately along both copies of the hinge edge (the next row shifted left by half a hinge) and
along one (shifted right), so the band runs straight and the attachments alternate: the next
link's A lands on this link's D, then on C. A last tab closes the ring. Where two rows meet along
both copies, the net has an interior vertex of degree 6. The printed patterns are original: the
four faces of every link each get one colour and motif (nested triangles, stripes, dots, rays), so
four colour sets take turns on the outside as the ring turns.

The script checks the folded net in every state: shared edges meet, every face prints outward, and
each glue tab lies inside its glue face.

## The mechanism

Each hinge is a revolute joint, so the ring is a closed chain of N rigid links. With the
alternating attachments it closes, meaning that the product of the N link transforms is the
identity, on a one-parameter loop of hinge angles: the hinges alternate between two angles
(a, b) = r(θ)·(cos θ, sin θ). The script solves r by Newton for each θ, from 0 to 360°, and one turn
of θ is one full cycle of the ring. Every hinge swings between ±720°/N (±120° for six links, ±90°
for eight, ±72° for ten).

The ring's closure runs through glue seams, which the 0.2 motion solver does not model (it closes
vertex loops), so the closure is solved here. The program is `Sequence.kinematic_path` over 72 key
states, 5° of the loop apart. Its solver brings each state onto the net's own vertex loops, and the
read-proof line reports the worst vertex residual (about 1e-8 rad) and the widest seam gap (zero
at every step). Between two steps the preview blends the angles, which opens the seams by at most
about 0.4 mm for a 40 mm ring.

**Limits.** A hinge cannot swing past 180° minus the tetrahedron's dihedral angle at that edge,
2·atan(`hinge` / 2·`height`), or neighbours would pass into each other. The script refuses
proportions that cannot reach ±720°/N with a 2° margin, and checks the other links point by point
for collisions in every key state.

**Preview and engine.** The whole cycle plays in the studio preview. The physics engine adds the
friction and slack of real paper hinges, which is what lets a hand-made ring turn smoothly.

## Making one by hand

1. Export the band (`svg` with the printed patterns, or `pdf`, `dxf`, `hpgl`) on light card.
2. Cut the outline, score every line, and pre-fold them all: the folds between triangles of a row
   go away from the print, and so do the tabs.
3. Fold each row into a tetrahedron and glue its tab inside. The `make` program shows the whole
   folding as one motion.
4. Bring the last row round and glue the ring tab onto the first row. Let the glue dry, then turn
   the ring through its centre with your fingertips.

## Parameters

| id | meaning | default | range |
|---|---|---|---|
| `links` | tetrahedra in the ring | 6 | 6, 8, 10 |
| `hinge` | length of each hinge edge | 40 mm | 20–80 mm |
| `height` | distance between a link's two hinges | 40 mm | 12–160 mm (clamped to 0.3–2 × `hinge`) |
| `palette` | colours: `bright` or `earth` | `bright` | |
| `stock` | `cardstock-160`, `copy-80` or `kraft-120` | `cardstock-160` | |

Presets: `octagonal` (8 links), `decagonal` (10 links, 30 × 30 mm), `slender` (30 × 50 mm, earth
colours).

## History and sources

The American designer Wallace Walker found the underlying net in 1958 during a paper-structures
project, patented it as the IsoAxis, and coined the word kaleidocycle from the Greek for beautiful,
form and ring. His work led Doris Schattschneider at Moravian College to the ring of tetrahedra, and
in 1977 the two published *M. C. Escher Kaleidocycles*, rings printed with Escher's patterns.
Sources: D. Schattschneider and W. Walker, *M. C. Escher Kaleidocycles* (1977); Wikipedia,
«Kaleidocycle», https://en.wikipedia.org/wiki/Kaleidocycle. No Escher artwork and no published net
is reproduced here: the band, its tabs and its patterns are generated by this cartridge.

## Provenance and licence

Original MADFAM geometry, motion and artwork, generated by `main.py`; the object is credited to its
history above. Published under CERN-OHL-W-2.0 like every object in the commons (see the commons root
`LICENSE`).
