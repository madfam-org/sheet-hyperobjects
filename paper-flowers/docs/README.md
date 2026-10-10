# Paper flowers

| | Title | Summary |
|---|---|---|
| en | Paper flowers | Tissue-paper flowers on rolled paper stems, two ways: a carnation made like a small pom-pom, and a cut-petal flower whose strip of petals is wound round the stem. Each is made step by step, exactly; the carnation's bloom, which crushes the tissue, is a reference frame. |
| es | Flores de papel | Flores de papel de china sobre tallos de papel enrollado, de dos maneras: un clavel hecho como un pompón chico y una flor de pétalos recortados cuya tira de pétalos se enrolla alrededor del tallo. Cada una se hace paso a paso, de forma exacta; la apertura del clavel, que aplasta el papel, es un marco de referencia. |
| fr | Fleurs en papier | Des fleurs en papier de soie sur des tiges de papier roulé, de deux façons : un œillet fait comme un petit pompon, et une fleur à pétales découpés dont la bande de pétales s'enroule autour de la tige. Chacune se fait pas à pas, exactement ; l'épanouissement de l'œillet, qui écrase le papier, est un cadre de référence. |
| pt | Flores de papel | Flores de papel de seda sobre caules de papel enrolado, de duas maneiras: um cravo feito como um pompom pequeno e uma flor de pétalas recortadas cuja tira de pétalas se enrola em volta do caule. Cada uma é feita passo a passo, de forma exata; a abertura do cravo, que amassa o papel, é um quadro de referência. |

## What it is

*Flores de papel*: flowers of tissue or crepe paper, on altars, at weddings, at fiestas and on Día
de Muertos. This cartridge is the family of tissue flowers on a rolled paper stem, in two modes:

- `carnation`: a few layers of tissue pleated together like a fan, their ends trimmed pointed or
  round, tied at the centre onto the stem, then pulled up into a bloom — the technique of the
  tissue pom-pom made small, with fewer and smaller layers;
- `cut-petal`: a strip of tissue cut into a row of petals along one edge, each petal curled, the
  strip wound round the top of the stem and the petals opened outward.

Both are made step by step, from flat paper to the flower standing on its stem.

## Geometry

**The stem.** A strip of kraft (41.4 × 180 mm by default) rolled straight into a tube on a thin core
(a skewer or a wire, 2 mm radius). Its `F` lines run along the stem, 1.8 mm apart, and fold by the
exterior angles of a polygonal spiral whose radius grows by the paper's thickness plus 0.1 mm of air
per turn: 2.5 turns, about 5.6 mm across. The roll is an exact isometry, several layers thick.

**The carnation.** `sheets` layers of papel de china (4 by default, 200 × 120 mm) lie one caliper
apart. Each carries pleat lines across its length, rounded to a whole number (17 pleats of 11.8 mm by
default), alternately valley and mountain (treatment `crease`), and a tie line along its middle (an
`F` line, plain paper). The ends are trimmed through every layer at once, pointed (pinked) or round,
so the outline is cut to that shape from the start (the same paper as trimming the folded stick).
Pleating is rigid: the lines are parallel. The bloom is not. A pleated layer whose panels stay flat
cannot fan out from the tie; the real bloom bends and crushes the tissue (the tissue pom-pom's
article explains why). So `target:bloom` is the closest exact state: every pleat closed flat and
every layer folded at the tie so that both its halves lift upward, away from the stem, the bottom
layer least: layer k of N lifts by (k + ½)·90°/N (11°, 34°, 56° and 79° for four layers).

**The cut-petal flower.** A strip of papel de china (121.5 × 49 mm by default) with a 14 mm base band
and a row of petals along its top edge, 4.5 mm apart with a 1.6 mm notch between them (so each
petal is 2.9 mm wide and 35 mm long, with a round or pointed tip). The base band is wound round the
top of the stem like the stem itself: `F` lines across the strip at every petal, folded by the
exterior angles of a polygonal spiral that grows 1 mm per turn (tissue gathers loosely): four turns,
27 petals. Each petal is hinged along its base panel's top edge (an `F` line) and has two more `F`
lines across it, so it can lift and curl. The notches mean every line ends on the outline or at the
end of another line: there is no interior vertex, and every fold is free. The petals open more on
the outer turns (8° at the centre to 60° at the edge) and curl outward by two folds of 8° to 20°.

The script checks that every pose keeps every edge length, that the rolls are valley rolls, that
every petal opens outward, and that the trimmed layers, the petal strip and the stem pass
`pliego.papercut.analyze` (1.5 mm for papel de china, the stem paper's own minimum). Every `F` line
is plain paper (treatment `none`): not scored, not on the cut file.

## The fold program

Both modes are `kinematic` programs. The lines never cross, so every step is an exact rigid motion.

`carnation`: roll a strip of kraft into a stem; pleat the stack of tissue like a fan (90°); press it
into a narrow stick on top of the stem (178°: the layers have thickness). The last step's note says
to wind wire round the middle and onto the stem and to pull the layers up; the pulled-up state is the
frame `target:bloom`. The program ends in `target:pleated`.

`cut-petal`: roll the stem; curl each petal outward; wind the strip round the top of the stem; open
the petals outward. It ends in `target:flower`.

The `initial` frame holds each sheet flat where its first face sits in the finished flower (the
studio preview keeps that face still), so the tissue starts flat in the air and the stem strip
stands beside it: the flower then builds itself upright on its stem.

**Preview and engine.** The studio preview plays both programs exactly: the end pose equals
`target:pleated` and `target:flower`. What needs the physics engine: the carnation's bloom (fanning
bends and crushes the tissue; `target:bloom` is a reference, not a state the program reaches), the
wire or glue that holds each flower together (described in the notes, not modelled as joins), and
crepe paper's stretch — there is no crepe-paper stock card, so the tissue is papel de china.

## Making one by hand

1. **Stem.** Roll a strip of kraft tightly round a skewer or a wire, from one long edge, and glue the
   last edge.
2. **Carnation.** Stack the layers, fold them like a fan into a narrow stick, trim both ends pointed
   or round, and wind thin wire round the middle and down onto the stem. Fan the two halves out, then
   lift the layers one by one toward the top.
3. **Cut-petal flower.** Cut the petal strip (or export it as a template), curl each petal over a
   pencil or between your fingers, glue one end to the top of the stem and wind the strip round it,
   petals up, gluing the last end. Open the petals outward, the outer ones most.

Tissue is thin: curl and lift it gently.

## Parameters

| id | meaning | default | range |
|---|---|---|---|
| `colour` | flower colour | pink | marigold, yellow, pink, red, white, purple |
| `stem_length` | stem length | 180 mm | 80–300 mm |
| `stem_stock` | `kraft-120` or `cardstock-160` | `kraft-120` | |
| `sheets` | carnation: tissue layers | 4 | 3–6 |
| `sheet_length` | carnation: the side that gets pleated | 200 mm | 120–300 mm |
| `sheet_width` | carnation: the other side (about the flower's diameter) | 120 mm | 80–200 mm |
| `pleat` | carnation: pleat width, rounded to fit | 12 mm | 8–25 mm |
| `ends` | carnation: `pointed` or `round` | `pointed` | |
| `petal_height` | cut-petal: petal length | 35 mm | 20–60 mm |
| `petal_width` | cut-petal: petal pitch (petal + 1.6 mm notch) | 4.5 mm | 3.5–10 mm |
| `turns` | cut-petal: turns of the strip round the stem | 4 | 2–6 |
| `tip` | cut-petal: `round` or `pointed` petal tips | `round` | |

Presets (applied to both modes): `marigold` (marigold orange, pointed), `big-bloom` (six larger
layers, longer petals, a 250 mm stem), `white-round` (white, round, card stem).

## History and sources

The Mexican Folk Art Guide («Mexican Paper Flowers»,
https://www.mexican-folk-art-guide.com/mexican-paper-flowers.html) describes Mexican paper flowers
as made of tissue or crepe paper, says that papel de China came from Asia on the Manila galleons and
that by the 17th century it was being shaped into flowers, flags and festival ornaments, and names
their uses: altars, weddings, festivals, religious processions and Día de Muertos. México
Desconocido (Arturo Cuevas, «El papel china sí proviene de China, conoce cómo llegó a México»,
https://www.mexicodesconocido.com.mx/papel-china.html) adds giant flowers at patron-saint fiestas and
flowers and garlands at weddings and quinceañeras. N+ («¿Cómo hacer flores de cempasúchil de papel
crepé?», 16 October 2023,
https://www.nmas.com.mx/cultura/como-hacer-flores-de-cempasuchil-de-papel-crepe-china-facil-y-rapido/)
gives a method for crepe-paper cempasúchil for Día de Muertos: fold the sheet, staple the centre, cut
a circle, cut petals and separate the layers upward.

What this cartridge takes from them, and what it adds: the credit (paper flowers as a Mexican
celebration craft) and the general technique (layers gathered at the centre and lifted; petals cut
and shaped). The two specific constructions — the pleated carnation and the wound petal strip — and
their geometry are this cartridge's own, chosen because every step can be modelled exactly; the
N+ method (stacked discs with petals) is described here, not modelled. No artisan's design or
published template is copied.

## Provenance and licence

Original MADFAM geometry. The lineage credits Mexican paper flowers and the method sources above.
Published under CERN-OHL-W-2.0 like every object in the commons (see the commons root `LICENSE`).
