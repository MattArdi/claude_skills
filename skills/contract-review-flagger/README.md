# Contract Review Flagger

## What it does

The Contract Review Flagger reads a contract and checks it against Start2 Asia's own contract standards. It returns one Excel workbook that shows:

- which of Start2's standard protections are in the contract, which are weak, and which are missing;
- clauses the client has added that Start2 would normally push back on;
- practical problems with the document itself, such as blanks, wrong dates, mismatched names or missing annexes;
- documents the contract relies on but that were not attached;
- for each issue, what it means for Start2, what to do about it, and Start2's standard wording to propose.

Each issue is rated Critical, High, Medium or Low, so the most important items are at the top.

It is a screen against Start2's own standards, not legal advice. Every Critical and High item, and every client-added clause, is confirmed by a person, and every contract still goes through the full sign-off chain.

### When to use it

| Situation | What it helps with |
|---|---|
| A client sends their own contract or terms | Spot clauses that go against Start2's position before you agree to anything. |
| Start2's template comes back with changes | See exactly where it now differs from the standard. |
| Before signing | Catch blanks, wrong dates, wrong entity names and missing annexes, which are hard to fix after signature. |
| A government or funder contract | Flag audit, clawback, payment and termination terms typical of public bodies, and list the general conditions they refer to. |
| A contract is already signed | Understand Start2's exposure and the obligations to keep track of during delivery. |
| A renewal is coming | Get a list of points to raise with the client in the next version. |

It works on English contracts where Start2 delivers a service or programme. The contract can be a PDF (including scanned pages) or a Word file.

## How a review works

1. **You share the contract.** Upload it and ask for a review.
2. **You answer four quick questions.** Before starting, the tool sends one message asking:
   - which Start2 company is signing, and in what role;
   - whether you can send any documents the contract mentions but that are not attached (for example general conditions or the original proposal);
   - whether legal terms should be explained in plain words (useful for readers who are not lawyers);
   - the purpose of the review: before signing, already signed, or ahead of a renewal.

   After your reply it does not stop to ask anything else.
3. **The tool reads the whole contract.** It compares every clause with Start2's standards, checks clauses the client may have added against Start2's playbook, runs 12 document checks, and goes over the money terms.
4. **It checks its own work.** Every quote is matched word for word against the contract, and the ratings are checked against the rating rules.
5. **You receive the workbook,** with a short summary of the most important points.

The purpose you give changes how actions are worded: before signing, they are requests to the client; after signing, they are checks and records to keep; for a renewal, they are points for the next version.

## How issues are rated

| Rating | What it means |
|---|---|
| **Critical** | Do not sign as it stands. For example: no limit on Start2's liability, the wrong Start2 company, payment that depends entirely on the client's judgement, or a client clause Start2 never accepts. |
| **High** | Fix it, or have the sign-off chain knowingly accept it, before signing. Real exposure on money, liability, intellectual property, data, disputes or scope. |
| **Medium** | Should be fixed and is usually negotiable. Raises the risk of a dispute rather than a direct loss. |
| **Low** | Housekeeping, optional clauses, or client clauses that are already within Start2's position. |

The starting point is how important the topic is: each Start2 standard clause has its own rating if it is missing or contradicted, and is rated one step lower if it is only partly covered. Two adjustments follow:

- **Up one step** when the clause lets the client alone judge Start2's work or payment, for example "acceptable to the client", "to the client's satisfaction" or "in its sole discretion". Those words are shown in bold in the quote.
- **Down one step** when Start2 has nothing to do about it, for example a standard government term that cannot be changed and has no effect on delivery. The action then starts "No action needed".

## What is in the workbook

### Read Me
A guide to the workbook: what each sheet and column means, and the rating scale.

### Summary

| Item | What it shows |
|---|---|
| Contract, Source file | The contract reviewed. |
| Status | Draft or Executed (signed). |
| Contract type | Service, Funding, Vendor or Other. |
| Whose paper | Start2's template unchanged, Start2's template changed, or the client's own paper. |
| Purpose | Before signing, already signed, or renewal, as given at the start. |
| Standards version | Which version of Start2's standards was used. |
| Our entity, Our role, Role basis, Counterparty | Which Start2 company is signing, its role, how that was confirmed, and the other party. |
| Critical, High, Medium, Low | The number of issues at each rating. These update automatically if you change a rating on the Findings sheet. |
| To confirm | How many Critical and High issues need a person to confirm them. |
| Documents not supplied | How many outside documents are missing. |
| Review lead time | The recommended review time before signature: 3 business days for Start2's unchanged template, 5 otherwise. |
| Sign-off chain | Director of People and Operations, then Regional Director of Innovation and Product Strategy, then CEO. |
| Key facts | Parties, dates, amounts, payment schedule, governing law, language and annexes, each with where it is in the contract. |

### Findings
One row per issue, most serious first.

| Column | What it shows |
|---|---|
| # | Row number. |
| Severity | Critical, High, Medium or Low. If a rating differs from the usual rule, a comment on the cell explains why. |
| Type | What kind of issue it is: a Start2 standard clause that is missing, partly covered or contradicted; a client-added clause (with Start2's position: accept, accept with conditions, escalate or reject); another unusual clause; a money issue; a document check that failed; or a missing document. |
| Clause | The Start2 standard clause, client clause or check concerned. |
| Where | The clause number and page in the contract. |
| Quote | The exact words from the contract, with the key words in bold. |
| Issue | What the clause says, what it means for Start2 in practice, and how it differs from Start2's standard. |
| Action | What to do next, who should do it, what to ask the client for, and a fallback if they say no. |
| Suggested language | Start2's standard wording, using the contract's own names for the parties, ready to propose to the client. Blank where no standard wording applies. |

Low and no-action items are kept short; Critical, High and Medium items are explained in full.

### Coverage
One row for each of Start2's 34 standard clauses, so you can see at a glance what the contract covers.

| Column | What it shows |
|---|---|
| ID, Clause | The Start2 standard clause. |
| Base severity | How serious it is if the clause is missing or contradicted. |
| Verdict | Conforming (meets the standard), Partial (something is missing), Deviant (contradicts the standard), Missing, Not supplied (the contract leaves this topic to a document that was not attached), or N/A. |
| Where | Where the clause is in the contract. |
| Severity | Worked out automatically from the verdict and the base severity. |
| Note | A short description of what is there or missing. Details are on the Findings sheet. |

### Checks
The 12 document checks Start2 runs before a draft leaves the company and again before signature.

| Column | What it shows |
|---|---|
| #, Check | The check, for example "every placeholder is filled" or "the company name is the same everywhere". |
| Result | Pass, Fail, N/A or Cannot verify. |
| Evidence | What was found, with page numbers. |
| Clauses to correct | For a failed check, a numbered list of the clauses or pages to correct and what to change. |

### Documents not supplied
Every outside document the contract relies on that was not attached, such as general conditions, the original proposal, policies or websites.

| Column | What it shows |
|---|---|
| Document | The document, as the contract names it. |
| Referenced at | Every place in the contract that mentions it. |
| Quotes | The contract text at each of those places. |
| Part of contract | Yes if the contract says the document forms part of it. Those also appear on the Findings sheet. |
| Governs | What the contract says the document covers. |
| Effect on this review | Which issues could not be fully checked without it. |
| Action | How to get it and what to check once you have it. |

## Good to know

- **Scanned pages** are read from the page images. Quotes from those pages should be checked against the original before you rely on them.
- **Missing documents** cannot be reviewed. If a contract relies on general conditions that were not attached, the related issues stay open until those conditions are read.
- **Only English contracts** where Start2 is the service provider are reviewed against the standards. If Start2 is the buyer, the workbook shows "Not assessed" and lists only general issues such as blanks and wrong dates.
- **You can edit the workbook.** Change a rating or verdict and the counts on the Summary update automatically.
- **Contracts stay private.** They are not sent to any outside service.
