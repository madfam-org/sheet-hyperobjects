# Rigid set-up box

| | |
|---|---|
| **en** | The wrapped greyboard box of luxury packaging — one tray, a telescope or a shoulder box with a neck — generated from inside dimensions and the real board and paper calipers. |
| **es** | La caja de cartón gris forrada del empaque de lujo —una charola, una telescópica o una caja con cuello— generada a partir de las medidas interiores y del calibre real del cartón y del papel. |
| **fr** | Le coffret en carton gris habillé de l'emballage de luxe — un plateau, un télescopique ou un coffret à hausse — généré à partir des dimensions intérieures et de l'épaisseur réelle du carton et du papier. |
| **pt** | A caixa de cartão cinza forrada da embalagem de luxo — uma bandeja, uma telescópica ou uma caixa com colarinho — gerada a partir das medidas internas e da espessura real do cartão e do papel. |

## What it is

A set-up (rigid) box is not folded flat and shipped flat like a carton: it is built once, as a
stiff greyboard shell, and covered with a printed paper wrap that is pasted on and turned in over
the rim. It is the box of watches, jewellery, fragrances and anything meant to be kept. This
hyperobject carries the three classic constructions:

- **Tray** (mode `tray`): one wrapped tray — a base on its own, or a presentation tray.
- **Telescope** (mode `telescope`): a base and a lid that slides down over it, deep or shallow.
- **Shoulder** (mode `shoulder`): a base with a wrapped neck glued inside it and standing above
  its rim; the lid slides over the neck and stands on the base's rim, the shoulder.

Each part is two sheets: the **board** tray (greyboard 1.5 mm or folding boxboard) and its
**wrap** (elephant hide, kraft, foil paper or washi).

## Geometry

Everything is computed from the inside dimensions L × W × D (W ≤ L), the board's caliper t and
the wrap's caliper w, both read from their stock cards. Panels are laid on the mid-surface, as
every Pliego dieline is:

- **Board tray.** Base (L + t) × (W + t). Long walls span the full outside, L + 2t (t/2 past the
  base at each end); end walls are butted between them, W long. Walls are D + t/2 tall. The
  inside is exactly L × W × D. Corner stay tape zones are marked on the long walls' ends.
- **Wrap.** Base (L + 2t + w) × (W + 2t + w), glued under the board. Walls rise D + t + w to the
  rim; a rim strip t + w wide crosses the wall top; the turn-in (`turn_in`, kept 3 mm clear of
  the floor) runs down the inside. The long sides carry the corner **ears** (`ear` mm), which
  turn round each corner and are covered by the end's wrap; long turn-ins are L − 1 long, end
  turn-ins W − 2w − 1, so they do not overlap at the corners.
- **Telescope lid.** Its board's inside is the base's outside (L + 2t + 2w) plus its own turn-in
  (2w) plus the `clearance` on every side, so the clearance is the air gap the lid slides on
  over its turn-in. Its depth is `lid_depth`, at most D. Closed, its top rests on the base's rim.
- **Shoulder.** The neck (board tube, closed by a glue flap) is the base's inside less the base's
  turn-ins and 0.1 mm, stands on the floor and rises `neck_height` above the rim; its wrap covers
  the exposed part and turns in over the neck. The lid slides over the neck with the clearance
  (again past its own turn-in), is `neck_height` deep and stands on the rim. It stands proud of
  the base by clearance + w − 0.1 mm per side (0.32 mm with the defaults).

Measured in the closed pose with the defaults (L 160, W 120, D 60, greyboard 1.5, elephant hide
0.12, clearance 0.3): inside 160 × 120 × 60, wrap 0.06 mm off the board's faces, the lid's
turn-in 0.30 mm off the base's wrap, the shoulder neck 0.10 mm off the base's turn-in.

## The fold program

A kinematic program, one dieline after another (the studio preview plays it in full):

1. raise the board tray's walls and stay the corners;
2. raise the wrap's long sides and wrap the ears round the corners;
3. raise the wrap's ends over the ears;
4. turn the wrap in over the rim;
5. the neck (shoulder): fold the band into a tube and glue it, then its wrap, turned in;
6. the lid: the same as the base, open side down.

Every blank is a face tree (flaps parted by slots and slits): rigidly foldable, nothing for the
motion solver to close. **What this does not model:** board thickness in the 3-D pose (folds
turn on the mid-surface; the inside dimensions are compensated, the pose is not), the paste and
its drying, the stay tape as its own sheet, and the slow, air-cushioned fall of a lid — which is
why the clearance is a parameter: a tighter gap traps more air, so the lid falls slower and is
harder to lift.

## Making one by hand

Cut the board tray from greyboard with a knife against a steel rule, score the wall folds on the
inside face (or V-groove them for a crisp outside corner), raise the walls and tape each corner
with gummed paper tape. Paste the wrap's base and set the tray on it, square to the marks; paste
and raise the long sides, burnish the ears round the corners, then the ends over them. Paste the
rims and turn-ins and burnish them down inside. For the lid repeat with the lid's blanks; for a
shoulder box glue the wrapped neck inside the base before fitting the lid.

## Parameters

| Parameter | Range | Meaning |
|---|---|---|
| `length`, `width`, `depth` | 40–500, 30–400, 15–250 mm | inside dimensions (width ≤ length) |
| `lid_depth` | 10–250 mm | telescope lid depth (at most the base depth) |
| `neck_height` | 8–80 mm | shoulder: neck above the rim, also the lid depth |
| `clearance` | 0.1–1.5 mm | lid air gap per side |
| `board` | greyboard 1.5 · folding boxboard 300 | board stock |
| `wrap` | elephant hide · kraft · foil · washi | wrap stock |
| `turn_in` | 5–30 mm | wrap turned in over the rim |
| `ear` | 6–25 mm | corner ear width |

Presets: watch box, jewellery shoulder box, apparel box, card or token box.

## History and sources

Rigid paper boxes, built up from board and covered with paper, came before the folding carton;
Robert Gair's pre-cut folding carton (1879) made the cheap carton possible, and the rigid box
stayed the premium format. This cartridge reproduces no manufacturer's drawing: the geometry is
generated from the parameters.

- Wikipedia, *Paperboard* — https://en.wikipedia.org/wiki/Paperboard
- Wikipedia, *Robert Gair* — https://en.wikipedia.org/wiki/Robert_Gair
- Pliego physics memo §(h), *Board, corrugation and foam* (in the Pliego repository), and
  `pliego.dieline` for the mid-surface conventions.

## Provenance and licence

Original MADFAM geometry, computed with `pliego.dieline` from the parameters; the construction is
an industry craft attributed to that tradition. Licence CERN-OHL-W-2.0 (both manifest fields).
