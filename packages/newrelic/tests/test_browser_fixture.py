"""Opt-in CDP integration against a local HTML fixture; never logs in to New Relic."""

import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parents[1] / "lib"))
import key_setup


@unittest.skipUnless(
    os.environ.get("NEWRELIC_LOCAL_BROWSER_TEST") == "1", "opt-in local Chrome fixture"
)
class BrowserFixture(unittest.TestCase):
    def test_cdp_create_capture_and_journal(self) -> None:
        from playwright.sync_api import sync_playwright

        chrome = shutil.which("google-chrome")
        self.assertIsNotNone(chrome)
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            process = subprocess.Popen(
                [
                    str(chrome),
                    "--headless=new",
                    f"--user-data-dir={root / 'browser'}",
                    "--remote-debugging-address=127.0.0.1",
                    "--remote-debugging-port=0",
                    "--no-first-run",
                    "about:blank",
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            try:
                portfile = root / "browser/DevToolsActivePort"
                deadline = time.monotonic() + 20
                while not portfile.exists() and time.monotonic() < deadline:
                    time.sleep(0.1)
                self.assertTrue(portfile.exists())
                port = int(portfile.read_text().splitlines()[0])
                with sync_playwright() as pw:
                    browser = pw.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
                    page = browser.contexts[0].new_page()
                    page.set_content("""<button onclick="document.querySelector('#dialog').hidden=false">Create a key</button>
                    <section id="dialog" hidden><button aria-label="Account">Account: 42 - Test</button><button aria-label="Key type">User</button>
                    <label>Name<input></label><label>Notes<input></label>
                    <button onclick="document.body.innerHTML='<button>Copy Key</button><p>NRAK-0000000000000000000000000</p>'">Create a key</button></section>""")
                    with patch.object(key_setup, "require_origin"):
                        value = key_setup.user_key_from_page(
                            page, 42, "US", "fixture-key", root / "journal.json"
                        )
                    self.assertTrue(value.startswith("NRAK-"))
                    self.assertNotIn(value, (root / "journal.json").read_text())
                    browser.new_browser_cdp_session().send("Browser.close")
                    process.wait(timeout=10)
            finally:
                process.terminate()
                process.wait(timeout=10)


if __name__ == "__main__":
    unittest.main()
