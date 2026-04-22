# Indexing Schema

> **Boundary:** This file defines the intended metadata model for the Civil Engineering knowledge system. It contains required fields, allowed values, relationship logic, and validation intent. It does not contain project narrative, role instructions, or session logs. Overridden by `Agent_SOP.md`.

---

## Status

This is the target metadata direction for the Civil Engineering second-brain MVP.

The current SQLite implementation in `.vscode/archive_inventory.db` is legacy and not yet fully aligned to this model.

## Core Record Types

* `manual`
* `manual_section_map`
* `manual_section_note`
* `reference_note`
* `precedent`
* `decision_driver`
* `discovery_report`
* `intake_item`

## Required Fields per Record

| Field | Type | Required | Description |
|---|---|---|---|
| title | text | yes | Human-readable record title |
| record_type | text | yes | One of the approved core record types |
| parent_source_id | integer | conditional | Required for section maps and section-level notes derived from a manual |
| authority_level | text | yes | One of: WSDOT, AASHTO, supporting, derived |
| discipline_tags | list | yes | One or more relevant Civil Engineering disciplines |
| topic_tags | list | yes | One or more issue, topic, or decision-driver tags |
| source_location | text | yes | Repository-relative file path |
| summary | text | conditional | Short grounded summary for distilled records |
| related_sources | list | no | Related source records or files |
| confidence_basis | text | conditional | Why the interpretation is strong, weak, or incomplete |
| last_reviewed | date | no | Format: YYYY-MM-DD |

## Authority Levels

| Level | Definition |
|---|---|
| WSDOT | Washington State Department of Transportation governing manual or standard |
| AASHTO | AASHTO governing manual or standard |
| supporting | Supporting functional document, reference, or precedent |
| derived | Agent-generated note or report tied to source records |

## Large Manual Rule

A source is classified as a **large manual** if it meets one or more of the following:

* more than 100 pages
* more than 10 MB file size
* spans multiple distinct decision domains or discipline-relevant sections
* is likely to be cited repeatedly across different questions

Large-manual handling requirements:

* the full manual remains the authoritative source file under `docs/manuals/`
* a `manual_section_map` record should be created to represent the manual retrieval structure
* `manual_section_note` records should be created for high-value or repeatedly cited sections
* derived section notes must remain traceable to the parent manual

## Relationship Types

* `governs`: source controls a topic or decision
* `supports`: source adds technical support or background
* `impacts`: source affects a discipline or decision driver
* `distills_to`: source is summarized into a derived note
* `reports_on`: report analyzes a source set or decision context

## Validation Intent

* Every derived record must link back to at least one non-derived source.
* Every `manual_section_map` or `manual_section_note` must link back to its parent manual.
* Every discovery report must cite its governing sources.
* Every record must carry both discipline and topic context.
* Agent reports must resolve to `docs/reports/agent_reports/`.
* Manuals should resolve to `docs/manuals/` when they are authoritative.