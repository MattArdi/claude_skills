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
    "standards_version": "optional; defaults to the standards file name",
    "our_entity": "Start2 entity as named in the contract",
    "our_role": "Provider | Buyer | Other",
    "role_basis": "one sentence; say 'assumed' when guessed",
    "counterparty": "the other party",
    "defined_terms": {"Start2": "the Contractor", "Company": "Canada"}
  },
  "facts": [ {"fact": "Total fee", "value": "USD 100,000 excl. tax = 60,000 + 40,000", "where": "5.1 (p. 3)"} ],
  "findings": [
    {"severity": "Critical | High | Medium | Low",
     "type": "Missing | Partial | Deviant | Client: Reject | Client: Escalate | Client: Conditional | Client: Accept | Unclassified clause | Commercial | Execution | Not supplied | Other",
     "clause": "standard clause ID (LOL), playbook row name, 'Check 3', or the document name for Not supplied",
     "where": "13.1 (p. 10) | Not in contract",
     "quote": "verbatim full sentence or sub-clause, the critical words in **bold**; excerpts joined by '...'; '(clause absent)' when nothing exists",
     "issue": "what the clause says, what it means for Start2, how it compares with the standard, why this severity (rubric section 9)",
     "action": "what to do and who, the concrete ask, the fallback (rubric section 9); never command text",
     "subjective": true,
     "suggested_language": "optional: wording to propose; omit for standard clauses to use the Start2 standard"}
  ],
  "coverage": { "LOL": {"verdict": "Conforming | Partial | Deviant | Missing | Not supplied | N/A", "where": "", "note": "a plain sentence"} },
  "checks":   { "1": {"result": "Pass | Fail | N/A | Cannot verify", "evidence": "what was seen, with pages"} },
  "documents_not_supplied": [
    {"document": "SACC 2035 (2022-12-01) General Conditions - Higher Complexity - Services",
     "referenced_at": "Art. 5 (p. 4); App. A 21.6, 21.8 (p. 7)",
     "quote": "2035 (2022-12-01), General Conditions - Higher Complexity - Services, **apply to and form part of the Contract**.",
     "part_of_contract": true,
     "governs": "what the contract says or shows it covers, never a guess at its content",
     "effect": "which findings and coverage rows could not be completed",
     "action": "how to obtain it and what to check once it is in hand"}
  ]
}
```

`subjective` (boolean) is true when the quote holds wording that lets the counterparty alone judge Start2's work,
payment or people (rubric section 5a); omit it otherwise. `part_of_contract` is a boolean. `defined_terms`,
`suggested_language` and `documents_not_supplied` are optional.

Rules enforced by `validate_review.py`:
- Every summary field except `standards_version` and `defined_terms` is filled.
- Provider role: `coverage` has all 34 clause IDs. Other roles: coverage may be all `N/A`.
- `checks` has results for 1 to 12.
- Quotes are found in the text of a text PDF or DOCX (`**` markers are ignored). Quotes of a scanned contract cannot be machine-checked.
- Action text that names a script is an error.
- A Missing, Partial or Deviant finding whose severity differs from the rule gives a warning. The rule includes the one-level raise when `subjective` is true. Keep a difference only when the issue text says why.
- A quote with subjective wording but no `subjective` flag, a quote with no bold part, a quote that ends mid-sentence, and an issue under 40 words or an action under 25 words each give a warning.
- A Missing, Partial or Deviant coverage verdict without a finding gives a warning. So does a failed check without an Execution finding, and a document with `part_of_contract` true without a `Not supplied` finding.
- A `Not supplied` coverage verdict with an empty `documents_not_supplied` list is an error.
