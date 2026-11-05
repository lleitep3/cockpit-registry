"""Valida assets distribuíveis sem consultar banco ou registros reais."""

import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import yaml

PACKAGE_ROOT = Path(__file__).resolve().parents[1]


class PackageAssetsTests(unittest.TestCase):
    def test_manifest_assets_exist(self) -> None:
        manifest = yaml.safe_load((PACKAGE_ROOT / "cockpit-package.yml").read_text())
        self.assertEqual(manifest["name"], "test-data")
        for features in manifest["features"].values():
            for feature in features:
                self.assertTrue((PACKAGE_ROOT / feature["path"]).exists())

    def test_skill_references_resolve(self) -> None:
        for document in (PACKAGE_ROOT / "skills").rglob("*.md"):
            for target in re.findall(r"\]\(([^)]+)\)", document.read_text()):
                if "://" not in target and not target.startswith("#"):
                    self.assertTrue((document.parent / target).exists(), target)

    def test_templates_and_skill_assets_match(self) -> None:
        for name in (
            "generation.example.yaml",
            "schema.example.yaml",
            "environments.example.yaml",
            "qa-report.md",
        ):
            original = PACKAGE_ROOT / "skills/schema-seed-qa/assets" / name
            copy = PACKAGE_ROOT / "boilerplates/schema-seeds" / name
            self.assertEqual(original.read_bytes(), copy.read_bytes())
        recipe = yaml.safe_load(
            original.with_name("generation.example.yaml").read_text()
        )
        self.assertEqual(recipe["version"], 1)
        self.assertIn("seed", recipe)

    def test_configuration_and_missing_runtime(self) -> None:
        configured = subprocess.run(
            [str(PACKAGE_ROOT / "bin/configure")],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("--env-file", configured.stdout)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "bin").mkdir()
            shutil.copy2(PACKAGE_ROOT / "bin/test-data", root / "bin/test-data")
            missing = subprocess.run(
                [str(root / "bin/test-data"), "--help"],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(missing.returncode, 0)
            self.assertIn("scripts/install.sh", missing.stderr)

    def test_no_project_catalog_or_private_paths(self) -> None:
        for document in PACKAGE_ROOT.rglob("*"):
            if document.is_file() and document.suffix in {".md", ".yaml", ".yml"}:
                self.assertNotIn("/home/lleite/", document.read_text())
        self.assertFalse((PACKAGE_ROOT / "examples/partilhar-schema.yaml").exists())


if __name__ == "__main__":
    unittest.main()
