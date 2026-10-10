# Paper mobile

| | Title | Summary |
|---|---|---|
| en | Paper mobile | A balanced hanging mobile of card shapes on threads and scored card arms; every arm hangs from a balance point computed from the areas and centroids below it. |
| es | Móvil de papel | Un móvil colgante y equilibrado de figuras de cartulina en hilos y brazos de cartulina marcada; cada brazo cuelga de un punto de equilibrio calculado a partir de las áreas y los centroides que tiene debajo. |
| fr | Mobile en papier | Un mobile suspendu et équilibré, fait de formes en bristol sur des fils et de bras en bristol rainé ; chaque bras pend à un point d'équilibre calculé à partir des aires et des centroïdes qu'il porte. |
| pt | Móbile de papel | Um móbile pendurado e equilibrado, feito de formas de cartão em fios e braços de cartão vincado; cada braço pende de um ponto de equilíbrio calculado a partir das áreas e dos centroides abaixo dele. |

## What it is

A hanging mobile: arms on threads, shapes hanging from the arms' ends, everything level because
each arm is tied exactly where what it carries balances. Here the arms are strips of scored card
and the shapes are original card silhouettes (discs, leaves, drops, stars). Two structures:

- **cascade**: one arm per tier; each arm carries a shape on its left end and the next arm on its
  right end, and the last arm carries two shapes;
- **tree**: every arm carries two arms of the next tier, and the last tier carries the shapes
  (2^tiers − 1 arms, up to three tiers).

## Geometry

**Shapes.** Each shape is a polygon of area A and centroid c, computed by the shoelace formulas.
Its mass is A × the stock's grammage. Its thread is tied on the vertical through c, 4 mm below the
top edge, so the shape hangs straight. Sizes vary between 0.7 and 1.15 × `shape_size`,
deterministically.

**Arms.** An arm is a strip `length` × 12 mm, scored along its middle; tier t is 0.8^(t−1) ×
`arm_length` long. Its own mass sits at ℓ/2; its loads W_L and W_R hang from points 5 mm inside
each end (e_L, e_R). Its thread is tied at the balance point

x_b = (m_arm · ℓ/2 + W_L · e_L + W_R · e_R) / (m_arm + W_L + W_R)

from its left end, where the moments cancel (the law of the lever). An arm's load on its parent is
everything that hangs from it. The script checks that every moment sum is zero, that every balance
point lies between the arm's ends, and that no two shapes' boxes touch, and fails loud otherwise.

For the default mobile (cascade, 4 tiers, 300 mm top arm, 160 g/m² shapes, 300 g/m² arms) the
balance points are 244.1, 185.4, 147.8 and 85.8 mm from the left ends, and the mobile weighs
5.28 g. The script prints these numbers. It also writes them into the note of the step that creases
each tier, because the sheet document's `pliego:meta` takes no extra keys.

**Hanging.** Threads are `string` joins. A shape's thread is 30 mm long; an arm hanging from an arm
hangs below its sibling shapes. Each tier turns 90° from the one above. The `initial` frame is the
mobile at rest: every thread taut and vertical, every arm level.

## The fold program

The program is `physical`, one step per tier: crease the tier's arms along their score to 90°,
into an L-shaped beam that keeps a card arm straight. The score lies on the thread line, so the
balance along the arm does not change. The step notes carry the balance points.

**Preview and engine.** The studio preview shows the balanced mobile and folds the arms' flanges.
It does not simulate the threads, gravity or the slow turning of the arms. The `Air` control (a
`wind` control) needs the physics engine and is disabled in the preview. The small sideways shift of
an arm's centroid when it is creased, the stretch of real thread and the swing of the tiers are also
left to the engine.

## Making one by hand

1. Export the arms and shapes (`svg`, `dxf`, `pdf` or `hpgl`). Score each arm along its middle
   line, cut everything out, and fold the arms to 90° along their scores.
2. Pierce each shape at its thread point, 4 mm below the top edge on the vertical through its
   centroid (the cut file does not mark it; a shape hung there from a pin hangs straight), and
   hang it on 30 mm of thread from its arm's end.
3. Work from the bottom tier up: find each arm's balance point (the printed value; check it on a
   finger) and tie its thread there.

## Parameters

| id | meaning | default | range |
|---|---|---|---|
| `structure` | `cascade` or `tree` | `cascade` | |
| `tiers` | tiers of arms | 4 | 1–5 (tree: 1–3) |
| `arm_length` | top arm length; each tier is 0.8 × the one above | 300 mm | 150–500 mm |
| `shape_size` | nominal shape size (0.7–1.15 ×) | 80 mm | 40–150 mm |
| `shapes` | `mixed`, `disc`, `leaf`, `drop`, `star` | `mixed` | |
| `palette` | `primary`, `pastel`, `kraft` | `primary` | |
| `shape_stock` | `cardstock-160`, `cardstock-250`, `kraft-120` | `cardstock-160` | |
| `arm_stock` | `cardstock-300`, `cardstock-250` | `cardstock-300` | |

Presets: `tree` (3 tiers, 7 arms, 8 shapes), `leaves` (5 tiers of kraft leaves), `small`
(2 tiers).

## History and sources

Wikipedia describes the mobile as a kinetic sculpture built on equilibrium: rods carrying weighted
objects that balance each other, each rod hanging from a single string so it can turn freely. The
form was pioneered by Alexander Calder from the 1930s to 1976, and Marcel Duchamp suggested the
name "mobile" in 1931 (Wikipedia, «Mobile (sculpture)», https://en.wikipedia.org/wiki/Mobile_(sculpture)).
The balance follows the law of the lever (Wikipedia, «Lever», https://en.wikipedia.org/wiki/Lever).
No artwork of Calder's or anyone's is reproduced: the structures and shapes are generated here.

## Provenance and licence

Original MADFAM design; the lineage credits the art form to Alexander Calder without reproducing
any of his works. Published under CERN-OHL-W-2.0 like every object in the commons (see the commons
root `LICENSE`).
