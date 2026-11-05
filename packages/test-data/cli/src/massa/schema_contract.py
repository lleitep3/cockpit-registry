"""Validação do catálogo de entrada, preservando metadados extras da extração."""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Metadata(BaseModel):
    model_config = ConfigDict(extra="allow", strict=True)


class Column(Metadata):
    type: str
    nullable: bool


class Constraint(Metadata):
    name: str
    type: str
    columns: list[str]
    referenced_columns: list[str] = Field(default_factory=list)
    referenced_table: str | None = None
    referenced_schema: str | None = None
    definition: str = ""


class Table(Metadata):
    fields: dict[str, Column]
    constraints: list[Constraint] = Field(default_factory=list)

    @model_validator(mode="after")
    def valid_constraints(self) -> "Table":
        for constraint in self.constraints:
            if not set(constraint.columns).issubset(self.fields):
                raise ValueError("Constraint referencia coluna ausente")
            if constraint.type in {"p", "u"} and not constraint.columns:
                raise ValueError("Chave sem colunas")
            if "NULLS NOT DISTINCT" in constraint.definition.upper():
                raise ValueError("Unicidade NULLS NOT DISTINCT ainda não suportada")
            if constraint.type == "f" and (
                not constraint.referenced_table
                or not constraint.columns
                or len(constraint.columns) != len(constraint.referenced_columns)
            ):
                raise ValueError("FK incompleta")
        return self


class Schema(Metadata):
    version: Literal[1]
    entities: dict[str, Table]
    source: dict[str, Any] = Field(default_factory=dict)


def validate_schema(document: dict[str, Any]) -> None:
    Schema.model_validate(document)
