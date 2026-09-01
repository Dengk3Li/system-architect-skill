from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GUARD = ROOT / "skills/system-architect/scripts/check_module_scope.py"


class ModuleScopeGuardTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repo = Path(self.temp_dir.name)
        (self.repo / "src/catalog").mkdir(parents=True)
        (self.repo / "src/checkout").mkdir(parents=True)
        (self.repo / "src/shell").mkdir(parents=True)
        (self.repo / "src/catalog/view.ts").write_text("export {}\n", encoding="utf-8")
        (self.repo / "src/checkout/view.ts").write_text("export {}\n", encoding="utf-8")
        (self.repo / "src/shell/index.ts").write_text("export {}\n", encoding="utf-8")
        self.manifest = self.repo / ".system-architect/module-boundaries.json"
        self.manifest.parent.mkdir()
        self.write_manifest()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def manifest_payload(self) -> dict[str, object]:
        return {
            "schema_version": "system-architect.module-boundaries/v1",
            "managed_roots": ["src"],
            "managed_extensions": [".ts"],
            "interfaces": [
                {
                    "interface_id": "shell.slot.v1",
                    "owner": "shell",
                    "version": "1.0.0",
                    "contract": "Feature modules mount through a named slot.",
                }
            ],
            "modules": [
                {
                    "module_id": "catalog",
                    "purpose": "Browse the catalog.",
                    "protected": False,
                    "allowed_roles": ["module-developer"],
                    "provides": [],
                    "consumes": ["shell.slot.v1"],
                    "owned_paths": ["src/catalog/**"],
                },
                {
                    "module_id": "checkout",
                    "purpose": "Complete purchases.",
                    "protected": False,
                    "allowed_roles": ["module-developer"],
                    "provides": [],
                    "consumes": ["shell.slot.v1"],
                    "owned_paths": ["src/checkout/**"],
                },
                {
                    "module_id": "shell",
                    "purpose": "Own shared navigation and integration slots.",
                    "protected": True,
                    "allowed_roles": ["system-architect", "integrator"],
                    "provides": ["shell.slot.v1"],
                    "consumes": [],
                    "owned_paths": ["src/shell/**", ".system-architect/**"],
                },
            ],
        }

    def write_manifest(self, payload: dict[str, object] | None = None) -> None:
        self.manifest.write_text(
            json.dumps(payload or self.manifest_payload(), indent=2) + "\n",
            encoding="utf-8",
        )

    def run_guard(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(GUARD),
                "--repo-root",
                str(self.repo),
                "--manifest",
                str(self.manifest),
                *args,
            ],
            text=True,
            capture_output=True,
            check=False,
        )

    def init_git_repo(self) -> None:
        subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=self.repo, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=self.repo, check=True)
        subprocess.run(["git", "add", "."], cwd=self.repo, check=True)
        subprocess.run(["git", "commit", "-qm", "baseline"], cwd=self.repo, check=True)

    def test_manifest_passes_when_every_managed_file_has_one_owner(self) -> None:
        result = self.run_guard("--check-manifest")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS (3 modules, 3 files, 1 interfaces)", result.stdout)

    def test_manifest_blocks_an_unowned_managed_file(self) -> None:
        (self.repo / "src/orphan.ts").write_text("export {}\n", encoding="utf-8")
        result = self.run_guard("--check-manifest")
        self.assertEqual(result.returncode, 2)
        self.assertIn("src/orphan.ts has no registered owner", result.stderr)

    def test_manifest_blocks_overlapping_owners(self) -> None:
        payload = self.manifest_payload()
        modules = payload["modules"]
        assert isinstance(modules, list)
        checkout = modules[1]
        assert isinstance(checkout, dict)
        checkout["owned_paths"] = ["src/**"]
        self.write_manifest(payload)
        result = self.run_guard("--check-manifest")
        self.assertEqual(result.returncode, 2)
        self.assertIn("has multiple owners", result.stderr)

    def test_manifest_blocks_incomplete_interface_contracts(self) -> None:
        payload = self.manifest_payload()
        interfaces = payload["interfaces"]
        assert isinstance(interfaces, list)
        interface = interfaces[0]
        assert isinstance(interface, dict)
        del interface["version"]
        self.write_manifest(payload)
        result = self.run_guard("--check-manifest")
        self.assertEqual(result.returncode, 2)
        self.assertIn("requires version", result.stderr)

    def test_module_developer_can_change_only_the_owned_module(self) -> None:
        result = self.run_guard(
            "--module",
            "catalog",
            "--role",
            "module-developer",
            "--files",
            "src/catalog/view.ts",
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS (catalog, 1 files)", result.stdout)

    def test_cross_module_change_is_blocked(self) -> None:
        result = self.run_guard(
            "--module",
            "catalog",
            "--role",
            "module-developer",
            "--files",
            "src/catalog/view.ts",
            "src/checkout/view.ts",
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("owned by checkout, not catalog", result.stderr)

    def test_protected_module_requires_architect_role_and_explicit_flag(self) -> None:
        wrong_role = self.run_guard(
            "--module",
            "shell",
            "--role",
            "module-developer",
            "--files",
            "src/shell/index.ts",
        )
        self.assertEqual(wrong_role.returncode, 2)
        self.assertIn("protected module requires system-architect or integrator", wrong_role.stderr)

        missing_flag = self.run_guard(
            "--module",
            "shell",
            "--role",
            "system-architect",
            "--files",
            "src/shell/index.ts",
        )
        self.assertEqual(missing_flag.returncode, 2)
        self.assertIn("requires --architecture-change", missing_flag.stderr)

        allowed = self.run_guard(
            "--module",
            "shell",
            "--role",
            "system-architect",
            "--architecture-change",
            "--files",
            "src/shell/index.ts",
        )
        self.assertEqual(allowed.returncode, 0, allowed.stdout + allowed.stderr)

    def test_git_diff_mode_includes_untracked_files(self) -> None:
        self.init_git_repo()
        (self.repo / "src/checkout/untracked.ts").write_text("export {}\n", encoding="utf-8")
        result = self.run_guard(
            "--module",
            "catalog",
            "--role",
            "module-developer",
            "--base",
            "HEAD",
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("owned by checkout, not catalog", result.stderr)

    def test_staged_mode_checks_only_the_index(self) -> None:
        self.init_git_repo()
        (self.repo / "src/catalog/view.ts").write_text("export const ok = true\n", encoding="utf-8")
        subprocess.run(["git", "add", "src/catalog/view.ts"], cwd=self.repo, check=True)
        (self.repo / "src/checkout/view.ts").write_text("export const later = true\n", encoding="utf-8")

        result = self.run_guard(
            "--module",
            "catalog",
            "--role",
            "module-developer",
            "--staged",
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS (catalog, 1 files)", result.stdout)


if __name__ == "__main__":
    unittest.main()
