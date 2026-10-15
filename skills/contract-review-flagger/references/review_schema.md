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
    "counterparty": "the other party"
  },
  "facts": [ {"fact": "Total fee", "value": "USD 100,000 excl. tax = 60,000 + 40,000", "where": "5.1 (p. 3)"} ],
  "findings": [
    {"severity": "Critical | High | Medium | Low",
     "type": "Missing | Partial | Deviant | Client: Reject | Client: Escalate | Client: Conditional | Client: Accept | Unclassified clause | Commercial | Execution | Other",
     "clause": "standard clause ID (LOL), playbook row name, or 'Check 3'",
     "where": "13.1 (p. 10) | Not in contract",
     "quote": "verbatim text, 300 characters at most; '(clause absent)' when nothing exists",
     "issue": "what is wrong and why it matters",
     "action": "what to do"}
  ],
  "coverage": { "LOL": {"verdict": "Conforming | Partial | Deviant | Missing | N/A", "where": "", "note": "one line"} },
  "checks":   { "1": {"result": "Pass | Fail | N/A | Cannot verify", "evidence": "what was seen, with pages"} }
}
```

Rules enforced by `validate_review.py`:
- Every summary field except `standards_version` is filled.
- Provider role: `coverage` has all 34 clause IDs. Other roles: coverage may be all `N/A`.
- `checks` has results for 1 to 12.
- Quotes are found in the text of a text PDF or DOCX. Quotes of a scanned contract cannot be machine-checked.
- A Missing, Partial or Deviant finding whose severity differs from the rule gives a warning. Keep the difference only when the issue text says why.
- A Missing, Partial or Deviant coverage verdict without a finding gives a warning. So does a failed check without an Execution finding.
