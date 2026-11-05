import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import yaml

from massa.cli import main
from massa.environments import Environment, SelectedEnvironment
from massa.export import export_jsonl, sha256
from massa.seed_project import (
    digest,
    prepare_seed,
    project_path,
    run_seed,
    validate_rows,
)

EXAMPLES = Path(__file__).resolve().parents[1] / "examples/relational"


class SeedProjectTests(unittest.TestCase):
    def make_project(self, root: Path) -> Path:
        schema = root / "schema.yaml"
        schema.write_bytes((EXAMPLES / "schema.yaml").read_bytes())
        recipe = yaml.safe_load((EXAMPLES / "generation.yaml").read_text())
        # Fixed scopes intentionally own each generated record.
        recipe["entities"]["clientes"]["fields"]["clinic_id"] = {
            "generator": "constant",
            "value": "qa",
        }
        recipe_path = root / "generation.yaml"
        recipe_path.write_text(yaml.safe_dump(recipe))
        export_jsonl(schema, recipe_path, root / "data")
        first = json.loads((root / "data/clientes.jsonl").read_text().splitlines()[0])
        project = root / "seed-project.yaml"
        project.write_text(
            yaml.safe_dump(
                {
                    "version": 1,
                    "name": "qa",
                    "schema_file": "schema.yaml",
                    "scenarios": {
                        "base": {
                            "bundle": "data",
                            "scope": {
                                "clientes": {"clinic_id": first["clinic_id"]},
                                "pedidos": {"clinic_id": first["clinic_id"]},
                            },
                        }
                    },
                }
            )
        )
        return project

    def test_bundle_hash_scope_and_schema_are_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project = self.make_project(root)
            seed = prepare_seed(project, "base")
            self.assertEqual(list(seed.rows), ["clientes", "pedidos"])
            self.assertEqual(
                seed.fingerprint, prepare_seed(project, "base").fingerprint
            )
            file = root / "data/clientes.jsonl"
            file.write_text(file.read_text().replace("tenant-a", "another-tenant"))
            # Tamper regardless of the example tenant spelling.
            file.write_text(file.read_text() + "\n")
            with self.assertRaisesRegex(ValueError, "Hash"):
                prepare_seed(project, "base")

    def test_wrong_schema_and_escaping_paths_fail(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project = self.make_project(root)
            with self.assertRaises(ValueError):
                project_path(root, "../private.env")
            (root / "schema.yaml").write_text((root / "schema.yaml").read_text() + "\n")
            with self.assertRaisesRegex(ValueError, "outro schema"):
                prepare_seed(project, "base")

    def test_scope_duplicate_primary_key_and_generated_columns_fail(self) -> None:
        entity = {
            "fields": {"id": {}, "clinic_id": {}, "computed": {"generated": "s"}},
            "constraints": [{"type": "p", "columns": ["id"]}],
        }
        row = {"id": 1, "clinic_id": "qa"}
        validate_rows([row], entity, {"clinic_id": "qa"})
        for rows, scope in [
            ([row], {}),
            ([row], {"clinic_id": "other"}),
            ([row, row], {"clinic_id": "qa"}),
            ([{**row, "computed": 3}], {"clinic_id": "qa"}),
        ]:
            with self.assertRaises(ValueError):
                validate_rows(rows, entity, scope)

    def test_cli_apply_requires_exact_destination_and_plan_hash(self) -> None:
        selected = SelectedEnvironment(
            "qa",
            Environment(
                source="env-file", path="private.env", database="test", writable=True
            ),
            "secret-url",
            "localhost",
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project = self.make_project(root)
            plan = root / "plan.json"
            plan.write_text('{"version":1}')
            args = [
                "seed",
                "apply",
                "--project",
                str(project),
                "--scenario",
                "base",
                "--environment",
                "qa",
                "--plan",
                str(plan),
                "--output",
                str(root / "receipt.json"),
                "--confirm",
                "wrong",
                "--confirm-plan",
                "wrong",
            ]
            errors = io.StringIO()
            with (
                patch("massa.cli.select_environment", return_value=selected),
                patch("massa.cli.run_seed") as run,
                contextlib.redirect_stderr(errors),
            ):
                self.assertEqual(main(args), 1)
                args[args.index("--confirm") + 1] = "test"
                self.assertEqual(main(args), 1)
                run.assert_not_called()
            self.assertNotIn("secret-url", errors.getvalue())
            self.assertFalse((root / "receipt.json").exists())

    def test_apply_denies_read_only_and_stale_plan_inside_transaction(self) -> None:
        selected = SelectedEnvironment(
            "qa",
            Environment(source="env-file", path="p", database="test"),
            "secret-url",
            "localhost",
        )
        with tempfile.TemporaryDirectory() as directory:
            seed = prepare_seed(self.make_project(Path(directory)), "base")
            with patch("massa.seed_project.psycopg.connect") as connect:
                with self.assertRaisesRegex(ValueError, "escrita"):
                    run_seed(selected, seed, "apply", {})
                connect.assert_not_called()
            selected.configuration.writable = True
            conn = MagicMock()
            with (
                patch("massa.seed_project.psycopg.connect") as connect,
                patch(
                    "massa.seed_project.inspect_plan", return_value={"current": True}
                ),
                patch("massa.seed_project.insert_and_verify") as insert,
            ):
                connect.return_value.__enter__.return_value = conn
                with self.assertRaisesRegex(ValueError, "Plano mudou"):
                    run_seed(selected, seed, "apply", {"current": False})
                insert.assert_not_called()
                self.assertIs(
                    connect.return_value.__exit__.call_args.args[0], ValueError
                )

    def test_plan_is_read_only_and_verify_rejects_missing_records(self) -> None:
        selected = SelectedEnvironment(
            "qa",
            Environment(source="env-file", path="p", database="test"),
            "secret-url",
            "localhost",
        )
        with tempfile.TemporaryDirectory() as directory:
            seed = prepare_seed(self.make_project(Path(directory)), "base")
            plan = {"counts": {"clientes": {"insert": 1, "reuse": 0}}}
            conn = MagicMock()
            with (
                patch("massa.seed_project.psycopg.connect") as connect,
                patch("massa.seed_project.inspect_plan", return_value=plan),
                patch("massa.seed_project.insert_and_verify") as insert,
            ):
                connect.return_value.__enter__.return_value = conn
                self.assertEqual(run_seed(selected, seed, "plan"), plan)
                self.assertIn("READ ONLY", conn.execute.call_args_list[0].args[0])
                with self.assertRaisesRegex(ValueError, "ausentes"):
                    run_seed(selected, seed, "verify")
                insert.assert_not_called()

    def test_cli_plan_and_apply_emit_confirmation_and_nonsecret_receipt(self) -> None:
        selected = SelectedEnvironment(
            "qa",
            Environment(source="env-file", path="p", database="test", writable=True),
            "secret-url",
            "localhost",
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project = self.make_project(root)
            plan = {"version": 1, "counts": {"clientes": {"insert": 10, "reuse": 0}}}
            base = [
                "seed",
                "plan",
                "--project",
                str(project),
                "--scenario",
                "base",
                "--environment",
                "qa",
                "--output",
                str(root / "plan.json"),
            ]
            output = io.StringIO()
            with (
                patch("massa.cli.select_environment", return_value=selected),
                patch("massa.cli.run_seed", return_value=plan) as run,
                contextlib.redirect_stdout(output),
            ):
                self.assertEqual(main(base), 0)
                self.assertIn(digest(plan), output.getvalue())
                base[1] = "apply"
                base[-1] = str(root / "receipt.json")
                base += [
                    "--plan",
                    str(root / "plan.json"),
                    "--confirm",
                    "test",
                    "--confirm-plan",
                    digest(plan),
                ]
                self.assertEqual(main(base), 0)
                self.assertEqual(run.call_args.args[3], plan)
                self.assertEqual(json.loads((root / "receipt.json").read_text()), plan)
            self.assertNotIn("secret-url", output.getvalue())

    def test_plan_receipt_digest_can_be_reused_for_confirmation(self) -> None:
        self.assertEqual(digest({"a": 1, "b": 2}), digest({"b": 2, "a": 1}))
        self.assertNotEqual(digest({"a": 1}), digest({"a": 2}))
        self.assertEqual(len(sha256(b"fixture")), 64)
