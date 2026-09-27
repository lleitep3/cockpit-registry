#!/bin/bash
# cockpit-package-builder registry validate
# Validates an AICockpit package registry.

set -uo pipefail

show_usage() {
    echo "Usage: cockpit-builder registry validate <registry-path>"
}

REGISTRY_PATH="${1:-}"
if [[ -z "${REGISTRY_PATH}" ]]; then
    echo "Error: registry path is required" >&2
    show_usage >&2
    exit 1
fi

if [[ ! -d "${REGISTRY_PATH}" ]]; then
    echo "Error: not a directory: ${REGISTRY_PATH}" >&2
    exit 1
fi

INDEX_PATH="${REGISTRY_PATH}/package-index.yaml"
if [[ ! -f "${INDEX_PATH}" ]]; then
    echo "Error: package-index.yaml not found in ${REGISTRY_PATH}" >&2
    exit 1
fi

# Prefer registry's own validator script if available
if [[ -f "${REGISTRY_PATH}/scripts/validate_packages.py" ]]; then
    if python3 "${REGISTRY_PATH}/scripts/validate_packages.py"; then
        exit 0
    else
        exit 1
    fi
fi

# Fallback to embedded Python validation
python3 - "${REGISTRY_PATH}" "${INDEX_PATH}" <<'PY'
import os
import sys
import yaml

repo_root = sys.argv[1]
index_path = sys.argv[2]
errors = 0

def err(msg):
    global errors
    print(f"  ✗ {msg}", file=sys.stderr)
    errors += 1

def ok(msg):
    print(f"  ✓ {msg}")

print(f"=== Validating registry: {repo_root} ===")

with open(index_path, 'r', encoding='utf-8') as f:
    index = yaml.safe_load(f)

if not isinstance(index, dict):
    err("package-index.yaml must be a YAML mapping")
    sys.exit(1)

metadata = index.get("metadata", {})
total_declared = metadata.get("total_packages")
packages = index.get("packages", [])

if not isinstance(packages, list):
    err("'packages' must be a list")
    sys.exit(1)

ok(f"package-index.yaml loaded: {len(packages)} packages declared")

if total_declared is not None and len(packages) != total_declared:
    err(f"metadata.total_packages ({total_declared}) does not match list length ({len(packages)})")

registered_paths = set()
for pkg in packages:
    name = pkg.get("name")
    version = pkg.get("version")
    path = pkg.get("path")

    if not name or not version or not path:
        err(f"package entry missing required fields: {pkg}")
        continue

    registered_paths.add(path)
    pkg_dir = os.path.join(repo_root, path)

    if not os.path.isdir(pkg_dir):
        err(f"package directory not found: {path}")
        continue

    manifest_path = os.path.join(pkg_dir, "cockpit-package.yml")
    if not os.path.exists(manifest_path):
        err(f"cockpit-package.yml missing for {name}")
        continue

    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = yaml.safe_load(f)
    except Exception as e:
        err(f"failed to parse manifest for {name}: {e}")
        continue

    if not isinstance(manifest, dict):
        err(f"manifest for {name} must be a mapping")
        continue

    if manifest.get("name") != name:
        err(f"name mismatch: index '{name}' vs manifest '{manifest.get('name')}'")

    if str(manifest.get("version")) != str(version):
        err(f"version mismatch for {name}: index '{version}' vs manifest '{manifest.get('version')}'")

    ok(f"package '{name}' ({version}) validated")

packages_root = os.path.join(repo_root, "packages")
if os.path.isdir(packages_root):
    for entry in os.listdir(packages_root):
        entry_path = os.path.join(packages_root, entry)
        if not os.path.isdir(entry_path) or entry.startswith("."):
            continue
        if not os.path.exists(os.path.join(entry_path, "cockpit-package.yml")):
            continue
        registered_path = f"packages/{entry}"
        if registered_path not in registered_paths:
            err(f"orphan package not registered: packages/{entry}")

print()
if errors == 0:
    print("✓ Registry validation passed")
    sys.exit(0)
else:
    print(f"✗ Registry validation failed with {errors} error(s)", file=sys.stderr)
    sys.exit(1)
PY
