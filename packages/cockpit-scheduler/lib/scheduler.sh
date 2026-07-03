#!/bin/bash
# scheduler.sh - Logica principal do agendamento
# AICockpit - cockpit-scheduler

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/store.sh"
source "${SCRIPT_DIR}/cron.sh"

now_iso() {
    date -u +"%Y-%m-%dT%H:%M:%SZ"
}

now_epoch() {
    date +%s
}

iso_to_epoch() {
    date -d "${1}" +%s 2>/dev/null || echo 0
}

# Valida um agendamento
validate_job() {
    local command="${1}"
    local job_type="${2}"
    local cron_expr="${3}"
    local interval="${4}"
    local repeat="${5}"

    if [[ -z "${command}" ]]; then
        echo "Erro: comando nao pode ser vazio" >&2
        return 1
    fi

    case "${job_type}" in
        cron)
            if [[ -z "${cron_expr}" ]]; then
                echo "Erro: expressao cron nao pode ser vazia" >&2
                return 1
            fi
            if [[ -z "$(normalize_cron "${cron_expr}")" ]]; then
                echo "Erro: expressao cron invalida: ${cron_expr}" >&2
                return 1
            fi
            ;;
        repeat)
            if [[ -z "${interval}" ]]; then
                echo "Erro: intervalo nao pode ser vazio" >&2
                return 1
            fi
            local sec
            sec=$(parse_interval "${interval}")
            if [[ -z "${sec}" ]]; then
                echo "Erro: intervalo invalido: ${interval}" >&2
                return 1
            fi
            ;;
        *)
            echo "Erro: tipo de agendamento invalido: ${job_type}" >&2
            return 1
            ;;
    esac

    if [[ -n "${repeat}" && ! "${repeat}" =~ ^[0-9]+$ ]]; then
        echo "Erro: repeticoes deve ser um numero inteiro" >&2
        return 1
    fi

    return 0
}

# Calcula proxima execucao
compute_next_run() {
    local job_type="${1}"
    local cron_expr="${2}"
    local interval="${3}"
    local last_run_epoch="${4:-0}"
    local now
    now=$(now_epoch)

    case "${job_type}" in
        cron)
            next_cron_run "${cron_expr}" "${now}"
            ;;
        repeat)
            local sec
            sec=$(parse_interval "${interval}")
            local base_epoch=${last_run_epoch}
            (( base_epoch == 0 )) && base_epoch=${now}
            date -d "@$((base_epoch + sec))" -u +"%Y-%m-%dT%H:%M:%SZ"
            ;;
    esac
}

# Adiciona um novo agendamento
add_job() {
    local command="${1}"
    local job_type="${2}"
    local cron_expr="${3}"
    local interval="${4}"
    local repeat="${5}"
    local description="${6:-}"

    validate_job "${command}" "${job_type}" "${cron_expr}" "${interval}" "${repeat}" || return 1

    local id
    id=$(generate_id)
    while id_exists "${id}"; do
        id=$(generate_id)
    done

    local next_run
    next_run=$(compute_next_run "${job_type}" "${cron_expr}" "${interval}" 0)

    local repeat_val="null"
    [[ -n "${repeat}" ]] && repeat_val="${repeat}"

    local new_job
    new_job=$(jq -n \
        --arg id "${id}" \
        --arg command "${command}" \
        --arg type "${job_type}" \
        --arg cron "${cron_expr}" \
        --arg interval "${interval}" \
        --argjson repeat "${repeat_val}" \
        --arg desc "${description}" \
        --arg next_run "${next_run}" \
        --arg created_at "$(now_iso)" \
        '{id: $id, command: $command, type: $type, cron_expr: $cron, interval: $interval, max_executions: $repeat, executions: 0, last_run: null, next_run: $next_run, status: "ativo", description: $desc, created_at: $created_at}')

    local jobs
    jobs=$(load_jobs)
    jobs=$(echo "${jobs}" | jq --argjson job "${new_job}" '. + [$job]')
    save_jobs "${jobs}"

    echo "${id}"
}

# Lista agendamentos
list_jobs() {
    load_jobs | jq -r '
        if length == 0 then
            "Nenhum agendamento encontrado."
        else
            "ID             | COMANDO                   | TIPO      | STATUS      | PROXIMA EXECUCAO\n" +
            ("--------------------------------------------------------------------------------" | .) +
            "\n" +
            (.[] | "\(.id) | \(.command[:25])\(if (.command | length) > 25 then "..." else "" end) | \(.type) | \(.status) | \(.next_run // "-")")
        end'
}

# Remove agendamento
remove_job() {
    local id="${1}"
    local jobs
    jobs=$(load_jobs)

    if ! echo "${jobs}" | jq -e --arg id "${id}" '.[] | select(.id == $id)' >/dev/null 2>&1; then
        echo "Erro: agendamento ${id} nao encontrado" >&2
        return 1
    fi

    jobs=$(echo "${jobs}" | jq --arg id "${id}" '[.[] | select(.id != $id)]')
    save_jobs "${jobs}"
    echo "Agendamento ${id} removido com sucesso."
}

# Executa agendamentos que estao devendo
run_due_jobs() {
    local now
    now=$(now_epoch)
    local jobs
    jobs=$(load_jobs)
    local ran=0

    local count
    count=$(echo "${jobs}" | jq 'length')

    for (( i=0; i<count; i++ )); do
        local job
        job=$(echo "${jobs}" | jq ".[${i}]")

        local id status next_run_epoch command type interval max_executions executions
        id=$(echo "${job}" | jq -r '.id')
        status=$(echo "${job}" | jq -r '.status')
        next_run=$(echo "${job}" | jq -r '.next_run // empty')
        command=$(echo "${job}" | jq -r '.command')
        type=$(echo "${job}" | jq -r '.type')
        interval=$(echo "${job}" | jq -r '.interval // empty')
        max_executions=$(echo "${job}" | jq -r '.max_executions // empty')
        executions=$(echo "${job}" | jq -r '.executions // 0')

        [[ "${status}" != "ativo" ]] && continue

        next_run_epoch=0
        [[ -n "${next_run}" ]] && next_run_epoch=$(iso_to_epoch "${next_run}")

        if (( next_run_epoch > 0 && next_run_epoch > now )); then
            continue
        fi

        echo "[scheduler] executando job ${id}: ${command}"
        eval "${command}"
        local exit_code=$?

        if (( exit_code == 0 )); then
            echo "[scheduler] job ${id} concluido com sucesso"
        else
            echo "[scheduler] job ${id} falhou com codigo ${exit_code}"
        fi

        executions=$((executions + 1))
        local new_status="ativo"
        local last_run_epoch
        last_run_epoch=$(now_epoch)

        if [[ -n "${max_executions}" && "${max_executions}" != "null" && "${max_executions}" -gt 0 && "${executions}" -ge "${max_executions}" ]]; then
            new_status="concluido"
            next_run="null"
        else
            next_run=$(compute_next_run "${type}" "$(echo "${job}" | jq -r '.cron_expr // empty')" "${interval}" "${last_run_epoch}")
        fi

        local last_run_iso
        last_run_iso=$(now_iso)

        jobs=$(echo "${jobs}" | jq \
            --arg id "${id}" \
            --arg last_run "${last_run_iso}" \
            --arg next_run "${next_run}" \
            --arg status "${new_status}" \
            --argjson executions "${executions}" \
            '[.[] | if .id == $id then .last_run = $last_run | .next_run = (if $next_run == "null" then null else $next_run end) | .status = $status | .executions = $executions else . end]')

        ran=$((ran + 1))
    done

    save_jobs "${jobs}"

    if (( ran == 0 )); then
        echo "[scheduler] nenhum agendamento pendente"
    else
        echo "[scheduler] ${ran} agendamento(s) executado(s)"
    fi
}

# Executa todos os jobs ativos imediatamente
run_all_jobs() {
    local jobs
    jobs=$(load_jobs)
    local count
    count=$(echo "${jobs}" | jq 'length')

    for (( i=0; i<count; i++ )); do
        local job
        job=$(echo "${jobs}" | jq ".[${i}]")

        local id status command
        id=$(echo "${job}" | jq -r '.id')
        status=$(echo "${job}" | jq -r '.status')
        command=$(echo "${job}" | jq -r '.command')

        [[ "${status}" != "ativo" ]] && continue

        echo "[scheduler] executando job ${id} imediatamente: ${command}"
        eval "${command}"
    done
}

# Instala cron job
install_cron() {
    local interval="${1:-5}"
    local cron_dir="${HOME}/.cockpit/scheduler"
    local cron_file="${cron_dir}/cron.txt"
    local binary
    binary=$(command -v cockpit || echo "cockpit")

    mkdir -p "${cron_dir}"

    cat > "${cron_file}" <<EOF
*/${interval} * * * * ${binary} scheduler run >> ${HOME}/.cockpit/logs/scheduler-cron.log 2>&1
EOF

    echo "[scheduler] entrada cron salva em ${cron_file}"
    echo "[scheduler] para ativar, rode: crontab ${cron_file}"
}

# Instala systemd user timer
# Args: interval (minutos), persistent (true/false)
install_systemd() {
    local interval="${1:-5}"
    local persistent="${2:-true}"
    local user_dir="${HOME}/.config/systemd/user"
    local binary
    binary=$(command -v cockpit || echo "cockpit")

    mkdir -p "${user_dir}"

    local persistent_line=""
    if [[ "${persistent}" == "true" ]]; then
        persistent_line="Persistent=true"
    fi

    cat > "${user_dir}/aicockpit-scheduler.service" <<EOF
[Unit]
Description=AICockpit Scheduler

[Service]
Type=oneshot
ExecStart=${binary} scheduler run
EOF

    cat > "${user_dir}/aicockpit-scheduler.timer" <<EOF
[Unit]
Description=AICockpit Scheduler Timer

[Timer]
OnBootSec=1min
OnUnitActiveSec=${interval}m
${persistent_line}

[Install]
WantedBy=timers.target
EOF

    echo "[scheduler] systemd user timer instalado em ${user_dir}"
    if [[ "${persistent}" == "true" ]]; then
        echo "[scheduler] Persistent=true ativado: jobs em atraso rodam apos boot."
    else
        echo "[scheduler] Persistent=false: jobs em atraso NAO serao executados automaticamente."
    fi
    echo "[scheduler] para ativar, rode: systemctl --user daemon-reload && systemctl --user enable --now aicockpit-scheduler.timer"
}
