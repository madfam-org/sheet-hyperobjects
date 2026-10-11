# Ofrenda pop-up

| | Title | Summary |
|---|---|---|
| en | Ofrenda pop-up | A Día de Muertos ofrenda as a 90° pop-up card: an altar of two to seven levels with candles, pan de muerto and a photo frame, cut from the card itself, under an arch of kirigami cempasúchil and a papel picado banner. |
| es | Ofrenda en pop-up | Una ofrenda de Día de Muertos en una tarjeta pop-up de 90°: un altar de dos a siete niveles con velas, pan de muerto y un marco para la foto, cortado de la propia tarjeta, bajo un arco de cempasúchil de kirigami y una tira de papel picado. |
| fr | Ofrenda en pop-up | Une ofrenda du Jour des morts en carte pop-up à 90° : un autel de deux à sept gradins avec bougies, pain des morts et cadre pour la photo, découpé dans la carte elle-même, sous un arc de roses d'Inde en kirigami et une guirlande de papel picado. |
| pt | Oferenda em pop-up | Uma oferenda do Dia dos Mortos num cartão pop-up de 90°: um altar de dois a sete níveis com velas, pão dos mortos e uma moldura para a foto, cortado do próprio cartão, sob um arco de cravos-de-defunto em kirigami e um varal de papel picado. |

## What it is

For Día de Muertos, families in Mexico set up an ofrenda. On a stepped altar they place candles,
cempasúchil (marigold) flowers, bread, favourite foods and photographs of the people they
remember, under papel picado. This cartridge is a pop-up card of that altar. Open it to 90° and
the levels rise from the corner where the back page (the wall) meets the floor page:

- candles stand at the foot of every level and against the wall on top;
- a round loaf sits on the step below the top level;
- an empty frame on the top level is left for a photograph;
- kirigami cempasúchil open in an arch on the wall;
- a banner of tissue papel picado flags hangs across the top.

The ofrenda is a living tradition, and this design honours it as a tradition. Every element is a
generic shape (levels, candles, a loaf, an empty frame, flowers, cut-paper flags), and the design
is original. It has no skulls and no characters, and it leaves the personal part, the photograph
and what goes on the altar, to whoever makes it.

The composition uses three mechanisms:

- the cut-and-fold step of [`step-popup`](../../step-popup/docs/README.md) (kernel builder
  `pliego.popup.cut_fold`);
- the fold-and-cut flags of [`papel-picado-banner`](../../papel-picado-banner/docs/README.md)
  (kernel builder `pliego.foldcut.papel_picado`);
- kirigami flowers drawn in this cartridge.

No cartridge's script is copied.

## Geometry

**The card.** One sheet of `card_width` × 2·`page_height`: the wall, then the floor, joined at the
gutter (a valley fold). Displayed at 90°, the wall stands upright and the floor lies in front of
it.

**The altar** is a cut-fold tree across the gutter. Each piece is a *block*: two slits and three
folds A, F and B that stand up as a box when the corner opens.

| piece | cut into | size | notes |
|---|---|---|---|
| level 1 | the gutter | height `tier_height`, depth `depth`, width 0.82 × `card_width` | |
| level k + 1 | level k's back corner (fold A, where its top meets the wall) | one `tier_height` higher, narrower, shallower | each level leaves a tread of `depth`/`levels` in front of the next |
| candles | the corner at the foot of each level (fold B), two per level; against the wall on the top level | | the flame is a crest that continues the candle's front past its top |
| pan de muerto | the foot of the top level | | a round dome with a small knob, also a crest |
| photo frame | the top level, against the wall | | a shallow box whose front has a window |

Nested in its parent's corner, each child is narrower than the parent. The parent's fold keeps
uncut ends, so every level stays square. Candles, the loaf and the frame are left out when a level
is too small for them; `main.py` prints how many it made.

**The marigolds** are glued to the wall. Each has two orange discs, stacked and glued at the centre.
On each disc, round-tipped petals are cut on three sides and scored at their base. The outer disc
has 10 petals, folded out 50°; the inner disc has 7, folded out 75°. On a small card the discs
shrink, with fewer petals or one disc only, to keep every bridge and face at the card's minimum
feature. The flowers form a half-ellipse over the altar, evenly spaced, and each one is glued on
uncut wall, clear of the altar's cuts.

**The banner.** `flags` flags of papel de china hang along one line 6 mm below the top of the wall.
Each flag is folded in half and cut through both layers: an original flower rosette or a diamond
lattice, with a picos (zigzag) fringe. It is checked to stay in one piece with every bridge at least
1.5 mm, then ironed flat. Its top strip folds back over the string and is glued down (`glue` join on
its own back), and every flag is pinned along that line (`pin` joins: "pins on a line"). The wall's
top edge is pinned too, so the card and the banner share one frame.

`main.py` fails loud unless:

- every altar state closes (closure residual below 1e-6 mm);
- the card, every flower disc and every flag pass `pliego.papercut.analyze` at their minimum
  feature (1.5 mm for 160 g/m² card and tissue, 2 mm for 250 g/m² card);
- every flower sits on uncut wall, and the flowers and the banner fit above the altar.

## The fold program

Every fold of the altar turns by the gutter angle (A and B folds with it, F folds against it), so
every state is rigid, and a linear blend of the angles is exact. The petals are free hinges.

The initial frame is the open card: altar standing, flowers open, banner hung. The kinematic program
then runs four steps:

1. **Press the marigolds flat.**
2. **Close the card.** The gutter goes to 176°, and every level, candle and the frame folds flat
   between the pages.
3. **Open the card to 90°.** The levels rise.
4. **The marigolds open.**

The sequence control starts at the end, with the ofrenda open.

**Preview and engine.** The studio preview plays the whole program, because the wall is held still:

- the altar is part of the card's own fold tree;
- each flower disc is glued to the wall (or to the disc below it), so its petals turn about
  creases on a sheet that does not move;
- the flags hang on the wall.

What needs the physics engine:

- the glue and the pins;
- the tissue flags' drape and flutter;
- the petals being pressed flat by the closing card. In the preview they fold flat first, as a
  step.

## Making one by hand

1. Export the card, the flowers and the flags (`svg`, `dxf`, `pdf` or `hpgl`). Cuts and slits are
   on the cut layer, folds on the score layer. Cut the flags from tissue paper, the flowers from
   orange card, and the card from cream card.
2. Score every fold of the card, then cut the slits, the frame's window and the flame and loaf
   outlines.
3. Fold the card shut along the gutter, folding every level, candle and the frame inward along its
   own scores. Then open it to 90° and push each piece into shape the first time.
4. Score each flower's petal bases, cut the petals, glue the inner disc onto the outer one at the
   centre and the pair onto the wall, then lift the petals.
5. Lay a thread across the top of the wall, fold each flag's top strip over it and glue it down.
   Tie the thread off at the sides.
6. Put a photograph in the frame.

## Parameters

| id | meaning | default | range |
|---|---|---|---|
| `card_width` | length of the gutter | 180 mm | 140–240 mm |
| `page_height` | wall height and floor depth | 170 mm | 140–240 mm |
| `stock` | `cardstock-160` or `cardstock-250` | `cardstock-160` | |
| `levels` | levels of the altar | 3 | 2–7 |
| `tier_height` | height of each level | 22 mm | 10–30 mm |
| `depth` | depth of the bottom level | 72 mm | 36–120 mm |
| `flowers` | marigolds in the arch (0 for none) | 7 | 0–11 |
| `flags` | papel picado flags | 5 | 3–6 |
| `picado` | `alternate`, `flower` or `lattice` | `alternate` | |

Presets: `two-levels`, `seven-levels` (on a 200 × 190 mm card) and `small-card` (150 mm, five
flowers, four flags).

## History and sources

UNESCO inscribed the Indigenous festivity dedicated to the dead on the Representative List of the
Intangible Cultural Heritage of Humanity in 2008 (proclaimed in 2003). Its description:

- families lay flower petals, candles and offerings along the path from the cemetery to the home;
- the dead person's favourite dishes go on the home altar and the tomb, alongside flowers and
  handicrafts such as paper cut-outs.

Source: UNESCO, «Indigenous festivity dedicated to the dead»,
https://ich.unesco.org/en/RL/indigenous-festivity-dedicated-to-the-dead-00054.

Ofrendas are commonly described with two, three or seven levels. The meanings given to the levels
vary from one account to another: heaven and earth for two; earth, heaven and the underworld, or
the Trinity, for three (Infobae México, «Altar de muertos: qué representan los 7 niveles», 2022,
https://www.infobae.com/america/mexico/2022/10/25/altar-de-muertos-que-representan-los-7-niveles/).
The cartridge offers those counts and claims no single meaning.

The cempasúchil (*Tagetes erecta*) takes its name from the Nahuatl *cempohualxochitl*. In Mexico it
decorates altars and tombs at Día de Muertos, hence its name «flower of the dead» (Wikipedia,
«Tagetes erecta», https://en.wikipedia.org/wiki/Tagetes_erecta).

Papel picado, the cut tissue banner of these altars, is credited to the papercut tradition of San
Salvador Huixcolotla, Puebla, which INAH recognised as cultural heritage in 1998 (México
Desconocido, «Papel picado de Huixcolotla»,
https://www.mexicodesconocido.com.mx/papel-picado-huixcolotla.html; Wikipedia, «Papel picado»,
https://en.wikipedia.org/wiki/Papel_picado).

The cut-and-fold pop-up comes from origamic architecture (Wikipedia, «Origamic architecture»,
https://en.wikipedia.org/wiki/Origamic_architecture).

Every motif and shape in this cartridge is original. No artisan's papel picado or published pop-up
is reproduced.

## Provenance and licence

Original MADFAM design: the altar, the candles, the loaf, the frame, the flowers, the flag motifs
and every angle are generated by `main.py` with the kernel's `cut_fold` and `papel_picado`
builders. The ofrenda is credited to the living tradition of Día de Muertos, and papel picado to San
Salvador Huixcolotla, Puebla. Published under CERN-OHL-W-2.0, like every object in the commons (see
the commons root `LICENSE`).
