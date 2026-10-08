import contextlib
import io
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import psycopg
import yaml

from massa.cli import connection_url, main, parser


class CliTests(unittest.TestCase):
    def test_defaults(self) -> None:
        args = parser().parse_args(["schema", "inspect", "--output", "schema.yaml"])
        self.assertIsNone(args.schema)
        self.assertEqual(args.exclude_table, ["pgmigrations"])

    def test_environment_file_wins(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / ".env"
            path.write_text("DATABASE_URL=postgresql://local/db\n", encoding="utf-8")
            with patch.dict(os.environ, {"DATABASE_URL": "postgresql://remote/db"}):
                self.assertEqual(
                    connection_url("DATABASE_URL", path), "postgresql://local/db"
                )

    def test_missing_variable(self) -> None:
        with patch.dict(os.environ, {}, clear=True), self.assertRaises(ValueError):
            connection_url("DATABASE_URL", None)

    def test_writes_yaml_without_credentials(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "schema.yaml"
            document = {"version": 1, "entities": {"clientes": {"fields": {}}}}
            with (
                patch.dict(os.environ, {"DATABASE_URL": "secret"}),
                patch("massa.cli.inspect_schema", return_value=document),
                contextlib.redirect_stdout(io.StringIO()),
            ):
                self.assertEqual(main(["schema", "inspect", "--output", str(path)]), 0)
            self.assertEqual(yaml.safe_load(path.read_text()), document)

    def test_refuses_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "schema.yaml"
            path.write_text("original", encoding="utf-8")
            with (
                patch.dict(os.environ, {"DATABASE_URL": "secret"}),
                patch("massa.cli.inspect_schema") as inspect,
                contextlib.redirect_stderr(io.StringIO()),
            ):
                self.assertEqual(main(["schema", "inspect", "--output", str(path)]), 1)
                inspect.assert_not_called()
            self.assertEqual(path.read_text(), "original")

    def test_database_error_does_not_leak_password(self) -> None:
        output = io.StringIO()
        with (
            patch.dict(os.environ, {"DATABASE_URL": "secret"}),
            patch(
                "massa.cli.inspect_schema",
                side_effect=psycopg.OperationalError("secret"),
            ),
            contextlib.redirect_stderr(output),
        ):
            self.assertEqual(
                main(["schema", "inspect", "--output", "/tmp/not-created.yaml"]), 1
            )
        self.assertNotIn("secret", output.getvalue())
