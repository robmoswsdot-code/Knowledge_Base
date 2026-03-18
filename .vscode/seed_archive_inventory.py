"""Seed and verify the Civil Engineering knowledge index."""

import datetime
import hashlib
import os
import sqlite3
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(SCRIPT_DIR, "archive_inventory.db")
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
TODAY = datetime.date.today().isoformat()
NOW = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_of_file(path):
    if not os.path.isfile(path):
        return None
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def rel_path(path):
    return os.path.relpath(path, REPO_ROOT).replace("\\", "/")


def first_file_under(path):
    if not os.path.isdir(path):
        return None
    for root, _, files in os.walk(path):
        for name in sorted(files):
            return os.path.join(root, name)
    return None


def ensure_seed_report():
    report_dir = os.path.join(REPO_ROOT, "docs", "reports", "agent_reports")
    os.makedirs(report_dir, exist_ok=True)
    report_path = os.path.join(report_dir, "seed_discovery_report.md")
    if not os.path.exists(report_path):
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("# Seed Discovery Report\n\nPlaceholder report for knowledge-index validation.\n")
    return report_path


def get_or_create_tag(conn, tag_type, tag_value):
    conn.execute("INSERT OR IGNORE INTO tags (tag_type, tag_value) VALUES (?, ?)", (tag_type, tag_value))
    row = conn.execute("SELECT id FROM tags WHERE tag_type = ? AND tag_value = ?", (tag_type, tag_value)).fetchone()
    return row[0]


def main():
    if not os.path.isfile(DB_PATH):
        print("FAIL  database not found")
        return 1

    manual_path = first_file_under(os.path.join(REPO_ROOT, "docs", "manuals"))
    artifact_path = first_file_under(os.path.join(REPO_ROOT, "docs", "artifacts"))
    report_path = ensure_seed_report()

    if artifact_path is None:
        print("FAIL  no supporting artifact found under docs/artifacts")
        return 1

    conn = sqlite3.connect(DB_PATH, isolation_level=None)
    conn.execute("PRAGMA foreign_keys = ON")

    results = []
    passed = True

    try:
        conn.execute("BEGIN")

        if manual_path is not None:
            conn.execute(
                "INSERT INTO sources (title, authority_level, source_kind, path, status, last_reviewed, notes, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (os.path.basename(manual_path), "WSDOT", "manual", rel_path(manual_path), "active", TODAY, "seed manual", NOW, NOW),
            )
            manual_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
            results.append(("PASS", f"insert source manual id={manual_id}"))
        else:
            manual_id = None
            results.append(("SKIP", "no manual file found under docs/manuals"))

        conn.execute(
            "INSERT INTO sources (title, authority_level, source_kind, path, status, last_reviewed, notes, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (os.path.basename(artifact_path), "supporting", "artifact", rel_path(artifact_path), "active", TODAY, "seed supporting artifact", NOW, NOW),
        )
        artifact_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        results.append(("PASS", f"insert source artifact id={artifact_id}"))

        conn.execute(
            "INSERT INTO knowledge_items (title, record_type, authority_level, summary, confidence_basis, output_path, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                "Seed discovery report",
                "discovery_report",
                "derived",
                "Seed report for validator coverage.",
                "Grounded in the seeded source set.",
                rel_path(report_path),
                NOW,
                NOW,
            ),
        )
        report_item_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        results.append(("PASS", f"insert knowledge item report id={report_item_id}"))

        for tag_type, tag_value in [("discipline", "civil_general"), ("topic", "decision_support"), ("decision_type", "discovery")]:
            tag_id = get_or_create_tag(conn, tag_type, tag_value)
            conn.execute(
                "INSERT INTO knowledge_item_tags (knowledge_item_id, tag_id) VALUES (?, ?)",
                (report_item_id, tag_id),
            )
        results.append(("PASS", "tagged discovery report"))

        conn.execute(
            "INSERT INTO knowledge_item_sources (knowledge_item_id, source_id) VALUES (?, ?)",
            (report_item_id, artifact_id),
        )
        if manual_id is not None:
            conn.execute(
                "INSERT INTO knowledge_item_sources (knowledge_item_id, source_id) VALUES (?, ?)",
                (report_item_id, manual_id),
            )
        results.append(("PASS", "linked report to non-derived source records"))

        if manual_id is not None:
            conn.execute(
                "INSERT INTO relationships (from_type, from_id, to_type, to_id, relationship_type) VALUES (?, ?, ?, ?, ?)",
                ("source", manual_id, "knowledge_item", report_item_id, "governs"),
            )
            results.append(("PASS", "manual governs report relationship inserted"))

        conn.execute(
            "INSERT INTO report_runs (request_summary, report_path, governing_sources_summary, created_at) VALUES (?, ?, ?, ?)",
            ("Seed discovery validation", rel_path(report_path), "Seeded sources", NOW),
        )
        results.append(("PASS", "report_runs record inserted"))

        bad_report_insert_rejected = False
        try:
            conn.execute(
                "INSERT INTO knowledge_items (title, record_type, authority_level, summary, confidence_basis, output_path, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                ("Bad report", "discovery_report", "derived", "bad", "bad", "docs/reports/outside.md", NOW, NOW),
            )
            bad_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
            tag_d = get_or_create_tag(conn, "discipline", "temp")
            tag_t = get_or_create_tag(conn, "topic", "temp")
            conn.execute("INSERT INTO knowledge_item_tags (knowledge_item_id, tag_id) VALUES (?, ?)", (bad_id, tag_d))
            conn.execute("INSERT INTO knowledge_item_tags (knowledge_item_id, tag_id) VALUES (?, ?)", (bad_id, tag_t))
            conn.execute("INSERT INTO knowledge_item_sources (knowledge_item_id, source_id) VALUES (?, ?)", (bad_id, artifact_id))
        except sqlite3.IntegrityError:
            bad_report_insert_rejected = True
        results.append(("INFO", f"invalid report path requires validator check={not bad_report_insert_rejected}"))

        conn.execute("ROLLBACK")
        results.append(("INFO", "transaction rolled back - database unchanged except seed report file"))
    except Exception as exc:
        conn.execute("ROLLBACK")
        print(f"FAIL  exception during seed test: {exc}")
        conn.close()
        return 1

    conn.close()

    print("=" * 64)
    print("  CE KNOWLEDGE INDEX SEED TEST RESULTS")
    print(f"  {NOW}")
    print("=" * 64)
    pass_count = 0
    skip_count = 0
    for status, message in results:
        print(f"  {status:<4}  {message}")
        if status == "PASS":
            pass_count += 1
        elif status == "SKIP":
            skip_count += 1
    print("-" * 64)
    print(f"  PASS: {pass_count}  SKIP: {skip_count}")
    print("  OVERALL: PASS")
    print("=" * 64)
    return 0


if __name__ == "__main__":
    sys.exit(main())