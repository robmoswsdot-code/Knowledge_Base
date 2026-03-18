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
12. `archive_inventory.db` and `schema.sql` as legacy implementation artifacts until replaced

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
      "Naming_Conventions.md"
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
  "qualityGate": {
    "mustBe": [
      "source-grounded",
      "no-fabrication",
      "constraints-explicit",
      "unknowns-explicit",
      "discipline-impacts-identified",
      "report-location-compliant"
    ]
  }
}
```

---

## 4. Mandatory Startup Sequence

On initialization, the agent must execute in this order:

### Step 1  Load Core Context

Read the following files:

1. `agent_persona.md`
2. `agent_journal.md`
3. `memory.md`
4. `agent_skills.md`
5. `agent_research.md`
6. `Writing-Styles.md`
7. `FolderStructure.md`
8. `Source_of_Truth_Map.md`
9. `Indexing_Schema.md`
10. `Naming_Conventions.md`

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

### 5.6 Legacy Inventory Tooling

`archive_inventory.db`, `schema.sql`, and related Python scripts are legacy implementation assets from the copied workspace package.

Rules:

* They may be used for local inventory support during transition.
* They are not yet the authoritative Civil Engineering knowledge model.
* No decision should rely on route-based legacy logic when the control-layer intent conflicts with it.

---

## 6. Required Workflow Pattern

Every substantive task must follow:

### Step 1  Define Task

Write in the journal: task description, inputs, expected output, governing references.

### Step 2  Gather Sources

Identify the governing manuals first in `docs/manuals/`, then supporting references elsewhere in `docs/`.

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

---

## 7. Knowledge Containers

The repository is organized around these working containers:

* `docs/manuals/` for governing manuals
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

---

## 9. Quality Control Gate

Before any report is accepted:

* [ ] Governing references are identified
* [ ] Source hierarchy is respected
* [ ] Relevant disciplines are identified
* [ ] Constraints and unknowns are explicit
* [ ] The report reads as a discovery, not a fabricated conclusion
* [ ] The output is saved to `docs/reports/agent_reports/`