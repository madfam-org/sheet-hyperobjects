# Gift wrap

| | Title | Summary |
|---|---|---|
| en | Gift wrap | Wrapping a box in paper, standard or diagonal, as an exact fold program round a rigid box, with the minimum paper size computed. |
| es | Envoltura de regalo | Envolver una caja en papel, a la manera clásica o en diagonal, como una secuencia de pliegues exacta alrededor de una caja rígida, con el tamaño mínimo de papel calculado. |
| fr | Emballage cadeau | Emballer une boîte dans du papier, de façon classique ou en diagonale, par une séquence de pliage exacte autour d'une boîte rigide, avec le format de papier minimal calculé. |
| pt | Embrulho de presente | Embrulhar uma caixa em papel, do jeito clássico ou na diagonal, como uma sequência de dobras exata em volta de uma caixa rígida, com o tamanho mínimo de papel calculado. |

## What it is

Two ways of wrapping a box in one sheet of paper, without cutting the paper at the corners:

- **`standard`:** the paper goes round the box and overlaps on top. At each end the side flaps
  are pushed in and the top and bottom flaps fold over them.
- **`diagonal`:** the box sits at 45° in the middle of a square sheet. The sheet's four corners
  come up over the four sides and onto the top.

The box is a rigid reference: a box net folded shut and posed on the table. It is a fixed board
(a kinematic sheet whose mechanism, `box-held`, does not move it), so the physics engine treats it
as rigid too. The cartridge folds the paper round it, computes the **minimum paper** for the box,
checks the paper you give it and trims what the wrap does not use.

## Geometry

The paper's panels are sized for the box plus the thickness of the paper and the box's card, so
the paper clears the box. A footprint's two sides are sorted, so `box_length` is always the longer
one.

**Standard.** Panels round the girth: top, front, bottom, back, and the overlap strip that comes
back over the top. At each end every panel continues:

- the top and the bottom by `e` = height/2 + overlap/2. These are the end flaps. Each covers half
  the end and more, so the two overlap by `overlap`, where they are taped;
- the front and the back by height/2. These are the side flaps. Each carries two 45° creases from
  the box's corners to its middle, folds in as a triangle, and its two corners (the ears) fold
  back over the triangle.

So each corner of an end has three layers: the side triangle against the box, the ear, and the
end flap outside. The script checks that order on the wrapped state. The side triangles meet at
most at their tips, so the end must be at least as wide as it is high: a taller box is laid on its
side, and the script says so. **Minimum paper:** (2 × (width + height) + 10 mm) by
(length + height + 8 mm), with 10 mm of overlap on top and 8 mm at the ends. The `overlap`
parameter (default 20 mm) sets how much is kept, and the rest is trimmed.

**Diagonal.** The sheet is a square of side (length + width + 2 × height)/√2, turned 45° to the
box, with the box in the middle. That is the **minimum paper**: the square's edges pass exactly
through the box's top corners, and the corners beyond the short sides reach exactly the long axis
of the top. Beyond each side of the box's footprint lies a flap. It rises against the side, and the
part beyond the side's top edge folds onto the top. Between two flaps, at each corner of the box,
lies a wedge of paper. It folds in half along its bisector into a pleat, which lies under the long
side's flap. The pleat reaches exactly the box's top corner. On top, the short sides' triangles
meet the long sides' flaps edge to edge along the diagonals. For a square box the four triangles
meet in the middle; on a longer box the two long flaps overlap by (length − width). A larger sheet
must be trimmed to the square.

**Corners as mechanisms.** In both modes every corner of the box is a degree-5 vertex: two faces
of the box (or a face and the footprint), the flap that covers it (90° each), and a pleat or ear
and a triangle (45° each). From its straight-folded start it has two branches. The script solves,
once on a single corner, the branch on which the ear ends tucked between the triangle and the
flap, and drives every corner along it. This is the same corner as the bottom of the paper bag
(`paper-bag`).

## The fold program

`kinematic` mode, built with `pliego.Sequence.kinematic_path`, so every in-between state is an
exact rigid state.

- **Standard (36 substeps):**
  1. down the front and under the box;
  2. up the back and over the top (tape the overlap);
  3. at each end, push the side flaps in (they fold into triangles; the top and bottom flaps come
     down);
  4. at each end, fold the top flap down and the bottom flap up over it (tape).
- **Diagonal (32 substeps):**
  1. the left corner over the short side and under the box;
  2. the right corner up against the other short side;
  3. the front and back corners up (the paper at each corner of the box folds into a pleat under
     the long sides);
  4. the right corner over the top;
  5. the front corner over, then the back corner over it (tape).

**The preview** plays both programs. The studio roots each sheet's face tree on the face holding
its lowest-left vertex. For the standard wrap that is the paper's top panel. For the diagonal wrap
it is the left corner's top triangle. So the sheet starts flat at the height of the box's top, off
to one side, and folds down round the box. This is the same motion as wrapping the box upside down
and turning it over.

**Limits and the physics engine.** Overlapping layers stop just short of flat (89.2°–89.6°, as the
corner branch requires) so they do not coincide. The real paper's bending round the box's edges,
the thickness of the stacked layers at the corners and the tape are the physics engine's job. The
department-store diagonal wrap of Japan (*naname-tsutsumi*) also starts with the box set
diagonally on the sheet. It then rolls the box over its edges, folds pleats as it goes and ends
in a pocket. That sequence is not reproduced here: the `diagonal` mode is the four-corner diagonal
wrap described above.

## Making one by hand

1. Measure the box. The script prints the minimum paper, and the size to trim your sheet to.
2. **Standard:** lay the box upside down on the back of the paper, wrap the girth and tape the
   overlap. At each end, push the two sides in so that their corners fold into triangles, then fold
   the top flap down and the bottom flap up over it, and tape. Turn the box over.
3. **Diagonal:** cut the paper to the printed square, lay it printed side down and set the box
   upside down in its middle at 45°. Bring a short-side corner up and over, then the other. Raise the long-side corners,
   tucking the paper at each corner of the box into a pleat under the long side. Fold the corners
   over the top and tape where they meet. Turn the box over.

## Parameters

| id | meaning | default | range |
|---|---|---|---|
| `box_length`, `box_width`, `box_height` | the box | 240 × 160 × 60 mm | 30–500, 30–500, 10–300 mm |
| `paper_width`, `paper_length` | the paper you have (standard: round the box × along it) | 500 × 500 mm | 100–2000 mm |
| `overlap` | overlap kept on top and at the ends (`standard`) | 20 mm | 10–80 mm |
| `stock` | `copy-80`, `kraft-120`, `kami`, `washi-kozo-30` | `copy-80` | — |

Presets (both modes): `book` (240 × 170 × 40 mm), `jewellery` (90 × 90 × 40 mm), `cube` (100 mm)
and `large` (330 × 200 × 120 mm), each with a sheet large enough for both wraps.

## History and sources

Wrapping gifts in paper is old. In China, gifts of money were wrapped in paper envelopes as early
as the Southern Song dynasty. The decorated gift paper of today spread from 1917, when the Hall
brothers of Kansas City sold French envelope liners as wrapping paper (Wikipedia, «Gift wrapping»,
https://en.wikipedia.org/wiki/Gift_wrapping). In Japan, department stores, confectioners and other
sellers of gifts use the diagonal wrap *naname-tsutsumi*. The box is set on the sheet diagonally,
with three of its corners inside the paper's edges and one outside, and wrapped by rolling it over
(Musubi Kiln, «How to wrap a present like a Japanese gifting pro»,
https://musubikiln.com/blogs/journal/how-to-wrap-a-present-like-a-japanese-gifting-pro). The
crease patterns, the minimum paper and the fold programs here are computed by the cartridge from
the box's geometry.

## Provenance and licence

Original MADFAM crease patterns and fold programs. The lineage entry says so and credits general
wrapping practice. Published under CERN-OHL-W-2.0 like every object in the commons (see the commons
root `LICENSE`).
