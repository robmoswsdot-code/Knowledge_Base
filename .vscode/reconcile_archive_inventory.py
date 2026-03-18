"""
reconcile_archive_inventory.py
Reconciliation script for archive_inventory.db vs docs/ file system.

Scans the docs/ tree, compares against every record in the database,
and reports:
  1. Unregistered files  — on disk but not in the database
  2. Orphaned records    — in the database but file missing from disk
  3. Hash mismatches     — file exists but content has changed
  4. Moved/renamed files — file missing at recorded path but hash found elsewhere

Does NOT modify the database. Read-only audit.

Conforms to: .vscode/Indexing_Schema.md, .vscode/schema.sql
Requires:    archive_inventory.db (initialized via init_archive_inventory.py)
Standard library only: sqlite3, os, sys, hashlib, datetime, json
"""

import sqlite3
import os
import sys
import hashlib
import datetime
import json

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(SCRIPT_DIR, "archive_inventory.db")
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
DOCS_DIR = os.path.join(REPO_ROOT, "docs")

# Files/patterns to exclude from reconciliation
EXCLUDE_NAMES = {
    "Thumbs.db",
    ".DS_Store",
    "desktop.ini",
}

EXCLUDE_PREFIXES = (
    "~$",   # Office temp files
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def sha256_of_file(path):
    """Return SHA-256 hex digest of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def repo_relative(abs_path):
    """Return repo-relative path with forward slashes."""
    return os.path.relpath(abs_path, REPO_ROOT).replace("\\", "/")


def scan_docs_directory():
    """Walk docs/ and return a dict of {repo_relative_path: abs_path}."""
    files = {}
    if not os.path.isdir(DOCS_DIR):
        return files
    for dirpath, _dirnames, filenames in os.walk(DOCS_DIR):
        for fname in filenames:
            if fname in EXCLUDE_NAMES:
                continue
            if any(fname.startswith(p) for p in EXCLUDE_PREFIXES):
                continue
            abs_path = os.path.join(dirpath, fname)
            rel_path = repo_relative(abs_path)
            files[rel_path] = abs_path
    return files


# ---------------------------------------------------------------------------
# Reconciliation
# ---------------------------------------------------------------------------

def reconcile():
    if not os.path.isfile(DB_PATH):
        print("FAIL  database not found at {}".format(DB_PATH))
        return False

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row

    # Load all document records
    db_rows = conn.execute(
        "SELECT id, route_id, site_name, source_location, file_hash, "
        "lifecycle_state, document_type FROM documents"
    ).fetchall()
    conn.close()

    # Build lookup structures
    db_by_path = {}      # source_location -> row
    db_hashes = {}       # file_hash -> [row, ...]  (for moved-file detection)
    for row in db_rows:
        db_by_path[row["source_location"]] = row
        h = row["file_hash"]
        if h:
            db_hashes.setdefault(h, []).append(row)

    # Scan file system
    disk_files = scan_docs_directory()

    # ----- Analysis -----
    unregistered = []     # on disk, not in DB
    orphaned = []         # in DB, not on disk
    hash_mismatches = []  # path matches, hash differs
    moved_files = []      # path missing, but hash found at another disk path
    verified = []         # path matches, hash matches

    # Check every file on disk against DB
    for rel_path, abs_path in sorted(disk_files.items()):
        if rel_path in db_by_path:
            row = db_by_path[rel_path]
            db_hash = row["file_hash"]
            if db_hash:
                disk_hash = sha256_of_file(abs_path)
                if disk_hash == db_hash:
                    verified.append(rel_path)
                else:
                    hash_mismatches.append({
                        "path": rel_path,
                        "db_id": row["id"],
                        "db_hash": db_hash[:16] + "...",
                        "disk_hash": disk_hash[:16] + "...",
                    })
            else:
                # No hash stored — can't verify integrity
                verified.append(rel_path)
        else:
            unregistered.append(rel_path)

    # Check every DB record against disk
    for src_loc, row in db_by_path.items():
        abs_path = os.path.join(REPO_ROOT, src_loc.replace("/", os.sep))
        if not os.path.isfile(abs_path):
            # File missing — check if it was moved (hash exists elsewhere)
            db_hash = row["file_hash"]
            found_at = None
            if db_hash:
                for disk_rel, disk_abs in disk_files.items():
                    if disk_rel == src_loc:
                        continue
                    if sha256_of_file(disk_abs) == db_hash:
                        found_at = disk_rel
                        break
            if found_at:
                moved_files.append({
                    "db_id": row["id"],
                    "db_path": src_loc,
                    "found_at": found_at,
                })
            else:
                orphaned.append({
                    "db_id": row["id"],
                    "db_path": src_loc,
                    "route_id": row["route_id"],
                })

    # ----- Report -----
    timestamp = datetime.datetime.now().isoformat()

    print("=" * 68)
    print("  ARCHIVE RECONCILIATION REPORT")
    print("  {}".format(timestamp))
    print("  Database: {}".format(DB_PATH))
    print("  Scan root: {}".format(DOCS_DIR))
    print("=" * 68)

    print("\n--- SUMMARY ---")
    print("  Files on disk:       {}".format(len(disk_files)))
    print("  Records in database: {}".format(len(db_rows)))
    print("  Verified (match):    {}".format(len(verified)))
    print("  Unregistered:        {}".format(len(unregistered)))
    print("  Orphaned records:    {}".format(len(orphaned)))
    print("  Hash mismatches:     {}".format(len(hash_mismatches)))
    print("  Moved/renamed:       {}".format(len(moved_files)))

    all_clean = True

    if unregistered:
        all_clean = False
        print("\n--- UNREGISTERED FILES (on disk, not in database) ---")
        for p in unregistered:
            print("  UNREG  {}".format(p))

    if orphaned:
        all_clean = False
        print("\n--- ORPHANED RECORDS (in database, not on disk) ---")
        for o in orphaned:
            print("  ORPHAN  id={} route={} path='{}'".format(
                o["db_id"], o["route_id"], o["db_path"]))

    if hash_mismatches:
        all_clean = False
        print("\n--- HASH MISMATCHES (file changed since ingestion) ---")
        for m in hash_mismatches:
            print("  MISMATCH  id={} path='{}'".format(m["db_id"], m["path"]))
            print("            db_hash={}  disk_hash={}".format(
                m["db_hash"], m["disk_hash"]))

    if moved_files:
        all_clean = False
        print("\n--- MOVED/RENAMED FILES (hash found at different path) ---")
        for mv in moved_files:
            print("  MOVED  id={} db_path='{}'".format(mv["db_id"], mv["db_path"]))
            print("         found_at='{}'".format(mv["found_at"]))

    if all_clean and len(db_rows) > 0:
        print("\n  STATUS: ALL RECORDS RECONCILED")
    elif len(db_rows) == 0:
        print("\n  STATUS: DATABASE EMPTY — no records to reconcile")
        print("  All {} files on disk are UNREGISTERED".format(len(unregistered)))
    else:
        print("\n  STATUS: DISCREPANCIES FOUND — review required")

    print("=" * 68)

    return all_clean


if __name__ == "__main__":
    ok = reconcile()
    sys.exit(0 if ok else 1)
