# Case binding

| | Title | Summary |
|---|---|---|
| en | Case binding | A hardcover book from three commons: Pliego boards, spine strip, endpapers and signatures; a Fashion Cabinet cover cloth used by reference and backed with kraft as a computed laminate; an optional Yantra4D magnetic clasp. The case is turned in and closed as a fold program, and the cased-in book opens and closes. |
| es | Encuadernación en tapa dura | Un libro de tapa dura hecho con tres repositorios comunes: cartones, lomera, guardas y cuadernillos de Pliego; una tela de cubierta de Fashion Cabinet usada por referencia y forrada con kraft como un laminado calculado; un broche magnético opcional de Yantra4D. La tapa se forra y se cierra como una secuencia de pliegues, y el libro encajado se abre y se cierra. |
| fr | Reliure emboîtée | Un livre à couverture rigide issu de trois communs : plats, carte de dos, gardes et cahiers de Pliego ; une toile de couverture de Fashion Cabinet utilisée par référence et contrecollée sur kraft en un stratifié calculé ; un fermoir aimanté facultatif de Yantra4D. L'emboîtage est rempli et refermé en séquence de pliage, et le livre emboîté s'ouvre et se ferme. |
| pt | Encadernação em capa dura | Um livro de capa dura feito a partir de três acervos comuns: cartões, lombada, guardas e cadernos da Pliego; um tecido de capa da Fashion Cabinet usado por referência e forrado com kraft como um laminado calculado; um fecho magnético opcional da Yantra4D. A capa é forrada e fechada como uma sequência de dobras, e o livro encaixado abre e fecha. |

## What it is

A case-bound book is a hardcover whose cover, the **case**, is made apart from the sewn text
block and then joined to it ("casing in"): two boards and a spine strip are glued to a sheet of
cloth, the cloth is turned in over their edges, and the text block's endpapers are pasted down on
the inside of the boards. It is the ordinary hardcover of publishers and of hand binders alike.

This cartridge is the first object built from all three MADFAM commons, each through the
keystone's links and none by copying another platform's data:

- **Pliego (paper and board):** greyboard for the boards, a card spine strip, kraft endpapers and
  the text block's signatures — committed Pliego stock cards.
- **Fashion Cabinet (cloth):** the cover cloth, `manta-cruda` (unbleached cotton) or
  `popelina-algodon` (cotton poplin), named in the manifest's `material_ref` with
  `behaviour: "sheet"`. Pliego reads the fabric's `sheet_behaviour` (the keystone's mapping
  `fc-fabric/1`) from its vendored snapshot; it never copies the fabric card.
- **Yantra4D (solid):** the optional magnetic clasp is Yantra4D's printed `magnetic-clasp`, named by
  the manifest's `hardware_ref` and checked name-level by the kernel. Pliego models no solid: it
  cuts the two recesses the clasp's halves sit in.

Two modes:

- `case` — the cover cloth as one sheet: crease the joints where the boards and spine strip lie,
  turn in the head and the tail, turn in the fore-edges over the mitred corners, then case in round
  the text block and close.
- `book` — the cased-in book: covered boards and spine, endpapers, signatures and, with the clasp,
  a fore-edge flap. The cover opens and closes, the flyleaf and every signature turn, and the
  clasp flap wraps the fore-edge onto the front cover.

## Geometry

Every number comes from the parameters and the stock cards; `main.py` computes it.

| quantity | rule |
|---|---|
| pages | 4 × sheets per signature × signatures (each sheet is folded once) |
| text block thickness T | pages / 2 × the text paper's caliper (read from its stock card: copy-80 0.10 mm, kraft-120 0.16 mm, cardstock-160 0.20 mm) |
| spine strip width S | T + 2 × board thickness |
| board | width = page width + square + the spine strip's thickness − joint; height = page height + 2 × square |
| cloth | width = 2 × (turn-in + board + joint) + S; height = board height + 2 × turn-in |
| mitred corners | cut at 45°, 1.5 board thicknesses off each board corner, so the turned-in corner covers the board edge |
| clasp | a flap of cloth on kraft as wide as S + 1 mm, then a covered tab max(30, housing + 16) mm wide; recess diameter = the clasp's housing = magnet diameter + 6 mm, centred half a tab in from the front board's fore-edge and in the tab |

The A5 defaults (96 pages of copy-80, 1.5 mm board, 7 mm joint, 3 mm square, 15 mm turn-in)
give a 4.8 mm text block, a 7.8 mm spine strip, 145.5 × 216 mm boards and a
342.8 × 246 mm piece of cloth.

**The laminates.** Four stocks are laminates (`pliego.laminate`, spec §5.40), layers listed from
the inside face out:

| stock | layers | caliper | coupled (B ≠ 0) |
|---|---|---|---|
| `case-cloth` (the cover cloth, the clasp flap) | kraft-120, cloth | 0.51 mm (manta), 0.41 mm (poplin) | yes |
| `covered-board`, `covered-board-back` | greyboard (board thickness), kraft-120, cloth | 2.01 mm at 1.5 mm board (manta) | yes |
| `covered-spine` | cardstock-300, kraft-120, cloth | 0.87 mm (manta) | yes |

The kernel reduces each stack by classical laminate theory and writes its free-stack stiffness
for the engine. For the default cloth, manta on kraft, it gives D11 = 0.00564 N·m and
D22 = 0.00265 N·m, against the kraft alone at 0.00243 and 0.00105 N·m: the cloth, nearly
limp by itself (0.0000196 N·m), more than doubles the kraft's bending stiffness because it sits
off the kraft's mid-plane. These are the keystone calculator's own numbers on the same layers, to
six significant digits. Every stack here is asymmetric, so B ≠ 0 and it is flagged `coupled`:
stretching it bends it. That is why a covered board warps when the glue dries and the cloth
shrinks, and why binders line the inside of a board. The engine reads the stack's bending and
membrane stiffness today; the curl itself is not simulated yet.

## The fold program and the mechanisms

`case` is a `pliego.FoldProgram` on the cloth, every step rigid and exact (closure residual of
order 1e-13 mm):

1. crease the four joints, the lines where the boards and the spine strip are laid on the glued
   cloth;
2. turn in the head, then the tail;
3. turn in each fore-edge: the folded corner of the head and tail turn-ins tucks under it;
4. case in: the spine stands up 90° about the back joint, round the text block's thickness;
5. close: the front board comes over 90° about the front joint and lies over the back board.

The studio preview plays the whole program and ends in the closed case.

`book` uses the preview's mechanisms: the front board and its pastedown turn on a `hinge` at the
top of the spine (control **Open the cover**, 0° closed to 180° open); the front flyleaf and each
signature turn on a `leaf` at the spine with a pin along the sewing (one control each); with the
clasp, the flap turns up the fore-edge and its tab over the front cover — two `hinge`s keyed to one
control **Close the magnetic clasp**, the tab riding the flap. The back board, spine, back
pastedown and back flyleaf are fixed boards. The glue between cloth, boards and pastedowns, and the
bending of the joints when the cover opens, need the physics engine; the preview moves the parts
rigidly.

## Making one by hand

1. Fold and sew the signatures; glue up the spine of the text block; tip the endpapers on.
2. Cut two boards and the spine strip to the sizes above, with their grain parallel to the spine.
3. Cut the cloth with its kraft backing (or line the cloth with kraft first) to the cloth size;
   mitre the four corners.
4. Glue the cloth, lay the back board, the spine strip and the front board with a joint gap each
   side of the strip; turn in the head and the tail, then the fore-edges, tucking each corner.
5. Case in: glue the pastedowns and close the case over the text block; press it with rods in the
   joints until dry.
6. For the clasp, print Yantra4D's `magnetic-clasp` at the mapped values, set its halves in the
   recesses in the front board and the flap tab before the boards are covered, and glue the flap
   to the back board's fore-edge.

## Parameters

| id | default | range | what it sets |
|---|---|---|---|
| `page_width`, `page_height` | 148, 210 mm | 80–300, 100–320 | the trimmed text block |
| `signatures` | 6 | 1–12 | sewn sections; each is one turning sheet in `book` |
| `sheets_per_signature` | 4 | 2–8 | folded sheets per signature (4 pages each) |
| `text_paper` | copy-80 | copy-80, kraft-120, cardstock-160 | the pages' stock; its caliper sets the spine |
| `board_caliper` | 1.5 mm | 1.0–3.0 | the greyboard layer's thickness |
| `joint` | 7 mm | 4–12 | the cloth hinge between board and spine strip |
| `square` | 3 mm | 2–5 | boards proud of the pages at head, tail and fore-edge |
| `turn_in` | 15 mm | 12–20 | cloth folded onto the inside of the boards |
| `cloth` | manta-cruda | manta-cruda, popelina-algodon | the Fashion Cabinet fabric of the cover |
| `clasp` (`book`) | off | on/off | the fore-edge flap and the magnetic clasp |
| `clasp_magnet` (`book`) | 12 mm | 6–20 | the clasp's magnet diameter (`hardware_ref.params_map`) |

Presets: A5 notebook, A4 album, A5 with magnetic clasp, square sketchbook. The clasp's
`params_map` sends `magnet_dia = clasp_magnet`, `disc_dia = clasp_magnet + 6` and
`disc_h = max(board_caliper + 1, 2.5)` to Yantra4D.

## Materials and where they come from

The cloth and the clasp are not paper, and Pliego does not make them:

- **The cover cloth** is a Fashion Cabinet fabric card. Its sheet stiffness is the keystone's rule
  `fc-fabric/1`, which estimates a fabric's bending from its bend class and its stretch from an
  assumed test load; every one of those numbers is marked `estimated` in the snapshot, and the
  ladder is a convention until fabric cards carry measured bending. Buy book cloth, or line a
  cotton yourself with kraft; the laminate is that lined cloth.
- **The clasp** is Yantra4D's `magnetic-clasp`, printed, with two magnets bought separately.
  Pliego checks that the part exists and that the parameter names it maps exist (the bridge
  handshake's first rule); whether the printed part fits the recess is checked only on the
  Yantra4D side, after it is rendered at those values.
- **Boards, spine strip, endpapers and pages** are Pliego stock cards; their cut outlines and the
  cloth's crease and cut lines export as SVG, DXF, PDF and HPGL. Glue is not modelled.

## History and sources

Case binding became the publishers' standard hardcover in the nineteenth century, once cloth
made for covering books let binderies cover boards in quantity, and it remains the ordinary
hardcover (Encyclopaedia Britannica, «Bookbinding»,
https://www.britannica.com/art/bookbinding; Wikipedia, «Bookbinding»,
https://en.wikipedia.org/wiki/Bookbinding; Wikipedia, «Hardcover»,
https://en.wikipedia.org/wiki/Hardcover). The terms used here — case binding, casing in, book
cloth, square, turn-in, joint — follow the conservators' dictionary of Etherington and Roberts
(«Bookbinding and the Conservation of Books: A Dictionary of Descriptive Terminology», 1982,
Conservation OnLine, https://cool.culturalheritage.org/don/) and the Ligatus «Language of
Bindings» thesaurus (https://www.ligatus.org.uk/lob/).

The tradition belongs to the bookbinders and the publishers' binderies that developed it. No
binder's diagram or template is copied: every dimension and line is computed by this cartridge.

## Provenance and licence

Original MADFAM design (the dimensioning rules, the mitres, the fold program, the clasp flap and
its recesses, the laminate stacks) of a traditional binding credited to the bookbinding tradition.
The cloth's physics comes from the keystone's mapping of a Fashion Cabinet card and the clasp is a
Yantra4D part, both by reference. Published under CERN-OHL-W-2.0 like every object in the commons
(see the commons root `LICENSE`).
