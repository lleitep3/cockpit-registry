from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.routers.mini_apps import _safe_name


client = TestClient(app)


class FakeSuccess:
    returncode = 0
    stdout = "ok"
    stderr = ""
    duration_ms = 100.0
    success = True


class FakeFailure:
    returncode = 1
    stdout = ""
    stderr = "error"
    duration_ms = 100.0
    success = False


def test_list_mini_apps_empty(tmp_path: Path):
    cockpit_dir = tmp_path / ".cockpit"
    cockpit_dir.mkdir()
    with patch.dict(os.environ, {"COCKPIT_HOME": str(cockpit_dir)}):
        response = client.get("/api/v1/mini-apps")
        assert response.status_code == 200
        assert response.json()["mini_apps"] == []


def test_get_mini_app_invalid_name(tmp_path: Path):
    cockpit_dir = tmp_path / ".cockpit"
    cockpit_dir.mkdir()
    with patch.dict(os.environ, {"COCKPIT_HOME": str(cockpit_dir)}):
        response = client.get("/api/v1/mini-apps/bad name")
        assert response.status_code == 400


def test_get_mini_app_not_found(tmp_path: Path):
    cockpit_dir = tmp_path / ".cockpit"
    cockpit_dir.mkdir()
    with patch.dict(os.environ, {"COCKPIT_HOME": str(cockpit_dir)}):
        response = client.get("/api/v1/mini-apps/nonexistent")
        assert response.status_code == 404


def test_mini_app_start_invalid_name(tmp_path: Path):
    cockpit_dir = tmp_path / ".cockpit"
    cockpit_dir.mkdir()
    with patch.dict(os.environ, {"COCKPIT_HOME": str(cockpit_dir)}):
        response = client.post("/api/v1/mini-apps/bad name/start")
        assert response.status_code == 400


def test_mini_app_logs_invalid_service(tmp_path: Path):
    cockpit_dir = tmp_path / ".cockpit"
    cockpit_dir.mkdir()
    with patch.dict(os.environ, {"COCKPIT_HOME": str(cockpit_dir)}):
        response = client.get("/api/v1/mini-apps/test/logs/stream?service=invalid")
        assert response.status_code == 400


def test_mini_app_metrics_not_found(tmp_path: Path):
    cockpit_dir = tmp_path / ".cockpit"
    cockpit_dir.mkdir()
    with patch.dict(os.environ, {"COCKPIT_HOME": str(cockpit_dir)}):
        response = client.get("/api/v1/mini-apps/nonexistent/metrics")
        assert response.status_code == 404


def test_mini_app_metrics_invalid_name(tmp_path: Path):
    cockpit_dir = tmp_path / ".cockpit"
    cockpit_dir.mkdir()
    with patch.dict(os.environ, {"COCKPIT_HOME": str(cockpit_dir)}):
        response = client.get("/api/v1/mini-apps/bad name/metrics")
        assert response.status_code == 400


def test_mini_app_logs_invalid_name(tmp_path: Path):
    cockpit_dir = tmp_path / ".cockpit"
    cockpit_dir.mkdir()
    with patch.dict(os.environ, {"COCKPIT_HOME": str(cockpit_dir)}):
        response = client.get("/api/v1/mini-apps/bad name/logs/stream?service=backend")
        assert response.status_code == 400


def test_start_success(tmp_path: Path):
    cockpit_dir = tmp_path / ".cockpit"
    workspace = cockpit_dir / "workspace" / "mini-apps" / "app"
    workspace.mkdir(parents=True)
    with patch.dict(os.environ, {"COCKPIT_HOME": str(cockpit_dir)}):
        with patch("app.routers.mini_apps.execute_command", return_value=FakeSuccess()):
            response = client.post("/api/v1/mini-apps/app/start")
            assert response.status_code == 200
            assert response.json()["success"] is True


def test_stop_failure(tmp_path: Path):
    cockpit_dir = tmp_path / ".cockpit"
    workspace = cockpit_dir / "workspace" / "mini-apps" / "app"
    workspace.mkdir(parents=True)
    with patch.dict(os.environ, {"COCKPIT_HOME": str(cockpit_dir)}):
        with patch("app.routers.mini_apps.execute_command", return_value=FakeFailure()):
            response = client.post("/api/v1/mini-apps/app/stop")
            assert response.status_code == 200
            assert response.json()["success"] is False


def test_restart_success(tmp_path: Path):
    cockpit_dir = tmp_path / ".cockpit"
    workspace = cockpit_dir / "workspace" / "mini-apps" / "app"
    workspace.mkdir(parents=True)
    with patch.dict(os.environ, {"COCKPIT_HOME": str(cockpit_dir)}):
        with patch("app.routers.mini_apps.execute_command", return_value=FakeSuccess()):
            response = client.post("/api/v1/mini-apps/app/restart")
            assert response.status_code == 200
            assert response.json()["success"] is True




def test_get_one_success(tmp_path: Path):
    cockpit_dir = tmp_path / ".cockpit"
    workspace = cockpit_dir / "workspace" / "mini-apps" / "app"
    workspace.mkdir(parents=True)
    (workspace / ".env").write_text("BACKEND_PORT=9999\n")
    with patch.dict(os.environ, {"COCKPIT_HOME": str(cockpit_dir)}):
        response = client.get("/api/v1/mini-apps/app")
        assert response.status_code == 200
        assert response.json()["name"] == "app"


def test_metrics_success(tmp_path: Path):
    cockpit_dir = tmp_path / ".cockpit"
    workspace = cockpit_dir / "workspace" / "mini-apps" / "app"
    workspace.mkdir(parents=True)
    (workspace / ".env").write_text("BACKEND_PORT=9999\n")
    pids = workspace / ".pids"
    pids.mkdir(parents=True)
    (pids / "backend.pid").write_text(str(os.getpid()))
    with patch.dict(os.environ, {"COCKPIT_HOME": str(cockpit_dir)}):
        response = client.get("/api/v1/mini-apps/app/metrics")
        assert response.status_code == 200
        data = response.json()
        assert "cpu_seconds" in data
        assert "memory_kb" in data


import asyncio
from app.routers.mini_apps import _log_event_generator, stream_logs


def test_log_event_generator(tmp_path: Path):
    log_file = tmp_path / "backend.log"
    log_file.write_text("line1\n")

    async def collect():
        gen = _log_event_generator(str(log_file))
        events = []
        for _ in range(5):
            try:
                item = await asyncio.wait_for(gen.__anext__(), timeout=0.5)
                events.append(item)
            except asyncio.TimeoutError:
                break
        return events

    events = asyncio.get_event_loop().run_until_complete(collect())
    assert len(events) > 0
    assert "line1" in events[0]


def test_log_event_generator_missing_file(tmp_path: Path):
    log_file = tmp_path / "missing.log"

    async def collect():
        gen = _log_event_generator(str(log_file))
        events = []
        for _ in range(3):
            try:
                item = await asyncio.wait_for(gen.__anext__(), timeout=0.5)
                events.append(item)
            except asyncio.TimeoutError:
                break
        return events

    events = asyncio.get_event_loop().run_until_complete(collect())
    assert events == []


def test_stream_logs_direct():
    async def run():
        response = await stream_logs("app", "backend")
        return response

    response = asyncio.get_event_loop().run_until_complete(run())
    assert response.status_code == 200
    assert response.media_type == "text/event-stream"


