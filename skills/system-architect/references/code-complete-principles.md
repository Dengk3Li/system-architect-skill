# Code Complete Principles for Architecture Work

Adapt these construction principles at module and interface scale. They guide judgment; they do not replace repository evidence or a workload-specific architecture decision.

## Manage complexity deliberately

Make the amount of system knowledge needed for one change small. Separate essential domain complexity from accidental complexity introduced by frameworks, indirection, duplicate state, generalized abstractions, or AI layers. Reject a new layer unless it hides a real variation, protects an invariant, or reduces the reasoning burden of future changes.

## Hide decisions that are likely to change

Put volatile representation, provider, persistence, protocol, or model choice behind a narrow owned interface. Expose the stable business meaning rather than storage shape or implementation mechanics. Record what each boundary hides and which consumer behavior remains stable.

## Prefer strong cohesion and loose coupling

Give a module one coherent responsibility tied to a business capability. Minimize the number, width, directionality, and instability of dependencies. A shared utility is not automatically a good boundary; move behavior to the owner of the data or invariant it protects.

## Keep intellectual distance short

Use names, contracts, states, and data shapes that match the business language. Avoid translations that force maintainers to hold several unrelated representations in mind. Make invalid states difficult to express and side-effect authority explicit.

## Design enough, then learn from construction

Compare alternatives before commitment, but do not attempt to specify every implementation detail. Freeze the decisions that protect ownership, invariants, quality targets, interfaces, migration, and acceptance. Let construction evidence refine internal design without silently changing product meaning or shared contracts.

## Build quality through the whole path

Use executable boundaries, assertions or validation, defensive error behavior, module tests, contract tests, and runtime observation where their failure consequence warrants them. Prefer prevention and early detection at the source over downstream repair or narrative assurances.

## Evolve safely

Refactor when the current structure obscures responsibility or increases change cost. Preserve behavior with tests and primary evidence, make the smallest coherent change, and remove superseded paths after the new path is proven.

Sources:

- [Microsoft Press: Code Complete, 2nd Edition](https://www.microsoftpressstore.com/store/code-complete-9780735619678)
- [Microsoft Press sample chapter: Design in Construction](https://www.microsoftpressstore.com/articles/article.aspx?p=2222451)
- [Microsoft Press chapter key points](https://www.microsoftpressstore.com/articles/article.aspx?p=2222451&seqNum=7)
