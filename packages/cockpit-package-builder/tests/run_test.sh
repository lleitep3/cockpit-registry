#!/bin/bash
# cockpit-package-builder test runner

set -uo pipefail

PACKAGE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEST_OUTPUT="$(mktemp -d)"

PASS=0
FAIL=0

pass() {
    echo "  ✓ $1"
    PASS=$((PASS + 1))
}

fail() {
    echo "  ✗ $1" >&2
    FAIL=$((FAIL + 1))
}

cleanup() {
    rm -rf "${TEST_OUTPUT}"
}
trap cleanup EXIT

echo "=== cockpit-package-builder tests ==="

# Package structure
if [[ -f "${PACKAGE_DIR}/cockpit-package.yml" ]]; then
    pass "manifest exists"
else
    fail "manifest missing"
fi

if [[ -x "${PACKAGE_DIR}/bin/cockpit-builder" ]]; then
    pass "main script is executable"
else
    fail "main script not executable"
fi

if bash -n "${PACKAGE_DIR}/bin/cockpit-builder"; then
    pass "main script syntax OK"
else
    fail "main script syntax error"
fi

if bash -n "${PACKAGE_DIR}/lib/create.sh"; then
    pass "create.sh syntax OK"
else
    fail "create.sh syntax error"
fi

if bash -n "${PACKAGE_DIR}/lib/validate.sh"; then
    pass "validate.sh syntax OK"
else
    fail "validate.sh syntax error"
fi

if bash -n "${PACKAGE_DIR}/lib/configure.sh"; then
    pass "configure.sh syntax OK"
else
    fail "configure.sh syntax error"
fi

# Boilerplate exists
if [[ -d "${PACKAGE_DIR}/boilerplates/default" ]]; then
    pass "default boilerplate exists"
else
    fail "default boilerplate missing"
fi

for f in cockpit-package.yml README.md bin/{PKG_NAME} lib/command.sh bin/configure bin/validate skills/{PKG_NAME}/SKILL.md tests/run_test.sh; do
    if [[ -f "${PACKAGE_DIR}/boilerplates/default/${f}" ]]; then
        pass "boilerplate file exists: ${f}"
    else
        fail "boilerplate file missing: ${f}"
    fi
done

# Test create subcommand
echo ""
echo "Testing create subcommand..."
TEST_PKG="test-generated-pkg"
"${PACKAGE_DIR}/bin/cockpit-builder" create "${TEST_PKG}" "${TEST_OUTPUT}"
GENERATED_DIR="${TEST_OUTPUT}/${TEST_PKG}"

if [[ -d "${GENERATED_DIR}" ]]; then
    pass "generated package directory exists"
else
    fail "generated package directory missing"
fi

if [[ -f "${GENERATED_DIR}/cockpit-package.yml" ]]; then
    pass "generated manifest exists"
    if grep -q "name: \"${TEST_PKG}\"" "${GENERATED_DIR}/cockpit-package.yml"; then
        pass "generated manifest has correct name"
    else
        fail "generated manifest name incorrect"
    fi
else
    fail "generated manifest missing"
fi

if [[ -x "${GENERATED_DIR}/bin/${TEST_PKG}" ]]; then
    pass "generated main script is executable"
else
    fail "generated main script not executable"
fi

if [[ -d "${GENERATED_DIR}/skills/${TEST_PKG}" ]]; then
    pass "generated skill directory renamed correctly"
else
    fail "generated skill directory not renamed"
fi

# Test generated package hello command
if "${GENERATED_DIR}/bin/${TEST_PKG}" hello >/dev/null 2>&1; then
    pass "generated package hello command works"
else
    fail "generated package hello command failed"
fi

# Test validate subcommand on generated package
echo ""
echo "Testing validate subcommand..."
if "${PACKAGE_DIR}/bin/cockpit-builder" validate "${GENERATED_DIR}" >/dev/null 2>&1; then
    pass "validate subcommand passes on generated package"
else
    fail "validate subcommand failed on generated package"
fi

# Invalid fixtures must fail validation, not merely print an error.
cp -R "${GENERATED_DIR}" "${TEST_OUTPUT}/invalid-path"
# Append to features using YAML rather than relying on indentation context.
python3 - "${TEST_OUTPUT}/invalid-path/cockpit-package.yml" <<'PYTEST'
import sys, yaml
p=sys.argv[1]
with open(p) as f: m=yaml.safe_load(f)
m['features']['skills'].append({'name':'missing','path':'missing-resource'})
with open(p,'w') as f: yaml.safe_dump(m,f)
PYTEST
if "${PACKAGE_DIR}/bin/cockpit-builder" validate "${TEST_OUTPUT}/invalid-path" >/dev/null 2>&1; then
    fail "missing feature path was accepted"
else
    pass "missing feature path rejected"
fi
cp -R "${GENERATED_DIR}" "${TEST_OUTPUT}/invalid-shell"
printf 'if then\n' > "${TEST_OUTPUT}/invalid-shell/lib/broken.sh"
if "${PACKAGE_DIR}/bin/cockpit-builder" validate "${TEST_OUTPUT}/invalid-shell" >/dev/null 2>&1; then
    fail "invalid shell syntax was accepted"
else
    pass "invalid shell syntax rejected"
fi
cp -R "${GENERATED_DIR}" "${TEST_OUTPUT}/outside-path"
python3 - "${TEST_OUTPUT}/outside-path/cockpit-package.yml" <<'PYTEST'
import sys, yaml
p=sys.argv[1]
with open(p) as f: m=yaml.safe_load(f)
m['features']['skills'].append({'name':'outside','path':'../test-generated-pkg/README.md'})
with open(p,'w') as f: yaml.safe_dump(m,f)
PYTEST
if "${PACKAGE_DIR}/bin/cockpit-builder" validate "${TEST_OUTPUT}/outside-path" >/dev/null 2>&1; then
    fail "escaping feature path was accepted"
else
    pass "escaping feature path rejected"
fi

# Test registry create
REGISTRY_DIR="${TEST_OUTPUT}/test-registry"
echo ""
echo "Testing registry create subcommand..."
if "${PACKAGE_DIR}/bin/cockpit-builder" registry create "${REGISTRY_DIR}" >/dev/null 2>&1; then
    pass "registry create subcommand works"
else
    fail "registry create subcommand failed"
fi

if [[ -f "${REGISTRY_DIR}/package-index.yaml" ]]; then
    pass "registry package-index.yaml exists"
else
    fail "registry package-index.yaml missing"
fi

if [[ -d "${REGISTRY_DIR}/packages" ]]; then
    pass "registry packages/ directory exists"
else
    fail "registry packages/ directory missing"
fi

if [[ -f "${REGISTRY_DIR}/.github/workflows/validate-packages.yml" ]]; then
    pass "registry workflow exists"
else
    fail "registry workflow missing"
fi

# Test new registry scripts and hooks
for f in scripts/validate-registry.sh scripts/validate-pr.sh scripts/install-hooks.sh; do
    if [[ -f "${REGISTRY_DIR}/${f}" ]]; then
        pass "registry file exists: ${f}"
    else
        fail "registry file missing: ${f}"
    fi
    if [[ -x "${REGISTRY_DIR}/${f}" ]]; then
        pass "registry file is executable: ${f}"
    else
        fail "registry file not executable: ${f}"
    fi
done

if [[ -f "${REGISTRY_DIR}/.githooks/pre-commit" ]]; then
    pass "registry .githooks/pre-commit exists"
else
    fail "registry .githooks/pre-commit missing"
fi
if [[ -x "${REGISTRY_DIR}/.githooks/pre-commit" ]]; then
    pass "registry .githooks/pre-commit is executable"
else
    fail "registry .githooks/pre-commit not executable"
fi

# Verify workflow calls shell entrypoints
if grep -q "validate-registry.sh" "${REGISTRY_DIR}/.github/workflows/validate-packages.yml"; then
    pass "registry workflow calls validate-registry.sh"
else
    fail "registry workflow does not call validate-registry.sh"
fi
if grep -q "validate-pr.sh" "${REGISTRY_DIR}/.github/workflows/validate-packages.yml"; then
    pass "registry workflow calls validate-pr.sh"
else
    fail "registry workflow does not call validate-pr.sh"
fi

# Test registry validate
if "${PACKAGE_DIR}/bin/cockpit-builder" registry validate "${REGISTRY_DIR}" >/dev/null 2>&1; then
    pass "registry validate subcommand works"
else
    fail "registry validate subcommand failed"
fi

# Test publish
if "${PACKAGE_DIR}/bin/cockpit-builder" publish "${GENERATED_DIR}" "${REGISTRY_DIR}" >/dev/null 2>&1; then
    pass "publish subcommand works"
else
    fail "publish subcommand failed"
fi

if [[ -d "${REGISTRY_DIR}/packages/${TEST_PKG}" ]]; then
    pass "published package directory exists"
else
    fail "published package directory missing"
fi

if grep -q "${TEST_PKG}" "${REGISTRY_DIR}/package-index.yaml"; then
    pass "published package registered in package-index.yaml"
else
    fail "published package not registered in package-index.yaml"
fi

# Test configure subcommand
if "${PACKAGE_DIR}/bin/cockpit-builder" configure >/dev/null 2>&1; then
    pass "configure subcommand works"
else
    fail "configure subcommand failed"
fi

# Test help
if "${PACKAGE_DIR}/bin/cockpit-builder" help >/dev/null 2>&1; then
    pass "help subcommand works"
else
    fail "help subcommand failed"
fi

# Summary
echo ""
echo "=== Test Summary ==="
echo "Passed: ${PASS}"
echo "Failed: ${FAIL}"
if [[ ${FAIL} -eq 0 ]]; then
    echo "✓ All tests passed"
    exit 0
else
    echo "✗ Some tests failed"
    exit 1
fi
