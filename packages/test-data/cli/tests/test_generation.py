import copy
import json
import random
import tempfile
import unittest
from pathlib import Path

from faker import Faker
from pydantic import ValidationError

from massa.export import build_manifest, export_jsonl, sha256
from massa.generator import field_value, generate, make_row
from massa.integrity import check_row, unique_keys, valid_type
from massa.recipe import (
    ChoiceField,
    ConstantField,
    Recipe,
    SequenceField,
    TimeField,
    generation_order,
    load_mapping,
    validate_recipe,
)
from massa.schema_contract import validate_schema

EXAMPLES = Path(__file__).resolve().parents[1] / "examples/relational"


class GenerationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.schema = load_mapping(EXAMPLES / "schema.yaml")
        self.raw = load_mapping(EXAMPLES / "generation.yaml")
        self.recipe = Recipe.model_validate(self.raw)

    def test_foreign_key_tuple_and_parent_order(self) -> None:
        data = generate(self.schema, self.recipe)
        self.assertEqual(list(data), ["clientes", "pedidos"])
        self.assertEqual(len(data["clientes"]), 10)
        self.assertEqual(len(data["pedidos"]), 30)
        parents = {(r["clinic_id"], r["id"]) for r in data["clientes"]}
        self.assertTrue(
            all((r["clinic_id"], r["cliente_id"]) in parents for r in data["pedidos"])
        )
        self.assertEqual(len({r["email"] for r in data["clientes"]}), 10)

    def test_reproducible_and_seed_changes_data(self) -> None:
        first = generate(self.schema, self.recipe)
        self.assertEqual(first, generate(self.schema, self.recipe))
        self.raw["seed"] += 1
        self.assertNotEqual(
            first, generate(self.schema, Recipe.model_validate(self.raw))
        )

    def test_sequence_constant_choice_and_clock(self) -> None:
        fake, rng = Faker("pt_BR"), random.Random(42)
        fields = [
            SequenceField(generator="sequence", start=10),
            ConstantField(generator="constant", value="ok"),
            ChoiceField(generator="choice", weights={"ok": 1}),
            TimeField(generator="reference_time"),
        ]
        values = [
            field_value(f, 2, {}, fake, rng, self.recipe.reference_time) for f in fields
        ]
        self.assertEqual(values, [12, "ok", "ok", self.recipe.reference_time])

    def test_template_resolves_dependency_regardless_of_field_order(self) -> None:
        entity = self.recipe.entities["clientes"].model_copy(deep=True)
        entity.fields = {"email": entity.fields["email"], "id": entity.fields["id"]}
        self.assertEqual(
            make_row(entity, 0, {}, Faker(), random.Random(1), "")["email"],
            "cliente1@example.test",
        )

    def test_contract_rejects_unknown_options_bad_weights_counts_and_timezone(
        self,
    ) -> None:
        mutations = [
            lambda r: r.update(unknown=True),
            lambda r: r.update(seed=True),
            lambda r: r.update(reference_time="2026-10-08T12:00:00"),
            lambda r: r["entities"]["clientes"].update(count=-1),
            lambda r: r["entities"]["clientes"]["fields"]["clinic_id"].update(
                weights={"x": 0}
            ),
        ]
        for mutate in mutations:
            raw = copy.deepcopy(self.raw)
            mutate(raw)
            with self.subTest(raw=raw), self.assertRaises(ValidationError):
                Recipe.model_validate(raw)

    def test_missing_parent_and_cycle_rejected(self) -> None:
        raw = copy.deepcopy(self.raw)
        raw["entities"]["clientes"]["references"] = [
            {"entity": "pedidos", "fields": {"id": "id"}}
        ]
        with self.assertRaisesRegex(ValueError, "ciclo"):
            generation_order(Recipe.model_validate(raw))
        self.raw["entities"]["pedidos"]["references"][0]["entity"] = "missing"
        with self.assertRaises(ValueError):
            validate_recipe(self.schema, Recipe.model_validate(self.raw))

    def test_composite_fk_cannot_be_split(self) -> None:
        entity = self.raw["entities"]["pedidos"]
        entity["references"][0]["fields"].pop("clinic_id")
        entity["fields"]["clinic_id"] = {"generator": "constant", "value": "clinica_a"}
        with self.assertRaisesRegex(ValueError, "referência conjunta"):
            validate_recipe(self.schema, Recipe.model_validate(self.raw))

    def test_empty_parent_unknown_field_and_duplicate_mapping(self) -> None:
        for mutation in ("empty", "unknown", "duplicate"):
            raw = copy.deepcopy(self.raw)
            if mutation == "empty":
                raw["entities"]["clientes"]["count"] = 0
            elif mutation == "unknown":
                raw["entities"]["clientes"]["fields"]["removed"] = {
                    "generator": "constant",
                    "value": 1,
                }
            else:
                raw["entities"]["pedidos"]["fields"]["cliente_id"] = {
                    "generator": "sequence"
                }
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                validate_recipe(self.schema, Recipe.model_validate(raw))

    def test_exhausted_unique_domain_fails_without_output(self) -> None:
        self.raw["entities"]["clientes"]["fields"]["email"] = {
            "generator": "constant",
            "value": "same",
        }
        with self.assertRaisesRegex(ValueError, "unicidade insuficiente"):
            generate(self.schema, Recipe.model_validate(self.raw))

    def test_template_cycle_fails(self) -> None:
        self.raw["entities"]["clientes"]["fields"]["email"] = {
            "generator": "template",
            "value": "{{ email }}",
        }
        with self.assertRaisesRegex(ValueError, "Template"):
            generate(self.schema, Recipe.model_validate(self.raw))

    def test_types_ranges_and_nullability(self) -> None:
        for sql_type, value, valid in (
            ("integer", True, False),
            ("smallint", 32768, False),
            ("integer", 5, True),
            ("boolean", False, True),
            ("uuid", "bad", False),
            ("character varying(2)", "long", False),
            ("timestamp with time zone", "bad", False),
        ):
            self.assertEqual(valid_type(sql_type, value), valid)
        with self.assertRaisesRegex(ValueError, "não suportado"):
            valid_type("jsonb", {})
        row = {"clinic_id": "x", "id": None, "nome": "x", "email": "x"}
        with self.assertRaisesRegex(ValueError, "obrigatório"):
            check_row(self.schema["entities"]["clientes"], row)
        self.assertEqual(len(unique_keys(self.schema["entities"]["clientes"])), 2)

    def test_export_files_hashes_manifest_and_no_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            first, second = Path(directory) / "first", Path(directory) / "second"
            manifest = export_jsonl(
                EXAMPLES / "schema.yaml", EXAMPLES / "generation.yaml", first
            )
            self.assertEqual(
                manifest,
                export_jsonl(
                    EXAMPLES / "schema.yaml", EXAMPLES / "generation.yaml", second
                ),
            )
            for file in first.iterdir():
                self.assertEqual(file.read_bytes(), (second / file.name).read_bytes())
            self.assertEqual(
                manifest["files"]["clientes.jsonl"],
                sha256((first / "clientes.jsonl").read_bytes()),
            )
            self.assertEqual(
                len((first / "clientes.jsonl").read_text().splitlines()), 10
            )
            self.assertNotIn(str(EXAMPLES), json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, "já existe"):
                export_jsonl(
                    EXAMPLES / "schema.yaml", EXAMPLES / "generation.yaml", first
                )

    def test_manifest_marks_database_and_sql_unverified(self) -> None:
        manifest = build_manifest(self.recipe, b"schema", b"recipe", {}, {})
        self.assertEqual(manifest["verification"]["database_load"], "not_executed")

    def test_invalid_yaml_and_non_mapping_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.yaml"
            for text in ("x: [", "- item"):
                path.write_text(text)
                with self.assertRaises((ValueError, TypeError)):
                    load_mapping(path)

    def test_malformed_schema_and_unsupported_null_unique_rejected(self) -> None:
        for mutation in ("missing_fields", "bad_fk", "bad_column", "null_unique"):
            schema = copy.deepcopy(self.schema)
            if mutation == "missing_fields":
                schema["entities"]["clientes"].pop("fields")
            elif mutation == "bad_fk":
                schema["entities"]["pedidos"]["constraints"][1].pop("referenced_table")
            elif mutation == "bad_column":
                schema["entities"]["clientes"]["constraints"][0]["columns"] = [
                    "removed"
                ]
            else:
                schema["entities"]["clientes"]["constraints"][1]["definition"] = (
                    "UNIQUE NULLS NOT DISTINCT (email)"
                )
            with self.subTest(mutation=mutation), self.assertRaises(ValidationError):
                validate_schema(schema)
