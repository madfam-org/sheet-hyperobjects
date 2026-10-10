# Lift-the-flap

| | Title | Summary |
|---|---|---|
| en | Lift-the-flap | A flap over a page that lifts to show what is under it: rectangle, rounded, arch or two doors, as a rigid flap on a hinge or as paper with a glued tab. |
| es | Solapa para levantar | Una solapa sobre una página que se levanta para mostrar lo que hay debajo: rectangular, redondeada, en arco o en dos puertas, rígida con bisagra o de papel con pestaña pegada. |
| fr | Rabat à soulever | Un rabat sur une page qui se soulève pour montrer ce qu'il cache : rectangle, arrondi, arc ou deux volets, rigide sur charnière ou en papier à patte collée. |
| pt | Aba para levantar | Uma aba sobre uma página que se levanta para mostrar o que há embaixo: retangular, arredondada, em arco ou em duas portas, rígida com dobradiça ou de papel com aba de cola. |

## What it is

A flap covers part of a page, and lifting it shows what is printed underneath. It is the simplest
movable in books, and for many children the first. This cartridge covers the common shapes: a
rectangle, rounded free corners, a round-ended arch, and a pair of doors meeting in the middle. A
single flap is hinged along its top (it lifts up) or its left side (it opens like a door).

It comes in two modes with the same geometry:

- **`hinged`**: the flap is a rigid board turned about its hinge edge by a `hinge` mechanism, with
  the `lift` angle control (0–180°). This is how a stiff flap in a board book behaves.
- **`glued-tab`**: the paper construction. The flap and a glue tab are one piece with a scored
  hinge between them, the tab is glued to the page, and a fold program lifts the flap and lowers it.

## Geometry

The page is a `page_width` × `page_height` sheet of 300 g/m² card. The flap covers a window
`flap_width` × `flap_height`, placed by `flap_x` and `flap_y` (0 to 1 across the free space). Each
flap is drawn in its own frame: u runs from the hinge (u = 0) to the free edge and v across it. A
rotation about the vertical places it on the page, so the hinge is the same line in every case:

- a rectangle, or rounded free corners (radius up to 10 mm), or a semicircular free end (the arch
  needs a flap longer than half its width plus 5 mm);
- for `doors`, two flaps each 0.5 mm short of half the window, hinged at the outer sides and turned
  180° to face each other;
- in `glued-tab` mode, a tab `tab_width` wide lies before the hinge (u from −t to 0) and the hinge
  is a scored valley.

The flaps lie 0.2 mm above the page, less than the stocks' collision thickness, so a glued tab sits
on the page within the weld tolerance of the sheet-document spec.

## The mechanism and the fold program

**`hinged`.** Each flap is a kinematic sheet. Its `hinge` mechanism turns it about the hinge line on
the page, by the `lift` control's value (rest 0°). The axis is oriented so that a positive angle
lifts the flap off the page, and both doors share the one control. The attachment itself (in a
board book, a strip of tape or cloth along the hinge) is the mechanism's axis and is not a sheet of
the document. That is deliberate: a `glue` join between the moving flap and the fixed page would
leave the control to the physics engine. The `glued-tab` mode models the attached paper flap
exactly.

**`glued-tab`.** The tab is welded to the page by a `glue` join. A `kinematic` fold program lifts
the flap to `lift_to` (150° by default) in 8 substeps and lowers it again in 8; its control starts
lifted. The flap's crease is its only fold, so the motion is exact.

**Preview and engine.** Both modes play in the studio preview. In `hinged` mode the preview turns
the board. In `glued-tab` mode it poses the piece from its tab, which never moves, so the tab
stays on its glue zone (checked on the exported documents: within 0.2 mm, the lift). The physics
engine adds what a rigid flap cannot show: a paper flap bends a little as it is lifted by its
corner, and it falls back when let go.

## Making one by hand

1. Export the sheets (`svg`, `dxf`, `pdf` or `hpgl`) and print the hidden picture on the page inside
   the window and the flap's picture on the flap.
2. Cut the page and the flap. In `glued-tab` mode, score the hinge between the flap and its tab.
3. Fold the tab back along the score, glue it to the page with the hinge on the window's edge, and
   press. For two doors, glue one on each side.
4. For a stiff flap (the `hinged` mode), cut it from heavier board and hinge it with a strip of
   book tape or cloth along its edge.

## Parameters

| id | meaning | default | range |
|---|---|---|---|
| `style` | `rectangle`, `rounded`, `arch`, `doors` | `rounded` | |
| `hinge_side` | `top` or `left` (single flaps) | `top` | |
| `flap_width`, `flap_height` | the covered window | 90 × 70 mm | 20–260 mm |
| `tab_width` | glue tab (mode `glued-tab`) | 10 mm | 6–20 mm |
| `page_width`, `page_height` | the page | 200 × 200 mm | 100–300 mm |
| `flap_x`, `flap_y` | position of the window on the page | 0.5, 0.5 | 0–1 |
| `lift_to` | how far the program lifts the flap (mode `glued-tab`) | 150° | 30–175° |

Presets: `window-doors`, `arched-door`, `small-page`.

## History and sources

Flaps are among the oldest movable devices in books: early movables illustrated anatomy books with
layers and flaps (Wikipedia, «Pop-up book», https://en.wikipedia.org/wiki/Pop-up_book), and the
flap remains a staple of children's books. No book's design is copied; the geometry is computed by
this cartridge.

## Provenance and licence

Original MADFAM geometry (the lineage records the general device, credited to the tradition).
Published under CERN-OHL-W-2.0 like every object in the commons (see the commons root `LICENSE`).
