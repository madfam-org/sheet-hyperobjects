# Paper chain

| | Title | Summary |
|---|---|---|
| en | Paper chain | Strips of paper looped and glued into rings, each threaded through the one before, so the rings interlock into a hanging chain. |
| es | Cadena de papel | Tiras de papel enrolladas y pegadas en aros, cada una pasada por la anterior, de modo que los aros se entrelazan en una cadena colgante. |
| fr | Guirlande de papier | Des bandes de papier bouclées et collées en anneaux, chacune passée dans la précédente, si bien que les anneaux s'entrelacent en une guirlande suspendue. |
| pt | Corrente de papel | Tiras de papel enroladas e coladas em aros, cada uma passada pela anterior, de modo que os aros se entrelaçam numa corrente pendurada. |

## What it is

The glued paper chain: cut strips, loop the first into a ring and glue its ends, pass the next strip
through it and glue that one too, and so on until the chain is long enough. Each link is one sheet;
the cartridge computes how far apart the rings hang so that they interlock without touching, shows
the chain growing link by link, and hands the glued chain to the physics engine.

## Geometry

Each strip is `strip_length` × `strip_width` mm. Its ring has circumference C = length − overlap,
and the overlap is rounded to whole panels and chamfered at its corners.

**Segmentation.** A ring is a curved band, modelled as a prism of `sides` narrow flat panels
(18 by default): `F` lines across the strip, with treatment `none` (plain paper, never scored or
cut). The closed ring is an exact isometry of the strip: a regular polygon prism whose side is one
panel wide, inscribed radius a = w / (2 tan(π/n)). In the closed ring the overlap lies exactly on
the first panels, inside, and a `glue` join welds it there (map = translation by −C).

**Linking.** The chain hangs straight down. Each link's plane turns 90° from the one before (planes
XY and YZ alternately), so every ring passes through its neighbours. Where two neighbours cross,
the lower sides of one ring rise by δ at the edge of the other's band, and the other's upper sides
fall by the same δ, so the pitch between centres is

p = 2a − 2δ − g,

with g = `gap` the clearance left between them (1 mm by default). The script refuses a chain whose
rings would not interlock (p ≥ 2a) or whose link k would touch link k + 2 (p ≤ circumradius). For
the default strips (200 × 25 mm, 20 mm overlap): a = 28.36 mm, p = 50.25 mm, and eight links hang
408 mm. Each strip's outline is checked with `pliego.papercut.analyze`.

## The fold program

**Mode `make`.** The links are flat strips, each placed where its ring will hang: its sheet
placement puts the strip's first panel at the bottom of its ring. A `kinematic` program then loops
and glues them one by one, each step "pass strip k through link k − 1, loop it and glue the ends".
A last short step holds the final seam. Each ring's seam is a `glue` join with `active_from`
(sheet-document spec §5.19): it takes hold at the next link's step, once its ring is closed (the
last one at the hold step), so the strips start flat and the program ends glued. It ends in the
chain, which is also written as `target:chain`.

**Mode `glued`** is the finished chain for the physics engine: eight glue welds and an `initial`
frame of the hanging chain. The first link is held at the top of its ring by a `pin` join that a
`translate` mechanism moves, so the control `Lift the chain` raises it by up to 100 mm.

**Why two modes.** A single physical program would have to roll each flat strip into a closed ring
by driving its panel lines, thread it through the previous ring and only then let the glue take
hold. The engine cannot close a rolled band that way yet (on the paper crown it leaves the ends
37 mm apart, so the glue finds nothing to weld), and a kinematic program holds every strip rigid,
so it cannot let the glued chain hang. `make` shows the making; `glued` hangs the chain.

**Preview and engine.** The studio preview plays the making. The flat strips start where the rings
will hang, and the preview does not stop one strip passing through another: threading a strip
through the previous ring, and the contact between links, are the engine's job. In mode `glued`
the `Lift` control needs the engine (it drives a pinned point) and is disabled in the preview,
which shows the hanging chain at rest. A real chain sags and its links rest on one another; the
rigid model keeps the computed pitch.

## Making one by hand

1. Export the strips (`svg`, `dxf`, `pdf` or `hpgl`) and cut them out; the panel lines are not on
   the cut file. A 200 mm strip fits across A4.
2. Put glue on the overlap of the first strip and close it into a ring, overlap inside.
3. Pass the next strip through the ring, close it and glue it. Repeat.

Copy paper and kraft hold the rings round; tissue paper makes a soft, light chain.

## Parameters

| id | meaning | default | range |
|---|---|---|---|
| `links` | number of links | 8 | 2–16 |
| `strip_length` | length of each strip, overlap included | 200 mm | 100–300 mm |
| `strip_width` | width of each strip | 25 mm | 10–50 mm |
| `overlap` | glue overlap (rounded to whole panels) | 20 mm | 10–40 mm |
| `sides` | panels per ring (model resolution, not cut) | 18 | 10–32, even |
| `gap` | clearance between crossing links | 1 mm | 0.5–10 mm |
| `stock` | `copy-80`, `kraft-120`, `cardstock-160`, `papel-de-china`, `foil-paper` | `copy-80` | |
| `palette` | colours: `rainbow`, `festive`, `kraft` | `rainbow` | |

Presets: `festive` (12 links in red, green and gold), `small-links` (150 × 18 mm strips),
`tissue` (papel de china).

## History and sources

David Mitchell's Public Paperfolding History Project finds the first record of paper chains in
Part Two of *The Kindergarten Guide* by Maria Kraus-Boelte and John Kraus (New York, 1882). Early
chains were often locked with slits and tabs; a glued construction appears in Will Blyth's
*More Paper Magic* (1923) (https://origamiheaven.com/historyofpaperchains.htm). A recollection of
Edwardian Christmases describes children cutting coloured paper into strips and gluing the ends
of each strip round another with home-made flour-and-water paste
(https://1900s.org.uk/1900s-christmas-decorations.htm). The chain made here is the glued kind; no
published design is copied.

## Provenance and licence

Original MADFAM geometry; the lineage credits the glued paper chain to the traditional children's
paper craft. Published under CERN-OHL-W-2.0 like every object in the commons (see the commons root
`LICENSE`).
