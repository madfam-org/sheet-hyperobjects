# Fastener joins

| | Title | Summary |
|---|---|---|
| en | Fastener joins | Two cards joined without glue: an arm turning on a brad, an eyelet or a rivet, or a cover held by staples or a running stitch and opening beside them. |
| es | Uniones con sujetadores | Dos tarjetas unidas sin pegamento: un brazo que gira sobre un broche, un ojillo o un remache, o una tapa sujeta con grapas o una puntada corrida que abre junto a ellas. |
| fr | Assemblages par attaches | Deux cartes assemblées sans colle : un bras qui tourne sur une attache parisienne, un œillet ou un rivet, ou une couverture tenue par des agrafes ou un point avant et qui s'ouvre à côté. |
| pt | Uniões com fixadores | Dois cartões unidos sem cola: um braço que gira num colchete, num ilhós ou num rebite, ou uma capa presa por grampos ou por um ponto corrido que abre ao lado deles. |

## What it is

Card can be joined with hardware or thread instead of glue, and the join decides how the parts
move. This cartridge shows five fasteners, one per mode, each joining two cards:

- **`brad`** (split pin, paper fastener): a domed head with two soft legs, pushed through a hole
  and spread behind. The joint turns, so it is the classic pivot of paper mechanisms.
- **`eyelet`**: a small metal tube whose end is rolled into a flange with a setting tool. It lines
  the hole and leaves a smooth pivot.
- **`rivet`**: a two-part fastener (a post and a cap) pressed or screwed together through the
  hole; it also turns.
- **`staple`**: two office staples whose legs pierce both cards and are clinched behind. The join
  is rigid; the cover opens beside it.
- **`stitch`**: a running stitch through pierced stations down the margin, as in a stitched
  binding. It is rigid too, and the cover opens beside it.

## Geometry

- **Pivoting modes.** The base card is `card_width` × `card_height`. The arm is a strip
  `arm_length` × `arm_width` with round ends, its pivot at the centre of one end, placed on the
  base with the pivot 4 mm plus half the arm's width from the base's left edge, at mid-height. The
  arm has a hole of the fastener's size (`brad_hole`, `eyelet_hole` or `rivet_hole`); the base's
  hole is a closed cut, whose slug stays in the document and drops out when the card is cut (the
  mechanism's centre must lie on the base's material). The arm must cover the fastener's head or
  flange, taken as 2.6 × the hole for a brad, 2.0 × for an eyelet and 2.4 × for a rivet, with 1 mm
  to spare on each side; the script refuses a narrower arm. Both cards pass
  `pliego.papercut.analyze` with a 2 mm minimum feature.
- **Fixed modes.** A cover the size of the base lies on it. The fastening runs down the middle of
  a `margin` along the left edge: two staples with a 12 mm crown at a quarter and three quarters of
  the height (their crowns drawn as kiss cuts on both cards), or `stations` sewing stations from
  8 mm off each end (kiss-cut crosses where the awl pierces). A valley score at the margin's inner
  edge is the cover's hinge. Every staple leg and every station is a `pivot` join between the cover
  and the base; two or more of them hold the margin rigidly.

The upper card sits 0.36 mm above the base, the base stock's caliper.

## The mechanism and the fold program

- **Pivoting modes.** The arm is a kinematic sheet moved by a `rotate` mechanism about the hole's
  centre, the `swing` control (0–360°). As in the volvelle, the fastener is the mechanism's centre,
  not a `pivot` join: a join between the turning arm and the fixed base would hand the control to
  the physics engine, and the rotation is exactly what the hardware allows.
- **Fixed modes.** The program opens the cover on its score (`open_angle`) and closes it again.
  The fastened margin is the cover's root face, so it stays on the base while the rest turns.

**Preview and engine.** Every mode plays in the studio preview: the arm turns, the cover opens and
closes. The physics engine adds what the preview leaves out: friction at the pivot, the cover
bending at its score rather than turning on an ideal line, and the pull of each staple or stitch
(the joins) on the cards.

**Hardware.** Brads, eyelets, rivets and staples are not paper and are not drawn as sheets. They
will link to the keystone's standard parts and to Yantra4D through `hardware_ref` later, as
cross-commons references the programme's coordinator adds.

## Making one by hand

1. Export the cards (`svg`, `dxf`, `pdf` or `hpgl`) and cut them out.
2. **Brad, eyelet, rivet:** punch the holes with a hole punch of the fastener's size. Push a brad
   through arm and base and spread its legs flat behind; set an eyelet with its setting tool from
   the arm's side; press or screw the rivet's cap onto its post. Leave the join loose enough to
   turn.
3. **Staples:** line up the cards and staple through the two crown marks, close to the margin's
   middle.
4. **Stitch:** pierce the stations through both cards with an awl, then sew in and out with a
   running stitch and tie off at the back.
5. Fold the cover along its score so it opens cleanly.

## Parameters

| id | meaning | default | range |
|---|---|---|---|
| `card_width`, `card_height` | base (and cover) size | 120 × 80 mm | 60–250 × 50–250 mm |
| `arm_length`, `arm_width` | the turning arm (pivoting modes) | 95 × 18 mm | 40–220 × 10–40 mm |
| `brad_hole` | hole for a brad | 3 mm | 2–5 mm |
| `eyelet_hole` | hole for an eyelet's shank | 3.2 mm | 2.5–6 mm |
| `rivet_hole` | hole for a rivet's post | 4 mm | 3–6 mm |
| `margin` | the fastened margin (fixed modes) | 14 mm | 8–30 mm |
| `stations` | sewing stations (mode `stitch`; fewer if they would come closer than 6 mm) | 5 | 3–11 |
| `open_angle` | how far the program opens the cover | 150° | 30–178° |

Presets: `pocket`, `wide-arm`, `seven-stations`.

## History and sources

- The brass fastener (split pin, paper fastener, brad) goes through punched holes with its legs
  spread to hold the sheets; it was patented in 1866, and it is used where rotation around the
  joint is wanted, as in moving paper and card models (Wikipedia, «Brass fastener»,
  https://en.wikipedia.org/wiki/Brass_fastener).
- A small grommet is also called an eyelet, set with a punch or a press (Wikipedia, «Grommet»,
  https://en.wikipedia.org/wiki/Grommet).
- An office staple's crown joins two legs that are clinched against an anvil to bind a stack of
  pages (Wikipedia, «Staple (fastener)», https://en.wikipedia.org/wiki/Staple_(fastener)).
- Stitched bindings sew thread through holes punched along the spine edge, a long East Asian
  tradition (Wikipedia, «Traditional Chinese bookbinding»,
  https://en.wikipedia.org/wiki/Traditional_Chinese_bookbinding).

The head factors and the default hole sizes are this cartridge's working assumptions for common
craft hardware; measure the hardware in hand.

## Provenance and licence

Original MADFAM geometry: the cards, holes, marks and joins are generated by `main.py`. The
fasteners are common stationery and bookbinding practice, credited to no designer. Published
under CERN-OHL-W-2.0 like every object in the commons (see the commons root `LICENSE`).
