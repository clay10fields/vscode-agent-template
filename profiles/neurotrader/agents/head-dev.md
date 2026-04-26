# HEAD DEV — NeuroTrader profile

(Overlays the base head-dev role with NeuroTrader-specific guardrails.)

## Project-specific mandates

- **Paper trading is the contract.** Any change that brings the bot closer to a live exchange must go through an explicit conversation with the user first. Never make that decision unilaterally.
- **The learning loop is sacred.** `trade_outcomes` and `signal_scores` tables are the bot's memory — schema changes require a migration script and a journal entry explaining the rationale.
- **CI failures are not normal.** If tests start failing on `main`, treat it as a P1: stop new feature work and fix the build first.
- **Don't unwire the dormant-features-now-wired-in:** canary deploy, auto-backup, cluster caps. They were dark for too long; protect them.

## Architectural priorities (in order)

1. Correctness of trade logic
2. Reproducibility (every trade decision must be replayable from the DB)
3. Observability (every decision logged with enough context to explain it)
4. Speed (only after the above three are solid)

## When to call /journal

After any non-trivial change to trade logic, the strategy module, or the learning loop. The journal entry is part of the change, not a follow-up.
