"""Named PostgreSQL environments: persist references, never connection strings."""

import json
import os
import re
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

import psycopg
import yaml
from dotenv import dotenv_values
from psycopg.conninfo import conninfo_to_dict
from pydantic import Field

from massa.recipe import IDENTIFIER, Contract, load_mapping


class Environment(Contract):
    source: Literal["env-file", "postman"]
    path: str = Field(min_length=1)
    variable: str = Field(default="DATABASE_URL", pattern=IDENTIFIER)
    database: str = Field(min_length=1)
    schema_name: str = Field(default="public", alias="schema", pattern=IDENTIFIER)
    writable: bool = False
    resettable: bool = False


class Registry(Contract):
    version: Literal[1] = 1
    environments: dict[str, Environment] = Field(default_factory=dict)


@dataclass(frozen=True)
class SelectedEnvironment:
    name: str
    configuration: Environment
    connection: str = field(repr=False)
    host: str


def read_connection(source: str, path: Path, variable: str) -> str:
    if source == "env-file":
        value = dotenv_values(path, interpolate=False).get(variable)
    else:
        try:
            document = json.loads(path.read_bytes())
        except (ValueError, UnicodeError) as error:
            raise ValueError("Export Postman inválido") from error
        if not isinstance(document, dict) or not isinstance(
            document.get("values"), list
        ):
            raise ValueError("Export Postman precisa de values")
        matches = [
            item.get("value")
            for item in document["values"]
            if isinstance(item, dict)
            and item.get("key") == variable
            and item.get("enabled", True) is not False
        ]
        if len(matches) != 1:
            raise ValueError("Variável de conexão ausente ou duplicada no Postman")
        value = matches[0]
    if not isinstance(value, str) or not value:
        raise ValueError("Variável de conexão ausente ou vazia")
    return value


def select_environment(registry_path: Path, name: str) -> SelectedEnvironment:
    registry = Registry.model_validate(load_mapping(registry_path))
    if name not in registry.environments:
        raise ValueError("Ambiente não cadastrado")
    return resolve_environment(registry_path, name, registry.environments[name])


def resolve_environment(
    registry_path: Path, name: str, environment: Environment
) -> SelectedEnvironment:
    source_path = Path(environment.path)
    if not source_path.is_absolute():
        source_path = registry_path.resolve().parent / source_path
    if not source_path.is_file():
        raise ValueError("Arquivo privado do ambiente não encontrado")
    connection = read_connection(environment.source, source_path, environment.variable)
    try:
        parsed = conninfo_to_dict(connection)
    except psycopg.ProgrammingError as error:
        # libpq diagnostics may include credentials; expose only a stable message.
        raise ValueError("Conexão PostgreSQL inválida") from error
    if parsed.get("dbname") != environment.database:
        raise ValueError("Conexão aponta para banco diferente do ambiente cadastrado")
    return SelectedEnvironment(name, environment, connection, str(parsed.get("host") or ""))


def add_environment(registry_path: Path, name: str, environment: Environment) -> None:
    if not re.fullmatch(IDENTIFIER, name):
        raise ValueError("Nome de ambiente inválido")
    registry = (
        Registry.model_validate(load_mapping(registry_path))
        if registry_path.exists()
        else Registry()
    )
    if name in registry.environments:
        raise ValueError("Ambiente já existe; revise o cadastro antes de alterá-lo")
    resolve_environment(registry_path, name, environment)
    registry.environments[name] = environment
    # Serialize only the reference and policy; credentials stay in the source file.
    content = yaml.safe_dump(registry.model_dump(by_alias=True), sort_keys=False)
    descriptor, staged = tempfile.mkstemp(
        prefix=".environments-", dir=registry_path.resolve().parent
    )
    with os.fdopen(descriptor, "w", encoding="utf-8") as output:
        output.write(content)
    os.replace(staged, registry_path)
