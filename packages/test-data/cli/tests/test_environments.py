import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from massa.cli import main
from massa.environments import (
    Environment,
    add_environment,
    read_connection,
    select_environment,
)


class EnvironmentTests(unittest.TestCase):
    def test_postman_resolves_enabled_variable_without_storing_secret(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "local.postman_environment.json"
            source.write_text(
                json.dumps(
                    {
                        "values": [
                            {
                                "key": "DATABASE_URL",
                                "value": "postgresql://user:secret@localhost/demo",
                                "enabled": True,
                            },
                            {
                                "key": "DATABASE_URL",
                                "value": "disabled",
                                "enabled": False,
                            },
                        ]
                    }
                )
            )
            registry = root / "environments.yaml"
            environment = Environment(
                source="postman", path=source.name, database="demo"
            )
            add_environment(registry, "local", environment)
            selected = select_environment(registry, "local")
            self.assertIn("secret", selected.connection)
            self.assertNotIn("secret", repr(selected))
            self.assertNotIn("secret", registry.read_text())
            self.assertFalse(selected.configuration.writable)
            self.assertFalse(selected.configuration.resettable)

    def test_wrong_database_and_duplicate_environment_preserve_registry(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / ".env"
            source.write_text("DATABASE_URL=postgresql://localhost/demo\n")
            registry = root / "environments.yaml"
            environment = Environment(
                source="env-file", path=source.name, database="demo"
            )
            add_environment(registry, "local", environment)
            snapshot = registry.read_bytes()
            with self.assertRaises(ValueError):
                add_environment(registry, "local", environment)
            with self.assertRaises(ValueError):
                add_environment(
                    registry,
                    "other",
                    environment.model_copy(update={"database": "wrong"}),
                )
            self.assertEqual(registry.read_bytes(), snapshot)
            with self.assertRaises(ValueError):
                select_environment(registry, "unknown")

    def test_postman_invalid_and_duplicate_values_fail_without_secret(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "postman.json"
            for content in (
                "secret-invalid-json",
                '{"values": []}',
                '{"values": [{"key":"DATABASE_URL","value":"secret"},{"key":"DATABASE_URL","value":"secret"}]}',
            ):
                path.write_text(content)
                with self.assertRaises(ValueError) as error:
                    read_connection("postman", path, "DATABASE_URL")
                self.assertNotIn("secret", str(error.exception))

    def test_schema_uses_environment_and_table_selection(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / ".env"
            source.write_text("DATABASE_URL=postgresql://localhost/demo\n")
            registry = root / "environments.yaml"
            add_environment(
                registry,
                "local",
                Environment.model_validate(
                    {
                        "source": "env-file",
                        "path": source.name,
                        "database": "demo",
                        "schema": "test",
                    }
                ),
            )
            with (
                patch(
                    "massa.cli.inspect_schema",
                    return_value={"version": 1, "entities": {}},
                ) as inspect,
                contextlib.redirect_stdout(io.StringIO()),
            ):
                self.assertEqual(
                    main(
                        [
                            "schema",
                            "inspect",
                            "--environment",
                            "local",
                            "--registry",
                            str(registry),
                            "--table",
                            "patients",
                            "--output",
                            str(root / "schema.yaml"),
                        ]
                    ),
                    0,
                )
                inspect.assert_called_once_with(
                    "postgresql://localhost/demo",
                    "test",
                    {"pgmigrations"},
                    {"patients"},
                )

    def test_cli_rejects_invalid_connection_without_printing_it(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / ".env"
            source.write_text("DATABASE_URL=secret-invalid-connection\n")
            errors = io.StringIO()
            with contextlib.redirect_stderr(errors):
                self.assertEqual(
                    main(
                        [
                            "environment",
                            "add",
                            "--name",
                            "local",
                            "--env-file",
                            str(source),
                            "--database",
                            "demo",
                            "--registry",
                            str(root / "envs.yaml"),
                        ]
                    ),
                    1,
                )
            self.assertNotIn("secret", errors.getvalue())
            self.assertFalse((root / "envs.yaml").exists())
