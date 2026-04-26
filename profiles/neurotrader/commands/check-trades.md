# /check-trades

Summarize recent trade outcomes from the NeuroTrader SQLite DB.

When the user invokes `/check-trades`:

1. Call the Trading Journal MCP `recent_trades(window="24h")` tool.
2. Render a table:
   - timestamp | symbol | side | entry | exit | P&L | strategy
3. Below the table, summarize:
   - Total trades, win rate, net P&L
   - Best and worst strategy by win rate
   - Anything anomalous (e.g. 5+ losses in a row, P&L >2σ from rolling mean)
4. Offer to follow up with `/journal` to write today's reflection.

Default window is 24h. Accept arguments like `/check-trades 7d` or `/check-trades since-monday`.
