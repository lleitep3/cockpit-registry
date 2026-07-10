#!/bin/bash
# store.sh - Persistencia de agendamentos em JSON
# AICockpit - cockpit-scheduler

set -uo pipefail

scheduler_dir() {
    echo "${HOME}/.cockpit/scheduler"
}

jobs_file() {
    echo "$(scheduler_dir)/jobs.json"
}

ensure_store() {
    local dir
    dir=$(scheduler_dir)
    mkdir -p "${dir}"
    local file
    file=$(jobs_file)
    if [[ ! -f "${file}" ]]; then
        echo "[]" > "${file}"
    fi
}

load_jobs() {
    ensure_store
    local file
    file=$(jobs_file)
    if [[ -s "${file}" ]]; then
        cat "${file}"
    else
        echo "[]"
    fi
}

save_jobs() {
    local jobs="${1}"
    ensure_store
    local file
    file=$(jobs_file)
    echo "${jobs}" > "${file}"
}

# Gera ID unico no formato sched_<hex>
generate_id() {
    local id
    id=$(head -c 6 /dev/urandom | xxd -p 2>/dev/null || printf '%x' "$RANDOM$RANDOM")
    echo "sched_${id}"
}

# Verifica se ID existe
id_exists() {
    local id="${1}"
    load_jobs | jq -e --arg id "${id}" '.[] | select(.id == $id)' >/dev/null 2>&1
}
