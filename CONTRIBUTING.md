# Contributing

> Boundary checkpoint (2026-10-10): public guide. Operational detail stays out of this repository
> per the repo-boundary contract ([docs/PUBLIC_REPO_BOUNDARY.md](docs/PUBLIC_REPO_BOUNDARY.md)).

Thank you for helping paper move. The commons accepts **objects**; the platform code lives in
[Pliego](https://github.com/madfam-org/pliego).

1. **Open an issue first** naming the object, its class and its sources. For a traditional model or
   a papercut tradition, list the sources you will cite and the community you will credit.
2. **Build one cartridge** in one `<slug>/` directory: `main.py`, `project.json`, `docs/README.md`
   (the contract is in [AGENTS.md](AGENTS.md)). Strict kebab-case slug.
3. **Licence.** Declare `CERN-OHL-W-2.0` in both `project.attribution.license` and
   `hyperobject.commons_license` (owner ruling, 2026-10-10). Do not add a licence file to your
   cartridge. Contributions are accepted under CERN-OHL-W-2.0: inbound equals outbound.
4. **Lineage.** Fill `project.attribution.lineage[]` with at least one entry: one per source, or one entry with `"license": "original"` that states the work is original.
5. **Four languages.** Every label and the article's title and summary in en, es, fr and pt,
   written or reviewed by a person.
6. **Never copy a designer's crease pattern or diagram.** Generate the geometry yourself.
7. **Run the checks:** `pliego-spec check cartridge <slug>` and the cartridge's generator, then open
   the pull request with the output lines.

**Sign-off (pending).** How third-party contributions are signed off — a Contributor Licence
Agreement or the Developer Certificate of Origin — is an owner ruling not yet made. Until it is,
pull requests from outside MADFAM are welcome for review but cannot be merged.
