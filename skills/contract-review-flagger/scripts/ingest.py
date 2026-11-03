#!/usr/bin/env python3
"""Turn a contract file into document.json (one model for every input type).

Usage:
  ingest.py <contract.pdf|.docx|.txt|.md> <outdir> [--transcript transcript.json] [--dpi 110]

PDF with a text layer: text is taken per page with pdftotext.
PDF without a text layer (scanned), with image-only pages, or with pages whose only text is a header, footer or
page number repeated across the file (for example an e-signature document ID over a scanned annex): those pages are
rendered to <outdir>/pages/page-NNN.jpg and flagged needs_vision. Claude reads the images, writes transcript.json
({"1": "page text", ...}) and re-runs this script with --transcript.
PDF comments (annotations such as notes, free text and highlights with a comment) are extracted like DOCX comments.
DOCX: paragraphs and tables are read from the XML; tracked insertions/deletions are counted and comments are
extracted with their author and the text they are attached to (used only if the requester asks for them at intake).

document.json: {file, format, source_note, pages:[{page, source, text}], paragraphs:[{id, page, text}],
                comments:[{id, author, text, anchor}],
                flags:{scanned, needs_vision_pages, tracked_changes:{ins,del}, comments, translation_hint}}
"""
import argparse
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile
import zlib
from pathlib import Path

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
MIN_CHARS = 25  # a page with fewer characters than this has no usable text layer
MIN_CONTENT = 150  # a page whose text outside repeated headers and footers is shorter than this, and that holds an image, needs vision
PAGE_NO = re.compile(r"^(?:page\s*:?\s*)?\d{1,4}(?:\s*(?:of|/|de|of/de)\s*\d{1,4})?$", re.I)
ANNOT = re.compile(rb"/Subtype\s*/(Text|FreeText|Highlight|Underline|StrikeOut|Squiggly|Caret|Ink|Stamp|Square|Circle|Line|Polygon|PolyLine|FileAttachment)\b")


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, check=True).stdout


def paragraphs_from(text, page):
    out = []
    for block in re.split(r"\n\s*\n", text.replace("\f", "\n")):
        line = " ".join(x.strip() for x in block.splitlines() if x.strip())
        if line:
            out.append({"page": page, "text": line})
    return out


def boilerplate(texts):
    """Lines repeated on many pages (headers, footers, e-signature IDs): not page content."""
    seen = {}
    for t in texts:
        for line in {re.sub(r"\s+", " ", x).strip() for x in t.splitlines() if x.strip()}:
            seen[line] = seen.get(line, 0) + 1
    floor = max(3, int(0.3 * len(texts)))
    return {line for line, k in seen.items() if k >= floor}


def has_image(path, i):
    try:
        out = run(["pdfimages", "-list", "-f", str(i), "-l", str(i), str(path)]).splitlines()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return True  # cannot tell: let the content test decide
    return len(out) > 2  # two header lines, then one line per image


def read_pdf(path, outdir, transcript, dpi):
    n = int(re.search(r"Pages:\s+(\d+)", run(["pdfinfo", str(path)])).group(1))
    raw = {i: run(["pdftotext", "-layout", "-f", str(i), "-l", str(i), str(path), "-"]).strip() for i in range(1, n + 1)}
    boiler = boilerplate(list(raw.values()))
    pages, need = [], []
    for i in range(1, n + 1):
        if transcript is not None and str(i) in transcript:
            pages.append({"page": i, "source": "vision", "text": transcript[str(i)].strip()})
            continue
        text = raw[i]
        content = "".join(x for x in (re.sub(r"\s+", " ", y).strip() for y in text.splitlines())
                          if x and x not in boiler and not PAGE_NO.match(x))
        if len(re.sub(r"\s", "", text)) < MIN_CHARS:
            need.append(i)
            pages.append({"page": i, "source": "needs_vision", "text": ""})
        elif len(re.sub(r"\s", "", content)) < MIN_CONTENT and has_image(path, i):
            need.append(i)  # only a header or footer as text over an image: read the image
            pages.append({"page": i, "source": "needs_vision", "text": text})
        else:
            pages.append({"page": i, "source": "text", "text": text})
    if need:
        img = Path(outdir) / "pages"
        img.mkdir(parents=True, exist_ok=True)
        for i in need:
            run(["pdftoppm", "-r", str(dpi), "-jpeg", "-f", str(i), "-l", str(i), "-singlefile", str(path), str(img / f"page-{i:03d}")])
    return pages, need


def pdf_string(b, i):
    """Parse a PDF literal (...) or hex <...> string starting at b[i]; return (text, end)."""
    if b[i:i + 1] == b"<":
        j = b.index(b">", i)
        raw = bytes.fromhex(re.sub(rb"\s", b"", b[i + 1:j]).decode() + ("0" if (j - i - 1) % 2 else ""))
        end = j + 1
    else:
        out, depth, j = bytearray(), 0, i + 1
        esc = {b"n": b"\n", b"r": b"\r", b"t": b"\t", b"b": b"\b", b"f": b"\f", b"(": b"(", b")": b")", b"\\": b"\\"}
        while j < len(b):
            c = b[j:j + 1]
            if c == b"\\":
                nxt = b[j + 1:j + 2]
                if nxt in esc: out += esc[nxt]; j += 2; continue
                m = re.match(rb"[0-7]{1,3}", b[j + 1:j + 4])
                if m: out.append(int(m.group(0), 8) & 255); j += 1 + len(m.group(0)); continue
                j += 2; continue
            if c == b"(": depth += 1
            elif c == b")":
                if depth == 0: break
                depth -= 1
            out += c; j += 1
        raw, end = bytes(out), j + 1
    if raw.startswith(b"\xfe\xff"):
        return raw[2:].decode("utf-16-be", errors="replace"), end
    return raw.decode("latin-1"), end


def pdf_field(d, key):
    m = re.search(rb"/" + key + rb"\s*([(<])", d)
    if not m or d[m.start(1):m.start(1) + 2] == b"<<":
        return ""
    return pdf_string(d, m.start(1))[0].strip()


def read_pdf_comments(path):
    """Annotations that carry a comment (notes, free text, highlights with text), best effort, without page numbers."""
    data = Path(path).read_bytes()
    chunks = [data]
    for m in re.finditer(rb"stream\r?\n(.*?)\r?\nendstream", data, re.S):
        try:
            chunks.append(zlib.decompress(m.group(1)))
        except zlib.error:
            pass
    out, seen = [], set()
    for ch in chunks:
        for m in ANNOT.finditer(ch):
            a = max(ch.rfind(b"<<", 0, m.start()), ch.rfind(b"obj", 0, m.start()))
            z = ch.find(b"endobj", m.end()); z = len(ch) if z == -1 else z
            nxt = ANNOT.search(ch, m.end())
            if nxt and nxt.start() < z: z = nxt.start()
            d = ch[max(a, 0):z]
            text = pdf_field(d, b"Contents")
            if not text or (text, m.group(1)) in seen:
                continue
            seen.add((text, m.group(1)))
            out.append({"id": str(len(out) + 1), "author": pdf_field(d, b"T") or None, "text": text, "anchor": "",
                        "kind": m.group(1).decode()})
    return out


def read_docx(path):
    z = zipfile.ZipFile(path)
    root = ET.fromstring(z.read("word/document.xml"))
    ins = len(root.findall(f".//{W}ins")); dele = len(root.findall(f".//{W}del"))
    comments = []
    if "word/comments.xml" in z.namelist():
        anchors, active = {}, set()
        for el in root.iter():
            if el.tag == f"{W}commentRangeStart":
                active.add(el.get(f"{W}id")); anchors.setdefault(el.get(f"{W}id"), [])
            elif el.tag == f"{W}commentRangeEnd":
                active.discard(el.get(f"{W}id"))
            elif el.tag == f"{W}t" and active:
                for cid in active: anchors[cid].append(el.text or "")
        for c in ET.fromstring(z.read("word/comments.xml")).iter(f"{W}comment"):
            cid = c.get(f"{W}id")
            text = "\n".join("".join(t.text or "" for t in p.iter(f"{W}t")) for p in c.iter(f"{W}p")).strip()
            comments.append({"id": cid, "author": c.get(f"{W}author"), "text": text,
                             "anchor": re.sub(r"\s+", " ", "".join(anchors.get(cid, []))).strip()[:300]})

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
    paragraphs, comment_list = [], []
    if ext == ".pdf":
        pages, need = read_pdf(path, out, transcript, a.dpi)
        comment_list = read_pdf_comments(path)
        flags["comments"] = bool(comment_list)
        flags["needs_vision_pages"] = need
        flags["scanned"] = len(need) == len(pages) or any(p["source"] == "vision" for p in pages) and not any(p["source"] == "text" for p in pages)
        for p in pages:
            paragraphs += paragraphs_from(p["text"], p["page"])
        fmt = "pdf"
    elif ext == ".docx":
        paras, tc, comment_list = read_docx(path)
        pages = [{"page": 1, "source": "text", "text": "\n\n".join(paras)}]
        paragraphs = [{"page": None, "text": t} for t in paras]
        flags["tracked_changes"], flags["comments"], fmt = tc, bool(comment_list), "docx"
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
    doc = {"file": path.name, "format": fmt, "pages": pages, "paragraphs": paragraphs, "comments": comment_list, "flags": flags}
    (out / "document.json").write_text(json.dumps(doc, indent=1, ensure_ascii=False))
    msg = f"{path.name}: {fmt}, {len(pages)} page(s), {len(paragraphs)} paragraph(s)"
    if flags["needs_vision_pages"]:
        msg += (f"\nNEEDS VISION: {len(flags['needs_vision_pages'])} page(s) have no text layer, or only a repeated header or footer over an image. Images are in {out/'pages'}. "
                "Read them (20 pages per call), write transcript.json, then re-run with --transcript.")
    if comment_list:
        msg += f"\nCOMMENTS: {len(comment_list)} by {', '.join(sorted({c['author'] or '?' for c in comment_list}))} (ask at intake whether to consider them)."
    if fmt == "docx" and (flags["tracked_changes"]["ins"] or flags["tracked_changes"]["del"]):
        msg += f"\nTRACKED CHANGES: {flags['tracked_changes']['ins']} insertions, {flags['tracked_changes']['del']} deletions (deleted text excluded)."
    print(msg)


if __name__ == "__main__":
    main()
