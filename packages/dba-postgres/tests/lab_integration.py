"""Exercise a NEW Compose lab. Stops containers, preserves test volumes/evidence."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def command(args: list[str], cwd: Path, data: bytes | None = None) -> bytes:
    result = subprocess.run(
        args, cwd=cwd, input=data, capture_output=True, check=False, timeout=180
    )
    if result.returncode:
        raise RuntimeError(
            "Lab step failed; inspect Compose status in the test directory. Raw output suppressed."
        )
    return result.stdout


def compose(lab: Path, args: list[str], data: bytes | None = None) -> bytes:
    return command(["docker", "compose", "--profile", "tools", *args], lab, data)


def query(lab: Path, sql: str, database: str = "lab") -> str:
    args = [
        "exec",
        "-T",
        "db",
        "psql",
        "-X",
        "-qAt",
        "-v",
        "ON_ERROR_STOP=1",
        "-U",
        "lab_admin",
        "-d",
        database,
    ]
    return compose(lab, args, sql.encode()).decode().strip()


def exercise_database(lab: Path) -> None:
    query(
        lab,
        "CREATE TABLE lab_probe(id integer PRIMARY KEY, value text NOT NULL); INSERT INTO lab_probe VALUES(1,'synthetic');",
    )
    auth = 'PGPASSWORD="$(cat "$POSTGRES_PASSWORD_FILE")" psql -X -w -qAt -h 127.0.0.1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT 1"'
    assert compose(lab, ["exec", "-T", "db", "sh", "-c", auth]).strip() == b"1"
    wrong = subprocess.run(
        [
            "docker",
            "compose",
            "exec",
            "-T",
            "db",
            "sh",
            "-c",
            'PGPASSWORD=incorrect psql -X -w -qAt -h 127.0.0.1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT 1"',
        ],
        cwd=lab,
        capture_output=True,
        check=False,
    )
    assert wrong.returncode != 0
    compose(lab, ["restart", "db"])
    compose(lab, ["up", "-d", "--wait", "db"])
    assert query(lab, "SELECT value FROM lab_probe WHERE id=1;") == "synthetic"
    dump = compose(
        lab, ["exec", "-T", "db", "pg_dump", "-U", "lab_admin", "-d", "lab", "-Fc"]
    )
    fd = os.open(lab / "evidence.dump", os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as output:
        output.write(dump)
    compose(
        lab,
        [
            "exec",
            "-T",
            "db",
            "createdb",
            "-U",
            "lab_admin",
            "--template=template0",
            "lab_restore_01",
        ],
    )
    compose(
        lab,
        [
            "exec",
            "-T",
            "db",
            "pg_restore",
            "-U",
            "lab_admin",
            "-d",
            "lab_restore_01",
            "--exit-on-error",
            "--no-owner",
            "--no-privileges",
        ],
        dump,
    )
    assert (
        query(lab, "SELECT value FROM lab_probe WHERE id=1;", "lab_restore_01")
        == "synthetic"
    )
    ops = json.loads(query(lab, (ROOT / "sql/operations.sql").read_text()))
    assert ops["server_version_num"] // 10000 == 17
    assert isinstance(ops["database_xid_age"], int)


def check_pgadmin(lab: Path) -> None:
    compose(lab, ["up", "-d", "--wait", "--wait-timeout", "90"])
    port = compose(lab, ["port", "pgadmin", "80"]).decode().strip()
    assert port.startswith("127.0.0.1:")
    for _ in range(45):
        try:
            with urllib.request.urlopen(
                "http://" + port + "/login", timeout=2
            ) as response:
                assert response.status == 200
                assert b"pgAdmin" in response.read()
                return
        except (urllib.error.URLError, TimeoutError, ConnectionError):
            time.sleep(1)
    raise RuntimeError("pgAdmin login page not available.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="NEW directory; test volumes and evidence are preserved",
    )
    parser.add_argument("--with-tools", action="store_true")
    args = parser.parse_args()
    lab = args.output.resolve()
    command(
        [
            sys.executable,
            str(ROOT / "lib/dba_postgres.py"),
            "lab-init",
            "--output",
            str(lab),
        ],
        ROOT,
    )
    env = lab / ".env"
    env.write_text(
        env.read_text()
        .replace("POSTGRES_PORT=55432", "POSTGRES_PORT=0")
        .replace("PGADMIN_PORT=55080", "PGADMIN_PORT=0")
    )
    try:
        compose(lab, ["config", "--quiet"])
        compose(lab, ["up", "-d", "--wait", "db"])
        exercise_database(lab)
        if args.with_tools:
            check_pgadmin(lab)
        print(
            "Compose integration passed: authenticated TCP, denied password, persistence, logical restore, operational SQL"
            + (", pgAdmin HTTP login page." if args.with_tools else ".")
        )
    finally:
        compose(lab, ["stop"])
        print(
            "Test containers stopped; volumes and evidence preserved in the selected lab."
        )


if __name__ == "__main__":
    main()
