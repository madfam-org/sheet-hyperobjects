# Paper circuit card · Tarjeta con circuito de papel

| | Title | Summary |
|---|---|---|
| en | Paper circuit card | A card that lights an LED from a coin cell through copper tape or conductive ink, switched by folding a tab over; flat, or folded with a box pop-up carrying the LED. |
| es | Tarjeta con circuito de papel | Una tarjeta que enciende un LED con una pila de botón a través de cinta de cobre o tinta conductora, con un interruptor que se acciona doblando una pestaña; plana, o doblada con una caja emergente que lleva el LED. |
| fr | Carte à circuit en papier | Une carte qui allume une LED grâce à une pile bouton, par du ruban de cuivre ou de l'encre conductrice, avec un interrupteur qu'on actionne en rabattant une languette ; plate, ou pliée avec une boîte pop-up qui porte la LED. |
| pt | Cartão com circuito de papel | Um cartão que acende um LED com uma pilha de botão através de fita de cobre ou tinta condutora, com um interruptor que se aciona dobrando uma aba; plano, ou dobrado com uma caixa pop-up que leva o LED. |

## What it is

A paper circuit: conductors laid on a card join a coin cell to an LED. The loop is broken at a
**fold switch**: a tab at the card's edge carries one contact, and folding the tab over presses it
onto the other contact, which closes the circuit and lights the LED. Lifting the tab opens it
again. Two modes:

- **card**: a flat card (one A6 page) with the switch tab on its left edge;
- **popup**: a folded card (two A6 pages) whose spread holds a box pop-up, cut and scored in the
  same sheet; the LED sits on the box's riser, and the traces climb onto it over the box's
  foot fold.

The slider switch from the catalogue is not included: a paper slider needs the slide mechanism,
which the studio preview cannot drive until the physics engine lands.

## Geometry

One page is `W × H = 105 × 148` mm (A6 portrait), sheet-local mm, y up. The switch tab is
35 mm wide on the left edge, between `y = 15` and `y = 50`; it folds (valley, scored) along the
page edge `u = 0`, so the front of the tab lands on the front of the page.

**The traces** (`pliego.press.trace`, spec §5.30), `width` wide (5 mm by default), all on the
front:

| Trace | Centre line | Pads |
|---|---|---|
| `plus` | (65, 115) → (65, 86) → (100, 86) | cell `plus` (10 mm) · LED `anode` (6 mm) |
| `return` | (100, 62) → (40, 62) → (40, 30) → (20, 30) | LED `cathode` (6 mm) · switch contact A (10 mm) |
| `tab` | (−20, 30) → (−20, 42) → (6, 42) → (6, 115) → (30, 115) | switch contact B (10 mm) · cell `minus` (20 mm, the cell sits on it) |

Contacts A `(20, 30)` and B `(−20, 30)` are mirror images across the tab's fold line; the tab
trace crosses that fold. Each trace's outline is its centre line stroked by the width, with
square ends.

**The pop-up** (popup mode): the spread is `2W × H` with the gutter at `u = W`. Two slits at
`y = 49` and `y = 99` run from `u = W − tread` to `u = W + riser` (`tread = 30`, `riser = 40`);
between them a foot fold (valley) at `u = 75`, a head fold (valley) at `u = 145` and a front edge
(mountain) at `u = 115`; the gutter (valley) runs outside the strip. The face between the foot
fold and the front edge is the riser, parallel to the right page; the LED pads sit on it at
`u = 100`. The `plus` and `return` traces cross the foot fold at `y = 86` and `y = 62`, inside
the strip, and never cross a slit (the script checks this).

## The fold program

The program is `kinematic` (`Sequence.kinematic_path`, six exact rigid substeps per key step).
In popup mode the card first folds shut and opens to the `angle` parameter (90° by default): the
box is a parallelogram four-bar, so every pop-up fold turns by the gutter angle, flat at 0° and
folded flat at 180°, never locked. Then, in both modes, the switch: fold the tab over (the
contacts meet), lift it, fold it over again. The tab's fold is a branch of its own, so it moves
alone.

**The switch in the document's notes.** Before building, the script runs the kernel's
continuity check, `pliego.press.circuit` (rule 30), on the traces: with the switch up there are
three nets and no loop; with the switch folded there are two nets and a loop runs from the
cell's plus through the LED, anode to cathode, through the switch to the cell's minus. It also
runs `pliego.press.fold_switch_closes`: folding the tab flat brings contact B onto contact A,
face to face on the front. Either check failing stops the build. The switch steps carry the
result in their notes ("Circuit closed (cell + → LED 'led' → switch → cell −): the LED lights",
"Circuit open"), in four languages.

**What the preview shows and what needs the physics engine.** The preview drives the whole
program: the card closing and opening, the box rising and the tab folding over. It does not
light the LED (the studio renders paper, not light) and it does not render the copper or the
ink: the traces live in the document's finishes and in the exports. The pressure that keeps the
contacts touching, the spring of the scored tab, and the tape bending over the folds are physics
the engine does not model yet.

## Making one by hand

**Parts list.** Card (250 g/m² recommended), one LED (a 3 mm or 5 mm through-hole LED, or a
flat LED sticker), one 3 V coin cell of 20 mm diameter (CR2032 size), copper tape with
conductive adhesive (5 mm wide) or a conductive-ink pen, and a piece of clear tape or a small
paper flap to hold the cell. **Not paper:** the LED, the coin cell, the copper tape (metal foil
with adhesive) and the conductive ink (a metal- or carbon-loaded ink). The card is the only
paper part.

1. Print or plot the export: cut the outline (and, for the pop-up, the two slits), score the
   folds.
2. Lay the copper tape (or draw the ink) along the centre-line layer. Where a trace turns, fold
   the tape over itself rather than cutting it; where it crosses a fold, press it down well.
3. Place the coin cell, minus side down, on the minus pad, and bring a short piece of tape from
   the plus pad onto the top of the cell (or fold a paper flap over it). The cell's two faces
   must not touch the same trace.
4. Bend the LED's legs flat: the longer leg (anode) on the anode pad of the `plus` trace, the
   shorter leg (cathode) on the cathode pad of the `return` trace. Tape them down.
5. Fold the switch tab over: the LED lights. Lift it: the LED goes out.
6. For the pop-up, fold the card shut with the box folding inside, then open it: the box stands
   up with the LED on its front.

## Parameters

| Parameter | Meaning |
|---|---|
| `material` | `copper-tape` or `conductive-ink` (the traces' material in the export) |
| `width` | trace width, 2–6 mm (5 by default) |
| `angle` | how far the pop-up card opens at the end of the program, 60°–150° (popup mode) |
| `stock` | card 250 g/m², 300 g/m² or 160 g/m² |

Presets: conductive ink with 3 mm lines; the pop-up opened to 120° on 300 g/m² card.

## History and sources

Paper circuits, copper tape, conductive ink and LEDs laid on paper, are a crafts and teaching
practice. Jie Qi and Leah Buechley built *Electronic Popables*, a pop-up book whose pages carry
circuits (2010), and later studied sketching circuits on paper (2014). The layout, the fold switch and the box here
are original to this cartridge.

- Jie Qi and Leah Buechley, "Electronic Popables: Exploring Paper-Based Computing through an
  Interactive Pop-Up Book", *Proceedings of the Fourth International Conference on Tangible,
  Embedded, and Embodied Interaction (TEI '10)*, 2010.
- Jie Qi and Leah Buechley, "Sketching in Circuits: Designing and Building Electronics on
  Paper", *Proceedings of the SIGCHI Conference on Human Factors in Computing Systems
  (CHI '14)*, 2014.
- Pliego sheet-document spec v1, §5.30 (conductive traces) and §8 rule 30 (continuity).

## Provenance and licence

Original design: the card layout, the circuit, the fold switch and the box pop-up are generated
by this cartridge with the Pliego kernel; no published template is copied. Licence
CERN-OHL-W-2.0 (both manifest fields).
