#!/usr/bin/env bash
# Runs after setup.sh's main copy step when --profile neurotrader is applied.
# $1 = TARGET project root, $2 = template root.
set -euo pipefail
TARGET="$1"
TEMPLATE="$2"

echo "Applying NeuroTrader post-install steps..."

# 1. Install the Trading Journal MCP server into the target's tools/
mkdir -p "$TARGET/tools/agent-stack/mcp-servers"
cp -R "$TEMPLATE/mcp/servers/trading-journal" "$TARGET/tools/agent-stack/mcp-servers/"

# 2. Install Python deps for it (in user site or active venv)
if command -v pip >/dev/null 2>&1; then
  pip install --user --quiet \
    mcp \
    obsidiantools \
    pyyaml \
    'qdrant-client>=1.7' \
    'sqlalchemy>=2.0' \
    || echo "  (some deps failed — run 'pip install -e tools/agent-stack/mcp-servers/trading-journal' manually if needed)"
fi

# 3. Make trading_journal importable: drop a pyproject + console script
cd "$TARGET/tools/agent-stack/mcp-servers/trading-journal"
if [ -f pyproject.toml ]; then
  pip install --user --quiet -e . || echo "  (editable install skipped)"
fi

# 4. Create the Obsidian vault if it doesn't exist
VAULT="${JOURNAL_VAULT_PATH:-$HOME/Documents/NeuroTrader-Journal}"
if [ ! -d "$VAULT" ]; then
  echo "Creating Obsidian vault at $VAULT"
  mkdir -p "$VAULT"/{Daily,Strategies,Symbols,Patterns}
  cat > "$VAULT/README.md" <<EOF
# NeuroTrader Journal

Auto-populated by the Trading Journal MCP. Open as an Obsidian vault for [[wikilinks]] and graph view.

- **Daily/** — one entry per trading day
- **Strategies/** — per-strategy notes (auto-linked from daily entries)
- **Symbols/** — per-symbol notes
- **Patterns/** — emergent patterns the agent notices over time
EOF
fi

# 5. Merge MCP config additions into target's mcp/config.json
PROFILE_MCP="$TEMPLATE/profiles/neurotrader/mcp/config.append.json"
TARGET_MCP="$TARGET/mcp/config.json"
if [ -f "$PROFILE_MCP" ] && [ -f "$TARGET_MCP" ] && command -v jq >/dev/null 2>&1; then
  TMP="$(mktemp)"
  jq -s '.[0].mcpServers + .[1].mcpServers | {mcpServers: .}' "$TARGET_MCP" "$PROFILE_MCP" > "$TMP"
  mv "$TMP" "$TARGET_MCP"
  echo "  Merged trading-journal + tradingview MCP configs."
else
  echo "  (jq not available — manually merge $PROFILE_MCP into $TARGET_MCP)"
fi

echo "NeuroTrader profile applied."
echo "  Vault:    $VAULT"
echo "  MCP src:  $TARGET/tools/agent-stack/mcp-servers/trading-journal"
