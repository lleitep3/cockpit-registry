from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from app.services.cockpit_reader import (
    list_kb,
    list_packages,
    list_registries,
    read_config,
    read_status,
)


@pytest.fixture
def fake_cockpit_dir(tmp_path: Path) -> Path:
    cockpit_dir = tmp_path / ".cockpit"
    cockpit_dir.mkdir()
    return cockpit_dir


@pytest.fixture
def set_cockpit_home(fake_cockpit_dir: Path):
    with patch.dict(os.environ, {"COCKPIT_HOME": str(fake_cockpit_dir)}):
        yield


def test_read_config_missing(set_cockpit_home: None, fake_cockpit_dir: Path):
    assert read_config() == {}


def test_read_config_present(set_cockpit_home: None, fake_cockpit_dir: Path):
    config = {"version": "1.0.0", "environment": "test"}
    (fake_cockpit_dir / "config.yml").write_text(yaml.safe_dump(config))
    assert read_config() == config


def test_list_packages_empty(set_cockpit_home: None, fake_cockpit_dir: Path):
    assert list_packages() == []


def test_list_packages_with_manifest(set_cockpit_home: None, fake_cockpit_dir: Path):
    pkg_dir = fake_cockpit_dir / "packages" / "test-pkg"
    pkg_dir.mkdir(parents=True)
    manifest = {"version": "0.1.0", "description": "Test package"}
    (pkg_dir / "cockpit-package.yml").write_text(yaml.safe_dump(manifest))
    result = list_packages()
    assert len(result) == 1
    assert result[0]["name"] == "test-pkg"
    assert result[0]["version"] == "0.1.0"


def test_list_registries_empty(set_cockpit_home: None, fake_cockpit_dir: Path):
    assert list_registries() == []


def test_list_registries_with_list(set_cockpit_home: None, fake_cockpit_dir: Path):
    data = {"registries": [{"name": "main", "url": "https://example.com"}]}
    (fake_cockpit_dir / "registries.yml").write_text(yaml.safe_dump(data))
    result = list_registries()
    assert len(result) == 1
    assert result[0]["name"] == "main"


def test_list_kb_empty(set_cockpit_home: None, fake_cockpit_dir: Path):
    assert list_kb() == []


def test_list_kb_with_docs(set_cockpit_home: None, fake_cockpit_dir: Path):
    kb_dir = fake_cockpit_dir / "kb"
    kb_dir.mkdir()
    (kb_dir / "guide.md").write_text("# Guide")
    sub = kb_dir / "sub"
    sub.mkdir()
    (sub / "note.md").write_text("# Note")
    result = list_kb()
    assert len(result) == 2
    names = {doc["name"] for doc in result}
    assert names == {"guide", "note"}


def test_read_status(set_cockpit_home: None, fake_cockpit_dir: Path):
    status = read_status()
    assert status["active"] is True
    assert status["version"] == "unknown"


def test_read_config_invalid_yaml(set_cockpit_home: None, fake_cockpit_dir: Path):
    (fake_cockpit_dir / "config.yml").write_text("invalid: yaml: :")
    assert read_config() == {}


def test_list_packages_invalid_manifest(set_cockpit_home: None, fake_cockpit_dir: Path):
    pkg_dir = fake_cockpit_dir / "packages" / "test-pkg"
    pkg_dir.mkdir(parents=True)
    (pkg_dir / "cockpit-package.yml").write_text("invalid: yaml: :")
    result = list_packages()
    assert len(result) == 1
    assert result[0]["version"] is None


def test_list_registries_dict(set_cockpit_home: None, fake_cockpit_dir: Path):
    data = {"main": {"url": "https://example.com"}}
    (fake_cockpit_dir / "registries.yml").write_text(yaml.safe_dump(data))
    result = list_registries()
    assert len(result) == 1
    assert result[0]["name"] == "main"


def test_list_registries_invalid(set_cockpit_home: None, fake_cockpit_dir: Path):
    (fake_cockpit_dir / "registries.yml").write_text("invalid: yaml: :")
    assert list_registries() == []


async def test_providers_list(set_cockpit_home: None, fake_cockpit_dir: Path):
    from app.routers.cockpit import providers
    data = {"providers": [{"name": "p1", "active": True}]}
    (fake_cockpit_dir / "config.yml").write_text(yaml.safe_dump(data))
    response = await providers()
    assert response["providers"] == [{"name": "p1", "active": True}]


async def test_providers_dict(set_cockpit_home: None, fake_cockpit_dir: Path):
    from app.routers.cockpit import providers
    data = {"providers": {"p1": {"active": True}}}
    (fake_cockpit_dir / "config.yml").write_text(yaml.safe_dump(data))
    response = await providers()
    assert response["providers"] == [{"name": "p1", "active": True}]
