#!/usr/bin/env python3
"""Split document.json into a clause tree (best effort; Claude corrects mistakes).

Usage: segment.py <document.json> <clauses.json>

Recognises: roman top-level headings (I., II.), dotted numbers (11.2), single numbers (1.),
parenthesised levels ((I), (a), (1)), Article/Clause N, and Annex/Appendix/Schedule/Attachment/Exhibit headings.
Paths: roman top + numbers restart under each heading, for example III(I).1, I.1, 11.2, 11.2(a).
Node types: front, clause, annex, signature.
"""
import json
import re
import sys

ANNEX = re.compile(r"^(ANNEX|Annex|APPENDIX|Appendix|SCHEDULE|Schedule|ATTACHMENT|Attachment|EXHIBIT|Exhibit)\s+([A-Z]\d?|\d+)\b[:.\s-]*(.*)$")
ROMAN = re.compile(r"^([IVXLC]{1,6})\.\s+(\S.{0,100})$")
DOTTED = re.compile(r"^(\d+(?:\.\d+)+)\.?\s+(\S.*)$")
SINGLE = re.compile(r"^(\d{1,2})\.\s+(\S.*)$")
PAREN = re.compile(r"^\(([IVXLC]{1,6}|[a-z]|\d{1,2})\)\s+(\S.*)$")
ARTICLE = re.compile(r"^(Article|ARTICLE|Clause)\s+(\d+)\b[.:]?\s*(.*)$")
SIGN = re.compile(r"^(SIGNED\b|IN WITNESS|For and on behalf|Party [AB]:\s*\(Seal\))", re.I)


def main(src, dst):
    doc = json.load(open(src))
    paras = doc["paragraphs"]
    romans = [p for p in paras if len(p["text"]) <= 110 and ROMAN.match(p["text"])]
    roman_top = len(romans) >= 3
    nodes = [{"id": "FRONT", "label": "", "heading": "Front matter", "type": "front", "page": paras[0]["page"] if paras else None, "text": [], "paragraphs": []}]
    cur = nodes[0]
    top = sec = None
    last_path = None

    def start(path, label, heading, typ, p):
        nonlocal cur
        cur = {"id": path, "label": label, "heading": heading[:110], "type": typ, "page": p["page"], "text": [p["text"]], "paragraphs": [p["id"]]}
        nodes.append(cur)

    for p in paras:
        t = p["text"]
        m = None
        if (m := ANNEX.match(t)) and len(t) <= 140:
            start(f"ANNEX-{m.group(2)}", m.group(2), t, "annex", p); last_path = None; top = sec = None; continue
        if cur["type"] == "annex" and not (ROMAN.match(t) or DOTTED.match(t)):
            pass  # annex content stays in the annex node unless a clause-style heading appears
        if SIGN.match(t) and any(n["type"] == "clause" for n in nodes) and cur["type"] != "signature":
            start("SIGNATURE", "", t, "signature", p); continue
        if cur["type"] == "annex":
            cur["text"].append(t); cur["paragraphs"].append(p["id"]); continue
        if (m := ROMAN.match(t)) and len(t) <= 110 and roman_top:
            top, sec = m.group(1), None; last_path = top
            start(top, top, m.group(2), "clause", p); continue
        if m := DOTTED.match(t):
            lab = m.group(1); top, sec = lab.split(".")[0], None; last_path = lab
            start(lab, lab, m.group(2), "clause", p); continue
        if m := ARTICLE.match(t):
            lab = f"{m.group(1).title()} {m.group(2)}"; top, sec = m.group(2), None; last_path = lab
            start(lab, m.group(2), m.group(3) or t, "clause", p); continue
        if m := SINGLE.match(t):
            n = m.group(1)
            path = (f"{top}{'(' + sec + ')' if sec else ''}.{n}" if roman_top and top else n)
            if not (roman_top and top): top, sec = n, None
            last_path = path
            start(path, n, m.group(2), "clause", p); continue
        if m := PAREN.match(t):
            lab = m.group(1)
            if roman_top and top and re.fullmatch(r"[IVXLC]{1,6}", lab):
                sec = lab; last_path = f"{top}({lab})"
                start(last_path, lab, m.group(2), "clause", p)
            else:
                base = last_path or ""
                start(f"{base}({lab})", lab, m.group(2), "clause", p)
            continue
        cur["text"].append(t); cur["paragraphs"].append(p["id"])
    for n in nodes:
        n["text"] = "\n".join(n["text"])
    ids = [n["id"] for n in nodes]
    dup = sorted({i for i in ids if ids.count(i) > 1})
    out = {"file": doc["file"], "roman_top_level": roman_top, "duplicate_ids": dup, "clauses": nodes}
    json.dump(out, open(dst, "w"), indent=1, ensure_ascii=False)
    print(f"{len(nodes)} nodes ({sum(n['type']=='clause' for n in nodes)} clauses, {sum(n['type']=='annex' for n in nodes)} annexes); duplicate ids: {dup or 'none'}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
