#!/usr/bin/env sh
# install-rtk.sh — Downloads and installs the rtk binary.
# Called by: cockpit pkg install rtk (pre_install hook)
set -e

INSTALL_DIR="${RTK_INSTALL_DIR:-$HOME/.local/bin}"
RTK_VERSION="${RTK_VERSION:-latest}"

# Check if rtk is already installed and up-to-date
if command -v rtk >/dev/null 2>&1; then
  CURRENT=$(rtk --version 2>/dev/null | awk '{print $2}' || echo "unknown")
  echo "rtk already installed: v${CURRENT}"
  if [ "$RTK_VERSION" = "latest" ] || [ "$CURRENT" = "$RTK_VERSION" ]; then
    echo "  → Nothing to do."
    exit 0
  fi
  echo "  → Upgrading to ${RTK_VERSION}..."
fi

# Detect OS and architecture
OS=$(uname -s | tr '[:upper:]' '[:lower:]')
ARCH=$(uname -m)

case "$ARCH" in
  x86_64)  ARCH="x86_64" ;;
  aarch64) ARCH="aarch64" ;;
  arm64)   ARCH="aarch64" ;;
  *)
    echo "ERROR: Unsupported architecture: $ARCH"
    exit 1
    ;;
esac

case "$OS" in
  linux)  TARGET="${ARCH}-unknown-linux-musl" ;;
  darwin) TARGET="${ARCH}-apple-darwin" ;;
  *)
    echo "ERROR: Unsupported OS: $OS"
    exit 1
    ;;
esac

# Resolve version
if [ "$RTK_VERSION" = "latest" ]; then
  echo "Fetching latest RTK release..."
  RTK_VERSION=$(curl -fsSL "https://api.github.com/repos/carlosles/rtk/releases/latest" \
    | grep '"tag_name"' | sed 's/.*"tag_name": *"\([^"]*\)".*/\1/')
  if [ -z "$RTK_VERSION" ]; then
    echo "ERROR: Could not determine latest RTK version."
    exit 1
  fi
  echo "  → Latest version: ${RTK_VERSION}"
fi

BINARY_NAME="rtk-${TARGET}"
DOWNLOAD_URL="https://github.com/carlosles/rtk/releases/download/${RTK_VERSION}/${BINARY_NAME}.tar.gz"

echo "Downloading RTK ${RTK_VERSION} for ${TARGET}..."
TMP_DIR=$(mktemp -d)
trap 'rm -rf "$TMP_DIR"' EXIT

curl -fsSL "$DOWNLOAD_URL" -o "${TMP_DIR}/rtk.tar.gz" || {
  echo "ERROR: Failed to download RTK from: $DOWNLOAD_URL"
  exit 1
}

tar -xzf "${TMP_DIR}/rtk.tar.gz" -C "$TMP_DIR"

mkdir -p "$INSTALL_DIR"
cp "${TMP_DIR}/rtk" "${INSTALL_DIR}/rtk"
chmod +x "${INSTALL_DIR}/rtk"

echo "✓ RTK installed: ${INSTALL_DIR}/rtk ($(rtk --version 2>/dev/null || echo 'version unknown'))"

# Ensure INSTALL_DIR is in PATH hint
case ":$PATH:" in
  *":$INSTALL_DIR:"*) ;;
  *)
    echo ""
    echo "  ⚠ ${INSTALL_DIR} is not in your PATH."
    echo "  Add this to your shell profile:"
    echo "    export PATH=\"${INSTALL_DIR}:\$PATH\""
    ;;
esac
