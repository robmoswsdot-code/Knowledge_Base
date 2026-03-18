# Agent Skills: Capability Register

> **Boundary:** This file is the capability register. It defines authorized agent skills with trigger conditions, inputs, outputs, and validation checks. It does not contain project-state notes, role identity text, or session history. Overridden by `Agent_SOP.md` and `agent_persona.md`.

---

## Skill 1: Governing Source Identification

* **Purpose:** Identify the controlling WSDOT or AASHTO source for a question.
* **Trigger:** When a user asks what governs a technical issue or decision path.
* **Inputs:** Manuals in `docs/manuals/`, supporting references in `docs/`.
* **Outputs:** Governing-source summary with citations and authority ranking.
* **Validation:** Output must identify both the governing source and any missing source coverage.

## Skill 2: Discipline Impact Scan

* **Purpose:** Determine which subject matter experts or disciplines are likely implicated by a question.
* **Trigger:** When a decision crosses functional boundaries or needs coordination.
* **Inputs:** Governing sources, supporting references, known decision context.
* **Outputs:** Discipline list with issue framing and likely concerns.
* **Validation:** Each discipline callout must be tied to a documented constraint, requirement, or precedent.

## Skill 3: Discovery Report Generation

* **Purpose:** Produce a narrated discovery report for a technical issue.
* **Trigger:** When the user requests an analysis, litmus test, or decision-support report.
* **Inputs:** Source documents, distilled knowledge, decision context.
* **Outputs:** A report saved to `docs/reports/agent_reports/`.
* **Validation:** Report must separate facts, interpretation, unknowns, and next steps.

## Skill 4: Transitional Knowledge Inventory

* **Purpose:** Track and classify repository content during migration from the copied archive logic.
* **Trigger:** When new manuals or supporting references are added.
* **Inputs:** Files under `docs/` and metadata intent from `Indexing_Schema.md`.
* **Outputs:** Working inventory notes or legacy database updates when useful.
* **Validation:** Inventory actions must not override the authority order or the new control-layer rules.