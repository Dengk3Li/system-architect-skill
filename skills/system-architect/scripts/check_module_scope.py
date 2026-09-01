#!/usr/bin/env python3
"""Validate owned module boundaries and block cross-module changes."""

from __future__ import annotations

import argparse
import fnmatch
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable


REQUIRED_SCHEMA = "system-architect.module-boundaries/v1"
ROLES = ("module-developer", "integrator", "system-architect")


class BoundaryError(ValueError):
    """Raised when a manifest or requested change violates a boundary."""


def load_manifest(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise BoundaryError(f"manifest does not exist: {path}") from exc
    except json.JSONDecodeError as exc:
        raise BoundaryError(f"manifest is not valid JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise BoundaryError("manifest root must be an object")
    return payload


def normalise_path(repo_root: Path, raw: str | Path) -> str:
    candidate = Path(raw)
    if candidate.is_absolute():
        try:
            candidate = candidate.resolve().relative_to(repo_root.resolve())
        except ValueError as exc:
            raise BoundaryError(f"path is outside repo root: {raw}") from exc
    text = candidate.as_posix()
    while text.startswith("./"):
        text = text[2:]
    if not text or text == ".." or text.startswith("../"):
        raise BoundaryError(f"path is outside repo root: {raw}")
    return text


def modules_by_id(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    raw_modules = manifest.get("modules")
    if not isinstance(raw_modules, list) or not raw_modules:
        raise BoundaryError("manifest modules must be a non-empty list")

    modules: dict[str, dict[str, Any]] = {}
    for raw_module in raw_modules:
        if not isinstance(raw_module, dict):
            raise BoundaryError("every module must be an object")
        module_id = raw_module.get("module_id")
        if not isinstance(module_id, str) or not module_id.strip():
            raise BoundaryError("every module requires module_id")
        if module_id in modules:
            raise BoundaryError(f"duplicate module_id: {module_id}")
        if not isinstance(raw_module.get("purpose"), str) or not raw_module["purpose"].strip():
            raise BoundaryError(f"module {module_id} requires purpose")

        owned_paths = raw_module.get("owned_paths")
        if (
            not isinstance(owned_paths, list)
            or not owned_paths
            or not all(isinstance(item, str) and item for item in owned_paths)
        ):
            raise BoundaryError(f"module {module_id} requires owned_paths")

        roles = raw_module.get("allowed_roles")
        if (
            not isinstance(roles, list)
            or not roles
            or any(role not in ROLES for role in roles)
        ):
            raise BoundaryError(f"module {module_id} has invalid allowed_roles")

        for key in ("provides", "consumes"):
            values = raw_module.get(key)
            if not isinstance(values, list) or not all(isinstance(item, str) for item in values):
                raise BoundaryError(f"module {module_id} requires {key} list")

        modules[module_id] = raw_module
    return modules


def interfaces_by_id(
    manifest: dict[str, Any], modules: dict[str, dict[str, Any]]
) -> dict[str, dict[str, Any]]:
    raw_interfaces = manifest.get("interfaces")
    if not isinstance(raw_interfaces, list):
        raise BoundaryError("interfaces must be a list")

    interfaces: dict[str, dict[str, Any]] = {}
    for raw_interface in raw_interfaces:
        if not isinstance(raw_interface, dict):
            raise BoundaryError("every interface must be an object")
        interface_id = raw_interface.get("interface_id")
        if not isinstance(interface_id, str) or not interface_id.strip():
            raise BoundaryError("every interface requires interface_id")
        if interface_id in interfaces:
            raise BoundaryError(f"duplicate interface_id: {interface_id}")
        for key in ("owner", "version", "contract"):
            value = raw_interface.get(key)
            if not isinstance(value, str) or not value.strip():
                raise BoundaryError(f"interface {interface_id} requires {key}")
        if raw_interface["owner"] not in modules:
            raise BoundaryError(f"interface {interface_id} has unknown owner")
        interfaces[interface_id] = raw_interface
    return interfaces


def owners_for(path: str, modules: dict[str, dict[str, Any]]) -> list[str]:
    return [
        module_id
        for module_id, module in modules.items()
        if any(fnmatch.fnmatchcase(path, pattern) for pattern in module["owned_paths"])
    ]


def managed_files(repo_root: Path, manifest: dict[str, Any]) -> list[str]:
    extensions = manifest.get("managed_extensions")
    roots = manifest.get("managed_roots")
    if (
        not isinstance(extensions, list)
        or not extensions
        or not all(isinstance(item, str) and item.startswith(".") for item in extensions)
    ):
        raise BoundaryError("managed_extensions must be a non-empty extension list")
    if (
        not isinstance(roots, list)
        or not roots
        or not all(isinstance(item, str) and item for item in roots)
    ):
        raise BoundaryError("managed_roots must be a non-empty path list")

    suffixes = {item.lower() for item in extensions}
    found: set[str] = set()
    for raw_root in roots:
        root_path = repo_root / normalise_path(repo_root, raw_root)
        if not root_path.is_dir():
            raise BoundaryError(f"managed root does not exist: {raw_root}")
        for path in root_path.rglob("*"):
            if path.is_file() and path.suffix.lower() in suffixes:
                found.add(path.relative_to(repo_root).as_posix())
    return sorted(found)


def validate_manifest(repo_root: Path, manifest: dict[str, Any]) -> tuple[int, int, int]:
    if manifest.get("schema_version") != REQUIRED_SCHEMA:
        raise BoundaryError(f"unsupported schema_version: {manifest.get('schema_version')}")

    modules = modules_by_id(manifest)
    interfaces = interfaces_by_id(manifest, modules)

    for module_id, module in modules.items():
        for interface_id in module["provides"] + module["consumes"]:
            if interface_id not in interfaces:
                raise BoundaryError(
                    f"module {module_id} references unknown interface: {interface_id}"
                )
        for interface_id in module["provides"]:
            if interfaces[interface_id]["owner"] != module_id:
                raise BoundaryError(
                    f"interface {interface_id} owner does not match provider {module_id}"
                )

    files = managed_files(repo_root, manifest)
    errors: list[str] = []
    for path in files:
        owners = owners_for(path, modules)
        if not owners:
            errors.append(f"{path} has no registered owner")
        elif len(owners) > 1:
            errors.append(f"{path} has multiple owners: {', '.join(owners)}")
    if errors:
        raise BoundaryError("\n".join(errors))
    return len(modules), len(files), len(interfaces)


def run_git(repo_root: Path, args: list[str], failure: str) -> list[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode:
        raise BoundaryError(result.stderr.strip() or failure)
    return [line for line in result.stdout.splitlines() if line.strip()]


def git_changed_files(repo_root: Path, base: str) -> list[str]:
    changed = run_git(
        repo_root,
        ["diff", "--name-only", "--diff-filter=ACDMRTUXB", base, "--"],
        f"git diff failed for base {base}",
    )
    untracked = run_git(
        repo_root,
        ["ls-files", "--others", "--exclude-standard"],
        "git ls-files failed",
    )
    return sorted(set(changed + untracked))


def git_staged_files(repo_root: Path) -> list[str]:
    return sorted(
        set(
            run_git(
                repo_root,
                ["diff", "--cached", "--name-only", "--diff-filter=ACDMRTUXB", "--"],
                "git staged diff failed",
            )
        )
    )


def validate_scope(
    repo_root: Path,
    manifest: dict[str, Any],
    *,
    module_id: str,
    role: str,
    architecture_change: bool,
    files: Iterable[str],
) -> int:
    validate_manifest(repo_root, manifest)
    modules = modules_by_id(manifest)
    if module_id not in modules:
        raise BoundaryError(f"unknown module: {module_id}")

    module = modules[module_id]
    if role not in module["allowed_roles"]:
        if module.get("protected"):
            raise BoundaryError(
                f"protected module requires system-architect or integrator: {module_id}"
            )
        raise BoundaryError(f"role {role} cannot modify module {module_id}")
    if module.get("protected") and not architecture_change:
        raise BoundaryError(f"protected module requires --architecture-change: {module_id}")

    checked = 0
    for raw_path in files:
        path = normalise_path(repo_root, raw_path)
        owners = owners_for(path, modules)
        if not owners:
            raise BoundaryError(f"{path} has no registered owner")
        if len(owners) > 1:
            raise BoundaryError(f"{path} has multiple owners: {', '.join(owners)}")
        if owners[0] != module_id:
            raise BoundaryError(f"{path} is owned by {owners[0]}, not {module_id}")
        checked += 1
    return checked


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--check-manifest", action="store_true")
    parser.add_argument("--module")
    parser.add_argument("--role", choices=ROLES, default="module-developer")
    parser.add_argument("--architecture-change", action="store_true")
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--files", nargs="*")
    source.add_argument("--base", help="check changes since a Git revision plus untracked files")
    source.add_argument("--staged", action="store_true", help="check only staged paths")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repo_root = args.repo_root.resolve()
    manifest_path = args.manifest or Path(".system-architect/module-boundaries.json")
    if not manifest_path.is_absolute():
        manifest_path = repo_root / manifest_path

    try:
        manifest = load_manifest(manifest_path)
        if args.check_manifest:
            module_count, file_count, interface_count = validate_manifest(repo_root, manifest)
            print(
                "module boundary manifest: PASS "
                f"({module_count} modules, {file_count} files, {interface_count} interfaces)"
            )
            return 0
        if not args.module:
            raise BoundaryError("--module is required unless --check-manifest is used")

        if args.base:
            files = git_changed_files(repo_root, args.base)
        elif args.staged:
            files = git_staged_files(repo_root)
        else:
            files = args.files or []

        checked = validate_scope(
            repo_root,
            manifest,
            module_id=args.module,
            role=args.role,
            architecture_change=args.architecture_change,
            files=files,
        )
        print(f"module scope: PASS ({args.module}, {checked} files)")
        return 0
    except BoundaryError as exc:
        print(f"module scope: BLOCKED\n{exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
