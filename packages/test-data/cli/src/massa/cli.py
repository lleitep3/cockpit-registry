"""Interface inicial de extração; nunca registra credenciais."""

import argparse
import os
import sys
from collections.abc import Sequence
from pathlib import Path

import psycopg
import yaml
from dotenv import dotenv_values
from pydantic import ValidationError

from massa.catalog import inspect_schema
from massa.export import export_jsonl
from massa.recipe import Recipe, load_mapping, validate_recipe


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="massa")
    commands = root.add_subparsers(dest="command", required=True)
    schema = commands.add_parser("schema")
    actions = schema.add_subparsers(dest="action", required=True)
    inspect = actions.add_parser("inspect", help="Extrair metadados PostgreSQL")
    inspect.add_argument("--connection-env", default="DATABASE_URL")
    inspect.add_argument("--env-file", type=Path)
    inspect.add_argument("--schema", default="public")
    inspect.add_argument("--exclude-table", action="append", default=["pgmigrations"])
    inspect.add_argument("--output", type=Path, required=True)
    for command in ("validate", "generate"):
        action = commands.add_parser(command)
        action.add_argument("--schema", type=Path, required=True)
        action.add_argument("--recipe", type=Path, required=True)
        if command == "generate":
            action.add_argument("--format", choices=["jsonl"], default="jsonl")
            action.add_argument("--output", type=Path, required=True)
    return root


def connection_url(variable: str, env_file: Path | None) -> str:
    # Arquivo explícito tem precedência para evitar usar uma URL remota herdada.
    if env_file is not None:
        if not env_file.is_file():
            raise ValueError("Arquivo de ambiente não encontrado")
        value = dotenv_values(env_file, interpolate=False).get(variable)
    else:
        value = os.environ.get(variable)
    if not value:
        raise ValueError(f"Variável obrigatória não definida: {variable}")
    return value


def extract_catalog(args: argparse.Namespace) -> None:
    url = connection_url(args.connection_env, args.env_file)
    if args.output.exists():
        raise ValueError("Arquivo de saída já existe; escolha outro destino")
    document = inspect_schema(url, args.schema, set(args.exclude_table))
    # Sem timestamps/OIDs: mesma estrutura produz um diff estável.
    serialized = yaml.safe_dump(document, sort_keys=False, allow_unicode=True)
    with args.output.open("x", encoding="utf-8") as output:
        output.write(serialized)
    print(f"Schema extraído: {len(document['entities'])} tabelas → {args.output}")


def execute(args: argparse.Namespace) -> None:
    if args.command == "validate":
        schema = load_mapping(args.schema)
        recipe = Recipe.model_validate(load_mapping(args.recipe))
        order = validate_recipe(schema, recipe)
        print(
            f"Estrutura da receita válida: {', '.join(order)}; regras SQL exigem QA em banco"
        )
        return
    if args.command == "generate":
        manifest = export_jsonl(args.schema, args.recipe, args.output)
        print(
            f"Massa gerada: {sum(manifest['counts'].values())} registros → {args.output}"
        )
        return
    extract_catalog(args)


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        execute(args)
        return 0
    except ValidationError as error:
        locations = [".".join(map(str, item["loc"])) for item in error.errors()]
        print(f"Contrato inválido nos campos: {', '.join(locations)}", file=sys.stderr)
        return 1
    except psycopg.Error:
        print(
            "Falha na consulta PostgreSQL; confira conexão e permissões.",
            file=sys.stderr,
        )
        return 1
    except (OSError, ValueError, TypeError) as error:
        print(f"Erro: {error}", file=sys.stderr)
        return 1
