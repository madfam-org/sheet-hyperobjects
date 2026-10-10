# Origamic architecture

| | Title | Summary |
|---|---|---|
| en | Origamic architecture | 90° cut-and-fold cards from one sheet: slits and folds make a staircase, an arched gateway or a building facade rise when the card opens to a right angle, and fold flat again when it closes. Original designs with an exact rigid open-and-close program. |
| es | Arquitectura origámica | Tarjetas de corte y pliegue a 90° hechas de una sola hoja: ranuras y dobleces hacen que una escalera, un portal con arco o una fachada se levanten cuando la tarjeta se abre en ángulo recto, y vuelvan a quedar planos al cerrarla. Diseños originales con una secuencia rígida exacta de apertura y cierre. |
| fr | Architecture origamique | Des cartes coupées-pliées à 90° tirées d'une seule feuille : fentes et plis font se dresser un escalier, un portail en arc ou une façade quand la carte s'ouvre à angle droit, et tout se replie à plat quand elle se ferme. Des modèles originaux, avec une séquence rigide exacte d'ouverture et de fermeture. |
| pt | Arquitetura origâmica | Cartões de corte e dobra a 90° feitos de uma só folha: fendas e dobras fazem uma escada, um portal em arco ou uma fachada erguer-se quando o cartão abre em ângulo reto, e voltar a ficar planos quando fecha. Desenhos originais com uma sequência rígida exata de abrir e fechar. |

## What it is

Origamic architecture makes a three-dimensional scene from a single card, using only cuts and
folds: no glue and no separate pieces. Open the card to a right angle and the scene stands up
between the floor page and the back page. Close it and every piece folds away flat inside. This
cartridge carries three original designs on that principle: a **staircase**, an **arched
gateway** between two lower walls, and a **building facade** of five blocks with windows and a
door.

## Geometry

The card is two pages of width `w` and height `H`, folded along the gutter. Every element is a
strip of the card between two slits that run perpendicular to the gutter. The strip is folded into
a zigzag whose segments are alternately parallel to the back page (risers) and to the floor page
(treads). It leaves the floor at distance `D` from the gutter, climbs, and meets the back page at
height `Σr`, with the treads adding up to `D`.

On the flat card that strip runs from `u = w − D` to `u = w + Σr`, with a valley fold at each end
and mountain and valley folds in turn between them. Because every segment stays parallel to one of
the pages, every fold turns by the same angle as the gutter: `ρ = 180° − φ`, where `φ` is the angle
between the pages. That makes each element a generalised parallelogram linkage. It lies flat at
`φ = 180°` and folds flat between the pages at `φ = 0°`.

- **Staircase.** One block with `steps` equal steps: risers `rise/steps`, treads `depth/steps`,
  climbing toward the back page.
- **Arched gateway.** A gate block of height `rise` and depth `depth`, with a round-arched opening
  in its front face (a rectangle under a semicircle, above a sill), between two wall blocks at 60 %
  of its height.
- **Building facade.** Five adjacent blocks of different widths, heights and depths, so the facade
  steps in plan as well as in silhouette, with two columns of windows in each and a door in the
  tallest.

Where two blocks meet, one slit separates them, across the full extent of both strips. Openings are
holes inside a riser, kept at least the minimum feature away from every fold and slit. The gutter
fold runs only where no element crosses it.

Before writing the document, the script checks the folding. `pliego.kinematics.closure_residual`
(which also tests the folds the face tree does not cross, that is, the loops around the slits)
stays below 10⁻¹³ mm at six openings from 30° to 180°. At 90° the floor page lies flat and the back
page stands vertical. A deliberately mismatched fold angle makes the check fail by more than 10 mm,
so it is not vacuous. `pliego.papercut.analyze` confirms one connected piece and the stock's
minimum feature.

## The fold program

The program is `kinematic`. Every fold is at `±ρ`, so the plain angle blend between key poses is
the exact rigid motion, and the studio preview shows it:

1. fold the card to a right angle: the design stands up;
2. close the card: every piece folds flat between the pages;
3. open it again to 90°.

The program ends with the card standing open at 90°, which is also written as the `target:open-90`
frame.

## Making one by hand

1. Print the PDF on cardstock: the solid lines are cuts, the folds are drawn as valleys and
   mountains.
2. On a cutting mat, cut the slits and the openings with a craft knife and a steel ruler.
3. Score every fold with a bone folder or a blunt stylus.
4. Push each element out from the back while you fold the card closed, so the mountains come
   forward and the valleys go back. Crease it flat, then open it to 90°.

A plotter or craft cutter can score and cut the card in one job from the SVG, DXF or HPGL export
(score pass first).

## Parameters

| Parameter | Meaning |
|---|---|
| `design` | staircase, arched gateway or building facade |
| `page_width` | width `w` of each page, mm |
| `page_height` | card height `H`, mm |
| `depth` | how far the design stands out from the back page, mm |
| `rise` | height of the tallest part of the design, mm |
| `steps` | number of steps of the staircase |
| `stock` | cardstock 160 or 250 g/m², or kraft 120 g/m² |

## History and sources

Origamic architecture is credited to the Japanese architect Masahiro Chatani, a professor at the
Tokyo Institute of Technology, who began making cut-and-fold pop-up cards in the early 1980s and
went on to publish many books of designs. The designs in this cartridge are not his: they are
original MADFAM geometry generated on the same 90° cut-and-fold principle.

- Wikipedia, "Origamic architecture": https://en.wikipedia.org/wiki/Origamic_architecture

## Provenance and licence

The three designs, the slit and fold layout, the closure checks and the fold program are generated
by `main.py`; no published card pattern is copied. Original MADFAM work, licensed CERN-OHL-W-2.0
(the commons' root licence).
