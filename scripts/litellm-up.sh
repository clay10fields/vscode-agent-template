#!/usr/bin/env bash
# Start the LiteLLM proxy that fronts all agents.
# Cline/Roo/Continue point at http://localhost:$LITELLM_PORT (default 4000).
#
# Uses uvx to run litellm in an isolated Python 3.13 env so we sidestep
# the pyo3-vs-Python-3.14 wheel issue.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

[ -f "$ROOT/.env" ] && { set -a; source "$ROOT/.env"; set +a; }

PORT="${LITELLM_PORT:-4000}"

if ! command -v uvx >/dev/null 2>&1; then
  echo "MISSING: uvx (Astral uv) — install with: brew install uv"
  exit 1
fi

mkdir -p .litellm-cache

if [ -z "${OPENROUTER_API_KEY:-}" ]; then
  echo "WARN: OPENROUTER_API_KEY is empty — only Ollama fallback routes will work."
fi

echo ">> Starting LiteLLM proxy on :$PORT  (uvx, Python 3.13)"
echo "   binding to: 127.0.0.1:$PORT"
exec uvx --python 3.13 --from 'litellm[proxy]' litellm \
  --config "$ROOT/litellm.config.yaml" \
  --port "$PORT" \
  --host 127.0.0.1
