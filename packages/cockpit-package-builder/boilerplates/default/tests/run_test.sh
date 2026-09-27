#!/bin/bash
# {PKG_NAME} test runner

set -uo pipefail

PACKAGE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
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

echo "=== {PKG_NAME} tests ==="

if [[ -f "${PACKAGE_DIR}/cockpit-package.yml" ]]; then
    pass "manifest exists"
else
    fail "manifest missing"
fi

if [[ -x "${PACKAGE_DIR}/bin/{PKG_NAME}" ]]; then
    pass "main script is executable"
else
    fail "main script not executable"
fi

if bash -n "${PACKAGE_DIR}/bin/{PKG_NAME}"; then
    pass "main script syntax OK"
else
    fail "main script syntax error"
fi

if "${PACKAGE_DIR}/bin/{PKG_NAME}" hello >/dev/null 2>&1; then
    pass "hello subcommand works"
else
    fail "hello subcommand failed"
fi

if [[ -x "${PACKAGE_DIR}/bin/configure" ]]; then
    pass "configure script is executable"
else
    fail "configure script not executable"
fi

if [[ -x "${PACKAGE_DIR}/bin/validate" ]]; then
    pass "validate script is executable"
else
    fail "validate script not executable"
fi

echo ""
echo "Passed: ${PASS}, Failed: ${FAIL}"
[[ ${FAIL} -eq 0 ]]
