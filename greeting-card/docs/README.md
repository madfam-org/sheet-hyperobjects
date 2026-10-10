# Greeting card

| | Title | Summary |
|---|---|---|
| en | Greeting card | Every common folded card in one object: single fold, tent, gatefold, z-fold, tri-fold and a card with an insert, in A6, A5, US A2 and US A7, scored for cardstock. |
| es | Tarjeta de felicitación | Todas las tarjetas plegadas comunes en un solo objeto: un doblez, tienda, díptico de puertas, zigzag, tríptico y tarjeta con hoja interior, en A6, A5, A2 y A7 de EE. UU., hendidas para cartulina. |
| fr | Carte de vœux | Toutes les cartes pliées courantes en un seul objet : pli simple, chevalet, volets, pli en Z, trois volets et carte avec feuillet, en A6, A5, A2 et A7 américains, rainées pour le bristol. |
| pt | Cartão de felicitações | Todos os cartões dobrados comuns num só objeto: dobra simples, tenda, portas, sanfona em Z, três dobras e cartão com folha interna, em A6, A5, A2 e A7 americanos, vincados para cartão. |

## What it is

The folded card is the most common paper object people make on purpose. This cartridge is the
whole family in one object. The fold style is a parameter, the paper insert is a mode, and the
standard sizes are presets. The size is always the **finished, folded face**: choose A6 and the
card closes to 105 × 148 mm whatever its style, and the script works out the flat sheet.

| style | flat sheet (face w × h) | folds |
|---|---|---|
| `single` | 2w × h | one, on the long side: the card opens like a book |
| `tent` | L × 2S (L, S the long and short side) | one, along the top: the card stands as a tent |
| `gatefold` | (2w − 2) × h | two doors, each 1 mm short of half the face, folding in to meet at the centre |
| `z-fold` | 3w × h | valley then mountain: an accordion that shows a Z from the side |
| `tri-fold` | (3w − 2) × h | two valleys, rolled in: the end panel is 2 mm narrower so it tucks inside |
| mode `with-insert` | 2w × h, plus an insert | a single-fold cover with a copy-paper insert glued beside its spine |

## Geometry

The card is one sheet in sheet-local millimetres, with every fold a **scored** line
(`pliego:edges_treatment = score`). Card of 250 g/m² and heavier cracks along the ridge if it is
folded without a score, as the `score-vs-crease` object shows. The grain runs parallel to the
folds (long grain for side folds, `grain_deg = 0` for the tent's horizontal fold), which is the
right way to cut a card.

The allowances are the ones print finishers use so that panels never collide: gatefold doors stop
1 mm short of the centre, and the tri-fold panel that folds inside is 2 mm narrower than the
others. The insert is the opened card less `insert_margin` on every side, on 80 g/m² paper, with its
fold over the card's spine. A 5 mm glue line just left of the spine (a `glue` join from the insert to
the card) holds it; a glue line beside the fold does not stop either sheet from folding.

The sheet's front side is the inside of the card and its back side the outside, so
`inside_color` and `outside_color` colour the two faces of the sheet document (eight stationery
colours).

## The fold program

All the folds of a card are parallel lines across the sheet, so the card has no vertex where folds
meet and its rigid motion is exact. The program is `kinematic`, built with
`pliego.Sequence.kinematic_path`, six substeps per key step:

- `single`, `tent`: fold the card shut, then open it to `display_open`;
- `gatefold`: fold the left door in, the right door in, then open both;
- `z-fold`: fold both scores together into the Z, then open the accordion;
- `tri-fold`: fold the narrow end panel in, fold the cover panel over it, then open both;
- `with-insert`: the cover and the insert fold together, the insert a little further than the
  cover at every substep so it stays inside.

The control `Fold and open` scrubs the program and starts at its end, the card standing open at
`display_open` (100° between panels by default).

**Preview and engine.** The studio preview animates every style. Shut folds are drawn at 178°
(and inner ones at 179.5°) rather than 180°, because zero-thickness panels cannot nest at exactly
180°; real card has thickness, and the engine resolves the contact. The insert's glue line is a
join that the preview does not need: the insert has its own fold in the same program. The physics
engine adds the spring-back of scored card and the weight of the panels.

## Making one by hand

1. Export the flat sheet (`svg`, `dxf`, `pdf` or `hpgl`). The outline is on the cut layer and every
   fold on the score layer. With the insert mode, the insert is a second sheet.
2. Score each fold with a bone folder or an empty ballpoint along a ruler (or the score pass of a
   cutting plotter) before folding anything.
3. Fold along the scores in the order of the program, and press each fold with the bone folder.
4. For the insert, fold it, run a 5 mm line of glue or double-sided tape just left of its fold on
   the back, and set it into the card with the two folds together.

## Parameters

| id | meaning | default | range |
|---|---|---|---|
| `style` | `single`, `tent`, `gatefold`, `z-fold`, `tri-fold` (mode `card`) | `single` | |
| `face_width`, `face_height` | the folded card | 105 × 148 mm (A6) | 70–220, 70–300 mm |
| `stock` | `cardstock-250`, `cardstock-300`, `cardstock-160`, `kraft-120` | `cardstock-250` | |
| `outside_color`, `inside_color` | the sheet's back and front | white | eight colours |
| `insert_margin` | insert inset per side (mode `with-insert`) | 4 mm | 2–10 mm |
| `display_open` | angle between panels at the end of the program | 100° | 30–180° |

Presets: `a6` (105 × 148 mm), `a5` (148 × 210 mm), `us-a2` (4¼ × 5½ in = 107.95 × 139.7 mm),
`us-a7` (5 × 7 in = 127 × 177.8 mm).

## History and sources

Printed greeting cards have a long history; their mass production dates from the nineteenth
century (Wikipedia, «Greeting card», https://en.wikipedia.org/wiki/Greeting_card). A6 and A5 are
ISO 216 paper sizes (Wikipedia, «ISO 216», https://en.wikipedia.org/wiki/ISO_216). A2 and A7 are
North American announcement-envelope sizes (4⅜ × 5¾ in and 5¼ × 7¼ in; Wikipedia, «Envelope»,
https://en.wikipedia.org/wiki/Envelope), and the cards made to fit them are conventionally 4¼ × 5½
in and 5 × 7 in. The fold styles and panel allowances are generic print-finishing practice. No
design is copied; every layout is computed by this cartridge.

## Provenance and licence

Original MADFAM layouts of generic stationery formats. Published under CERN-OHL-W-2.0 like every
object in the commons (see the commons root `LICENSE`).
