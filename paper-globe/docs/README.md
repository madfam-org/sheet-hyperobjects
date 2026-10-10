# Paper globe

| | Title | Summary |
|---|---|---|
| en | Paper globe | Twelve or twenty-four gores, each a pole-to-pole slice of a sphere developed flat, bent along their length until they close into a globe. |
| es | Globo de papel | Doce o veinticuatro husos, cada uno una franja de esfera de polo a polo desarrollada en plano, curvados a lo largo hasta cerrarse en un globo. |
| fr | Globe en papier | Douze ou vingt-quatre fuseaux, chacun une tranche de sphère d'un pôle à l'autre développée à plat, courbés sur leur longueur jusqu'à se refermer en globe. |
| pt | Globo de papel | Doze ou vinte e quatro fusos, cada um uma fatia de esfera de polo a polo desenvolvida no plano, curvados ao longo do comprimento até se fecharem num globo. |

## What it is

Globe makers cover a ball with **gores**: lens-shaped strips, each one a slice of longitude from
pole to pole, printed flat and pasted on side by side. This cartridge makes the gores (12 of 30°
or 24 of 15°) and shows them bending along their length until neighbours meet edge to edge and the
globe closes. The surface patterns are simple and original — alternating colours, a two-tone
graticule, or plain paper; no map artwork is used.

## Geometry

A sphere is curved in two directions, so a gore can never lie on it exactly: real paper gores
stretch and crumple a little when pasted. This cartridge uses an approximation that is exact for
its own surface. The sphere is replaced by the polyhedron with a vertex on the sphere every `band`
degrees of latitude and every 360°/G of longitude (a latitude–longitude, or "UV", sphere). One
gore of it is a chain of isosceles trapezoids, with a triangle at each pole, and each panel shares
a latitude chord with the next, so the chain unrolls flat without stretching:

- the parallel sides of the panel between latitudes φᵢ and φᵢ₊₁ are cᵢ = 2ρ · cos φᵢ · sin(π/G),
  with ρ the globe's radius;
- the slant sides are s = 2ρ · sin(Δφ/2), with Δφ = `band`.

The flat gore is the familiar lens, whose width follows cos φ and narrows to a point at each pole.
For the default globe (150 mm, 12 gores, 10° bands) a gore is 231.3 × 38.8 mm, against a true
meridian of 235.6 mm, and the polyhedron's equator is 98.9% of the sphere's (99.7% with 24 gores):
more gores, closer to the sphere.

**Segmentation.** The latitude chords are the panel lines: `F` lines with treatment `none` (plain
paper, never scored or cut). In the assembled globe every panel is mapped rigidly onto its
trapezoid of the polyhedron; the script checks that no edge stretches and that each gore's east
edge meets its neighbour's west edge, and fails loud otherwise. The gore outline is checked with
`pliego.papercut.analyze`. Gores bend printed side out (mountain).

## The fold program

Each gore sheet is placed so that its south-pole triangle (the sheet's first face) sits where it
belongs on the globe, so the flat gores start radiating from the south pole like petals on the
table. A `kinematic` program then bends them along their meridians in two steps (halfway, then
closed) until each gore meets its neighbours edge to edge. It ends in the globe, written as
`target:globe`.

**Preview and engine.** The studio preview plays the whole program and ends exactly on the target
globe. Nothing joins the gores to one another: on a real globe they are pasted onto a ball, a
solid core that this sheet cartridge does not model (solids belong to Yantra4D). The flat-to-sphere
mismatch of real paper on a real ball (the small stretching the polyhedron avoids) is a physics
question for the engine.

## Making one by hand

1. Export the gores (`svg`, `dxf`, `pdf` or `hpgl`) and cut them out; the panel lines are not on
   the cut file. A 150 mm globe's gores are 231 mm long and fit A4.
2. Paste each gore onto a ball of the same diameter, starting at the equator and smoothing towards
   the poles, so that its edges meet its neighbours'.
3. Cover the points at the poles with a small paper disc, as globe makers do.

## Parameters

| id | meaning | default | range |
|---|---|---|---|
| `gores` | number of gores | 12 | 12 or 24 |
| `diameter` | globe diameter | 150 mm | 60–400 mm |
| `band` | latitude step of the polyhedron (model resolution, not cut) | 10° | 7.5, 9, 10, 12, 15° |
| `pattern` | `beach-ball`, `graticule`, `plain` | `beach-ball` | |
| `stock` | `copy-80`, `kraft-120`, `cardstock-160`, `washi-kozo-30` | `copy-80` | |

Presets: `twenty-four` (24 gores, graticule), `big-kraft` (300 mm kraft globe, 7.5° bands).
With 24 gores the step must be at least 9° to stay inside the render budget.

## History and sources

Wikipedia describes a gore as the curved surface between two meridians, which can be flattened
with little distortion; Martin Waldseemüller's 1507 globe gores are famous as the first to use the
name "America", and Johannes Schöner mass-produced globes by printing map details on 12 paper gores
that were cut out and pasted on a sphere, a method still often used; 12 gores of 30° each are
usual (Wikipedia, «Gore (segment)», https://en.wikipedia.org/wiki/Gore_(segment)). The «Globe»
article adds that the long, thin gores narrow to a point at the poles, where small discs cover the
irregularities, and that more gores need less stretching and crumpling; the method was illustrated
in 1802 in an engraving in George Kearsley's *English Encyclopedia*
(https://en.wikipedia.org/wiki/Globe). This cartridge reproduces no historical gore or map: the
gores are computed geometry with original colour patterns.

## Provenance and licence

Original MADFAM geometry and patterns; the lineage credits globe gores as a historical
globe-making technique. Published under CERN-OHL-W-2.0 like every object in the commons (see the
commons root `LICENSE`).
