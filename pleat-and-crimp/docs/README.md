# Pleat and crimp

| | Title | Summary |
|---|---|---|
| en | Pleat and crimp | Mountain and valley lines in pairs: a pleat folds a band of one layer back on itself; a crimp does it through a strip folded in half, and can turn the strip. |
| es | Pliegue escalonado y crimp | Líneas de montaña y valle en pares: el pliegue escalonado dobla una franja de una capa sobre sí misma; el crimp lo hace a través de una tira doblada a la mitad y puede hacerla girar. |
| fr | Pli escalier et crimp | Des lignes montagne et vallée par paires : le pli escalier replie sur elle-même une bande d'une couche ; le crimp le fait à travers une bande pliée en deux et peut la faire tourner. |
| pt | Prega e crimp | Linhas de montanha e vale em pares: a prega dobra uma faixa de uma camada sobre si mesma; o crimp faz isso através de uma tira dobrada ao meio e pode fazê-la girar. |

A **pleat** is the simplest fold that uses both kinds of crease. A valley line and a mountain line
run side by side, and folding both flat tucks the band between them under itself, like a step.
A **crimp** is a pleat made through a strip already folded in half. The pleat goes through both
layers at once, and the centre fold has to reverse between the two lines to let it. Origami uses
crimps to bend a strip into a neck, a leg or a beak and lock it there.

## Geometry

The sheet is a strip `length × width` (200 × 80 mm by default). It carries `pleats` pairs, spaced
evenly along it. Each pair is a valley line and a mountain line crossing the **reference edge**
`pleat_width` apart. For a pleat, the reference edge is the bottom edge of the strip; for a crimp,
it is the centre fold.

**Why a pair moves the strip.** Folding a line flat reflects everything beyond it across that line.
A pair is two reflections in a row, and two reflections compose into one of two rigid motions:

- **parallel lines** compose to a **translation**. The far part of the strip slides back by twice
  the distance between the lines. With `tilt` > 0 the lines lean, and the far part also shifts
  sideways;
- **lines meeting at an angle α** compose to a **rotation by 2α**. The `turn` parameter is that
  rotation: the second line of each pair is splayed by `turn/2` from the first, and the far part of
  the strip turns by `turn` degrees at every pair.

The `target:flat-folded` frame is the exact rigid pose of the folded strip, computed by the
kernel's face tree, so these motions can be read off it. Every edge keeps its length in that frame.

**The crimp's crease pattern.** Unfolded, a crimp shows each pleat line as a chevron mirrored about
the centre line. The centre fold is split at every chevron tip: it is a valley outside the pairs
and a **mountain between the two lines of a pair**, where it reverses. Every tip is a degree-4
vertex. With φ the angle between a chevron leg and the centre line, its four sector angles are φ,
180° − φ, 180° − φ and φ, so the alternate sums are both 180° (Kawasaki's theorem) for any φ. Three
of its four creases share one assignment and the fourth has the other (Maekawa's theorem,
|M − V| = 2). The script runs the kernel's local flat-foldability check (`pliego.flatfold`:
Maekawa, exact Kawasaki, big-little-big) on the pattern it generates and refuses to return one that
fails.

**Fit.** Every line leans at most 45° (`tilt` + `turn/2`), so it runs at most one strip width
sideways. Pairs are therefore spaced at least `pleat_width + width` apart; the manifest's error
constraint, `length >= (pleats + 1) * (pleat_width + width)`, says so and the script enforces it.

## The fold program

Both techniques run in `physical` mode: hinges are driven by the hand, and the paper is paper.

- **Pleat**: one step per pair, *Pleat k: valley, then mountain*, driving both lines to ±180°
  together, as a hand pinches a pleat.
- **Crimp**: *Valley-fold the strip in half lengthwise* (every centre segment to +180°), *Open it
  to a right angle* (to +90°), then one step per pair, *Crimp k: pleat through both layers*, which
  drives the pair's chevrons to ±180° and the centre segment between them through flat to −180°.
  Last, *Close the strip flat* returns the outer centre segments to +180°. The open-then-push order
  is how a crimp is made by hand: you cannot reverse the middle of a fold that is pressed shut.

## Making one

1. Cut the strip (export `svg`, `dxf`, `pdf` or `hpgl`; valley and mountain lines in the
   exporter's palette styles).
2. **Pleat**: fold the valley line, then fold the paper back along the mountain line so the band
   lies under itself. Press both.
3. **Crimp**: fold the strip in half along the centre line and crease it. Crease the pleat lines
   through both layers. Open the strip a little, push the section between the pleat lines inside
   out on both layers at once, and close the strip again.

Kami and copy paper hold sharp pleats. Kraft paper at 120 g/m² resists: folding it through two
layers needs more force.

## Parameters

| Parameter | Meaning | Default |
|---|---|---|
| `technique` | `pleat` (one layer) or `crimp` (through the strip folded in half) | `pleat` |
| `length` | strip length (mm) | 200 |
| `width` | strip width (mm) | 80 |
| `pleat_width` | distance between the two lines of a pair on the reference edge (mm) | 15 |
| `pleats` | number of pairs (1–4) | 1 |
| `tilt` | lean of the lines from square (°) | 0 |
| `turn` | rotation of the strip at each pair (°) | 0 |
| `stock` | `kami`, `copy-80`, `kraft-120` | `kami` |

Presets: `crimp`, `tilted-crimp` (20° tilt), `turning-crimp` (30° turn), `three-pleats` (on a
400 mm strip).

## History and sources

The pleat and the crimp are traditional techniques, written in diagrams with the symbols of the
Yoshizawa–Randlett system (Wikipedia, «Yoshizawa–Randlett system»,
https://en.wikipedia.org/wiki/Yoshizawa%E2%80%93Randlett_system). Maekawa's and Kawasaki's
theorems are the standard local conditions for flat foldability (Wikipedia, «Mathematics of paper
folding», https://en.wikipedia.org/wiki/Mathematics_of_paper_folding). No model's crease pattern
or diagram is reproduced; the geometry is generated by this cartridge.

## Provenance and licence

Traditional techniques (public domain); original geometry. Published under CERN-OHL-W-2.0 like
every object in the commons (see the commons root `LICENSE`).
