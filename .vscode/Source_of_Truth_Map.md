# Source of Truth Map

> **Boundary:** This file is the authority routing map. It defines where authoritative information lives by record type. It does not contain naming rules, workflow steps, or narrative summaries. Overridden by `Agent_SOP.md`.

---

## Authority by Record Type

| Record Type | Authoritative Location | Format |
|---|---|---|
| WSDOT manuals | `docs/manuals/` | Manual files |
| AASHTO manuals | `docs/manuals/` | Manual files |
| Supporting functional documents | `docs/artifacts/` and other `docs/` subfolders | Mixed |
| Intake material pending classification | `docs/intake/` | Mixed |
| Debrief and review notes | `docs/debriefs/` | Mixed |
| Agent-generated reports | `docs/reports/agent_reports/` | Markdown |
| Agent control files | `.vscode/` | Markdown and JSON |
| Legacy inventory database | `.vscode/archive_inventory.db` | SQLite |

## Resolution Rule

When the same information appears in multiple locations, authority resolves in this order:

1. WSDOT manuals in `docs/manuals/`
2. AASHTO manuals in `docs/manuals/`
3. Supporting functional documents in `docs/`
4. Agent-generated distilled outputs that explicitly cite the governing sources

## Writing Standard Authority

The authoritative writing standard is `./.vscode/Writing-Styles.md`.

## Report Location Rule

All agent-generated reports must be saved to `docs/reports/agent_reports/`.