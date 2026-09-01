# Evidence Basis

Use these sources to explain or revise the Skill's decision rules. Adopt the principle that fits the current risk; do not install every referenced workflow.

## Multi-agent coordination has a measurable tax

- [Anthropic: How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) reports strong results for breadth-first, independently searchable work, but roughly 15 times chat token use and poor fit for tasks with shared context or many dependencies.
- [Capable language models can outgrow the benefits of collaboration](https://www.nature.com/articles/s42256-026-01268-y) finds that coordination can help or harm depending on baseline capability and task structure; information fragmentation, synchronization and error amplification are material costs.
- [Why Do Multi-Agent LLM Systems Fail?](https://arxiv.org/html/2503.13657v2) derives 14 failure modes from more than 200 traces, grouped under specification, inter-agent alignment and task verification.

Adaptation: start with a strong single-agent or single-session baseline. Add agents only for independent exploration, context isolation, distinct ownership or durable recovery that outweighs coordination cost.

## Governance should be proportional to risk

- [NIST AI RMF Core](https://airc.nist.gov/airmf-resources/airmf/5-sec-core/) says its actions are not a checklist and calls for the level of risk-management activity and inventory resourcing to follow organizational risk priorities and tolerance.
- [Google SRE: Eliminating Toil](https://sre.google/workbook/eliminating-toil/) identifies repetitive, manual, automatable work with little enduring value as toil and recommends comparing the cost of reduction with the benefit.

Adaptation: require `risk -> failure mode -> control -> minimum evidence`. Treat repeated status copying, receipts and reviews as toil when they do not change a decision, prevent a failure or preserve required recovery evidence.

## Small independent batches improve feedback

- [DORA: Working in small batches](https://dora.dev/capabilities/working-in-small-batches/) recommends independent, valuable, small and testable units to shorten feedback and make AI-generated changes easier to review and integrate.

Adaptation: split work by independently usable output, writer, write set or recovery boundary. Do not split one risky result into multiple governance-only tasks.

## One authority can feed many projections

- [Flux core concepts](https://fluxcd.io/flux/concepts/) describes declarative desired state, reconciliation and shared source artifacts that deduplicate configuration and storage.
- [Git worktree documentation](https://git-scm.com/docs/git-worktree.html) separates per-worktree state such as `HEAD` and index while sharing repository data, and provides explicit locking for worktrees on intermittently available storage.

Adaptation: keep one current-state authority for each decision, derive views from it, and isolate writers through write sets or worktrees. Treat locks and handoff records as real controls only when the corresponding writer or availability risk exists.

## Persistent workflow systems solve specific persistence problems

- [OpenSpec core concepts](https://openspec.dev/docs/core-concepts) uses progressive rigor: lite specifications by default and fuller treatment for cross-team, cross-repository, migration, security or privacy risk.
- [GitHub Spec Kit](https://github.com/github/spec-kit) provides an explicit specification, plan, task and convergence workflow for software changes, with optional extensions for narrower workflows.
- [Beads](https://github.com/gastownhall/beads) provides a persistent dependency graph, atomic claims and multi-machine synchronization for long-horizon coding agents.

Adaptation: use durable specs and task graphs when work must survive context, ownership or machine boundaries. Do not duplicate them with parallel plans, cards and status files for ordinary bounded work.
