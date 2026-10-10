# Paper bag

| | Title | Summary |
|---|---|---|
| en | Paper bag | The flat-bottomed paper bag with side gussets, from one sheet of kraft, folded from flat to open by an exact rigid program. |
| es | Bolsa de papel | La bolsa de papel de fondo plano con fuelles laterales, hecha de una sola hoja de kraft y plegada de plana a abierta con una secuencia rígida exacta. |
| fr | Sac en papier | Le sac en papier à fond plat et soufflets latéraux, tiré d'une seule feuille de kraft et plié de la feuille au sac ouvert par une séquence rigide exacte. |
| pt | Saco de papel | O saco de papel de fundo chato com foles laterais, feito de uma única folha de kraft e dobrado de plano a aberto por uma sequência rígida exata. |

## What it is

The everyday kraft bag: a front, a back, two side gussets that let it fold flat, and a flat
rectangular bottom on which it stands open. This is the self-opening sack (SOS) form, made here
by hand from a single sheet. The tube is closed by one glue flap, and the bottom by folding and one
glued overlap. The sheet is not cut at the corners: the excess paper at each bottom corner folds
back into an ear.

## Geometry

**The blank.** A row of panels: front (`width`), gusset (`gusset`), back (`width`), gusset, and a
15 mm glue flap, all `height` tall. The flap closes the tube inside the front. Each gusset is
scored down its centre (a flat score) so the made bag can pleat in. The blank is
2 × (`width` + `gusset`) + 15 mm wide.

**The bottom.** Below the bottom score every panel continues by an extension
`e` = `gusset`/2 + `overlap`/2. Folded in:

- the gusset extensions lie flat and cover the sides of the bottom, `e` deep;
- the back and front extensions cover the bottom from the back and from the front, each `e`
  deep, so they overlap by `overlap` in the middle, where they are glued;
- where a front or back extension meets a gusset extension, a 45° crease runs from the bag's
  corner across the front or back extension. The corner of the flap folds back on itself along
  it into an ear, tucked between the gusset extension and the flap, and the corner line between
  the two extensions folds flat.

Seen from below, the two flaps overlap across the middle and each gusset extension shows as a
triangle between their 45° edges. At the glue-flap corner the front extension and the gusset
extension are separate pieces of paper, so there the front flap's corner is simply cut at 45°,
and its extension starts 1 mm in from the corner. The gusset extensions must not meet in the middle
of the bottom: `gusset` + `overlap` must stay under `width` − 4 mm, or the script stops.

**Corners as mechanisms.** A bottom corner is a degree-5 vertex. Around it lie the gusset, the
front (or back), the flap, the ear and the gusset extension (90°, 90°, 45°, 45°, 90°). With the
bag's corner held at 90° it keeps two degrees of freedom. From the tube state, which is singular
(the corner line and the extension line form one straight fold), the motion solver could take
either of two branches. One tucks the ear inside the bottom; the other would turn the back flap
outward. The script solves the right branch once on a single corner (its angles do not depend on
the bag's size) and drives every corner of the bag along it.

## The fold program

`kinematic` mode, built with `pliego.Sequence.kinematic_path`, so every in-between state is an
exact rigid state (26 substeps from three key poses):

1. **tube:** fold the four corners to 90° and the glue flap inside the front;
2. **gussets in:** the gusset flaps fold halfway in; the front and back flaps rise with them and
   their corners fold back into ears;
3. **bottom:** press the bottom flat and glue the overlap.

The bottom is shown 0.4° short of flat (gusset flaps at 89.6°, front and back flaps at 89.8°, as
the branch requires). That keeps the layers from coinciding; in a zero-thickness rigid model the
ears cannot fold past flat. Before it writes the document the script checks the erected bag: the
glue flap meets the front edge, the panels close round the bottom, the flaps overlap by `overlap`,
and every crease closes (`kinematics.closure_residual`, about 1e-13 mm). The erected state is the
`target:erected` frame. **The preview** plays the whole program, from the flat sheet (standing in
the front panel's plane) to the open bag on the table.

**Limits: what is not modelled, or needs the physics engine.**

- The glued closure (the seam and the bottom overlap) is given as interfaces, not as `glue` joins.
- The order of the layers in the bottom is a thickness question for the engine: gusset flaps,
  then ears, then the back flap, and the front flap outermost.
- The bag is not folded flat again, and its self-opening snap is not modelled.
- The gussets stay flat in the open bag: the pleat in the gusset centre bends the paper, which is
  the engine's job.

## Making one by hand

1. Export the blank (`svg`, `dxf`, `pdf` or `hpgl`) and cut it from kraft.
2. Score every line, including the 45° ear creases and the gusset centres.
3. Fold the four corners and glue the flap inside the front edge: a tube.
4. Push the two gusset flaps in. The front and back flaps rise, and their corners fold back into
   ears along the 45° creases.
5. Fold the back flap down, then the front flap over it, and glue the overlap.
6. Open the bag on its bottom. To store it flat, push the gussets in along their centre scores.

## Parameters

| id | meaning | default | range |
|---|---|---|---|
| `width` | front and back | 180 mm | 80–320 mm |
| `gusset` | depth of the bag (each gusset and the bottom) | 100 mm | 40–200 mm |
| `height` | height of the bag | 260 mm | 100–460 mm |
| `overlap` | overlap of the bottom flaps, glued | 20 mm | 8–40 mm |
| `stock` | `kraft-120`, `copy-80`, `cardstock-160` | `kraft-120` | — |

Presets: `lunch` (130 × 80 × 240 mm), `grocery` (305 × 178 × 430 mm) and `gift` (150 × 80 ×
200 mm in 160 g/m² card).

## History and sources

Paper bags were made by machine before 1870, but they were shaped like envelopes, weak and
narrow, and could not stand on their bases. Margaret E. Knight, working at the Columbia Paper Bag
Company, built a machine that cut, folded and glued paper into flat-bottomed bags. It was patented
as US 116,842 on 11 July 1871, after an interference case against Charles Annan, who had copied
her design (Wikipedia, «Margaret E. Knight», https://en.wikipedia.org/wiki/Margaret_E._Knight;
Lemelson-MIT, «Margaret Knight», https://lemelson.mit.edu/resources/margaret-knight). On 12 June
1883 Charles Stilwell was granted a patent for a machine that made square-bottomed bags, which he
called the self-opening sack (S.O.S.) because it stood open on its own (Wikipedia, «Charles
Stilwell», https://en.wikipedia.org/wiki/Charles_Stilwell). The blank and its hand-folding order
are MADFAM's own, computed by the cartridge: no bag machine's sequence or patent drawing is
reproduced.

## Provenance and licence

Original MADFAM blank and fold program. The lineage entry says so and credits the history of the
flat-bottomed bag. Published under CERN-OHL-W-2.0 like every object in the commons (see the commons
root `LICENSE`).
