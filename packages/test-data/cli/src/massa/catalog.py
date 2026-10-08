"""Consulta apenas metadados, em um snapshot PostgreSQL somente leitura."""

from typing import Any

import psycopg
from psycopg.rows import dict_row

TABLES = """
SELECT c.oid, c.relname AS name, c.relkind AS kind,
       obj_description(c.oid, 'pg_class') AS comment
FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE n.nspname = %s AND c.relkind IN ('r', 'p')
ORDER BY c.relname
"""

COLUMNS = """
SELECT a.attname AS name, format_type(a.atttypid, a.atttypmod) AS type,
       NOT a.attnotnull AS nullable,
       pg_get_expr(d.adbin, d.adrelid) AS default,
       NULLIF(a.attidentity, '') AS identity,
       NULLIF(a.attgenerated, '') AS generated,
       col_description(a.attrelid, a.attnum) AS comment
FROM pg_attribute a
LEFT JOIN pg_attrdef d ON d.adrelid = a.attrelid AND d.adnum = a.attnum
WHERE a.attrelid = %s AND a.attnum > 0 AND NOT a.attisdropped
ORDER BY a.attnum
"""

CONSTRAINTS = """
SELECT con.conname AS name, con.contype AS type,
       pg_get_constraintdef(con.oid, true) AS definition,
       con.condeferrable AS deferrable, con.condeferred AS initially_deferred,
       con.convalidated AS validated,
       ARRAY(SELECT a.attname FROM unnest(con.conkey) WITH ORDINALITY k(num, ord)
             JOIN pg_attribute a ON a.attrelid = con.conrelid AND a.attnum = k.num
             ORDER BY k.ord) AS columns,
       rn.nspname AS referenced_schema, rc.relname AS referenced_table,
       ARRAY(SELECT a.attname FROM unnest(con.confkey) WITH ORDINALITY k(num, ord)
             JOIN pg_attribute a ON a.attrelid = con.confrelid AND a.attnum = k.num
             ORDER BY k.ord) AS referenced_columns
FROM pg_constraint con
LEFT JOIN pg_class rc ON rc.oid = con.confrelid
LEFT JOIN pg_namespace rn ON rn.oid = rc.relnamespace
WHERE con.conrelid = %s ORDER BY con.conname
"""

INDEXES = """
SELECT c.relname AS name, pg_get_indexdef(i.indexrelid) AS definition,
       i.indisunique AS unique, i.indisprimary AS primary,
       pg_get_expr(i.indpred, i.indrelid) AS predicate
FROM pg_index i JOIN pg_class c ON c.oid = i.indexrelid
WHERE i.indrelid = %s ORDER BY c.relname
"""

TRIGGERS = """
SELECT tgname AS name, pg_get_triggerdef(oid, true) AS definition
FROM pg_trigger WHERE tgrelid = %s AND NOT tgisinternal ORDER BY tgname
"""

ENUMS = """
SELECT t.typname AS name, array_agg(e.enumlabel ORDER BY e.enumsortorder) AS values
FROM pg_type t JOIN pg_namespace n ON n.oid = t.typnamespace
JOIN pg_enum e ON e.enumtypid = t.oid
WHERE n.nspname = %s GROUP BY t.typname ORDER BY t.typname
"""


def inspect_schema(
    connection_url: str, schema: str, exclude: set[str], include: set[str] | None = None
) -> dict[str, Any]:
    """Preserva FKs compostas, SQL original e ordem estável para revisão."""
    with psycopg.connect(
        connection_url, row_factory=dict_row, connect_timeout=5
    ) as conn:
        conn.execute("BEGIN ISOLATION LEVEL REPEATABLE READ READ ONLY")
        conn.execute("SET LOCAL statement_timeout = '10s'")
        if not conn.execute(
            "SELECT 1 FROM pg_namespace WHERE nspname = %s", (schema,)
        ).fetchone():
            raise ValueError(f"Schema inexistente: {schema}")
        version = conn.execute("SHOW server_version").fetchone()
        tables: dict[str, Any] = {}
        discovered = conn.execute(TABLES, (schema,)).fetchall()
        available = {table["name"] for table in discovered} - exclude
        if include is not None and not include.issubset(available):
            raise ValueError("Tabela solicitada ausente ou excluída do catálogo")
        for table in discovered:
            if table["name"] in exclude or (
                include is not None and table["name"] not in include
            ):
                continue
            tables[table["name"]] = inspect_table(conn, table)
        enums = conn.execute(ENUMS, (schema,)).fetchall()
    return {
        "version": 1,
        "source": {
            "dialect": "postgresql",
            "server_version": version["server_version"] if version else "unknown",
            "schema": schema,
            "excluded_tables": sorted(exclude),
            **({"selected_tables": sorted(include)} if include is not None else {}),
        },
        "enums": enums,
        "entities": tables,
    }


def inspect_table(
    conn: psycopg.Connection[dict[str, Any]], table: dict[str, Any]
) -> dict[str, Any]:
    oid = table["oid"]
    columns = conn.execute(COLUMNS, (oid,)).fetchall()
    return {
        "kind": "partitioned_table" if table["kind"] == "p" else "table",
        "comment": table["comment"],
        "fields": {column.pop("name"): column for column in columns},
        "constraints": conn.execute(CONSTRAINTS, (oid,)).fetchall(),
        "indexes": conn.execute(INDEXES, (oid,)).fetchall(),
        "triggers": conn.execute(TRIGGERS, (oid,)).fetchall(),
    }
