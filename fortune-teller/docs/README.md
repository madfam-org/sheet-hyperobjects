# Fortune teller · Comecocos

| | Title | Summary |
|---|---|---|
| en | Fortune teller | The paper fortune teller (salt cellar, chatterbox): two blintzes, four creases and one rigid degree-8 vertex whose mouth opens one way and then the other. |
| es | Comecocos | El comecocos (sacapiojos, salero): dos plegados al centro, cuatro marcas y un único vértice rígido de grado 8 cuya boca se abre hacia un lado y luego hacia el otro. |
| fr | Cocotte en papier | La cocotte en papier (salière, pince-mots) : deux plis des coins au centre, quatre marques et un seul sommet rigide de degré 8 dont la bouche s'ouvre dans un sens puis dans l'autre. |
| pt | Quantos queres | O quantos queres (saleiro, adivinha): duas dobras dos cantos ao centro, quatro vincos e um único vértice rígido de grau 8 cuja boca abre para um lado e depois para o outro. |

## What it is

The children's game toy: four points worked with thumbs and forefingers, opening alternately one
way and the other while a rhyme is counted, with messages hidden under the inner flaps. Standing on
its points it is the old salt cellar. The cartridge folds it from a square, shapes it and operates
it: the studio's timeline opens the mouth one way, closes it, opens it the other way and stops in the
pose you choose (`rest`).

## Geometry

The sheet is a square of side `s`, centre `O`.

- **Two blintzes.** The four corners are folded to `O` (a square of side s/√2 on the front), then
  the four new corners are folded to `O` on the back. The result is a square of side s/2 whose
  midlines and diagonals are the original sheet's.
- **Four creases through every layer.** Both midlines and both diagonals are folded and unfolded,
  so eight creases leave `O`, 45° apart, through all the layers.
- **One rigid vertex.** Each 45° sector moves as one rigid body (every layer in it), so the toy is
  a degree-8 single-vertex mechanism. With an "up" axis through `O`:
  - **Shaping** keeps fourfold symmetry. The diagonals sit at a polar angle α from the axis and
    the midlines at β, with cos 45° · sin α · sin β + cos α · cos β = cos 45° so every sector
    keeps its 45°. α runs from 90° (flat) to 0°: the four corners meet at the tip, closed.
  - **Opening one way** tilts the two north diagonals together by τ towards the north and the
    two south ones towards the south. The north and south midlines then sit at β = 45° + τ (those
    jaws stay folded flat), and the east and west midlines at β = arccos(cos 45° / cos τ), so the
    east and west fins open. Opening the other way is the same, turned a quarter.
- The closed toy is where the two openings meet, exactly as the real toy can open either way from
  closed.

## The fold program

The program is `kinematic`: the two blintzes, the four creases (each fold and unfold), six steps of
shaping, then three steps each to open one way, close, open the other way and close, and, unless
`rest` is closed, three more to the resting pose. Every state is an exact rigid state (worst
loop-closure residual about 3 × 10⁻¹³ mm). A straight blend between two neighbouring states misses
closure by up to 1.1 mm, because the vertex's motion is not linear in the fold angles; the
cartridge prints the figure.

The preview can drive the toy through the fold program's timeline. A separate `open` slider would
need either a second program or the physics engine; this is noted as an open question for the
platform.

## Making one by hand

1. Fold a square in half both ways and along both diagonals; unfold.
2. Fold the four corners to the centre.
3. Turn over and fold the four new corners to the centre.
4. Fold in half both ways again, crease firmly, unfold.
5. Slide thumbs and forefingers under the four square flaps on the back and push them together:
   the points rise and meet.
6. Move your fingers apart one way, then the other: the mouth opens one way, then the other.

## Parameters

| Parameter | Meaning |
|---|---|
| `size` | side of the square, mm |
| `mouth` | how far the jaws tilt apart when the mouth opens, 8–34° |
| `rest` | the final pose: closed, open one way, open the other way |
| `stock` | copy paper 80 g/m² or kami |

## History and sources

The Public Paperfolding History Project records the design under its older name, the Salt Cellar,
with the Pepperpot (the same model with its outside corners folded in) and later names such as
Fortune Teller, Cootie Catcher and Chatterbox. The earliest reference to a paper salt cellar it
cites is the November 1836 issue of *The Lady's Book* (Philadelphia). Wikipedia's article reports
that the historian David Mitchell found the first unambiguous picture of the fortune-teller form in
a German children's book of 1876, and that Koshiro Hatori has suggested the shape is European
rather than Japanese; its exact origin is unclear.

- The Public Paperfolding History Project, "The salt cellar":
  https://origamiheaven.com/historyofthesaltcellar.htm
- "Paper fortune teller", Wikipedia: https://en.wikipedia.org/wiki/Paper_fortune_teller

## Provenance and licence

Geometry generated by this cartridge with the Pliego kernel; credited to tradition. Licence
CERN-OHL-W-2.0 (both manifest fields).
