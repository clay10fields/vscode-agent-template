# /journal

Write today's trading journal entry to the Obsidian vault.

When the user invokes `/journal`:

1. Call the Trading Journal MCP `summarize_day(date="today")` tool to get the structured day summary.
2. Generate a markdown entry with:
   - YAML frontmatter (date, total_trades, net_pnl, win_rate, best_strategy, worst_strategy, tags)
   - **What worked** — strategies/symbols that won, with [[wikilinks]] to strategy notes
   - **What didn't** — strategies/symbols that lost, with [[wikilinks]]
   - **Patterns I noticed** — any anomalies surfaced by /check-trades
   - **Hypotheses to test** — concrete experiments for tomorrow
   - **Code/config changes today** — pulled from git log
3. Call `journal_write(date, content)` to save it to `~/Documents/NeuroTrader-Journal/Daily/YYYY-MM-DD.md`.
4. If Qdrant is enabled, the MCP automatically embeds the entry for semantic search later.

Tone: honest, brief, second-person ("you"). The agent writes to the user, not about itself.
