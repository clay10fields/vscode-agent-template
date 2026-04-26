"""MCP server entrypoint.

Exposes:
  recent_trades(window="24h", limit=200)
  summarize_day(date="today")
  journal_write(date, content, frontmatter_extras=None)
  journal_search(query, k=5)
  strategy_stats(name)
"""

from __future__ import annotations

import json
import subprocess
from datetime import date as Date, datetime
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

from . import config, db, vault
from .embed import Embedder

CFG = config.load()
EMB = Embedder(CFG.qdrant_url, CFG.qdrant_api_key)
mcp = FastMCP("trading-journal")


def _today() -> Date:
    return datetime.utcnow().date()


def _resolve_date(d: str) -> Date:
    if d == "today":
        return _today()
    return Date.fromisoformat(d)


# ----------------------------------------------------------------------
# tools
# ----------------------------------------------------------------------
@mcp.tool()
def recent_trades(window: str = "24h", limit: int = 200) -> dict[str, Any]:
    """Last N trades within `window` (e.g. '24h', '7d', '30m')."""
    rows = db.recent_trades(CFG.db_path, window=window, limit=limit)
    summary = vault.summarize_trades(rows)
    return {"trades": rows, "summary": summary, "window": window}


@mcp.tool()
def summarize_day(date: str = "today") -> dict[str, Any]:
    """Structured summary of one day's trading."""
    d = _resolve_date(date)
    rows = db.day_rows(CFG.db_path, d.isoformat())
    summary = vault.summarize_trades(rows)
    return {"date": d.isoformat(), "summary": summary, "trades": rows}


@mcp.tool()
def journal_write(
    date: str,
    content: str,
    frontmatter_extras: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Save a daily journal entry to the Obsidian vault.

    The agent passes the markdown body; we compute the day's stats from the DB
    and merge them into the YAML frontmatter so Dataview can query them.
    """
    d = _resolve_date(date)
    rows = db.day_rows(CFG.db_path, d.isoformat())
    summary = vault.summarize_trades(rows)
    fm = {**summary, **(frontmatter_extras or {}), "tags": ["trading", "neurotrader", "daily"]}
    path = vault.write_daily(
        CFG.vault, d, content, fm,
        strategies=summary["strategies"],
        symbols=summary["symbols"],
    )
    EMB.upsert(
        doc_id=f"daily/{d.isoformat()}",
        text=content,
        payload={"date": d.isoformat(), **summary},
    )
    return {"path": str(path), "wrote_to_qdrant": EMB.enabled}


@mcp.tool()
def journal_search(query: str, k: int = 5) -> dict[str, Any]:
    """Semantic search if Qdrant is enabled, else fallback to ripgrep over the vault."""
    if EMB.enabled:
        return {"backend": "qdrant", "hits": EMB.search(query, k=k)}

    # Fallback: ripgrep
    if not CFG.vault.exists():
        return {"backend": "fs", "hits": [], "note": "vault does not exist"}
    try:
        out = subprocess.run(
            ["rg", "--no-heading", "--line-number", "-i", query, str(CFG.vault)],
            capture_output=True, text=True, timeout=10,
        )
        hits = [
            {"file": line.split(":", 2)[0], "line": int(line.split(":", 2)[1]), "text": line.split(":", 2)[2]}
            for line in out.stdout.splitlines()[: k * 5]
            if line.count(":") >= 2
        ]
    except FileNotFoundError:
        hits = []
    return {"backend": "fs", "hits": hits[:k]}


@mcp.tool()
def strategy_stats(name: str) -> dict[str, Any]:
    """Aggregate metrics for a single strategy across all history."""
    return db.strategy_stats(CFG.db_path, name)


def main() -> None:
    """Console entrypoint."""
    mcp.run()


if __name__ == "__main__":
    main()
