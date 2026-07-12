from __future__ import annotations

import asyncio
import uuid
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Request
from fastapi.responses import StreamingResponse

from app.core.command_executor import execute_command
from app.services.cockpit_reader import list_packages
from app.services.registry_reader import find_registry_package, list_registry_packages

router = APIRouter(prefix="/packages", tags=["packages"])

# In-memory job store (sufficient for single-user dashboard).
_jobs: dict[str, dict[str, Any]] = {}


@router.get("")
async def get_packages() -> dict[str, Any]:
    """Lista pacotes instalados localmente."""
    return {"packages": list_packages()}


@router.get("/registry")
async def get_registry() -> dict[str, Any]:
    """Lista pacotes disponíveis nos registries."""
    return {"packages": list_registry_packages()}


@router.post("/install")
async def install_package(request: Request) -> dict[str, Any]:
    """Inicia instalação de pacote de forma assíncrona."""
    body = await request.json()
    name = body.get("name", "").strip()
    if not name:
        return {"error": "package name is required"}

    pkg = find_registry_package(name)
    if not pkg:
        return {"error": f"package not found in registry: {name}"}

    job_id = str(uuid.uuid4())
    _jobs[job_id] = {
        "id": job_id,
        "command": "install",
        "package": name,
        "status": "running",
        "progress": 0,
        "messages": [],
        "result": None,
    }

    asyncio.create_task(_run_install_job(job_id, name))
    return {"job_id": job_id}


@router.get("/jobs/{job_id}")
async def get_job(job_id: str) -> dict[str, Any]:
    """Retorna status de um job."""
    return _jobs.get(job_id, {"error": "job not found"})


@router.get("/jobs/{job_id}/stream")
async def stream_job(job_id: str) -> StreamingResponse:
    """Stream SSE com progresso do job."""

    async def event_generator():
        last = None
        while True:
            job = _jobs.get(job_id)
            if job is None:
                yield "event: error\ndata: job not found\n\n"
                break
            if job != last:
                yield f"event: message\ndata: {__import__('json').dumps(job)}\n\n"
                last = dict(job)
            if job["status"] in ("completed", "failed"):
                yield "event: close\ndata: done\n\n"
                break
            await asyncio.sleep(1)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


async def _run_install_job(job_id: str, name: str) -> None:
    """Executa a instalação em background."""
    job = _jobs[job_id]
    job["messages"].append(f"Starting installation of {name}...")
    job["progress"] = 10

    result = await asyncio.to_thread(execute_command, "pkg", ["install", name], 300)

    job["progress"] = 100
    job["result"] = {
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }
    job["status"] = "completed" if result.success else "failed"
    if not result.success:
        job["messages"].append(f"Installation failed: {result.stderr}")
    else:
        job["messages"].append("Installation completed.")
