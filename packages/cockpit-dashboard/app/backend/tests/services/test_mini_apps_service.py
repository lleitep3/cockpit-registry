from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

from app.services.mini_apps import _is_port_open, _read_pid, _read_port, list_mini_apps, read_logs


def test_list_mini_apps_empty(tmp_path: Path):
    cockpit_dir = tmp_path / ".cockpit"
    cockpit_dir.mkdir()
    with patch.dict(os.environ, {"COCKPIT_HOME": str(cockpit_dir)}):
        assert list_mini_apps() == []


def test_list_mini_apps_with_stopped_app(tmp_path: Path):
    cockpit_dir = tmp_path / ".cockpit"
    workspace = cockpit_dir / "workspace" / "mini-apps" / "stopped-app"
    workspace.mkdir(parents=True)
    (workspace / ".env").write_text("BACKEND_PORT=8000\n")
    with patch.dict(os.environ, {"COCKPIT_HOME": str(cockpit_dir)}):
        apps = list_mini_apps()
        assert len(apps) == 1
        assert apps[0]["name"] == "stopped-app"
        assert apps[0]["status"] == "stopped"


def test_read_port_missing(tmp_path: Path):
    cockpit_dir = tmp_path / ".cockpit"
    workspace = cockpit_dir / "workspace" / "mini-apps" / "no-port"
    workspace.mkdir(parents=True)
    with patch.dict(os.environ, {"COCKPIT_HOME": str(cockpit_dir)}):
        assert _read_port(workspace) is None


def test_read_port_found(tmp_path: Path):
    cockpit_dir = tmp_path / ".cockpit"
    workspace = cockpit_dir / "workspace" / "mini-apps" / "port-app"
    workspace.mkdir(parents=True)
    (workspace / ".env").write_text("BACKEND_PORT=8001\nFRONTEND_PORT=3001\n")
    with patch.dict(os.environ, {"COCKPIT_HOME": str(cockpit_dir)}):
        assert _read_port(workspace) == 8001


def test_read_pid_invalid(tmp_path: Path):
    cockpit_dir = tmp_path / ".cockpit"
    workspace = cockpit_dir / "workspace" / "mini-apps" / "pid-app"
    pids = workspace / ".pids"
    pids.mkdir(parents=True)
    (pids / "backend.pid").write_text("not-a-number")
    with patch.dict(os.environ, {"COCKPIT_HOME": str(cockpit_dir)}):
        assert _read_pid(pids / "backend.pid") is None


def test_read_logs(tmp_path: Path):
    cockpit_dir = tmp_path / ".cockpit"
    workspace = cockpit_dir / "workspace" / "mini-apps" / "log-app"
    workspace.mkdir(parents=True)
    (workspace / "backend.log").write_text("a\nb\nc\n")
    with patch.dict(os.environ, {"COCKPIT_HOME": str(cockpit_dir)}):
        assert read_logs("log-app", "backend", 2) == ["b\n", "c\n"]


def test_read_logs_missing(tmp_path: Path):
    cockpit_dir = tmp_path / ".cockpit"
    cockpit_dir.mkdir()
    with patch.dict(os.environ, {"COCKPIT_HOME": str(cockpit_dir)}):
        assert read_logs("missing", "backend") == []


def test_is_port_open_false():
    assert _is_port_open(0) is False


def test_read_pid_valid(tmp_path: Path):
    cockpit_dir = tmp_path / ".cockpit"
    workspace = cockpit_dir / "workspace" / "mini-apps" / "pid-app"
    pids = workspace / ".pids"
    pids.mkdir(parents=True)
    (pids / "backend.pid").write_text(str(os.getpid()))
    with patch.dict(os.environ, {"COCKPIT_HOME": str(cockpit_dir)}):
        assert _read_pid(pids / "backend.pid") == os.getpid()


def test_list_mini_apps_running_with_uptime(tmp_path: Path):
    cockpit_dir = tmp_path / ".cockpit"
    workspace = cockpit_dir / "workspace" / "mini-apps" / "running-app"
    workspace.mkdir(parents=True)
    (workspace / ".env").write_text("BACKEND_PORT=8000\n")
    pids = workspace / ".pids"
    pids.mkdir(parents=True)
    (pids / "backend.pid").write_text(str(os.getpid()))
    with patch.dict(os.environ, {"COCKPIT_HOME": str(cockpit_dir)}):
        with patch("app.services.mini_apps._is_port_open", return_value=True):
            apps = list_mini_apps()
            assert len(apps) == 1
            assert apps[0]["status"] == "running"
            assert apps[0]["health"] is True
            assert apps[0]["uptime"] is not None


def test_read_logs_exception(tmp_path: Path):
    cockpit_dir = tmp_path / ".cockpit"
    workspace = cockpit_dir / "workspace" / "mini-apps" / "log-app"
    workspace.mkdir(parents=True)
    log_file = workspace / "backend.log"
    log_file.write_text("x\n")
    # Make file unreadable by removing read permissions
    log_file.chmod(0o000)
    try:
        with patch.dict(os.environ, {"COCKPIT_HOME": str(cockpit_dir)}):
            assert read_logs("log-app", "backend") == []
    finally:
        log_file.chmod(0o644)
