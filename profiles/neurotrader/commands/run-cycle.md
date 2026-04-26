# /run-cycle

Trigger one full trade evaluation cycle on NeuroTrader.

When the user invokes `/run-cycle`:

1. Confirm the bot is in paper mode (read `~/Documents/GitHub/neuro-trade-bot/.env`, check `MODE=paper`).
2. Run `python -m neurotrader.cycle --once` from the bot repo.
3. Tail the resulting log line and report back:
   - How many signals evaluated
   - How many trades opened/closed
   - Any errors
4. Offer to call `/journal` to log the cycle's outcome.

If the bot is NOT in paper mode, refuse and ask the user to confirm explicitly before proceeding.
