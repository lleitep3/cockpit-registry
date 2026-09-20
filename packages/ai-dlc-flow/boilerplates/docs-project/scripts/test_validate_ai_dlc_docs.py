import tempfile
import unittest
from pathlib import Path

from validate_ai_dlc_docs import has_heading_and_status, validate


class DocumentationValidatorTests(unittest.TestCase):
    def test_title_and_status_are_required(self) -> None:
        self.assertTrue(has_heading_and_status("# Intent\n\n**Status:** proposed\n"))
        self.assertFalse(has_heading_and_status("# Intent\n"))

    def test_required_files_are_checked(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "docs/ai-dlc").mkdir(parents=True)
            (root / "docs/ai-dlc/README.md").write_text("# AI-DLC\n", encoding="utf-8")

            errors = validate(root)

            self.assertIn("missing required AI-DLC file: docs/ai-dlc/backlog.md", errors)


if __name__ == "__main__":
    unittest.main()
