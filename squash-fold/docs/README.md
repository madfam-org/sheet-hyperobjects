# Squash fold

A squash fold flattens a flap symmetrically. You lift a flap of two layers, open its layers, and
press its folded edge down onto the line it was hinged on. The flap spreads out on both sides of
that line. The classic first squash is the one taught on the way to the preliminary base. Fold a
square in half along a diagonal, fold the triangle in half again, then squash the top flap into a
square. The result is half a preliminary base: a square with a triangular flap sticking out to one
side. Turn it over, squash the other flap the same way, and you have the full base.

## The geometry: one vertex, three degrees of freedom

Every crease of this squash passes through the centre O of the square. Counter-clockwise from the
north-east:

| ray | role | at the end |
|---|---|---|
| O–NE (45°) | diagonal, first fold; stays flat-folded | valley +180° |
| O–NW (135°) | hinge of the flap, top layer | mountain −180° |
| O–W (180°) | book fold the squash creates | valley +180° |
| O–SW (225°) | the flap's spine (diagonal) | opens to 0° |
| O–S (270°) | book fold the squash creates | valley +180° |
| O–SE (315°) | hinge of the flap, bottom layer | opens to 0° |

The sectors are 90°, 45°, 45°, 45°, 45° and 90°. Kawasaki's condition holds: alternate sectors add
to 180°. The end state has four folded creases, three valleys and a mountain, so Maekawa's
condition holds too. The start of the squash, the triangle folded in half, uses the other four:
both halves of the diagonal and both hinges.

A single vertex of degree n moves rigidly with n − 3 degrees of freedom. This vertex has three:
`pliego.kinematics.dof` reports 3 at a generic state. The program removes two of them:

1. **The first diagonal stays flat-folded.** O–NE is held at 180°, so the north quarter lies
   exactly on the east quarter. Together they act as one rigid base whose two edges, O–SE and
   O–NW, point the same way. That direction is the hinge.
2. **The squash is mirror-symmetric.** The flap is a closed spherical chain of four 45° sectors
   that starts and ends on the hinge direction. The program keeps that chain symmetric about the
   vertical plane through the hinge.

The remaining freedom is the squash itself, parameterised by the elevation φ of the spine O–SW in
that symmetry plane. The spine is (cos φ)·h + (sin φ)·up, with h the hinge direction. The two book
folds sit symmetrically on either side, each at 45° from the hinge and 45° from the spine:

O–W, O–S = cos 45°·h ± b·p + c·up,  with c = cos 45°·tan(φ/2) and b = √(½ − c²),

where p is the in-plane direction perpendicular to the hinge. At φ = 90° the flap stands upright
and folded in half, so b = 0. At φ = 0 the spine lies on the hinge and the book folds lie flat at
±45° from it: the squashed square. Before the squash, the flap turns rigidly about the hinge, from
lying unfolded (ψ = 180°) to folded over (ψ = 0°) to upright (ψ = 90°).

Each state is built as ray directions, and every sector angle is exact by construction. The fold
angles are read off as signed dihedrals between neighbouring faces: positive for valleys, with the
same convention as `pliego.kinematics`. Single-vertex crease patterns that fold flat can always be
reached from the flat sheet by a rigid motion (Streinu and Whiteley, 2004). This construction is one
such motion, written down explicitly.

## How to fold it by hand

1. Fold the square in half along a diagonal.
2. Fold the triangle in half, bringing its two sharp corners together.
3. Lift the top flap so it stands straight up along its hinge.
4. Open the flap's two layers and press its folded edge (the spine) straight down onto the hinge
   line. The flap spreads into a square, centred on the hinge.
5. Crease the two new edges of the square. They are half of the book folds of the full sheet.

## What the engine simulates

The program has eleven kinematic steps:

1. Fold the diagonal.
2. Fold the triangle in half.
3. Lift the flap upright.
4. Squash in eight steps, sampled evenly in the spine's elevation.

The first three steps are rotations about a single axis, so a linear blend between them is exact.
The squash steps are not linear in the fold angles. A plain linear blend of two neighbouring targets
misses closure by up to about 3 mm on the default 150 mm sheet. A Tier R projection removes that
error. The cartridge prints the figure so it stays visible.

Before the document is written, every target is checked with `pliego.kinematics`:

- the loop-closure residual;
- the edge-length error of the face-tree pose.

If either exceeds 10⁻⁵ mm, the cartridge fails loud. At the defaults both are below 10⁻¹² mm. The
`target:squashed` frame records the exact half-preliminary state.

Zero thickness means the layers coincide in the flat states. The kinematics fixes where every face
is; which layer lies on top is decided by the folding order. Tier C contact handles thickness.

## Parameters

| Parameter | Meaning |
|---|---|
| `size` | side of the square, mm |
| `stock` | paper stock card |

## Sources

- The squash fold is a traditional origami technique. This cartridge computes its own crease
  geometry; no published diagram or crease pattern is copied.
- T. Hull, *Origametry: Mathematical Methods in Paper Folding*, Cambridge University Press, 2020,
  covers Kawasaki's and Maekawa's conditions for single-vertex flat foldability.
- I. Streinu, W. Whiteley, "Single-vertex origami and spherical expansive motions", JCDCG 2004,
  LNCS 3742: single-vertex crease patterns fold rigidly from flat.
