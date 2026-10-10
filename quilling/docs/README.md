# Quilling

| | Title | Summary |
|---|---|---|
| en | Quilling | Paper filigree: a narrow strip rolled on a slotted tool into a tight coil, released into a loose coil, pinched into a teardrop or a marquise, or left open as a scroll. |
| es | Filigrana de papel (quilling) | Filigrana de papel: una tira angosta enrollada en una herramienta ranurada hasta formar una espiral cerrada, soltada en una espiral abierta, pellizcada en gota o en ojo, o dejada abierta como voluta. |
| fr | Paperolles (quilling) | Le papier filigrané : une bande étroite roulée sur un outil fendu en rouleau serré, relâchée en spirale lâche, pincée en goutte ou en œil, ou laissée ouverte en volute. |
| pt | Quilling (filigrana de papel) | Filigrana de papel: uma tira estreita enrolada numa ferramenta com fenda até virar um rolinho fechado, solta numa espiral aberta, beliscada em gota ou em olho, ou deixada aberta como arabesco. |

## What it is

Quilling, or paper filigree, builds decorations from narrow strips of paper that are rolled, shaped
and glued. Every design starts from a handful of basic shapes, and this cartridge makes five of
them from one strip (`style`):

- **tight coil**: the strip rolled snugly on the tool and glued;
- **loose coil**: the tight coil slid off and let go, so it relaxes before the end is glued;
- **teardrop**: a loose coil pinched at one point;
- **marquise** (the eye): a loose coil pinched at two opposite points;
- **scroll**: a coil released and left open-ended.

## Geometry

**The spirals, in closed form.** The strip's midsurface is a polar spiral ρ(φ). Write t for the
stock's caliper and r₀ = 0.5 mm (the tool's tine) + t/2.

- **Tight coil**: ρ = r₀ + t·φ/2π, an Archimedean spiral with one caliper per turn. The default
  150 mm copy-paper strip rolls into a 4.6 mm coil.
- **Loose coil**: ρ = r₀ + t·φ/2π + B·H(min(x/(1 − δ), 1)), with x = φ/Φ,
  H(y) = y³(4 − 3y) and δ = 2π/Φ (one turn). The extra spacing grows outward over the first two
  thirds of the turns, so the coil gets less dense as it relaxes, then closes up. The last turn is
  a tight turn: the end lies exactly one caliper outside the turn beneath, where it is glued (the
  script checks it). Φ (the turns left after relaxing) is solved so the spiral is as long as the
  strip and reaches the chosen diameter: B = D/2 − r₀ − t·Φ/2π. The default relaxes to 7.5 turns.
- **Scroll**: the same spiral with x³ instead of H, with no closing turn. The outer turns open out
  and the end stays free.
- **Teardrop and marquise**: each turn of the loose coil is reshaped by a polar shape function S(θ),
  blended by the turn's radius: r = ρ(φ)·(1 + w·(S(θ) − 1)), with w = (ρ − r₀)/(ρmax − r₀). The
  inner turns stay round, as they do in a pinched coil, and the outer turns take the full shape.
  The teardrop's S is a unit circle with two tangent lines meeting at a tip 1.7 radii from the
  centre (a 72° tip). The marquise's S is a lens of two circular arcs with tips 1.8 radii out
  (a 64° tip). B is solved again so the pinched coil keeps the strip's length, and the number of
  turns stays that of the loose coil. The pinched coil comes out a little smaller across.

**Segmentation.** `F` lines across the strip (plain paper, treatment `none`, never scored) split it
into narrow panels. Each pose is a prism over a polygon whose sides are the panels, so every pose is
an exact isometry of the strip (the script checks every edge to 1e-6 mm). The stations, where the F
lines fall, are walked along the final shape:

- each chord is c = 0.85·√(8·r·t), with r the tight coil's radius at that point along the strip, so
  even in the tight coil a chord never cuts into the turn beneath (sagitta below 0.73 t);
- a station lands exactly on every pinch corner, so each turn of a teardrop or marquise has a
  sharp tip.

The same chord lengths are then walked along the tight and the loose spirals. The default teardrop
has 164 panels and 6 tips on stations. Panels are at least 0.35 mm long, enough to stay above the
1 mm² face floor on a 3 mm strip.

**True caliper.** The tight coil's turns lie one caliper apart: 0.10 mm for copy paper, 0.072 mm
for kami, 0.12 mm for Elephant Hide and 0.16 mm for kraft. They look coincident in a viewer, and
the coil's size is the real one. Quilling paper itself (often around 120 g/m²) has no stock card
in the Pliego materials; the four stocks offered stand in for it.

## The fold program

**Mode `make`** is a `kinematic` program on the F lines (a strip has no interior vertices, so every
pose is rigid-valid):

1. slip the strip's end into the tool's slot and turn the first turns;
2. roll evenly, keeping the edges aligned;
3. roll to the end: a tight coil (the `tight` style ends here, glued);
4. slide it off and let it go: it relaxes into a loose coil, end glued (or, for `scroll`, opens
   with the end left free);
5. pinch it at one point (teardrop) or at two opposite points (marquise).

Every intermediate shape is written as a frame (`target:tight`, `target:loose`, and
`target:teardrop`, `target:marquise` or `target:scroll`). The program ends exactly in the chosen
shape's frame. The strip's outer end lies at the sheet's left edge, so the studio preview keeps that
panel on the table and the coil stands on its edge on it. A finished quilled shape usually lies flat
on its backing.

**Preview and engine.** The preview plays the program exactly at each step's end. In between, it
blends the panel angles linearly: the roll curls the stretch being rolled as a loose spiral, the
release expands every turn at once, and the pinch reshapes all turns together. By hand the coil
unwinds from the outside and the fingers squeeze only the outer turns. The relaxed spiral is a
chosen closed form, not a simulation. How far a real coil opens depends on the paper's stiffness,
the tightness of the roll and friction between turns, which is the physics engine's job, as are
the glue and the tool (neither is modelled). The eccentric coil and other shapes (husking,
combing) are not in this cartridge.

## Making one by hand

1. Export the strip (`svg`, `dxf`, `pdf` or `hpgl`) and cut it, or cut a strip of the same size.
   The default is 150 × 5 mm. The F lines are not on the cut file.
2. Slip one end into the slot of a quilling tool and turn the tool, keeping the edges level.
3. For a tight coil, glue the end while the coil is still on the tool, then slide it off.
4. For a loose coil, slide the coil off and let it relax, then glue the end to the turn beneath.
5. Pinch the glued loose coil between finger and thumb at one point for a teardrop, or at two
   opposite points for a marquise. For a scroll, leave the end unglued.

## Parameters

| id | meaning | default | range |
|---|---|---|---|
| `style` | `tight`, `loose`, `teardrop`, `marquise`, `scroll` | `teardrop` | |
| `length` | strip length | 150 mm | 60–300 mm |
| `width` | strip width | 5 mm | 3–10 mm |
| `diameter` | diameter the coil relaxes to (all styles but `tight`) | 12 mm | 6–25 mm |
| `stock` | `copy-80`, `kami`, `elephant-hide-110`, `kraft-120` | `copy-80` | |
| `colour` | strip colour | purple | five colours |

Presets: `tight-coil` (200 mm), `eye-kami` (a marquise from a 3 mm strip of kami) and `big-scroll`
(300 × 10 mm Elephant Hide). The script refuses a relaxed diameter less than twice the tight
coil's, and a strip too short to make two and a half turns at the chosen diameter.

## History and sources

Wikipedia's article «Quilling» defines it as an art form that uses strips of paper rolled, shaped
and glued together into decorative designs. It traces the craft to French and Italian nuns of the
12th to 16th centuries, who wrapped the gilded edges of holy books round goose quills to make
coils for reliquaries and holy pictures, imitating costly metalwork and carved ivory. In the 18th
and 19th centuries it was an accomplishment of well-to-do women, especially in England, who
decorated screens, cabinets and tea caddies. William Bemrose revived it in 1875 with a kit called
"Mosaicon", and Jane Austen's *Sense and Sensibility* shows Lucy Steele making a filigree basket.
The article names the slotted tool, once made from bird feathers, and strips 3 to 10 mm wide, 5 mm
being the most common (https://en.wikipedia.org/wiki/Quilling).

The Origami Resource Center's «Quilling instructions» describes the basic shapes this cartridge
models:

- the tight coil, rolled in the slotted tool and glued;
- the loose coil, made by releasing a tight coil so it unwinds before gluing;
- the teardrop and the eye or marquise, made by pinching a loose coil;
- the scroll, a loose coil left open-ended.

It also describes the eccentric coil and gives strip widths of ⅛ or ¼ inch
(https://origami-resource-center.com/quilling-instructions/).

## Provenance and licence

Original MADFAM geometry: the relaxed spiral, the pinch shapes and the isometric polygon of panels
are computed by `main.py`. Quilling and its basic shapes are credited to the craft's tradition,
with the sources above; no published design is copied. Published under CERN-OHL-W-2.0 like every
object in the commons (see the commons root `LICENSE`).
