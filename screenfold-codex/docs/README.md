# Screenfold codex

| | Title | Summary |
|---|---|---|
| en | Screenfold codex | The book form of Mesoamerica: a long amate strip folded back and forth like a screen, its leaves coated white on both sides; a blank structure, no historical imagery reproduced. |
| es | Códice biombo | La forma del libro mesoamericano: una tira larga de amate plegada en zigzag como un biombo, con las hojas cubiertas de blanco por ambos lados; una estructura en blanco, sin reproducir ninguna imagen histórica. |
| fr | Codex en paravent | La forme du livre mésoaméricain : une longue bande d'amate pliée en zigzag comme un paravent, ses feuillets enduits de blanc des deux côtés ; une structure vierge, sans aucune image historique reproduite. |
| pt | Códice em biombo | A forma do livro mesoamericano: uma tira longa de amate dobrada em zigue-zague como um biombo, com as folhas cobertas de branco dos dois lados; uma estrutura em branco, sem reproduzir nenhuma imagem histórica. |

## What it is

Before the European codex arrived, the books of Mesoamerica were screenfolds: a long strip of bark
paper or hide folded back and forth into leaves, read and painted on both sides, so that opening it
shows a run of pages at once. This cartridge gives the **structure** of that book form — a blank
strip on the commons' `amate` stock card, with a white ground on both faces — for people to fold,
study and fill with their own work.

**Heritage care.** No image of any historical codex is reproduced, traced or imitated: the leaves
are blank. The proportions preset follows the dimensions published for one surviving codex and
nothing else from it.

## Geometry

One strip, `leaves` × `leaf_width` long and `height` high, computed by `main.py`. The folds between
leaves (edge name `leaf-fold`) alternate valley and mountain, so the strip closes into a stack of
leaves, each carrying a page on each side (2 × `leaves` pages). The two ends of the strip are named
`end-first` and `end-last`, where covers would be attached.

`surface = gesso` gives both faces of the sheet the white of the ground layer laid on before
painting; `bare` leaves the amate stock's own colour. The ground is a surface treatment and is not
part of the stock card's mechanics (the stock card's values for amate are estimates; see
`materials/amate` in Pliego).

Historical screenfolds were made by gluing strips of roughly equal height end to end; this
cartridge draws the strip in one piece. A strip longer than the cutting bed is cut as several
pieces joined on a fold with an overlap of glue, or printed with the PDF exporter's 1:1 tiling.

## The fold program

All folds are parallel, so they never meet: the kinematic program is exact and linear in the
angles, and `main.py` checks both key states with `pliego.kinematics.closure_residual`.

1. **Fold the strip closed** — every fold to ±179° (a degree short of flat keeps the leaves in
   order in the preview); the step note gives the page count and the strip's length.
2. **Stand it open as a screen** — neighbouring leaves `display_angle` apart (90° by default).

The strip stands upright on its lower edge. **Preview and engine:** the studio preview runs the
whole program. The engine adds the bark paper's stiffness and weight, which decide whether a long
screen stands on its own.

## Making one by hand

1. Export the strip (`svg`, `dxf`, `pdf` or `hpgl`); the folds are on the mountain and valley
   layers.
2. Join amate sheets end to end, overlapping each joint by a few millimetres on a fold line, with
   a thin wheat-starch or PVA glue; let it dry flat under weight.
3. If you want a painting ground, brush a thin white ground (a gesso or a chalk-and-glue ground)
   on both faces and let it dry.
4. Fold along the lines alternately, valley and mountain, pressing each fold with a bone folder.

## Parameters

| id | meaning | default | range |
|---|---|---|---|
| `leaves` | leaves of the folded book | 10 | 4–48 |
| `leaf_width` | width of one leaf | 100 mm | 40–200 mm |
| `height` | height of the strip | 200 mm | 60–400 mm |
| `surface` | `gesso` (white ground) or `bare` | `gesso` | |
| `display_angle` | angle between leaves at the end of the program | 90° | 20–170° |

Presets: `classroom` (8 leaves, 100 × 150 mm); `dresden-proportions` (39 leaves of 92 × 200 mm,
3.59 m unfolded — the proportions only).

## History and sources

Mesoamerican codices are screenfolds: a strip folded into a folding book; Aztec, Maya and Mixtec
codices are among the best known, and only about twenty pre-Columbian codices survive (Wikipedia,
«Mesoamerican codices», https://en.wikipedia.org/wiki/Mesoamerican_codices). Amate is a bark paper
made in Mexico since before contact, used for Maya and Aztec codices, which were made into books by
folding them in an accordion pattern; its fibres are soaked and beaten into thin sheets, the Otomí
people still make it, and San Pablito, Puebla, makes it commercially (Wikipedia, «Amate»,
https://en.wikipedia.org/wiki/Amate). Screenfolds were made by gluing strips of leather or paper of
about the same height into a longer strip, folded back and forth into pages, whose two sides were
covered with white gesso before painting (Smarthistory, «Codex Borgia», LibreTexts edition,
https://human.libretexts.org/Bookshelves/Art/Art_History_and_Theory/SmartHistory_of_Art_2e/SmartHistory_of_Art_XIa_-_The_Americas_before_1500/03%3A_Mesoamerica/3.14%3A_Aztec_(Mexica)_art/3.14.12%3A_Codex_Borgia).
The Dresden Codex, a Maya screenfold of amate, has pages about 20 cm high and 10 cm wide and is
about 3.7 m long unfolded (Wikipedia, «Dresden Codex», https://en.wikipedia.org/wiki/Dresden_Codex);
the preset uses those proportions and nothing else.

The cartridge credits the Mesoamerican codex traditions for the book form, and the Otomí
papermakers of San Pablito, Pahuatlán, Puebla, for the living amate tradition its stock card is
named after. It makes no claim about any one codex beyond the cited dimensions.

## Provenance and licence

The book form is credited to the Mesoamerican codex traditions (lineage entry `traditional`); the
geometry and program are original MADFAM work. Published under CERN-OHL-W-2.0 like every object in
the commons (see the commons root `LICENSE`).
