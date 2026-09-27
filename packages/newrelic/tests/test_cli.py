import argparse
import importlib.util
import io
import json
import os
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location(
    "nr", Path(__file__).parents[1] / "lib/newrelic_cli.py"
)
nr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(nr)


class Tests(unittest.TestCase):
    def test_private_file_and_permissions(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "key"
            p.write_text("NRAK-offline-placeholder")
            p.chmod(0o600)
            with patch.dict(os.environ, {"NEW_RELIC_API_KEY_FILE": str(p)}, clear=True):
                self.assertEqual(nr.credential(), "NRAK-offline-placeholder")
                p.chmod(0o644)
                with self.assertRaises(nr.ClientError):
                    nr.credential()

    def test_ambiguous_or_absent_key(self) -> None:
        for env in [
            {},
            {"NEW_RELIC_API_KEY": "NRAK-test", "NEW_RELIC_API_KEY_FILE": "any"},
        ]:
            with patch.dict(os.environ, env, clear=True), self.assertRaises(nr.ClientError):
                nr.credential()

    def test_nrql_requires_read_and_window(self) -> None:
        for q in [
            "DELETE FROM Log",
            "SELECT * FROM Log",
            "FROM Log SELECT count(*) SINCE 1 hour ago; DELETE FROM Log",
        ]:
            with self.assertRaises(nr.ClientError):
                nr.validate_nrql(q)
        for q in nr.QUERIES.values():
            self.assertEqual(nr.validate_nrql(q), q)

    def test_credentials_redacted_recursively(self) -> None:
        result = nr.scrub(
            {"token": "private", "rows": [{"message": "NRAK-test-123", "count": 3}]},
            "NRAK-test-123",
        )
        self.assertNotIn("private", json.dumps(result))
        self.assertNotIn("NRAK-", json.dumps(result))
        self.assertEqual(result["rows"][0]["count"], 3)

    def test_redirect_refused(self) -> None:
        with self.assertRaises(nr.ClientError):
            nr.NoRedirect().redirect_request(
                None, None, 302, "", {}, "https://other.example"
            )

    def test_partial_errors_fail_without_echo(self) -> None:
        response = io.BytesIO(
            json.dumps({"data": {}, "errors": [{"message": "sensitive-body"}]}).encode()
        )
        with patch.object(nr.urllib.request, "build_opener") as opener:
            opener.return_value.open.return_value = response
            with self.assertRaises(nr.ClientError) as ctx:
                nr.request("query", {}, "NRAK-test", "US")
        self.assertNotIn("sensitive-body", str(ctx.exception))

    def test_size_cap(self) -> None:
        with patch.object(nr.urllib.request, "build_opener") as opener:
            opener.return_value.open.return_value = io.BytesIO(
                b"x" * (nr.MAX_BYTES + 1)
            )
            with self.assertRaises(nr.ClientError):
                nr.request("query", {}, "NRAK-test", "EU")

    def test_region_headers_and_variables(self) -> None:
        with patch.object(nr.urllib.request, "build_opener") as opener:
            opener.return_value.open.return_value = io.BytesIO(b'{"data":{"ok":true}}')
            self.assertEqual(
                nr.request("query", {"id": 42}, "NRAK-test", "EU"), {"ok": True}
            )
            req = opener.return_value.open.call_args.args[0]
            self.assertEqual(req.full_url, nr.ENDPOINTS["EU"])
            self.assertEqual(json.loads(req.data)["variables"], {"id": 42})

    def test_http_errors_dont_echo_body(self) -> None:
        with patch.object(nr.urllib.request, "build_opener") as opener:
            opener.return_value.open.side_effect = urllib.error.HTTPError(
                "", 429, "secret", {}, None
            )
            with self.assertRaises(nr.ClientError) as ctx:
                nr.request("query", {}, "NRAK-test", "US")
            self.assertIn("429", str(ctx.exception))
            self.assertNotIn("secret", str(ctx.exception))

    def test_empty_results_not_error_and_null_account_fails(self) -> None:
        args = argparse.Namespace(command="apm", account=42, region="US")
        with (
            patch.object(nr, "credential", return_value="NRAK-test"),
            patch.object(nr, "request") as request,
        ):
            request.return_value = {"actor": {"account": {"nrql": {"results": []}}}}
            self.assertEqual(nr.run(args)["results"], [])
            request.return_value = {"actor": {"account": None}}
            with self.assertRaises(nr.ClientError):
                nr.run(args)

    def test_scaffold_never_overwrites(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            dest = Path(d) / "new"
            args = argparse.Namespace(command="scaffold", directory=str(dest))
            self.assertFalse(nr.run(args)["applied"])
            self.assertTrue((dest / "environment/main.tf").exists())
            with self.assertRaises(nr.ClientError):
                nr.run(args)

    def test_positive_account(self) -> None:
        for value in ["0", "-1", "abc"]:
            with self.assertRaises(argparse.ArgumentTypeError):
                nr.positive(value)
        self.assertEqual(nr.positive("42"), 42)


if __name__ == "__main__":
    unittest.main()
