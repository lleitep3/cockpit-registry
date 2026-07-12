from __future__ import annotations

import json
import os
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_get_logs_insights_empty(tmp_path: Path):
    cockpit_dir = tmp_path / ".cockpit"
    cockpit_dir.mkdir()
    with patch.dict(os.environ, {"COCKPIT_HOME": str(cockpit_dir)}):
        response = client.get("/api/v1/logs/insights")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0


def test_get_logs_insights_with_data(tmp_path: Path):
    cockpit_dir = tmp_path / ".cockpit"
    cockpit_dir.mkdir()
    metrics = [
        {"timestamp": "2026-07-12T10:00:00", "command": "info", "status": "success", "duration_ms": 10},
    ]
    (cockpit_dir / "metrics.json").write_text(json.dumps(metrics))
    with patch.dict(os.environ, {"COCKPIT_HOME": str(cockpit_dir)}):
        response = client.get("/api/v1/logs/insights")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["successful"] == 1
        assert data["success_rate"] == 100.0


def test_get_logs_empty(tmp_path: Path):
    cockpit_dir = tmp_path / ".cockpit"
    cockpit_dir.mkdir()
    with patch.dict(os.environ, {"COCKPIT_HOME": str(cockpit_dir)}):
        response = client.get("/api/v1/logs")
        assert response.status_code == 200
        assert response.json()["logs"] == []


def test_get_metrics_empty(tmp_path: Path):
    cockpit_dir = tmp_path / ".cockpit"
    cockpit_dir.mkdir()
    with patch.dict(os.environ, {"COCKPIT_HOME": str(cockpit_dir)}):
        response = client.get("/api/v1/logs/metrics")
        assert response.status_code == 200
        assert response.json()["metrics"] == []
