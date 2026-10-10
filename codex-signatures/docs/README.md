# Codex signatures

| | Title | Summary |
|---|---|---|
| en | Codex signatures | A printed press sheet (pliego) folded into a folio, quarto or octavo signature, with the imposition computed from the fold and checked, and signatures gathered into a sewn book block. |
| es | Cuadernillos del códice | Un pliego impreso doblado en un cuadernillo en folio, en cuarto o en octavo, con la imposición calculada a partir del doblado y comprobada, y cuadernillos alzados en un cuerpo de libro cosido. |
| fr | Cahiers du codex | Une feuille d'impression (pliego) pliée en cahier in-folio, in-quarto ou in-octavo, avec l'imposition calculée à partir du pliage et vérifiée, et des cahiers assemblés en un corps d'ouvrage cousu. |
| pt | Cadernos do códice | Uma folha impressa (pliego) dobrada num caderno in-fólio, in-quarto ou in-oitavo, com a imposição calculada a partir da dobra e verificada, e cadernos alceados num miolo costurado. |

## What it is

A codex — the book with pages, as opposed to the scroll — is made of **signatures**: large printed
sheets folded down to page size and sewn through the fold. In Spanish the folded sheet is a
*pliego*, the word this platform takes its name from. This cartridge folds one press sheet into a
signature in the three classical formats and then gathers several signatures into a sewn book
block:

| format | folds | leaves | pages | page size from the sheet W × H |
|---|---|---|---|---|
| `folio` (2°) | 1 | 2 | 4 | W/2 × H |
| `quarto` (4°) | 2 | 4 | 8 | H/2 × W/2 (turned) |
| `octavo` (8°) | 3 | 8 | 16 | W/4 × H/2 |

An A2 sheet (594 × 420 mm) gives an A3 folio, an A4 quarto and an A5 octavo, since every fold of an
ISO sheet keeps the √2 proportion.

Mode `signature` folds one press sheet. Mode `gathered` shows 2–6 folded signatures gathered into
a book block and sewn, and opens the book at the centre of the signature on top.

## Geometry

Each fold halves the folded sheet across its longer side, **through every layer**: the left half
over the right, or the top half down. The crease pattern is not drawn by hand; `main.py` folds the
sheet with the kernel's simple-fold model (`pliego.simplefold.FoldedState`), which reflects every
layer the fold line crosses and records where the fold lands on the flat sheet. A fold made through
a stack lands on the sheet as several segments whose mountain/valley alternate with the layers'
flips. The last fold is the **spine** (edge name `spine`); the earlier folds (`fold-1`, `fold-2`)
end up at the head or the fore-edge as closed folds, the *bolts*, which are trimmed (or slit with a
paper knife) before the leaves can be turned.

**The imposition is computed from the folded stack.** The simple-fold model keeps the layers in
order. Page 1 is the outer face whose spine lies on the binding side when its head is up; the pages
are numbered down the stack, recto then verso of each leaf. Each page's head direction is mapped
back to the flat sheet, so the cartridge knows which pages print head down. `main.py` then checks
the result against three classical rules and fails loud otherwise:

1. one side of the sheet carries pages 1, 4, 5, 8, … (the **outer forme**, the side with the first
   and last pages) and the other pages 2, 3, 6, 7, … (the **inner forme**);
2. the two pages either side of a spine fold add up to the page count plus one (4 + 1, 13 + 4 …);
3. posed in 3-D with `pliego.kinematics.face_transforms`, every folded page's head points the same
   way.

For the default octavo with left binding, the formes come out as follows. ↓ marks a page printed
head down; the inner forme is read with the sheet turned over left to right:

| forme | top row | bottom row |
|---|---|---|
| outer | 1↓ 16↓ 13↓ 4↓ | 8 9 12 5 |
| inner | 3↓ 14↓ 15↓ 2↓ | 6 11 10 7 |

This is the classical octavo outer forme (bottom row 4 13 16 1, top row 5 12 9 8 head down) turned
through 180°. The quarto prints its pages sideways, heads toward the middle; the folio prints 4 and
1 on the outside, 2 and 3 inside. With right binding the imposition is mirrored. The studio draws no
text on faces, so the step notes carry the computed formes.

**Gathered and sewn.** Identical signatures are posed folded (the spine sprung 2° open, as real
paper does) and stacked one signature's thickness apart (leaves × caliper + 0.5 mm). The sewing is
modelled as `string` joins: the thread runs inside each centre fold between sewing stations (10 mm
from head and tail, with two to four more evenly spaced between them), and kettle stitches link each signature to the
next at head and tail. Signature k carries pages 16·(k − 1) + 1 to 16·k (octavo).

## The fold program

Mode `signature`, kinematic: one step per fold. A fold through a stack turns the moving half of the
stack rigidly about the fold line, so every segment of that fold moves by the same angle while the
earlier folds stay shut: the motion is linear in the angles and exact. `main.py` checks it with
`pliego.kinematics.closure_residual` halfway through and at the end of every fold.

Mode `gathered`: the book block is the initial frame; the program opens the book at the centre of
the signature on top (its spine segments go to 0°, carrying half of that signature over) and closes
it again. The studio poses each sheet from its lower-left leaf, which lies in the first half of
every signature with left binding, so a left-bound book is shown lying face down and opens at the
centre of its last signature; a right-bound one lies face up and opens at signature 1.

**Preview and engine.** The studio preview runs both programs. Gathering and sewing need string
joins, which only the physics engine resolves: the preview shows the sewn block as posed (the
thread does not move anything there), and turning single leaves needs the bolts trimmed, which
this document does not model (a sewn but untrimmed book opens only at the centre of a signature,
which is what the program shows).

## Making one by hand

1. Print the eight (octavo) pages of each forme in the layout above on the two sides of the sheet,
   or simply number a blank sheet as a folding dummy: fold it, write 1, 2, 3 … on the folded pages,
   and unfold it.
2. Fold in half across the long side, left half over the right; crease with a bone folder.
3. Fold in half again, at right angles, top half down; then again at right angles for an octavo.
   Keep the folds square to each other.
4. Gather the signatures in order, pierce sewing stations along the centre fold, and sew through
   the fold, linking each signature to the last with a kettle stitch at head and tail.
5. Trim (or slit with a paper knife) the head and fore-edge folds so the leaves turn.

## Parameters

| id | meaning | default | range |
|---|---|---|---|
| `imposition` | `folio`, `quarto` or `octavo` | `octavo` | |
| `binding` | `left` (left-to-right reading) or `right` | `left` | |
| `sheet_width`, `sheet_height` | the press sheet, laid landscape | 594 × 420 mm (A2) | 200–1000, 140–1000 mm |
| `stock` | `copy-80`, `washi-kozo-30`, `kraft-120` | `copy-80` | |
| `signatures` | signatures gathered (mode `gathered`) | 3 | 2–6 |

Presets: `a2` (594 × 420 mm), `a3` (420 × 297 mm), `us-tabloid` (431.8 × 279.4 mm).

## History and sources

Books printed two pages to a side and folded once are folios; four pages to a side and folded
twice, quartos; eight pages to a side and folded three times into gatherings of sixteen pages,
octavos; the arrangement of the pages in the press is the imposition (Wikipedia, «Book size»,
https://en.wikipedia.org/wiki/Book_size). The outer forme is the one that prints the side of the
sheet on which the first and last pages appear (Merriam-Webster, «outer form»,
https://www.merriam-webster.com/dictionary/outer%20form). Sewing through the fold is the
traditional standard for bound books, the kettle stitch is a common link stitch, and a sheet folded
in quarto has folds at the spine and at the top that must be trimmed before the leaves can be
turned (Wikipedia, «Bookbinding», https://en.wikipedia.org/wiki/Bookbinding). In Spanish a
*pliego* is a sheet of paper with one or more folds (Wikcionario, «pliego»,
https://es.wiktionary.org/wiki/pliego). No imposition scheme is copied from a manual: the folds and
the page order are computed by this cartridge and checked against the rules above.

## Provenance and licence

Original MADFAM geometry for the traditional formats of the printing and bookbinding trades.
Published under CERN-OHL-W-2.0 like every object in the commons (see the commons root `LICENSE`).
