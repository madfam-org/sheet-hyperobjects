# Paper bridge under load

| | Title | Summary |
|---|---|---|
| **en** | Paper bridge under load | A strip of paper spans a gap and a weight is let go over its middle. Flat, the strip gives way; folded into a channel, the same paper carries the weight. |
| **es** | Puente de papel con carga | Una tira de papel cruza un claro y se suelta un peso sobre su centro. Plana, la tira cede; doblada en canal, el mismo papel sostiene el peso. |
| **fr** | Pont de papier sous charge | Une bande de papier franchit un vide et l'on lâche un poids en son milieu. À plat, la bande cède ; pliée en gouttière, le même papier porte le poids. |
| **pt** | Ponte de papel com carga | Uma tira de papel atravessa um vão e solta-se um peso sobre o meio. Plana, a tira cede; dobrada em calha, o mesmo papel sustenta o peso. |

## What it is

A load test you can run in the browser. A strip of copy paper (or light card) rests across the gap
between two supports, like a sheet laid between two stacks of books. A small square of 1.5 mm
greyboard is held above the middle of the span and then let go. The section parameter changes only
the shape of the strip: flat, or with its two long edges folded up into walls. The paper, the span,
the supports and the weight stay the same, so whatever difference you see comes from the folds.

## Geometry

The strip is a rectangle `span + 40` mm long (a 20 mm bearing rests on each support) and `width` mm
wide, grain along its length. Its walls are two valley folds along the full length:

| `section` | Wall height (each side) | Deck between the walls |
|---|---|---|
| `flat` | none | the full width |
| `channel` | a fifth of the width | three fifths of the width |
| `deep-channel` | three tenths of the width | two fifths of the width |

The supports are two 60 mm greyboard boards whose tops sit 60 mm above the table; the strip lies on
them. The weight is a greyboard square of side `weight_size` (made smaller if it would not fit
between the walls), centred over the middle of the span, 4 mm above the deck.

## The load test

The fold program has up to three steps, played by the physics engine:

1. **Fold both walls up** (channel sections only): the two valley folds go to 90°.
2. **Let go of the weight**: the pin that held the weight is untied (sheet-document §5.20) and it
   falls onto the deck.
3. **Watch the bridge carry it**: nothing is driven; gravity, contact with friction and the two
   supports decide where the strip and the weight come to rest.

A second control, **Move the right support out**, slides the right-hand board up to 15 mm away
from the gap, so the strip's bearing shrinks while it carries the weight.

Nothing in this model is scripted to bend: the strip rests on its supports by contact, so it can slide
in as it sags, the way a sheet laid across two books does. Measured with the studio's engine settings
(defaults, copy paper 80 g/m², span 180 mm, width 60 mm, weight 30 mm): with the `flat` section the
strip gives way and the weight ends on the table; with the `channel` section the deck comes to rest
about 4.5 mm below the supports and holds the weight (deep channel: about 4 mm).

**Honest limits.** The engine's membrane is softer than real paper in tension (a deliberate cap for
numerical stability, documented in the engine), the walls are folded by a hand drive, and the heavy
weight presses on light paper through position-level contact. Together they stretch the paper locally:
about 8 % at the peak and 3–6 % at rest for the channel sections in the engine of 2026-10-18
(more in the deep channel while it folds), against the 0.5 % real paper allows. The simulation matrix
therefore counts these documents as stretched; the sag numbers above are what the model shows, not
a laboratory measurement. The weight's mass comes from the greyboard stock card, which is an
engineering estimate (1100 g/m²).

## Why the folds help

A strip resists bending through its bending stiffness, E·I, where I, the second moment of area of
its cross-section, grows with the cube of the depth. A flat strip of copy paper is about 0.1 mm deep;
a channel with 12 mm walls puts most of the same paper far from the bending axis, which raises I by
several orders of magnitude for the same weight of paper. Folded plates, corrugated board and
sheet-metal channels use the same idea.

## Making one

1. Cut a strip 220 × 60 mm from copy paper, grain along its length.
2. Score and fold two valley folds 12 mm in from each long edge, and stand the walls up at 90°.
3. Lay the strip across two stacks of books 180 mm apart, 20 mm resting on each.
4. Set a coin or a small square of board in the middle. Try the same strip flat for comparison.

## Parameters

| Parameter | Meaning | Default |
|---|---|---|
| `section` | `flat`, `channel`, `deep-channel` | `channel` |
| `span` | distance between the supports (mm), 100–260 | 180 |
| `width` | strip width (mm), 40–90 | 60 |
| `stock` | `copy-80`, `cardstock-160` | `copy-80` |
| `weight_size` | side of the greyboard weight (mm), 20–40 | 30 |

Presets: **Flat strip (it sags)**, **Deep channel**, **Long span in cardstock** (240 mm).

## History and sources

- Beam bending as used here (stiffness E·I, deflection of a simply supported beam) is
  Euler–Bernoulli beam theory, developed in the 18th century: Wikipedia, «Euler–Bernoulli beam
  theory», https://en.wikipedia.org/wiki/Euler%E2%80%93Bernoulli_beam_theory
- The second moment of area and its growth with section depth: Wikipedia, «Second moment of area»,
  https://en.wikipedia.org/wiki/Second_moment_of_area
- The physics that runs the test: Pliego engine (`docs/strategy/engine.md`) and the sheet-document
  spec v1, §5.3 (joins) and §5.20 (untying a join at a step).

## Provenance and licence

Original MADFAM design: the geometry is generated by this cartridge's `main.py`. Folding a paper
strip into a channel to make it carry a load is a general classroom demonstration of bending
stiffness and is credited to that practice, not to a designer. Licence: CERN-OHL-W-2.0.
