# trading-journal-mcp

MCP server for NeuroTrader. Reads trade outcomes from SQLite, writes Obsidian-friendly markdown to a vault, and optionally embeds entries to Qdrant for semantic search.

## Tools exposed

| Tool                           | Purpose                                                       |
| ------------------------------ | ------------------------------------------------------------- |
| `recent_trades(window)`        | Last N hours/days of trades, formatted for chat               |
| `summarize_day(date)`          | Structured day summary (counts, win rate, P&L by strategy)    |
| `journal_write(date, content)` | Save a markdown entry to `Daily/YYYY-MM-DD.md` in the vault   |
| `journal_search(query, k)`     | Semantic search if Qdrant enabled, else fallback to ripgrep   |
| `strategy_stats(name)`         | Aggregate metrics for one strategy across history             |

## Config (env vars)

- `JOURNAL_VAULT_PATH` — Obsidian vault root (default `~/Documents/NeuroTrader-Journal`)
- `NEUROTRADER_DB_PATH` — SQLite file (default `~/Documents/GitHub/neuro-trade-bot/data/neurotrader.db`)
- `QDRANT_URL` / `QDRANT_API_KEY` — optional, leave empty to disable semantic search

## Run

```bash
python -m trading_journal.server
```

Or via the `trading-journal-mcp` console script after `pip install -e .`.

## Vault layout

```
NeuroTrader-Journal/
├── Daily/         <- one per trading day, YAML frontmatter + markdown body
├── Strategies/    <- per-strategy notes, auto-linked from Daily entries
├── Symbols/       <- per-symbol notes
└── Patterns/      <- emergent patterns the agent flagged
```
