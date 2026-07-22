from __future__ import annotations

import os
from unittest.mock import patch

import pytest

from app.core.command_executor import ALLOWED_COMMANDS, execute_command, run_doctor


def test_execute_command_not_allowed():
    with pytest.raises(ValueError, match="command not allowed"):
        execute_command("rm", ["-rf", "/"])


def test_execute_command_invalid_argument():
    with pytest.raises(ValueError, match="argument contains invalid characters"):
        execute_command("doctor", ["; rm -rf"])


def test_execute_command_timeout():
    with patch.dict(ALLOWED_COMMANDS, {"sleep": ["sleep", "10"]}, clear=False):
        result = execute_command("sleep", timeout=0.1)
        assert not result.success
        assert "timed out" in result.stderr


def test_run_doctor_no_cockpit():
    with patch.dict(os.environ, {"PATH": "/nonexistent"}):
        result = run_doctor()
        assert not result["passed"]
        assert result.get("error", "")
