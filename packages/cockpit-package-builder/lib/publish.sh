#!/bin/bash
# cockpit-package-builder publish
# Publishes a package into an AICockpit registry.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

show_usage() {
    echo "Usage: cockpit-builder publish <package-path> <registry-path>"
    echo ""
    echo "Publishes a package into a registry:"
    echo "  1. Validates the package"
    echo "  2. Copies it to registry/packages/<package-name>"
    echo "  3. Updates package-index.yaml"
    echo "  4. If the registry has a remote, creates a feature branch and opens a PR"
}

PACKAGE_PATH="${1:-}"
REGISTRY_PATH="${2:-}"

if [[ -z "${PACKAGE_PATH}" || -z "${REGISTRY_PATH}" ]]; then
    echo "Error: package path and registry path are required" >&2
    show_usage >&2
    exit 1
fi

if [[ ! -d "${PACKAGE_PATH}" ]]; then
    echo "Error: package path is not a directory: ${PACKAGE_PATH}" >&2
    exit 1
fi

if [[ ! -f "${PACKAGE_PATH}/cockpit-package.yml" ]]; then
    echo "Error: cockpit-package.yml not found in ${PACKAGE_PATH}" >&2
    exit 1
fi

if [[ ! -d "${REGISTRY_PATH}" ]]; then
    echo "Error: registry path is not a directory: ${REGISTRY_PATH}" >&2
    exit 1
fi

if [[ ! -f "${REGISTRY_PATH}/package-index.yaml" ]]; then
    echo "Error: package-index.yaml not found in ${REGISTRY_PATH}" >&2
    exit 1
fi

# Validate the package
"${SCRIPT_DIR}/validate.sh" "${PACKAGE_PATH}" || {
    echo "Error: package validation failed" >&2
    exit 1
}

# Read package name and version from manifest
PKG_NAME=$(python3 - "${PACKAGE_PATH}/cockpit-package.yml" <<'PY'
import sys, yaml
with open(sys.argv[1], 'r') as f:
    m = yaml.safe_load(f)
print(m.get('name', ''))
PY
)

PKG_VERSION=$(python3 - "${PACKAGE_PATH}/cockpit-package.yml" <<'PY'
import sys, yaml
with open(sys.argv[1], 'r') as f:
    m = yaml.safe_load(f)
print(m.get('version', ''))
PY
)

if [[ -z "${PKG_NAME}" || -z "${PKG_VERSION}" ]]; then
    echo "Error: could not read package name or version from manifest" >&2
    exit 1
fi

# Check if package already exists in registry
PKG_TARGET_DIR="${REGISTRY_PATH}/packages/${PKG_NAME}"
IS_UPDATE=false
if [[ -d "${PKG_TARGET_DIR}" ]]; then
    IS_UPDATE=true
    echo "Package '${PKG_NAME}' already exists in registry. Updating to ${PKG_VERSION}..."
else
    echo "Publishing new package '${PKG_NAME}' ${PKG_VERSION}..."
fi

# Copy package to registry
mkdir -p "${REGISTRY_PATH}/packages"
rm -rf "${PKG_TARGET_DIR}"
cp -r "${PACKAGE_PATH}" "${PKG_TARGET_DIR}"

# Update package-index.yaml
python3 - "${REGISTRY_PATH}" "${PKG_NAME}" "${PKG_VERSION}" <<'PY'
import sys, os, yaml, re
from datetime import datetime, timezone

registry_path = sys.argv[1]
name = sys.argv[2]
version = sys.argv[3]

index_path = os.path.join(registry_path, "package-index.yaml")
with open(index_path, 'r', encoding='utf-8') as f:
    index = yaml.safe_load(f)

# Determine repository URL
repo_url = None
if os.path.exists(os.path.join(registry_path, ".git")):
    import subprocess
    try:
        result = subprocess.run(
            ["git", "-C", registry_path, "remote", "get-url", "origin"],
            capture_output=True, text=True, check=True
        )
        repo_url = result.stdout.strip()
    except Exception:
        pass

if repo_url:
    # Normalize to HTTPS-ish browse URL
    repo_url = repo_url.rstrip('/')
    if repo_url.startswith("git@"):
        repo_url = re.sub(r"^git@([^:]+):(.+)\.git$", r"https://\1/\2", repo_url)
        repo_url = re.sub(r"^git@([^:]+):(.+)$", r"https://\1/\2", repo_url)
    elif repo_url.endswith(".git"):
        repo_url = repo_url[:-4]
    pkg_url = f"{repo_url}/tree/main/packages/{name}"
else:
    pkg_url = f"https://github.com/user/cockpit-registry/tree/main/packages/{name}"

# Read package manifest for metadata
manifest_path = os.path.join(registry_path, "packages", name, "cockpit-package.yml")
with open(manifest_path, 'r', encoding='utf-8') as f:
    manifest = yaml.safe_load(f)

features = []
for section in ['agents', 'skills', 'modules', 'rules', 'workflows', 'kb']:
    if manifest.get('features', {}).get(section):
        features.append(section)

installation = manifest.get('installation', {})

entry = {
    "name": name,
    "version": version,
    "description": manifest.get('description', ''),
    "author": manifest.get('author', ''),
    "license": manifest.get('license', ''),
    "category": manifest.get('category', ''),
    "tags": manifest.get('metadata', {}).get('tags', []),
    "path": f"packages/{name}",
    "url": pkg_url,
    "homepage": manifest.get('homepage', repo_url or ''),
    "repository": repo_url or manifest.get('repository', ''),
    "supported_providers": installation.get('supported_providers', []),
    "features": features,
    "requirements": manifest.get('requirements', {}),
    "installation_method": installation.get('method', 'copy'),
    "status": manifest.get('metadata', {}).get('status', 'stable'),
    "released_at": datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
}

packages = index.get('packages', [])
updated = False
for i, pkg in enumerate(packages):
    if pkg.get('name') == name:
        packages[i] = entry
        updated = True
        break

if not updated:
    packages.append(entry)

index['packages'] = packages
index['metadata'] = index.get('metadata', {})
index['metadata']['total_packages'] = len(packages)
index['updated_at'] = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

with open(index_path, 'w', encoding='utf-8') as f:
    yaml.dump(index, f, default_flow_style=False, sort_keys=False)

print(f"Updated {index_path} with package '{name}' {version}")
PY

# Validate the updated registry
"${SCRIPT_DIR}/registry_validate.sh" "${REGISTRY_PATH}" || {
    echo "Error: registry validation failed after publish" >&2
    exit 1
}

# Git operations if registry has a remote
if git -C "${REGISTRY_PATH}" rev-parse --git-dir >/dev/null 2>&1; then
    if git -C "${REGISTRY_PATH}" remote | grep -q origin; then
        REMOTE_URL=$(git -C "${REGISTRY_PATH}" remote get-url origin)
        echo ""
        echo "Remote detected: ${REMOTE_URL}"

        # Check for gh
        if command -v gh >/dev/null 2>&1; then
            BRANCH="feature/pkg-${PKG_NAME}"
            if [[ "${IS_UPDATE}" == true ]]; then
                BRANCH="feature/update-${PKG_NAME}-${PKG_VERSION}"
            fi

            cd "${REGISTRY_PATH}" || exit 1
            git checkout -b "${BRANCH}"
            git add "packages/${PKG_NAME}" package-index.yaml
            if [[ "${IS_UPDATE}" == true ]]; then
                git commit -m "feat(packages): update ${PKG_NAME} to ${PKG_VERSION}"
            else
                git commit -m "feat(packages): add ${PKG_NAME} ${PKG_VERSION}"
            fi
            git push -u origin "${BRANCH}"

            echo ""
            echo "Creating pull request..."
            gh pr create \
                --title "feat(packages): ${IS_UPDATE:+update }${PKG_NAME} ${PKG_VERSION}" \
                --body "$(cat <<EOF
## Summary

${IS_UPDATE:+Updates:New package} **${PKG_NAME}** ${PKG_VERSION} to the registry.

## Changes

- Added/updated \`packages/${PKG_NAME}\`
- Updated \`package-index.yaml\`

## Validation

- [x] Package manifest validated
- [x] Registry index validated
- [x] Feature paths verified

Generated with [cockpit-package-builder](https://github.com/lleitep3/aicockpit)
EOF
)"
            echo ""
            echo "Pull request created for branch ${BRANCH}"
        else
            echo ""
            echo "Remote detected but 'gh' CLI not found. Please commit and open PR manually."
            echo "Suggested branch: feature/pkg-${PKG_NAME}"
        fi
    fi
fi

echo ""
echo "=== Publish complete ==="
echo "Package: ${PKG_NAME} ${PKG_VERSION}"
echo "Registry: ${REGISTRY_PATH}/packages/${PKG_NAME}"
echo "========================"
