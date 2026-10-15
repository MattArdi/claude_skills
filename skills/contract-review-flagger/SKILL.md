---
name: contract-review-flagger
description: Review a contract against the Start2 Asia contract standards and return an Excel review workbook. Reads a contract (text PDF, scanned PDF, DOCX), finds every standard clause that is missing, partial or deviant, screens client-inserted and other non-standard clauses against the Start2 playbook, runs the execution checks (blanks, dates, annexes, numbering, arithmetic), and rates each finding Critical, High, Medium or Low. Use whenever someone at Start2 Group asks to review, check, vet, screen or flag risks in a contract, agreement, MoU or service contract, asks what is missing from a contract, whether a client clause is acceptable, or uploads a contract and wants a risk list, even if they do not name this skill. English contracts only. Provider-side contracts only: if Start2 is the buyer, the skill reports "Not assessed" and lists only role-neutral findings. Do not use it to draft a contract, to build a tender tracker (tender-prep-xlsx), or for legal advice.
---

# Contract Review Flagger

Reads one contract and produces one workbook: Summary, Findings, Coverage, Checks. Claude does the judgement (mapping clauses, screening client clauses, writing findings). Scripts do everything that must be exact (reading files, finding blanks and date errors, checking quotes, building the workbook).

Scope today: English contracts where Start2 delivers a service or programme (service, funding or collaboration agreements). It never stops to ask which party Start2 is: it guesses, records the guess on the Summary, and carries on.

## Files

| Path | What it is |
|---|---|
| `references/Start2_Asia_Contract_Standards_UP_15_Oct_v5.xlsx` | The standards workbook. Source of truth. Never edit `standards.json` by hand. |
| `references/standards.json` | Generated from the workbook by `scripts/parse_standards.py`: 34 clauses with required content, standard language, base severity; client-inserted playbook; 12 execution checks. |
| `references/rubric.md` | How to judge: role guess, verdicts, client-clause screen, severity table, writing rules. Read it before step 4. |
| `references/review_schema.md` | The `review.json` format. |
| `references/start2_entities.json` | Known Start2 entities for the role guess. Incomplete. |
| `references/base_agreement_assembled.md` | The base English agreement, assembled from the standards (for "template unmodified" checks). |
| `templates/Contract_Review_Template.xlsx` | Blank review workbook with a Read Me that explains every sheet and column. |
| `examples/` | ESG (scanned, executed, funding) and BMW (draft, buyer-side) as `*_review.json` plus the workbooks they produce. |
| `scripts/ingest.py` | Contract file to `document.json`; renders image-only pages. |
| `scripts/segment.py` | `document.json` to a clause tree. |
| `scripts/run_checks.py` | Candidates: blanks, dates, duplicate numbers, annexes, percentages. |
| `scripts/match_entities.py` | Finds known Start2 entities in the text. |
| `scripts/validate_review.py` | Schema, severity and quote checks on `review.json`. |
| `scripts/build_review_workbook.py` | `review.json` to the review workbook. |
| `scripts/suggest_language.py` | Prints Start2 standard language for clause IDs. |
| `scripts/parse_standards.py`, `assemble_agreement.py` | Rebuild `standards.json` and the assembled agreement after the workbook changes. |
| `OPEN_ITEMS.md` | What still needs checking, editing or confirming. |

Needs `poppler-utils` (`pdftotext`, `pdftoppm`, `pdfinfo`) and Python `openpyxl`.

## Workflow

Work in a scratch directory `W` (for example `/tmp/review-<contract>/`). `S` is this skill directory.

### 1. Ingest
```
python3 S/scripts/ingest.py <contract> W
```
- Text PDF or DOCX: `W/document.json` is ready. DOCX tracked changes are counted; deleted text is excluded.
- Scanned PDF: the script lists the pages needing vision and writes them as images to `W/pages/`. Read them with the Read tool (20 pages per call), write `W/transcript.json` as `{"1": "page text", ...}`, keep paragraph breaks as blank lines, and re-run with `--transcript W/transcript.json`. Quotes from a transcript cannot be machine-verified: record the page for every quote.
- If a file is neither PDF, DOCX nor text, say so and stop.

### 2. Context and role
Read the contract. Establish status (Draft or Executed), paper, contract type and page types as in `references/rubric.md` section 1. Run `python3 S/scripts/match_entities.py W/document.json`, then guess the role (rubric section 2) and write `role_basis`. A Buyer or Other role means no standards coverage (rubric section 2, step 5).

### 3. Segment and extract
```
python3 S/scripts/segment.py W/document.json W/clauses.json
python3 S/scripts/run_checks.py W/document.json W/candidates.json
```
Check the clause tree by eye and fix mistakes (the segmenter is best effort). Extract the key facts. Confirm or dismiss each candidate in `candidates.json`.

### 4. Review (provider role)
Follow `references/rubric.md` sections 4 to 8: coverage verdicts for all 34 clauses, client and non-standard clause screen, the 12 execution checks, the commercial pass. Use `references/standards.json` for required content, standard language, mutuality, cap position and the playbook. Parallel subagents may handle clause groups, but one agent writes the final `review.json`.

### 5. Write and validate
Write `W/review.json` (format in `references/review_schema.md`), then:
```
python3 S/scripts/validate_review.py S/references/standards.json W/review.json W/document.json
```
Fix every ERROR. Read every WARN: justify a severity that differs from the rule in the issue text, add missing findings, and for scanned contracts check the quoted pages by eye.

### 6. Build and deliver
```
python3 S/scripts/build_review_workbook.py S/references/standards.json W/review.json W/<contract>_review.xlsx
```
Hand over the workbook with a short message: role guess and basis, status, counts by severity, the recommendation, the three to five items that matter most, and anything uncertain (scanned pages, role guess, items needing a person). Counts and recommendation are formulas in the workbook; state them as the workbook will show them.

## Rules
- No quote, no finding. Scanned quotes are transcriptions: say so.
- Do not mark a clause Conforming without reading it.
- Do not apply provider standards to a buyer-side contract.
- Never invent contract text, page numbers or clause numbers.
- Every Critical, High and client-clause finding is confirmed by a person before action. Sign-off is always the full chain: Director of People and Operations, Regional Director of Innovation and Product Strategy, CEO.
- Contracts hold personal and bank data. Keep them local. No external services.
- After the standards workbook changes, run `parse_standards.py` and `assemble_agreement.py`, then retest on the examples.
