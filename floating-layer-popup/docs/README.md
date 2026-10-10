# Floating-layer pop-up

| | Title | Summary |
|---|---|---|
| en | Floating-layer pop-up | A layer carried only by two side supports, cut and scored from one card: it floats clear of the page, upright or as a shelf. No glue. |
| es | Pop-up de capa flotante | Una capa sostenida solo por dos soportes laterales, cortada y hendida en una sola tarjeta: flota separada de la página, vertical o como repisa. Sin pegamento. |
| fr | Pop-up à couche flottante | Une couche portée seulement par deux supports latéraux, découpée et rainée dans une seule carte : elle flotte à l'écart de la page, debout ou en étagère. Sans colle. |
| pt | Pop-up de camada flutuante | Uma camada sustentada só por dois suportes laterais, cortada e vincada num único cartão: flutua afastada da página, em pé ou como prateleira. Sem cola. |

## What it is

In layered pop-up scenes, a picture often seems to hang in the air in front of the background. It
is held up by supports the eye barely notices. This cartridge makes that **floating layer** from a
single card without glue. Two narrow step folds at the sides are the supports. The layer is the
panel between them, cut free of the card everywhere except along its two sides. A gap cut under it
lifts it off the page, and its top can rise above the supports with an arch, a gable or scallops.
Opened to 90°, the layer stands parallel to one page and touches neither.

`orientation = upright` puts the layer parallel to the back page, `layer_distance` in front of it.
`level` makes it a shelf parallel to the base page, `layer_distance` above it, floating free of
the back page and overhanging its supports.

## Geometry

The card is a spread of two pages, `page_width` × `page_height` each, gutter in the middle.
Measured from the gutter, the supports are a parallelogram four-bar G–A–F–B (as in `step-popup`):
the base fold A at p = `layer_distance`, the shoulder F at q − p (q = `support_height`), and the
head fold B at q, with F = A + B − G. Two slits bound the structure, `support_width` outside the
layer on each side.

The layer is the middle of the A–F band, with no fold anywhere inside it:

- a rectangular hole from A to `gap` past it cuts the layer off the base page;
- the shoulder fold F exists only on the supports, so the layer continues straight past it by
  `rise`, and two short slits separate those extensions from the supports;
- a hole from the layer's top outline to B removes the rest of the middle. The outline is
  straight, an arch, a gable or three scallops, `peak` high.

The layer is therefore rigid with the supports' A–F panels and moves exactly as they do, so every
fold of the card turns by the gutter angle γ: A and B valleys, F a mountain. The level orientation
is the mirror image across the gutter, so the same panels end up parallel to the other page. The
layer comes out of the band between the shoulders and the far page, so the script refuses
`rise + peak > layer_distance − 4 mm`. It also refuses a gap that leaves less than 8 mm of support,
a layer that would stick out of the shut card, and anything wider than the card. The cuts pass
`pliego.papercut.analyze` (one piece, narrowest bridge ≥ 2 mm).

## The fold program

The program is `kinematic`, built with `pliego.Sequence.kinematic_path`:

1. **Fold the card shut** (10 substeps): the layer folds down with its supports;
2. **Open it to 90°** (8 substeps): the layer floats.

`kinematics.closure_residual` over every crease (the loop through the supports is a loop around a
cut, so the solver has no vertex to close) stays near 10⁻¹³ mm at every state and midpoint, and the
shut card must be flat and inside its page.

**Preview and engine.** One sheet driven by its own fold program: the studio preview animates the
whole card. The engine adds what a rigid preview cannot show: a wide layer on narrow supports sags
a little under its own weight, more in light paper.

## Making one by hand

1. Export the sheet (`svg`, `dxf`, `pdf` or `hpgl`): slits, holes and outline on the cut layer, the
   folds on the score layer.
2. Cut the two holes and the slits first, then score the folds.
3. Fold the gutter, then fold each support (valley, mountain, valley) and push it through to the
   inside: the layer follows.
4. Close the card, press, and open it to a right angle.

## Parameters

| id | meaning | default | range |
|---|---|---|---|
| `page_width`, `page_height` | one page of the card | 150, 150 mm | 90–220, 90–260 mm |
| `stock` | `cardstock-160`, `cardstock-250`, `kraft-120` | `cardstock-160` | |
| `orientation` | `upright` or `level` | `upright` | |
| `layer_distance` | distance from the page the layer is parallel to | 35 mm | 8–80 mm |
| `layer_width` | width of the layer between the supports | 70 mm | 20–200 mm |
| `gap` | clearance under the layer | 10 mm | 2–40 mm |
| `rise` | how far the layer's sides continue past the supports | 12 mm | 0–60 mm |
| `outline` | `straight`, `arch`, `gable`, `scallops` | `arch` | |
| `peak` | height of the outline above `rise` | 12 mm | 0–40 mm |
| `support_height` | supports from base fold to shoulder | 40 mm | 15–100 mm |
| `support_width` | width of each support | 10 mm | 5–30 mm |

Presets: `shelf` (level, straight), `house-front` (a gable), `a6-card`.

## History and sources

Floating layers are a standard device of pop-up design, usually built from separate glued pieces.
The pop-up literature describes them, for example David A. Carter and James Diaz, *The Elements of
Pop-Up* (Little Simon, 1999) and Duncan Birmingham, *Pop-Up Design and Paper Mechanics* (GMC
Publications, 2010). The single-sheet construction here applies the cut-and-fold method of
origamic architecture (Wikipedia, «Origamic architecture»,
https://en.wikipedia.org/wiki/Origamic_architecture). No published design is copied; the geometry
is computed by this cartridge.

## Provenance and licence

Original MADFAM geometry (the lineage records the general technique, credited to the tradition).
Published under CERN-OHL-W-2.0 like every object in the commons (see the commons root `LICENSE`).
