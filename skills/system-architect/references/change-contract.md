# Protected Architecture Change Contract

Use this only for a new module, a shared interface, or a protected shell/API change.

```yaml
module_id: "one registered module"
role: "system-architect | integrator"
requirement_ids: []
user_outcome: "one observable result"
business_context:
  objective: "business result this change serves"
  critical_flows: []
  domain_invariants: []
  constraints: []
quality_requirements:
  - attribute: "reliability | security | performance | cost | privacy | operability | changeability"
    target: "measurable target or UNKNOWN"
    consequence: "business or user impact if missed"
implementation_model:
  decision: "NO_AI | AI_ASSISTED | AI_CORE | NOT_APPLICABLE"
  deterministic_baseline: "best non-AI approach and what it can achieve"
  selected_reason: "decisive product and architecture advantage"
  rejected_alternatives: []
  ai_boundary: "structured AI responsibility, or none"
  provider_substitutability: "how the provider can change behind the interface"
  validation: "how the system validates AI output"
  unavailable_behavior: "timeout, uncertainty and no-AI behavior"
  comparison_evidence: "observable evidence that would confirm the choice"
placement:
  surface: "route, slot, panel or background adapter"
  presentation_budget: "what appears, where and how much"
allowed_paths: []
preserve:
  routes: []
  surfaces: []
  contracts: []
interfaces:
  provides: []
  consumes: []
  compatibility: "compatible extension | explicit version change"
states:
  loading: ""
  empty: ""
  error: ""
  unavailable: ""
side_effect_owner: "the only module or capability allowed to write"
non_goals: []
evidence:
  primary_observed: []
  human_accepted: []
  ai_proposals: []
  unknowns: []
human_feedback:
  tradeoffs: []
  risks: []
  decisions_required: []
visualization:
  model_path: "path to architecture-model.json, or NOT_REQUIRED"
  views: []
verification:
  module_test: "command"
  boundary_test: "command"
  regression_test: "command"
```

Rules:

- Select one primary module. Split only independently usable outputs with separate owners.
- Complete `implementation_model` when the capability proposes AI. Use `NOT_APPLICABLE` for ordinary non-AI changes.
- Keep authority, permissions, calculations, state transitions and acceptance deterministic unless the product requirement explicitly establishes a different authority model.
- Tie every quality target and significant component to a business flow, invariant or operational consequence.
- Map modules and interfaces to product requirement IDs supplied by the product owner; return missing or conflicting mappings instead of inventing product intent.
- Keep primary observations, human acceptance, AI proposals, and unknowns separate. An AI proposal cannot verify itself or another AI artifact.
- Preserve every existing route and surface unless the user explicitly retires it.
- Change an interface version when existing consumers would interpret the payload differently.
- Give writes to one authority. Other modules receive a result or event, not direct storage access.
- Keep exceptions narrow, visible and temporary; do not widen an ordinary module to absorb unrelated work.
