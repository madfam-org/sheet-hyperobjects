# Reveal block

| | Title | Summary |
|---|---|---|
| en | Reveal block | A memo-block sculpture: every sheet of a paper pad is pre-cut along its layer of a 3-D scene, and tearing the sheets away from the top leaves the scene standing inside the block. |
| es | Bloque revelable | Una escultura en bloc de notas: cada hoja de un bloc de papel viene precortada según su capa de una escena tridimensional, y al arrancar las hojas desde arriba la escena queda en pie dentro del bloque. |
| fr | Bloc à révéler | Une sculpture en bloc-notes : chaque feuille d'un bloc de papier est prédécoupée selon sa couche d'une scène en trois dimensions, et en arrachant les feuilles par le dessus on laisse la scène debout dans le bloc. |
| pt | Bloco revelável | Uma escultura em bloco de notas: cada folha de um bloco de papel vem pré-cortada segundo a sua camada de uma cena tridimensional, e ao destacar as folhas a partir de cima a cena fica de pé dentro do bloco. |

## What it is

A reveal block looks like an ordinary cube of memo paper. Each sheet, though, has been cut along
the outline of one slice of a hidden object. As the sheets are used — or torn off deliberately, top
first — the part of every sheet outside the outline comes away and the part inside stays behind.
Hundreds of slices, each a sheet thick, rebuild the object as a finely stepped relief: a stepped
pyramid, a volcano, a landscape, a sphere on a pedestal or a city skyline in this cartridge.

The cartridge is one hyperobject. The five scenes are a `scene` parameter, the block's size,
height, paper and cut type are parameters, and two presets give a coarse **preview** and the
**fabrication** document with every real sheet of the pad.

## Geometry

Each scene is a field computed by `main.py`: negative inside the object, positive outside.

- **Stepped pyramid**: six square terraces with battered (sloping) faces, a stairway climbing the
  front face and a flat-roofed shrine on top. A heightfield z = h(x, y).
- **Volcano**: a concave cone with radial gullies, a crater and a smaller parasitic cone on its
  flank, standing on a plain. A heightfield.
- **Landscape**: rolling hills, a mountain, a winding river valley and a flat-topped mesa. A
  heightfield.
- **Sphere on a pedestal**: a disc plinth, a slender stem and a sphere — built from cylinders and a
  sphere (constructive geometry). Its lower half overhangs.
- **City skyline**: a 4 × 4 street grid of towers on a base slab, some with a setback halfway up,
  and one round tower with a conical spire. Boxes, a cylinder and a cone.

`pliego.reveal.slice_block` cuts the block into layers and, for every layer:

1. samples the field on a grid at mid-layer height (a grid step of half the minimum feature);
2. **opens and closes** the inside mask with a square structuring element of the minimum feature
   (a square keeps the corners of towers and terraces sharp), so spikes, necks, slits and specks
   thinner than it disappear (the spire's last millimetres are honestly lost), and keeps the material at least 4 mm (twice the minimum feature, at least) from
   the block's edge, so the waste always forms a frame that can be torn off;
3. traces the outline with **marching squares** — saddle cells resolved by the value at the cell's
   centre, crossings interpolated linearly — simplifies it and checks every loop is simple;
4. cuts the outline into the sheet: right through, perforated, or kiss-cut;
5. adds **tear lines**: a perforated grid (`tear_grid` chunks per side) clipped to the waste, moved
   off the outline's vertices and dropped where it would leave a sliver;
6. turns every separable region of the sheet into a **piece**: inside the outline it is `keep`,
   outside it is `excess` (sheet-document spec §5.8). Islands become separate keep pieces, holes
   in the material become separate excess pieces.

The minimum feature is the stock card's own (1 mm for copy paper) raised to 2 mm: a column of
separate sheets is far weaker than one sheet, and a narrower chunk tears unpredictably. The sheets
form a **stack** — `pitch_mm` apart, bound by padding along the back edge, with the kept pieces
bonded to the sheet below. A 50 mm block of 80 g/m² copy paper (0.1 mm caliper) has 500 real
sheets; the preview draws 40, each standing for 12 real sheets of the same cut (`represents`), and
samples the scene over the full height. The fabrication preset slices all 500.

At the default 40 layers the documents hold 736 (pyramid) to about 2,700 (city) vertices; the
fabrication documents hold about 9,200 to 33,300. The studio preview poses the city's default
document in about 0.5 ms a frame.

## The reveal program

The fold program is a **reveal program**: one step per layer, from the top sheet down, and each step
`remove`s that layer's excess pieces. The `reveal` control scrubs it.

**What the studio preview shows.** The preview engine lifts each removed piece away from the block
along its pull direction (straight up) during the first three quarters of its step, then hides it,
so scrubbing the control tears the block down to the scene and back. Overlay lines of removed
pieces disappear with them.

**What needs the physics engine.** The tearing itself: a hand gripping the sheet, perforation
bridges and the padding parting at the paper's tear strain, the sheet bending as it peels, and
chunks sliding out from under an overhang. The preview does none of that — pieces move rigidly and
vanish, and the stack's contact, bond and padding are declared in the document but not simulated.
That arrives with the engine's tearing (wave 3).

## Making one by hand

A real block needs a cutter that can cut **every sheet differently**: a laser or a digital
cutter fed one sheet at a time.

1. Export the **fabrication** document (preset `fabrication`). It holds one cut file per real sheet,
   numbered from the bottom (`layer-001`) to the top. In the SVG and DXF exports the outlines and
   perforations are cut lines; kiss cuts go to the score layer (a reduced-power pass).
2. Cut the sheets in order and stack them **bottom first**, registered against two straight edges.
   Through-cut contours leave the kept pieces loose in their sheet: keep them in place, and glue
   each kept piece lightly to the one below (the document's `bond: keep`) — a dab of glue stick in
   the middle of the piece, never near its outline.
3. Square the stack, clamp it and **pad** the back edge (the spine): brush padding compound or
   diluted PVA along it, two thin coats, and let it dry under the clamp.
4. Tear the sheets off from the top. Each sheet's waste parts along its perforated tear lines;
   where a chunk sits under an overhang, slide it out sideways.

For a first try use the preview preset with a coarse layer count and thicker paper (cardstock 250
g/m²): fewer sheets, each cut by hand with a craft knife from the exported outlines.

## Parameters

| Parameter | Meaning |
|---|---|
| `scene` | stepped pyramid, volcano, landscape, sphere on a pedestal or city skyline |
| `size` | side of the square block, mm |
| `height` | height of the pad, mm; real sheets = height ÷ caliper |
| `layers` | sheets the preview draws (each stands for several real sheets); ignored when slicing every sheet |
| `fabrication` | slice every real sheet: the cut files for making the block |
| `tear_grid` | perforated tear chunks per side (1 = none; the sphere needs at least 2) |
| `contour` | how each outline is cut: through cut, perforation or kiss cut |
| `stock` | copy paper 80 g/m² (memo pad), kraft 120 g/m², cardstock 160 or 250 g/m² |

## History and sources

Memo pads are padded blocks: stacked sheets glued along one edge so a sheet tears off cleanly (the
spine of US patent 6,254,960, which also cuts a shaped edge into the whole stack). The reveal block
turns the cut inward: each sheet is cut differently, which became practical with digitally driven
laser and die cutting. A published case study describes a memo-pad portrait made of about 500
sheets of uncoated 250 g/m² paper, glued at one end and laser-cut sheet by sheet with
perforations, so that the head appears as the pages are removed. Japanese stationers sell blocks of
laser-cut memo sheets that reveal architectural models in the same way, and layered memo blocks of
720 sheets in 58 mm of height (about 0.08 mm a sheet) show the caliper involved. How the kept
sculpture is held together inside commercial blocks is not documented in the sources found; this
cartridge declares the kept pieces bonded to the sheet below. Paper 3-D printing works the same
way: sheets of office paper are glued one on another and a blade cuts each sheet along the part's
cross-section; laminated-object manufacturing also cross-hatches the waste of every sheet so it
comes out in small cubes — the origin of the tear grid here.

- PaperSpecs, «3D Einstein Memo Pad», https://www.paperspecs.com/gallery/3d-einstein-memo-pad/ —
  laser cutting sheet by sheet, about 500 sheets of uncoated 250 g/m², glued at one end,
  perforations.
- Boing Boing, «Blocks of laser-perforated note-cards that reveal architectural models as leaves
  are torn away» (2018), https://boingboing.net/2018/01/15/omoshiro-block.html — laser pre-scored
  sheets that separate to leave a model behind.
- bungu.store, «Layer Memo Block / Marumo Printing», https://bungu.store/products/layer-memo-block-marumo-printing
  — 720 sheets in a 70 × 70 × 58 mm glued block.
- US patent 6,254,960 B1, «Memo block», https://patents.google.com/patent/US6254960 — notepapers
  glued at the rear into a spine; the stack's front cut to a shape.
- 3DPrint.com, «Mcor 3D printers: IRIS and Matrix 300»,
  https://3dprint.com/9603/mcor-3d-printers-iris-matrix-300/ — standard printer paper fed sheet by
  sheet, adhesive deposited between sheets, a blade cutting each layer.
- US patent 5,657,679, «Method and apparatus for separating an LOM sculpture from an adherent
  base», https://patents.google.com/patent/US5657679 — laminated-object manufacturing: each sheet
  cut to a cross-section, the unused portions cross-hatched for removal in small cubes.
- W. E. Lorensen and H. E. Cline, «Marching cubes: a high resolution 3D surface construction
  algorithm», SIGGRAPH '87 — the contouring family marching squares belongs to.

## Provenance and licence

Original MADFAM work: the five scenes and their geometry are computed by `main.py`, and the slicing
by the Pliego kernel. No commercial block's design is copied, and no product name is used for the
object. Licence: CERN-OHL-W-2.0 (the commons' root licence).
