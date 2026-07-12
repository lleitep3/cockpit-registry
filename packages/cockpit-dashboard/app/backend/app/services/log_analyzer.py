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
        }

    total = len(metrics)
    successful = sum(1 for m in metrics if m.get("status") == "success")
    failed = total - successful
    success_rate = round((successful / total) * 100, 2) if total else 0.0

    durations = [float(m.get("duration_ms", 0) or 0) for m in metrics]
    total_duration = sum(durations)
    avg_duration = round(total_duration / total, 2) if total else 0.0

    command_counter: Counter[str] = Counter()
    error_counter: Counter[str] = Counter()
    command_durations: defaultdict[str, list[float]] = defaultdict(list)
    timeline: defaultdict[str, dict[str, int]] = defaultdict(lambda: {"success": 0, "error": 0})

    for m in metrics:
        cmd = m.get("command", "unknown")
        status = m.get("status", "unknown")
        duration = float(m.get("duration_ms", 0) or 0)
        error_type = m.get("error_type", "unknown")
        ts = m.get("timestamp", "")

        command_counter[cmd] += 1
        command_durations[cmd].append(duration)

        if status != "success" and error_type:
            error_counter[error_type] += 1

        day = ts[:10] if isinstance(ts, str) and len(ts) >= 10 else "unknown"
        if status == "success":
            timeline[day]["success"] += 1
        else:
            timeline[day]["error"] += 1

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
            {"command": cmd, "avg_duration_ms": round(sum(durations) / len(durations), 2), "max_duration_ms": round(max(durations), 2)}
            for cmd, durations in command_durations.items()
        ],
        key=lambda x: x["avg_duration_ms"],
        reverse=True,
    )[:10]

    timeline_sorted = [
        {"date": day, "success": data["success"], "error": data["error"]}
        for day, data in sorted(timeline.items())
    ]

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
    }
