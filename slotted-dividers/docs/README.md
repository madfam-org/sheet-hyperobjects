# Slotted dividers

| | |
|---|---|
| **en** | Interlocking partitions that divide a case into cells: board strips with half-height slots one caliper wide, generated from the cell grid, assembled as the initial frame and lifted apart by a control. |
| **es** | Separadores que se entrelazan y dividen una caja en celdas: tiras de cartón con ranuras de media altura y un calibre de ancho, generadas a partir de la cuadrícula, armadas como cuadro inicial y separadas con un control. |
| **fr** | Des croisillons qui s'emboîtent et divisent une caisse en alvéoles : des bandes de carton à fentes de mi-hauteur, larges d'une épaisseur, générées à partir de la grille, montées comme état initial et séparées par un curseur. |
| **pt** | Divisórias que se encaixam e dividem uma caixa em células: tiras de cartão com ranhuras de meia altura e uma espessura de largura, geradas a partir da grelha, montadas como estado inicial e separadas por um controlo. |

## What it is

Slotted dividers (partitions, cell dividers) are the insert that keeps bottles, jars or parts
apart inside a shipping case: flat strips of board, each slotted halfway, that cross-lock into a
grid of cells. This hyperobject generates the strips from the cell grid you need — cells along
the length and across, each cell's inside length and width, and the partition height — in
greyboard or corrugated board, and shows them assembled.

## Geometry

With t the board's caliper:

- **Strips.** `rows − 1` long partitions run the box's length and `columns − 1` cross partitions
  run its width; the case's own walls close the outside cells. A long strip is
  `columns × cell_length + (columns − 1) × t` long and a cross strip
  `rows × cell_width + (rows − 1) × t`, because every partition between two cells takes t.
- **Slots.** Long strips are slotted from the top and cross strips from the bottom. Each slot is
  half the height deep and exactly one caliper wide, centred on the crossing partition's centre
  line, so at every crossing one strip keeps its lower half and the other its upper half and the
  two meet flush. The script fails loudly unless the slot width equals the caliper, the depth is
  half the height, the slots stay clear of the strip ends and at least three calipers of board
  stand between slots; it also runs `pliego.papercut.analyze` on every strip.
- **Grain.** Strips are cut with the grain along their length, so corrugated strips have their
  flutes running up the height, the stiffer orientation for a partition.
- **Assembly.** Every strip is a rigid board standing in its plane (long strips at their z
  offsets, cross strips at their x offsets): the assembled grid is the initial frame.

## The fold program

There are no folds. The interaction is a mechanism the preview drives: the long strips are fixed
boards and the cross strips ride a `translate` mechanism; the `lift` control raises them straight
out of their slots (half the height plus a margin of at least 10 mm) and lowers them back in.
**Limits.** Slot contact is edge-to-edge contact between boards, which the engine does not
model in v0.1: nothing stops one strip from passing through another, and the grid's stiffness,
the friction in the slots and their fit need the physics engine. The slots here are exactly one
caliper wide; makers often add a fraction of a millimetre so the strips slide together easily.

## Making one by hand

Print or draw the strips at 100 %, cut them, and cut each slot with two parallel cuts one
caliper apart (a strip of the same board makes a good gauge), then snap the waste out. Stand the
long strips up with their slots on top and drop the cross strips over them, slots down.

## Parameters

| Parameter | Range | Meaning |
|---|---|---|
| `columns` | 2–8 | cells along the length |
| `rows` | 2–8 | cells across |
| `cell_length` | 25–250 mm | cell inside length |
| `cell_width` | 25–250 mm | cell inside width |
| `height` | 30–400 mm | partition height |
| `stock` | corrugated E, B, C flute; greyboard 1.5 mm | board (its caliper is the slot width) |

Presets: 12 jars, 6 bottles (B flute), parts tray (greyboard).

## History and sources

Partitions of slotted board strips are a standard interior fitting of corrugated cases. No
origin is claimed here.

- Wikipedia, *Corrugated box design* — https://en.wikipedia.org/wiki/Corrugated_box_design
- Wikipedia, *Corrugated fiberboard* — https://en.wikipedia.org/wiki/Corrugated_fiberboard
- Pliego `pliego.board` (flute geometry and calipers) and the sheet-document spec, mechanisms
  (§5.4), in the Pliego repository.

## Provenance and licence

Original MADFAM design: the strips, their slots and the assembled grid are computed in `main.py`
(the `lineage` entry says so, licence `original`). No catalogue drawing is reproduced. Licence
CERN-OHL-W-2.0 (both manifest fields).
