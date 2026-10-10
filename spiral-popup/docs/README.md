# Spiral pop-up

| | Title | Summary |
|---|---|---|
| en | Spiral pop-up | A spiral cut from a disc, glued across a card's gutter, springs out like a spring when the card opens and lies flat when it closes. |
| es | Pop-up de espiral | Una espiral cortada de un disco y pegada de un lado al otro del pliegue central salta como un resorte al abrir la tarjeta y queda plana al cerrarla. |
| fr | Pop-up spirale | Une spirale découpée dans un disque et collée de part et d'autre de la pliure jaillit comme un ressort quand la carte s'ouvre et se couche à plat quand elle se ferme. |
| pt | Pop-up de espiral | Uma espiral cortada de um disco e colada dos dois lados da dobra central salta como uma mola quando o cartão se abre e fica plana quando ele se fecha. |

## What it is

Cut a paper disc along a spiral and you have a spring. In a spiral pop-up the spiral lies flat
inside a closed card. Its outer end is glued to one page beside the gutter and its centre to the
opposite page. Open the card and the opposite page lifts the centre, pulling the coils out of the
gutter into a bouncing, helix-like spring; close it and the spiral lies flat again.

## Geometry

Two sheets. The **card** is one scored sheet (300 g/m²), a spread of two pages with the gutter
between them. The **spiral** is a disc of `diameter` with an Archimedean spiral strip:

- centreline r(θ) = r₀ + p·θ/2π, with `turns` turns between the centre disc (radius `centre`)
  and the rim, so the coil pitch is p = (R − `centre`) / `turns`;
- the strip is p − 1 mm wide: a 1 mm kerf is cut away between coils, so neighbouring coils never
  rub. The script refuses a strip narrower than 4 mm;
- the spiral is turned so that its outer end points at the gutter, `gutter_gap` away from it. Its
  centre is then R + `gutter_gap` from the gutter on the left page;
- `pliego.papercut.analyze` checks it: one piece, narrowest material bridge ≥ 3 mm, kerf ≥ 0.5 mm.

Two `glue` joins hold it: the last 40° of the strip (the end beside the gutter) on the left page,
and a disc at the centre on the right page, at the mirror image of the spiral's centre. The
`initial` frame is the shut card, with the right page opened by a fraction of a degree (δ, where
sin δ = 2 × the piece's 0.25 mm offset ÷ the centre's distance from the gutter) so that it meets
the top of the spiral at its centre. Both welds then hold within the stocks' collision thickness,
and the gutter starts from an unambiguous angle (about 179.5°).

## The fold program

The spiral's rise is bending and twisting of a long strip, not folding: it is a **compliant
(tier C)** object, and no rigid program can describe it. The program is `physical`. It opens the
card's gutter to 90° and then closes it again, and the physics engine is meant to bend the spiral
through its two glue joins. The control `Open and close` starts at the open card.

**Preview and engine.** The studio preview opens and closes the card, but **the spiral stays flat
on the left page**: the preview has no physics and the spiral has no folds to pose, so it cannot
follow the glue join at its centre. The rise of the spiral needs the physics engine, which is not
yet landed. The document is complete for it (stocks, glue welds, initial frame, physical program).

## Making one by hand

1. Export both sheets (`svg`, `dxf`, `pdf` or `hpgl`). Score the card's gutter and cut the spiral,
   following the two spiral lines on the cut layer.
2. Fold the card and open it flat. Glue the strip's outer end on the left page, beside the gutter,
   with the spiral lying flat.
3. Put glue on the centre disc and close the card on it, then press. Open the card: the spiral
   springs up.

Lighter paper (120 g/m² kraft, 80 g/m² copy) makes a softer spring that hangs lower; 160 g/m² card
holds its shape best.

## Parameters

| id | meaning | default | range |
|---|---|---|---|
| `page_width`, `page_height` | one page of the card | 150, 150 mm | 90–220, 90–260 mm |
| `diameter` | the spiral disc | 100 mm | 50–200 mm |
| `turns` | number of turns | 3 | 1.5–6 |
| `centre` | radius of the uncut centre disc | 12 mm | 8–30 mm |
| `gutter_gap` | distance from the spiral's outer end to the gutter | 6 mm | 3–20 mm |
| `stock` | the spiral's paper: `cardstock-160`, `kraft-120`, `copy-80` | `cardstock-160` | |

Presets: `tight-spring` (5 turns), `loose-coil` (2 turns), `a6-card`.

## History and sources

The spiral is a common pop-up card technique, described in the pop-up literature, for example
Duncan Birmingham, *Pop-Up Design and Paper Mechanics* (GMC Publications, 2010). The Archimedean
spiral is the curve whose radius grows in proportion to its angle (Wikipedia, «Archimedean
spiral», https://en.wikipedia.org/wiki/Archimedean_spiral). No published design is copied; the
geometry is computed by this cartridge.

## Provenance and licence

Original MADFAM geometry (the lineage records the general technique, credited to the tradition).
Published under CERN-OHL-W-2.0 like every object in the commons (see the commons root `LICENSE`).
