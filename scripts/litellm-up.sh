#!/usr/bin/env bash
# Start the LiteLLM proxy that fronts all agents.
# Cline/Roo/Continue point at http://localhost:$LITELLM_PORT (default 4000).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [ -f .env ]; then
  set -a; source .env; set +a
fi

PORT="${LITELLM_PORT:-4000}"

if ! command -v litellm >/dev/null 2>&1; then
  echo "Installing litellm via pipx..."
  pipx install 'litellm[proxy]' || pip install --user 'litellm[proxy]'
fi

mkdir -p .litellm-cache

echo "Starting LiteLLM proxy on :$PORT — Ctrl-C to stop."
exec litellm --config "$ROOT/litellm.config.yaml" --port "$PORT" --host 127.0.0.1
