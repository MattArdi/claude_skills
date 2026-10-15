# Open items

What still needs checking, editing or confirming. Status as of 15 Oct 2026.

## A. Confirm (needs a decision from you)
1. **Start2 entity list.** `references/start2_entities.json` has three entries, two of them guesses (GEA from the ESG sample, Deruchuang from the BMW sample). Supply the real legal names, aliases and former names for Singapore, Korea, Japan, China, Germany and any other entity.
2. **BMW role guess.** The example assumes Start2 is Party A (buyer), so the BMW workbook reads "Not assessed". If Start2 is Party B, the BMW review must be redone as a provider review (the earlier draft findings on penalties, joint IP, forum, missing liability cap would return).
3. **Buyer-side contracts.** Out of scope by your decision. The skill reports "Not assessed" and role-neutral findings only. Confirm this is the behaviour you want when the guess is Buyer.
4. **Severity rules beyond the base table.** You accepted the base severities. These rules are mine and not yet reviewed: Partial = one level lower; Good and Nice = Low; client clause Reject = Critical, escalate-always = High, conditional = Medium, within position = Low; execution check severities; Commercial severities (rubric section 8).
5. **Recommendation wording.** Draft: Escalate / Proceed with named conditions / Proceed. Executed: escalate Critical, log High. "Escalate" has no named owner (you chose to ignore escalation).
6. **Human check rule.** Every Critical, High and client-clause finding is confirmed by a person. Confirm that is the right bar.
7. **FAQ and appended pages.** Treated as part of the contract (your answer for ESG). Confirm this applies as a general rule for appended guidance pages.
8. **Skill registration.** The skill lives in the repo only. It is not installed anywhere and its trigger description has not been tested.

## B. Check (built, not verified)
1. **Excel formulas.** LibreOffice would not start in this environment, so the workbook formulas (counts, recommendation, lead time, coverage severity) were checked for structure and against a Python model only. Open the three workbooks in Excel once and confirm values and colours.
2. **Scanned contracts.** No OCR tool is installed. The skill relies on Claude reading page images, so quotes from scans are transcriptions and cannot be machine-verified. The ESG quotes were read from images: check the cited page for each High and Critical finding. A real OCR (for example tesseract) would help.
3. **ESG findings that need a person.** Annex B eligibility of consultant lines (including one named person who is also the signatory); whether the audit rights count as a government grant flow-down; exact wording of the FAQ quote (p. 27); the "20019" date typo; the claim that annexes A, D, E and F are icons only (the scan shows icons, the originals may exist elsewhere).
4. **Segmenter and checks were tested on one text PDF (BMW) and one synthetic DOCX.** Not tested on: real DOCX with tracked changes and comments, bilingual contracts, contracts with unusual numbering (Chinese `第X条`, `1)` lists, nested tables), two-column PDFs.
5. **`run_checks.py` heuristics.** Blank-field detection flags heading-like labels (for example "Party B Bank Account Information:"). Date, percentage and sum checks cover common formats only. Claude must confirm or dismiss every candidate.
6. **Quote verification** ignores punctuation and case. A paraphrase that keeps the same letters in order would pass. Short segments (under 15 characters) are not checked.
7. **No evaluation set.** The two samples are the only regression cases. Verdicts depend on Claude's reading of `required_content`; there is no measured accuracy.
8. **Standards workbook v5** was parsed and assembled successfully (27 clauses numbered, no leftover tokens) but the base-severity column and Design Guide edits were not reviewed in Excel.

## C. Edit (known defects in the standards)
1. Unset figures: late-payment interest rate and suspension days, termination-for-convenience notice period, non-solicit duration, force majeure good-faith window (`[14]` is a bracketed default), cap multiple (`[multiple]`, 2x is a suggestion).
2. The Survival clause omits Intellectual Property although IP breaches carry the higher cap.
3. The Entire agreement note still cites the Enterprise Singapore exhibition agreement.
4. The Execution Check column "Risk Ref" is empty and unused.
5. Static columns: Open placeholders and Survives termination do not update by formula. Refresh them when the language or Survival clause changes.
6. Optional clauses (Good and Nice) have no Order and are not assembled into the base agreement.
7. `base_agreement_assembled.md` still names no sub-clause for the cap multiple etc. (placeholders by design).

## D. Gaps found in the ESG review (not yet in the standards)
1. Data protection names PDPA, PIPA, APPI, PIPL only. Add the EU or German regime (GDPR) for programmes in Europe.
2. No guidance for funding agreements (ceilings, claims, audits, set-off, refunds). Add a variant or notes for `FEE` and `COSTREC`.
3. No required payment due date for the client in `FEE`.
4. Boilerplate seen in ESG but absent from the standard: third-party rights exclusion, financial-control obligations.
5. `required_content` is prose. Atomic required elements per clause (as in the architecture plan) would make mapping more consistent.

## E. Build later
1. Contract-type variants (service, funding, vendor) in the rubric.
2. Buyer-side playbook (declined for now).
3. A suggested-redline output (tracked changes for DOCX input).
4. Multi-contract batch runs and a combined register.
