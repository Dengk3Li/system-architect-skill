# System Architect Skills

Keep AI coding agents inside independently owned modules and keep project governance proportional to real coordination risk.

让负责单个功能的 AI 对话只修改自己的模块；跨模块连接通过明确接口完成；长程、多对话和多机器工作只保留真正防止失败的控制。

## Included skills

| Skill | Responsibility | Invocation |
|---|---|---|
| `system-architect` | Module placement, ownership, protected surfaces and interface contracts | Architecture and integration work |
| `right-size-governance` | Direct/Coordinated/Controlled routing and duplicate-governance removal | Explicit, on-demand workflow review |

`right-size-governance` sets `allow_implicit_invocation: false`. It does not intervene in ordinary bounded implementation.

## What it adds

- A `system-architect` role between product planning and module implementation.
- One registered owner for every managed source file.
- Protected shared shells, APIs and design-system surfaces.
- Versioned interface contracts between modules.
- A deterministic guard for planned files, working diffs and staged changes.
- A safe path for extracting features from a frontend monolith incrementally.
- A risk-linked audit for task boards, plans, gates, receipts, registries and handoffs.
- Deterministic task-mode and governance-inventory classification.

## Role split

| Role | Decision |
|---|---|
| Product owner / product manager | User problem, priority, scope, acceptance |
| System architect | Placement, presentation budget, ownership, interfaces |
| Governance reviewer | Necessary controls, authority consolidation, activation triggers |
| Module developer | One registered module |
| Integrator | Connect accepted modules through declared contracts |

## Install

Install the repository as a Codex plugin to use both skills. You can also copy either complete directory under `skills/` into an Agent Skills-compatible harness.

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

## Right-size project governance

Use `$right-size-governance` during architecture or workflow reviews when long-running work has accumulated overlapping cards, plans, gates, receipts, status files or handoff records.

Assess one task:

```bash
python3 skills/right-size-governance/scripts/governance_rightsizer.py \
  assess-task --input task-facts.json
```

Audit a control inventory:

```bash
python3 skills/right-size-governance/scripts/governance_rightsizer.py \
  audit-controls --input controls.json
```

The audit returns `KEEP`, `EMBED`, `ON_DEMAND`, `MERGE`, `REMOVE` or `UNKNOWN`. It is read-only and never edits the target project. See `skills/right-size-governance/references/evidence-basis.md` for the public research behind the decision rules.

## Why this is different

Most public architect skills produce blueprints, ADRs, technology choices or architecture reviews. Those are useful, but prose alone does not stop an agent from editing a sibling module or a workflow from accumulating duplicate control layers. This package combines architecture placement with two machine-checkable boundaries: file scope and proportional governance.

It complements CODEOWNERS and stack-native dependency tools:

- CODEOWNERS routes human review.
- The module guard restricts the files an agent task may change.
- The governance rightsizer distinguishes durable controls from delivery attributes and repeated ceremony.
- Nx, dependency-cruiser, ArchUnit or similar tools restrict imports and dependencies.

See `skills/system-architect/references/architecture-sources.md` and `skills/right-size-governance/references/evidence-basis.md` for related work and adapted principles.

## Development

```bash
python3 -m unittest discover -s tests -v
```
