# v0.4.0 validation record

This record describes engineering and interface checks, not scientific validation or external user research. The tested workspace uses only synthetic temporary files and the bundled synthetic catalog.

## Automated checks

Local platform: macOS, Python 3.10.2, Node 20.20.2. All 55 Python tests passed, including 28 workspace tests and the 27 existing architect/visualizer tests. All three Skill manifests and the plugin manifest passed the installed creator validators. The JavaScript syntax check passed.

Workspace cases cover full hashing, unknown content, overwritten historical inputs, source binding, path exclusions and symlinks, hardlinks, partial scans, explicit and empty-output runs, invalid references and forged hashes, snapshot/receipt integrity, conflicting maps, changing/unreadable content, lock conflicts, atomic replacement failure, source write avoidance, malformed policy/time/numeric fields, boundary-map projection, empty catalogs, script embedding, and deterministic example generation.

A separate CLI journey created two temporary files and exercised scan → second snapshot → record-run → validate → render → diff. It retained both historical observations, imported one explicit receipt, and wrote no extra files in the source. The command text in the receipt was not executed.

CI repeats tests, script syntax, ownership checks and example freshness on Ubuntu and macOS, Python 3.10 and 3.13. Workflow results are authoritative for remote execution; this document does not turn a configured matrix into a passing run.

## Browser checks

The actual offline reader was exercised in the Codex in-app browser at 1440px and 390px widths. The three views were checked for horizontal page overflow; wide tables scroll inside their own containers. Browser console checks returned no warnings/errors during the inspected journey.

Verified tasks:

1. Filter the experiment-results module and select the 24-step prediction. Follow its recorded run and open the earlier feature input. File references resolve to the selected historical snapshot and retain their own bytes and full digest.
2. Inspect the baseline feature input at 240,009 B and the later version at 320,009 B. Inspect the same-size 27 B configuration versions with distinct content hashes.
3. Compare baseline and final snapshots: two content changes and three additions. Compare explicit run metrics while retaining the cancelled attempt with no outputs.
4. Inspect logical and allocated storage totals, plus nature/module/extension/directory grouping. The synthetic allocation normalization is visible.
5. Export JSON and compare it to the complete source catalog: equality passed. Export HTML, reopen the downloaded file through a separate local preview, and confirm that the selected historical file and catalog remained available.

## Navigation correction review

The finish review found two material navigation defects: a selected run could remain above the mobile viewport, and old filters could hide an explicitly selected historical input. The source now moves focus and viewport to the selected run, clears conflicting filters for explicit file selection, and locates the selected file's sorted page. Returning from a run to files focuses its row.

The exact path “filtered results → prediction → related run → earlier input → files” was repeated. The selected row and inspector both identified `data/features/window.csv` at 320,009 B in the new-configuration snapshot. Mobile run title and input/output controls became immediately visible. The independent verdict marked all three listed fixes resolved, including the direction-contract documentation. It did not certify an unbounded visual quality ceiling.

Public screenshots in the example directory are actual page captures, recorded in `preview-provenance.json`. The build was code-led, with no approved image comp or QUALITY BAR image cards. No screenshot of a competitor is distributed.

## Limits

No Windows scanner claim, large-directory performance benchmark, exhaustive browser matrix, adversarially authenticated provenance, or scientific admission is asserted. The scanner is not an atomic filesystem snapshot or secret classifier. The chosen user segment and first-use success remain hypotheses for later observation with target users.
