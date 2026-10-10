# Presentation folder

| | |
|---|---|
| **en** | A pocket folder from one sheet of board: two covers on a capacity spine (two scores), a glued pocket in each cover and business-card slits, for A4 or US Letter papers. |
| **es** | Una carpeta con bolsillos de una sola hoja de cartulina: dos tapas sobre un lomo de capacidad (dos marcados), un bolsillo pegado en cada tapa y ranuras para tarjeta, para hojas A4 o carta. |
| **fr** | Une chemise à pochettes dans une seule feuille de carton : deux couvertures sur un dos de capacité (deux rainages), une pochette collée dans chaque couverture et des fentes pour carte, pour feuilles A4 ou US Letter. |
| **pt** | Uma pasta com bolsos de uma só folha de cartão: duas capas sobre uma lombada de capacidade (dois vincos), um bolso colado em cada capa e fendas para cartão, para folhas A4 ou US Letter. |

## What it is

A presentation folder holds loose papers between two covers, with a pocket inside each cover.
This hyperobject cuts one from a single sheet of board: back cover, spine and front cover side
by side (the print side is the folder's outside), two pockets below the covers that fold up and
glue in place, and optional slits in the front pocket that hold a business card by its corners.
Presets give an A4 folder and a US Letter folder (the usual 9 × 12 in size).

## Geometry

- **Covers** are the content size plus a margin: 222 × 310 mm for A4, 9 × 12 in (228.6 ×
  304.8 mm) for US Letter, 158 × 222 mm for A5 (design margins [E]).
- **Capacity spine.** Two parallel scores `capacity` + t apart (t the board's caliper — the
  centre-line rule for two 90° folds), so the closed folder holds a stack `capacity` thick.
- **Pockets** fold up 180° from each cover's bottom edge, `pocket` deep, their top corner at the
  spine cut away at 45° for a grip. Each pocket stops a tab's width plus 1 mm (13 mm) short of its
  cover's outer edge, so its outer glue tab, folded under it, does not show; its inner tab, next to
  the spine, is as wide as the space between the two pockets allows (each pocket also keeps
  max(2 + t, 3.5 − spine/2) mm clear of the spine scores). The tabs carry glue zones.
- **Card slits.** A card (85 × 55 mm, or 3.5 × 2 in) is placed on the folded pocket; at each of
  its corners (four, or two opposite ones) a 14 mm knife cut runs across the corner,
  perpendicular to the card's diagonal and 4 mm in from the corner, so the corner tucks under it.
  The cuts are mapped back to the flat blank through the 180° pocket fold, (x, y₀ + d) ↦
  (x, y₀ − d).

## The fold program

Every fold is straight and no hinge meets another inside the sheet, so the blank is a face tree
and the program is kinematic and exact: fold the pocket tabs under, fold the pockets up onto the
covers, then close the folder about its two spine scores. The folder rests on its back cover.
**Limits.** The tabs' glue zones are fabrication data; welding them and the papers inside
pushing the spine open are the physics engine's part.

## Making one by hand

Print the blank at 100 % on the outside of the board, cut the outline and the card slits, and
score the two spine scores, the pocket folds and the tab folds. Fold each pocket's tabs under,
spread glue on their outer faces, fold the pocket up and press the tabs onto the cover's inside.
Fold the covers about the spine with the scores on the outside of the bends.

## Parameters

| Parameter | Range | Meaning |
|---|---|---|
| `size` | A4, US Letter, A5 | content size (covers add a margin) |
| `capacity` | 0–25 mm | stack the closed folder holds |
| `pocket` | 60–140 mm | pocket height (up to 0.45 × the cover's height) |
| `cards` | four, two, none | business-card slits in the front pocket |
| `card_size` | 85 × 55 mm, 3.5 × 2 in | the card the slits hold |
| `stock` | SBS 350, FBB 300, cardstock 300/250 | board |
| `branding` | on / off | sample brand artwork on the front cover (`pliego:artwork`) |

Presets: A4 folder, US Letter folder (9 × 12 in), A4 report folder (12 mm capacity).

## History and sources

Folders that keep loose papers between covers are long-standing office stationery; pocket folders
with card slits are a common printed-stationery product. No origin is claimed here.

- Wikipedia, *File folder* — https://en.wikipedia.org/wiki/File_folder
- Wikipedia, *Business card* (common card sizes) — https://en.wikipedia.org/wiki/Business_card
- Wikipedia, *ISO 216* (A4, A5) — https://en.wikipedia.org/wiki/ISO_216
- Pliego sheet-document spec, `pliego:dielines` (§5.9), and `pliego.dieline` (in the Pliego
  repository).

## Provenance and licence

Original MADFAM design: the covers, capacity spine, inset pockets with their tabs and the card
slits mapped through the pocket fold are computed in `main.py` (the `lineage` entry says so,
licence `original`). No catalogue drawing is reproduced. The sample brand mark is original
placeholder artwork. Licence CERN-OHL-W-2.0 (both manifest fields).
