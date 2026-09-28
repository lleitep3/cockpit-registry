"""Read-only PostgreSQL evidence collection; offline reports use no network."""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MAX_BYTES = 20 * 1024 * 1024
LIMITS = {"tables": 5000, "columns": 50000, "constraints": 50000, "indexes": 50000}
BINDINGS = {
    "PGHOST": "host",
    "PGPORT": "port",
    "PGDATABASE": "database",
    "PGUSER": "user",
    "PGPASSWORD": "password",
    "PGSSLMODE": "sslmode",
}
Snapshot = dict[str, Any]


def validate(data: Any) -> Snapshot:
    if not isinstance(data, dict) or data.get("format_version") != 1:
        raise ValueError("Unsupported snapshot format; collect with this package.")
    if not isinstance(data.get("schema"), str) or not isinstance(
        data.get("server_version_num"), int
    ):
        raise ValueError("Missing schema or PostgreSQL version.")
    if not 160000 <= data["server_version_num"] < 190000:
        raise ValueError(
            "Collector targets PostgreSQL 16–18; review SQL for this version."
        )
    for key, limit in LIMITS.items():
        rows = data.get(key)
        if not isinstance(rows, list) or len(rows) >= limit:
            raise ValueError("Missing or truncated metadata; narrow the schema.")
        if not all(isinstance(row, dict) for row in rows):
            raise ValueError("Malformed metadata rows.")
    names = [t["name"] for t in data["tables"]]
    if len(names) != len(set(names)):
        raise ValueError("Duplicate table names.")
    for key in ("constraints", "indexes"):
        for row in data[key]:
            if not isinstance(row.get("columns"), list):
                raise ValueError("Column arrays must be JSON arrays.")
    return data


def read_snapshot(path: Path) -> Snapshot:
    if path.stat().st_size > MAX_BYTES:
        raise ValueError("Snapshot exceeds 20 MiB limit.")
    return validate(json.loads(path.read_text()))


def write_new(path: Path, content: str) -> None:
    # Exclusive creation also refuses symlinks and existing artifacts.
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w") as stream:
        stream.write(content)


def safe_label(value: Any) -> str:
    return re.sub(r"[^A-Za-z0-9_. -]", "_", str(value))


def markdown_text(value: Any) -> str:
    return (
        html.escape(str(value))
        .replace("|", "&#124;")
        .replace("`", "&#96;")
        .replace("\n", " ")
    )


def erd(data: Snapshot) -> str:
    ids = {t["name"]: f"t{i}" for i, t in enumerate(data["tables"])}
    lines = ["erDiagram"]
    for name, identifier in ids.items():
        lines.append(f'  {identifier}["{safe_label(name)}"] {{')
        for i, col in enumerate(c for c in data["columns"] if c["table_name"] == name):
            kind = re.sub(r"[^A-Za-z0-9_]", "_", col["type"])
            fk = any(
                k["type"] == "f"
                and k["table_name"] == name
                and col["name"] in k["columns"]
                for k in data["constraints"]
            )
            keys = ",".join(
                k for k, yes in (("PK", col["primary_key"]), ("FK", fk)) if yes
            )
            null = "NOT NULL" if col["required"] else "nullable"
            lines.append(
                f'    {kind} c{i}{" " + keys if keys else ""} "{safe_label(col["name"])}; {null}"'
            )
        lines.append("  }")
    for fk in data["constraints"]:
        if (
            fk["type"] != "f"
            or fk.get("parent_schema") != data["schema"]
            or fk.get("parent") not in ids
        ):
            continue
        cols = [
            c
            for c in data["columns"]
            if c["table_name"] == fk["table_name"] and c["name"] in fk["columns"]
        ]
        # MATCH FULL permits all-null or all-present. Any NOT NULL makes parent required.
        required = bool(cols) and (
            any(c["required"] for c in cols)
            if fk.get("match_type") == "f"
            else all(c["required"] for c in cols)
        )
        unique = any(
            k["type"] in ("p", "u")
            and k["table_name"] == fk["table_name"]
            and k["columns"]
            and set(k["columns"]) <= set(fk["columns"])
            for k in data["constraints"]
        )
        left, right = ("||" if required else "|o"), ("o|" if unique else "o{")
        lines.append(
            f'  {ids[fk["parent"]]} {left}--{right} {ids[fk["table_name"]]} : "{safe_label(fk["name"])}"'
        )
    return "\n".join(lines) + "\n"


def findings(data: Snapshot) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []

    def add(code: str, subject: str, evidence: str, next_step: str) -> None:
        result.append(
            dict(code=code, subject=subject, evidence=evidence, next_step=next_step)
        )

    for table in data["tables"]:
        if not any(
            k["type"] == "p" and k["table_name"] == table["name"]
            for k in data["constraints"]
        ):
            add(
                "review-primary-key",
                table["name"],
                "No declared primary key.",
                "Check identity and intended table purpose before proposing a migration.",
            )
    for index in data["indexes"]:
        if not index.get("valid", True) or not index.get("ready", True):
            add(
                "invalid-index",
                index["name"],
                "Index is invalid or not ready.",
                "Check concurrent build state/failure and dependencies; do not drop automatically.",
            )
    for fk in data["constraints"]:
        if fk.get("validated") is False:
            add(
                "unvalidated-constraint",
                fk["name"],
                "Existing rows are not validated.",
                "Review migration intent, existing rows and lock budget.",
            )
        if fk["type"] != "f":
            continue
        covered = any(
            i["table_name"] == fk["table_name"]
            and i.get("method") == "btree"
            and i.get("valid")
            and i.get("ready")
            and not i.get("partial")
            and not i.get("expressions")
            and set(i["columns"][: len(fk["columns"])]) == set(fk["columns"])
            for i in data["indexes"]
        )
        if not covered:
            add(
                "review-fk-index",
                fk["name"],
                "No full valid B-tree with these FK columns as leading keys found.",
                "Candidate only: inspect plans, parent deletes/updates, other index methods, table size and write cost.",
            )
    return result


def report(data: Snapshot) -> str:
    total = sum(int(t["total_bytes"]) for t in data["tables"])
    issues = findings(data)
    lines = [
        "# PostgreSQL — relatório de evidências",
        "",
        f"Coleta: {markdown_text(data.get('collected_at', 'unknown'))}; PostgreSQL: {data['server_version_num']}; schema: {markdown_text(data['schema'])}.",
        f"{len(data['tables'])} tabelas; {total} bytes em relações, incluindo índices/TOAST. Não representa disco provisionado, WAL ou backups.",
        "",
        "## Limites",
        "",
        "Snapshot único; contadores acumulados não provam taxas ou causalidade. Sem workload, planos ou SLO, não há recomendação de capacidade nem economia comprovada.",
        f"Reset das estatísticas: {markdown_text((data.get('database_stats') or {}).get('stats_reset'))}. track_counts: {markdown_text(data.get('track_counts'))}.",
        "Ausência de métricas não significa ausência de problemas. n_live_tup/n_dead_tup são estimativas, não medida de bloat.",
        "DER contém FKs declaradas; relações não validadas podem ter linhas legadas inconsistentes. Índices parciais não definem cardinalidade global. Funções, views, triggers, RLS policies e corpos de CHECKs não são exportados.",
        "",
        "## Pontos para revisão (nenhuma mudança aplicada)",
        "",
    ]
    for issue in issues[:50]:
        lines.append(
            f"- **{issue['code']} — {markdown_text(issue['subject'])}**: {issue['evidence']} {issue['next_step']}"
        )
    if not issues:
        lines.append(
            "Nenhum candidato nestas heurísticas limitadas; não equivale a auditoria completa."
        )
    if len(issues) > 50:
        lines.append(
            f"Exibidos 50 de {len(issues)} candidatos. findings.json contém todos."
        )
    lines += [
        "",
        "## Tabelas",
        "",
        "| Tabela | Bytes totais | Bytes índices | Vivas estimadas | Mortas estimadas |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for t in data["tables"]:
        lines.append(
            f"| {markdown_text(t['name'])} | {t['total_bytes']} | {t['index_bytes']} | {t.get('n_live_tup')} | {t.get('n_dead_tup')} |"
        )
    lines += [
        "",
        "## DER implementado",
        "",
        "```mermaid",
        erd(data).rstrip(),
        "```",
        "",
        "## Próxima decisão",
        "",
        "Para cada candidato: hipótese, consulta/janela representativa, evidência, confiança, alternativa, custo de escrita, validação e rollback. Consultar workflows do pacote antes de propor mudanças.",
    ]
    return "\n".join(lines) + "\n"


def collect_local(schema: str, output: Path) -> None:
    if not shutil.which("psql"):
        raise ValueError(
            "psql is required for collection; offline analysis needs only Python."
        )
    if output.exists() or output.is_symlink():
        raise ValueError("Output exists; choose a new evidence file.")
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", schema):
        raise ValueError("Use a simple schema identifier for this collector.")
    if any(not os.environ.get(key) for key in BINDINGS):
        raise ValueError("Missing explicit connection fields; use collect --profile.")
    env = {k: v for k, v in os.environ.items() if not k.startswith("PG")}
    env.update({k: os.environ[k] for k in BINDINGS})
    env.update(PGCONNECT_TIMEOUT="5", PGAPPNAME="cockpit-dba-postgres")
    run = subprocess.run(
        [
            "psql",
            "-X",
            "-w",
            "-qAt",
            "-v",
            f"schema={schema}",
            "-f",
            str(ROOT / "sql/baseline.sql"),
        ],
        env=env,
        capture_output=True,
        text=True,
        check=False,
        timeout=45,
    )
    if run.returncode:
        raise ValueError(
            "PostgreSQL collection failed: check connectivity, TLS, privileges and version. Raw server errors suppressed."
        )
    if len(run.stdout.encode()) > MAX_BYTES:
        raise ValueError("Metadata output too large; narrow the schema.")
    data = validate(json.loads(run.stdout))
    write_new(output, json.dumps(data, indent=2) + "\n")


def collect_profile(profile: str, schema: str, output: Path) -> None:
    if not re.fullmatch(r"[a-zA-Z0-9_-]+", profile):
        raise ValueError("Invalid profile name.")
    if not shutil.which("cockpit"):
        raise ValueError("Cockpit with config exec is required; upgrade Cockpit.")
    command = [
        "cockpit",
        "config",
        "--namespace",
        "dba-postgres",
        "--profile",
        profile,
        "exec",
    ]
    for variable, field in BINDINGS.items():
        command.extend(["--env", f"{variable}={field}"])
    command.extend(
        [
            "--",
            sys.executable,
            str(Path(__file__).resolve()),
            "_collect",
            "--schema",
            schema,
            "--output",
            str(output),
        ]
    )
    run = subprocess.run(
        command, capture_output=True, text=True, check=False, timeout=60
    )
    if run.returncode:
        raise ValueError(
            "Collection failed. Verify explicit profile fields, vault unlock/grants, output path, psql and PostgreSQL access; no fallback credentials used."
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="DBA PostgreSQL: read-only collection, offline DER and evidence reports."
    )
    subs = parser.add_subparsers(
        dest="command", required=True, metavar="{collect,analyze,sql}"
    )
    for name in ("collect", "_collect"):
        if name == "collect":
            item = subs.add_parser(name, help="Collect fixed metadata queries")
        else:
            item = subs.add_parser(name)
        if name == "collect":
            item.add_argument("--profile", required=True)
        item.add_argument("--schema", default="public")
        item.add_argument("--output", type=Path, required=True)
    analysis = subs.add_parser(
        "analyze",
        help="Generate offline report, Mermaid and findings; output must be new",
    )
    analysis.add_argument("snapshot", type=Path)
    analysis.add_argument("--output", type=Path, required=True)
    subs.add_parser("sql", help="Print the fixed read-only collector SQL for review")
    args = parser.parse_args(argv)
    try:
        if args.command == "sql":
            print((ROOT / "sql/baseline.sql").read_text(), end="")
        elif args.command == "collect":
            collect_profile(args.profile, args.schema, args.output)
        elif args.command == "_collect":
            collect_local(args.schema, args.output)
        else:
            data = read_snapshot(args.snapshot)
            artifacts = {
                "report.md": report(data),
                "schema.mmd": erd(data),
                "findings.json": json.dumps(findings(data), indent=2) + "\n",
            }
            args.output.mkdir(mode=0o700, parents=False, exist_ok=False)
            for name, content in artifacts.items():
                write_new(args.output / name, content)
        return 0
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError):
        # Do not echo source data, credentials, argv or raw PostgreSQL stderr.
        print(
            "DBA operation failed. Check input format/version, new output path, dependencies and profile/access. No database changes performed.",
            file=sys.stderr,
        )
        return 2


if __name__ == "__main__":
    if sys.version_info < (3, 10):
        sys.exit("Python 3.10+ required.")
    sys.exit(main())
