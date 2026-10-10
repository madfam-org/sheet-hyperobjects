# Paper spring (witch's ladder)

| | Title | Summary |
|---|---|---|
| en | Paper spring (witch's ladder) | Two strips glued crosswise and folded over each other in turn: a stack that stretches by itself when let go and closes when squashed. Square or triangular section. |
| es | Resorte de papel (escalera de bruja) | Dos tiras pegadas en cruz y dobladas una sobre otra por turnos: una pila que se estira sola al soltarla y se cierra al aplastarla. Sección cuadrada o triangular. |
| fr | Ressort en papier (escalier de sorcière) | Deux bandes collées en croix et repliées l'une sur l'autre à tour de rôle : une pile qui s'allonge toute seule quand on la lâche et se referme quand on l'écrase. Section carrée ou triangulaire. |
| pt | Mola de papel (escada de bruxa) | Duas tiras coladas em cruz e dobradas uma sobre a outra à vez: uma pilha que estica sozinha quando é solta e fecha quando é esmagada. Secção quadrada ou triangular. |

## What it is

Glue two strips of paper together at one end, crossing them, and fold them over each other in
turn: A over B, then B over A, and so on until both are used up. The result is a small stack
that behaves like a spring. Let go and it stretches by itself; squash it and it closes. The fold
goes by many names: witch's ladder or devil's staircase in English, *Hexentreppe* or *Harmonika*
in German, *muizentrapje* in Dutch.

| Mode | Strips | Stack |
|---|---|---|
| `square` | two strips of square panels, crossed at 90° | a square |
| `triangular` | two strips of equilateral triangles, the second turned by 120° | a triangle |

The square version is the traditional one. The triangular section is a variant generated here
from the same rule.

## Geometry

**The strips.** Each strip is written by the script.

- **Square.** A strip of `folds + 1` square panels of side `width`, with a crease at every panel
  boundary.
- **Triangular.** A strip of `folds + 1` equilateral triangles, alternately pointing up and down,
  with a crease along every shared edge. The creases therefore run at ±60° to the strip.

In both, the creases alternate valley and mountain. Every fold takes the strip's tail up and over
the top of the stack, and every other time the panel underneath is face-down; hence the
alternation. No crease ends inside a strip; the script checks that, so every folded state of a
strip is consistent.

**Stacking.** Folded flat, a strip of squares stacks every panel on the first, folding alternately
across the panel's left and right edges. A strip of triangles also stacks every triangle on the
first, but its fold line moves round the triangle's three edges, because reflecting a triangle
over one edge brings the next shared edge onto another edge of the first triangle.

**Crossing.** Strip B is strip A turned about the centre of A's first panel, by 90° (square) or
120° (triangular), and laid on top of it. Its first panel coincides with A's, and its tail leaves
across a different edge. In the square, A folds across left and right and B across top and
bottom. In the triangle, A's folds go right, bottom, left, … and B's go left, right, bottom, ….
The two first panels are joined by a `glue` join, inset 1.5 mm from their edges, which the
initial frame satisfies. Strip B carries its turn as a `placement`.

## The fold program

The program is `physical`:

1. **The making.** `2 × folds` steps, each folding one crease to 180°: A over B, then B over A,
   in turn.
2. **Let go.** Every crease is released.
3. **Pull the ends apart.** Every crease opens to `stretch` (120° by default).
4. **Squash it shut.** Every crease goes back to 180°.
5. **Let go again.** Every crease is released.

**Release does not unfold** (spec §5.6). A released crease springs back only by about the stock's
yield angle. Here every crease does that at once, which stretches the stack: that is the spring.
The stretch is written as a step of the program, which opens every crease the way pulling the
ends does. A pull control (pins on the two ends, driven by a `translate` mechanism) would hold the
ends from the very first frame and fight the making, so the cartridge does not use one.

**What the preview shows and what needs the physics engine.** The studio preview poses each strip
along its face tree. The making is shown exactly, fold by fold. After the last fold both stacks
sit on the glued square or triangle, one panel wide. Releasing and stretching open every crease
of both strips together, so the stack rises. The preview has no contact, though: the two strips'
zigzags pass through each other where real paper presses one strip against the other. The
interleaving, the friction that locks the strips together and the springiness itself come from the
physics engine (tier C).

## Making one by hand

1. Plot or print two strips (SVG, PDF, DXF or HPGL) and score the lines.
2. Glue the first panel of strip B onto the first panel of strip A, crossed: at 90° for squares,
   or turned by 120° for triangles.
3. Fold the strip underneath over the other, along the first line, and press.
4. Fold the other strip back over it, along its first line. Keep alternating until both strips are
   used up.
5. Glue the last two panels together so that the stack cannot unravel (this glue is not
   modelled), then let go and pull.

Copy paper and kraft make lively springs; 160 g/m² cardstock gives a stiffer one.

## Parameters

| Parameter | Meaning |
|---|---|
| `folds` | folds per strip (4–24); each strip has `folds + 1` panels |
| `width` | side of each square or triangle, mm |
| `stretch` | fold angle of every crease when the spring is pulled out, degrees (180 = shut) |
| `stock` | copy paper, kraft, kami or 160 g/m² cardstock |

Presets: `short-fat` (6 folds, 40 mm) and `long-thin` (24 folds, 15 mm, stretched to 100°).

## History and sources

The witch's ladder is a traditional paperfold. Its first clear appearance in the historical
record is an illustration in *De Kleine Papierwerkers*, vol. 2 (K. H. Schadd, Amsterdam, 1863).
From the 1870s it is common in craft books of the Froebel and Pestalozzi schools of children's
education, and it appears in a Shanghai paper-folding guide of 1917 as a "paper chain".

- D. Mitchell, The Public Paperfolding History Project, "History of the Witch's Ladder" —
  https://origamiheaven.com/historyofwitchsladder.htm

## Provenance and licence

The square paper spring is credited to its tradition. The triangular section is an original
variant. All geometry, strips, creases, crossing and glue, is generated by this cartridge's
`main.py`, and no published diagram is copied. Licence: CERN-OHL-W-2.0 (the commons' root
licence).
