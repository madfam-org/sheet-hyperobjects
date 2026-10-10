# Carousel book

| | Title | Summary |
|---|---|---|
| en | Carousel book | A book that opens 360° into a star of chambers, made from one scored strip of card, with tie ribbons and optional windows through its walls. |
| es | Libro carrusel | Un libro que se abre 360° en una estrella de cámaras, hecho de una sola tira de cartulina hendida, con listones para atarlo y ventanas opcionales en sus paredes. |
| fr | Livre carrousel | Un livre qui s'ouvre à 360° en une étoile de chambres, fait d'une seule bande de bristol rainée, avec des rubans pour le nouer et des fenêtres facultatives dans ses parois. |
| pt | Livro carrossel | Um livro que se abre 360° numa estrela de câmaras, feito de uma única tira de cartão vincada, com fitas para amarrar e janelas opcionais nas paredes. |

## What it is

A carousel book looks like an ordinary closed book, but it opens all the way round until its back
cover meets its front cover; stood upright and tied with its ribbons, it becomes a ring of
chambers that can be seen from every side. This cartridge builds the structure from one strip of
card: the covers and the walls are panels of the strip, every wall hinges on the same spine, and
the chambers are the wedges of space between neighbouring walls.

`chambers` sets how many chambers the open book shows (3–8), `page_width` is the distance from the
spine to the fore-edge (the radius of the open carousel), and `windows` cuts the same arched or
round window through every inner wall so that each chamber looks into the next.

## Geometry

The strip is 2·N panels of `page_width` × `page_height` (N = `chambers`), all computed by
`main.py`:

| panel | role |
|---|---|
| 1 | front cover |
| 2k, 2k + 1 (k = 1 … N − 1) | the two layers of wall k: a page folded at its fore-edge, back to back |
| 2N | back cover |

Scored folds separate the panels and alternate:

- **spine folds** (`spine`, valley): between a cover or a wall and the next wall. Every one of them
  lies on the spine axis in the open book;
- **fore-edge folds** (`fore-edge`, mountain, shut at 180°): the outer edge of each double wall.

Open, the walls stand α = (360° − 2°)/N apart round the spine, and the two covers meet 2° apart
(the thickness of the card), where two ribbons tie them, 15 mm from the top and the bottom. The
ribbons are `string` joins between points 6 mm in from the two covers' fore-edges, as long as the
gap between those points in the open book plus 0.5 mm. The valley sense of the spine folds puts the
front of the card inside every chamber; the back of the card lines the inside of each double wall.

Windows are cut through both layers of a wall at the same place, mirrored about the fore-edge
fold, so they line up when the wall is folded; covers have none. The cut strip is checked with
`pliego.papercut.analyze` (one piece, every bridge at least 2 mm on 250 g/m² card, 1.5 mm on the
lighter stocks).

`main.py` checks the open state and fails loud if it is wrong: it must be a rigid state
(`pliego.kinematics.closure_residual`), wall k must stand k·α from the front cover, and the back
cover must arrive at 360° − 2°.

## The fold program

Every spine fold turns about the same axis, so any set of spine-fold angles is a rigid state and
a program linear in the angles is exact (the fore-edge folds stay shut). The initial frame is the
displayed state, the book open and tied; the kinematic program then

1. **closes the book** — every spine fold to 178°, so the walls stack 2° apart, and
2. **opens it all the way round** again, to α.

The sequence control `Close and open` starts at the end of the program, the book open.

**Preview and engine.** The studio preview runs the whole program, the book standing upright. The
ribbons are joins that only the physics engine resolves. A string join cannot be untied in spec
v1: in an engine run the ribbons hold the covers together throughout, so the engine shows the tied,
displayed book and the close-and-open motion stays a preview of what hands do with the ribbons
untied (an open question for the spec). The engine adds the card's stiffness and its weight
standing on the table.

## Making one by hand

1. Export the strip (`svg`, `dxf`, `pdf` or `hpgl`). The outline and the windows are on the cut
   layer, every fold on the score layer. A long strip can be made from several sheets joined on a
   spine fold with a strip of tape.
2. Score every fold with a bone folder along a ruler, then cut the windows.
3. Fold every fore-edge fold shut (mountain) and glue the two layers of each wall together, keeping
   the windows aligned and the spine end free.
4. Fold the spine folds as valleys and stack the walls into a closed book.
5. Punch the ribbon points on both covers, thread a ribbon through each and knot it inside.
6. Open the book until the covers meet and tie the ribbons in bows.

## Parameters

| id | meaning | default | range |
|---|---|---|---|
| `chambers` | chambers in the open book | 5 | 3–8 |
| `page_width` | spine to fore-edge (radius) | 100 mm | 60–200 mm |
| `page_height` | height of the book | 140 mm | 80–300 mm |
| `stock` | `cardstock-250`, `cardstock-160`, `kraft-120` | `cardstock-250` | |
| `windows` | `arch`, `circle` or `none` | `arch` | |

Presets: `pocket` (70 × 100 mm), `a6` (105 × 148 mm), `a5` (148 × 210 mm) pages.

## History and sources

Carousel books, also called 360° books, are bound like ordinary picture books, but their front and
back covers are designed to touch so that the book opens into a full circle, usually held with
ribbons or magnets (Let's Talk Picture Books, «Favorite Carousel Books», 2022,
https://www.letstalkpicturebooks.com/2022/02/favorite-carousel-books.html). The Smithsonian
Libraries describe a carousel that looks like an ordinary flat book but unfolds into a 360-degree
circle when stood upright, opens until back and front covers touch and is held as a circle by tying
its ribbons; they cite examples from 2004 and 2017 in the Cooper Hewitt collection (Smithsonian
Libraries and Archives, «A Carousel Holiday Decoration»,
https://library.si.edu/finding-aid/carousel-holiday-decoration). The structure belongs to the
general practice of book arts and paper engineering; no published carousel is reproduced, and the
strip, the windows and the angles are computed by this cartridge.

## Provenance and licence

Original MADFAM geometry for a general book structure. Published under CERN-OHL-W-2.0 like every
object in the commons (see the commons root `LICENSE`).
