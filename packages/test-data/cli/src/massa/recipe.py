"""Contrato fechado de receitas e planejamento de dependências."""

import re
from datetime import datetime
from pathlib import Path
from typing import Annotated, Any, Literal

import yaml
from faker import Faker
from pydantic import BaseModel, ConfigDict, Field, model_validator

from massa.schema_contract import validate_schema

MAX_ROWS = 100_000
IDENTIFIER = r"^[A-Za-z_][A-Za-z0-9_]*$"
TEMPLATE_TOKEN = re.compile(r"{{\s*([A-Za-z_][A-Za-z0-9_]*)\s*}}")
Scalar = str | int | bool | None


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class SequenceField(Contract):
    generator: Literal["sequence"]
    start: int = 1


class FakerField(Contract):
    generator: Literal["faker"]
    provider: Literal["name", "first_name", "last_name", "email", "uuid4", "city"]


class ConstantField(Contract):
    generator: Literal["constant"]
    value: Scalar


class TemplateField(Contract):
    generator: Literal["template"]
    value: str


class ChoiceField(Contract):
    generator: Literal["choice"]
    weights: dict[str, int] = Field(min_length=1)

    @model_validator(mode="after")
    def positive_weights(self) -> "ChoiceField":
        if any(weight <= 0 for weight in self.weights.values()):
            raise ValueError("Pesos devem ser inteiros positivos")
        return self


class TimeField(Contract):
    generator: Literal["reference_time"]


FieldRecipe = Annotated[
    SequenceField
    | FakerField
    | ConstantField
    | TemplateField
    | ChoiceField
    | TimeField,
    Field(discriminator="generator"),
]


class Reference(Contract):
    entity: str = Field(pattern=IDENTIFIER)
    fields: dict[str, str] = Field(min_length=1)


class EntityRecipe(Contract):
    count: int = Field(ge=0, le=MAX_ROWS)
    fields: dict[str, FieldRecipe]
    references: list[Reference] = Field(default_factory=list)


class Recipe(Contract):
    version: Literal[1]
    seed: int
    locale: str
    reference_time: str
    entities: dict[str, EntityRecipe] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_settings(self) -> "Recipe":
        time = datetime.fromisoformat(self.reference_time)
        if time.tzinfo is None or time.utcoffset() is None:
            raise ValueError("reference_time deve incluir timezone")
        try:
            Faker(self.locale)
        except AttributeError as error:
            raise ValueError("Locale Faker não suportado") from error
        if sum(entity.count for entity in self.entities.values()) > MAX_ROWS:
            raise ValueError(f"Limite desta versão: {MAX_ROWS} registros em memória")
        if any(not re.fullmatch(IDENTIFIER, name) for name in self.entities):
            raise ValueError("Nome de entidade inválido")
        return self


def load_mapping(path: Path, content: bytes | None = None) -> dict[str, Any]:
    try:
        document = yaml.safe_load(content if content is not None else path.read_bytes())
    except yaml.YAMLError as error:
        raise ValueError("YAML inválido") from error
    if not isinstance(document, dict):
        raise TypeError("Documento deve ser um mapping YAML")
    return document


def generation_order(recipe: Recipe) -> list[str]:
    pending = set(recipe.entities)
    ordered: list[str] = []
    while pending:
        ready = sorted(
            name
            for name in pending
            if all(ref.entity in ordered for ref in recipe.entities[name].references)
        )
        if not ready:
            raise ValueError("Referência inexistente ou ciclo de dependências")
        ordered.extend(ready)
        pending.difference_update(ready)
    return ordered


def validate_recipe(schema: dict[str, Any], recipe: Recipe) -> list[str]:
    validate_schema(schema)
    order = generation_order(recipe)
    for name in order:
        entity = recipe.entities[name]
        if name not in schema["entities"]:
            raise ValueError(f"Entidade ausente no schema: {name}")
        fields = schema["entities"][name]["fields"]
        configured = set(entity.fields)
        for ref in entity.references:
            parent = recipe.entities[ref.entity]
            if entity.count and not parent.count:
                raise ValueError(f"Referência sem registros pais: {name}")
            if configured.intersection(ref.fields):
                raise ValueError(f"Campo definido mais de uma vez: {name}")
            configured.update(ref.fields)
            parent_fields = schema["entities"][ref.entity]["fields"]
            if not set(ref.fields.values()).issubset(parent_fields):
                raise ValueError(f"Campo de referência inexistente: {name}")
        if configured != set(fields):
            raise ValueError(f"Configure exatamente os campos do schema: {name}")
        validate_templates(entity)
        validate_foreign_keys(name, schema, entity)
    return order


def validate_templates(entity: EntityRecipe) -> None:
    available = {key for ref in entity.references for key in ref.fields}
    pending = dict(entity.fields)
    while pending:
        ready = []
        for name, field in pending.items():
            if isinstance(field, TemplateField):
                remainder = TEMPLATE_TOKEN.sub("", field.value)
                if "{{" in remainder or "}}" in remainder:
                    raise ValueError("Template suporta apenas tokens de campo")
                if not set(TEMPLATE_TOKEN.findall(field.value)).issubset(available):
                    continue
            ready.append(name)
        if not ready:
            raise ValueError("Template com campo ausente ou dependência circular")
        for name in ready:
            available.add(name)
            del pending[name]


def validate_foreign_keys(
    name: str, schema: dict[str, Any], entity: EntityRecipe
) -> None:
    for constraint in schema["entities"][name].get("constraints", []):
        if constraint["type"] != "f":
            continue
        pairs = dict(
            zip(constraint["columns"], constraint["referenced_columns"], strict=True)
        )
        matches = [
            ref
            for ref in entity.references
            if ref.entity == constraint["referenced_table"]
            and all(ref.fields.get(key) == value for key, value in pairs.items())
        ]
        source_schema = schema.get("source", {}).get("schema", "public")
        if (
            constraint.get("referenced_schema", source_schema) != source_schema
            or not matches
        ):
            raise ValueError(
                f"FK precisa de referência conjunta explícita: {name}.{constraint['name']}"
            )
