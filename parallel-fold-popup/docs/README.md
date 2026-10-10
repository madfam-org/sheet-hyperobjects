# Parallel-fold pop-up

| | |
|---|---|
| **en** | A three-fold strip glued across the gutter becomes a standing box when the spread opens, and folds flat again when it closes. |
| **es** | Una tira con tres dobleces, pegada sobre el pliegue central, se convierte en una caja de pie al abrir el pliego y vuelve a quedar plana al cerrarlo. |
| **fr** | Une bande à trois plis, collée de part et d'autre de la pliure, devient une boîte debout à l'ouverture et se range de nouveau à plat à la fermeture. |
| **pt** | Uma tira com três dobras, colada sobre a dobra central, vira uma caixa de pé quando a página dupla se abre e volta a ficar plana ao fechar. |

## The mechanism

The spread is two boards hinged along the gutter `G`. The piece is a strip with a glue tab at
each end and three scored folds, all parallel to the gutter: a valley where the first tab meets
the strip (glue line `A`, on the left page at `left_depth` = p from the gutter), a mountain in the
middle (`F`, the box's front edge) and a valley at the second tab (glue line `B`, on the right page
at `right_depth` = q from the gutter).

Because every fold is parallel to the gutter, the whole piece moves in its cross-section: it is a
**four-bar linkage** G–A–F–B whose fixed links are the two pages (G–A = p, G–B = q) and whose
moving links are the two panels (A–F, F–B). This cartridge always cuts the panels to the opposite
sides — A–F = q and F–B = p — so the linkage is a **parallelogram** at every opening: F − A = B − G.
That has three consequences:

- **The box is square-cornered at 90°.** The left page is the floor and the right page the back
  wall. The front panel A–F stands parallel to the back wall, q tall; the top panel F–B lies
  parallel to the floor, p deep. (`left_depth` sets the depth of the top, `right_depth` its height.)
- **It closes flat.** Shut (0°) the pages coincide and so do the two pairs of opposite sides: the
  strip lies folded between the pages, reaching p + q from the gutter.
- **It opens flat.** At 180° the pages are collinear, and so is the parallelogram: the strip lies
  on the spread with its middle fold at q − p from the gutter.

A strip whose panels did not match the opposite sides would be a general four-bar: it could lock
(the panels too short to span A–B, so the paper tears) or stand when the book lies open. The kernel
solves the linkage at each opening as the intersection of two circles and reports a lock where the
intersection does not exist; this cartridge never produces one.

**Why it stays inside the book.** Closed, the folded strip reaches p + q from the gutter. Both
glue distances stop at 60 mm and the page is at least 120 mm wide, so it always fits; the script
checks the closed and the flat pose and refuses anything that sticks out.

## Fabrication

- **Stock.** Pages: `cardstock-300`. Piece: `cardstock-250` (a box face must not sag);
  `cardstock-160` works for small boxes.
- **Cut** the strip: tab, front panel (q long), top panel (p long), tab — all `piece_width` wide.
  The exports carry the outline on the cut layer and the three folds on the score layers.
- **Score** the three folds: valley, mountain, valley. Fold them before gluing.
- **Glue.** Mark the two glue lines on the inside of the spread, p from the gutter on the left page
  and q on the right, both starting `piece_offset` from the bottom edge. Glue the first tab on the
  left page with its fold on the line; put glue on the second tab and close the book — the
  parallelogram places it. Press, let it dry, open slowly.

## What the engine simulates

The sheet document holds three sheets. `page-left` and `page-right` are **kinematic boards**: the
`spread` hinge (axis along the gutter, rest 180°) turns `page-right` by `open − 180°`; the left
page references the hinge but does not move. The strip is a **physical sheet** of `cardstock-250`
with three scored creases; two `glue` joins weld its tabs to the pages. The `initial` frame is the
kernel's four-bar pose at the starting opening, so every weld holds exactly at t = 0; the `open`
control (0–180°) drives the boards and the paper follows. Rigid closure is checked in the kernel
(tier R): flat at 0° and 180°, no lock at any whole degree in between.

**Verified for this cartridge** (glue distances 20/35/50/60 mm in every pairing, every other
parameter at both ends of its range: 512 documents): `verify` errors = 0, closure ok, largest
glue-weld residual over openings 0–180° = 1.4e-14 mm, largest out-of-plane deviation at 0° and
180° = 9.2e-15 mm.

## Parameters

| id | meaning | range |
|---|---|---|
| `page_width`, `page_height` | one page of the spread | 120–200, 180–260 mm |
| `left_depth` | p: glue line on the left page = depth of the box top | 20–60 mm |
| `right_depth` | q: glue line on the right page = height of the box front | 20–60 mm |
| `piece_width` | width of the strip along the gutter | 30–100 mm |
| `piece_offset` | the strip's distance from the bottom edge | 15–80 mm |
| `tab_width` | glue tab width | 8–15 mm |
| `opening` | spread angle the model starts at | 20–180° |

## Interfaces

- `gutter` (neutral) — the spread's hinge line, for other pop-ups and dioramas to mount on.
- `glue_flaps` (male) / `glue_zones` (female) — the strip's tabs and where they land.
- `box_top` (female) — the top panel, the surface a second layer (a floating layer, a scene) is
  glued to.

## Provenance

Original MADFAM geometry, computed by `pliego.popup.parallel_fold`; no published pop-up was
copied. The parallel (box) fold is a general mechanism of the paper-engineering tradition and is
credited to that tradition, not to a designer.
