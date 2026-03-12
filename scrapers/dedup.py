"""
Aberdeen Insider — Deduplication Store
Tracks every event and news item we've ever seen so we never surface
the same thing twice across weekly runs.

Uses SQLite — no dependencies, just a file at data/seen.db.
"""

import sqlite3
import hashlib
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "seen.db"


def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS seen_items (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            identifier  TEXT UNIQUE NOT NULL,
            title       TEXT,
            source      TEXT,
            item_type   TEXT,
            first_seen  TEXT NOT NULL
        )
    """)
    conn.commit()
    return conn


def _make_identifier(item: dict, id_key: str) -> str:
    """Build a stable unique identifier for an item."""
    raw = str(item.get(id_key, ""))
    if raw:
        return raw.strip().lower()
    # Fallback: hash the title if no ID/URL
    title = item.get("title", item.get("name", ""))
    return hashlib.md5(title.strip().lower().encode()).hexdigest()


def is_seen(identifier: str) -> bool:
    """Return True if this identifier has been seen before."""
    with _connect() as conn:
        row = conn.execute(
            "SELECT 1 FROM seen_items WHERE identifier = ?", (identifier,)
        ).fetchone()
        return row is not None


def mark_seen(identifier: str, title: str = "", source: str = "", item_type: str = "") -> None:
    """Record an identifier as seen. Safe to call multiple times."""
    with _connect() as conn:
        conn.execute(
            """INSERT OR IGNORE INTO seen_items
               (identifier, title, source, item_type, first_seen)
               VALUES (?, ?, ?, ?, ?)""",
            (identifier, title, source, item_type, datetime.now().isoformat())
        )
        conn.commit()


def filter_new(items: list[dict], id_key: str = "url") -> tuple[list[dict], int]:
    """
    Filter a list of items, returning only ones we haven't seen before.
    Also marks all new items as seen immediately.

    Returns (new_items, skipped_count)
    """
    new_items = []
    skipped = 0

    for item in items:
        identifier = _make_identifier(item, id_key)

        if is_seen(identifier):
            skipped += 1
        else:
            new_items.append(item)
            mark_seen(
                identifier=identifier,
                title=item.get("title", item.get("name", "")),
                source=item.get("source", ""),
                item_type=item.get("type", ""),
            )

    return new_items, skipped


def seen_count() -> int:
    """Total number of items tracked in the store."""
    with _connect() as conn:
        return conn.execute("SELECT COUNT(*) FROM seen_items").fetchone()[0]


def clear_all() -> None:
    """Wipe the seen store — use only in dev/testing."""
    with _connect() as conn:
        conn.execute("DELETE FROM seen_items")
        conn.commit()
    print("⚠️  Seen store cleared.")


if __name__ == "__main__":
    print(f"Seen store at: {DB_PATH}")
    print(f"Total items tracked: {seen_count()}")
