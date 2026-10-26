#!/usr/bin/env python3
"""Find subjective standards: wording that lets the counterparty alone judge Start2's work, payment or people.

Usage: subjective.py <document.json>     (prints every hit with its page)
Imported by run_checks.py (candidates) and validate_review.py (severity warnings).

A finding whose quote holds such wording is raised one severity level (references/rubric.md section 8).
"""
import json
import re
import sys

PATTERNS = [
    r"\bacceptable to (?:the )?[A-Z][\w-]*",                      # "standards of quality acceptable to Canada"
    r"\bin (?:an )?acceptable (?:form|condition|manner|quality)",  # "invoice in acceptable form", "acceptable condition"
    r"\bsatisfactory to\b",
    r"\bto the (?:sole |complete |full |reasonable )?satisfaction of\b",
    r"\b(?:sole|absolute|unfettered|own) (?:discretion|opinion|judge?ment)\b",
    r"\bin (?:its|their|his|her) (?:reasonable )?(?:discretion|opinion|judge?ment)\b",
    r"\b(?:opinion|judge?ment) of (?:the )?[A-Z][\w-]*",
    r"\bas (?:determined|decided|deemed|considered) (?:appropriate |necessary |suitable )?by (?:the )?[A-Z][\w-]*",
    r"\b(?:deemed|considered) (?:necessary|appropriate|suitable|unsuitable|satisfactory) by\b",
    r"\b(?:suitable|unsuitable) to (?:the )?[A-Z][\w-]*",
    r"\bdecide that\b[^.]{0,80}\b(?:unsuitable|unsatisfactory|unacceptable)\b",
]
RX = re.compile("|".join(f"(?:{p})" for p in PATTERNS))


def find(text):
    """Return the subjective phrases in text (bold markers ignored)."""
    return [m.group(0) for m in RX.finditer((text or "").replace("**", ""))]


if __name__ == "__main__":
    doc = json.load(open(sys.argv[1]))
    for p in doc["paragraphs"]:
        for hit in find(p["text"]):
            print(f"p.{p['page']} {p['id']}: {hit!r}  | {p['text'][:120]}")
