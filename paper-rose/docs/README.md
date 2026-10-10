# Rolled paper rose

| | Title | Summary |
|---|---|---|
| en | Rolled paper rose | A spiral cut into a disc of paper, rolled from its outer end into a tight bud, let loosen and glued onto the uncut centre circle; the curved strip stacks into cones, upright at the heart and opening toward flat at the outside. |
| es | Rosa de papel enrollado | Una espiral recortada en un disco de papel, enrollada desde su punta exterior en un capullo apretado, aflojada y pegada sobre el círculo central sin cortar; la tira curva se apila en conos, erguidos en el corazón y cada vez más abiertos hacia fuera. |
| fr | Rose en papier roulé | Une spirale découpée dans un disque de papier, roulée depuis son bout extérieur en un bouton serré, desserrée puis collée sur le cercle central non découpé ; la bande courbe s'empile en cônes, droits au cœur et de plus en plus ouverts vers l'extérieur. |
| pt | Rosa de papel enrolado | Uma espiral recortada num disco de papel, enrolada a partir da ponta externa num botão apertado, afrouxada e colada sobre o círculo central sem corte; a tira curva se empilha em cones, eretos no miolo e cada vez mais abertos para fora. |

## What it is

The rolled paper rose is a familiar paper craft. Cut a spiral into a circle of paper, leaving a
small circle uncut in the middle. Roll the strip up from its outer end to the centre, let the roll
loosen a little, and glue it onto the centre circle, which becomes the flower's base. This cartridge
computes the spiral for any disc, strip width and centre, with a plain or scalloped petal edge
(`edge`), and plays the rolling: a tight bud first, then the loosened rose on its base.

## Geometry

**The spiral is an involute of a circle.** We use an involute of a circle of radius b = w/2π
rather than the usual Archimedean spiral (w is the strip's width); the two look alike to the eye.
An involute's turns are parallel curves exactly w apart. Every tangent line of the small base
circle crosses every turn at right angles, so the strip has the same width everywhere. The default
disc (120 mm, 12 mm strip, 30 mm centre) gives 2.75 turns and a strip about 648 mm long.

**Segmentation.** `F` lines lie on those tangent lines: 96 stations per turn by default, at the
same angles on every turn. Each F line is normal to the strip's centreline, and every panel is a
flat quadrilateral (plain paper, treatment `none`, never scored). The cut removes a 1 mm kerf. A
zero-width slit cannot open in the kernel's model, because a point on it is a single vertex, and
the turns must be able to separate. The scalloped edge offsets the cut along the F lines by
A·|sin(4(t − t₀))|, with A = 0.22 w: eight rounded scallops per turn, nodes on F lines. The outline
passes `pliego.papercut.analyze` at the stock's minimum feature (0.5 mm cutter).

**Why it makes a rose and not a tube.** The spiral strip is curved in its own plane. Each panel is a
thin wedge whose two F lines meet near the centre, at a development distance ℓ from the panel. A
straight strip rolls into a cylinder; a curved one cannot. Rolled onto a coil of radius ρ, a panel
lies on a cone whose half-angle α obeys sin α = ρ/ℓ, which is how a cone unrolls into a flat
annulus.

- At the heart of the rose (the strip's outer end, where ℓ is large and ρ small), α is small: the
  turns stand nearly upright.
- Toward the centre circle (small ℓ, larger ρ), α grows: the turns open out like petals.
- A curved strip cannot wrap a turn wider than its own curvature radius (ρ ≤ ℓ). Where the roll
  would need more, the panels stay flat and lie round the centre circle as they did in the sheet.

**The pose, honestly.** Each F line gets the fold angle between two facets of a pyramid inscribed in
its own cone, with facet apex angle Δt (the station step):

- cos Δψ = (cos Δt − cos²α)/sin²α;
- the angle is that between the facet normals g(−Δψ)×g(0) and g(0)×g(Δψ), with g the cone's
  generators.

Successive F lines have slightly different cones, so the rolled strip is a stack of cones, not one
surface of revolution. The coil's axis is measured on the result (the mean binormal of the
centreline). Where ρ/ℓ meets 1 it is clamped softly (a parabolic blend over 1 ± 0.15), which keeps
the coil's twist finite where the turns settle flat. The coil radius follows ρ(s) = √(ρ₀² + g·s/π)
along the strip from its outer end, with ρ₀ = 4 mm. Two poses:

- **bud** (rolled tight): g = 0.59 mm by default, the paper's caliper raised to 1.5 times the core
  panel's sagitta. This is a display spacing so the panels' chords never cut through the turn
  beneath. A real bud is tighter.
- **rose** (loosened): g = 2.75 mm by default, chosen so the turn next to the centre circle lies
  flat.

The fold at the centre circle's hinge is chosen by forward kinematics so the circle's front faces
the coil along its axis. In the default rose the circle is 1.4° from square to the axis and the
rose is about 34 mm tall and 56 mm across. The script fails loud if the loosened rose does not
stand on the circle's front within 15°. These poses are an approximation of a hand-rolled rose,
not a simulation of one.

## The fold program

**Mode `make`** is a `kinematic` program on the F lines (the strip has no interior vertices, so every
pose is rigid-valid):

1. roll the outer end into a tight core;
2. keep rolling along the spiral, the inner edge down;
3. roll on: the turns begin to flare;
4. roll up to the centre circle: a tight bud (`target:bud`);
5. let it loosen and glue it down onto the centre circle: the rose (`target:rose`).

The program ends exactly in `target:rose`. The sheet is turned so the strip's outer end is its
leftmost point. The studio preview keeps that panel, the heart of the rose, on the table, so the
rose lies on its side in the preview and part of it hangs below the table plane. The rolls are
valley folds: the front of the paper ends up inside each turn, the side you see from above. The
back is printed a darker shade of the same colour.

**Preview and engine.** The preview plays each step's end exactly. In between, it blends the panel
angles linearly: a whole stretch curls at once, where a hand winds turn by turn. Three things are
left to the physics engine:

- **the settle**: how far a real bud springs open, and how the petals curl when the glue sets;
- **the glue**: in the loosened pose the coil stands on its outermost turn, which rises from the
  flat collar round the circle, and its lower edges stay a few millimetres above the base. Pressing
  the coil down and gluing it would buckle the paper, and the kinematic model cannot show that;
- **contact** between turns.

## Making one by hand

1. Export the disc (`svg`, `dxf`, `pdf` or `hpgl`) and cut it out along the outline, spiral
   included. The default disc is 120 mm across.
2. Hold the outer end and roll it tightly round itself, keeping the inner edge (toward the centre)
   down.
3. Keep rolling along the spiral until you reach the centre circle.
4. Let the roll loosen a little, put glue on the centre circle and press the roll onto it.

Thin paper (copy paper, book pages) rolls easily; kraft makes a sturdier, more open rose.

## Parameters

| id | meaning | default | range |
|---|---|---|---|
| `edge` | `plain` or `scalloped` petal edge | `plain` | |
| `diameter` | disc diameter | 120 mm | 80–200 mm |
| `width` | spiral strip width (petal height) | 12 mm | 8–20 mm |
| `base` | centre circle diameter | 30 mm | 20–50 mm |
| `panels` | stations per turn (model resolution, not cut; lowered to stay within the render budget) | 96 | 48–144 |
| `stock` | `copy-80`, `kraft-120`, `kami`, `elephant-hide-110` | `copy-80` | |
| `colour` | paper colour | rose red | five colours |

Presets: `scalloped` (pink, scalloped edge), `large` (180 mm disc, 14 mm strip, 34 mm centre) and
`kraft-mini` (90 mm disc in kraft). The disc must leave between one and a half and about eight
turns: diameter − base between 5 and 18 strip widths.

## History and sources

The rolled paper rose is a general craft, credited to no designer. HGTV's «How to Make Rolled Paper
Roses» describes the method this cartridge models:

- cut a rough circle from book pages, newspaper, scrapbook paper or kraft;
- cut a spiral starting from the edge, leaving a circle in the centre;
- roll the spiral from the edge to the centre;
- release the swirl and hot-glue it to the centre circle.

(https://hgtv.com/lifestyle/entertaining/how-to-make-rolled-paper-roses)

The Archdiocese of Milwaukee's craft sheet «Rolled paper rose» gives the same steps: cut the
spiral from the outside inward, roll it from the outside in as tightly as you can, glue it to the
centre circle and let the rest unfold a little to make the rose shape
(https://www.archmil.org/ArchMil/Resources/CraftInstructionsRolledPaperRose.pdf).

## Provenance and licence

Original MADFAM geometry: the involute spiral, its normal segmentation and the cone-stack rolled
poses are computed by `main.py`. The craft is credited to its general tradition, with the sources
above; no template is copied. Published under CERN-OHL-W-2.0 like every object in the commons (see
the commons root `LICENSE`).
