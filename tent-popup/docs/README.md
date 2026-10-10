# Tent pop-up

| | Title | Summary |
|---|---|---|
| en | Tent pop-up | A strip folded in the middle and glued across the gutter stands as a tent when the card lies open flat, and folds flat inside when it closes. |
| es | Pop-up en tienda | Una tira doblada a la mitad y pegada sobre el pliegue central se levanta como una tienda cuando la tarjeta está abierta del todo, y queda plana por dentro al cerrarla. |
| fr | Pop-up en tente | Une bande pliée en son milieu et collée de part et d'autre de la pliure se dresse en tente quand la carte est ouverte à plat, et se range à plat à la fermeture. |
| pt | Pop-up em tenda | Uma tira dobrada ao meio e colada sobre a dobra central se ergue como uma tenda quando o cartão está aberto por completo, e fica plana por dentro ao fechá-lo. |

## What it is

Most pop-ups stand best when the card is open at a right angle. The tent is the simplest of the
others, the **180° pop-ups**: it stands when the card or book lies open flat. It is a strip of card
with a glue tab at each end and a fold (the ridge) in the middle, glued across the gutter with both
tabs at the same distance from it. The two sides are longer than that distance, so there is too much
paper to lie flat between the glue lines: the strip rises into a roof. Close the card and the roof
folds flat inside. A tent is the base of many pop-up roofs, hills and animal backs.

## Geometry

Two sheets. The **card** is one scored sheet, a spread of two pages with the gutter between them.
The **tent piece** is a strip `tent_width` wide: a tab, a side of length `s` (`side`), the ridge,
a second side and a second tab, with three scored folds. Its tabs are glued on the pages at
distance `p` (`glue_distance`) from the gutter, `tent_offset` along it.

In the card's cross-section the piece is a **kite four-bar** G–A–F–B: G is the gutter, A and B are
the tab folds (`p` from G on each page), and F is the ridge, with |AF| = |FB| = `s`. F lies on the
far side of AB from G:

F = M + √(s² − |AM|²) · n,

where M is the midpoint of AB and n the unit normal pointing away from the gutter. Because
`s > p`, the square root never vanishes: the kite never locks, and the ridge stays above the card at
every opening. Open flat, the ridge stands √(s² − p²) high. Shut, the folded strip reaches `p + s`
from the gutter, so the script refuses `glue_distance + side > page_width − 6 mm`, sides less than
2 mm longer than the glue distance, and tents wider than the card. The piece lies 0.2 mm above the
card (less than either stock's collision thickness), and its fold angles are the signed turns
between consecutive links of that slightly lifted kite.

## The fold program

The program is `kinematic`. It closes the card from flat to 170° (10 substeps): the tent folds down
inside. Then it opens the card flat again (10 substeps), and the tent stands. Each state lists the
card's gutter and the piece's three folds.

The script checks the motion exactly: it poses the piece from its left tab with
`pliego.kinematics.face_transforms` and the program's angles, and requires every vertex to land
where the kite puts it, including the right tab on its glue zone on the turning page. The worst
error is about 10⁻¹³ mm.

**Preview and engine.** The two `glue` joins hold the tabs to the card for the physics engine. The
preview does not need them: the card's gutter and the piece's folds are in the same fold program,
and the piece is posed from its left tab, which sits on the card's fixed page. So the studio
preview animates both, with the right tab staying on its page (checked on the exported documents:
within 0.35 mm at the defaults and presets, the lift plus the preview's linear blend between states). The preview stops at 170°
because its sheets have no thickness; the real card shuts flat. The engine adds the card's weight
and spring.

## Making one by hand

1. Export both sheets (`svg`, `dxf`, `pdf` or `hpgl`): cut the card and the strip, and score the
   gutter and the strip's three folds.
2. Fold the strip: valley at each tab, mountain at the ridge.
3. Mark the two glue lines on the inside of the card, `glue_distance` from the gutter on each page.
4. Glue one tab with its fold on the line. Put glue on the other tab, close the card on it and press:
   the kite places it. Let it dry, then open the card flat.

## Parameters

| id | meaning | default | range |
|---|---|---|---|
| `page_width`, `page_height` | one page of the card | 150, 150 mm | 90–220, 90–260 mm |
| `glue_distance` | p: tab folds from the gutter | 35 mm | 10–90 mm |
| `side` | s: tab fold to ridge | 55 mm | 15–120 mm |
| `tent_width` | width of the strip along the gutter | 80 mm | 20–200 mm |
| `tab_width` | glue tab width | 12 mm | 8–20 mm |
| `tent_offset` | position along the gutter (0 bottom, 1 top) | 0.5 | 0–1 |

Presets: `steep-roof`, `low-roof`, `a6-card`.

## History and sources

The tent is a general mechanism of paper engineering. The pop-up literature describes it, for
example David A. Carter and James Diaz, *The Elements of Pop-Up* (Little Simon, 1999) and Duncan
Birmingham, *Pop-Up Design and Paper Mechanics* (GMC Publications, 2010). The kernel's own
`pliego.popup.tent` generator solves the same kite. No published design is copied; the geometry is
computed by this cartridge.

## Provenance and licence

Original MADFAM geometry (the lineage records the general mechanism, credited to the tradition).
Published under CERN-OHL-W-2.0 like every object in the commons (see the commons root `LICENSE`).
