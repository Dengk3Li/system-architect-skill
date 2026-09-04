# Architecture decision workflow

Use this workflow for medium or larger architecture work. A small, already-settled placement or interface correction can proceed directly.

## Explore the decision tree

Model the design as a dependency tree. The **decision frontier** contains every unresolved architecture choice whose prerequisites are already settled.

1. Read the approved product intent, domain language, source code, contracts, runtime evidence, and active work boundaries.
2. Classify every frontier node as a **fact investigation**, an **architect decision**, or a **user decision**. Resolve facts through inspection or research. The architect selects technical placement, interface, versioning, failure, and implementation options. Ask the human only for business, operational, risk, cost, priority, or ownership decisions.
3. Present only the user-decision frontier as a compact question round, with a recommended option and decisive trade-off. Record fact findings and architect decisions directly in the architecture proposal.
4. Recompute the frontier after every round. Reopen dependent decisions when a premise changes.
5. Stop when no material unresolved fact or decision prevents safely freezing the change contract. Local, inexpensive, reversible parameters can use a documented architect default and remain tunable.

Keep the remaining uncertainty explicit when it is local, inexpensive, or reversible; it does not need another interview round.

## Use executable evidence when words are insufficient

Build the smallest throwaway prototype when a state model, integration behavior, or user interface must be run or seen before the architecture choice can be made. Keep the prototype as cited evidence on an isolated branch or directory. It remains a candidate source, not production architecture.

Delegate external documentation research to a bounded background investigation using primary sources. Bring back a cited note; research informs the decision and does not replace it.

Every detour records: the blocked decision, one bounded question, success and failure criteria, source or time boundary, output location, and the conclusion returned to the frontier. Apply the normal repository and module-scope preflight inside the isolated prototype workspace. Prototype code never promotes directly into production; only its conclusion and preserved evidence return, or the behavior is rebuilt through the accepted change contract.

## Keep a shared language

Use the project's canonical domain terms in modules, interfaces, tests, and diagrams. Challenge overloaded words and reconcile contradictions between the glossary, code, and product intent. A glossary defines domain language; it does not become an implementation specification.

## Admit ADRs selectively

Record an ADR only when all three conditions hold:

1. **Hard to reverse:** changing the decision later has meaningful cost.
2. **Surprising without context:** a future maintainer would reasonably ask why this option was chosen.
3. **Real trade-off:** credible alternatives existed and the decision selected among them for concrete reasons.

Capture context, decision, alternatives, consequences, evidence, and the condition that would justify revisiting it. Skip routine, local, and easily reversible choices.

## Hand off to delivery

Translate the accepted architecture into vertical implementation packages. Each package should complete a narrow behavior through the public seam and declare only genuine blockers. At phase boundaries, pass context pointers to the requirements, architecture model, ADRs, research, prototype, and tickets instead of copying their contents.

For an authorized build or integration request, the delivery workflow may create a feature branch and owned worktree, commit scoped changes, push the branch, open a pull request, and merge it after required checks and review. Clean up only branches and worktrees created by this task after confirming the PR is `MERGED`, the merge commit is reachable from the target branch, the worktree has no uncommitted or untracked content, no active writer remains, and any prototype conclusion or cited evidence has been preserved. Otherwise retain the workspace and report the unmet condition.

After delivery, review both whether the implementation follows repository standards and whether it satisfies the originating requirements. Keep runtime, security, data, and product acceptance checks alongside those two axes when the system requires them.
