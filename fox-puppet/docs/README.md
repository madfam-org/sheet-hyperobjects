# Fox puppet · Zorro títere

| | Title | Summary |
|---|---|---|
| en | Fox puppet | The talking fox from one square: the traditional organ base folded exactly, a head shaped by this cartridge's own folds, and a pleated mouth that opens and closes as rigid paper in the preview. |
| es | Zorro títere | El zorro que habla, con un solo cuadrado: la base de órgano tradicional doblada con exactitud, una cabeza con pliegues propios de este cartucho y una boca plisada que se abre y se cierra como papel rígido en la vista previa. |
| fr | Renard marionnette | Le renard qui parle, dans un seul carré : la base de l'orgue traditionnelle pliée exactement, une tête façonnée par les plis propres à cette cartouche et une bouche plissée qui s'ouvre et se ferme comme du papier rigide dans l'aperçu. |
| pt | Raposa fantoche | A raposa que fala, com um só quadrado: a base de órgão tradicional dobrada com exatidão, uma cabeça moldada pelas dobras próprias deste cartucho e uma boca pregueada que abre e fecha como papel rígido na pré-visualização. |

## What it is

A paper fox whose mouth opens and closes. The traditional fox puppet is folded from the
**organ base**: a square folded in half, its sides folded to the middle and both side flaps
squashed into roof-shaped points. This cartridge folds that base exactly. The head is its own:
the lower jaw's side folded behind and its corner turned under, the other flap opened out into a
pointed ear, and a pleat creased from the middle of the folded edge. When the pleat folds, the two
jaws turn about the mouth's corner. Published diagrams of the traditional head differ from one
another and none is copied here, so the head is credited to this cartridge, not to tradition.

Two modes: **fold** is the whole program, from the flat square to the finished fox talking twice;
**talk** starts from the finished fox (mouth closed) and its **mouth** control opens and closes it.
The fox colour is the back of the square; the front becomes the inside of the mouth. The optional
drawn face prints an eye on each cheek and a nose at the tip of the upper jaw (an original drawing
made by the script).

## Geometry

The square has side `S`; `h = S/2`, `q = S/4`, sheet-local mm, y up. The folds, in the folded
frame of each step:

1. **Half:** the top edge to the bottom edge along `y = h` (the fox colour outside).
2. **Middle crease:** `x = h`, folded and unfolded.
3. **Sides:** `x = 3q` and `x = q`, through both layers.
4. **Squashes:** each side flap stands on its side fold, opens between its two layers and is
   pressed flat symmetric about the fold. The squash line runs from the top of the side fold,
   `(3q, h)`, to the middle crease at `(h, q)` (mirror on the left). This is the organ base.
5. **Chin:** the lower jaw's point folded behind along `x = 3q`.
6. **Taper:** the jaw's outer corner turned under along `(h, 0)–(3q, q)`.
7. **Ear:** the upper flap opened out flat along `x = q`; its bottom corner folded up along
   `(q, 0)–(0, q)`; its front edge folded behind along `(q, 0)–(q/2, (q + h)/2)`.
8. **Mouth creases:** from `M = (h, h)`, the middle of the folded edge, to `(q, 0)` (the nose line,
   which bounds the upper jaw) and to `(h − h·tan(½·atan ½), 0) ≈ (0.764 h, 0)` (the pleat line,
   which halves the 26.57° wedge between the nose line and the middle crease).

**The mouth.** The wedge between the nose line and the middle crease is the mouth's lining, on
both halves of the folded square. Its two halves (each `a = ½·atan ½ ≈ 13.28°` at `M`) fold along
the pleat line like a fan while the jaws turn about `M`; both ridges of the folded edge stay
pressed flat. The mouth's opening angle `φ` and the pleat's fold angle `β` satisfy
`cos φ = cos² a + sin² a · cos(180° − β)`: the pleat lies flat at `φ = 2a ≈ 26.57°` and is
folded shut at `φ = 0`. The cartridge closes the mouth to `φ = 2°` (`β ≈ 171.3°`) and opens it to
the `gape` parameter (22° by default, `β ≈ 67.7°`).

## The fold program

Fold mode is 19 operations and 60 preview steps. Each flat fold is an operation of
`pliego.FoldProgram` on a layer-ordered flat state; after every one the kernel checks the layer
order (taco and tortilla conditions, transitivity) and Kawasaki and Maekawa at every vertex, and
the crease pattern is the final state unfolded (28 faces, 34 creases; the flat-foldability check
of the finished pattern passes at all 6 interior vertices). The flat folds are exact; each
squash is a spherical linkage exact at its samples, and the preview's straight-line blend
between samples opens gaps of at most 0.4 mm.

The mouth steps are rigid 3-D steps on the whole pattern (`FoldProgram.kinematic`): the pleat
crease is driven to its angle, the nose and middle creases follow, every other crease holds, and
the kernel solves loop closure at every vertex. Every sample is an exact rigid state; the
preview's blend between samples opens gaps of about 0.03 mm, and no face passes through
another (penetration 0 mm). Talk mode starts after the first closing step: open, close, open,
close. The studio shows the talking fox standing on its side, ear up.

**What the preview shows and what needs the physics engine.** The preview shows every fold and
the mouth opening and closing as rigid paper. In a real fox the paper also bends: the pleat
rounds, the jaws flex under the fingers and the squashed points spring back a little. Those are
the physics engine's part. A vertex pose (`FoldProgram.vertex_pose`) cannot drive this mouth:
the organ base's squashes join the two halves of the square away from the mouth's corner, so the
kernel's rigid step over the whole pattern drives it instead.

## Making one by hand

1. Start with the fox colour face down. Fold the square in half, top edge to bottom edge.
2. Fold it in half side to side and unfold.
3. Fold both sides to the middle crease.
4. Lift one side flap, open it from below and squash its top flat into a point. Repeat on the
   other side: this is the organ base.
5. Fold the right-hand point behind, to the middle (this side becomes the lower jaw), and turn its
   outer bottom corner under.
6. Open the left flap out flat again; fold its bottom corner up along the diagonal, then fold the
   front edge behind to leave a pointed ear.
7. Crease two lines from the middle of the top folded edge: one to the bottom of the left side
   fold, one halfway between it and the middle crease.
8. Push the pleat in: the jaws close. Pinch the back of the head and move the lower jaw to make
   the fox talk.

This version is worked by pinching. The traditional hand puppet takes fingers in pockets; this
head has no finger pocket in the upper jaw.

## Parameters

| Parameter | Meaning |
|---|---|
| `size` | side of the square, 120–400 mm (200 by default) |
| `gape` | how far the mouth opens, 6°–26° (22° by default); the pleat lies flat at about 26.6° |
| `face` | `drawn`: an eye on each cheek and a nose on the snout; `plain`: no print |
| `stock` | kami, copy paper 80 g/m² or kraft paper 120 g/m² |

Presets: finger puppet (15 cm kami), hand puppet (25 cm kami), a square cut from A4 copy paper
(210 mm, plain face) and a big fox (35 cm kraft, mouth opening 26°).

## History and sources

The organ base takes its name from the paper organ (piano) folded from it. Russell and co-authors
describe it as the starting point for the piano, the fox puppet, the GI hat and the house, and
give its folding steps: fold in half top to bottom, crease the middle, fold the outer edges to the
middle crease, then squash each side by separating its two layers while pressing down from the
top.

Gilad Aharoni's origami database lists a "Fox puppet" credited to tradition in many books,
among them Isao Honda's *The World of Origami*, Robert Harbin's *Origami 2* and John Montroll's
*Easy Origami*. The traditional head's exact folds are not reproduced here; the head is this
cartridge's design.

- R. Alan Russell, William DeMichele, Nicole Holland, Caroline Lanzarone and Nettie Leepson,
  "The Organ Base in Origami: Teaching Mathematics and Creativity in the Elementary Classroom",
  *Bridges 2019 Conference Proceedings*, pp. 651–658:
  https://archive.bridgesmathart.org/2019/bridges2019-651.pdf
- Gilad Aharoni, Gilad's Origami Page, origami database, entries "Fox puppet" (Traditional):
  https://www.giladorigami.com/
- Marshall Bern and Barry Hayes, "The complexity of flat origami", *Proceedings of the 7th
  ACM-SIAM Symposium on Discrete Algorithms*, 1996 (the layer-order conditions the kernel checks).

## Provenance and licence

The organ base is traditional and credited to tradition; the head, the mouth's rigid motion and
the face drawing are original to this cartridge (two lineage entries in the manifest). Every line
is generated by this cartridge with the Pliego kernel; no published diagram or crease pattern is
copied. Licence CERN-OHL-W-2.0 (both manifest fields).
