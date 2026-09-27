#!/bin/bash
# cockpit-package-builder registry create
# Creates a new AICockpit package registry repository.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PACKAGE_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

show_usage() {
    echo "Usage: cockpit-builder registry create <path> [--remote URL]"
    echo ""
    echo "Creates a new AICockpit package registry at the given path."
    echo "Options:"
    echo "  --remote URL    Add a Git remote and optionally push initial commit"
}

parse_args() {
    local -n path_ref=$1
    local -n remote_ref=$2
    shift 2

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --remote)
                if [[ -n "${2:-}" && "${2:-}" != --* ]]; then
                    remote_ref="$2"
                    shift 2
                else
                    echo "Error: --remote requires a value" >&2
                    exit 1
                fi
                ;;
            --help|-h)
                show_usage
                exit 0
                ;;
            *)
                if [[ -z "${path_ref}" ]]; then
                    path_ref="$1"
                    shift
                else
                    echo "Error: unknown argument '$1'" >&2
                    show_usage >&2
                    exit 1
                fi
                ;;
        esac
    done
}

REGISTRY_PATH=""
REMOTE_URL=""
parse_args REGISTRY_PATH REMOTE_URL "$@"

if [[ -z "${REGISTRY_PATH}" ]]; then
    echo "Error: registry path is required" >&2
    show_usage >&2
    exit 1
fi

REGISTRY_PATH="$(cd "$(dirname "${REGISTRY_PATH}")" && pwd)/$(basename "${REGISTRY_PATH}")"

if [[ -e "${REGISTRY_PATH}" && -n "$(ls -A "${REGISTRY_PATH}" 2>/dev/null)" ]]; then
    echo "Error: target directory already exists and is not empty: ${REGISTRY_PATH}" >&2
    exit 1
fi

mkdir -p "${REGISTRY_PATH}/packages"
mkdir -p "${REGISTRY_PATH}/.github/workflows"
mkdir -p "${REGISTRY_PATH}/docs"
mkdir -p "${REGISTRY_PATH}/scripts"
mkdir -p "${REGISTRY_PATH}/.githooks"

# Create .github/CODEOWNERS
cat > "${REGISTRY_PATH}/.github/CODEOWNERS" <<'EOF'
# Global fallback — anything without a specific owner defaults to the maintainer
* @lleitep3

# Core infrastructure and validation scripts are restricted to the maintainer
.github/ @lleitep3
scripts/ @lleitep3
EOF

# Create package-index.yaml
NOW=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
cat > "${REGISTRY_PATH}/package-index.yaml" <<EOF
# AICockpit Package Registry Index
version: "1.0"
name: "My AICockpit Registry"
description: "Package registry for AICockpit"
url: "${REMOTE_URL:-https://github.com/user/cockpit-registry}"
maintainer: "AICockpit"
maintainer_email: "team@aicockpit.dev"

# Last update timestamp
updated_at: "${NOW}"

# Registry metadata
metadata:
  total_packages: 0
  categories: []

# Packages in this registry
packages: []
EOF

# Create CONTRIBUTIONS.md
cp "${PACKAGE_DIR}/boilerplates/default/CONTRIBUTIONS.md" "${REGISTRY_PATH}/CONTRIBUTIONS.md" 2>/dev/null || true

# Create README.md
cat > "${REGISTRY_PATH}/README.md" <<'EOF'
# AICockpit Package Registry

This repository hosts AICockpit packages.

## Structure

```
.
├── package-index.yaml       # Registry index
├── packages/                # Package directory root
│   └── [package-name]/
│       ├── cockpit-package.yml
│       └── ...
├── .github/
│   └── workflows/
│       └── validate-packages.yml
└── docs/                    # Optional documentation
```

## Adding a package

```bash
cockpit cockpit-builder publish /path/to/package /path/to/this/registry
```

## Validating the registry

```bash
cockpit cockpit-builder registry validate /path/to/this/registry
```

## Validation

A GitHub Actions workflow validates every PR against the registry conventions.
EOF

# Create .gitignore
cat > "${REGISTRY_PATH}/.gitignore" <<'EOF'
# IDE
.idea/
.vscode/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Python
__pycache__/
*.pyc

# Node
node_modules/
EOF

# Create validation workflow
cat > "${REGISTRY_PATH}/.github/workflows/validate-packages.yml" <<'EOF'
name: Validate Packages

on:
  pull_request:
    branches:
      - main
  push:
    branches:
      - main

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install pyyaml

      - name: Validate registry
        run: |
          ./scripts/validate-registry.sh

  validate-pr:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install pyyaml

      - name: Validate PR
        run: |
          ./scripts/validate-pr.sh
EOF

# Create validation scripts
cat > "${REGISTRY_PATH}/scripts/validate_packages.py" <<'EOF'
#!/usr/bin/env python3
import os
import sys
import yaml

def print_err(msg):
    print(f"\033[91mERROR: {msg}\033[0m", file=sys.stderr)

def print_ok(msg):
    print(f"\033[92mOK: {msg}\033[0m")

def print_info(msg):
    print(f"\033[94mINFO: {msg}\033[0m")

def validate_registry():
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    index_path = os.path.join(repo_root, "package-index.yaml")

    if not os.path.exists(index_path):
        print_err(f"package-index.yaml not found at {index_path}")
        return False

    print_info(f"Loading package-index.yaml from {index_path}...")
    try:
        with open(index_path, 'r', encoding='utf-8') as f:
            index = yaml.safe_load(f)
    except Exception as e:
        print_err(f"Failed to parse package-index.yaml: {e}")
        return False

    if not isinstance(index, dict):
        print_err("package-index.yaml must be a YAML mapping/dictionary")
        return False

    metadata = index.get("metadata", {})
    total_packages_declared = metadata.get("total_packages")
    packages = index.get("packages", [])

    if not isinstance(packages, list):
        print_err("'packages' in package-index.yaml must be a list")
        return False

    print_info(f"Registry declared packages: {len(packages)} (metadata total: {total_packages_declared})")

    if len(packages) != total_packages_declared:
        print_err(f"Metadata total_packages ({total_packages_declared}) does not match actual packages list length ({len(packages)})")
        return False

    registered_paths = set()
    errors = 0

    for pkg in packages:
        name = pkg.get("name")
        version = pkg.get("version")
        path = pkg.get("path")

        if not name or not version or not path:
            print_err(f"Package definition missing required fields (name, version, path): {pkg}")
            errors += 1
            continue

        registered_paths.add(path)
        pkg_dir = os.path.join(repo_root, path)

        if not os.path.isdir(pkg_dir):
            print_err(f"Package directory not found: {path} (resolved: {pkg_dir})")
            errors += 1
            continue

        manifest_path = os.path.join(pkg_dir, "cockpit-package.yml")
        if not os.path.exists(manifest_path):
            print_err(f"cockpit-package.yml not found for package {name} at {manifest_path}")
            errors += 1
            continue

        print_info(f"Validating manifest for '{name}'...")
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = yaml.safe_load(f)
        except Exception as e:
            print_err(f"Failed to parse cockpit-package.yml for {name}: {e}")
            errors += 1
            continue

        if not isinstance(manifest, dict):
            print_err(f"Manifest for {name} must be a YAML mapping")
            errors += 1
            continue

        manifest_name = manifest.get("name")
        manifest_version = str(manifest.get("version"))

        if manifest_name != name:
            print_err(f"Package name mismatch: index has '{name}', manifest has '{manifest_name}'")
            errors += 1

        if manifest_version != str(version):
            print_err(f"Package version mismatch for '{name}': index has '{version}', manifest has '{manifest_version}'")
            errors += 1

        features = manifest.get("features", {})
        if isinstance(features, dict):
            for feature_type, feature_list in features.items():
                if not isinstance(feature_list, list):
                    continue
                for item in feature_list:
                    if isinstance(item, dict) and "path" in item:
                        fpath = item["path"]
                        if os.path.isabs(fpath):
                            print_err(f"Package '{name}' declares feature '{feature_type}' with absolute path '{fpath}' which is not allowed")
                            errors += 1
                        else:
                            full_fpath = os.path.normpath(os.path.join(pkg_dir, fpath))
                            if not os.path.exists(full_fpath):
                                print_err(f"Package '{name}' declares feature '{feature_type}' with path '{fpath}', but it does not exist at '{full_fpath}'")
                                errors += 1
                            else:
                                print_ok(f"  Feature '{feature_type}' path verified: {fpath}")

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
                print_err(f"Orphan package directory found: 'packages/{entry}' contains cockpit-package.yml but is not registered in package-index.yaml")
                errors += 1

    if errors > 0:
        print_err(f"Validation failed with {errors} errors.")
        return False

    print_ok("All packages and index validated successfully!")
    return True

if __name__ == "__main__":
    success = validate_registry()
    sys.exit(0 if success else 1)
EOF
chmod +x "${REGISTRY_PATH}/scripts/validate_packages.py"
cp "${PACKAGE_DIR}/lib/validate_pr.py" "${REGISTRY_PATH}/scripts/validate_pr.py"
chmod +x "${REGISTRY_PATH}/scripts/validate_pr.py"

# Create validate-registry.sh shell entrypoint
cat > "${REGISTRY_PATH}/scripts/validate-registry.sh" <<'EOF'
#!/bin/bash
# Validate the registry structure and all packages.
# Usage: ./scripts/validate-registry.sh
set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "${SCRIPT_DIR}/validate_packages.py" "$@"
EOF
chmod +x "${REGISTRY_PATH}/scripts/validate-registry.sh"

# Create validate-pr.sh shell entrypoint
cat > "${REGISTRY_PATH}/scripts/validate-pr.sh" <<'EOF'
#!/bin/bash
# Validate a pull request against registry contribution rules.
# Usage: ./scripts/validate-pr.sh
# Optional env: GITHUB_BASE_REF (defaults to main)
set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "${SCRIPT_DIR}/validate_pr.py" "$@"
EOF
chmod +x "${REGISTRY_PATH}/scripts/validate-pr.sh"

# Create .githooks/pre-commit hook
cat > "${REGISTRY_PATH}/.githooks/pre-commit" <<'EOF'
#!/bin/bash
# Pre-commit hook: validate registry before every commit.
# Optionally validates PR rules when on a non-main branch.
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

echo "Running registry validation..."
if ! "${REPO_ROOT}/scripts/validate-registry.sh"; then
    echo "Pre-commit: registry validation failed. Commit aborted." >&2
    exit 1
fi

CURRENT_BRANCH="$(git -C "${REPO_ROOT}" rev-parse --abbrev-ref HEAD 2>/dev/null || true)"
if [[ -n "${CURRENT_BRANCH}" && "${CURRENT_BRANCH}" != "main" && "${CURRENT_BRANCH}" != "HEAD" ]]; then
    echo "Running PR validation (branch: ${CURRENT_BRANCH})..."
    if ! "${REPO_ROOT}/scripts/validate-pr.sh" 2>/dev/null; then
        echo "Pre-commit: PR validation failed. Commit aborted." >&2
        exit 1
    fi
fi

exit 0
EOF
chmod +x "${REGISTRY_PATH}/.githooks/pre-commit"

# Create scripts/install-hooks.sh
cat > "${REGISTRY_PATH}/scripts/install-hooks.sh" <<'EOF'
#!/bin/bash
# Configure git to use the repository's .githooks directory.
# Run once after cloning: ./scripts/install-hooks.sh
set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
git -C "${REPO_ROOT}" config core.hooksPath .githooks
echo "Git hooks installed: core.hooksPath set to .githooks"
EOF
chmod +x "${REGISTRY_PATH}/scripts/install-hooks.sh"

cd "${REGISTRY_PATH}" || exit 1

if ! git rev-parse --git-dir >/dev/null 2>&1; then
    git init
    git branch -m main
fi

if [[ -n "${REMOTE_URL}" ]]; then
    if ! git remote | grep -q origin; then
        git remote add origin "${REMOTE_URL}"
    else
        git remote set-url origin "${REMOTE_URL}"
    fi
fi

git add .
if git diff --cached --quiet; then
    echo "No changes to commit"
else
    git commit -m "chore(registry): initialize package registry structure"
fi

if [[ -n "${REMOTE_URL}" ]]; then
    if git remote | grep -q origin; then
        echo ""
        echo "Pushing initial commit to ${REMOTE_URL}..."
        git push -u origin main || echo "Warning: push failed. You may need to push manually." >&2
    fi
fi

echo ""
echo "=== Registry created ==="
echo "Path: ${REGISTRY_PATH}"
if [[ -n "${REMOTE_URL}" ]]; then
    echo "Remote: ${REMOTE_URL}"
fi
echo ""
echo "Next steps:"
echo "  1. Customize package-index.yaml and README.md"
echo "  2. Install git hooks:  ${REGISTRY_PATH}/scripts/install-hooks.sh"
echo "  3. Validate registry:  ${REGISTRY_PATH}/scripts/validate-registry.sh"
echo "  4. Publish packages:   cockpit cockpit-builder publish <package-path> ${REGISTRY_PATH}"
echo "========================"
