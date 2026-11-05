"""Verificações explícitas; não interpreta SQL de checks ou triggers."""

import re
from datetime import datetime
from typing import Any
from uuid import UUID


def unique_keys(table: dict[str, Any]) -> list[list[str]]:
    return [
        constraint["columns"]
        for constraint in table.get("constraints", [])
        if constraint["type"] in {"p", "u"}
    ]


def check_row(table: dict[str, Any], row: dict[str, Any]) -> None:
    for name, column in table["fields"].items():
        value = row[name]
        if value is None:
            if not column["nullable"]:
                raise ValueError(f"Campo obrigatório nulo: {name}")
            continue
        if not valid_type(column["type"], value):
            raise ValueError(f"Valor incompatível com tipo SQL: {name}")


def valid_type(sql_type: str, value: Any) -> bool:
    bounds = {
        "smallint": (-32768, 32767),
        "integer": (-2147483648, 2147483647),
        "bigint": (-9223372036854775808, 9223372036854775807),
    }
    if sql_type in bounds:
        minimum, maximum = bounds[sql_type]
        return type(value) is int and minimum <= value <= maximum
    if sql_type == "boolean":
        return type(value) is bool
    if sql_type == "text" or sql_type.startswith("character varying"):
        limit = re.search(r"\((\d+)\)", sql_type)
        return isinstance(value, str) and (limit is None or len(value) <= int(limit[1]))
    if sql_type == "uuid":
        try:
            UUID(value)
            return isinstance(value, str)
        except (ValueError, TypeError, AttributeError):
            return False
    if sql_type == "timestamp with time zone":
        try:
            return (
                isinstance(value, str)
                and datetime.fromisoformat(value).tzinfo is not None
            )
        except ValueError:
            return False
    raise ValueError(f"Tipo SQL não suportado nesta versão: {sql_type}")
