from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import structlog
import yaml

logger = structlog.get_logger()


def _cockpit_dir() -> Path:
    home = Path.home()
    return Path(os.environ.get("COCKPIT_HOME", home / ".cockpit"))


def read_config() -> dict[str, Any]:
    """Lê ~/.cockpit/config.yml."""
    path = _cockpit_dir() / "config.yml"
    if not path.exists():
        logger.warning("config_not_found", path=str(path))
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        logger.error("config_read_error", error=str(e))
        return {}


def list_packages() -> list[dict[str, Any]]:
    """Lista pacotes instalados em ~/.cockpit/packages/."""
    packages_dir = _cockpit_dir() / "packages"
    if not packages_dir.exists():
        return []
    packages: list[dict[str, Any]] = []
    for entry in sorted(packages_dir.iterdir()):
        if not entry.is_dir():
            continue
        manifest = entry / "cockpit-package.yml"
        pkg = {"name": entry.name, "path": str(entry), "version": None, "status": "installed"}
        if manifest.exists():
            try:
                with open(manifest, encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}
                pkg["version"] = data.get("version")
                pkg["description"] = data.get("description")
            except Exception as e:
                logger.warning("manifest_read_error", package=entry.name, error=str(e))
        packages.append(pkg)
    return packages


def list_registries() -> list[dict[str, Any]]:
    """Lê ~/.cockpit/registries.yml."""
    path = _cockpit_dir() / "registries.yml"
    if not path.exists():
        return []
    try:
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    except Exception as e:
        logger.error("registries_read_error", error=str(e))
        return []

    registries = data.get("registries", data)
    if isinstance(registries, dict):
        return [
            {"name": name, **info}
            for name, info in registries.items()
            if isinstance(info, dict)
        ]
    if isinstance(registries, list):
        return registries
    return []


def list_kb() -> list[dict[str, Any]]:
    """Lista documentos da KB em ~/.cockpit/kb/."""
    kb_dir = _cockpit_dir() / "kb"
    if not kb_dir.exists():
        return []
    docs: list[dict[str, Any]] = []
    for root, _dirs, files in os.walk(kb_dir):
        for file in sorted(files):
            if not file.endswith(".md"):
                continue
            path = Path(root) / file
            rel = path.relative_to(kb_dir)
            docs.append(
                {
                    "name": path.stem,
                    "category": str(rel.parent) if str(rel.parent) != "." else "general",
                    "path": str(path),
                }
            )
    return docs


def read_status() -> dict[str, Any]:
    """Monta o status geral do cockpit."""
    config = read_config()
    return {
        "version": config.get("version", "unknown"),
        "environment": config.get("environment", "development"),
        "active": True,
        "uptime": "unknown",
    }
