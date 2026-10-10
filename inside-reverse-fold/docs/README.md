# Inside reverse fold

The inside reverse fold turns one end of a folded strip back *inside itself*. Start with a strip
folded in half along its spine. Crease a line across both layers, open the layers a little, and push
the end in between them along that line. Then flatten. The flap's spine, which was a valley, comes
out as a mountain. The flap now points in a new direction, tucked between the two layers of the
body. Birds' necks, heads and tails are made this way, from the crane to the simplest flapping bird.

## The geometry: one degree-4 vertex

All the action happens at one point: the vertex **V**, where the reverse crease meets the spine.
Four creases leave V, counter-clockwise from the flap's spine:

| crease | final assignment | sheet direction |
|---|---|---|
| e₁ flap spine | mountain −180° | 0° |
| e₂ reverse crease, front layer | valley +180° | θ |
| e₃ body spine | valley +180° | 180° |
| e₄ reverse crease, back layer | valley +180° | 360° − θ |

Here θ is the acute angle between the flap's spine and the reverse crease (the `angle` parameter).
The two reverse creases are mirror images across the spine, so the sector angles are
(θ, 180° − θ, 180° − θ, θ). Opposite sectors add up to 180°, so the vertex satisfies Kawasaki's
theorem and folds flat. Three valleys and one mountain satisfy Maekawa's theorem (|M − V| = 2).

A flat-foldable degree-4 vertex is also *rigidly* foldable: its four faces can move as rigid
plates with the creases as hinges. It has one degree of freedom and two folding modes. Foschi, Hull
and Ku (arXiv:2206.12691, Theorem 1) give both in closed form. With sector angles
(α₁, α₂, π − α₁, π − α₂) and fold angles ρ₁…ρ₄:

- **Mode 1**: ρ₁ = ρ₃, ρ₂ = −ρ₄ and tan(ρ₂/2) = −cos((α₁+α₂)/2) / cos((α₁−α₂)/2) · tan(ρ₁/2).
  Here α₁ + α₂ = 180°, so the factor is zero. The reverse creases stay flat and the spine folds:
  this is **folding the strip in half**.
- **Mode 2**: ρ₁ = −ρ₃, ρ₂ = ρ₄ and tan(ρ₁/2) = sin((α₁−α₂)/2) / sin((α₁+α₂)/2) · tan(ρ₂/2),
  which reduces to tan(ρ₁/2) = −cos θ · tan(ρ₂/2). Driven positive, the two reverse creases fold
  as valleys. The flap's spine goes the other way, towards a mountain, and the flap sinks between
  the layers: this is **the inside reverse fold**.

Driven negative, mode 2 gives the outside reverse fold of the other side of the vertex (see
`outside-reverse-fold`). The fully folded states of the two moves coincide in position; they differ
only in which layers lie inside.

### Why the rigid program opens the strip flat

The two modes are two curves in the space of fold angles, and they cross only at the flat sheet.
The folded strip is the end of mode 1. The reverse-folded strip is the end of mode 2. So no
rigid motion goes straight from one to the other. A model with rigid faces has to unfold to the
flat sheet, change mode, and fold again.

At the moment the strip lies flat-folded (spine at exactly 180°), one more branch opens. The two
layers lie on top of each other, so they can turn together about the coincident reverse creases.
That is the precrease, the state (180°, t, 180°, −t). By hand, you do not open the strip all the
way: the faces near V bend a little and the paper slips through. That bending is what the `hand`
mode leaves to the engine's paper physics.

## How to fold it by hand

1. Valley-fold the strip in half along its length.
2. Valley-fold the end over at the angle you want, through both layers. Crease firmly.
3. Unfold the end.
4. Open the two layers slightly. Push the spine of the end inwards, so it turns inside out along
   the creases you made.
5. Close the layers and flatten. The end now points along the reflected direction, between the
   layers.

## What the engine simulates

**`rigid` mode (kinematic).** Every step's target is an exact rigid state of the four creases:

1. Fold in half (mode 1).
2. Precrease through both layers (the flat-folded branch).
3. Unfold the precrease.
4. Open flat (the mode crossing).
5. Collapse in eight steps sampled along mode 2, spaced evenly in fold-angle arc length.

The cartridge checks every target with `pliego.kinematics` before it writes the document:

- the loop-closure residual (how far the faces disagree on shared vertices);
- the edge-length error of the face-tree pose.

If either exceeds 10⁻⁵ mm, the cartridge fails loud instead of writing an inconsistent program. At
the defaults both are below 10⁻¹² mm.

Between steps, mode 2 is not linear in the fold angles. A plain linear blend of two neighbouring
targets misses closure by up to about 0.7 mm on the default 200 mm strip. A Tier R solver
projecting onto the constraint manifold removes that error. The cartridge prints the figure so it
stays visible.

**`hand` mode (physical).** The same precrease, then a single step that drives the creases
straight from the folded strip to the reverse-folded state. The paper physics has to bend the faces
to get there. The midpoint of that straight drive misses rigid closure by about 150 mm, which is the
measure of how much the paper must flex.

The document also carries a `target:reverse-folded` frame, the exact final state, which the
engine's checks can compare against.

## Parameters

| Parameter | Meaning |
|---|---|
| `length` | strip length, mm |
| `width` | full strip width before folding in half, mm |
| `angle` | acute angle θ between the flap's spine and the reverse crease; the flap turns through 2θ |
| `position` | where V sits along the strip, as a fraction of the length |
| `stock` | paper stock card |

## Sources

- The inside reverse fold is a traditional origami technique, found in standard diagram notation.
  This cartridge computes its own crease geometry; no published diagram or crease pattern is
  copied.
- F. Foschi, T. Hull, J. S. Ku, "Explicit kinematic equations for degree-4 rigid origami vertices,
  Euclidean and non-Euclidean", arXiv:2206.12691: the degree-4 closed forms used in
  `pliego.kinematics`.
