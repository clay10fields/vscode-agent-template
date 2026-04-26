"""Read-only access to the NeuroTrader SQLite DB.

Schema we depend on (from neuro-trade-bot):
  trade_outcomes (id, ts_open, ts_close, symbol, side, entry, exit, pnl, strategy)
  signal_scores  (id, ts, symbol, strategy, score, raw_signal_json)

If your schema differs, adjust the SQL strings here — they're isolated
to one file on purpose.
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterator


def parse_window(window: str) -> timedelta:
    """Accept '24h', '7d', '30m', '2w' and return a timedelta."""
    window = window.strip().lower()
    if not window or not window[-1].isalpha():
        raise ValueError(f"bad window: {window!r}")
    n, unit = int(window[:-1]), window[-1]
    return {
        "m": timedelta(minutes=n),
        "h": timedelta(hours=n),
        "d": timedelta(days=n),
        "w": timedelta(weeks=n),
    }[unit]


@contextmanager
def open_db(path: Path) -> Iterator[sqlite3.Connection]:
    if not path.exists():
        raise FileNotFoundError(f"NeuroTrader DB not found: {path}")
    conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def recent_trades(path: Path, window: str = "24h", limit: int = 200) -> list[dict]:
    cutoff = (datetime.utcnow() - parse_window(window)).isoformat()
    with open_db(path) as c:
        rows = c.execute(
            """
            SELECT ts_open, ts_close, symbol, side, entry, exit, pnl, strategy
            FROM trade_outcomes
            WHERE ts_close >= ?
            ORDER BY ts_close DESC
            LIMIT ?
            """,
            (cutoff, limit),
        ).fetchall()
        return [dict(r) for r in rows]


def day_rows(path: Path, day_iso: str) -> list[dict]:
    """All trades closed on `day_iso` (YYYY-MM-DD)."""
    start = f"{day_iso}T00:00:00"
    end = f"{day_iso}T23:59:59"
    with open_db(path) as c:
        rows = c.execute(
            """
            SELECT ts_open, ts_close, symbol, side, entry, exit, pnl, strategy
            FROM trade_outcomes
            WHERE ts_close BETWEEN ? AND ?
            ORDER BY ts_close
            """,
            (start, end),
        ).fetchall()
        return [dict(r) for r in rows]


def strategy_stats(path: Path, name: str) -> dict:
    with open_db(path) as c:
        agg = c.execute(
            """
            SELECT
              COUNT(*)              AS n,
              SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) * 1.0 / COUNT(*) AS win_rate,
              SUM(pnl)              AS total_pnl,
              AVG(pnl)              AS avg_pnl,
              MIN(ts_close)         AS first_trade,
              MAX(ts_close)         AS last_trade
            FROM trade_outcomes
            WHERE strategy = ?
            """,
            (name,),
        ).fetchone()
        return dict(agg) if agg else {}
