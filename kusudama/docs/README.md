# Kusudama

| | Title | Summary |
|---|---|---|
| en | Kusudama | The traditional Japanese flower ball, glued: a square folded on its diagonal, its corners brought up into a diamond and rolled into a cone makes a petal; five petals make a flower and twelve flowers make the ball. |
| es | Kusudama | La tradicional bola de flores japonesa, pegada: un cuadrado doblado por la diagonal, con las esquinas subidas en un rombo y enrollado en cono, forma un pétalo; cinco pétalos forman una flor y doce flores forman la bola. |
| fr | Kusudama | La boule de fleurs japonaise traditionnelle, collée : un carré plié sur sa diagonale, ses coins remontés en losange puis roulé en cône, donne un pétale ; cinq pétales font une fleur et douze fleurs font la boule. |
| pt | Kusudama | A tradicional bola de flores japonesa, colada: um quadrado dobrado na diagonal, com os cantos levados para cima num losango e enrolado em cone, faz uma pétala; cinco pétalas fazem uma flor e doze flores fazem a bola. |

## What it is

A kusudama is a ball made from many identical folded paper units. This cartridge models the
glued flower kind: every petal is one square, folded and rolled into a cone; five petals glued
side by side make a flower; twelve flowers glued together make the ball, one flower on each face
of a dodecahedron (12 × 5 = 60 squares).

It has three modes:

- `petal`: one square folded into a petal, step by step, in the studio preview;
- `flower`: the five glued petals of one flower;
- `ball`: the twelve flowers of the finished ball.

The petal is the traditional glued construction: fold a diagonal, bring the corners up, roll and
glue. No designer's modular unit is used, and no published diagram is copied. All the geometry is
computed by `main.py`.

## Geometry

**The petal is a single-vertex fold.** Call the centre of the square O. On the sheet, the outer
corner B is at the lower left, A at the upper left, C at the lower right and D at the upper right.

1. The diagonal fold A–C puts D on B.
2. Folding A and C up to B adds the two midlines of the square.

Every crease passes through O. The folded state is therefore a diamond: a quarter of the square,
in four layers, with its 90° corner at O. Each of the six sectors of the sheet lands on the
diamond by a rotation or a reflection about O.

**Rolling.** The diamond is rolled into a cone around O, coloured side out and flaps inside. Its
two straight edges overlap by 10°, and that strip is the glued seam. The cone's development angle
is therefore Ψ = 90° − 10° = 80°.

**Segmentation.** A rolled surface is modelled as a pyramid of flat facets, following the commons
convention. The facet edges are rulings from O: `F` lines with treatment `none`, which is plain
paper that is never scored or cut. Every layer of the stack carries its rulings at the same
diamond angles, so the four layers roll as one. For that reason, the loop of creases around O
closes for any amount of roll. The script checks this with `pliego.kinematics.closure_residual`
on the blended states of every step, and the worst residual is about 1e-13 mm.

**The cross-section is designed for the flower.** The axis of the flower runs through the common
tip O of its five petals. A petal is bounded by the two planes at ±36° about that axis, which are
the mirror planes between neighbours. Going round the petal, its cross-section has:

- an **inner facet** 30° wide that faces the axis and holds the seam;
- two **contact facets**, each lying in one of the two planes, so neighbouring petals touch face
  to face and are glued there;
- four **outer facets** whose profile leans out by `flare`.

The inner facet fixes how far the contact rays sit from the axis (sin θ = sin 15° / sin 36°,
θ ≈ 26.1°). The width of the contact facets is solved so that the facets add up to Ψ: 4.76° at the
default flare, which is a glue strip about 4 mm wide at 75 mm. In the flower, the petals lie
between 26° and 35° from the axis. The five inner facets leave a small pentagonal well at the
centre.

**The glue is exact in the closed form.** Each weld is an isometry of the sheet:

- the seam welds the outer layer of one overlap strip onto the inner flap of the other (a
  reflection about O);
- a petal-to-petal weld maps a contact facet onto the neighbour's mirror facet (a reflection
  across the diagonal through B).

The script fails loud if any weld point misses by more than 1e-6 mm. In the built documents, the
worst gap is 1.4e-5 mm, which is coordinate rounding.

**The ball.** The script places the flowers on the twelve faces of a dodecahedron, with the
petals pointing at the edge midpoints of each face. It then solves the radius at which
neighbouring flowers just touch: the flower's farthest vertex towards the plane that bisects two
faces lies on that plane. With these narrow cone petals, the flower tips end up almost at the
centre of the ball, 1.3 mm from it. At 75 mm squares the ball fits in a sphere 108 mm across
(103 mm along each axis).

Touching petals of two flowers meet along a chord of their rims. That contact is a line, so it
cannot be an area weld. The model joins each such pair at both ends with a short `string` join,
a dab of glue in effect: 60 strings in all.

For the render budget, the ball uses the plainest petal: one outer facet instead of four (contact
facets 6.5°). That gives 22 faces and 68 render vertices per petal, so 4,080 render vertices for
60 sheets. The ball is the one document above the commons' preview budget of about 2,000
vertices, and the studio stub still loads and scrubs it in well under a second. The petal and
flower modes use 96 and 480 render vertices.

The square passes `pliego.papercut.analyze` at 1 mm.

## The fold program

**Mode `petal`** is a `kinematic` program:

1. coloured side down, fold the diagonal (two creases to 180°);
2. bring the base corners up to the top corner (the two midlines: 180° on the lower layer, −180°
   on the upper);
3. curl the diamond (every ruling at half its final angle);
4. overlap the edges and glue: the cone;
5. hold the seam until the glue sets.

The seam is a `glue` join with `active_from: "press"` (sheet-document spec §5.19), so the square
starts flat and the program ends glued. The rolling steps are exact for a straight blend of
angles, because the layered fan has no loop of its own. The program ends in the petal, which is
also written as `target:petal`.

**Mode `flower`** starts from an `initial` frame: the glued flower standing on its tip. It has 10
glue joins: five seams and five petal-to-petal welds. Its `physical` program presses the flower
against the palm, which opens the rolls to 60% of their angle, then eases the petals back. The
end state is the glued flower again, and it is written as `target:flower`.

**Mode `ball`** starts from the assembled ball as its `initial` frame, also written as
`target:ball`. It has 120 glue joins and 60 strings. Its `physical` program presses one petal
and eases it back.

**Preview and engine.** The studio preview plays all three programs. In `petal` mode the end
pose equals `target:petal` to 7e-7 mm once the preview's display offset is removed. The preview
draws flat-folded layers at 179.5° rather than 180° so that they do not z-fight, which leaves a
0.25 mm offset. The `flower` and `ball` previews start on their `initial` frames in the same way.

In between, the preview blends the press as plain angles. Each petal stays a rigid, valid shape,
but the welds open for a moment. The physics engine keeps the welds and bends the paper instead.
The preview also ignores joins, so it cannot show the gluing itself. Moving petals from the petal
into the flower, or flowers into the ball, is an assembly step that is not modelled.

## Making one by hand

1. Cut 60 squares, 75 mm by default (`svg`, `dxf`, `pdf` or `hpgl` export). The rulings are not
   on the cut file; the creases are drawn as the diagram lines.
2. For each petal, start coloured side down:
   - fold the square on its diagonal into a triangle;
   - bring the two base corners up to the top corner to make a diamond;
   - roll it into a cone around the bottom point, flaps inside;
   - glue the 10° overlap of the two edges.
3. Glue five petals side by side, contact faces together, with their tips meeting at the centre:
   a flower.
4. Glue the twelve flowers into a ball with a dab of glue where the petals of neighbouring
   flowers touch.

Kami holds a crisp cone. Kozo washi is softer and forgiving, and copy paper is stiffer. A glue
stick suits kami.

## Parameters

| id | meaning | default | range |
|---|---|---|---|
| `size` | side of each square | 75 mm | 50–150 mm |
| `flare` | how far each petal's lip leans out (petal and flower modes) | 4° | 0–8° |
| `stock` | `kami`, `washi-kozo-30`, `copy-80` | `kami` | |
| `colour` | colour of the outside (the back of the sheet) | red | five colours |

Presets:

- `small`: 50 mm, pink;
- `washi-large`: 150 mm kozo washi, indigo;
- `round`: no flare, gold.

The script refuses a cross-section whose contact facets would be narrower than 2°.

## History and sources

- **What a kusudama is.** Wikipedia describes the kusudama as a paper model usually made by
  sewing identical pyramidal units together into a sphere. The units may also be glued.
- **The name.** It joins the Japanese words *kusuri* (medicine) and *tama* (ball).
- **Early use.** Kusudama were used for incense and potpourri, and were possibly once real
  bunches of flowers or herbs.
- **Paste and modules.** Early traditional Japanese origami often used both cutting and pasting.
  Many modern kusudama are modular origami, whose units slot into pockets (Wikipedia,
  «Kusudama», https://en.wikipedia.org/wiki/Kusudama).

David Mitchell's Public Paperfolding History Project says kusudama were originally cloth bags of
herbs. At a date he does not know, the word also came to mean hanging balls of flowers folded
from paper, often glued or sewn together. This is said to be one of the roots of modular origami,
but historical sources that confirm it are lacking. He also notes that the *Pillow Book* of Sei
Shōnagon, completed in 1002, refers to herbal balls (Mitchell, «Kusudama»,
https://origamiheaven.com/historyofkusudama.htm).

This cartridge credits the glued flower ball to that Japanese tradition. It claims no date and no
inventor for the petal.

## Provenance and licence

Original MADFAM geometry: the single-vertex petal, the faceted cone, the contact solve for the
flower and the dodecahedral ball are computed by `main.py`. The lineage credits the kusudama
tradition with its sources. No modular unit by any designer and no published diagram is used.

Published under CERN-OHL-W-2.0 like every object in the commons (see the commons root `LICENSE`).
