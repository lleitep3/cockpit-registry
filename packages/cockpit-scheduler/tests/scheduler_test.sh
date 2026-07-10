#!/bin/bash
# Tests basicos para o cockpit-scheduler
# Executar: bash tests/scheduler_test.sh

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LIB_DIR="${SCRIPT_DIR}/../lib"
source "${LIB_DIR}/scheduler.sh"

TMP_HOME=$(mktemp -d)
export HOME="${TMP_HOME}"

JOBS_FILE="${HOME}/.cockpit/scheduler/jobs.json"

cleanup() {
    rm -rf "${TMP_HOME}"
}
trap cleanup EXIT

reset_store() {
    rm -f "${HOME}/.cockpit/scheduler/jobs.json"
}

assert_eq() {
    local expected="${1}"
    local actual="${2}"
    local msg="${3}"
    if [[ "${expected}" != "${actual}" ]]; then
        echo "FAIL: ${msg}"
        echo "  expected: ${expected}"
        echo "  actual:   ${actual}"
        exit 1
    fi
}

test_normalize_cron() {
    assert_eq "0 0 * * *" "$(normalize_cron "daily")" "normalize daily"
    assert_eq "0 * * * *" "$(normalize_cron "hourly")" "normalize hourly"
    assert_eq "0 0 * * *" "$(normalize_cron "@daily")" "normalize @daily"
    assert_eq "" "$(normalize_cron "invalid")" "invalid cron returns empty"
    echo "PASS: test_normalize_cron"
}

test_parse_interval() {
    assert_eq "3600" "$(parse_interval "1h")" "parse 1h"
    assert_eq "1800" "$(parse_interval "30m")" "parse 30m"
    assert_eq "10" "$(parse_interval "10s")" "parse 10s"
    assert_eq "" "$(parse_interval "invalid")" "invalid interval returns empty"
    echo "PASS: test_parse_interval"
}

test_add_job() {
    reset_store
    local id
    id=$(add_job "echo hello" "cron" "0 9 * * *" "" "" "test")
    [[ -n "${id}" ]] || { echo "FAIL: add_job did not return id"; exit 1; }

    local count
    count=$(load_jobs | jq 'length')
    assert_eq "1" "${count}" "add_job creates one job"

    local status
    status=$(load_jobs | jq -r '.[0].status')
    assert_eq "ativo" "${status}" "job status is ativo"
    echo "PASS: test_add_job"
}

test_remove_job() {
    reset_store
    local id
    id=$(add_job "echo hello" "cron" "0 9 * * *" "" "" "test")
    remove_job "${id}"

    local count
    count=$(load_jobs | jq 'length')
    assert_eq "0" "${count}" "remove_job deletes job"
    echo "PASS: test_remove_job"
}

test_repeat_job() {
    reset_store
    local id
    id=$(add_job "echo hello" "repeat" "" "1m" "2" "test")

    local interval
    interval=$(load_jobs | jq -r '.[0].interval')
    assert_eq "1m" "${interval}" "repeat interval stored"

    local max
    max=$(load_jobs | jq -r '.[0].max_executions')
    assert_eq "2" "${max}" "max executions stored"
    echo "PASS: test_repeat_job"
}

test_store_persistence() {
    reset_store
    add_job "echo test" "cron" "0 9 * * *" "" "" "persist"
    local file
    file=$(jobs_file)
    [[ -f "${file}" ]] || { echo "FAIL: jobs file not created"; exit 1; }

    local count
    count=$(jq 'length' "${file}")
    assert_eq "1" "${count}" "jobs persisted to file"
    echo "PASS: test_store_persistence"
}

main() {
    test_normalize_cron
    test_parse_interval
    test_add_job
    test_remove_job
    test_repeat_job
    test_store_persistence
    echo ""
    echo "All tests passed!"
}

main
