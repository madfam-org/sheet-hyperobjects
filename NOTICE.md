# Notice — licence, provenance and carve-outs

> Last Updated: 2026-10-10
> Boundary: public. This file reports rulings made elsewhere; it does not make any.

sheet-hyperobjects
Copyright (C) 2026 Innovaciones MADFAM S.A.S. de C.V., Cuernavaca, Morelos, México.

## Licence

Every object in this repository is licensed under the **CERN Open Hardware Licence Version 2 —
Weakly Reciprocal (CERN-OHL-W-2.0)**. That is an owner ruling made on 2026-10-10 for sheet commons
objects (this repository's cartridges and Pliego's stock cards); the dated decision record is kept in
MADFAM's private ops repository. The full licence text is in [LICENSE](./LICENSE): the canonical
CERN text, whose preamble names "this licence, CERN-OHL-W (weakly reciprocal)".

**No agent, and no maintainer, chooses a licence.** Licences are owner rulings
([GOVERNANCE.md](./GOVERNANCE.md)).

### How an object declares it

Every manifest carries the SPDX identifier in **two** machine-read fields that must both be present
and agree:

```json
{
  "project":     { "attribution": { "license": "CERN-OHL-W-2.0", "lineage": [] } },
  "hyperobject": { "commons_license": "CERN-OHL-W-2.0" }
}
```

Objects do **not** ship a per-directory `LICENSE` or `COPYING` file; the root LICENSE plus the
declared `commons_license` cover each one.

## Provenance

Every object is authored by MADFAM from geometry its own generator computes. Traditional models and
techniques are credited to their tradition with cited sources, with no copied diagram or
crease-pattern file; modern designers' crease patterns are never used. Heritage objects credit their
communities in `attribution.lineage[]` and in their article.

## Carve-outs

**There are none, and an empty registry is the correct state.** A genuinely third-party-licensed
object would need an explicit, owner-ruled carve-out recorded in the platform's
[`docs/licenses/CARVE-OUTS.md`](https://github.com/madfam-org/pliego/blob/main/docs/licenses/CARVE-OUTS.md),
which the platform's compliance lane machine-reads — never a lone differing manifest.
