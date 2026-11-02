# Retention insert · Inserto de retención · Insert de maintien · Inserto de retenção

| Language | Summary |
|---|---|
| en | An open paperboard pocket built around a content envelope and clearance, with foldable walls and optional rolled locking ends. |
| es | Un alojamiento abierto de cartulina construido a partir de la envolvente del contenido y la holgura, con paredes plegables y cabeceras enrolladas opcionales. |
| fr | Un logement ouvert en carton construit autour de l'enveloppe du contenu et du jeu, avec des parois pliables et des extrémités roulées facultatives. |
| pt | Um encaixe aberto de cartolina construído a partir do envelope do conteúdo e da folga, com paredes dobráveis e cabeceiras enroladas opcionais. |

## Construction

The content is `pocket_w × pocket_h × pocket_d`. The inside pocket is
`(pocket_w + 2·clearance) × (pocket_h + 2·clearance) × (pocket_d + clearance)`.
Clearance is an authored allowance per side, not a manufacturer fact. Panel
mid-surfaces include the selected board's caliper. Four side-wall ears tuck
behind the ends. With `lock_tabs`, each end rolls over those ears and its two
tabs enter the floor slots. Without locking ends, the open tray needs external
support; it is not claimed to be self-locking.

The original MADFAM rolled-end construction is adapted from
[sleeve-and-tray](https://github.com/madfam-org/sheet-hyperobjects/tree/main/sleeve-and-tray).
This family exposes the content envelope directly and produces the insert alone.
It does not recreate a commercial game's insert or die line.

`wall_folds` enables the erected pose. Turn it off to inspect the same cut-and-score
blank flat. The native kinematic sequence raises the long walls, folds the corner
ears, raises the ends and, when selected, rolls the locking leaves. SVG/PDF/DXF
carry the cutting layout; FOLD carries the native fold program. Animated GLB
exports use `pliego.export.to_glb(document, animate=True)`; the cartridge CLI
GLB export is a static initial pose by default. No artwork
or printed game material is included.

## Reference and archetypes

`atari-2600-envelope` reads the keystone's sourced media envelope at commit
`316287c00db2914c4b46b7c611e8a2af08e2c6ff`:
[published record](https://github.com/madfam-org/hyperobjects-spec/blob/316287c00db2914c4b46b7c611e8a2af08e2c6ff/src/hyperobjects_reference/objects/atari-2600-cartridge.json).
The CHM axes are width 82.6, height 25.4 and length/depth 95.2 mm. The thin
25.4 mm axis becomes `pocket_d`; the face is 82.6 ×95.2 mm. The source object's
centimetres were converted exactly by the catalog. The generated values and
field map are recorded in `preset-sources.json`. The 1 mm allowance belongs to
this design. This names a fit around that media envelope, not an original
Atari box or tray measurement.

The other presets and the defaults are labelled archetypes. A title edition
gets a named preset only when its content, insert and box measurements have
value-tier evidence. Unknown N64 and other title dimensions are not filled
from photographs, scans, a nearby model or a PDF page box.

## Making and verification limits

Cut the outline and floor slots, score the hinges, raise the side walls, tuck
the ears and close the ends. Confirm stock caliper with a test coupon before
cutting a specimen's final insert. The native model checks the planar sheet
and fold program; friction, lock strength, shock protection, archival material
compatibility and clearance under real stock compression need physical checks.
The preview is a geometric fold program, not a shipping-protection certification.
