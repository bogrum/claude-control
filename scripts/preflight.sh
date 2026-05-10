#!/usr/bin/env bash
# Run this before `git push` to a public repo. It refuses to pass if any
# obvious secrets or sensitive paths are present.
set -uo pipefail
cd "$(dirname "$0")/.."

red() { printf '\033[31m%s\033[0m\n' "$1"; }
green() { printf '\033[32m%s\033[0m\n' "$1"; }
yellow() { printf '\033[33m%s\033[0m\n' "$1"; }

fail=0

echo "▸ Checking for committed .env files…"
bad_env=$(git ls-files | grep -E '^\.env$|^\.env\.' | grep -v '^\.env\.example$' || true)
if [ -n "$bad_env" ]; then
  red "  ✗ Found tracked .env file(s):"
  echo "$bad_env"
  fail=1
else
  green "  ✓ ok"
fi

echo "▸ Checking for tracked settings.local.json or .claude/ dir…"
if git ls-files | grep -qE 'settings\.local\.json$|^\.claude/'; then
  red "  ✗ Found tracked Claude config — these belong in .gitignore"
  fail=1
else
  green "  ✓ ok"
fi

echo "▸ Scanning for likely secrets in tracked files…"
secrets=$(git ls-files | xargs grep -nIE 'sk-ant-[a-zA-Z0-9_-]{20,}|AKIA[0-9A-Z]{16}|ghp_[a-zA-Z0-9]{30,}|api[_-]?key\s*=\s*["'"'"'][^"'"'"']{20,}' 2>/dev/null || true)
if [ -n "$secrets" ]; then
  red "  ✗ Possible secrets found:"
  echo "$secrets"
  fail=1
else
  green "  ✓ ok"
fi

echo "▸ Checking for personal absolute paths…"
paths=$(git ls-files | xargs grep -nIE '/home/[a-z]+/(?!claude)' 2>/dev/null | grep -v '\.example' | grep -v 'README' || true)
if [ -n "$paths" ]; then
  yellow "  ⚠ Personal paths found (review manually):"
  echo "$paths" | head -20
fi

echo "▸ Checking gitignore exists and excludes secrets…"
if [ ! -f .gitignore ]; then
  red "  ✗ No .gitignore"
  fail=1
elif ! grep -q '^\.env$' .gitignore; then
  red "  ✗ .gitignore does not exclude .env"
  fail=1
else
  green "  ✓ ok"
fi

echo
if [ "$fail" -eq 0 ]; then
  green "All checks passed. Safe to push."
  exit 0
else
  red "FAILED — fix the issues above before pushing."
  exit 1
fi
