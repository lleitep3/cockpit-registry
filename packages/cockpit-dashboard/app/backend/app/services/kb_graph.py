from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path
from typing import Any

import structlog

from app.services.cockpit_reader import list_kb

logger = structlog.get_logger()

LINK_RE = re.compile(r"\[\[([^\]]+)\]\]|")  # support [[Note]] style wiki links
MARKDOWN_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+\.md)\)")


def _extract_links(text: str) -> set[str]:
    links: set[str] = set()
    for match in LINK_RE.finditer(text):
        if match.group(1):
            links.add(match.group(1).strip().lower().replace(" ", "-"))
    for match in MARKDOWN_LINK_RE.finditer(text):
        target = match.group(2).split("/")[-1].replace(".md", "").strip().lower().replace(" ", "-")
        if target:
            links.add(target)
    return links


def build_kb_graph() -> dict[str, Any]:
    """Constroi grafo de notas e links entre elas."""
    kb = list_kb()
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    node_ids: set[str] = set()
    link_counts: dict[str, int] = defaultdict(int)

    for entry in kb:
        doc_id = entry["name"].lower().replace(" ", "-")
        node_ids.add(doc_id)
        nodes.append({"id": doc_id, "label": entry["name"], "path": entry["path"]})

    for entry in kb:
        doc_id = entry["name"].lower().replace(" ", "-")
        try:
            text = Path(entry["path"]).read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            logger.warning("kb_read_error", path=entry["path"], error=str(e))
            continue
        targets = _extract_links(text)
        for target in targets:
            if target in node_ids:
                edges.append({"source": doc_id, "target": target})
                link_counts[doc_id] += 1
                link_counts[target] += 1

    # Mark orphan nodes (no links)
    for node in nodes:
        node["orphan"] = link_counts[node["id"]] == 0

    return {"nodes": nodes, "edges": edges}


def search_kb(query: str) -> list[dict[str, Any]]:
    """Busca fuzzy simples nos documentos do KB."""
    q = query.lower()
    results = []
    for entry in list_kb():
        try:
            text = Path(entry["path"]).read_text(encoding="utf-8", errors="replace").lower()
        except Exception:
            text = ""
        title = entry["name"].lower()
        if q in title or q in text:
            snippet = text[max(0, text.find(q) - 60):text.find(q) + 120] if q in text else ""
            results.append(
                {
                    "id": entry["name"].lower().replace(" ", "-"),
                    "name": entry["name"],
                    "path": entry["path"],
                    "snippet": snippet,
                }
            )
    return results
