# Paper crane

| | Title | Summary |
|---|---|---|
| en | Paper crane | The traditional orizuru, folded move by move on layer-ordered flat states: preliminary base, bird base, narrowing folds, inside reverse folds for the neck, the tail and the head, and the wings brought down or spread. Every state is checked; the crease pattern is the finished crane unfolded. |
| es | Grulla de papel | La orizuru tradicional, plegada paso a paso sobre estados planos con orden de capas: base preliminar, base de pájaro, pliegues para estrechar, pliegues invertidos interiores para el cuello, la cola y la cabeza, y las alas bajadas o abiertas. Cada estado se comprueba; el patrón de pliegues es la grulla terminada, desplegada. |
| fr | Grue en papier | L'orizuru traditionnelle, pliée geste par geste sur des états à plat avec ordre des couches : base préliminaire, base de l'oiseau, plis d'affinage, plis inversés intérieurs pour le cou, la queue et la tête, et les ailes rabattues ou déployées. Chaque état est vérifié ; le motif de plis est la grue terminée, dépliée. |
| pt | Grou de papel | O orizuru tradicional, dobrado passo a passo sobre estados planos com ordem de camadas: base preliminar, base do pássaro, dobras para afinar, dobras invertidas internas para o pescoço, a cauda e a cabeça, e as asas baixadas ou abertas. Cada estado é verificado; o padrão de vincos é o grou acabado, desdobrado. |

The folded crane, *orizuru* in Japanese, is the best-known model of the paper-folding
tradition. A square becomes a bird base. Its two lower flaps are narrowed and turned up inside the
body as the neck and the tail, the tip of the neck is turned down as the head, and the two petals
of the base come down as the wings. This cartridge folds it the way a diagram reads, one move at a
time, and every move acts on chosen layers of a flat-folded state rather than on the whole sheet.

## Geometry

The sheet is a square of side `size`. Nothing here is drawn from a crease pattern: the cartridge
performs the moves, and the crease pattern is what the finished crane leaves on the square when it
is unfolded (`FlatState.unfold`).

Each move is a `pliego.flatops` operation on a **layer-ordered flat state**: every face of the
paper has its placement in the folded frame, and every pair of overlapping faces has a layer
order. After each move the kernel checks the whole state (`pliego.flatcheck`):

- the two faces of every crease agree on its end points;
- the faces covering any point are totally ordered (transitivity, per cell of the overlay);
- no layer passes between the two faces of a folded crease it covers (taco–tortilla), two folded
  creases on one line nest or stay apart (taco–taco), and layers keep their order across flat
  creases (tortilla–tortilla);
- Kawasaki's and Maekawa's conditions and the big–little–big lemma at every interior vertex.

A fold through a chosen flap moves the layers picked at a point and every layer joined to them on
that side of the line; it is refused if any other layer lies in its way. Valley and mountain
assignments come from the layer order, never from a table.

The finished crane has 80 faces. Unfolded at the default parameters, its pattern has 69 crease
lines: 34 valley, 28 mountain and 7 creases left flat (precreases the crane does not use), meeting
at 38 interior vertices, each of which passes Kawasaki, Maekawa and big–little–big.

Where the computed points come from:

- the kite points K: each lower edge of the preliminary base laid on the centre line;
- the narrowing creases: each lower edge of the bird base laid on the centre line (11.25° from
  it, at the leg tip);
- the neck and tail lines: through the inner edge of each lower flap, at 62 % of its height,
  turned by half of 90° − `rise`, so the reversed flap rises at `rise` above the horizontal;
- the head line: a fifth of the neck from its tip, turned by half of `head`;
- the wing hinge: the horizontal through the points where the narrowing creases meet the petals'
  edges.

## The fold program

The program has 25 operations (98 steps at the defaults; 106 with spread wings):

1. Fold the square along a diagonal, fold the triangle in half, squash the top flap; turn over and
   squash the other: the preliminary base.
2. Front: fold both lower edges to the centre line through two layers, fold the top triangle down,
   open all three, petal fold. Turn over and repeat (the hinge crease already runs through every
   layer above it): the bird base.
3. Narrow both lower flaps, front and back.
4. Inside reverse fold the left flap (neck) and the right flap (tail); inside reverse fold the tip
   of the neck (head).
5. Fold the wings down, front and back; with `wings` = `spread`, turn them out as a 3-D pose.

**What the preview shows.** The studio preview poses the paper as a face tree and blends angles
step by step. The kernel replicates that tree (`pliego.preview`) and reports what it draws:

| Moves | Preview |
|---|---|
| simple folds, unfolds, narrowing folds, wings | exact: one rigid rotation per step |
| squashes and petal folds | exact rigid motion at every sample (spherical linkage at the moving vertex); samples are added until the blend between two tears less than 0.5 mm |
| inside reverse folds (neck, tail, head) | approximate |

A rigid flap cannot reverse with its root closed: the two rigid modes of the reverse-fold vertex
meet only at the open, flat flap (see `inside-reverse-fold`). The program measures several rigid
paths and keeps the one the preview draws best. At the defaults that is the tip turning as one
stack, drawn without a tear, with its back half flipping inside during the last sub-step. That
flip is a jump the blend cannot follow: up to about 113 mm of tear for the length of that one
sub-step. Each reverse-fold step carries a note that says so. In real paper the layers spread and
bend instead.

The fold program is `physical`: the engine drives the creases with the hand. The document carries
the reference frame `target:flat-folded` (and `target:wings-spread` when the wings are spread).

## Making one

1. Fold a preliminary base (fold the square diagonally, fold in half, squash both flaps).
2. Fold the lower edges of the front flap to the centre line, fold the top triangle down, unfold,
   and petal fold. Turn over and repeat: a bird base.
3. Fold the lower edges of the front layers to the centre line; turn over and repeat.
4. Inside reverse fold the two thin flaps up between the layers: the neck and the tail.
5. Inside reverse fold the tip of the neck to make the head.
6. Fold the wings down, or spread them and pull them gently apart.

## Parameters

| Parameter | Meaning | Default |
|---|---|---|
| `size` | side of the square (mm), 80–300 | 150 |
| `rise` | how steeply the neck and the tail rise (°), 40–65 | 60 |
| `head` | angle the head turns away from the neck (°), 80–140 | 110 |
| `wings` | `down` (flat) or `spread` (3-D pose at the end) | `down` |
| `spread` | how far each wing opens when spread (°), 10–90 | 80 |
| `stock` | `kami`, `washi-kozo-30`, `copy-80` | `kami` |

Presets: `spread-wings`, `proud-neck` (`rise` 65°, `head` 125°), `senbazuru-small` (80 mm). Above
65° the tail's reverse-fold line runs into the narrowed layers near the top of the flap, which the
kernel refuses (a layer would sit inside the reversed tip), so `rise` stops there.

## History and sources

The folded crane is a traditional Japanese model. *Hiden Senbazuru Orikata* (Kyoto, 1797), with text attributed to
Akisato Rito, is often cited as the oldest known book of folding instructions; it shows cranes
folded and joined from a single sheet. The bird base and its use for the crane are described in
Robert J. Lang, *Origami Design Secrets: Mathematical Methods for an Ancient Art*, 2nd ed., CRC
Press, 2011. The layer conditions checked here (taco–taco, taco–tortilla) come from Marshall Bern
and Barry Hayes, "The complexity of flat origami", *Proceedings of the 7th ACM-SIAM Symposium on
Discrete Algorithms* (1996); Kawasaki's and Maekawa's theorems are as presented in Thomas C.
Hull, *Origametry: Mathematical Methods in Paper Folding*, Cambridge University Press, 2020. No
diagram is reproduced; the geometry and the program are computed by this cartridge.

## Provenance and licence

Traditional model (public domain); original geometry and program by Innovaciones MADFAM.
Published under CERN-OHL-W-2.0, like every object in the commons (see the commons root
`LICENSE`).
