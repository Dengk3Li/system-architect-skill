import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    REPO_ROOT
    / "skills"
    / "right-size-governance"
    / "scripts"
    / "governance_rightsizer.py"
)


class GovernanceRightsizerTest(unittest.TestCase):
    def run_cli(self, command, payload):
        with tempfile.TemporaryDirectory() as tmp:
            input_file = Path(tmp) / "input.json"
            input_file.write_text(json.dumps(payload), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, str(SCRIPT), command, "--input", str(input_file)],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        return json.loads(completed.stdout)

    def test_single_reversible_write_stays_direct(self):
        result = self.run_cli(
            "assess-task",
            {
                "deliverables": 1,
                "writers": 1,
                "write_sets": 1,
                "cross_session": False,
                "cross_machine": False,
                "public_release": False,
                "irreversible": False,
                "authority_or_lifecycle": False,
                "migration": False,
                "security_or_privacy": False,
                "cross_repo_contract": False,
                "write_conflict": False,
                "durable_recovery_required": False,
            },
        )

        self.assertEqual(result["mode"], "DIRECT")
        self.assertEqual(result["decomposition"], "single-deliverable")
        self.assertEqual(
            result["required_controls"],
            ["goal", "write_scope", "observable_acceptance", "minimal_verification"],
        )
        self.assertEqual(
            result["avoid"],
            ["separate_wbs", "separate_receipt", "extra_gate", "parallel_task_id"],
        )

    def test_cross_session_multi_writer_work_is_coordinated(self):
        result = self.run_cli(
            "assess-task",
            {
                "deliverables": 2,
                "writers": 2,
                "write_sets": 2,
                "cross_session": True,
                "cross_machine": False,
                "public_release": False,
                "irreversible": False,
                "authority_or_lifecycle": False,
                "migration": False,
                "security_or_privacy": False,
                "cross_repo_contract": False,
                "write_conflict": False,
                "durable_recovery_required": True,
            },
        )

        self.assertEqual(result["mode"], "COORDINATED")
        self.assertEqual(result["decomposition"], "split-only-by-independent-output")
        self.assertEqual(
            result["required_controls"],
            [
                "goal",
                "write_scope",
                "observable_acceptance",
                "minimal_verification",
                "authoritative_task_id",
                "owners_and_write_sets",
                "dependencies",
                "handoff_state",
            ],
        )

    def test_public_release_adds_controls_without_forcing_more_decomposition(self):
        result = self.run_cli(
            "assess-task",
            {
                "deliverables": 1,
                "writers": 1,
                "write_sets": 1,
                "cross_session": False,
                "cross_machine": False,
                "public_release": True,
                "irreversible": False,
                "authority_or_lifecycle": False,
                "migration": False,
                "security_or_privacy": False,
                "cross_repo_contract": False,
                "write_conflict": False,
                "durable_recovery_required": False,
            },
        )

        self.assertEqual(result["mode"], "CONTROLLED")
        self.assertEqual(result["decomposition"], "single-deliverable")
        self.assertEqual(
            result["required_controls"],
            [
                "goal",
                "write_scope",
                "observable_acceptance",
                "minimal_verification",
                "publication_allowlist",
                "human_release_decision",
            ],
        )

    def test_control_audit_separates_real_controls_from_ceremony(self):
        result = self.run_cli(
            "audit-controls",
            {
                "controls": [
                    {
                        "id": "qa-readback",
                        "risk": "A generated file is malformed.",
                        "failure_mode": "The user receives an unreadable artifact.",
                        "control": "Open and read back the final artifact.",
                        "minimum_evidence": "Successful readback.",
                        "trigger_scope": "always",
                    },
                    {
                        "id": "machine-handoff",
                        "risk": "A second machine receives the wrong state.",
                        "failure_mode": "Work resumes from an unrelated revision.",
                        "control": "Bind the handoff to source and target identity.",
                        "minimum_evidence": "Matching revision and target receipt.",
                        "trigger_scope": "cross_machine",
                    },
                    {
                        "id": "handoff-copy",
                        "risk": "A second machine receives the wrong state.",
                        "failure_mode": "Work resumes from an unrelated revision.",
                        "control": "Bind the handoff to source and target identity.",
                        "minimum_evidence": "Matching revision and target receipt.",
                        "duplicate_of": "machine-handoff",
                        "trigger_scope": "cross_machine",
                    },
                    {
                        "id": "status-report",
                        "risk": "",
                        "failure_mode": "",
                        "control": "Write a separate progress receipt every turn.",
                        "minimum_evidence": "A receipt file exists.",
                        "trigger_scope": "always",
                    },
                    {
                        "id": "authority-switch",
                        "risk": "The wrong source becomes canonical.",
                        "failure_mode": "A candidate silently replaces accepted state.",
                        "control": "Require an explicit authority decision.",
                        "minimum_evidence": "Accepted decision references both states.",
                        "authority_dependency": True,
                        "authority_known": False,
                        "trigger_scope": "authority_lifecycle",
                    },
                    {
                        "id": "release-decision",
                        "risk": "Private material becomes public.",
                        "failure_mode": "The publication exposes excluded files.",
                        "control": "Use an allowlist and one release decision.",
                        "minimum_evidence": "Reviewed allowlist and decision.",
                        "separate_decision": True,
                        "trigger_scope": "always",
                    },
                ]
            },
        )

        decisions = {item["id"]: item["decision"] for item in result["decisions"]}
        self.assertEqual(
            decisions,
            {
                "qa-readback": "EMBED",
                "machine-handoff": "ON_DEMAND",
                "handoff-copy": "MERGE",
                "status-report": "REMOVE",
                "authority-switch": "UNKNOWN",
                "release-decision": "KEEP",
            },
        )
        self.assertEqual(
            result["summary"],
            {
                "KEEP": 1,
                "EMBED": 1,
                "ON_DEMAND": 1,
                "MERGE": 1,
                "REMOVE": 1,
                "UNKNOWN": 1,
            },
        )

    def test_unknown_duplicate_target_fails_closed(self):
        result = self.run_cli(
            "audit-controls",
            {
                "controls": [
                    {
                        "id": "orphan-copy",
                        "risk": "Duplicate control drift.",
                        "failure_mode": "Two records disagree.",
                        "control": "Reuse the existing control.",
                        "minimum_evidence": "One authoritative record.",
                        "duplicate_of": "missing-control",
                        "trigger_scope": "always",
                    }
                ]
            },
        )

        self.assertEqual(result["decisions"][0]["decision"], "UNKNOWN")
        self.assertEqual(result["decisions"][0]["reason"], "duplicate target is unresolved")

    def test_invalid_duplicate_target_cannot_become_authority(self):
        result = self.run_cli(
            "audit-controls",
            {
                "controls": [
                    {
                        "id": "empty-target",
                        "risk": "",
                        "failure_mode": "",
                        "control": "Write a report.",
                        "minimum_evidence": "A file exists.",
                        "trigger_scope": "always",
                    },
                    {
                        "id": "copy",
                        "risk": "A decision is lost.",
                        "failure_mode": "A later session cannot recover it.",
                        "control": "Reuse the authoritative decision.",
                        "minimum_evidence": "The authority can be read back.",
                        "duplicate_of": "empty-target",
                        "trigger_scope": "always",
                    },
                ]
            },
        )

        self.assertEqual(result["decisions"][0]["decision"], "REMOVE")
        self.assertEqual(result["decisions"][1]["decision"], "UNKNOWN")
        self.assertEqual(result["decisions"][1]["reason"], "duplicate target is not a valid control")


if __name__ == "__main__":
    unittest.main()
