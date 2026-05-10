#!/usr/bin/env bash
# Removes the desktop entry and icon. Leaves the project directory and venv
# alone — delete them manually if you want a full uninstall.
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
APPS_DIR="$HOME/.local/share/applications"
ICONS_DIR="$HOME/.local/share/icons/hicolor/256x256/apps"

# Stop running instance first
if [ -x "$PROJECT_DIR/.venv/bin/python" ]; then
  "$PROJECT_DIR/.venv/bin/python" "$PROJECT_DIR/launcher.py" --stop || true
fi

rm -f "$APPS_DIR/claude-control.desktop"
rm -f "$ICONS_DIR/claude-control.png"

if command -v update-desktop-database >/dev/null; then
  update-desktop-database "$APPS_DIR" 2>/dev/null || true
fi

echo "✓ Desktop entry removed."
echo "  To remove project files:  rm -rf '$PROJECT_DIR'"
