"""Scoped synthetic inserts with reviewed plans and transactional verification."""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

import psycopg
from psycopg import sql
from psycopg.rows import dict_row
from pydantic import Field

from massa.catalog import ENUMS, TABLES, inspect_table
from massa.environments import SelectedEnvironment
from massa.export import sha256
from massa.recipe import IDENTIFIER, Contract, load_mapping
from massa.schema_diff import compare_values

MAX_ROWS = 100_000
MAX_FILE_BYTES = 64 * 1024 * 1024


class Scenario(Contract):
    bundle: str
    scope: dict[str, dict[str, str | int]]


class SeedProject(Contract):
    version: Literal[1] = 1
    name: str = Field(pattern=IDENTIFIER)
    schema_file: str
    scenarios: dict[str, Scenario]


@dataclass(frozen=True)
class PreparedSeed:
    name: str
    scenario: str
    schema: dict[str, Any]
    rows: dict[str, list[dict[str, Any]]]
    fingerprint: str
    scope: dict[str, dict[str, str | int]] = field(default_factory=dict)


def digest(document: Any) -> str:
    return sha256(json.dumps(document, sort_keys=True, separators=(",", ":")).encode())


def project_path(root: Path, relative: str) -> Path:
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError("Arquivo de cenário fora do projeto")
    return path


def read_limited(path: Path) -> bytes:
    if path.stat().st_size > MAX_FILE_BYTES:
        raise ValueError("Arquivo de seed excede limite de tamanho")
    return path.read_bytes()


def prepare_seed(path: Path, scenario_name: str) -> PreparedSeed:
    project_bytes = read_limited(path)
    project = SeedProject.model_validate(load_mapping(path, project_bytes))
    if scenario_name not in project.scenarios:
        raise ValueError("Cenário não cadastrado")
    scenario = project.scenarios[scenario_name]
    schema_path = project_path(path.parent, project.schema_file)
    schema_bytes = read_limited(schema_path)
    schema = load_mapping(schema_path, schema_bytes)
    bundle = project_path(path.parent, scenario.bundle)
    manifest_bytes = read_limited(bundle / "manifest.json")
    manifest = json.loads(manifest_bytes)
    if manifest.get("inputs", {}).get("schema_sha256") != sha256(schema_bytes):
        raise ValueError("Manifesto foi gerado com outro schema")
    rows = read_bundle(bundle, manifest, schema, scenario)
    fingerprint = digest(
        {
            "project": sha256(project_bytes),
            "schema": sha256(schema_bytes),
            "manifest": sha256(manifest_bytes),
        }
    )
    return PreparedSeed(
        project.name, scenario_name, schema, rows, fingerprint, scenario.scope
    )


def read_bundle(
    bundle: Path, manifest: dict[str, Any], schema: dict[str, Any], scenario: Scenario
) -> dict[str, list[dict[str, Any]]]:
    if manifest.get("version") != 1 or manifest.get("format") != "jsonl":
        raise ValueError("Manifesto de geração incompatível")
    counts = manifest.get("counts", {})
    if not isinstance(counts, dict) or any(
        type(count) is not int or count < 0 for count in counts.values()
    ):
        raise ValueError("Contagens do manifesto inválidas")
    if sum(counts.values()) > MAX_ROWS:
        raise ValueError("Cenário excede limite de registros")
    order = manifest.get("generation_order")
    if not isinstance(order, list) or not order or len(set(order)) != len(order):
        raise ValueError("Ordem de geração inválida")
    if set(order) != set(scenario.scope) or set(order) != set(manifest["counts"]):
        raise ValueError("Escopo precisa corresponder exatamente às tabelas geradas")
    if set(manifest["files"]) != {name + ".jsonl" for name in order}:
        raise ValueError("Arquivos do manifesto inconsistentes")
    data: dict[str, list[dict[str, Any]]] = {}
    for name in order:
        if name not in schema["entities"]:
            raise ValueError("Tabela fora do schema declarado")
        content = read_limited(project_path(bundle, name + ".jsonl"))
        if sha256(content) != manifest["files"][name + ".jsonl"]:
            raise ValueError("Hash de arquivo de seed divergente")
        data[name] = [json.loads(line) for line in content.splitlines()]
        if len(data[name]) != manifest["counts"][name]:
            raise ValueError("Contagem de arquivo divergente")
        validate_rows(data[name], schema["entities"][name], scenario.scope[name])
    if sum(map(len, data.values())) > MAX_ROWS:
        raise ValueError("Cenário excede limite de registros")
    return data


def primary_key(entity: dict[str, Any]) -> list[str]:
    keys = [item["columns"] for item in entity["constraints"] if item["type"] == "p"]
    if len(keys) != 1 or not keys[0]:
        raise ValueError("Carga exige chave primária explícita")
    return list(keys[0])


def validate_rows(
    rows: list[dict[str, Any]], entity: dict[str, Any], scope: dict[str, str | int]
) -> None:
    keys = primary_key(entity)
    if not scope or not set(scope).issubset(entity["fields"]):
        raise ValueError("Escopo por tabela obrigatório e deve usar colunas existentes")
    seen: set[tuple[Any, ...]] = set()
    for row in rows:
        if (
            not isinstance(row, dict)
            or not row
            or not set(row).issubset(entity["fields"])
        ):
            raise ValueError("Registro possui campos inválidos")
        if any(row.get(key) != value for key, value in scope.items()):
            raise ValueError("Registro fora do escopo sintético declarado")
        if any(key not in row or row[key] is None for key in keys):
            raise ValueError("Registro precisa de chave primária não nula")
        if any(isinstance(value, (dict, list)) for value in row.values()):
            raise ValueError("Carga de valores compostos não suportada")
        if any(
            entity["fields"][key].get("generated")
            or entity["fields"][key].get("identity") == "a"
            for key in row
        ):
            raise ValueError("Campo gerado ou identity always não pode ser fornecido")
        identity = tuple(row[key] for key in keys)
        if identity in seen:
            raise ValueError("Chave primária duplicada na massa")
        seen.add(identity)


def table_identifier(schema: str, name: str) -> sql.Identifier:
    return sql.Identifier(schema, name)


def row_state(
    conn: psycopg.Connection[dict[str, Any]],
    schema: str,
    name: str,
    keys: list[str],
    row: dict[str, Any],
) -> str:
    predicate = sql.SQL(" AND ").join(
        sql.SQL("{} IS NOT DISTINCT FROM %s").format(sql.Identifier(key))
        for key in keys
    )
    equal = sql.SQL(" AND ").join(
        sql.SQL("{} IS NOT DISTINCT FROM %s").format(sql.Identifier(key)) for key in row
    )
    found = conn.execute(
        sql.SQL("SELECT ({}) AS matches FROM {} WHERE {}").format(
            equal, table_identifier(schema, name), predicate
        ),
        [*row.values(), *(row[key] for key in keys)],
    ).fetchone()
    if found is None:
        return "insert"
    if not found["matches"]:
        raise ValueError(
            "Conflito: chave existente com conteúdo diferente; nada será sobrescrito"
        )
    return "reuse"


def inspect_plan(
    conn: psycopg.Connection[dict[str, Any]],
    selected: SelectedEnvironment,
    seed: PreparedSeed,
) -> dict[str, Any]:
    schema = selected.configuration.schema_name
    if seed.schema.get("source", {}).get("schema") != schema:
        raise ValueError("Schema do projeto diverge do environment")
    tables = conn.execute(TABLES, (schema,)).fetchall()
    live = {t["name"]: inspect_table(conn, t) for t in tables if t["name"] in seed.rows}
    expected = {name: seed.schema["entities"][name] for name in seed.rows}
    if compare_values(expected, live, ["entities"]):
        raise ValueError(
            "Drift no catálogo; extraia schema e revise receita antes da carga"
        )
    identity = conn.execute(
        "SELECT current_database() AS database, current_user AS role, "
        "inet_server_addr()::text AS server, inet_server_port() AS port, "
        "(SELECT oid FROM pg_database WHERE datname=current_database()) AS database_oid"
    ).fetchone()
    if identity is None or identity["database"] != selected.configuration.database:
        raise ValueError("Banco conectado diverge do environment")
    enums = conn.execute(ENUMS, (schema,)).fetchall()
    if compare_values(seed.schema.get("enums", []), enums, ["enums"]):
        raise ValueError("Drift nos enums do schema")
    counts = {}
    for name, rows in seed.rows.items():
        states = [
            row_state(conn, schema, name, primary_key(live[name]), row) for row in rows
        ]
        counts[name] = {
            "insert": states.count("insert"),
            "reuse": states.count("reuse"),
        }
    return {
        "version": 1,
        "project": seed.name,
        "scenario": seed.scenario,
        "environment": selected.name,
        "database": identity,
        "schema": schema,
        "inputs_sha256": seed.fingerprint,
        "catalogue_sha256": digest({"entities": live, "enums": enums}),
        "counts": counts,
        "scope": seed.scope,
        "operation": "insert_or_verify",
        "deletes": 0,
        "updates": 0,
        "domain_http_ui": "not_verified",
    }


def insert_and_verify(
    conn: psycopg.Connection[dict[str, Any]], schema: str, seed: PreparedSeed
) -> None:
    for name, rows in seed.rows.items():
        keys = primary_key(seed.schema["entities"][name])
        for row in rows:
            if row_state(conn, schema, name, keys, row) == "insert":
                statement = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
                    table_identifier(schema, name),
                    sql.SQL(",").join(map(sql.Identifier, row)),
                    sql.SQL(",").join(sql.Placeholder() for _ in row),
                )
                conn.execute(statement, list(row.values()))
    # Checks and deferred FKs must pass before issuing a success receipt.
    conn.execute("SET CONSTRAINTS ALL IMMEDIATE")
    for name, rows in seed.rows.items():
        for row in rows:
            if (
                row_state(
                    conn, schema, name, primary_key(seed.schema["entities"][name]), row
                )
                != "reuse"
            ):
                raise ValueError("Verificação após carga falhou")


def run_seed(
    selected: SelectedEnvironment,
    seed: PreparedSeed,
    action: str,
    reviewed: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if action == "apply" and not selected.configuration.writable:
        raise ValueError("Environment não permite escrita")
    with psycopg.connect(
        selected.connection, row_factory=dict_row, connect_timeout=5
    ) as conn:
        conn.execute(
            "BEGIN ISOLATION LEVEL REPEATABLE READ"
            + (" READ ONLY" if action != "apply" else "")
        )
        conn.execute("SET LOCAL statement_timeout = '10s'")
        conn.execute("SET LOCAL lock_timeout = '5s'")
        if action == "apply":
            for name in sorted(seed.rows):
                conn.execute(
                    sql.SQL("LOCK TABLE {} IN SHARE ROW EXCLUSIVE MODE").format(
                        table_identifier(selected.configuration.schema_name, name)
                    )
                )
        plan = inspect_plan(conn, selected, seed)
        if action == "apply":
            if reviewed != plan:
                raise ValueError(
                    "Plano mudou; gere e revise um novo plano antes de aplicar"
                )
            insert_and_verify(conn, selected.configuration.schema_name, seed)
        elif action == "verify" and any(c["insert"] for c in plan["counts"].values()):
            raise ValueError("Verificação falhou: registros do cenário ausentes")
    if action == "plan":
        return plan
    return {**plan, "result": "committed_and_verified" if action == "apply" else action}
