# Card linkages

| | Title | Summary |
|---|---|---|
| en | Card linkages | Levers and linkages in card: a four-bar folded from one strip, a scissor extender folded as a rhombus chain, and a crank and rocker of flat links on brads, every pose solved so the links stay joined. |
| es | Mecanismos articulados de cartulina | Palancas y mecanismos de cartulina: un cuadrilátero articulado doblado de una tira, un extensor de tijera doblado como cadena de rombos y una manivela con balancín de eslabones planos con broches; cada posición está resuelta para que los eslabones sigan unidos. |
| fr | Mécanismes articulés en carte | Leviers et mécanismes en carte : un quadrilatère articulé plié d'une bande, un extenseur à ciseaux plié en chaîne de losanges et une manivelle-balancier en biellettes plates sur attaches ; chaque position est résolue pour que les biellettes restent jointes. |
| pt | Mecanismos articulados de cartão | Alavancas e mecanismos em cartão: um quadrilátero articulado dobrado de uma tira, um extensor de tesoura dobrado como cadeia de losangos e uma manivela com balancim de elos planos com colchetes; cada posição é resolvida para que os elos fiquem unidos. |

## What it is

A linkage is a set of rigid links joined by pivots; it turns one motion into another. Card makes
good links, and there are two ways to join them: score lines (living hinges), whose axes lie in the
card, so the links stand on their edges; and brads through holes, whose axes cross the card, so the
links lie flat in layers. This cartridge has three modes:

- **`four-bar`**: a four-bar linkage folded from one strip standing on a base. A post, the input
  link, the coupler, the output link and a second post are joined by score lines; the posts' feet
  are glued to the base, which is the fourth, fixed link. The proportions (ground 64, input 50,
  coupler 22, output 46 mm × `scale`) satisfy Grashof's condition with the coupler shortest, so it
  is a double rocker: the input and the output both swing.
- **`extender`**: a scissor (lazy-tongs) extender folded as a rhombus chain. One strip zig-zags out
  along the top of the chain and back along the bottom; the two zig-zags meet tip to tip at the
  crossing points, where they are stapled. Its joints sit exactly where a lazy tongs' joints sit.
- **`crank-rocker`**: a crank that turns all the way round drives a rocker through a coupler, with
  flat links joined by brads (ground 80, crank 24, coupler 76, rocker 56 mm × `scale`; Grashof with
  the crank shortest). It is the classic linkage of movable books and card automata.

## Geometry

- **Closed-form poses.** The input angle fixes the input link's far pivot *B*; the coupler's far
  pivot *C* is the intersection of the circle of the coupler's length about *B* and the circle of
  the output's length about the output's ground pivot *D*, taking the intersection nearest the
  previous pose so the linkage never jumps to its other assembly.
- **Four-bar.** The script searches the input's reach from the mid-reach angle outward and keeps
  3° clear of its ends, so every hinge stays under 170° and both moving pivots stay on the links'
  side of the ground line: 24°–69° at the default size. The strip is the posts (8 mm), the three
  links and the hinges between them as flat score lines; each post has a 10 mm foot on a valley
  score, folded square and glued to the base.
- **Extender.** Each half-bar (a rhombus side) is 22 mm × `scale`. With the cells' half-angle α,
  every hinge angle is a whole multiple of α: ±2α along the zig-zags, α at the first post and at
  the closing tab, and 180° − 2α at the tip. The closing tab lies back on the first post and is
  glued there; staples at the inner crossings join the two zig-zags. α runs from 70° (closed) to
  18° (open).
- **Crank and rocker.** Each link is a strip `link_width` wide with round ends; the brad positions
  on the links and the base are kiss-cut crosses, where the holes are punched (a `pivot` join's
  point must lie on the card). The links stack 0.32 mm apart: rocker, coupler, crank. The script
  checks the Grashof crank-rocker condition and solves a full turn every 5° for the base's size.

## The mechanism and the fold program

- **`four-bar`**: the program swings the input link from the middle of its range out to one end,
  back to the other and home, in key poses solved as above. The score lines are driven to each
  key's angles; between keys the preview blends the angles, and the script refines the keys until
  the strip's free end comes no further than 0.25 mm from its glued foot between them (0.21 mm at
  the default size, with 25 keys).
- **`extender`**: two steps, open and close. Because every angle is linear in α, the blend
  between the two poses is itself a valid pose: the chain stays closed throughout, not only at the
  keys.
- **`crank-rocker`**: one control, `crank`, drives all three links as kinematic sheets through
  keyed mechanisms (sheet-document spec §5.18). The crank turns on a `rotate` about its ground
  brad. The rocker turns about its own ground brad on a `rotate` whose `keys` table maps the crank
  angle to the rocker's closed-form swing (periodic, 360°). The coupler turns about the crank's
  brad on a `rotate` that **rides** the crank: its keys hold the coupler's heading minus the crank
  angle, so the crank carries it round and it turns on its brad by the difference. The keys start
  every 5° and are refined (3°, 2°, 1°) until the moving brads stay within 0.05 mm of joined
  between keys: 0.036 mm at the default size with 73 keys, 0.019 mm for `large` with 121 keys
  every 3°. The two moving brads stay `pivot` joins; the ground brads are the mechanisms'
  centres. Twelve `target:crank-000` … `target:crank-330` frames hold the exact solved pose every
  30°.

**Preview and engine.** All three modes play in the studio preview, `crank-rocker` included: the
preview and the physics engine evaluate the same key tables, so the coupler stays on both of its
brads at every crank angle. Measured over two turns in 2.5° steps (engine `World`, mesh edge
10 mm), the worst gap at a moving brad is 0.036 mm in the engine and in the preview, and the links
do not stretch (largest strain about 3e-14). Before the keyed mechanisms only the crank was a
mechanism: the preview left the coupler and rocker behind (48 mm off the crank's brad) and the
engine dragged them through their pivots with up to 4.8 mm of gap and strains above 2. The
crank-and-rocker is still not folded: a crank that turns fully folds flat onto its coupler twice a
turn, and standing links on score lines would pass through each other there.

The folded extender has no crossing bars, so in card its cells can flex a little independently;
crossing bars on brads (true lazy tongs) tie every cell to one angle. The physics engine will show
that difference; the preview moves the cells together.

## Making one by hand

1. Export the sheets (`svg`, `dxf`, `pdf` or `hpgl`) and cut them out; score every score line.
2. **Four-bar:** fold the feet square and the hinges, glue the first foot to the base, then glue
   the second foot where the strip closes. Push the input link and watch the output swing.
3. **Extender:** fold the zig-zags, glue the closing tab behind the first post, staple the two
   zig-zags together at each inner crossing, glue the foot down and pull the tip.
4. **Crank and rocker:** punch the brad holes at the crosses, stack base, rocker, coupler and crank,
   and join them with brads (the crank's brad through the base too). Leave the joints loose.

## Parameters

| id | meaning | default | range |
|---|---|---|---|
| `scale` | multiplies every link length | 1.0 | 0.6–2.0 |
| `wall` | height of the folded strip (modes `four-bar`, `extender`) | 30 mm | 15–60 mm |
| `cells` | scissor cells (mode `extender`) | 4 | 2–8 |
| `link_width` | width of the flat links (mode `crank-rocker`) | 14 mm | 10–24 mm |

Presets: `large`, `six-cells`, `low-walls`.

## History and sources

- Grashof's condition: if the shortest and the longest link together are no longer than the other
  two, the shortest link can turn fully relative to a neighbour; whether the result is a
  crank-rocker or a double rocker depends on which link is shortest (Wikipedia, «Four-bar
  linkage», https://en.wikipedia.org/wiki/Four-bar_linkage).
- Lazy tongs are a parallelogram linkage of the pantograph family (Wikipedia, «Pantograph», the
  target of the «Lazy tongs» redirect, https://en.wikipedia.org/wiki/Pantograph).
- The brass fastener is used where rotation around the joint is wanted, as in moving card models
  (Wikipedia, «Brass fastener», https://en.wikipedia.org/wiki/Brass_fastener).

The link proportions and the folded constructions are this cartridge's own.

## Provenance and licence

Original MADFAM geometry: the proportions, strips, links and every solved pose are computed by
`main.py`. Four-bar linkages, lazy tongs and the crank and rocker are classical kinematics,
credited to no designer. Published under CERN-OHL-W-2.0 like every object in the commons (see the
commons root `LICENSE`).
