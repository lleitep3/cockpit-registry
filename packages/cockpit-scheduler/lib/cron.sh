#!/bin/bash
# cron.sh - Parsing simples de cron e calculo de proxima execucao
# AICockpit - cockpit-scheduler

set -uo pipefail

# Normaliza aliases comuns para expressao cron padrao
normalize_cron() {
    local expr="${1,,}"

    case "${expr}" in
        "@yearly"|"@annually") echo "0 0 1 1 *" ;;
        "@monthly") echo "0 0 1 * *" ;;
        "@weekly") echo "0 0 * * 0" ;;
        "@daily"|"@midnight") echo "0 0 * * *" ;;
        "@hourly") echo "0 * * * *" ;;
        "daily") echo "0 0 * * *" ;;
        "hourly") echo "0 * * * *" ;;
        "weekdays") echo "0 0 * * 1-5" ;;
        "weekends") echo "0 0 * * 0,6" ;;
        *)
            # Valida formato basico 5 campos
            local fields
            fields=$(echo "${expr}" | awk '{print NF}')
            if [[ "${fields}" -eq 5 ]]; then
                echo "${expr}"
            else
                echo ""
            fi
            ;;
    esac
}

# Calcula proxima execucao a partir de uma data (usando date e awk)
# Retorna timestamp no formato ISO 8601
next_cron_run() {
    local expr="${1}"
    local from_epoch="${2:-$(date +%s)}"

    local normalized
    normalized=$(normalize_cron "${expr}")
    if [[ -z "${normalized}" ]]; then
        echo ""
        return 1
    fi

    # Para simplificar, usa o minuto e hora da expressao e calcula a proxima ocorrencia
    local minute hour
    minute=$(echo "${normalized}" | awk '{print $1}')
    hour=$(echo "${normalized}" | awk '{print $2}')

    # Se for * no minuto/hora, usa 0/0 como base para daily
    [[ "${minute}" == "*" ]] && minute="0"
    [[ "${hour}" == "*" ]] && hour="0"

    # Verifica se eh um numero valido
    if [[ "${minute}" =~ ^[0-9]+$ && "${hour}" =~ ^[0-9]+$ ]]; then
        local from_date next_date
        from_date=$(date -d "@${from_epoch}" "+%Y-%m-%d")

        # Proxima ocorrencia: hoje se ainda nao passou, senao amanha
        next_date=$(date -d "${from_date} ${hour}:${minute}:00" "+%Y-%m-%d %H:%M:%S" 2>/dev/null || true)
        if [[ -z "${next_date}" ]]; then
            echo ""
            return 1
        fi

        local next_epoch
        next_epoch=$(date -d "${next_date}" +%s)
        if (( next_epoch <= from_epoch )); then
            next_epoch=$((next_epoch + 86400))
        fi
        date -d "@${next_epoch}" -u +"%Y-%m-%dT%H:%M:%SZ"
    else
        # Caso mais complexo: incrementa 1 dia
        local next_epoch=$((from_epoch + 86400))
        date -d "@${next_epoch}" -u +"%Y-%m-%dT%H:%M:%SZ"
    fi
}

# Converte intervalo humano (1h, 30m, 1d) para segundos
parse_interval() {
    local interval="${1,,}"

    case "${interval}" in
        "1h") echo 3600 ;;
        "30m") echo 1800 ;;
        "15m") echo 900 ;;
        "5m") echo 300 ;;
        "1m") echo 60 ;;
        "1d") echo 86400 ;;
        "1w") echo 604800 ;;
        *)
            # Tenta extrair numero e unidade
            local value unit
            value=$(echo "${interval}" | grep -oE '^[0-9]+')
            unit=$(echo "${interval}" | grep -oE '[shmdw]$')
            if [[ -z "${value}" || -z "${unit}" ]]; then
                echo ""
                return 1
            fi
            case "${unit}" in
                s) echo $((value)) ;;
                m) echo $((value * 60)) ;;
                h) echo $((value * 3600)) ;;
                d) echo $((value * 86400)) ;;
                w) echo $((value * 604800)) ;;
            esac
            ;;
    esac
}

# Descreve um padrao cron de forma legivel
describe_cron() {
    local expr="${1,,}"

    case "${expr}" in
        "@yearly"|"@annually") echo "Anualmente" ;;
        "@monthly") echo "Mensalmente" ;;
        "@weekly") echo "Semanalmente" ;;
        "@daily"|"@midnight"|"daily") echo "Diariamente" ;;
        "@hourly"|"hourly") echo "A cada hora" ;;
        "weekdays") echo "Dias de semana" ;;
        "weekends") echo "Fins de semana" ;;
        *) echo "Cron: ${expr}" ;;
    esac
}
