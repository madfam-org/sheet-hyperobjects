# Corrugated board

| | |
|---|---|
| **en** | Corrugation itself — fluted media between liners in single face, single, double and triple wall, A/B/C/E/F flutes, craft corrugated paper and a cross-section template — formed flute by flute. |
| **es** | La corrugación misma —médiums ondulados entre liners en una cara, pared sencilla, doble y triple, flautas A/B/C/E/F, papel corrugado de manualidades y una plantilla del corte— formada flauta por flauta. |
| **fr** | L'ondulation elle-même — cannelures entre couvertures en simple face, double face, double-double et triple, profils A/B/C/E/F, papier ondulé de loisirs et gabarit de coupe — formée onde après onde. |
| **pt** | A própria ondulação — miolos ondulados entre capas em face simples, parede simples, dupla e tripla, ondas A/B/C/E/F, papel ondulado de artesanato e um gabarito do corte — formada onda a onda. |

## What it is

Corrugated board is a sandwich: a **fluted medium** — paper pressed into a wave between
corrugating rolls — glued with starch to flat **liners**. One medium and one liner make
*single-face* board (the flexible craft "corrugated paper", flutes exposed); one medium between
two liners is *single wall*; two and three media make *double* and *triple wall*. The flute
profile sets the board's thickness and character: A (the tallest), C, B, E and F (microflute).

Modes:

- **board** — the chosen construction and flutes: the liners lie in place and each medium is
  fed flat and corrugated until it fits between them;
- **craft** — craft corrugated paper: single face, the coloured medium on top;
- **section** — a cut template of the board's cross-section, enlarged up to ten times, with a
  folding foot so it stands on a desk.

## Geometry

The flute table is `pliego.board.FLUTES`, the same one the corrugated stock cards are derived
from:

| flute | flutes per metre (Foster 1997) | pitch (mm) | flute height (mm) |
|---|---|---|---|
| A | 108 | 9.26 | 4.7 [E] |
| B | 154 | 6.49 | 2.70 (measured) |
| C | 128 | 7.81 | 3.60 (measured) |
| E | 295 | 3.39 | 1.30 (measured) |
| F | 420 | 2.38 | 0.6 [E] |

Measured heights are from cross-section images (Rogalka, Grabski & Garbowski 2023); A and F are
estimates. The medium's centre line has amplitude (h − t)/2. The stock model integrates it as a
sinusoid; the foldable medium here is a **trapezoid** — flat lands at the flute tips, where the
glue goes, and straight flanks — whose land width is solved so it uses exactly the sinusoid's
length of medium per length of board (the take-up α: B 1.31, C 1.37, E 1.23 with a 0.16 mm
medium). Real profiles have steeper flanks, and handbook take-up values run a little higher; the
model's grammage is therefore a slight underestimate (stated on the stock cards).

Each medium is a flat sheet `pitches × 4` facets long (flat length = α × board length) with one
crease per facet junction: mountain where the profile turns down, valley where it turns up, at
the flank angle β = atan(2a / (λ/2 − w)). The section template is the board seen along the
flutes, from mid land to mid land: an outline with every flute void cut out (a single-face
board's exposed flutes shape its upper edge), scaled, with a scored foot.

## The fold program

**board / craft** (kinematic): for each medium in turn, three steps feed it through the
corrugating rolls — each step forms a third of the flutes, so the flat tail is drawn in and the
medium shortens by its take-up. The flutes are parallel creases that never meet, so each medium
is a face tree; its first land stays level at the height of the upper liner. **section**: one
step folds the foot 90° so the template stands.

**Needs the physics engine:** the starch glue lines between the flute tips and the liners (not
written as joins: the program starts with a flat medium, so no weld holds at t = 0), and the
board behaving as a board — its orthotropic stiffness is on the stock cards
(`corrugated-*-flute`, `corrugated-bc-double-wall`, `corrugated-aac-triple-wall`,
`corrugated-single-face-b`), derived from the same geometry.

## Making one by hand

Craft corrugated paper can be made with a pasta machine's corrugating attachment or by pleating
a strip over a pencil; for a model of real board, crease the medium sheet's lines alternately
mountain and valley, pinch it to the profile and glue the lands to card liners. The section
template is cut from card at the chosen scale, the foot folded back along its score.

## Parameters

| Parameter | Range | Meaning |
|---|---|---|
| `construction` | single face · single wall · double wall · triple wall | layers |
| `flute`, `inner_flute` | A · B · C · E · F | outer walls; last wall of double and triple boards |
| `length`, `width` | 40–200, 30–150 mm | sample size (width runs along the flutes) |
| `liner`, `medium` | kraftliner 150, kraft 120, copy 80 | component papers |
| `scale` | 1–10 × | section template enlargement |
| `color` | five colours | craft mode medium colour |

Presets: E flute single wall, BC double wall, AAC triple wall, F microflute single face.

## History and sources

Pleated paper was patented in England in 1856 as a hat liner; Albert Jones patented corrugated
paper for wrapping bottles in the United States in 1871, and Oliver Long added the liners in
1874. Corrugated board has carried most shipped goods since the early twentieth century.

- Wikipedia, *Corrugated fiberboard* (history; flute table after Foster 1997, *The Wiley
  Encyclopedia of Packaging Technology*) — https://en.wikipedia.org/wiki/Corrugated_fiberboard
- Rogalka, Grabski & Garbowski 2023, *Identification of geometric features of the corrugated
  board using images and genetic algorithm*, Sensors 23(13):6242 — https://doi.org/10.3390/s23136242
- Pliego physics memo §(h), *Board, corrugation and foam*, and the `pliego.board` model (in the
  Pliego repository).

## Provenance and licence

Original MADFAM geometry, computed by `pliego.corrugate` from the flute table; corrugated board is
an industrial material attributed to that tradition. Licence CERN-OHL-W-2.0 (both manifest fields).
