from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml
from fastapi.testclient import TestClient

from app.main import app
from app.routers.packages import _jobs


client = TestClient(app)


def test_get_packages_empty(tmp_path: Path):
    cockpit_dir = tmp_path / ".cockpit"
    cockpit_dir.mkdir()
    with patch.dict(os.environ, {"COCKPIT_HOME": str(cockpit_dir)}):
        response = client.get("/api/v1/packages")
        assert response.status_code == 200
        assert response.json()["packages"] == []


def test_get_registry_empty(tmp_path: Path):
    cockpit_dir = tmp_path / ".cockpit"
    cockpit_dir.mkdir()
    with patch.dict(os.environ, {"COCKPIT_HOME": str(cockpit_dir)}):
        response = client.get("/api/v1/packages/registry")
        assert response.status_code == 200
        assert response.json()["packages"] == []


def test_install_package_missing_name(tmp_path: Path):
    cockpit_dir = tmp_path / ".cockpit"
    cockpit_dir.mkdir()
    with patch.dict(os.environ, {"COCKPIT_HOME": str(cockpit_dir)}):
        response = client.post("/api/v1/packages/install", json={})
        assert response.status_code == 200
        assert "error" in response.json()


def test_install_package_not_found(tmp_path: Path):
    cockpit_dir = tmp_path / ".cockpit"
    cockpit_dir.mkdir()
    with patch.dict(os.environ, {"COCKPIT_HOME": str(cockpit_dir)}):
        response = client.post("/api/v1/packages/install", json={"name": "nonexistent"})
        assert response.status_code == 200
        assert "error" in response.json()


def test_job_not_found(tmp_path: Path):
    cockpit_dir = tmp_path / ".cockpit"
    cockpit_dir.mkdir()
    with patch.dict(os.environ, {"COCKPIT_HOME": str(cockpit_dir)}):
        response = client.get("/api/v1/packages/jobs/invalid-id")
        assert response.status_code == 200
        assert "error" in response.json()


def test_job_stream_not_found(tmp_path: Path):
    cockpit_dir = tmp_path / ".cockpit"
    cockpit_dir.mkdir()
    with patch.dict(os.environ, {"COCKPIT_HOME": str(cockpit_dir)}):
        response = client.get("/api/v1/packages/jobs/invalid-id/stream")
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream; charset=utf-8"


@pytest.fixture(autouse=True)
def clear_jobs():
    _jobs.clear()
    yield
    _jobs.clear()


def test_install_package_success(tmp_path: Path):
    cockpit_dir = tmp_path / ".cockpit"
    cockpit_dir.mkdir()
    cache_dir = cockpit_dir / "cache" / "registries" / "main"
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

    class FakeResult:
        returncode = 0
        stdout = "installed"
        stderr = ""
        duration_ms = 100.0
        success = True

    with patch.dict(os.environ, {"COCKPIT_HOME": str(cockpit_dir)}):
        with patch("app.routers.packages.execute_command", return_value=FakeResult()):
            response = client.post("/api/v1/packages/install", json={"name": "test-pkg"})
            assert response.status_code == 200
            data = response.json()
            assert "job_id" in data
            # Wait a bit for background task to complete
            import time
            time.sleep(0.3)
            job_response = client.get(f"/api/v1/packages/jobs/{data['job_id']}")
            job_data = job_response.json()
            assert job_data["status"] in ("completed", "running")
