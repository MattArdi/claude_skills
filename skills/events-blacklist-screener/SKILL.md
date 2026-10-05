---
name: events-blacklist-screener
description: Screen an event guest, RSVP, registration, attendee or invite list against the Start2 events blacklist and return the same Excel with one extra column, "Blacklist Status" (OK / Review / Blacklisted). Use whenever someone asks to check, vet, screen, cross-check or clean a guest list, attendee list, registration export, RSVP sheet or invite list against the blacklist, or asks "is anyone on this list blacklisted", even if the list has odd columns, a title row above the headers, separate first/last name columns, or arrives as csv.
---

# Events Blacklist Screener

Takes a guest list in any reasonable spreadsheet layout, checks every person against the blacklist workbook, and hands back the same workbook with one new column, `Blacklist Status`. Nothing else in the file changes, so the owner of the list can keep working in their own file.

## Inputs

1. **Guest list**: `.xlsx`, `.xlsm` or `.csv`. Legacy `.xls` must be converted to `.xlsx` first.
2. **Blacklist workbook**: the cleaned `Events_Blacklist_Clean.xlsx` (sheet `Blacklist`, columns Name, Also Registered As, Company, Email(s), LinkedIn, ...). It holds personal data, so it is not stored in this repo. Ask the user for it if it is not attached or named. Never paste its contents into chat beyond the matched rows.

## Workflow

1. **Dry run to see the mapping.** The guest list will not match the blacklist layout, so the script first maps each sheet's columns to roles (name, first, last, email, company, LinkedIn):

   ```bash
   python scripts/screen.py --input guests.xlsx --blacklist Events_Blacklist_Clean.xlsx --dry-run
   ```

   The script finds the header row (it may sit under a title block), recognises common header wordings ("Attendee", "Organisation", "E-mail", "Surname"...), and sniffs columns whose headers say nothing but whose cells are emails or LinkedIn URLs. It also pulls emails out of name cells such as `Jane Doe <jane@x.com>`, accepts several email columns, and splits `;` separated emails.

2. **Check the printed mapping against the sheet.** Open the guest file if anything looks off: a sheet skipped, a wrong header row, name and company swapped, an ID column read as a name. Fix with an explicit map and re-run the dry run:

   ```bash
   --map '{"header_row": 3, "name": "B", "email": ["E", "F"], "company": "D"}'
   # several sheets: {"Day 1": {...}, "Day 2": {...}}
   ```

   A wrong mapping silently produces wrong statuses, so this check is the step that matters most.

3. **Run for real**, keeping the original file name so the result is "the same Excel":

   ```bash
   python scripts/screen.py --input guests.xlsx --blacklist Events_Blacklist_Clean.xlsx --out <outputs dir>/guests.xlsx
   ```

   Never overwrite the user's original. A `.csv` input comes back as `.xlsx`.

4. **Report in chat.** Give the counts, then a table of every `Review` and `Blacklisted` row: sheet, row, guest, status, and the `why` text from the script. The reasons live in chat only, because the workbook must stay identical apart from the one column. Mention rows left blank and any warnings.

## Decision rules

| Evidence | Status |
|---|---|
| Exact email match, against any of the blacklisted person's addresses | `Blacklisted` |
| Exact LinkedIn profile match (`/in/<slug>`) | `Blacklisted` |
| Name only: exact, reordered ("Chan Eddie" / "Eddie Chan"), initials ("E H Lim"), fuzzy (typos) | `Review` |
| Single-token name ("Joanne"), only when company or a non-free email domain also matches | `Review` |
| Nothing matched | `OK` |
| Row has no name, email or LinkedIn | blank, so a row that could not be checked is never shown as OK |

Why these rules:
- Emails and LinkedIn URLs identify one person. Names do not: common names (Peter Tan, Linda Lim) collide, and wrongly excluding a real guest is costly. So name matches never reach `Blacklisted`; a human decides.
- A lone first name with no corroboration is too weak to flag, so it stays `OK`.
- Free-mail domains (gmail, yahoo, ...) never count as corroboration.
- Email beats name: if both fire, the status is `Blacklisted`.

## Output contract

- Same workbook, same sheets, same cell styles. One column, `Blacklist Status`, appended after the last column of each screened sheet, header styled like its neighbour. If the column already exists it is overwritten rather than duplicated.
- Values are exactly `OK`, `Review`, `Blacklisted`.
- Sheets with no name, email or LinkedIn column are left untouched and reported.
- openpyxl rewrites the file, so charts, images and Excel tables may not survive. The script warns when it sees them; tell the user and check the output.

## Tuning

Thresholds and noise lists (fuzzy cut-off 0.88, free-mail domains, company suffixes) are constants at the top of `scripts/screen.py`. Name matching is order-insensitive and accent-insensitive; blacklist aliases ("Also Registered As") are matched as extra names.
