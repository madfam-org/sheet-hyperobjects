# Kite base

| | Title | Summary |
|---|---|---|
| en | Kite base | The simplest base: the two edges at one corner folded onto the diagonal. Two 22.5° creases that meet only on the boundary, so each folds on its own as a plain hinge. |
| es | Base de cometa | La base más sencilla: los dos bordes de una esquina doblados sobre la diagonal. Dos pliegues a 22,5° que solo se tocan en el borde, así que cada uno se dobla por su cuenta, como una bisagra. |
| fr | Base du cerf-volant | La base la plus simple : les deux bords d'un coin rabattus sur la diagonale. Deux plis à 22,5° qui ne se rencontrent que sur le bord, si bien que chacun se plie seul, comme une charnière. |
| pt | Base da pipa | A base mais simples: as duas arestas de um canto dobradas sobre a diagonal. Dois vincos a 22,5° que só se encontram na borda, por isso cada um dobra sozinho, como uma dobradiça. |

The kite base is the first fold of many traditional models. Crease a square along a diagonal,
open it, and fold the two edges at one corner onto the crease. The result is a kite: a long point
at one end, the opposite corner at the other. Folding a second pair of edges from the other end is
the first half of the fish base (see `fish-base`); narrowing the kite again gives the stem of the
traditional tulip (see `tulip`).

## Geometry

The sheet is a square of side `size`, with the corner P at (0, 0) and the diagonal running to the
opposite corner Q at (`size`, `size`).

| Crease | From | To | Assignment |
|---|---|---|---|
| diagonal (precrease) | P | Q | valley, unfolded at the end |
| lower kite crease | P | (`size`, `size`·(√2 − 1)) | valley |
| left kite crease | P | (`size`·(√2 − 1), `size`) | valley |

Each kite crease bisects the 45° angle between an edge and the diagonal, so it leaves P at 22.5°
to its edge. It meets the opposite edge at `size`·tan 22.5° = `size`·(√2 − 1), about 0.414·`size`,
from the corner on that edge. Folding along it lays the edge exactly on the diagonal.

The three creases meet only at P, which is on the boundary. The pattern has **no interior vertex**,
so Maekawa's and Kawasaki's conditions have nothing to constrain: `pliego.flatfold.check` reports
zero vertices, and the cartridge still runs it. Every crease is an independent hinge. The kernel
reports three rigid degrees of freedom, one per crease.

## The fold program

The program has 19 kinematic steps, written as four key poses:

1. Valley-fold the diagonal, coloured side up (4 steps), and unfold it (3 steps).
2. Fold the lower edge onto the diagonal (6 steps).
3. Fold the left edge onto the diagonal (6 steps).

`pliego.Sequence.kinematic_path` expands each key pose into exact rigid states. Each step turns one
flap about one straight crease, so every state is a rotation about a fixed axis, and every loop
closes to rounding error. The body of the kite below the diagonal stays on the table. The finished
kite is written as the `target:flat-folded` frame, with the diagonal open and both kite creases at
180°.

What the program does **not** model:

- **No crease memory.** The unfolded diagonal is exactly flat in kinematic mode. Real paper keeps a
  rest angle there, which is what guides the edges by hand (see `crease-and-unfold`).
- **No layer contact.** The two flaps meet edge to edge on the diagonal. Zero-thickness kinematics
  lets them touch exactly; real paper leaves a hairline gap.

## Making one

1. Lay the square coloured side up, one corner toward you.
2. Fold it in half along the diagonal that runs away from you, crease and unfold.
3. Fold the lower right edge onto the diagonal, starting at the near corner.
4. Fold the lower left edge onto the diagonal the same way. The two edges meet on the crease.

## Parameters

| Parameter | Meaning | Default |
|---|---|---|
| `size` | side of the square (mm) | 150 |
| `stock` | `kami`, `copy-80`, `washi-kozo-30` | `kami` |

Presets: `large-24cm` (a 240 mm square).

## History and sources

The kite base is a traditional base, the first step of the fish base and of many traditional
animals. It is described among the classic bases in Robert J. Lang, *Origami Design Secrets:
Mathematical Methods for an Ancient Art*, 2nd ed., CRC Press, 2011. The diagram notation the step
labels follow is the Yoshizawa–Randlett system (Wikipedia, «Yoshizawa–Randlett system»,
https://en.wikipedia.org/wiki/Yoshizawa%E2%80%93Randlett_system). No diagram is reproduced; the
geometry is computed by this cartridge.

## Provenance and licence

Traditional base (public domain); original geometry and program by Innovaciones MADFAM. Published
under CERN-OHL-W-2.0, like every object in the commons (see the commons root `LICENSE`).
