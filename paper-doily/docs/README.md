# Paper doily

| | Title | Summary |
|---|---|---|
| en | Paper doily | Radial lace by fold-and-cut: a square folded into a 4-, 6- or 8-fold wedge and cut once into a round doily with a scalloped edge and rings of small holes. The lace density sets how many rings and holes there are. |
| es | Carpeta de papel | Encaje radial doblando y cortando: un cuadrado doblado en una cuña de 4, 6 u 8 ejes y cortado una sola vez en una carpeta redonda con orilla festoneada y anillos de agujeritos. La densidad del encaje fija cuántos anillos y agujeros lleva. |
| fr | Napperon en papier | Dentelle rayonnante par pliage-découpage : un carré plié en un coin d'ordre 4, 6 ou 8 et découpé une seule fois en un napperon rond, bord festonné et anneaux de petits jours. La densité de la dentelle fixe le nombre d'anneaux et de jours. |
| pt | Toalhinha de papel | Renda radial por dobra e corte: um quadrado dobrado numa cunha de 4, 6 ou 8 eixos e cortado uma só vez numa toalhinha redonda com borda recortada e anéis de furinhos. A densidade da renda define quantos anéis e furos ela tem. |

## What it is

A paper doily imitates lace: a round sheet with a scalloped edge and rings of small openings. Here it
is made the way a snowflake is: fold a square into a narrow wedge, cut once through every layer and
unfold. One parameter, the **lace density**, turns a few large holes into many small ones.

## Geometry

The square is folded through its centre into a wedge of `180°/n` with `2n` layers
(`pliego.simplefold`), with the same fold sequences as the window flower: 4-fold (45°, 8 layers),
6-fold (30°, 12 layers) or 8-fold (22.5°, 16 layers). It unfolds with `n`-fold rotation and `n`
mirror lines. The lace is laid out in polar coordinates inside the wedge, from the edge inward:

- **Scallops.** Up to `density + 1` per wedge, as many as fit with a picot (a small round hole)
  in each, at least 1.2 times the minimum feature in radius.
- **Lace rings.** `density + 2` rings, never pitched closer than four minimum features. Each ring's
  holes are circles, radial diamonds or petals in turn, about half the ring pitch in size. A ring
  holds as many holes as its inner circumference allows with 2.5 minimum features between holes,
  so every hole keeps its bridges, across the mirror lines too. A ring too narrow for even one hole
  is left solid.
- **Rosette.** One petal per wedge around a small round centre hole, when the wedge is wide enough.

`pliego.foldcut` maps the cut through every layer and unfolds it, and `pliego.papercut.analyze`
must find one connected piece with every bridge at least the stock's minimum feature (1.0 mm for
copy paper, kami and washi; 1.5 mm for tissue).

**A kernel limit, worked around.** For some lace layouts, kernel 0.2.0's hole bridging (the `J`
edges that make every face simple) leaves a self-touching face, which the document check rejects.
The script checks every face before it writes the document. If one is not simple, it tries again
with the holes shrunk in 3 % steps (up to three times), then with the picots moved further in from
the scallops and the same shrink steps, and it fails loud if none of these eight layouts works. The
printed `hole_scale` and `picot_inset` say which layout was used (1.00 and 1.5 at the defaults). A
sweep over every symmetry, density and five sizes from 120 to 300 mm built a valid document in
every case. The issue is reported to the kernel.

## The fold program

The program re-folds the cut sheet along its creases in the original order, one step per fold,
then opens it and presses it flat (the hand holds it). It does not let go: following spec §5.6, a
release would leave every crease standing at about the paper's yield angle. Version 1 documents
describe the sheet after cutting, so the preview shows the folding on the cut paper.

## Making one by hand

1. Fold a square of thin paper as in the program; thin paper folds into many layers best.
2. Transfer one wedge of the exported cut lines onto the top layer.
3. Cut the edge with scissors and the holes with a craft knife on a mat.
4. Unfold slowly and press flat under a book.

A plotter, craft cutter or laser can instead cut the flat, unfolded doily from the SVG, DXF or HPGL
export, which is the easier way to the finest lace.

## Parameters

| Parameter | Meaning |
|---|---|
| `folds` | symmetry: 4-, 6- or 8-fold (8, 12 or 16 layers) |
| `density` | lace density, 1 to 5: more rings of smaller holes, and more scallops |
| `size` | side of the starting square, mm |
| `stock` | copy paper, kami, kozo washi or tissue paper |

## History and sources

Paper doilies are a familiar household and craft item. This cartridge describes only the
geometry it generates and makes no historical claim. The mathematics of cutting folded paper is
studied in the paper below.

- E. D. Demaine, M. L. Demaine and A. Lubiw, "Folding and cutting paper", in *Discrete and
  Computational Geometry* (JCDCG '98), Lecture Notes in Computer Science 1763, Springer (2000).

## Provenance and licence

The folds, the lace layout and the checks are generated by `main.py`; no published doily template
is copied. Original MADFAM work, licensed CERN-OHL-W-2.0 (the commons' root licence).
