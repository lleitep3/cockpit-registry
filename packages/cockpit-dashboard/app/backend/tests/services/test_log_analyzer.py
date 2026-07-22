from __future__ import annotations

import json
import os
from pathlib import Path
from unittest.mock import patch

import pytest

from app.services.log_analyzer import analyze_metrics, load_metrics, load_logs


@pytest.fixture
def fake_cockpit_dir(tmp_path: Path) -> Path:
    cockpit_dir = tmp_path / ".cockpit"
    cockpit_dir.mkdir()
    return cockpit_dir


@pytest.fixture
def set_cockpit_home(fake_cockpit_dir: Path):
    with patch.dict(os.environ, {"COCKPIT_HOME": str(fake_cockpit_dir)}):
        yield


def test_load_metrics_empty(set_cockpit_home: None, fake_cockpit_dir: Path):
    assert load_metrics() == []


def test_load_metrics_returns_data(set_cockpit_home: None, fake_cockpit_dir: Path):
    metrics = [
        {
            "timestamp": "2026-07-12T10:00:00",
            "command": "info",
            "args": [],
            "status": "success",
            "exit_code": 0,
            "duration_ms": 10,
        }
    ]
    (fake_cockpit_dir / "metrics.json").write_text(json.dumps(metrics))
    result = load_metrics()
    assert len(result) == 1
    assert result[0]["command"] == "info"


def test_load_logs_empty(set_cockpit_home: None, fake_cockpit_dir: Path):
    assert load_logs() == []


def test_load_logs_returns_entries(set_cockpit_home: None, fake_cockpit_dir: Path):
    logs_dir = fake_cockpit_dir / "logs"
    logs_dir.mkdir()
    entry = {
        "timestamp": "2026-07-12T10:00:00",
        "level": "INFO",
        "message": "Command executed: info",
        "context": {"command": "info"},
    }
    (logs_dir / "cockpit-2026-07-12.log").write_text(json.dumps(entry) + "\n")
    result = load_logs()
    assert len(result) == 1
    assert result[0]["level"] == "INFO"


def test_analyze_metrics_empty():
    result = analyze_metrics([])
    assert result["total"] == 0
    assert result["success_rate"] == 0.0


def test_analyze_metrics_success_rate():
    metrics = [
        {"command": "info", "status": "success", "duration_ms": 10},
        {"command": "info", "status": "success", "duration_ms": 20},
        {"command": "doctor", "status": "error", "duration_ms": 5, "error_type": "RuntimeError"},
    ]
    result = analyze_metrics(metrics)
    assert result["total"] == 3
    assert result["successful"] == 2
    assert result["failed"] == 1
    assert result["success_rate"] == 66.67
    assert result["avg_duration_ms"] == 11.67
    assert len(result["commands"]) == 2
    assert len(result["error_types"]) == 1
    assert len(result["timeline"]) == 1


def test_load_metrics_invalid_json(set_cockpit_home: None, fake_cockpit_dir: Path):
    (fake_cockpit_dir / "metrics.json").write_text("not json")
    assert load_metrics() == []


def test_load_metrics_not_list(set_cockpit_home: None, fake_cockpit_dir: Path):
    (fake_cockpit_dir / "metrics.json").write_text('{"foo": "bar"}')
    assert load_metrics() == []


def test_load_logs_invalid_json(set_cockpit_home: None, fake_cockpit_dir: Path):
    logs_dir = fake_cockpit_dir / "logs"
    logs_dir.mkdir()
    (logs_dir / "cockpit-2026-07-12.log").write_text("not json\n")
    assert load_logs() == []


def test_analyze_metrics_with_timestamps():
    metrics = [
        {"timestamp": "2026-07-12T10:00:00", "command": "info", "status": "success", "duration_ms": 10},
        {"timestamp": "2026-07-13T10:00:00", "command": "doctor", "status": "error", "duration_ms": 5, "error_type": "RuntimeError"},
    ]
    result = analyze_metrics(metrics)
    assert len(result["timeline"]) == 2
