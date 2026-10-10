# Branded tag

| | |
|---|---|
| **en** | A folded board hang tag showing the four ways a brand goes onto board — printed artwork, a pressed mark (emboss or deboss), an iron burn and a laser burn — with an eyelet hole through both panels and a string to hang it. |
| **es** | Una etiqueta colgante de cartón doblada que muestra las cuatro formas de marcar el cartón —arte impreso, marca prensada (relieve o bajorrelieve), quemado con hierro y quemado láser—, con un ojillo que atraviesa ambas caras y un hilo para colgarla. |
| **fr** | Une étiquette suspendue en carton pliée qui montre les quatre façons de marquer le carton — illustration imprimée, marque pressée (gaufrage ou embossage en creux), brûlure au fer et brûlure laser — avec un œillet qui traverse les deux volets et un fil pour la suspendre. |
| **pt** | Uma etiqueta pendente de cartão dobrada que mostra as quatro maneiras de marcar o cartão — arte impressa, marca prensada (relevo ou baixo-relevo), queima a ferro e queima a laser — com um ilhó que atravessa as duas faces e um fio para a pendurar. |

## What it is

A hang tag is a small folded card tied to a product, and often the first thing a maker brands.
This hyperobject makes one in board and applies the brand mark in one of four ways, chosen with
`style`:

- **printed artwork** — the mark as a placed image (`pliego:artwork`, `assets/mark.svg`);
- **pressed mark** — the mark raised (**emboss**) or pressed in (**deboss**) between a die and a
  counter;
- **iron burn** — the mark charred into the board by a hot branding iron;
- **laser burn** — the mark engraved by a laser, outline and raster fill.

The mark is an original, brand-neutral motif — a rounded-square ring around a folded-corner
triangle and a dot, a sheet with its corner turned over — computed in `main.py` and drawn with
the same geometry in the SVG asset, so the printed, pressed and burned versions match. No real
brand logo is used.

## Geometry

- **Tag.** Two panels (40 × 70, 55 × 90 or 70 × 120 mm) joined by a scored spine: the cover on
  the left, the back on the right. Their top corners are clipped at 45° (0.22 of the width).
- **Eyelet.** A round hole (3–8 mm) through each panel, centred and level with the clips; the two
  holes are mirror images about the spine, so they align when the tag is folded. The script
  requires at least max(2t, 2 mm) of board between the hole and the top edge and runs
  `pliego.papercut.analyze` on the blank.
- **Mark** (width `mark_scale` × the tag's width, on the cover): outer ring = rounded square with
  corner radius 0.18 of its width, inner = 0.8 of its width (even-odd, so the ring is a band);
  the triangle and the dot sit inside it.
- **Finishes** (`pliego:finishes`, `pliego.press`): emboss — ring 0.4 mm (bevel), triangle and dot
  0.5 mm; deboss — 0.35 mm, flat; iron burn — one region, char 0.9, depth up to 0.4 mm; laser
  burn — char 0.75, depth up to 0.15 mm. A burn never chars more than half the board's caliper
  (a design limit [E]); depths are typical design values [E], not press specifications. The
  dieline export profile writes each finish as its plates: emboss die and counter, deboss die and
  counter, the branding iron's face, or the laser's vector outline and raster hatch.
- **String.** A `string` join from the top of the cover's eyelet to a point `string_length` above
  it: the tag hangs from it.

## The fold program

The tag hangs upright as a rigid placement, its cover's print side facing the viewer. One
kinematic step folds the back behind the cover along the spine (a mountain fold of 180°), so both
printed faces end outward and the holes line up. **Limits.** The string, the tag swinging on it
and the finishes' local effects — an embossed area is stiffer, a burned area thinner and more
brittle — are the physics engine's part; the studio does not yet render relief, sheen or char.
A metal eyelet can be set in the hole; it is not modelled.

## Making one by hand

Cut the tag, the eyelet holes and the score. For a printed tag, print the cover before cutting.
For a blind emboss or deboss, cut the mark from thin card as a stencil and burnish the board into
it over a light box (or use a die and counter). For an iron burn, heat a branding iron cut to the
mark's face and press it briefly; for a laser burn, start at low power on scrap of the same board.
Fold along the score, thread the string through both holes and tie it.

## Parameters

| Parameter | Range | Meaning |
|---|---|---|
| `style` | artwork, emboss, deboss, iron burn, laser burn | how the mark goes on |
| `mark_scale` | 0.35–0.8 | mark width / tag width |
| `size` | small, medium, large | tag panel size |
| `hole` | 3–8 mm | eyelet hole diameter |
| `string_length` | 30–300 mm | string from the eyelet to its hanging point |
| `stock` | greyboard 1.5 mm, SBS 350, FBB 300, cardstock 300 | board |

Presets: iron-burned greyboard tag, printed SBS tag, large laser-burned tag.

## History and sources

Marking goods with a stamped or burned mark is very old; embossing and letterpress survive as
tactile finishes, and laser engraving made heat branding digital.

- Wikipedia, *Embossing (paper)* — https://en.wikipedia.org/wiki/Embossing_(paper)
- Wikipedia, *Branding iron* — https://en.wikipedia.org/wiki/Branding_iron
- Wikipedia, *Laser engraving* — https://en.wikipedia.org/wiki/Laser_engraving
- Pliego sheet-document spec, `pliego:finishes` and `pliego:artwork` (§5.10–§5.11), and
  `pliego.press` (in the Pliego repository).

## Provenance and licence

Original MADFAM design: the tag and the brand-neutral mark are computed in `main.py` and drawn in
`assets/mark.svg` (original placeholder artwork); the `lineage` entry says so, licence `original`.
The finishing processes are general crafts. Licence CERN-OHL-W-2.0 (both manifest fields).
