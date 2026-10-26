# Review rubric

How Claude judges a contract. Read once per review. The standards live in `standards.json` (built from the standards workbook). The severity rules in section 8 are approved.

## 0. Principles
- Evidence first. Every finding carries a verbatim quote and a page. No quote, no finding. For an absent clause write `(clause absent)` and `Not in contract`.
- Quotes give the fullest context. Quote the whole sentence, sub-clause or list the finding rests on, never a fragment cut off mid-sentence or ending at "that:" or "by:" before the list it introduces. Where the relevant words sit in a long clause, join the excerpts with `...` (each excerpt still verbatim and complete in itself). Aim for under about 1,200 characters per quote.
- Bold the critical words. Wrap the words the finding turns on in `**double asterisks**` (rendered bold in the workbook), for example `perform the Work in accordance with **standards of quality acceptable to Canada**`. Bold only what the Issue discusses, usually one to three phrases.
- Never describe what an unsupplied document contains. Write "not supplied, so not reviewed", not "may provide", "typically includes" or "usually covers" (section 1, Documents not supplied).
- Never mark a clause Conforming without reading the clause text against `required_content` and `standard_language`.
- English only. A translated contract is reviewed as written; say that the original was not seen.
- This is a screen against Start2's own standard. It is not legal advice. Do not send contract text to any external service.
- Do not stop to ask about the role. Guess, record the guess in `role_basis`, and carry on. The one exception: a name containing "Start2" that is not Start2 Asia is flagged and confirmed with the user (section 2).

## 1. Context to establish first
**Status.** Executed if signature blocks carry signatures and dates, Draft otherwise.
**Paper.** Start2 template unmodified (compare to `base_agreement_assembled.md`), Start2 template modified, or client or third-party paper. A new contract on anyone else's paper is the 5-business-day case.
**Contract type.** Service (Start2 sells a service for a fee), Funding (a funder pays a programme through ceilings, claims and audits), Vendor (Start2 buys), Other. For a Funding contract read `FEE` as the funding terms and `COSTREC` as reimbursement and refund terms; set-off, audit, clawback and claim documents matter more.
**Documents not supplied.** List every outside document the contract names that was not supplied with it: general or supplementary conditions, standard clause sets (for example SACC 2035), the bid or proposal, statements of work, policies, codes of conduct, manuals, guidelines, websites and links, other agreements, and annexes or schedules cited but not attached. `run_checks.py` lists candidates (kind `referenced_document`); read the whole contract for more. Leave out statutes and regulations unless the contract makes a named code or policy a contract term. When unsure, list it.
- Tell the user once, before the clause review, which documents are missing and where they are named, and ask whether they can supply them. If they do, ingest them and review them as part of the contract. If they cannot, continue.
- Find every place each document is named: run `scripts/find_references.py W/document.json "<name>" "<other names>" --json` with every name the contract uses for it (for example "2035 (2022-12-01)", "General Conditions", "SACC"). Check each hit, correct its clause number, and keep every one that refers to the document, including the cover page and the priority-of-documents list.
- Record each in `documents_not_supplied`: document name and version, `search` (the names used to find it), `references` (every place it is named, each with `where` and a verbatim `quote` with the name in **bold**), `part_of_contract` (true when the contract says it applies to or forms part of the contract), what the contract says it governs, which findings and coverage rows it leaves open, and the action.
- Each document with `part_of_contract` true, or that imposes obligations on Start2, also becomes a finding of type `Not supplied` with the document name as the clause (section 8 for severity).
- A standard clause whose topic the contract hands to an unsupplied document (for example "interest will be paid in accordance with section 17 of 2035") gets coverage verdict `Not supplied` and a note naming the document.

**Page types.** Body, annex, template form (blank claim or bank forms: note them, do not review them as clauses), FAQ or guidance pages (treat as part of the contract). An annex page that holds only a file icon or a title means the annex is not included.

## 2. Role
Run `scripts/match_entities.py`. Start2 Asia is the only entity treated as ours.
1. **KNOWN** (Start2 Asia named): that party is ours.
2. **FLAG** (any other name containing "Start2", including the bare word): stop, tell the user which name was found and where, and ask whether it is a Start2 entity of ours and in what role. Wait for the answer, then continue.
3. Nothing found: guess. Signals: who performs the service and who pays; names that resemble Start2; who the standards' provider protections would protect (mentors, methodology, programme delivery).
4. Role is Provider (we deliver), Buyer (we pay a vendor) or Other (neither). Write `our_entity`, `our_role` and a one-sentence `role_basis` containing "assumed" when guessed.
5. Provider: run the full review. Buyer or Other: do not apply the standards. Set every coverage verdict to N/A with note "Not assessed: not provider-side", report only role-neutral findings (checks, commercial arithmetic, internal contradictions, blank or missing content), and let the Summary "To confirm" line read "Not assessed".

## 3. Facts to extract (Summary, Key facts)
Parties and addresses, signing date, term and end date, fee or funding amounts with currency and tax treatment, payment schedule, percentages and their arithmetic (use `run_checks.py` info), governing law and forum, language, list of annexes present or absent. Give the clause and page for each.

## 4. Coverage (provider role)
For each clause in `standards.json` (34 rows, Must Have first):
1. Find every contract clause that deals with the topic. One standard clause may map to several contract clauses and the reverse.
2. Break `required_content` into its elements and check each one. Use `standard_language` and `mutuality` to see what a conforming clause looks like and who it binds.
3. Verdict: **Conforming** all elements present and balanced as in the standard; **Partial** present but an element is missing; **Deviant** present but it contradicts the standard (one-sided against Start2, a different number, a different mechanism); **Missing** no such clause; **Not supplied** the contract hands the topic to a document that was not supplied, so it could not be checked; **N/A** the standard does not apply (for example `LANG` in a monolingual contract, `NOCOST` always).
4. Fill `where` (clause number and page) and a `note` in a plain sentence.
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

## 5a. Subjective standards
A subjective standard lets the counterparty alone judge Start2's work, payment or people: "acceptable to Canada", "to the satisfaction of the Client", "in its sole discretion", "as determined by the Company", "suitable to", "in acceptable form or condition". Such wording can be used to withhold acceptance, and so payment, without an objective test Start2 can point to.
- `run_checks.py` lists candidates (check `S`, kind `subjective_standard`); `scripts/subjective.py` holds the patterns. Confirm each and look for others in the text.
- Every finding whose quoted text holds such wording sets `"subjective": true` and is raised one severity level above the section 8 rule (Low to Medium, Medium to High, High to Critical; Critical stays Critical). Bold the subjective words in the quote and say in the Issue that the severity was raised for subjective wording and why.
- Subjective wording that no other finding covers gets its own finding: type `Deviant` under the standard clause it bears on (`WARR` for quality, `FEE` for payment conditions, `SCOPE` for deliverables), otherwise `Unclassified clause`, raised one level from its usual severity.
- Where subjective acceptance controls payment, say how much of the fee depends on it.

## 6. Execution checks (1 to 12)
Run `scripts/run_checks.py` and judge each candidate. It covers blanks and placeholders (1), duplicate or undefined clause numbers (2), date errors (3), annex presence and outside documents (9), translation (5) and tracked changes (8), plus subjective standards (S, section 5a). You must still judge 4, 6, 7, 10, 11, 12 yourself and confirm or dismiss every candidate (labels that introduce a list and end in a colon are false positives).
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
| Not supplied: document that forms part of the contract | High |
| Not supplied: document that imposes obligations on Start2 but is not stated to form part of the contract | Medium |
| Any finding whose quote holds subjective wording (section 5a) | one level above its rule, Critical at most |
| Any finding that needs no action (below) | one level below its rule, after any subjective raise, Low at least |
`validate_review.py` warns when a Missing, Partial or Deviant severity differs from the rule, including both adjustments.

**No action needed.** Set `"action_required": false` when Start2 has nothing to do about the finding, now or at renewal: no negotiation, no internal check, no change to how the work is delivered, only noting it. Typical cases: a client clause within Start2's position, a standard government term that cannot be changed and has no practical effect on delivery or payment, a slip with no consequence. The Action then starts "No action needed" and says in a sentence or two why, and what would change that (for example "unless Start2 later opens an office in Canada"). Lower the severity one level. If any step remains, even a check, the finding needs action and keeps its severity. Critical and High findings that remain after the reduction still go to a person to confirm.

## 9. Writing findings
Findings are read by colleagues who may not be lawyers and may raise the point with the counterparty. Write in a measured, explanatory tone: complete sentences, no fragments, no one-word actions, no shorthand ("one-sided", "no carve-out") left unexplained. Be specific, not alarmist.

**Plain language.** Each cell is read on its own, so explain every legal term the first time it appears in that cell, straight after the term: "set-off, meaning Canada deducts amounts it claims from payments due", "a carve-out (an exception written into the clause)". Refer to Start2 standard clauses by name with the code in brackets, "the Start2 force majeure standard (FM)", never the bare code. Name verdicts in words: "the review rates this Deviant, meaning it contradicts the standard". Before validating, run `scripts/plain_language.py S/references/standards.json W/review.json`; it lists every term and code from `references/plain_terms.json` left unexplained in Issue, Action, coverage notes, check evidence and document rows. Rewrite each one. The workbook adds a "Terms used" line to any cell still holding an unexplained term, but that is a safety net, not a substitute for clear wording. Add new terms to `plain_terms.json` when a review uses one it does not list.

**`issue`** (usually four to six sentences, at least 40 words):
1. What the clause says, in plain words, with its number.
2. What it means for Start2 in practice: a concrete situation in which it would bite, and its consequence in money, time or rights.
3. How it compares with the Start2 standard (`required_content`), naming what is missing or different.
4. Why it has this severity, including any subjective-wording raise.
Do not put recommendations in the Issue; they belong in the Action.

**`action`** (usually three to five sentences, at least 25 words):
1. What to do next and who should do it (check internally, ask the counterparty, escalate through the sign-off chain).
2. The concrete ask, using the standard's numbers where they exist (for example the 14-day cure period in `TERM-CAUSE`), and pointing to the Suggested language column when it is filled.
3. A fallback if the counterparty declines, and what to record.
4. For an executed contract: what to check or record now, and what to ask for at renewal.
Never put command text or script names in the Action. The Suggested language column is filled automatically from the standard; for client, unclassified and commercial findings where a change is asked, write `suggested_language` in the finding.

**`summary.defined_terms`** maps the standard's party names to the contract's own (for example `{"Start2": "the Contractor", "Company": "Canada"}`) so the suggested language reads as the contract does.

Example of the expected depth, from a government services contract:
- Too terse: "Excusable Delay protects the Contractor only, needs a work-around plan within 15 working days, and after 30 days only Canada may terminate with no claim for costs." / "Record."
- Expected issue: "Clause 11 is Canada's version of a force majeure clause (one that excuses delay caused by events outside a party's control). It treats a delay outside Start2's control as an 'Excusable Delay' only if Start2 tells Canada's Representative straight away and, within 15 working days, sends a detailed work-around plan for Canada's approval. If the delay lasts 30 days or more, Canada alone may terminate (11.3), and neither party may then claim costs, so money Start2 has already spent on mentors, venues or travel for the cancelled programme would not be recovered. Clause 11.4 adds that Canada bears none of Start2's delay costs unless Canada caused the delay. The Start2 force majeure standard (FM) applies to both parties, provides a good-faith discussion period before termination and keeps Start2's right to recover its costs, so the review rates this clause Deviant, meaning it contradicts the standard rather than just leaving something out."
- Expected action: "Diarise the 15-working-day notice and work-around-plan requirement with the programme lead so that Start2 does not lose Excusable Delay protection on a technicality. Ask Canada to add that, on termination under 11.3, Start2 is paid for work performed and non-cancellable costs committed before the notice, as in the Start2 standard shown in Suggested language. If Canada declines, record the accepted exposure for the sign-off chain (the Director of People and Operations, the Regional Director of Innovation and Product Strategy and the CEO, who approve every contract) and avoid committing third-party costs earlier than needed."

Other rules:
- Order does not matter; the workbook sorts by severity.
- Confirm Critical, High and client-clause findings with a person (the workbook says so in Read Me).
- For scanned contracts say in the issue when a reading is uncertain.

## 10. What to log
Critical and High findings are logged for a person to confirm. The workbook counts them on the Summary. The skill gives no other recommendation and does not decide sign-off (the full chain applies).
