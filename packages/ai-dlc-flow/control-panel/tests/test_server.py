import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


PACKAGE_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PACKAGE_ROOT / "control-panel"))

from server import ProjectReader  # noqa: E402


class ProjectReaderTest(unittest.TestCase):
    def test_reads_parallel_intentions_and_focus(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = {
                "name": "Demo",
                "phase": "define",
                "focus_intention_id": "INT-1",
                "intentions": [
                    {
                        "id": "INT-1",
                        "title": "Validar escopo",
                        "state": "blocked",
                        "blockers": [{"id": "BLK-1"}],
                    },
                    {"id": "INT-2", "title": "Preparar arquitetura", "state": "active"},
                ],
            }
            (root / "ai-dlc-flow.json").write_text(
                json.dumps(manifest), encoding="utf-8"
            )

            payload = ProjectReader(root).payload()

            self.assertEqual(payload["project"]["focus_intention_id"], "INT-1")
            self.assertEqual(len(payload["intentions"]), 2)
            self.assertEqual(payload["intentions"][0]["state"], "blocked")

    def test_reads_docs_dashboard_contract_without_project_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            dashboard = root / "dashboard"
            dashboard.mkdir()
            (dashboard / "data.json").write_text(
                json.dumps(
                    {
                        "project": "partilhar-aba",
                        "lifecycle": {"macro_phase": "define"},
                        "roadmap": {
                            "items": [
                                {"id": "scope", "label": "Escopo B", "state": "current"},
                                {"id": "build", "label": "Construção", "state": "upcoming"},
                            ]
                        },
                        "gates": [
                            {
                                "id": "G-SCOPE",
                                "state": "ready_for_review",
                                "authority": "human",
                                "required_for": ["WU-001", "WU-002"],
                            }
                        ],
                        "work_units": [
                            {
                                "id": "WU-001",
                                "title": "confirm_first_useful_mvp_step",
                                "state": "in_review",
                                "owner_type": "human",
                                "lifecycle": "validate",
                                "inputs": ["ART-SCOPE-B-001"],
                                "exit_gate": "G-SCOPE",
                                "next_action": "validar B com a clínica",
                                "blockers": ["HD-001"],
                                "dependencies": [],
                                "acceptance_criteria": ["clínica confirma B"],
                                "evidence_required": ["decision_record"],
                            }
                        ],
                        "intentions": [
                            {
                                "id": "INT-SCOPE-B",
                                "title": "validate_first_useful_mvp_step",
                                "objective": "confirm_with_clinic_that_scope_b_is_the_first_useful_step",
                                "phase": "validate",
                                "state": "current",
                                "priority": "now",
                                "owner": "clínica",
                                "gate": "G-SCOPE",
                                "work_units": ["WU-001"],
                                "blockers": ["HD-001"],
                                "dependencies": [],
                                "next_action": "validate_B_with_clinic_and_record_the_decision",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            payload = ProjectReader(root).payload()

            self.assertEqual(payload["project"]["name"], "partilhar-aba")
            self.assertEqual(payload["project"]["phase"], "define")
            self.assertEqual(payload["project"]["focus_intention_id"], "INT-SCOPE-B")
            self.assertEqual(payload["roadmap"][0]["status"], "current")
            self.assertEqual(len(payload["intentions"]), 1)
            self.assertEqual(payload["gates"][0]["id"], "G-SCOPE")
            self.assertEqual(payload["gates"][0]["state_label"], "pronto para revisão")
            self.assertEqual(payload["gates"][0]["work_units"], ["WU-001", "WU-002"])
            self.assertEqual(
                payload["gates"][0]["work_unit_details"][0]["title"],
                "confirm_first_useful_mvp_step",
            )
            self.assertEqual(
                payload["intentions"][0]["title"],
                "validate_first_useful_mvp_step",
            )
            self.assertEqual(
                payload["intentions"][0]["phase"],
                "Validação",
            )
            self.assertEqual(payload["intentions"][0]["work_units"][0]["id"], "WU-001")
            self.assertEqual(
                payload["intentions"][0]["work_units"][0]["title"],
                "confirm_first_useful_mvp_step",
            )
            self.assertEqual(
                payload["intentions"][0]["work_units"][0]["state_label"],
                "em revisão",
            )
            self.assertEqual(
                payload["intentions"][0]["work_units"][0]["lifecycle"],
                "validate",
            )
            self.assertEqual(
                payload["intentions"][0]["work_units"][0]["inputs"],
                ["ART-SCOPE-B-001"],
            )

    def test_extracts_decisions_and_scope_b_from_docs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            decisions = root / "architecture" / "decisions"
            decisions.mkdir(parents=True)
            (decisions / "ADR-0001.md").write_text(
                "# Escolha de arquitetura\n\n**Data:** 2026-09-18\n\nDecisão registrada.",
                encoding="utf-8",
            )
            requirements = root / "requirements"
            requirements.mkdir()
            (requirements / "mvp-scope.md").write_text(
                "# MVP\n\n| B — Supervisão | Pendências e revisão |\n",
                encoding="utf-8",
            )

            payload = ProjectReader(root).payload()

            self.assertEqual(payload["decisions"][0]["id"], "ADR-0001")
            self.assertEqual(payload["scope_b"]["summary"], "MVP")
            self.assertEqual(payload["scope_b"]["source"], "requirements/mvp-scope.md")

    def test_infers_decision_date_from_git_creation_commit(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            decisions = root / "architecture" / "decisions"
            decisions.mkdir(parents=True)
            (decisions / "ADR-0002.md").write_text(
                "# Decisão sem data no documento\n\nConteúdo da decisão.",
                encoding="utf-8",
            )

            git_result = type(
                "CompletedProcess",
                (),
                {"stdout": "2026-09-17T16:59:49-03:00|4bfd759|docs: add ADR\n"},
            )()
            with patch("server.subprocess.run", return_value=git_result):
                payload = ProjectReader(root).payload()

            decision = payload["decisions"][0]
            self.assertEqual(decision["date"], "2026-09-17")
            self.assertEqual(decision["date_source"], "commit")
            self.assertEqual(decision["commit"], "4bfd759")


if __name__ == "__main__":
    unittest.main()
