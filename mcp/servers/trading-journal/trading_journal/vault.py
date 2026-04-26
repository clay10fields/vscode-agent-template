"""Obsidian-friendly markdown writer.

Convention:
  Daily/YYYY-MM-DD.md          one per trading day
  Strategies/<name>.md         autocreated when a strategy is wikilinked
  Symbols/<TICKER>.md          autocreated when a symbol is wikilinked
  Patterns/<slug>.md           manually curated by the agent

Every Daily entry has YAML frontmatter — Obsidian Dataview reads it.
"""

from __future__ import annotations

import re
from collections import Counter
from datetime import date as Date, datetime
from pathlib import Path
from typing import Any

import yaml


def ensure_layout(vault: Path) -> None:
    for sub in ("Daily", "Strategies", "Symbols", "Patterns"):
        (vault / sub).mkdir(parents=True, exist_ok=True)


def _slug(s: str) -> str:
    return re.sub(r"[^\w-]+", "-", s.strip()).strip("-")


def _ensure_stub(path: Path, title: str, kind: str) -> None:
    if path.exists():
        return
    path.write_text(
        f"---\ntitle: {title}\nkind: {kind}\ncreated: {datetime.utcnow().isoformat()}\n---\n\n"
        f"# {title}\n\n_Auto-created by trading-journal-mcp. Add notes here._\n"
    )


def daily_path(vault: Path, day: Date) -> Path:
    return vault / "Daily" / f"{day.isoformat()}.md"


def write_daily(
    vault: Path,
    day: Date,
    body: str,
    frontmatter: dict[str, Any],
    strategies: list[str] | None = None,
    symbols: list[str] | None = None,
) -> Path:
    ensure_layout(vault)
    fm = {"date": day.isoformat(), **frontmatter}
    rendered = "---\n" + yaml.safe_dump(fm, sort_keys=False).strip() + "\n---\n\n" + body.strip() + "\n"

    p = daily_path(vault, day)
    p.write_text(rendered)

    for s in strategies or []:
        _ensure_stub(vault / "Strategies" / f"{_slug(s)}.md", s, "strategy")
    for s in symbols or []:
        _ensure_stub(vault / "Symbols" / f"{s.upper()}.md", s.upper(), "symbol")

    return p


def summarize_trades(trades: list[dict]) -> dict[str, Any]:
    """Compute the stats a daily entry's frontmatter wants."""
    if not trades:
        return {
            "total_trades": 0, "net_pnl": 0.0, "win_rate": 0.0,
            "best_strategy": None, "worst_strategy": None,
            "strategies": [], "symbols": [],
        }

    by_strategy: dict[str, list[float]] = {}
    by_symbol: Counter[str] = Counter()
    total_pnl = 0.0
    wins = 0
    for t in trades:
        pnl = float(t.get("pnl") or 0)
        total_pnl += pnl
        if pnl > 0:
            wins += 1
        by_strategy.setdefault(t.get("strategy") or "?", []).append(pnl)
        by_symbol[t.get("symbol") or "?"] += 1

    strat_pnl = {k: sum(v) for k, v in by_strategy.items()}
    best = max(strat_pnl, key=strat_pnl.get) if strat_pnl else None
    worst = min(strat_pnl, key=strat_pnl.get) if strat_pnl else None

    return {
        "total_trades": len(trades),
        "net_pnl": round(total_pnl, 2),
        "win_rate": round(wins / len(trades), 3),
        "best_strategy": best,
        "worst_strategy": worst,
        "strategies": sorted(by_strategy.keys()),
        "symbols": [s for s, _ in by_symbol.most_common()],
    }
