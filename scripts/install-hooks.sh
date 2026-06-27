#!/bin/bash

# Install git hooks script
# Configures git core.hooksPath to .githooks and makes hooks executable

echo "Installing git hooks..."

# Set git hooks path to .githooks directory
git config core.hooksPath .githooks

# Ensure pre-commit hook is executable
chmod +x .githooks/pre-commit

echo "Git hooks installed successfully!"
echo "Hooks are now configured to run before each commit."
echo ""
echo "To uninstall hooks, run:"
echo "  git config --unset core.hooksPath"