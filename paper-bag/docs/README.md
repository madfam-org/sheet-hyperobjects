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
glued overlap. The sheet is not cut at the corners: the gusset's bottom folds into a triangle, and
its corners fold back as ears tucked under the front and back flaps.

## Geometry

**The blank.** A row of panels: front (`width`), gusset (`gusset`), back (`width`), gusset, and a
15 mm glue flap, all `height` tall. The flap closes the tube inside the front. Each gusset is
scored down its centre (a flat score) so the made bag can pleat in. The blank is
2 × (`width` + `gusset`) + 15 mm wide.

**The bottom.** Below the bottom score the front and the back continue by an extension
`e` = `gusset`/2 + `overlap`/2, and each gusset by `gusset`/2. Folded in:

- each gusset extension carries two 45° creases from the bag's corners to its middle. It folds in
  flat as a triangle whose tip reaches the middle of the bottom, and the two corners outside the
  creases (the ears) fold back over the triangle;
- the back and front extensions fold over the triangles and the ears. They are full rectangles,
  `e` deep, so they overlap by `overlap` in the middle, where they are glued.

So the bottom has three layers at each corner: the gusset triangle inside, the ear, and the flap
outside. The flaps cover the whole bottom; from inside the bag each gusset shows as a triangle
(the diamond fold). At the glue-flap corner, the second gusset's ear has no front panel to join,
so it is a free flap that folds over its triangle like the others. The front's extension starts
1 mm in from that corner. The gusset triangles must not meet in the middle (`gusset` at most
`width` − 2 mm), and the overlap must stay under the gusset minus 4 mm, or the script stops.

**Corners as mechanisms.** A bottom corner is a degree-5 vertex. Around it lie the gusset, the
front (or back), the flap (90° each), the ear and the gusset triangle (45° each). With the bag's
corner held at 90° it keeps two degrees of freedom. From the tube state, which is singular (the
corner line and the extension line form one straight fold), the motion solver could take either of
two branches. On one, the flap folds in and the ear ends between the gusset triangle and the flap.
On the other, the flap would turn outward. The script solves the first branch once on a single
corner (its angles do not depend on the bag's size) and drives every corner of the bag along it.
With the 45° creases in the front flap instead, the reachable branch would leave the ears on the
outside of the flaps; that is why they are in the gussets.

## The fold program

`kinematic` mode, built with `pliego.Sequence.kinematic_path`, so every in-between state is an
exact rigid state (26 substeps from three key poses):

1. **tube:** fold the four corners to 90° and the glue flap inside the front;
2. **gussets in:** the gusset flaps fold halfway in; the front and back flaps rise with them and
   the gussets' ears fold back;
3. **bottom:** press the bottom flat and glue the overlap.

The bottom is shown just short of flat (gusset flaps at 89.6°, front and back flaps at 89.2°, as
the branch requires). That keeps the layers from coinciding; in a zero-thickness rigid model the
ears cannot fold past flat. Before it writes the document the script checks the erected bag: the
glue flap meets the front edge, the panels close round the bottom, the flaps overlap by `overlap`,
the ear lies between the gusset triangle and the flap, and every crease closes
(`kinematics.closure_residual`, about 1e-11 mm). The erected state is the
`target:erected` frame. **The preview** plays the whole program, from the flat sheet (standing in
the front panel's plane) to the open bag on the table.

**Glue that takes hold at its step.** The seam and the bottom overlap are `glue` joins with
`active_from` (sheet-document spec §5.19), their welds read from the erected pose: the seam takes
hold once the tube is formed (at the first `gussets-in` substep), the overlap in a short final
*press* step, so the program starts from the flat sheet and ends glued. The front flap's weld is
declared on the outside of the back flap (the order of making it by hand), because the rigid pose
alone cannot say which flap is outside.

**Limits: what is not modelled, or needs the physics engine.**

- In the physics engine a kinematic program poses the sheet rigidly, so the two welds are
  recorded state there, not forces.
- The front and back flaps reach the same angle, so where they overlap they cross; the glue join
  says which one lies outside, and the layer thickness is the engine's question.
- The bag is not folded flat again, and its self-opening snap is not modelled.
- The gussets stay flat in the open bag: the pleat in the gusset centre bends the paper, which is
  the engine's job.

## Making one by hand

1. Export the blank (`svg`, `dxf`, `pdf` or `hpgl`) and cut it from kraft.
2. Score every line, including the 45° ear creases and the gusset centres.
3. Fold the four corners and glue the flap inside the front edge: a tube.
4. Push the two gusset flaps in. Their corners fold back along the 45° creases into ears, and the
   front and back flaps rise.
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
