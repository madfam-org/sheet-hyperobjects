# Public repository boundary

> Last Updated: 2026-10-10

`sheet-hyperobjects` is a **public** commons (objects CERN-OHL-W-2.0). It holds sheet-hyperobject
cartridges and their articles. Platform code lives in [Pliego](https://github.com/madfam-org/pliego);
schemas and validators in [hyperobjects-spec](https://github.com/madfam-org/hyperobjects-spec).

Keep here: cartridges (`main.py`, `project.json`, `docs/README.md`), public articles with cited
sources, synthetic test fixtures, and this repository's CI.

Never put here:

- secret values, tokens or credentials of any kind;
- node hostnames, IP addresses, cluster names, tunnel ids or secret-store paths;
- raw links into MADFAM's private ops repository (name a document, never link it);
- prices, quotes or tiers; client identities; people's names beyond public maintainer handles and
  the cited authors of public sources;
- a modern designer's crease pattern or diagram, or any third-party file whose licence is not
  CERN-OHL-W-2.0 without an owner-ruled carve-out.

Licensing, governance and topology rulings remain with the owner. A test skip or an unavailable
dependency is not verification, and a pending CI run is not green.

Canonical policy: the MADFAM repository boundary contract, kept in MADFAM's private ops
repository. The [public ecosystem contract hub](https://github.com/madfam-org/solarpunk-foundry)
owns shared public ecosystem guidance.
