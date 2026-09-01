#!/usr/bin/env python3
"""Choose proportional workflow controls and audit governance inventories."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List


SCHEMA_VERSION = "governance-rightsizer.v1"
DECISION_ORDER = ["KEEP", "EMBED", "ON_DEMAND", "MERGE", "REMOVE", "UNKNOWN"]
BASE_CONTROLS = ["goal", "write_scope", "observable_acceptance", "minimal_verification"]
COORDINATION_CONTROLS = [
    "authoritative_task_id",
    "owners_and_write_sets",
    "dependencies",
    "handoff_state",
]
DIRECT_AVOID = ["separate_wbs", "separate_receipt", "extra_gate", "parallel_task_id"]


class InputError(ValueError):
    pass


def unique(items: Iterable[str]) -> List[str]:
    return list(dict.fromkeys(items))


def require_positive_integer(payload: Dict[str, Any], field: str) -> int:
    value = payload.get(field)
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise InputError(f"{field} must be a positive integer")
    return value


def enabled(payload: Dict[str, Any], field: str) -> bool:
    value = payload.get(field, False)
    if not isinstance(value, bool):
        raise InputError(f"{field} must be a boolean")
    return value


def assess_task(payload: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(payload, dict):
        raise InputError("task input must be a JSON object")

    deliverables = require_positive_integer(payload, "deliverables")
    writers = require_positive_integer(payload, "writers")
    write_sets = require_positive_integer(payload, "write_sets")

    flags = {
        field: enabled(payload, field)
        for field in [
            "cross_session",
            "cross_machine",
            "public_release",
            "irreversible",
            "authority_or_lifecycle",
            "migration",
            "security_or_privacy",
            "cross_repo_contract",
            "write_conflict",
            "durable_recovery_required",
        ]
    }

    controlled_reasons = [
        field
        for field in [
            "cross_machine",
            "public_release",
            "irreversible",
            "authority_or_lifecycle",
            "migration",
            "security_or_privacy",
            "cross_repo_contract",
            "write_conflict",
        ]
        if flags[field]
    ]
    coordinated = (
        deliverables > 1
        or writers > 1
        or write_sets > 1
        or flags["cross_session"]
        or flags["durable_recovery_required"]
    )

    if controlled_reasons:
        mode = "CONTROLLED"
    elif coordinated:
        mode = "COORDINATED"
    else:
        mode = "DIRECT"

    controls = list(BASE_CONTROLS)
    if coordinated:
        controls.extend(COORDINATION_CONTROLS)
    if flags["cross_machine"]:
        controls.extend(
            ["immutable_handoff", "source_and_target_identity", "writer_free_or_lock_state"]
        )
    if flags["public_release"]:
        controls.extend(["publication_allowlist", "human_release_decision"])
    if flags["irreversible"]:
        controls.extend(["human_release_decision", "recovery_or_retention_plan"])
    if flags["authority_or_lifecycle"]:
        controls.append("authority_and_lifecycle_check")
    if flags["migration"]:
        controls.extend(["source_target_manifest", "cutover_and_rollback"])
    if flags["security_or_privacy"]:
        controls.append("security_or_privacy_review")
    if flags["cross_repo_contract"]:
        controls.append("versioned_interface_contract")
    if flags["write_conflict"]:
        controls.append("exclusive_writer_or_isolation")

    if deliverables == writers == write_sets == 1:
        decomposition = "single-deliverable"
    else:
        decomposition = "split-only-by-independent-output"

    reasons = controlled_reasons
    if mode == "COORDINATED":
        reasons = [
            name
            for name, active in [
                ("multiple_deliverables", deliverables > 1),
                ("multiple_writers", writers > 1),
                ("multiple_write_sets", write_sets > 1),
                ("cross_session", flags["cross_session"]),
                ("durable_recovery_required", flags["durable_recovery_required"]),
            ]
            if active
        ]
    if mode == "DIRECT":
        reasons = ["single reversible write path"]

    return {
        "schema_version": SCHEMA_VERSION,
        "mode": mode,
        "decomposition": decomposition,
        "reasons": reasons,
        "required_controls": unique(controls),
        "avoid": DIRECT_AVOID if mode == "DIRECT" else ["governance_only_tasks", "duplicate_state_records"],
    }


def text_field(control: Dict[str, Any], field: str) -> str:
    value = control.get(field, "")
    return value.strip() if isinstance(value, str) else ""


def is_valid_control_target(control: Dict[str, Any]) -> bool:
    if text_field(control, "duplicate_of"):
        return False
    if control.get("authority_dependency") is True and control.get("authority_known") is not True:
        return False
    return all(
        text_field(control, field)
        for field in ["risk", "failure_mode", "control", "minimum_evidence"]
    )


def audit_controls(payload: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(payload, dict) or not isinstance(payload.get("controls"), list):
        raise InputError("audit input must contain a controls array")

    controls = payload["controls"]
    ids: List[str] = []
    for control in controls:
        if not isinstance(control, dict):
            raise InputError("every control must be a JSON object")
        control_id = text_field(control, "id")
        if not control_id:
            raise InputError("every control must have a non-empty id")
        if control_id in ids:
            raise InputError(f"duplicate control id: {control_id}")
        ids.append(control_id)

    controls_by_id = {text_field(control, "id"): control for control in controls}
    known_ids = set(controls_by_id)
    semantic_owner: Dict[tuple, str] = {}
    decisions: List[Dict[str, str]] = []

    for control in controls:
        control_id = text_field(control, "id")
        duplicate_of = text_field(control, "duplicate_of")
        risk = text_field(control, "risk")
        failure_mode = text_field(control, "failure_mode")
        action = text_field(control, "control")
        evidence = text_field(control, "minimum_evidence")
        trigger_scope = text_field(control, "trigger_scope") or "always"

        if duplicate_of:
            if duplicate_of == control_id or duplicate_of not in known_ids:
                decision, reason = "UNKNOWN", "duplicate target is unresolved"
            elif not is_valid_control_target(controls_by_id[duplicate_of]):
                decision, reason = "UNKNOWN", "duplicate target is not a valid control"
            else:
                decision, reason = "MERGE", f"reuse authoritative control {duplicate_of}"
        elif control.get("authority_dependency") is True and control.get("authority_known") is not True:
            decision, reason = "UNKNOWN", "authority is unresolved"
        elif not risk or not failure_mode or not action:
            decision, reason = "REMOVE", "no complete risk-to-failure-to-control chain"
        elif not evidence:
            decision, reason = "UNKNOWN", "minimum evidence is unresolved"
        else:
            semantic_key = (risk.casefold(), failure_mode.casefold(), action.casefold())
            if semantic_key in semantic_owner:
                owner = semantic_owner[semantic_key]
                decision, reason = "MERGE", f"same control already exists as {owner}"
            else:
                semantic_owner[semantic_key] = control_id
                if trigger_scope != "always":
                    decision, reason = "ON_DEMAND", f"activate only for {trigger_scope}"
                elif control.get("separate_owner") is True or control.get("separate_decision") is True:
                    decision, reason = "KEEP", "control owns a distinct decision or authority"
                else:
                    decision, reason = "EMBED", "control belongs in the deliverable definition of done"

        decisions.append({"id": control_id, "decision": decision, "reason": reason})

    counts = Counter(item["decision"] for item in decisions)
    summary = {decision: counts.get(decision, 0) for decision in DECISION_ORDER}
    return {
        "schema_version": SCHEMA_VERSION,
        "decisions": decisions,
        "summary": summary,
    }


def read_json(input_file: Path) -> Dict[str, Any]:
    try:
        return json.loads(input_file.read_text(encoding="utf-8"))
    except OSError as exc:
        raise InputError(f"cannot read input: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise InputError(f"invalid JSON: {exc.msg}") from exc


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Right-size task governance and remove duplicate controls."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ["assess-task", "audit-controls"]:
        command_parser = subparsers.add_parser(command)
        command_parser.add_argument("--input", type=Path, required=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        payload = read_json(args.input)
        if args.command == "assess-task":
            result = assess_task(payload)
        else:
            result = audit_controls(payload)
    except InputError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
