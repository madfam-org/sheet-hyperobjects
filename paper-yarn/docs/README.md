# Paper yarn, cord and rope

| | Title | Summary |
|---|---|---|
| en | Paper yarn, cord and rope | A narrow strip of paper twisted into yarn; two yarns plied into a cord, three into a rope. The twist is modelled as the strip winding round a tube, so it plays step by step and exactly. |
| es | Hilo, cordón y cuerda de papel | Una tira angosta de papel torcida hasta hacer hilo; dos hilos torcidos juntos dan un cordón y tres, una cuerda. La torsión se modela como la tira enrollada alrededor de un tubo, así que se reproduce paso a paso y de forma exacta. |
| fr | Fil, cordelette et corde de papier | Une bande étroite de papier tordue en fil ; deux fils retordus donnent une cordelette, trois une corde. La torsion est modélisée comme la bande enroulée autour d'un tube : elle se joue pas à pas et de façon exacte. |
| pt | Fio, cordão e corda de papel | Uma tira estreita de papel torcida até virar fio; dois fios torcidos juntos dão um cordão e três, uma corda. A torção é modelada como a tira enrolada em volta de um tubo, de modo que se reproduz passo a passo e de forma exata. |

## What it is

Paper can be spun. Cut it into a narrow strip, twist it, and it rolls up on itself into a thread;
twist two threads together and you have a cord, three and you have a rope. In Japan, thread made
this way from strips of washi is woven into a cloth called *shifu*. This cartridge is the family of
twisted paper: three modes, `yarn` (one strip), `cord` (two plies) and `rope` (three plies), with
the strip width, the twist angle, the length and the twist direction (S or Z) as parameters. Each
mode plays the twist step by step, from a flat strip to the finished thread.

## Geometry

**What can and cannot be modelled.** A strip twisted about its own long axis is not developable:
real paper yarn is rolled, crushed and twisted all at once, and the paper wrinkles. Pliego's sheets
only bend without stretching, so the cartridge uses the developable shape closest to a twisted
strip: **the strip wound as a helical ribbon round a tube.** A cylinder unrolls flat, and on the
unrolled cylinder the strip is a straight band crossing it at the twist angle β, the angle between
the paper's length and the yarn's axis. Wind that band back up and every point of the paper keeps
its distances: an exact isometry.

**Sizes.** With m plies of width w wound butt to butt, one turn of the tube is m bands wide, so the
tube's perimeter is C = m·w / cos β and one strip advances P = C / tan β along the axis per turn.
The default yarn (w = 12 mm, β = 35°, m = 1) has C = 14.65 mm (about 4.8 mm across), P = 20.9 mm,
9.6 turns over 200 mm, so about 48 turns per metre. The default cord is 9.6 mm across and the rope
14.4 mm, from the same 12 mm strips.

**Segmentation.** The round tube is a prism of `facets` sides (8 by default). Its generators, the
lines parallel to the axis, are `F` lines on the strip: straight lines at angle β to the strip's
length, h = C / facets apart (measured square to them). They are plain paper (treatment `none`):
not scored, not on the cut file. The strip's two ends are cut on the bias, parallel to these lines,
so every panel is the same parallelogram and no sliver is left at the ends (the default strip is
242.6 × 12 mm with 76 panels).

**Why the twist is exact.** All the lines are parallel and none of them cross. Folding every one by
the same angle φ rotates each panel about an axis parallel to the same direction, so the strip
coils into a polygonal helix whose cross-section is a regular polygon of exterior angle φ. At
φ = 360° / facets (45° by default) the polygon closes and the turns butt edge to edge. Every
intermediate state is an exact rigid state. The script checks that the tube keeps every edge length,
that each fold is a valley of 360°/facets, that the bands butt, and that the helix has the right
handedness for its twist letter.

**Plies.** A cord or a rope is two or three identical strips, one sheet each, wound round one tube
side by side. In the flat start they lie next to each other on the table, ply k shifted by
k·w / sin β along the direction of the twist lines. A shift along that direction commutes with every
fold, so the plies stay interleaved at every step and close into a tube made of two or three
helical bands. This shows the ply count and the ply twist. It does not show each ply's own twist,
or a ply's round cross-section: plying round yarns crushes and bends them, which no flat strip can
do without stretching.

**Twist direction.** Z: the turns slant like the middle stroke of a Z, a right-handed helix. S: like
the middle stroke of an S, left-handed. Choosing S mirrors the pattern.

The colour of the outside of the yarn is printed on the back of the strip: the rolls are valley
folds, so the front ends up inside.

## The fold program

Every mode is a `kinematic` program on the twist lines (all of them at once):

1. start twisting: the strip curls into a loose helix (a third of the final angle);
2. keep twisting: the helix tightens and narrows (two thirds);
3. twist until the turns close up edge to edge (360° / facets).

It ends in the finished yarn, cord or rope, which is also written as the frame `target:yarn`,
`target:cord` or `target:rope`. The thread lies along the table at the twist angle to the strip's
first position, because the preview keeps the strip's first panel on the table.

**Preview and engine.** The studio preview plays the program exactly: the lines are parallel, so a
blend of angles is the true rigid motion, and the end pose equals the target frame. What only a
physics engine (or a hand) does: rolling the strip tight so that the thread is solid rather than a
hollow tube, the crumpling of the paper, and the opposite twist of each ply inside a plied cord.
None of them is a fold of rigid panels.

## Making one by hand

1. Export a strip (`svg`, `dxf`, `pdf` or `hpgl`) as a cutting guide, or simply cut a long strip of
   the chosen width with a ruler. The twist lines are not on the file.
2. Pinch one end and twist it between your fingers, always the same way, feeding the strip in at
   the twist angle. It curls into a tube and then rolls tight.
3. For a cord, twist two yarns the same way, then hold them together and twist them the opposite
   way. For a rope, do the same with three.

Wikipedia's articles on yarn and rope note that plied yarn and laid rope are twisted in the
opposite direction to the twist of their components, and that this counter-twist is what holds the
rope together. The model shows the plying twist only.

## Parameters

| id | meaning | default | range |
|---|---|---|---|
| `strip_width` | width of each ply's strip | 12 mm | 4–40 mm |
| `twist_angle` | angle between the paper's length and the yarn's axis | 35° | 20–60° |
| `length` | yarn length (along its axis) | 200 mm | 60–400 mm |
| `twist` | twist direction | `Z` | `Z`, `S` |
| `facets` | sides of the polygonal tube (model resolution, not cut) | 8 | 6–16 |
| `stock` | `washi-kozo-30`, `kraft-120`, `copy-80` | `washi-kozo-30` | |
| `colour` | colour of ply A (the others take the next colours) | undyed | five colours |

Modes: `yarn` (one strip), `cord` (two plies), `rope` (three plies). Presets: `fine` (6 mm strip,
30°), `kraft-twine` (kraft, 20 mm strip, 40°), `s-twist` (S twist, indigo). The strip's bias-cut
ends make an acute corner one facet wide, so the script lowers `facets` (and says so) until every
facet is at least the stock's minimum feature (1 mm); it refuses a model of more than 700 panels.

## History and sources

*Shifu* is Japanese cloth woven from paper thread. The Endangered Material Knowledge Programme
describes it as made from fine, strong paper cut into strips and rolled on a stone; the rolled
strips are separated, twisted into thread and woven («Learn about the traditional Paper Textiles of
Japan with expert Japanese weaver Kazuko Satō», 23 May 2024,
https://www.emkp.org/discover-the-traditional-paper-textiles-of-japan-with-expert-kazuko-sato/).
GetHiroshima's profile of Tsushima Textiles, on Etajima in Hiroshima Bay, says its threads are made
by twisting thin strips of paper and calls it one of only two companies in Japan that weave cloth
from paper thread («Tsushima Textiles: Weaving Paper Cloth in Hiroshima Bay», 1 November 2024,
https://gethiroshima.com/?p=40197). The cartridge credits the paper-thread tradition; it does not
simulate the shifu process (cutting, rolling on a stone, separating) and copies no maker's method
or pattern.

The S and Z letters follow the ISO 2 convention as described by Wikipedia («Rope»,
https://en.wikipedia.org/wiki/Rope: Z-twist is right-handed, S-twist left-handed; standard laid
rope has three strands; each stage is twisted opposite to the one before). Wikipedia's «Yarn»
(https://en.wikipedia.org/wiki/Yarn) also says plies are twisted together in the opposite direction
to make a thicker yarn.

A later link is planned: an internal ruling (S1) will connect sheet materials to the soft-goods
commons by material reference, so that paper thread can be used as a textile material there. This
cartridge makes no such reference yet.

## Provenance and licence

Original MADFAM geometry: the helical winding is computed by `main.py` from the development of a
cylinder. The lineage credits the paper-thread tradition of *shifu* with its sources; nothing is
copied. Published under CERN-OHL-W-2.0 like every object in the commons (see the commons root
`LICENSE`).
