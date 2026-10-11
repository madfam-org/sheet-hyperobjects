# Carousel village

| | Title | Summary |
|---|---|---|
| en | Carousel village | A carousel book whose chambers are a village street: each house is a box fold cut from the walls across the spine, with a roof, belfry or parapet and doors that open. |
| es | Aldea carrusel | Un libro carrusel cuyas cámaras son la calle de una aldea: cada casa es un pliegue de caja cortado de las paredes a través del lomo, con techo, espadaña o pretil y puertas que se abren. |
| fr | Village carrousel | Un livre carrousel dont les chambres forment la rue d'un village : chaque maison est un pli en boîte découpé dans les parois en travers du dos, avec toit, clocher-mur ou parapet et des portes qui s'ouvrent. |
| pt | Aldeia carrossel | Um livro carrossel cujas câmaras são a rua de uma aldeia: cada casa é uma dobra em caixa cortada das paredes através da lombada, com telhado, espadana ou platibanda e portas que se abrem. |

## What it is

A carousel book opens all the way round until its covers meet; stood upright and tied, it is a
ring of chambers seen from every side. In this diorama every chamber holds a house, and the houses
are not glued in: each one is cut from the two walls that meet at the chamber's spine fold, so it
stands up when the book opens and folds flat inside it when the book closes. Six chambers make a
short street that rises from a granary to a tower (`village` = `mixed`); a street of gabled
cottages or of flat-roofed houses is one option away.

It is a composition of two mechanisms of the commons: the one-strip carousel
([`carousel-book`](../../carousel-book/docs/README.md)) and the parallel (box) fold made from the
page itself, the single-sheet form of the
[`parallel-fold-popup`](../../parallel-fold-popup/docs/README.md) and the step of
[`step-popup`](../../step-popup/docs/README.md). Both come from kernel builders
(`pliego.book.carousel_strip`, `pliego.popup.cut_fold`), so no cartridge's script is copied.

## Geometry

**The strip.** 2·N + 2 panels of `page_width` × `page_height` (N = `chambers`): a lining, the
front cover, N − 1 double walls, the back cover and a lining. Spine folds (valley) join the walls
on one axis; fore-edge folds (mountain, shut at 180°) make each double wall; each lining folds
flat behind its cover and is glued to it, so the openings that the first and last houses leave in
the covers stay hidden. Open, neighbouring walls stand α = (360° − 2°)/N apart and two ribbons
(`string` joins) tie the covers' fore-edges, as in `carousel-book`.

**The houses.** Across spine fold k, `cut_fold` cuts one block: two horizontal slits from fold A
on the left wall (a from the spine) to fold B on the right wall (b from the spine), and three
vertical folds A, F and B between them. When the chamber opens, the strip between the slits
stands as a parallelogram: the facade (A–F, b wide) parallel to the right wall, the side wall
(F–B, a long) parallel to the left wall, the corner F toward the viewer. The roof is a crest: the
facade continues past the upper slit with the house's silhouette, a gable with a chimney, a bell
gable, a stepped parapet or a pyramid roof, and leaves its shape as a window in the left wall.

| style | a | b | wall | crest | openings |
|---|---|---|---|---|---|
| granary | 0.48 W | 0.32 W | 0.24 H | low gable | double doors, gable vent, side window |
| flat-roofed house | 0.44 W | 0.30 W | 0.26 H | stepped parapet | door, two windows |
| cottage | 0.44 W | 0.27 W | 0.30 H | gable and chimney | door, round gable window, two side windows |
| chapel | 0.38 W | 0.24 W | 0.36 H | bell gable with an arched opening | arched door, round window, two arched side windows |
| two-storey house | 0.36 W | 0.30 W | 0.42 H | cornice step | door, two upper windows, four side windows |
| tower | 0.28 W | 0.14 W | 0.52 H | pyramid roof | arched door, round clock opening, slits |

(W = `page_width`, H = `page_height`.) Every house stands 3 mm above the table, so each fold keeps
3 mm uncut at its ends. Windows are holes in the moving panels; doors are flaps cut on three sides
and scored on the fourth (hinged on the side toward the house's corner, double doors on their
outer sides).

`main.py` fails loud unless:

- every state of the program closes (`pliego.kinematics.closure_residual` below 1e-6 mm);
- the cut strip passes `pliego.papercut.analyze`: one piece, every bridge at least 2 mm on
  250 g/m² card and 1.5 mm on 160 g/m²;
- no roof window overlaps the opening that the previous house leaves behind it in the same
  double wall. A taller, wider neighbour would show through. This is why the mixed street rises;
- every open door stays inside its chamber.

## The fold program

The cut-fold builder makes every fold of a house turn by the same angle as the spine fold it is cut
across (A and B with it, F against it). Every spine fold turns about the book's axis, and the doors
are free hinges. So every state of the program is rigid, and a linear blend of the angles is exact.

The initial frame is the open book, ribbons tied, doors open. The kinematic program then runs four
steps:

1. **Close the doors.**
2. **Close the book.** Every spine fold and every house fold goes to 178°, and the houses fold flat
   between the walls.
3. **Open it all the way round** again, to the turn 180° − α.
4. **Open the doors** again (70°).

With `doors` = `none`, only steps 2 and 3 remain. The sequence control starts at the end, with the
village open.

**Preview and engine.** The studio preview plays the whole program, with the book standing upright:
the strip is one sheet whose face tree carries every house and door. The ribbons and the lining
glue are joins that only the physics engine resolves. As in `carousel-book`, a string join cannot
be untied in spec v1, so an engine run keeps the book tied. The engine adds the card's stiffness
and the weight of the standing book.

## Making one by hand

1. Export the strip (`svg`, `dxf`, `pdf` or `hpgl`). Outline, slits, windows and door edges are on
   the cut layer, every fold on the score layer. A long strip can be printed in pieces and joined on
   a spine fold with tape on the outside.
2. Score every fold, cut every window, then cut the slits and the door edges.
3. Fold the fore-edge folds shut and glue the two layers of each double wall back to back, but
   leave the houses free: glue only outside each house's outline.
4. Fold each lining behind its cover and glue it down.
5. Close the book gently. Each house folds inward along its three folds. Open it until the covers
   meet, tie the ribbons, and push each house into shape the first time.

## Parameters

| id | meaning | default | range |
|---|---|---|---|
| `chambers` | chambers (houses) in the open book | 6 | 4–8 |
| `page_width` | spine to fore-edge (radius); houses scale with it | 110 mm | 80–180 mm |
| `page_height` | height of the book; walls and roofs scale with it | 150 mm | 110–260 mm |
| `village` | `mixed`, `cottages` or `flat-roofs` | `mixed` | |
| `doors` | `opening` (flaps) or `none` | `opening` | |
| `stock` | `cardstock-250` or `cardstock-160` | `cardstock-250` | |

Presets: `four-houses`, `eight-houses`, `cottage-row` (five cottages), `a5` (148 × 210 mm
pages).

## History and sources

Carousel books look like ordinary books but open until their front and back covers touch. The
Smithsonian Libraries describe one that becomes a three-dimensional object seen from all angles
and is held as a circle by tying its ribbons (Smithsonian Libraries and Archives, «A Carousel
Holiday Decoration», https://library.si.edu/finding-aid/carousel-holiday-decoration). Let's Talk
Picture Books, «Favorite Carousel Books» (2022,
https://www.letstalkpicturebooks.com/2022/02/favorite-carousel-books.html) gives more examples.

Pop-ups cut and folded from a single sheet are the basis of origamic architecture. That practice is
associated with the Japanese architect Masahiro Chatani from the early 1980s (Wikipedia,
«Origamic architecture», https://en.wikipedia.org/wiki/Origamic_architecture). The box or
parallel fold is a general mechanism of the pop-up literature, for example Paul Jackson, *Cut and
Fold Techniques for Pop-Up Designs* (Laurence King, 2014) and Duncan Birmingham, *Pop-Up Design
and Paper Mechanics* (GMC Publications, 2010).

The house shapes are generic village forms drawn for this cartridge. They depict no particular
place or building, and no published carousel or pop-up is reproduced.

## Provenance and licence

Original MADFAM design: the strip, the houses and every angle are generated by `main.py` with the
kernel's `carousel_strip` and `cut_fold` builders. Published under CERN-OHL-W-2.0, like every object
in the commons (see the commons root `LICENSE`).
