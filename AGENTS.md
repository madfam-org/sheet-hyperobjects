# sheet-hyperobjects — agent operating guide

> Last Updated: 2026-10-10

<!-- MADFAM-AGENTS-CANONICAL v1 -->

> **Boundary checkpoint (2026-10-10, platform ops):** public repository. Operational detail
> (cluster topology, secret paths, break-glass procedures, operator runbooks, people) lives in
> MADFAM's private ops repository and is only pointed to from here — the rules are the
> repo-boundary contract, summarised in [`docs/PUBLIC_REPO_BOUNDARY.md`](docs/PUBLIC_REPO_BOUNDARY.md).
> Never copy that detail in.

This is the canonical instruction file for Claude, Codex and any other LLM agent working in this
repository. `CLAUDE.md` is only a compatibility redirect.

## What this repository is

The commons of **sheet hyperobjects** (origami, kirigami, papercut, pop-up, book structures,
flexagons, dioramas), mounted by [Pliego](https://github.com/madfam-org/pliego) at `projects/` and
validated by the [`hyperobjects-spec`](https://github.com/madfam-org/hyperobjects-spec) keystone
(`pliego-spec`). It holds objects and their articles only — **no platform code**. Status:
incubating.

## The cartridge contract

```
<slug>/main.py          generator (the platform sandbox injects `pliego` and `math`)
<slug>/project.json     manifest (validated by `pliego-spec check cartridge <slug>`)
<slug>/docs/README.md   the article
```

1. **Slugs** are strict kebab case, `^[a-z0-9]+(-[a-z0-9]+)*$`, 2–80 characters, at the repository
   root. A slug is permanent once landed.
2. **The triple is required** and nothing else is required: every directory holding a `project.json`
   has `main.py` and `docs/README.md` (CI `triple` lane).
3. **No per-cartridge `LICENSE`, `LICENCE` or `COPYING`** at any depth. The root [LICENSE](LICENSE)
   covers every object.
4. **Licence: two agreeing fields.** `project.attribution.license` and
   `hyperobject.commons_license` are both present, equal, and `CERN-OHL-W-2.0` (owner ruling,
   2026-10-10). An exception exists only as an owner-ruled carve-out ([NOTICE.md](NOTICE.md)).
5. **`project.attribution.lineage[]` is required** from object number one: an empty list means
   original MADFAM work; otherwise one entry per source.
6. **Born quadrilingual.** Every i18n object (name, description, parameter and step labels, the
   article's title and summary) carries `en`, `es`, `fr` and `pt`. Translation is written and
   reviewed, never machine-only; the Spanish register is the quality bar.
7. **Heritage objects cite sources and credit communities.** Traditional models are attributed to
   their tradition; papercut traditions credit their communities (papel picado: San Salvador
   Huixcolotla, Puebla; amate: the Otomí of San Pablito, Pahuatlán, Puebla). No claim the cited
   sources do not support.
8. **Never copy a designer's crease pattern or diagram.** Modern designers' crease patterns are
   copyrighted works. Every object is generated from geometry its own `main.py` computes.
9. **No prices, no client names, no secrets** anywhere — not in manifests, articles or commit
   messages.
10. Units: mm, degrees, grams, seconds; y-up in sheet space.

## Wave protocol (parallel agents)

- **One agent per slug.** An agent owns exactly one `<slug>/` directory, creates only files inside it,
  and never edits another slug, a root file or an index.
- **The coordinator claims indexes.** Catalog indexes (for example `docs/catalog/*.json`) are written
  only by the coordinator, and only in the same change that lands a cartridge that passes. A slot is
  never claimed ahead of a passing object.
- **Self-verify before reporting:** `pliego-spec check cartridge <slug>` with zero FAIL, the
  cartridge's generator run once with its defaults and once with a non-default parameter, and the
  triple lane. Report the exact output lines.
- **Partial files from a killed agent are purged,** never finished by someone else silently.
- Agents never merge and never move the platform's pin.

## CI lanes (`.github/workflows/ci.yml`)

GitHub-hosted `ubuntu-24.04` only, actions pinned to full commit SHAs, `permissions: contents: read`.
Lanes: `triple` (the cartridge triple and no stray licence files), `manifests` (`pliego-spec check
cartridge` at `env.SPEC_PIN`), `render` (every cartridge through `pliego-kernel` at
`env.PLIEGO_PIN`), `quality-gates` (byte gate, file-size gate 600/800). A lane whose pin is not set
prints `skip: <PIN> not set` — a printed skip, never a silent pass. Every lane prints how many
cartridges it read.

## Rulings

Ruled (owner, 2026-10-10): this commons exists, named `sheet-hyperobjects` — a third commons beside
the solid and soft commons, split by kernel; object licence CERN-OHL-W-2.0. Pending: CLA vs DCO for
third-party contributions (`contribution-signoff.yml` stays inert). Agents prepare to a ruling and
stop; they never take one.
