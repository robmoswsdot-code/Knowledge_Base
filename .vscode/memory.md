# Archive Process Memory

> **Boundary:** This file is the active operating memory. It contains current project state, current priorities, unresolved information gaps, and authoritative location pointers. It does not contain full artifact catalogs, append-only session history, or policy definitions. Overridden by `Agent_SOP.md`, `agent_persona.md`, and `agent_journal.md`.

---

## Current Status

* **Project State:** Civil Engineering decision-support setup.
* **Last Action:** Transitioned the workspace from archive-specific logic toward a technical second-brain workflow.

## Key Decisions

* **Primary purpose:** Technical reference and engineering judgment support.
* **Organization model:** Hybrid by discipline and topic.
* **Manual source:** `docs/manuals/` is the authoritative location for manuals.
* **Report location:** All agent reports must be saved to `docs/reports/agent_reports/`.

## Current Priorities

* Build a Civil Engineering-first knowledge structure.
* Replace archive-era assumptions with decision-support logic.
* Keep conclusions grounded in WSDOT, AASHTO, and supporting functional documents.

## Unresolved Information Gaps

* The long-term metadata and retrieval model is still transitional.
* Legacy SQLite tooling is not yet aligned to the Civil Engineering logic.
* Manual classification standards inside `docs/manuals/` are not yet fully defined.

## Authoritative Locations

* Manuals: `docs/manuals/`
* Supporting references: `docs/artifacts/`
* Intake material: `docs/intake/`
* Debrief notes: `docs/debriefs/`
* Agent reports: `docs/reports/agent_reports/`
* Control files: `.vscode/`