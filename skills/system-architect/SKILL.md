---
name: system-architect
description: Design and enforce independently owned product modules, protected shared surfaces, stable upstream/downstream interfaces, and incremental integration. Use when a request spans multiple PRDs or modules, asks where and how much a feature should appear, adds or connects a frontend module, changes shared navigation, APIs or design tokens, asks to merge prior work, risks replacing existing UI, or needs architecture-wide placement before implementation.
---

# System Architect

Keep each product capability independently changeable while preserving the accepted system around it. Treat integration as a narrow contract change, not permission to redesign the product.

## Separate the roles

- Let the product owner or product manager decide the user problem, priority, release scope and acceptance outcome.
- Let the system architect decide placement, presentation budget, module ownership, stable interfaces and integration order.
- Let a module developer implement one registered module.
- Let an integrator connect accepted outputs through declared interfaces without rewriting module internals.

Do not turn the system architect into a global feature developer or final product owner.

## Preflight

1. Read repository guidance, accepted architecture, current Git state and active work boundaries.
2. Locate `.system-architect/module-boundaries.json`. If it is absent, copy `assets/module-boundaries.template.json`, then replace every example path and contract with verified repository facts before allowing writes.
3. Run the manifest check:

```bash
python3 <skill-dir>/scripts/check_module_scope.py --repo-root <repo> --check-manifest
```

4. Preserve dirty files, active writers, accepted routes and existing user-visible surfaces. Return `UNKNOWN` when ownership, interface shape or authority is unresolved.

## Place the change

Choose one path:

1. **Existing module:** keep the change inside its `owned_paths`.
2. **New independent module:** assign one user purpose, one primary surface, one owner, explicit interfaces and local tests before implementation.
3. **Shared contract change:** use only when the outcome truly changes the shell, shared API, design tokens or cross-module protocol. Treat it as protected architecture work.

Prefer vertical product slices over technical buckets. If feature logic lives in a protected monolith, freeze that file for module developers and extract the smallest standalone slice or adapter. Do not add more feature logic to the monolith.

## Freeze the change contract

Before code, state:

- module ID and role;
- user-visible placement and presentation budget;
- allowed files;
- inputs, outputs and interface versions;
- upstream and downstream modules;
- preserved surfaces and non-goals;
- module test and boundary test.

For new modules, interfaces or protected changes, read `references/change-contract.md` and complete the compact contract in the task.

## Enforce the write boundary

Check planned files before editing:

```bash
python3 <skill-dir>/scripts/check_module_scope.py \
  --repo-root <repo> --module <module-id> --role module-developer \
  --files <path> [<path> ...]
```

Check the actual working diff, including untracked files:

```bash
python3 <skill-dir>/scripts/check_module_scope.py \
  --repo-root <repo> --module <module-id> --role module-developer \
  --base HEAD
```

Use `--staged` for a pre-commit check. Protected modules require an allowed architect or integrator role plus `--architecture-change`. That flag records intent; it never substitutes for user authority.

## Define interfaces

For every cross-module connection, define:

- provider and consumer;
- payload, event, DOM slot or API contract;
- semantic version and compatibility rule;
- loading, empty, error and unavailable behavior;
- write authority and side effects;
- one boundary test that fails when the contract breaks.

Share contracts, not internal state. A consumer must not reach into another module's private DOM, storage, files or implementation functions.

## Integrate safely

1. Keep existing routes, navigation, accepted content and module directories intact.
2. Connect through a registered shell slot, API, event or adapter.
3. Add the smallest shared-surface change only after the module works independently.
4. Run module, contract, scope and affected regression tests.
5. Record durable shared decisions as an ADR when future modules need the rationale.
6. Report the candidate and remaining coupling. Do not merge, push, publish or retire existing surfaces without authority.

Read `references/architecture-sources.md` when designing a new boundary policy or choosing enforcement tools for a specific stack.

## Stop conditions

Stop with `BLOCKED` or `UNKNOWN` when:

- a managed file has no single owner;
- the request needs sibling-module edits without an authorized interface change;
- a module developer needs a protected shell or server file;
- integration would delete, replace or silently hide an existing surface;
- a contract omits version, error behavior or write authority;
- the product decision or architecture decision remains unresolved.

