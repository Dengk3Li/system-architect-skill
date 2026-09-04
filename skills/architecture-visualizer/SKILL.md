---
name: architecture-visualizer
description: Turn an accepted or discovered system architecture into a stable model plus human-readable SVG, interactive HTML, and feedback. Use when the user asks for an architecture diagram, system map, interactive walkthrough, presentation-ready architecture view, or repeatable visualization from graphify evidence.
---

# Architecture Visualizer

Create architecture communication that helps a specific audience understand the system and make a decision. Keep one structured architecture model as the source; render views from it instead of redrawing disconnected diagrams.

## Establish evidence and audience

Read human-approved product requirements, architecture decisions, repository guidance, source code, executable tests, runtime evidence, contracts, and operational constraints. When a current graphify graph exists, query it for relevant nodes and paths rather than rebuilding it. Use graphify as a locator and candidate model of the codebase, not as authority for product intent or accepted architecture.

Treat AI-generated summaries, inferred relationships, diagrams, and prior agent reports as `AI_PROPOSAL`. Trace each accepted or verified element to primary evidence. An AI proposal may help find or explain evidence; it cannot establish an architecture fact, validate another AI artifact, or promote itself to `VERIFIED`.

Identify the audience and decision:

- executives or product teams need business capabilities, people, systems, consequences, and major risks;
- engineering teams need containers, components, interfaces, data and control flow, ownership, and failure behavior;
- operations and security teams need deployment, trust boundaries, runtime dependencies, observability, and recovery.

Do not mix every abstraction level in one view. Use only the C4-style zoom levels, frontend workspaces, or dynamic/deployment views that add value.

## Create the architecture model

Read [references/architecture-model.md](references/architecture-model.md), then populate architecture-model.json. Every element needs a responsibility, business driver, type, source, source type, and evidence status. Every relationship needs a direction, specific label, evidence, evidence type, and evidence status.

Keep uncertain discovered relationships explicit. A graph edge or folder relationship is not automatically an accepted runtime dependency.

When the frontend is material to the decision, copy `assets/frontend-module.template.json`. Keep the frontend capability as a system node plus a linked `frontend_modules` entry. Map accepted requirement IDs to its pages, components, states, interactions, data contracts, quality requirements, and canvas elements. Read the frontend schema in the model reference. Do not invent product acceptance criteria or treat a wireframe as proof of implementation.

## Render repeatably

Run:

    python3 <skill-dir>/scripts/render_architecture.py \
      architecture-model.json --output-dir <destination>

The renderer creates:

- architecture.svg for documents and slides;
- architecture.html with view switching, search, element details, source evidence, architecture feedback, and an editable frontend workspace when the model defines one;
- architecture-summary.md for the decision and feedback narrative.

In a frontend workspace, select and drag an element to move it, use the lower-right handle to resize it, edit its requirement mapping and implementation note, and attach a local annotation. Export the edited JSON before leaving the page. Browser edits are review candidates until the exported model is validated and accepted; do not treat the generated HTML or local browser state as architecture authority.

Edit the source model and rerun the renderer when accepted architecture changes. Do not hand-edit generated views as independent sources.

Use ppt-master only when the user asks for a presentation or the architecture must join a broader slide narrative. Give it the SVG and summary as source artifacts; do not ask it to rediscover architecture.

## Human feedback

The output must state what the architecture enables, the decisive trade-offs, business or operational consequences, material risks, unresolved assumptions, and decisions required from humans. A diagram is supporting evidence, not the whole answer.

Validate the model, open the HTML, and inspect the SVG before delivery. Preserve UNKNOWN when the source, runtime relationship, ownership, or acceptance state is not verified.
