# Petal fold

The petal fold lifts one layer's corner up over a fold line while that layer's two sides swing in
to the middle. Start from a preliminary base, open end down. Fold the lower edges of the front
flap to the centre line, fold the top down over them, and unfold all three. Then lift the bottom
corner of the front layer up along the horizontal crease. The sides cave in along the kite creases
and meet in the middle as the corner rises. Flattened, the front layer is a long diamond, the petal.
Petal-fold the back as well and you have the bird base of the traditional crane.

## The geometry: three vertices

Take the sheet as the square with centre O. The front quadrant is the one between the book-fold rays
O–L (east) and O–R (north), with the corner B between them. Its diagonal O–B stays flat in the
preliminary base. The petal creases are:

- the **hinge** K1–K2, where K1 and K2 sit on the book folds at distance h·(2 − √2) from O. That
  is where a line from B at 22.5° to the diagonal meets them: the kite creases fold the edges
  LB and RB onto the centre line;
- the **kite creases** K1–B and K2–B on the front layer, and their mirror images K1–C1 and K2–C2
  on the inner layers. The kite fold goes through both layers of each side of the front flap;
- the book folds, now split at K1 and K2 into an inner part (O–K1) and an outer part (K1–L).

Three interior vertices move:

**O, degree 6.** The four book-fold rays and one diagonal (the other diagonal stays flat), with
sectors 90°, 45°, 45°, 90°, 45° and 45°. They meet Kawasaki's condition, and the preliminary base
has four mountains and two valleys (Maekawa). The collapse uses the symmetric one-parameter family:

- the front and back quadrants tilt by τ;
- the two diagonal rays rise by σ = 2·atan(sin τ). This value is what keeps every 45° sector exact.

From τ = 0 to 90°, the sheet goes from flat to the preliminary base. The diagonal's fold angle is
exactly 2τ. The book folds' angles are not linear in τ.

**K1 and K2, degree 5.** Round K1, counter-clockwise from K1–L, the sectors are 67.5° (L to B),
67.5° (B to K2), 45° (K2 to O, the top triangle), 112.5° (O to C1) and 67.5° (C1 to L). In the preliminary base, the top triangle and
the inner layer behind it are pressed flat together at O–K1. They act as one rigid base. The
petal, the front-layer kite flap and the inner flap then form a **spherical rhombus**: four 67.5°
sides, one of them that base. A spherical four-bar has one degree of freedom. Turn the petal by λ
about the hinge, and the ray K1–L is fixed: it must sit 67.5° from both of its neighbours. In the
preliminary base (λ = 0) the rhombus is collapsed and K1–L is folded at 180°. At λ = 180° the
rhombus is flat again: K1–L has unfolded to 0°, and L lands on the midpoint of the hinge. The sides
meet in the middle because the geometry forces it. K2 is the mirror image of K1, and the single
parameter λ drives both through the shared hinge.

`pliego.kinematics.dof` reports 4 for the whole crease pattern at a generic state. The program
removes three of them: the symmetric collapse family, the frozen preliminary base during the petal,
and the mirror symmetry between K1 and K2.

## How to fold it by hand

1. Collapse the square into a preliminary base, coloured side out, open end down.
2. Fold the lower edges of the front flap to the centre line (both layers on each side). Fold the
   top triangle down over them. Unfold all three.
3. Lift the bottom corner of the front layer and swing it up along the horizontal crease.
4. As it rises, push the sides in along the kite creases. They meet at the centre line.
5. Flatten the long diamond. Turn over and repeat for a bird base.

## What the engine simulates

The program has sixteen kinematic steps:

1. Six steps of the preliminary collapse, sampled evenly in τ.
2. The kite precrease: on the flat-folded base, each side's two layers turn together about their
   coincident kite lines.
3. Unfold the precrease.
4. Eight steps of the petal, sampled evenly in λ.

Each state is built as ray directions on the unit sphere and read off as signed dihedrals.

Before the document is written, every target is checked with `pliego.kinematics`:

- the loop-closure residual over the whole sheet;
- the edge-length error of the face-tree pose.

If either exceeds 10⁻⁵ mm, the cartridge fails loud. At the defaults both are below 5·10⁻⁷ mm, the
floor of the arrangement's coordinate grid (K1 and K2 sit at irrational positions). A linear blend
between neighbouring targets misses closure by up to about 3 mm on the default 200 mm sheet. The
cartridge prints that figure; a Tier R projection removes it. The document carries the exact
`target:preliminary-base` and `target:petal-folded` frames.

What this program does **not** include, and why:

- **No top-triangle precrease.** In a rigid model, the "fold the top down" precrease through the
  front layers needs a crease in the inner layers as well. The petal itself does not use it, so the
  program skips it.
- **No layer collisions.** Zero-thickness kinematics guarantees that every face is where its hinges
  put it. It does not check that the kite flaps pass cleanly under the petal; that is Tier C
  contact.
- **The petal starts from a frozen preliminary base.** By hand, the base flexes a little as you
  lift. Here O does not move during the petal, which is an exact rigid path but not the only one.

## Parameters

| Parameter | Meaning |
|---|---|
| `size` | side of the square, mm |
| `stock` | paper stock card |

## Sources

- The petal fold and the bird base are traditional origami techniques; the crane is folded from
  them. This cartridge computes its own crease geometry; no published diagram or crease pattern
  is copied.
- T. Hull, *Origametry: Mathematical Methods in Paper Folding*, Cambridge University Press, 2020:
  Kawasaki's and Maekawa's conditions.
- I. Streinu, W. Whiteley, "Single-vertex origami and spherical expansive motions", JCDCG 2004,
  LNCS 3742.
