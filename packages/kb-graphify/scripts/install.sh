#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
command -v uv >/dev/null 2>&1 || { echo "uv is required to install kb-graphify" >&2; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "Python 3 is required to install kb-graphify" >&2; exit 1; }
python3 -m venv --copies --without-pip .venv
uv pip install --link-mode copy --python .venv/bin/python --requirement requirements.txt
.venv/bin/graphify --help >/dev/null
printf '%s\n' 'Graphify runtime ready (package-local virtual environment)'
