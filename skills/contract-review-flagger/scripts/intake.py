#!/usr/bin/env python3
"""Draft the one intake message sent to the user before the review starts.

Usage: intake.py <document.json> [start2_entities.json]

Collects everything the review needs from the user, so it can run without stopping again:
  1. Start2 entity and role: known Start2 entities found, and any other "Start2" names to confirm.
  2. Outside documents the contract names (general conditions, bid, policies, links): can the user supply them?
  3. Plain-language explanations: explain legal terms and clause codes where used? (summary.explain_terms)
  4. Purpose of the review: Pre-signature, Signed or Renewal (rubric section 1a).
  5. Only when the file has comments: should they be considered? (summary.consider_comments)
Text in another language is not mentioned at intake; it is flagged on the Checks sheet (rubric section 0).
Prints a draft of the questions only. Claude fills the bracketed prompts (the role guess, documents the patterns missed,
the purpose guess) inside the questions and deletes the brackets, then sends the questions as one message with nothing
else: no introduction, no first-read summary or observations, no notes, no closing line. It waits for the answer and
records it in review.json (summary.purpose, summary.explain_terms, summary.consider_comments, documents_not_supplied).
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from match_entities import START2, n  # noqa: E402
from run_checks import ANNEX_HEAD, ANNEX_PLURAL, ANNEX_REF, doc_refs  # noqa: E402

UPPER = re.compile(r"START2(?:\s+[A-Z0-9&.,'()-]+){0,4}")  # cover pages often print the name in capitals
EDGE = {"address", "about", "sent", "to", "a", "b", "c", "d", "the", "our", "and", "of", "company"}
TRIGGER = re.compile(r"^(?:apply to|forms? part|incorporated|as amended|available|constitutes?|shall form|forms? (?:an? )?integral)", re.I)  # wording, not a document name
PURPOSES = {  # meaning of each purpose (rubric section 1a); not printed in the questions
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
        for m in doc_refs(p["text"]):
            name = re.sub(r"\s+", " ", m.group(0)).strip()
            if TRIGGER.match(name):
                name = snippet(p["text"], m.start())
            docs.setdefault(name.lower(), (name, set()))[1].add(p["page"])
    heads = {(m.group(1).lower(), m.group(2)) for p in doc["paragraphs"] for m in [ANNEX_HEAD.match(p["text"])] if m and len(p["text"]) <= 140}
    for p in doc["paragraphs"]:  # annexes cited but not present
        for m in ANNEX_REF.finditer(p["text"]):
            if (m.group(1).lower(), m.group(2)) not in heads:
                docs.setdefault(f"{m.group(1)} {m.group(2)}".lower(), (f"{m.group(1)} {m.group(2)} (cited, not attached)", set()))[1].add(p["page"])
        if not heads:
            for m in ANNEX_PLURAL.finditer(p["text"]):
                docs.setdefault(m.group(1).lower(), (f"{m.group(1)} (cited, none attached)", set()))[1].add(p["page"])
    signed = bool(re.search(r"\b(?:signed|signature)\b.{0,80}\b20\d\d\b", " ".join(p["text"] for p in doc["pages"]), re.I | re.S))

    comments = doc.get("comments") or []

    def pp(pages):
        pages = sorted(p for p in pages if p is not None)
        return ("p. " if len(pages) == 1 else "pp. ") + ", ".join(map(str, pages)) if pages else "no page numbers"
    names = [f"{name} ({pp(pages)})" for name, pages in known.items()] + [f"'{name}' ({pp(pages)})" for name, pages in flagged.values()]
    out = ["1. Start2 entity and role: " + (f"is {', '.join(names)} our entity, " if names else "which Start2 entity is ours, ")
           + "and is Start2 [the party and role you guess, for example the Provider]?"]
    out += ["", "2. Can you send any of these documents the contract names but does not attach?"]
    for name, pages in sorted(docs.values(), key=lambda x: min((p or 0) for p in x[1])):
        out.append(f"   - {name} ({pp(pages)})")
    out.append("   [Remove names that are attached or are only statutes or arbitration rules; add any the patterns missed.]")
    out += ["", "3. Should legal terms be explained in plain words where they are used? (Yes or No)"]
    out += ["", "4. Purpose: Pre-signature, Signed or Renewal?" + (" [The contract looks signed: say which you guess.]" if signed else " [Say which you guess.]")]
    if comments:
        authors = ", ".join(sorted({c.get("author") or "unknown" for c in comments}))
        out += ["", f"5. Should the {len(comments)} comment(s) in the file (by {authors}) be considered? (Yes or No)"]
    print("\n".join(out))


if __name__ == "__main__":
    main(*sys.argv[1:3])
