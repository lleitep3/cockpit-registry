import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from massa.cli import main

EXAMPLES = Path(__file__).resolve().parents[1] / "examples/relational"


class GenerationCliTests(unittest.TestCase):
    def test_validate_and_generate_commands(self) -> None:
        args = [
            "--schema",
            str(EXAMPLES / "schema.yaml"),
            "--recipe",
            str(EXAMPLES / "generation.yaml"),
        ]
        with (
            tempfile.TemporaryDirectory() as directory,
            contextlib.redirect_stdout(io.StringIO()),
        ):
            self.assertEqual(main(["validate", *args]), 0)
            destination = Path(directory) / "output"
            self.assertEqual(main(["generate", *args, "--output", str(destination)]), 0)
            manifest = json.loads((destination / "manifest.json").read_text())
            self.assertEqual(manifest["counts"], {"clientes": 10, "pedidos": 30})

    def test_invalid_contract_returns_error_without_input_values(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            recipe = Path(directory) / "invalid.yaml"
            recipe.write_text("version: 1\nseed: PRIVATE_VALUE\n")
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                result = main(
                    [
                        "validate",
                        "--schema",
                        str(EXAMPLES / "schema.yaml"),
                        "--recipe",
                        str(recipe),
                    ]
                )
            self.assertEqual(result, 1)
            self.assertNotIn("PRIVATE_VALUE", stderr.getvalue())
