# Score vs crease

| | Title | Summary |
|---|---|---|
| en | Score vs crease | Two identical 300 g/m² cards folded side by side, one scored first and one not: why every fold in card is scored. |
| es | Hendida o sin hender | Dos cartulinas idénticas de 300 g/m² dobladas lado a lado, una hendida antes y otra no: por qué todo doblez en cartulina se hiende. |
| fr | Rainé ou non rainé | Deux cartes identiques de 300 g/m² pliées côte à côte, l'une rainée au préalable, l'autre non : pourquoi on raine tout pli dans du bristol. |
| pt | Vincado ou não vincado | Dois cartões idênticos de 300 g/m² dobrados lado a lado, um vincado antes e o outro não: por que toda dobra em cartão é vincada. |

Fold a sheet of 300 g/m² card in half without preparing it and the fold wanders, springs back,
and the outer surface often cracks along the ridge. Run a scoring tool along the line first, and
the same card folds exactly there, crisply and without cracking. Print finishers score every fold in
heavy stock; the commons' card for 300 g/m² cardstock records it as *required: score every fold*.
This object puts the two cases side by side so the difference can be seen and measured.

## Geometry

Two sheets, **`scored`** and **`unscored`**, each a rectangle `width × height` (210 × 148 mm by
default: an A5 sheet that folds to an A6 card). Each has one valley line down its middle, at
`u = width / 2`. The kernel lays them out side by side in the layout frame. Both are long grain
(`grain_deg = 90`), so the fold runs parallel to the grain, which is the right way to cut a card.

The only difference between the two sheets is the **treatment** of the fold line
(`pliego:edges_treatment`, sheet-document spec v1 §4):

| Sheet | Line | Treatment | Assignment | Fold angle |
|---|---|---|---|---|
| `scored` | scored fold line | `score` | `V` | `+angle` |
| `unscored` | fold line, not scored | `crease` | `V` | `+angle` |

## What the engine is asked to simulate

The fold program has one `physical` step, *Fold both cards in half*, which drives both hinges to
`angle` (180° by default) at the same time with the hand factor. Per the sheet-document spec (§4),
a `crease` hinge has the stock's crease stiffness per unit length (`crease_k`), and a `score`
hinge has that stiffness multiplied by the stock's `score_factor`, with a lower yield. For
`cardstock-300` the snapshot in the document carries:

| `derived` key | Value | Meaning |
|---|---|---|
| `thickness` | 0.36 mm | caliper (measured or estimated on the stock card) |
| `crease_k` | 1.77 × 10⁵ g·mm/s² per rad per mm | hand-crease hinge, `√(D_md·D_cd) / L*` with `L* = 200·t` |
| `score_factor` | 0.35 | a scored hinge is about a third as stiff (a documented default) |
| `crease_yield_deg` | 35° | elastic range before the crease takes a set (estimate) |

So under the same drive, the scored card should follow the hand more readily and take a set
sooner. The unscored card's stiffer hinge pushes back on the hand and on the panels, which are
heavy, stiff plates (`D_md`, `D_cd`).

Honest limit: the engine contract has no fracture of plain paper yet (spec §5.2 reserves
`tear_strain` for perforations "and, later, plain paper"). The cracked outer surface of an
unscored fold is therefore explained here, not simulated.

## Why heavy card cracks, and why a score helps

Bending a sheet of thickness `t` to an inner radius `R` stretches its outer surface by roughly
`t / (2R + t)`. The stock card gives 300 g/m² card a tear strain of 1.5 % (an estimate). Keeping the
outer surface under that would need an inner radius of about 33 times the thickness, some 12 mm
for this card, which is nothing like a sharp fold. A flat fold of unprepared card therefore
overstretches the outer fibres, and they break.

A score is made before folding by pressing a rule or a scoring blade into the card (or by a
reduced-power laser or blade pass, as the exporters' `score` layer is meant for). It compresses
and weakens a narrow band, giving the fold a prepared hinge line. The board bends in that band, and
the outer surface stretches less than an unprepared sheet forced through the same angle.

## Making one

1. Export the two cards (`svg`, `dxf`, `pdf` or `hpgl`). On the `scored` card the line is on the
   score layer; on the `unscored` card it is drawn as an ordinary fold line, for reference only.
2. Score the `scored` card's line: a bone folder or an empty ballpoint pen along a ruler, a
   scoring board, or the score pass of a cutting plotter.
3. Fold both cards in half along their lines.
4. Compare the ridges, how far each card springs back, and the outer surface of the unscored one.

Fold parallel to the grain when you can. Folding across the grain of heavy card cracks it more
readily, scored or not.

## Parameters

| Parameter | Meaning | Default |
|---|---|---|
| `stock` | `cardstock-300`, `cardstock-250`, `cardstock-160`, `kraft-120` | `cardstock-300` |
| `width` | card width, unfolded (mm) | 210 |
| `height` | card height (mm) | 148 |
| `angle` | target fold angle (°); 180 is folded flat | 180 |

Presets: `card-250` (250 g/m² card), `right-angle` (90°, a standing card).

## History and sources

Scoring before folding is long-standing print-finishing and bookbinding practice, attributed to no
one. The figures above are from the commons' stock card (`materials/cardstock-300/stock.json`)
and the sheet-document spec v1 §4 and §5.2. The crease length scale `L* ≈ 200·t` that sets
`crease_k` is the kernel's documented estimate after Lechenault, Thiria and Adda-Bedia,
*Mechanical response of a creased sheet*, Physical Review Letters 112, 244301 (2014),
https://arxiv.org/abs/1404.1243 (measured on Mylar; unmeasured for paper). No design is copied;
the geometry is generated by this cartridge.

## Provenance and licence

Traditional practice (public domain); original geometry. Published under CERN-OHL-W-2.0 like every
object in the commons (see the commons root `LICENSE`).
