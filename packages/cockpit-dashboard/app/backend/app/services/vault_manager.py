from __future__ import annotations

import json
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import structlog

logger = structlog.get_logger()

NAMESPACE = "cockpit-dashboard"


@dataclass
class VaultSecret:
    key: str
    value: str
    created_at: str


def _vault_index_path() -> Path:
    home = Path.home()
    return Path(os.environ.get("COCKPIT_HOME", home / ".cockpit")) / "vault-index.json"


def _read_index() -> dict[str, Any]:
    path = _vault_index_path()
    if not path.exists():
        return {"secrets": []}
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.warning("vault_index_read_error", error=str(e))
        return {"secrets": []}


def _write_index(data: dict[str, Any]) -> None:
    try:
        _vault_index_path().write_text(json.dumps(data, indent=2), encoding="utf-8")
    except Exception as e:
        logger.error("vault_index_write_error", error=str(e))
        raise


def get_status() -> dict[str, Any]:
    """Retorna status do vault via `cockpit vault status`."""
    try:
        result = subprocess.run(
            ["cockpit", "vault", "status"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        # Fix the substring bug where "LOCKED" is in "UNLOCKED"
        locked = "UNLOCKED" not in result.stdout or result.returncode != 0
        return {"locked": locked, "raw": result.stdout}
    except Exception as e:
        logger.error("vault_status_error", error=str(e))
        return {"locked": True, "raw": str(e)}


def list_secrets() -> list[dict[str, Any]]:
    """Lista secrets do namespace do dashboard."""
    index = _read_index()
    return [
        {"key": s["key"], "created_at": s.get("created_at", "")}
        for s in index.get("secrets", [])
    ]


def add_secret(key: str, value: str, master_password: str) -> dict[str, Any]:
    """Adiciona secret no vault usando namespace isolado."""
    env = os.environ.copy()
    env["COCKPIT_DEV_MODE"] = "true"
    env["COCKPIT_VAULT_MASTER_PASSWORD"] = master_password
    try:
        result = subprocess.run(
            ["cockpit", "vault", "set", key, "--value", value, "--namespace", NAMESPACE],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
            env=env,
        )
        if result.returncode != 0:
            return {"success": False, "error": result.stderr or "failed to store secret"}
        index = _read_index()
        secrets = index.get("secrets", [])
        if not any(s["key"] == key for s in secrets):
            secrets.append({"key": key, "created_at": __import__("datetime").datetime.now().isoformat()})
        index["secrets"] = secrets
        _write_index(index)
        return {"success": True}
    except Exception as e:
        logger.error("vault_add_error", error=str(e))
        return {"success": False, "error": str(e)}


def get_secret(key: str, master_password: str) -> dict[str, Any]:
    """Recupera secret do vault."""
    env = os.environ.copy()
    env["COCKPIT_DEV_MODE"] = "true"
    env["COCKPIT_VAULT_MASTER_PASSWORD"] = master_password
    try:
        result = subprocess.run(
            ["cockpit", "vault", "get", key, "--namespace", NAMESPACE],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
            env=env,
        )
        if result.returncode != 0:
            return {"success": False, "error": result.stderr or "failed to retrieve secret"}
        return {"success": True, "value": result.stdout}
    except Exception as e:
        logger.error("vault_get_error", error=str(e))
        return {"success": False, "error": str(e)}


def lock_vault(master_password: str) -> dict[str, Any]:
    env = os.environ.copy()
    env["COCKPIT_DEV_MODE"] = "true"
    env["COCKPIT_VAULT_MASTER_PASSWORD"] = master_password
    try:
        result = subprocess.run(
            ["cockpit", "vault", "lock"],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
            env=env,
        )
        return {"success": result.returncode == 0, "error": result.stderr if result.returncode != 0 else None}
    except Exception as e:
        return {"success": False, "error": str(e)}


def unlock_vault(master_password: str) -> dict[str, Any]:
    env = os.environ.copy()
    env["COCKPIT_DEV_MODE"] = "true"
    env["COCKPIT_VAULT_MASTER_PASSWORD"] = master_password
    try:
        result = subprocess.run(
            ["cockpit", "vault", "unlock"],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
            env=env,
        )
        return {"success": result.returncode == 0, "error": result.stderr if result.returncode != 0 else None}
    except Exception as e:
        return {"success": False, "error": str(e)}
