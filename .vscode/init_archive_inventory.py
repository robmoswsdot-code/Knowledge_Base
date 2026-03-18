"""
Initialize the Civil Engineering knowledge index.

Behavior:
- If a legacy route-based database is detected, back it up and create a fresh v2 database.
- If a v2 database already exists, perform a no-op validation check.
"""

import os
import shutil
import sqlite3
import sys
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(SCRIPT_DIR, "archive_inventory.db")
SCHEMA_PATH = os.path.join(SCRIPT_DIR, "schema.sql")
SCHEMA_VERSION = 2
SCHEMA_DESCRIPTION = "Civil Engineering knowledge index"


def utc_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def log(message):
    print(f"[{utc_now()}] {message}")


def read_schema_sql():
    if not os.path.exists(SCHEMA_PATH):
        log(f"FATAL: Schema file not found: {SCHEMA_PATH}")
        sys.exit(1)
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        return f.read()


def existing_db_kind(path):
    if not os.path.exists(path):
        return "missing"
    if os.path.getsize(path) == 0:
        return "empty"

    try:
        conn = sqlite3.connect(path)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in cur.fetchall()}
        conn.close()
    except sqlite3.DatabaseError:
        return "invalid"

    if "sources" in tables and "knowledge_items" in tables:
        return "v2"
    if "documents" in tables and "route_ids" in tables:
        return "legacy"
    return "unknown"


def backup_existing_db(path):
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup_path = os.path.join(SCRIPT_DIR, f"archive_inventory.legacy.{stamp}.db.bak")
    shutil.copy2(path, backup_path)
    log(f"Legacy database backed up to: {backup_path}")
    os.remove(path)
    log(f"Legacy database removed: {path}")


def version_already_applied(conn):
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM schema_version WHERE version = ?", (SCHEMA_VERSION,))
        return cur.fetchone()[0] > 0
    except sqlite3.Error:
        return False


def post_init_check(conn):
    expected = {
        "schema_version",
        "authority_levels",
        "source_kinds",
        "record_types",
        "relationship_types",
        "tag_types",
        "sources",
        "knowledge_items",
        "tags",
        "source_tags",
        "knowledge_item_tags",
        "knowledge_item_sources",
        "relationships",
        "report_runs",
        "validation_results",
    }
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    actual = {row[0] for row in cur.fetchall()}
    missing = sorted(expected - actual)
    if missing:
        log(f"FATAL: Post-init check failed. Missing tables: {missing}")
        sys.exit(1)
    log("Post-init check passed.")


def initialize_database():
    db_kind = existing_db_kind(DB_PATH)
    log(f"Database state detected: {db_kind}")

    if db_kind == "invalid":
        log("FATAL: Existing archive_inventory.db is not a valid SQLite database.")
        sys.exit(1)
    if db_kind == "legacy":
        backup_existing_db(DB_PATH)
    elif db_kind == "unknown":
        backup_existing_db(DB_PATH)
    elif db_kind == "v2":
        conn = sqlite3.connect(DB_PATH)
        conn.execute("PRAGMA foreign_keys = ON")
        if version_already_applied(conn):
            post_init_check(conn)
            conn.close()
            log("Initialization complete (no-op).")
            return
        conn.close()

    schema_sql = read_schema_sql()
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")

    try:
        conn.execute("BEGIN")
        conn.executescript(schema_sql)
        conn.execute(
            "INSERT INTO schema_version (version, applied_at, description) VALUES (?, ?, ?)",
            (SCHEMA_VERSION, utc_now(), SCHEMA_DESCRIPTION),
        )
        conn.commit()
    except sqlite3.Error as exc:
        conn.rollback()
        conn.close()
        log(f"FATAL: SQL execution failed: {exc}")
        sys.exit(1)

    post_init_check(conn)
    conn.close()
    log("Initialization complete.")


if __name__ == "__main__":
    initialize_database()