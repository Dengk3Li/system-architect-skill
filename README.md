# System Architect Skill Suite

English | [简体中文](README.zh-CN.md)

[![CI](https://github.com/Dengk3Li/system-architect-skill/actions/workflows/ci.yml/badge.svg)](https://github.com/Dengk3Li/system-architect-skill/actions/workflows/ci.yml)

An Agent Skill suite for translating approved requirements and primary evidence into low-complexity architecture decisions, quality targets, owned modules, interfaces, repeatable diagrams, and human feedback.

## Quick start

Install with the open skills CLI:

```bash
npx skills add Dengk3Li/system-architect-skill --skill system-architect
npx skills add Dengk3Li/system-architect-skill --skill architecture-visualizer
```

Ask your agent to establish module boundaries:

```text
Use $system-architect to place this change in one owned module and define the
interfaces needed for integration.
Use $architecture-visualizer to render this architecture as interactive HTML
and presentation-ready SVG.
```

Copy the starter manifest into a repository:

```bash
mkdir -p .system-architect
cp skills/system-architect/assets/module-boundaries.template.json \
  .system-architect/module-boundaries.json
```

Replace every example entry with verified paths and interfaces, then check the manifest:

```bash
python3 skills/system-architect/scripts/check_module_scope.py --check-manifest
```

The manifest becomes the repository's explicit map of module ownership and protected shared surfaces.

## What it does

System Architect helps a team:

- translate accepted business outcomes, critical flows, and domain rules into architecture decisions;
- manage accidental complexity through information hiding, cohesive modules, narrow coupling, and iterative construction evidence;
- keep AI-generated summaries, graphs, and diagrams as proposals until primary evidence verifies them;
- define measurable quality targets and explain their business consequences;
- assign every managed file to exactly one module;
- reserve the application shell, global styles, shared APIs, and design tokens for authorized integration work;
- define provider, consumer, version, errors, side effects, and ownership for module interfaces;
- check planned files, the working tree, or the staged diff against a module boundary;
- extract new features from a frontend monolith without requiring a full rewrite;
- distinguish observed, accepted, and proposed architecture;
- create one architecture model and rerender audience-specific HTML and SVG views;
- return trade-offs, risks, assumptions, and decisions to human stakeholders;
- stop with `UNKNOWN` when ownership, authority, or an interface contract has not been verified.

The skill supplies both architecture instructions and a Python scope checker.

## The problem this suite solves

Coding agents can produce a plausible architecture from a prompt without checking the running system, source code, contracts, or accepted requirements. The next agent may treat that generated diagram or summary as evidence. After several rounds, the system is designed from earlier AI interpretations instead of the business logic and code that actually exist.

A second failure appears during implementation. A developer assigned to one feature can still edit the router, application shell, shared APIs, global styles, and sibling modules. Local work then increases coupling, duplicates state, or replaces accepted behavior outside the product scope.

This suite starts from approved requirement IDs and primary evidence. It applies complexity management, information hiding, cohesion, narrow coupling, and iterative construction principles adapted from *Code Complete*. AI-generated summaries, graphs, and diagrams remain proposals until source code, tests, runtime observations, contracts, or human decisions verify them.

The repository records module ownership and checks the actual Git change set. Shared integration stays possible through declared interfaces and authorized architecture changes. Product scope remains with the product manager; the architect owns placement, boundaries, quality targets, and integration consequences.

## Architecture model

### Business drivers and quality requirements

Architecture starts from accepted customer and business outcomes. Critical journeys, domain invariants, data authority, failure consequences, cost, reliability, security, performance, privacy, operability, and changeability become explicit design inputs. Only qualities that affect the workload are applied.

### Owned modules

Each managed file must match one module's `owned_paths`. Unowned files and overlapping ownership fail validation.

### Protected shared surfaces

Shells, global tokens, public API adapters, and other shared surfaces can be marked as protected. A module developer cannot modify them. An authorized architect or integrator must declare an architecture change explicitly.

### Versioned interfaces

Modules depend on published contracts rather than another module's private DOM, storage, files, or internal functions. A contract identifies its provider, consumers, version, behavior, and side-effect owner.

### Scope checks

The checker can validate a proposed file list before work begins and the real Git diff before delivery. Violations return exit code `2`, which can fail a local hook or CI job.

## Example

Suppose a team is adding a refund dashboard to an existing commerce application.

The product decision is already settled. System Architect assigns the page and tests to `refund-board`. The module consumes a published `orders.events.v2` contract. The main navigation belongs to the protected `app-shell` and is changed later by an integrator through `shell.slot.v1`.

The refund developer can change:

```text
src/features/refunds/**
tests/refunds/**
```

The same developer cannot change:

```text
src/shell/**
src/api/**
src/features/orders/internal/**
```

If the order-event payload, error behavior, or write authority is missing, the architecture decision remains `UNKNOWN`. The agent does not invent a temporary interface to keep coding.

## Typical workflow

1. Read accepted product outcomes, business constraints, repository guidance, and runtime evidence.
2. Map actors, critical flows, domain rules, quality targets, and data authority.
3. Compare architecture options and explain the decisive trade-offs.
4. Select an existing module, define a new module, or identify a protected shared-contract change.
5. Record placement, ownership, interfaces, evidence, feedback, and verification.
6. Render architecture views when they help a stakeholder decision.
7. Check planned and actual files before integration.
8. Revisit assumptions when runtime, cost, incident, or user evidence arrives.

The system architect owns placement and interfaces. It does not become the developer for every module.

## Scope checker

Check a planned file list:

```bash
python3 skills/system-architect/scripts/check_module_scope.py \
  --module catalog \
  --role module-developer \
  --files src/catalog/view.ts tests/catalog_view_test.ts
```

Check the working tree relative to a Git baseline, including untracked files:

```bash
python3 skills/system-architect/scripts/check_module_scope.py \
  --module catalog \
  --role module-developer \
  --base HEAD
```

Check only staged files:

```bash
python3 skills/system-architect/scripts/check_module_scope.py \
  --module catalog \
  --role module-developer \
  --staged
```

Check an authorized protected change:

```bash
python3 skills/system-architect/scripts/check_module_scope.py \
  --module app-shell \
  --role system-architect \
  --architecture-change \
  --files src/shell/navigation.ts
```

`--architecture-change` records the type of change. It does not grant authorization by itself.

## Adopting it in an existing frontend

You do not need to modularize the entire application first.

1. Register the current application shell and other shared files as protected.
2. Put new features in owned directories.
3. Connect them through narrow adapters or slots.
4. Move legacy logic out of shared files when real changes create a useful extraction point.

This keeps current behavior available while reducing the write surface of each new task.

## Role boundary

| Role | Owns |
|---|---|
| Product manager | User problem, priority, release scope, acceptance |
| System architect | Module placement, presentation budget, ownership, interfaces, integration order |
| Architecture visualizer | Stable architecture model, audience views, source evidence, and diagram feedback |
| Module developer | Implementation and tests inside one registered module |
| Integrator | Authorized changes to protected surfaces through declared contracts |

For proportional product scope and release decisions, use the companion [Product Manager Skill](https://github.com/Dengk3Li/product-manager-skill).

## When to use it

Use this skill when:

- several agents or conversations work in the same repository;
- frontend features share a router, navigation, global stylesheet, or large entry file;
- a new module must connect to existing data or UI surfaces;
- separate modules need stable upstream and downstream contracts;
- an existing monolith must be split gradually;
- a change risks replacing accepted UI outside its scope.

A small repository with one maintainer and no shared integration surface usually does not need this boundary layer.

## Package contents

```text
.codex-plugin/plugin.json
skills/system-architect/
  SKILL.md
  agents/openai.yaml
  assets/module-boundaries.template.json
  references/architecture-sources.md
  references/change-contract.md
  references/code-complete-principles.md
  scripts/check_module_scope.py
skills/architecture-visualizer/
  SKILL.md
  agents/openai.yaml
  assets/architecture-model.template.json
  references/architecture-model.md
  scripts/render_architecture.py
tests/test_architecture_visualizer.py
tests/test_check_module_scope.py
```

`SKILL.md` contains the agent instructions. The repository README is written for people evaluating or installing the skill.

## Design references

The skill adapts ideas from:

- [Micro Frontends](https://martinfowler.com/articles/micro-frontends.html)
- [GitHub CODEOWNERS](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners)
- [Nx module boundaries](https://nx.dev/docs/guides/enforce-module-boundaries)
- [dependency-cruiser rules](https://github.com/sverweij/dependency-cruiser/blob/main/doc/rules-reference.md)
- [Building Evolutionary Architectures](https://www.thoughtworks.com/content/dam/thoughtworks/documents/books/bk_building_evolutionary_architectures_second_edition_free_chapter.pdf)
- [MADR](https://adr.github.io/madr/)
- [C4 model](https://c4model.com/diagrams)
- [C4 tooling](https://c4model.com/tooling)
- [Azure Well-Architected Framework](https://learn.microsoft.com/en-us/azure/well-architected/)
- [Code Complete, 2nd Edition](https://www.microsoftpressstore.com/store/code-complete-9780735619678)
- [Code Complete: Design in Construction](https://www.microsoftpressstore.com/articles/article.aspx?p=2222451)

See [architecture-sources.md](skills/system-architect/references/architecture-sources.md) for adaptation notes and related public tools.

## Development

Run the tests:

```bash
python3 -m unittest discover -s tests -v
```

Validate the skill and plugin manifests with the corresponding creator tools:

```bash
python3 <skill-creator>/scripts/quick_validate.py skills/system-architect
python3 <plugin-creator>/scripts/validate_plugin.py .
```

The checker uses the Python standard library and has no third-party runtime dependency.

## License

This repository is publicly visible but does not currently grant an open-source license.
