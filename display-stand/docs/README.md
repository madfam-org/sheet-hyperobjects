# Display stand

| | |
|---|---|
| **en** | A counter display from one sheet of board: a product tray with a double front lip, a header card leaning back and an easel back that locks into a rigid triangle, with the print side facing the shopper. |
| **es** | Un exhibidor de mostrador de una sola hoja de cartón: una charola con frente doble, una cabecera inclinada hacia atrás y un atril que se traba en un triángulo rígido, con la cara impresa hacia el cliente. |
| **fr** | Un présentoir de comptoir dans une seule feuille de carton : un plateau à bord avant double, un fronton incliné vers l'arrière et une béquille qui se verrouille en un triangle rigide, la face imprimée vers le client. |
| **pt** | Um expositor de balcão de uma só folha de cartão: uma bandeja com frente dupla, uma cabeceira inclinada para trás e um cavalete que trava num triângulo rígido, com a face impressa para o cliente. |

## What it is

A counter display holds products on a shop counter under a printed header card. This hyperobject
makes one from a single blank of corrugated board or paperboard: a tray, a header card rising
behind it and leaning back, and an easel back that props the header — the easel, its floor and
the header lock into a triangle with tabs, so the stand needs no glue to stand up. The print side
faces the shopper: the tray's inside, the header's front and the outside of the front lip.

## Geometry

With t the board's caliper, panels are inside + t.

- **Print side up.** Unlike a shipping box, the blank is placed print side up and the tray's walls
  rise as valley folds, so the print shows inside the tray and on the header's front.
- **Front lip.** A double wall: the inner leaf rises 90° and the outer leaf (t shorter) rolls 180°
  over its top to the outside, so its print faces the shopper. The side walls' front ears fold in
  between the two leaves and are trapped there; lock tabs on the outer leaf drop 1.5t into slots
  2t wide through the base's front fold.
- **Side walls** follow the leaning header: their back edges are slanted by `lean`. An ear on each
  slanted edge folds in by exactly 90° (the header contains the stand's width direction, so it is
  perpendicular to the side walls) and is glued to the header's front.
- **Header and easel.** In the side view the header runs from the base's back edge B to its top T
  (length `header`, leaning back by `lean`), a strut 0.6 of the width hangs from T down behind to
  the easel's foot E on the table (`foot` behind B), and a floor panel runs from E back to B,
  where its tabs slide flat into slots through the base's back fold. The fold angles are the
  triangle's own: base–header 90° − lean (valley), header–strut and strut–floor from the angles of
  triangle BTE (mountain: the easel lies behind the print side). At the defaults they are 80°,
  155.1° and 104.9°, and the strut is 327.8 mm long. The header's top corners outside the strut's
  hinge are rounded.

## The fold program

Every fold is straight and the blank is a face tree, so the program is kinematic and exact: raise
the lip's inner leaf; raise the side walls and fold their ears in; roll the lip's outer leaf over
the ears and lock it; raise the header; fold the easel down behind and run its floor under until
the tabs reach the back slots — the triangle closes exactly at the end of that step. The preview
poses the blank from its first face, so the first side wall starts already raised.

Each glue zone is also a `glue` join with `active_from` (sheet-document spec §5.19): the script
reads the weld from the closed pose (the face the zone lands on, the map onto it and the side the
tab lies on; the region is the zone inset by 0.75 mm), and the glue takes hold at the step after
the last fold on the path from tab to zone, so the program starts from the flat blank and ends
glued. The back ears take hold once the header is up. **Limits.** The tabs' snap and the stand's
stability with products in it are the physics engine's part; no load rating is claimed.

## Making one by hand

Print the blank at 100 % (print side up), cut it out with the slots and tabs, and score the folds.
Raise the lip's inner leaf, then the side walls with their front ears folded in front of the lip;
roll the outer leaf down over the ears and push its tabs into the slots. Glue the back ears to the
header. Stand the header up, fold the easel down behind it, lay its floor on the table and slide
the floor's tabs into the slots at the back of the tray.

## Parameters

| Parameter | Range | Meaning |
|---|---|---|
| `width` | 80–500 mm | tray width, inside |
| `depth` | 50–400 mm | tray depth, front to back, inside |
| `lip` | 15 mm – depth/2 | front lip height |
| `side` | lip – 1.5 × depth | side wall height |
| `header` | side + 60 – 800 mm | header panel length, from the base to its top |
| `lean` | 0–25° | header lean |
| `foot` | 0.25–0.8 × header | how far behind the tray the easel meets the table |
| `stock` | corrugated E or B flute, SBS 350, FBB 300 | board |
| `branding` | on / off | sample brand artwork on the header (`pliego:artwork`) |

Presets: small counter display (SBS), tall header (B flute), upright header.

## History and sources

Printed board counter displays are a common point-of-sale fixture. No origin is claimed here.

- Wikipedia, *Point of sale display* — https://en.wikipedia.org/wiki/Point_of_sale_display
- Wikipedia, *Corrugated fiberboard* — https://en.wikipedia.org/wiki/Corrugated_fiberboard
- Pliego sheet-document spec, `pliego:dielines` (§5.9), and `pliego.dieline` (in the Pliego
  repository).

## Provenance and licence

Original MADFAM design: the tray, the rolled front lip with trapped ears, the header and the locked
easel triangle are computed in `main.py` (the `lineage` entry says so, licence `original`). No
catalogue drawing is reproduced. The sample brand mark is original placeholder artwork. Licence
CERN-OHL-W-2.0 (both manifest fields).
