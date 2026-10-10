# Frog base

| | Title | Summary |
|---|---|---|
| en | Frog base | The traditional frog base: a preliminary base with its four flaps squashed and petal-folded, folded move by move on layer-ordered flat states. Every state is checked, every step of the preview is a rigid motion, and the unfolded pattern has the base's four-fold symmetry. |
| es | Base de rana | La base de rana tradicional: una base preliminar con sus cuatro solapas aplastadas y plegadas en pétalo, plegada paso a paso sobre estados planos con orden de capas. Cada estado se comprueba, cada paso de la vista previa es un movimiento rígido y el patrón desplegado tiene la simetría de cuatro vías de la base. |
| fr | Base de la grenouille | La base de la grenouille traditionnelle : une base préliminaire dont les quatre rabats sont écrasés puis pliés en pétale, pliée geste par geste sur des états à plat avec ordre des couches. Chaque état est vérifié, chaque pas de l'aperçu est un mouvement rigide et le motif déplié a la symétrie d'ordre quatre de la base. |
| pt | Base do sapo | A base do sapo tradicional: uma base preliminar com as quatro abas esmagadas e dobradas em pétala, dobrada passo a passo sobre estados planos com ordem de camadas. Cada estado é verificado, cada passo da pré-visualização é um movimento rígido e o padrão desdobrado tem a simetria de ordem quatro da base. |

The frog base is the starting point of the traditional frog and of the lily and the iris (see
`lily`). Fold a preliminary base, squash each of its four flaps into a kite, then petal-fold each
kite. The result is a long, narrow diamond with eight flaps: four points at the open end, which are
the corners of the square, and four petals, whose tips are the midpoints of its edges.

## Geometry

The sheet is a square of side `size`. As in `paper-crane`, nothing is drawn from a crease pattern:
every move is a `pliego.flatops` operation on a layer-ordered flat state, each result is checked
by `pliego.flatcheck` (a complete, consistent layer order; taco–taco, taco–tortilla and
tortilla–tortilla conditions; Kawasaki, Maekawa and big–little–big at every vertex), and the crease
pattern is the base unfolded. The cartridge also checks that the unfolded pattern is unchanged by
a quarter turn about the centre of the square: the four-fold symmetry of the traditional base.

At the defaults the base has 40 faces; the pattern has 40 crease lines, 22 valley, 8 mountain and
10 left flat, meeting at 11 interior vertices.

The petal fold on a squashed flap differs from the one in the bird base, and the kernel works out
which way each layer moves:

- After the squash, the top layer of each kite reaches only halfway down: its lower edges are
  the raw edges of the paper, meeting at the midpoint of an edge of the square, which lies on the
  centre line. That point is the one the petal fold lifts. Its kite lines run at 45° to the centre
  line, from that point to the kite's upper edges.
- Under each side of the top layer lies the kite's lower layer, joined to it along the upper edge.
  It must open flat with the side and stay joined, so it folds along the line that keeps both
  conditions: the axis of reflection in the hinge, then the kite line, then the upper edge. On a
  square flap (the bird base) that line is the kite line itself. Here it runs from the kite point
  down to the bottom of the kite. `pliego.flatops.petal` computes it in both cases.

## The fold program

The program has 16 operations, 104 steps at the defaults:

1. Fold the square along a diagonal, fold the triangle in half, squash the top flap; turn over and
   squash the other: the preliminary base.
2. Squash a flap; turn a page (the kite's half over to the other side); squash the next flap; turn
   over and do the same on the back.
3. Petal-fold the front face; turn over and petal-fold the back face; turn a page and petal-fold
   the third face; turn a page the other way and petal-fold the fourth.

**What the preview shows.** Every step is a rigid motion of the faces it moves, so the studio
preview shows it without tearing: page turns are single rotations, squashes and petal folds
follow their spherical linkages at the moving vertex, sampled until the blend between two samples
tears less than 0.5 mm. The document carries the reference frame `target:flat-folded`. The
program is `physical`: the engine drives the creases with the hand.

**What it leaves out.** When folding by hand, you usually precrease the petal folds first (fold
the lower edges to the centre and the top down, and unfold). The program makes each petal fold
directly; the precreases do not change the folded state.

## Making one

1. Fold a preliminary base, open end toward you.
2. Lift one flap upright, open it and squash it flat into a kite. Fold the kite's half over like a
   page and squash the flap underneath. Turn over and repeat on the back.
3. On each face in turn: lift the point where the top layer's edges meet, fold it up along the line
   between the face's side points, and let the sides fold in to the centre line. Turn pages to
   reach each face.

## Parameters

| Parameter | Meaning | Default |
|---|---|---|
| `size` | side of the square (mm), 80–300 | 150 |
| `stock` | `kami`, `washi-kozo-30`, `copy-80` | `kami` |

Presets: `large-24cm` (a 240 mm square).

## History and sources

The frog base is a traditional base, named after the traditional frog folded from it. Its
derivation from the preliminary base by squash and petal folds is described in Robert J. Lang,
*Origami Design Secrets: Mathematical Methods for an Ancient Art*, 2nd ed., CRC Press, 2011. The
layer conditions checked here come from Marshall Bern and Barry Hayes, "The complexity of flat
origami", *Proceedings of the 7th ACM-SIAM Symposium on Discrete Algorithms* (1996); Kawasaki's and
Maekawa's theorems are as presented in Thomas C. Hull, *Origametry: Mathematical Methods in Paper
Folding*, Cambridge University Press, 2020. No diagram is reproduced; the geometry and the program
are computed by this cartridge.

## Provenance and licence

Traditional base (public domain); original geometry and program by Innovaciones MADFAM. Published
under CERN-OHL-W-2.0, like every object in the commons (see the commons root `LICENSE`).
