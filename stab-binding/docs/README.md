# Japanese stab binding

| | Title | Summary |
|---|---|---|
| en | Japanese stab binding | A stab-bound book in the fukuro-toji tradition: folded or single leaves between two covers, holes stabbed beside the spine and a thread sewn round the spine, head and tail, in four patterns with generated hole layouts and computed sewing routes. |
| es | Encuadernación japonesa cosida | Un libro cosido a la japonesa, en la tradición del fukuro-toji: hojas dobladas o sencillas entre dos tapas, agujeros junto al lomo y un hilo cosido alrededor del lomo, la cabeza y el pie, en cuatro patrones con agujeros calculados y recorridos de costura calculados. |
| fr | Reliure japonaise cousue | Un livre cousu à la japonaise, dans la tradition du fukuro-toji : feuillets pliés ou simples entre deux couvertures, trous percés le long du dos et fil cousu autour du dos, de la tête et de la queue, en quatre motifs aux trous et aux parcours de couture calculés. |
| pt | Encadernação japonesa costurada | Um livro costurado à japonesa, na tradição do fukuro-toji: folhas dobradas ou simples entre duas capas, furos junto à lombada e uma linha costurada em volta da lombada, da cabeça e do pé, em quatro padrões com furos e percursos de costura calculados. |

## What it is

Stab binding (fukuro-toji, «pouch binding») is the sewn book of East Asia: sheets are folded in
half and stacked, holes are pierced through the whole stack along the spine and the covers are
sewn on with thread, with no paste. In the Japanese four-hole form (yotsume toji) the thread
passes through each hole, wraps round the spine and, at the two end holes, round the head and the
tail. Decorative variants add holes and stitches: the noble or Kangxi binding (kōki toji), the
hemp leaf (asa-no-ha toji) and the tortoise shell (kikkō toji).

The cartridge builds the whole book as sheets: a front cover, the text leaves and a back cover,
every one carrying the same holes. Two modes:

- `fukuro` — each text leaf is one sheet folded in half, the fold at the fore-edge and the two open
  edges at the spine (the pouch); both halves are holed so the holes meet when the leaf is folded.
- `single` — single text leaves, one layer each.

The `pattern` select picks the stitch pattern; the page width, book height, number of leaves,
spine margin, hole diameter, hinge distance and the two papers are parameters.

## Geometry

All dimensions are computed by `main.py` in sheet millimetres. W is the page width (spine to
fore-edge), H the book height (head to tail), d the spine margin, r the hole radius.

| sheet | outline | lines | edge names |
|---|---|---|---|
| front cover | W × H | the hinge score (valley, scored) at x = x_deep + r + gap | `spine`, `hinge` |
| text leaf, `fukuro` | 2W × H | the fore-edge fold (mountain 180°) at x = W; holes on both halves, mirrored | `spine` (both open edges), `fore-edge` |
| text leaf, `single` | W × H | none | `spine`, `fore-edge` |
| back cover | W × H | none | `spine` |

Holes are 16-sided polygons whose inscribed circle has the chosen diameter, cut through every sheet
with `sheet.hole`, every polygon turned by half a side. (An earlier kernel's hole bridging could
graze a polygon corner and leave a face that is not simple, so the script searched for a turn that
worked; the kernel's split cuts made the search unnecessary, and it is gone. A sweep of the four
patterns over book heights 100–400 mm and hole diameters 1.5 and 3.3 mm built a valid document
every time.) Each sheet type is checked with `pliego.papercut.analyze` (one connected piece,
every bridge at least the stock's minimum feature); the script also checks that every hole keeps
the minimum feature from the spine, head and tail and from its neighbours, that no stitch runs over
a hole it does not use, and that the hinge leaves at least 40 mm of page.

**The hinge.** The Tokyo Metropolitan Library's guide finishes the book by creasing the cover
about 1 mm from the thread line toward the fore-edge, so it opens there. The cartridge places that
score `hinge_gap` (default 1 mm) outside the rim of the outermost hole, never less than the cover's
minimum feature, so the score never touches a hole. The text leaves are not scored: they bend
there by themselves, and nothing is drawn for it.

## The stitch patterns

The hole layouts are **MADFAM's own rules**, generated from H and d. The sources cited below
describe the patterns in words (four holes; two extra holes at the corners for the noble binding;
Y-shaped stitches between the main holes for the hemp leaf; triangular groups of holes whose
stitches wrap round the spine in parallel for the tortoise shell) but give no measurements, so the
positions below are an original layout in each pattern's spirit, not a reproduction of a
historical binding or of any binder's diagram.

Every pattern starts from four main stations on the row x = d: the outer two e = H/8 in from the
head and the tail, the inner two dividing the span between them in thirds.

| pattern | holes | added holes (rule) | outside stitches, front and back alike |
|---|---|---|---|
| `four-hole` (yotsume toji) | 4 | — | along the row between neighbours; a spine wrap at every hole; a head wrap at hole 1, a tail wrap at hole 4 |
| `noble` (kōki toji) | 6 | a corner hole halfway along the diagonal from each outer station to its corner, (d/2, e/2) | four-hole, plus a diagonal stitch from each corner hole to its station and a spine wrap and a head (tail) wrap at each corner hole: a nested square at each corner |
| `hemp-leaf` (asa-no-ha toji) | 9 | the noble corners, plus a second row at 2d with one hole midway between each pair of neighbouring stations | noble, plus from each second-row hole a stitch to both neighbouring stations and a spine wrap: a Y between the main holes |
| `tortoise-shell` (kikkō toji) | 12 | each station gets two holes on the row 2d, s = min(gap/4, e/2) above and below it, a triangular group | the two sides of every triangle, a stitch along the second row from one group to the next, a spine wrap at every hole, head and tail wraps at the outer stations; with the spine edge each cell between two stations reads as a hexagon |

The six holes of the noble pattern agree with the Smithsonian's «binding with six holes» for
kōki toji; the hole counts of the hemp leaf and tortoise shell are this cartridge's choice.

## The sewing route and the preview

**The thread graph.** Each pattern's stitches form a graph whose nodes are (hole, side) — the
front or the back of the book. Outside stitches are row stitches on each side and spine, head and
tail wraps from front to back; through-passes go through the stack. A needle alternates between
the two kinds, so a hole needs as many passes as it has outside stitches on one side (the script
checks that front and back agree). `main.py` then builds one closed route that uses every stitch
once, alternating passes and outside stitches, starting with a pass at the second station, and
fails loud if the graph cannot be sewn in one thread. For the four-hole pattern the route is

`2↓ · 2–1 · 1↑ · spine · 1↑ · head · 1↑ · 1–2 · 2↓ · 2–3 · 3↑ · 3–4 · 4↓ · spine · 4↓ · tail · 4↓ · 4–3 · 3↑ · spine · 3↑ · 3–2 · 2↓ · spine`

(holes numbered from the head, ↓ front to back, ↑ back to front). Its length is the sum of the
outside stitches and the passes through the real stack thickness; for the four-hole pattern the
script checks it fits the Tokyo guide's thread allowance (three times the height plus the
diagonal). The route and its length are written in the `sew` step note in four languages.

**The thread as string joins.** The document records the thread as `string` joins: every row
stitch on both covers, every spine, head and tail wrap from the front cover to the back cover
(length: the stitch on both faces plus the real stack thickness), and every through-pass as a chain
from layer to layer at each hole. Nothing is drawn on the fabrication layers for the thread.

**What the preview shows.** The program has two steps: `sew` (no motion; the note gives the
route) and `open`, which turns the front cover to 178° on its hinge score while the stitched strip
stays put. The studio preview drives this sequence (string joins never disable a sequence control).
The preview draws a shut fold at 179.5°, so the lower half of each folded leaf opens W·sin 0.5° at
the spine; the back cover is placed that much lower to leave it room, and the folded leaves are
posed at that angle in the initial frame.

**What needs the physics engine.** Holding the stack together with the thread (the strings),
the thread's wrap round the spine edge (a string is a straight-line limit), the bending of the
leaves beside the stitching as they turn, and paper thickness and friction. The text leaves do
not turn in the preview because they carry no line to turn on.

## Making one by hand

1. Export the sheets (`svg`, `dxf`, `pdf` or `hpgl`). The outlines and the holes are on the cut
   layer, the leaf folds on the mountain layer and the cover's hinge on the score layer. Cut the
   holes with a punch or pierce them with an awl through the stacked book instead.
2. For `fukuro`, fold each leaf in half with the printed side out, the fold at the fore-edge.
   Stack the leaves between the covers and square the spine edge.
3. The Tokyo guide first ties the text block together with twisted paper strings (koyori)
   through holes of their own before the covers go on; this inner binding is not modelled.
4. Cut a thread three times the book's height plus the diagonal (the guide's allowance), start
   with the knot tucked among the leaves as the guide does, and sew the route from the `sew` step
   note.
5. Crease the cover along the hinge score so it opens beside the stitching.

## Parameters

| id | meaning | default | range |
|---|---|---|---|
| `pattern` | `four-hole`, `tortoise-shell`, `hemp-leaf` or `noble` | `four-hole` | |
| `page_width` | spine to fore-edge | 150 mm | 80–300 mm |
| `book_height` | head to tail | 220 mm | 100–400 mm |
| `leaves` | text leaves between the covers | 6 | 1–24 |
| `spine_margin` | spine edge to the main row of holes (second rows at twice it) | 10 mm | 8–25 mm |
| `hole_diameter` | hole size, at least the stock's minimum feature | 2 mm | 1.5–4 mm |
| `hinge_gap` | outermost hole rim to the hinge score (at least the cover's minimum feature) | 1 mm | 0.5–5 mm |
| `text_stock` | `washi-kozo-30` or `copy-80` | `washi-kozo-30` | |
| `cover_stock` | `kraft-120`, `cardstock-160` or `elephant-hide-110` | `kraft-120` | |

Presets: `a5-four-hole` (148 × 210 mm), `pocket-noble` (105 × 148 mm, four leaves, 8 mm margin),
`b5-tortoise` (182 × 257 mm) and `hemp-leaf-card` (card covers, copy paper, 2.5 mm holes). Every
preset runs in both modes.

## History and sources

Pouch binding developed from the wrapped-back binding of Ming China (1368–1644); sheets are folded
in half, stacked, pierced with four or more holes along the spine and sewn with silk thread, and
the binding is praised for using no paste, so a book can be repaired or rebound (Vanderbilt
University Library, «Threads of Tradition: Pouch Binding in East Asia»,
https://exhibitions.library.vanderbilt.edu/book-as-art/section/pouch-binding/). The binding was
developed in China and was the dominant book form in East Asia for centuries; fukuro-toji is its
Japanese name (University of Utah Library, Opening Artists' Books, «Asian stab binding»,
https://oab.lib.utah.edu/?p=700). In Japan it was used from the Muromachi period and became
widespread in the Edo period, the sheet folded so that the bound edge is opposite the fold
(Wikipedia (ja), «袋とじ», https://ja.wikipedia.org/wiki/袋綴じ); the sheet is folded with the
written side out and bound with four to six holes (Wikipedia (ja), «和装本»,
https://ja.wikipedia.org/wiki/和装本).

The Smithsonian's terminology list for Edo-period woodblock-printed books names fukurotoji
(pouch binding), yotsumetoji (binding with four holes), Kōkitoji (binding with six holes) and
shitatoji with koyori paper strips (Smithsonian National Museum of Asian Art, «Terminology List
for Illustrated Woodblock-Printed Books of the Edo Period», 2021,
https://asia-archive.si.edu/wp-content/uploads/2021/08/1.-Terminology-List-for-Illustrated-Woodblock-Printed-Books.pdf).
Holes are commonly placed about 1 cm from the spine and the stitches wrap across it (PaperSpecs,
«Japanese stab binding», https://www.paperspecs.com/glossary/japanese-stab-binding/); the thread
wraps round the spine at each hole and round the edge at the end holes (Dorset History Centre,
«Bookbinding DIY – Japanese Stab-Stitch binding»,
https://news.dorsetcouncil.gov.uk/dorset-history-centre-blog/?p=1389). The Tokyo Metropolitan
Library's guide to making a yotsume-toji book gives the koyori inner binding, the thread allowance
and the crease beside the thread line (Tokyo Metropolitan Library, «Text 7», 2005, revised 2020,
https://www.library.metro.tokyo.lg.jp/guide/uploads/07_yotume2020.pdf).

The Kangxi binding, named after an early Qing emperor, adds an embellishment at the corners; the
hemp leaf builds on it with Y-shaped stitches between the main holes; the tortoise shell is named
for its resemblance to a tortoise's shell (University of Kansas Libraries, bookbinding exhibition,
case 3, https://exhibits.lib.ku.edu/exhibits/show/bookbinding/case-3). Kikko-toji uses triangular
groups of stab holes whose stitches wrap round the spine in parallel, and asa-no-ha-toji is a
decorative variation named for the hemp leaf (University of Utah Library, Opening Artists' Books,
https://oab.lib.utah.edu/?p=1250 and https://oab.lib.utah.edu/?p=1241).

The tradition is credited to the bookbinders of China, Japan and Korea. No diagram is copied: the
hole layouts, stitch graphs and routes are generated by this cartridge.

## Provenance and licence

Original MADFAM geometry (hole-layout rules, stitch graphs, sewing routes, hinge placement) for a
traditional binding credited to East Asian bookbinders. Published under CERN-OHL-W-2.0 like every
object in the commons (see the commons root `LICENSE`).
