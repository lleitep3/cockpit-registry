from __future__ import annotations

import os
import subprocess
from pathlib import Path
from unittest.mock import patch

from app.services.vault_manager import (
    _read_index,
    _write_index,
    add_secret,
    get_secret,
    get_status,
    list_secrets,
    lock_vault,
    unlock_vault,
)


def test_read_index_empty(tmp_path: Path):
    cockpit_dir = tmp_path / ".cockpit"
    cockpit_dir.mkdir()
    with patch.dict(os.environ, {"COCKPIT_HOME": str(cockpit_dir)}):
        assert _read_index() == {"secrets": []}


def test_write_and_read_index(tmp_path: Path):
    cockpit_dir = tmp_path / ".cockpit"
    cockpit_dir.mkdir()
    with patch.dict(os.environ, {"COCKPIT_HOME": str(cockpit_dir)}):
        data = {"secrets": [{"key": "api", "created_at": "2024-01-01"}]}
        _write_index(data)
        assert _read_index() == data


def test_list_secrets_empty(tmp_path: Path):
    cockpit_dir = tmp_path / ".cockpit"
    cockpit_dir.mkdir()
    with patch.dict(os.environ, {"COCKPIT_HOME": str(cockpit_dir)}):
        assert list_secrets() == []


def test_get_status_no_cockpit(tmp_path: Path):
    cockpit_dir = tmp_path / ".cockpit"
    cockpit_dir.mkdir()
    with patch.dict(os.environ, {"COCKPIT_HOME": str(cockpit_dir), "PATH": "/nonexistent"}):
        status = get_status()
        assert status["locked"] is True


def test_add_secret_missing_args(tmp_path: Path):
    cockpit_dir = tmp_path / ".cockpit"
    cockpit_dir.mkdir()
    with patch.dict(os.environ, {"COCKPIT_HOME": str(cockpit_dir)}):
        assert add_secret("", "value", "pass")["success"] is False
        assert add_secret("key", "", "pass")["success"] is False


def test_get_secret_missing_args(tmp_path: Path):
    cockpit_dir = tmp_path / ".cockpit"
    cockpit_dir.mkdir()
    with patch.dict(os.environ, {"COCKPIT_HOME": str(cockpit_dir)}):
        assert get_secret("", "pass")["success"] is False


def test_add_secret_mocked(tmp_path: Path):
    cockpit_dir = tmp_path / ".cockpit"
    cockpit_dir.mkdir()
    class FakeResult:
        returncode = 0
        stdout = "ok"
        stderr = ""
        success = True
    with patch.dict(os.environ, {"COCKPIT_HOME": str(cockpit_dir)}):
        with patch("app.services.vault_manager.subprocess.run", return_value=FakeResult()):
            res = add_secret("api-key", "secret", "pass")
            assert res["success"] is True
            assert len(list_secrets()) == 1


def test_get_secret_mocked(tmp_path: Path):
    cockpit_dir = tmp_path / ".cockpit"
    cockpit_dir.mkdir()
    class FakeResult:
        returncode = 0
        stdout = "secret-value"
        stderr = ""
        success = True
    with patch.dict(os.environ, {"COCKPIT_HOME": str(cockpit_dir)}):
        with patch("app.services.vault_manager.subprocess.run", return_value=FakeResult()):
            res = get_secret("api-key", "pass")
            assert res["success"] is True
            assert res["value"] == "secret-value"


def test_lock_vault_mocked(tmp_path: Path):
    cockpit_dir = tmp_path / ".cockpit"
    cockpit_dir.mkdir()
    class FakeResult:
        returncode = 0
        stdout = "locked"
        stderr = ""
        success = True
    with patch.dict(os.environ, {"COCKPIT_HOME": str(cockpit_dir)}):
        with patch("app.services.vault_manager.subprocess.run", return_value=FakeResult()):
            res = lock_vault("pass")
            assert res["success"] is True


def test_unlock_vault_mocked(tmp_path: Path):
    cockpit_dir = tmp_path / ".cockpit"
    cockpit_dir.mkdir()
    class FakeResult:
        returncode = 0
        stdout = "unlocked"
        stderr = ""
        success = True
    with patch.dict(os.environ, {"COCKPIT_HOME": str(cockpit_dir)}):
        with patch("app.services.vault_manager.subprocess.run", return_value=FakeResult()):
            res = unlock_vault("pass")
            assert res["success"] is True


def test_lock_vault_missing_password(tmp_path: Path):
    cockpit_dir = tmp_path / ".cockpit"
    cockpit_dir.mkdir()
    with patch.dict(os.environ, {"COCKPIT_HOME": str(cockpit_dir)}):
        res = lock_vault("")
        assert res["success"] is False
