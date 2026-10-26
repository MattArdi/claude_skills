#!/usr/bin/env python3
"""Find every place the contract names a document, with the clause, page and sentence.

Usage: find_references.py <document.json> "<search term>" ["<another name for it>" ...] [--json]

Prints one line per paragraph that holds any of the terms, with the nearest clause number before it and the
sentence(s) holding the term, the term in **bold**. --json prints the same as a "references" list ready for
documents_not_supplied in review.json; check each "where" against the contract and widen a quote if the sentence
alone loses its meaning. validate_review.py warns when a document's references miss a paragraph these terms match.
"""
import json
import re
import sys

LABEL = re.compile(r"^((?:\d+\.)*\d+)\.?\s|^((?:Annex|Appendix|Schedule|Article|Section)\s+[A-Z0-9]+)\b", re.I)
SENT = re.compile(r"(?<=[.;:])\s+(?=[A-Z0-9(])")


def matches(doc, terms):
    """[(paragraph, label, [sentences with the term in bold])] for paragraphs holding any term."""
    rx = re.compile("|".join(re.escape(t).replace(r"\ ", r"\s+") for t in terms), re.I)
    label, out = "", []
    for p in doc["paragraphs"]:
        text = re.sub(r"\s+", " ", p["text"]).strip()
        if m := LABEL.match(text):
            label = m.group(1) or m.group(2)
        if not rx.search(text):
            continue
        sents = [rx.sub(lambda m: f"**{m.group(0)}**", s) for s in SENT.split(text) if rx.search(s)]
        out.append((p, label, sents))
    return out


if __name__ == "__main__":
    args = [a for a in sys.argv[2:] if a != "--json"]
    doc = json.load(open(sys.argv[1]))
    found = matches(doc, args)
    if "--json" in sys.argv:
        refs = [{"where": f"{lab + ' ' if lab else ''}(p. {p['page']})", "quote": " ... ".join(s)} for p, lab, s in found]
        print(json.dumps(refs, indent=1, ensure_ascii=False))
    else:
        for p, lab, s in found:
            print(f"{p['id']} p.{p['page']} {lab or '-'}: {' ... '.join(s)}")
        print(f"{len(found)} paragraphs")
