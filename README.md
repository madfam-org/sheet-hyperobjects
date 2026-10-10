# sheet-hyperobjects

> Boundary: public repository. It carries sheet hyperobjects and their public documentation only;
> operational detail lives in MADFAM's private ops repository. See
> [`docs/PUBLIC_REPO_BOUNDARY.md`](docs/PUBLIC_REPO_BOUNDARY.md).

**Status: incubating** — the commons exists; its first cartridges are being built.

The commons of **sheet hyperobjects**: origami, kirigami, papercut traditions, pop-up and paper
engineering, book structures, flexagons and whole interactive paper dioramas. Each object is a
parametric cartridge whose generator writes a flat sheet — outline, cuts, creases, glue tabs — and a
fold program, verified by the [`hyperobjects-spec`](https://github.com/madfam-org/hyperobjects-spec)
keystone (`pliego-spec`) and animated with real paper physics by
[Pliego](https://github.com/madfam-org/pliego), the platform that mounts this repository at
`projects/`.

Objects are licensed **CERN-OHL-W-2.0** (owner ruling, 2026-10-10; [LICENSE](LICENSE),
[NOTICE.md](NOTICE.md)).

## What a cartridge is

```
<slug>/
├── main.py          generator: parameters in, a sheet document (FOLD 1.2 + pliego:) out
├── project.json     manifest: identity, parameters, interfaces, attribution, licence
└── docs/README.md   the article: what it is, how it folds, its history and sources
```

One directory per object at the repository root, strict kebab-case slugs
(`^[a-z0-9]+(-[a-z0-9]+)*$`), no platform code, no per-cartridge licence file. Labels and articles
are born quadrilingual (en/es/fr/pt). The full contract is in [AGENTS.md](AGENTS.md).

## The classes, from turning a page to a diorama

The launch catalog climbs ten rungs (Pliego's
[launch catalog](https://github.com/madfam-org/pliego/blob/main/docs/strategy/launch-catalog.md)):

| # | Class | Examples |
|---|---|---|
| 1 | **Techniques** — the atoms | page turn, valley and mountain folds, crease-and-unfold, reverse folds, squash, petal, rabbit ear, pleat and crimp, tab-and-slot, glue flap, score vs crease, perforated tear |
| 2 | **Bases** | preliminary, waterbomb, kite, fish, bird, frog |
| 3 | **Traditional models** (attributed to tradition, with sources) | crane, flapping bird, jumping frog, dart, fortune teller (*comecocos*), boat (*barquito*), cup, masu box |
| 4 | **Tessellations and engineering origami** | Miura-ori, Yoshimura, Kresling tower, waterbomb tessellation, twists, curved-crease hypar |
| 5 | **Kirigami** | rotating-square auxetic, lattice kirigami, kirigami spring, origamic architecture |
| 6 | **Papercut traditions** (cited sources, community credit) | papel picado (San Salvador Huixcolotla, Puebla), jianzhi, wycinanki, kirie, scherenschnitte, sanjhi |
| 7 | **Paper engineering** | V-fold, parallel fold, floating layer, step, tent, pull-tab slider, volvelle, pivot, lift-the-flap |
| 8 | **Book structures** | codex, saddle stitch, leporello, screenfold codex (amate), tunnel book, carousel, flip book, flag book |
| 9 | **Flexagons and toys** | trihexaflexagon, hexahexaflexagon, tetraflexagon, kaleidocycle, paper helicopter |
| 10 | **Dioramas** — compositions through interfaces | an ofrenda pop-up with papel picado banners, a tunnel-book forest, a carousel village |

**Interfaces are how objects compose:** `spine`/`gutter`, `glue_flap` ↔ `glue_zone`, `tab` ↔ `slot`,
`hinge`, `page_edge`, `pivot` (diameter-matched to a Yantra4D brad), `track`. A pop-up piece declaring
`gutter` mounts on any spread exposing it, checked before anything is cut.

## How Pliego mounts it

The platform holds this repository as **one git submodule at `projects/`, pinned by commit SHA**. The
pin moves only after this repository's lanes are green, by the coordinator, in one pull request in
the platform. The platform's commons pin guard fails any job that reads `projects/` when the
submodule is an empty directory (an uninitialised submodule would make every glob-based lane green).

```bash
git clone --recurse-submodules https://github.com/madfam-org/pliego   # platform + this commons
```

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md) and [GOVERNANCE.md](GOVERNANCE.md). Third-party objects wait
on one pending owner ruling (CLA vs DCO); until it is made, the gate in
`.github/workflows/contribution-signoff.yml` is inert and third-party merges are blocked by policy.
Security reports: [SECURITY.md](SECURITY.md).
