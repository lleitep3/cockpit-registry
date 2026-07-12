from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from app.services.registry_reader import find_registry_package, list_registry_packages


@pytest.fixture
def fake_cockpit_dir(tmp_path: Path) -> Path:
    cockpit_dir = tmp_path / ".cockpit"
    cockpit_dir.mkdir()
    return cockpit_dir


@pytest.fixture
def set_cockpit_home(fake_cockpit_dir: Path):
    with patch.dict(os.environ, {"COCKPIT_HOME": str(fake_cockpit_dir)}):
        yield


def test_list_registry_packages_empty(set_cockpit_home: None, fake_cockpit_dir: Path):
    assert list_registry_packages() == []


def test_list_registry_packages_from_cache(set_cockpit_home: None, fake_cockpit_dir: Path):
    cache_dir = fake_cockpit_dir / "cache" / "registries" / "main"
    cache_dir.mkdir(parents=True)
    index = {
        "packages": [
            {
                "name": "test-pkg",
                "version": "0.1.0",
                "author": "dev",
                "description": "Test",
                "category": "test",
                "status": "stable",
            }
        ]
    }
    (cache_dir / "package-index.yaml").write_text(yaml.safe_dump(index))
    result = list_registry_packages()
    assert len(result) == 1
    assert result[0]["name"] == "test-pkg"
    assert result[0]["registry"] == "main"


def test_find_registry_package(set_cockpit_home: None, fake_cockpit_dir: Path):
    cache_dir = fake_cockpit_dir / "cache" / "registries" / "main"
    cache_dir.mkdir(parents=True)
    index = {"packages": [{"name": "find-me", "version": "1.0.0"}]}
    (cache_dir / "package-index.yaml").write_text(yaml.safe_dump(index))
    pkg = find_registry_package("find-me")
    assert pkg is not None
    assert pkg["version"] == "1.0.0"
