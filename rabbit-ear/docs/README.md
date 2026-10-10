# Rabbit ear

The rabbit ear turns a corner of a triangle into a standing flap. Fold the two edges that meet at
the corner down onto the opposite edge at the same time. The corner has nowhere to go but up, so it
rises as a narrow flap. Pinch that flap along its middle and lay it down to one side. It is one of
the oldest moves in the origami vocabulary. The fish base is two rabbit ears, and it narrows points
all through traditional and modern models.

## The geometry: bisectors, incentre and swivel

Let the triangle be ABC with base AC. Folding edge AB onto AC creases the bisector of the angle at
A. Folding CB onto AC creases the bisector at C. The two bisectors meet at the **incentre I**, the
centre of the inscribed circle, and so does the bisector at B. The flap is pinched along IB.

Three creases at a point cannot fold flat: Maekawa's theorem needs an even number. The fourth crease
is the **swivel**. It runs from I perpendicular to side BC, to the point **E** where the inscribed
circle touches BC. The sectors at I, counter-clockwise from IE, are then

(90° − B/2, 90° + C/2, 90° + B/2, 90° − C/2).

Each sector is read off a right triangle formed by I, a corner and a point where the incircle
touches a side. Opposite sectors add to 180°, so Kawasaki's theorem holds and the vertex folds
flat. When it does, AB lies on AC from A to a point at distance AB along the base. E lands on the
base at the incircle's touch point there. The flap I–E–B lies on top with its tip on the base,
pointing towards C.

A flat-foldable degree-4 vertex is rigidly foldable with one degree of freedom and two modes
(Foschi, Hull and Ku, arXiv:2206.12691, Theorem 1). With creases e₁ = IE, e₂ = IB, e₃ = IA,
e₄ = IC and sector angles α₁ = 90° − B/2, α₂ = 90° + C/2:

- **Mode 1** keeps opposite creases IE and IA equal and makes IB = −IC, with
  tan(ρ_IB/2) = −cos((α₁+α₂)/2) / cos((α₁−α₂)/2) · tan(ρ_IE/2). Driving IE to +180° folds IA and
  IC as valleys and IB as a mountain: **the rabbit ear**, three valleys and one mountain.
- **Mode 2** (IE = −IA, IB = IC) reaches a flat state with the same vertex positions but the
  opposite layer order (IE a mountain, IB a valley). It is not the traditional move, so the
  program does not use it.

The factor in mode 1 equals −sin((B − C)/4) / cos((B + C)/4). It is negative, so IB comes out a
mountain, exactly when the apex angle B is larger than C. When B is smaller than C, the same mode
lays the flap over the other way, with IC a mountain. The cartridge refuses that case, and its
manifest says why (`angle_a + 2·angle_c ≤ 178`). To lay the flap towards A instead, mirror the
triangle: swap the two base angles.

## How to fold it by hand

1. Fold edge AB onto the base and unfold. Fold edge CB onto the base and unfold. The two creases
   cross at I.
2. Fold both edges down along those creases together. The corner B stands up as a flap.
3. Pinch the flap in half along its middle, from I to B.
4. Lay the flap down towards C and flatten. A short swivel crease forms from I to the side BC.

## What the engine simulates

The program has eight kinematic steps along mode 1, spaced evenly in fold-angle arc length from the
flat sheet to the flat rabbit ear. A rigid single-vertex motion has one degree of freedom
(`pliego.kinematics.dof` reports 1 at a generic state), so pinching and swinging the flap happen
together. The step labels follow what a folder sees, first the rising flap and then the swing.

The cartridge checks every target with `pliego.kinematics` before it writes the document:

- the loop-closure residual;
- the edge-length error of the face-tree pose.

If either exceeds 10⁻⁵ mm, the cartridge fails loud. At the defaults both are about 10⁻⁶ mm, the
floor set by the arrangement's 10⁻⁶ mm coordinate grid: the incentre is irrational. A linear blend
between neighbouring targets misses closure by up to about 3 mm on the default 200 mm base. The
cartridge prints that figure; a Tier R projection removes it. The `target:rabbit-eared` frame
records the exact flat state.

## Parameters

| Parameter | Meaning |
|---|---|
| `base` | length of the base AC, mm |
| `angle_a`, `angle_c` | base angles at A and C; the apex angle is B = 180° − A − C |
| `stock` | paper stock card |

## Sources

- The rabbit ear is a traditional origami technique. This cartridge computes its own crease
  geometry; no published diagram or crease pattern is copied.
- R. J. Lang, *Origami Design Secrets*, 2nd ed., CRC Press, 2011: the rabbit-ear molecule, whose
  creases are a triangle's angle bisectors meeting at its incentre.
- F. Foschi, T. Hull, J. S. Ku, "Explicit kinematic equations for degree-4 rigid origami vertices,
  Euclidean and non-Euclidean", arXiv:2206.12691.
