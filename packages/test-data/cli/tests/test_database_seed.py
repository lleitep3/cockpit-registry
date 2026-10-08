"""Opt-in PostgreSQL seed QA: all fixture DDL/data rolled back."""

import os
import unittest
from pathlib import Path
from uuid import uuid4

import psycopg
from psycopg import sql
from psycopg.conninfo import conninfo_to_dict
from psycopg.rows import dict_row

from massa.catalog import TABLES, inspect_table
from massa.cli import connection_url
from massa.environments import Environment, SelectedEnvironment
from massa.generator import generate
from massa.recipe import Recipe, load_mapping
from massa.seed_project import PreparedSeed, insert_and_verify, inspect_plan

EXAMPLES = Path(__file__).resolve().parents[1] / "examples/relational"


@unittest.skipUnless(os.environ.get("MASSA_TEST_ENV_FILE"), "QA PostgreSQL opt-in")
class DatabaseSeedTests(unittest.TestCase):
    def test_load_replay_conflict_drift_and_fk_failure_rollback(self) -> None:
        url = connection_url("DATABASE_URL", Path(os.environ["MASSA_TEST_ENV_FILE"]))
        parsed = conninfo_to_dict(url)
        self.assertIn(parsed.get("host"), ("localhost", "127.0.0.1"))
        schema_name = "massa_qa_" + uuid4().hex
        environment = Environment.model_validate(
            {
                "source": "env-file",
                "path": "private.env",
                "database": parsed["dbname"],
                "schema": schema_name,
                "writable": True,
            }
        )
        selected = SelectedEnvironment("qa", environment, url, parsed["host"])
        with psycopg.connect(url, row_factory=dict_row, autocommit=True) as conn:
            with conn.transaction(force_rollback=True):
                conn.execute(
                    sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(schema_name))
                )
                conn.execute(
                    sql.SQL("SET LOCAL search_path TO {}").format(
                        sql.Identifier(schema_name)
                    )
                )
                conn.execute((EXAMPLES / "001_fixture.sql").read_text())
                schema = {
                    "version": 1,
                    "source": {"schema": schema_name},
                    "enums": [],
                    "entities": {
                        table["name"]: inspect_table(conn, table)
                        for table in conn.execute(TABLES, (schema_name,)).fetchall()
                    },
                }
                recipe = Recipe.model_validate(
                    load_mapping(EXAMPLES / "generation.yaml")
                )
                data = generate(schema, recipe)
                seed = PreparedSeed("qa", "base", schema, data, "input-hash")
                plan = inspect_plan(conn, selected, seed)
                self.assertEqual(plan["counts"]["clientes"]["insert"], 10)
                # Failed child FK rolls parents back in the same transaction.
                broken = {
                    name: [dict(row) for row in rows] for name, rows in data.items()
                }
                broken["pedidos"][0]["cliente_id"] = 99999
                with (
                    self.assertRaises(psycopg.errors.ForeignKeyViolation),
                    conn.transaction(),
                ):
                    insert_and_verify(
                        conn,
                        schema_name,
                        PreparedSeed("qa", "bad", schema, broken, "bad"),
                    )
                self.assertEqual(inspect_plan(conn, selected, seed), plan)
                insert_and_verify(conn, schema_name, seed)
                replay = inspect_plan(conn, selected, seed)
                self.assertEqual(
                    replay["counts"]["clientes"], {"insert": 0, "reuse": 10}
                )
                self.assertEqual(
                    replay["counts"]["pedidos"], {"insert": 0, "reuse": 30}
                )
                insert_and_verify(conn, schema_name, seed)
                conn.execute("UPDATE clientes SET nome='changed' WHERE id=1")
                with self.assertRaisesRegex(ValueError, "Conflito"):
                    inspect_plan(conn, selected, seed)
                conn.execute("ALTER TABLE clientes ADD COLUMN extra text")
                with self.assertRaisesRegex(ValueError, "Drift"):
                    inspect_plan(conn, selected, seed)
            self.assertIsNone(
                conn.execute(
                    "SELECT 1 FROM pg_namespace WHERE nspname=%s", (schema_name,)
                ).fetchone()
            )
