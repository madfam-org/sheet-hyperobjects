# Print folds

| | Title | Summary |
|---|---|---|
| en | Print folds | Every commercial print fold from one generator: letter, z-fold, gatefold, French, roll, double parallel, accordion, cross and map folds, with allowances computed from the caliper and an exact fold program. |
| es | Plegados de imprenta | Todos los plegados comerciales de imprenta con un solo generador: tríptico enrollado, zigzag, díptico de puertas, francés, enrollado, doble paralelo, acordeón, cruzado y de mapa, con holguras calculadas con el calibre y una secuencia exacta. |
| fr | Pliages d'imprimerie | Tous les pliages commerciaux d'imprimerie avec un seul générateur : pli lettre, en Z, fenêtre, à la française, roulé, double parallèle, accordéon, croisé et carte, avec des jeux calculés d'après l'épaisseur et un programme exact. |
| pt | Dobras gráficas | Todas as dobras gráficas comerciais com um só gerador: carta, Z, folder com portas, francesa, enrolada, paralela dupla, sanfona, cruzada e mapa, com folgas calculadas pela espessura e uma sequência exata. |

## What it is

The folds a print shop's folding machine puts into leaflets, brochures, menus, inserts and maps.
One sheet, one `style` parameter:

| style | folds | finished piece |
|---|---|---|
| `letter` | two parallel folds, rolled in (C fold, tri-fold) | a third of the sheet; the end panel tucks inside |
| `z-fold` | two parallel folds in opposite directions | a third of the sheet, equal panels |
| `gatefold` | two doors folded to the middle | half the sheet plus the gap; the doors stop short of the centre |
| `french` | in half, then in half across (right-angle fold) | a quarter of the sheet, four panels |
| `roll` | 4–8 panels rolled in, each inner panel narrower | the outer panel |
| `double-parallel` | in half, then in half again, parallel | a quarter of the width, the folded edge inside |
| `accordion` | 4–8 panels, folds alternating (concertina) | one panel |
| `cross` | in half, then a letter fold across | half the width × a third of the height |
| `map` | an accordion, then folded across in two or in a Z of three | one panel of the grid |

Presets set only the sheet: A4, US Letter, US Legal, Tabloid and A3, every one valid for every
style (the map fold usually goes on Tabloid or A3). The stock selects text paper or card; card is
scored.

## Geometry

**The crease pattern is folded, not drawn.** `main.py` describes each style as the sequence of
folds a finisher makes: a directed fold line in the world frame, valley or mountain. It folds the
sheet with the kernel's simple-fold model (`pliego.simplefold.FoldedState`): every fold splits
the layers it meets, reflects the moving part and restacks it, and records the crease it made in
each layer, in the sheet frame, with its M/V assignment. These segments become the sheet's
creases. A fold that goes through stacked layers therefore gets one segment per layer, and the
segments on the far side of an earlier fold come out with the opposite assignment, because that
layer is face down: the French fold's cross fold is valley on one half and mountain on the other,
and the map fold's cross fold alternates valley/mountain across every accordion panel. Every
crossing is a flat-foldable degree-4 vertex (three of one kind, one of the other).

The script then checks, failing loud:

- the folded stack's bounding box equals the expected finished size, and it has one layer per
  panel;
- no panel is narrower than 25 mm;
- the fold program closes at every state (below).

**Allowances.** A panel that folds inside another must stop short of the fold that wraps round
it, or it buckles against it. The cartridge uses the trade step, `allowance` (default 1/16 in =
1.6 mm), and raises it where the paper inside the wrap needs more: a fold that closes round
k layers needs at least (k + 1) × caliper. That bound comes from the bend: a 180° fold round a
stack of thickness T = k·c has its middle surface on a half-circle of radius (T + c)/2, so the
tucked edge must stop about π(T + c)/4 − T/2 ≈ 0.29 T + 0.79 c short of the fold line, which
(k + 1)·c always covers. It only matters on card and with many layers (an 8-panel roll on 300 g/m²
card gets 2.5 mm, 2.2 mm and 1.8 mm for its deepest tucks); on text paper the trade step governs.

| style | rule (a = allowance used) | panel widths |
|---|---|---|
| `letter` | the tuck-in panel is a narrower; k = 1 | (W + a)/3, (W + a)/3, (W + a)/3 − a |
| `roll` | panel i (i ≥ 2) is aᵢ narrower than panel i − 1, aᵢ for k = n − i layers | w, w, w − a₂, w − a₂ − a₃, … (sum = W) |
| `gatefold` | each door stops a short of the centre line (gap 2a); at least one caliper | (W − a)/4, W/2 + a, (W − a)/4 |
| `double-parallel` | the folded-in pair of panels is a narrower than the outer pair; k = 2 | s + a, s, s, s + a with s = (W/2 − a)/2 |
| `cross` | the tuck-in third across is a narrower; k = 2 (the sheet is halved) | heights (H + a)/3, (H + a)/3, (H + a)/3 − a |
| `z-fold`, `accordion`, `french`, `map` | no panel goes inside another | equal panels |

With the defaults these give the trade's published layouts: a US Letter letter fold of
3.6875, 3.6875 and 3.625 in, and an 11 × 17 in double parallel of 4.28 in outer and 4.22 in inner
panels (4over4, below).

**Scoring.** The rule is by stock: text papers (80 and 120 g/m² here) get plain creases; card
stocks (160 g/m² and up) get every fold with the `score` treatment, because heavy stock cracks
along an unscored fold (see the commons object `score-vs-crease`, and the sources below). The
grain runs along the parallel folds (`grain_deg` 90). The cross folds of the French, cross and
map styles necessarily run against it; on card that fold is scored like the others.

**Names.** Fold edges are named by role: `cover-fold`, `tuck-fold`, `roll-fold`, `panel-fold`,
`door-fold`, `half-fold`, `parallel-fold` and `cross-fold`. The interfaces expose `cover-fold`
(letter and roll) and `cross-fold` (French, cross and map).

The studio renders no print on faces. The panel widths, the allowances used, the treatment and
the finished size are written into the first step's note and printed on the read-proof line.

## The fold program

Kinematic (`pliego:sequence` mode `kinematic`), four substeps per fold, in the order a finisher
folds: the tuck-in panel first, then the cover (letter, roll); the right panel back, then the left
over (z-fold); left door, right door (gatefold); the first parallel fold, then the cross folds
(French, cross, map); the end panel first, alternating (accordion).

While a fold turns from 0 to 180°, every earlier fold is held shut at exactly ±180°. All the
layers the fold meets are then coplanar, and every crease of that fold turns by the same angle,
valley +θ and mountain −θ. The motion is linear in the angles, so each state the studio
interpolates is an exact rigid state. `main.py` checks it with `pliego.kinematics.closure_residual`
(which tests every hinge, crossings included) at every substep and fails loud above 1e-6 mm; it is
about 1e-13 mm. With the sign of the French fold's mountain cross-fold segment flipped, the residual is
210 mm, so the check has teeth.

The last step opens the outermost fold (both doors of a gatefold) by `display_open` (default 60°),
the way a leaflet is shown in a rack or opened by a reader; with 0 the piece ends folded as
delivered.

**Preview and engine.** The studio preview runs the whole program (sequence control `Fold and
display`). It draws shut folds at 179.5° so stacked layers do not share a plane; during a cross
fold this leaves a fraction of a millimetre of mismatch at the crossing, which the document itself
does not have. Paper thickness, creep (the outer layers of a thick stack pushing out past the
inner ones) and the springback of unscored card are physics; they are what the allowances pay
for, and they wait for the physics engine. Nothing in the preview needs it.

## Making one by hand

1. Export the sheet (`svg`, `dxf`, `pdf` or `hpgl`). The outline is on the cut layer; the folds
   are on the valley and mountain layers, or on the score layer for card. Print the artwork with
   the panel widths from the first step's note.
2. On card, score every fold first with a bone folder against a ruler, on the side the fold
   closes away from.
3. Fold in the order of the program. For the letter and roll folds, start with the narrowest end
   panel. For the French, cross and map folds, finish all the parallel folds, then turn the piece
   a quarter turn and fold across through all the layers.
4. Burnish each fold flat before the next; a machine does this with its rollers.

## Parameters

| id | meaning | default | range |
|---|---|---|---|
| `style` | letter, z-fold, gatefold, french, roll, double-parallel, accordion, cross, map | `letter` | |
| `panels` | panels across for roll, accordion and map | 4 | 4–8 |
| `cross_panels` | map only: folded across in half (2) or in a Z of thirds (3) | 2 | 2–3 |
| `sheet_width` | flat sheet, across the parallel folds | 297 mm | 150–900 mm |
| `sheet_height` | flat sheet, along the parallel folds | 210 mm | 100–700 mm |
| `stock` | text paper (80, 120 g/m²) or card (160, 250, 300 g/m², scored) | `copy-80` | |
| `allowance` | fold-in step and gate-door shortfall; raised to (k + 1) × caliper where needed | 1.6 mm | 0.5–4 mm |
| `display_open` | how far the last fold opens at the end | 60° | 0–180° |

Presets: `a4` (297 × 210 mm), `us-letter` (279.4 × 215.9 mm), `us-legal` (355.6 × 215.9 mm),
`tabloid` (431.8 × 279.4 mm), `a3` (420 × 297 mm).

## History and sources

The fold names are the print trade's. Parallel folding folds the paper more than once with
parallel creases; a cross fold folds it, turns it 90° and folds it again, and the French or
right-angle fold is the most basic cross fold; a concertina, zig-zag or accordion fold is a
continuous parallel fold in alternating directions (Wikipedia, «Book folding»,
https://en.wikipedia.org/wiki/Book_folding). Folding machines make these folds with buckle
plates or with a knife; knife folding is used for thick paper and for cross folds, and right-angle
folds need the sheet turned 90° (Wikipedia, «Folding machine»,
https://en.wikipedia.org/wiki/Folding_machine). Printers' guides describe the roll fold's panels
folding inward again and again in the same direction, the double parallel as folded twice into
four panels a side, and the French fold as folded in half and then in half again perpendicularly
(Smartpress, «12 types of brochure folds for marketing & how to use them»,
https://smartpress.com/blog/on-press/12-types-of-brochure-folds-for-marketing-how-to-use-them;
4over4, «What is a right angle or French fold?»,
https://www.4over4.com/faqs/marketing-materials/what-is-a-right-angle-or-french-fold). A map fold
collapses the sheet into a strip with an accordion, then folds the strip in the perpendicular
direction (Qin Printing, «Map fold», https://www.qinprinting.com/map-fold/).

On allowances: roll-fold panels are fractionally different widths so they nest, and gate-fold
doors fold in to meet in the middle (University of Southampton, Valley Graphics, «Folding»,
https://www.southampton.ac.uk/valleygraphics/finishing/folding.page). For roll folds each panel
width changes by 1/16 in, and gate-fold doors are sized 1/8 in smaller (Vomela, «7 facts to know
about paper folding in commercial printing»,
https://blog.vomela.com/7-facts-to-know-about-paper-folding-commercial-printing); this cartridge
reads the 1/8 in as the total gap between the doors, each door stopping 1/16 in short of the
centre line. A US Letter tri-fold is laid out 3.6875, 3.6875 and 3.625 in, the sixteenth being
clearance (4over4, «Blank brochure templates and the panel widths that make a fold work»,
https://v2.4over4.com/guide/how-blank-brochure-templates-work), and an 11 × 17 in double parallel
runs about 4.28 in outer and 4.22 in inner panels, since the panel that tucks inside must be a
little narrower to fold flat (4over4, «Free tri-fold brochure templates with real panel
dimensions», https://v2.4over4.com/guide/free-tri-fold-brochure-templates-guide).

On scoring: heavy paper or heavy ink coverage should be scored, or the fold cracks (Vomela,
above); cover stock from about 100 lb cover upward needs a score, while text weights of 100 lb
and below fold cleanly without one (4over4, «Blank brochure templates», above). The cartridge's
threshold of 160 g/m² sits between those two weights; the score-vs-crease object shows the
difference.

The cross fold here (in half, then a letter fold across) is one member of the cross-fold class;
other cross folds (a 16-page signature, a closed gate, a letter fold folded in half) are not
carried, nor are the double gate, the half fold alone or folds with an uneven, off-centre panel.
The book-signature folds belong to the `codex-signatures` object.

## Provenance and licence

Original MADFAM layouts and fold programs, computed by `main.py`; the fold styles and sheet sizes
are generic print-trade formats and no printer's template is copied. Published under
CERN-OHL-W-2.0 like every object in the commons (see the commons root `LICENSE`).
