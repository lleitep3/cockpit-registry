import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from server import ProjectReader


class CanonicalScopeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "dashboard").mkdir()
        (self.root / "requirements").mkdir()
        (self.root / "requirements/old.md").write_text("# Escopo B", encoding="utf-8")
        (self.root / "requirements/mvp-scope.md").write_text("# Escopo B", encoding="utf-8")
        (self.root / "requirements/current.md").write_text("# Novo contrato\n\nRegistro de sessões.", encoding="utf-8")
        self.data = {
            "scope": {"label": "MVP — Registro de sessões", "source": "requirements/current.md"},
            "intentions": [{"id": "INT-SCOPE-B", "title": "Revisar registro de sessões",
                           "objective": "Dois pacientes e quatro sessões",
                           "next_action": "Confirmar ajustes na quinta", "work_units": ["WU-001"]}],
            "work_units": [{"id": "WU-001", "title": "Revisar proposta única",
                            "state": "in_review", "acceptance_criteria": ["Preservar história"]}],
        }

    def payload(self) -> dict:
        (self.root / "dashboard/data.json").write_text(json.dumps(self.data), encoding="utf-8")
        return ProjectReader(self.root).payload()

    def test_current_sources_override_legacy_identifiers(self) -> None:
        payload = self.payload()
        intention = payload["intentions"][0]
        for key in ("title", "objective", "next_action"):
            self.assertEqual(intention[key], self.data["intentions"][0][key])
        self.assertEqual(intention["work_units"][0]["title"], "Revisar proposta única")
        self.assertEqual(intention["work_units"][0]["state"], "in_review")
        self.assertEqual(payload["scope"]["source"], "requirements/current.md")
        self.assertEqual(payload["scope"]["title"], "MVP — Registro de sessões")
        self.assertEqual(payload["scope"], payload["scope_b"])
        self.assertNotIn("Escopo B", payload["scope"]["content"])

    def test_analysis_can_declare_source(self) -> None:
        self.data["scope"].pop("source")
        self.data["analysis"] = {"current_scope_artifact": "requirements/current.md"}
        self.assertEqual(self.payload()["scope"]["source"], "requirements/current.md")

    def test_missing_unsafe_or_symlink_source_never_falls_back(self) -> None:
        with tempfile.TemporaryDirectory() as external:
            secret = Path(external) / "secret.md"
            secret.write_text("private", encoding="utf-8")
            (self.root / "requirements/link.md").symlink_to(secret)
            for source in ("requirements/missing.md", "../secret.md", str(secret), "requirements/link.md"):
                self.data["scope"]["source"] = source
                scope = self.payload()["scope"]
                self.assertIsNone(scope["source"])
                self.assertEqual(scope["content"], "")
                self.assertNotIn("private", str(scope))

    def test_scope_without_declared_source_uses_generic_legacy_document(self) -> None:
        self.data.pop("scope")
        self.assertEqual(self.payload()["scope"]["source"], "requirements/mvp-scope.md")

    def test_other_projects_keep_their_own_words(self) -> None:
        self.data["intentions"][0].update(title="Conferir estoque", objective="Contar peças", next_action="Auditar loja")
        payload = self.payload()
        self.assertEqual(payload["intentions"][0]["title"], "Conferir estoque")
        self.assertEqual(payload["intentions"][0]["objective"], "Contar peças")
        self.assertEqual(payload["intentions"][0]["next_action"], "Auditar loja")
