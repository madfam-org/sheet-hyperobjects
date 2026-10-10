# Folding carton

| | |
|---|---|
| **en** | The folding cartons as one family — straight and reverse tuck end, seal end, crash-lock and 1-2-3 bottoms — generated from inside dimensions, with window and brand artwork on the print side. |
| **es** | Los estuches plegadizos como una sola familia —cierre recto e invertido, cierre por pegado, fondo automático y fondo 1-2-3— generados a partir de las medidas interiores, con ventana y arte de marca en la cara impresa. |
| **fr** | Les étuis pliants en une seule famille — patte rentrante droite et inversée, fermeture collée, fonds automatique et 1-2-3 — générés à partir des dimensions intérieures, avec fenêtre et illustration de marque sur la face imprimée. |
| **pt** | Os cartuchos dobráveis como uma só família — fecho reto e invertido, fecho colado, fundos automático e 1-2-3 — gerados a partir das medidas internas, com janela e arte de marca na face impressa. |

## What it is

A folding carton is the printed paperboard box of retail shelves: one die-cut, creased blank,
four panels in a row (front · side · back · side) closed by a glued manufacturer's joint, with a
closure at each end. The family carried here:

- **Straight tuck end** — tuck lids at both ends, hinged to the same (back) panel.
- **Reverse tuck end** — the top tuck on the back panel, the bottom tuck on the front panel, so
  the two lids open in opposite directions and the blank nests better on the sheet.
- **Seal end** — four flaps at each end, the outer flap glued over the inner flap.
- **Crash-lock (auto) bottom** — two major bottom flaps and two minor flaps whose diagonal
  crease and glue triangle are glued to the neighbouring major flap in the factory, so the
  bottom springs into place when the flat carton is opened; tuck top.
- **1-2-3 bottom** (snap lock) — minor, major, minor flap folded in turn, then the front flap's
  tongue locks under them; tuck top.

## Geometry

`pliego.dieline.carton` builds the blank from inside length L (front width), width W (front to
back) and height D, and the board's caliper t from its stock card:

- body panels L + t and W + t, height D + t (the centre-line rule for 90° folds);
- tuck lids are W + t deep, the tuck tongue 0.3·(W + t) (12–25 mm) with chamfered corners;
- dust flaps reach 0.6·(W + t), never past half the opening; the front panel's flaps are
  trimmed t (at least 0.5 mm) at the free edge for clearance against the joint;
- seal-end flaps: inner (back) W + t, outer (front) 0.55·(W + t) with its glue zone;
- crash-lock: major flaps 0.62·(W + t), minor flaps (W + t)/2 with a 45° diagonal crease
  inset by the clearance, so the glue triangle never shares an edge with a major flap;
- 1-2-3: minor flaps (W + t)/2, back flap 0.7·(W + t), front flap with a central tongue.

All folds are crease-rule scores (mountain folds from the print side), named after their
panels; flaps between neighbours are separated by slits that end at the folds. The optional
window is a die-cut opening in the front panel. The `pliego:dielines` block carries every panel
with its bleed (3 mm, cut edges only) and safe area (3 mm inset), the glue zones and the inside
dimensions; the dieline export profile draws them on named layers in spot colours (CutContour,
Crease, Glue, Bleed, Safe area, Dimensions, Panel labels, Grain arrow, Artwork).

**Branding.** With `branding` on, the sample mark `assets/brand-mark.svg` (original placeholder
art, CERN-OHL-W-2.0) is placed on the front panel's print side, inside its safe area, as a
`pliego:artwork` record clipped to the panel. The SVG export places the image; PDF and DXF draw
its frame. Previewing the artwork as a texture on the folded carton is a studio follow-up.

## The fold program

Kinematic, played in full by the studio preview: form the tube and glue the joint; fold the
bottom dust (or minor) flaps; close the bottom; fold the top dust flaps; close the top (lid,
then tongue; or the seal flaps). Flaps are separated by slits, so no two folds meet inside the
board: the blank is a face tree and folds rigidly. The blank lies print side down and the carton
erects lying on its front panel.

**Limits.** The glue welds (joint, seal ends, crash-lock triangles) are glue zones, not joins:
welding is the physics engine's job. The crash-lock's diagonal crease is drawn but left flat by
the erecting program — it folds only when the glued carton is knocked flat, and the pop-open
action needs the engine. Tongues are shown kinematically; their friction lock needs contact.

## Making one by hand

Print the blank on the board, cut the outline and the window, and crease every fold on the
unprinted side with a bone folder or a creasing rule. Glue the joint, square the tube, then close
the ends in the order of the program. For the crash-lock, glue each triangle onto its neighbour
while the carton lies flat, let it dry, then push the carton open.

## Parameters

| Parameter | Range | Meaning |
|---|---|---|
| `style` | 5 closures | straight tuck, reverse tuck, seal end, crash-lock, 1-2-3 |
| `length`, `width`, `depth` | 30–250, 20–150, 30–300 mm | inside dimensions (width ≤ length) |
| `stock` | FBB 300, SBS 350, cardstock 300, kraftliner 150 | board |
| `window` | on/off | die-cut window in the front panel |
| `branding` | on/off | sample brand mark on the front panel |

Presets: cosmetic box (SBS), tea box with window, kraft carton.

## History and sources

Machine-made folding cartons date from the late nineteenth century, when cutting and creasing
in one press stroke made printed boxes cheap; the tuck, seal and auto-bottom families are the
common styles converters offer today, catalogued by ECMA (the European Carton Makers
Association). This cartridge generates its own geometry and reproduces no catalogue drawing.

- ECMA, *The ECMA Code of Folding Carton Design Styles* (style families) — https://www.ecma.org/
- Pliego physics memo §(h) (folding boxboard as a laminated board) and the `folding-boxboard-300`
  and `sbs-board-350` stock cards (in the Pliego repository).

## Provenance and licence

Original MADFAM geometry, computed by `pliego.dieline` from the parameters; the carton styles
are industry styles attributed to that tradition; the sample brand mark is original placeholder
artwork. Licence CERN-OHL-W-2.0 (both manifest fields).
