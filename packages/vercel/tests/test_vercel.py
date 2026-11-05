import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch, Mock
from urllib.error import HTTPError, URLError

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import vercel


class VercelTests(unittest.TestCase):
    def test_auth_alias_is_explicit_and_token_flag_has_no_value(self) -> None:
        args = vercel.build_parser().parse_args(
            ["auth", "m2b", "--scope", "lleitelab", "--token"]
        )
        self.assertEqual((args.account, args.scope), ("m2b", "lleitelab"))
        with self.assertRaises(vercel.Error) as error:
            vercel.build_parser().parse_args(["auth", "m2b", "--token", "DO_NOT_LOG"])
        self.assertNotIn("DO_NOT_LOG", str(error.exception))

    def test_noninteractive_auth_does_not_hang(self) -> None:
        args = vercel.build_parser().parse_args(["auth", "m2b"])
        with patch.object(vercel, "config", return_value="{}"), patch.object(
            sys.stdin, "isatty", return_value=False
        ):
            with self.assertRaisesRegex(vercel.Error, "terminal"):
                vercel.auth(args)

    def test_auth_preserves_existing_scope(self) -> None:
        args = vercel.build_parser().parse_args(["auth", "m2b", "--token-stdin"])
        with patch.object(
            vercel, "config", return_value='{"scope":{"value":"lleitelab"}}'
        ) as config, patch.object(vercel, "store_token"), patch.object(
            sys, "stdin", io.StringIO("new-secret")
        ), contextlib.redirect_stdout(
            io.StringIO()
        ):
            self.assertEqual(vercel.auth(args), 0)
        config.assert_any_call("m2b", ["set", "scope", "lleitelab"])

    def test_token_goes_to_stdin_not_argv(self) -> None:
        fake = subprocess.CompletedProcess([], 0, "", "")
        with patch.object(subprocess, "run", return_value=fake) as run:
            vercel.store_token("m2b", "TEST_SECRET")
        self.assertNotIn("TEST_SECRET", repr(run.call_args.args))
        self.assertEqual(run.call_args.kwargs["input"], "TEST_SECRET")
        self.assertIn("--stdin", run.call_args.args[0])

    def test_vault_failure_never_echoes_token(self) -> None:
        fake = subprocess.CompletedProcess([], 1, "", "TEST_SECRET")
        with patch.object(subprocess, "run", return_value=fake):
            with self.assertRaises(vercel.Error) as error:
                vercel.store_token("m2b", "TEST_SECRET")
        self.assertNotIn("TEST_SECRET", str(error.exception))

    def test_empty_token_is_rejected(self) -> None:
        with self.assertRaises(vercel.Error):
            vercel.store_token("m2b", "")

    def test_api_cannot_escape_or_override_scope(self) -> None:
        for path in [
            "https://evil.test",
            "//evil.test",
            "/v9/projects?teamId=other",
            "/v9/projects?slug=other",
            "/v9/projects?token=secret",
            "/x#fragment",
        ]:
            with self.subTest(path=path), self.assertRaises(vercel.Error):
                vercel.api_url(path, "team-a")
        self.assertEqual(
            vercel.api_url("/v9/projects?limit=2", "team-a"),
            "https://api.vercel.com/v9/projects?limit=2&slug=team-a",
        )

    def test_api_redirect_is_refused(self) -> None:
        with self.assertRaises(vercel.Error):
            vercel.NoRedirect().redirect_request(
                None, None, 302, "", {}, "https://evil.test"
            )

    def test_missing_token_is_actionable(self) -> None:
        with patch.dict(os.environ, {}, clear=True), self.assertRaisesRegex(
            vercel.Error, "Token unavailable"
        ):
            vercel.request("GET", "/v9/projects", "team-a")

    def test_api_401_is_safe_and_not_retried(self):
        opener = Mock()
        opener.open.side_effect = HTTPError(
            "https://api.vercel.com", 401, "RAW_SECRET", {}, None
        )
        with patch.dict(os.environ, {"VERCEL_TOKEN": "RAW_SECRET"}), patch.object(
            vercel, "build_opener", return_value=opener
        ):
            with self.assertRaises(vercel.Error) as error:
                vercel.request("GET", "/v9/projects", "team-a")
        self.assertIn("401", str(error.exception))
        self.assertNotIn("RAW_SECRET", str(error.exception))
        self.assertEqual(opener.open.call_count, 1)

    def test_unknown_write_outcome_not_retried(self) -> None:
        opener = Mock()
        opener.open.side_effect = URLError("private details")
        with patch.dict(os.environ, {"VERCEL_TOKEN": "secret"}), patch.object(
            vercel, "build_opener", return_value=opener
        ):
            with self.assertRaisesRegex(vercel.Error, "outcome may be unknown"):
                vercel.request("POST", "/v10/projects", "team-a", {"name": "demo"})
        self.assertEqual(opener.open.call_count, 1)

    def test_nested_secrets_are_redacted(self) -> None:
        with patch.dict(os.environ, {"VERCEL_TOKEN": "selected-secret"}):
            result = vercel.redact(
                {
                    "token": "hidden",
                    "items": [{"value": "hidden", "note": "selected-secret"}],
                }
            )
        self.assertNotIn("hidden", json.dumps(result))
        self.assertNotIn("selected-secret", json.dumps(result))

    def test_cli_rejects_account_or_credential_overrides(self) -> None:
        for args in [
            ["project", "ls", "--scope=other"],
            ["deploy", "--api", "evil"],
            ["deploy", "-tsecret"],
            ["tokens", "add", "new"],
            ["login"],
        ]:
            with self.subTest(args=args), self.assertRaises(vercel.Error):
                vercel.cli_args(args, "team-a")

    def test_missing_cli_dependency(self) -> None:
        with patch.dict(os.environ, {}, clear=True), patch.object(
            vercel.shutil, "which", return_value=None
        ):
            with self.assertRaisesRegex(vercel.Error, "CLI missing"):
                vercel.cli_args(["project", "ls"], "team-a")

    def test_cli_injects_scope_and_masks_selected_token(self) -> None:
        with patch.dict(
            os.environ,
            {
                "VERCEL_CLI": sys.executable,
                "VERCEL_TOKEN": "test-secret",
                "VERCEL_ORG_ID": "wrong-org",
                "VERCEL_PROJECT_ID": "wrong-project",
            },
        ):
            with patch.object(
                subprocess,
                "run",
                return_value=subprocess.CompletedProcess(
                    [], 7, "test-secret", "test-secret"
                ),
            ) as run:
                out, err = io.StringIO(), io.StringIO()
                with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                    self.assertEqual(vercel.run_cli(["project", "ls"], "team-a"), 7)
        self.assertNotIn("test-secret", out.getvalue() + err.getvalue())
        self.assertNotIn("test-secret", repr(run.call_args.args))
        self.assertNotIn("VERCEL_ORG_ID", run.call_args.kwargs["env"])
        self.assertIn("team-a", run.call_args.args[0])

    def test_profile_is_required(self) -> None:
        with self.assertRaises(vercel.Error):
            vercel.build_parser().parse_args(["projects"])

    def test_parent_selects_only_requested_profile(self) -> None:
        with patch.object(
            subprocess, "run", return_value=subprocess.CompletedProcess([], 0)
        ) as run:
            self.assertEqual(vercel.main(["projects", "--profile", "m2b"]), 0)
        command = run.call_args.args[0]
        self.assertEqual(command[command.index("--profile") + 1], "m2b")
        self.assertIn("VERCEL_TOKEN=token", command)

    def test_write_needs_apply(self) -> None:
        args = vercel.build_parser().parse_args(
            ["api", "--profile", "m2b", "DELETE", "/v9/projects/example"]
        )
        with patch.dict(os.environ, {"VERCEL_SCOPE": "team-a"}), self.assertRaisesRegex(
            vercel.Error, "--apply"
        ):
            vercel.worker(args)

    def test_token_create_stores_without_printing(self) -> None:
        args = vercel.build_parser().parse_args(
            [
                "token-create",
                "--profile",
                "bootstrap",
                "--name",
                "test",
                "--save-as",
                "m2b",
            ]
        )
        with patch.object(
            vercel,
            "request",
            return_value={"bearerToken": "new-secret", "token": {"id": "tok-1"}},
        ), patch.object(vercel, "store_token") as store, patch.object(vercel, "config"):
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                vercel.create_token(args, "team-a")
        store.assert_called_once_with("m2b", "new-secret")
        self.assertNotIn("new-secret", out.getvalue())

    def test_failed_save_after_token_creation_is_explicit(self) -> None:
        args = vercel.build_parser().parse_args(
            [
                "token-create",
                "--profile",
                "bootstrap",
                "--name",
                "test",
                "--save-as",
                "m2b",
            ]
        )
        with patch.object(
            vercel, "request", return_value={"bearerToken": "new-secret"}
        ) as req, patch.object(
            vercel, "store_token", side_effect=vercel.Error("locked")
        ):
            with self.assertRaisesRegex(vercel.Error, "created but vault save failed"):
                vercel.create_token(args, "team-a")
        self.assertEqual(req.call_count, 1)


if __name__ == "__main__":
    unittest.main()
