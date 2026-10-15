#!/usr/bin/env python3
"""Turn a contract file into document.json (one model for every input type).

Usage:
  ingest.py <contract.pdf|.docx|.txt|.md> <outdir> [--transcript transcript.json] [--dpi 110]

PDF with a text layer: text is taken per page with pdftotext.
PDF without a text layer (scanned) or with image-only pages: those pages are rendered to
<outdir>/pages/page-NNN.jpg and flagged needs_vision. Claude reads the images, writes
transcript.json ({"1": "page text", ...}) and re-runs this script with --transcript.
DOCX: paragraphs and tables are read from the XML; tracked insertions/deletions and comments are counted.

document.json: {file, format, source_note, pages:[{page, source, text}], paragraphs:[{id, page, text}],
                flags:{scanned, needs_vision_pages, tracked_changes:{ins,del}, comments, translation_hint}}
"""
import argparse
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
MIN_CHARS = 25  # a page with fewer characters than this has no usable text layer


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, check=True).stdout


def paragraphs_from(text, page):
    out = []
    for block in re.split(r"\n\s*\n", text.replace("\f", "\n")):
        line = " ".join(x.strip() for x in block.splitlines() if x.strip())
        if line:
            out.append({"page": page, "text": line})
    return out


def read_pdf(path, outdir, transcript, dpi):
    n = int(re.search(r"Pages:\s+(\d+)", run(["pdfinfo", str(path)])).group(1))
    pages, need = [], []
    for i in range(1, n + 1):
        if transcript is not None and str(i) in transcript:
            pages.append({"page": i, "source": "vision", "text": transcript[str(i)].strip()})
            continue
        text = run(["pdftotext", "-layout", "-f", str(i), "-l", str(i), str(path), "-"]).strip()
        if len(re.sub(r"\s", "", text)) >= MIN_CHARS:
            pages.append({"page": i, "source": "text", "text": text})
        else:
            need.append(i)
            pages.append({"page": i, "source": "needs_vision", "text": ""})
    if need:
        img = Path(outdir) / "pages"
        img.mkdir(parents=True, exist_ok=True)
        for i in need:
            run(["pdftoppm", "-r", str(dpi), "-jpeg", "-f", str(i), "-l", str(i), "-singlefile", str(path), str(img / f"page-{i:03d}")])
    return pages, need


def read_docx(path):
    z = zipfile.ZipFile(path)
    root = ET.fromstring(z.read("word/document.xml"))
    ins = len(root.findall(f".//{W}ins")); dele = len(root.findall(f".//{W}del"))
    comments = "word/comments.xml" in z.namelist()

    def ptext(p):
        parts = []
        for el in p.iter():
            if el.tag == f"{W}t":
                parts.append(el.text or "")
            elif el.tag == f"{W}tab":
                parts.append("\t")
        return "".join(parts).strip()  # w:delText (deleted text) is deliberately not read

    paras = []
    body = root.find(f"{W}body")
    for child in body:
        if child.tag == f"{W}p":
            t = ptext(child)
            if t: paras.append(t)
        elif child.tag == f"{W}tbl":
            for tr in child.iter(f"{W}tr"):
                cells = [" ".join(ptext(p) for p in tc.iter(f"{W}p")).strip() for tc in tr.findall(f"{W}tc")]
                row = " | ".join(c for c in cells if c)
                if row: paras.append(row)
    return paras, {"ins": ins, "del": dele}, comments


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("contract"); ap.add_argument("outdir")
    ap.add_argument("--transcript"); ap.add_argument("--dpi", type=int, default=110)
    a = ap.parse_args()
    path, out = Path(a.contract), Path(a.outdir)
    out.mkdir(parents=True, exist_ok=True)
    ext = path.suffix.lower()
    transcript = json.load(open(a.transcript)) if a.transcript else None
    flags = {"scanned": False, "needs_vision_pages": [], "tracked_changes": {"ins": 0, "del": 0}, "comments": False}
    paragraphs = []
    if ext == ".pdf":
        pages, need = read_pdf(path, out, transcript, a.dpi)
        flags["needs_vision_pages"] = need
        flags["scanned"] = len(need) == len(pages) or any(p["source"] == "vision" for p in pages) and not any(p["source"] == "text" for p in pages)
        for p in pages:
            paragraphs += paragraphs_from(p["text"], p["page"])
        fmt = "pdf"
    elif ext == ".docx":
        paras, tc, com = read_docx(path)
        pages = [{"page": 1, "source": "text", "text": "\n\n".join(paras)}]
        paragraphs = [{"page": None, "text": t} for t in paras]
        flags["tracked_changes"], flags["comments"], fmt = tc, com, "docx"
    elif ext in (".txt", ".md"):
        text = path.read_text(errors="replace")
        pages = [{"page": 1, "source": "text", "text": text}]
        paragraphs = paragraphs_from(text, 1); fmt = "text"
    else:
        sys.exit(f"unsupported file type: {ext}")
    for i, p in enumerate(paragraphs, 1):
        p["id"] = f"P{i:04d}"
    corpus = " ".join(p["text"] for p in pages) + " " + path.name
    flags["translation_hint"] = bool(re.search(r"translat", corpus, re.I))
    doc = {"file": path.name, "format": fmt, "pages": pages, "paragraphs": paragraphs, "flags": flags}
    (out / "document.json").write_text(json.dumps(doc, indent=1, ensure_ascii=False))
    msg = f"{path.name}: {fmt}, {len(pages)} page(s), {len(paragraphs)} paragraph(s)"
    if flags["needs_vision_pages"]:
        msg += (f"\nNEEDS VISION: {len(flags['needs_vision_pages'])} page(s) have no text layer. Images are in {out/'pages'}. "
                "Read them (20 pages per call), write transcript.json, then re-run with --transcript.")
    if fmt == "docx" and (flags["tracked_changes"]["ins"] or flags["tracked_changes"]["del"]):
        msg += f"\nTRACKED CHANGES: {flags['tracked_changes']['ins']} insertions, {flags['tracked_changes']['del']} deletions (deleted text excluded)."
    print(msg)


if __name__ == "__main__":
    main()
