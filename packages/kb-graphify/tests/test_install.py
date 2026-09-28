import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


class GraphifyInstallTests(unittest.TestCase):
    def test_private_install_and_failure(self):
        source = Path(__file__).resolve().parents[1]
        for fail in (False, True):
            with self.subTest(fail=fail), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                package = root / "package with spaces"
                shutil.copytree(source / "scripts", package / "scripts")
                fake = root / "bin"
                fake.mkdir()
                calls = root / "calls"
                python = fake / "python3"
                python.write_text('#!/bin/sh\necho "python3 $*" >> "$CALLS"\nmkdir -p .venv/bin\nprintf "#!/bin/sh\\nexit 0\\n" > .venv/bin/graphify\nchmod +x .venv/bin/graphify\n')
                python.chmod(0o755)
                uv = fake / "uv"
                uv.write_text('#!/bin/sh\necho "uv $*" >> "$CALLS"\nexit ' + ('7' if fail else '0') + '\n')
                uv.chmod(0o755)
                env = dict(os.environ, PATH=str(fake) + os.pathsep + os.environ["PATH"], CALLS=str(calls))
                result = subprocess.run(["sh", str(package / "scripts/install.sh")], cwd=root, env=env, capture_output=True)
                self.assertEqual(result.returncode, 7 if fail else 0, result.stderr)
                self.assertIn("python3 -m venv --copies --without-pip .venv", calls.read_text())
                self.assertIn("uv pip install --link-mode copy --python .venv/bin/python --requirement requirements.txt", calls.read_text())

    def test_extensions_reject_missing_private_runtime(self):
        source = Path(__file__).resolve().parents[1]
        for name in ("kb-search", "kb-index"):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                shutil.copytree(source / "bin", root / "bin")
                result = subprocess.run(["sh", str(root / "bin" / name), "test"], capture_output=True, text=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("Graphify runtime missing", result.stderr)

    def test_extension_runs_private_runtime_under_sh(self):
        source = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shutil.copytree(source / "bin", root / "bin")
            runtime = root / ".venv/bin"
            runtime.mkdir(parents=True)
            graphify = runtime / "graphify"
            graphify.write_text('#!/bin/sh\nprintf "private-runtime-ok\\n"\n')
            graphify.chmod(0o755)
            fake = root / "fake"
            fake.mkdir()
            cockpit = fake / "cockpit"
            cockpit.write_text('#!/bin/sh\nprintf "offline-test\\n"\n')
            cockpit.chmod(0o755)
            env = dict(os.environ, PATH=str(fake) + os.pathsep + os.environ["PATH"])
            result = subprocess.run(["sh", str(root / "bin/kb-search"), "fixture"], env=env, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("private-runtime-ok", result.stdout)
            self.assertNotIn("Bad substitution", result.stderr)


if __name__ == "__main__":
    unittest.main()
