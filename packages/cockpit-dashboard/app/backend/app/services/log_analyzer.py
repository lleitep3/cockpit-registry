from __future__ import annotations

import json
import os
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import structlog

logger = structlog.get_logger()


def _cockpit_dir() -> Path:
    home = Path.home()
    return Path(os.environ.get("COCKPIT_HOME", home / ".cockpit"))


def _metrics_file() -> Path:
    return _cockpit_dir() / "metrics.json"


def _logs_dir() -> Path:
    return _cockpit_dir() / "logs"


def load_metrics(limit: int = 10000) -> list[dict[str, Any]]:
    """Lê ~/.cockpit/metrics.json com métricas de execução de comandos."""
    path = _metrics_file()
    if not path.exists():
        logger.warning("metrics_file_not_found", path=str(path))
        return []
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            return []
        return data[-limit:]
    except Exception as e:
        logger.error("metrics_read_error", error=str(e))
        return []


def load_logs(limit: int = 1000) -> list[dict[str, Any]]:
    """Lê arquivos de log JSON rotacionados em ~/.cockpit/logs/."""
    logs_dir = _logs_dir()
    if not logs_dir.exists():
        return []

    entries: list[dict[str, Any]] = []
    for entry in sorted(logs_dir.iterdir(), reverse=True):
        if not entry.is_file() or not entry.name.endswith(".log"):
            continue
        try:
            with open(entry, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        parsed = json.loads(line)
                        entries.append(parsed)
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            logger.warning("log_read_error", file=str(entry), error=str(e))
            continue

        if len(entries) >= limit:
            break

    return entries[:limit]


def parse_ts(ts_str: Any) -> datetime | None:
    if not ts_str or not isinstance(ts_str, str):
        return None
    try:
        return datetime.strptime(ts_str[:19], "%Y-%m-%dT%H:%M:%S")
    except Exception:
        return None


def analyze_metrics(metrics: list[dict[str, Any]]) -> dict[str, Any]:
    """Gera insights a partir das métricas de execução."""
    if not metrics:
        return {
            "total": 0,
            "successful": 0,
            "failed": 0,
            "success_rate": 0.0,
            "avg_duration_ms": 0.0,
            "total_duration_ms": 0.0,
            "commands": [],
            "error_types": [],
            "slowest_commands": [],
            "timeline": [],
            "recent_errors": [],
            "command_error_rates": [],
            "generated_insights": [],
        }

    total = len(metrics)
    successful = sum(1 for m in metrics if m.get("status") == "success")
    failed = total - successful
    success_rate = round((successful / total) * 100, 2) if total else 0.0

    durations = [float(m.get("duration_ms", 0) or 0) for m in metrics]
    total_duration = sum(durations)
    avg_duration = round(total_duration / total, 2) if total else 0.0

    command_counter: Counter[str] = Counter()
    command_failures: Counter[str] = Counter()
    error_counter: Counter[str] = Counter()
    command_durations: defaultdict[str, list[float]] = defaultdict(list)
    timeline: defaultdict[str, dict[str, int]] = defaultdict(lambda: {"success": 0, "error": 0})
    recent_errors_list: list[dict[str, Any]] = []

    for m in metrics:
        cmd = m.get("command", "unknown")
        status = m.get("status", "unknown")
        duration = float(m.get("duration_ms", 0) or 0)
        error_type = m.get("error_type", "unknown")
        ts = m.get("timestamp", "")

        command_counter[cmd] += 1
        command_durations[cmd].append(duration)

        day = ts[:10] if isinstance(ts, str) and len(ts) >= 10 else "unknown"
        if status == "success":
            timeline[day]["success"] += 1
        else:
            timeline[day]["error"] += 1
            command_failures[cmd] += 1
            if error_type:
                error_counter[error_type] += 1
            
            recent_errors_list.append({
                "timestamp": ts,
                "command": cmd,
                "args": m.get("args", []),
                "exit_code": m.get("exit_code", 1),
                "duration_ms": duration,
                "user": m.get("user", "unknown"),
                "version": m.get("version", "0.1.0"),
                "language": m.get("language", "en-us"),
                "error": m.get("error", "Erro desconhecido"),
                "error_type": error_type
            })

    # Sort recent errors by timestamp descending
    recent_errors_list.sort(key=lambda x: x["timestamp"], reverse=True)
    recent_errors = recent_errors_list[:20]

    commands = [
        {"command": cmd, "count": count, "avg_duration_ms": round(sum(command_durations[cmd]) / len(command_durations[cmd]), 2)}
        for cmd, count in command_counter.most_common()
    ]

    error_types = [
        {"error_type": err, "count": count}
        for err, count in error_counter.most_common()
    ]

    slowest = sorted(
        [
            {"command": cmd, "avg_duration_ms": round(sum(durs) / len(durs), 2), "max_duration_ms": round(max(durs), 2)}
            for cmd, durs in command_durations.items()
        ],
        key=lambda x: x["avg_duration_ms"],
        reverse=True,
    )[:10]

    timeline_sorted = [
        {"date": day, "success": data["success"], "error": data["error"]}
        for day, data in sorted(timeline.items())
    ]

    # Calculate error rate per command
    command_error_rates = []
    for cmd, count in command_counter.items():
        fails = command_failures[cmd]
        rate = round((fails / count) * 100, 2)
        command_error_rates.append({
            "command": cmd,
            "total": count,
            "failed": fails,
            "rate": rate
        })
    command_error_rates.sort(key=lambda x: x["rate"], reverse=True)

    # Generate smart insights
    generated_insights = []
    
    # 1. Success Rate Insight
    if success_rate == 100.0:
        generated_insights.append({
            "type": "success",
            "title": "Excelente Estabilidade",
            "description": "Todas as execuções recentes de comandos foram concluídas com sucesso (100% de taxa de sucesso)!"
        })
    elif success_rate >= 95.0:
        generated_insights.append({
            "type": "info",
            "title": "Boa Estabilidade",
            "description": f"A taxa de sucesso geral dos comandos está em {success_rate}%, mantendo-se dentro do padrão esperado."
        })
    else:
        generated_insights.append({
            "type": "error",
            "title": "Atenção: Instabilidade Detectada",
            "description": f"A taxa de sucesso geral caiu para {success_rate}%, abaixo da meta recomendada de 95%. Verifique os logs de erro."
        })

    # 2. Command Error Rate Alert
    high_failure_cmds = [c for c in command_error_rates if c["rate"] > 10.0 and c["total"] >= 3]
    for hfc in high_failure_cmds[:3]:
        generated_insights.append({
            "type": "warning",
            "title": f"Alta taxa de erro em '{hfc['command']}'",
            "description": f"O comando '{hfc['command']}' falhou em {hfc['rate']}% das execuções ({hfc['failed']} de {hfc['total']})."
        })

    # 3. Last 24 Hours Error Volume
    errors_24h = 0
    now = datetime.now()
    for e in recent_errors_list:
        ts = parse_ts(e["timestamp"])
        if ts and (now - ts).total_seconds() < 86400:
            errors_24h += 1
    
    if errors_24h > 0:
        generated_insights.append({
            "type": "warning",
            "title": "Erros Recentes",
            "description": f"Houve {errors_24h} falha(s) de comando registrada(s) nas últimas 24 horas."
        })
    elif failed > 0:
        generated_insights.append({
            "type": "success",
            "title": "Livre de erros recentemente",
            "description": "Nenhum erro de comando foi registrado nas últimas 24 horas."
        })

    # 4. Slowness Alert
    if slowest:
        worst_slow = slowest[0]
        if worst_slow["avg_duration_ms"] > 1000.0:
            generated_insights.append({
                "type": "info",
                "title": f"Gargalo de Performance em '{worst_slow['command']}'",
                "description": f"O comando '{worst_slow['command']}' é o mais lento em média, levando {worst_slow['avg_duration_ms']:.0f}ms por execução."
            })

    return {
        "total": total,
        "successful": successful,
        "failed": failed,
        "success_rate": success_rate,
        "avg_duration_ms": avg_duration,
        "total_duration_ms": round(total_duration, 2),
        "commands": commands,
        "error_types": error_types,
        "slowest_commands": slowest,
        "timeline": timeline_sorted,
        "recent_errors": recent_errors,
        "command_error_rates": command_error_rates,
        "generated_insights": generated_insights,
    }
