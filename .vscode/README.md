# `.vscode` Workspace Notes

This folder has two roles in this repository:

1. VS Code workspace configuration for editing this knowledge base
2. Repo-local control files and transitional Python/SQLite helpers used during migration

## Current workspace model

This repository is being converted into a Civil Engineering decision-support brain.

Hard rules:

- Governing manuals live in `docs/manuals/`
- All agent-generated reports must be saved to `docs/reports/agent_reports/`
- The current SQLite tooling is transitional and not yet the final Civil Engineering knowledge model

## What belongs here

- Workspace files: `settings.json`, `tasks.json`, `extensions.json`
- Control and guidance files: `Agent_SOP.md`, `Source_of_Truth_Map.md`, `FolderStructure.md`, related Markdown files
- Transitional database helpers: `schema.sql`, `init_archive_inventory.py`, `validate_archive_inventory.py`, `seed_archive_inventory.py`, `archive_inventory.db`