# Volvelle

| | Title | Summary |
|---|---|---|
| en | Volvelle | A wheel chart: paper discs turning on a pivot through a base, under a cover with windows or as a stack of independent rings. |
| es | Volvela | Una rueda de papel: discos que giran sobre un eje que atraviesa una base, bajo una tapa con ventanas o como una pila de anillos independientes. |
| fr | Volvelle | Une roue à calcul : des disques de papier qui tournent sur un axe traversant une base, sous un couvercle à fenêtres ou en pile d'anneaux indépendants. |
| pt | Volvela | Uma roda de papel: discos que giram num eixo que atravessa uma base, sob uma tampa com janelas ou como uma pilha de anéis independentes. |

## What it is

A volvelle, or wheel chart, is a paper machine: printed discs that turn on a common pivot so that
values on one line up with values on another. Astronomy books used them to find the positions of
the sun and moon, and the same device later served as calendars, calculators and code wheels. This
cartridge makes the two classic layouts:

- **`windows`**: a square base, a wheel and a square cover. The cover has openings in a ring, and
  turning the wheel shows one printed sector of it at a time in each window. The wheel is larger
  than the base and the cover, so its rim shows at the four sides, where the thumb turns it.
- **`rings`**: a square base and a stack of discs of decreasing radius. Each disc turns on its
  own and leaves a band of the disc below it visible, and a small V notch in its rim points at that
  band.

## Geometry

Every disc is a 96-segment circle in its own frame, centred on the pivot by its placement and
stacked 0.25 mm above the layer below. Each turning disc has a pivot hole of `pivot_hole`. The base
has no hole: a kiss-cut cross (treatment `halfcut`; the exporters draw it with the score lines) marks where the pivot
pierces it.

- **Windows.** The wheel's diameter is `wheel_ratio` × the base. The cover's openings sit in a
  band between `band_inner` and `band_outer` of half the base, evenly spaced: ring sectors
  `window_angle` wide, or round windows filling the band. The script refuses a band narrower than
  8 mm or too close to the pivot, and windows whose bridges at the band's inner edge would fall
  under 3 mm. The cover then passes `pliego.papercut.analyze` (one piece, narrowest bridge ≥ 3 mm).
- **Rings.** The largest disc stops 4 mm inside the base, and each further disc is `ring_band`
  smaller in radius. The script refuses a top disc too small to hold its pivot.

## The mechanism

Each turning disc is a kinematic sheet driven by a `rotate` mechanism about the pivot, the normal
of the base at its centre, with its own angle control (0–360°): `turn` for the wheel, `ring-1` …
`ring-5` for the rings. The pivot hardware is the mechanism's centre, not a `pivot` join. That is
deliberate: a join between a turning disc and the fixed base would leave the control to the
physics engine, while the rotation about the pivot is exactly what the hardware enforces.

**Preview and engine.** Every control plays in the studio preview. The physics engine adds the
friction between the layers and the slight dishing of a disc pinched at its centre.

## Making one by hand

1. Export the sheets (`svg`, `dxf`, `pdf` or `hpgl`). Print the wheel's sectors (or each disc's
   band) and the base's labels before cutting.
2. Cut the discs and the cover; cut the windows with a craft knife, inside corners first.
3. Punch the pivot holes. Stack base, wheel and cover (or the discs, largest first), push a paper
   brad (split pin) or a binding post through the stack at the kiss-cut mark, and open its legs or
   screw it shut. Leave it loose enough to turn.

## Parameters

| id | meaning | default | range |
|---|---|---|---|
| `size` | side of the square base (and cover) | 150 mm | 80–300 mm |
| `pivot_hole` | pivot hole in each turning disc | 3 mm | 2–6 mm |
| `wheel_ratio` | wheel diameter ÷ base (mode `windows`) | 1.2 | 1.05–1.35 |
| `windows` | number of windows | 2 | 1–8 |
| `window_shape` | `sector` or `round` | `sector` | |
| `window_angle` | angular width of a sector window | 40° | 8–120° |
| `band_inner`, `band_outer` | the window band, ÷ half the base | 0.35, 0.8 | 0.15–0.95 |
| `rings` | number of discs (mode `rings`) | 3 | 2–5 |
| `ring_band` | visible band of each disc | 16 mm | 8–40 mm |

Presets: `four-windows`, `five-rings`, `pocket` (100 mm).

## History and sources

Volvelles appear in medieval and Renaissance books. Matthew Paris used them around 1240 in his
*Chronica Majora*, and Petrus Apianus's *Astronomicum Caesareum* (1540) is a celebrated example
(Wikipedia, «Pop-up book», https://en.wikipedia.org/wiki/Pop-up_book). They were used to work out
the positions of the sun and moon, and in the twentieth century for tasks from inventory control to
verb conjugation (Wikipedia, «Volvelle», https://en.wikipedia.org/wiki/Volvelle). No historical
volvelle's design is copied; the geometry is computed by this cartridge.

## Provenance and licence

Original MADFAM geometry (the lineage records the historical device, credited to the tradition).
Published under CERN-OHL-W-2.0 like every object in the commons (see the commons root `LICENSE`).
