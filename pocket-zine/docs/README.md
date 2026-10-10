# Pocket zine

| | Title | Summary |
|---|---|---|
| en | Pocket zine | The eight-page booklet folded from one sheet with one cut, with an exact fold program and an imposition computed from the fold. |
| es | Fanzine de bolsillo | El cuadernillo de ocho páginas doblado de una sola hoja con un solo corte, con una secuencia exacta y una imposición calculada a partir del doblado. |
| fr | Fanzine de poche | Le livret de huit pages plié dans une seule feuille avec une seule coupe, avec un programme exact et une imposition calculée à partir du pliage. |
| pt | Fanzine de bolso | O livrinho de oito páginas dobrado de uma única folha com um único corte, com uma sequência exata e uma imposição calculada a partir da dobra. |

## What it is

The pocket zine (also called a mini-zine or one-page zine) turns one sheet of printer paper into
an eight-page booklet with no glue, no staples and a single cut. The sheet is printed on one side,
cut once along its middle, folded lengthwise and pushed into a cross; the four wings of the cross
then wrap round each other into a booklet a quarter of the sheet wide and half of it high. An A4
sheet gives 74.25 × 105 mm pages, a US Letter sheet 69.85 × 107.95 mm pages.

The cartridge carries the size (`sheet_width`, `sheet_height`, presets A4, US Letter and A3), the
paper and the binding side: `left` for scripts read left to right, `right` for scripts read right
to left, which reverses the page numbers.

## Geometry

One landscape sheet, W × H, divided into a grid of four columns and two rows of pages
(w = W/4, h = H/2), all in sheet-local millimetres computed by `main.py`:

| line | where | kind | edge name |
|---|---|---|---|
| slit | y = h, from x = w to x = 3w | cut | `slit` |
| head fold | y = h, outer columns | mountain 180° (the top half goes behind) | `head-fold` |
| spine folds | x = w and x = 3w, each row its own mark | valley | `spine` |
| fore-edge folds | x = 2w, each row its own mark | mountain 180° | `fore-edge` |

The slit is what makes the format work: it turns the eight pages into a closed ring of faces
around a hole. Both ends of the slit are boundary vertices, so the crease pattern has **no interior
vertex** at all; the motion is constrained only by the ring itself closing.

**The imposition is computed, not typed in.** `main.py` poses the finished booklet with
`pliego.kinematics.face_transforms`, orders the four wings along the stack, finds the outer face
whose spine lies on the chosen binding side (the cover) and numbers the faces in stack order. It
then checks the result against the classic template and checks that every page's head points the
same way (the head fold is the top edge of every page). With left binding, the front of the sheet
reads:

| | column 1 | column 2 | column 3 | column 4 |
|---|---|---|---|---|
| top row (printed upside down) | 1 (front cover) | 8 (back cover) | 7 | 6 |
| bottom row | 2 | 3 | 4 | 5 |

With right binding every page number p becomes 9 − p. The back of the sheet is never seen: every
wing is two layers held back to back by a fold, with nothing printed between them.

## The fold program

Kinematic, built with `pliego.Sequence.kinematic_path` (four exact substeps per key pose):

1. **Fold in half lengthwise, top half behind** — the head fold closes to −180°.
2. **Push the ends together** — the spine folds go to 90° while the fore-edge folds close at
   −180°; along the way the spine folds are at α and the fore-edge folds at −2α, so the two
   end columns stay in line and the slit opens into a diamond, then into a cross of four wings.
3. **Wrap the wings** — the front wing, then the left wing, fold onto the right wing and the
   back wing goes under it. The wings end 2° apart (`GAP`, for paper thickness), so the hinge
   between back and left wraps round the whole stack at −174° and the ring stays closed.

The kernel's motion solver closes vertex loops only, and the ring round the slit is not a vertex
loop, so `main.py` checks it with `pliego.kinematics.closure_residual` at every state of the
program and fails loud above 1e-6 mm (it is 1e-13 mm). The step notes carry the computed
imposition.

**Preview and engine.** The studio preview runs the whole program (sequence control `Fold the
zine`). Shut folds are drawn a hair short of flat, because zero-thickness layers cannot stack at
exactly 180°. The physics engine adds paper thickness, friction between the wings and the
springiness of the folds; it is not needed to show the making.

## Making one by hand

1. Export the sheet (`svg`, `dxf`, `pdf` or `hpgl`): the outline and the slit are on the cut
   layer, the folds on the mountain and valley layers. Lay out the eight pages on the front with
   the imposition above, the top row upside down.
2. Crease the grid: fold in half lengthwise, unfold; in half across, unfold; each end to the
   centre, unfold.
3. Fold in half across and cut along the middle crease from the fold to the quarter crease: that
   is the slit, half the sheet's width long. Unfold.
4. Fold in half lengthwise with the top half going behind. Hold the ends and push them together
   until the slit opens into a cross, then wrap the pages round with the front cover outside.

## Parameters

| id | meaning | default | range |
|---|---|---|---|
| `sheet_width` | long side of the sheet (landscape) | 297 mm | 180–600 mm |
| `sheet_height` | short side, not more than the width | 210 mm | 120–450 mm |
| `stock` | `copy-80` or `kraft-120` | `copy-80` | |
| `binding` | `left` (left-to-right reading) or `right` | `left` | |

Presets: `a4` (297 × 210 mm), `us-letter` (279.4 × 215.9 mm), `a3` (420 × 297 mm, A6 pages).

## History and sources

Zines are small, self-published, usually photocopied magazines; the science-fiction fanzines of
the 1930s, the punk zines of the 1970s and the riot grrrl zines of the 1990s are part of their
history (Wikipedia, «Zine», https://en.wikipedia.org/wiki/Zine). The one-sheet, one-cut
eight-page format is taught in libraries, studios and schools as the easiest zine to copy and
fold: fold the sheet into eighths, cut the middle line from the fold to the centre, refold
lengthwise and push the ends together into a plus sign (University of Wisconsin–Madison, Wisconsin
Union Wheelhouse Studios, «One Page Zine Instructions»,
https://union.wisc.edu/events-and-activities/open-art-studio-and-classes/wheelhouse-studios-at-home/one-page-zine-instructions;
Niagara County Community College Library, «Zines: Make Zines»,
https://libguides.niagaracc.suny.edu/zines/makezines). The format has no known single inventor
and is credited here to the zine tradition. No template is copied; the layout and the page
order are computed by this cartridge.

## Provenance and licence

Original MADFAM geometry and fold program for a traditional folk format. Published under
CERN-OHL-W-2.0 like every object in the commons (see the commons root `LICENSE`).
