---
title: "FolderStructure.md"
description: "Generated folder tree intended for agent use and quick project navigation."
lastUpdated: "2026-03-18"
---

## Project Folder Structure

This file reflects the current repository layout and is safe for agents or humans to scan.

```text
Folder PATH listing for volume DATA
Volume serial number is 6E5A-D1EC
I:.
+---.vscode
|       Agent_SOP.md
|       agent_journal.md
|       agent_persona.md
|       agent_research.md
|       agent_skills.md
|       archive_inventory.db
|       archive_inventory_LEGACY_SCRIPT.py.bak
|       extensions.json
|       FolderStructure.md
|       Handoff_Prompt.md
|       Indexing_Schema.md
|       init_archive_inventory.py
|       memory.md
|       Naming_Conventions.md
|       README.md
|       README_DB_Init.md
|       reconcile_archive_inventory.py
|       schema.sql
|       seed_archive_inventory.py
|       settings.json
|       Source_of_Truth_Map.md
|       tasks.json
|       validate_archive_inventory.py
|       Writing-Styles.md
|
\---docs
    +---artifacts
    |       Design_Manual-CDA.md
    |       Utility_Franchise.md
    |
    +---debriefs
    +---intake
    +---manuals
    \---reports
        \---agent_reports
```

## Agent Parse Hints

- Root-level folders: `.vscode`, `docs`
- `.vscode` contains workspace config, control docs, and legacy/transitional helper scripts.
- `docs/manuals/` is the authoritative source for manuals.
- `docs/reports/agent_reports/` is the mandatory save location for all agent reports.

## JSON Model

```json
{
  "root": {
    ".vscode": {
      "Agent_SOP.md": "file",
      "agent_journal.md": "file",
      "agent_persona.md": "file",
      "agent_research.md": "file",
      "agent_skills.md": "file",
      "archive_inventory.db": "file",
      "archive_inventory_LEGACY_SCRIPT.py.bak": "file",
      "extensions.json": "file",
      "FolderStructure.md": "file",
      "Handoff_Prompt.md": "file",
      "Indexing_Schema.md": "file",
      "init_archive_inventory.py": "file",
      "memory.md": "file",
      "Naming_Conventions.md": "file",
      "README.md": "file",
      "README_DB_Init.md": "file",
      "reconcile_archive_inventory.py": "file",
      "schema.sql": "file",
      "seed_archive_inventory.py": "file",
      "settings.json": "file",
      "Source_of_Truth_Map.md": "file",
      "tasks.json": "file",
      "validate_archive_inventory.py": "file",
      "Writing-Styles.md": "file"
    },
    "docs": {
      "artifacts": {
        "Design_Manual-CDA.md": "file",
        "Utility_Franchise.md": "file"
      },
      "debriefs": {},
      "intake": {},
      "manuals": {},
      "reports": {
        "agent_reports": {}
      }
    }
  }
}
```