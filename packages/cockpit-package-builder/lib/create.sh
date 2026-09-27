#!/bin/bash
# cockpit-package-builder create
# Scaffolds a new AICockpit package from the default boilerplate.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PACKAGE_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
BOILERPLATE_DIR="${PACKAGE_DIR}/boilerplates/default"

DEFAULT_OUTPUT_DIR="${HOME}/.cockpit/local-registry"

show_usage() {
    echo "Usage: cockpit-builder create <package-name> [output-path]"
    echo ""
    echo "Creates a new AICockpit package from the default boilerplate."
    echo "If output-path is omitted, the package is created under:"
    echo "  ${DEFAULT_OUTPUT_DIR}"
}

PACKAGE_NAME="${1:-}"
if [[ -z "${PACKAGE_NAME}" ]]; then
    echo "Error: package name is required" >&2
    show_usage >&2
    exit 1
fi

if [[ ! "${PACKAGE_NAME}" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]]; then
    echo "Error: package name must be lowercase letters, numbers, and hyphens only" >&2
    exit 1
fi

OUTPUT_DIR="${2:-${DEFAULT_OUTPUT_DIR}}"
TARGET_DIR="${OUTPUT_DIR}/${PACKAGE_NAME}"

if [[ -e "${TARGET_DIR}" ]]; then
    echo "Error: target directory already exists: ${TARGET_DIR}" >&2
    exit 1
fi

if [[ ! -d "${BOILERPLATE_DIR}" ]]; then
    echo "Error: boilerplate not found: ${BOILERPLATE_DIR}" >&2
    exit 1
fi

mkdir -p "${TARGET_DIR}"
cp -r "${BOILERPLATE_DIR}/." "${TARGET_DIR}/"

# Rename placeholders
find "${TARGET_DIR}" -type f -exec sed -i \
    -e "s/{PKG_NAME}/${PACKAGE_NAME}/g" \
    -e "s/{PKG_AUTHOR}/AICockpit/g" \
    -e "s/{PKG_DATE}/$(date -u +%Y-%m-%d)/g" \
    {} +

# Rename skill directory from {PKG_NAME} to actual name
if [[ -d "${TARGET_DIR}/skills/{PKG_NAME}" ]]; then
    mv "${TARGET_DIR}/skills/{PKG_NAME}" "${TARGET_DIR}/skills/${PACKAGE_NAME}"
fi

# Rename bin script from {PKG_NAME} to actual name
if [[ -f "${TARGET_DIR}/bin/{PKG_NAME}" ]]; then
    mv "${TARGET_DIR}/bin/{PKG_NAME}" "${TARGET_DIR}/bin/${PACKAGE_NAME}"
fi

# Make scripts executable
chmod +x "${TARGET_DIR}/bin/${PACKAGE_NAME}" 2>/dev/null || true
chmod +x "${TARGET_DIR}/lib/command.sh" 2>/dev/null || true
chmod +x "${TARGET_DIR}/bin/configure" 2>/dev/null || true
chmod +x "${TARGET_DIR}/bin/validate" 2>/dev/null || true
chmod +x "${TARGET_DIR}/tests/run_test.sh" 2>/dev/null || true

# Validate the generated package
"${SCRIPT_DIR}/validate.sh" "${TARGET_DIR}" || {
    echo "Warning: generated package validation produced warnings/errors above" >&2
}

echo ""
echo "=== Package created ==="
echo "Name: ${PACKAGE_NAME}"
echo "Location: ${TARGET_DIR}"
echo ""
echo "Next steps:"
echo "  1. Edit ${TARGET_DIR}/cockpit-package.yml"
echo "  2. Implement ${TARGET_DIR}/lib/command.sh"
echo "  3. Add tests in ${TARGET_DIR}/tests/run_test.sh"
echo "  4. Validate with: cockpit cockpit-builder validate ${TARGET_DIR}"
echo "  5. Test locally with: cp -r ${TARGET_DIR} ~/.cockpit/packages/ && cockpit deploy"
echo "========================"
