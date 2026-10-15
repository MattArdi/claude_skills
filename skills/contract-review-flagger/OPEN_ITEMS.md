# Open items

What still needs checking, editing or confirming. Status as of 15 Oct 2026. The severity rules are approved.

## A. Confirm
1. **Start2 Asia name.** Only Start2 Asia is treated as ours (`references/start2_entities.json`). Add its exact legal names if contracts use them. Any other name containing "Start2" is flagged and confirmed with the user.
2. **Buyer-side contracts.** Out of scope. When the guess is Buyer or Other the skill reports "Not assessed" and role-neutral findings only. Confirm this behaviour.
3. **Recommendation wording.** Draft: Escalate / Proceed with named conditions / Proceed. Executed: escalate Critical, log High. "Escalate" has no named owner.
4. **Human check rule.** Every Critical, High and client-clause finding is confirmed by a person.
5. **Appended guidance pages** (FAQs, notes) are treated as part of the contract. Confirm as a general rule.
6. **Skill registration.** The skill lives in the repo only. It is not installed and its trigger description has not been tested.

## B. Check
1. **Excel formulas.** Counts, recommendation, lead time and coverage severity were checked for structure and against a Python model only (LibreOffice would not start in the build environment). Open the template in Excel once and confirm values and colours.

## C. Edit
1. **Unset figures** (policy numbers still open in the standards, standards v6):

| Clause ID | Where | Unset figure |
|---|---|---|
| LATEPAY | 7.1 | Interest rate on overdue amounts: `[X]`% per annum |
| LATEPAY | 7.2 | Days overdue before Start2 may suspend delivery: `[X]` days |
| LOL | 17.3 | Liability cap multiple for confidentiality, data and IP breaches: `[multiple]` x total fee (a 2x starting ask is suggested in the LOL notes) |
| FM | 18.2 | Good-faith discussion window before termination: `[14]` days (a bracketed default, not confirmed). The 60-day long-stop is set. |
| TERM-CONV | G1 (optional) | Notice period for termination without cause: `[X]` days |
| NONSOL | G2 (optional) | Non-solicit duration after the agreement ends: `[X]` months |

   Per-deal fill-ins (names, fee, dates, bank details) are not policy figures and are not listed.
2. The Survival clause does not list Intellectual Property although IP breaches carry the higher cap.
3. Static columns: Open placeholders and Survives termination do not update by formula. Refresh them when the language or the Survival clause changes.
4. Optional clauses (Good and Nice) have no Order and are not assembled into the base agreement.

## D. Gaps in the standards found during testing
1. Data protection names PDPA, PIPA, APPI and PIPL only. Add the EU or German regime for programmes in Europe.
2. No guidance for funding agreements (ceilings, claims, audits, set-off, refunds). Add a variant or notes for `FEE` and `COSTREC`.
3. No required payment due date for the client in `FEE`.
4. Boilerplate seen in practice but absent from the standard: third-party rights exclusion, financial-control obligations.
5. `required_content` is prose. Atomic required elements per clause would make mapping more consistent.

## E. Build later
1. Contract-type variants (service, funding, vendor) in the rubric.
2. A buyer-side playbook (declined for now).
3. A suggested-redline output (tracked changes for DOCX input).
4. Multi-contract batch runs and a combined register.
