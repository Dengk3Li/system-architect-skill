# Protected Architecture Change Contract

Use this only for a new module, a shared interface, or a protected shell/API change.

```yaml
module_id: "one registered module"
role: "system-architect | integrator"
user_outcome: "one observable result"
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
verification:
  module_test: "command"
  boundary_test: "command"
  regression_test: "command"
```

Rules:

- Select one primary module. Split only independently usable outputs with separate owners.
- Preserve every existing route and surface unless the user explicitly retires it.
- Change an interface version when existing consumers would interpret the payload differently.
- Give writes to one authority. Other modules receive a result or event, not direct storage access.
- Keep exceptions narrow, visible and temporary; do not widen an ordinary module to absorb unrelated work.

