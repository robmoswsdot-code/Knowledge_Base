# Naming Conventions

> **Boundary:** This file defines file naming control rules. It contains naming syntax, date format, version format, route and site naming rules, and prohibited naming patterns. It does not contain schema logic, source-of-truth rules, or workflow instructions. Overridden by `Agent_SOP.md`.

---

## Date Format

* Standard: `YYYY-MM-DD`
* Example: `2026-03-17`
* Use in filenames when date is relevant.

## Version Format

* Suffix: `_R{n}` where `{n}` is the revision number.
* Example: `Comanager Project Report_R3.docx`
* First version has no suffix. Subsequent revisions use `_R2`, `_R3`, etc.

## Route Naming

* Format in filenames: `SR{number}` (no space between SR and route number).
* Example: `SR92`, `SR164`, `SR410`
* In body text: `State Route 92` (full form, per language constraints).

## Site Naming

* Format: Title case, matching the Washington Department of Fish and Wildlife report name.
* Example: `Lundeen`, `Munson Creek`, `Ebey Slough`, `Boise Creek`

## Washington Department of Fish and Wildlife Report Files

* Pattern: `WDFW SR{route} {site_name} {report_id}_Report.pdf`
* Example: `WDFW SR92 Lundeen 991827_Report.pdf`

## General Project Files

* Use descriptive names with spaces.
* Example: `Comanager Project Report.docx`, `Schedule extension request.docx`

## Prohibited Patterns

* No special characters except hyphens, underscores, and periods.
* No trailing spaces in filenames.
* No abbreviations in filenames (e.g., use full terms, not shortened forms).
* No generic names (e.g., `Document1.docx`, `Untitled.docx`).

## Agent-Generated Reports

* Destination: `docs/reports/agent/`
* Pattern: `AGT_{route}_{description}_{YYYY-MM-DD}.{ext}`
* Example: `AGT_SR92_Residual_Risk_Catalog_2026-03-18.md`
* Rules:
  * Prefix `AGT_` is mandatory for all agent-generated outputs.
  * Route identifier follows the route naming format above.
  * Description uses underscores between words, title case.
  * Date is the generation date.
  * Extension matches output format (markdown, docx, xlsx).
