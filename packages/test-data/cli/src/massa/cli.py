"""Interface inicial de extração; nunca registra credenciais."""

import argparse
import json
import os
import sys
from collections.abc import Sequence
from pathlib import Path

import psycopg
import yaml
from dotenv import dotenv_values
from pydantic import ValidationError

from massa.catalog import inspect_schema
from massa.environments import Environment, add_environment, select_environment
from massa.export import export_jsonl
from massa.recipe import Recipe, load_mapping, validate_recipe
from massa.schema_diff import diff_files
from massa.seed_project import digest, prepare_seed, run_seed


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="massa")
    commands = root.add_subparsers(dest="command", required=True)
    configure_environment(
        commands.add_parser("environment", help="Cadastrar conexões por referência")
    )
    configure_schema(commands.add_parser("schema"))
    configure_seed(
        commands.add_parser("seed", help="Planejar, carregar e verificar cenários")
    )
    for command in ("validate", "generate"):
        action = commands.add_parser(command)
        action.add_argument("--schema", type=Path, required=True)
        action.add_argument("--recipe", type=Path, required=True)
        if command == "generate":
            action.add_argument("--format", choices=["jsonl"], default="jsonl")
            action.add_argument("--output", type=Path, required=True)
    return root


def configure_seed(command: argparse.ArgumentParser) -> None:
    actions = command.add_subparsers(dest="action", required=True)
    for name in ("plan", "apply", "verify"):
        action = actions.add_parser(name)
        action.add_argument("--project", type=Path, required=True)
        action.add_argument("--scenario", required=True)
        action.add_argument("--environment", required=True)
        action.add_argument("--registry", type=Path, default=Path("environments.yaml"))
        action.add_argument("--output", type=Path, required=True)
        if name == "apply":
            action.add_argument("--plan", type=Path, required=True)
            action.add_argument("--confirm", required=True)
            action.add_argument("--confirm-plan", required=True)


def execute_seed(args: argparse.Namespace) -> int:
    if args.output.exists() or not args.output.parent.is_dir():
        raise ValueError("Escolha saída nova em diretório existente")
    selected = select_environment(args.registry, args.environment)
    seed = prepare_seed(args.project, args.scenario)
    reviewed = None
    if args.action == "apply":
        if args.confirm != selected.configuration.database:
            raise ValueError("Confirmação precisa ser o nome exato do banco")
        reviewed = load_mapping(args.plan)
        if digest(reviewed) != args.confirm_plan:
            raise ValueError("Hash de confirmação diverge do plano revisado")
    receipt = run_seed(selected, seed, args.action, reviewed)
    with args.output.open("x", encoding="utf-8") as output:
        json.dump(receipt, output, ensure_ascii=False, indent=2, sort_keys=True)
        output.write("\n")
    print(f"Seed {args.action}: {args.output}")
    if args.action == "plan":
        print(f"Hash do plano para confirmação: {digest(receipt)}")
    return 0


def configure_environment(command: argparse.ArgumentParser) -> None:
    env_actions = command.add_subparsers(dest="action", required=True)
    add = env_actions.add_parser("add")
    add.add_argument("--registry", type=Path, default=Path("environments.yaml"))
    add.add_argument("--name", required=True)
    source = add.add_mutually_exclusive_group(required=True)
    source.add_argument("--env-file", type=Path)
    source.add_argument("--postman", type=Path)
    add.add_argument("--connection-env", default="DATABASE_URL")
    add.add_argument("--database", required=True)
    add.add_argument("--schema", default="public")
    add.add_argument("--writable", action="store_true")
    add.add_argument("--resettable", action="store_true")


def configure_schema(command: argparse.ArgumentParser) -> None:
    actions = command.add_subparsers(dest="action", required=True)
    inspect = actions.add_parser("inspect", help="Extrair metadados PostgreSQL")
    inspect.add_argument("--connection-env", default="DATABASE_URL")
    inspect.add_argument("--env-file", type=Path)
    inspect.add_argument("--schema")
    inspect.add_argument("--environment")
    inspect.add_argument("--registry", type=Path, default=Path("environments.yaml"))
    inspect.add_argument("--table", action="append")
    inspect.add_argument("--exclude-table", action="append", default=["pgmigrations"])
    inspect.add_argument("--output", type=Path, required=True)
    diff = actions.add_parser("diff", help="Comparar catálogos sem alterar receitas")
    diff.add_argument("--before", type=Path, required=True)
    diff.add_argument("--after", type=Path, required=True)
    diff.add_argument("--output", type=Path)
    diff.add_argument("--fail-on-change", action="store_true")


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
    schema_name = args.schema or "public"
    if args.environment:
        if args.env_file is not None:
            raise ValueError("Selecione ambiente ou arquivo direto, sem misturar")
        selected = select_environment(args.registry, args.environment)
        url = selected.connection
        schema_name = args.schema or selected.configuration.schema_name
    else:
        url = connection_url(args.connection_env, args.env_file)
    if args.output.exists():
        raise ValueError("Arquivo de saída já existe; escolha outro destino")
    if args.table:
        document = inspect_schema(
            url, schema_name, set(args.exclude_table), set(args.table)
        )
    else:
        document = inspect_schema(url, schema_name, set(args.exclude_table))
    # Sem timestamps/OIDs: mesma estrutura produz um diff estável.
    serialized = yaml.safe_dump(document, sort_keys=False, allow_unicode=True)
    with args.output.open("x", encoding="utf-8") as output:
        output.write(serialized)
    print(f"Schema extraído: {len(document['entities'])} tabelas → {args.output}")


def execute_diff(args: argparse.Namespace) -> int:
    if args.output is not None and args.output.exists():
        raise ValueError("Arquivo de saída já existe; escolha outro destino")
    report = diff_files(args.before, args.after)
    serialized = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output is None:
        print(serialized, end="")
    else:
        with args.output.open("x", encoding="utf-8") as output:
            output.write(serialized)
    return 2 if report["changed"] and args.fail_on_change else 0


def execute(args: argparse.Namespace) -> int:
    if args.command == "seed":
        return execute_seed(args)
    if args.command == "environment":
        path = args.env_file if args.env_file else args.postman
        environment = Environment.model_validate(
            {
                "source": "env-file" if args.env_file else "postman",
                "path": os.path.relpath(path.resolve(), args.registry.resolve().parent),
                "variable": args.connection_env,
                "database": args.database,
                "schema": args.schema,
                "writable": args.writable,
                "resettable": args.resettable,
            }
        )
        add_environment(args.registry, args.name, environment)
        print(f"Ambiente cadastrado: {args.name}; conexão permanece no arquivo privado")
        return 0
    if args.command == "schema" and args.action == "diff":
        return execute_diff(args)
    if args.command == "validate":
        schema = load_mapping(args.schema)
        recipe = Recipe.model_validate(load_mapping(args.recipe))
        order = validate_recipe(schema, recipe)
        print(
            f"Estrutura da receita válida: {', '.join(order)}; regras SQL exigem QA em banco"
        )
        return 0
    if args.command == "generate":
        manifest = export_jsonl(args.schema, args.recipe, args.output)
        print(
            f"Massa gerada: {sum(manifest['counts'].values())} registros → {args.output}"
        )
        return 0
    extract_catalog(args)
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        return execute(args)
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
    except (OSError, ValueError, TypeError, KeyError) as error:
        print(f"Erro: {error}", file=sys.stderr)
        return 1
