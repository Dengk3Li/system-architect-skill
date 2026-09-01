# Architecture Sources and Adapted Principles

Use these sources to choose a boundary policy. The skill applies their principles without copying their implementations.

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

