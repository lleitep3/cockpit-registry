import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


class InstallHookTests(unittest.TestCase):
    def test_install_and_failure_propagation(self):
        source = Path(__file__).resolve().parents[1]
        for fail in (False, True):
            with self.subTest(fail=fail), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                package = root / "package with spaces"
                shutil.copytree(source / "scripts", package / "scripts")
                fake = root / "bin"
                fake.mkdir()
                log = root / "calls"
                for name in ("npm", "node"):
                    script = fake / name
                    script.write_text('#!/bin/sh\necho "' + name + ' $*" >> "$CALLS"\n' + ("exit 7\n" if fail and name == "npm" else "exit 0\n"))
                    script.chmod(0o755)
                env = dict(os.environ, PATH=str(fake) + os.pathsep + os.environ["PATH"], CALLS=str(log))
                result = subprocess.run(["sh", str(package / "scripts/install.sh")], cwd=root, env=env, capture_output=True)
                self.assertEqual(result.returncode, 7 if fail else 0)
                calls = log.read_text()
                self.assertIn("npm ci --omit=dev --ignore-scripts --no-audit --no-fund", calls)
                self.assertEqual("node " in calls, not fail)


if __name__ == "__main__":
    unittest.main()
