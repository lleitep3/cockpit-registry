from typing import Any

from fastapi import APIRouter

from app.services.cockpit_reader import (
    list_kb,
    list_packages,
    list_registries,
    read_config,
    read_status,
)

router = APIRouter(prefix="/cockpit", tags=["cockpit"])


@router.get("/status")
async def status() -> dict[str, Any]:
    return read_status()


@router.get("/config")
async def config() -> dict[str, Any]:
    return read_config()


@router.get("/providers")
async def providers() -> dict[str, Any]:
    cfg = read_config()
    providers_data = cfg.get("providers", {})
    if isinstance(providers_data, dict):
        items = [
            {"name": name, **info}
            for name, info in providers_data.items()
            if isinstance(info, dict)
        ]
    elif isinstance(providers_data, list):
        items = providers_data
    else:
        items = []
    return {"providers": items}


@router.get("/packages")
async def packages() -> dict[str, Any]:
    return {"packages": list_packages()}


@router.get("/registries")
async def registries() -> dict[str, Any]:
    return {"registries": list_registries()}


@router.get("/kb")
async def kb() -> dict[str, Any]:
    return {"documents": list_kb()}
