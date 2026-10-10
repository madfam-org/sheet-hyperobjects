# Honeycomb panel

| | |
|---|---|
| **en** | Structural paper honeycomb: kraft ribbons glued along alternate stripes and expanded into hexagonal cells between two liners, with the core's density and the panel's areal density computed from the cell size and the papers. |
| **es** | Panal estructural de papel: tiras de kraft pegadas en franjas alternas y expandidas en celdas hexagonales entre dos caras, con la densidad del núcleo y la densidad superficial del panel calculadas a partir del tamaño de celda y los papeles. |
| **fr** | Nid d'abeilles structurel en papier : des rubans de kraft collés en bandes alternées et expansés en alvéoles hexagonales entre deux peaux, avec la masse volumique de l'âme et la masse surfacique du panneau calculées à partir de la taille d'alvéole et des papiers. |
| **pt** | Colmeia estrutural de papel: fitas de kraft coladas em faixas alternadas e expandidas em células hexagonais entre duas faces, com a densidade do núcleo e a gramagem do painel calculadas a partir do tamanho da célula e dos papéis. |

## What it is

A paper honeycomb panel is a sandwich: a light core of hexagonal paper cells between two flat
liners. The core is made by gluing paper ribbons to each other along alternate stripes, stacking
them, and pulling the stack open so every unglued stretch of ribbon becomes a cell wall. This
hyperobject generates the expanded core and its liners from the cell size and the core height,
and computes what the panel weighs. It has two modes:

- **`panel`** — the expanded core between its liners; the `lift` control raises the top liner
  so the cells show.
- **`expand`** — two glued ribbons pulled open into one row of cells, the expansion itself.

## Geometry

- **Cells.** Cell size s is the hexagon's width across flats; the wall length is a = s/√3. A
  ribbon repeats a node wall (a, along the ribbon), a wall rising at 60°, a node wall and a wall
  falling at 60°: period 3a along the panel, pitch a·√3/2 between ribbons. Neighbouring ribbons
  run in opposite phase, so one ribbon's upper node walls lie on the next one's lower node walls:
  those are glued (`glue` joins, which the initial frame satisfies) and become double walls; all
  other walls are single. The creases between walls are folded 60° and pre-set (`rest`) in the
  panel, as an expanded core holds its shape.
- **Panel.** The core spans `periods` cells along the ribbons and `ribbons` ribbons across, and
  the liners cover it; the liners sit half their caliper above and below the core.
- **Densities.** Per unit area of panel the core holds 8/(3√3·a) mm of ribbon per mm², so its
  paper weighs `gsm_core × h × 8/(3√3·a)` g/m² for a core height h — a relative density of
  8/(3√3)·(t/a), the double-walled hexagonal honeycomb. The glued node area adds
  `10 g/m² × h/(3·a·√3/2)` (10 g/m² of bonded area is an adhesive estimate [E]). The core density
  is that mass over h; the panel's areal density adds both liners and 15 g/m² of adhesive on each
  face [E]. At the defaults (20 mm cells, 25 mm core, kraft 120 g/m², kraftliner 150 g/m²) the
  core paper is 400 g/m², the node glue 8.3 g/m², the core density **16.3 kg/m³** and the panel's
  areal density **738 g/m²**. The script also weighs the ribbons it generates over the panel's
  plan (392 g/m² at the defaults; the edge cells make the difference).

## The fold program

In the `panel` mode the expanded core is the initial frame: each ribbon is a rigid face tree
posed from its first node wall. The liners are rigid boards, the bottom one fixed, the top one on
a `translate` mechanism; `lift` raises it off the core (the preview drives it). In the `expand`
mode the kinematic program folds every crease of both ribbons from 0° to ±60°. Both ribbons are
posed from their first node wall, which is glued to the other's, and the two waves are mirror
images, so every glued stripe of one stays face to face with the other's at every instant — the
motion is exact. A full core cannot be shown that way in the preview (each ribbon would need its
own moving root), so the panel mode shows it expanded. **Limits.** The liners are not glued to
the core in the document; the core's crushing and shear strength, the ribbons bending as they
open and the liners' bond are the physics engine's part. No strength rating is claimed.

## Making one by hand

Cut kraft ribbons as wide as the core height. Lay one flat, draw glue stripes a wide every 2a
along it, lay the next ribbon on top with its stripes shifted by a, and repeat. Once dry, pull the
stack open across the ribbons until the cells are regular hexagons, and glue a liner on each face.
The stripes must be a apart and as wide as a wall, or the cells come out irregular.

## Parameters

| Parameter | Range | Meaning |
|---|---|---|
| `cell` | 8–40 mm | cell size across flats |
| `core_height` | 5–100 mm | core height (ribbon width) |
| `periods` | 2–8 | cells along a ribbon |
| `ribbons` | 3–12 | ribbons in the core (`panel` mode) |
| `core_stock` | kraft 120, kraftliner 150 | core paper |
| `liner_stock` | kraftliner 150, cardstock 300, greyboard 1.5 mm | liners (`panel` mode) |

Presets: packaging board (10 mm cells), thick core (30 mm cells, greyboard liners).

## History and sources

Expanded honeycomb cores — sheets glued in staggered stripes and pulled open — are made from paper,
aramid paper and metal foils for packaging, doors, furniture and aerospace panels.

- L. J. Gibson and M. F. Ashby, *Cellular Solids: Structure and Properties*, 2nd ed., Cambridge
  University Press, 1997 (honeycomb geometry and relative density).
- Wikipedia, *Honeycomb structure* — https://en.wikipedia.org/wiki/Honeycomb_structure
- Wikipedia, *Sandwich-structured composite* —
  https://en.wikipedia.org/wiki/Sandwich-structured_composite

## Provenance and licence

Original MADFAM design: the ribbons, their bonded stripes, the expanded core, the liners and the
density formulas are computed in `main.py` (the `lineage` entry says so, licence `original`); the
expansion process is general industrial practice. Licence CERN-OHL-W-2.0 (both manifest fields).
