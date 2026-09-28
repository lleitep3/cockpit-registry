import argparse
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parents[1] / "lib"))
import key_setup as setup


class KeySetupTests(unittest.TestCase):
    def test_origin_rejects_external_http_and_spoof(self) -> None:
        for url in [
            "http://one.newrelic.com",
            "https://one.newrelic.com.evil.test",
            "https://one.eu.newrelic.com",
            "https://one.newrelic.com:9443",
        ]:
            with self.assertRaises(setup.nr.ClientError):
                setup.require_origin(url, "US")
        setup.require_origin("https://one.newrelic.com/admin-portal", "US")

    def test_atomic_journal_private_and_no_secret(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "journal.json"
            setup.atomic_json(p, {"status": "submission-started", "name": "test"})
            self.assertEqual(p.stat().st_mode & 0o777, 0o600)
            self.assertEqual(json.loads(p.read_text())["name"], "test")

    def test_locked_vault_stops_before_browser(self) -> None:
        with (
            patch.object(
                setup.subprocess,
                "run",
                return_value=subprocess.CompletedProcess(
                    [], 0, "Status: 🔒 LOCKED", ""
                ),
            ),
            self.assertRaises(setup.nr.ClientError),
        ):
            setup.vault_ready()

    def test_preview_has_no_side_effects(self) -> None:
        args = argparse.Namespace(
            setup_profile="dev", profile=None, plan=True, types=["user"]
        )
        with (
            patch.dict(os.environ, {}, clear=True),
            patch.object(
                setup.nr,
                "load_profiles",
                return_value={
                    "dev": {
                        "account_id": 42,
                        "region": "US",
                        "vault_key": "newrelic-dev",
                    }
                },
            ),
            patch.object(setup, "vault_ready") as vault,
            patch.object(setup, "launch_user_bootstrap") as browser,
        ):
            result = setup.execute(args)
            self.assertFalse(result["creates_keys"])
            vault.assert_not_called()
            browser.assert_not_called()

    def test_uncertain_submission_never_retries(self) -> None:
        with (
            tempfile.TemporaryDirectory() as d,
            patch.object(setup, "launch_user_bootstrap") as browser,
        ):
            root = Path(d)
            setup.atomic_json(
                root / "dev.key-setup.json", {"status": "submission-started"}
            )
            with self.assertRaises(setup.nr.ClientError):
                setup.provision(
                    "dev", {"account_id": 42, "region": "US"}, ["user"], root
                )
            browser.assert_not_called()

    def test_valid_key_reused_without_browser_or_mutation(self) -> None:
        with (
            tempfile.TemporaryDirectory() as d,
            patch.object(setup.nr, "vault_credential", return_value="offline-test"),
            patch.object(setup, "check_account"),
            patch.object(setup, "launch_user_bootstrap") as browser,
            patch.object(setup, "create_ingest") as ingest,
        ):
            result = setup.provision(
                "dev",
                {"account_id": 42, "region": "US", "vault_key": "newrelic-dev"},
                ["user"],
                Path(d),
            )
            self.assertEqual(result["configured_types"], ["user"])
            browser.assert_not_called()
            ingest.assert_not_called()

    def test_wrong_account_stops_before_create_submit(self) -> None:
        page = MagicMock()
        page.url = "https://one.newrelic.com/admin-portal"
        page.get_by_text.return_value.count.return_value = 0
        page.get_by_role.return_value.inner_text.return_value = "Account: 99 - Other"
        with (
            tempfile.TemporaryDirectory() as d,
            self.assertRaises(setup.nr.ClientError),
        ):
            setup.user_key_from_page(page, 42, "US", "test", Path(d) / "journal")
        page.get_by_role.return_value.last.click.assert_not_called()

    def test_vault_pty_input_no_secret_in_arguments(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            fake = p / "cockpit"
            fake.write_text(
                "#!/usr/bin/env python3\nimport sys,getpass,os\nfrom pathlib import Path\np=Path(os.environ['FAKE_SECRET_FILE'])\nif sys.argv[2]=='set': p.write_text(getpass.getpass(\"Enter secret for 'test': \"))\nelif sys.argv[2]=='get': print(p.read_text(),end='')\n"
            )
            fake.chmod(0o700)
            with (
                patch.dict(
                    os.environ,
                    {
                        "PATH": str(p) + os.pathsep + os.environ["PATH"],
                        "FAKE_SECRET_FILE": str(p / "secret"),
                    },
                ),
                patch.object(
                    setup.subprocess, "Popen", wraps=subprocess.Popen
                ) as launch,
            ):
                setup.vault_save("newrelic-test", "offline-private-value")
                self.assertNotIn("offline-private-value", str(launch.call_args))
                self.assertEqual(
                    launch.call_args_list[0].args[0],
                    [
                        "cockpit",
                        "vault",
                        "set",
                        "--namespace",
                        "newrelic",
                        "newrelic-test",
                    ],
                )
                self.assertEqual(
                    launch.call_args_list[1].args[0],
                    [
                        "cockpit",
                        "vault",
                        "get",
                        "--namespace",
                        "newrelic",
                        "newrelic-test",
                    ],
                )
                self.assertEqual((p / "secret").read_text(), "offline-private-value")

    def test_ingest_mutation_has_fixed_type_and_handles_partial_failure(self) -> None:
        good = {
            "data": {
                "apiAccessCreateKeys": {
                    "createdKeys": [
                        {
                            "id": "1",
                            "key": "offline-ingest",
                            "type": "INGEST",
                            "ingestType": "LICENSE",
                        }
                    ],
                    "errors": [],
                }
            }
        }
        with patch.object(setup.urllib.request, "build_opener") as opener:
            opener.return_value.open.return_value = io.BytesIO(
                json.dumps(good).encode()
            )
            result = setup.create_ingest("offline-user", 42, "US", "LICENSE", "fixture")
            self.assertEqual(result["id"], "1")
            req = opener.return_value.open.call_args.args[0]
            self.assertEqual(json.loads(req.data)["variables"]["id"], 42)
            self.assertEqual(req.full_url, setup.nr.ENDPOINTS["US"])
            good["data"]["apiAccessCreateKeys"]["errors"] = [{"type": "failure"}]
            opener.return_value.open.return_value = io.BytesIO(
                json.dumps(good).encode()
            )
            with self.assertRaises(setup.nr.ClientError):
                setup.create_ingest("offline-user", 42, "US", "LICENSE", "fixture")
        with self.assertRaises(setup.nr.ClientError):
            setup.create_ingest("offline-user", 42, "US", "OTHER", "fixture")

    def test_network_failure_never_creates_replacement_key(self) -> None:
        with (
            tempfile.TemporaryDirectory() as d,
            patch.object(setup.nr, "vault_credential", return_value="offline-test"),
            patch.object(
                setup,
                "check_account",
                side_effect=setup.nr.ClientError("network failure"),
            ),
            patch.object(setup, "launch_user_bootstrap") as browser,
        ):
            with self.assertRaises(setup.nr.ClientError):
                setup.provision(
                    "dev",
                    {"account_id": 42, "region": "US", "vault_key": "newrelic-dev"},
                    ["user"],
                    Path(d),
                )
            browser.assert_not_called()


if __name__ == "__main__":
    unittest.main()
