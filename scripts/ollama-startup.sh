#!/usr/bin/env bash
# Boot Ollama and pull the local fallback models. Idempotent.
set -euo pipefail

if ! command -v ollama >/dev/null 2>&1; then
  echo "Installing Ollama..."
  curl -fsSL https://ollama.com/install.sh | sh
fi

# Start the daemon if not already running
if ! pgrep -x "ollama" >/dev/null; then
  echo "Starting Ollama daemon..."
  ollama serve >/dev/null 2>&1 &
  sleep 3
fi

# Models to pull. Comment out anything your hardware can't handle.
MODELS=(
  "qwen2.5-coder:7b"      # autocomplete
  "qwen2.5-coder:14b"     # quick-shell fallback
  "qwen2.5-coder:32b"     # code-gen fallback (~20 GB)
  "qwen3:14b"             # co-lead fallback
  "qwen3:32b"             # head-dev fallback (~20 GB)
  "nomic-embed-text"      # embeddings for journal/qdrant
)

for m in "${MODELS[@]}"; do
  if ! ollama list | awk '{print $1}' | grep -qx "$m"; then
    echo "Pulling $m..."
    ollama pull "$m"
  else
    echo "$m already present, skipping."
  fi
done

echo "Ollama ready. Models: $(ollama list | tail -n +2 | awk '{print $1}' | xargs)"
