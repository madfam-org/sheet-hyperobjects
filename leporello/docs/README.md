# Leporello

| | |
|---|---|
| **en** | An accordion book: one strip folded back and forth into equal panels, valley and mountain in turn, that closes into a stack and opens into a continuous surface. |
| **es** | Un libro acordeón: una sola tira doblada en zigzag en paneles iguales, valle y monte por turnos, que se cierra en una pila y se abre en una superficie continua. |
| **fr** | Un livre accordéon : une seule bande pliée en zigzag en panneaux égaux, vallée et montagne tour à tour, qui se ferme en pile et s'ouvre en une surface continue. |
| **pt** | Um livro sanfona: uma única tira dobrada em zigue-zague em painéis iguais, vale e montanha alternados, que se fecha numa pilha e se abre numa superfície contínua. |

## The structure

A leporello (accordion book, *libro acordeón*) is a strip of `panels × panel_width` by
`panel_height` with a scored fold between each pair of panels. The folds alternate — valley,
mountain, valley, … — so that closing the book makes each panel turn back on the one before it.

**Why it closes flat.** All the folds are parallel, so the strip only moves in its cross-section,
like a hinged chain of rigid panels. Each fold turns its panel by 180°, valley folds one way and
mountain folds the other, so every panel ends up exactly on top of the first: the closed book is a
stack with the footprint of one panel. No panel has to bend; the pattern is **rigid-foldable**,
which is why the fold program can run in kinematic mode and the folded state is exact.

**Why the folds alternate.** If two neighbouring folds turned the same way, the second panel
would wrap around the first instead of lying on it, and the strip would roll into a spiral rather
than stack. Alternation is what makes the accordion.

## Fabrication

- **Stock.** `cardstock-160` by default: it holds a crisp fold and stands up when the book is
  displayed half open. `cardstock-250` for a sturdier panorama, `kraft-120` or
  `elephant-hide-110` for a lighter book.
- **Grain.** The grain runs up the panels (`grain_deg` = 90°), parallel to the folds. Paper folds
  cleanly along its grain and cracks across it, so cut the strip with the grain running the short
  way.
- **Cut** the strip — the exports carry the outline on the cut layer. A strip longer than a sheet
  can be made of several pieces joined with a narrow glue tab on a panel edge.
- **Score** every fold line, then fold them in turn — valley, mountain, valley — and press the
  closed stack under a weight.

## What the engine simulates

The sheet document holds one physical sheet with `panels − 1` scored creases: valley folds at
+180°, mountain folds at −180°. Its fold program has a single step, *Close the book*, that drives
every crease to its target in **kinematic** mode (rigid panels, exact folded state). The program's
clock is exposed as the **Close** control: 0 is the strip lying open and flat, 1 the book closed;
any value between is a partly folded accordion. There are no joins and no initial frame — the
strip starts flat.

**Verified for this cartridge.** Folding the creases to their targets through the kernel's
face-tree pose puts every panel on the first: for 2, 8, 13 and 24 panels the closed stack's
footprint is exactly one panel wide and its out-of-plane spread is at most 2.2e-13 mm. The script
also refuses any strip whose creases do not alternate or do not fold a full 180°.

## Parameters

| id | meaning | range |
|---|---|---|
| `panels` | number of panels (pages) | 2–24 |
| `panel_width` | width of one panel | 50–150 mm |
| `panel_height` | height of the strip | 60–250 mm |
| `stock` | paper | cardstock 160 / 250 g/m², kraft 120 g/m², Elephant Hide 110 g/m² |

## Interfaces

- `front_edge`, `back_edge` (page edges, neutral) — the two ends of the strip.
- `cover_zones` (female glue zones) — the two end panels, where covers are glued, or where a
  tunnel book glues its frames when the strip serves as a wall.

## Provenance

Original MADFAM geometry, computed by `pliego.book.leporello`; no published design was copied.
The accordion fold is a general book structure of the bookbinding tradition and is credited to
that tradition, not to a designer. (Mesoamerican screenfold codices are folded the same way; they
have their own cartridge with their own sources.)
