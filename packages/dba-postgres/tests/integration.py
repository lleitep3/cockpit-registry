"""Opt-in integration test in an isolated, ephemeral Docker PostgreSQL 17."""

from __future__ import annotations

import json
import subprocess
import time
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(args: list[str], text: str | None = None) -> str:
    return subprocess.run(
        args, input=text, text=True, capture_output=True, check=True, timeout=60
    ).stdout


def main() -> None:
    name = "cockpit-dba-test-" + uuid.uuid4().hex[:8]
    run(
        [
            "docker",
            "run",
            "-d",
            "--rm",
            "--network",
            "none",
            "--name",
            name,
            "-e",
            "POSTGRES_HOST_AUTH_METHOD=trust",
            "postgres:17-alpine",
        ]
    )
    try:
        for _ in range(30):
            ready = subprocess.run(
                ["docker", "exec", name, "pg_isready", "-U", "postgres"],
                capture_output=True,
                check=False,
                timeout=5,
            )
            if ready.returncode == 0:
                break
            time.sleep(1)
        else:
            raise RuntimeError("Disposable PostgreSQL did not become ready.")
        psql = [
            "docker",
            "exec",
            "-i",
            name,
            "psql",
            "-U",
            "postgres",
            "-d",
            "postgres",
            "-X",
            "-qAt",
            "-v",
            "ON_ERROR_STOP=1",
        ]
        run(
            psql,
            """
CREATE TABLE parent (id integer PRIMARY KEY, tenant integer NOT NULL, UNIQUE(tenant,id));
CREATE TABLE child (id integer PRIMARY KEY, tenant integer NOT NULL, parent_id integer,
 FOREIGN KEY(tenant,parent_id) REFERENCES parent(tenant,id));
CREATE UNIQUE INDEX child_current ON child(tenant,parent_id) WHERE parent_id IS NOT NULL;
CREATE TABLE audit_sample (event_id integer);
""",
        )
        snapshot = json.loads(
            run(psql + ["-v", "schema=public"], (ROOT / "sql/baseline.sql").read_text())
        )
        assert len(snapshot["tables"]) == 3
        assert snapshot["server_version_num"] // 10000 == 17
        assert any(
            k["type"] == "f" and k["columns"] == ["tenant", "parent_id"]
            for k in snapshot["constraints"]
        )
        assert any(i["partial"] for i in snapshot["indexes"])
        assert all("query" not in row for row in snapshot["indexes"])
        # A second catalog query confirms collection did not change schema.
        assert (
            run(
                psql, "SELECT count(*) FROM pg_tables WHERE schemaname='public';"
            ).strip()
            == "3"
        )
        print(
            "PostgreSQL 17 integration passed: 3 tables, composite FK, partial index, JSON arrays, no schema changes."
        )
    finally:
        run(["docker", "stop", name])


if __name__ == "__main__":
    main()
