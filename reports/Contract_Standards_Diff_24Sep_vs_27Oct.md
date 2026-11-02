# Start2 Asia Contract Standards: 24 Sep vs 27 Oct comparison

Files compared:

- **Old:** `Start2_Asia_Contract_Standards_UP_24_Sep_1.xlsx` (last modified 2026-09-24 09:21 UTC by U-sa Phalakornkitti)
- **New:** `Start2_Asia_Contract_Standards_UP_27_Oct.xlsx` (last modified 2026-10-27 07:34 UTC by U-sa Phalakornkitti)
- **Skill baseline (for section 5):** `skills/contract-review-flagger/references/Start2_Asia_Contract_Standards_UP_15_Oct_v6.xlsx` and `references/standards.json`

Method: every cell value in all ten sheets was dumped and diffed; cell styles, comments, hyperlinks, merged cells, data validation, conditional formatting, hidden rows/columns, column widths and the raw sheet XML were compared separately. Shared-string index renumbering (a side effect of Excel re-saving) was filtered out.

---

## 1. Bottom line

1. **The 27 Oct file is the 24 Sep file with the Decisions sheet resolved.** Nine of ten sheets are content-identical. The only substantive edits are: the Decisions sheet (sheet 4) replaced its Options / Claude / U-sa / What-it-affects columns with a single "Decision made" column, and the Draft Clause Language sheet (sheet 10) gained a comment column with one comment (on Cost recovery).
2. **The 27 Oct file branched from the 24 Sep original (v0), not from the 15 Oct v6 the skill uses.** It carries none of the v1 to v6 fixes. Re-parsing it wholesale into `standards.json` would undo those fixes. Apply it as a delta (section 6).
3. **The decisions were not propagated inside the 27 Oct workbook.** Process & Authority, Caps and the Draft Clause notes still show the pre-decision positions, wrong decision IDs and "not yet settled" text (section 4).
4. **Two decisions conflict with positions the v6 Design Guide records as instructions from the workbook owner:** review lead time (27 Oct: 2 business days; v6: 3) and the approval chain (27 Oct: tiered, CEO only on a trigger; v6: full three-step chain on every contract). These need an explicit call before the skill changes (section 5).
5. **Genuinely new positions vs the skill:** payment split (50/30/20 preferred, 50/50 fallback), cap multiple (2x for data breach, mutual), cost-recovery roll-forward condition. Force majeure long-stop (60 days) and cost-recovery-only default are unchanged.

---

## 2. What stayed the same (24 Sep to 27 Oct)

Every cell value below is byte-identical between the two files. No comments, hyperlinks, hidden rows/columns, merged cells, data validation or conditional formatting exist in either file. Sheet names, sheet order and row counts are unchanged.

| Sheet | Size | Contents (unchanged) |
|---|---|---|
| 1. Must Have | 28 clauses, cols A:G (#, Clause, What must be on the page, Why it protects Start2, Mutuality, Cap position, Reference clause) | 1 Contracting entity & jurisdiction; 2 Recitals; 3 Defined scope of service (Appendix); 4 Term; 5 Fee, currency, payment trigger; 6 No set-off; 7 Late payment: interest and right to suspend; 8 Confidentiality; 9 Assignment restriction; 10 Independent contractor / no agency or partnership; 11 Notices; 12 Amendment; 13 Termination; 14 No cost committed before payment received; 15 Cost recovery on cancellation; 16 Warranties; 17 Indemnity; 18 Limitation of liability; 19 Force majeure; 20 Compliance with laws / sanctions; 21 Intellectual property (standalone clause); 22 Data protection; 23 Governing language; 24 Governing law & dispute resolution; 25 Entire agreement; 26 Survival; 27 Electronic signature / counterparts; 28 Signature block |
| 2. Good to Have | 3 items | Termination for convenience; Non-solicitation of Start2 network (client-to-Start2 only); Anti-bribery and corruption representation |
| 3. Nice to Have | 3 items + rule | Publicity / case study rights; Defined escalation contact; Severability clause. Rule: "ask once. Drop immediately if resisted." |
| 5. Client-Inserted Clauses | 14 clauses, cols A:C (clause, Start2 position, rejection threshold) | Exclusivity; Clawback / refund on underperformance; Most-favoured-client pricing; Unlimited liability or liability tied to total spend; Assignment of program IP to client; Governing law switched to client jurisdiction; Payment terms beyond 30 days or tied to client funding; Confidentiality carve-out for parent/affiliates; Insurance requirement; Audit rights; Payment suspension or clawback on alleged misstatement; Revenue contingent on a minimum threshold; EU or government grant flow-down audit rights; Liquidated damages or fixed penalty per breach |
| 6. Caps | 6 rows, cols A:E | Direct loss (capped at total Service Fee, 17.2); Confidentiality and data protection breach (capped higher, 17.3); IP infringement Start2 causes (capped higher, 17.3); Gross negligence and wilful misconduct (uncapped, 17.4); Fraud (uncapped, add, 17.4); Confidentiality duty itself (not capped, survives) |
| 7. Execution Check | 12 checks | Placeholders filled; numbering and cross-references; term dates agree; entity name consistent; bilingual versions agree; signature lines; bank details match entity; no tracked-change residue; appendix references resolve; appendix is deal-specific; cross-references resolve; currency/law/arbitration match entity |
| 8. Review Method | 4 passes + reviewer output | 1 Commercial terms; 2 Client-inserted clauses; 3 Deviations from base template; 4 Completeness check. Output: marked-up draft plus cover note (a) to (d) |
| 9. Process & Authority | 11 rows, cols A:C (Topic, Rule, Decision Ref) | Never without review; Lead time standard deal (3 business days); Lead time with client-inserted clause (5 business days); Approval threshold (fee threshold, country lead signs below it); Client says contract cannot be changed; Side letter; Addendum; Tender clarification wording; Point after which leverage is gone; No external cost before payment received; Public-sector exception route |
| 10. Draft Clause Language, cols A:D | 27 Must Have + G1 to G3 + N1 to N3 | All clause text in column C and all notes in column D are unchanged, including every `[X]`, `[Clause name]` and decision-ID placeholder |

Unchanged Decisions content: the seven decision IDs (D-01 to D-07) and their titles in column B are identical.

---

## 3. What changed (24 Sep to 27 Oct)

### 3.1 Decisions sheet structure

| | 24 Sep | 27 Oct |
|---|---|---|
| Columns | A Ref, B Decision, C Options, D Recommendation - Claude, E Recommendation - U-sa, F What it affects | A Ref, B Decision, C Decision made |
| Removed | | Options, both recommendation columns, and "What it affects" cross-references. Columns D:F are now empty and unstyled; autofilter range shrank from A1:F8 to A1:B8 |

Consequence: the 27 Oct file no longer records the alternatives considered, the reasoning, or which clauses each decision affects. The v6 skill baseline still holds the alternatives and reasoning in clause notes; that text has no successor in 27 Oct.

### 3.2 Decision-by-decision changes

Quoted text is verbatim, including original spelling.

#### D-01 Payment split: **NEW POSITION**

- 24 Sep options: (a) Keep 50/50 default; (b) 100% upfront as default; (c) Staged upfront tied to program phases.
- 24 Sep Claude: "(a) 50/50". U-sa: "a) 50/50 default - 50% upon signing of contract and 50% upon completion of service. Completion of Service is to be defined."
- 24 Sep affects: "Cash exposure. Clause B in all five templates."
- **27 Oct:** "Preferred option: 50% upon signing of contract, 30% in the middle of the contract, 20% upon completion of service. Otherwise, 50% upon signing of contract and 50% upon completion of service."
- Change: a three-tranche 50/30/20 split becomes the preferred position; 50/50 is demoted to fallback. "Completion of Service is to be defined" is no longer in the decision text (it survives in the Draft 5.2 note). None of the original options (a), (b), (c) matched 50/30/20 exactly; (c) was closest.

#### D-02 Liability cap multiple for confidentiality/data/IP breaches: **NEW POSITION (previously unresolved)**

- 24 Sep options: (a) Same cap as general liability (total fees); (b) A stated multiple of total fees (2x, 3x).
- 24 Sep Claude: "(b), 2x total fees as a starting ask. These breach types carry third-party exposure the general cap was not built for." U-sa: "Not sure".
- 24 Sep affects: "Caps sheet. Clause F / new Limitation of Liability clause."
- **27 Oct:** "if they breach data, then liability is 2X contract value and VV"
- Change: 2x adopted. Text names only a data breach (not confidentiality or IP), uses "contract value" instead of "total Service Fee paid or payable", and ends "VV" (read as "vice versa", i.e. mutual). See ambiguities, section 7.

#### D-03 Review lead time, standard deal: **NO CHANGE vs U-sa's 24 Sep recommendation**

- 24 Sep options: (a) 1 day; (b) 3 business days; (c) 5 business days.
- 24 Sep Claude: "(b) for unmodified base template; 5 business days if any client clause is present." U-sa: "2 business days if using unmodified template. 5 business days if clauses are updated from template or client's own template".
- **27 Oct:** identical to U-sa's 24 Sep text.
- Change: U-sa's recommendation confirmed as the decision. 2 business days was not one of the listed options. Process & Authority in the same file still says 3 (section 4).

#### D-04 Approval by Director of Ops and Regional Director: **CONFIRMED U-sa recommendation**

- 24 Sep options: (a) Every deal; (b) Fee-based threshold; (c) Fee-based threshold plus any client-inserted clause or Critical/High flag.
- 24 Sep Claude: "(c). Ties escalation to actual risk rather than deal count." U-sa: "Every contract except for unmodified template by Start2."
- **27 Oct:** "Every contract except for unmodified template by Start2."
- Change: U-sa's position adopted. Director of Ops and Regional Director sign-off is required on every contract except an unmodified Start2 template. No fee threshold.

#### D-05 Approval required by CEO: **NEW POSITION**

- 24 Sep options: none listed. Claude: none. U-sa: "I recommend that when a contract involves money, CEO will review the contract and approve."
- **27 Oct:** "CEO Approval is required if the terms of the agreement defers drastically from the approved service agreement template. Amount is different from approved project brief."
- Change: CEO approval moves from "any contract involving money" (effectively all) to two triggers: (1) terms deviate drastically from the approved template; (2) amount differs from the approved project brief. The second trigger is new and introduces the project brief as a reference document.

#### D-06 Force majeure long-stop: **CONFIRMED**

- 24 Sep options: (a) 30 days; (b) 60 days; (c) fraction of remaining term. Claude and U-sa both: "(b), 60 days as a default."
- **27 Oct:** "60 days as a default."
- Change: wording only (option letter dropped).

#### D-07 Fee treatment on force majeure cancellation: **CONFIRMED, WITH NEW CONDITION**

- 24 Sep options: (a) recover only third-party costs actually committed or paid; (b) retain the entire Service Fee, credited toward a future or rescheduled program.
- 24 Sep Claude: "(a) as the default ... easier to defend as fair if challenged." U-sa: "(a)".
- 24 Sep affects: "Must Have: Cost recovery on cancellation. Interacts with D-01 (payment terms)."
- **27 Oct:** "Start2 recovers only costs actually committed or paid to third parties (current Must Have: Cost recovery on cancellation approach). Roll it to future events makes only sense when no third party cost were incured so far and the delivery is mainly Start2 dependant."
- Change: (a) confirmed. New second sentence sets when option (b) roll-forward is appropriate: both (i) no third-party cost incurred so far, and (ii) delivery is mainly Start2-dependent.

### 3.3 Draft Clause Language: new comment column

- New header **E1:** "Claus Commnets" (styled like the other headers).
- New cell **E16** (row for clause 14, Cost recovery on cancellation): "Roll it to future events makes only sense when no third party csost were incured so far and the delivery is mainly Start2 dependant."
- This duplicates the D-07 second sentence. No other row has a comment. The clause text (C16) and the existing note (D16) are unchanged.

### 3.4 Non-substantive changes

- Decisions: column widths changed (C 45.0 to 43.7; D 13.0 to 30.8; F 30.0 to 13.0); styles cleared on D1:F8; wrap text added on C6.
- Client-Inserted Clauses and Draft Clause Language: frozen-pane scroll position and active cell changed; Draft Clause Language zoom set to 144%.
- Workbook: window size, Excel build number and document ID changed. None affect content.

---

## 4. Inconsistencies inside the 27 Oct file

The decisions were recorded on sheet 4 only. These cells still contradict them or point to the wrong decision:

| Location | Current text (abridged) | Conflict |
|---|---|---|
| 9. Process & Authority, Lead time standard deal | "Recommended minimum 3 business days ..." | D-03 says 2 |
| 9. Process & Authority, Lead time client-inserted clause, Decision Ref | "Decisions tab: Review lead time, standard deal." | Refs the standard-deal decision; no separate decision exists |
| 9. Process & Authority, Approval threshold | Fee threshold; country lead signs below it; Director of People and Operations above it or on client clause / Critical / High flag | Contradicts D-04 (every contract except unmodified template) and D-05 (CEO triggers). Decision Ref points to "Approval threshold for Director sign-off", a title that does not exist on sheet 4 |
| 9. Process & Authority, Public-sector exception route | Present | Removed in v1 (superseded by the single sign-off chain); still in 27 Oct |
| 6. Caps, row 3 | "Defined multiple of the Service Fee (figure is yours to set, see Decision D-03)" | Cap multiple is D-02, now set to 2x |
| 10. Draft, 5.2 and its note | "[payment schedule per Decision D-01 ...] OR [50% on signing ...; 50% on Completion]"; note "D-01, not yet settled ... (R-03)" | D-01 now settled at 50/30/20 preferred; R-03 undefined |
| 10. Draft, 14 note (D16) | "Decision D-08 is whether this is the right model ... Not yet settled." | D-08 does not exist; this is D-07, now settled |
| 10. Draft, 17.3 and note | "capped instead at [a multiple, see Decision D-03]"; note "(Decision D-03) is not yet settled" | Wrong ID; D-02 now 2x |
| 10. Draft, 18.2 | "continues for more than [X] days" | D-06 sets 60 |
| 1. Must Have, 19 Reference clause | Includes "one (1) month" long-stop and "failure of the Exhibitor to provide the Exhibitor Items" | Counterparty-specific text removed in v1; one month replaced by 60 days in v1.1 |

---

## 5. 27 Oct vs the skill's current baseline (15 Oct v6 / standards.json)

| Topic | Skill today (v6) | 27 Oct | Status | Skill files affected |
|---|---|---|---|---|
| Payment split (FEE) | 50/50 default; Completion defined per deal; alternatives 100% upfront, staged by phase | 50/30/20 preferred; 50/50 fallback | **Change** | `standards.json` FEE `standard_language` ({{FEE}}.2), `notes`, `open_placeholders`; regenerate `base_agreement_assembled.md`; rubric guidance on what counts as a deviant split |
| Cap multiple (LOL 17.3) | Not set; `[multiple]` placeholder; open item #2 | 2x, mutual; wording names data breach only | **Change** (closes open item) | `standards.json` LOL `standard_language`, `notes`, `open_placeholders`, `cap_position`; `cap_measure` on CONF, IP, DP; Caps reference; regenerate base agreement |
| Review lead time | 3 business days unmodified, 5 otherwise ("instruction from the workbook owner", overriding U-sa's 2) | 2 unmodified, 5 otherwise | **Conflict** | `standards.json` process rule; `scripts/build_review_workbook.py` lines 128 and 227; `README.md` line 79 |
| Director of Ops + Regional Director approval | Every contract, no exceptions | Every contract except unmodified Start2 template | **Conflict** | `standards.json` "Sign-off chain" rule; `SKILL.md` line 93; `README.md` lines 15, 51, 80; `scripts/build_review_workbook.py` lines 49, 118, 139, 177, 228; `references/plain_terms.json` line 56; `references/rubric.md` lines 134, 142 |
| CEO approval | Every contract (step 3 of chain); the "CEO when money involved" rule was explicitly removed in v1 | Only if terms deviate drastically from the approved template, or amount differs from the approved project brief | **Conflict** | Same files as the row above |
| Force majeure long-stop | 60 days | 60 days | Same | None |
| FM cancellation fee treatment (COSTREC) | Recover committed third-party costs only; roll-forward recorded as rejected alternative | Same default; roll-forward acceptable only if no third-party cost incurred and delivery mainly Start2-dependent | **Addition** | `standards.json` COSTREC `notes`; rubric handling when a contract uses roll-forward instead of cost recovery |
| All other clause, client-clause, caps, execution and review content | v6 (restructured, IDs, severities, fixed refs) | v0 text | v6 is ahead | Do not overwrite |

Conflict note: the v6 Design Guide records the 3-business-day lead time and the full three-step chain as "Instruction from the workbook owner", and records that the "CEO-when-money-involved rule" and fee-threshold model were superseded. The 27 Oct decisions come from U-sa's file. Which source prevails is a governance decision, not a drafting one.

---

## 6. Implementation guidance for the skill

1. Treat 27 Oct as a delta on v6. Do not run `parse_standards.py` on the 27 Oct file: that would reintroduce the wrong decision IDs, the R-03 reference, the Exhibitor wording, the one-month long-stop in the reference clause, the approval-threshold and public-sector rows, and drop the clause IDs, severities, cap types, negotiation stances and cross-reference tokens added in v1 to v6.
2. Edit the v6 workbook (as v7) and `standards.json` together, then regenerate `base_agreement_assembled.md` with `assemble_agreement.py`, and keep the v6 rule of no decision IDs in notes.
3. Uncontested changes that can go in once wording is fixed: FEE split, LOL 2x, COSTREC roll-forward condition.
4. Contested changes (lead time, approval chain, CEO trigger) wait for a decision on which source prevails.
5. Add a v7 row to the Design Guide version history and close open item #2 if 2x is adopted.

---

## 7. Ambiguities to resolve before implementing

| Decision | Ambiguity | Why it matters for the skill |
|---|---|---|
| D-01 | "30% in the middle of the contract": calendar midpoint, a named milestone, or a mid-program deliverable? | Must Have #5 requires a plain-language trigger per tranche. The skill needs to know whether to flag an undefined mid-point trigger like an undefined Completion |
| D-01 | Is 50/50 a fully acceptable fallback, or a deviation to note? Are other splits (e.g. 40/60, 100% on completion) deviations? | Determines severity when a contract does not use 50/30/20 |
| D-01 | Does the 20% completion tranche change the no-cost-before-payment rule or the COSTREC exposure analysis? | Smaller final tranche reduces exposure; the rubric may need to reflect it |
| D-02 | Scope: "breach data" only, or confidentiality, data protection and IP as in 17.3 and the Caps sheet? | If data only, CONF and IP fall back to the general cap and 17.3 must split |
| D-02 | "Contract value" vs "total Service Fee paid or payable" | Contract value could include reimbursable costs; 17.2 and 17.3 use Service Fee |
| D-02 | "VV" assumed to mean vice versa (mutual) | 17.3 already reads "each Party's"; confirm before relying on it |
| D-02 | Is 2x a starting ask (Claude's original framing) or a floor? | Determines whether a contract at 1x for data breach is High or Medium |
| D-04 | "Unmodified template by Start2": does an unmodified template still need any approval? | The skill currently says every contract goes to all three approvers |
| D-05 | "Defers drastically": no threshold defined | The skill cannot decide this mechanically; it would need a rule (e.g. any Critical or High finding, any client-inserted clause) or leave it to the reviewer |
| D-05 | "Amount is different from approved project brief": the skill has no project brief input | Either add a project-brief input at intake or report this trigger as a manual check |
| D-07 | Roll-forward conditions: who confirms "no third party cost incurred" and "mainly Start2 dependent", and at what point (signature or cancellation)? | Determines whether a roll-forward clause in a contract is acceptable at review time or only conditionally |
