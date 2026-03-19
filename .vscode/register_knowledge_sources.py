"""Register source documents in the Civil Engineering knowledge index."""

import os
import sqlite3
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
DB_PATH = os.path.join(SCRIPT_DIR, "archive_inventory.db")

SOURCE_REGISTRATIONS = [
    {
        "title": "WSDOT Standard Specifications",
        "authority_level": "WSDOT",
        "source_kind": "manual",
        "path": "docs/manuals/Standard_Specifications.pdf",
        "status": "active",
        "notes": "Authoritative specifications manual added for Civil Engineering reference.",
        "tags": {
            "discipline": ["civil_general"],
            "topic": ["standards", "specifications"],
            "decision_type": ["design_review"]
        }
    },
    {
        "title": "RES Utility Project Coordination Process Matrix",
        "authority_level": "supporting",
        "source_kind": "reference",
        "path": "docs/debriefs/RES_Utility Project Coordination Process Matrix.09.2025.pdf",
        "status": "active",
        "notes": "Training debrief reference on utility coordination process.",
        "tags": {
            "discipline": ["utilities"],
            "topic": ["coordination", "process"],
            "decision_type": ["stakeholder_coordination"]
        }
    },
    {
        "title": "Utilities in WSDOT Projects - Grub Club 3-2026",
        "authority_level": "supporting",
        "source_kind": "note",
        "path": "docs/debriefs/Utilities in WSDOT Projects - Grub Club 3-2026.pdf",
        "status": "active",
        "notes": "Training debrief on utility considerations in WSDOT projects.",
        "tags": {
            "discipline": ["utilities"],
            "topic": ["utility_coordination", "training"],
            "decision_type": ["discipline_briefing"]
        }
    }
]


def utc_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def get_or_create_tag(conn, tag_type, tag_value):
    conn.execute(
        "INSERT OR IGNORE INTO tags (tag_type, tag_value) VALUES (?, ?)",
        (tag_type, tag_value),
    )
    row = conn.execute(
        "SELECT id FROM tags WHERE tag_type = ? AND tag_value = ?",
        (tag_type, tag_value),
    ).fetchone()
    return row[0]


def register_source(conn, source):
    abs_path = os.path.join(REPO_ROOT, source["path"].replace("/", os.sep))
    if not os.path.isfile(abs_path):
        raise FileNotFoundError(f"Missing file: {source['path']}")

    existing = conn.execute(
        "SELECT id FROM sources WHERE path = ?",
        (source["path"],),
    ).fetchone()

    now = utc_now()
    if existing:
        source_id = existing[0]
        conn.execute(
            """
            UPDATE sources
            SET title = ?, authority_level = ?, source_kind = ?, status = ?,
                notes = ?, updated_at = ?
            WHERE id = ?
            """,
            (
                source["title"],
                source["authority_level"],
                source["source_kind"],
                source["status"],
                source["notes"],
                now,
                source_id,
            ),
        )
        conn.execute("DELETE FROM source_tags WHERE source_id = ?", (source_id,))
        mode = "updated"
    else:
        conn.execute(
            """
            INSERT INTO sources
            (title, authority_level, source_kind, path, status, last_reviewed, notes, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                source["title"],
                source["authority_level"],
                source["source_kind"],
                source["path"],
                source["status"],
                now[:10],
                source["notes"],
                now,
                now,
            ),
        )
        source_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        mode = "inserted"

    for tag_type, values in source["tags"].items():
        for value in values:
            tag_id = get_or_create_tag(conn, tag_type, value)
            conn.execute(
                "INSERT OR IGNORE INTO source_tags (source_id, tag_id) VALUES (?, ?)",
                (source_id, tag_id),
            )

    return source_id, mode


def main():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("BEGIN")
    try:
        for source in SOURCE_REGISTRATIONS:
            source_id, mode = register_source(conn, source)
            print(f"{mode.upper()}: source_id={source_id} path={source['path']}")
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()