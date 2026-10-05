#!/usr/bin/env python3
"""Assemble the base English agreement from the Clauses sheet.

Usage: assemble_agreement.py <standards.xlsx> [out.md]

Numbers the client-facing Must Have clauses in `Order`, resolves {{ID}}
tokens to clause numbers, and fails on any defect that would leave a stale or
literal cross-reference in the draft (Execution Check items 2 and 12).
Bracketed fill-ins ([Start Date], [X]% ...) are left in place and listed.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from parse_standards import TOKEN, parse  # noqa: E402


def assemble(path):
    data = parse(path)
    body = sorted((c for c in data["clauses"] if c["tier"] == "Must Have" and c["client_facing"] == "Y"),
                  key=lambda c: c["order"])
    numbers = {c["id"]: i for i, c in enumerate(body, 1)}
    errors, parts, open_ph = [], [], {}

    def resolve(text, where):
        def rep(m):
            if m.group(1) not in numbers:
                errors.append(f"{where}: {{{{{m.group(1)}}}}} is not an assembled clause")
                return m.group(0)
            return str(numbers[m.group(1)])
        return TOKEN.sub(rep, text)

    for c in body:
        n = numbers[c["id"]]
        text = resolve(c["standard_language"] or "", c["id"])
        if not c["standard_language"]:
            errors.append(f"{c['id']}: no standard language")
        for m in re.finditer(r"(?m)^(?:Clause )?(\d+)\.\d", text):  # own sub-clause numbering must match own number
            if int(m.group(1)) != n:
                errors.append(f"{c['id']}: sub-clause {m.group(0).strip()} does not match clause number {n}")
        left = re.findall(r"\[[^\]]+\]", text)
        if left:
            open_ph[c["id"]] = sorted(set(left))
        parts.append(f"## {n}. {c['draft_heading']}\n\n{text}\n")
    stray = [c["id"] for c in body if "{{" in resolve(c["standard_language"] or "", c["id"])]
    errors += [f"{i}: literal token left" for i in stray]
    return "\n".join(parts), numbers, open_ph, errors, data["_audit"]


if __name__ == "__main__":
    md, numbers, open_ph, errors, audit = assemble(sys.argv[1])
    if len(sys.argv) > 2:
        Path(sys.argv[2]).write_text(md)
    print(f"assembled {len(numbers)} clauses; open placeholders in {len(open_ph)} clauses; audit {audit}")
    for e in errors:
        print("ERROR", e)
    sys.exit(1 if errors or any(audit.values()) else 0)
