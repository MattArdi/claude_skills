#!/usr/bin/env python3
"""Draft the one intake message sent to the user before the review starts.

Usage: intake.py <document.json> [start2_entities.json]

Collects everything the review needs from the user, so it can run without stopping again:
  1. Start2 entity and role: known Start2 entities found, and any other "Start2" names to confirm.
  2. Outside documents the contract names (general conditions, bid, policies, links): can the user supply them?
  3. Purpose of the review: Pre-signature, Signed or Renewal (rubric section 1).
Prints a draft. Claude adds its own reading (the role guess, documents the patterns missed, a status guess), sends
it as one message, waits for the answer, and records it in review.json (summary.purpose, documents_not_supplied).
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from match_entities import START2, n  # noqa: E402
from run_checks import DOC_REF  # noqa: E402

UPPER = re.compile(r"START2(?:\s+[A-Z0-9&.,'()-]+){0,4}")  # cover pages often print the name in capitals
EDGE = {"address", "about", "sent", "to", "a", "b", "c", "d", "the", "our", "and", "of", "company"}
TRIGGER = re.compile(r"^(?:apply to|forms? part|incorporated|as amended|available)", re.I)  # wording, not a document name
PURPOSES = {
    "Pre-signature": "not signed yet; findings become requests to the counterparty before signing",
    "Signed": "already signed; findings become checks and records for the current contract",
    "Renewal": "signed, with a renewal or new version coming; findings become requests for the next version",
}


def core(name):
    """'Start2 Group Pte. Ltd. Sent' and 'About Start2 Group' both become 'start2 group'."""
    words = n(name).split()
    while words and words[0] in EDGE: words.pop(0)
    while words and words[-1] in EDGE: words.pop()
    return " ".join(words)


def snippet(text, start):
    """The sentence around a trigger phrase, cut to about 100 characters."""
    a = max(text.rfind(". ", 0, start) + 2, 0)
    return re.sub(r"\s+", " ", text[a:a + 100]).strip() + "..."


def main(doc_path, ent_path=None):
    ent_path = ent_path or Path(__file__).parent.parent / "references" / "start2_entities.json"
    doc = json.load(open(doc_path))
    ents = json.load(open(ent_path))["entities"]
    keys = {n(x): e["name"] for e in ents for x in [e["name"]] + e.get("aliases", []) if len(n(x)) >= 4}

    known, flagged, docs = {}, {}, {}
    for p in doc["paragraphs"]:
        for m in list(START2.finditer(p["text"])) + list(UPPER.finditer(p["text"])):
            cand = m.group(0).strip(" ,.")
            hit = next((v for k, v in keys.items() if k in n(cand)), None)
            if hit:
                known.setdefault(hit, set()).add(p["page"])
            else:
                key = core(cand) or n(cand)
                flagged.setdefault(key, [cand, set()])[1].add(p["page"])
        for m in DOC_REF.finditer(p["text"]):
            name = re.sub(r"\s+", " ", m.group(0)).strip()
            if TRIGGER.match(name):
                name = snippet(p["text"], m.start())
            docs.setdefault(name.lower(), (name, set()))[1].add(p["page"])
    signed = bool(re.search(r"\b(?:signed|signature)\b.{0,80}\b20\d\d\b", " ".join(p["text"] for p in doc["pages"]), re.I | re.S))

    out = [f"Before I review {doc['file']}, three questions so the review can run without stopping:", ""]
    out.append("1. Start2 entity and role")
    pp = lambda pages: ("p. " if len(pages) == 1 else "pp. ") + ", ".join(map(str, sorted(pages)))  # noqa: E731
    for name, pages in known.items():
        out.append(f"   - Found {name} ({pp(pages)}).")
    for name, pages in flagged.values():
        out.append(f"   - Found '{name}' ({pp(pages)}), which is not Start2 Asia. Is it a Start2 entity of ours?")
    if not known and not flagged:
        out.append("   - No Start2 name found. [Add your role guess and ask the user to confirm it.]")
    out.append("   [Add: which party Start2 appears to be and in what role, for the user to confirm.]")
    out += ["", "2. Documents the contract names but that may not be attached"]
    for name, pages in sorted(docs.values(), key=lambda x: min(x[1])):
        out.append(f"   - {name} ({pp(pages)})")
    out.append("   [Remove names that are attached or are only statutes; add any the patterns missed.]")
    out.append("   Can you send any of these? I will review what you send as part of the contract and list the rest as not supplied.")
    out += ["", "3. Purpose of the review" + (" (the contract looks signed)" if signed else "")]
    for k, v in PURPOSES.items():
        out.append(f"   - {k}: {v}")
    out += ["", "I will start once you reply."]
    print("\n".join(out))


if __name__ == "__main__":
    main(*sys.argv[1:3])
