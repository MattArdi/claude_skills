#!/usr/bin/env python3
"""Find Start2 entities in the contract (helps the role guess) and flag any that are not Start2 Asia.

Usage: match_entities.py <document.json> [start2_entities.json]
KNOWN: a name that contains a listed entity name or alias (after stripping company suffixes).
FLAG:  any other name containing "Start2", including "Start2" on its own. The skill must stop and ask the user
       to confirm whether that entity is ours (and in what role) before it continues.
No hit does not mean Start2 is absent: guess the role from the text (see references/rubric.md).
"""
import json
import re
import sys
from pathlib import Path

SUFFIX = re.compile(r"\b(pte\.?|ltd\.?|limited|gmbh|co\.?|inc\.?|llc|corp\.?|company|\(shanghai\)|\(singapore\))\b", re.I)
START2 = re.compile(r"(?:[A-Z][A-Za-z0-9&.'-]*\s+){0,3}Start2(?:\s+[A-Z][A-Za-z0-9&.,'()-]*){0,5}")


def n(s): return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", SUFFIX.sub(" ", s.lower()))).strip()


def main(doc_path, ent_path=None):
    ent_path = ent_path or Path(__file__).parent.parent / "references" / "start2_entities.json"
    doc = json.load(open(doc_path)); ents = json.load(open(ent_path))["entities"]
    keys = {n(x): e["name"] for e in ents for x in [e["name"]] + e.get("aliases", []) if len(n(x)) >= 4}
    known, flagged = {}, {}
    for p in doc["paragraphs"]:
        for m in START2.finditer(p["text"]):
            cand = m.group(0).strip(" ,.")
            hit = next((v for k, v in keys.items() if k in n(cand)), None)
            (known if hit else flagged).setdefault(cand if not hit else hit, (p["page"], p["text"][:100]))
    for name, (pg, snip) in known.items(): print(f"KNOWN {name} p.{pg}: {snip}")
    for name, (pg, snip) in flagged.items(): print(f"FLAG  {name!r} p.{pg}: {snip}")
    if flagged:
        print("ASK THE USER: confirm whether the flagged name is a Start2 entity of ours and in what role, then continue.")
    if not known and not flagged:
        print("no Start2 name found: guess the role from the text")


if __name__ == "__main__":
    main(*sys.argv[1:3])
