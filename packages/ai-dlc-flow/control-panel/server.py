#!/usr/bin/env python3
"""Serve a provider-neutral AI-DLC control panel for a documentation repo."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from datetime import datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


PHASES = [
    ("intent", "Intenção"),
    ("explore", "Explorar"),
    ("define", "Definir"),
    ("design", "Desenhar"),
    ("validate", "Validar"),
    ("plan", "Planejar"),
    ("build", "Construir"),
    ("verify", "Verificar"),
    ("release", "Liberar"),
    ("observe", "Observar"),
    ("learn", "Aprender"),
    ("replan", "Replanejar"),
]

INTENTION_TITLES = {
    "INT-SCOPE-B": "Validar o primeiro degrau útil do MVP",
    "INT-DOMAIN-FORMS": "Validar formulários e pontuação",
    "INT-PATIENT-SESSION": "Fechar paciente, sessão e encaminhamento",
    "INT-AUTHORIZATION": "Aprovar autorização e auditoria",
    "INT-UX-VERTICAL-SLICE": "Validar o fluxo vertical de app e web",
    "INT-ARCHITECTURE": "Escolher backend, repositórios e ambiente",
    "INT-IDENTITY-ACCESS": "Definir login e cadastro profissional",
    "INT-DATA-FOUNDATION": "Mapear os dados mínimos do MVP",
}

INTENTION_OBJECTIVES = {
    "INT-SCOPE-B": "Confirmar com a clínica se B é o primeiro degrau útil.",
    "INT-DOMAIN-FORMS": "Confirmar formulários, tipos, opções, pesos e fórmula.",
    "INT-PATIENT-SESSION": "Definir cenários operacionais e transições.",
    "INT-AUTHORIZATION": "Fechar perfis, recursos, escopos e auditoria.",
    "INT-UX-VERTICAL-SLICE": "Representar o fluxo de criar, preencher, revisar e consultar.",
    "INT-ARCHITECTURE": "Definir topologia, repositórios e ambiente fictício.",
    "INT-IDENTITY-ACCESS": "Definir login, convite, vinculação e estados de acesso.",
    "INT-DATA-FOUNDATION": "Separar dados mínimos, candidatos e perguntas abertas.",
}

INTENTION_NEXT_ACTIONS = {
    "INT-SCOPE-B": "Validar B com a clínica e registrar a decisão.",
    "INT-DOMAIN-FORMS": "Obter materiais reais e validação clínica.",
    "INT-PATIENT-SESSION": "Validar os cenários operacionais com a clínica.",
    "INT-AUTHORIZATION": "Revisar a matriz antes de implementar autorização.",
    "INT-UX-VERTICAL-SLICE": "Preparar a revisão do fluxo depois da definição de escopo.",
    "INT-ARCHITECTURE": "Decidir a topologia antes de criar código do produto.",
    "INT-IDENTITY-ACCESS": "Decidir a política de e-mail, login, convite e vinculação.",
    "INT-DATA-FOUNDATION": "Revisar o inventário mínimo e as perguntas clínicas abertas.",
}

PHASE_LABELS = {
    "intent": "Intenção",
    "explore": "Exploração",
    "define": "Definição",
    "design": "Design",
    "validate": "Validação",
    "plan": "Planejamento",
    "build": "Construção",
    "verify": "Verificação",
    "release": "Liberação",
}

WORK_UNIT_TITLES = {
    "WU-001": "Confirmar o primeiro degrau útil do MVP",
    "WU-002": "Validar dois formulários reais e regras de pontuação",
    "WU-003": "Fechar cenários de paciente, sessão e encaminhamento",
    "WU-004": "Aprovar matriz de permissões e escopos",
    "WU-005": "Validar fluxo vertical de app e web",
    "WU-006": "Escolher backend, repositórios e ambiente de teste",
    "WU-007": "Transformar escopo aceito em unidades executáveis",
    "WU-008": "Construir fatia vertical dos formulários",
    "WU-009": "Verificar autorização, versões, pontuação e canais",
    "WU-010": "Autorizar liberação do piloto controlado",
    "WU-011": "Preparar identidade e onboarding profissional",
    "WU-012": "Mapear contrato mínimo de dados do MVP",
    "WU-013": "Preparar baseline local de backend e infraestrutura",
}

WORK_UNIT_STATE_LABELS = {
    "blocked": "bloqueada",
    "in_review": "em revisão",
    "proposed": "proposta",
    "active": "ativa",
    "completed": "concluída",
}


def _clean_scalar(value: str) -> str:
    """Read a simple YAML-like scalar without requiring PyYAML."""
    value = value.strip().strip('"').strip("'")
    return value.split(" #", 1)[0].strip()


class ProjectReader:
    """Build the panel contract from versioned project documents."""

    def __init__(self, root: Path) -> None:
        self.root = root.resolve()

    def payload(self) -> dict[str, Any]:
        metadata = self._metadata()
        dashboard_data = self._dashboard_data()
        if not metadata and dashboard_data:
            return self._dashboard_payload(dashboard_data)

        current_phase = self._phase(metadata)
        return {
            "project": {
                "name": metadata.get("name") or self.root.name,
                "summary": metadata.get(
                    "summary",
                    "Painel operacional do AI-DLC Flow.",
                ),
                "started_at": metadata.get("started_at") or self._git_start(),
                "phase": current_phase,
                "repo_root": str(self.root),
                "focus_intention_id": self._focus_intention_id(metadata),
            },
            "intentions": self._intentions(metadata),
            "roadmap": self._roadmap(current_phase),
            "decisions": self._decisions(),
            "scope_b": self._scope_b(),
            "signals": self._signals(),
            "gates": [],
            "generated_at": datetime.now().astimezone().isoformat(),
        }

    def _dashboard_data(self) -> dict[str, Any] | None:
        """Read the generated contract used by docs-only AI-DLC repositories."""
        path = self.root / "dashboard" / "data.json"
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None
        return raw if isinstance(raw, dict) else None

    def _dashboard_payload(self, data: dict[str, Any]) -> dict[str, Any]:
        """Adapt the docs dashboard contract to the live control-panel contract."""
        lifecycle = data.get("lifecycle", {})
        current_phase = lifecycle.get("macro_phase", "unknown")
        if current_phase not in {item[0] for item in PHASES}:
            current_phase = "unknown"
        intentions = self._normalise_intentions(
            data.get("intentions", []),
            humanize=True,
            work_units_by_id=self._dashboard_work_units(data),
        )
        focus = next(
            (
                item
                for item in intentions
                if item["state"] == "current" or item["priority"] == "now"
            ),
            None,
        )
        return {
            "project": {
                "name": str(data.get("project") or self.root.name),
                "summary": (
                    "Evolução do produto clínico com decisões humanas, "
                    "evidências e gates rastreáveis."
                ),
                "started_at": self._git_start(),
                "phase": current_phase,
                "repo_root": str(self.root),
                "focus_intention_id": focus["id"] if focus else None,
            },
            "intentions": intentions,
            "roadmap": self._dashboard_roadmap(data, current_phase),
            "decisions": self._decisions(),
            "scope_b": self._scope_b(),
            "signals": self._signals(),
            "gates": self._dashboard_gates(data),
            "generated_at": datetime.now().astimezone().isoformat(),
        }

    def _metadata(self) -> dict[str, Any]:
        candidates = [
            self.root / ".ai-dlc-flow" / "project.json",
            self.root / "ai-dlc-flow.json",
            self.root / ".ai-dlc-flow.yml",
            self.root / "ai-dlc-flow.yml",
        ]
        for path in candidates:
            if not path.is_file():
                continue
            if path.suffix == ".json":
                try:
                    raw = json.loads(path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    continue
                return raw if isinstance(raw, dict) else {}
            return self._simple_yaml(path)
        return {}

    @staticmethod
    def _simple_yaml(path: Path) -> dict[str, Any]:
        values: dict[str, str] = {}
        pattern = re.compile(
            r"^\s*(name|project_name|summary|phase|current_phase|started_at)"
            r"\s*:\s*(.*?)\s*$"
        )
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except OSError:
            return values
        for line in lines:
            match = pattern.match(line)
            if match:
                values[match.group(1)] = _clean_scalar(match.group(2))
        if "project_name" in values and "name" not in values:
            values["name"] = values["project_name"]
        if "current_phase" in values and "phase" not in values:
            values["phase"] = values["current_phase"]
        return values

    def _focus_intention_id(self, metadata: dict[str, Any]) -> str | None:
        focus = metadata.get("focus_intention_id", metadata.get("focus"))
        return str(focus) if focus else None

    def _intentions(self, metadata: dict[str, Any]) -> list[dict[str, Any]]:
        """Read parallel intentions from the project manifest or JSON records."""
        candidates: list[Any] = []
        manifest_intentions = metadata.get("intentions")
        if isinstance(manifest_intentions, list):
            candidates.extend(manifest_intentions)
        intention_dir = self.root / ".ai-dlc-flow" / "intentions"
        if intention_dir.is_dir():
            for path in sorted(intention_dir.glob("*.json")):
                try:
                    value = json.loads(path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    continue
                candidates.append(value)

        return self._normalise_intentions(candidates)

    @staticmethod
    def _normalise_intentions(
        candidates: Any,
        *,
        humanize: bool = False,
        work_units_by_id: dict[str, dict[str, Any]] | None = None,
    ) -> list[dict[str, Any]]:
        if not isinstance(candidates, list):
            return []

        intentions: list[dict[str, Any]] = []
        for item in candidates:
            if not isinstance(item, dict) or not item.get("id"):
                continue
            intention_id = str(item["id"])
            title = str(item.get("title", intention_id))
            objective = str(item.get("objective", ""))
            phase = str(item.get("phase", "unknown"))
            next_action = str(item.get("next_action", "Não registrada"))
            if humanize:
                title = INTENTION_TITLES.get(intention_id, title)
                objective = INTENTION_OBJECTIVES.get(intention_id, objective)
                phase = PHASE_LABELS.get(phase, phase)
                next_action = INTENTION_NEXT_ACTIONS.get(intention_id, next_action)
            raw_work_units = item.get("work_units", [])
            work_units: list[Any] = []
            if isinstance(raw_work_units, list):
                for unit in raw_work_units:
                    if isinstance(unit, dict):
                        work_units.append(unit)
                        continue
                    unit_id = str(unit)
                    resolved = (work_units_by_id or {}).get(unit_id)
                    work_units.append(
                        resolved
                        or {
                            "id": unit_id,
                            "title": "Registro não encontrado",
                            "state": "not_registered",
                            "state_label": "não registrado",
                        }
                    )

            intentions.append(
                {
                    "id": intention_id,
                    "title": title,
                    "objective": objective,
                    "phase": phase,
                    "state": str(item.get("state", "proposed")),
                    "owner": str(item.get("owner", "não definido")),
                    "priority": str(item.get("priority", "normal")),
                    "gate": str(item.get("gate", "não definido")),
                    "next_action": next_action,
                    "dependencies": item.get("dependencies", []),
                    "blockers": item.get("blockers", []),
                    "history": item.get("history", []),
                    "work_units": work_units,
                }
            )
        return intentions

    def _dashboard_roadmap(
        self, data: dict[str, Any], current_phase: str
    ) -> list[dict[str, str]]:
        roadmap = data.get("roadmap", {})
        items = roadmap.get("items", []) if isinstance(roadmap, dict) else []
        if not isinstance(items, list) or not items:
            return self._roadmap(current_phase)

        state_map = {
            "documented": "done",
            "completed": "done",
            "done": "done",
            "current": "current",
            "upcoming": "upcoming",
            "future": "upcoming",
        }
        return [
            {
                "id": str(item.get("id", "step")),
                "label": str(item.get("label", item.get("id", "Etapa"))),
                "status": state_map.get(
                    str(item.get("state", item.get("status", "upcoming"))),
                    "upcoming",
                ),
            }
            for item in items
            if isinstance(item, dict)
        ]

    @staticmethod
    def _dashboard_gates(data: dict[str, Any]) -> list[dict[str, Any]]:
        gates = data.get("gates", [])
        if not isinstance(gates, list):
            return []
        work_units_by_id = ProjectReader._dashboard_work_units(data)
        authority_labels = {
            "human": "autoridade humana",
            "human_plus_agent": "humana + agente",
            "agent_check_plus_human_exceptions": "agente + exceções humanas",
            "agent_or_ci": "agente ou CI",
            "qa_agent_plus_human_when_required": "QA + humano quando necessário",
        }
        state_labels = {
            "open": "aberto",
            "ready_for_review": "pronto para revisão",
            "passed": "aprovado",
            "failed": "falhou",
            "waived_by_human": "dispensado por humano",
            "superseded": "substituído",
        }
        result: list[dict[str, Any]] = []
        for gate in gates:
            if not isinstance(gate, dict) or not gate.get("id"):
                continue
            work_units = gate.get("required_for", [])
            if not isinstance(work_units, list):
                work_units = []
            state = str(gate.get("state", "open"))
            authority = str(gate.get("authority", "não definida"))
            result.append(
                {
                    "id": str(gate["id"]),
                    "state": state,
                    "state_label": state_labels.get(state, state),
                    "authority": authority_labels.get(authority, authority),
                    "work_units": [str(unit) for unit in work_units],
                    "work_unit_details": [
                        work_units_by_id[unit]
                        for unit in work_units
                        if str(unit) in work_units_by_id
                    ],
                }
            )
        return result

    @staticmethod
    def _dashboard_work_units(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
        work_units = data.get("work_units", [])
        if not isinstance(work_units, list):
            return {}
        details: dict[str, dict[str, Any]] = {}
        for unit in work_units:
            if not isinstance(unit, dict) or not unit.get("id"):
                continue
            unit_id = str(unit["id"])
            state = str(unit.get("state", "proposed"))
            title = WORK_UNIT_TITLES.get(unit_id, str(unit.get("title", unit_id)))
            details[unit_id] = {
                "id": unit_id,
                "title": title,
                "lifecycle": str(unit.get("lifecycle", "não definido")),
                "state": state,
                "state_label": WORK_UNIT_STATE_LABELS.get(state, state),
                "owner": str(unit.get("owner_type", "não definido")),
                "exit_gate": str(unit.get("exit_gate", "não definido")),
                "next_action": str(unit.get("next_action", "Não registrada")),
                "inputs": [str(item) for item in unit.get("inputs", [])],
                "blockers": [str(item) for item in unit.get("blockers", [])],
                "dependencies": [str(item) for item in unit.get("dependencies", [])],
                "acceptance_criteria": [
                    str(item) for item in unit.get("acceptance_criteria", [])
                ],
                "evidence_required": [
                    str(item) for item in unit.get("evidence_required", [])
                ],
            }
        return details

    def _phase(self, metadata: dict[str, str]) -> str:
        phase = metadata.get("phase", "").strip().lower()
        return phase if phase in {item[0] for item in PHASES} else "unknown"

    def _git_start(self) -> str | None:
        try:
            result = subprocess.run(
                ["git", "-C", str(self.root), "log", "--reverse", "--format=%aI", "-1"],
                capture_output=True,
                check=True,
                text=True,
                timeout=3,
            )
        except (OSError, subprocess.SubprocessError):
            return None
        value = result.stdout.strip()
        return value or None

    def _roadmap(self, current_phase: str) -> list[dict[str, str]]:
        current_index = next(
            (index for index, item in enumerate(PHASES) if item[0] == current_phase),
            -1,
        )
        roadmap: list[dict[str, str]] = []
        for index, (phase_id, label) in enumerate(PHASES):
            if current_index >= 0 and index < current_index:
                status = "done"
            elif index == current_index:
                status = "current"
            else:
                status = "upcoming"
            roadmap.append(
                {
                    "id": phase_id,
                    "label": label,
                    "status": status,
                }
            )
        return roadmap

    def _decision_files(self) -> list[Path]:
        candidates = [self.root / "architecture" / "decisions", self.root / "decisions"]
        files: set[Path] = set()
        for directory in candidates:
            if directory.is_dir():
                files.update(path for path in directory.glob("*.md") if path.is_file())
        return sorted(files, key=lambda path: path.name.lower(), reverse=True)

    def _decisions(self) -> list[dict[str, str | None]]:
        decisions: list[dict[str, str | None]] = []
        for path in self._decision_files():
            try:
                content = path.read_text(encoding="utf-8")
            except OSError:
                continue
            heading = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
            date = re.search(r"(?:date|data)\s*[:|]\s*[*_]*([0-9]{4}-[0-9]{2}-[0-9]{2})", content, re.IGNORECASE)
            status = re.search(r"status\s*[:|]\s*[*_]*([^\n*_]+)", content, re.IGNORECASE)
            git_metadata = self._git_decision_metadata(path)
            date_value = date.group(1) if date else git_metadata.get("date")
            date_source = "documento" if date else git_metadata.get("date_source")
            summary = self._summary(content)
            decisions.append(
                {
                    "id": path.stem,
                    "title": heading.group(1).strip() if heading else path.stem,
                    "date": date_value,
                    "date_source": date_source,
                    "commit": git_metadata.get("commit"),
                    "commit_subject": git_metadata.get("commit_subject"),
                    "status": status.group(1).strip() if status else "registrada",
                    "path": path.relative_to(self.root).as_posix(),
                    "summary": summary,
                }
            )
        return decisions

    def _git_decision_metadata(self, path: Path) -> dict[str, str | None]:
        """Infer an ADR date from the commit that added its file."""
        try:
            relative_path = path.relative_to(self.root).as_posix()
            result = subprocess.run(
                [
                    "git",
                    "-C",
                    str(self.root),
                    "log",
                    "--follow",
                    "--diff-filter=A",
                    "--format=%cI|%h|%s",
                    "-1",
                    "--",
                    relative_path,
                ],
                capture_output=True,
                check=True,
                text=True,
                timeout=3,
            )
        except (OSError, subprocess.SubprocessError, ValueError):
            return {}

        line = result.stdout.strip()
        if not line:
            return {}
        date, separator, remainder = line.partition("|")
        if not separator:
            return {}
        commit, separator, subject = remainder.partition("|")
        return {
            "date": date[:10],
            "date_source": "commit",
            "commit": commit or None,
            "commit_subject": subject or None,
        }

    @staticmethod
    def _summary(content: str) -> str:
        for block in re.split(r"\n\s*\n", content):
            text = re.sub(r"[*_`>#]", "", block).strip()
            if text and not text.startswith("---") and not text.startswith("|"):
                if not text.lower().startswith(("status:", "data:", "date:")):
                    return text[:240]
        return "Sem resumo registrado."

    def _scope_file(self) -> Path | None:
        candidates = [
            self.root / "requirements" / "mvp-step-b-scope.md",
            self.root / "requirements" / "mvp-scope.md",
            self.root / "requirements" / "scope-b.md",
            self.root / "scope-b.md",
        ]
        for path in candidates:
            if path.is_file():
                return path
        matches = sorted(self.root.rglob("*mvp-scope*.md"))
        return matches[0] if matches else None

    def _scope_b(self) -> dict[str, str | None]:
        path = self._scope_file()
        if path is None:
            return {
                "title": "Escopo B — Supervisão",
                "summary": "Documento de escopo B não encontrado no repositório.",
                "source": None,
                "content": "",
            }
        try:
            content = path.read_text(encoding="utf-8")
        except OSError:
            content = ""
        row = re.search(r"^\|\s*B\s*[—-]\s*(.+?)\s*\|", content, re.MULTILINE)
        summary = row.group(1).strip() if row else self._summary(content)
        return {
            "title": "Escopo B — Supervisão",
            "summary": summary,
            "source": path.relative_to(self.root).as_posix(),
            "content": content[:20000],
        }

    def _signals(self) -> dict[str, int]:
        markdown_files = [
            path
            for path in self.root.rglob("*.md")
            if ".git" not in path.parts and "node_modules" not in path.parts
        ]
        requirements_dir = self.root / "requirements"
        evidence_dirs = {"evidence", "evidences"}
        evidence_count = sum(
            1
            for path in markdown_files
            if any(part.lower() in evidence_dirs for part in path.parts)
        )
        return {
            "documents": len(markdown_files),
            "requirements": sum(
                1 for path in markdown_files if requirements_dir in path.parents
            ),
            "decisions": len(self._decision_files()),
            "evidence": evidence_count,
        }


class PanelHandler(BaseHTTPRequestHandler):
    """Serve the panel and its repository-backed JSON contract."""

    server_version = "ai-dlc-flow-control-panel/0.2"

    def __init__(
        self,
        *args: Any,
        repository_root: Path,
        static_root: Path,
        base_path: str,
        **kwargs: Any,
    ) -> None:
        self.repository_root = repository_root
        self.static_root = static_root
        self.base_path = base_path.rstrip("/") or "/"
        super().__init__(*args, **kwargs)

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        relative_path = self._without_base(path)
        if relative_path in {"/api/project", "/api/project/"}:
            self._json(ProjectReader(self.repository_root).payload())
            return
        if relative_path in {"/api/health", "/api/health/"}:
            self._json({"status": "ok"})
            return
        self._static(relative_path)

    def _without_base(self, path: str) -> str:
        if self.base_path == "/":
            return path
        if path == self.base_path:
            return "/"
        if path.startswith(f"{self.base_path}/"):
            return path[len(self.base_path) :]
        return path

    def _json(self, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _static(self, relative_path: str) -> None:
        target = (self.static_root / relative_path.lstrip("/")).resolve()
        if relative_path in {"", "/"}:
            target = self.static_root / "index.html"
        if self.static_root not in target.parents and target != self.static_root:
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        if not target.is_file():
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        content_types = {
            ".css": "text/css; charset=utf-8",
            ".html": "text/html; charset=utf-8",
            ".js": "text/javascript; charset=utf-8",
            ".svg": "image/svg+xml",
        }
        body = target.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header(
            "Content-Type",
            content_types.get(target.suffix, "application/octet-stream"),
        )
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format_string: str, *args: Any) -> None:
        print(f"[control-panel] {format_string % args}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--base-path", default="/partilhar")
    args = parser.parse_args()
    repository_root = args.root.resolve()
    if not repository_root.is_dir():
        parser.error(f"repository root does not exist: {repository_root}")
    static_root = Path(__file__).resolve().parent

    def handler(*handler_args: Any, **handler_kwargs: Any) -> PanelHandler:
        return PanelHandler(
            *handler_args,
            repository_root=repository_root,
            static_root=static_root,
            base_path=args.base_path,
            **handler_kwargs,
        )

    server = ThreadingHTTPServer((args.host, args.port), handler)
    print(
        f"AI-DLC Control Panel: http://{args.host}:{args.port}"
        f"{args.base_path.rstrip('/')}/"
    )
    server.serve_forever()


if __name__ == "__main__":
    main()
