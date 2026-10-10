# Embossed stationery

| | |
|---|---|
| **en** | Sheet pressing and heat branding on a folded card — blind and registered emboss, deboss, hot foil, letterpress, laser burn and branding iron — with each finish's plates for the press. |
| **es** | Prensado y marcado al fuego sobre una tarjeta doblada —relieve en seco y en registro, bajorrelieve, hot stamping, tipografía, quemado láser y hierro de marcar— con las placas de cada acabado para la prensa. |
| **fr** | Pressage et marquage à chaud sur une carte pliée — gaufrage à sec et repéré, embossage en creux, dorure à chaud, typographie, brûlure laser et fer à marquer — avec les clichés de chaque finition pour la presse. |
| **pt** | Prensagem e marcação a fogo num cartão dobrado — relevo seco e em registo, baixo-relevo, hot stamping, tipografia, queima a laser e ferro de marcar — com as chapas de cada acabamento para a prensa. |

## What it is

Pressing changes a sheet's surface without cutting it. This hyperobject applies one finish, chosen
with `style`, to the cover of a scored, folded card:

- **blind emboss** — the motif raised from the cover, no ink: the sheet is squeezed between a
  recessed die (female) on the face and a raised counter (male) behind;
- **registered emboss** — the same relief, aligned over printed art (the sample print
  `assets/motif-print.svg`, placed as `pliego:artwork`);
- **deboss** — the motif pressed in: a raised die on the face;
- **hot foil** — metallic foil transferred by a heated plate, flat (depth 0);
- **letterpress** — an inked relief plate pressed into the card, leaving ink and an impression;
- **laser burn** and **branding iron** — heat branding: the surface charred by a laser (engraved
  line by line, or along the outline) or by a hot die.

## Geometry

The card is two panels of the folded size with one scored fold (`spine`). The motif is original
geometry computed in `main.py`: a ring (outer radius R, inner 0.88 R, even-odd) around an
n-point star (radii 0.76 R and 0.34 R), centred on the cover, R = `motif` × half the cover's
shorter side. Each finish is a `pliego:finishes` record (`pliego.press`) on the cover's front
(print) side:

| style | kind | depth | other |
|---|---|---|---|
| blind emboss | emboss | ring 0.35 mm (bevel), star 0.45 mm (dome) | — |
| registered emboss | emboss | as blind | `registered`, plus the printed motif |
| deboss | deboss | 0.3 mm | flat |
| hot foil | foil | 0 | gold, metallic |
| letterpress | letterpress | 0.15 mm | navy ring, red star |
| laser burn | burn | 0.1–0.15 mm | laser, char 0.6–0.8 |
| branding iron | burn | 0.4 mm | iron, char 0.9 |

Depths are typical design values [E], not press specifications. The dieline export profile
writes the plates on their own spot-coloured layers: emboss die (female) and counter (male,
inset by the caliper so the board fits between them — a design estimate), deboss die and counter,
foil plate, letterpress plate, branding-iron face, laser engrave vector and raster (a 0.3 mm scan
hatch). Plates are drawn right-reading as seen on the cover; the platemaker mirrors the die face.

## The fold program

One kinematic step folds the card closed along its score; the card lies print side down, so the
cover lands on top with its finish facing up. **Not yet modelled** (documented limits): the
studio does not render relief, foil sheen or char, and the engine does not change the local
stiffness (an embossed area is stiffer) or thickness (a burned area is thinner and more brittle)
from the finish records. The registered emboss's sample print is drawn for 8 star points: with
another count the relief falls out of register.

## Making one by hand

Cut and score the card. For a blind emboss, cut the motif from thin card as a stencil, lay the
cover face down on it over a light box and burnish the paper into the opening with a ball stylus
(the stencil is the female die). Foil needs a heated press or a foil quill; letterpress a relief
plate and a press; burning a laser engraver (start with low power on scrap of the same board) or
a branding iron, with ventilation.

## Parameters

| Parameter | Range | Meaning |
|---|---|---|
| `style` | 7 finishes | blind emboss, registered emboss, deboss, hot foil, letterpress, laser burn, branding iron |
| `size` | A6, A7, 5 × 7 in, square 150 mm | folded size |
| `points` | 5–12 | star points |
| `motif` | 0.3–0.8 | motif diameter / cover's shorter side |
| `stock` | cardstock 250/300, SBS 350, FBB 300, greyboard 1.5 mm | board |

Presets: gold-foil invitation, letterpress note card, branded greyboard tag.

## History and sources

Blind embossing and seals are old stationery crafts; letterpress was the main printing process from
the fifteenth to the twentieth century and survives as a tactile finish; hot-foil stamping became
common in the twentieth century; heat branding of leather, wood and board is older still, and laser
engraving made it digital.

- Wikipedia, *Embossing (paper)* — https://en.wikipedia.org/wiki/Embossing_(paper)
- Wikipedia, *Letterpress printing* — https://en.wikipedia.org/wiki/Letterpress_printing
- Wikipedia, *Hot stamping* — https://en.wikipedia.org/wiki/Hot_stamping
- Pliego sheet-document spec, `pliego:finishes` (lane P draft), and `pliego.press` (in the Pliego
  repository).

## Provenance and licence

Original MADFAM design: the motif and card are computed in `main.py` (the `lineage` entry says
so, licence `original`); the finishing processes are general crafts. The sample print is original placeholder artwork.
Licence CERN-OHL-W-2.0 (both manifest fields).
