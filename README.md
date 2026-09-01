# System Architect Skill

Keep AI coding agents inside independently owned modules while preserving shared shells and stable interfaces.

让负责单个功能的 AI 对话只修改自己的模块；跨模块连接通过明确接口完成，共享外壳只有架构师或集成者能够修改。

## What it adds

- A `system-architect` role between product planning and module implementation.
- One registered owner for every managed source file.
- Protected shared shells, APIs and design-system surfaces.
- Versioned interface contracts between modules.
- A deterministic guard for planned files, working diffs and staged changes.
- A safe path for extracting features from a frontend monolith incrementally.

## Role split

| Role | Decision |
|---|---|
| Product owner / product manager | User problem, priority, scope, acceptance |
| System architect | Placement, presentation budget, ownership, interfaces |
| Module developer | One registered module |
| Integrator | Connect accepted modules through declared contracts |

## Install

Install the complete `skills/system-architect` directory with your Agent Skills-compatible installer, or copy that directory into your harness's skills directory. The repository also includes a Codex plugin manifest at `.codex-plugin/plugin.json`.

## Start in a repository

1. Copy `skills/system-architect/assets/module-boundaries.template.json` to `.system-architect/module-boundaries.json`.
2. Replace every example module, path and interface with facts from the target repository.
3. Validate full coverage:

```bash
python3 skills/system-architect/scripts/check_module_scope.py --check-manifest
```

4. Check a module's planned files:

```bash
python3 skills/system-architect/scripts/check_module_scope.py \
  --module catalog --role module-developer \
  --files src/catalog/view.ts tests/catalog_view_test.ts
```

5. Check the actual change before handoff:

```bash
python3 skills/system-architect/scripts/check_module_scope.py \
  --module catalog --role module-developer --base HEAD
```

The guard exits with code `2` when a file is unowned, has multiple owners, belongs to another module, or touches a protected module without explicit architecture intent.

## Why this is different

Most public architect skills produce blueprints, ADRs, technology choices or architecture reviews. Those are useful, but prose alone does not stop an agent from editing a sibling module. This package combines architecture placement with a machine-checkable file boundary.

It complements CODEOWNERS and stack-native dependency tools:

- CODEOWNERS routes human review.
- This guard restricts the files an agent task may change.
- Nx, dependency-cruiser, ArchUnit or similar tools restrict imports and dependencies.

See `skills/system-architect/references/architecture-sources.md` for related work and the principles adapted into this workflow.

## Development

```bash
python3 -m unittest discover -s tests -v
```

