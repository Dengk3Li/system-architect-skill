# Architecture Sources and Adapted Principles

Use these sources to choose a boundary policy. The skill applies their principles without copying their implementations.

## Business-driven architecture and communication

- [Azure Well-Architected Framework](https://learn.microsoft.com/en-us/azure/well-architected/): evaluate reliability, security, cost, operational excellence, and performance as trade-offs in service of business value.
- [Azure architecture design principles](https://learn.microsoft.com/en-us/azure/architecture/guide/design-principles/): begin with business requirements, design for change and failure, and make quality targets measurable.
- [C4 model](https://c4model.com/diagrams): communicate a system through audience-appropriate levels of abstraction and use only the views that add value.
- [C4 tooling](https://c4model.com/tooling): keep architecture as structured data and render multiple views over one model.

Adaptation: trace architecture decisions to business flows and quality targets, separate the stable architecture model from its visual views, and return explicit feedback to the human decision-maker.

## Construction quality and complexity

- [Microsoft Press: Code Complete, 2nd Edition](https://www.microsoftpressstore.com/store/code-complete-9780735619678): treat quality as a concern throughout construction, use right-sized practices, refactor safely, and prevent defects with defensive techniques.
- [Microsoft Press sample chapter: Design in Construction](https://www.microsoftpressstore.com/articles/article.aspx?p=2222451): manage complexity, design iteratively, prefer simplicity, and use information hiding to resolve difficult boundaries.

Adaptation: apply these construction principles at architecture scale. Minimize accidental complexity, hide volatile choices behind narrow interfaces, keep modules cohesive and dependencies explicit, let implementation evidence refine internal design, and protect accepted behavior while refactoring.

## Evidence integrity

Generated summaries, inferred graphs, diagrams, and agent reports are navigation aids or proposals. They do not become architecture facts by repetition. Trace verified claims to source code, executable tests, runtime observations, schemas, contracts, primary external sources, or explicit human decisions. If the primary chain is missing, keep the claim proposed or `UNKNOWN`.

## Graph evidence and architecture views

Graphify provides a persistent source graph, incremental extraction, relationship queries, and broad interactive exploration. It is useful for discovering candidate structure in an unfamiliar codebase.

The architecture visualizer curates a smaller decision-specific model from accepted requirements and verified evidence. Store selected node IDs and sources, then rerender HTML or SVG without re-extracting the repository. Update graphify only when source evidence changes; update the architecture model when architectural meaning changes.

## Editable frontend architecture workspaces

- [React Flow](https://reactflow.dev/) and its [examples](https://reactflow.dev/examples) provide an MIT-licensed reference for stable node IDs, controlled node state, selection, dragging, resizing, and save/restore behavior.
- [Storybook](https://storybook.js.org/) and its [interaction testing guide](https://storybook.js.org/docs/9/writing-tests/interaction-testing) provide an MIT-licensed reference for expressing components and pages in defined states, exercising user behavior, and keeping implementation examples reviewable in isolation.
- [Excalidraw](https://github.com/excalidraw/excalidraw) provides an MIT-licensed reference for an embeddable element scene and human-directed whiteboard editing.
- [draw.io](https://github.com/jgraph/drawio) provides an Apache-2.0 reference for a mature diagram editor, editable diagram storage, and embedded editing workflows.
- [Structurizr](https://docs.structurizr.com/) demonstrates one architecture model rendered into multiple audience-specific views.

Adaptation: keep a small JSON model as authority, give every frontend element stable identity and geometry, and render an offline HTML review workspace with move, resize, annotation, reset, and JSON export. Store pages, components, interaction states, data contracts, and quality requirements alongside the canvas so the picture remains tied to implementation. Use Storybook or a stack-native equivalent later for executable component states and interaction tests.

The bundled renderer does not copy or bundle these projects. It implements the small required interaction set with browser-native SVG and JavaScript so the public Skill remains dependency-free. If a product already uses React Flow, Excalidraw, draw.io, or another approved editor, adapt `frontend-module-canvas-v1` to that host instead of rebuilding the editor.

## Product slices and ownership

- [Micro Frontends](https://martinfowler.com/articles/micro-frontends.html): divide a large frontend into cohesive, user-visible vertical slices that can evolve independently. Keep shared libraries narrow and assign a custodian to shared assets.
- [Linking Modular Architecture to Development Teams](https://martinfowler.com/articles/linking-modular-arch.html): align module boundaries with durable ownership and maintain a cross-system view without centralizing every change.
- [Design Token-Based UI Architecture](https://martinfowler.com/articles/design-token-based-ui-architecture.html): use explicit shared tokens for cross-module visual rules instead of scattered magic values.

Adaptation: register one owner per managed file, protect the shared shell, and let feature modules consume explicit shell and design-token contracts.

## Review ownership and mechanical enforcement

- [GitHub CODEOWNERS](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners): route reviews to responsible people or teams and combine with branch protection when approval must be required.
- [Nx module boundaries](https://nx.dev/docs/guides/enforce-module-boundaries): express allowed dependencies with project tags and enforce them continuously.
- [dependency-cruiser rules](https://github.com/sverweij/dependency-cruiser/blob/main/doc/rules-reference.md): encode forbidden dependencies and make violations return a failing status.
- [Building Evolutionary Architectures](https://www.thoughtworks.com/content/dam/thoughtworks/documents/books/bk_building_evolutionary_architectures_second_edition_free_chapter.pdf): preserve architectural characteristics with automated fitness functions rather than prose alone.

Adaptation: use CODEOWNERS for review routing, the bundled scope guard for file ownership, and stack-native dependency rules for imports. No single mechanism covers all three.

## Contracts and durable decisions

- [MADR](https://adr.github.io/madr/): keep important architecture decisions and trade-offs in lightweight decision records.
- [Project Blueprint Skill](https://github.com/DrewGGM/project-blueprint-skill): define boundaries, ownership, data and API contracts before implementation.
- [Architect Skill](https://github.com/alonbaron/claude-skills/tree/main/skills/architect): keep system invariants and architecture documents synchronized with planned work.
- [Architectural Principles Skill](https://github.com/maxgribov/arch-expert-skill): let modules depend on narrow abstractions and connect concrete implementations at a composition root.

Adaptation: keep routine changes lightweight. Use a compact change contract for every cross-module connection and an ADR only for durable shared decisions.

## Related system-architect skills

- [wonderslife/pdd-skills](https://github.com/wonderslife/pdd-skills/tree/main/system-architect) emphasizes project scaffolding, technology selection and coding standards.
- [MachineLearning-Nerd/skills](https://github.com/MachineLearning-Nerd/skills/tree/main/system-architect) provides a concise architecture review workflow covering ownership, interfaces, failures and migration.
- [vladikk/modularity](https://github.com/vladikk/modularity/tree/main/skills/design) focuses on coupling-aware module design and organizational distance.

These are complementary. This skill's distinct responsibility is to turn ownership and interface decisions into a fail-closed file-scope check for coding agents.
