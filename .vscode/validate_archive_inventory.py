"""Validate the Civil Engineering knowledge index."""

import json
import os
import sqlite3
import sys
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(SCRIPT_DIR, "archive_inventory.db")
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))

EXPECTED_TABLES = {
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

EXPECTED_AUTHORITY_LEVELS = ["WSDOT", "AASHTO", "supporting", "derived"]
EXPECTED_SOURCE_KINDS = ["manual", "reference", "artifact", "note", "report"]
EXPECTED_RECORD_TYPES = [
    "manual",
    "manual_section_map",
    "manual_section_note",
    "reference_note",
    "precedent",
    "decision_driver",
    "discovery_report",
    "intake_item",
]
EXPECTED_RELATIONSHIP_TYPES = ["governs", "supports", "impacts", "distills_to", "reports_on"]
EXPECTED_TAG_TYPES = ["discipline", "topic", "decision_type"]


def utc_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def log(message):
    print(f"[{utc_now()}] {message}")


def check_result(name, passed, detail=""):
    status = "PASS" if passed else "FAIL"
    suffix = f" -- {detail}" if detail else ""
    log(f"  [{status}] {name}{suffix}")
    return passed


def fetch_single_column(conn, table, column):
    cur = conn.execute(f"SELECT {column} FROM {table}")
    return [row[0] for row in cur.fetchall()]


def rel_repo(path):
    return os.path.relpath(path, REPO_ROOT).replace("\\", "/")


class Validator:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None
        self.results = []

    def run(self):
        if not os.path.exists(self.db_path):
            log(f"FATAL: Database file not found: {self.db_path}")
            return 2

        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute("PRAGMA foreign_keys = ON")

        passed = True
        passed = self.check_tables() and passed
        passed = self.check_vocab() and passed
        passed = self.check_schema_version() and passed
        passed = self.check_derived_links() and passed
        passed = self.check_report_paths() and passed
        passed = self.check_manual_paths() and passed
        passed = self.check_tag_requirements() and passed

        self.record_result(passed)
        self.conn.close()
        log("OVERALL RESULT: PASS" if passed else "OVERALL RESULT: FAIL")
        return 0 if passed else 1

    def check_tables(self):
        log("Check: Required tables exist")
        cur = self.conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        actual = {row[0] for row in cur.fetchall()}
        ok = True
        for table in sorted(EXPECTED_TABLES):
            ok = check_result(f"Table '{table}'", table in actual) and ok
        return ok

    def check_vocab(self):
        log("Check: Controlled vocabularies")
        ok = True
        ok = check_result("authority_levels", set(fetch_single_column(self.conn, "authority_levels", "authority_level")) == set(EXPECTED_AUTHORITY_LEVELS)) and ok
        ok = check_result("source_kinds", set(fetch_single_column(self.conn, "source_kinds", "source_kind")) == set(EXPECTED_SOURCE_KINDS)) and ok
        ok = check_result("record_types", set(fetch_single_column(self.conn, "record_types", "record_type")) == set(EXPECTED_RECORD_TYPES)) and ok
        ok = check_result("relationship_types", set(fetch_single_column(self.conn, "relationship_types", "relationship_type")) == set(EXPECTED_RELATIONSHIP_TYPES)) and ok
        ok = check_result("tag_types", set(fetch_single_column(self.conn, "tag_types", "tag_type")) == set(EXPECTED_TAG_TYPES)) and ok
        return ok

    def check_schema_version(self):
        log("Check: Schema version")
        cur = self.conn.execute("SELECT COUNT(*) FROM schema_version WHERE version = 2")
        count = cur.fetchone()[0]
        return check_result("schema_version has v2 record", count >= 1, f"rows={count}")

    def check_derived_links(self):
        log("Check: Derived records link to non-derived sources")
        query = """
        SELECT ki.id, ki.title
        FROM knowledge_items ki
        LEFT JOIN knowledge_item_sources kis ON kis.knowledge_item_id = ki.id
        LEFT JOIN sources s ON s.id = kis.source_id
        WHERE ki.authority_level = 'derived'
        GROUP BY ki.id, ki.title
        HAVING SUM(CASE WHEN s.authority_level IS NOT NULL AND s.authority_level != 'derived' THEN 1 ELSE 0 END) = 0
        """
        rows = self.conn.execute(query).fetchall()
        return check_result("derived knowledge items have non-derived sources", len(rows) == 0, f"violations={len(rows)}")

    def check_report_paths(self):
        log("Check: Discovery report paths")
        query = """
        SELECT id, title, output_path
        FROM knowledge_items
        WHERE record_type = 'discovery_report'
          AND (output_path IS NULL OR output_path NOT LIKE 'docs/reports/agent_reports/%')
        """
        rows = self.conn.execute(query).fetchall()
        ok1 = check_result("knowledge_items discovery_report output_path", len(rows) == 0, f"violations={len(rows)}")
        query2 = "SELECT id, report_path FROM report_runs WHERE report_path NOT LIKE 'docs/reports/agent_reports/%'"
        rows2 = self.conn.execute(query2).fetchall()
        ok2 = check_result("report_runs report_path", len(rows2) == 0, f"violations={len(rows2)}")
        return ok1 and ok2

    def check_manual_paths(self):
        log("Check: Authoritative manual paths")
        query = """
        SELECT id, title, path
        FROM sources
        WHERE authority_level IN ('WSDOT', 'AASHTO')
          AND path NOT LIKE 'docs/manuals/%'
        """
        rows = self.conn.execute(query).fetchall()
        return check_result("WSDOT and AASHTO sources resolve under docs/manuals/", len(rows) == 0, f"violations={len(rows)}")

    def check_tag_requirements(self):
        log("Check: Knowledge item tag requirements")
        query = """
        SELECT ki.id, ki.title,
               SUM(CASE WHEN t.tag_type = 'discipline' THEN 1 ELSE 0 END) AS discipline_count,
               SUM(CASE WHEN t.tag_type = 'topic' THEN 1 ELSE 0 END) AS topic_count
        FROM knowledge_items ki
        LEFT JOIN knowledge_item_tags kit ON kit.knowledge_item_id = ki.id
        LEFT JOIN tags t ON t.id = kit.tag_id
        GROUP BY ki.id, ki.title
        HAVING discipline_count = 0 OR topic_count = 0
        """
        rows = self.conn.execute(query).fetchall()
        return check_result("knowledge items have discipline and topic tags", len(rows) == 0, f"violations={len(rows)}")

    def record_result(self, passed):
        detail = json.dumps({"passed": passed, "validator": "v2"})
        self.conn.execute(
            "INSERT INTO validation_results (run_at, passed, details) VALUES (?, ?, ?)",
            (utc_now(), 1 if passed else 0, detail),
        )
        self.conn.commit()


if __name__ == "__main__":
    sys.exit(Validator(DB_PATH).run())