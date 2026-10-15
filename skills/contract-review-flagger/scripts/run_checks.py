#!/usr/bin/env python3
"""Deterministic checks over document.json. Produces candidates for Claude to confirm, not final findings.

Usage: run_checks.py <document.json> <candidates.json>

Check numbers match the Execution Check list in the standards workbook:
 1 blank fields and placeholders   2 duplicate or undefined clause numbers   3 date errors
 9 annex/attachment references against what is present   plus info: amount reconciliation, translation hint.
A page with source needs_vision has no text and is reported as unchecked.
"""
import json
import re
import sys
from itertools import combinations

MONTHS = "January|February|March|April|May|June|July|August|September|October|November|December"
D_NUM = re.compile(r"\b(\d{1,2})[/.-](\d{1,2})[/.-](\d{4,5})\b")
D_MDY = re.compile(rf"\b({MONTHS})\s+(\d{{1,2}}),?\s+(\d{{4,5}})\b")
D_DMY = re.compile(rf"\b(\d{{1,2}})\s+({MONTHS})\s+(\d{{4,5}})\b")
AMT = re.compile(r"(RMB|SGD|S\$|USD|US\$|EUR|€|CNY|GBP|£|KRW|JPY|\$)\s?(\d[\d,]*(?:\.\d+)?)")
PCT = re.compile(r"(\d+(?:\.\d+)?)\s?%")
ANNEX_REF = re.compile(r"\b(Annex|Appendix|Schedule|Attachment|Exhibit)\s+([A-Z]\d?|\d+)\b")
ANNEX_HEAD = re.compile(r"^(ANNEX|Annex|APPENDIX|Appendix|SCHEDULE|Schedule|ATTACHMENT|Attachment|EXHIBIT|Exhibit)\s+([A-Z]\d?|\d+)\b[:.\s-]*(.*)$")
LABEL_ONLY = re.compile(r"^[A-Za-z][A-Za-z /]{2,45}:\s*$")
LABEL_START = re.compile(r"^[A-Za-z][A-Za-z /]{2,45}:|^Party [AB]\b")
PLACEHOLDER = re.compile(r"\[[^\]]{1,80}\]|_{3,}|\bTBD\b|\bto be confirmed\b|\bXXX\b", re.I)
DOTLABEL = re.compile(r"^(\d+\.\d+(?:\.\d+)*)\.?\s+\S")
CLAUSEREF = re.compile(r"\b[Cc]lauses?\s+(\d+\.\d+(?:\.\d+)*)")


def num(s): return float(s.replace(",", ""))


def main(src, dst):
    doc = json.load(open(src))
    paras = doc["paragraphs"]; cands = []; info = []
    def add(check, kind, p, quote, note, bucket=cands):
        bucket.append({"check": check, "kind": kind, "page": p.get("page") if p else None, "quote": quote[:300], "note": note})

    unchecked = [p["page"] for p in doc["pages"] if p["source"] == "needs_vision"]
    if unchecked:
        info.append({"check": 0, "kind": "unchecked_pages", "page": None, "quote": "", "note": f"No text on pages {unchecked}; transcribe them first."})

    # 3 dates
    for p in paras:
        found = []
        for m in D_NUM.finditer(p["text"]): found.append((m.group(0), m.group(2), m.group(3)))   # month, year
        for m in D_MDY.finditer(p["text"]): found.append((m.group(0), m.group(1).lower(), m.group(3)))
        for m in D_DMY.finditer(p["text"]): found.append((m.group(0), m.group(2).lower(), m.group(3)))
        for raw, mo, yr in found:
            if len(yr) != 4:
                add(3, "malformed_year", p, raw, f"Year '{yr}' has {len(yr)} digits.")
        for (r1, m1, y1), (r2, m2, y2) in combinations(found, 2):
            if m1.lstrip("0") == m2.lstrip("0") and y1 != y2 and len(y1) == len(y2) == 4:
                add(3, "year_mismatch_in_sentence", p, f"{r1} ... {r2}", "Same month with different years in one paragraph.")

    # amounts: percentage reconciliation, sums
    amounts = []
    for p in paras:
        for m in AMT.finditer(p["text"]):
            v = num(m.group(2))
            if v >= 100: amounts.append((m.group(1), v, p, m.group(0)))
    for p in paras:
        for pm in PCT.finditer(p["text"]):
            pct = float(pm.group(1)); tail = p["text"][pm.end():pm.end() + 160]
            am = AMT.search(tail)
            if not am: continue
            derived = num(am.group(2)); cur = am.group(1)
            bases = [v for c, v, _, _ in amounts if c == cur and v != derived]
            ok = [b for b in bases if abs(b * pct / 100 - derived) <= 0.005 * max(derived, 1)]
            if ok:
                add(0, "percent_reconciles", p, pm.group(0) + " ... " + am.group(0), f"{pct:g}% of {ok[0]:,.0f} = {derived:,.0f}.", info)
            elif bases:
                add(1, "percent_does_not_reconcile", p, pm.group(0) + " ... " + am.group(0), f"{pct:g}% of no other stated amount equals {derived:,.0f}.")
    seen = {}
    for c, v, p, raw in amounts: seen.setdefault((c, v), p)
    keys = list(seen)
    for (a, b) in combinations(keys, 2):
        if a[0] == b[0]:
            tot = a[1] + b[1]
            for k in keys:
                if k[0] == a[0] and abs(k[1] - tot) < 0.5 and k not in (a, b):
                    add(0, "sum_reconciles", seen[k], f"{a[0]} {a[1]:,.0f} + {b[1]:,.0f}", f"= {k[1]:,.0f}.", info)

    # 1 blanks and placeholders
    for i, p in enumerate(paras):
        t = p["text"]
        nxt = paras[i + 1]["text"] if i + 1 < len(paras) else ""
        if LABEL_ONLY.match(t) and (not nxt or LABEL_START.match(nxt)):
            add(1, "blank_field", p, t, "Label with no value.")
        elif PLACEHOLDER.search(t):
            add(1, "placeholder", p, t, "Bracketed, underscored or TBD text.")

    # 2 numbering
    labels = {}
    for p in paras:
        m = DOTLABEL.match(p["text"])
        if m: labels.setdefault(m.group(1), []).append(p)
    for lab, ps in labels.items():
        if len(ps) > 1:
            add(2, "duplicate_clause_number", ps[1], ps[1]["text"], f"Clause {lab} appears {len(ps)} times (pages {[x['page'] for x in ps]}).")
    refs = {}
    for p in paras:
        for m in CLAUSEREF.finditer(p["text"]): refs.setdefault(m.group(1), p)
    for r, p in refs.items():
        if labels and r not in labels:
            add(2, "reference_to_undefined_clause", p, p["text"], f"Clause {r} is referenced but no such heading was found (check the segmentation first).")

    # 9 annexes
    heads, order = {}, []
    for i, p in enumerate(paras):
        m = ANNEX_HEAD.match(p["text"])
        if m and len(p["text"]) <= 140:
            key = (m.group(1).lower(), m.group(2)); heads[key] = i; order.append((i, key))
    order.sort()
    for n, (i, key) in enumerate(order):
        end = order[n + 1][0] if n + 1 < len(order) else len(paras)
        body = " ".join(x["text"] for x in paras[i + 1:end])
        if len(body) < 80:
            add(9, "annex_title_only", paras[i], paras[i]["text"], f"{key[0].title()} {key[1]} has almost no content ({len(body)} characters).")
    cited = {}
    for i, p in enumerate(paras):
        if ANNEX_HEAD.match(p["text"]) and len(p["text"]) <= 140: continue
        for m in ANNEX_REF.finditer(p["text"]): cited.setdefault((m.group(1).lower(), m.group(2)), p)
    for key, p in cited.items():
        if key not in heads:
            add(9, "annex_referenced_not_found", p, p["text"], f"{key[0].title()} {key[1]} is cited but no heading was found. May still be an image or an icon (check the pages).")

    if doc["flags"].get("translation_hint"):
        info.append({"check": 5, "kind": "translation_hint", "page": None, "quote": "", "note": "Text or file name says translated. The original and the precedence rule were not supplied."})
    tc = doc["flags"].get("tracked_changes", {})
    if tc.get("ins") or tc.get("del"):
        cands.append({"check": 8, "kind": "tracked_changes", "page": None, "quote": "", "note": f"{tc['ins']} insertions and {tc['del']} deletions in the file."})
    json.dump({"file": doc["file"], "candidates": cands, "info": info}, open(dst, "w"), indent=1, ensure_ascii=False)
    kinds = {}
    for c in cands: kinds[c["kind"]] = kinds.get(c["kind"], 0) + 1
    print(f"{len(cands)} candidates {kinds}; {len(info)} info")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
