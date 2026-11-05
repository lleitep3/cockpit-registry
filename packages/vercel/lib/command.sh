#!/usr/bin/env bash
set -euo pipefail
PACKAGE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
command -v python3 >/dev/null || { echo "Python 3.10+ required" >&2; exit 127; }
exec python3 "${PACKAGE_DIR}/lib/vercel.py" "$@"
