# V-fold pop-up

| | |
|---|---|
| **en** | The basic pop-up: a folded kite glued across the gutter rises as the spread opens and folds flat when it closes. |
| **es** | El pop-up básico: una cometa doblada, pegada sobre el pliegue central, se levanta al abrir el pliego y queda plana al cerrarlo. |
| **fr** | Le pop-up de base : un cerf-volant plié, collé de part et d'autre de la pliure, se dresse à l'ouverture et se range à plat à la fermeture. |
| **pt** | O pop-up básico: uma pipa dobrada, colada sobre a dobra central, levanta-se ao abrir a página dupla e fica plana ao fechá-la. |

## The mechanism

A spread is two boards hinged along the gutter. The piece is a kite of card with a fold along
its long axis and a glue tab on each of its two lower edges. It is glued with its fold point `O`
on the gutter, `piece_offset` from the bottom edge, and each tab along a glue line that leaves
`O` at `glue_angle` (α) from the gutter, one on each page.

Four folds meet at `O`: the gutter, the two glue lines and the piece's own fold. That is a
**degree-4 vertex** with one degree of freedom, so the spread angle φ alone decides where the
piece's fold points. Let δ be half the angle between the two glue lines in space (it grows from 0
when the book is shut to α when it lies open), m the bisector of the glue lines and n the normal
on the inner side of the spread. With the piece cut to a half-angle β, its fold runs along

    f = (cos β / cos δ) · m + √(1 − cos²β / cos²δ) · n

**Why it closes flat.** Shut (φ = 0°) the two glue lines coincide, δ = 0, and the two halves of
the piece lie on top of each other between the pages. Open flat (φ = 180°) the glue lines are 2α
apart, δ = α, and the square root vanishes only if β = α: the fold lies in the page plane and the
piece lies flat on the spread. This cartridge always cuts the piece with β = α, which is the only
choice that is flat at both ends. (With β < α the root becomes imaginary before 180°: the paper
would have to stretch and tears — a *lock*. With β > α the piece still stands when the book lies
open.)

**Why it stays inside the book.** As the book closes, the piece's fold swings to 2α from the
gutter, so its tip lands `piece_height · sin 2α` from the gutter and
`piece_offset + piece_height · cos 2α` from the bottom edge. The parameter ranges keep that point
inside the page for every combination (glue angle ≤ 42°, piece height ≤ 120 mm ≤ page width),
and the script checks the closed and the flat pose and refuses anything that sticks out.

## Fabrication

- **Stock.** Pages: `cardstock-300` (stiff boards). Piece: `cardstock-250` (the piece must hold
  its shape while it stands). `cardstock-160` works for small pieces.
- **Cut.** Two page boards (or one board scored at the gutter) and the kite with its two tabs —
  the SVG, DXF, PDF (1:1, tiled) and HPGL exports carry the outline on the cut layer.
- **Score.** The piece's long axis (mountain) and the two tab hinges (valley). Card this heavy
  cracks if it is folded unscored.
- **Fold** the axis and the tabs, and check that the kite closes on itself.
- **Glue.** With the spread open flat, lay the piece closed on one page with its fold point on the
  gutter, glue that tab along its glue line; close the book with glue on the other tab and press —
  the book places the second tab itself. Let it dry, then open slowly.

## What the engine simulates

The sheet document holds three sheets. `page-left` and `page-right` are **kinematic boards**: the
`spread` hinge (axis along the gutter, rest 180°) turns `page-right` by `open − 180°`; the left
page references the same hinge but does not move. The piece is a **physical sheet** of
`cardstock-250`: it bends, its scored creases have the stock's crease stiffness, and two `glue`
joins weld its tab regions to the pages. The `initial` frame is the kernel's closed-form pose at
the starting opening, so every weld holds exactly at t = 0; the `open` control (0–180°) drives the
boards and the paper follows through the welds. Rigid closure is checked in the kernel (tier R):
flat at 0° and 180°, no lock at any whole degree in between.

**Verified for this cartridge** (every combination of the parameter-box corners, every glue angle
from 25° to 42°: 1152 documents): `verify` errors = 0, closure ok, largest glue-weld residual over
openings 0–180° = 2.8e-14 mm, largest out-of-plane deviation at 0° and 180° = 6.6e-15 mm.

## Parameters

| id | meaning | range |
|---|---|---|
| `page_width`, `page_height` | one page of the spread | 120–200, 180–260 mm |
| `glue_angle` | α, between the gutter and each glue line (= the piece's half-angle) | 25–42° |
| `glue_length` | length of each glue line | 30–55 mm |
| `piece_height` | length of the piece's fold, gutter point to tip | 60–120 mm |
| `piece_offset` | gutter point's distance from the bottom edge | 15–60 mm |
| `tab_width` | glue tab width | 6–15 mm |
| `opening` | spread angle the model starts at | 20–180° |

The glue angle stops at 42°: at 43° and 45° the kernel's closed form leaves a 1.8e-6 mm
rounding residual at 180°, just over its 1e-6 mm flatness tolerance, so closure reports a failure
there although the geometry is flat (reported to the kernel).

## Interfaces

- `gutter` (neutral) — the spread's hinge line, so other pop-ups and dioramas can mount on this
  spread.
- `glue_flaps` (male) — the piece's two tabs; `glue_zones` (female) — where they land on the pages.

## Provenance

Original MADFAM geometry, computed by `pliego.popup.v_fold`; no published pop-up or crease
pattern was copied. The V-fold is a general mechanism of the paper-engineering tradition and is
credited to that tradition, not to a designer.
