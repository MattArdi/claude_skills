# Review rubric

How Claude judges a contract. Read once per review. The standards live in `standards.json` (built from the standards workbook). The severity rules in section 8 are approved.

## 0. Principles
- Evidence first. Every finding carries a verbatim quote (300 characters at most) and a page. No quote, no finding. For an absent clause write `(clause absent)` and `Not in contract`.
- Never mark a clause Conforming without reading the clause text against `required_content` and `standard_language`.
- English only. A translated contract is reviewed as written; say that the original was not seen.
- This is a screen against Start2's own standard. It is not legal advice. Do not send contract text to any external service.
- Do not stop to ask about the role. Guess, record the guess in `role_basis`, and carry on. The one exception: a name containing "Start2" that is not Start2 Asia is flagged and confirmed with the user (section 2).

## 1. Context to establish first
**Status.** Executed if signature blocks carry signatures and dates, Draft otherwise.
**Paper.** Start2 template unmodified (compare to `base_agreement_assembled.md`), Start2 template modified, or client or third-party paper. A new contract on anyone else's paper is the 5-business-day case.
**Contract type.** Service (Start2 sells a service for a fee), Funding (a funder pays a programme through ceilings, claims and audits), Vendor (Start2 buys), Other. For a Funding contract read `FEE` as the funding terms and `COSTREC` as reimbursement and refund terms; set-off, audit, clawback and claim documents matter more.
**Page types.** Body, annex, template form (blank claim or bank forms: note them, do not review them as clauses), FAQ or guidance pages (treat as part of the contract when they set conditions). An annex page that holds only a file icon or a title means the annex is not included.

## 2. Role
Run `scripts/match_entities.py`. Start2 Asia is the only entity treated as ours.
1. **KNOWN** (Start2 Asia named): that party is ours.
2. **FLAG** (any other name containing "Start2", including the bare word): stop, tell the user which name was found and where, and ask whether it is a Start2 entity of ours and in what role. Wait for the answer, then continue.
3. Nothing found: guess. Signals: who performs the service and who pays; names that resemble Start2; who the standards' provider protections would protect (mentors, methodology, programme delivery).
4. Role is Provider (we deliver), Buyer (we pay a vendor) or Other (neither). Write `our_entity`, `our_role` and a one-sentence `role_basis` containing "assumed" when guessed.
5. Provider: run the full review. Buyer or Other: do not apply the standards. Set every coverage verdict to N/A with note "Not assessed: not provider-side", report only role-neutral findings (checks, commercial arithmetic, internal contradictions, blank or missing content), and let the Summary recommendation read "Not assessed".

## 3. Facts to extract (Summary, Key facts)
Parties and addresses, signing date, term and end date, fee or funding amounts with currency and tax treatment, payment schedule, percentages and their arithmetic (use `run_checks.py` info), governing law and forum, language, list of annexes present or absent. Give the clause and page for each.

## 4. Coverage (provider role)
For each clause in `standards.json` (34 rows, Must Have first):
1. Find every contract clause that deals with the topic. One standard clause may map to several contract clauses and the reverse.
2. Break `required_content` into its elements and check each one. Use `standard_language` and `mutuality` to see what a conforming clause looks like and who it binds.
3. Verdict: **Conforming** all elements present and balanced as in the standard; **Partial** present but an element is missing; **Deviant** present but it contradicts the standard (one-sided against Start2, a different number, a different mechanism); **Missing** no such clause; **N/A** the standard does not apply (for example `LANG` in a monolingual contract, `NOCOST` always).
4. Fill `where` (clause number and page) and a one-line `note`.
5. Missing, Partial and Deviant verdicts each get a Finding (type = the verdict, clause = the ID).
6. Good to Have and Nice to Have clauses: Missing is Low. For `ABC` raise to Medium when the counterparty is government-linked or state-owned and say so in the issue.

## 5. Client clauses and anything outside the standard
Every contract clause not mapped in step 4 is a candidate. Compare it with the playbook rows in `standards.json` (`client_inserted_clauses`): exclusivity, clawback or refund on underperformance, most-favoured pricing, unlimited liability, IP assignment, governing law switch, payment terms beyond 30 days, confidentiality carve-outs for affiliates, insurance, audit rights, payment suspension on allegation, minimum-threshold revenue, grant flow-down audit rights, liquidated damages.
- Within Start2's position: type `Client: Accept`, Low.
- Position met with conditions to confirm: `Client: Conditional`, Medium.
- Playbook says escalate or the grant flow-down row applies: `Client: Escalate`, High.
- Reject threshold met: `Client: Reject`, Critical. "Hard stop" rows are always Critical.
- Not in the playbook: apply the generic screen below and use `Unclassified clause`. Default Medium, Low if benign.
Generic screen: one-way termination or cancellation rights, open-ended scope, per-breach penalties, uncapped indemnity, price control, unfunded obligations, outcome-linked payment, payment conditions with no deadline, data or audit access, exclusivity, non-compete.

## 6. Execution checks (1 to 12)
Run `scripts/run_checks.py` and judge each candidate. It covers blanks and placeholders (1), duplicate or undefined clause numbers (2), date errors (3), annex presence (9), translation (5) and tracked changes (8). You must still judge 4, 6, 7, 10, 11, 12 yourself and confirm or dismiss every candidate (labels that introduce a list and end in a colon are false positives).
Result per check: Pass, Fail, N/A, Cannot verify. Each Fail also becomes a Finding with type `Execution` and clause `Check n`.

## 7. Commercial pass
Fee, currency, tax, payment trigger and due date, term dates, balance amounts, ceilings against annex totals. Findings of type `Commercial`.

## 8. Severity
| Source | Severity |
|---|---|
| Missing or Deviant Must Have clause | the clause's `base_severity` |
| Partial Must Have clause | one level lower, floor Low |
| Good or Nice clause missing | Low (`ABC` Medium for government-linked counterparty) |
| Client clause: Reject threshold met or hard stop | Critical |
| Client clause: escalate-always row or grant flow-down | High |
| Client clause accepted with conditions to confirm | Medium |
| Client clause within position | Low |
| Execution: blank essential field in a draft for signature | High (Critical if already executed) |
| Execution: annex missing or wrong in a payment or scope clause | High |
| Execution: date or cross-reference mismatch | Medium |
| Execution: numbering, typo, naming | Low |
| Commercial: contradiction or undefined money term | High; unusual but explained Medium |
`validate_review.py` warns when a Missing, Partial or Deviant severity differs from the rule.

## 9. Writing findings
- `issue`: one to three sentences: what is wrong and why it matters to Start2.
- `action`: imperative. When a Start2 clause exists, name its ID and the way to get the text: `scripts/suggest_language.py references/standards.json LOL`.
- Order does not matter; the workbook sorts by severity.
- Confirm Critical, High and client-clause findings with a person (the workbook says so in Read Me).
- For scanned contracts say in the issue when a reading is uncertain.

## 10. Recommendation
The workbook computes it. Draft: any Critical = Escalate; any High = Proceed with named conditions; else Proceed. Executed: escalate Critical, log High for amendment or renewal. Sign-off is always the full chain; the skill does not decide it.
