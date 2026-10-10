# Dissolve scene

| | Title | Summary |
|---|---|---|
| en | Dissolve scene | A venetian-blind picture change: a window of slats, picture A on their fronts and picture B on their backs; turn them all half a turn and A becomes B. |
| es | Escena que se transforma | Un cambio de imagen de persiana veneciana: una ventana de lamas con la imagen A al frente y la B al reverso; al girarlas todas media vuelta, A se vuelve B. |
| fr | Scène changeante | Un changement d'image à jalousie : une fenêtre de lamelles, l'image A au recto et l'image B au verso ; un demi-tour de toutes et A devient B. |
| pt | Cena que se transforma | Uma troca de imagem de persiana: uma janela de lâminas com a imagem A na frente e a B no verso; ao girá-las todas meia volta, A vira B. |

## What it is

Movable books have long had pictures that change into other pictures. The best known form,
the transformation, is a scene made of slats that slide under and over one another when a tab is
pulled. This cartridge makes the **venetian-blind** form of the same idea. A window is filled
with slats that each carry one band of picture A on the front and the matching band of picture B
on the back. Turn every slat half a turn about its own centre line, all together like the slats of
a blind, and scene A dissolves into scene B. Halfway, the slats stand open like louvres and you see
through the window.

## Geometry

A frame (300 g/m² card) with a window `window_width` × `window_height`, framed by `frame_margin`.
The window holds `slats` slats, horizontal or vertical (`direction`), at an even pitch:

- each slat is as wide as the pitch less a 0.6 mm gap and 1 mm shorter than the window, so it turns
  inside the opening without touching the frame;
- at each end, a 4 mm tongue on the slat's axis runs 8 mm under the frame. That is where the slat is
  held: on a thread or wire axle, or in a pocket behind the frame;
- slats narrower than 4 mm are refused, and so is a frame margin too narrow for the tongues.

Neighbouring slats turn by the same angle, so they stay parallel and never collide. Their fronts
take picture A's colour and their backs picture B's (`picture_a`, `picture_b`), so the preview
shows the change. For real pictures, print the bands on the slats.

## The mechanism

Each slat is a kinematic board turned by its own `hinge` mechanism about its centre line, and every
hinge reads the one `change` angle control: 0° shows picture A, 90° opens the louvres, 180° shows
picture B. The slats' pivots and the linkage that turns them together (a thin strip tied to one
edge of every slat, as a blind's cord is) are not sheets or joins of the document. The shared
control and the hinge axes stand for them, which is what lets the studio preview play the change.
A string join for the linkage would hand the control to the physics engine, which is a possible
refinement once that engine lands.

**Preview and engine.** The `change` control plays in the preview. Near the pivots the turning
tongues pass through the frame in the preview, because its sheets have no thickness; in the real
object they turn in the gap behind the frame.

## Making one by hand

1. Export the sheets (`svg`, `dxf`, `pdf` or `hpgl`): the frame and one outline per slat.
2. Print picture A across the slats as they lie side by side, in order, face up. Then turn the row
   of slats over about its long axis and print or glue picture B's bands on the backs as they lie.
3. Cut out the slats and the window.
4. Hold each slat by its tongues: thread a fine wire or a strong thread through a hole at the tip of
   each tongue and into the frame sides, or glue a strip with a pocket behind each side of the
   window. Tie or glue a thin strip to one edge of every slat so that one pull turns them all.

## Parameters

| id | meaning | default | range |
|---|---|---|---|
| `slats` | number of slats | 9 | 3–24 |
| `direction` | `horizontal` (a venetian blind) or `vertical` | `horizontal` | |
| `window_width`, `window_height` | the window | 120 × 90 mm | 40–260 mm |
| `frame_margin` | the frame around the window | 25 mm | 15–60 mm |
| `picture_a`, `picture_b` | colours of the slats' fronts and backs | navy, blush pink | eight colours |

Presets: `fine` (20 slats in a 120 mm high window), `tall-vertical`, `postcard`.

## History and sources

Tab-operated movable books flourished in the nineteenth century (Lothar Meggendorfer, Ernest
Nister). Their transformations show "a scene made up of vertical slats" that slide under and
over one another when a tab is pulled (Wikipedia, «Pop-up book»,
https://en.wikipedia.org/wiki/Pop-up_book). This cartridge implements the turning-slat
(venetian-blind) variant of the picture change named in the commons catalogue. It makes no claim
about which historical books used it. No book's design is copied; the geometry is computed by this
cartridge.

## Provenance and licence

Original MADFAM geometry (the lineage records the general device, credited to the tradition).
Published under CERN-OHL-W-2.0 like every object in the commons (see the commons root `LICENSE`).
