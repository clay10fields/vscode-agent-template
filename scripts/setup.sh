#!/usr/bin/env bash
# vscode-agent-template — setup.sh
# Installs the multi-agent stack into the current project (the "target").
#
# Usage:
#   bash setup.sh                          # bare install
#   bash setup.sh --profile neurotrader    # with NeuroTrader overlay
#   bash setup.sh --target /path/to/proj   # install into a specific project
#
set -euo pipefail

# ------------------------------------------------------------------
# Args
# ------------------------------------------------------------------
PROFILE=""
TARGET="$(pwd)"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --profile) PROFILE="$2"; shift 2 ;;
    --target)  TARGET="$2"; shift 2 ;;
    -h|--help)
      sed -n '2,12p' "$0"
      exit 0 ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

TEMPLATE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET="$(cd "$TARGET" && pwd)"

echo ""
echo "== vscode-agent-template setup =="
echo "  template:  $TEMPLATE_ROOT"
echo "  target:    $TARGET"
echo "  profile:   ${PROFILE:-<none>}"
echo ""

# ------------------------------------------------------------------
# Pre-flight
# ------------------------------------------------------------------
need() { command -v "$1" >/dev/null 2>&1 || { echo "MISSING: $1 — install with brew"; return 1; }; }
need git
need code || echo "  (VS Code 'code' CLI not on PATH — install via Cmd+Shift+P > 'Shell Command: Install code command')"
need curl
need jq || true   # not strictly required, used for nicer prompts

# ------------------------------------------------------------------
# Copy core configs into target
# ------------------------------------------------------------------
copy_dir() {
  local src="$1" dst="$2"
  mkdir -p "$dst"
  cp -R "$src/." "$dst/"
}

echo "Copying core configs..."
copy_dir "$TEMPLATE_ROOT/dot-vscode"  "$TARGET/.vscode"
copy_dir "$TEMPLATE_ROOT/.cline"      "$TARGET/.cline"
copy_dir "$TEMPLATE_ROOT/agents"      "$TARGET/agents"
copy_dir "$TEMPLATE_ROOT/mcp"         "$TARGET/mcp"

# scripts and litellm config — put in a tools/ subfolder so we don't pollute root
mkdir -p "$TARGET/tools/agent-stack"
cp "$TEMPLATE_ROOT/litellm.config.yaml" "$TARGET/tools/agent-stack/litellm.config.yaml"
cp "$TEMPLATE_ROOT/scripts/litellm-up.sh"      "$TARGET/tools/agent-stack/litellm-up.sh"
cp "$TEMPLATE_ROOT/scripts/ollama-startup.sh"  "$TARGET/tools/agent-stack/ollama-startup.sh"
chmod +x "$TARGET/tools/agent-stack/"*.sh

# .env scaffold
if [ ! -f "$TARGET/.env" ]; then
  cp "$TEMPLATE_ROOT/.env.example" "$TARGET/.env"
  echo "  Created $TARGET/.env (fill in OPENROUTER_API_KEY)"
fi

# Continue.dev config — lives in user home, not project
if [ ! -f "$HOME/.continue/config.json" ]; then
  mkdir -p "$HOME/.continue"
  cp "$TEMPLATE_ROOT/agents/continue-config.json" "$HOME/.continue/config.json"
  echo "  Installed Continue.dev config at ~/.continue/config.json"
else
  echo "  ~/.continue/config.json already exists, leaving as is."
fi

# ------------------------------------------------------------------
# Rewrite ${PROJECT_ROOT} in mcp/config.json
# ------------------------------------------------------------------
if [ -f "$TARGET/mcp/config.json" ]; then
  sed -i.bak "s|\${PROJECT_ROOT}|$TARGET|g" "$TARGET/mcp/config.json"
  rm -f "$TARGET/mcp/config.json.bak"
fi

# ------------------------------------------------------------------
# Apply profile overlay (if requested)
# ------------------------------------------------------------------
if [ -n "$PROFILE" ]; then
  PROFILE_DIR="$TEMPLATE_ROOT/profiles/$PROFILE"
  if [ ! -d "$PROFILE_DIR" ]; then
    echo "ERROR: profile '$PROFILE' not found at $PROFILE_DIR"
    exit 1
  fi
  echo "Applying profile: $PROFILE"

  # Profiles can ship: agents/, commands/, mcp/, CLAUDE.md.append, post-install.sh
  [ -d "$PROFILE_DIR/agents" ]   && cp -R "$PROFILE_DIR/agents/."   "$TARGET/agents/"
  [ -d "$PROFILE_DIR/commands" ] && { mkdir -p "$TARGET/.cline/commands"; cp -R "$PROFILE_DIR/commands/." "$TARGET/.cline/commands/"; }
  [ -d "$PROFILE_DIR/mcp" ]      && cp -R "$PROFILE_DIR/mcp/."      "$TARGET/mcp/"

  # Append to CLAUDE.md if profile provides extras
  if [ -f "$PROFILE_DIR/CLAUDE.md.append" ]; then
    if [ ! -f "$TARGET/CLAUDE.md" ]; then
      cp "$PROFILE_DIR/CLAUDE.md.append" "$TARGET/CLAUDE.md"
    else
      printf "\n\n%s\n" "$(cat "$PROFILE_DIR/CLAUDE.md.append")" >> "$TARGET/CLAUDE.md"
    fi
  fi

  # Per-profile post-install hook (eg. install Trading Journal MCP deps)
  if [ -f "$PROFILE_DIR/post-install.sh" ]; then
    bash "$PROFILE_DIR/post-install.sh" "$TARGET" "$TEMPLATE_ROOT"
  fi
fi

# ------------------------------------------------------------------
# .gitignore — append our exclusions if not already present
# ------------------------------------------------------------------
GITIGNORE="$TARGET/.gitignore"
touch "$GITIGNORE"
for line in ".env" ".litellm-cache/" ".cline/cache/" "qdrant-data/" "journal-vault.local/"; do
  grep -qxF "$line" "$GITIGNORE" || echo "$line" >> "$GITIGNORE"
done

# ------------------------------------------------------------------
# Friendly finish
# ------------------------------------------------------------------
cat <<EOF

== DONE ==

Next steps:
  1. Edit $TARGET/.env and set OPENROUTER_API_KEY.
  2. (One-time) Pull Ollama models in the background:
       bash $TARGET/tools/agent-stack/ollama-startup.sh
  3. Start the LiteLLM proxy in a terminal tab:
       bash $TARGET/tools/agent-stack/litellm-up.sh
  4. Open the project in VS Code:
       code $TARGET
     Accept the recommended extensions when prompted.
  5. Open Cline (sidebar) and verify it connects to localhost:4000.

Profile applied: ${PROFILE:-<none>}
EOF
