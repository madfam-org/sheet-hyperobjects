# Envelope

| | |
|---|---|
| **en** | Every common envelope as one family — eight styles, the ISO 269 and US sizes, gummed or peel-and-seal — generated from the finished size and folded closed. |
| **es** | Todos los sobres comunes como una sola familia —ocho estilos, los tamaños ISO 269 y estadounidenses, engomado o autoadhesivo— generados a partir del tamaño terminado y cerrados con su secuencia. |
| **fr** | Toutes les enveloppes courantes en une seule famille — huit styles, les formats ISO 269 et américains, gommée ou autocollante — générées à partir du format fini et fermées par leur séquence. |
| **pt** | Todos os envelopes comuns como uma só família — oito estilos, os tamanhos ISO 269 e americanos, gomado ou autoadesivo — gerados a partir do tamanho acabado e fechados pela sua sequência. |

## What it is

An envelope is a die-cut blank whose flaps fold behind a front panel and are glued together
into a pocket. The family here, from one generator (`pliego.envelope`):

- **commercial** — the business envelope: side flaps, a bottom flap glued over them and a seal
  flap with a shallow point;
- **baronial** — the same seams with a deep pointed seal flap, usual for invitations (A-sizes);
- **square** — a square front with a pointed flap;
- **wallet** — a deep straight flap across the long edge;
- **catalog** and **pocket** — open on the short edge, with a deep or a shallow straight flap;
- **diamond flap** — four triangular flaps meeting near the centre;
- **window** — commercial with a die-cut window and a glue frame for the film.

Sizes are finished (outside) sizes: ISO 269 C4 229 × 324, C5 162 × 229, C6 114 × 162 and DL
110 × 220 mm; US #10 4⅛ × 9½, A2 4⅜ × 5¾ and A7 5¼ × 7¼ in (converted at 25.4 mm/in).

## Geometry

- The front panel is the finished size less the paper caliper (a 180° fold adds about t), so the
  closed envelope measures the nominal size.
- Side flaps are trapezoids (triangles for the diamond style), the bottom flap a trapezoid with
  slanted edges, the seal flap shaped by the style: shallow point (commercial, window), deep
  point (baronial, square, diamond) or straight with rounded corners (wallet, catalog, pocket).
  Every flap starts a corner clearance (3t, at least 1 mm) from the panel corners, so no two
  flaps share an edge.
- Glue zones: two side-seam strips along the bottom flap's slanted edges (they land on the side
  flaps), and a seal strip on the seal flap — `gum` (remoistenable) or `peel-and-seal`
  (pressure-sensitive under a release liner; the liner itself is not modelled).
- Window style: a window about 90 × 45 mm, 20 mm from the left and 15 mm from the bottom edge —
  a common DL placement, an estimate rather than a cited standard — framed by four film-glue
  strips.

Seams vary between converters (side seam, centre seam, diagonal seam); these blanks use side
seams. All folds are creases (mountain from the address side), named after their flaps; the
`pliego:dielines` block carries the panels, bleed and safe areas, glue zones and the finished
size for the dieline export.

## The fold program

Kinematic, played in full in the preview: fold the side flaps in; fold the bottom flap up and
glue the seams; insert the letter and close the seal flap. Each flap folds 180° behind the
front; the blank lies address side down, so the flaps fold up off the table. No two folds meet
inside the paper (corner clearances), so the blank is a face tree. **Needs the physics engine:**
the glue welds of the seams and the seal, and the stacked flaps' thickness (the zero-thickness
preview lays them on one plane).

## Making one by hand

Print or trace the blank, cut it out, and crease the four fold lines with a bone folder. Fold
the side flaps in, put glue on the bottom flap's seam strips and fold it up onto them. Insert the
letter, moisten the gum (or peel the liner) and close the seal flap.

## Parameters

| Parameter | Range | Meaning |
|---|---|---|
| `style` | 8 styles | commercial, baronial, square, wallet, catalog, pocket, diamond, window |
| `size` | C4, C5, C6, DL, #10, A2, A7 | finished size |
| `seal` | gum · peel-and-seal | seal strip |
| `stock` | copy 80, kraft 120, elephant hide 110, cardstock 160 | paper |

Presets: DL window envelope, A7 baronial invitation, C4 kraft catalog, US #10 business.

## History and sources

Folded paper envelopes go back centuries; machine-cut envelopes and the gummed flap arrived in
the nineteenth century, and the ISO 269 C-series (withdrawn as a standard in 2019 but still the sizes in use, made to hold A-series paper: C4 holds A4 flat,
C5 holds A4 folded once) and the US commercial and announcement sizes are the series in daily use.

- ISO 269:1985, *Correspondence envelopes — Designation and sizes* (withdrawn by ISO in 2019; the size series remains in everyday use) — https://www.iso.org/standard/4178.html
- Wikipedia, *Envelope* (styles, ISO and US sizes) — https://en.wikipedia.org/wiki/Envelope
- Wikipedia, *Paper size* (C-series relation to A-series) — https://en.wikipedia.org/wiki/Paper_size

## Provenance and licence

Original MADFAM geometry, computed by `pliego.envelope` from the parameters; the styles and size
series are common stationery conventions. Licence CERN-OHL-W-2.0 (both manifest fields).
