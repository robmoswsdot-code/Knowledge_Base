# Knowledge_Base Constitution

> A Civil Engineering second brain for design reference and technical knowledge. It exists to help a project manager make grounded decisions, frame next steps, and produce discovery-style reports based on authoritative manuals and supporting documents rather than unsupported opinion.

---

## Context Detection

**Ralph Loop Mode** (started by ralph-loop*.sh):
- Pick highest priority incomplete spec from specs/
- Implement, validate, and document changes
- Output <promise>DONE</promise> only when 100% complete
- Output <promise>ALL_DONE</promise> when no work remains

**Interactive Mode** (normal conversation):
- Be helpful, guide decisions, create specs
- Keep recommendations grounded in the repo's control layer and source material

---

## Core Principles

- Source-grounded over opinion: prefer WSDOT manuals first, AASHTO second, supporting functional documents third.
- Traceability matters: every derived note or report must point back to source material.
- Decision-support, not project delivery: this repo supports technical judgment and discovery reporting, not execution tracking or document control.
- Keep the system practical: favor lightweight structures that improve retrieval and reuse.

---

## Technical Stack

- Markdown-first knowledge base
- Python helper scripts in .vscode/
- SQLite knowledge index in .vscode/archive_inventory.db
- Local manuals under docs/manuals/
- Agent reports under docs/reports/agent_reports/

---

## Autonomy

YOLO Mode: ENABLED
Git Autonomy: DISABLED

---

## Specs

Specs live in specs/ as markdown files. Pick the highest priority incomplete spec (lower number = higher priority). A spec is incomplete if it lacks ## Status: COMPLETE.

Spec template: https://raw.githubusercontent.com/github/spec-kit/refs/heads/main/templates/spec-template.md

When all specs are complete, re-verify a random one before signaling done.

---

## NR_OF_TRIES

Track attempts per spec via <!-- NR_OF_TRIES: N --> at the bottom of the spec file. Increment each attempt. At 10+, the spec is too hard and should be split into smaller specs.

---

## History

Append a 1-line summary to history.md after each spec completion. For details, create history/YYYY-MM-DD--spec-name.md with lessons learned, decisions made, and issues encountered. Check history before starting work on any spec.

---

## Completion Signal

All acceptance criteria verified, relevant validations pass, and changes are ready for review -> output <promise>DONE</promise>. Never output this until truly complete.

---

## Ralph Source

Installed from standhartinger/ralph-wiggum commit $commit.