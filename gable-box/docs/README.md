# Gable box

| | |
|---|---|
| **en** | A gable-top carry box with a handle, from inside dimensions: roof panels that meet at the ridge, handles back to back with matching hand holes, gable ends whose support flaps carry the roof, and a tuck or 1-2-3 bottom. |
| **es** | Una caja de transporte con techo a dos aguas y asa, a partir de las medidas interiores: techos que se juntan en la cumbrera, asas espalda con espalda con orificios que coinciden, frontones cuyas solapas de apoyo sostienen el techo y fondo de lengüeta o 1-2-3. |
| **fr** | Une boîte de transport à pignon et à poignée, à partir des dimensions intérieures : toits qui se rejoignent au faîtage, poignées dos à dos aux trous de prise alignés, pignons dont les rabats d'appui portent le toit, et fond à patte rentrante ou 1-2-3. |
| **pt** | Uma caixa de transporte com telhado de duas águas e alça, a partir das medidas internas: telhados que se juntam na cumeeira, alças costas com costas com furos coincidentes, frontões cujas abas de apoio sustentam o telhado e fundo de encaixe ou 1-2-3. |

## What it is

A gable box is a carry box whose top rises into a pitched roof and ends in a handle: the front
and back walls fold in as two roof panels, then turn back up as two handle panels that meet back
to back, each with the same hand hole. This hyperobject generates the whole blank — four walls, a
glue flap, the bottom, the roofs, the handles and the two gable ends — from the inside dimensions
of the contents, in folding boxboard, SBS, cardstock or kraftliner. It is a different construction
from the gable-top liquid carton (the milk carton), whose top is a folded gusset sealed into a fin.

## Geometry

Panels run front · side · back · side with the glue flap on the last side. With t the board's
caliper (thickness compensation, centre-line rule):

- **Walls** are inside + t; the front panel's top and bottom flaps are trimmed by max(t, 0.5 mm)
  where they meet the glue flap.
- **Roofs.** The handles meet at the box's middle, each t/2 off the centre plane, so the roof's
  run is (W + t)/2 − t/2 = W/2 and its slant is √(h² + (W/2)²) for a rise h. Each roof tilts in by
  β = atan(W / 2h) from the wall (a mountain fold) and its handle turns back up by β (a valley
  fold).
- **Gable ends.** Each side wall ends in a triangle whose slanted edges run parallel to the roof
  and t inside it, so the base corners move in by t·r/h (r the slant) and the apex sits just under
  the ridge. A support flap hinged on each slanted edge folds in by exactly 90°, because the roof
  plane contains the box's length direction and is therefore perpendicular to the gable; the roof
  rests on it. The gable ends are slit free of the roofs.
- **Handle.** Both handle panels carry the same stadium-shaped hand hole (up to 95 × 24 mm,
  centred), so the holes align when the handles close. A peel-and-seal strip along the front
  handle's top holds the two together.
- **Bottom.** A tuck bottom (two dust flaps and a tuck lid on the back panel), or a 1-2-3
  snap-lock bottom (minor, major and minor flaps, then the front flap's tongue locked under them).

## The fold program

Every fold is straight and no hinge meets another inside the sheet — flaps are separated by slits —
so the blank is a face tree and the program is kinematic and exact: form the tube and glue the
joint, close the bottom (two steps for the tuck, four for the 1-2-3), fold the roof supports in,
then bring the roofs together and raise the handles back to back. The box rests on its front
panel throughout.

Each glue zone is also a `glue` join with `active_from` (sheet-document spec §5.19): the script
reads the weld from the closed pose (the face the zone lands on, the map onto it and the side the
tab lies on; the region is the zone inset by 0.75 mm), and the glue takes hold at the step after
the last fold on the path from tab to zone, so the program starts from the flat blank and ends
glued. The joint takes hold once the tube is formed; the handle seal, closed in the last step, in
a short final *press* step. **Limits.** In the physics engine a kinematic program poses the blank
rigidly, so the welds are recorded state there, not forces. The snap-lock tongue's friction and
the handle carrying a load need the physics engine. No load rating is claimed.

## Making one by hand

Print the die at 100 %, cut the outline and the hand holes, and score the folds. Glue the joint
flap inside the front panel's free edge. Close the bottom, then fold the four roof supports in
against the gable ends. Bring the roofs down onto the supports, raise the handles, check that the
hand holes line up and press the peel-and-seal strip (or a line of glue) to close them.

## Parameters

| Parameter | Range | Meaning |
|---|---|---|
| `length` | 40–300 mm | width of the front wall, inside |
| `width` | 30–200 mm | front to back, inside (clamped to the length) |
| `depth` | 30–300 mm | wall height, inside |
| `rise` | 0.3–1.5 × width | ridge height above the walls |
| `handle` | 30–120 mm | handle panel height |
| `bottom` | 1-2-3 snap-lock, tuck | bottom closure |
| `stock` | FBB 300, SBS 350, cardstock 300, kraftliner 150 | board |
| `branding` | on / off | sample brand artwork on the front wall (`pliego:artwork`) |

Presets: favour box, kraft lunch box, bakery box (SBS).

## History and sources

Gable-topped carry boxes are a general style of folding carton, used for food, favours and gifts;
the sources consulted give no single origin, and none is claimed here.

- Wikipedia, *Folding carton* — https://en.wikipedia.org/wiki/Folding_carton
- Wikipedia, *Carton* — https://en.wikipedia.org/wiki/Carton
- Pliego sheet-document spec, `pliego:dielines` (§5.9), and `pliego.dieline` (in the Pliego
  repository).

## Provenance and licence

Original MADFAM design: the gable ends and their roof supports, the roof and handle geometry, the
hand holes and both bottoms are computed in `main.py` (the `lineage` entry says so, licence
`original`). No catalogue drawing is reproduced. The sample brand mark is original placeholder
artwork. Licence CERN-OHL-W-2.0 (both manifest fields).
