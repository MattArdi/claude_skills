#!/usr/bin/env python3
"""Parse the Start2 Asia Contract Standards workbook into structured JSON.

Usage: parse_standards.py <standards.xlsx> [out.json]

Sheets are located by their numeric prefix ("1. Clauses", ...), so renamed
suffixes do not break parsing. Missing or reshaped sheets raise, never skip.
Clause cross-references are {{ID}} tokens; they are not resolved here (see
assemble_agreement.py).
"""
import json
import re
import sys
from pathlib import Path

import openpyxl

CLAUSE_KEYS = {
    "ID": "id", "Order": "order", "#": "number", "Tier": "tier", "Client-facing": "client_facing",
    "Clause": "clause", "Draft heading": "draft_heading", "What must be on the page": "required_content",
    "Why it protects Start2": "rationale", "Mutuality": "mutuality", "Cap position": "cap_position",
    "Cap type": "cap_type", "Cap measure": "cap_measure", "Negotiation stance": "negotiation_stance",
    "Standard language": "standard_language", "Notes / placeholders": "notes",
    "Open placeholders": "open_placeholders", "Survives termination": "survives", "Reference clause": "reference_clause",
}
TOKEN = re.compile(r"\{\{([A-Z][A-Z0-9-]*)\}\}")


def clean(v):
    if isinstance(v, str):
        v = v.strip()
        return v or None
    return v


def rows(ws, header_row=1):
    hdr = [clean(c.value) for c in ws[header_row]]
    for r in ws.iter_rows(min_row=header_row + 1, values_only=True):
        if all(clean(c) is None for c in r):
            continue
        yield {h: clean(v) for h, v in zip(hdr, r) if h}


def sheet(wb, n):
    for ws in wb:
        if ws.title.startswith(f"{n}."):
            return ws
    raise KeyError(f"sheet {n} not found")


def parse(path):
    wb = openpyxl.load_workbook(path)
    out = {"source": Path(path).name}

    clauses = []
    for d in rows(sheet(wb, 1)):
        c = {CLAUSE_KEYS[h]: d.get(h) for h in CLAUSE_KEYS}
        c["refs"] = sorted(set(TOKEN.findall(" ".join(str(c[k] or "") for k in ("standard_language", "notes", "cap_measure", "reference_clause")))))
        clauses.append(c)
    out["clauses"] = clauses

    out["decisions"] = [
        {"ref": d["Ref"], "decision": d["Decision"], "options": d.get("Options"),
         "recommendation_claude": d.get("Recommendation - Claude"),
         "recommendation_usa": d.get("Recommendation - U-sa"),
         "affects": d.get("What it affects"), "settled": False}  # no decision is marked final in the source
        for d in rows(sheet(wb, 2))
    ]
    out["client_inserted_clauses"] = [
        {"clause": d["Clause client may insert"], "start2_position": d["Start2 position"],
         "rejection_threshold": d["Rejection threshold"]} for d in rows(sheet(wb, 3))
    ]
    out["execution_checks"] = [
        {"id": i + 1, "check": d["Check before every draft leaves Start2, and again before signature"]}
        for i, d in enumerate(rows(sheet(wb, 4)))
    ]
    review, reviewer_output = [], None
    for d in rows(sheet(wb, 5)):
        if isinstance(d.get("Order"), int):
            review.append({"order": d["Order"], "pass": d["Review pass"], "what_to_check": d["What to check and why"]})
        elif d.get("Order") and not d["Order"].startswith("Reviewer"):
            reviewer_output = d["Order"]
    out["review_method"] = {"passes": review, "reviewer_output_spec": reviewer_output}
    out["process_and_authority"] = [
        {"topic": d["Topic"], "rule": d["Rule / guidance"], "decision_ref": d.get("Decision Ref")}
        for d in rows(sheet(wb, 6))
    ]

    # Audit: duplicate IDs, tokens naming no clause, decision refs naming no decision.
    ids = [c["id"] for c in clauses]
    known = set(ids)
    dec_ids = {x["ref"] for x in out["decisions"]}
    dec_cited = sorted({m for c in clauses for k in ("standard_language", "notes", "cap_measure")
                        for m in re.findall(r"D-0\d", c[k] or "")})
    out["_audit"] = {
        "duplicate_ids": sorted({i for i in ids if ids.count(i) > 1}),
        "tokens_naming_no_clause": sorted({r for c in clauses for r in c["refs"] if r not in known}),
        "decision_refs_undefined": [d for d in dec_cited if d not in dec_ids],
    }
    return out


if __name__ == "__main__":
    src = sys.argv[1]
    dst = Path(sys.argv[2] if len(sys.argv) > 2 else "standards.json")
    data = parse(src)
    dst.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    tiers = {}
    for c in data["clauses"]:
        tiers[c["tier"]] = tiers.get(c["tier"], 0) + 1
    print(f"wrote {dst}: clauses {tiers}, {len(data['decisions'])} decisions, "
          f"{len(data['client_inserted_clauses'])} client clauses, {len(data['execution_checks'])} exec checks; audit {data['_audit']}")
