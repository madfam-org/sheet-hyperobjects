# Glue flap

| | |
|---|---|
| **en** | A strip folded into a closed tube and shut with a tapered glue tab: the joint behind every glued box, sleeve and pop-up piece. |
| **es** | Una tira doblada en un tubo cerrado y sellada con una pestaña de pegado en trapecio: la unión detrás de toda caja, funda o pieza pop-up pegada. |
| **fr** | Une bande pliée en tube fermé et close par une patte de collage biseautée : l'assemblage de toute boîte, de tout fourreau et de toute pièce pop-up collés. |
| **pt** | Uma tira dobrada em um tubo fechado e selada com uma aba de colagem chanfrada: a junta por trás de toda caixa, luva ou peça pop-up colada. |

## The technique

A **glue flap** (glue tab) is a strip of extra paper hinged to an edge by a fold. It carries no
picture and is never seen: its job is to give glue a surface to grip, so that two edges which must
meet can be joined face to face instead of edge to edge. The surface it is glued to is its **glue
zone**.

This object shows the joint on its own. A strip of `sides` equal faces, `side_width` wide and
`tube_length` long, has a scored valley fold between each pair of faces and a tab on its last edge.
Folding every crease by 360° / `sides` (90° for the default square tube) turns the strip into the
cross-section of a regular polygon; the tab, hinged on a last fold of the same angle, has then
turned a full 360° and lies back on the first face, on its inside. Glue holds it there and the
tube is closed.

**Why the tab is tapered.** At each end of the tube the tab meets the folds that close the
polygon. Cutting its two short ends at `tab_taper` keeps it from bunching into those corners — the
reason glue tabs are drawn as trapezoids rather than rectangles.

**Why valley folds put the glue inside.** A valley fold turns the faces toward the front of the
sheet, so the strip closes with its front inward and the tab lands on the inside of the first
face — the outside of the tube stays clean.

## Fabrication

- **Stock.** `cardstock-250` by default; `cardstock-160` or `kraft-120` for light sleeves,
  `cardstock-300` for a stiff box wall.
- **Grain.** The grain runs along the tube (`grain_deg` = 90°), parallel to the folds, so they
  fold cleanly.
- **Cut** the outline with its tab; **score** every fold, including the tab's hinge (card cracks
  if it is folded unscored).
- **Fold** each crease to the polygon's angle and check that the strip closes on itself.
- **Glue.** Put glue on the tab only, close the tube with the tab inside the first face and press
  along the seam until it holds.

## What the engine simulates

The sheet document holds one physical sheet, `strip`, with `sides` scored valley creases (the last
is the tab's hinge). One `glue` join welds the tab's region — the tab less a 0.5 mm margin at its
hinge, its free edge and its tapered ends — onto the first face: the map is a translation by
−`sides` × `side_width`, because the tab's sheet coordinates sit exactly one strip length from
that zone. Joins live on one sheet here, which the sheet document allows.

The `initial` frame is the folded tube, computed in closed form: face k lies along direction
k × 360° / `sides` in the tube's cross-section, the tube lies on the ground on its first face and
its axis runs along the sheet's length. There is no control and no fold program: the object
starts closed and glued, and the engine's paper physics (bending, crease stiffness, the weld)
holds it.

**Verified for this cartridge** (3 to 8 sides, every face width, length, tab width, taper and
stock at the ends and middle of their ranges: 648 documents): `verify` errors = 0; every crease's
fold angle in the initial frame equals 360° / `sides`, valley (to the emit grid, ±2e-6°); largest
glue-weld residual in the emitted initial frame = 5.7e-14 mm.

## Parameters

| id | meaning | range |
|---|---|---|
| `sides` | faces of the tube (4 = square) | 3–8 |
| `side_width` | width of one face | 20–80 mm |
| `tube_length` | length of the tube | 40–200 mm |
| `tab_width` | width of the tab (always narrower than a face) | 6–15 mm |
| `tab_taper` | angle of the tab's slanted ends | 40–75° |
| `stock` | paper | cardstock 160 / 250 / 300 g/m², kraft 120 g/m² |

## Interfaces

- `glue_flap` (male) — the tab.
- `glue_zone` (female) — the strip of the first face it is glued to.

## Provenance

Original MADFAM geometry, computed in this cartridge's `main.py`. The glued tab is a general
technique of paper engineering and box making and is credited to that tradition, not to a
designer.
