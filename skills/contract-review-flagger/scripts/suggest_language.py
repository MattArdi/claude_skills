#!/usr/bin/env python3
"""Print the Start2 standard language for clause IDs, for a redline or a request to the counterparty.

Usage: suggest_language.py <standards.json> ID [ID ...] [--terms '{"Start2": "the Contractor", "Company": "Canada"}']
{{ID}} cross-references are shown as the clause name, for example "Clause [Limitation of liability]".
--terms swaps the standard's defined terms for the contract's own, outside [placeholders].
Open [placeholders] are left in place.
build_review_workbook.py imports render() to fill the Suggested language column, so this text never has to be
copied into the Action column by hand.
"""
import json
import re
import sys


def swap_terms(text, terms):
    """Replace defined terms (whole words) everywhere except inside [placeholders]."""
    if not terms:
        return text
    rx = re.compile(r"\b(" + "|".join(re.escape(k) for k in sorted(terms, key=len, reverse=True)) + r")\b")

    def rep(m):
        new = terms[m.group(1)]
        before = m.string[:m.start()].rstrip(" ")
        if not before or before[-1] in ".!?\n" or re.search(r"(?:^|\n)\s*(?:\d+(?:\.\d+)*\.?|\([a-z0-9]{1,4}\)|[a-z]\.)$", before):
            new = new[:1].upper() + new[1:]  # sentence or numbered-line start
        return new
    parts = re.split(r"(\[[^\]]*\])", text)
    return "".join(p if p.startswith("[") else rx.sub(rep, p) for p in parts)


def render(by, cid, terms=None):
    """Standard language of clause cid with cross-references named, or None when the clause has none."""
    c = by.get(cid)
    if not c or not c["standard_language"]:
        return None
    text = re.sub(r"(?m)^\{\{[A-Z-]+\}\}\.(\d+(?:\.\d+)*)", r"\1", c["standard_language"])  # own sub-clause numbers
    text = re.sub(r"\{\{([A-Z-]+)\}\}(\.\d+(?:\.\d+)*)?", lambda m: f"[{by[m.group(1)]['draft_heading'] or m.group(1)}]" + (f" sub-clause {m.group(2)[1:]}" if m.group(2) else ""), text)
    return swap_terms(text, terms)


if __name__ == "__main__":
    args = sys.argv[1:]
    terms = None
    if "--terms" in args:
        i = args.index("--terms"); terms = json.loads(args[i + 1]); del args[i:i + 2]
    std = json.load(open(args[0])); by = {c["id"]: c for c in std["clauses"]}
    for cid in args[1:]:
        text = render(by, cid, terms)
        print(f"{cid}: no standard language" if text is None else f"== {cid}: {by[cid]['draft_heading']} ==\n{text}\n")
