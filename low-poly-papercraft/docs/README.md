# Low-poly papercraft

| | Title | Summary |
|---|---|---|
| en | Low-poly papercraft | A family of original low-poly paper models (a heart, a ringed planet, a vase, a gem, a fox head, a mask and a car), each unfolded into numbered, tabbed pieces on pages, with a program that folds the pieces into the model. |
| es | Papercraft low-poly | Una familia de modelos de papel low-poly originales (un corazón, un planeta con anillos, un jarrón, una gema, una cabeza de zorro, una máscara y un coche), cada uno desplegado en piezas numeradas y con pestañas sobre hojas, con una secuencia que dobla las piezas hasta formar el modelo. |
| fr | Papercraft low-poly | Une famille de modèles en papier low-poly originaux (un cœur, une planète à anneaux, un vase, une gemme, une tête de renard, un masque et une voiture), chacun déplié en pièces numérotées à languettes sur des pages, avec un programme qui plie les pièces jusqu'au modèle. |
| pt | Papercraft low-poly | Uma família de modelos de papel low-poly originais (um coração, um planeta com anéis, um vaso, uma gema, uma cabeça de raposa, uma máscara e um carro), cada um desdobrado em peças numeradas e com abas em folhas, com uma sequência que dobra as peças até formar o modelo. |

## What it is

**Low-poly papercraft** builds a model out of a few dozen flat faces of card. The facets are the
look: the model is faceted on purpose, and every face is a piece of paper you can see. This object
is one family of such models, all original MADFAM designs, selected by the `design` parameter:

| design | how it is built | open or closed |
|---|---|---|
| `heart` | a heart outline extruded into a slab, both faces bevelled toward a smaller copy (a pillow heart) | closed |
| `planet` | one surface of revolution that climbs a faceted sphere, runs out along a flat ring and back, then tilted 20° | closed |
| `vase` | a surface of revolution with a flat foot and an open mouth | open (the lip) |
| `gem` | a surface of revolution: pointed pavilion, girdle band, crown and flat table | closed |
| `fox` | the convex hull of a few control points (long snout, wide cheek ruff), with two pyramid ears raised from the faces nearest the ear positions | closed |
| `mask` | a patch of an ellipsoid, narrowed toward the chin, with a raised nose and brow ridge and two eye holes | open (outline and eyes) |
| `car` | the side profile of a small car, wheels drawn into it, extruded across the car's width: the paper-toy car | closed |

Each design comes out as printable pages and a folding program, from the same unfolder as
`papercraft-unfold`. Like that object, it has two modes: `fold`, the kinematic fold-up, and
`glued`, the finished model held by glue, for the paper physics engine.

## Geometry

Every mesh is generated in `main.py` from the kernel's mesh primitives (`pliego.mesh`): `prism`,
`lathe`, `hull`, `extrude`, and affine maps. Each design's details:

- **Heart.** The outline is 14 samples of the classic parametric heart curve
  x = 16 sin³t, y = 13 cos t − 5 cos 2t − 2 cos 3t − cos 4t (see the sources). Extruding a face
  toward a copy scaled about its centroid keeps every bevel quad planar: the near and far edges
  lie on lines through one point.
- **Planet.** The lathe's profile runs from the south pole through latitudes at 28°, 56° and
  80°, out to the ring's outer edge at 1.7 radii, back in 0.08 radii higher, and on to the north
  pole. Sphere and ring are therefore one closed surface, with no glue line where they meet.
- **Vase and gem.** The lathe makes every quad between two rings an isosceles trapezoid, which is
  planar.
- **Fox.** A convex hull is the simplest closed surface through chosen points. The face nearest
  each ear position is extruded to a single apex (`shrink` 0), which raises a triangular pyramid.
- **Mask and other bent surfaces.** Quads that are not planar are split along their shorter
  diagonal, so every face is a flat piece of card.

`pliego.unfold.net()` then does what kernel.md §5 describes. It scales the model to `size`
(the largest dimension) and grows a cut tree greedily: two pieces are joined only when the result
does not overlap itself, keeps room for its tabs, and fits the page. Each cut gets its number on
both sides and one glue tab, alternating sides. Mountain or valley comes from each edge's 3-D
dihedral, and the pieces are packed onto A4 or Letter pages. On the open designs (`vase`, `mask`),
edges that border a single face are plain cut edges with no tab. Every fold line is a score line
on card stock.

The front faces print in each design's colour in the studio (heart red, planet sand, vase blue,
gem teal, fox orange, mask cream, car blue). On paper, the colour is the card you print on.

## The fold program

**`fold` mode (kinematic).** One sheet per piece. The steps:

1. *Fold the glue tabs in*: every tab to the angle of its cut, which puts the tab in the plane of
   the face it is glued under.
2. *Fold piece N into shape*, one step per piece. The step's note lists the edge numbers to glue.

Every piece is a tree of faces with no fold line meeting another inside it, so every
intermediate state is rigid and exact. The last step shows the finished model, and the document
carries it as a `target:assembled` frame.

**`glued` mode (physical).** The assembled model is the initial frame. A glue join sits under
every tab, each weld checked to the card's contact thickness. Every crease carries its fold angle
as crease memory, since the card was folded before it was glued. One step lets go of all of them.

**Preview limits.**

- The fold-up is kinematic: each piece folds in place about its first face, starting flat in that
  face's plane. Nothing carries flat pieces in from the table; whole-piece moves need rigid
  (kinematic) sheets, and a folding piece is not rigid.
- In the preview, `glued` mode stands still. The glue, the card's springback and the model's
  settling need the physics engine.

## Making one by hand

1. Print the PDF at 100 % on 160–300 g/m² card. Coloured card gives the model its colour. The PDF
   prints one sheet of paper per page of the layout, and each piece carries its name underneath.
2. Score every fold line against a ruler with an empty ballpoint pen or a bone folder.
3. Cut out the pieces, tabs included. For the mask, also cut out the eye holes.
4. Pre-fold every line. Most folds are mountains (the printed side stays out). The valley folds
   are where the surface turns inward: the heart's notch, the planet where the ring meets the
   sphere, the vase's neck, the base of the fox's ears, around the mask's nose and eyes, and the
   car's windscreen and wheel arches. The gem has none.
5. Glue tab by tab, each one under the edge with the **same number**, largest piece first. Close
   the last edges from the inside with tweezers.
6. For the mask: punch a hole near each side edge and tie an elastic cord through.

## Parameters

| Parameter | Meaning |
|---|---|
| `design` | heart, planet, vase, gem, fox, mask or car |
| `size` | largest dimension of the finished model, mm |
| `page` | A4 or US Letter |
| `method` | cutting strategy: shortest cuts (long edges stay folded) or steepest edge |
| `tab_style` | trapezoid, triangle or none |
| `tab_angle` | angle between a tab's sides and its fold, degrees |
| `tab_height` | the tallest a tab may be, mm |
| `stock` | card weight (160, 250 or 300 g/m²) |

Presets: one per design at a size that prints on two to four pages. The fox is the default. The
mask preset is at wearable size on Letter, and the vase preset uses the steepest-edge strategy,
which gives it fewer pieces.

## History and sources

- Cutting a solid's surface open along its edges and laying it flat goes back at least to
  Albrecht Dürer's *Underweysung der Messung* (1525), whose polyhedra are drawn as nets.
- The theory behind an unfolder that may split a model into pieces: E. D. Demaine and
  J. O'Rourke, *Geometric Folding Algorithms: Linkages, Origami, Polyhedra*, Cambridge University
  Press, 2007, Part III.
- The heart outline: E. W. Weisstein, "Heart Curve", *MathWorld*, Wolfram Research
  (mathworld.wolfram.com/HeartCurve.html).

## Provenance and licence

Original MADFAM designs. Every model is generated by this cartridge's `main.py` from the
kernel's mesh primitives, and unfolded by `pliego.unfold`. No commercial papercraft model, pattern
or Pepakura file was copied, traced or used as a reference. Object licence: CERN-OHL-W-2.0 (the
commons' root LICENSE); the kernel is AGPL-3.0.
