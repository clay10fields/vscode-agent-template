# CODE GEN — NeuroTrader profile

(Overlays the base code-gen role.)

## Project-specific patterns

- **Prefer small modules in `neurotrader/strategies/`** over adding to a god-module. Each strategy is a class with `score(signal) -> float`.
- **Trade-touching code needs a test in `tests/test_*.py`** before merging — no exceptions, even for "obvious" fixes.
- **Use the existing `db.session()` helper** — don't open raw SQLite connections in new code.
- **TradingView signals come through the `tradingview-mcp` server.** Don't re-implement TV API calls — go through the MCP.

## Common patterns to copy

When adding a new strategy: see `neurotrader/strategies/momentum.py` as the canonical example. Same shape: dataclass for params, `score()` method, registered in `strategies/__init__.py`.

When adding a new metric: emit it through `neurotrader/observability/metrics.py` so the dashboard picks it up automatically.
