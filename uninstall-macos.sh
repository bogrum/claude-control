#!/usr/bin/env bash
# Removes the macOS .app bundle. Leaves project files alone.
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
APP_DIR="$HOME/Applications/Claude Control.app"

if [ -x "$PROJECT_DIR/.venv/bin/python" ]; then
  "$PROJECT_DIR/.venv/bin/python" "$PROJECT_DIR/launcher.py" --stop || true
fi

rm -rf "$APP_DIR"
echo "✓ App bundle removed."
echo "  To remove project files: rm -rf '$PROJECT_DIR'"
