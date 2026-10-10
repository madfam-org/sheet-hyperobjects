# Flip book

| | Title | Summary |
|---|---|---|
| en | Flip book | A padded stack of 12 to 48 hinged pages thumbed by one control in a staggered cascade, riffled or flicked, with a computed frame plan that says which page carries each frame and where to draw it. |
| es | Folioscopio | Un taco de 12 a 48 páginas con bisagra, encolado por el lomo, que se hojea con un solo control en cascada escalonada, en abanico o desde la portada, con un plan de cuadros calculado que dice qué página lleva cada cuadro y dónde dibujarlo. |
| fr | Folioscope | Un bloc de 12 à 48 pages articulées, encollé au dos, feuilleté par une seule commande en cascade décalée, en défilement ou depuis la couverture, avec un plan d'images calculé qui indique quelle page porte chaque image et où la dessiner. |
| pt | Flip book | Um bloco de 12 a 48 páginas articuladas, colado pela lombada, folheado por um único controle em cascata escalonada, soltando as páginas ou a partir da capa, com um plano de quadros calculado que diz que página leva cada quadro e onde desenhá-lo. |

## What it is

A flip book (kineograph, *Daumenkino* in German, "thumb cinema") is a small book whose pages
each carry one drawing of a sequence; thumbed quickly, the drawings seem to move. This cartridge
makes the book itself: 12 to 48 pages (`pages`) of one size (`page_width` × `page_height`,
presets index card, A7 landscape and pocket), cut from cardstock or copy paper, stacked and
padded (glued) along the spine. One control, **Thumb the book**, plays the whole riffle.

Two ways of thumbing are offered (`thumbing`):

* **riffle** (default): the thumb bends all the pages back at the free edge and lets them spring
  free one at a time. The page nearest the pile is freed first, so the **bottom page carries
  frame 1** and the cover carries the last frame;
* **flick**: the thumb lifts the free edge and flicks the pages over the spine one at a time
  from the cover, so the **cover carries frame 1**.

The pages are blank. The studio draws no art on faces, and a drawn line on the sheet would land
on a fabrication layer (score or cut), so this cartridge prints no fake marks. Instead,
`frames = bouncing-ball` computes a **frame plan**: for every frame, the page that carries it
and the centre of a bouncing ball, measured from the hinge line and from the tail (bottom) edge.
The plan is written into the step notes of the program, frame by frame. `frames = blank` lists
only which page carries which frame.

## Geometry

Every page is its own sheet (`page-01` is the cover, `page-NN` the last page), W × H, in
sheet-local millimetres computed by `main.py`:

| line | where | kind | edge name |
|---|---|---|---|
| spine | u = 0 | outline, padded (glued) | `spine` |
| hinge score | u = M (`binding_margin`) | valley, scored | `hinge` |
| free edge | u = W | outline | `fore-edge` |

The strip 0 ≤ u ≤ M is the **binding margin**: it goes into the padded block and is never seen.
The **picture area** is the rest, (W − M) × H. The margin is held to at most a third of the
page width, so the picture area is always at least twice the margin and at least 30 mm wide
(checked). The binding margin is the root face of each sheet (checked), so
in the preview the margin stays put and the page turns about the hinge score.

The sheets form one `pliego:stacks` entry, `block`, listed bottom to top, `pitch_mm` equal to
the stock's caliper (0.1 mm for copy paper, 0.2 mm and 0.3 mm for the cardstocks), bond `none`
(the pages only rest on each other) and binding `padding` along the spine edge: the padded
block of a memo pad. Spec rule 12 checks that the pitch matches the caliper and that every page
sits one pitch above the one below.

For cutting, the pages are laid out six to a row (page 1 at the bottom left). The outlines are
on the cut layer and the hinge scores on the score layer; nothing else is drawn.

## The thumbing program

A `kinematic` program of one bend step and 8 to 24 cascade steps (`pages` ÷ 2, at least 8, at
most 24). Each page has one hinge and no loop, so every state is rigid and exact.

1. **Bend.** Riffle: the stack stands up past upright on its hinges, fanned half a degree per
   page with the cover outermost (the rigid hinges stand in for the curl a thumb puts in real
   paper). Flick: the thumb lifts the free edge, the cover 35° and the last page not at all.
2. **Release.** The pages spring free in order. Page *j* starts at time
   s<sub>j</sub> = r / (N − 1) × (1 − 0.25), r being its place in the release order, and takes a
   quarter of the riffle to land (riffle: back flat on the pile; flick: over the spine). Its angle
   is linear in time, which is exactly how the studio blends one step into the next, so the
   preview shows the true staggered cascade. At every key state the script checks that no page
   passes through the one below it (top-to-bottom angles never increase), that every frame
   springs free in exactly one step and that every page lands.

`riffle_speed` (pages per second) sets the tempo: the release front passes the N pages in
(N − 1) / speed seconds. Every step lasts at least 0.1 s, so a 12-page book at top speed plays a
little slower than real time.

**Preview and engine.** The studio preview plays the whole riffle (sequence control). It does not
bend the paper: pages turn rigidly at the hinge score. In flick mode the turned pages lie in the
reverse depth order on the left (zero-thickness rigid pages cannot pile up by contact). The
physics engine adds what makes a real riffle: the paper's spring, the curl under the thumb, the
padding holding the block, contact between the pages and their thickness. The program itself
needs no join and no slide, so nothing is disabled in the preview.

## Making one by hand

1. **Cut the pages.** Export (`svg`, `dxf`, `pdf` or `hpgl`) and cut the outlines, or use index
   cards, which are the right size already (the `index-card` preset). The pages should be
   springy, so card is the default; copy paper is offered for small pages (`pocket`). Score
   each hinge line.
2. **Number the pages** lightly in the binding margin, where it will be hidden.
3. **Plan the frames.** Pick a motion (the bouncing ball is the classic first exercise) and read
   the frame plan in the step notes: frame *f*, page *j*, the ball's centre so many millimetres
   from the hinge line and from the tail edge. Keep every drawing near the free edge: that is
   the part the eye sees while the pages spring past; the margin and the inner part of the page
   are hidden by the thumb and the block.
4. **Draw with registration.** Draw a key drawing first. Put it on a window (or a light box),
   lay the page for frame 1 over it with the spine and the tail edge against the same two
   straight edges, and trace. Then lay the page for frame 2 over frame 1, trace it with a small
   change, and so on; test the run every few pages. Aligning every page by the spine and the
   tail edge keeps the frames registered, so only the drawing moves, not the page.
5. **Bind.** Square the stack on the spine and the tail edge, the pages in order (riffle: the
   page with frame 1 at the bottom; flick: on top), and hold the margin with a binder clip, as
   the handout cited below does. The document models the other way, a padded block: glue
   brushed along the clamped spine edge, which keeps the pages in register for good.
6. **Thumb it.** Hold the block by the spine, bend the free edges back with your thumb and let
   the pages slip free one at a time.

## Parameters

| id | meaning | default | range |
|---|---|---|---|
| `pages` | number of pages (one frame each) | 24 | 12–48 |
| `thumbing` | `riffle` (bend back, release) or `flick` (from the cover) | `riffle` | |
| `riffle_speed` | pages released per second (timeline tempo) | 12 | 6–24 |
| `page_width` | spine to free edge, margin included | 127 mm | 50–150 mm |
| `page_height` | spine length | 76.2 mm | 40–110 mm |
| `binding_margin` | padded strip; the hinge score runs along it (at most a third of the width) | 10 mm | 6–20 mm |
| `stock` | `cardstock-160`, `cardstock-250` or `copy-80` | `cardstock-160` | |
| `frames` | `bouncing-ball` frame plan or `blank` (page order only) | `bouncing-ball` | |

Presets: `index-card` (5 × 3 in = 127 × 76.2 mm, cardstock 160 g/m², 24 pages), `a7` (A7 landscape
105 × 74 mm, cardstock 250 g/m², 32 pages), `pocket` (80 × 50 mm, copy paper, 48 pages, 8 mm
margin).

## History and sources

The flip book's oldest known documentation is the patent John Barnes Linnett took out on
18 March 1868 for the "kineograph" ("moving picture"); in 1894 Max Skladanowsky showed serial
photographs in flip-book form, the same year Herman Casler's Mutoscope mounted the pages on a
rotating cylinder instead of binding them, and in 1897 Henry William Short marketed the Filoscope,
a flip book in a metal holder (Wikipedia, «Flip book», https://en.wikipedia.org/wiki/Flip_book).
Linnett was a lithograph printer in Birmingham; although the Frenchman Pierre-Hubert Desvignes is
generally credited with the invention, Linnett was the first to patent it (Wikipedia, «John
Barnes Linnett», https://en.wikipedia.org/wiki/John_Barnes_Linnett). Birmingham's Flatpack
Festival places his shop on Smithfield Street, near the Bull Ring, and notes that the patent
document is held by Birmingham Central Library (Flatpack Festival, «Home of the flipbook»,
https://flatpackfestival.org.uk/posts/home-of-the-flipbook).

How it is used: a flip book has relatively springy pages, each with one image of the sequence
near its unbound edge; the user bends the pages back, normally with the thumb, and lets them
spring free one at a time (Wikipedia, «1868 in animation»,
https://en.wikipedia.org/wiki/1868_in_animation). The German name *Daumenkino* means "thumb
cinema" (Wikipedia, «Flip book»). The making steps above follow a library maker handout: index
cards or a sticky-note pad, numbered pages, a key drawing traced on a bright window, each page
traced over the one before with a small change, regular tests, and a binder clip to finish
(College of San Mateo, Family Science Day 2021, «Flip Books!»,
https://collegeofsanmateo.edu/familyscienceday/docs/FlipBookHandout.pdf).

The padded block, the hinge score, the release order, the frame plan and the bouncing-ball path
are this cartridge's own; no template is copied.

## Provenance and licence

Original MADFAM geometry, thumbing program and frame plan for a public-domain format (the
kineograph, patented in 1868). Published under CERN-OHL-W-2.0 like every object in the commons
(see the commons root `LICENSE`).
