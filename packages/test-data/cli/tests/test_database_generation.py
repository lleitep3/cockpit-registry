"""QA opt-in: fixture isolada, sem tocar tabelas da aplicação."""

import os
import unittest
from pathlib import Path
from uuid import uuid4

import psycopg
from psycopg import sql
from psycopg.rows import dict_row

from massa.catalog import TABLES, inspect_schema, inspect_table
from massa.cli import connection_url
from massa.generator import generate
from massa.recipe import Recipe, load_mapping

EXAMPLES = Path(__file__).resolve().parents[1] / "examples/relational"


@unittest.skipUnless(os.environ.get("MASSA_TEST_ENV_FILE"), "QA PostgreSQL opt-in")
class DatabaseGenerationTests(unittest.TestCase):
    def test_filtered_catalog_preserves_metadata_and_rejects_missing_table(
        self,
    ) -> None:
        url = connection_url("DATABASE_URL", Path(os.environ["MASSA_TEST_ENV_FILE"]))
        from urllib.parse import urlparse

        self.assertIn(urlparse(url).hostname, ("localhost", "127.0.0.1"))
        full = inspect_schema(url, "public", {"pgmigrations"})
        if not full["entities"]:
            self.skipTest("Seleção exige uma tabela existente no ambiente de QA")
        table_name = next(iter(full["entities"]))
        catalogue = inspect_schema(url, "public", {"pgmigrations"}, {table_name})
        self.assertEqual(set(catalogue["entities"]), {table_name})
        self.assertEqual(catalogue["source"]["selected_tables"], [table_name])
        self.assertEqual(
            catalogue["entities"][table_name], full["entities"][table_name]
        )
        with self.assertRaises(ValueError):
            inspect_schema(url, "public", {"pgmigrations"}, {"missing_table"})

    def test_fixture_accepts_mass_and_rejects_cross_tenant_reference(self) -> None:
        env = Path(os.environ["MASSA_TEST_ENV_FILE"])
        url = connection_url("DATABASE_URL", env)
        from urllib.parse import urlparse

        self.assertIn(urlparse(url).hostname, ("localhost", "127.0.0.1"))
        schema_name = "massa_qa_" + uuid4().hex
        with psycopg.connect(url, row_factory=dict_row, autocommit=True) as conn:
            with conn.transaction(force_rollback=True):
                conn.execute("SET LOCAL statement_timeout = '10s'")
                conn.execute(
                    sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(schema_name))
                )
                conn.execute(
                    sql.SQL("SET LOCAL search_path TO {}").format(
                        sql.Identifier(schema_name)
                    )
                )
                conn.execute((EXAMPLES / "001_fixture.sql").read_text())
                tables = conn.execute(TABLES, (schema_name,)).fetchall()
                schema = {
                    "version": 1,
                    "source": {"schema": schema_name},
                    "entities": {
                        table["name"]: inspect_table(conn, table) for table in tables
                    },
                }
                recipe = Recipe.model_validate(
                    load_mapping(EXAMPLES / "generation.yaml")
                )
                data = generate(schema, recipe)
                for name, rows in data.items():
                    for row in rows:
                        statement = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
                            sql.Identifier(name),
                            sql.SQL(",").join(map(sql.Identifier, row)),
                            sql.SQL(",").join(sql.Placeholder() for _ in row),
                        )
                        conn.execute(statement, list(row.values()))
                count = conn.execute("SELECT count(*) AS count FROM pedidos").fetchone()
                self.assertEqual(count["count"] if count else None, 30)
                with (
                    self.assertRaises(psycopg.errors.ForeignKeyViolation),
                    conn.transaction(),
                ):
                    conn.execute(
                        "INSERT INTO pedidos VALUES (999, 'tenant_inexistente', 1, 'pago', now())"
                    )
            found = conn.execute(
                "SELECT 1 FROM pg_namespace WHERE nspname=%s", (schema_name,)
            ).fetchone()
            self.assertIsNone(found)
