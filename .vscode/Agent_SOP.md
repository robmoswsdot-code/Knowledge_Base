# Agent_SOP.md  Master Execution Law

> **Boundary:** This file governs startup sequence, workflow rules, validation gates, forbidden actions, output requirements, and precedence rules. It does not govern role identity (see `agent_persona.md`), writing quality details (see `Writing-Styles.md`), file naming (see `Naming_Conventions.md`), metadata intent (see `Indexing_Schema.md`), or authority routing (see `Source_of_Truth_Map.md`). This file takes precedence over all other control-layer files.

---

## 1. Purpose

This repository is a Civil Engineering decision-support brain.

Objective: support technically grounded project-manager judgment by organizing manuals, discipline knowledge, distilled references, and discovery-style reports.

In scope:

* Technical reference retrieval
* Cross-discipline issue framing
* Constraint identification
* Decision-path evaluation
* Next-step discovery reporting

Out of scope:

* Project delivery execution system behavior
* Document control system-of-record workflows
* Schedule, budget, or deliverable management as a separate toolset

---

## 2. Precedence Model

If control-layer files overlap, authority resolves in this order:

1. `Agent_SOP.md`
2. `agent_persona.md`
3. `agent_journal.md`
4. `memory.md`
5. `Source_of_Truth_Map.md`
6. `agent_research.md`
7. `Indexing_Schema.md`
8. `Naming_Conventions.md`
9. `FolderStructure.md`
10. `agent_skills.md`
11. `Writing-Styles.md`
12. `Question_Answering_SOP.md`
13. `qa_history.json` as append-only answer audit trail
14. `archive_inventory.db` and `schema.sql` as legacy implementation artifacts until replaced

---

## 3. Machine-Readable Control

```json
{
  "startup": {
    "requiredFiles": [
      "agent_persona.md",
      "agent_journal.md",
      "memory.md",
      "agent_skills.md",
      "agent_research.md",
      "Writing-Styles.md",
      "FolderStructure.md",
      "Source_of_Truth_Map.md",
      "Indexing_Schema.md",
      "Naming_Conventions.md",
      "agent_files.yaml"
    ],
    "stateChecks": {
      "repositoryPurpose": "civil-engineering-decision-support",
      "manualsSource": "docs/manuals/",
      "agentReportsLocation": "docs/reports/agent_reports/"
    }
  },
  "reportRequirement": {
    "outputType": "discovery-report",
    "mustSaveTo": "docs/reports/agent_reports/"
  },
  "questionAnsweringRule": {
    "allowedSources": ["docs/", ".vscode/"],
    "externalSourcesAllowed": false,
    "mustCiteSourcePaths": true,
    "ifNotFound": "state-unavailable-in-repository"
  },
  "qualityGate": {
    "mustBe": [
      "source-grounded",
      "no-fabrication",
      "constraints-explicit",
      "unknowns-explicit",
      "discipline-impacts-identified",
      "report-location-compliant",
      "source-paths-cited",
      "no-external-sources"
    ]
  }
}
```

---

## 4. Mandatory Startup Sequence

On initialization, the agent must execute in this order:

### Step 1  Load Core Context

Read and verify the following files (explicitly document completion in the journal):

- [ ] `agent_persona.md` (role/behavior constraints)
- [ ] `agent_journal.md` (workflow logging)
- [ ] `memory.md` (user/repo memory state)
- [ ] `agent_skills.md` (available domains and capability rules)
- [ ] `agent_research.md` (source mapping)
- [ ] `Writing-Styles.md` (output quality and style rules)
- [ ] `FolderStructure.md` (repo organization policy)
- [ ] `Source_of_Truth_Map.md` (authority routing)
- [ ] `Indexing_Schema.md` (metadata schema)
- [ ] `Naming_Conventions.md` (artifact naming rules)
- [ ] `agent_files.yaml` (machine-readable agent file manifest)

### Step 2  Validate Operating State

Confirm:

* Repository purpose = Civil Engineering decision support
* Manuals source = `docs/manuals/`
* Agent report destination = `docs/reports/agent_reports/`

### Step 3  Journal Enforcement

Before substantive work:

* Create or update a task entry in `agent_journal.md`.
* Define: objective, inputs, expected output, governing references.

Failure to comply = invalid execution.

---

## 5. Core Operating Rules

### 5.1 Evidence-Only Execution

All outputs must be grounded in traceable source material.

Authority order:

1. Washington State Department of Transportation manuals stored under `docs/manuals/`
2. AASHTO manuals stored under `docs/manuals/`
3. Supporting functional documents stored elsewhere in `docs/`
4. Agent-generated distilled notes only when traceable to one of the above

No fabricated facts. No unsupported technical claims.

### 5.2 Report Destination Rule

All agent-generated reports must be saved to:

`docs/reports/agent_reports/`

Saving agent reports outside that folder is non-compliant unless a later rule explicitly overrides this requirement.

### 5.3 Writing Standard

All outputs must comply with `Writing-Styles.md`.

### 5.4 Language Constraints

All outputs must comply with the behavioral limits defined in `agent_persona.md`.

### 5.5 Distinguish Facts from Interpretation

Every report must clearly separate:

* Source-backed facts
* Derived interpretation
* Open questions
* Missing inputs

### 5.6 Large Manual Rule

A source is treated as a **large manual** if it meets one or more of the following:

* more than 100 pages
* more than 10 MB file size
* spans multiple distinct decision domains or discipline-relevant sections
* is expected to be cited repeatedly across different questions

Workflow requirements for large manuals:

* register the full file in `docs/manuals/` as the authoritative source
* create a companion section map for retrieval and navigation
* create section-level distilled notes when a section is repeatedly used or decision-critical
* cite section-level references in reports whenever practical instead of broad whole-manual generalizations

### 5.7 Legacy Inventory Tooling

`archive_inventory.db`, `schema.sql`, and related Python scripts are legacy implementation assets from the copied workspace package.

Rules:

* They may be used for local inventory support during transition.
* They are not yet the authoritative Civil Engineering knowledge model.
* No decision should rely on route-based legacy logic when the control-layer intent conflicts with it.

### 5.8 Question Answering Rule

When the agent is asked a question, it must follow the full procedure defined in `Question_Answering_SOP.md`.

Summary:

* Run `query_knowledge_index.py <keyword>` against `archive_inventory.db` first.
* Search `docs/` and `.vscode/` control files for keyword matches.
* Answer only from sources found in those locations; cite exact paths.
* If no match is found, state explicitly that the information is unavailable and identify what document type is needed.
* Do not use external sources, internet knowledge, or unsourced memory.
* Every query result (found or not found) is automatically logged to `qa_history.json`.

### 5.9 Acronym Index Maintenance Rule

To keep acronym interpretation consistent across agents and reports:

* To rebuild after adding new docs: `python .vscode/build_acronym_index.py`
* To add a new known acronym: extend `SEED_EXPANSIONS` in the script.
* Treat `.vscode/Acronym_Index.md` as the working acronym reference for report writing and review.

---

## 6. Required Workflow Pattern

Every substantive task must follow:

### Step 1  Define Task

Write in the journal: task description, inputs, expected output, governing references.

### Step 2  Gather Sources

Identify the governing manuals first in `docs/manuals/`, then supporting references elsewhere in `docs/`.

If a governing source is a large manual, use its section map and section-level notes when available before relying on whole-manual framing.

### Step 3  Analyze by Discipline and Topic

For each task, identify:

* relevant disciplines or subject matter experts
* governing topics or decision drivers
* constraints, dependencies, and unknowns

### Step 4  Produce Discovery Report

The default output is a discovery-style report that includes:

* decision context
* governing sources
* discipline considerations
* constraints and risks
* viable paths
* unknowns and missing inputs
* recommended next steps
* confidence notes

### Step 5  Save and Log

* Save the report to `docs/reports/agent_reports/`
* Append the action to `agent_journal.md`
* If new source documents were added or acronym usage changed, rebuild the acronym index using: `python .vscode/build_acronym_index.py`

---

## 7. Knowledge Containers

The repository is organized around these working containers:

* `docs/manuals/` for governing manuals
* companion section maps and section-level notes for large manuals
* `docs/artifacts/` for supporting reference documents
* `docs/intake/` for unclassified incoming material
* `docs/debriefs/` for review or retrospective notes
* `docs/reports/agent_reports/` for agent-generated reports

Hybrid organization requirement:

* folder structure supports navigation
* metadata must support both discipline and topic

---

## 8. Forbidden Actions

The agent must not:

* invent technical facts
* treat unsupported memory as authoritative
* save agent reports outside `docs/reports/agent_reports/`
* confuse project delivery execution with technical decision support
* overwrite the append-only journal without explicit instruction
* answer questions using external sources outside `docs/` and `.vscode/`
* omit source path citations from any answer or report claim

---

## 9. Quality Control Gate

Before any report is accepted:

* [ ] Governing references are identified
* [ ] Source hierarchy is respected
* [ ] Relevant disciplines are identified
* [ ] Constraints and unknowns are explicit
* [ ] The report reads as a discovery, not a fabricated conclusion
* [ ] The output is saved to `docs/reports/agent_reports/`
* [ ] All claims cite exact source paths from `docs/` or `.vscode/`
* [ ] No external or unsourced content used in answering
* [ ] Acronym index is rebuilt after new document ingestion when needed
* [ ] New known acronyms are added to `SEED_EXPANSIONS` before final submission
