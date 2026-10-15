#!/usr/bin/env python3
"""Print the Start2 standard language for clause IDs, for use in an Action column or a redline.

Usage: suggest_language.py <standards.json> ID [ID ...]
{{ID}} cross-references are shown as the clause name, for example "Clause [Limitation of liability]".
Open [placeholders] are left in place.
"""
import json
import re
import sys

std = json.load(open(sys.argv[1])); by = {c["id"]: c for c in std["clauses"]}
for cid in sys.argv[2:]:
    c = by.get(cid)
    if not c or not c["standard_language"]:
        print(f"{cid}: no standard language"); continue
    text = re.sub(r"(?m)^\{\{[A-Z-]+\}\}\.(\d+(?:\.\d+)*)", r"\1", c["standard_language"])  # own sub-clause numbers
    text = re.sub(r"\{\{([A-Z-]+)\}\}(\.\d+(?:\.\d+)*)?", lambda m: f"[{by[m.group(1)]['draft_heading'] or m.group(1)}]" + (f" sub-clause {m.group(2)[1:]}" if m.group(2) else ""), text)
    print(f"== {cid}: {c['draft_heading']} ==\n{text}\n")
