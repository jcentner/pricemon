from __future__ import annotations

import sqlite3
from pathlib import Path

from .models import FeedItem


class SeenStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def init(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS seen_items (
                    item_id TEXT PRIMARY KEY,
                    source_name TEXT NOT NULL,
                    title TEXT NOT NULL,
                    link TEXT NOT NULL,
                    rule_name TEXT,
                    delivered INTEGER NOT NULL DEFAULT 0,
                    first_seen_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    delivered_at TEXT
                );

                CREATE TABLE IF NOT EXISTS state (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
                """
            )

    def is_initialized(self) -> bool:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT value FROM state WHERE key = 'initialized'"
            ).fetchone()
        return row is not None and row[0] == "1"

    def set_initialized(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO state (key, value)
                VALUES ('initialized', '1')
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
                """
            )

    def is_source_initialized(self, source_name: str) -> bool:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT value FROM state WHERE key = ?",
                (_source_key(source_name),),
            ).fetchone()
        return row is not None and row[0] == "1"

    def set_source_initialized(self, source_name: str) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO state (key, value)
                VALUES (?, '1')
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
                """,
                (_source_key(source_name),),
            )

    def is_seen(self, item_id: str) -> bool:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT 1 FROM seen_items WHERE item_id = ?",
                (item_id,),
            ).fetchone()
        return row is not None

    def mark_seen(
        self,
        item: FeedItem,
        *,
        rule_name: str | None = None,
        delivered: bool = False,
    ) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR IGNORE INTO seen_items (
                    item_id, source_name, title, link, rule_name, delivered, delivered_at
                )
                VALUES (?, ?, ?, ?, ?, ?, CASE WHEN ? THEN CURRENT_TIMESTAMP ELSE NULL END)
                """,
                (
                    item.item_id,
                    item.source_name,
                    item.title,
                    item.link,
                    rule_name,
                    1 if delivered else 0,
                    1 if delivered else 0,
                ),
            )

    def mark_many_seen(self, items: list[FeedItem]) -> None:
        with self._connect() as conn:
            conn.executemany(
                """
                INSERT OR IGNORE INTO seen_items (item_id, source_name, title, link)
                VALUES (?, ?, ?, ?)
                """,
                [(item.item_id, item.source_name, item.title, item.link) for item in items],
            )

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path)


def _source_key(source_name: str) -> str:
    return f"source_initialized:{source_name}"