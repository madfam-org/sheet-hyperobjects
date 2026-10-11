# Party hat

| | Title | Summary |
|---|---|---|
| en | Party hat | A cone hat rolled from a flat sector of card and closed with a glue tab; the sector angle follows from the hat's height and base diameter. |
| es | Gorro de fiesta | Un gorro cónico enrollado a partir de un sector plano de cartulina y cerrado con una pestaña de pegado; el ángulo del sector se deduce de la altura y del diámetro de la base. |
| fr | Chapeau de fête | Un chapeau conique roulé dans un secteur plat de bristol et fermé par une languette de collage ; l'angle du secteur découle de la hauteur et du diamètre de la base. |
| pt | Chapéu de festa | Um chapéu cônico enrolado a partir de um setor plano de cartão e fechado com uma aba de colagem; o ângulo do setor decorre da altura e do diâmetro da base. |

## What it is

The cone party hat: a sector of card, rolled until its two straight edges meet, glued along a tab
and worn with an elastic under the chin. You choose how tall the hat is and how wide its base is;
everything else is geometry. This cartridge shows the making (curl, close, tuck the tab) and the
finished hat, which can be pressed flat for storage and opened again.

## Geometry

The lateral surface of a cone unrolls into a circular sector:

- the sector's radius is the cone's slant height L = √(h² + r²), with h the height and r the base
  radius;
- its angle is θ = 360° · r / L, because the arc of the sector becomes the base circle (2πr).

The default hat (h = 180 mm, d = 150 mm) has L = 195 mm and θ ≈ 138.5°.

**Segmentation.** Pliego's sheets bend along edges, so the curved cone is modelled as a pyramid of
`panels` narrow triangles (48 by default). Rulings run from the apex to the rim; they are `F`
(flat) lines with treatment `none`: plain paper, never scored or cut, and the physics engine treats
them as panel hinges inside the paper. The rim between two rulings is a chord, so the closed form is
an exact isometry of the sheet: a right pyramid on a regular N-gon of circumradius
R′ = L·sin(Δ/2) / sin(π/N), with Δ = θ/N. For the default hat R′ = 75.05 mm (the true cone has
75 mm). The script fails loud if the pose is not a valley roll or if the glue does not land.

**The glue tab** continues the sector over enough extra panels to be 12 mm wide at the rim (two
panels by default). It stops at 0.3 L from the apex and is chamfered at the rim. Its rulings carry
on from the sector's, so in the closed hat the tab lies exactly on the first panels, inside the
cone. A `glue` join welds it there: the map is a rotation by −θ about the apex.

The outline is checked with `pliego.papercut.analyze` against the stock's minimum feature.

The colour is printed on the back of the sheet (the outside of the hat); the rolls are valley folds,
so the front ends up inside.

## The fold program

**Mode `make`** is a `kinematic` program on the rulings, the one the studio preview plays:

1. curl the sector into a loose cone (every ruling at half its final angle);
2. bring the straight edges together: the cone closes;
3. tuck the glue tab inside and glue it;
4. hold the tab until the glue sets.

The tab's glue is a `glue` join with `active_from: "press"` (sheet-document spec §5.19): the
sector starts flat and the program ends glued. It ends in the cone, which is also written as the
frame `target:cone`. The hat lies on its side because the preview keeps the first panel on the
table.

**Mode `worn`** is the finished hat for the physics engine: the glue weld, an elastic as a `string`
join between two points 8 mm above the rim on opposite sides, and an `initial` frame standing upright
on the table. Its `physical` program presses the hat flat for storage (two layers, with folds at the
seam and at the opposite ruling) and opens it again. The glue weld holds in both states: the
flattened state is written as `target:flat`.

**Why two modes.** One physical program that rolls the flat sector, glues it, then presses it
flat and opens it would need the engine to close the cone by driving its rulings one by one. It
cannot yet: the same construction on the paper crown's band leaves the ends 37 mm apart, so the
glue finds nothing to weld when it switches on. A kinematic program closes the cone exactly but
holds the sheet rigid, so it cannot show the weld holding while the hat is pressed flat. `make`
shows the making; `worn` shows the glued hat's physics.

**Preview and engine.** The preview plays both programs exactly at their ends. In between, the flat
press is a straight blend of angles, so the tab drifts off the glue for a moment; the engine keeps
the weld and bends the paper instead. A string cannot stretch, so the elastic's length is its
stretched limit (an approximation of an elastic). Putting the hat on a head is not modelled.

## Making one by hand

1. Export the sector (`svg`, `dxf`, `pdf` or `hpgl`) and cut it out. The default sheet is about
   368 × 195 mm and fits A3; the rulings are not on the cut file.
2. Curl it, coloured side out, until the straight edges meet.
3. Glue the tab and slide it under the other edge, inside the cone. Hold it until the glue grips.
4. Staple an elastic 8 mm above the rim, on opposite sides.

Card of 160 g/m² holds a cone well. 250 g/m² is stiffer but harder to curl; copy paper makes a
floppy hat.

## Parameters

| id | meaning | default | range |
|---|---|---|---|
| `height` | the hat's height | 180 mm | 80–400 mm |
| `diameter` | its base diameter | 150 mm | 80–260 mm |
| `panels` | rulings that approximate the cone (model resolution, not cut) | 48 | 24–96, even |
| `elastic` | elastic length, worn mode (0 = none) | 300 mm | 0–600 mm |
| `stock` | `cardstock-160`, `cardstock-250`, `kraft-120`, `foil-paper`, `copy-80` | `cardstock-160` | |
| `colour` | colour of the outside | red | five colours |

Presets: `child` (150 × 120 mm), `tall-cone` (320 × 170 mm), `foil` (foil paper, no elastic).
The script refuses a sector wider than 330° with its tab (a hat flatter than about 0.35 of its
diameter).

## History and sources

Wikipedia describes the party hat as a cone of thin paperboard, usually printed on the outside and
held by an elastic chinstrap, worn most often at birthday parties and on New Year's Eve; it traces
the hat to the dunce cap of the mid-19th to early 20th century (Wikipedia, «Party hat»,
https://en.wikipedia.org/wiki/Party_hat). The development of a cone into a sector is classical
geometry (Wikipedia, «Cone», https://en.wikipedia.org/wiki/Cone). No published template is copied;
the sector is computed by this cartridge.

## Provenance and licence

Original MADFAM geometry; the lineage credits the cone party hat as a common celebration object
rather than any designer. Published under CERN-OHL-W-2.0 like every object in the commons (see the
commons root `LICENSE`).
