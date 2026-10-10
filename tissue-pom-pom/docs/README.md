# Tissue pom-pom

| | Title | Summary |
|---|---|---|
| en | Tissue pom-pom | A stack of tissue sheets pleated together like a fan, tied at the centre, its ends trimmed round or pointed, then pulled apart into a ball. The pleating plays exactly; the fluffing into a ball is physics. |
| es | Pompón de papel de china | Una pila de hojas de papel de china dobladas juntas en acordeón, amarradas al centro, con las puntas recortadas redondas o en pico, y luego abiertas hasta formar una bola. El plisado se reproduce de forma exacta; el esponjado de la bola es física. |
| fr | Pompon en papier de soie | Une pile de feuilles de papier de soie pliées ensemble en accordéon, nouées au centre, aux extrémités taillées en rond ou en pointe, puis écartées en boule. Le plissage se joue exactement ; le gonflage en boule relève de la physique. |
| pt | Pompom de papel de seda | Uma pilha de folhas de papel de seda dobradas juntas em sanfona, amarradas no centro, com as pontas aparadas redondas ou em bico, e depois abertas até formar uma bola. O plissado se reproduz de forma exata; o afofamento da bola é física. |

## What it is

The tissue pom-pom (*pompón de papel de china*): a few sheets of tissue laid on top of each other,
folded together in a fan, tied tightly at the middle, trimmed at both ends, and then opened layer by
layer until the paper fills a ball that can hang over a party. This cartridge models the stack and
its pleating exactly (mode `make`), offers round and pointed ends, and writes the spread layers as a
reference frame. Mode `hung` is the finished pom-pom for the physics engine: the spread layers held
by the tie, in the wind. The fluffing that turns the layers into a ball is left to the engine,
because it is not folding (see below).

## Geometry

**The stack.** `sheets` identical sheets of papel de china (6 by default, 360 × 250 mm), one sheet
each in the document, lie one caliper (0.04 mm, the stock card's estimate) apart. Each carries
pleat lines across its length, parallel to its short side, rounded so that a whole number of pleats
fits: 12 pleats of 30 mm by default. They alternate valley and mountain and are creased by hand
(treatment `crease`). One more line runs along the middle of the sheet, square to the pleats: the
tie line, where the thread gathers the stick. It is an `F` line with treatment `none` (plain paper,
not creased, not on the cut file).

**The ends.** The folded stick is trimmed through every layer at once, so every panel gets the same
end: a semicircular lobe (`round`) or a point (`pointed`), cut 1 mm in at the tip. The sheet outline
is cut to that shape from the start, which gives the same paper as trimming the folded stick and
keeps each sheet one connected piece for the studio preview. The trimmed outline passes
`pliego.papercut.analyze` at papel de china's minimum feature, 1.5 mm.

**Pleating is rigid.** The pleat lines are parallel and none of them cross, so the whole stack folds
as rigid panels: every intermediate state is exact.

**Fanning is not.** A pleated sheet whose panels stay flat can only take shapes that are cylinders
over a zigzag: every cross-section along the stick is the same. To fan out, the pleats would have to
spread wider at the ends than at the tie, which no flat panel allows; at a crossing of a pleat with
the tie line (four right angles) a straight-line fold is possible only when the pleat is fully
closed. Real fanning bends the tissue and crushes it under the thread. So the frame
`target:spread` is the closest exact state: every pleat closed flat (180°) and every sheet folded at
the tie so that both its halves lift by their own angle. Sheet k of N (bottom to top) lifts by
−90° + (k + ½)·180°/N, which places the 2N halves evenly round the tie, 180°/N apart (−75°, −45°,
−15°, 15°, 45° and 75° for six sheets): the layers pulled apart, half up and half down. In a real
pom-pom each half then fans sideways into a half-disc and the half-discs fill the sphere, like the
segments of an orange round the tie. The script checks that the spread state keeps every edge
length.

## The fold program

Mode `make` is a `kinematic` program on the pleats of every sheet at once:

1. pleat the whole stack like a fan (every pleat at 90°);
2. press the pleats closed into a narrow stick (178°).

The pleats stop at 178°, not 180°: the stack has thickness and creases spring back a little (and the
studio draws closed folds 0.5° open anyway). The program ends in the pleated stick, about
30 × 250 × 6 mm, also written as the frame `target:pleated`. The last step's note says to tie the
middle and pull the layers apart; that spread state is the frame `target:spread`.

**Mode `hung`** is the finished pom-pom for the physics engine. Its `initial` frame is the spread
state (the same as `target:spread`). The tie is one `pin` join per sheet along its tie line, which
holds that line where it is: the thread wound round the centre, from which the pom-pom hangs. A
`wind` control (default 1 m/s) moves it. It has no fold program: what happens next (the layers
sagging, swaying and fluffing) is physics.

**Preview and engine.** The studio preview plays the pleating exactly, and its end pose equals
`target:pleated`. It cannot show the tie or the fanning, which bend and crush the tissue: those need
the physics engine. `target:spread` is a reference for it, not a state the `make` program reaches.
In mode `hung` the preview shows the spread layers standing still, clear of the table (wind
needs the engine). It draws each flat-folded pleat 0.5° open, so the folded panels of each half fan
out: at the default size the 30 mm-wide halves are drawn about 50 mm wide.

## Making one by hand

1. Export a sheet outline (`svg`, `dxf`, `pdf` or `hpgl`) as a template for the ends, or cut the
   ends freehand after folding.
2. Stack the sheets neatly. Fold the stack like a fan, one pleat up and one pleat down, along its
   whole length, and press it into a narrow stick.
3. Tie the middle tightly with thread or thin wire, leaving a tail to hang it.
4. Trim both ends of the stick round or pointed, through every layer at once (or follow the
   template).
5. Open the two halves into a fan. Starting at the top, lift each sheet gently away from the next,
   half of them up and half down, and fluff them until the paper fills a ball.

Tissue tears easily: separate the layers slowly, near the tie.

## Parameters

| id | meaning | default | range |
|---|---|---|---|
| `sheets` | sheets in the stack | 6 | 3–10 |
| `sheet_length` | the side that gets pleated | 360 mm | 150–700 mm |
| `sheet_width` | the side that becomes the stick (about the ball's diameter) | 250 mm | 100–500 mm |
| `pleat` | pleat width, rounded to fit the sheet | 30 mm | 15–60 mm |
| `ends` | `round` or `pointed` | `round` | |
| `colours` | pink, orange, yellow, turquoise, purple, green-white-red, mixed | pink | |
| `wind` | starting wind for the hanging pom-pom (mode `hung`) | 1 m/s | 0–8 m/s |

Modes: `make` (pleat the stack) and `hung` (the finished pom-pom in the wind). Presets: `small`
(4 sheets, 240 × 160 mm, 20 mm pleats), `large` (8 sheets, 500 × 350 mm, 45 mm pleats),
`tricolour` (green, white and red, pointed ends). The stock is papel de china, the only tissue
stock card in the commons. The script refuses a sheet shorter than four trim depths.

## History and sources

Papel de china is a festive paper in Mexico. México Desconocido (Arturo Cuevas, «El papel china sí
proviene de China, conoce cómo llegó a México», https://www.mexicodesconocido.com.mx/papel-china.html)
says it reached what is now Mexico on the Manila Galleon, the trade route that linked Asia with the
port of Acapulco between the 16th and 19th centuries, and that artisans use it for giant flowers at
patron-saint fiestas, fair ornaments, the first papel picado designs, traditional piñatas and
festive arches, and for flowers and garlands at weddings and quinceañeras. That article does not
mention pom-poms, and we found no source that documents the tissue pom-pom as a specifically
Mexican form; this cartridge therefore credits it as one of the family of papel de china party
decorations, not as a documented tradition of its own.

The method — tissue sheets folded in a fan, tied in the middle, edges trimmed round, then the halves
lifted to either side — follows El Corte Inglés's craft page «Pompón de papel de seda casero»
(https://www.elcorteingles.es/contenidos/ninos/pompon-papel-seda-casero/), a method source from
Spain. No template is copied; the pleats, the ends and the spread state are computed by this
cartridge.

## Provenance and licence

Original MADFAM geometry. The lineage credits the method source and the papel de china
festive-decoration practice of Mexico with their sources. Published under CERN-OHL-W-2.0 like every
object in the commons (see the commons root `LICENSE`).
