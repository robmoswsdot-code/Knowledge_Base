# Question Answering SOP

> **Boundary:** This file governs the step-by-step procedure the agent must follow when asked any question. It does not govern report generation, workflow execution, or file naming. Overridden by `Agent_SOP.md`.

---

## 1. Purpose

Define a deterministic, auditable question-answering procedure that enforces source-only retrieval and produces a traceable answer or an explicit unavailability statement.

---

## 2. Mandatory Retrieval Sequence

The agent must execute all steps in order before producing any answer.

### Step 0  Check Prior Correct Answers

Before any database query, run:

```
python .vscode/query_knowledge_index.py <keyword>
```

The script automatically checks `qa_history.json` for prior entries with `verdict=correct` on the same keyword.

* If a prior correct answer exists → use it as the starting answer; verify it is still source-consistent before presenting.
* If no prior correct answer exists → proceed to Step 1.

### Step 1  Identify Keywords

Extract 1–3 search keywords from the question. Record them explicitly before searching.

### Step 2  Query the Knowledge Index

Run:

```
python .vscode/query_knowledge_index.py <keyword>
```

Check results for:
- Matching `sources` entries
- Matching `knowledge_items` entries
- Matching `tags`

### Step 3  Search `docs/` Files

Search the following locations for keyword matches:

- `docs/manuals/`
- `docs/artifacts/`
- `docs/debriefs/`
- `docs/intake/`
- `docs/reports/agent_reports/`

### Step 4  Search `.vscode/` Control Files

Search the following for keyword matches:

- `memory.md`
- `agent_research.md`
- `agent_skills.md`
- `agent_files.yaml`

---

## 3. Answer Decision Rules

| Result | Action |
|--------|--------|
| Match found in database or `docs/` | Answer from that source; cite exact path |
| Match found in `.vscode/` control files | Answer from that source; cite exact path |
| No match in any location | State: "Information unavailable in repository. Source required: [describe what document type is needed]." |

**Never answer from general knowledge, external memory, or inference alone.**

---

## 4. Required Answer Format

Every answer must include:

- **Source:** exact file path(s) used
- **Finding:** the specific fact or statement drawn from the source
- **Confidence:** `confirmed` (direct source text) or `inferred` (derived from source context)
- **Gap (if any):** what additional source would resolve remaining unknowns

---

## 5. Query History and Knowledge Reinforcement

Every query — whether found or not found — is recorded in `.vscode/qa_history.json` automatically.

The agent must:

* Record `answer_given` for every response produced.
* Default `verdict` to `unverified` until the user or reviewer confirms the answer.
* Consult entries with `verdict=correct` on repeat questions to reinforce known answers.
* Never use entries with `verdict=incorrect` as a basis for a new answer.

---

## 6. Not-Found Protocol

When no source is found:

1. State explicitly: "Information unavailable in repository."
2. Identify what document type would answer the question.
3. Recommend the user add the document to `docs/intake/` for ingestion.
4. Do not speculate or supplement with external knowledge.

---

## 7. Forbidden Answering Behaviors

* Answering without running Step 2 and Step 3 first
* Using external knowledge when repository search returns no result
* Omitting source path citations
* Stating partial answers without identifying the gap
