---
name: right-size-governance
description: Audit and right-size project governance for long-horizon, multi-session, multi-agent, multi-worktree, or multi-machine work. Use explicitly alongside system architecture when a project accumulates overlapping task boards, plans, gates, receipts, registries, handoffs, status files, or repeated verification; when choosing Direct, Coordinated, or Controlled execution; or when removing ceremonial governance without weakening authority, safety, privacy, rollback, or recovery. Do not invoke for ordinary bounded implementation.
---

# Right-Size Governance

Reduce coordination burden while preserving the controls that prevent a concrete failure. Produce one simpler operating model, not another governance layer.

## Keep the boundary

- Invoke this Skill for an architecture or workflow review, not on every task.
- Treat the current architecture, repository guidance, task system and runtime state as inputs. Do not replace their authority.
- Audit read-only first. Do not close tasks, rewrite state, delete history, merge records, publish, migrate or reclaim workspaces without explicit authority.
- Return `UNKNOWN` when the current authority, writer, lifecycle, handoff or duplicate relationship cannot be established.
- Pair with `$system-architect` when the same review also changes module ownership, protected surfaces or cross-module interfaces.

## 1. Establish the unit of analysis

Name one user outcome and identify:

- deliverables;
- writers and write sets;
- sessions and machines;
- authority or lifecycle decisions;
- migration, security, privacy, public or irreversible actions;
- required recovery after interruption.

Do not infer complexity from task length, file count, a project label or the word "long".

Use the deterministic assessment when these facts can be represented as JSON:

```bash
python3 <skill-dir>/scripts/governance_rightsizer.py assess-task \
  --input <task-facts.json>
```

Read `references/input-schema.md` for the input fields and examples.

## 2. Choose the smallest operating mode

### Direct

Use for one bounded result, one writer, one write set, one active session or a safely resumable local change. Keep only the goal, write scope, observable acceptance and minimal verification. Do not create a WBS, card, receipt or extra gate by default.

### Coordinated

Use when independent outputs, multiple writers, cross-session ownership or durable recovery create real coordination needs. Add one authoritative task identity, owners and write sets, dependencies, and handoff state. Split only independently usable outputs.

### Controlled

Use when the work crosses authority or lifecycle boundaries, machines, repositories or security/privacy boundaries; performs migration, public or irreversible actions; or has a real write conflict. Add the control that addresses that risk. Keep a single bounded deliverable as one task when it has no independent sub-outputs.

Controlled raises control strength, not decomposition depth.

## 3. Inventory controls by function

Group current artifacts and steps by the decision they serve:

1. current task truth;
2. ownership and write isolation;
3. authority and lifecycle;
4. handoff and recovery;
5. verification and acceptance;
6. release, security and privacy;
7. historical trace.

For each function, identify one canonical owner. Treat dashboards, summaries, generated views and receipts as projections unless they own a distinct decision. Do not count filenames as separate controls when they repeat the same state.

## 4. Require a complete justification chain

For every governance item, state:

```text
risk -> failure mode -> control -> minimum evidence
```

Also record its trigger, owner, recurring cost and authoritative source. A control without a concrete risk or failure mode is ceremony. A material control without known evidence or authority is `UNKNOWN`, not safe to remove.

Run the inventory audit when the controls are structured:

```bash
python3 <skill-dir>/scripts/governance_rightsizer.py audit-controls \
  --input <controls.json>
```

## 5. Decide each item's future

- `KEEP`: owns a distinct decision, authority or non-substitutable safety boundary.
- `EMBED`: remains necessary but belongs in the deliverable's definition of done, test, review or readback.
- `ON_DEMAND`: activates only for its named risk trigger.
- `MERGE`: duplicates an existing authoritative control; keep one owner and redirect consumers.
- `REMOVE`: has no complete risk-to-failure-to-control chain and changes no decision.
- `UNKNOWN`: authority, evidence or duplicate target is unresolved; investigate before changing it.

Do not create separate governance tasks for QA, rollback, security or evidence unless they need an independent owner, decision, write set or recovery boundary.

## 6. Design the lean target state

Produce a target architecture with:

- one current-state authority per decision;
- one durable task identity only when work must survive a context or ownership boundary;
- one isolated write set per writer;
- one handoff record per real handoff;
- verification attached to the output it proves;
- history separated from current state;
- exceptional controls activated by explicit triggers;
- generated views that never become competing authorities.

Prefer removing reads and writes over adding synchronization. If two records must always match, keep one as authority and derive the other.

## 7. Apply changes safely

1. Present the inventory and proposed decisions before mutation.
2. Redirect readers and writers to the surviving authority.
3. Verify current behavior and recovery paths.
4. Preserve required history and supersession links.
5. Remove or archive redundant artifacts only after authorization.
6. Re-run the smallest relevant task, handoff and recovery checks.

## Deliver the review

Lead with the business result:

1. recommended operating mode;
2. the governance burden to remove;
3. the controls that remain and the failures they prevent;
4. a table of `current item -> decision -> surviving authority -> action`;
5. the smallest architecture change;
6. unresolved `UNKNOWN` items and the evidence needed.

Read `references/evidence-basis.md` when changing a policy, explaining the rationale, or comparing external approaches. It supports the decision rules; it is not a second framework to install.

## Stop conditions

Stop with `UNKNOWN` or `BLOCKED` when:

- two systems both claim authority and no owner has resolved them;
- a writer, lease, lock or worktree is active but cannot be identified;
- a proposed removal would erase required history, rollback or recovery evidence;
- a public, privacy, security, migration or irreversible decision lacks human authority;
- the audit would expose private project facts in a public artifact.
