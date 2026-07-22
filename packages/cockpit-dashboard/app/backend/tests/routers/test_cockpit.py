from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_status_empty(tmp_path: Path):
    cockpit_dir = tmp_path / ".cockpit"
    cockpit_dir.mkdir()
    with patch.dict(os.environ, {"COCKPIT_HOME": str(cockpit_dir)}):
        response = client.get("/api/v1/cockpit/status")
        assert response.status_code == 200
        assert response.json()["active"] is True


def test_packages_empty(tmp_path: Path):
    cockpit_dir = tmp_path / ".cockpit"
    cockpit_dir.mkdir()
    with patch.dict(os.environ, {"COCKPIT_HOME": str(cockpit_dir)}):
        response = client.get("/api/v1/cockpit/packages")
        assert response.status_code == 200
        assert response.json()["packages"] == []


def test_registries_empty(tmp_path: Path):
    cockpit_dir = tmp_path / ".cockpit"
    cockpit_dir.mkdir()
    with patch.dict(os.environ, {"COCKPIT_HOME": str(cockpit_dir)}):
        response = client.get("/api/v1/cockpit/registries")
        assert response.status_code == 200
        assert response.json()["registries"] == []


def test_kb_empty(tmp_path: Path):
    cockpit_dir = tmp_path / ".cockpit"
    cockpit_dir.mkdir()
    with patch.dict(os.environ, {"COCKPIT_HOME": str(cockpit_dir)}):
        response = client.get("/api/v1/cockpit/kb")
        assert response.status_code == 200
        assert response.json()["documents"] == []
