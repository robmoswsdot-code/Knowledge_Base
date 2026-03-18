# README: Civil Engineering Knowledge Index Initialization

## Purpose

This package initializes and validates `archive_inventory.db`, the transitional SQLite knowledge index for this Civil Engineering second brain.

The schema conforms to `.vscode/Indexing_Schema.md` and uses the Civil Engineering v2 model rather than the legacy route-based archive model.

## Files

| File | Role |
|---|---|
| `schema.sql` | Canonical DDL for the Civil Engineering knowledge index |
| `init_archive_inventory.py` | Initializes the v2 schema and backs up legacy DBs |
| `validate_archive_inventory.py` | Validates schema structure and Civil Engineering path rules |
| `seed_archive_inventory.py` | Runs a non-destructive seed test against real repo files |
| `archive_inventory.db` | Active transitional knowledge index |

## Initialization Behavior

```powershell
cd I:\Wkng_Fldr_RobM\111 Knowledge_Base
python .vscode\init_archive_inventory.py
```

Behavior:

* if a legacy route-based database is detected, it is backed up to `.vscode/archive_inventory.legacy.<timestamp>.db.bak`
* a fresh Civil Engineering v2 database is created
* if a valid v2 database already exists, initialization is a no-op

## Validation

```powershell
cd I:\Wkng_Fldr_RobM\111 Knowledge_Base
python .vscode\validate_archive_inventory.py
```

Validation checks include:

* required v2 tables exist
* controlled vocabularies exist
* schema version 2 exists
* derived knowledge items link to non-derived sources
* discovery reports resolve under `docs/reports/agent_reports/`
* WSDOT and AASHTO sources resolve under `docs/manuals/`
* knowledge items have both discipline and topic tags

## Seed Test

```powershell
cd I:\Wkng_Fldr_RobM\111 Knowledge_Base
python .vscode\seed_archive_inventory.py
```

Notes:

* the seed test uses real files when available
* if `docs/manuals/` has no files yet, the manual portion is skipped
* the database transaction is rolled back after the test
* the seed script may create `docs/reports/agent_reports/seed_discovery_report.md` as a reusable placeholder report file