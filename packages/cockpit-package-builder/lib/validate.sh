#!/bin/bash
# cockpit-package-builder validate
# Validates an AICockpit package against official conventions.

set -uo pipefail

show_usage() {
    echo "Usage: cockpit-builder validate <package-path>"
}

PKG_DIR="${1:-}"
if [[ -z "${PKG_DIR}" ]]; then
    echo "Error: package path is required" >&2
    show_usage >&2
    exit 1
fi

if [[ ! -d "${PKG_DIR}" ]]; then
    echo "Error: not a directory: ${PKG_DIR}" >&2
    exit 1
fi

MANIFEST="${PKG_DIR}/cockpit-package.yml"

ERRORS=0
error() {
    echo "  ✗ $1" >&2
    ERRORS=$((ERRORS + 1))
}

ok() {
    echo "  ✓ $1"
}

echo "=== Validating package: ${PKG_DIR} ==="

if [[ -f "${MANIFEST}" ]]; then
    ok "cockpit-package.yml exists"
else
    error "cockpit-package.yml missing"
fi

if command -v python3 >/dev/null 2>&1 && python3 -c "import yaml" >/dev/null 2>&1; then
    if python3 - "${MANIFEST}" <<'PY'
import sys, yaml, re
path = sys.argv[1]
with open(path, 'r') as f:
    m = yaml.safe_load(f)
required = ['name', 'version', 'description', 'author', 'license', 'type', 'requirements', 'features', 'installation']
for field in required:
    if not m.get(field):
        print(f"Missing required field: {field}", file=sys.stderr)
        sys.exit(1)
if not re.match(r'^\d+\.\d+\.\d+', str(m.get('version', ''))):
    print("Version must follow semver MAJOR.MINOR.PATCH", file=sys.stderr)
    sys.exit(1)
if not m.get('requirements', {}).get('cockpit'):
    print("Missing requirements.cockpit", file=sys.stderr)
    sys.exit(1)
features = m.get('features', {})
has_feature = any(features.get(k) for k in ['agents', 'skills', 'modules', 'workflows', 'kb'])
if not has_feature:
    print("At least one feature must be defined", file=sys.stderr)
    sys.exit(1)
installation = m.get('installation', {})
if not installation.get('supported_providers'):
    print("Missing installation.supported_providers", file=sys.stderr)
    sys.exit(1)
if not installation.get('provider_features'):
    print("Missing installation.provider_features", file=sys.stderr)
    sys.exit(1)
PY
    then
        ok "manifest structure is valid"
    else
        error "manifest validation failed"
        exit 1
    fi
else
    error "python3 and PyYAML are required; install dependencies in your package runtime"
    exit 1
fi

# Validate feature paths
if [[ -f "${MANIFEST}" ]]; then
    python3 - "${PKG_DIR}" "${MANIFEST}" <<'PY' || error "feature path validation failed"
import sys, os, yaml
pkg_dir = sys.argv[1]
manifest_path = sys.argv[2]
with open(manifest_path, 'r') as f:
    m = yaml.safe_load(f)
features = m.get('features', {})
exit_code = 0
for ftype, flist in features.items():
    if not isinstance(flist, list):
        continue
    for item in flist:
        if isinstance(item, dict) and 'path' in item:
            fpath = item['path']
            if os.path.isabs(fpath):
                print(f"  ✗ Feature {ftype} has absolute path: {fpath}", file=sys.stderr)
                exit_code = 1
                continue
            full = os.path.realpath(os.path.join(pkg_dir, fpath))
            root = os.path.realpath(pkg_dir)
            if os.path.commonpath([root, full]) != root:
                print(f"  ✗ Feature {ftype} escapes package: {fpath}", file=sys.stderr)
                exit_code = 1
                continue
            if not os.path.exists(full):
                print(f"  ✗ Feature {ftype} path missing: {fpath}", file=sys.stderr)
                exit_code = 1
            else:
                print(f"  ✓ Feature {ftype} path verified: {fpath}")
sys.exit(exit_code)
PY
fi

# Check required documentation
if [[ -f "${PKG_DIR}/README.md" ]]; then
    ok "README.md exists"
else
    error "README.md missing"
fi

# Check CLI scripts
if [[ -d "${PKG_DIR}/bin" ]]; then
    ok "bin/ directory exists"
else
    error "bin/ directory missing"
fi

# Check if main module script is executable
if [[ -f "${MANIFEST}" ]]; then
    MODULE_PATH=$(python3 - "${MANIFEST}" <<'PY'
import sys, yaml
with open(sys.argv[1], 'r') as f:
    m = yaml.safe_load(f)
for item in m.get('features', {}).get('modules', []):
    print(item.get('path', ''))
    break
PY
    )
    if [[ -n "${MODULE_PATH}" ]]; then
        SCRIPT="${PKG_DIR}/${MODULE_PATH}"
        if [[ -x "${SCRIPT}" ]]; then
            ok "module script is executable: ${MODULE_PATH}"
        else
            error "module script not executable: ${MODULE_PATH}"
        fi
    fi
fi

# Validate bash syntax of all .sh scripts
while IFS= read -r -d '' script; do
    if bash -n "${script}" 2>/dev/null; then
        ok "bash syntax OK: $(basename "${script}")"
    else
        error "bash syntax error: ${script}"
    fi
done < <(find "${PKG_DIR}" -type f \( -name "*.sh" -o -name "validate" -o -name "configure" \) -print0)

echo ""
if [[ ${ERRORS} -eq 0 ]]; then
    echo "✓ Package validation passed"
    exit 0
else
    echo "✗ Package validation failed with ${ERRORS} error(s)" >&2
    exit 1
fi
