#!/usr/bin/env python3
"""Validate review.json before it is rendered: schema, severity sanity and quote verification.

Usage: validate_review.py <standards.json> <review.json> [document.json]

Errors (exit 1): bad enumerations, unknown clause IDs, missing required fields, quotes not found in a text document.
Warnings: severity differs from the rule (including the one-level raise for subjective wording), a non-conforming
verdict without a finding, a failed check without a finding, quotes that cannot be verified because the document is
scanned (verify the cited page by eye), quotes cut off mid-sentence or with nothing in **bold**, Issue or Action
text too short to explain itself (or too long for a Low or no-action finding), command text left in Action, documents not supplied without a finding,
legal terms or clause codes left unexplained (plain_language.py), a no-action finding not lowered one level,
document references that miss a paragraph where the document is named.
Quotes starting with "(" are placeholders such as "(clause absent)" and are not verified. **bold** markers are
ignored when quotes are matched against the document.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from subjective import find as find_subjective  # noqa: E402
from plain_language import load as load_terms, scan as scan_terms  # noqa: E402
from find_references import matches as find_mentions  # noqa: E402

SEV = ["Low", "Medium", "High", "Critical"]
TYPES = {"Missing", "Partial", "Deviant", "Client: Reject", "Client: Escalate", "Client: Conditional", "Client: Accept",
         "Unclassified clause", "Commercial", "Execution", "Not supplied", "Other"}
VERDICTS = {"Conforming", "Partial", "Deviant", "Missing", "Not supplied", "N/A"}
RESULTS = {"Pass", "Fail", "N/A", "Cannot verify"}
STATUS = {"Draft", "Executed"}; ROLE = {"Provider", "Buyer", "Other"}
CTYPE = {"Service", "Funding", "Vendor", "Other"}
PURPOSE = {"Pre-signature", "Signed", "Renewal"}
REQ_SUMMARY = ["contract", "file", "status", "contract_type", "paper", "purpose", "our_entity", "our_role", "role_basis", "counterparty"]
# word limits by form (rubric section 9): full form for Critical, High and Medium; short form for Low or no-action
FULL = {"issue": (40, None), "action": (25, None)}
SHORT = {"issue": (15, 70), "action": (8, 40)}
QUOTE_END = re.compile(r"""(?:[.;!?)"'”’]|\.\.\.|…)\s*$""")


def norm(s):
    s = s.lower().replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"[^a-z0-9]+", "", s)


def expected(base, verdict, subjective=False, action_required=True):
    if base == "n/a" or verdict in ("Conforming", "N/A"): return None
    sev = base if verdict in ("Missing", "Deviant") else SEV[max(0, SEV.index(base) - 1)]
    if subjective: sev = SEV[min(len(SEV) - 1, SEV.index(sev) + 1)]
    if not action_required: sev = SEV[max(0, SEV.index(sev) - 1)]
    return sev


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
    if S.get("purpose") and S["purpose"] not in PURPOSE: errors.append(f"summary.purpose {S['purpose']!r} (Pre-signature, Signed or Renewal)")

    corpus, scanned = "", True
    fname = ""
    if doc_path:
        doc = json.load(open(doc_path)); fname = doc["file"]
        texts = [p["text"] for p in doc["pages"] if p["source"] in ("text", "vision")]
        corpus = norm(" ".join(texts) + " " + fname); scanned = not texts
        if any(p["source"] == "vision" for p in doc["pages"]):
            warns.append("document text is a vision transcript: quotes match the transcript, not the original image. Check cited pages.")
    para_ends = [norm(p["text"]) for p in doc["paragraphs"]] if doc_path else []
    unverified = 0
    for i, f in enumerate(rev.get("findings", []), 1):
        tag = f"finding {i} ({f.get('clause')})"
        for k in ("severity", "type", "clause", "where", "quote", "issue", "action"):
            if not f.get(k): errors.append(f"{tag}: {k} is empty")
        if f.get("severity") not in SEV: errors.append(f"{tag}: severity {f.get('severity')!r}")
        if f.get("type") not in TYPES: errors.append(f"{tag}: type {f.get('type')!r}")
        q = f.get("quote") or ""
        no_action = f.get("action_required") is False
        short = no_action or f.get("severity") == "Low"
        for k, (lo, hi) in (SHORT if short else FULL).items():
            words = len((f.get(k) or "").split())
            if f.get(k) and words < lo:
                warns.append(f"{tag}: {k} has {words} words; explain it in full (rubric section 9)")
            if hi and words > hi:
                warns.append(f"{tag}: {k} has {words} words; a {'no-action' if no_action else 'Low'} finding uses the short form "
                             f"(about {hi} words at most, rubric section 9)")
        if no_action and not (f.get("action") or "").startswith("No action needed"):
            warns.append(f"{tag}: action_required is false; start the action with 'No action needed' and say why")
        if not no_action and re.match(r"\s*(?:No action\b|None\.|Record\.)", f.get("action") or ""):
            warns.append(f"{tag}: action asks for nothing; set \"action_required\": false and lower severity one level")
        if re.search(r"suggest_language|scripts/|\.py\b", f.get("action") or ""):
            errors.append(f"{tag}: action contains command text; the Suggested language column is filled automatically")
        if q and not q.startswith("("):
            if "**" not in q:
                warns.append(f"{tag}: quote has no **bold** part; bold the words the issue turns on")
            last = norm(re.split(r"\s*(?:\.\.\.|…)\s*", q.replace("**", ""))[-1])
            ends_source = bool(last) and any(t.endswith(last) for t in para_ends)  # a list item or table row that ends without a stop
            if not QUOTE_END.search(q.replace("**", "")) and not ends_source:
                warns.append(f"{tag}: quote ends mid-sentence ({q.replace('**', '')[-30:]!r}); quote the full sentence or sub-clause")
            hits = find_subjective(q)
            if hits and not f.get("subjective"):
                warns.append(f"{tag}: quote has subjective wording {hits}; set \"subjective\": true and raise severity one level")
            if not doc_path or scanned:
                unverified += 1
            else:
                for seg in re.split(r"\s*(?:\.\.\.|…)\s*", q):
                    if len(norm(seg)) >= 15 and norm(seg) not in corpus:
                        errors.append(f"{tag}: quote not found in document: {seg[:70]!r}")
        if f.get("type") in ("Missing", "Partial", "Deviant") and f.get("clause") in base:
            exp = expected(base[f["clause"]], f["type"], bool(f.get("subjective")), f.get("action_required") is not False)
            if exp and f["severity"] != exp:
                adj = [x for x, on in (("raised one level for subjective wording", f.get("subjective")),
                                       ("lowered one level as no action is needed", f.get("action_required") is False)) if on]
                warns.append(f"{tag}: severity {f['severity']} differs from rule {exp} (base {base[f['clause']]}"
                             f"{'; ' + ', '.join(adj) if adj else ''}); keep only if justified in the issue text")
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
    docs = rev.get("documents_not_supplied", [])
    noted = {f.get("clause") for f in rev.get("findings", []) if f.get("type") == "Not supplied"}
    paras = doc["paragraphs"] if doc_path else []
    pnorm = {p["id"]: norm(p["text"]) for p in paras}
    for i, d in enumerate(docs, 1):
        for k in ("document", "references", "governs", "effect", "action"):
            if not d.get(k): errors.append(f"document {i}: {k} is empty")
        covered = set()
        for j, ref in enumerate(d.get("references", []), 1):
            if not ref.get("where") or not ref.get("quote"):
                errors.append(f"document {i} reference {j}: where and quote are both required"); continue
            segs = [norm(x) for x in re.split(r"\s*(?:\.\.\.|…)\s*", ref["quote"]) if len(norm(x)) >= 15]
            if doc_path and not scanned:
                for sg in segs:
                    if sg not in corpus: errors.append(f"document {i} reference {j}: quote not found in document: {sg[:60]!r}")
            # each reference accounts for one paragraph: the first not yet claimed that holds all of its quote
            hit = next((p["id"] for p in paras if p["id"] not in covered and segs and all(sg in pnorm[p["id"]] for sg in segs)), None)
            if hit: covered.add(hit)
        if d.get("search") and paras:
            missed = [p for p, _, _ in find_mentions(doc, d["search"]) if p["id"] not in covered]
            if missed:
                warns.append(f"document {i} ({d.get('document')}): named in {len(missed)} more place(s) not in references: "
                             + ", ".join(f"p.{p['page']} {p['id']}" for p in missed) + " (run find_references.py)")
        elif not d.get("search"):
            warns.append(f"document {i}: no search terms; add \"search\" so every reference can be checked")
        if d.get("part_of_contract") and d.get("document") not in noted:
            warns.append(f"document {i} ({d.get('document')}) forms part of the contract but has no 'Not supplied' finding")
    for cid, v in cov.items():
        if v.get("verdict") == "Not supplied" and not docs:
            errors.append(f"coverage {cid} is Not supplied but documents_not_supplied is empty")
    checks = rev.get("checks", {})
    for n, v in checks.items():
        if v.get("result") not in RESULTS: errors.append(f"check {n}: result {v.get('result')!r}")
    for n in range(1, len(std["execution_checks"]) + 1):
        if str(n) not in checks: errors.append(f"checks: no result for check {n}")
    for n, v in checks.items():
        fix = v.get("correct")
        if fix is not None and not (isinstance(fix, list) and all(isinstance(x, str) and x for x in fix)):
            errors.append(f"check {n}: correct must be a list of clause descriptions")
        if v.get("result") == "Fail" and not fix:
            warns.append(f"check {n} failed but lists no clauses to correct")
    has_exec = {f.get("clause") for f in rev.get("findings", []) if f.get("type") == "Execution"}
    for n, v in checks.items():
        if v.get("result") == "Fail" and f"Check {n}" not in has_exec:
            warns.append(f"check {n} failed but no Execution finding has clause 'Check {n}'")
    terms, codes = load_terms(std)
    for where, field, hits in scan_terms(rev, terms, codes):
        warns.append(f"{where} {field}: explain " + ", ".join(a for a, _ in hits)
                     + " in plain words (otherwise the workbook adds a 'Terms used' line)")
    for w in warns: print("WARN ", w)
    for e in errors: print("ERROR", e)
    print(f"{len(rev.get('findings', []))} findings, {len(errors)} errors, {len(warns)} warnings")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main(*sys.argv[1:4])
