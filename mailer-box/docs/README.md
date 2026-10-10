# Mailer box

| | |
|---|---|
| **en** | One-piece corrugated mailers with a hinged lid — the roll-end tuck-front mailer and the pizza style — generated from inside dimensions, glue-free, with brand artwork on the lid. |
| **es** | Cajas de envío de una pieza en cartón corrugado con tapa abisagrada —el mailer de extremos enrollados y el estilo pizza— generadas a partir de las medidas interiores, sin pegamento y con arte de marca en la tapa. |
| **fr** | Boîtes postales d'une pièce en carton ondulé à couvercle articulé — à bouts roulés et patte rentrante, et style pizza — générées à partir des dimensions intérieures, sans colle, avec illustration de marque sur le couvercle. |
| **pt** | Caixas de envio de uma peça em papelão ondulado com tampa articulada — o mailer de pontas enroladas e o estilo pizza — geradas a partir das medidas internas, sem cola e com arte de marca na tampa. |

## What it is

The mailer is the glue-free e-commerce box: one blank folds into a tray with double walls and
a lid that opens like a book.

- **Roll-end tuck-front mailer** (FEFCO 0427 style): the base, a front and a back wall each with
  two ears, two **rolled end walls** — each an outer leaf, a fold over the top and an inner leaf
  with two lock tabs — and the lid, hinged to the back wall, with two dust flaps and a front
  tuck. The ears are trapped between the leaves of the rolled ends; the tabs drop into slots cut
  through the base folds, so the tray holds itself.
- **Pizza style**: the front wall rolls instead (three lock tabs into slots through the
  base–front fold) and the side walls carry corner ears that tuck behind the front and back
  walls; the lid's tuck slides inside the rolled front.

## Geometry

`pliego.dieline.mailer` builds the blank from inside length L, width W (front to back) and
height D (D ≤ W), and the board caliper t:

- base L + t by W + t; walls D + t high; the rolled inner leaf is t shorter than the outer leaf
  and its lock tabs drop 2t + 2 mm through the slots;
- slots are 2t across the fold (a notch cut into each of the two panels it separates), with
  0.5 mm clearance around each tab;
- ears are (W + t)/2 − t long, shortened by a slot width at the folds they meet, so ears and
  walls never share an edge; lid dust flaps D deep; the tuck D + t − 2t deep;
- slot width 2t (at least 2 mm) everywhere flaps meet.

Folds are crease-rule scores named after their panels; the `pliego:dielines` block carries
panels, bleed and safe areas, dimension lines and the flute arrow for the dieline export.
With `branding` on, the sample mark is placed centred on the lid's print side
(`pliego:artwork`, clipped to the lid).

## The fold program

Kinematic, played in full in the preview. Mailer: walls up; ears in; end walls up over the
ears; roll the end walls in (180°) so the tabs drop into the slots; close the lid (dust flaps,
lid, tuck). Pizza: side walls up; corner ears in; back and front walls up; roll the front wall
in; close the lid.

The blank lies print side down with the base on the table. The studio's preview poses the blank
from its first face, which lies on the first end wall, so that wall starts already rolled (the
initial frame) and the base never leaves the table. No two folds meet inside the board (ears
and walls are separated by slots), so the program is a rigid face tree. **Needs the physics
engine:** the friction of the lock tabs in their slots, the ears pinched between the leaves,
and the lid's tuck holding by contact. The zero-thickness preview draws the rolled inner leaf on
the outer leaf.

## Making one by hand

Cut the blank from E or F flute board, cut out the slots, and crease every fold on the inside.
Raise the walls, fold the ears in, raise the end walls over them and roll the inner leaves down
until the tabs click into the slots. Close the lid, dust flaps inside the walls, tuck inside
the front.

## Parameters

| Parameter | Range | Meaning |
|---|---|---|
| `style` | mailer · pizza | rolled ends or rolled front |
| `length`, `width`, `depth` | 80–500, 60–400, 25–200 mm | inside dimensions (width ≤ length, height ≤ width) |
| `board` | F · E · B flute | corrugated board stock |
| `branding` | on/off | sample brand mark on the lid |

Presets: book mailer, pizza box (B flute), small gift mailer (F flute).

## History and sources

Roll-end mailers spread with mail-order and e-commerce shipping; FEFCO's code lists the style
as 0427, and the folded corrugated pizza box is its common open-front relative. This cartridge
cites the code as an identifier only and generates its own geometry.

- FEFCO, *International Fibreboard Case Code* (code list) — https://www.fefco.org/
- Wikipedia, *Corrugated fiberboard* (flute designations after Foster 1997) — https://en.wikipedia.org/wiki/Corrugated_fiberboard
- Pliego physics memo §(h) and the corrugated stock cards (in the Pliego repository).

## Provenance and licence

Original MADFAM geometry, computed by `pliego.dieline` from the parameters; the mailer styles
are industry styles attributed to that tradition; the sample brand mark is original placeholder
artwork. Licence CERN-OHL-W-2.0 (both manifest fields).
