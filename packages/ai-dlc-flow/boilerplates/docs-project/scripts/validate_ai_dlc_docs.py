#!/usr/bin/env python3
"""Validate the minimum AI-DLC documentation contract."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


DOC_ROOTS = ("docs/", "process/", "requirements/", "architecture/", "experiments/")
REQUIRED_FILES = ("docs/ai-dlc/README.md", "docs/ai-dlc/backlog.md")


def changed_paths(root: Path) -> list[str]:
    base_ref = os.environ.get("GITHUB_BASE_REF")
    comparison = f"origin/{base_ref}...HEAD" if base_ref else "HEAD^...HEAD"
    result = subprocess.run(
        ["git", "-C", str(root), "diff", "--name-only", comparison],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return []
    return [line for line in result.stdout.splitlines() if line]


def is_document(path: str) -> bool:
    return path.endswith(".md") and (path == "README.md" or path.startswith(DOC_ROOTS))


def has_heading_and_status(content: str) -> bool:
    lines = content.splitlines()
    has_heading = any(line.startswith("# ") for line in lines)
    has_status = any("**Status:**" in line or line.startswith("Status:") for line in lines)
    return has_heading and has_status


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).is_file():
            errors.append(f"missing required AI-DLC file: {relative_path}")

    paths = changed_paths(root)
    if not paths:
        paths = [
            str(path.relative_to(root))
            for directory in DOC_ROOTS
            for path in (root / directory).rglob("*.md")
            if path.is_file()
        ]

    for relative_path in paths:
        if not is_document(relative_path):
            continue
        path = root / relative_path
        if not path.is_file():
            errors.append(f"changed document does not exist: {relative_path}")
            continue
        if relative_path.endswith("/README.md") or relative_path == "README.md":
            continue
        if not has_heading_and_status(path.read_text(encoding="utf-8")):
            errors.append(f"document needs a Markdown title and explicit Status: {relative_path}")

    return errors


def main() -> int:
    errors = validate(Path.cwd().resolve())
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("AI-DLC documentation validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
