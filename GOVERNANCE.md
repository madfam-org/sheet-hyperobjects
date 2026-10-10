# Governance

> Last Updated: 2026-10-10
> Boundary: public. How the sheet commons decides what enters it, who checks it and who lands it.

`sheet-hyperobjects` is a MADFAM project. It is not a foundation and has no board. It has a few roles
with separated powers, and one rule: no role substitutes assertion for evidence.

| Role | Held by | Decides |
|---|---|---|
| **Owner / maintainer of record** | Innovaciones MADFAM S.A.S. de C.V. | Licences, carve-outs, topology, the sign-off mechanism, governance itself, and anything not delegated below |
| **Coordinator** | A maintainer, per wave | Slot claims in indexes, wave integration, merges, and Pliego's pin to this repository |
| **Reviewer** | A maintainer or a delegated contributor | Whether a pull request meets the bar; never merges their own work |
| **Lanes (CI)** | `.github/workflows/ci.yml` here, plus Pliego's lanes against the pin | Whether an object is verified; blocking, not advisory |
| **Contributor** | Anyone | What to propose, and what to build once a route is agreed |

## Owner rulings

- **No agent and no maintainer chooses a licence.** The object licence is CERN-OHL-W-2.0 (owner
  ruling, 2026-10-10; [NOTICE.md](NOTICE.md)). Any deviation is an owner-ruled carve-out.
- **Topology** — that sheet objects live in their own commons beside the solid and soft commons —
  was ruled by the owner on 2026-10-10; any change to it is an owner matter.
- **Rulings are dated records.** A decision that lives only in someone's memory of a conversation
  has not been made.

## The coordinator

- Claims an index slot **only after** the cartridge has passed the lanes, in the same change that
  lands it. A slot claimed ahead of a verified object is a false public statement.
- Advances Pliego's pin to this repository only after these lanes are green, in one platform pull
  request.
- Does not review their own object into the commons.

## Verification

The lanes verify the object (manifest schema, the cartridge triple, licence fields, rendering);
the reviewer verifies what a machine cannot: whether a lineage is true, whether a cited source says
what the pull request claims, whether a heritage article credits its community fairly.

## Rulings this commons is waiting on

1. **CLA vs DCO** for third-party contributions. Until ruled, `contribution-signoff.yml` is inert
   (gated on the unset repository variable `SHEET_CONTRIBUTION_SIGNOFF`) and third-party merges are
   blocked by policy.
