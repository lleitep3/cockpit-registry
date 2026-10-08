import unittest
from unittest.mock import MagicMock, patch

from massa.catalog import inspect_schema, inspect_table


class CatalogTests(unittest.TestCase):
    def test_table_preserves_composite_foreign_key(self) -> None:
        conn = MagicMock()
        foreign_key = {
            "columns": ["clinic_id", "professional_id"],
            "referenced_columns": ["clinic_id", "id"],
        }
        conn.execute.return_value.fetchall.side_effect = [
            [{"name": "clinic_id", "type": "text", "nullable": False}],
            [foreign_key],
            [{"predicate": "ended_at IS NULL"}],
            [{"name": "guard"}],
        ]
        result = inspect_table(conn, {"oid": 1, "kind": "r", "comment": None})
        self.assertEqual(result["fields"]["clinic_id"]["type"], "text")
        self.assertEqual(result["constraints"][0], foreign_key)
        self.assertEqual(result["indexes"][0]["predicate"], "ended_at IS NULL")

    def test_schema_is_read_only_and_excludes_migrations(self) -> None:
        conn = MagicMock()
        conn.execute.return_value.fetchone.side_effect = [
            {"exists": 1},
            {"server_version": "17.11"},
        ]
        conn.execute.return_value.fetchall.side_effect = [
            [{"name": "pgmigrations"}, {"name": "customers"}],
            [],
        ]
        with (
            patch("massa.catalog.psycopg.connect") as connect,
            patch("massa.catalog.inspect_table", return_value={"fields": {}}),
        ):
            connect.return_value.__enter__.return_value = conn
            result = inspect_schema("secret", "public", {"pgmigrations"})
        self.assertEqual(list(result["entities"]), ["customers"])
        conn.execute.assert_any_call("BEGIN ISOLATION LEVEL REPEATABLE READ READ ONLY")
        self.assertNotIn("secret", str(result))

    def test_missing_schema_is_rejected(self) -> None:
        conn = MagicMock()
        conn.execute.return_value.fetchone.return_value = None
        with patch("massa.catalog.psycopg.connect") as connect:
            connect.return_value.__enter__.return_value = conn
            with self.assertRaisesRegex(ValueError, "Schema inexistente"):
                inspect_schema("secret", "missing", set())
