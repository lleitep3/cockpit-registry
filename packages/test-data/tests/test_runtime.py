"""Behavioral installation tests; opt in to dependency downloads."""

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

PACKAGE = Path(__file__).resolve().parents[1]


@unittest.skipUnless(os.environ.get("TEST_DATA_INSTALL_TESTS") == "1", "opt-in install")
class RuntimeTests(unittest.TestCase):
    def test_install_upgrade_failure_and_generation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            package = root / "package"
            shutil.copytree(
                PACKAGE,
                package,
                ignore=shutil.ignore_patterns(
                    ".venv",
                    ".runtime",
                    "__pycache__",
                    "build",
                    "*.egg-info",
                    ".ruff_cache",
                ),
            )
            env = {
                **os.environ,
                "PYTHON": os.environ.get("PYTHON", "python3.12"),
                "TEST_DATA_RUNTIME_ROOT": str(root / "runtimes"),
            }
            installer = ["sh", str(package / "scripts/install.sh")]
            subprocess.run(installer, env=env, check=True, capture_output=True)
            old_runtime = (package / ".venv").resolve()
            subprocess.run(installer, env=env, check=True, capture_output=True)
            active = (package / ".venv").resolve()
            self.assertNotEqual(old_runtime, active)
            self.assertTrue((old_runtime / "bin/massa").exists())
            failed = subprocess.run(
                installer,
                env={**env, "PYTHON": "/missing-python"},
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(failed.returncode, 0)
            self.assertEqual(active, (package / ".venv").resolve())
            output = root / "data"
            command = [
                str(package / "bin/test-data"),
                "generate",
                "--schema",
                str(package / "boilerplates/schema-seeds/schema.example.yaml"),
                "--recipe",
                str(package / "boilerplates/schema-seeds/generation.example.yaml"),
                "--format",
                "jsonl",
                "--output",
                str(output),
            ]
            subprocess.run(command, cwd=root, check=True, capture_output=True)
            self.assertTrue((output / "manifest.json").exists())
            rejected = subprocess.run(
                command, cwd=root, capture_output=True, check=False
            )
            self.assertNotEqual(rejected.returncode, 0)


if __name__ == "__main__":
    unittest.main()
