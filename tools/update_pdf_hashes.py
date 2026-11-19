# -*- coding: utf-8 -*-
"""Regenerate pdfs/library_hashes.json from the local PDF library.

Run after adding/removing a PDF in pdfs/:
    python tools/update_pdf_hashes.py

The hash manifest is tracked in Git so pdf-inbox PR checks can tell whether an
uploaded PDF is already in the library, even though the PDF files themselves
are not tracked.
"""
import hashlib
import json
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "assets" / "data.js"
PDFS_DIR = ROOT / "pdfs"
OUT_PATH = PDFS_DIR / "library_hashes.json"


def load_data():
    text = DATA_PATH.read_text(encoding="utf-8")
    return json.loads(text[text.index("=") + 1 :].strip().rstrip(";"))


def pdf_name(paper):
    href = str(paper.get("pdf_href", "") or "")
    if not href or href.startswith(("http://", "https://", "file:")):
        return ""
    return Path(unquote(href.split("?", 1)[0])).name


def sha256_file(path):
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
            size += len(chunk)
    return digest.hexdigest(), size


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass
    papers = load_data().get("papers", [])
    meta = {}
    for paper in papers:
        name = pdf_name(paper)
        if name:
            meta[name] = paper

    entries = []
    for path in sorted(PDFS_DIR.glob("*.pdf")):
        digest, size = sha256_file(path)
        paper = meta.get(path.name, {})
        entries.append(
            {
                "file": path.name,
                "sha256": digest,
                "size": size,
                "id": paper.get("id"),
                "doi": paper.get("doi", ""),
                "title": paper.get("title", ""),
            }
        )

    OUT_PATH.write_text(
        json.dumps(entries, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    print(f"wrote {len(entries)} hashes to {OUT_PATH.relative_to(ROOT)}")
    print(f"referenced by data.js: {sum(1 for e in entries if e['id'] is not None)}")


if __name__ == "__main__":
    sys.exit(main())
