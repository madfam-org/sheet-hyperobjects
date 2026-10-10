# Tab and slot

| | |
|---|---|
| **en** | Two slotted cards, turned a quarter turn to each other, slide together into a standing cross held only by contact — no glue. |
| **es** | Dos tarjetas ranuradas, giradas un cuarto de vuelta entre sí, se deslizan una en otra hasta formar una cruz de pie que solo sostiene el contacto, sin pegamento. |
| **fr** | Deux cartes fendues, tournées d'un quart de tour l'une par rapport à l'autre, s'emboîtent en une croix debout tenue par le seul contact, sans colle. |
| **pt** | Dois cartões com fenda, girados um quarto de volta um em relação ao outro, encaixam-se numa cruz de pé sustentada só pelo contato, sem cola. |

## The technique

A **slot joint** (here the crossed, half-lap form) joins two flat parts without glue. Each card
has a straight slit on its centre line: card A from the middle of its top edge down, card B from
the middle of its bottom edge up. `slit_ratio` of the height is slotted on card A and the rest on
card B, so the two slits always end at the same height.

Turn card B a quarter turn about the vertical and push it down onto card A: B's slit runs over
the solid lower part of A while A's slit runs over the solid upper part of B. When the slit ends
meet, each card passes through the other along the whole height, the top and bottom edges are
flush, and the pair stands on its four bottom edges as a cross.

**What holds it.** Nothing but contact. Each card can only leave the other by sliding back along
the slits, and gravity presses B's slit end onto A's; any rotation is blocked because each card
sits inside the other's slit. The `slot` (card A) and `tab` (card B) interfaces name this pair
with complementary polarity — the solid half of each card is the tab that enters the other's slot.

## Fabrication

- **Stock.** `cardstock-250` by default; `cardstock-300` for a stiffer stand, `cardstock-160`
  for small cards.
- **Cut** the two cards and their slits. A slit cut with a single blade stroke is tight; for heavy
  card cut a narrow slot instead — about the card's thickness (0.3 mm for 250 g/m²) up to twice it
  for an easy fit.
- **Assemble** by turning card B a quarter turn, aligning the slit mouths and sliding B down until
  the edges are flush. It comes apart the same way.

## What the engine simulates

The sheet document holds two physical sheets with one `C` cut each, from an edge to the meeting
point. There are no joins and no mechanisms: the cards are placed rigidly — card A standing in the
plane z = 0, card B in the plane x = 0, both on the ground — so that in the `initial` frame the two
slits lie on the cards' common line and meet. From there the engine's paper physics and contact
take over: gravity and the contact between the cards are what keep the cross standing.

Honest limit: in sheet-document v1 a cut's two sides share their vertices, so a slit has no width
in the model. The cards therefore touch along the slit lines at t = 0 instead of resting in a slot
with clearance; the cut file carries the slit as a single line.

**Verified for this cartridge** (widths and heights 50/125/200 mm, slit ratios 0.25–0.75, all
three stocks: 135 documents): `verify` errors = 0; the cut layer carries each outline and its slit
as one line. The script checks that both slits lie on the cards' common line
(|x|, |z| ≤ 1e-9 mm), meet at the same height and together span the card from the ground to its
top edge, and fails otherwise.

## Parameters

| id | meaning | range |
|---|---|---|
| `card_width` | width of each card | 50–200 mm |
| `card_height` | height of each card | 50–200 mm |
| `slit_ratio` | share of the height slotted on card A (card B takes the rest) | 0.25–0.75 |
| `stock` | card | cardstock 160 / 250 / 300 g/m² |

## Interfaces

- `slot` (female) — card A's slit, from its top edge.
- `tab` (male) — card B's complementary slit, from its bottom edge.

Both carry a frame in the assembled state: the slit mouth, the card's normal and the slit
direction.

## Provenance

Original MADFAM geometry, computed in this cartridge's `main.py`. Interlocking slotted cards are a
general technique of paper and card construction and are credited to that tradition, not to a
designer.
