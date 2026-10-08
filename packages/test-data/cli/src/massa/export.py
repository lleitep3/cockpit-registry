"""Exportação para diretório novo e manifesto sem caminhos privados."""

import hashlib
import json
import platform
from importlib.metadata import version
from pathlib import Path
from typing import Any

from massa.generator import generate
from massa.recipe import Recipe, load_mapping


def sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def export_jsonl(schema_path: Path, recipe_path: Path, output: Path) -> dict[str, Any]:
    if output.exists():
        raise ValueError("Diretório de saída já existe; escolha outro destino")
    schema_bytes = schema_path.read_bytes()
    recipe_bytes = recipe_path.read_bytes()
    schema = load_mapping(schema_path, schema_bytes)
    recipe = Recipe.model_validate(load_mapping(recipe_path, recipe_bytes))
    data = generate(schema, recipe)
    files = {
        f"{name}.jsonl": "".join(
            json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            + "\n"
            for row in rows
        ).encode("utf-8")
        for name, rows in data.items()
    }
    manifest = build_manifest(recipe, schema_bytes, recipe_bytes, data, files)
    output.mkdir(parents=False, exist_ok=False)
    # Manifesto por último: sua presença indica exportação concluída.
    for name, content in files.items():
        (output / name).write_bytes(content)
    (output / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifest


def build_manifest(
    recipe: Recipe,
    schema_bytes: bytes,
    recipe_bytes: bytes,
    data: dict[str, list[dict[str, Any]]],
    files: dict[str, bytes],
) -> dict[str, Any]:
    return {
        "version": 1,
        "format": "jsonl",
        "seed": recipe.seed,
        "locale": recipe.locale,
        "reference_time": recipe.reference_time,
        "versions": {
            "python": platform.python_version(),
            **{
                name: version(name)
                for name in ("massa-cli", "Faker", "pydantic", "PyYAML")
            },
        },
        "inputs": {
            "schema_sha256": sha256(schema_bytes),
            "recipe_sha256": sha256(recipe_bytes),
        },
        "counts": {name: len(rows) for name, rows in data.items()},
        "files": {name: sha256(content) for name, content in files.items()},
        "generation_order": list(data),
        "verification": {
            "types_nullability_primary_unique_foreign_keys": "passed",
            "database_load": "not_executed",
            "sql_checks_triggers_indexes_domains_rls": "not_verified",
        },
        "schema_entities_generated": sorted(data),
    }
