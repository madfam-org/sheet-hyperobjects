# Saddle-stitched booklet

| | Title | Summary |
|---|---|---|
| en | Saddle-stitched booklet | The stapled booklet of nested folded sheets, with the creep of the inner sheets computed from the paper's caliper and trimmed off in advance, a computed imposition and the staples as joins. |
| es | Cuadernillo engrapado a caballete | El cuadernillo engrapado de pliegos doblados uno dentro de otro, con el corrimiento de los pliegos interiores calculado con el calibre del papel y refinado de antemano, una imposición calculada y las grapas como uniones. |
| fr | Livret piqué à cheval | Le livret agrafé de feuilles pliées emboîtées, avec la chasse des feuilles intérieures calculée d'après l'épaisseur du papier et recoupée d'avance, une imposition calculée et les agrafes comme liens. |
| pt | Livreto com grampo canoa | O livreto grampeado de folhas dobradas encaixadas umas nas outras, com o deslocamento das folhas internas calculado pela espessura do papel e refilado de antemão, uma imposição calculada e os grampos como uniões. |

## What it is

A saddle-stitched booklet is the simplest bound book: sheets printed with four pages each (two
per side) are folded once, nested one inside the other and stapled through the fold. The page
count is therefore a multiple of four, and the outer sheet is the cover: either the same paper
(self-cover) or a heavier sheet. The name comes from the saddle, the V-shaped support over which
the folded sheets are draped for stitching.

The cartridge carries the page count (`pages`, 8 to 64, i.e. 2 to 16 sheets), the finished page
size (presets A5, A6, US half-letter and an A5 64-page booklet with a 250 g/m² cover), the text
paper and the cover paper, the creep rule, the number of staples and the binding side (`left` for
scripts read left to right, `right` for right to left, which mirrors the imposition).

## Geometry

Each sheet is its own document sheet, `sheet-1` (the cover) to `sheet-n`, n = pages / 4. Sheet k
(counted from the outside, cover k = 0) is a rectangle 2·(w − shift_k) wide and H high, with one
valley fold, `spine`, at its centre (scored on a cardstock cover, plain crease otherwise) and its
two short edges named `fore-edge`. The grain runs parallel to the spine. The sheets are nested in
3-D with `pliego.Placement`: the fold of each sheet lies one fold spacing outside the fold it wraps.

**Imposition, computed.** `main.py` poses the shut booklet, orders its 2n leaves along the stack
(checking they are nested cover-outside), finds the front cover from the binding side and numbers
the faces in reading order. The result is compared with the classic rule and the script fails if
they differ. For N pages and left binding, sheet k carries (left|right as you look at each face,
the outside seen with the sheet turned over):

| sheet | outside | inside |
|---|---|---|
| 1 (cover) | N \| 1 | 2 \| N − 1 |
| k + 1 | N − 2k \| 2k + 1 | 2k + 2 \| N − 2k − 1 |
| 16-page example, sheet 4 | 10 \| 7 | 8 \| 9 |

With right binding, left and right swap on every face. The studio renders no text on faces, so
the page numbers of every sheet are written into the note of the first fold step and the cover's
are printed on the read-proof line (`cover=16|1/2|15`).

## Creep (shingling)

When folded sheets are nested, each sheet wraps round all the sheets inside it, so the inner
sheets stick out at the fore-edge. Printers call this creep, and compensate it by shingling:
moving the page images of the inner pages progressively toward the binding (Kodak). Without it,
content on the centre pages ends up closer to the trimmed edge than on the outer pages
(Printivity).

**The formula.** The fold of sheet j + 1 sits (t_j + t_{j+1}) / 2 inside the fold of sheet j
(t = the caliper of each sheet, read from its stock card: copy paper 0.10 mm, kraft 0.16 mm,
washi 0.08 mm, cardstock 0.20 or 0.30 mm). Adding these spacings, the fold of sheet k lies
D_k = Σ_{j<k} (t_j + t_{j+1}) / 2 inside the cover's fold, and its fore-edge pushes out by

    shift_k = f · D_k,   f = 1 (pressed fold) or π/2 (round fold).

With one paper throughout this is shift_k = k·t or (π/2)·k·t.

* **Pressed fold, f = 1** (default): each sheet adds one caliper. A fold pressed flat takes, on
  each side, half the thickness of the stack it wraps. This is the trade rule of thumb: Kodak's
  approximate formula is (pages / 4) × stock thickness for the whole booklet, and a common
  variant counts (pages / 4 − 1) calipers because the cover wraps no sheet of its own (PrintPlanet
  forum), which is what this rule gives for the innermost sheet.
* **Round fold, f = π/2**: the folds are concentric half-circles around the middle of the stack,
  as a thick unpressed booklet looks from the head; each half-circle is longer than the one inside
  it by π/2 per caliper on each side. A PrintPlanet contributor describes this "((((((" shape and
  gives a π-based formula.

Both are starting points: the sources agree that the creep of a real job is best measured on a
folded dummy of the same paper.

**Applying it.** This cartridge pre-trims: sheet k is cut 2·shift_k narrower than the cover,
centred on its fold, so the fore-edges line up once the booklet is folded and no guillotine trim
is needed (the trade's way is to print oversize and trim after stitching; the result is the
same). In both cases lay each page out from its fore-edge, not from the fold: the gutter of page
k is shift_k narrower, which is the shingling.

**Self-check.** The nest is folded again in 3-D with thickness: for every sheet an auxiliary sheet
whose fold is a band of m facets lying on the half-circle of that sheet's radius in the stack
(m = 1 for the pressed fold, a flat spine strip; m = 60 for the round one), posed with fold angles
through `pliego.kinematics.face_transforms` and placed at its layer height. The script checks
that each sheet wraps exactly onto its layer and that all 2n trimmed fore-edges coincide within
0.005 mm; the spread is printed (`fore-edge-spread`, about 1e-13 mm pressed and 3e-4 mm round,
the facet error).

Shifts per sheet, outside in (mm per side):

| booklet | rule | shifts |
|---|---|---|
| 16 pages, copy paper (default) | pressed | 0, 0.10, 0.20, 0.30 |
| 32 pages, kraft paper | pressed | 0, 0.16, 0.32 … 1.12 |
| 64 pages, copy paper | pressed | 0, 0.10, 0.20 … 1.50 |
| 64 pages, copy paper | round | 0, 0.16, 0.31 … 2.36 |
| 64 pages, 250 g/m² cover | pressed | 0, 0.20, 0.30 … 1.60 |
| 64 pages, 250 g/m² cover | round | 0, 0.31, 0.47 … 2.51 |

The heavier cover moves every inner fold by (0.30 + 0.10) / 2 = 0.20 mm at once.

## The fold program

A kinematic program of three steps (sequence control `Stitch the booklet`); every sheet has a
single fold, so the angles move linearly and every in-between state is exact:

1. **Nest the sheets and fold them over the saddle**: from open flat to half shut. The note
   lists the page numbers of every sheet.
2. **Staple through the spine fold**: the booklet holds still; the note gives the staple
   positions from the head.
3. **Fold the booklet shut**; the note gives the creep trims.

**Layer order in the preview.** Sheets without thickness cannot stack at exactly 180°. The
preview therefore nests the creases a fold spacing apart and fans the sheets by 0.2° per layer;
the innermost sheet shuts to 179.5°, the preview's flat limit. `main.py` checks at five states of
the fold that every inner sheet lies inside the wedge of the sheet that wraps it, so no layers
cross. The shut booklet shows as slightly open, about 6.5° at the cover for 64 pages.

**Staples.** Each staple is a chain of `string` joins between the spine folds of consecutive
sheets at the staple height, each as long as the fold spacing: the physics engine will keep the
folds from parting there. String joins are used, not drawn marks, because a staple is hardware
and the fabrication layers must carry only what is cut or folded. They are not `pin` joins either,
since a staple ties the sheets to each other, not to the world. The staples sit at (2i + 1)/(2m)
of the spine for m staples: ¼ and ¾ of the spine for two (52.5 and 157.5 mm on A5); ⅙, ½ and ⅚ for
three.

**Preview and engine.** The studio preview runs the whole program, since joins never disable a
sequence. The physics engine adds what the preview cannot show: paper thickness and bending at
the spine, the strings holding the nest at the staples, and the springiness of the folds.

## Making one by hand

1. Export the sheets (`svg`, `dxf`, `pdf` or `hpgl`): each sheet's outline is on the cut layer,
   already trimmed for creep, and its fold on the valley layer. Print the pages with the
   imposition from the first step note, each page laid out from its fore-edge.
2. Cut the sheets out. Fold each sheet in half along its fold, printed inside; score a cardstock
   cover first.
3. Nest the sheets in order, sheet 2 inside the cover and so on, and line up the folds and the
   head.
4. Open the nest over a saddle, or flat on a board, and staple through the fold from the outside
   at the noted positions; clinch the legs flat in the centre spread. A long-reach stapler does
   this flat.
5. Fold shut and press the spine. The fore-edges meet without trimming. If your paper's caliper
   differs from the stock card, or a dummy shows a different creep, change the rule or the paper.

## Parameters

| id | meaning | default | range |
|---|---|---|---|
| `pages` | total pages, covers included (multiple of 4) | 16 | 8–64 |
| `page_width` | finished page, fold to fore-edge | 148 mm | 70–300 mm |
| `page_height` | head to foot (spine length) | 210 mm | 70–420 mm |
| `stock` | text paper: `copy-80`, `kraft-120`, `washi-kozo-30` | `copy-80` | |
| `cover_stock` | `self`, `cardstock-160`, `cardstock-250`, `kraft-120` | `self` | |
| `creep_rule` | `pressed` (1 caliper per sheet) or `round` (π/2) | `pressed` | |
| `staples` | number of staples | 2 | 2–3 |
| `binding` | `left` (left-to-right reading) or `right` | `left` | |

Presets: `a5` (148 × 210 mm), `a6` (105 × 148 mm), `us-half-letter` (139.7 × 215.9 mm) and
`a5-card-cover-64` (A5, 64 pages, 250 g/m² cover).

## History and sources

Saddle stitching secures folded sheets through the centre fold with wire staples that pass
through all the leaves and are clinched inside. A saddle stitch stapler aligns the fold on its
V-shaped saddle so the staple legs go in on either side of the crease (Wikipedia, «Saddle stitch
stapler», https://en.wikipedia.org/wiki/Saddle_stitch_stapler). Each folded sheet carries four
pages, never consecutive: on an eight-page booklet the outer sheet prints 8 and 1 on one side
and 2 and 7 on the other. The sheets are nested, folded together and stitched with two staples
through the spine, driven from outside and clinched inside; taller pieces take three (4over4,
«What a Saddle Stitched Booklet Is and Why Pages Come in Fours»,
https://v2.4over4.com/guide/what-is-a-saddle-stitched-booklet). Stitching machines let the
operator adjust the staple spacing (pitch) (Konica Minolta, AccurioPress C7100/C7090 user's
guide, «Adjusting Booklet Finishing»,
https://manuals.konicaminolta.eu/ineo-plus-7100-7090/EN/contents/guide03_05_06.html). The ¼–¾
placement is this cartridge's even-spacing convention; no fetched source states it as a rule.

Creep and its compensation: Kodak workflow documentation, «Shingling the Page Images for Creep
Compensation» (https://workflowhelp.kodak.com/x/1QDTE): creep pushes the inner sections out at the
fold, compensated by shingling the page images toward the binding; approximate formula
(pages / 4) × stock thickness; a dummy gives the exact value. PrintPlanet forum, «Creep, how do you
calculate it?» (https://printplanet.com/threads/creep-how-do-you-calculate-it.19494/): the
caliper-per-four-pages rule, the (pages / 4 − 1) variant, the round "((((((" spine and a π-based
formula, and advice to measure a bindery dummy. Printivity, «What is Creep in a Saddle-Stitch
Booklet?» (https://www.printivity.com/insights/what-is-creep-in-a-saddle-stitch-booklet): inner
pages end up with narrower trim margins, and content nearer the centre must shift inward more.

Saddle stitching is a print-trade practice with no single inventor. No template is copied; the
sheet sizes, creep trims, page order and staple positions are computed by this cartridge.

## Provenance and licence

Original MADFAM geometry, creep model, imposition check and fold program for a common
print-finishing format. Published under CERN-OHL-W-2.0 like every object in the commons (see the
commons root `LICENSE`).
