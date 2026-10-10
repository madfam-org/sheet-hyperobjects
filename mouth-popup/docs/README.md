# Mouth pop-up

| | Title | Summary |
|---|---|---|
| en | Mouth pop-up | The talking mouth: one slit and six scored folds in a card make two lips that open and shut with the card. One sheet, no glue. |
| es | Pop-up de boca | La boca que habla: un corte y seis dobleces hendidos en una tarjeta forman dos labios que se abren y se cierran con ella. Una sola hoja, sin pegamento. |
| fr | Pop-up bouche | La bouche qui parle : une fente et six plis rainés dans une carte forment deux lèvres qui s'ouvrent et se ferment avec elle. Une seule feuille, sans colle. |
| pt | Pop-up de boca | A boca que fala: um corte e seis dobras vincadas num cartão formam dois lábios que se abrem e se fecham com ele. Uma só folha, sem cola. |

## What it is

The talking mouth is a cut-and-fold pop-up children make in a few minutes: fold a card, cut one
slit in from the fold, fold the two flaps back into triangles, unfold them and push them through to
the inside. Open the card and the triangles become a pair of lips, or a beak, that open; close it a
little and they shut. Draw a face around it and the card talks.

## Geometry

The card is a spread of two pages, `page_width` × `page_height` each, with the gutter at
u = `page_width`. The mouth is a slit of length `mouth_width` across the gutter, at
`mouth_position` of the card's height. Each lip is bounded by the slit and two diagonal folds that
meet on the gutter at a point P, `upper_lip` above the slit for the upper lip and `lower_lip` below
it for the lower. Between P and the slit, the gutter is folded the other way: that short mountain is
the lip's ridge.

P is a **degree-4 vertex**: the gutter beyond P (valley), the ridge (mountain, in line with the
gutter) and the two diagonals (valleys). With θ the angle between a diagonal and the slit, the
sectors around P are 90° + θ, 90° + θ, 90° − θ and 90° − θ. Opposite sectors add up to 180°, so the
vertex folds flat (Kawasaki), and it moves on its mode-1 branch (Foschi–Hull–Ku, the same closed form
as `pliego.kinematics.degree4_mode1`):

- the ridge folds by −γ, where γ is the gutter angle (180° − the opening);
- both diagonals fold by ρ, with tan(γ/2) = sin θ · tan(ρ/2).

Because sin θ < 1 the diagonals always lead the gutter, and they reach 180° together with it: the
lips lie flat inside the shut card. The slit separates the two lips, so each has its own θ and its
own motion, driven by the same gutter. The script cross-checks its closed form against
`degree4_mode1`, refuses lips that run off the card, and checks that the shut card is flat and that
nothing sticks out of it.

## The fold program

The program is `kinematic` (rigid panels, exact states):

1. **Fold the card shut** (16 substeps): the lips fold inside;
2. **Open it to 90°** (10 substeps): the mouth opens;
3. **Talk**: close the card by `talk` degrees (the mouth shuts) and open it to 90° again (4 + 4).

Substeps are spaced evenly along the path in fold-angle space, not in the gutter angle, because the
diagonals race near the flat card. Every state is checked with `kinematics.closure_residual`
(about 10⁻¹³ mm). The preview blends linearly between states; the largest closure error of that
blend, at a midpoint, is printed as `max_linear_midpoint_closure_mm` (under 1 mm at the defaults).
The kernel's DOF count reports 2, because the two lengths of gutter are separate variables at the
two vertices; the card itself ties them together, so the object has one degree of freedom.

**Preview and engine.** One sheet driven by its own fold program: the studio preview animates the
whole card. The physics engine adds the stiffness of the scored folds and contact between the lips.

## Making one by hand

1. Export the sheet (`svg`, `dxf`, `pdf` or `hpgl`): the outline and the slit on the cut layer, the
   six folds on the score layer.
2. Cut the slit and score the folds.
3. Fold the card in half. Fold each lip back along its diagonals, crease firmly, and fold it forward
   again.
4. Open the card a little and push each lip through to the inside, reversing the gutter between
   the lips. Close the card, press, and open it to see the mouth move.

## Parameters

| id | meaning | default | range |
|---|---|---|---|
| `page_width`, `page_height` | one page of the card | 150, 150 mm | 90–220, 90–260 mm |
| `stock` | `cardstock-160`, `cardstock-250`, `kraft-120`, `copy-80` | `cardstock-160` | |
| `mouth_width` | length of the slit | 80 mm | 20–180 mm |
| `upper_lip`, `lower_lip` | how far along the gutter each lip's diagonals meet | 22, 28 mm | 6–80 mm |
| `mouth_position` | height of the slit as a fraction of the card | 0.5 | 0.2–0.8 |
| `talk` | how far the program closes the card to make the mouth speak | 40° | 10–60° |

Presets: `wide-grin`, `beak` (a bird's beak), `a6-card`.

## History and sources

The talking mouth is a standard cut-and-fold pop-up card mechanism, described in the pop-up
literature, for example Paul Jackson, *Cut and Fold Techniques for Pop-Up Designs* (Laurence King,
2014). The motion of a flat-foldable degree-4 vertex is the closed form the kernel implements in
`pliego.kinematics` (rigid foldability of degree-4 vertices is treated in Thomas C. Hull,
*Origametry*, Cambridge University Press, 2020). No published design or diagram is copied; the
geometry and its motion are computed by this cartridge.

## Provenance and licence

Original MADFAM geometry (the lineage records the general technique, credited to the tradition).
Published under CERN-OHL-W-2.0 like every object in the commons (see the commons root `LICENSE`).
