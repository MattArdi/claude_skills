#!/usr/bin/env python3
"""Parse the Start2 Asia Contract Standards workbook into structured JSON.

Usage: parse_standards.py <standards.xlsx> [out.json]

Sheets are located by their numeric prefix ("1. Must Have", ...), so renamed
suffixes do not break parsing. Missing or reshaped sheets raise, never skip.
"""
import json
import re
import sys
from pathlib import Path

import openpyxl

# Must Have # -> Draft Clause Language # (sheet 1 -> sheet 10). Must Have 14 is an internal rule with no draft clause.
MUST_TO_DRAFT = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 10: 10, 11: 11, 12: 12, 13: 13,
                 14: None, 15: 14, 16: 15, 17: 16, 18: 17, 19: 18, 20: 19, 21: 20, 22: 21, 23: 22,
                 24: 23, 25: 24, 26: 25, 27: 26, 28: 27}


def clean(v):
    if v is None:
        return None
    if isinstance(v, str):
        v = v.strip()
        return v or None
    return v


def rows(ws, header_row=1):
    hdr = [clean(c.value) for c in ws[header_row]]
    for r in ws.iter_rows(min_row=header_row + 1, values_only=True):
        if all(clean(c) is None for c in r):
            continue
        yield {h: clean(v) for h, v in zip(hdr, r) if h}, [clean(v) for v in r]


def sheet(wb, n):
    for ws in wb:
        if ws.title.startswith(f"{n}."):
            return ws
    raise KeyError(f"sheet {n} not found")


def placeholders(text):
    """Bracketed fill-ins in draft language, e.g. [X]% or [Start Date]."""
    return sorted(set(re.findall(r"\[[^\]]+\]", text or "")))


def refs_to_decisions(text):
    return sorted(set(re.findall(r"\bD-0\d\b|\bDecision D-\d+", text or "")))


def parse(path):
    wb = openpyxl.load_workbook(path)
    out = {"source": Path(path).name}

    drafts = {"must": {}, "good": {}, "nice": {}}
    tier = None
    for r in sheet(wb, 10).iter_rows(min_row=2, values_only=True):
        a, b, c, d = (clean(x) for x in r[:4])
        if a in ("MUST HAVE", "GOOD TO HAVE", "NICE TO HAVE"):
            tier = {"MUST HAVE": "must", "GOOD TO HAVE": "good", "NICE TO HAVE": "nice"}[a]
            continue
        if a is None:
            continue
        drafts[tier][a] = {"id": a, "clause": b, "language": c, "notes": d,
                           "placeholders": placeholders(c)}

    must = []
    for d, _ in rows(sheet(wb, 1)):
        n = d["#"]
        di = MUST_TO_DRAFT[n]
        must.append({
            "id": n, "clause": d["Clause"], "required_content": d["What must be on the page"],
            "rationale": d["Why it protects Start2"], "mutuality": d["Mutuality"],
            "cap_position": d["Cap position"], "reference_clause": d["Reference clause"],
            "client_facing": di is not None,
            "draft": drafts["must"].get(di) if di else None,
        })
    out["must_have"] = must

    out["good_to_have"] = [
        {"clause": d["Clause"], "description": d["Description"], "negotiation_stance": d["Negotiation stance"],
         "draft": next((v for v in drafts["good"].values() if v["clause"] and v["clause"].split()[0] in (d["Clause"] or "")), None)}
        for d, _ in rows(sheet(wb, 2))
    ]
    # Sheet 3 has a trailing free-text rule row (A6) with no description.
    nice, rule = [], None
    for d, _ in rows(sheet(wb, 3)):
        if d.get("Description") is None:
            rule = d["Clause"]
        else:
            nice.append({"clause": d["Clause"], "description": d["Description"]})
    out["nice_to_have"] = nice
    out["nice_to_have_rule"] = rule
    out["draft_language_extras"] = {"good": drafts["good"], "nice": drafts["nice"]}

    out["decisions"] = [
        {"ref": d["Ref"], "decision": d["Decision"], "options": d.get("Options"),
         "recommendation_claude": d.get("Recommendation - Claude"),
         "recommendation_usa": d.get("Recommendation - U-sa"),
         "affects": d.get("What it affects"),
         "settled": False}  # no decision is marked final in the source
        for d, _ in rows(sheet(wb, 4))
    ]

    out["client_inserted_clauses"] = [
        {"clause": d["Clause client may insert"], "start2_position": d["Start2 position"],
         "rejection_threshold": d["Rejection threshold"]}
        for d, _ in rows(sheet(wb, 5))
    ]

    out["caps"] = [
        {"status": d["Status"], "item": d["Item"], "measure": d["Measure"], "notes": d["Notes"],
         "drafted_in": d["Covered in which drafted Clause"]}
        for d, _ in rows(sheet(wb, 6))
    ]

    out["execution_checks"] = [{"id": i + 1, "check": d["Check before every draft leaves Start2, and again before signature"]}
                               for i, (d, _) in enumerate(rows(sheet(wb, 7)))]

    review, reviewer_output = [], None
    for d, raw in rows(sheet(wb, 8)):
        if isinstance(d.get("Order"), int):
            review.append({"order": d["Order"], "pass": d["Review pass"], "what_to_check": d["What to check and why"]})
        elif d.get("Order") and not d["Order"].startswith("Reviewer"):
            reviewer_output = d["Order"]
    out["review_method"] = {"passes": review, "reviewer_output_spec": reviewer_output}

    out["process_and_authority"] = [
        {"topic": d["Topic"], "rule": d["Rule / guidance"], "decision_ref": d.get("Decision Ref")}
        for d, _ in rows(sheet(wb, 9))
    ]

    # Cross-reference audit: decision refs cited anywhere vs. refs that exist.
    existing = {x["ref"] for x in out["decisions"]}
    cited = {}
    def scan(where, text):
        for m in re.findall(r"D-0\d", text or ""):
            cited.setdefault(m, []).append(where)
    for m in must:
        if m["draft"]:
            scan(f"draft:{m['clause']}", (m["draft"]["language"] or "") + (m["draft"]["notes"] or ""))
    for c in out["caps"]:
        scan(f"caps:{c['item']}", (c["measure"] or "") + (c["notes"] or ""))
    out["_audit"] = {"decision_refs_cited_but_undefined": {k: v for k, v in cited.items() if k not in existing},
                     "decision_refs_cited": cited}
    return out


if __name__ == "__main__":
    src = sys.argv[1]
    dst = Path(sys.argv[2] if len(sys.argv) > 2 else "standards.json")
    data = parse(src)
    dst.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    print(f"wrote {dst}: {len(data['must_have'])} must-have, {len(data['good_to_have'])} good, "
          f"{len(data['nice_to_have'])} nice, {len(data['decisions'])} decisions, "
          f"{len(data['client_inserted_clauses'])} client clauses, {len(data['caps'])} caps, "
          f"{len(data['execution_checks'])} exec checks")
