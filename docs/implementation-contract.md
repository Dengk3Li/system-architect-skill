# v0.4.0 implementation contract

This is a technical design and review record.

Primary module: `workspace`, implemented under `skills/architecture-workspace/`. Supporting `delivery` changes cover synthetic examples, docs, tests, CI and package metadata. Architect changes add routing to the new capability. Existing renderer contracts and the refund example remain compatible.

| Requirement | Outcome | Implementation |
|---|---|---|
| WS-01 | Locate a file through directory and module responsibility | Explicit workspace map, shared snapshot file records, module relationship view |
| WS-02 | Trace an output to a run and historical input/configuration | Append-only run records referring to snapshot ID + relative path |
| WS-03 | Understand versions and missing evidence | Full content hashes, observation IDs, hash states, snapshot comparison |
| WS-04 | Understand space and business nature | Measured byte fields, separate physical/logical totals, explicit nature rules |
| WS-05 | Try and share without installing a platform | Generated offline HTML, synthetic published example, JSON/HTML export |

Implementation model: `NO_AI`. Deterministic baseline fully satisfies recording, identity, arithmetic, filtering, validation and navigation. `AI_ASSISTED` may later propose module responsibilities, nature rules and explanations from user-approved context; suggestions require source links and explicit adoption. `AI_CORE` has no justified role in these facts. No model or provider dependency is introduced. Without AI all first-release tasks remain available.

Interfaces: `system-architect.workspace-map/v1` for explicit modules, relations and nature rules; `system-architect.workspace/v1` for snapshots and runs; `system-architect.run/v1` for imported run records. Only the CLI writes the catalog, using a file lock and atomic replacement. The renderer reads a validated catalog; browser navigation and export cannot alter source files or the catalog. Data model and invariants are in `skills/architecture-workspace/references/model.md`.

UI: architecture + directory, runs + lineage, storage; common file inspector and snapshot selector. Keyboard navigation, meaningful buttons and labels, 390px mobile stacking, 1440px desktop split layout, visible empty states, local error recovery, reduced-motion support. The browser presents at most 200 matching file rows per page; search covers the selected snapshot.

Validation: boundary checker; unit tests for scanning, hardlinks, symlinks, file mutation, unknown hashes, cross-snapshot references, immutable records, invalid maps/catalogs, interrupted/concurrent writes and injection escaping; synthetic end-to-end reproduction; browser tasks at desktop and mobile sizes. Scans read only temporary synthetic directories during this release. Public outputs contain no real workspace paths or data.

Non-goals and preserved scope: PRODUCT.md. Publication is authorized for this repository, including PR, passing CI, merge and release. No unrelated PR, installed Skill, real experimental directory or companion product-manager repository belongs to the write scope.
