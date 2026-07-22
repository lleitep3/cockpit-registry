from __future__ import annotations

import asyncio
import os
import time
from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.core.command_executor import execute_command
from app.services.mini_apps import get_mini_app, list_mini_apps, read_logs

router = APIRouter(prefix="/mini-apps", tags=["mini-apps"])


def _safe_name(name: str) -> bool:
    return all(c.isalnum() or c in "_-" for c in name) and len(name) > 0


@router.get("")
async def get_all() -> dict[str, Any]:
    return {"mini_apps": list_mini_apps()}


@router.get("/{name}")
async def get_one(name: str) -> dict[str, Any]:
    if not _safe_name(name):
        raise HTTPException(status_code=400, detail="invalid mini-app name")
    app = get_mini_app(name)
    if not app:
        raise HTTPException(status_code=404, detail="mini-app not found")
    return app


@router.post("/{name}/start")
async def start(name: str) -> dict[str, Any]:
    if not _safe_name(name):
        raise HTTPException(status_code=400, detail="invalid mini-app name")
    result = await asyncio.to_thread(execute_command, "mini-app", ["start", name], 60)
    return {"success": result.success, "error": result.stderr if not result.success else None}


@router.post("/{name}/stop")
async def stop(name: str) -> dict[str, Any]:
    if not _safe_name(name):
        raise HTTPException(status_code=400, detail="invalid mini-app name")
    result = await asyncio.to_thread(execute_command, "mini-app", ["stop", name], 60)
    return {"success": result.success, "error": result.stderr if not result.success else None}


@router.post("/{name}/restart")
async def restart(name: str) -> dict[str, Any]:
    if not _safe_name(name):
        raise HTTPException(status_code=400, detail="invalid mini-app name")
    await asyncio.to_thread(execute_command, "mini-app", ["stop", name], 60)
    await asyncio.sleep(1)
    result = await asyncio.to_thread(execute_command, "mini-app", ["start", name], 60)
    return {"success": result.success, "error": result.stderr if not result.success else None}


async def _log_event_generator(log_file: str) -> Any:
    last_size = 0
    while True:
        try:
            current_size = os.path.getsize(log_file)
        except OSError:
            current_size = 0
        if current_size > last_size:
            try:
                with open(log_file, "r", encoding="utf-8", errors="replace") as f:
                    f.seek(last_size)
                    new_data = f.read()
                for line in new_data.splitlines():
                    yield f"data: {line}\n\n"
                last_size = current_size
            except Exception:
                pass
        await asyncio.sleep(1)


@router.get("/{name}/logs/stream")
async def stream_logs(name: str, service: str = "backend") -> StreamingResponse:
    if not _safe_name(name):
        raise HTTPException(status_code=400, detail="invalid mini-app name")
    if service not in ("backend", "frontend"):
        raise HTTPException(status_code=400, detail="invalid service")

    log_file = os.path.expanduser(f"~/.cockpit/workspace/mini-apps/{name}/{service}.log")
    return StreamingResponse(_log_event_generator(log_file), media_type="text/event-stream")


@router.get("/{name}/metrics")
async def metrics(name: str) -> dict[str, Any]:
    if not _safe_name(name):
        raise HTTPException(status_code=400, detail="invalid mini-app name")
    app = get_mini_app(name)
    if not app:
        raise HTTPException(status_code=404, detail="mini-app not found")

    pids = [pid for pid in [app.get("backend_pid"), app.get("frontend_pid")] if pid]
    cpu = 0.0
    mem = 0.0
    for pid in pids:
        try:
            stat = Path(f"/proc/{pid}/stat").read_text()
            utime = int(stat.split()[13])
            stime = int(stat.split()[14])
            total_time = utime + stime
            cpu += total_time / os.sysconf(os.sysconf_names["SC_CLK_TCK"])
            status = Path(f"/proc/{pid}/status").read_text()
            for line in status.splitlines():
                if line.startswith("VmRSS:"):
                    mem += int(line.split()[1])
                    break
        except Exception:
            continue

    return {"cpu_seconds": round(cpu, 2), "memory_kb": round(mem, 2)}
