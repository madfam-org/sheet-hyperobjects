# Paper house

| | Title | Summary |
|---|---|---|
| en | Paper house | An original cut-out paper house in four designs (a cottage with a chimney, a townhouse with its gable to the street, a gambrel-roofed barn with double doors and a house with a hip roof), built as a model at 1:100, 1:87 or 1:50 and unfolded into tabbed, numbered pieces on pages, with windows and doors cut out or scored and a program that folds the pieces into the house and opens its doors. |
| es | Casa de papel | Una casa de papel recortable original en cuatro diseños (una casita con chimenea, una casa de ciudad con el hastial a la calle, un granero de tejado holandés con puerta doble y una casa con tejado a cuatro aguas), construida como maqueta a 1:100, 1:87 o 1:50 y desplegada en piezas numeradas y con pestañas sobre hojas, con ventanas y puertas recortadas o marcadas y una secuencia que dobla las piezas hasta formar la casa y abre sus puertas. |
| fr | Maison en papier | Une maison en papier à découper originale en quatre modèles (une maisonnette avec cheminée, une maison de ville pignon sur rue, une grange à comble brisé avec porte à deux battants et une maison à toit en croupe), construite en maquette au 1/100, au 1/87 ou au 1/50 et dépliée en pièces numérotées à languettes sur des pages, avec fenêtres et portes découpées ou rainées et un programme qui plie les pièces jusqu'à la maison et ouvre ses portes. |
| pt | Casa de papel | Uma casa de papel para recortar original em quatro modelos (uma casinha com chaminé, um sobrado urbano com a empena para a rua, um celeiro de telhado de mansarda com porta dupla e uma casa com telhado de quatro águas), construída como maquete em 1:100, 1:87 ou 1:50 e desdobrada em peças numeradas e com abas em folhas, com janelas e portas recortadas ou vincadas e uma sequência que dobra as peças até formar a casa e abre as portas. |

## What it is

A **cut-out house**: a small building printed flat on card, cut out, folded and glued into a
model. This object is one family of original MADFAM houses, selected by `design`, each drawn at a
real size in metres and printed at a model scale:

| `design` | footprint | walls | roof | chimney | doors |
|---|---|---|---|---|---|
| `cottage` | 8 × 5.5 m | 2.7 m | gable, 45° | on the ridge | one, front |
| `townhouse` | 5 m frontage × 9 m deep | 8.4 m (three storeys) | gable to the street, 55° | on the ridge, at the back | one, on the street gable |
| `barn` | 11 × 8 m | 3.4 m | gambrel: 62° below, 26° above | none | double doors and a side door |
| `hip-house` | 10 × 7 m | 3.0 m | hip, 30° on all four sides | on the ridge | one, front |

`scale` prints it at 1:100, 1:87 (H0, the model railway scale) or 1:50. At 1:87 every design
fits on one or two A4 or Letter pages, in two or three pieces. Windows and doors are `cut`
(windows cut out, doors cut on three sides so they swing open), `scored` (outlines only; the
house stays closed) or left off. The studio paints each design's walls in its own colour; on
paper the colour is the card you print on.

## Geometry

Every house is a polygon mesh generated in `main.py` (metres; x along the ridge, y up, z toward
the front):

- **Walls and roof.** The end-wall profile runs from the front ground corner up the wall, over
  the roof and down the back. It is a triangle on a rectangle for a gable, and two slopes a side
  for a gambrel (the knee sits at 62 % of the half-depth). Carrying the profile along x gives the
  long walls and the roof planes, and the profile itself is each end wall. A hip roof has a short
  ridge, half-length (width − depth)/2 so that all four planes share one pitch. It has a
  trapezoid roof plane front and back and a triangle at each end.
- **Chimney.** A box straddles the ridge. The two roof planes beside the ridge are notched around
  its footprint, and the chimney's two side walls come down to a peak that sits on the ridge.
  Roof and chimney are one closed surface with no hole and no overlap, so the chimney glues on
  with numbered tabs like any other edge.
- **Open bottom.** The walls' bottom edges are plain cut edges. The doors reach the ground and the
  model sits flat on a base board.
- **Orientation.** The faces are turned consistently by a walk across shared edges, and outward by
  the sign of the enclosed volume. The kernel checks the mesh (`Mesh.check()`) before unfolding.

The mesh is scaled to the card (1 m is 10 mm at 1:100, 11.5 mm at 1:87, 20 mm at 1:50) and
unfolded by `pliego.unfold.net()` (kernel.md §6). The unfolder grows a cut tree, joining two
pieces only when the result does not overlap, keeps room for its tabs, and fits the page. Each cut
gets one glue tab and its number on both sides. Folds are mountain or valley from the 3-D
dihedral; the valleys are where the chimney meets the roof.

**Windows and doors** are then drawn onto the pieces. Each opening is placed on its wall in
metres, carried into that face's own flat frame, and from there onto its piece by the same rigid
map the unfolder used, checked against every corner of the face. Every opening keeps at least the
tab height plus 1 mm from each edge of its wall, except the ground edge for doors, so it never
cuts into a glue tab glued behind the wall. A design that cannot keep that clearance at a given
scale fails loud. Windows are holes. A door is a cut up one side and across the top, with a
scored hinge down the other side; the barn's double doors are two leaves with one cut down the
middle. Each piece is checked with `pliego.papercut.analyze`: one part, and no neck of card
narrower than the card's minimum feature (1.5 mm at 160 g/m², 2 mm at 250 and 300 g/m²).

One workaround is visible in the code. The kernel joins each window (a hole inside a face) to the
face's edge with an invisible bridge. On a piece turned by the page layout, a bridge laid almost
along another window's edge can leave a face that is not simple, which the document check
rejects. Each opening on a wall is therefore moved by its own multiple of 0.1 mm on the card, so
no two openings share an edge line. The shift is under 1 mm in all. Windows are single openings
for the same reason: glazing bars (four panes per window) put four holes on one grid, which the
bridges cannot yet handle reliably.

## The fold program

**`fold` mode (kinematic).** One sheet per piece. The steps:

1. *Fold the glue tabs in*: every tab to the angle of its cut, so it lies in the plane of the
   face it is glued under.
2. *Fold piece N into shape*, one step per piece. The step's note lists the edge numbers to glue.
3. *Open the door* (or *doors*): every door swings 70° inward on its scored hinge (only with
   `cut` openings).

Every piece is a tree of faces in which every corner keeps at least one cut, so every state in
between is rigid and exact. Step 2 ends on the finished house, which the document also carries as a
`target:assembled` frame.

**`glued` mode (physical).** The finished house is the initial frame. A glue join sits under
every tab, each weld checked to the card's contact thickness, and every crease carries its fold
angle as crease memory (the card was folded before it was glued). One step lets go of every
crease (spec §5.6: letting go does not unfold; the glue holds the house). The doors stay shut.

**Preview limits.**

- The fold-up is kinematic: each piece folds in place about its first face, starting flat in
  that face's plane. Nothing carries flat pieces in from the table, because whole-piece moves
  need rigid sheets and a folding piece is not rigid (§5.4).
- In the preview, `glued` mode stands still. The glue, the card's springback and the house's
  settling need the physics engine.

## Making one by hand

1. Print the PDF at 100 % (no "fit to page") on 160–300 g/m² card.
2. On a cutting mat, cut out the windows with a craft knife first, while the sheet is still
   whole. Cut each door up its free side and across its top. Then score its hinge line.
3. Score every fold line against a ruler with an empty ballpoint pen or a bone folder.
4. Cut out the pieces, tabs included.
5. Pre-fold every line. The folds are mountains (printed side out) except where the chimney
   meets the roof.
6. Glue the walls first, each tab under the edge with the **same number**, then the roof planes.
   Glue the chimney last: its tabs go under the roof notch.
7. Open the doors with a fingernail. Glue the house onto a card base if you like.

The cottage is the easiest build. The townhouse is tall: let each glued edge set before the next.

## Parameters

| Parameter | Meaning |
|---|---|
| `design` | cottage, townhouse, barn or hip-house |
| `scale` | 1:100, 1:87 (H0) or 1:50 |
| `openings` | `cut` (windows cut out, doors open), `scored` (outlines only) or `none` |
| `chimney` | the chimney on the ridge, on or off (the barn has none) |
| `page` | A4 or US Letter |
| `method` | cutting strategy: shortest cuts or steepest edge |
| `tab_style` | trapezoid, triangle or none |
| `tab_height` | the tallest a tab may be, mm (3–6, so openings keep clear of the tabs) |
| `stock` | card weight (160, 250 or 300 g/m²) |

Presets: one per design at 1:87; the cottage at 1:50 as a desk model (three pages); and the barn
at 1:100 with scored openings, a closed model to set beside a model railway.

## History and sources

- Printed cut-out sheets of buildings, to be cut, folded and glued by children, were sold in
  Europe from the nineteenth century. Well-known publishers include the Imagerie Pellerin in
  Épinal (France) and J. F. Schreiber in Esslingen (Germany). This object belongs to that
  tradition but copies none of its sheets.
- The roofs are standard building forms: a **gable** roof slopes two ways from a ridge and leaves a
  triangular gable at each end; a **hip** roof slopes on all four sides; a **gambrel** roof has two
  slopes on each side, the lower one steeper, the classic barn roof (Ching).
- Model railway scales are standardised: H0 is 1:87 (NEM 010).
- The unfolding into a net that may split into pieces follows the kernel (kernel.md §6); the
  theory is in Demaine and O'Rourke, Part III.

Sources:

- F. D. K. Ching, *A Visual Dictionary of Architecture*, 2nd ed., Wiley, 2012 (roof forms).
- MOROP, *NEM 010: Scales and gauges* (model railway standards).
- Musée de l'Image, Épinal: the Imagerie Pellerin collections (printed paper constructions).
- E. D. Demaine and J. O'Rourke, *Geometric Folding Algorithms: Linkages, Origami, Polyhedra*,
  Cambridge University Press, 2007, Part III.

## Provenance and licence

Original MADFAM designs. The four houses, with their proportions, roofs, chimney, windows and
doors, are generated as meshes by this cartridge's `main.py` and unfolded by `pliego.unfold`. No
published cut-out sheet, kit or model was copied, traced or used as a reference. Object licence:
CERN-OHL-W-2.0 (the commons' root LICENSE); the kernel is AGPL-3.0.
