#!/usr/bin/env python3
"""Render a contract review into the standard review workbook.

Usage:
  build_review_workbook.py <standards.json> <review.json> <out.xlsx>
  build_review_workbook.py <standards.json> --template <out.xlsx>

review.json (all keys optional):
  summary:  contract, file, status (Draft|Executed), contract_type (Service|Funding|Vendor|Other),
            paper, standards_version, our_entity, our_role (Provider|Buyer|Other), role_basis, counterparty
  facts:    [{fact, value, where}]
  findings: [{severity, type, clause, where, quote, issue, action}]
  coverage: {CLAUSE_ID: {verdict, where, note}}
  checks:   {"1": {result, evidence}, ...}   (keys are Execution Check numbers)
Counts and the recommendation are formulas over the Findings sheet, so edits in Excel flow through.
"""
import json
import sys

import openpyxl
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

SEV = ["Critical", "High", "Medium", "Low"]
TYPES = ["Missing", "Partial", "Deviant", "Client: Reject", "Client: Escalate", "Client: Conditional",
         "Client: Accept", "Unclassified clause", "Commercial", "Execution", "Other"]
VERDICTS = ["Conforming", "Partial", "Deviant", "Missing", "N/A"]
RESULTS = ["Pass", "Fail", "N/A", "Cannot verify"]
PAPER = ["Start2 template, unmodified", "Start2 template, modified", "Client or third-party paper"]
SIGNOFF = ("1. Director of People and Operations; 2. Regional Director of Innovation and Product Strategy; 3. CEO. "
           "Applies to every contract.")
CHECK_LABEL_OVERRIDE = {11: "Cross-references in the contract point to clauses and annexes that exist and are correctly numbered."}

HFILL = PatternFill("solid", fgColor="FF1F3864"); HFONT = Font(name="Arial", size=10, bold=True, color="FFFFFFFF")
SFILL = PatternFill("solid", fgColor="FFD9E1F2"); BFONT = Font(name="Arial", size=10); BOLD = Font(name="Arial", size=10, bold=True)
thin = Side(style="thin", color="FFBFBFBF"); BORDER = Border(left=thin, right=thin, top=thin, bottom=thin)
COLORS = {"Critical": "FFF4B6B6", "High": "FFF9D6A5", "Medium": "FFFFF2B3", "Low": "FFDCEBF7"}
MAXROW = 300


def cell(ws, r, c, v=None, font=BFONT, fill=None, wrap=True):
    x = ws.cell(r, c, v)
    x.font = font; x.border = BORDER
    x.alignment = Alignment(wrap_text=wrap, vertical="top")
    if fill: x.fill = fill
    return x


def header(ws, heads, widths):
    for j, (h, w) in enumerate(zip(heads, widths), 1):
        c = cell(ws, 1, j, h, HFONT, HFILL); c.alignment = Alignment(wrap_text=True, vertical="center")
        ws.column_dimensions[get_column_letter(j)].width = w
    ws.freeze_panes = "A2"


def colour(ws, rng):
    for k, col in COLORS.items():
        ws.conditional_formatting.add(rng, CellIsRule(operator="equal", formula=[f'"{k}"'], fill=PatternFill("solid", bgColor=col, fgColor=col)))


def dropdown(ws, rng, items):
    dv = DataValidation(type="list", formula1='"' + ",".join(items) + '"', allow_blank=True)
    ws.add_data_validation(dv); dv.add(rng)


def readme(ws):
    rows = [
        ("S", "What this workbook is"),
        ("One contract per workbook", "Produced by the contract review skill from the contract text and the Start2 standards workbook, then checked by a person. Counts and the recommendation update when you edit the Findings sheet."),
        ("S", "How to use it"),
        ("1. Summary", "Read the role, the counts and the recommendation. Check the role guess first: if it is wrong, nothing else applies."),
        ("2. Findings", "Work down the list. It is sorted Critical to Low. Fix, negotiate or accept each item, and change Severity or Type if you disagree. Every Critical, High and client-clause finding must be confirmed by a person."),
        ("3. Coverage", "Use it to see which standard clauses are present, partial, deviant or missing. It is a view; issues are listed in Findings."),
        ("4. Checks", "The 12 execution checks. A failed check also appears in Findings."),
        ("S", "Severity"),
        ("Critical", "Do not sign (if already executed, escalate at once). Reject threshold met, hard stop, wrong entity, no liability cap, blank essential fields."),
        ("High", "Fix, or have the full sign-off chain knowingly accept it, before signing. Material cash, liability, IP, data, forum or scope exposure."),
        ("Medium", "Should be fixed. Negotiable. Raises dispute risk but not direct cash loss."),
        ("Low", "Housekeeping, optional clauses, accepted client clauses."),
        ("S", "Sheet: Summary (Item / Value / Where)"),
        ("Contract", "Name or title of the contract being reviewed."),
        ("Source file", "File name of the contract that was reviewed."),
        ("Status", "Draft (unsigned) or Executed (signed). Executed contracts get remediation wording instead of sign/no-sign."),
        ("Contract type", "Service, Funding, Vendor or Other. Funding agreements (grants, claims, audits) read the fee and cost clauses differently."),
        ("Whose paper", "Start2 template unmodified, Start2 template modified, or client or third-party paper. Sets the review lead time: 3 business days for the unmodified template, otherwise 5."),
        ("Standards version", "Version of the standards workbook the contract was checked against."),
        ("Our entity", "The Start2 entity in this contract. Guessed from the entity list and the text when not obvious."),
        ("Our role", "Provider, Buyer or Other. The standards cover provider-side contracts only. If the role is not Provider, standards coverage is not applied and the recommendation says so."),
        ("Role basis", "One sentence on why that role was chosen. Always filled when the role was guessed."),
        ("Counterparty", "The other party."),
        ("Critical / High / Medium / Low", "Formulas: number of Findings at each severity."),
        ("Recommendation", "Formula. Draft: any Critical = Escalate; any High = Proceed with named conditions; otherwise Proceed. Executed: no signature gate; Critical items are escalated and High items logged for amendment or renewal."),
        ("Review lead time", "Formula from Whose paper."),
        ("Sign-off chain", "Fixed. Every contract goes to all three approvers in order."),
        ("Key facts (Fact / Value / Where)", "Facts used in the review: parties, dates, amounts, law, forum, language, annexes, with arithmetic checks. Where gives the contract reference and page."),
        ("S", "Sheet: Findings (one row per issue)"),
        ("#", "Running number."),
        ("Severity", "Critical, High, Medium or Low (drop-down)."),
        ("Type", "Missing, Partial or Deviant (a standard clause); Client: Reject, Escalate, Conditional or Accept (a client-added clause matched to the playbook); Unclassified clause (not in the standard or playbook, generic screen); Commercial (fee, dates, arithmetic); Execution (a failed check); Other."),
        ("Clause", "Standard clause ID (for example LOL), the playbook row name, or Check n."),
        ("Where", "Contract clause number and page, for example 13.1 (p. 10). 'Not in contract' for an absent clause."),
        ("Quote", "Verbatim text from the contract. Scanned contracts are transcribed from page images, so check the page before relying on a quote."),
        ("Issue", "What is wrong and why it matters, against the standard."),
        ("Action", "What to do: insert, change, accept, escalate, or confirm."),
        ("S", "Sheet: Coverage (one row per standard clause)"),
        ("ID", "Stable clause key from the standards workbook."),
        ("Clause", "Clause name."),
        ("Base severity", "Severity if the clause is missing or deviant. Editable for this contract (for example raise anti-bribery to Medium for a government counterparty). n/a for internal rules."),
        ("Verdict", "Conforming, Partial, Deviant, Missing, or N/A (drop-down)."),
        ("Where", "Contract clause number and page where the clause was found."),
        ("Severity", "Formula. Missing or Deviant = Base severity; Partial = one level lower (floor Low); Conforming or N/A = '-'."),
        ("Note", "One line on what is present or absent. Details are in Findings."),
        ("S", "Sheet: Checks (one row per execution check)"),
        ("#", "Number of the check in the standards workbook."),
        ("Check", "What is verified before a draft leaves Start2 and again before signature."),
        ("Result", "Pass, Fail, N/A or Cannot verify (drop-down)."),
        ("Evidence", "What was seen, with page references."),
        ("S", "Rules"),
        ("Counts", "Counts and the recommendation use the Findings sheet only. Coverage severity is a view and is not counted."),
        ("Role", "The role is guessed when unclear and recorded on Summary. The skill never stops to ask."),
        ("Not legal advice", "A screen against Start2 standards. Decisions follow the sign-off chain."),
    ]
    header(ws, ["Item", "Description"], [34, 120]); ws.freeze_panes = None
    r = 2
    for a, b in rows:
        if a == "S":
            for j in (1, 2): cell(ws, r, j, b if j == 1 else None, BOLD, SFILL)
            ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=2)
        else:
            cell(ws, r, 1, a, BOLD); cell(ws, r, 2, b)
        r += 1


def build(standards, review, out):
    review = review or {}
    S = review.get("summary", {})
    wb = openpyxl.Workbook()
    ws = wb.active; ws.title = "Read Me"; readme(ws)

    # ---- Summary
    ws = wb.create_sheet("Summary"); header(ws, ["Item", "Value", "Where"], [34, 90, 30]); ws.freeze_panes = None
    r = 2; pos = {}
    def section(t):
        nonlocal r
        for j in (1, 2, 3): cell(ws, r, j, t if j == 1 else None, BOLD, SFILL)
        r += 1
    def row(label, key, value=None):
        nonlocal r
        cell(ws, r, 1, label, BOLD); cell(ws, r, 2, value); cell(ws, r, 3)
        pos[key] = r; r += 1
    section("Contract")
    for label, key in (("Contract", "contract"), ("Source file", "file"), ("Status", "status"), ("Contract type", "contract_type"),
                       ("Whose paper", "paper"), ("Standards version", "standards_version")):
        row(label, key, S.get(key))
    section("Our side")
    for label, key in (("Our entity", "our_entity"), ("Our role", "our_role"), ("Role basis", "role_basis"), ("Counterparty", "counterparty")):
        row(label, key, S.get(key))
    dropdown(ws, f"B{pos['status']}", ["Draft", "Executed"]); dropdown(ws, f"B{pos['contract_type']}", ["Service", "Funding", "Vendor", "Other"])
    dropdown(ws, f"B{pos['paper']}", PAPER); dropdown(ws, f"B{pos['our_role']}", ["Provider", "Buyer", "Other"])
    section("Result")
    for k in SEV: row(k, k, f'=COUNTIF(Findings!$B$2:$B${MAXROW},"{k}")')
    st, ro, c, h = (f"B{pos[x]}" for x in ("status", "our_role", "Critical", "High"))
    row("Recommendation", "rec",
        f'=IF(OR({st}="",{ro}=""),"",IF({ro}<>"Provider","Not assessed: the standards cover provider-side contracts only",'
        f'IF({st}="Executed",IF({c}>0,"Executed: escalate Critical items and log High items for amendment or renewal",'
        f'IF({h}>0,"Executed: log High items for amendment or renewal","Executed: no action required")),'
        f'IF({c}>0,"Escalate",IF({h}>0,"Proceed with named conditions","Proceed")))))')
    pp = f"B{pos['paper']}"
    row("Review lead time", "lead", f'=IF({pp}="","",IF({pp}="Start2 template, unmodified","3 business days","5 business days"))')
    row("Sign-off chain", "chain", SIGNOFF)
    for k in SEV: ws.cell(pos[k], 2).alignment = Alignment(horizontal="left", vertical="top")
    colour(ws, f"A{pos['Critical']}:A{pos['Low']}")
    # colour the label cells directly (static) for readability
    for k in SEV: ws.cell(pos[k], 1).fill = PatternFill("solid", fgColor=COLORS[k])
    section("Key facts")
    for f in review.get("facts", []):
        cell(ws, r, 1, f.get("fact"), BOLD); cell(ws, r, 2, f.get("value")); cell(ws, r, 3, f.get("where")); r += 1

    # ---- Findings
    ws = wb.create_sheet("Findings")
    header(ws, ["#", "Severity", "Type", "Clause", "Where", "Quote", "Issue", "Action"], [5, 11, 18, 18, 22, 50, 62, 44])
    order = {k: i for i, k in enumerate(SEV)}
    fl = sorted(review.get("findings", []), key=lambda f: order.get(f["severity"], 9))
    for i, f in enumerate(fl, 1):
        for j, v in enumerate([i, f["severity"], f["type"], f["clause"], f.get("where"), f.get("quote"), f.get("issue"), f.get("action")], 1):
            cell(ws, i + 1, j, v)
    dropdown(ws, f"B2:B{MAXROW}", SEV); dropdown(ws, f"C2:C{MAXROW}", TYPES)
    colour(ws, f"B2:B{MAXROW}"); ws.auto_filter.ref = f"A1:H{max(len(fl), 1) + 1}"

    # ---- Coverage
    ws = wb.create_sheet("Coverage")
    header(ws, ["ID", "Clause", "Base severity", "Verdict", "Where", "Severity", "Note"], [14, 36, 12, 14, 26, 12, 70])
    cov = review.get("coverage", {})
    clauses = [x for x in standards["clauses"]]
    for i, x in enumerate(clauses, 2):
        v = cov.get(x["id"], {})
        cell(ws, i, 1, x["id"], BOLD); cell(ws, i, 2, x["clause"]); cell(ws, i, 3, x["base_severity"]); cell(ws, i, 4, v.get("verdict"))
        cell(ws, i, 5, v.get("where")); cell(ws, i, 7, v.get("note"))
        cell(ws, i, 6, f'=IF(D{i}="","",IF(OR(D{i}="Conforming",D{i}="N/A",C{i}="n/a"),"-",IF(D{i}="Partial",'
                       f'INDEX({{"Low","Low","Medium","High"}},MATCH(C{i},{{"Low","Medium","High","Critical"}},0)),C{i})))')
    n = len(clauses) + 1
    dropdown(ws, f"C2:C{n}", SEV + ["n/a"]); dropdown(ws, f"D2:D{n}", VERDICTS)
    colour(ws, f"C2:C{n}"); colour(ws, f"F2:F{n}"); ws.auto_filter.ref = f"A1:G{n}"

    # ---- Checks
    ws = wb.create_sheet("Checks"); header(ws, ["#", "Check", "Result", "Evidence"], [5, 80, 14, 80])
    res = review.get("checks", {})
    for i, ck in enumerate(standards["execution_checks"], 2):
        v = res.get(str(ck["id"]), {})
        label = CHECK_LABEL_OVERRIDE.get(ck["id"], ck["check"])
        cell(ws, i, 1, ck["id"]); cell(ws, i, 2, label); cell(ws, i, 3, v.get("result")); cell(ws, i, 4, v.get("evidence"))
    dropdown(ws, f"C2:C{len(standards['execution_checks']) + 1}", RESULTS)
    wb.save(out)


if __name__ == "__main__":
    std = json.load(open(sys.argv[1]))
    if sys.argv[2] == "--template":
        build(std, None, sys.argv[3])
    else:
        build(std, json.load(open(sys.argv[2])), sys.argv[3])
    print("wrote", sys.argv[-1])
