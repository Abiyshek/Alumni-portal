"""SQLite helpers for the alumni portal."""

import os
import sqlite3

from flask import current_app, g

SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")

# (table, column, definition) for columns added after the first release
ADDED_COLUMNS = [
    ("memories", "image", "TEXT"),
    ("users", "notify_email", "INTEGER NOT NULL DEFAULT 1"),
    ("users", "notif_seen_at", "TEXT"),
]


def get_db():
    if "db" not in g:
        # Wait up to 30s for another request's write to finish instead of failing with "database is locked".
        g.db = sqlite3.connect(current_app.config["DATABASE"], timeout=30)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(_exc=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with sqlite3.connect(path) as conn, open(SCHEMA_PATH, encoding="utf-8") as f:
        conn.executescript(f.read())
        # Columns added after launch: CREATE TABLE IF NOT EXISTS won't add them to an existing database.
        for table, column, definition in ADDED_COLUMNS:
            existing = {row[1] for row in conn.execute(f"PRAGMA table_info({table})")}
            if column not in existing:
                conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def query(sql, args=(), one=False):
    rows = get_db().execute(sql, args).fetchall()
    return (rows[0] if rows else None) if one else rows


def execute(sql, args=()):
    db = get_db()
    cur = db.execute(sql, args)
    db.commit()
    return cur.lastrowid


def requires_approval():
    """Whether new signups wait for a coordinator. The Admin panel switch wins over REQUIRE_APPROVAL."""
    row = query("SELECT value FROM settings WHERE key='auto_approve'", one=True)
    if row is None:
        return current_app.config["REQUIRE_APPROVAL"]
    return row["value"] != "1"
