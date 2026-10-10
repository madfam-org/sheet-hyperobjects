# Flapping bird

| | Title | Summary |
|---|---|---|
| en | Flapping bird | The traditional action model from the bird base: a long neck and a tail reversed up inside, a head, and wings opened into a V. Fold mode folds it move by move on checked layer-ordered states; flap mode starts from the finished bird, and its flap control beats the wings on their hinges in the preview. |
| es | Pájaro que aletea | El modelo de acción tradicional desde la base de pájaro: un cuello largo y una cola invertidos hacia dentro, una cabeza y las alas abiertas en V. El modo de plegado lo pliega paso a paso sobre estados con orden de capas comprobados; el modo de aleteo parte del pájaro terminado y su control bate las alas sobre sus bisagras en la vista previa. |
| fr | Oiseau qui bat des ailes | Le modèle d'action traditionnel depuis la base de l'oiseau : un long cou et une queue inversés vers l'intérieur, une tête et des ailes ouvertes en V. Le mode pliage le plie geste par geste sur des états vérifiés avec ordre des couches ; le mode battement part de l'oiseau terminé et sa commande bat des ailes sur leurs charnières dans l'aperçu. |
| pt | Pássaro que bate as asas | O modelo de ação tradicional a partir da base do pássaro: um pescoço comprido e uma cauda invertidos para dentro, uma cabeça e as asas abertas em V. O modo de dobragem dobra-o passo a passo sobre estados verificados com ordem de camadas; o modo de bater parte do pássaro acabado e o seu controlo bate as asas nas dobradiças na pré-visualização. |

The flapping bird is the classic action model: hold it at the base of the neck, pull the tail,
and the wings beat. It comes from the same bird base as the crane (see `paper-crane`), but its
lower flaps are not narrowed. They are reversed up inside the body as they are, a long neck in
front and a tail behind, the tip of the neck becomes the head, and the wings are creased down at
their base and opened.

## Geometry

The sheet is a square of side `size`. As in `paper-crane`, nothing is drawn from a crease
pattern: every move is a `pliego.flatops` operation on a layer-ordered flat state, each result is
checked by `pliego.flatcheck` (a consistent, complete layer order; taco–taco, taco–tortilla and
tortilla–tortilla conditions; Kawasaki, Maekawa and big–little–big at every vertex), and the crease
pattern is the finished bird unfolded.

At the defaults the bird has 36 faces; its pattern has 35 crease lines, 18 valley, 12 mountain and
5 left flat, meeting at 14 interior vertices.

Where the computed points come from:

- the bird base exactly as in `paper-crane` (kite points from the lower edges laid on the centre
  line, petal hinges through them);
- the neck and tail lines: through the inner edge of each lower flap at `neck` × its height,
  turned by half of 90° − `rise`, so each reversed flap rises at `rise`; long enough (0.7–0.85)
  that the head lies outside the body;
- the head line: a fifth of the neck from its tip, turned by 55°;
- the wing hinges: the petal hinge K₁–K₂, along which each wing is joined to the body.

## The fold program

**Mode `fold`** (26 operations; 114 steps at the defaults): the bird base (as in `paper-crane`),
inside reverse folds for the neck, the tail and the head, the wings folded down front and back,
the wings opened into a V (`rest` degrees from the body), then two beats.

**Mode `flap`**: the document starts from the finished bird (its `initial` frame is the exact
folded pose) and has one control, `flap`, a sequence of four steps: pull, release, pull, release.
In each pull both wings turn `beat` degrees in towards each other on their hinges, and they open
again on the release. This is what the preview can drive.

What the preview shows and what needs the physics engine:

- **The beat.** In paper, pulling the tail bends the body and that bend swings the wings. The tail
  cannot turn as a rigid plate: it is wedged between the two halves of the body, and any rigid turn
  about its crease would push one half of it through the paper. So the flap cycle drives what moves
  rigidly, the wings on their hinges, and the tail stays still in the preview. The bend that
  couples the tail to the wings belongs to the physics engine. The first pull step carries a note
  that says so.
- **The reverse folds** are approximated as in `paper-crane`: the program measures several rigid
  paths in the preview's own face tree and keeps the best. The neck turns with at most about 2 mm
  of tear and 43 mm of deviation from the intended path; each of the three ends with a quick flip
  (up to about 113 mm of tear for one sub-step). The notes on those steps say so.
- **Everything else is exact.** The simple folds, the squashes and petal folds (to within 0.5 mm in
  the blend between samples), the wing folds and every wing hinge motion.

## Making one

1. Fold a bird base (see `bird-base`).
2. Inside reverse fold the two lower flaps up between the layers, one each side: the neck and the
   tail.
3. Inside reverse fold the tip of one of them for the head.
4. Fold each wing down at its base and open it again, so the wings stand in a V.
5. Hold the bird under the neck and pull the tail gently: the wings beat.

## Parameters

| Parameter | Meaning | Default |
|---|---|---|
| `size` | side of the square (mm), 80–300 | 150 |
| `rise` | how steeply the neck and the tail rise (°), 35–60 | 50 |
| `neck` | where the reverse-fold line crosses the lower flap, as a fraction of its height, 0.70–0.85 | 0.80 |
| `rest` | angle of each wing from the body in the resting V (°), 20–90 | 60 |
| `beat` | how far each wing turns in a beat (°), 5–40, never more than `rest` | 30 |
| `stock` | `kami`, `washi-kozo-30`, `copy-80` | `kami` |

Modes: `fold` (the fold program, ending in two beats) and `flap` (the finished bird with its
`flap` control). Presets: `short-neck` (`neck` 0.72, `rise` 45°), `wide-beat` (`rest` 70°,
`beat` 40°), `large-24cm` (240 mm).

## History and sources

The flapping bird is a traditional model; it is folded from the bird base, the base of the
Japanese crane. The bird base and the models folded from it are described in Robert J. Lang,
*Origami Design Secrets: Mathematical Methods for an Ancient Art*, 2nd ed., CRC Press, 2011. The
layer conditions checked here come from Marshall Bern and Barry Hayes, "The complexity of flat
origami", *Proceedings of the 7th ACM-SIAM Symposium on Discrete Algorithms* (1996); Kawasaki's and
Maekawa's theorems are as presented in Thomas C. Hull, *Origametry: Mathematical Methods in Paper
Folding*, Cambridge University Press, 2020. No diagram is reproduced; the geometry, the fold
program and the operating cycle are computed by this cartridge.

## Provenance and licence

Traditional model (public domain); original geometry, program and operating cycle by Innovaciones
MADFAM. Published under CERN-OHL-W-2.0, like every object in the commons (see the commons root
`LICENSE`).
