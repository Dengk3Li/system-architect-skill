---
name: architecture-workspace
description: Connect declared architecture to local directories, file sizes and content versions, explicit experiment runs, and conclusions. Use for a read-only file or research workspace, historical input/output tracing, snapshot comparison, storage analysis, or a shareable offline catalog.
---

# Architecture Workspace

Create a local metadata catalog and one self-contained HTML reader. The scanner and renderer use Python's standard library; they do not call an AI model. The three views share the same file observations: **files and architecture**, **runs and history**, and **storage**.

## Start with the outcome

Use the bundled synthetic research example to explain the result when helpful. For real work, establish the explicit source directory, a catalog location outside it, and the user's desired questions. A bounded read-only scan needs no extra architecture ceremony.

Keep responsibilities clear:

- Product manager owns audience, priority, release scope, and acceptance.
- System architect owns verified module placement and interfaces.
- Architecture visualizer renders architecture models as editable HTML/SVG.
- This Skill observes files and joins explicit run receipts to their exact historical observations. It does not redesign module boundaries.

## Prepare the map

Run `python3 scripts/workspace.py --help` from this Skill directory to inspect commands. Requires Python 3.10+; scanning and catalog writes support macOS/Linux. Use a modern browser for the offline reader.

If an existing module-boundary manifest is authoritative, derive its declarations:

```bash
python3 scripts/workspace.py map-from-boundaries /path/to/module-boundaries.json \
  --project-id project-one --title "Project one" --output /path/to/review/workspace-map.json
```

Otherwise copy `assets/workspace-map.template.json` and edit the project. Add module path rules, relationship evidence, and business-nature rules only from verified declarations. An empty mapping is valid and keeps ownership/nature unknown. File format is an extension label, separate from business nature. Paths use case-sensitive Python fnmatch semantics: `*` also matches `/`; overlapping owners or conflicting nature rules fail validation.

## Observe and preserve history

```bash
python3 scripts/workspace.py scan /path/to/project \
  --map /path/to/review/workspace-map.json \
  --catalog /path/to/review/catalog.json --label "Before experiment"
```

Read the returned completeness, counts, and skipped reasons. Default exclusions include hidden entries, common dependency directories, common credential names, and symlinks. These rules are not a comprehensive secret detector. File bodies stay in the source directory; hashing reads their bytes. Reading may update access times according to the filesystem.

Each scan appends an immutable observation. Full SHA-256 is calculated only for stable files at or below 16 MiB by default. Adjust `--hash-max-bytes` for the actual I/O budget; `0` disables hashing. Larger, unreadable, or changing files keep unknown content identity. A metadata match cannot promote them to equal content. Catalog source binding rejects accidental mixing of different roots.

## Record a run explicitly

Scan before execution; perform the user's experiment through its existing authorized workflow; scan after execution. Then prepare a JSON receipt with a unique run ID, status, timezone-bearing times, actual command text, input/config/output references (`snapshot_id`, relative `path`), measured metrics, conclusion, and evidence. See `references/catalog-model.md` for the exact format.

```bash
python3 scripts/workspace.py record-run /path/to/review/run.json \
  --catalog /path/to/review/catalog.json
```

The command records metadata; it never executes the receipt's command. A cancelled or failed run may have no outputs. Reusing an ID fails. References must resolve in the catalog; the tool attaches their stored full content identities. Never infer a run from file timestamps or present declared metrics as independently verified science.

## Render, inspect, and deliver

```bash
python3 scripts/workspace.py validate /path/to/review/catalog.json
python3 scripts/workspace.py render /path/to/review/catalog.json \
  --output /path/to/review/workspace.html
```

Open the HTML and verify the user's concrete question: module to file; result to recorded run to historical input/configuration; logical size by nature/module/extension/directory; two snapshots and run conclusions. Explicit historical selection clears conflicting filters and locates the selected page. JSON export preserves facts; HTML export also preserves navigation. Existing render files are protected from replacement: use a new output name.

Report the observed scope and real limitations. The catalog stores metadata, not backups or original file bytes. Full hashes support equality and accidental-corruption checks, not authorship or trustworthy execution. Shared physical blocks and clones make allocated bytes different from reclaimable storage. The reader never offers delete, move, deduplicate, or automatic classification actions.

Before external sharing, inspect relative paths, commands, metric names, and conclusions for private material and follow the user's existing publication scope. Generated HTML has no runtime network dependency; opening a hosted example still contacts its hosting provider.

## References

- `references/catalog-model.md`: model, run receipt, scan and comparison semantics.
- `assets/workspace-map.template.json`: unclassified starting map.
- Repository `examples/research-workspace/`: reproducible, explicitly synthetic example.
- Repository `docs/research/`: competitor evidence and selection rationale.
