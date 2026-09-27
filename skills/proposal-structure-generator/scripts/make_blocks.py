"""Turn Notion Boilerplate Content Blocks rows into blocks.json for build_proposal.py.

Usage: python make_blocks.py <notion_rows.json> -o blocks.json [--map section_map.json]

notion_rows.json is the result of querying the Boilerplate Content Blocks data source
in rows mode, saved as-is: {"results": [{"Main Section": ..., "Sub Section": ...,
"Section Title": ..., "Select": ..., "Text": ...}, ...]} (a bare list also works).
Each checklist ID in the section map is matched to its Notion row by Main Section plus
the last part of its Notion Block path.
"""
import argparse, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_MAP = os.path.join(HERE, "..", "assets", "section_map_public_partners.json")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rows")
    ap.add_argument("-o", "--output", required=True)
    ap.add_argument("--map", default=DEFAULT_MAP)
    a = ap.parse_args()
    data = json.load(open(a.rows, encoding="utf-8"))
    rows = data["results"] if isinstance(data, dict) else data
    smap = json.load(open(a.map, encoding="utf-8"))["sections"]
    blocks, problems = {}, []
    for rid, m in smap.items():
        path = m.get("notion_block")
        if not path:
            continue
        parts = [p.strip() for p in path.split(">")]
        hits = [r for r in rows if (r.get("Main Section") or "").strip() == parts[0]
                and ((r.get("Section Title") or "").strip() or (r.get("Main Section") or "").strip()) == parts[-1]]
        if len(hits) != 1:
            problems.append(f"{rid} {path}: {len(hits)} matching rows")
            continue
        r = hits[0]
        text = r.get("Text") or ""
        status = (r.get("Select") or "Pending Review") if text.strip() else "Empty"
        blocks[rid] = {"status": status, "text": text, "notion_block": path}
    json.dump(blocks, open(a.output, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(f"{len(blocks)} blocks -> {a.output}")
    for p in problems:
        print("Check:", p)


if __name__ == "__main__":
    main()
