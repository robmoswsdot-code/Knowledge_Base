"""Query the Civil Engineering knowledge index by keyword.

Usage:
    python .vscode/query_knowledge_index.py <keyword>

Returns matching sources, knowledge items, and tags from archive_inventory.db.
"""

import os
import sqlite3
import sys
import json
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(SCRIPT_DIR, "archive_inventory.db")
QA_HISTORY_PATH = os.path.join(SCRIPT_DIR, "qa_history.json")


def utc_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def query_sources(conn, keyword):
    rows = conn.execute(
        """
        SELECT s.id, s.title, s.authority_level, s.source_kind, s.path, s.notes,
               GROUP_CONCAT(DISTINCT t.tag_type || ':' || t.tag_value) AS tags
        FROM sources s
        LEFT JOIN source_tags st ON st.source_id = s.id
        LEFT JOIN tags t ON t.id = st.tag_id
        WHERE s.title LIKE ?
           OR s.notes LIKE ?
           OR t.tag_value LIKE ?
        GROUP BY s.id
        ORDER BY s.authority_level, s.title
        """,
        (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"),
    ).fetchall()
    return rows


def query_knowledge_items(conn, keyword):
    rows = conn.execute(
        """
        SELECT ki.id, ki.title, ki.record_type, ki.authority_level, ki.summary,
               ki.confidence_basis, ki.output_path,
               GROUP_CONCAT(DISTINCT t.tag_type || ':' || t.tag_value) AS tags
        FROM knowledge_items ki
        LEFT JOIN knowledge_item_tags kit ON kit.knowledge_item_id = ki.id
        LEFT JOIN tags t ON t.id = kit.tag_id
        WHERE ki.title LIKE ?
           OR ki.summary LIKE ?
           OR t.tag_value LIKE ?
        GROUP BY ki.id
        ORDER BY ki.authority_level, ki.title
        """,
        (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"),
    ).fetchall()
    return rows


def print_results(keyword, sources, knowledge_items):
    print(f"\n=== Knowledge Index Query: '{keyword}' ===\n")

    print(f"--- Sources ({len(sources)} match(es)) ---")
    if sources:
        for row in sources:
            print(f"  [source_id={row[0]}] {row[1]}")
            print(f"    authority : {row[2]}")
            print(f"    kind      : {row[3]}")
            print(f"    path      : {row[4]}")
            print(f"    notes     : {row[5]}")
            print(f"    tags      : {row[6] or 'none'}")
            print()
    else:
        print("  No matching sources found.\n")

    print(f"--- Knowledge Items ({len(knowledge_items)} match(es)) ---")
    if knowledge_items:
        for row in knowledge_items:
            print(f"  [item_id={row[0]}] {row[1]}")
            print(f"    type      : {row[2]}")
            print(f"    authority : {row[3]}")
            print(f"    summary   : {row[4]}")
            print(f"    confidence: {row[5]}")
            print(f"    output    : {row[6]}")
            print(f"    tags      : {row[7] or 'none'}")
            print()
    else:
        print("  No matching knowledge items found.\n")

    total = len(sources) + len(knowledge_items)
    if total == 0:
        print("RESULT: No matches found. Topic is not registered in the repository.")
    else:
        print(f"RESULT: {total} match(es) found.")


def load_qa_history():
    if not os.path.exists(QA_HISTORY_PATH):
        return {"qa_history": []}
    with open(QA_HISTORY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_qa_history(history):
    with open(QA_HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)


def lookup_prior_correct_answers(keyword):
    """Return all qa_history entries with verdict=correct for this keyword."""
    history = load_qa_history()
    return [
        e for e in history.get("qa_history", [])
        if e.get("keyword", "").lower() == keyword.lower()
        and e.get("verdict") == "correct"
    ]


def record_query(keyword, sources, knowledge_items, answer_given="", verdict="unverified"):
    """Append this query result to qa_history.json for audit trail and knowledge reinforcement."""
    history = load_qa_history()
    next_id = len(history["qa_history"]) + 1
    found = len(sources) + len(knowledge_items) > 0
    entry = {
        "id": next_id,
        "timestamp": utc_now(),
        "keyword": keyword,
        "sources_matched": [{"source_id": r[0], "path": r[4]} for r in sources],
        "knowledge_items_matched": [{"item_id": r[0], "title": r[1]} for r in knowledge_items],
        "answer_given": answer_given,
        "result": "found" if found else "not_found",
        "verdict": verdict
    }
    history["qa_history"].append(entry)
    save_qa_history(history)


def main():
    if len(sys.argv) < 2:
        print("Usage: python query_knowledge_index.py <keyword>")
        sys.exit(1)

    keyword = sys.argv[1]

    if not os.path.exists(DB_PATH):
        print(f"FATAL: Database not found at {DB_PATH}. Run init_archive_inventory.py first.")
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")

    try:
        # Step 0: check prior correct answers before querying
        prior = lookup_prior_correct_answers(keyword)
        if prior:
            print(f"\n=== Prior Correct Answer Found for '{keyword}' ===")
            for p in prior:
                print(f"  [id={p['id']}] {p['timestamp']}")
                print(f"    answer  : {p['answer_given']}")
                print(f"    sources : {p['sources_matched']}")
                print()
            print("RESULT: Prior correct answer available. Verify before re-querying.\n")

        sources = query_sources(conn, keyword)
        knowledge_items = query_knowledge_items(conn, keyword)
        print_results(keyword, sources, knowledge_items)
        record_query(keyword, sources, knowledge_items)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
