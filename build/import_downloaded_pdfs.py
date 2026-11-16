# -*- coding: utf-8 -*-
"""Import PDFs downloaded manually (e.g. via CST/CNKI) into pdfs/<slug>.pdf.

Usage:
    python build/import_downloaded_pdfs.py
    python build/import_downloaded_pdfs.py --dry-run

Put downloaded files anywhere under pdfs/incoming/. The script matches by:
1. numeric filename equal to the internal id (e.g. 2085.pdf);
2. DOI in the filename or first pages;
3. normalized title in the first pages.

It only copies files; the next build_site.py run will attach them to pages.
"""
import argparse
import json
import re
import shutil
import sys
from pathlib import Path


BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
INCOMING = ROOT / "pdfs" / "incoming"
TARGET_DIR = ROOT / "pdfs"
DATA_PATH = ROOT / "assets" / "data.js"
DOI_RE = re.compile(r"10\.\d{4,9}/[-._;()/:A-Za-z0-9]+", re.I)


def normalize(text):
    return re.sub(r"[^0-9a-z一-鿿]+", "", str(text or "").lower())


def page_text(path, max_pages=3):
    try:
        import fitz
        doc = fitz.open(path)
        return "\n".join(doc[i].get_text() for i in range(min(max_pages, doc.page_count)))
    except Exception:
        return ""


def load_papers():
    text = DATA_PATH.read_text(encoding="utf-8")
    data = json.loads(text[text.index("=") + 1 :].strip().rstrip(";"))
    return data.get("papers", [])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if not INCOMING.exists():
        print(f"missing directory: {INCOMING}")
        return 1
    papers = load_papers()
    by_id = {str(p["id"]): p for p in papers}
    by_doi = {str(p.get("doi", "")).lower(): p for p in papers if p.get("doi")}
    by_title = {normalize(p.get("title")): p for p in papers if p.get("title")}
    candidates = [p for p in papers if not p.get("pdf_href")]
    pending = {str(p["id"]): p for p in candidates}
    matched = 0
    unmatched = []
    for src in sorted(INCOMING.rglob("*.pdf")):
        try:
            if src.read_bytes()[:5] != b"%PDF-":
                unmatched.append((src, "not a PDF"))
                continue
        except OSError as exc:
            unmatched.append((src, str(exc)))
            continue
        stem = src.stem
        text = page_text(src)
        hay = f"{stem}\n{text}"
        paper = None
        reason = ""
        if stem in pending:
            paper = pending[stem]
            reason = "numeric id"
        if paper is None:
            for doi in DOI_RE.findall(hay):
                key = doi.lower().rstrip(".,;)]}")
                if key in by_doi:
                    paper = by_doi[key]
                    reason = f"DOI {key}"
                    break
        if paper is None:
            nt = normalize(text)
            for title_key, p in by_title.items():
                if len(title_key) >= 8 and title_key in nt:
                    paper = p
                    reason = "title"
                    break
        if paper is None:
            unmatched.append((src, "no matching record"))
            continue
        pid = str(paper["id"])
        if pid not in pending:
            unmatched.append((src, f"already has PDF: {pid}"))
            continue
        target = TARGET_DIR / f"{paper['slug']}.pdf"
        print(f"MATCH {src.name} -> {target.name} ({reason}, id={pid})")
        if not args.dry_run:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, target)
        pending.pop(pid, None)
        matched += 1
    print(f"matched {matched}; remaining no-PDF {len(pending)}")
    if unmatched:
        print("unmatched:")
        for src, why in unmatched:
            print(f"  {src} -> {why}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
