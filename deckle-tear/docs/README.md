# Torn and deckle edges

| | Title | Summary |
|---|---|---|
| en | Torn and deckle edges | A strip torn off a sheet three ways (folded and creased first, freely, or against a ruler); the torn outline follows the paper's fibre length and grain, and the strip lifts away. |
| es | Bordes rasgados y de barba | Una tira que se desprende de una hoja de tres maneras (doblada y marcada antes, a mano libre o contra una regla); el contorno rasgado sigue el largo de fibra y el hilo del papel, y la tira se levanta y se aparta. |
| fr | Bords déchirés et à barbes | Une bande détachée d'une feuille de trois façons (pliée et marquée d'abord, à main levée ou contre une règle) ; le contour déchiré suit la longueur des fibres et le sens du papier, et la bande se soulève et s'écarte. |
| pt | Bordas rasgadas e de barba | Uma tira destacada de uma folha de três maneiras (dobrada e vincada antes, à mão livre ou contra uma régua); o contorno rasgado segue o comprimento de fibra e o sentido do papel, e a tira se ergue e se afasta. |

## What it is

Tearing is the oldest way to divide a sheet, and a torn edge is a finish of its own. A *deckle
edge* is the feathered edge of handmade paper, where pulp crept under the removable frame (the
deckle) of the papermaker's mould; a torn edge imitates it. This cartridge tears a strip off one
side of a sheet in three ways (the three modes):

- **`crease`**: fold, crease, tear. The strip is folded over along a line, opened, folded back the
  other way and opened again. The double crease breaks the fibres along the line, and the strip
  tears off almost straight.
- **`deckle`**: a free tear. Pulled apart by hand, the edge wanders and frays at the scale of the
  paper's fibres. Optionally the whole outline is deckled too (`all_edges`), like a sheet straight
  from the mould.
- **`ruler`**: a strip torn upward against a straightedge. The ruler holds the sheet, so the torn
  edge stays on the free side of the ruler line and wanders less than a free tear.

## Geometry

The sheet is `width` × `height`; the tear runs from the bottom edge to the top edge, `strip` mm in
from the right edge. The torn line is generated, not simulated:

- **Fibre scale.** Each offered paper has a fibre length *L*: copy paper 1.5 mm, light card
  1.8 mm, kraft 3 mm, kozo washi 8 mm. These are engineering estimates of the fibre furnish
  (office and card pulps are short hardwood and softwood fibres, sack kraft is long softwood fibre,
  kozo is a long bast fibre), not measurements. They set the scale of the fringe.
- **Grain.** A tear along the grain runs cleaner than one across it. The cartridge sets the
  sheet's grain along the tear (`grain` = `along`) or across it, and multiplies the wander by 1.0
  along and 1.6 across; washi, which is handmade and has no machine direction, uses 1.3.
- **The outline.** The torn line is *x(v) = x₀ + A · e(v) · n(v)*: four octaves of smoothed value
  noise *n* with a longest wavelength of 2.5 *L*, sampled every 0.5 mm or finer. The amplitude *A*
  is 0.6 *L* for a free tear and 0.25 *L* for a ruler tear (one-sided there: the line never crosses
  to the ruler's side), times the grain factor and `roughness`. The envelope *e* brings the line in
  square to the edges within one wavelength, as a tear starts. The noise is a deterministic hash
  of the `seed`, so the same parameters always give the same bytes.
- **Deckled outline.** With `all_edges`, every point of the outline moves inward by up to
  0.45 *L* × `roughness`, walked continuously round the perimeter (corners move along their
  bisector, so the outline stays simple) and flat where the tear meets it.
- **Checks.** `pliego.papercut.analyze` must find exactly two pieces and no tongue of paper
  narrower than 1 mm; the script refuses the parameters otherwise. The strip is widened, if
  needed, to stay clear of the line's wander.

In `crease` mode the line is straight and is a kiss cut (`F` + `halfcut`): an `F` line can be
folded by the program, and a kiss cut is a separating edge for removable pieces (spec §5.8). In the
other modes the torn line is a cut (`C`).

## The fold program

The sheet holds two pieces (spec §5.8): the body (`keep`) and the strip (`excess`), and the last
step's `remove` lifts the strip away, drawn up and to the right.

- `crease`: fold the strip over (180°), open it, fold it back the other way (−180°), open it again,
  then tear it off. Opening is a target, not a release (spec §5.6).
- `deckle` and `ruler`: one step, the tear.

**Preview and engine.** The studio preview plays every step: the folds, and the strip lifting
away. The tear itself is not physics: the outline is generated, and the piece separates along it.
Real fracture (stress concentrating at the tip of the tear, fibres pulling out, the fringe
standing up from the sheet) is the physics engine's wave-3 work.

## Making one by hand

- **Fold, crease, tear.** Fold along the line and press it hard with a bone folder or a
  thumbnail; open, fold it back the other way and press again; open, then pull the strip off
  slowly, starting at one end and keeping the pull close to the line. Wetting the crease with a
  damp brush softens the fibres and gives a softer edge.
- **Free tear.** Pinch both sides of the line and pull apart slowly; tear along the grain for a
  cleaner edge, across it for a rougher one.
- **Against a ruler.** Press a metal ruler down along the line and pull the strip up and toward
  you.

**Fabrication.** The exporters draw the generated torn line as a cut: a blade or laser can cut the
faux-deckle outline, while a hand tear makes its own edge, which the outline only stands in for.
In `crease` mode the line is a kiss cut, drawn with the score lines as a guide.

## Parameters

| id | meaning | default | range |
|---|---|---|---|
| `width`, `height` | sheet size; the tear runs along the height | 148 × 105 mm | 60–300 × 40–300 mm |
| `strip` | width of the torn-off strip | 32 mm | 12 mm – half the sheet |
| `stock` | `copy-80`, `cardstock-160`, `kraft-120`, `washi-kozo-30` | `kraft-120` | |
| `grain` | tear `along` or `across` the grain | `along` | |
| `roughness` | scales the wander (modes `deckle`, `ruler`) | 1.0 | 0.25–2.0 |
| `seed` | another seed, another tear | 7 | 1–9999 |
| `all_edges` | deckle the whole outline (mode `deckle`) | off | |

Presets: `washi-feather`, `across-grain`, `card-strip`.

## History and sources

- The deckle edge is the feathered edge of handmade paper, named after the deckle, the removable
  frame of the papermaking mould; before the nineteenth century it was unavoidable, and machine-made
  paper later imitated it (Wikipedia, «Deckle edge», https://en.wikipedia.org/wiki/Deckle_edge).
- Paper torn with the grain leaves a cleaner tear and paper torn across it a messier one, which is
  the common test for grain direction (British Letterpress, «Machine or Grain Direction in Paper»,
  https://britishletterpress.co.uk/letterpress-guides/printing/paper/machine-or-grain-direction-in-paper/).
- Kozo washi is made from long bast fibres and resists tearing (Pliego research memo, «Paper
  physics», `docs/research/paper-physics-memo.md`, material table).

The noise model, the fibre lengths and the amplitude factors are this cartridge's own estimates for
a convincing edge; they are not fitted to measured tears.

## Provenance and licence

Original MADFAM geometry: the torn and deckled outlines are generated by `main.py`. Tearing and the
deckle edge are traditional practice, credited to no one. Published under CERN-OHL-W-2.0 like every
object in the commons (see the commons root `LICENSE`).
