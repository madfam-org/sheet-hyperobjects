# Paper crown

| | Title | Summary |
|---|---|---|
| en | Paper crown | A band of card with zigzag points, battlements or scallops along its top edge, rolled into a ring and glued with a plain overlap. |
| es | Corona de papel | Una banda de cartulina con picos en zigzag, almenas u ondas en el borde superior, enrollada en un aro y pegada con un traslape liso. |
| fr | Couronne en papier | Un bandeau de bristol à pointes en zigzag, créneaux ou festons sur le bord supérieur, roulé en anneau et collé par un recouvrement uni. |
| pt | Coroa de papel | Uma faixa de cartão com pontas em zigue-zague, ameias ou ondas na borda superior, enrolada num aro e colada com uma sobreposição lisa. |

## What it is

The cut-and-rolled paper crown: a strip of card as long as a head is round, its top edge cut into
points, rolled into a ring and closed with a glued overlap. One generator makes three edge styles:

- **zigzag points**, the classic crown;
- **battlements** (castellated), square teeth and gaps;
- **scallops**, rounded waves.

The head size, the heights of the band and the points, and the number of points are parameters.

## Geometry

The band is a strip `head` long (the ring's inner circumference C) plus a 25 mm overlap. Its top
edge repeats one point every C / `points`: a triangle for zigzag, a half-period step for
battlements, a half sine wave for scallops (sampled at four vertices per panel). The overlap is a
plain band, without points, chamfered at its corners so it slides inside easily.

**Segmentation.** The rolled band is a curved surface, modelled as a prism of narrow flat panels:
vertical `F` lines (treatment `none`: plain paper, never scored or cut) from the bottom edge to the
decorated top edge, `sub` per point (6 by default). They are placed so that a line passes through
every valley, every peak and every battlement step, and every line ends on an outline vertex. The
closed crown is an exact isometry of the sheet: an upright regular N-gon prism (N = `points` ×
`sub`), each side one panel wide, circumradius w / (2 sin(π/N)). For the default crown, N = 48,
the panel width is 11.67 mm and the ring's radius is 89.19 mm.

The overlap is segmented like the rest. In the closed crown it lies exactly on the first panels,
inside the ring, and a `glue` join welds it there (map = translation by −C). The script checks the
weld and the valley roll, and fails loud otherwise. The cut outline is checked with
`pliego.papercut.analyze` against the stock's minimum feature. The colour is on the back of the
sheet, which becomes the outside.

## The fold program

**Mode `make`** is a `kinematic` program on the panel lines, the one the studio preview plays:

1. curl the band into a loose ring (every line at half its final angle);
2. close the ring until the ends meet;
3. slide the plain overlap inside and glue it;
4. hold the overlap until the glue sets.

The overlap's glue is a `glue` join with `active_from: "press"` (sheet-document spec §5.19): the
band starts flat and the program ends glued. It ends in the ring, which is also written as the
frame `target:crown`. The crown stands on its side because the preview keeps the first panel on
the table.

**Mode `glued`** is the finished crown for the physics engine: the glue weld and an `initial` frame
standing upright. Its `physical` program presses the crown flat to store it (two layers, folds at
the seam and at the opposite line) and opens it again. The weld holds in both states; the flat state
is written as `target:flat`.

**Why two modes.** Step-activated glue would let one physical program roll the flat band, glue it
and then press it flat and open it. Measured in the physics engine, it does not close: driven
crease by crease, the rolled band's ends stay 37 mm apart after the close step (42 mm after the
overlap step), so the glue finds nothing to weld when it switches on. A kinematic program closes
the ring exactly but holds the sheet rigid, so it cannot show the weld keeping the ring shut while
it is pressed flat. Until the engine can close a rolled band, `make` shows the making and `glued`
shows the glued crown's physics.

**Preview and engine.** The preview plays both programs exactly at their ends. In between, the flat
press is a straight blend of angles, so the overlap drifts off the glue for a moment; the engine
keeps the weld and bends the card instead. Fitting the crown on a head is not modelled.

## Making one by hand

1. Export the band (`svg`, `dxf`, `pdf` or `hpgl`) and cut it out. The default band is about
   595 × 90 mm, longer than A3: cut it from a long strip of card or print the PDF in tiles and join
   them with a glue lap. The panel lines are not on the cut file.
2. Curl it, coloured side out, into a ring.
3. Put glue on the plain overlap and slide it inside the other end. Hold it until the glue grips.

Card of 250 g/m² keeps tall points upright; lighter paper droops.

## Parameters

| id | meaning | default | range |
|---|---|---|---|
| `edge` | top edge: `zigzag`, `castellated`, `scalloped` | `zigzag` | |
| `head` | head circumference (the ring's inner length) | 560 mm | 400–640 mm |
| `band` | height of the band below the points | 40 mm | 20–80 mm |
| `point` | height of the points | 50 mm | 15–120 mm |
| `points` | number of points around | 8 | 5–16 |
| `sub` | panels per point (model resolution, not cut) | 6 | 4–12, even |
| `stock` | `cardstock-250`, `cardstock-160`, `foil-paper`, `kraft-120` | `cardstock-250` | |
| `colour` | colour of the outside | gold | five colours |

Presets: `child` (500 mm, scallops), `castle` (battlements), `tall-points` (12 tall points, foil).

## History and sources

Paper crowns are worn at celebrations. Wikipedia notes that Christmas crackers traditionally
contain a crown-shaped hat of tissue paper, usually worn at Christmas dinner; crackers were invented
by Tom Smith of London in 1847, and the paper hats were added later by his son Walter Smith
(Wikipedia, «Christmas cracker», https://en.wikipedia.org/wiki/Christmas_cracker). No published
template is copied; the band and its edges are computed by this cartridge.

## Provenance and licence

Original MADFAM geometry; the lineage credits the paper crown as a common celebration object rather
than any designer. Published under CERN-OHL-W-2.0 like every object in the commons (see the commons
root `LICENSE`).
