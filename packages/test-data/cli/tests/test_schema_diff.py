import contextlib
import copy
import io
import json
import tempfile
import unittest
from pathlib import Path

import yaml

from massa.cli import main
from massa.schema_diff import catalogue, compare_values, diff_files, named_entries


class SchemaDiffTests(unittest.TestCase):
    def test_ordered_fk_tuple_and_type_changes(self) -> None:
        before = {"constraints": [{"name": "fk", "columns": ["tenant", "id"]}]}
        after = {"constraints": [{"name": "fk", "columns": ["id", "tenant"]}]}
        changes = compare_values(before, after, [])
        self.assertEqual(changes[0]["path"], ["constraints", "fk", "columns"])
        self.assertEqual(compare_values(True, 1, ["nullable"])[0]["kind"], "changed")

    def test_named_metadata_reordering_is_ignored(self) -> None:
        items = [{"name": "a", "definition": "UNIQUE(id)"}, {"name": "b"}]
        self.assertEqual(
            compare_values({"indexes": items}, {"indexes": items[::-1]}, []), []
        )

    def test_column_order_and_enum_order_preserved(self) -> None:
        changes = compare_values(
            {"fields": {"a": {}, "b": {}}}, {"fields": {"b": {}, "a": {}}}, []
        )
        self.assertEqual(changes[0]["path"], ["fields", "$order"])
        changes = compare_values(
            {"enums": [{"name": "state", "values": ["a", "b"]}]},
            {"enums": [{"name": "state", "values": ["b", "a"]}]},
            [],
        )
        self.assertEqual(changes[0]["path"], ["enums", "state", "values"])

    def test_added_removed_and_no_rename_inference(self) -> None:
        self.assertEqual(
            [item["kind"] for item in compare_values({"a": 1}, {"b": 1}, [])],
            ["removed", "added"],
        )

    def test_metadata_validation(self) -> None:
        for items in ([{}], [{"name": "a"}, {"name": "a"}]):
            with self.assertRaises((ValueError, TypeError)):
                named_entries(items)
        with self.assertRaises(ValueError):
            catalogue({"version": 2, "entities": {}})

    def test_server_version_is_ignored_without_mutating_inputs(self) -> None:
        before = {"version": 1, "source": {"server_version": "17"}, "entities": {}}
        snapshot = copy.deepcopy(before)
        after = {"version": 1, "source": {"server_version": "18"}, "entities": {}}
        self.assertEqual(compare_values(catalogue(before), catalogue(after), []), [])
        self.assertEqual(before, snapshot)

    def test_cli_report_drift_exit_and_no_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            before, after, output = [
                root / name for name in ("before.yaml", "after.yaml", "diff.json")
            ]
            before.write_text(yaml.safe_dump({"version": 1, "entities": {}}))
            after.write_text(
                yaml.safe_dump({"version": 1, "entities": {}, "enums": []})
            )
            args = ["schema", "diff", "--before", str(before), "--after", str(after)]
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                self.assertEqual(main(args + ["--fail-on-change"]), 2)
            report = json.loads(stdout.getvalue())
            self.assertTrue(report["changed"])
            self.assertEqual(len(report["inputs"]["before_sha256"]), 64)
            self.assertEqual(main(args + ["--output", str(output)]), 0)
            content = output.read_bytes()
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(main(args + ["--output", str(output)]), 1)
            self.assertEqual(content, output.read_bytes())
            self.assertFalse(diff_files(before, before)["changed"])
