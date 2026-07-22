from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

from app.services.kb_graph import build_kb_graph, search_kb


def test_build_kb_graph_empty(tmp_path: Path):
    cockpit_dir = tmp_path / ".cockpit"
    cockpit_dir.mkdir()
    with patch.dict(os.environ, {"COCKPIT_HOME": str(cockpit_dir)}):
        graph = build_kb_graph()
        assert graph["nodes"] == []
        assert graph["edges"] == []


def test_build_kb_graph_with_links(tmp_path: Path):
    cockpit_dir = tmp_path / ".cockpit"
    kb_dir = cockpit_dir / "kb"
    kb_dir.mkdir(parents=True)
    (kb_dir / "README.md").write_text("# Root\n\n[[getting-started]]")
    (kb_dir / "getting-started.md").write_text("# Getting Started\n\nSee [README](README.md)")
    with patch.dict(os.environ, {"COCKPIT_HOME": str(cockpit_dir)}):
        graph = build_kb_graph()
        assert len(graph["nodes"]) == 2
        assert len(graph["edges"]) >= 1
        ids = {n["id"] for n in graph["nodes"]}
        assert "readme" in ids
        assert "getting-started" in ids


def test_search_kb(tmp_path: Path):
    cockpit_dir = tmp_path / ".cockpit"
    kb_dir = cockpit_dir / "kb"
    kb_dir.mkdir(parents=True)
    (kb_dir / "findme.md").write_text("this is a special keyword xyz")
    with patch.dict(os.environ, {"COCKPIT_HOME": str(cockpit_dir)}):
        results = search_kb("special")
        assert len(results) == 1
        assert results[0]["name"] == "findme"
