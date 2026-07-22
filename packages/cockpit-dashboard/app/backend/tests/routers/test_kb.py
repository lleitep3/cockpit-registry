from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_kb_empty(tmp_path: Path):
    cockpit_dir = tmp_path / ".cockpit"
    cockpit_dir.mkdir()
    with patch.dict(os.environ, {"COCKPIT_HOME": str(cockpit_dir)}):
        response = client.get("/api/v1/kb")
        assert response.status_code == 200
        assert response.json()["documents"] == []


def test_kb_graph_empty(tmp_path: Path):
    cockpit_dir = tmp_path / ".cockpit"
    cockpit_dir.mkdir()
    with patch.dict(os.environ, {"COCKPIT_HOME": str(cockpit_dir)}):
        response = client.get("/api/v1/kb/graph")
        assert response.status_code == 200
        assert response.json()["nodes"] == []


def test_kb_search(tmp_path: Path):
    cockpit_dir = tmp_path / ".cockpit"
    kb_dir = cockpit_dir / "kb"
    kb_dir.mkdir(parents=True)
    (kb_dir / "test.md").write_text("hello world")
    with patch.dict(os.environ, {"COCKPIT_HOME": str(cockpit_dir)}):
        response = client.get("/api/v1/kb/search?query=hello")
        assert response.status_code == 200
        assert len(response.json()["results"]) == 1


def test_kb_search_missing_query(tmp_path: Path):
    cockpit_dir = tmp_path / ".cockpit"
    cockpit_dir.mkdir()
    with patch.dict(os.environ, {"COCKPIT_HOME": str(cockpit_dir)}):
        response = client.get("/api/v1/kb/search")
        assert response.status_code == 422
