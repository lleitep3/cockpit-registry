#!/usr/bin/env python3
"""
Validate the cockpit-registry structure as a whole.

This script builds on top of validate_packages.py and adds checks for:
  - package-index.yaml header and metadata consistency
  - unique package names/versions in the index
  - semantic versioning across the registry
  - on pull requests: changed packages are reflected in the index (version
    bump, updated_at refresh, total_packages count)
"""

import os
import re
import subprocess
import sys
from datetime import datetime, timezone

import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from validate_packages import (
    print_err,
    print_info,
    print_ok,
    validate_registry,
)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


REQUIRED_INDEX_FIELDS = [
    "version",
    "name",
    "description",
    "url",
    "maintainer",
    "maintainer_email",
    "updated_at",
    "metadata",
    "packages",
]

SEMVER_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)(?:-[\w.]+)?(?:\+[\w.]+)?$")


def is_semver(value):
    return bool(SEMVER_RE.match(str(value)))


def _run_git(args):
    result = subprocess.run(
        ["git", "-C", REPO_ROOT] + args,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def _get_changed_paths(base_ref="main"):
    base = os.environ.get("GITHUB_BASE_REF", base_ref)
    diff = _run_git(["diff", f"origin/{base}...HEAD", "--name-status"])
    if not diff:
        diff = _run_git(["diff", f"{base}...HEAD", "--name-status"])

    changed = {"index": False, "packages": set()}
    for line in diff.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        status, path = parts[0], parts[1]

        if status.startswith("R") and len(parts) >= 3:
            path = parts[2]

        if path == "package-index.yaml":
            changed["index"] = True
        elif path.startswith("packages/"):
            pkg_name = path.split("/", 2)[1] if len(path.split("/")) >= 2 else ""
            if pkg_name:
                changed["packages"].add(pkg_name)

    return changed


def _load_base_index(base_ref="main"):
    base = os.environ.get("GITHUB_BASE_REF", base_ref)
    raw = _run_git(["show", f"origin/{base}:package-index.yaml"])
    if not raw:
        raw = _run_git(["show", f"{base}:package-index.yaml"])
    if not raw:
        return None
    try:
        return yaml.safe_load(raw)
    except Exception as exc:
        print_err(f"Could not parse base package-index.yaml: {exc}")
        return None


def validate_index_header(index):
    errors = 0
    for field in REQUIRED_INDEX_FIELDS:
        if field not in index:
            print_err(f"package-index.yaml is missing required top-level field: {field}")
            errors += 1

    metadata = index.get("metadata") if isinstance(index, dict) else {}
    if isinstance(metadata, dict):
        if "total_packages" not in metadata:
            print_err("package-index.yaml metadata is missing 'total_packages'")
            errors += 1
        if "categories" not in metadata or not isinstance(metadata.get("categories"), list):
            print_err("package-index.yaml metadata is missing 'categories' list")
            errors += 1

    return errors


def validate_index_packages(index):
    errors = 0
    packages = index.get("packages", []) if isinstance(index, dict) else []
    metadata_total = (index.get("metadata", {}) or {}).get("total_packages")

    if not isinstance(packages, list):
        print_err("'packages' in package-index.yaml must be a list")
        return errors + 1

    if metadata_total is not None and len(packages) != metadata_total:
        print_err(
            f"metadata.total_packages ({metadata_total}) does not match actual "
            f"packages list length ({len(packages)})"
        )
        errors += 1

    seen_names = set()
    seen_versions = set()
    required_pkg_fields = ["name", "version", "path"]

    for pkg in packages:
        if not isinstance(pkg, dict):
            print_err(f"Invalid package entry in index (not a mapping): {pkg}")
            errors += 1
            continue

        name = pkg.get("name")
        version = pkg.get("version")

        if not name or not version:
            print_err(f"Package entry missing required fields (name, version): {pkg}")
            errors += 1
            continue

        if name in seen_names:
            print_err(f"Duplicate package name in index: {name}")
            errors += 1
        seen_names.add(name)

        key = (name, str(version))
        if key in seen_versions:
            print_err(f"Duplicate package name/version in index: {name}@{version}")
            errors += 1
        seen_versions.add(key)

        if not is_semver(version):
            print_err(f"Package '{name}' has invalid semantic version: {version}")
            errors += 1

        for field in required_pkg_fields:
            if field not in pkg or pkg[field] in (None, ""):
                print_err(f"Package '{name}' index entry missing required field: {field}")
                errors += 1

        if pkg.get("path") and pkg.get("path") != f"packages/{name}":
            print_err(
                f"Package '{name}' path mismatch: index says '{pkg.get('path')}', "
                f"expected 'packages/{name}'"
            )
            errors += 1

        released_at = pkg.get("released_at")
        if released_at:
            try:
                datetime.fromisoformat(released_at.replace("Z", "+00:00"))
            except ValueError:
                print_err(
                    f"Package '{name}' released_at '{released_at}' is not a valid ISO 8601 timestamp"
                )
                errors += 1

    return errors


def validate_pr_index_sync(index):
    errors = 0
    changed = _get_changed_paths()

    if not changed["packages"]:
        print_info("No package directories changed in this PR")
        return 0

    print_info(f"Changed package directories: {sorted(changed['packages'])}")

    if not changed["index"]:
        print_err(
            "package-index.yaml was not updated. Any change to a package "
            "directory must be reflected in the index (version, released_at, updated_at, etc.)"
        )
        errors += 1

    base_index = _load_base_index()
    if base_index is None:
        print_info("Could not load base package-index.yaml; skipping version-bump checks")
        return errors

    base_packages = {p.get("name"): p for p in base_index.get("packages", [])}
    current_packages = {p.get("name"): p for p in index.get("packages", [])}

    for name in changed["packages"]:
        current = current_packages.get(name)
        base = base_packages.get(name)

        if current is None:
            print_err(
                f"Changed package directory 'packages/{name}' is not registered "
                "in the current package-index.yaml"
            )
            errors += 1
            continue

        if base is None:
            print_ok(f"Package '{name}' is new in this PR")
            continue

        if str(base.get("version")) == str(current.get("version")):
            print_err(
                f"Package '{name}' was modified but its version was not bumped: "
                f"{base.get('version')} -> {current.get('version')}"
            )
            errors += 1
        else:
            print_ok(
                f"Package '{name}' version bumped: {base.get('version')} -> {current.get('version')}"
            )

    return errors


def main():
    print_info("Validating registry structure...")

    index_path = os.path.join(REPO_ROOT, "package-index.yaml")
    if not os.path.exists(index_path):
        print_err("package-index.yaml not found")
        return 1

    try:
        with open(index_path, "r", encoding="utf-8") as f:
            index = yaml.safe_load(f)
    except Exception as exc:
        print_err(f"Failed to parse package-index.yaml: {exc}")
        return 1

    errors = 0
    errors += validate_index_header(index)
    errors += validate_index_packages(index)

    # Reuse the per-package manifest validation from validate_packages.py.
    print_info("Running per-package manifest validation...")
    if not validate_registry():
        errors += 1

    # PR-specific checks (only when a base ref is provided by the environment).
    if os.environ.get("GITHUB_BASE_REF"):
        print_info("Running PR-specific index-sync checks...")
        errors += validate_pr_index_sync(index)

    if errors > 0:
        print_err(f"Registry structure validation failed with {errors} error(s).")
        return 1

    print_ok("Registry structure is valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
