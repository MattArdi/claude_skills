#!/usr/bin/env python3
"""List which known Start2 entities appear in the contract (helps the role guess).

Usage: match_entities.py <document.json> [start2_entities.json]
Matches names and aliases after stripping company suffixes. Prints page and a snippet per hit.
No hit does not mean Start2 is absent: guess the role from the text (see references/rubric.md).
"""
import json
import re
import sys
from pathlib import Path

SUFFIX = re.compile(r"\b(pte\.?|ltd\.?|limited|gmbh|co\.?|inc\.?|llc|corp\.?|company|\(shanghai\)|\(singapore\))\b", re.I)


def n(s): return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", SUFFIX.sub(" ", s.lower()))).strip()


def main(doc_path, ent_path=None):
    ent_path = ent_path or Path(__file__).parent.parent / "references" / "start2_entities.json"
    doc = json.load(open(doc_path)); ents = json.load(open(ent_path))["entities"]
    hits = []
    for e in ents:
        for name in [e["name"]] + e.get("aliases", []):
            key = n(name)
            if len(key) < 4: continue
            for p in doc["paragraphs"]:
                if key in n(p["text"]):
                    hits.append((e["name"], e.get("status"), p["page"], p["text"][:100])); break
    seen = set()
    for h in hits:
        if h[:3] in seen: continue
        seen.add(h[:3]); print(f"{h[0]} [{h[1]}] p.{h[2]}: {h[3]}")
    if not hits: print("no known Start2 entity found")


if __name__ == "__main__":
    main(*sys.argv[1:3])
