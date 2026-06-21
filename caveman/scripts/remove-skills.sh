#!/usr/bin/env sh
# remove-skills.sh — Removes caveman skills from AI providers.
# Called by: cockpit pkg uninstall caveman (pre_uninstall hook)
set -e

echo "Removing caveman skills from AI providers..."
echo ""

removed=0

ANTIGRAVITY_SKILLS_DIR="$HOME/.gemini/config/skills/caveman"
if [ -d "$ANTIGRAVITY_SKILLS_DIR" ]; then
  rm -rf "$ANTIGRAVITY_SKILLS_DIR"
  echo "  ✓ Antigravity: removed ${ANTIGRAVITY_SKILLS_DIR}"
  removed=$((removed + 1))
fi

GOOSE_SKILLS_DIR="$HOME/.config/goose/skills/caveman"
if [ -d "$GOOSE_SKILLS_DIR" ]; then
  rm -rf "$GOOSE_SKILLS_DIR"
  echo "  ✓ Goose: removed ${GOOSE_SKILLS_DIR}"
  removed=$((removed + 1))
fi

echo ""
echo "Done. Removed from ${removed} provider(s)."
