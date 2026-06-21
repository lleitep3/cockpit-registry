#!/usr/bin/env sh
# deploy-skills.sh — Deploys caveman skills to each active AI provider.
# Called by: cockpit pkg install caveman (post_install hook)
set -e

PACKAGE_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "Deploying caveman skills to active AI providers..."
echo ""

deployed=0
skipped=0

# ── Antigravity (Google DeepMind) ────────────────────────────────────────────
ANTIGRAVITY_SKILLS_DIR="$HOME/.gemini/config/skills/caveman"
if [ -d "$HOME/.gemini/config" ]; then
  mkdir -p "$ANTIGRAVITY_SKILLS_DIR"
  cp "$PACKAGE_DIR/skills/antigravity/SKILL.md" "$ANTIGRAVITY_SKILLS_DIR/SKILL.md"
  echo "  ✓ Antigravity: ${ANTIGRAVITY_SKILLS_DIR}/SKILL.md"
  deployed=$((deployed + 1))
else
  echo "  - Antigravity: not detected (no ~/.gemini/config)"
  skipped=$((skipped + 1))
fi

# ── Goose (Block) ─────────────────────────────────────────────────────────────
GOOSE_SKILLS_DIR="$HOME/.config/goose/skills/caveman"
if [ -d "$HOME/.config/goose" ] || command -v goose >/dev/null 2>&1; then
  mkdir -p "$GOOSE_SKILLS_DIR"
  cp "$PACKAGE_DIR/skills/goose/SKILL.md" "$GOOSE_SKILLS_DIR/SKILL.md"
  echo "  ✓ Goose: ${GOOSE_SKILLS_DIR}/SKILL.md"
  deployed=$((deployed + 1))
else
  echo "  - Goose: not detected (no ~/.config/goose)"
  skipped=$((skipped + 1))
fi

# ── Devin (Cognition AI) ──────────────────────────────────────────────────────
if command -v devin >/dev/null 2>&1 || [ -f "$HOME/.devin/config.json" ]; then
  echo "  ✓ Devin: skill available at ${PACKAGE_DIR}/skills/devin/SKILL.md"
  deployed=$((deployed + 1))
else
  echo "  - Devin: not detected"
  skipped=$((skipped + 1))
fi

echo ""
echo "Done. Deployed: ${deployed} provider(s), skipped: ${skipped}."
echo ""
echo "Activate with: /caveman"
echo "Levels: /caveman lite | /caveman full (default) | /caveman ultra"
echo "Deactivate: \"normal mode\" or \"stop caveman\""
