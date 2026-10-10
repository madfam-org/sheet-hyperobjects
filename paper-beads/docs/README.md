# Paper beads

| | Title | Summary |
|---|---|---|
| en | Paper beads | A long strip of paper wound round a needle from its wide end to its tip: a long triangle gives a bead that tapers to both ends, a rectangle a tube, and a strip with bowed sides, computed for the paper and needle, an oval. |
| es | Cuentas de papel | Una tira larga de papel enrollada en una aguja desde su extremo ancho hasta la punta: un triángulo largo da una cuenta que se adelgaza hacia los dos extremos, un rectángulo da un tubo, y una tira de lados abombados, calculada para el papel y la aguja, da un óvalo. |
| fr | Perles en papier | Une longue bande de papier enroulée autour d'une aiguille, du bout large à la pointe : un long triangle donne une perle effilée aux deux bouts, un rectangle un tube, et une bande aux bords bombés, calculée pour le papier et l'aiguille, un ovale. |
| pt | Contas de papel | Uma tira comprida de papel enrolada numa agulha da ponta larga até a ponta fina: um triângulo comprido dá uma conta que afina nas duas pontas, um retângulo dá um tubo, e uma tira de lados abaulados, calculada para o papel e a agulha, dá um oval. |

## What it is

The rolled paper bead: a long strip of paper, often a magazine page or a printer's offcut, wound
tightly round a needle or skewer from its wide end to its narrow tip, the tip glued down and the
bead slid off and sealed. The outline of the strip is the profile of the bead, wound up. This
cartridge has one generator with three strip shapes (`style`):

- **bicone**: a long isosceles triangle, blunted at the tip. The bead is fattest in the middle and
  tapers to both ends.
- **tube**: a rectangle. Every turn is as wide as the strip: a cylinder.
- **oval**: a strip with bowed-out sides, derived so the bead's profile is an ellipse with round
  ends (see Geometry). Its outline depends on the paper and the needle, so it is computed for each
  run.

## Geometry

**The coil.** The paper's midsurface winds as an Archimedean spiral r(φ) = r₀ + t·φ/2π, where t is
the stock's caliper and r₀ is the needle's radius plus t/2. Paper fills the annulus it winds into,
so after a length u of strip the radius is r(u) ≈ √(r₀² + t·u/π), and the bead's outer radius is
R = r(Ls) for a strip of length Ls.

**From strip to profile.** Each layer covers the strip's width at that point, centred on the bead's
middle. So the bead's radius at axial position z is r(u\*), where u\* is how far along the strip
the width is still 2|z|. Read the other way: the strip's width w(u) sets the profile.

- A straight triangle, w(u) = TIP + (W − TIP)(1 − u/Ls), gives r(z)² falling linearly toward each
  end: a profile that comes to a point at both ends (the bicone).
- A rectangle gives a cylinder of radius R and length W.
- For an ellipse standing on the needle, r(z) − r₀ = (R − r₀)·√(1 − ζ²) with ζ the axial position
  scaled to the strip's half-width. Solving for the width gives
  **w(u) = TIP + (W − TIP)·√(1 − ((r(u) − r₀)/(R − r₀))²)**. The strip stays almost full width
  for most of its length, then narrows quickly toward the tip: its sides are convex. This is the
  oval strip; it is not a template from a source but the inverse of the profile.

**True caliper, no exaggeration.** Turns lie one caliper apart (0.10 mm for copy paper, 0.072 mm
for kami, 0.16 mm for kraft, 0.06 mm for foil paper). They look coincident in a viewer; we kept the
real spacing so the bead has its real diameter. The default bead (a 280 × 25 mm copy-paper strip on
a 3 mm needle) makes 18.3 turns and is 6.8 mm across.

**Segmentation.** The strip is split into narrow panels by `F` lines across its length (plain
paper, treatment `none`: never scored or cut). The coiled pose is a prism over a polygon inscribed
in the spiral: polygon vertex k sits on the spiral at the arclength of F line k, so the pose is an
exact isometry of the strip (the script checks every outline edge to 1e-6 mm). Panel chords are
c = 0.85·√(8·r·t), clamped to 0.6–6 mm, so a chord's sagitta c²/8r stays below 0.73 t and no
turn's chords cut into the turn beneath. The default strip has 234 panels. Past 480 panels (the
render budget) the factor grows until the strip fits; the run prints the resulting
sagitta/caliper ratio, about 1.0 at worst (450 mm of foil paper on a 1.5 mm needle).

**The tip** is blunted to twice the stock's minimum feature (2 mm for copy paper) so the last panel
can be cut. The strip passes `pliego.papercut.analyze` at the stock's minimum feature.

## The fold program

**Mode `make`** is a `kinematic` program on the F lines (the strip has no interior vertices, so
every combination of panel angles is rigid-valid):

1. wrap the wide end once round the needle, coloured side down;
2. keep winding tightly, keeping the strip centred;
3. wind on: the bead grows in the middle;
4. wind almost to the tip;
5. glue the tip and wind the last turn, then slide the bead off the needle and seal it.

It ends in the bead, which is also written as the frame `target:bead`. The tip lies at the sheet's
left edge, so the studio preview keeps the tip panel on the table and the coil rolls up the strip
toward it, as it does on a table under the needle. The rolls are valley folds: the front ends up
inside, the colour (printed on the back) outside.

**Preview and engine.** The preview plays the program exactly at each step's end. Within a step it
blends the panel angles linearly, so the stretch being wound curls as a loose spiral that tightens
onto the bead; a real strip wraps the bead one turn at a time under tension. The needle is not
modelled, nor the glue between turns, nor the varnish. The paper's tension, its springback when the
needle is pulled out and the contact between turns are the physics engine's job.

## Making one by hand

1. Export the strip (`svg`, `dxf`, `pdf` or `hpgl`) and cut it; the default strip is 280 × 25 mm.
   The F lines are not on the cut file. Printed paper goes coloured side down.
2. Lay a needle, skewer or knitting needle across the wide end and wrap the paper once round it.
3. Wind tightly toward the tip, keeping the strip centred so the bead stays symmetrical.
4. Glue the last few centimetres, finish winding and hold the tip down until it grips.
5. Slide the bead off and seal it with varnish or white glue.

## Parameters

| id | meaning | default | range |
|---|---|---|---|
| `style` | `bicone`, `tube`, `oval` | `bicone` | |
| `length` | strip length (a longer strip makes a fatter bead) | 280 mm | 150–450 mm |
| `width` | strip width, which is the bead's length | 25 mm | 10–40 mm |
| `core` | needle diameter (the bead's hole) | 3 mm | 1.5–6 mm |
| `stock` | `copy-80`, `kami`, `kraft-120`, `foil-paper` | `copy-80` | |
| `colour` | colour of the outside | blue | five colours |

Presets: `long-bicone` (420 × 30 mm), `kraft-tube` (kraft, 200 × 15 mm on a 4 mm needle) and
`kami-oval` (kami, 320 × 22 mm). The paper beads made by cooperatives are often wound from
magazine pages; no magazine stock card exists in the Pliego materials, so copy paper stands in for
it.

## History and sources

The i-beads blog post «Paper Beads - History and Trends» traces the craft in the UK to the
Victorian age, when wallpaper was a new fashion: young women rolled beads from scraps of wallpaper
on knitting needles, finished them with beeswax and strung them into door curtains. It describes
the craft's revival through development cooperatives in places like Uganda, which wind scrap paper
from printers and recycling markets round a central form much as the Victorians did
(https://i-beads.co.uk/blogs/blog/38).

The Bead Chest's page on paper beads describes the method this cartridge models, winding each strip
tightly from its wide base to its narrow point round a needle or skewer and gluing the tip down,
and pairs the strip shapes with the beads: a narrow even strip makes a tube, a long isosceles
triangle an oval or football shape, short wide triangles discs. It describes paper beads as a
parlour craft of Victorian England and of the Depression, and names the women's cooperatives of
Uganda from the late 1990s (https://www.thebeadchest.com/pages/bead-types/paper-beads).

Naming: the source calls the bead from a long isosceles triangle "oval or football". Our `bicone`
is that straight triangle; its computed profile comes to points at both ends. Our `oval` is a
derived strip with convex sides that gives round ends. Disc and saucer beads (short wide
triangles) are not included in this cartridge.

## Provenance and licence

Original MADFAM geometry: the strip outlines, the elliptical-profile strip derived from the
paper's caliper, and the coil as a polygon inscribed in an Archimedean spiral are computed by
`main.py`. The rolled paper bead is credited to its tradition, with the sources above; no template
is copied. Published under CERN-OHL-W-2.0 like every object in the commons (see the commons root
`LICENSE`).
