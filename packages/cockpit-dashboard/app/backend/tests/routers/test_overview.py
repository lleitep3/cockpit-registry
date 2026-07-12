from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_overview_kpi_empty(tmp_path: Path):
    cockpit_dir = tmp_path / ".cockpit"
    cockpit_dir.mkdir()
    with patch.dict(os.environ, {"COCKPIT_HOME": str(cockpit_dir)}):
        response = client.get("/api/v1/overview/kpi")
        assert response.status_code == 200
        data = response.json()
        assert data["packages_total"] == 0
        assert data["kb_total"] == 0
        assert data["executions_total"] == 0


def test_overview_doctor(tmp_path: Path):
    cockpit_dir = tmp_path / ".cockpit"
    cockpit_dir.mkdir()
    with patch.dict(os.environ, {"COCKPIT_HOME": str(cockpit_dir)}):
        response = client.get("/api/v1/overview/doctor")
        assert response.status_code == 200
        data = response.json()
        assert "passed" in data
        assert "checks" in data
