from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request

from app.services.vault_manager import (
    add_secret,
    get_secret,
    get_status,
    list_secrets,
    lock_vault,
    unlock_vault,
)

router = APIRouter(prefix="/vault", tags=["vault"])


@router.get("/status")
async def status() -> dict[str, Any]:
    return get_status()


@router.get("/secrets")
async def secrets() -> dict[str, Any]:
    return {"secrets": list_secrets()}


@router.post("/secrets")
async def create_secret(request: Request) -> dict[str, Any]:
    body = await request.json()
    key = body.get("key", "").strip()
    value = body.get("value", "")
    master_password = body.get("master_password", "")
    if not key or not value or not master_password:
        return {"success": False, "error": "key, value and master_password are required"}
    return add_secret(key, value, master_password)


@router.post("/secrets/reveal")
async def reveal_secret(request: Request) -> dict[str, Any]:
    body = await request.json()
    key = body.get("key", "").strip()
    master_password = body.get("master_password", "")
    if not key or not master_password:
        return {"success": False, "error": "key and master_password are required"}
    return get_secret(key, master_password)


@router.post("/lock")
async def lock(request: Request) -> dict[str, Any]:
    body = await request.json()
    master_password = body.get("master_password", "")
    if not master_password:
        return {"success": False, "error": "master_password is required"}
    return lock_vault(master_password)


@router.post("/unlock")
async def unlock(request: Request) -> dict[str, Any]:
    body = await request.json()
    master_password = body.get("master_password", "")
    if not master_password:
        return {"success": False, "error": "master_password is required"}
    return unlock_vault(master_password)
