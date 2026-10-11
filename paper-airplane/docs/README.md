# Paper airplane · Avión de papel

| | Title | Summary |
|---|---|---|
| en | Paper airplane | One family, every common paper plane: dart, glider, delta, flat-nose square plane, an original canard and the ring wing, each folded flat and then opened to its 3-D form. |
| es | Avión de papel | Una sola familia con todos los aviones de papel habituales: dardo, planeador, delta, avión cuadrado de nariz plana, un canard original y el ala anular; cada uno se dobla en plano y luego se abre a su forma 3D. |
| fr | Avion en papier | Une seule famille pour tous les avions en papier courants : fléchette, planeur, delta, avion carré à nez plat, un canard original et l'aile annulaire, chacun plié à plat puis ouvert dans sa forme 3D. |
| pt | Avião de papel | Uma só família com todos os aviões de papel habituais: dardo, planador, delta, avião quadrado de nariz plano, um canard original e a asa anelar, cada um dobrado em plano e depois aberto na sua forma 3D. |

## What it is

The paper airplane is one hyperobject with many manifestations. The `design` parameter picks the
plane; the other parameters shape its 3-D form:

| design | what it is | credit |
|---|---|---|
| `dart` | the classic dart: corners to the centre twice, folded in half, wings folded down | traditional |
| `glider` | corners to the centre, the nose triangle folded down to a blunt leading edge, a shallow keel and wide wings | traditional |
| `delta` | corners to the centre once; the wing line runs from the nose to the trailing edge, so the wing is a triangle | traditional, anonymous |
| `square` | the leading edge rolled over two or more times, folded in half, rectangular wings | traditional, anonymous |
| `canard` | a rolled leading edge, a slit through both layers, a main wing behind and a smaller foreplane in front, each on its own line | original MADFAM design |
| `ring` | a strip cut along the sheet's long side, its leading edge rolled into a weighted rim, rolled into a hoop | traditional, anonymous |

Sheet sizes: A4, US Letter or a 210 mm square (`paper`). The ring wing uses a strip `ring_width`
wide and as long as the sheet's long side.

## Geometry

Everything is computed by `main.py` with the Pliego kernel; no published diagram or crease
pattern is used. The sheet's long axis is the keel, the nose is the top edge.

- **Corners to the centre.** The fold line runs from the nose point at 45° to the side edge, so the
  top edge lands on the centre line. The dart's second fold bisects the remaining angle (22.5° from
  the centre line), so the first folded edge also lands on the centre line.
- **Keel and wings.** After the plane is folded in half (a valley, flaps inside), each wing is
  folded down along a line `keel` mm from the keel fold, parallel to it. The delta's wing line runs
  from the nose to a point `keel` mm from the keel on the trailing edge.
- **Opening.** The two fuselage sides open 16° apart. A wing that makes the dihedral angle Γ with
  the horizontal then meets its fuselage side at 90° + 8° + Γ, so each wing crease is set to a fold
  angle of 180° − (98° + Γ) = 82° − Γ.
- **Winglets** are the outer `winglet_height` mm of each wing, creased flat and set at 90° to the
  wing, up or down. **Elevator trim** cuts two short slits into each trailing edge, through both
  layers, and sets the tab between them to `trim` degrees: positive bends it up, which pitches the
  nose up.
- **Nose weight** rolls the nose (or the leading edge) over `nose_folds` more times. The square
  plane always rolls its leading edge at least twice and the canard at least once.
- **The ring wing** rolls its strip into a 16-sided hoop: 16 flat facets around a circle of
  circumference (length − 6 % overlap), each facet line turned 22.5°. Real paper curves smoothly;
  the facets are the preview's polygonal approximation, written as flat (`F`) lines.

The cartridge measures the folded plane and prints the figures on its `kinematics:` line (the
sheet-document schema keeps `pliego:meta` closed, so they are not written into the document). It
counts every layer of uniform paper: the centre of gravity is the area-weighted mean of every
face's own area centroid. With the defaults on A4:

| design | span | length | centre of gravity behind the nose |
|---|---|---|---|
| dart | 165.7 mm | 297.0 mm | 159.8 mm (53.8 %) |
| glider | 180.1 mm | 192.0 mm | 74.4 mm (38.8 %) |
| delta | 187.6 mm | 303.0 mm | 157.3 mm (51.9 %) |
| square | 172.9 mm | 267.3 mm | 121.0 mm (45.3 %) |
| canard | 172.9 mm | 279.2 mm | 131.7 mm (47.2 %) |
| ring | hoop diameter 88.9 mm | — | — |

The delta's length is longer than the sheet: its wing lines are slanted, so opening the wings swings
the wing tips aft. Folding corners to the centre moves paper backwards, which is why the dart's
centre of gravity sits behind the middle until nose folds are added.

**Flight is not simulated yet.** It needs the engine's air model (wave W3). These figures describe
the folded shape; they do not predict how the plane flies.

## The fold program

The program is `kinematic`. Each step lists only the creases it moves, and every state is an exact
rigid state.

- **Flat folds are kernel operations.** Every fold is an operation of `pliego.FoldProgram` on a
  layer-ordered flat state. After each one the kernel checks the layer order (taco and tortilla
  conditions, transitivity) and Kawasaki and Maekawa at every vertex. The crease pattern is the
  final flat state unfolded. Each wing, foreplane and winglet folds with every layer of its side
  beyond its line, the flaps folded inside included.
- **Slits are kernel cuts.** The canard's slit and the elevator slits are `FoldProgram.cut`
  operations through both layers; the sheet carries them as cut lines from the first frame. A cut
  is not a fold, so a slit step shows no motion; its label tells the hand what to do.
- **Opening is a set of hinge poses** about the existing creases: the fuselage sides 16° apart,
  the wings (and foreplanes) to the dihedral, the winglets up or down, the elevator tabs to the
  trim. The diagram shows them as one step. The left fuselage side lifts with every layer of its
  own half, including a flap whose crease lies along the keel (the dart's corners).
- **The ring** is the leading edge rolled over, sixteen facet lines scored, then the strip rolled
  into its hoop, each facet turning 22.5° about its line.
- **The pattern.** The crease pattern is the flat state unfolded, so each crease's fold angle is
  its flat-folded one (±180°, or `F` for a line left open, such as the scored ring facets and the
  elevator-tab hinges). The opening angles live in the sequence and in the `folded` target.
- **Closure.** The cartridge checks each state and the linear midpoint between states with
  `pliego.kinematics.closure_residual`, and fails if any state misses closure by more than
  10⁻³ mm. At the defaults the worst residual is below 10⁻⁶ mm.

Typical steps (the dart): fold in half lengthwise; unfold; corners to the centre; edges to the
centre; (nose weight); fold in half; fold each wing down; open the wings to the dihedral and set the
trim.

The studio's preview poses the sheet from one face. The cartridge places the sheet so that the
finished plane shows level and upright, which tilts the flat sheet slightly at the start. With a
slit, no `folded` target is written: a slit's two sides still share their end vertices in the
kernel, so a target that opens a slit would draw them on one side.

## Making one by hand

1. Take an A4 or Letter sheet of copy paper. Fold it in half lengthwise and unfold it.
2. Follow your design's steps from the studio's timeline; crease each fold firmly.
3. For elevator tabs, cut two slits about 15 mm long into the trailing edge through both layers
   before folding the wings, then bend the tab up a little.
4. Open the fuselage slightly, set the wings to a small dihedral, and throw level.
5. For the ring wing, cut a strip along the long side, fold its long edge over two or three times,
   roll it into a hoop with the rim inside and tuck one end into the other. Throw it rim first.

## Parameters

| Parameter | Meaning |
|---|---|
| `design` | dart, glider, delta, square, canard or ring |
| `paper` | A4, US Letter or a 210 mm square |
| `keel` | distance from the keel fold to the wing line, mm (0 uses the design's own depth) |
| `dihedral` | angle of each wing above level when opened, 0–20° |
| `winglets` | none, up or down |
| `winglet_height` | width of the winglet strip, mm |
| `trim` | elevator tab angle, −20° to 30° (0 cuts no tabs) |
| `nose_folds` | extra nose or leading-edge rolls, 0–3 |
| `ring_width` | strip width for the ring wing, mm |
| `stock` | copy paper 80 g/m² or kami |

Presets give classic configurations: a glider on Letter, a delta from a square, a square plane with
winglets, a trimmed canard, a tuned dart and the ring wing.

## History and sources

Paper darts are documented in English from 1786: Richard Cumberland's story in *The European
Magazine* describes schoolboys throwing them. The first known instructions appear in *Games and
Sports for Young Boys* (Routledge, 1859). The Public Paperfolding History Project collects these
records. Paper planes in general are documented from the mid-19th century; the claim that they
began in ancient China has no supporting evidence. The other traditional planes here (the glider
with a folded-down nose, the delta, the flat-nose plane and the paper hoop) are anonymous folk
designs; this cartridge credits them to tradition and generates its own geometry for each.

- The Public Paperfolding History Project, "The paper dart":
  https://origamiheaven.com/historyofthepaperdart.htm
- The Public Paperfolding History Project, history of paper planes:
  https://origamiheaven.com/historyofpaperplanes.htm
- "Paper plane", Wikipedia: https://en.wikipedia.org/wiki/Paper_plane

No designer's model is included: no Nakamura lock and no record-holding designs.

## Provenance and licence

Geometry generated by this cartridge with the Pliego kernel. The dart, glider, delta, flat-nose
plane and ring wing are credited to tradition; the canard is an original MADFAM design. Licence
CERN-OHL-W-2.0 (both manifest fields).
