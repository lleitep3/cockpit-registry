from __future__ import annotations

import contextlib
import copy
import importlib.util
import io
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("dba", ROOT / "lib/dba_postgres.py")
assert SPEC and SPEC.loader
dba = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(dba)
FIXTURE = json.loads((ROOT / "tests/fixtures/example.json").read_text())


class DatabaseTests(unittest.TestCase):
    def test_optional_fk(self) -> None:
        self.assertIn("t0 |o--o{ t1", dba.erd(FIXTURE))

    def test_unique_fk_and_composite_cardinality(self) -> None:
        data = copy.deepcopy(FIXTURE)
        data["constraints"].append(
            dict(type="u", table_name="child", columns=["parent_id"])
        )
        self.assertIn("--o|", dba.erd(data))
        data["columns"][-1]["required"] = True
        self.assertIn("||--o|", dba.erd(data))

    def test_match_full_not_null(self) -> None:
        data = copy.deepcopy(FIXTURE)
        data["constraints"][-1].update(columns=["id", "parent_id"], match_type="f")
        self.assertIn("||--o|", dba.erd(data))

    def test_cross_schema_fk_not_invented(self) -> None:
        data = copy.deepcopy(FIXTURE)
        data["constraints"][-1]["parent_schema"] = "other"
        self.assertNotIn("--", dba.erd(data))

    def test_fk_index_is_candidate_not_ddl(self) -> None:
        issues = dba.findings(FIXTURE)
        self.assertEqual(issues[0]["code"], "review-fk-index")
        self.assertIn("Candidate only", issues[0]["next_step"])
        data = copy.deepcopy(FIXTURE)
        index = dict(
            table_name="child",
            name="child_fk_idx",
            method="btree",
            valid=True,
            ready=True,
            partial=False,
            expressions=False,
            columns=["parent_id", "id"],
        )
        data["indexes"].append(index)
        self.assertEqual([], dba.findings(data))
        index["partial"] = True
        self.assertEqual("review-fk-index", dba.findings(data)[0]["code"])

    def test_invalid_index_and_unvalidated(self) -> None:
        data = copy.deepcopy(FIXTURE)
        data["indexes"].append(
            dict(name="broken", valid=False, columns=[], table_name="child")
        )
        data["constraints"][-1]["validated"] = False
        codes = {i["code"] for i in dba.findings(data)}
        self.assertIn("invalid-index", codes)
        self.assertIn("unvalidated-constraint", codes)

    def test_reject_bad_format_version_arrays_truncation(self) -> None:
        for mutate in (
            lambda d: d.update(format_version=99),
            lambda d: d.update(server_version_num=150000),
            lambda d: d["constraints"][0].update(columns="{id}"),
            lambda d: d.update(tables=[d["tables"][0]] * 5000),
        ):
            data = copy.deepcopy(FIXTURE)
            mutate(data)
            with self.assertRaises(ValueError):
                dba.validate(data)

    def test_labels_cannot_inject_mermaid(self) -> None:
        self.assertNotIn('"', dba.safe_label('evil"}\nclick href'))
        self.assertNotIn("\n", dba.safe_label("x\ny"))

    def test_report_explains_unknown_and_cost_limits(self) -> None:
        result = dba.report(FIXTURE)
        self.assertIn("Não representa disco provisionado", result)
        self.assertIn("não provam taxas", result)
        self.assertIn("não medida de bloat", result)

    def test_offline_artifacts_private_and_no_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "report"
            self.assertEqual(
                0,
                dba.main(
                    [
                        "analyze",
                        str(ROOT / "tests/fixtures/example.json"),
                        "--output",
                        str(out),
                    ]
                ),
            )
            self.assertEqual(0o600, (out / "report.md").stat().st_mode & 0o777)
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(
                    2,
                    dba.main(
                        [
                            "analyze",
                            str(ROOT / "tests/fixtures/example.json"),
                            "--output",
                            str(out),
                        ]
                    ),
                )

    def test_symlink_refused(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            original = Path(tmp) / "original"
            original.write_text("preserve")
            link = Path(tmp) / "link"
            link.symlink_to(original)
            with self.assertRaises(FileExistsError):
                dba.write_new(link, "new")
            self.assertEqual("preserve", original.read_text())

    @patch.object(dba.shutil, "which", return_value=None)
    def test_missing_psql(self, _: object) -> None:
        with self.assertRaisesRegex(ValueError, "psql"):
            dba.collect_local("public", Path("unused.json"))

    @patch.object(dba.shutil, "which", return_value="psql")
    def test_collect_credentials_child_only_and_clear_pgoptions(
        self, _: object
    ) -> None:
        env = {k: "example" for k in dba.BINDINGS}
        env.update(PGPASSWORD="SECRET_SENTINEL", PGOPTIONS="unsafe", PGSERVICE="wrong")
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, env):
            result = subprocess.CompletedProcess([], 0, json.dumps(FIXTURE), "")
            with patch.object(dba.subprocess, "run", return_value=result) as run:
                dba.collect_local("public", Path(tmp) / "snapshot.json")
                self.assertNotIn("SECRET_SENTINEL", str(run.call_args.args))
                child = run.call_args.kwargs["env"]
                self.assertNotIn("PGOPTIONS", child)
                self.assertNotIn("PGSERVICE", child)
                self.assertIn("-X", run.call_args.args[0])
                self.assertIn("-w", run.call_args.args[0])

    @patch.object(dba.shutil, "which", return_value="cockpit")
    def test_profile_denied_no_fallback(self, _: object) -> None:
        with patch.object(
            dba.subprocess,
            "run",
            return_value=subprocess.CompletedProcess([], 1, "", "SECRET_SENTINEL"),
        ) as run:
            with self.assertRaisesRegex(ValueError, "no fallback"):
                dba.collect_profile("example-dev", "public", Path("unused.json"))
            self.assertEqual(1, run.call_count)
            self.assertIn("example-dev", run.call_args.args[0])

    @patch.object(dba.shutil, "which", return_value="psql")
    def test_query_failure_no_file_or_raw_error(self, _: object) -> None:
        with (
            tempfile.TemporaryDirectory() as tmp,
            patch.dict(os.environ, {k: "x" for k in dba.BINDINGS}),
        ):
            with patch.object(
                dba.subprocess,
                "run",
                return_value=subprocess.CompletedProcess([], 1, "", "SECRET_SENTINEL"),
            ):
                out = Path(tmp) / "snapshot.json"
                with self.assertRaises(ValueError) as caught:
                    dba.collect_local("public", out)
                self.assertNotIn("SECRET_SENTINEL", str(caught.exception))
                self.assertFalse(out.exists())

    def test_lab_generation_private_unique_and_preserves_existing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            lab = Path(tmp) / "lab"
            dba.init_lab(lab)
            self.assertTrue((lab / "compose.yaml").is_file())
            a = (lab / ".secrets/postgres_password").read_text()
            b = (lab / ".secrets/pgadmin_password").read_text()
            self.assertNotEqual(a, b)
            self.assertGreater(len(a), 32)
            self.assertNotIn(a.strip(), (lab / ".env").read_text())
            self.assertEqual(
                0o600, (lab / ".secrets/postgres_password").stat().st_mode & 0o777
            )
            self.assertEqual(0o700, lab.stat().st_mode & 0o777)
            self.assertEqual(0o700, (lab / ".secrets").stat().st_mode & 0o777)
            self.assertEqual(
                0o444, (lab / ".secrets/pgadmin_password").stat().st_mode & 0o777
            )
            with self.assertRaises(ValueError):
                dba.init_lab(lab)
            self.assertEqual(a, (lab / ".secrets/postgres_password").read_text())

    def test_lab_symlink_and_cli_do_not_start_docker(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "link"
            target.symlink_to(Path(tmp) / "missing")
            with self.assertRaises(ValueError):
                dba.init_lab(target)
            with patch.object(dba.subprocess, "run") as run:
                self.assertEqual(
                    0, dba.main(["lab-init", "--output", str(Path(tmp) / "new")])
                )
                run.assert_not_called()

    def test_operations_sql_has_no_credential_settings(self) -> None:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(0, dba.main(["sql", "--kind", "operations"]))
        self.assertIn("BEGIN READ ONLY", output.getvalue())
        self.assertNotIn("primary_conninfo", output.getvalue())
        self.assertNotIn("pg_authid", output.getvalue())

    def test_sql_is_bounded_readonly_without_query_text(self) -> None:
        sql = (ROOT / "sql/baseline.sql").read_text()
        self.assertIn("REPEATABLE READ READ ONLY", sql)
        self.assertIn("statement_timeout", sql)
        self.assertNotIn("pg_stat_statements_reset", sql)
        self.assertNotIn("pg_terminate_backend", sql)
        self.assertNotIn("query,", sql)


if __name__ == "__main__":
    unittest.main()
