#!/usr/bin/env python3
"""Validate review.json before it is rendered: schema, severity sanity and quote verification.

Usage: validate_review.py <standards.json> <review.json> [document.json]

Errors (exit 1): bad enumerations, unknown clause IDs, missing required fields, quotes not found in a text document.
Warnings: severity differs from the rule, a non-conforming verdict without a finding, a failed check without a finding,
quotes that cannot be verified because the document is scanned (verify the cited page by eye).
Quotes starting with "(" are placeholders such as "(clause absent)" and are not verified.
"""
import json
import re
import sys

SEV = ["Low", "Medium", "High", "Critical"]
TYPES = {"Missing", "Partial", "Deviant", "Client: Reject", "Client: Escalate", "Client: Conditional", "Client: Accept",
         "Unclassified clause", "Commercial", "Execution", "Other"}
VERDICTS = {"Conforming", "Partial", "Deviant", "Missing", "N/A"}
RESULTS = {"Pass", "Fail", "N/A", "Cannot verify"}
STATUS = {"Draft", "Executed"}; ROLE = {"Provider", "Buyer", "Other"}
CTYPE = {"Service", "Funding", "Vendor", "Other"}
REQ_SUMMARY = ["contract", "file", "status", "contract_type", "paper", "our_entity", "our_role", "role_basis", "counterparty"]


def norm(s):
    s = s.lower().replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"[^a-z0-9]+", "", s)


def expected(base, verdict):
    if base == "n/a" or verdict in ("Conforming", "N/A"): return None
    if verdict in ("Missing", "Deviant"): return base
    return SEV[max(0, SEV.index(base) - 1)]


def main(std_path, rev_path, doc_path=None):
    std = json.load(open(std_path)); rev = json.load(open(rev_path))
    base = {c["id"]: c["base_severity"] for c in std["clauses"]}
    errors, warns = [], []
    S = rev.get("summary", {})
    for k in REQ_SUMMARY:
        if not S.get(k): errors.append(f"summary.{k} is empty")
    if S.get("status") and S["status"] not in STATUS: errors.append(f"summary.status {S['status']!r}")
    if S.get("our_role") and S["our_role"] not in ROLE: errors.append(f"summary.our_role {S['our_role']!r}")
    if S.get("contract_type") and S["contract_type"] not in CTYPE: errors.append(f"summary.contract_type {S['contract_type']!r}")

    corpus, scanned = "", True
    fname = ""
    if doc_path:
        doc = json.load(open(doc_path)); fname = doc["file"]
        texts = [p["text"] for p in doc["pages"] if p["source"] in ("text", "vision")]
        corpus = norm(" ".join(texts) + " " + fname); scanned = not texts
        if any(p["source"] == "vision" for p in doc["pages"]):
            warns.append("document text is a vision transcript: quotes match the transcript, not the original image. Check cited pages.")
    unverified = 0
    for i, f in enumerate(rev.get("findings", []), 1):
        tag = f"finding {i} ({f.get('clause')})"
        for k in ("severity", "type", "clause", "where", "quote", "issue", "action"):
            if not f.get(k): errors.append(f"{tag}: {k} is empty")
        if f.get("severity") not in SEV: errors.append(f"{tag}: severity {f.get('severity')!r}")
        if f.get("type") not in TYPES: errors.append(f"{tag}: type {f.get('type')!r}")
        q = f.get("quote") or ""
        if q and not q.startswith("("):
            if not doc_path or scanned:
                unverified += 1
            else:
                for seg in re.split(r"\s*(?:\.\.\.|…)\s*", q):
                    if len(norm(seg)) >= 15 and norm(seg) not in corpus:
                        errors.append(f"{tag}: quote not found in document: {seg[:70]!r}")
        if f.get("type") in ("Missing", "Partial", "Deviant") and f.get("clause") in base:
            exp = expected(base[f["clause"]], f["type"])
            if exp and f["severity"] != exp:
                warns.append(f"{tag}: severity {f['severity']} differs from rule {exp} (base {base[f['clause']]}); keep only if justified in the issue text")
        elif f.get("type") in ("Missing", "Partial", "Deviant") and f.get("clause") not in base:
            errors.append(f"{tag}: unknown clause ID {f.get('clause')!r}")
    if unverified:
        warns.append(f"{unverified} quotes could not be machine-verified (scanned or no document.json given). Check each cited page by eye.")

    cov = rev.get("coverage", {})
    S_role = S.get("our_role")
    for cid, v in cov.items():
        if cid not in base: errors.append(f"coverage: unknown clause ID {cid!r}")
        if v.get("verdict") not in VERDICTS: errors.append(f"coverage {cid}: verdict {v.get('verdict')!r}")
    if S_role == "Provider":
        missing = [c for c in base if c not in cov]
        if missing: errors.append(f"coverage: no verdict for {missing}")
        have = {(f.get("clause")) for f in rev.get("findings", [])}
        for cid, v in cov.items():
            if v.get("verdict") in ("Missing", "Partial", "Deviant") and cid not in have and base.get(cid) != "n/a":
                warns.append(f"coverage {cid} is {v['verdict']} but there is no finding for it")
    checks = rev.get("checks", {})
    for n, v in checks.items():
        if v.get("result") not in RESULTS: errors.append(f"check {n}: result {v.get('result')!r}")
    for n in range(1, len(std["execution_checks"]) + 1):
        if str(n) not in checks: errors.append(f"checks: no result for check {n}")
    has_exec = {f.get("clause") for f in rev.get("findings", []) if f.get("type") == "Execution"}
    for n, v in checks.items():
        if v.get("result") == "Fail" and f"Check {n}" not in has_exec:
            warns.append(f"check {n} failed but no Execution finding has clause 'Check {n}'")
    for w in warns: print("WARN ", w)
    for e in errors: print("ERROR", e)
    print(f"{len(rev.get('findings', []))} findings, {len(errors)} errors, {len(warns)} warnings")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main(*sys.argv[1:4])
