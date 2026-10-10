# Ecosystem roles

> Last Updated: 2026-10-10
>
> Boundary checkpoint (2026-10-10): roles only. MADFAM's private ops repository owns topology,
> operator procedures and secret handling; see [docs/PUBLIC_REPO_BOUNDARY.md](docs/PUBLIC_REPO_BOUNDARY.md).

`sheet-hyperobjects` is a commons, not a product: no hosts, no deploy, no identity client.

| Repository | Role for this commons |
|---|---|
| [Pliego](https://github.com/madfam-org/pliego) | The platform: mounts this repository at `projects/` (pinned submodule), renders and simulates every cartridge, owns the stock cards and the sheet-document contract |
| [hyperobjects-spec](https://github.com/madfam-org/hyperobjects-spec) | The keystone: `pliego-spec` validates every manifest and cartridge; shared lexicon terms |
| [solid-hyperobjects](https://github.com/madfam-org/solid-hyperobjects) | Sibling commons (Yantra4D): solid hardware a sheet object references through `hardware_ref` (brads, eyelets, magnets, stands) |
| [soft-hyperobjects](https://github.com/madfam-org/soft-hyperobjects) | Sibling commons (Fashion Cabinet): textiles a sheet object references (book cloth, ribbon, binding thread) |

Objects never embed another commons' geometry; they reference it by slug and parameters.
