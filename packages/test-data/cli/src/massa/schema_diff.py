"""Structural catalogue comparison, without rename or compatibility inference."""

import hashlib
from pathlib import Path
from typing import Any

from massa.recipe import load_mapping

NAMED_COLLECTIONS = frozenset({"constraints", "indexes", "triggers", "enums"})


def named_entries(value: list[Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for item in value:
        if not isinstance(item, dict) or not isinstance(item.get("name"), str):
            raise TypeError("Coleção de metadados precisa de nomes explícitos")
        name = item["name"]
        if name in result:
            raise ValueError("Nome duplicado em coleção de metadados")
        result[name] = item
    return result


def compare_values(before: Any, after: Any, path: list[str]) -> list[dict[str, Any]]:
    changes: list[dict[str, Any]] = []
    if isinstance(before, dict) and isinstance(after, dict):
        if not all(isinstance(key, str) for key in before.keys() | after.keys()):
            raise ValueError("Chaves de metadados precisam ser strings")
        for key in sorted(before.keys() | after.keys()):
            location = [*path, key]
            if key not in before:
                changes.append({"kind": "added", "path": location, "after": after[key]})
            elif key not in after:
                changes.append(
                    {"kind": "removed", "path": location, "before": before[key]}
                )
            else:
                changes.extend(compare_values(before[key], after[key], location))
        if path and path[-1] == "fields" and list(before) != list(after):
            changes.append(
                {
                    "kind": "changed",
                    "path": [*path, "$order"],
                    "before": list(before),
                    "after": list(after),
                }
            )
    elif (
        isinstance(before, list)
        and isinstance(after, list)
        and path
        and path[-1] in NAMED_COLLECTIONS
    ):
        changes.extend(
            compare_values(named_entries(before), named_entries(after), path)
        )
    elif type(before) is not type(after) or before != after:
        changes.append(
            {"kind": "changed", "path": path, "before": before, "after": after}
        )
    return changes


def catalogue(document: dict[str, Any]) -> dict[str, Any]:
    if type(document.get("version")) is not int or document["version"] != 1:
        raise ValueError("Versão de schema não suportada")
    if not isinstance(document.get("entities"), dict):
        raise TypeError("Schema precisa de entities")
    result = dict(document)
    source = result.get("source", {})
    if not isinstance(source, dict):
        raise TypeError("source precisa ser um objeto")
    result["source"] = {
        key: value for key, value in source.items() if key != "server_version"
    }
    return result


def diff_files(before: Path, after: Path) -> dict[str, Any]:
    old_bytes, new_bytes = before.read_bytes(), after.read_bytes()
    old = catalogue(load_mapping(before, content=old_bytes))
    new = catalogue(load_mapping(after, content=new_bytes))
    changes = compare_values(old, new, [])
    return {
        "version": 1,
        "changed": bool(changes),
        "inputs": {
            "before_sha256": hashlib.sha256(old_bytes).hexdigest(),
            "after_sha256": hashlib.sha256(new_bytes).hexdigest(),
        },
        "ignored": ["source.server_version"],
        "changes": changes,
    }
