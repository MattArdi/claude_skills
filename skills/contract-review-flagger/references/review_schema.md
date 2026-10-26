# review.json

The file Claude writes after reading a contract. `build_review_workbook.py` turns it into the review workbook, and
`validate_review.py` checks it first. Every value is a string unless stated.

```json
{
  "summary": {
    "contract": "Name or title of the contract",
    "file": "source file name",
    "status": "Draft | Executed",
    "contract_type": "Service | Funding | Vendor | Other",
    "paper": "Start2 template, unmodified | Start2 template, modified | Client or third-party paper",
    "purpose": "Pre-signature | Signed | Renewal (from the intake message)",
    "standards_version": "optional; defaults to the standards file name",
    "our_entity": "Start2 entity as named in the contract",
    "our_role": "Provider | Buyer | Other",
    "role_basis": "one sentence; say 'assumed' when guessed",
    "counterparty": "the other party",
    "defined_terms": {"Start2": "the Contractor", "Company": "Canada"},
    "explain_terms": true
  },
  "facts": [ {"fact": "Total fee", "value": "USD 100,000 excl. tax = 60,000 + 40,000", "where": "5.1 (p. 3)"} ],
  "findings": [
    {"severity": "Critical | High | Medium | Low",
     "type": "Missing | Partial | Deviant | Client: Reject | Client: Escalate | Client: Conditional | Client: Accept | Unclassified clause | Commercial | Execution | Not supplied | Other",
     "clause": "standard clause ID (LOL), playbook row name, 'Check 3', or the document name for Not supplied",
     "where": "13.1 (p. 10) | Not in contract",
     "quote": "verbatim full sentence or sub-clause, the critical words in **bold**; excerpts joined by '...'; '(clause absent)' when nothing exists",
     "issue": "what the clause says, what it means for Start2, how it compares with the standard, why this severity (rubric section 9); two sentences for Low or no-action findings",
     "action": "what to do and who, the concrete ask, the fallback (rubric section 9); one sentence for Low or no-action findings; never command text",
     "subjective": true,
     "action_required": false,
     "severity_note": "optional: why the severity differs from the rule; shown as a comment on the Severity cell",
     "suggested_language": "optional: wording to propose; omit for standard clauses to use the Start2 standard"}
  ],
  "coverage": { "LOL": {"verdict": "Conforming | Partial | Deviant | Missing | Not supplied | N/A", "where": "", "note": "a plain sentence"} },
  "checks":   { "4": {"result": "Pass | Fail | N/A | Cannot verify", "evidence": "what was seen, with pages",
                    "correct": ["App. A 3.5 (p. 3): replace 'Start2 Group' with START2 GROUP PTE LTD", "..."]} },
  "documents_not_supplied": [
    {"document": "SACC 2035 (2022-12-01) General Conditions - Higher Complexity - Services",
     "search": ["2035 (2022-12-01)", "General Conditions"],
     "references": [
       {"where": "Art. 5 (p. 4)", "quote": "**2035 (2022-12-01), General Conditions** - Higher Complexity - Services, apply to and form part of the Contract."},
       {"where": "App. A 21.6 (p. 7)", "quote": "... interest will be paid in accordance with section 17 of **2035 (2022-12-01), General Conditions** – Higher Complexity – Services."}
     ],
     "part_of_contract": true,
     "governs": "what the contract says or shows it covers, never a guess at its content",
     "effect": "which findings and coverage rows could not be completed",
     "action": "how to obtain it and what to check once it is in hand"}
  ]
}
```

`subjective` (boolean) is true when the quote holds wording that lets the counterparty alone judge Start2's work,
payment or people (rubric section 5a); omit it otherwise. `action_required` (boolean) is false only when the finding
needs nothing beyond noting it (rubric section 8); omit it otherwise. `part_of_contract` is a boolean. `references`
lists every place the document is named; `search` holds the names used to find them (`find_references.py`). `defined_terms`,
`suggested_language` and `documents_not_supplied` are optional.

Rules enforced by `validate_review.py`:
- Every summary field except `standards_version` and `defined_terms` is filled; `purpose` is Pre-signature, Signed or Renewal.
- Provider role: `coverage` has all 34 clause IDs. Other roles: coverage may be all `N/A`.
- `checks` has results for 1 to 12.
- Quotes are found in the text of a text PDF or DOCX (`**` markers are ignored). Quotes of a scanned contract cannot be machine-checked.
- Action text that names a script is an error.
- A Missing, Partial or Deviant finding whose severity differs from the rule gives a warning. The rule includes the one-level raise when `subjective` is true and the one-level reduction when `action_required` is false. Keep a difference only with a `severity_note` saying why; a note silences the warning.
- An action that asks for nothing ("Record.", "None.") without `action_required: false`, or `action_required: false` without an action starting "No action needed", gives a warning.
- When `explain_terms` is true (the default if it is missing), a legal term or Start2 clause code left unexplained (`plain_language.py`) gives a warning and the workbook adds a "Terms used" line for it. When false, neither happens.
- An Issue that states or justifies the severity or verdict ("rated High", "raised one level", "rates this Partial") gives a warning.
- Document references: every quote must be found in the document (error), and a paragraph matching `search` that no reference covers gives a warning.
- A quote with subjective wording but no `subjective` flag, a quote with no bold part and a quote that ends mid-sentence each give a warning. So does text outside its form: for Critical, High and Medium, an issue under 40 words or an action under 25; for Low or no-action findings, an issue over 70 words or an action over 40.
- A failed check with no `correct` list gives a warning; `correct` must be a list of strings.
- A Missing, Partial or Deviant coverage verdict without a finding gives a warning. So does a failed check without an Execution finding, and a document with `part_of_contract` true without a `Not supplied` finding.
- A `Not supplied` coverage verdict with an empty `documents_not_supplied` list is an error.
