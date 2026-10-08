#!/bin/sh
set -eu
PACKAGE_DIR="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
if [ -z "${PYTHON:-}" ]; then
  if command -v python3.12 >/dev/null 2>&1; then PYTHON=python3.12; else PYTHON=python3; fi
fi
"$PYTHON" -c 'import sys; assert sys.version_info >= (3,12), "Python >=3.12 necessário"'
RUNTIME_ROOT="${TEST_DATA_RUNTIME_ROOT:-${XDG_DATA_HOME:-$HOME/.local/share}/cockpit/test-data/runtimes}"
mkdir -p "$RUNTIME_ROOT"
RUNTIME="$(mktemp -d "$RUNTIME_ROOT/install.XXXXXXXX")"
"$PYTHON" -m venv --copies "$RUNTIME"
"$RUNTIME/bin/python" -m pip install --disable-pip-version-check --no-input -r "$PACKAGE_DIR/cli/requirements.lock"
"$RUNTIME/bin/python" -m pip install --disable-pip-version-check --no-input --no-deps "$PACKAGE_DIR/cli"
"$RUNTIME/bin/python" -m pip check
"$RUNTIME/bin/massa" --help >/dev/null
"$RUNTIME/bin/python" - "$PACKAGE_DIR" "$RUNTIME" <<'ACTIVATE'
import os
import sys
from pathlib import Path
package, runtime = map(Path, sys.argv[1:])
active = package / '.venv'
if active.exists() and not active.is_symlink():
    raise SystemExit('Preserve o diretório .venv existente antes de instalar')
staged = package / (runtime.name + '.link')
staged.symlink_to(runtime)
os.replace(staged, active)
ACTIVATE
