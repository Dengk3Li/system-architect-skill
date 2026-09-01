# Governance Rightsizer Input

The script accepts UTF-8 JSON and prints JSON. It never edits the target project.

## Assess a task

Required positive integers:

- `deliverables`
- `writers`
- `write_sets`

Optional booleans default to `false`:

- `cross_session`
- `cross_machine`
- `public_release`
- `irreversible`
- `authority_or_lifecycle`
- `migration`
- `security_or_privacy`
- `cross_repo_contract`
- `write_conflict`
- `durable_recovery_required`

Example:

```json
{
  "deliverables": 1,
  "writers": 1,
  "write_sets": 1,
  "public_release": true
}
```

The output contains `mode`, `decomposition`, `reasons`, `required_controls` and controls to `avoid`.

## Audit controls

Pass a `controls` array. Every item requires:

- `id`
- `risk`
- `failure_mode`
- `control`
- `minimum_evidence`

Optional fields:

- `trigger_scope`: `always` or a specific condition such as `cross_machine`, `public_release`, `migration`, `security_privacy` or `authority_lifecycle`
- `separate_owner`: true when the control needs an independent owner
- `separate_decision`: true when it owns an independent human or system decision
- `authority_dependency`: true when classification depends on a verified authority
- `authority_known`: true only after that authority is verified
- `duplicate_of`: ID of the authoritative control this item repeats

Example:

```json
{
  "controls": [
    {
      "id": "artifact-readback",
      "risk": "The artifact is malformed.",
      "failure_mode": "The user cannot open the delivery.",
      "control": "Open and read back the final artifact.",
      "minimum_evidence": "Successful readback.",
      "trigger_scope": "always"
    }
  ]
}
```

The output decision is one of `KEEP`, `EMBED`, `ON_DEMAND`, `MERGE`, `REMOVE` or `UNKNOWN`. A valid always-on control defaults to `EMBED`; use `separate_owner` or `separate_decision` only when it truly owns an independent boundary.
