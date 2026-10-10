# Paper lantern

| | Title | Summary |
|---|---|---|
| en | Paper lantern | The slit lantern: a sheet folded in half, cut from the fold, opened, rolled into a cylinder and glued. Push the top down and the strips between the slits bow outward. Make it step by step, or shape the finished lantern. |
| es | Farol de papel | El farol de ranuras: una hoja doblada por la mitad, cortada desde el doblez, abierta, enrollada en un cilindro y pegada. Al empujar la parte de arriba, las tiras entre las ranuras se arquean hacia fuera. Hazlo paso a paso o dale forma al farol terminado. |
| fr | Lanterne en papier | La lanterne à fentes : une feuille pliée en deux, découpée depuis le pli, ouverte, roulée en cylindre et collée. Appuyez sur le haut et les bandes entre les fentes se bombent vers l'extérieur. Fabriquez-la pas à pas, ou donnez forme à la lanterne finie. |
| pt | Lanterna de papel | A lanterna de fendas: uma folha dobrada ao meio, cortada a partir da dobra, aberta, enrolada num cilindro e colada. Empurre o topo e as tiras entre as fendas arqueiam para fora. Faça-a passo a passo ou dê forma à lanterna pronta. |

## What it is

A classic paper craft: fold a sheet in half along its length, cut slits from the fold that stop
short of the edges, open it, roll it into a tube and glue the ends together. Press the top down and
the strips between the slits bow outward into a lantern. This cartridge carries both the making
and the finished lantern.

## Geometry

The sheet is `circumference + g` long and `height` high, where `g` is a glue strip at the right
end, `min(12 mm, 0.45 s)` wide. `n` slits run up the middle, one at the centre of every strip of
width `s = circumference / n`, each from the bottom band to the top band (`band` high, uncut). The
middle fold crosses every slit at half height: cutting from the fold of the folded sheet makes each
slit in one cut, through both layers.

This lantern is **scored**. Score lines continue each slit through the top and bottom bands, and
two more cross the strips at the slit ends. They make the rolled lantern a crisp regular `n`-sided
prism whose facet edges pass through the slits, with each facet exactly one strip wide (radius
`s / (2 sin(π/n))`, 38.5 mm at the defaults). They also let each strip fold cleanly at its ends.
`pliego.papercut.analyze` confirms one connected piece and the stock's minimum feature, and the
cartridge refuses strips narrower than four times that minimum.

## The fold program

The cartridge has two modes, both previewed in the studio.

- **The lantern (`lantern`).** The `initial` frame is the rolled prism: every facet edge turns by
  `−360°/n`, printed side out. That pose is exactly isometric, and it lays the glue strip on the
  first half facet, where a `glue` join welds it. The program has one step: push the top down and
  the strips bow outward. In the rigid model each strip's lower half tilts outward by `γ` (the
  `bow` parameter) about its lower scored line, folds by `−2γ` at the middle crease, and the upper
  half tilts back by `γ`. The top ring then moves straight down by `(yt − yb)(1 − cos γ)`, 35.7 mm at
  the defaults. Every strip moves the same way, so the loops around the slits close; the script
  checks `pliego.kinematics.closure_residual` (below 10⁻¹² mm) before it writes the document. The
  program is `kinematic` and ends with the lantern bowed.
- **Make it (`make`).** Fold the sheet in half along its length, printed side out; cut the slits
  from the fold and open the sheet; let go. As spec §5.6 requires, letting go does not flatten the
  sheet: the middle fold springs back only by about the paper's yield angle.

Two limits are stated here. Between the scores, real paper still bends a little, so the strips bow
in a curve rather than as two flat panels; that needs the physics engine. And the bowed state is not
written as a frame: where a slit crosses the middle crease, the two neighbouring strips share one
vertex in a v1 document, and bowed strips would need two positions for it (v1 frames cannot
separate the two sides of a cut).

## Making one by hand

1. Print the PDF on cardstock and score the score lines with a bone folder against a ruler.
2. Fold the sheet in half along the middle line, printed side out.
3. Cut along the slit lines from the fold through both layers, stopping at the band.
4. Open the sheet, roll it into a tube with the printed side out, and glue the strip at the end
   onto the inside of the other end.
5. Push the top gently down so the strips bow outward. A paper strip glued inside the top rim
   makes a handle.

A plotter or craft cutter can score and cut the flat sheet from the SVG, DXF or HPGL export (score
pass first).

## Parameters

| Parameter | Meaning |
|---|---|
| `circumference` | sheet length before rolling, without the glue strip, mm |
| `height` | sheet height, mm |
| `slits` | number of slits (and of prism facets) |
| `band` | height of the uncut rim at the top and at the bottom, mm |
| `bow` | outward tilt `γ` of each half strip at the end of the lantern program, degrees |
| `stock` | cardstock, kraft, copy paper or foil paper |

## History and sources

The slit lantern is a widespread children's paper craft. Craft guides describe exactly these steps
(fold lengthwise, cut from the fold, open, form a tube and fasten the ends) and often present it as
a Chinese New Year decoration. This cartridge makes no claim about the craft's origin.

- FirstPalette, "Paper Lanterns" (kids' craft instructions):
  https://www.firstpalette.com/craft/paper-lantern.html

## Provenance and licence

The sheet layout, the scored prism model, the closure check and both fold programs are generated by
`main.py`; no published template is copied. The craft is traditional; this rendering is MADFAM
work, licensed CERN-OHL-W-2.0 (the commons' root licence).
