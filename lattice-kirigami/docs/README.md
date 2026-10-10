# Lattice kirigami

| | Title | Summary |
|---|---|---|
| en | Lattice kirigami | Rows of straight slits, staggered by half a pitch, turn a sheet into a mesh that stretches far beyond plain paper. Make it by hand from an accordion cut from alternate folds, or cut it flat and pull it open. |
| es | Kirigami de retícula | Hileras de ranuras rectas, desfasadas medio paso entre sí, convierten una hoja en una malla que se estira mucho más que el papel liso. Se hace a mano con un acordeón cortado desde dobleces alternos, o se corta en plano y se jala para abrirla. |
| fr | Kirigami en treillis | Des rangées de fentes droites, décalées d'un demi-pas, font d'une feuille un filet qui s'étire bien plus que le papier ordinaire. On le fabrique à la main à partir d'un accordéon découpé depuis un pli sur deux, ou on le découpe à plat et on le tire pour l'ouvrir. |
| pt | Kirigami em treliça | Fileiras de fendas retas, desencontradas meio passo entre si, transformam uma folha numa malha que estica muito além do papel liso. Faz-se à mão a partir de uma sanfona cortada em dobras alternadas, ou corta-se com a folha estendida e puxa-se para abrir. |

## What it is

A sheet of paper barely stretches: pull it and it tears before it grows by a few percent. Cut it
with rows of parallel slits, each row shifted by half a slit, and it becomes a net. Under a pull
the slits open into diamond-shaped holes, the strips between them bend and twist out of the plane,
and the sheet grows many times further before anything tears. The same pattern is used in
packaging, in stretchable electronics research and in children's paper crafts.

## Geometry

Every row holds slits of length `Ls` separated by ligaments of width `g`, so the pitch along a row
is `P = Ls + g`. Rows are `h` apart (the `spacing`). Odd rows are shifted by `P/2`: the ligaments of
one row sit at the middle of the slits of the next, and every other row starts and ends with a half
slit that runs off the side edge.

The generator places the slits on a grid of lines every `P/2` across the sheet. Row `j` carries a
slit centred on every other line, starting with line `j mod 2`, so the rows alternate. The sheet
width is rounded down to a whole number of half pitches, so the side edges fall on grid lines too.
That is why the ligaments at the side edges are half as wide (`g/2`), and why the cartridge refuses
a ligament whose half is below the paper's minimum feature. Two uncut grip bands, 15 mm high, run
along the top and the bottom.

`pliego.papercut.analyze` checks the result before it is drawn: one connected piece, and every
material bridge (ligaments and the strips between rows) at least the stock's minimum feature
(1.0 mm for copy and kraft paper, 1.5 mm for cardstock and polypropylene). The document declares
that minimum as `pliego:meta.min_feature_mm`.

## The fold program and the pull

The cartridge has two modes.

- **Make it (`fold-and-cut`).** The grid lines become pleats, valley and mountain in turn: the
  sheet folds into an accordion one half pitch wide. A slit centred on a fold line is a single cut
  from that fold through the two layers of the pleat, and a half slit at a side edge is a cut from
  the open edge. So the whole lattice is cut from alternate folds of the accordion, which is how it
  is made by hand. The program pleats the sheet, opens the accordion and lets go. Following spec
  §5.6, letting go does not flatten the sheet: the pleats spring back only by about the paper's
  yield angle and keep a little of their fold. The studio preview plays this program.
- **Stretch it (`stretch`).** The same pattern, cut flat, is pulled open. The bottom grip band is
  pinned and the top band is pinned to a `translate` driver moved by the **Pull** control. The pull
  range is a geometric estimate: each row of slits opening by a quarter of the slit length. The
  modes are separate because pinned grip bands would fight the pleats.

The opening itself needs the physics engine. Version 1 frames cannot separate the two lips of a
cut, and the opened mesh bends and twists its strips, which a rigid model cannot show. Until the
engine lands, the preview shows the stretch mode flat with its Pull control disabled.

## Making one by hand

1. Print the PDF (it shows the fold lines every half pitch) on copy paper, or mark the lines
   yourself. Fold the sheet back and forth on them into an accordion.
2. Hold the accordion so its folds point left and right. Cut straight slits from the left folds
   inward, stopping short of the right folds, every `2h` along the height.
3. Between those cuts, cut slits from the right folds inward, stopping short of the left folds.
   The two sets of cuts interleave.
4. Open the accordion, flatten it gently and pull the top and bottom edges apart.

A plotter, a craft cutter or a laser can cut the flat pattern from the SVG, DXF or HPGL export
instead. Polypropylene sheet makes a lattice that survives many pulls.

## Parameters

| Parameter | Meaning |
|---|---|
| `width` | sheet width, mm (rounded down to whole half pitches) |
| `height` | sheet height, mm (including the two 15 mm grip bands) |
| `slit_length` | length `Ls` of every full slit, mm |
| `ligament` | paper `g` left between two slits of a row, mm (half as wide at the side edges) |
| `spacing` | distance `h` between two rows of slits, mm |
| `stock` | copy paper, kraft, cardstock or polypropylene |

## History and sources

Staggered parallel slits are a long-standing paper-craft pattern and a well-studied cut geometry in
materials research. The two papers below test this geometry in thin sheets and describe its
behaviour: a stiff initial response, then a soft regime in which the strips rotate out of the
plane. This cartridge makes no quantitative claim of its own about strength or stretch.

- T. C. Shyu, P. F. Damasceno, P. M. Dodd, A. Lamoureux, L. Xu, M. Shlian, M. Shtein,
  S. C. Glotzer and N. A. Kotov, "A kirigami approach to engineering elasticity in nanocomposites
  through patterned defects", *Nature Materials* 14, 785–789 (2015).
- M. Isobe and K. Okumura, "Initial rigid response and softening transition of highly stretchable
  kirigami sheet materials", *Scientific Reports* 6, 24758 (2016).

## Provenance and licence

The slit pattern, the accordion fold-and-cut and the fold program are generated by `main.py`; no
published cut file is copied. Original MADFAM work, licensed CERN-OHL-W-2.0 (the commons' root
licence).
