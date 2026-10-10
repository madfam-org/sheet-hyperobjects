# Step pop-up

| | Title | Summary |
|---|---|---|
| en | Step pop-up | A staircase cut and scored into one card: nested step folds that stand when the card opens and fold flat inside when it shuts. No glue. |
| es | Pop-up de escalones | Una escalera cortada y hendida en una sola tarjeta: escalones anidados que se levantan al abrir la tarjeta y quedan planos por dentro al cerrarla. Sin pegamento. |
| fr | Pop-up à marches | Un escalier découpé et rainé dans une seule carte : des marches emboîtées qui se dressent à l'ouverture et se rangent à plat à la fermeture. Sans colle. |
| pt | Pop-up de degraus | Uma escada cortada e vincada num único cartão: degraus aninhados que se erguem ao abrir o cartão e ficam planos por dentro ao fechá-lo. Sem cola. |

## What it is

The step fold is the first cut-and-fold pop-up most people make: fold a card, cut two slits in
from the fold, fold the flap between them back and forth, and push it through to the inside. When
the card opens to a right angle, the flap stands as a box-shaped step. This cartridge makes a
whole staircase the same way, from one sheet and without glue: each further step is cut into the
corner of the step before it, a little narrower, so `steps` levels give `steps` risers.

The card is a spread of two pages, `page_width` × `page_height` each, with the gutter (the card's
spine) between them. With the card open at 90° the left page is the floor and the right page the
back wall.

## Geometry

Every fold is parallel to the gutter, so the whole card moves in its cross-section and each level
is a **parallelogram four-bar linkage**:

- its corner `C` (the gutter for the first level, a fold of the previous level after that);
- two attachment folds `A` and `B` on the two panels that meet at `C`, at distances `a` and `b`
  from it;
- a new fold `F = A + B − C`, the corner of the next level.

Opposite sides are equal (A–F = C–B = `b`, F–B = C–A = `a`), so the angle at `F` always equals the
angle at `C`. Nesting therefore costs nothing: every level sees the same opening, and **every fold
of the card turns by the same magnitude γ as the gutter** (γ = 180° − the opening). `A` and `B`
fold with the sign of their corner and `F` with the opposite sign, so concave corners (valleys) and
convex corners (mountains) alternate up the stairs.

For an n-step staircase with tread `t` and riser `r`, level k (k = 1 … n, m = n − k + 1) uses
`a = m·t`, `b = m·r` on odd levels and `a = m·r`, `b = m·t` on even levels. Level 1 is a box `n·t`
deep and `n·r` high; level 2 cuts a notch into its nose, level 3 puts a box back into that notch,
and so on, which leaves the staircase profile in the middle band. In the flat card, measured from
the gutter, a level's folds sit at `c − a`, `c − a + b` and `c + b`, and its two slits run from
`c − a` to `c + b`.

**Why the levels get narrower.** If a level were as wide as its parent, the parent's corner fold
would vanish and the strip would become a chain of 2n panels, a linkage with 2n − 1 degrees of
freedom that the card no longer controls. Leaving the ends of each corner fold uncut (`inset` on
each side) keeps every level square to the one below: the whole card has one degree of freedom.

**Fit.** Shut, the first level reaches `n·(t + r)` from the gutter, so the script refuses
`steps·(tread + riser) > page_width − 6 mm`, a top step narrower than 10 mm, and a first step wider
than the page allows.

## The fold program

The program is `kinematic` (rigid panels, exact states), built with
`pliego.Sequence.kinematic_path`:

1. **Fold the card shut** (10 substeps): γ goes from 0 to 180°; every step folds inward and lies
   flat between the pages.
2. **Open the card** to `open_angle` (8 substeps, 90° by default), where every tread is level and
   every riser upright.

The control `Close and open` scrubs the program and starts at its end, the open card. Because the
slits touch every fold vertex, the motion solver has no vertex loop to close; the loop through
each step is a loop around a cut. The script checks it directly: `kinematics.closure_residual`
over every crease, at every program state and every midpoint, must stay below 10⁻⁶ mm (it is about
10⁻¹³ mm), and the shut card must be flat and inside its page.

**Preview and engine.** Everything here is one sheet driven by its own fold program, so the
studio preview animates the whole card. The physics engine adds what rigid panels cannot show:
the stiffness of the scores, the slight spring of card left half open, and contact between the
folded layers.

## Making one by hand

1. Print or cut the sheet (export `svg`, `dxf`, `pdf` or `hpgl`): the outline and the slits are on
   the cut layer, the folds on the score layer (the PDF draws them in mountain and valley styles).
2. Cut the slits; a craft knife and a steel rule are enough. Score every fold before folding
   anything.
3. Fold the gutter, then work from the outside in: fold each level's three folds (valley, mountain,
   valley, then the reverse for the next level), so the steps push through to the inside.
4. Close the card and press it flat, then open it slowly to a right angle.

Card of 160 g/m² cuts and folds cleanly; 250 g/m² makes sturdier steps but needs careful scoring.
Mount the finished card on a slightly larger plain card if the slits should not show from outside.

## Parameters

| id | meaning | default | range |
|---|---|---|---|
| `page_width`, `page_height` | one page of the card | 150, 150 mm | 90–220, 90–260 mm |
| `stock` | `cardstock-160`, `cardstock-250`, `kraft-120`, `copy-80` | `cardstock-160` | |
| `steps` | number of risers (levels) | 3 | 1–5 |
| `riser`, `tread` | height and depth of one step | 18, 18 mm | 6–40 mm |
| `step_width` | width of the first level along the gutter | 90 mm | 30–200 mm |
| `inset` | how much narrower each level is, per side | 10 mm | 3–25 mm |
| `open_angle` | opening at the end of the program | 90° | 30–150° |

Presets: `single-step` (one 35 mm box), `grand-stair` (five 12 mm steps), `a6-card` (A6 pages).

## History and sources

Cut-and-fold pop-ups made from a single sheet are the basis of origamic architecture, associated
with the Japanese architect Masahiro Chatani, who developed and published it from the early 1980s
(Wikipedia, «Origamic architecture», https://en.wikipedia.org/wiki/Origamic_architecture). The
step fold is a general mechanism described in the pop-up literature, for example Paul Jackson,
*Cut and Fold Techniques for Pop-Up Designs* (Laurence King, 2014) and Duncan Birmingham, *Pop-Up
Design and Paper Mechanics* (GMC Publications, 2010). No published design or diagram is copied; the
staircase and its kinematics are computed by this cartridge.

## Provenance and licence

Original MADFAM geometry (the lineage records the general technique, credited to the tradition).
Published under CERN-OHL-W-2.0 like every object in the commons (see the commons root `LICENSE`).
