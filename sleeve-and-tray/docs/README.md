# Sleeve and tray

| | |
|---|---|
| **en** | The matchbox-style pack from the tray's inside dimensions: a tray with rolled locking ends and a glued sleeve that fits it, with a fold program for the blanks and a slide control for the assembled pack. |
| **es** | El empaque tipo caja de cerillos a partir de las medidas interiores de la charola: una charola con cabeceras enrolladas que se traban y una funda pegada a su medida, con secuencia de armado para los suajes y un control de deslizamiento para el empaque armado. |
| **fr** | L'emballage façon boîte d'allumettes à partir des dimensions intérieures du tiroir : un tiroir aux extrémités roulées et verrouillées et un fourreau collé à sa mesure, avec une séquence de montage pour les flans et un curseur de glissement pour l'emballage monté. |
| **pt** | A embalagem estilo caixa de fósforos a partir das medidas internas da gaveta: uma gaveta com cabeceiras enroladas que travam e uma luva colada à sua medida, com sequência de montagem para os cortes e um controlo de deslize para a embalagem montada. |

## What it is

A sleeve-and-tray pack is an open tray that slides into a tube. This hyperobject makes both parts
from the tray's inside dimensions: the tray locks together without glue, and the sleeve is a glued
tube sized to the tray's outside plus a clearance you choose. It has two modes:

- **`slide`** (assembled): both parts erected, the sleeve a fixed rigid board and the tray a rigid
  board on a `translate` mechanism; the `slide` control pushes the tray out of the sleeve and back.
- **`fold`** (blanks): the two die-cut blanks, side by side, with their fold programs.

## Geometry

With t the board's caliper (thickness compensation), the tray's inside L × W × D and the
clearance c:

- **Tray.** The base is (W + t) × (L + t), its long axis along the slide. The long walls are
  D + t high, each with an ear on both ends (W/2 + t/2 − t wide, inset from the knife lines by
  max(2t, 1.5 mm)). Each end wall is a double leaf: the outer leaf is D + t high, the inner leaf
  t shorter, so the rolled wall closes flush. Lock tabs on the inner leaf's edge drop into slots
  2t wide cut through the base fold (the base and the outer leaf are notched t each); the tabs
  drop 1.5t, because the inner leaf ends t above the base's centre plane, so they end flush with
  the base's underside and nothing hangs below the tray to catch on the sleeve.
- **Sleeve.** Bottom, side, top, side and a tapered glue flap, folded into a tube along the
  tray's long axis. Inside it is W + 2t + c across and D + t + c high (the tray's outside plus
  c); it is L + 2t long, and its panels are inside + t.
- **Assembled.** The sleeve's bottom sits t + c/2 under the tray's base, centred on it; the
  `translate` mechanism moves the tray along its long axis by up to 0.8 of the sleeve's length.

## The fold program

Both blanks are face trees (every fold is straight, no hinge meets another inside a sheet), so the
`fold` mode's program is kinematic and exact: raise the tray's long walls, fold the ears in,
raise the end walls over the ears, then roll the ends in and drop the tabs into the slots; fold
the sleeve into a tube and glue the joint. The preview poses each blank from its first face, so
the tray's first long wall starts already raised. The `slide` mode has no fold program: its
`slide` control drives a rigid translation the preview can show.

In the `fold` mode the sleeve's joint is also a `glue` join with `active_from` (sheet-document
spec §5.19), its weld read from the closed pose; it takes hold in a short final *press* step,
after the sleeve is formed, so the blanks start flat and end glued. **Limits.** The tabs' snap
into the slots and the friction of the tray in the sleeve are the physics engine's part.

## Making one by hand

Print both blanks at 100 %, cut them out (including the slots and the tabs) and score the folds.
For the tray: raise the long walls, fold the ears in, raise each end wall, roll its inner leaf
down over the ears and push the tabs into the slots. For the sleeve: fold it around the tray to
check the fit, then glue the joint flap inside the far side panel and let it dry before sliding
the tray in.

## Parameters

| Parameter | Range | Meaning |
|---|---|---|
| `length` | 40–300 mm | tray inside length, along the slide |
| `width` | 30–200 mm | tray inside width (clamped to the length) |
| `depth` | 12–80 mm | tray inside height (clamped to the width) |
| `clearance` | 0.3–3 mm | added to the sleeve's inside width and height |
| `stock` | FBB 300, SBS 350, cardstock 300, greyboard 1.5 mm | board for both parts |
| `branding` | on / off | sample brand artwork on the sleeve's top (`pliego:artwork`) |

Presets: matchbox size, jewellery box (SBS), rigid greyboard drawer.

## History and sources

The tray-in-sleeve construction is best known from the matchbox, whose sliding box has long been
made of card or thin wood; this hyperobject uses the construction for any contents and makes no
claim about who first used it.

- Wikipedia, *Matchbox* — https://en.wikipedia.org/wiki/Matchbox
- Wikipedia, *Folding carton* — https://en.wikipedia.org/wiki/Folding_carton
- Pliego sheet-document spec, `pliego:dielines` (§5.9) and mechanisms (§5.4), and
  `pliego.dieline` (in the Pliego repository).

## Provenance and licence

Original MADFAM design: the tray's rolled locking ends, ears and flush tabs, and the sleeve, are
computed in `main.py` (the `lineage` entry says so, licence `original`). No catalogue drawing is
reproduced. The sample brand mark is original placeholder artwork. Licence CERN-OHL-W-2.0 (both
manifest fields).
