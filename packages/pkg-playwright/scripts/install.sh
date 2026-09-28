#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
command -v npm >/dev/null 2>&1 || { echo "Node.js/npm required to install pkg-playwright" >&2; exit 1; }
npm ci --omit=dev --ignore-scripts --no-audit --no-fund
node -e 'require("playwright"); require("express"); console.log("Playwright runtime ready")'
