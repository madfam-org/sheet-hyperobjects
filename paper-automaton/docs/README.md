# Paper automaton

| | Title | Summary |
|---|---|---|
| en | Paper automaton | A cam-and-crank automaton box in card: the handle turns a cam that lifts a follower through the lid, and a bird on top bobs. Snail, eccentric or egg cam, with a cut-and-score net for every part. |
| es | Autómata de papel | Una caja autómata de leva y manivela en cartulina: la manivela gira una leva que levanta un seguidor a través de la tapa, y un pájaro arriba se balancea. Leva de caracol, excéntrica o de huevo, con plantilla para cortar y marcar de cada pieza. |
| fr | Automate en papier | Une boîte automate à came et manivelle en carte : la manivelle tourne une came qui soulève un poussoir à travers le couvercle, et un oiseau perché dessus hoche. Came en escargot, excentrique ou en œuf, avec un gabarit à découper et rainer pour chaque pièce. |
| pt | Autômato de papel | Uma caixa autômata de came e manivela em cartão: a manivela gira um came que levanta um seguidor através da tampa, e um pássaro em cima balança. Came caracol, excêntrico ou ovo, com molde para cortar e vincar de cada peça. |

## What it is

A card automaton is a small machine in a box: a handle turns a shaft, a cam on the shaft pushes a
follower, and a figure on the follower moves. This one is an original MADFAM design: a box with
windows in its sides, a shaft (a bamboo skewer) through the front and back walls, a cam inside, a
follower rising through a slot in the lid, and a bird on top that bobs. Two modes:

- **`automaton`**: the assembled box, driven by the `crank` control.
- **`nets`**: every part flat, ready to cut and score: the box, three cam layers, two handle
  layers, two follower layers and two shaft collars. Its program folds the box.

The cam's shape (`profile`) decides the bird's motion:

- **`snail`**: an Archimedean spiral with a drop. The bird rises steadily through a whole turn,
  then falls at once. It must be turned one way only: turned backwards, the drop jams the follower.
- **`eccentric`**: a disc set off-centre on the shaft. The bird rises and falls smoothly, once a
  turn.
- **`egg`**: a round cam with one longer end. The bird rests low for most of the turn and bobs up
  quickly when the long end passes.

## Geometry

The box is 90 × 70 mm with a `box_height` (85 mm); the shaft runs front to back 32 mm above the
table. The cam's smallest radius is 14 mm and its `lift` is up to 14 mm, so it always clears the
table. Its radius along each direction φ of the cam is:

- snail: *r* = 14 + `lift` × ((90° − φ) mod 360°) / 360°;
- eccentric: a disc of radius 14 + `lift`/2 whose centre is `lift`/2 above the shaft;
- egg: *r* = 14 + `lift` × ((1 + cos(φ − 90°)) / 2)³.

The follower is a strip 8 mm wide with a pointed foot (a knife edge) straight above the shaft.
The cam turns counter-clockwise seen from the front, so at crank angle θ the foot rests on the
cam's radius at φ = 90° − θ: the follower's height is *h*(θ) = *r*(90° − θ). For the snail that is
14 + `lift` × θ/360°, linear in the crank. The script computes the pressure angle (the angle
between the follower's line and the cam's normal) round the turn and refuses a cam above 35°; at
the default lift the snail reaches 7.8°, the eccentric 17.5° and the egg 24.8°.

The bird is an original silhouette (an elliptical body, a round head with a beak, a tail) drawn in
one piece with the follower. The box net is four walls in a row with a glue tab, and a lid on the
back wall with a tuck flap; the corners are valley-scored from inside (mountain seen from the
outside), the front and back walls have holes for the skewer, the side walls have windows, and the
lid has a slot for the follower. The cam, handle and collars are pierced at the centre for the
skewer.

## The mechanism and the fold program

- **`automaton`**: the cam and the handle are kinematic sheets on `rotate` mechanisms about their
  own centres, and the shaft on a `hinge` about its axis, all on the `crank` control (0–360°).
  The follower rides a `translate` mechanism on the same control. With the snail it moves
  linearly (travel `lift` over 360°), which is exactly *h*(θ). With the eccentric or the egg,
  *h*(θ) rises and falls; the `translate` is then **keyed** (sheet-document spec §5.18): a `keys`
  table maps the crank angle to the displacement *h*(θ) − *h*(0), with `period: 360`, so it repeats
  every turn and the closing segment runs back to the first key. The keys start every 5° and are
  refined until the foot stays within 0.05 mm of the cam between keys (0.007 mm for the eccentric,
  0.013 mm for the egg, both at 5°). The follower starts where the cam holds it at crank 0. The
  studio preview and the physics engine evaluate the same table: measured over a turn in 2.5°
  steps, the foot stays 0.007 mm (eccentric) and 0.013 mm (egg) from the top of the cam in both.
  Before the keys, these followers were physical sheets left to ride the cam under gravity; the
  preview left them at the top of the stroke (12 mm and 9 mm off the cam) and in the engine they
  fell off it. Twelve `target:crank-000` … `target:crank-330` frames record the exact solved pose
  every 30° for every profile.
- **`nets`**: fold the four walls into a ring, fold the tab inside, close the lid and tuck its
  flap.

The box's scores carry a 90° rest angle (they are pre-creased), and its tab is glued, so it keeps
its shape in the physics engine.

## Making one by hand

1. Export the nets (`svg`, `dxf`, `pdf` or `hpgl`) and cut them out; score the box's lines.
2. Glue the three cam layers together, and the two handle layers, and the two follower layers:
   laminated card is stiff enough to push and to be pushed.
3. Fold the box and glue the tab inside; close the lid.
4. Push a bamboo skewer through the front wall, a collar, the cam, a collar and the back wall;
   glue the cam to the skewer with its drop (or its high point) facing up when the handle points
   right, and glue the collars against the walls so the shaft cannot slide.
5. Glue the handle to the skewer outside the front wall, and a short piece of skewer into its end
   as a knob.
6. Drop the follower through the lid's slot onto the cam, and turn the handle.

## Parameters

| id | meaning | default | range |
|---|---|---|---|
| `profile` | `snail`, `eccentric` or `egg` | `snail` | |
| `lift` | how far the cam raises the bird | 12 mm | 6–14 mm |
| `handle_length` | crank radius of the handle | 30 mm | 20–45 mm |
| `box_height` | height of the box | 85 mm | 70–120 mm |

Presets: `eccentric-bob`, `egg-nod`, `tall-box`.

## History and sources

- A cam is a rotating piece that turns rotary motion into the linear motion of a follower; an
  eccentric disc gives the follower a smooth back-and-forth motion, and snail drop cams drove the
  day advance of clocking-in clocks (Wikipedia, «Cam (mechanism)»,
  https://en.wikipedia.org/wiki/Cam_(mechanism)).
- Cams have driven automata for centuries: al-Jazari's thirteenth-century musical automaton used a
  drum of pegs (cams) bumping levers (Wikipedia, «Automaton», https://en.wikipedia.org/wiki/Automaton).

The box, the cam laws, the follower and the bird are this cartridge's own; no published kit is
copied.

## Provenance and licence

Original MADFAM design: every part is generated by `main.py`. Published under CERN-OHL-W-2.0 like
every object in the commons (see the commons root `LICENSE`).
