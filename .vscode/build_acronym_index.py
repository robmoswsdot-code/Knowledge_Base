"""
build_acronym_index.py
Scans .vscode/*.md and docs/**/*.md for acronyms and their expansions.
Outputs .vscode/Acronym_Index.md — append-mode: new entries are added,
existing entries are left unmodified so manual edits are preserved.

Run:
    python .vscode/build_acronym_index.py

Output:
    .vscode/Acronym_Index.md
"""

import re
import os
import sys
from pathlib import Path
from collections import defaultdict

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent  # repo root
SEARCH_DIRS = [
    ROOT / ".vscode",
    ROOT / "docs",
]
EXTENSIONS = {".md"}
OUTPUT_FILE = ROOT / ".vscode" / "Acronym_Index.md"

# Minimum / maximum uppercase letters to qualify as an acronym
ACRONYM_MIN = 2
ACRONYM_MAX = 8

# Regex: an all-caps token (letters only, optionally with digits after first letter)
# e.g. WSDOT, AASHTO, RFP, NHS, DBB, DB, PS&E handled separately
ACRONYM_RE = re.compile(r"\b([A-Z][A-Z0-9&]{1,7})\b")

# Regex: expansion pattern — "Full Phrase (ACRONYM)" or "ACRONYM (Full Phrase)"
# Captures both conventions used in WSDOT documents
PAREN_EXPAND_RE = re.compile(
    r"([A-Za-z][A-Za-z0-9 \-/&,]{3,80}?)\s+\(([A-Z][A-Z0-9&]{1,7})\)"
    r"|"
    r"\b([A-Z][A-Z0-9&]{1,7})\s+\(([A-Za-z][A-Za-z0-9 \-/&,]{3,80}?)\)"
)

# Known stop-words: single common words that look like acronyms but aren't
STOPWORDS = {
    "I", "A", "AN", "AS", "AT", "BE", "BY", "DO", "GO", "IF", "IN",
    "IS", "IT", "ME", "MY", "NO", "OF", "OK", "ON", "OR", "SO", "TO",
    "UP", "US", "WE", "AM", "PM", "III", "II", "IV", "VI", "VII",
    "AND", "FOR", "NOT", "THE", "ARE", "BUT", "CAN", "DID", "GET",
    "GOT", "HAD", "HAS", "HIM", "HIS", "HOW", "ITS", "LET", "OUT",
    "PUT", "RAN", "RUN", "SAY", "SEE", "SET", "SHE", "SIT", "SIX",
    "TEN", "TWO", "USE", "VIA", "WAS", "WAY", "WHO", "WHY", "YET",
    "YOU", "ALL", "ANY", "OUR", "OWN", "OFF", "OLD", "NEW", "ONE",
    "TOO", "YES", "III", "PDF", "URL", "HTTP", "HTTPS", "SHA",
    "MD", "YML", "YAML", "JSON", "SQL", "SOP",  # file extensions / generic
    # Common English words and file/folder name fragments that appear capitalized
    "DATA", "PATH", "PASS", "FAIL", "DONE", "README", "NULL", "TRUE", "FALSE",
    "NONE", "TYPE", "NAME", "NOTE", "DATE", "TIME", "LIST", "FILE", "ITEM",
    "MB", "KB", "GB", "MM", "DD", "HH", "SS", "UTC", "EST", "PST",
    "MVP", "DDL", "DML",  # overly generic tech abbreviations
    # Date/version format tokens
    "YYYY", "MM", "DD", "HH",
    # State Route number prefixes (SR + digits handled separately)
    "SR164", "SR410", "SR92",
    # VS Code / software context
    "VS",
}

# Seed dictionary: well-known acronyms whose expansions may not appear
# parenthetically in the source docs. Parenthetical extraction takes priority;
# seed is the fallback.
SEED_EXPANSIONS = {
    "AASHTO":  "American Association of State Highway and Transportation Officials",
    "ASDE":    "Assistant State Design Engineer",
    "ATC":     "Alternative Technical Concept",
    "BOD":     "Basis of Design",
    "CADD":    "Computer Aided Design and Drafting",
    "CATS":    "Construction Audit Tracking System",
    "CDA":     "Conceptual Design Approval",
    "DBB":     "Design-Bid-Build",
    "DB":      "Design-Build",
    "DDP":     "Design Documentation Package",
    "ESA":     "Endangered Species Act",
    "EPS":     "Environmental Permit Specialist",
    "FHWA":    "Federal Highway Administration",
    "HQ":      "Headquarters",
    "LP":      "Local Programs",
    "M3126":   "WSDOT Standard Plan M 31-26 (Guard Rail)",
    "NCI":     "Non-Compliance Issue",
    "NCR":     "Non-Conformance Report",
    "NEPA":    "National Environmental Policy Act",
    "NHS":     "National Highway System",
    "PDA":     "Project Design Approval",
    "PDMSG":   "Project Delivery Method Selection Guidance",
    "PE":      "Professional Engineer",
    "PS&E":    "Plans, Specifications, and Estimate",
    "QMP":     "Quality Management Plan",
    "RCW":     "Revised Code of Washington",
    "RES":     "Right-of-Entry Specialist",
    "RFC":     "Release for Construction",
    "RFP":     "Request for Proposal",
    "RFQ":     "Request for Qualifications",
    "ROW":     "Right of Way",
    "SEPA":    "State Environmental Policy Act",
    "TMP":     "Transportation Management Plan",
    "WAC":     "Washington Administrative Code",
    "WSDOT":   "Washington State Department of Transportation",
    "AI":      "Artificial Intelligence",
    "D1EC":    "District 1 Environmental Coordinator",
    "SR":      "State Route",
    "USDOT":   "U.S. Department of Transportation",
    "WDFW":    "Washington Department of Fish and Wildlife",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def collect_files(search_dirs, extensions):
    files = []
    for d in search_dirs:
        if not d.exists():
            continue
        for path in d.rglob("*"):
            if path.suffix.lower() in extensions and path.is_file():
                # Skip the output file itself to avoid circular reads
                if path.resolve() == OUTPUT_FILE.resolve():
                    continue
                files.append(path)
    return sorted(files)


def extract_expansions(text):
    """Return dict {ACRONYM: expansion_string} found via parenthetical patterns."""
    found = {}
    for m in PAREN_EXPAND_RE.finditer(text):
        if m.group(1) and m.group(2):
            # "Full Phrase (ACRONYM)"
            acronym = m.group(2).strip()
            expansion = m.group(1).strip()
        else:
            # "ACRONYM (Full Phrase)"
            acronym = m.group(3).strip()
            expansion = m.group(4).strip()
        if len(acronym) >= ACRONYM_MIN and acronym not in STOPWORDS:
            # Prefer shorter, cleaner expansions when multiple are found
            if acronym not in found or len(expansion) < len(found[acronym]):
                found[acronym] = expansion
    return found


def extract_all_acronyms(text):
    """Return set of all uppercase tokens that look like acronyms."""
    tokens = set()
    for m in ACRONYM_RE.finditer(text):
        token = m.group(1)
        if len(token) >= ACRONYM_MIN and token not in STOPWORDS:
            tokens.add(token)
    return tokens


def first_seen_context(text, acronym, window=120):
    """
    Return a short snippet of text surrounding the first occurrence of the acronym
    to give a usage example (helps manual reviewers verify entries).
    """
    idx = text.find(acronym)
    if idx == -1:
        return ""
    start = max(0, idx - 40)
    end = min(len(text), idx + window)
    snippet = text[start:end].replace("\n", " ").strip()
    return f"…{snippet}…"


# ---------------------------------------------------------------------------
# Load existing index so we don't overwrite manual edits
# ---------------------------------------------------------------------------

def load_existing_index(path):
    """Return dict {ACRONYM: (expansion, source_note)} from existing index file."""
    existing = {}
    if not path.exists():
        return existing
    current_acronym = None
    with open(path, encoding="utf-8") as f:
        for line in f:
            # Match table rows: | ACRONYM | expansion | ... |
            m = re.match(r"\|\s*`?([A-Z][A-Z0-9&]{1,7})`?\s*\|([^|]+)\|", line)
            if m:
                acronym = m.group(1).strip()
                expansion = m.group(2).strip()
                if acronym and acronym not in STOPWORDS:
                    existing[acronym] = expansion
    return existing


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    files = collect_files(SEARCH_DIRS, EXTENSIONS)
    if not files:
        print("No markdown files found in search paths.")
        sys.exit(1)

    print(f"Scanning {len(files)} file(s)...")

    all_expansions = {}        # acronym -> best expansion string found
    acronym_sources = defaultdict(set)   # acronym -> set of relative file paths
    acronym_contexts = {}      # acronym -> first context snippet

    for fpath in files:
        try:
            text = fpath.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            print(f"  WARNING: could not read {fpath}: {e}")
            continue

        rel = fpath.relative_to(ROOT).as_posix()

        # Extract parenthetical expansions first (highest confidence)
        expansions = extract_expansions(text)
        for acr, exp in expansions.items():
            if acr not in all_expansions:
                all_expansions[acr] = exp
            acronym_sources[acr].add(rel)

        # Extract all acronym tokens (may not have explicit expansions)
        tokens = extract_all_acronyms(text)
        for acr in tokens:
            acronym_sources[acr].add(rel)
            if acr not in acronym_contexts:
                ctx = first_seen_context(text, acr)
                if ctx:
                    acronym_contexts[acr] = (ctx, rel)

    # Load existing index to preserve manual edits
    existing = load_existing_index(OUTPUT_FILE)

    # Merge: new entries added, existing entries preserved
    all_acronyms = sorted(set(list(all_expansions.keys()) + list(acronym_sources.keys())))

    # Filter: only keep acronyms with at least 2 characters after filtering stopwords
    all_acronyms = [a for a in all_acronyms if len(a) >= ACRONYM_MIN and a not in STOPWORDS]

    # Build final table rows
    rows = []
    new_count = 0
    for acr in all_acronyms:
        if acr in existing and "not found" not in existing[acr]:
            # Preserve existing row only if it has a real expansion (not the placeholder)
            expansion = existing[acr]
            status = "existing"
        else:
            # Seed takes priority (authoritative, clean); fall back to parenthetical extraction
            expansion = (
                SEED_EXPANSIONS.get(acr)
                or all_expansions.get(acr)
                or "_[expansion not found — review required]_"
            )
            status = "new"
            new_count += 1

        sources = ", ".join(sorted(acronym_sources.get(acr, set())))
        rows.append((acr, expansion, sources, status))
    # ---------------------------------------------------------------------------
    # Write output
    # ---------------------------------------------------------------------------

    header = """\
# Acronym Index
> **Boundary:** This file is the authoritative acronym reference for this repository.
> All agents must consult this file when interpreting or writing acronyms in reports and analyses.
> Expansions marked `[expansion not found — review required]` need manual completion.
> Do not abbreviate terms in outputs without a matching entry here.
> Governed by `Agent_SOP.md`. Updated by `build_acronym_index.py`.

---

## How to Use

1. Before writing a report, verify each acronym used is listed here.
2. On first use of an acronym in any report, write the full expansion followed by the acronym in parentheses.
3. If an acronym is ambiguous (multiple expansions), cite the source that governs the context.
4. To add an acronym: add a row and run `build_acronym_index.py` to merge.

---

## Acronym Table

| Acronym | Expansion | Source File(s) | Status |
|---------|-----------|----------------|--------|
"""

    existing_count = len(existing)
    total_count = len(rows)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(header)
        for acr, expansion, sources, status in rows:
            # Truncate very long source lists for readability
            if len(sources) > 120:
                sources = sources[:117] + "..."
            f.write(f"| `{acr}` | {expansion} | {sources} | {status} |\n")

        import datetime as _dt
        f.write(f"""
---

## Build Statistics

- **Last run:** {_dt.datetime.now().strftime('%Y-%m-%d %H:%M')}
- **Files scanned:** {len(files)}
- **Total acronyms indexed:** {total_count}
- **New entries this run:** {new_count}
- **Preserved existing entries:** {existing_count}
- **Search paths:** {', '.join(str(d.relative_to(ROOT)) for d in SEARCH_DIRS if d.exists())}
""")

    print(f"\nDone.")
    print(f"  Total acronyms indexed : {total_count}")
    print(f"  New entries this run   : {new_count}")
    print(f"  Preserved existing     : {existing_count}")
    print(f"  Output                 : {OUTPUT_FILE.relative_to(ROOT)}")

    if new_count > 0:
        needs_review = [r for r in rows if "not found" in r[1]]
        if needs_review:
            print(f"\n  {len(needs_review)} entries need manual expansion review:")
            for acr, exp, src, _ in needs_review[:20]:
                print(f"    {acr:12s}  (seen in: {src[:60]})")
            if len(needs_review) > 20:
                print(f"    ...and {len(needs_review) - 20} more.")


if __name__ == "__main__":
    main()
