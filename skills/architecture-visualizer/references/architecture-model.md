# Architecture Model and View Rules

Use this reference before creating architecture-model.json.

## Model contract

Required top-level fields:

    title: string
    scope: string
    language: en | zh-CN
    audience: [string]
    views: [view]
    nodes: [node]
    relationships: [relationship]
    feedback: [feedback item]

A node contains:

    id: stable machine-readable identifier
    name: human-readable name
    type: person | external-system | system | container | component | data-store
    responsibility: one short responsibility
    business_driver: requirement or quality attribute served
    source: file, contract, decision record, runtime evidence, or accepted brief
    source_type: HUMAN_APPROVED_REQUIREMENT | SOURCE_CODE | TEST_RESULT | RUNTIME_OBSERVATION | CONTRACT | EXTERNAL_PRIMARY_SOURCE | AI_PROPOSAL
    evidence_status: PROPOSED | OBSERVED | VERIFIED | ACCEPTED

A relationship contains:

    id: stable identifier
    source: node id
    target: node id
    label: directional action, data flow, or dependency
    evidence: source supporting the relationship
    evidence_type: same evidence vocabulary as source_type
    evidence_status: PROPOSED | OBSERVED | VERIFIED | ACCEPTED

A view contains:

    id: stable identifier
    title: audience-readable title
    node_ids: [node id]
    relationship_ids: [relationship id]

A feedback item contains:

    severity: decision | risk | warning | note
    message: consequence or action in business-readable language

## View selection

- Context: people and external systems around the system in scope.
- Container: deployable applications and data stores, with protocols and responsibilities.
- Component: significant functional groupings inside one container; create only when it improves an engineering decision.
- Dynamic: numbered interactions for a critical use case or failure path.
- Deployment: runtime instances, zones, networks, and operational dependencies.

Every view has a clear title, scope, audience, and legend. Every arrow is directional and specifically labelled. Use consistent names across views.

## Graphify boundary

Graphify maintains a broad source graph and can reveal code structure, clusters, paths, and candidate dependencies. The architecture model is a curated, evidence-backed subset shaped for a human decision.

Store stable IDs and selected source references in the model. Rerender from the same model without re-running graph extraction. Re-query or update graphify only when source files changed or the required evidence is absent.

## Evidence firewall

`AI_PROPOSAL` covers generated summaries, diagrams, inferred mappings, and agent reports. It may remain `PROPOSED`; it cannot establish `VERIFIED` or `ACCEPTED`. Use it to navigate toward source code, tests, runtime observations, contracts, primary external sources, or human-approved requirements.

Do not cite one generated architecture view as the sole source of another. When the primary source is unavailable, keep the element proposed or mark the relevant fact `UNKNOWN`.

## Source adaptations

- [C4 abstractions](https://c4model.com/abstractions): model people, systems, containers, components, and code at explicit abstraction levels.
- [C4 diagrams](https://c4model.com/diagrams): use only the views that add value for the audience.
- [C4 notation](https://c4model.com/diagrams/notation): give diagrams titles, legends, typed elements, descriptions, and labelled directional relationships.
- [C4 tooling](https://c4model.com/tooling): separate one architecture model from the views rendered over it.
- [Azure Well-Architected Framework](https://learn.microsoft.com/en-us/azure/well-architected/): connect technical trade-offs to business value and quality requirements.
