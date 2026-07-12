from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass, field
from typing import Any

import structlog

logger = structlog.get_logger()


ALLOWED_COMMANDS: dict[str, list[str]] = {
    "doctor": ["cockpit", "doctor", "--json"],
}

# Restrictive regex for names/keys passed as arguments.
SAFE_NAME_RE = re.compile(r"^[a-z0-9_.-]+$")


@dataclass
class ExecutionResult:
    command: str
    args: list[str] = field(default_factory=list)
    returncode: int = 0
    stdout: str = ""
    stderr: str = ""
    duration_ms: float = 0.0
    success: bool = False


def _validate_command(name: str, extra_args: list[str]) -> list[str]:
    """Valida e monta a lista de argumentos para execução."""
    if name not in ALLOWED_COMMANDS:
        raise ValueError(f"command not allowed: {name}")

    base = list(ALLOWED_COMMANDS[name])
    for arg in extra_args:
        if not SAFE_NAME_RE.match(arg):
            raise ValueError(f"argument contains invalid characters: {arg}")
        base.append(arg)
    return base


def execute_command(name: str, extra_args: list[str] | None = None, timeout: int = 30) -> ExecutionResult:
    """Executa um comando do cockpit whitelistado de forma segura."""
    extra_args = extra_args or []
    cmd = _validate_command(name, extra_args)

    start = __import__("time").time()
    logger.info("command_start", command=name, args=extra_args)
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        duration_ms = (__import__("time").time() - start) * 1000
        result = ExecutionResult(
            command=name,
            args=extra_args,
            returncode=proc.returncode,
            stdout=proc.stdout,
            stderr=proc.stderr,
            duration_ms=round(duration_ms, 2),
            success=proc.returncode == 0,
        )
        logger.info(
            "command_end",
            command=name,
            returncode=proc.returncode,
            duration_ms=result.duration_ms,
        )
        return result
    except subprocess.TimeoutExpired:
        logger.error("command_timeout", command=name, timeout=timeout)
        return ExecutionResult(
            command=name,
            args=extra_args,
            returncode=-1,
            stderr=f"command timed out after {timeout}s",
            duration_ms=round(timeout * 1000, 2),
            success=False,
        )
    except Exception as e:
        logger.error("command_error", command=name, error=str(e))
        return ExecutionResult(
            command=name,
            args=extra_args,
            returncode=-1,
            stderr=str(e),
            duration_ms=0.0,
            success=False,
        )


def run_doctor() -> dict[str, Any]:
    """Executa `cockpit doctor --json` e retorna o resultado parseado."""
    result = execute_command("doctor", timeout=30)
    if not result.success:
        return {
            "passed": False,
            "checks": [],
            "error": result.stderr or "doctor failed",
            "raw": result.stdout,
        }
    try:
        data = json.loads(result.stdout)
        data["duration_ms"] = result.duration_ms
        return data
    except json.JSONDecodeError as e:
        logger.error("doctor_json_parse_error", error=str(e), stdout=result.stdout)
        return {
            "passed": False,
            "checks": [],
            "error": "failed to parse doctor JSON output",
            "raw": result.stdout,
        }
