# Accordion fan

| | Title | Summary |
|---|---|---|
| en | Accordion fan | Two fans on one geometry, the radial pleat: a hand fan whose pleats gather at the base, and the paper leaf of a ribbed folding fan with its card ribs. The pleats close and open rigidly, exact at every step. |
| es | Abanico plegable | Dos abanicos sobre una misma geometría, el plisado radial: un abanico de mano cuyos pliegues se recogen en la base y el país de papel de un abanico de varillas, con sus varillas de cartulina. El plisado se cierra y se abre de forma rígida, exacto en cada paso. |
| fr | Éventail plissé | Deux éventails sur une même géométrie, le plissé radial : un éventail à main dont les plis se resserrent à la base, et la feuille de papier d'un éventail à brins, avec ses brins de carton. Le plissé se ferme et s'ouvre de façon rigide, exact à chaque étape. |
| pt | Leque plissado | Dois leques sobre uma mesma geometria, o plissado radial: um leque de mão cujas pregas se recolhem na base e a folha de papel de um leque de varetas, com as suas varetas de cartolina. O plissado fecha e abre de forma rígida, exato em cada passo. |

## What it is

A pleated fan is a sheet folded back and forth so that it can close into a narrow stack and open
into a wide surface. This cartridge builds both of the common paper fans on one geometry, the
**radial pleat**: every crease runs along a ray from one point O, alternating valley and
mountain, with equal angles δ between neighbouring creases.

| Mode | Sheets | What you get |
|---|---|---|
| `hand-fan` | one trapezoid of paper | a hand fan whose pleats converge to a point just below its base, so they gather there and spread at the top |
| `folding-fan` | the leaf (an annular sector of paper) plus `panels/2 + 1` ribs of card | a ribbed folding fan: the ribs are glued under the leaf and riveted together at O |

The classroom fan made from a rectangle with *parallel* pleats can only be pinched at the base by
bending the paper; no rigid motion gathers parallel pleats at one end. Converging the pleats
removes that bending. The hand fan here is cut as a trapezoid (a rectangle with its two bottom
corners trimmed along the outer rays) and opens with flat panels.

## Geometry

**The radial pleat.** Number the rays r₀ … r_N from one edge of the fan. In a symmetric state:

- the even rays (the valleys, and the two edges) stay in one plane, turned 2ψ apart;
- the odd rays (the mountains) rise out of that plane by an angle β, half-way between their
  neighbours in azimuth.

Each panel keeps its flat angle δ exactly when

    cos δ = cos β · cos ψ

So ψ = δ is the flat sheet, ψ → 0 is the closed stack, and the fan spans N·ψ. Every leaf point
is placed in its panel's plane, between that panel's two rays. No crease ends inside the paper,
because O lies off the sheet, so there is no vertex loop to close and every state of this
one-parameter family is an exact rigid state. The script still checks three things on the 3-D
model: the fold angles (read off as signed dihedrals) agree with the assignment, every panel
keeps its flat angle, and the loop-closure residual stays at rounding level.

**The hand fan.** O sits `gather × height` below the middle of the base, and the creases are
spaced equally in angle between the rays to the two top corners. With the defaults (297 × 105 mm,
gather 0.15, 16 panels) the flat span is 101.8°, and the base is about 39 mm wide.

**The folding fan.** The leaf is an annular sector with outer radius `radius`, inner radius
`leaf_depth × radius` and flat span `fan_angle`, centred on O. There is one rib under every
valley ray and one under each edge of the leaf. Each rib is a card strip from O to the rim:

- it is glued along a narrow strip to the panel beside its ray, so it tilts with that panel
  about its own axis, as a stick does;
- it is riveted to the first rib at O with a `pivot` join.

The first and last ribs are the guards. The document starts from the open fan (the `initial`
frame), with every glue weld satisfied.

## The fold program

Both programs are `kinematic`; every step is an exact rigid state, and its note gives the fan's
span.

- **`hand-fan`.** Four steps fold every pleat together from the flat sheet to the closed stack.
  Three more spread the top to `spread` × the flat span; the base stays gathered.
- **`folding-fan`.** Four steps close the fan from its open state; four more open it again.

**What the preview shows and what needs the physics engine.** The studio preview poses each
sheet along its face tree. The hand fan is shown exactly at every step. In the folding fan the
leaf is exact, but the preview does not enforce glue or rivets, so the ribs stay where the
initial frame put them (the open fan) while the leaf closes. At the end of the program the fan is
open again and leaf and ribs agree. In the physics engine (tier C) the ribs follow the leaf
through the glue and turn about the rivet. The ribs also overlap near the rivet, as a real stack
of sticks does, and the engine's contact separates them.

## Making one by hand

**Hand fan.**

1. Plot or print the trapezoid (SVG, PDF, DXF or HPGL) on washi or kami.
2. Score every line, then fold valleys and mountains alternately, so that the sheet closes into a
   narrow wedge.
3. Wrap the narrow base with a strip of paper or tape. The top opens into a fan.

**Folding fan.**

1. Cut the leaf from washi and nine ribs (for 16 panels) from 300 g/m² card, 6 mm wide.
2. Punch each rib at 6 mm from its narrow end.
3. Pleat the leaf and press the stack.
4. Glue each rib along the panel beside its valley; the outer ribs go under the leaf's edges.
5. Stack the ribs on a rivet, a split pin or a short bolt through the punched holes. The
   rivet is not modelled: the document joins the ribs at O with a free `pivot`.

## Parameters

| Parameter | Modes | Meaning |
|---|---|---|
| `pleats` | both | number of panels (even, 8–32) |
| `spread` | both | open span as a fraction of the flat span |
| `width`, `height` | `hand-fan` | top edge and height of the trapezoid, mm |
| `gather` | `hand-fan` | how far below the base the pleats converge, as a fraction of the height |
| `radius` | `folding-fan` | outer radius of the leaf, mm |
| `leaf_depth` | `folding-fan` | inner edge of the leaf as a fraction of the radius |
| `fan_angle` | `folding-fan` | flat span of the leaf, degrees |
| `stock` | both | paper for the leaf: kozo washi, kami, copy paper or kraft; the ribs are 300 g/m² card |

Presets: `fine-pleats` (24 panels) and `wide-open` (spread 0.95, folding-fan span 170°, hand-fan
gather 0.1). The folding fan's sheets are the leaf and `rib-0` … `rib-k`, with k = panels/2.

## History and sources

Hand fans are found in many cultures. The folding fan, with ribs that pivot on a rivet and a
pleated leaf, is generally traced to Japan, where it is called *sensu* or *ōgi*. From there it
spread to China and, later, to Europe.

- Wikipedia, «Hand fan» — https://en.wikipedia.org/wiki/Hand_fan (history of hand and folding
  fans).
- Pliego sheet-document spec v1, §5.3 (glue and pivot joins) and §6 (the initial frame).

## Provenance and licence

The object types are traditional and are credited to their tradition; the folding fan in
particular is traced to Japan. The geometry is original MADFAM work: the radial pleat, both
sheets' outlines and the rib layout are computed by this cartridge's `main.py`, and no maker's fan
design is copied. Licence: CERN-OHL-W-2.0 (the commons' root licence).
