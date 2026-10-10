# Pillow box

| | |
|---|---|
| **en** | The curved-score pillow pack from inside dimensions: bulging panels, side scores and lens flaps whose curved scores come from an exact reflection construction. The flattened tube pops open in one exact rigid motion. |
| **es** | La caja almohada de marcados curvos, a partir de las medidas interiores: paneles abombados, marcados laterales y solapas en forma de lente cuyos marcados curvos salen de una construcción exacta por reflexión. El tubo aplanado se abre en un solo movimiento rígido y exacto. |
| **fr** | Le berlingot à rainages courbes, à partir des dimensions intérieures : panneaux bombés, rainages latéraux et rabats en lentille dont les rainages courbes viennent d'une construction exacte par réflexion. Le tube aplati s'ouvre en un seul mouvement rigide et exact. |
| **pt** | A caixa travesseiro de vincos curvos, a partir das medidas internas: painéis abaulados, vincos laterais e abas em forma de lente cujos vincos curvos vêm de uma construção exata por reflexão. O tubo achatado abre-se num só movimento rígido e exato. |

## What it is

A pillow box is a small pack cut from one blank of paperboard: a tube with two bulging faces,
closed at each end by two lens-shaped flaps that fold inward along curved scores. It needs no
tuck flaps and only one glue line, and it ships flat. This hyperobject generates the blank from
the contents' inside dimensions — closed width, tip-to-tip length and thickness at the middle —
in folding boxboard, SBS, cardstock or kraftliner, with every dimension compensated for the
board's caliper t (the centre-line rule: inside + t). The seam is a lap joint down the middle of
the back face, so the blank is symmetric about its centre.

## Geometry

**Panels.** Each face bends into a cylinder whose straight generators (rulings) run along the
box. Its cross-section is a polygon of `facets` equal facets turning by equal angles — a discrete
circular arc — solved so that two of them span the closed width and bulge to half the thickness.
The middle facet lies level, so `facets` is odd.

**Ends: the reflection construction.** An end of the box is the plane `Y + k·|Z| = y_end`
(k = tan `end_tilt`), tilted from the cross-section by `end_tilt`. The board beyond that plane is
reflected across it. A developable surface cut by a plane and reflected is an exact curved fold —
both sides stay developable and the fold angle varies along the crease — so the folded end is a
true state of the board, not an approximation of one. With `z(u)` the face's height above the
box's mid-plane at flat position `u`:

- the curved score is `y = y_end − k·z(u)`: a planar ellipse in 3-D, a cosine-like curve on the
  die (the score is curved because the face is);
- the flap's outer cut is where the reflected board reaches the mid-plane,
  `y = y_end + z(u)·(1 − k²)/(2k)`, so the front and back flaps of one end meet edge to edge;
- both curves meet at the side scores (z = 0): every flap is a lens. At `end_tilt` = 30°
  (k = 1/√3) the score and cut sagittas are equal and the lens is symmetric.

The curves are polylines with one vertex per ruling. The rulings are bending lines of plain board,
written as FOLD `F` lines with treatment `none` (patched into the built document, because the
kernel's authoring API scores every line it folds), so the die carries only the two straight side
scores and the curved scores. At the defaults (90 × 160 × 34 mm, FBB 300) the facets are
11.0 mm wide, both sagittas are 9.95 mm, and the curved score folds from 120° at the middle of
the face to 133° at the tips.

## The fold program

The program is kinematic and every pose is exact:

1. **Fold the back's second half over the front**, then **fold the front over and glue the
   lap**: two straight folds give the flattened, glued tube, the form in which a pillow box can be
   stored and shipped flat.
2. **Squeeze the tube** (eight key poses). Erecting is a one-parameter family of exact
   rigid-ruling states: for an end tilt ψ running from 90° to `end_tilt`, every height scales as
   `z'(u) = z(u)·k / tan ψ` while the scores stay where the die put them, and the board beyond
   each end plane is reflected again. The panels bulge and all four lens flaps fold in together,
   as a pillow box is popped open by hand. The script checks each pose with
   `pliego.kinematics.closure_residual` (about 3·10⁻⁵ mm, the coordinate grid's floor).

The preview poses the blank from its first face, which is the level half-facet at the seam, so
the box erects in place and finishes resting on its back. **Limits.** With the rulings fixed,
one end cannot close on its own once the faces bulge: the motion solver finds no rigid path from
the open, bulged tube, so in this model both ends close together. Real board also bends a little
between the rulings and lets one end close first; that, the glue weld and the board's spring
are the physics engine's part.

## Making one by hand

Print the die at 100 %. Score the two side scores and the curved scores with a blunt stylus or
a scoring wheel against a ruler and a flexible curve, cut the outline, and glue the lap inside the
other half of the back. Squeeze the flat tube at its side scores: the faces bulge, and the lens
flaps start to fold in along their scores. Press each pair of flaps home with your thumbs.

## Parameters

| Parameter | Range | Meaning |
|---|---|---|
| `width` | 40–250 mm | closed width across the side scores, inside |
| `length` | 60–400 mm | tip to tip, inside |
| `thickness` | 0.12–0.6 × width | bulge at the middle, inside |
| `end_tilt` | 20–40° | tilt of the end planes; 30° gives symmetric lenses |
| `facets` | 5–15 (odd) | facets per face; more give smoother curves |
| `stock` | FBB 300, SBS 350, cardstock 300, kraftliner 150 | board |
| `branding` | on / off | sample brand artwork on the front's middle facet (`pliego:artwork`) |

Presets: party favour, soap bar (SBS), flat kraft sleeve.

## History and sources

The pillow box is a common folding-carton style used for small gifts, soap and favours; no single
origin is documented in the sources consulted, and none is claimed here. The geometry of curved
folds — that a planar crease makes the two sides mirror images across the crease's plane, and that
reflecting a developable surface across a plane yields a valid curved fold — is established in
the curved-folding literature:

- D. Fuchs and S. Tabachnikov, "More on paperfolding", *The American Mathematical Monthly* 106(1),
  1999, pp. 27–35.
- M. Kilian, S. Flöry, Z. Chen, N. J. Mitra, A. Sheffer and H. Pottmann, "Curved folding",
  *ACM Transactions on Graphics* 27(3), 2008 (SIGGRAPH).
- J. Mitani, "Column-shaped origami design based on mirror reflections", *Journal for Geometry and
  Graphics* 16(2), 2012.
- Wikipedia, *Folding carton* — https://en.wikipedia.org/wiki/Folding_carton
- Pliego sheet-document spec, `pliego:dielines` (§5.9), and `pliego.dieline` (in the Pliego
  repository).

## Provenance and licence

Original MADFAM design: the faces, the reflection-construction scores and cuts, the centre-seam
layout and the erecting motion are computed in `main.py` (the `lineage` entry says so, licence
`original`). No catalogue drawing is reproduced. The sample brand mark is original placeholder
artwork. Licence CERN-OHL-W-2.0 (both manifest fields).
