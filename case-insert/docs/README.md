# Case insert · Inserto para estuche · Insert de boîtier · Inserto para estojo

| Language | Summary |
|---|---|
| en | Blank case wraps, two-spine tray inlays and front panels generated from paper-channel dimensions, with bleed and an optional flap. |
| es | Fundas de papel sin arte, insertos de bandeja con dos lomos y paneles frontales generados a partir del canal del estuche, con sangrado y solapa opcional. |
| fr | Jaquettes vierges, inserts de plateau à deux dos et panneaux avant générés à partir du logement papier du boîtier, avec fond perdu et rabat facultatif. |
| pt | Capas sem arte, insertos de bandeja com duas lombadas e painéis frontais gerados a partir do canal de papel do estojo, com sangria e aba opcional. |

## Geometry

`panel_w` and `panel_h` describe the paper channel inside the selected case,
not the case's outside envelope. `spine_w` is the channel across its spine.
The `wrap` blank is two panels plus one spine: `2·panel_w + spine_w` wide.
The `tray-inlay` blank is one panel plus two spine strips:
`panel_w + 2·spine_w`. The `front` blank is one panel. A nonzero `flap` adds
one strip beyond the outer edge, scored or creased according to the stock.
`bleed` expands only the print-production region; it does not enlarge the
cut trim. No artwork or a game's printed cover is included.

The native sequence folds the spine lines to `fold_angle`. A plain front panel
has no moving folds. FOLD preserves the native sequence; animated GLB uses
`pliego.export.to_glb(document, animate=True)`. The cartridge CLI's ordinary
GLB export is a static initial pose. Geometry is original MADFAM work computed
here, with no copied commercial cutting drawing.

## Presets and exact editions

Every default and preset is an explicitly labelled archetype. The tall wrap,
square inlay, front panel and optional-flap examples demonstrate the family;
they do not assert retail-case, booklet or title-edition measurements.

An exact edition needs evidence for the selected case's paper-channel width,
height and spine width, plus any flap. An outside case size alone cannot
supply those values. Do not infer a physical trim from PDF MediaBox, a cropped
scan, a photograph or another regional edition. Edition and case measurements
belong in `hyperobjects_reference`; refresh these values after that evidence
lands. Consumer products bind a SKU to its experience, without copying this
geometry or its physical facts.

## Assembly and limits

Cut the trim outline, crease the spine lines and slide the blank into the
case's paper channel. Leave the printing bleed outside the trim during print
production. Stock thickness, the clear sleeve's friction and the paper channel's
true clearance require a physical fit check. The native fold program checks
paper geometry and sequence; it does not verify a particular commercial case.
