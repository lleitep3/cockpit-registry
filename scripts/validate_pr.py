#!/usr/bin/env python3
"""
Validate a pull request against contribution rules for an AICockpit package registry.
"""

import os
import re
import subprocess
import sys
import yaml

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX_PATH = os.path.join(REPO_ROOT, "package-index.yaml")


def error(msg):
    print(f"\033[91mERROR: {msg}\033[0m", file=sys.stderr)


def info(msg):
    print(f"\033[94mINFO: {msg}\033[0m")


def ok(msg):
    print(f"\033[92mOK: {msg}\033[0m")


def run_git(args):
    result = subprocess.run(
        ["git", "-C", REPO_ROOT] + args,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def _all_package_names(index):
    return {pkg.get("name") for pkg in index.get("packages", []) if pkg.get("name")}


def _package_name_from_path(path, package_names):
    """Map a changed path to a package name based on the package index."""
    path = path.strip("/")
    if not path:
        return None
    parts = path.split("/")

    # Standard layout: packages/<package-name>/...
    if len(parts) >= 2 and parts[0] == "packages":
        return parts[1]

    # Legacy / moved layout: <package-name>/... at repo root
    if len(parts) > 1 and parts[0] in package_names:
        return parts[0]

    return None


def get_changed_package_dirs():
    base = os.environ.get("GITHUB_BASE_REF", "main")
    try:
        diff = run_git(["diff", f"origin/{base}...HEAD", "--name-status"])
    except subprocess.CalledProcessError:
        diff = run_git(["diff", "main...HEAD", "--name-status"])

    index = load_index(INDEX_PATH)
    package_names = _all_package_names(index)

    # Collect every status that touches each package directory.
    per_package_statuses = {}
    for line in diff.splitlines():
        line = line.strip()
        if not line:
            continue

        parts = line.split("\t")
        if not parts:
            continue

        status = parts[0]

        if status.startswith("R"):
            # Rename lines: status, old_path, new_path
            if len(parts) < 3:
                continue
            paths = [parts[1], parts[2]]
        else:
            paths = [parts[1]] if len(parts) >= 2 else []

        for path in paths:
            pkg_name = _package_name_from_path(path, package_names)
            if pkg_name is None:
                continue
            per_package_statuses.setdefault(pkg_name, set()).add(status)

    # A package is considered "modified" only if at least one of its changes is
    # not a pure rename (R100). Pure renames or whole-directory moves do not
    # count as content changes for the "one package per PR" rule.
    changed = {
        pkg
        for pkg, statuses in per_package_statuses.items()
        if any(not s.startswith("R100") for s in statuses)
    }
    return changed


def get_commit_messages():
    base = os.environ.get("GITHUB_BASE_REF", "main")
    try:
        log = run_git(["log", f"origin/{base}...HEAD", "--pretty=format:%s"])
    except subprocess.CalledProcessError:
        log = run_git(["log", "main...HEAD", "--pretty=format:%s"])
    return [msg.strip() for msg in log.splitlines() if msg.strip()]


def classify_bump(commits):
    has_breaking = any(
        re.search(r"^\w+!:|BREAKING CHANGE", msg) or "breaking" in msg.lower()
        for msg in commits
    )
    if has_breaking:
        return "major"

    has_feat = any(
        re.search(r"^feat(?:\([^)]*\))?!?:", msg) or "feat" in msg.lower()
        for msg in commits
    )
    if has_feat:
        return "minor"

    has_fix = any(
        re.search(r"^fix(?:\([^)]*\))?!?:", msg) or "fix" in msg.lower()
        for msg in commits
    )
    if has_fix:
        return "patch"

    return None


def parse_version(version):
    match = re.match(r"^(\d+)\.(\d+)\.(\d+)", str(version))
    if not match:
        raise ValueError(f"Invalid semver version: {version}")
    return (int(match.group(1)), int(match.group(2)), int(match.group(3)))


def compare_versions(old, new):
    if old == new:
        return None
    if new[0] > old[0]:
        return "major"
    if new[0] == old[0] and new[1] > old[1]:
        return "minor"
    if new[0] == old[0] and new[1] == old[1] and new[2] > old[2]:
        return "patch"
    return "invalid"


def load_index(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main():
    errors = 0

    info("Checking changed packages in PR...")
    changed_packages = get_changed_package_dirs()

    if not changed_packages:
        info("No package changes detected.")
        return 0

    if len(changed_packages) > 1:
        error(
            f"PR modifies {len(changed_packages)} packages: {sorted(changed_packages)}. "
            "Only one package is allowed per PR."
        )
        errors += 1

    package_name = sorted(changed_packages)[0]
    info(f"Detected package change: {package_name}")

    base = os.environ.get("GITHUB_BASE_REF", "main")
    try:
        old_index_content = run_git(["show", f"origin/{base}:package-index.yaml"])
        old_index = yaml.safe_load(old_index_content)
    except subprocess.CalledProcessError:
        try:
            old_index_content = run_git(["show", "main:package-index.yaml"])
            old_index = yaml.safe_load(old_index_content)
        except subprocess.CalledProcessError:
            old_index = {"packages": []}

    old_version = None
    for pkg in old_index.get("packages", []):
        if pkg.get("name") == package_name:
            old_version = str(pkg.get("version", ""))
            break

    if not old_version:
        info(f"Package '{package_name}' is new; no version bump check needed.")
        ok("New package accepted")
        return 0 if errors == 0 else 1

    new_index = load_index(INDEX_PATH)
    new_version = None
    for pkg in new_index.get("packages", []):
        if pkg.get("name") == package_name:
            new_version = str(pkg.get("version", ""))
            break

    if not new_version:
        error(f"Package '{package_name}' not found in current package-index.yaml")
        return 1

    info(f"Version change: {old_version} -> {new_version}")

    try:
        old_v = parse_version(old_version)
        new_v = parse_version(new_version)
    except ValueError as e:
        error(str(e))
        return 1

    bump = compare_versions(old_v, new_v)
    if bump is None:
        error(
            f"Package '{package_name}' was updated but version was not bumped: {old_version} -> {new_version}"
        )
        errors += 1
    elif bump == "invalid":
        error(
            f"Package '{package_name}' version was downgraded or changed unexpectedly: {old_version} -> {new_version}"
        )
        errors += 1
    else:
        ok(f"Version bumped: {bump} ({old_version} -> {new_version})")

    commits = get_commit_messages()
    if not commits:
        error("No commits found in PR; cannot validate bump scope.")
        errors += 1
    else:
        required_bump = classify_bump(commits)
        info(f"Commit scope suggests bump: {required_bump or 'none/patch'}")
        if required_bump and bump != required_bump:
            hierarchy = {"patch": 0, "minor": 1, "major": 2}
            if hierarchy.get(bump, 0) < hierarchy.get(required_bump, 0):
                error(
                    f"Version bump ({bump}) does not match PR scope ({required_bump}). "
                    f"Commits: {commits}"
                )
                errors += 1
            else:
                ok(f"Bump ({bump}) covers required scope ({required_bump})")
        else:
            ok("Version bump matches PR scope")

    if errors > 0:
        error(f"PR validation failed with {errors} error(s).")
        return 1

    ok("PR validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
