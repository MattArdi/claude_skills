#!/usr/bin/env python3
"""Plain-language pass: find legal terms and Start2 clause codes used without an explanation.

Usage: plain_language.py <standards.json> <review.json>    (prints every unexplained term, by location)

A term counts as explained in a text when one of its uses is followed, within a few words, by an explanation:
"(...)", ", meaning", ", i.e.", ", that is", ", which means", ", such as", ": ", " - ", or "is a/an/the". A clause code in
brackets "(CODE)" does not count as an explanation. A Start2 clause code (WARR, LOL) counts as explained when it
follows a description in brackets, "the Start2 warranties standard (WARR)", or when the clause name also appears.
Words in a description that ends in "(CODE)" are part of the clause's name and need no explanation of their own.
Terms live in references/plain_terms.json.
Only used when summary.explain_terms is true (the default when missing): validate_review.py then warns on what this
finds and build_review_workbook.py adds the plain explanation to any text still holding an unexplained term.
"""
import json
import re
import sys
from pathlib import Path

TERMS_FILE = Path(__file__).parent.parent / "references" / "plain_terms.json"
EXPLAINED = re.compile(r"^[\w-]*['’]?s?(?:\s+[\w'’-]+){0,3}?(?:\s*\((?![A-Z0-9-]+\))|,?\s*(?:meaning|i\.e\.|that is|which means|in other words)\b"
                       r"|:\s|\s[-–]\s|,?\s(?:such as|being)\s|\s(?:is|are|means)\s(?:a|an|the|when|where)\b)")
SCANNED = {  # review.json texts that readers see as prose
    "findings": ("issue", "action"),
    "coverage": ("note",),
    "checks": ("evidence",),
    "documents_not_supplied": ("governs", "effect", "action"),
}


def load(standards=None):
    terms = json.load(open(TERMS_FILE))["terms"]
    for t in terms:
        t["rx"] = re.compile(r"\b(?:" + t["pattern"] + r")", re.I)
    codes = {}
    for c in (standards or {}).get("clauses", []):
        if any(t["rx"].fullmatch(c["id"]) for t in terms):
            continue  # a code that is also a glossary term (IP) is explained by the glossary
        codes[c["id"]] = {"name": c["clause"], "heading": c["draft_heading"] or c["clause"],
                          "rx": re.compile(r"(?<![\w-])" + re.escape(c["id"]) + r"(?![\w-])")}
    return terms, codes


def described(text, cid, c):
    """True when "(CODE)" follows a description holding a word of the clause's name: "force majeure standard (FM)"."""
    words = {w for w in re.findall(r"[a-z]{4,}", (c["name"] + " " + c["heading"]).lower())}
    return any(words & set(re.findall(r"[a-z]{4,}", m.group(1).lower()))
               for m in re.finditer(r"([^.;:()]{0,90})\(" + re.escape(cid) + r"\)", text))


def unexplained(text, terms, codes):
    """[(label, plain)] for terms and clause codes in text that are never explained."""
    if not text:
        return []
    out = []
    if codes:  # "the Start2 standard for governing law and dispute resolution (DISPUTE)" names a clause
        named = re.compile(r"[^.;:()]{0,90}\((?:" + "|".join(re.escape(c) for c in codes) + r")\)")
        prose = named.sub(lambda m: re.sub(r"\S", "x", m.group(0)), text)  # mask, keep positions
    else:
        prose = text
    for t in terms:
        uses = list(t["rx"].finditer(prose))
        if uses and not any(EXPLAINED.match(prose[m.end():]) for m in uses):
            out.append((t["term"], t["plain"]))
    for cid, c in codes.items():
        if c["rx"].search(text) and not described(text, cid, c) \
                and c["name"].lower() not in text.lower() and c["heading"].lower() not in text.lower():
            out.append((cid, f"the Start2 standard clause on {c['name'].lower()}"))
    return out


def annotate(text, terms, codes):
    """Text with a 'Terms used' line explaining whatever is still unexplained."""
    missing = unexplained(text, terms, codes)
    if not missing:
        return text
    return text.rstrip() + "\n\nTerms used: " + " ".join(f"{a}: {b}." for a, b in missing)


def scan(review, terms, codes):
    """Yield (location, field, [(label, plain)]) for every review text with unexplained terms."""
    for i, f in enumerate(review.get("findings", []), 1):
        for k in SCANNED["findings"]:
            if hits := unexplained(f.get(k), terms, codes):
                yield f"finding {i} ({f.get('clause')})", k, hits
    for cid, v in review.get("coverage", {}).items():
        if hits := unexplained(v.get("note"), terms, codes):
            yield f"coverage {cid}", "note", hits
    for n, v in review.get("checks", {}).items():
        if hits := unexplained(v.get("evidence"), terms, codes):
            yield f"check {n}", "evidence", hits
    for i, d in enumerate(review.get("documents_not_supplied", []), 1):
        for k in SCANNED["documents_not_supplied"]:
            if hits := unexplained(d.get(k), terms, codes):
                yield f"document {i}", k, hits


if __name__ == "__main__":
    terms, codes = load(json.load(open(sys.argv[1])))
    n = 0
    for where, field, hits in scan(json.load(open(sys.argv[2])), terms, codes):
        n += 1
        print(f"{where} {field}: " + "; ".join(f"{a} ({b})" for a, b in hits))
    print(f"{n} texts with unexplained terms")
