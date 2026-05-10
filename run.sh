#!/usr/bin/env bash
# Launch claude-control bound to loopback only.
set -euo pipefail
cd "$(dirname "$0")"

HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8765}"

if [[ "$HOST" != "127.0.0.1" && "$HOST" != "localhost" ]]; then
  echo "WARNING: binding to $HOST. claude-control has no auth. Make sure your firewall blocks $PORT from untrusted networks."
fi

exec python -m uvicorn app.main:app --host "$HOST" --port "$PORT" --reload
