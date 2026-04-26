# /audit-ghost-code

Scan for unreachable, dormant, or orphaned code paths.

When the user invokes `/audit-ghost-code`:

1. Use `vulture` (or `ruff` with the dead-code rules) on `neurotrader/`.
2. Cross-reference: any function that's not called AND not in `__all__` AND not registered in a strategy plugin → flag it.
3. Look at `git log -S` to see if the function was ever used historically — if it was wired in then unwired, that's a "ghost feature." Surface it.
4. Output a markdown table:
   - file:line | symbol | status (orphan / dormant / never-called) | suggestion (delete / wire in / keep + add comment)
5. Do NOT delete anything automatically. The user reviews and decides.

Background: three dormant features were recently wired in (canary, auto-backup, cluster caps). The goal of this audit is to catch the next wave before they go stale.
