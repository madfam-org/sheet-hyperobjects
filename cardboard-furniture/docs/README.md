# Cardboard furniture

| | |
|---|---|
| **en** | Original slotted furniture in thick corrugated board — a stool and a side table — assembled without glue: two cross-halved legs and a top held by tabs in mortises, with the slots checked against the caliper and the parts laid out on a stock sheet. A prototype, with no load rating. |
| **es** | Muebles ranurados originales de cartón corrugado grueso —un banco y una mesa auxiliar— armados sin pegamento: dos patas a media madera y una cubierta sujeta con espigas en mortajas, con las ranuras comprobadas contra el calibre y las piezas acomodadas en una hoja. Es un prototipo, sin capacidad de carga declarada. |
| **fr** | Du mobilier original à fentes en carton ondulé épais — un tabouret et une table d'appoint — monté sans colle : deux pieds à mi-bois et un plateau tenu par des tenons dans des mortaises, avec les fentes vérifiées par rapport à l'épaisseur et les pièces imposées sur une feuille. Un prototype, sans charge admissible annoncée. |
| **pt** | Móveis ranhurados originais de cartão canelado grosso — um banco e uma mesa de apoio — montados sem cola: duas pernas a meia-madeira e um tampo preso por espigas em encaixes, com as ranhuras verificadas contra a espessura e as peças dispostas numa folha. É um protótipo, sem capacidade de carga declarada. |

## What it is

Three flat parts of thick corrugated board slot together into a piece of furniture: two legs that
cross-halve into an X (a "+" in plan) and a top whose mortises take tabs on the legs' top edges.
Nothing is glued or screwed. `piece` selects an original design — a **stool** (square seat with
rounded corners, straight legs) or a **side table** (round top, tapered legs) — and the board is
BC double wall (6.84 mm) or AAC triple wall (14 mm). The catalogue's third variant, a shelf, is
not part of this cartridge.

## Geometry

With t the board's caliper and H the height:

- **Legs** run from the floor to the top's underside (H − t). Each has an arch between its feet
  (half an ellipse, 0.3 of the leg's height) to save board and stand on two feet. The stool's legs
  are the seat's width less 15 mm a side; the side table's taper from 0.82 to 0.62 of the top.
- **Cross-halving.** Leg A is slotted from the top and leg B from the bottom (up from its arch),
  each slot exactly one caliper wide and reaching half the leg's height, so the two legs meet
  flush. Legs are cut with the flutes running up their height.
- **Top.** Two tabs on each leg's top edge, one caliper tall so they finish flush with the top's
  upper face (40 mm wide in BC, 60 mm in AAC), pass through mortises one caliper wide and one tab
  long.
- **Checks.** The script fails loudly unless the slots and mortises are one caliper wide, the
  slots reach half the height, the arch stays two calipers clear of the cross slot, the tabs stay
  clear of the slot and on the legs' top edges, and the tabs land inside the top; it runs
  `pliego.papercut.analyze` on every part.
- **Layout.** The parts are shelf-packed onto a stock sheet — 1200 × 1000, 1600 × 1200 or
  2000 × 1200 mm, common formats rather than a standard [E] — with 10 mm margins and gaps and the
  parts' heights along the sheet's flutes; the document's layout places them that way, so the cut
  files show the nesting. At the defaults (BC stool, 1600 × 1200) one set uses 16 % of a sheet and
  four sets fit on one (63 %); the side table preset fits two sets per sheet (47 %).

## The fold program

There are no folds. The assembled piece is the initial frame, every part a rigid board, and the
`explode` control takes it apart: two `translate` mechanisms on the same control lift the top out
of its tabs and leg B out of the cross slot, the top travelling twice as far so it stays clear.
The preview drives it. **Prototype only.** Whether the piece carries a person or a load is a
statics claim this cartridge cannot verify — the board's crushing and buckling, the joints' play,
humidity — so no load rating is given. Slot contact is edge-to-edge contact, which the engine
does not model in v0.1.

## Making one by hand

Print or plot the parts at 100 % and cut them from the board with a sharp knife or a CNC knife
cutter, cutting each slot and mortise as two parallel cuts one caliper apart (a strip of the same
board is the gauge). Stand leg A up, slot on top, and drop leg B over it, slot down; press the top
onto the four tabs. Test it with weights before anyone sits on it.

## Parameters

| Parameter | Range | Meaning |
|---|---|---|
| `piece` | stool, side table | design |
| `height` | 300–700 mm | floor to the top's upper face |
| `top` | 260–600 mm | seat side, or table-top diameter |
| `stock` | corrugated BC double wall, AAC triple wall | board (its caliper is every slot's width) |
| `sheet_format` | 1200 × 1000, 1600 × 1200, 2000 × 1200 mm | stock sheet for the layout |

Presets: stool (BC), stool (AAC triple wall), side table.

## History and sources

Furniture of slotted and laminated corrugated board has been designed since at least the
mid-twentieth century; the cross-halving and the mortise and tenon are old joinery techniques
applied here to board. This design copies no published piece.

- Wikipedia, *Cardboard furniture* — https://en.wikipedia.org/wiki/Cardboard_furniture
- Wikipedia, *Halving joint* — https://en.wikipedia.org/wiki/Halving_joint
- Wikipedia, *Mortise and tenon* — https://en.wikipedia.org/wiki/Mortise_and_tenon
- Pliego `pliego.board` (calipers of the corrugated stocks), in the Pliego repository.

## Provenance and licence

Original MADFAM design: the stool, the side table, their joinery checks and the stock-sheet layout
are computed in `main.py` (the `lineage` entry says so, licence `original`). Licence
CERN-OHL-W-2.0 (both manifest fields).
