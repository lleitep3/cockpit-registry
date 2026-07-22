from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import structlog
import yaml

from app.services.cockpit_reader import _cockpit_dir

logger = structlog.get_logger()


def _registries_file() -> Path:
    return _cockpit_dir() / "registries.yml"


def _registry_cache_dir() -> Path:
    return _cockpit_dir() / "cache" / "registries"


def list_registry_packages() -> list[dict[str, Any]]:
    """Lista pacotes disponíveis nos registries a partir do cache local."""
    packages: list[dict[str, Any]] = []
    cache_dir = _registry_cache_dir()
    if not cache_dir.exists():
        logger.warning("registry_cache_not_found", path=str(cache_dir))
        return packages

    for registry_dir in sorted(cache_dir.iterdir()):
        if not registry_dir.is_dir():
            continue
        index_path = registry_dir / "package-index.yaml"
        if not index_path.exists():
            continue
        try:
            with open(index_path, encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
        except Exception as e:
            logger.warning("registry_index_read_error", registry=registry_dir.name, error=str(e))
            continue

        entries = data.get("packages", [])
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            pkg = dict(entry)
            pkg["registry"] = registry_dir.name
            packages.append(pkg)

    return packages


def find_registry_package(name: str) -> dict[str, Any] | None:
    """Busca um pacote específico nos registries."""
    for pkg in list_registry_packages():
        if pkg.get("name") == name:
            return pkg
    return None
