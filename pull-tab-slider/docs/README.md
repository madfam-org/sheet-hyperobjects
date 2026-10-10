# Pull-tab slider

| | Title | Summary |
|---|---|---|
| en | Pull-tab slider | A pull tab that moves a part: a picture strip sliding in a glued channel behind a window, or a lever on a brad that swings a paddle. |
| es | Lengüeta deslizante | Una lengüeta que mueve una pieza: una tira de imágenes que se desliza por un canal pegado detrás de una ventana, o una palanca sobre un broche que hace girar una paleta. |
| fr | Tirette coulissante | Une tirette qui fait bouger une pièce : une bande d'images qui coulisse dans un canal collé derrière une fenêtre, ou un levier sur une attache parisienne qui fait pivoter une palette. |
| pt | Puxador deslizante | Um puxador que move uma peça: uma tira de imagens que desliza num canal colado atrás de uma janela, ou uma alavanca num colchete que faz uma paleta girar. |

## What it is

Pull tabs are the working parts of movable books: a strip of card sticks out of the page edge, and
pulling it makes something on the page move. This cartridge has the two basic forms:

- **`straight`**: a picture strip slides in a channel behind the page. Pull its tab and the
  strip's second picture slides into a window cut in the page.
- **`pivoting`**: a lever turns on a brad in front of the page. Move its tab along the page edge
  and the paddle at its other end swings the other way, through an arc.

## Geometry

**Straight.** Five sheets stacked 0.3 mm apart, inside the 0.36 mm collision thickness of the
300 g/m² page stock, so every glue weld holds in the initial frame: from the bottom up, the backing,
two rails, the strip (between the rails) and the page.

- The page has a window `window_width` × `window_height`, at least 4 mm lower than the strip, so
  the strip's edges never show.
- The strip is `strip_width` wide. It travels the window's width plus 6 mm, so its second picture
  (printed that far to the left of the first) replaces the first.
- **Stops.** The strip's inner end is a head 3 mm wider on each side. The rails leave a wide
  channel for it as far as the point where the head arrives at full travel, and from there to the
  page edge the channel narrows to the strip's width plus 1 mm each side: the head stops there.
  At the other end, a grip wider than the channel mouth sits 2 mm outside the page edge, so the
  strip cannot be pushed in further than its rest position.
- Each rail's outer, full-length band is glued to the backing below and to the page above (four
  `glue` joins, all between sheets that do not move).

**Pivoting.** Two sheets: the page and the lever, 0.3 mm above it. The lever is a round paddle
(`paddle` across), a neck `lever_width` wide and a wider grip, `lever_length` in all. It turns on a
brad through a 3 mm hole at the paddle's neck, marked on the page by a kiss-cut cross. The pivot
is placed so that the grip reaches `grip` past the page's right edge.

## The mechanism

- **Straight**: the strip is a kinematic sheet moved by a `translate` mechanism along the
  channel. The `pull` control (a distance, 0 to the full travel, in mm) is the strip's position.
- **Pivoting**: the lever is a kinematic sheet turned by a `rotate` mechanism about the brad. The
  `swing` control (0 to `swing` degrees) is its angle.

Neither moving sheet has a join of its own. The rails, page and backing are glued to each other,
and the brad is the rotate mechanism's centre. So **both controls play in the studio preview**.
The `slide` mechanism and `slider` joins in the spec would also describe a strip on a track, but
the preview leaves them to the physics engine, and a straight strip in a straight channel is
exactly a translation. What this cartridge does not include is the classic linkage that turns a
straight pull into a rotation (a pin running in a slot). That needs a `slider` join, so it waits
for the engine, and the pivoting lever here is moved at its own tab instead.

**Preview and engine.** The physics engine adds friction in the channel and the slight flex of a
long strip.

## Making one by hand

1. Export the sheets (`svg`, `dxf`, `pdf` or `hpgl`) and print the two pictures on the strip, one
   `window_width + 6` mm to the left of the other.
2. Cut everything; cut the window from the page.
3. **Straight:** glue the two rails to the backing, lay the strip between them with its head in the
   wide part, and glue the page on top along the rails. Pull the tab and check the stops.
4. **Pivoting:** punch the lever's hole, push a paper brad through it and through the page at the
   kiss-cut mark, and open the brad's legs behind the page.

## Parameters

| id | meaning | default | range |
|---|---|---|---|
| `page_width`, `page_height` | the page | 200 × 150 mm | 120–300, 100–300 mm |
| `grip` | how far the tab reaches past the page edge | 18 mm | 10–40 mm |
| `window_width`, `window_height` | the window (mode `straight`) | 50 × 34 mm | 15–120, 10–100 mm |
| `strip_width` | the picture strip | 44 mm | 15–110 mm |
| `lever_length`, `lever_width` | the lever (mode `pivoting`) | 120, 14 mm | 60–260, 8–30 mm |
| `paddle` | diameter of the paddle | 30 mm | 10–60 mm |
| `swing` | how far the lever turns | 40° | 10–70° |

Presets: `wide-window`, `long-lever`, `small-page`.

## History and sources

Tab-operated movable books were made in nineteenth-century Germany and Britain by Lothar
Meggendorfer and Ernest Nister, among others (Wikipedia, «Pop-up book»,
https://en.wikipedia.org/wiki/Pop-up_book). Pull tabs and levers are described in the pop-up
literature, for example David A. Carter and James Diaz, *The Elements of Pop-Up* (Little Simon,
1999). No book's design is copied; the geometry is computed by this cartridge.

## Provenance and licence

Original MADFAM geometry (the lineage records the general devices, credited to the tradition).
Published under CERN-OHL-W-2.0 like every object in the commons (see the commons root `LICENSE`).
