"""Resolve config from env, with sensible defaults."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Config:
    vault: Path
    db_path: Path
    qdrant_url: str | None
    qdrant_api_key: str | None

    @property
    def qdrant_enabled(self) -> bool:
        return bool(self.qdrant_url)


def load() -> Config:
    home = Path.home()
    vault = Path(
        os.environ.get(
            "JOURNAL_VAULT_PATH",
            home / "Documents" / "NeuroTrader-Journal",
        )
    ).expanduser()
    db = Path(
        os.environ.get(
            "NEUROTRADER_DB_PATH",
            home / "Documents" / "GitHub" / "neuro-trade-bot" / "data" / "neurotrader.db",
        )
    ).expanduser()
    qurl = os.environ.get("QDRANT_URL") or None
    qkey = os.environ.get("QDRANT_API_KEY") or None
    return Config(vault=vault, db_path=db, qdrant_url=qurl, qdrant_api_key=qkey)
