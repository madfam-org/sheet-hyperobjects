# Papercraft unfold

| | Title | Summary |
|---|---|---|
| en | Papercraft unfold | Any low-poly mesh unfolded into papercraft nets: numbered, tabbed pieces packed onto A4 or Letter pages, and a program that folds every piece from the page into its place on the model. |
| es | Despliegue de papercraft | Cualquier malla low-poly desplegada en plantillas de papercraft: piezas numeradas y con pestañas, acomodadas en hojas A4 o carta, y una secuencia que dobla cada pieza desde la hoja hasta su lugar en el modelo. |
| fr | Dépliage de papercraft | N'importe quel maillage low-poly déplié en patrons de papercraft : pièces numérotées, à languettes, rangées sur des pages A4 ou Lettre, et un programme qui plie chaque pièce depuis la page jusqu'à sa place sur le modèle. |
| pt | Desdobramento de papercraft | Qualquer malha low-poly desdobrada em moldes de papercraft: peças numeradas e com abas, arrumadas em folhas A4 ou Carta, e uma sequência que dobra cada peça da folha até o seu lugar no modelo. |

## What it is

A **papercraft net** is a polyhedron cut open along some of its edges and laid flat, so it can be
printed on card, cut out, folded along the remaining edges and glued shut. This object is the
general unfolder as a hyperobject. Give it a polygon mesh and a target size, and it returns the
printable pages and the folding program, in one of two modes:

- **`fold`** (default): the pieces start flat and a kinematic program folds each one into its
  pose on the model.
- **`glued`**: the finished model, held together by a glue join under every tab, for the paper
  physics engine.

Three meshes ship with it, selected by `shape`:

- an **icosphere** (a geodesic sphere: the icosahedron, with every triangle split in four once
  or twice);
- a **torus**, which is not convex: its inner edges fold as valleys;
- an **embedded crystal**: plain vertex and face lists written out in `main.py`. They are the form
  any exported low-poly mesh takes, so the same few lines are where a mesh from another tool (a
  solid from Yantra4D, for example) would go.

Its sibling `low-poly-papercraft` uses the same unfolder for a family of original models.

## Geometry

The kernel's `pliego.unfold.net()` does the work (kernel.md §5). Its steps:

1. **Scale.** The mesh is scaled uniformly so its largest extent is `size` mm, and stands on the
   ground. Faces that are not flat are split into triangles, since paper faces must be planar.
2. **Choose the cuts.** Every interior edge is a candidate fold. Candidates are tried in a
   heuristic order:
   - *Shortest cuts* (`min-perimeter`): long edges first. They stay folded, so the cut
     perimeter, and with it the gluing, is short.
   - *Steepest edge* (`steepest-edge`): at every vertex, the edge that climbs most steeply
     toward a fixed direction is cut, and the others are tried first as folds.
     Schlickenrieder's heuristic for convex polyhedra.

   Kruskal's algorithm joins the two pieces an edge separates, unfolding one onto the other
   about that edge, but only when the joined piece:
   - does not overlap itself (a separating-axis test on slightly shrunken triangles, plus a test
     that no corner comes to rest on another piece's edge);
   - still leaves room beside every open edge for a tab;
   - still fits the printable page.

   An edge that is never joined is a cut. A net that would overlap is therefore split into
   several pieces (islands).
3. **Tabs and numbers.** Every cut gets a number, printed on both of its sides, and one glue
   tab:
   - The tab sits on one side only, alternating by number. It is a trapezoid (or a triangle)
     whose sides meet the fold at `tab_angle`.
   - It shrinks until it lies inside the face it will be glued under and overlaps neither its own
     piece nor its other tabs.
   - On an open mesh, edges that border only one face are plain cut edges, with no tab.
4. **Folds.** The fold angle of each edge is the signed angle between the two faces' normals.
   The printed side is the outside of the model, so convex edges are mountain folds and concave
   edges (the inside of the torus) are valley folds. A tab folds by the same angle as its cut, so
   it ends up in the plane of the face it is glued under. On card stock every fold line is a
   score line.
5. **Pages.** Each piece is turned to fit the printable area (the page minus `margin`) and packed,
   biggest first, at the lowest free spot (skyline packing). The document records the pages
   (`pliego:pages`), so the PDF prints each page once at 1:1 and the SVG draws the page frames.

Every piece is a tree of faces. Inside a piece, each mesh vertex keeps at least one cut, so no
fold line meets another at an interior vertex. Any set of fold angles is therefore a rigid state,
and the fold program is exact. Each sheet's placement maps the piece's first face onto its pose
on the model, so folding every crease to its target rebuilds the model; the kernel tests check
this to 10⁻⁴ mm.

## The fold program

**`fold` mode (kinematic).** One sheet per piece. The steps:

1. *Fold the glue tabs in*: every tab to its angle.
2. *Fold piece N into shape*, one step per piece: every fold of that piece at once. The step's
   note lists the edge numbers to glue.

Each piece folds in place, about its first face. It starts flat in that face's plane and ends in
its exact pose, so the last step shows the finished model. The document also carries the model as
a `target:assembled` frame.

**`glued` mode (physical).** The finished model is the initial frame, with a glue join under every
tab (rule 9 checks each weld to the stock's contact thickness). One step lets go of every crease.
Glue holding the pieces, card springing back against it, and the model settling are left to the
physics engine.

**What the studio preview shows, and what it does not.**

- The fold-up is kinematic. Pieces fold in place; nothing carries a flat piece in from the
  table. A rigid move of a whole piece needs a kinematic (rigid) sheet, and a folding piece is not
  rigid.
- In the preview, `glued` mode shows the finished model standing still. Its welds, springback and
  settling need the engine.

## Making one by hand

1. Print the PDF at 100 % (no "fit to page") on card of the chosen weight. Each piece carries its
   name ("Piece 1"…) underneath.
2. Score every fold line with an empty ballpoint pen or a bone folder against a ruler. Scoring
   matters on card: an unscored fold cracks and rounds.
3. Cut out each piece along its outline, tabs included.
4. Pre-fold: bend each fold line, then open it partly. On a convex model nearly every fold is a
   mountain (the printed side stays outside); valleys appear only where the surface turns inward.
5. Glue tab by tab: put a thin line of glue on a tab, then press it under the face edge that
   carries the **same number**. Start with the largest piece and close the last edges from the
   inside with tweezers or a pencil.

## Parameters

| Parameter | Meaning |
|---|---|
| `shape` | icosphere, torus or the embedded crystal |
| `subdivisions` | icosphere: 0 is the icosahedron (20 faces), 1 gives 80 faces, 2 gives 320 |
| `torus_segments`, `torus_sides`, `torus_tube` | torus: segments around the ring, sides around the tube, tube radius as a fraction of the ring radius |
| `size` | largest dimension of the finished model, mm |
| `page` | A4 or US Letter |
| `method` | cutting strategy: shortest cuts or steepest edge |
| `tab_style` | trapezoid, triangle or none (edges butted and taped) |
| `tab_angle` | angle between a tab's sides and its fold, degrees |
| `tab_height` | the tallest a tab may be, mm |
| `stock` | card weight (160, 250 or 300 g/m²) |

Presets: icosahedron, a 320-face geodesic ball, a donut and the crystal.

## History and sources

- The earliest published nets of polyhedra are in Albrecht Dürer's *Underweysung der Messung*
  (1525). He drew the solids unfolded flat, to be cut and folded.
- Whether every convex polyhedron can be cut along its edges into one net that does not overlap
  itself is still an open problem ("Dürer's problem"). Some non-convex polyhedra have no such
  net at all, which is why an unfolder must be ready to split a model into several pieces. See
  E. D. Demaine and J. O'Rourke, *Geometric Folding Algorithms: Linkages, Origami, Polyhedra*,
  Cambridge University Press, 2007, Part III.
- M. Bern, E. D. Demaine, D. Eppstein, E. Kuo, A. Mantler and J. Snoeyink, "Ununfoldable
  polyhedra with convex faces", *Computational Geometry* 24 (2003): polyhedra with no
  non-overlapping edge unfolding.
- W. Schlickenrieder, *Nets of Polyhedra*, Diplomarbeit, Technische Universität Berlin, 1997: the
  steepest-edge heuristic, among others.
- J. B. Kruskal, "On the shortest spanning subtree of a graph and the traveling salesman
  problem", *Proceedings of the American Mathematical Society* 7 (1956): the greedy spanning
  tree the cut tree is grown with.

## Provenance and licence

Original MADFAM work. The unfolding is computed by the Pliego kernel (`pliego.unfold`). The
icosphere and the torus are generated, and the crystal is a mesh authored here. No published net,
template or papercraft file is copied. Object licence: CERN-OHL-W-2.0 (the commons' root LICENSE);
the kernel is AGPL-3.0.
