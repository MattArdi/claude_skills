# Contract Review Flagger: how it works

This skill reviews one contract against the Start2 Asia contract standards and produces one Excel workbook. This file explains exactly what happens at each step and where every column in the workbook comes from. `SKILL.md` is the short operating guide Claude follows; `references/rubric.md` holds the judgement rules; this file ties them together for people.

## 1. The split of work

| Done by | What | Examples |
|---|---|---|
| **Scripts** (exact, repeatable) | Reading files, finding patterns, checking quotes and severities, building the workbook, Excel formulas | `ingest.py`, `run_checks.py`, `validate_review.py`, `build_review_workbook.py` |
| **Claude** (judgement) | Reading the contract, deciding verdicts, writing findings, choosing what to quote and what to bold | everything in `review.json` |
| **The standards workbook** (source of truth) | The 34 standard clauses, the client-clause playbook, the 12 execution checks, process rules | `references/Start2_Asia_Contract_Standards_UP_15_Oct_v6.xlsx` |
| **The user** (once, at intake) | Entity and role, missing documents, plain-language preference, purpose | the intake reply |

Nothing in the workbook is invented by the scripts: every value is either written by Claude into `review.json`, copied from the standards, or an Excel formula over those values.

## 2. Files

| File | Role |
|---|---|
| `references/Start2_Asia_Contract_Standards_UP_15_Oct_v6.xlsx` | The standards. Edited by people. |
| `references/standards.json` | Machine copy of the standards, made by `parse_standards.py`. Never edited by hand. |
| `references/base_agreement_assembled.md` | Start2's base agreement, assembled from the standards by `assemble_agreement.py`; used to tell whether a contract is the Start2 template unchanged. |
| `references/rubric.md` | Judgement rules: context, intake, role, coverage verdicts, client-clause screen, subjective wording, checks, severity, writing. |
| `references/review_schema.md` | The format of `review.json` and the rules the validator enforces. |
| `references/plain_terms.json` | Legal terms with plain meanings, for the optional plain-language pass. |
| `references/start2_entities.json` | Start2 entities treated as ours (today: Start2 Asia only). |
| `templates/Contract_Review_Template.xlsx` | A blank workbook with the Read Me sheet, rebuilt with `build_review_workbook.py --template`. |
| `scripts/ingest.py` | Contract file to `document.json` (text per page, paragraphs, flags). |
| `scripts/intake.py` | Drafts the single intake message. |
| `scripts/match_entities.py` | Finds Start2 names in the text. |
| `scripts/segment.py` | Best-effort split into clauses. |
| `scripts/run_checks.py` | Candidate problems for Claude to confirm or dismiss. |
| `scripts/subjective.py` | Patterns for wording that lets the counterparty alone judge Start2. |
| `scripts/find_references.py` | Every place a named document appears, with clause, page and sentence. |
| `scripts/plain_language.py` | Lists legal terms and clause codes left unexplained. |
| `scripts/suggest_language.py` | Start2 standard wording for a clause, with the contract's party names. |
| `scripts/validate_review.py` | Checks `review.json` before the workbook is built. |
| `scripts/build_review_workbook.py` | `review.json` plus `standards.json` to the workbook. |
| `scripts/parse_standards.py`, `scripts/assemble_agreement.py` | Rebuild `standards.json` and the base agreement after the standards workbook changes. |

## 3. The process, step by step

`S` is the skill folder; `W` is a working folder for one contract.

| # | Step | Command or action | Output |
|---|---|---|---|
| 1 | **Ingest** | `ingest.py <contract> W` | `W/document.json`. A PDF page with fewer than 25 characters of text is treated as an image: it is saved to `W/pages/` for Claude to read, and Claude writes `W/transcript.json` and re-runs ingest with `--transcript`. DOCX tracked changes are counted and deleted text is left out. |
| 2 | **Intake** | `intake.py W/document.json`; Claude edits the draft and sends it | One message with four questions: (1) Start2 entity and role, (2) documents the contract names but that may not be attached, (3) whether to explain legal terms in plain words, (4) purpose: Pre-signature, Signed or Renewal. The review waits for the reply and does not stop again. |
| 3 | **Context and role** | Claude reads the contract | Status (Draft or Executed), whose paper, contract type, page types, role. Documents the user sent are ingested and reviewed with the contract; the rest go on the Documents not supplied sheet with every reference (`find_references.py`). A Buyer or Other role means the standards are not applied. |
| 4 | **Candidates** | `segment.py`, `run_checks.py` | `W/clauses.json` and `W/candidates.json`: blanks and placeholders (check 1), duplicate or undefined clause numbers (2), date errors (3), annexes and outside documents (9), tracked changes (8), translation hints (5), subjective wording (S), and amount arithmetic. Claude confirms or dismisses each. |
| 5 | **Review** | Claude, following `rubric.md` sections 4 to 9 | A verdict for each of the 34 standard clauses; a screen of every other clause against the playbook; the subjective-wording pass; the 12 checks; a pass over money terms. |
| 6 | **Write** | Claude writes `W/review.json` | Summary, key facts, findings, coverage, checks, documents not supplied (format in `review_schema.md`). |
| 7 | **Validate** | `plain_language.py` (if terms are to be explained), then `validate_review.py` | Errors must be fixed; warnings are read and fixed or accepted with a reason. |
| 8 | **Build** | `build_review_workbook.py S/references/standards.json W/review.json W/<name>_review.xlsx` | The workbook. |
| 9 | **Hand-over** | Claude | A short message: role, status, counts, the Critical and High items, missing documents, anything uncertain. |

## 4. How severity is decided

Claude sets each finding's severity in `review.json` by these rules (`rubric.md` section 8); the validator recomputes the rule for Missing, Partial and Deviant findings and warns on any difference.

| Source | Severity |
|---|---|
| Missing or Deviant Must Have clause | the clause's base severity in the standards |
| Partial Must Have clause | one level lower, Low at least |
| Good to Have or Nice to Have clause missing | Low (anti-bribery `ABC` is Medium for a government-linked counterparty) |
| Client clause: reject threshold met, or a hard stop | Critical |
| Client clause: escalate-always row, or grant flow-down | High |
| Client clause: acceptable with conditions to confirm | Medium |
| Client clause: within Start2's position | Low |
| Blank essential field in a draft for signature | High (Critical if already executed) |
| Annex missing or wrong in a payment or scope clause | High |
| Date or cross-reference mismatch | Medium |
| Numbering, typo, naming | Low |
| Money term that contradicts another or is undefined | High; unusual but explained, Medium |
| Document not supplied that forms part of the contract | High |
| Document not supplied that imposes obligations but is not part of the contract | Medium |

Then two adjustments, in this order:
1. **Subjective wording** (the quote lets the counterparty alone judge Start2's work, payment or people, such as "acceptable to Canada" or "in its sole discretion"): one level up, Critical at most. Recorded as `"subjective": true`.
2. **No action needed** (nothing for Start2 to do now or later beyond noting it): one level down, Low at least. Recorded as `"action_required": false`; the Action starts "No action needed".

Neither adjustment is shown as a column or mentioned in the Issue. If a severity departs from these rules for another reason, the reason goes in `severity_note` and appears as a comment on the Severity cell.

## 5. The workbook, sheet by sheet

Source key: **Claude** = written by Claude into `review.json`; **Standards** = copied from `standards.json`; **Script** = computed by `build_review_workbook.py` when the workbook is built; **Formula** = a live Excel formula that recalculates when cells are edited.

### Read Me
Fixed text written by `build_review_workbook.py`: what the workbook is, how to use each sheet, the severity scale, every column, and the rules. It is the same for every contract.

### Summary

| Row | Source | How it is computed |
|---|---|---|
| Contract, Source file | Claude | `summary.contract`, `summary.file`. |
| Status | Claude | Executed if the signature blocks carry signatures and dates, Draft otherwise (drop-down). |
| Contract type | Claude | Service, Funding, Vendor or Other (drop-down). |
| Whose paper | Claude | Start2 template unmodified (compared with `base_agreement_assembled.md`), Start2 template modified, or client or third-party paper (drop-down). |
| Purpose | User, via intake | Pre-signature, Signed or Renewal (drop-down). Sets how every Action is worded. |
| Standards version | Script | `summary.standards_version`, else the standards file name. |
| Our entity, Our role, Role basis, Counterparty | Claude, confirmed at intake | `summary.our_entity`, `our_role` (drop-down), `role_basis`, `counterparty`. |
| Critical, High, Medium, Low | Formula | `=COUNTIF(Findings!B2:B300, "<level>")`. |
| To confirm | Formula | If Our role is not Provider: "Not assessed: the standards cover provider-side contracts only". Otherwise Critical + High, as "n Critical and High findings to confirm". |
| Documents not supplied | Formula | `=COUNTA('Documents not supplied'!B2:B300)`. |
| Review lead time | Formula | "3 business days" if Whose paper is the unmodified Start2 template, otherwise "5 business days". |
| Sign-off chain | Script (fixed text) | Director of People and Operations, then Regional Director of Innovation and Product Strategy, then CEO. |
| Key facts (Fact, Value, Where) | Claude | `facts[]`: parties, signing, term, amounts with arithmetic, milestones, law and forum, language, annexes, each with its clause and page. |

### Findings
One row per finding, sorted Critical, High, Medium, Low (order within a level follows `review.json`).

| Column | Source | How it is computed |
|---|---|---|
| # | Script | Running number after sorting. |
| Severity | Claude | By the rules in section 4 (drop-down, coloured). A comment on the cell, if any, is `severity_note`. |
| Type | Claude | Missing, Partial or Deviant (a standard clause); Client: Reject, Escalate, Conditional or Accept (a playbook row); Unclassified clause (generic screen); Commercial; Execution (a failed check); Not supplied (a missing document); Other. |
| Clause | Claude | The standard clause ID (for example `LOL`), the playbook row name, "Check n", or the document name. |
| Where | Claude | Contract clause and page, or "Not in contract". |
| Quote | Claude, checked by script | Verbatim contract text: the full sentence or sub-clause, excerpts joined by "...", "(clause absent)" when nothing exists. Words wrapped in `**` in `review.json` are rendered bold. The validator confirms every excerpt of 15 or more characters appears in the document text (letters and digits compared, case and punctuation ignored). |
| Issue | Claude | Full form (Critical, High, Medium): what the clause says, what it means for Start2 in practice, how it compares with the Start2 standard. Short form (Low or no-action): two sentences. Never states or justifies the severity, verdict or type. If plain-language explanations were requested and a term is still unexplained, the script appends a "Terms used" line from `plain_terms.json`. |
| Action | Claude | Full form: what to do and who, the concrete ask, a fallback, worded for the Purpose. Short form: one sentence. No-action findings start "No action needed". Same "Terms used" rule as Issue. |
| Suggested language | Script, or Claude | If the finding has `suggested_language`, that text. Otherwise, for a Missing, Partial or Deviant finding on a standard clause that has standard wording: "Start2 standard clause ID (heading), worded for this contract:" followed by the standard language from `standards.json`, with cross-references shown as clause names and the standard's party names swapped for the contract's (`summary.defined_terms`, for example Start2 to "the Contractor", Company to "Canada"); bracketed placeholders are left as they are. Otherwise blank. |

### Coverage
One row per standard clause, all 34, in the order of the standards workbook.

| Column | Source | How it is computed |
|---|---|---|
| ID, Clause | Standards | The clause ID and name. |
| Base severity | Standards | The clause's base severity (editable drop-down, for example to raise `ABC` for a government counterparty). |
| Verdict | Claude | Conforming (all required elements present and balanced), Partial (an element missing), Deviant (contradicts the standard), Missing, Not supplied (the contract hands the topic to a document that was not supplied), or N/A (drop-down). |
| Where | Claude | Contract clause and page. |
| Severity | Formula | "-" if Verdict is Conforming or N/A or Base severity is n/a; one level below Base severity (Low at least) if Partial; otherwise Base severity. It is a view: the counts on Summary use Findings only. |
| Note | Claude | A plain sentence on what is present or missing. Same "Terms used" rule as Issue. |

### Checks
One row per execution check, all 12, in the order of the standards workbook.

| Column | Source | How it is computed |
|---|---|---|
| # | Standards | Check number. |
| Check | Standards | The check text; check 11 uses a reworded label because the original refers to Start2's own template tokens. |
| Result | Claude | Pass, Fail, N/A or Cannot verify (drop-down), after confirming or dismissing the `run_checks.py` candidates and judging checks 4, 6, 7, 10, 11 and 12 by reading. |
| Evidence | Claude | What was seen, with pages. Same "Terms used" rule as Issue. |
| Clauses to correct | Claude | For a failed check, a numbered list of each contract clause or page to correct and what to change (`checks.n.correct`). Blank for checks that pass. |

### Documents not supplied
One row per outside document the contract names that was not supplied with it.

| Column | Source | How it is computed |
|---|---|---|
| # | Script | Running number. |
| Document | Claude | The name and version as the contract gives it. |
| Referenced at | Script, from Claude's list | Numbered list of every `references[].where`. |
| Quotes | Script, from Claude's list | Numbered "where: quote" for every reference, document name in bold. Each quote is verified against the document text, and the validator warns if a paragraph matching the document's `search` terms is not referenced. |
| Part of contract | Claude | Yes when the contract says the document applies to or forms part of it. Those also appear in Findings as type Not supplied. |
| Governs | Claude | What the contract says or shows the document covers. Never a guess at its content. |
| Effect on this review | Claude | Which findings and coverage rows it leaves open. |
| Action | Claude | How to obtain it and what to check once it is in hand. |

## 6. What the validator checks

`validate_review.py <standards.json> <review.json> <document.json>` exits with an error code if any ERROR is found.

| Level | Check |
|---|---|
| Error | A required summary field is empty (contract, file, status, contract type, paper, purpose, entity, role, role basis, counterparty), or status, contract type, role or purpose is not an allowed value. |
| Error | A finding is missing a field or has an unknown severity or type; a Missing, Partial or Deviant finding, or a coverage row, names a clause ID that is not in the standards. |
| Error | A quote excerpt is not found in the document text (text PDF or DOCX). |
| Error | An Action contains script names or commands. |
| Error | Provider role without a verdict for all 34 clauses; a check without a result; `correct` is not a list of strings; a document row missing a field or a reference not found in the text; a Not supplied verdict with no documents listed. |
| Warning | A Missing, Partial or Deviant severity differs from the rule (including both adjustments) and has no `severity_note`. |
| Warning | An Issue states or justifies the rating ("rated High", "raised one level", "this is Partial"). |
| Warning | Text outside its form: full form below 40 words (Issue) or 25 (Action); short form above about 70 (Issue) or 40 (Action). |
| Warning | A quote with no bold part, a quote that ends mid-sentence (unless the source paragraph ends there), or a quote with subjective wording but no `subjective` flag. |
| Warning | An Action that asks for nothing without `action_required: false`, or the reverse. |
| Warning | A non-conforming verdict with no finding; a failed check with no Execution finding or no clauses to correct; a document that forms part of the contract with no Not supplied finding; a document named in more places than its references list. |
| Warning | When plain-language explanations are on (`summary.explain_terms` is not false): a legal term or clause code left unexplained. If `explain_terms` is missing, a warning that it was not asked at intake. |
| Warning | Quotes from transcribed image pages cannot be checked against the image itself. |

## 7. Keeping it current

| When | Do this |
|---|---|
| The standards workbook changes | Run `parse_standards.py` and `assemble_agreement.py`, then rebuild the template with `build_review_workbook.py S/references/standards.json --template S/templates/Contract_Review_Template.xlsx`. |
| A review meets a legal term the glossary lacks | Add it to `references/plain_terms.json` (term, pattern, plain meaning). |
| A review meets subjective wording the patterns missed | Add a pattern to `scripts/subjective.py`. |
| A new Start2 entity is confirmed as ours | Add it to `references/start2_entities.json`. |
