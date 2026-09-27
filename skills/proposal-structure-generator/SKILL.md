---
name: proposal-structure-generator
description: Build a Start2 Group proposal skeleton (.docx) from a section checklist. Starts from the Public Partners master template, keeps only the headings ticked in the checklist, fills them with approved boilerplate from the Notion "Boilerplate Content Blocks" database, and applies the Start2 Group Proposal Writing Guide in code. Use whenever someone at Start2 Group wants a proposal skeleton, proposal structure, boilerplate proposal, or "build the proposal from the checklist", uploads a filled proposal checklist (ID / No. / Level / Section / Include), asks which boilerplate goes under each section, or asks for the Build Result of a checklist, even if they do not name this skill. Use it for government, public partner, tender or accelerator program proposals. Do not use it to analyze an RFP into a requirements tracker (tender-prep-xlsx) or for pricing models.
---

# Proposal Structure Generator

Turns a ticked checklist into a proposal skeleton that a writer then finishes. The skill never writes proposal content of its own: every paragraph comes from the master template or from a Reviewed Notion boilerplate block, and anything missing is marked so the writer sees the gap.

Scope today: **Public Partners** (government and public-partner projects). The Corporate template is bundled in `assets/` but has no checklist or section map yet. If someone asks for a corporate proposal, say it is not built yet and offer the Public Partners skeleton only if they want it.

## Files

| Path | What it is |
|---|---|
| `assets/Start2_Proposal_Template_for_Public_Partners.docx` | Master template. Every build starts from this file, never from scratch. |
| `assets/Start2_Group_Proposal_Writing_Guide.docx` | Formatting and wording standard. The build script enforces the rules that can be checked in code. |
| `assets/checklist_public_partners.xlsx` | Blank checklist to hand out: ID, No., Level, Section, Include. |
| `assets/section_map_public_partners.json` | Per checklist ID: template content (Table, Placeholder, Fixed text, Replaced, None), Notion block path, snapshot status. |
| `scripts/build_result.py` | Adds the Build Result column to a checklist. |
| `scripts/make_blocks.py` | Converts Notion rows into `blocks.json` for the build. |
| `scripts/build_proposal.py` | Builds the .docx. |
| `examples/` | A filled checklist, a Notion snapshot, and the proposal built from them. |

Python needs `python-docx`, `openpyxl`, `lxml` (`pip install python-docx openpyxl lxml` if an import fails).

## Workflow

### 1. Get the checklist

If the user has no checklist, give them `assets/checklist_public_partners.xlsx` and explain: set Include to Yes or No in column E; rows marked Always cannot be switched off (Cover Page, Table of Contents, Company Information/Cover Page, Joint Submission, Executive Summary, Compliance and Eligibility, Company Overview).

If they upload one, check it has an ID column and an Include column. IDs (PP-001 ...) are the join key to the section map. `build_result.py` warns about IDs it does not know, and the build treats them as headings with no content (empty note). Do not renumber or rename IDs.

### 2. Fetch the boilerplate from Notion (live, every time)

The snapshot status in the section map goes stale, so always read the current database:

- Data source: `collection://3d40b29a-394d-80f1-b7cb-000b905399f6` (Boilerplate Content Blocks, under the Proposal Structure Generator page).
- Query it in **rows mode** (not SQL). SQL mode drops bold, italics and line breaks.
- Save the result unchanged as `notion_rows.json`, then run:

```bash
python scripts/make_blocks.py notion_rows.json -o blocks.json
```

It prints any section map entry that did not match exactly one Notion row. If a block was renamed or moved in Notion, the match fails; tell the user which one rather than guessing.

This skill only reads Notion. Do not edit the database from here: writing rich text back through the connector auto-links dotted names (start2.group, 1MX.AI, Scale-up.NRW) and can break bold markers. Content fixes belong in Notion itself, by a person, after a backup.

If Notion is not connected, say so. Building from `examples/sample_blocks_public_partners.json` is acceptable only when the user agrees, and the result must be labeled as built from the 27 September 2026 snapshot.

### 3. Show the Build Result (optional, fast)

```bash
python scripts/build_result.py checklist.xlsx -o checklist_build_result.xlsx
```

This adds a Build Result column that says what each row will produce. Useful when the user wants to review choices before the document is built, or asks only for the Build Result.

### 4. Build the proposal

```bash
python scripts/build_proposal.py --checklist checklist.xlsx --blocks blocks.json \
  -o "<Client>_<Proposal Name> <Year> with Start2 Group_V1.docx"
```

Name the file per the writing guide: `[Name of Client]_[Proposal Name] [Year] with Start2 Group_V(n)`. Ask for client and proposal name if you do not have them; otherwise use `Sample Client_Sample Program <year>` and say so.

The script prints one line per checklist row saying what it did. Validate the output with the docx skill's `validate.py` and, if LibreOffice is available, render it and look at the pages before handing it over.

### 5. Report

Tell the user, briefly:
- which sections carry Notion text, which got the note "Subheader was empty.", and which headings were added because the template lacks them;
- that Word will ask to update fields on open (this refreshes the Table of Contents);
- which placeholders remain for the writer (cover fields such as [Client Name], `[to-update ...]` markers from Notion, template table rows).

## Build rules

These are what `build_result.py` and `build_proposal.py` implement. Keep the two in agreement if either changes.

- A row is built only if Include is Yes or Always and every parent heading above it is included. A child under an excluded parent shows "Omitted (parent heading excluded)".
- **Reviewed** Notion block: heading plus the block text. Template paragraphs under that heading are replaced; template tables stay.
- **Pending Review, empty, or no Notion block**: heading plus the note "Subheader was empty." directly under it. Template tables stay. Pending Review text is never inserted, because it has not been approved.
- **Not used** (template owns the section, for example Company Information, Compliance and Eligibility, Price Summary): heading plus the template's own table or text.
- A heading switched on with no content and no subheads switched on gets the empty note.
- **Company Overview**: the template's text is removed and the three Notion blocks (About Start2 Group, Geographical Presence, Key Benefits) are inserted as body text without their own headings.
- Template placeholder paragraphs (`[Insert write-up here]` and similar) are always removed from included sections. Blank template headings are removed so they do not appear in the TOC.
- Headings the template does not have (for example Contact Details, verticals such as Fintech) are added at their checklist position with the template heading styles.

## Writing guide rules enforced in code

`build_proposal.py` applies these after assembling the document:

- Palette normalized to the template values: Dark Purple 51389D, Lilac F2EFFE, Light Grey EFF4FC, Midnight Grey 374050, Dark Grey 888888.
- Font set to Inter throughout (the template itself uses Source Sans Pro; the guide says Inter, no exceptions).
- Heading styles: H1 20pt bold Dark Purple; H2, H3, H4 16, 14, 12pt bold Midnight Grey. Headings number themselves (1, 1.1, 1.1.1) through the template's heading numbering.
- Lists use Word numbering, never typed numerals. A typed "1." starts a new list; a higher number continues the current one.
- Wording: "programme" to "program", "BMWK" to "BMWE", em or en dashes to commas, a bare "Start2" to "Start2 Group".
- Links from Notion are dropped; the link text stays.

Rules the script cannot check (hype words, closing slogans, client naming conventions, figures against the canonical numbers source) remain the writer's job. Mention them in the report if the Notion text visibly breaks them.

## Maintaining the skill

- New Notion block for an existing section: nothing to change; it is picked up on the next live fetch.
- New section: add a row to `assets/checklist_public_partners.xlsx` with a new ID, and add the same ID to `assets/section_map_public_partners.json` with its template content and Notion block path.
- Template heading renamed: the Section text in the checklist must match the template heading text, or the build adds it as a new heading instead of using the template's.
- Corporate proposals: needs `checklist_corporate.xlsx`, `section_map_corporate.json`, and the build pointed at `--template assets/Start2_Proposal_Template_for_Corporates.docx --map assets/section_map_corporate.json`.
