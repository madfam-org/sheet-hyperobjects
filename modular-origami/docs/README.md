# Modular origami

| | Title | Summary |
|---|---|---|
| en | Modular origami | Interlocking-unit assemblies from generic units: a cube of six sleeve units, and a wreath and a crown of triangular units in the folk 3-D origami idiom; one unit folds step by step beside the finished object. |
| es | Origami modular | Ensambles de unidades entrelazadas hechas con unidades genéricas: un cubo de seis unidades de funda, y una corona plana y una corona de pie de unidades triangulares al estilo popular del origami 3D; una unidad se dobla paso a paso junto al objeto terminado. |
| fr | Origami modulaire | Des assemblages de modules imbriqués faits de modules génériques : un cube de six modules en fourreau, et une couronne à plat et une couronne debout de modules triangulaires dans l'idiome populaire de l'origami 3D ; un module se plie pas à pas à côté de l'objet fini. |
| pt | Origami modular | Montagens de unidades encaixadas feitas de unidades genéricas: um cubo de seis unidades de luva, e uma guirlanda e uma coroa de unidades triangulares no estilo popular do origami 3D; uma unidade se dobra passo a passo ao lado do objeto pronto. |

## What it is

Modular origami builds one object from many identical folded units that hold each other: a flap of
one unit slides into a pocket of the next, without glue. This cartridge uses only generic units
whose fold sequences it derives itself; no named designer's unit appears. Three modes, each with one
unit folding step by step beside the assembled object:

- **`cube`**: six sleeve units. A 3:1 strip folds into a two-layer square face whose top and bottom
  edges stay open (the pockets), with a tab on each of the other two edges. Each tab slides into a
  neighbouring face's pocket.
- **`wreath`**: a flat ring of triangular units in the folk Chinese 3-D origami idiom. Each unit's
  point slides into the next unit's pocket, and the ring closes on itself.
- **`crown`**: the same ring with every unit standing up.

## Geometry

**The sleeve unit (cube).** The strip is 2*f* + 3*t* long and *f* tall, with *t* = *f*/3
(`unit_size` = *f*): back face [0, *f*], a double tab [*f*, *f* + 2*t*] folded flat at its middle,
the front face, and a single tab. The sleeve fold (180°) lays the front face on the back face; the
tabs then fold square (the double tab's two scores at −90° and +90°, the single tab's at +90°).
The top and bottom edges of the face are raw edges of both layers: the pockets. In the cube each
face gives its two tabs along one axis and takes two along another (faces facing ±z give tabs to
the ±x faces, ±x to ±y, ±y to ±z), so every tab finds a pocket open along the shared edge, and
every face gives two and takes two. Opposite faces share a colour. In the assembled cube the tabs
stand 1.5° past square: the document has no paper thickness, so a tab exactly square would lie in
its pocket's own plane; tilted, it sits just inside the pocket. This unit is derived here; we
know of no attribution for it.

**The triangular unit.** A 2:3 rectangle (`unit_size` × 1.5 `unit_size`) is folded with simple
folds (`pliego.simplefold`, which tracks every layer and records every crease):

1. fold it in half;
2. fold the two corners of the folded edge down to the centre line, which leaves a triangle and a
   flap;
3. turn over and fold the flap's corners in, so they will not stick out past the triangle;
4. fold the flap down over the triangle;
5. turn over, and repeat 3 and 4 with the other flap;
6. turn over and fold the triangle in half.

The result is a right isosceles triangle with legs half the paper's width. Its two layers part
along one leg: two points at one corner, and a pocket between them. The script checks that the
crease pattern closes (loop-closure residual 3 × 10⁻¹⁴ mm). The folk unit is usually folded from
1:2 paper; this sequence and its 2:3 proportion are the cartridge's own.

**The ring.** Turning unit *k* by 360°/`units` about the ring's centre must carry its point onto
the next unit's pocket edge, `depth` × the leg in from that unit's point; the centre solves that
rotation. In the `crown` each unit stands up by `tilt` about its own pocket edge: the points lie on
those edges, so every point stays in its pocket. Neighbouring units sit 0.15 mm apart, so the layers
of a point and of the pocket it fills never share a plane.

## The fold program

The program folds the loose unit: three steps for the sleeve unit (the sleeve, the double tab, the
single tab), seven for the triangular unit (the steps above, the corner and flap folds counted as
one step each per side). The assembled units stand folded in the initial frame. Every crease of
the triangular unit folds to ±180° (flat); the program drives the creases of each simple fold
together, which turns the moving layers as one stack about the fold line.

**Preview and engine.** The studio preview plays the unit's folds and shows the assembly. The
physics engine adds what the preview leaves out: the thickness and spring of the layers, and the
friction that holds a tab in its pocket.

## Making one by hand

- **Cube.** Cut six 3:1 strips (for example 120 × 40 mm). Fold each into a sleeve at one third plus
  a little (the fold leaves a double tab one ninth of the strip long), then fold both tabs square.
  Slide the tabs of two opposite faces into the pockets of a third, and keep going; the last face
  closes the cube.
- **Wreath and crown.** Cut 2:3 rectangles and fold the triangular unit as above. Slide the point
  of one unit into the pocket of the next, a little more than halfway, and go round until the ring
  closes. For the crown, stand every unit up the same amount.

## Parameters

| id | meaning | default | range |
|---|---|---|---|
| `unit_size` | cube face, or the triangular unit's paper width | 40 mm | 24–90 mm |
| `units` | units in the ring (modes `wreath`, `crown`) | 12 | 6–24 |
| `depth` | how much of the leg each point slides in | 0.55 | 0.3–0.75 |
| `tilt` | how far the crown's units stand up (mode `crown`) | 70° | 20–85° |

Presets: `big-units`, `eight-units`, `tall-crown`.

## History and sources

- Modular origami assembles identical modules by inserting flaps into pockets; its earliest known
  record is a modular cube, a *tamatebako*, in the Japanese book *Ranma Zushiki* of 1734
  (Wikipedia, «Modular origami», https://en.wikipedia.org/wiki/Modular_origami).
- Chinese paper folding (*zhezhi*) includes 3-D modular folding with triangles connected by
  inserting a flap into a pocket; it became widely known after Chinese refugees detained from the
  ship *Golden Venture* (1993) folded large models from such units (Wikipedia, «Chinese paper
  folding», https://en.wikipedia.org/wiki/Zhezhi).

The triangular unit here is credited to that folk idiom; its exact fold sequence is derived by
this cartridge. No named designer's unit is used.

## Provenance and licence

Original MADFAM geometry: both units' creases and every assembly are computed by `main.py`. The
triangular-unit idiom belongs to the Chinese folk tradition of modular folding. Published under
CERN-OHL-W-2.0 like every object in the commons (see the commons root `LICENSE`).
