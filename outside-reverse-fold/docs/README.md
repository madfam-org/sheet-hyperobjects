# Outside reverse fold

The outside reverse fold wraps one end of a folded strip back *around its own outside*. Start with
a strip folded in half along its spine. Crease a line across both layers, open the end, and turn
it inside out over the body, so that its two layers close around the body's two layers. Then
flatten. The flap's spine, which was a valley, comes out as a mountain. Heads and beaks are made
this way, wherever a tip turns down and must stay locked round the neck below it.

## The geometry: the other direction of mode 2

As in the inside reverse fold, everything happens at the vertex **V** where the reverse crease
meets the spine. Four creases leave V, counter-clockwise from the flap's spine:

| crease | final assignment | sheet direction |
|---|---|---|
| e₁ flap spine | mountain −180° | 0° |
| e₂ reverse crease, front layer | mountain −180° | 180° − β |
| e₃ body spine | valley +180° | 180° |
| e₄ reverse crease, back layer | mountain −180° | 180° + β |

β is the acute angle between the **body's** spine and the reverse crease (the `angle` parameter).
The flap's sectors are therefore obtuse: (180° − β, β, β, 180° − β). Opposite sectors add up to
180° (Kawasaki), and three mountains against one valley satisfy Maekawa's theorem.

With the Foschi–Hull–Ku closed forms (arXiv:2206.12691, Theorem 1) for sector angles
(α₁, α₂, π − α₁, π − α₂) = (180° − β, β, β, 180° − β):

- **Mode 1** (ρ₁ = ρ₃, ρ₂ = −ρ₄): the factor −cos((α₁+α₂)/2)/cos((α₁−α₂)/2) is zero because
  α₁ + α₂ = 180°. Only the spine folds: **folding the strip in half**.
- **Mode 2** (ρ₁ = −ρ₃, ρ₂ = ρ₄): tan(ρ₁/2) = sin((α₁−α₂)/2) / sin((α₁+α₂)/2) · tan(ρ₂/2)
  = cos β · tan(ρ₂/2). Driven **negative**, the reverse creases fold as mountains, the flap's
  spine follows them towards a mountain, and the body's spine turns towards a valley. At −180° the
  flap is wrapped flat around the outside: **the outside reverse fold**.

The inside and outside reverse folds are the two directions of the same mode 2. Driven positive at
a vertex whose flap sectors are acute, mode 2 tucks the flap inside (`inside-reverse-fold`). Driven
negative at a vertex whose flap sectors are obtuse, it wraps the flap outside. Their flat-folded end
states have identical positions. Zero-thickness kinematics cannot tell them apart; only the order of
the layers can. So the fold program, not the final shape, carries the difference.

The flap's direction turns clockwise through 2β: at the default β = 45° it ends pointing straight
down from V.

### Why the rigid program opens the strip flat

Mode 1 and mode 2 cross only at the flat sheet. The folded strip lies on mode 1 and the wrapped
strip on mode 2, so a model with rigid faces must unfold to flat, change mode, and fold again. At
the flat-folded strip (spine at exactly 180°), both layers can also turn together about the
coincident reverse creases. That branch gives the precrease. By hand the paper bends near V and
skips the full opening; the `hand` mode leaves that bending to the paper physics.

## How to fold it by hand

1. Valley-fold the strip in half along its length.
2. Fold the end back at the angle you want, through both layers. Crease firmly, then unfold.
3. Open the end's two layers. Turn the end inside out over the body along the creases, so the
   end's layers come down on the outside of the body's layers.
4. Flatten. The spine of the end is now a mountain.

## What the engine simulates

**`rigid` mode (kinematic).** Every step's target is an exact rigid state of the four creases:

1. Fold in half (mode 1).
2. Precrease (the flat-folded branch).
3. Unfold the precrease.
4. Open flat (the mode crossing).
5. Collapse in eight steps sampled along the negative side of mode 2, evenly spaced in fold-angle
   arc length.

Every target is checked with `pliego.kinematics` before the document is written:

- the loop-closure residual;
- the edge-length error of the face-tree pose.

If either exceeds 10⁻⁵ mm, the cartridge fails loud. At the defaults both stay below 10⁻¹² mm. A
linear blend between neighbouring targets misses closure by up to about 0.9 mm on the default strip.
The cartridge prints that figure; a Tier R projection removes it.

**`hand` mode (physical).** The precrease, then one step from the folded strip straight to the
wrapped state. The paper must bend to follow it.

The `target:reverse-folded` frame records the exact final state.

## Parameters

| Parameter | Meaning |
|---|---|
| `length` | strip length, mm |
| `width` | full strip width before folding in half, mm |
| `angle` | acute angle β between the body's spine and the reverse crease; the flap turns through 2β |
| `position` | where V sits along the strip, as a fraction of the length |
| `stock` | paper stock card |

## Sources

- The outside reverse fold is a traditional origami technique, found in standard diagram
  notation. This cartridge computes its own crease geometry; no published diagram or crease
  pattern is copied.
- F. Foschi, T. Hull, J. S. Ku, "Explicit kinematic equations for degree-4 rigid origami vertices,
  Euclidean and non-Euclidean", arXiv:2206.12691.
