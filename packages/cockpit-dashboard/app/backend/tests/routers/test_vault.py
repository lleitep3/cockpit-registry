from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_vault_status_empty(tmp_path: Path):
    cockpit_dir = tmp_path / ".cockpit"
    cockpit_dir.mkdir()
    with patch.dict(os.environ, {"COCKPIT_HOME": str(cockpit_dir), "PATH": "/nonexistent"}):
        response = client.get("/api/v1/vault/status")
        assert response.status_code == 200
        assert response.json()["locked"] is True


def test_vault_secrets_empty(tmp_path: Path):
    cockpit_dir = tmp_path / ".cockpit"
    cockpit_dir.mkdir()
    with patch.dict(os.environ, {"COCKPIT_HOME": str(cockpit_dir)}):
        response = client.get("/api/v1/vault/secrets")
        assert response.status_code == 200
        assert response.json()["secrets"] == []


def test_vault_create_missing_fields(tmp_path: Path):
    cockpit_dir = tmp_path / ".cockpit"
    cockpit_dir.mkdir()
    with patch.dict(os.environ, {"COCKPIT_HOME": str(cockpit_dir)}):
        response = client.post("/api/v1/vault/secrets", json={})
        assert response.status_code == 200
        assert response.json()["success"] is False


def test_vault_reveal_missing_fields(tmp_path: Path):
    cockpit_dir = tmp_path / ".cockpit"
    cockpit_dir.mkdir()
    with patch.dict(os.environ, {"COCKPIT_HOME": str(cockpit_dir)}):
        response = client.post("/api/v1/vault/secrets/reveal", json={})
        assert response.status_code == 200
        assert response.json()["success"] is False


def test_vault_lock_missing_password(tmp_path: Path):
    cockpit_dir = tmp_path / ".cockpit"
    cockpit_dir.mkdir()
    with patch.dict(os.environ, {"COCKPIT_HOME": str(cockpit_dir)}):
        response = client.post("/api/v1/vault/lock", json={})
        assert response.status_code == 200
        assert response.json()["success"] is False


def test_vault_unlock_missing_password(tmp_path: Path):
    cockpit_dir = tmp_path / ".cockpit"
    cockpit_dir.mkdir()
    with patch.dict(os.environ, {"COCKPIT_HOME": str(cockpit_dir)}):
        response = client.post("/api/v1/vault/unlock", json={})
        assert response.status_code == 200
        assert response.json()["success"] is False
