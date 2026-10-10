# Platonic solids

| | Title | Summary |
|---|---|---|
| en | Platonic solids | The five Platonic solids (tetrahedron, cube, octahedron, dodecahedron and icosahedron), one by one or as a set, sized by edge or by the sphere around them and unfolded into tabbed, numbered card nets on pages, with a program that folds each net ring by ring into its solid. |
| es | Sólidos platónicos | Los cinco sólidos platónicos (tetraedro, cubo, octaedro, dodecaedro e icosaedro), uno por uno o en juego, medidos por la arista o por la esfera que los rodea y desplegados en plantillas de cartulina con pestañas y aristas numeradas, sobre hojas, con una secuencia que dobla cada plantilla, anillo por anillo, hasta cerrar su sólido. |
| fr | Solides de Platon | Les cinq solides de Platon (tétraèdre, cube, octaèdre, dodécaèdre et icosaèdre), un par un ou en jeu, dimensionnés par l'arête ou par la sphère qui les entoure et dépliés en patrons de bristol à languettes et arêtes numérotées, sur des pages, avec un programme qui plie chaque patron, couronne par couronne, jusqu'à son solide. |
| pt | Sólidos platônicos | Os cinco sólidos platônicos (tetraedro, cubo, octaedro, dodecaedro e icosaedro), um a um ou em conjunto, medidos pela aresta ou pela esfera que os envolve e desdobrados em moldes de cartolina com abas e arestas numeradas, em folhas, com uma sequência que dobra cada molde, anel por anel, até fechar o sólido. |

## What it is

A **Platonic solid** is a convex solid whose faces are all the same regular polygon, with the
same number of faces meeting at every corner. There are exactly five:

| `solid` | faces | at each corner | edges | corners | Plato's element |
|---|---|---|---|---|---|
| `tetrahedron` | 4 triangles | 3 | 6 | 4 | fire |
| `cube` | 6 squares | 3 | 12 | 8 | earth |
| `octahedron` | 8 triangles | 4 | 12 | 6 | air |
| `dodecahedron` | 12 pentagons | 3 | 30 | 20 | the whole |
| `icosahedron` | 20 triangles | 5 | 30 | 12 | water |

This object makes any of them out of one sheet of card: a **net**, the solid's surface cut open
along some of its edges and laid flat, with glue tabs and matching numbers on the edges to join.
`solid` picks one, or `set`, all five side by side at the same size. In the studio each face is
coloured by Plato's element (our colours; on paper the colour is the card you print on).

## Geometry

Each solid is generated in `main.py` from its corner coordinates, with φ = (1 + √5)/2 the golden
ratio:

- tetrahedron: four alternate corners of a cube, (±1, ±1, ±1) with an even number of minus signs;
- cube: (±1, ±1, ±1);
- octahedron: (±1, 0, 0), (0, ±1, 0), (0, 0, ±1);
- dodecahedron: the cube's corners plus (0, ±1/φ, ±φ), (±1/φ, ±φ, 0) and (±φ, 0, ±1/φ);
- icosahedron: (0, ±1, ±φ), (±1, ±φ, 0) and (±φ, 0, ±1).

The kernel's convex hull (`pliego.mesh.hull`) turns the corners into faces and merges coplanar
triangles, so the dodecahedron's faces come out as true pentagons. The solid is turned to stand on
a face and scaled so that the chosen `measure` equals `size`:

- **sphere radius** (circumradius *R*), the radius of the sphere through every corner. All five
  then fit the same ball, as Euclid builds them in Book XIII. The edges at *R* are 1.633 *R*
  (tetrahedron), 1.155 *R* (cube), 1.414 *R* (octahedron), 0.714 *R* (dodecahedron) and
  1.051 *R* (icosahedron);
- **edge length** *a*: every edge is `size` mm.

`pliego.unfold.net()` (kernel.md §6) then grows a cut tree. Edges are tried longest first (on a
regular solid all are equal, so ties go by corner number) or by Schlickenrieder's steepest-edge
rule. Two pieces are joined across an edge only when the joined piece does not overlap itself,
keeps room for its tabs and still fits the printable page. Edges never joined are cut, and each
gets one glue tab and its number printed on both sides. A net has one fewer fold than the solid
has faces: 3, 5, 7, 11 and 19 folds, so 3, 7, 5, 19 and 11 glued edges.

Every fold is a mountain fold (printed side out). The fold angle is 180° minus the dihedral angle:
109.47° (tetrahedron), 90° (cube), 70.53° (octahedron), 63.43° (dodecahedron) and 41.81°
(icosahedron). At the default 40 mm sphere radius every solid comes out as one piece on one A4 or
Letter page. Larger sizes split the net into pieces with more numbered edges, one page per piece
or more. Each piece is then checked with `pliego.papercut.analyze`: it is in one part, and no
neck of card is narrower than the card's minimum feature (1.5 mm at 160 g/m², 2 mm at 250 and
300 g/m²).

## The fold program

**`fold` mode (kinematic).** One sheet per piece. The steps:

1. *Fold the glue tabs in*: each tab to the angle of its edge, so it lies in the plane of the face
   it is glued under.
2. *Fold up ring 1, ring 2, …*: ring 1 is every face hinged to the piece's first face (the base,
   the face the solid stands on), ring 2 every face hinged to ring 1, and so on. At the
   defaults the cube's cross rises in two rings, four walls and then the lid; the dodecahedron
   needs five and the icosahedron six. The last ring's note lists the numbers to glue.

A piece is a tree of faces in which every corner keeps at least one cut, so every state in
between is rigid and exact. The last step is the closed solid, and the document also carries it
as a `target:assembled` frame. For the `set`, the program folds the pieces one after another,
largest first.

**`glued` mode (physical).** The finished solid is the initial frame. A glue join sits under
every tab, each weld checked to the card's contact thickness. Every crease carries its fold angle
as crease memory, because the card was folded before it was glued. One step lets go of every
crease (spec §5.6: letting go does not unfold; the glue holds the solid).

**Preview limits.**

- The fold-up is kinematic: each piece folds in place about its first face, starting flat in
  that face's plane. Nothing carries flat pieces in from the table, because whole-piece moves
  need rigid sheets and a folding piece is not rigid (§5.4).
- In the preview, `glued` mode stands still. The glue, the card's springback and the solid's
  settling need the physics engine.

## Making one by hand

1. Print the PDF at 100 % (no "fit to page") on 160–300 g/m² card.
2. Score every fold line against a ruler with an empty ballpoint pen or a bone folder.
3. Cut out the piece along the outline, tabs included.
4. Pre-fold every line away from you (mountain folds: the printed side stays outside), then open
   them a little.
5. Fold up ring by ring as the program does, gluing each tab under the edge with the **same
   number**. Glue the last faces from the outside: press each tab through the gap with a pencil
   tip or tweezers.
6. Let the glue set with the solid resting on its base.

The tetrahedron and cube are a good first build. The icosahedron's 20 small triangles, and the
dodecahedron's 19 glued edges, take patience.

## Parameters

| Parameter | Meaning |
|---|---|
| `solid` | tetrahedron, cube, octahedron, dodecahedron, icosahedron, or `set` (all five) |
| `measure` | `circumradius` (radius of the sphere through the corners) or `edge` (edge length) |
| `size` | that radius or edge length, mm (20–100) |
| `page` | A4 or US Letter |
| `method` | cutting strategy: shortest cuts or steepest edge (a different net) |
| `tab_style` | trapezoid, triangle or none |
| `tab_angle` | angle between a tab's sides and its fold, degrees |
| `tab_height` | the tallest a tab may be, mm |
| `stock` | card weight (160, 250 or 300 g/m²) |

Presets: one per solid, named by its element. "All five in one sphere" puts the set at a 40 mm
sphere radius, as in Euclid's Book XIII, and "All five with equal edges" at a 40 mm edge. "Large
dodecahedron" is a 60 mm sphere radius on Letter, in two pieces.

## History and sources

- **Plato.** In the *Timaeus* (53c–56c) Plato builds fire, air, water and earth from the
  tetrahedron, octahedron, icosahedron and cube, and says a fifth construction was used for the
  whole: the dodecahedron (55c). The solids carry his name for that reason, not because he found
  them.
- **Euclid.** The *Elements* end with the five solids: Book XIII constructs each one inside a
  given sphere (propositions 13–17) and compares their edges (18). The note after proposition 18
  shows there is no sixth: at least three faces meet at each corner, and their angles must add
  up to less than four right angles. A scholium to Book XIII credits the octahedron and
  icosahedron to Theaetetus (Heath's commentary).
- **Dürer.** Albrecht Dürer's *Underweysung der Messung* (Nuremberg, 1525), book IV, is the first
  printed book to show polyhedra as nets: the surface drawn flat, ready to cut out and fold.
  Whether every convex polyhedron can be cut along its edges into a net that does not overlap
  itself is still open. It is known as Dürer's problem (Demaine and O'Rourke, ch. 22).
- **How many nets.** The tetrahedron has 2 distinct nets, the cube and octahedron 11 each, and
  the dodecahedron and icosahedron 43,380 each (Buekenhout and Parker, 1998). This object
  generates one of them per setting; `method` picks another.

Sources:

- Plato, *Timaeus*, 53c–56c.
- Euclid, *Elements*, Book XIII; T. L. Heath (trans. and comm.), *The Thirteen Books of Euclid's
  Elements*, vol. 3, Cambridge University Press, 1908.
- A. Dürer, *Underweysung der Messung mit dem Zirckel und Richtscheyt*, Nuremberg, 1525.
- E. D. Demaine and J. O'Rourke, *Geometric Folding Algorithms: Linkages, Origami, Polyhedra*,
  Cambridge University Press, 2007, Part III.
- F. Buekenhout and M. Parker, "The number of nets of the regular convex polytopes in dimension
  ≤ 4", *Discrete Mathematics* 186 (1998).
- W. Schlickenrieder, *Nets of Polyhedra*, diploma thesis, Technische Universität Berlin, 1997
  (the steepest-edge cut tree).

## Provenance and licence

The solids are public-domain mathematics. No net is copied from Dürer, a textbook or a template:
every net, tab and number is generated by this cartridge's `main.py` and the kernel's
`pliego.unfold`. The ring-by-ring program and the cartridge itself are original MADFAM work.
Object licence: CERN-OHL-W-2.0 (the commons' root LICENSE); the kernel is AGPL-3.0.
