from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any

import structlog

logger = structlog.get_logger()


def _workspace_dir() -> Path:
    home = Path.home()
    return Path(os.environ.get("COCKPIT_HOME", home / ".cockpit")) / "workspace" / "mini-apps"


def _pid_file(project_dir: Path, service: str) -> Path:
    return project_dir / ".pids" / f"{service}.pid"


def _is_port_open(port: int) -> bool:
    import socket

    try:
        with socket.create_connection(("localhost", port), timeout=1):
            return True
    except OSError:
        return False


def _read_port(project_dir: Path) -> int | None:
    env_path = project_dir / ".env"
    if not env_path.exists():
        return None
    try:
        for line in env_path.read_text(encoding="utf-8").splitlines():
            if line.startswith("BACKEND_PORT="):
                return int(line.split("=", 1)[1].strip())
            if line.startswith("FRONTEND_PORT="):
                return int(line.split("=", 1)[1].strip())
    except Exception:
        pass
    return None


def _read_pid(pid_file: Path) -> int | None:
    if not pid_file.exists():
        return None
    try:
        pid = int(pid_file.read_text(encoding="utf-8").strip())
        os.kill(pid, 0)
        return pid
    except (ValueError, OSError, ProcessLookupError):
        pass
    return None


def list_mini_apps() -> list[dict[str, Any]]:
    """Lista mini-apps no workspace."""
    workspace = _workspace_dir()
    if not workspace.exists():
        return []

    apps: list[dict[str, Any]] = []
    for entry in sorted(workspace.iterdir()):
        if not entry.is_dir():
            continue
        backend_pid = _read_pid(_pid_file(entry, "backend"))
        frontend_pid = _read_pid(_pid_file(entry, "frontend"))
        port = _read_port(entry)
        health = port and _is_port_open(port)
        uptime = None
        if backend_pid or frontend_pid:
            try:
                stat = Path(f"/proc/{backend_pid or frontend_pid}/stat").read_text()
                start_time = int(stat.split()[21]) / os.sysconf(os.sysconf_names["SC_CLK_TCK"])
                uptime = round(time.time() - start_time, 0)
            except Exception:
                pass

        apps.append(
            {
                "name": entry.name,
                "path": str(entry),
                "backend_pid": backend_pid,
                "frontend_pid": frontend_pid,
                "port": port,
                "health": bool(health),
                "status": "running" if (backend_pid or frontend_pid) else "stopped",
                "uptime": uptime,
            }
        )
    return apps


def get_mini_app(name: str) -> dict[str, Any] | None:
    for app in list_mini_apps():
        if app["name"] == name:
            return app
    return None


def read_logs(name: str, service: str, lines: int = 100) -> list[str]:
    project_dir = _workspace_dir() / name
    log_file = project_dir / f"{service}.log"
    if not log_file.exists():
        return []
    try:
        with open(log_file, encoding="utf-8", errors="replace") as f:
            return f.readlines()[-lines:]
    except Exception as e:
        logger.warning("read_log_error", file=str(log_file), error=str(e))
        return []
