# Fish base

| | Title | Summary |
|---|---|---|
| en | Fish base | Two rabbit ears on one diagonal: kite folds from both ends, then each side corner rises as a flap laid toward the same end. Two degree-4 vertices, each folded along its exact rigid path. |
| es | Base de pez | Dos orejas de conejo sobre una diagonal: pliegues de cometa desde los dos extremos y luego cada esquina lateral se levanta como una solapa que se acuesta hacia el mismo extremo. Dos vértices de grado 4, cada uno doblado por su trayectoria rígida exacta. |
| fr | Base du poisson | Deux oreilles de lapin sur une diagonale : des plis cerf-volant depuis les deux bouts, puis chaque coin latéral se dresse en rabat couché vers le même bout. Deux sommets de degré 4, chacun plié le long de sa trajectoire rigide exacte. |
| pt | Base do peixe | Duas orelhas de coelho sobre uma diagonal: dobras de pipa desde as duas pontas e depois cada canto lateral ergue-se como uma aba deitada para a mesma ponta. Dois vértices de grau 4, cada um dobrado pela sua trajetória rígida exata. |

The fish base is the kite base folded from both ends. Crease the diagonal PQ, make a kite from P
and unfold it, make a kite from Q and unfold it. Then fold the edges onto the diagonal along the
inner halves of all four kite creases at once. Each side corner has nowhere to go but up, so it
rises as a pinched flap and is laid down toward Q. The two flaps are rabbit ears (see
`rabbit-ear`); the long diamond with its two flaps is the base of traditional fish and many
animals.

## Geometry

The sheet is a square of side `size`: P at (0, 0), Q at (`size`, `size`), and the side corners
R₁ at (`size`, 0) and R₂ at (0, `size`). The diagonal PQ splits the square into two right
isosceles triangles, P–R₁–Q and P–R₂–Q, with the right angle at R.

In each triangle the rabbit ear uses the triangle's angle bisectors:

- the **kite creases** from P and from Q bisect the 45° corners. They meet at the incentre V, at
  distance `size`/(cos 22.5° + sin 22.5°) ≈ 0.765·`size` from P, on the other diagonal;
- the **ridge** R–V bisects the right angle. It is the flap's spine (mountain);
- the **swivel** runs from V perpendicular to the side RQ. Its foot is the incircle's touch point
  on that side, so the flap lies toward Q.

| Crease | Assignment in the base |
|---|---|
| diagonal PQ | precrease, open in the base |
| kite creases P–V and Q–V (four) | valley |
| kite creases beyond V, to the far edges (four) | precrease, open in the base |
| ridges R₁–V₁, R₂–V₂ | mountain |
| swivels V₁–E₁, V₂–E₂ | valley |

At each incentre the folded creases make a degree-4 vertex with sectors 67.5°, 135°, 112.5° and
45°, counter-clockwise from the swivel:

- **Kawasaki:** 67.5° + 112.5° = 180°. The 22.5° slopes are irrational, so the kernel checks it in
  floating point within the bound set by its coordinate grid (Σ √2·10⁻⁶ mm / Lᵢ), not exactly.
- **Maekawa:** three valleys and the mountain ridge, |M − V| = 2.
- **Big-little-big:** the 45° sector lies between the ridge (mountain) and the swivel (valley).

`pliego.flatfold.check` runs these tests on the folded creases every time the cartridge runs, and
the cartridge fails if any of them fails. The two vertices share no crease, because the diagonal
stays open, so each rabbit ear is one rigid degree of freedom.

## The fold program

The program has 39 kinematic steps, written as eight key poses:

1. Fold the diagonal (4 steps) and unfold it (3 steps).
2. Kite-fold from P (5 steps) and unfold (3 steps): the full kite creases, through V.
3. Kite-fold from Q (5 steps) and unfold (3 steps).
4. Rabbit-ear the right corner (8 steps).
5. Rabbit-ear the top corner (8 steps).

`pliego.Sequence.kinematic_path` expands each key pose into exact rigid in-between states with
the kernel's motion solver. A kite fold turns one flap about a straight crease. Each rabbit ear
drives one degree-4 vertex along its rigid mode (mode 1 of the Foschi–Hull–Ku closed forms: three
valleys and a mountain on the ridge) while the precreases through V hold flat. Every loop closes
to within the coordinate grid's floor (about 3·10⁻⁸ rad at the defaults). The finished base is
written as the `target:flat-folded` frame.

What the program does **not** model:

- **No crease memory.** In kinematic mode the unfolded precreases are exactly flat, and the paper
  does not use them. By hand, those creases are what make the collapse fall into place.
- **No layer contact.** The flaps slide over the folded edges. Zero-thickness kinematics does not
  check that they pass cleanly; contact belongs to the physics engine.

## Making one

1. Coloured side up, fold the diagonal PQ, crease and unfold.
2. Fold both edges at P onto the diagonal, crease well and unfold.
3. Fold both edges at Q onto the diagonal, crease well and unfold.
4. Refold the edges at P and Q along the creases, but only as far as the point where the creases
   cross. The side corner stands up as a flap. Pinch it along its middle and lay it toward Q.
5. Do the same on the other side.

## Parameters

| Parameter | Meaning | Default |
|---|---|---|
| `size` | side of the square (mm) | 150 |
| `stock` | `kami`, `copy-80`, `washi-kozo-30` | `kami` |

Presets: `large-24cm` (a 240 mm square).

## History and sources

The fish base is a traditional base, used for traditional fish and as a starting point for
animals with two short flaps. It is described among the classic bases in Robert J. Lang,
*Origami Design Secrets: Mathematical Methods for an Ancient Art*, 2nd ed., CRC Press, 2011. The
flat-foldability conditions checked here are Kawasaki's and Maekawa's theorems, as presented in
Thomas C. Hull, *Origametry: Mathematical Methods in Paper Folding*, Cambridge University Press,
2020. No diagram is reproduced; the geometry is computed by this cartridge.

## Provenance and licence

Traditional base (public domain); original geometry and program by Innovaciones MADFAM. Published
under CERN-OHL-W-2.0, like every object in the commons (see the commons root `LICENSE`).
