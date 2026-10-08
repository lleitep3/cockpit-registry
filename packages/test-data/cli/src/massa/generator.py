"""Geração determinística, com referências selecionadas como tuplas."""

import random
import re
from typing import Any

from faker import Faker

from massa.integrity import check_row, unique_keys
from massa.recipe import (
    ChoiceField,
    ConstantField,
    EntityRecipe,
    FakerField,
    FieldRecipe,
    Recipe,
    SequenceField,
    TemplateField,
    TimeField,
    validate_recipe,
)

MAX_ATTEMPTS = 100
TOKEN = re.compile(r"{{\s*([A-Za-z_][A-Za-z0-9_]*)\s*}}")


def field_value(
    field: FieldRecipe,
    index: int,
    row: dict[str, Any],
    fake: Faker,
    rng: random.Random,
    reference_time: str,
) -> Any:
    if isinstance(field, SequenceField):
        return field.start + index
    if isinstance(field, FakerField):
        return fake.format(field.provider)
    if isinstance(field, ConstantField):
        return field.value
    if isinstance(field, ChoiceField):
        return rng.choices(
            list(field.weights), weights=list(field.weights.values()), k=1
        )[0]
    if isinstance(field, TimeField):
        return reference_time
    if isinstance(field, TemplateField):
        return TOKEN.sub(lambda match: str(row[match.group(1)]), field.value)
    raise ValueError("Gerador não suportado")


def make_row(
    entity: EntityRecipe,
    index: int,
    data: dict[str, list[dict[str, Any]]],
    fake: Faker,
    rng: random.Random,
    reference_time: str,
) -> dict[str, Any]:
    row: dict[str, Any] = {}
    for ref in entity.references:
        parent = rng.choice(data[ref.entity])
        row.update({local: parent[remote] for local, remote in ref.fields.items()})
    pending = dict(entity.fields)
    while pending:
        progressed = False
        for name, field in list(pending.items()):
            if isinstance(field, TemplateField) and not set(
                TOKEN.findall(field.value)
            ).issubset(row):
                continue
            row[name] = field_value(field, index, row, fake, rng, reference_time)
            del pending[name]
            progressed = True
        if not progressed:
            raise ValueError("Template com campo ausente ou dependência circular")
    return row


def generate(schema: dict[str, Any], recipe: Recipe) -> dict[str, list[dict[str, Any]]]:
    order = validate_recipe(schema, recipe)
    fake = Faker(recipe.locale)
    fake.seed_instance(recipe.seed)
    rng = random.Random(recipe.seed)
    data: dict[str, list[dict[str, Any]]] = {}
    for name in order:
        table = schema["entities"][name]
        keys = unique_keys(table)
        seen: list[set[tuple[Any, ...]]] = [set() for _ in keys]
        rows: list[dict[str, Any]] = []
        for index in range(recipe.entities[name].count):
            row = generate_unique_row(
                recipe, name, index, data, fake, rng, table, keys, seen
            )
            rows.append(row)
        data[name] = rows
    return data


def generate_unique_row(
    recipe: Recipe,
    name: str,
    index: int,
    data: dict[str, list[dict[str, Any]]],
    fake: Faker,
    rng: random.Random,
    table: dict[str, Any],
    keys: list[list[str]],
    seen: list[set[tuple[Any, ...]]],
) -> dict[str, Any]:
    for _ in range(MAX_ATTEMPTS):
        row = make_row(
            recipe.entities[name], index, data, fake, rng, recipe.reference_time
        )
        check_row(table, row)
        values = [tuple(row[column] for column in key) for key in keys]
        if any(
            None not in value and value in existing
            for value, existing in zip(values, seen, strict=True)
        ):
            continue
        for value, existing in zip(values, seen, strict=True):
            if None not in value:
                existing.add(value)
        return row
    raise ValueError(
        f"Domínio de unicidade insuficiente em {name}; limite de {MAX_ATTEMPTS} tentativas"
    )
