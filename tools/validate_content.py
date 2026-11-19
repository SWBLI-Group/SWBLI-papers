# -*- coding: utf-8 -*-
"""Validate papers/ + assets/data.js consistency.

Run from project root:
    python tools/validate_content.py
    python tools/validate_content.py --allow-orphan-pages   # member PR before admin updates data.js

Checks include:
- duplicate paper ids / hrefs;
- every data paper has an existing HTML page and vice versa;
- page data-pid matches the data id;
- PDF links point to existing files when they are local;
- meta.total / with_pdf / tagCounts / focusCounts / boardCounts / regimeCounts
  / methodCounts / geometryCounts / gasCounts match the papers array;
- duplicate DOI/title are reported as warnings.
"""
import json
import re
import sys
import unicodedata
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "assets" / "data.js"
PAPERS_DIR = ROOT / "papers"


def norm_title(value):
    value = unicodedata.normalize("NFKC", str(value or "")).lower()
    return re.sub(r"[^0-9a-z一-鿿]+", "", value)


def load_data():
    text = DATA_PATH.read_text(encoding="utf-8")
    marker = "window.SWBLI_DATA"
    if marker not in text:
        raise ValueError("assets/data.js does not contain window.SWBLI_DATA")
    return json.loads(text[text.index("=") + 1 :].strip().rstrip(";"))


def page_pid(path):
    text = path.read_text(encoding="utf-8", errors="ignore")
    match = re.search(r'data-pid="([^"]+)"', text)
    return match.group(1) if match else ""


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass
    allow_orphan_pages = "--allow-orphan-pages" in sys.argv
    errors = []
    warnings = []
    data = load_data()
    meta = data.get("meta", {})
    papers = data.get("papers", [])

    ids = {}
    hrefs = {}
    for paper in papers:
        pid = str(paper.get("id", ""))
        href = str(paper.get("href", ""))
        if not pid:
            errors.append(f"paper without id: {paper.get('title', '')[:80]}")
            continue
        if pid in ids:
            errors.append(f"duplicate id {pid}: {ids[pid]} vs {paper.get('title', '')[:60]}")
        ids[pid] = paper.get("title", "")
        if href in hrefs:
            errors.append(f"duplicate href {href}: {hrefs[href]} vs {paper.get('title', '')[:60]}")
        hrefs[href] = paper.get("title", "")
        page = ROOT / href if href else None
        if not page or not page.is_file():
            errors.append(f"missing page for id {pid}: {href}")
        if page and page.is_file():
            ppid = page_pid(page)
            if ppid and ppid != pid:
                errors.append(f"page {href}: data-pid={ppid}, data id={pid}")
        pdf = str(paper.get("pdf_href", "") or "")
        if pdf and not pdf.startswith(("http://", "https://", "file:")):
            target = ROOT / unquote(pdf.split("?", 1)[0])
            if not target.is_file():
                errors.append(f"missing PDF for id {pid}: {pdf}")

    pages = sorted(PAPERS_DIR.glob("*.html")) if PAPERS_DIR.exists() else []
    data_pages = {str(Path(p.get("href", "")).name) for p in papers if p.get("href")}
    page_ids = {}
    for page in pages:
        ppid = page_pid(page)
        if page.name not in data_pages:
            message = f"HTML page without data entry: {page.name}"
            if allow_orphan_pages:
                warnings.append(message + " (allowed in member PR; admin must add it to data.js)")
                if ppid:
                    errors.append(f"{page.name}: new page must leave data-pid empty until the admin assigns an id")
            else:
                errors.append(message)
        if ppid:
            if ppid in page_ids:
                errors.append(f"duplicate page data-pid {ppid}: {page_ids[ppid]} / {page.name}")
            page_ids[ppid] = page.name

    total = len(papers)
    with_pdf = sum(1 for p in papers if p.get("pdf_href"))
    if meta.get("total") != total:
        errors.append(f"meta.total={meta.get('total')} but papers={total}")
    if meta.get("with_pdf") != with_pdf:
        errors.append(f"meta.with_pdf={meta.get('with_pdf')} but actual={with_pdf}")

    def counts(key, values):
        out = {}
        for value in values:
            if value == "多流态":
                out[value] = sum(1 for p in papers if p.get("regime") == value)
            else:
                out[value] = sum(1 for p in papers if value in (p.get(key) or []))
        return out

    for meta_key, paper_key, values_key in (
        ("tagCounts", "tags", "tags"),
        ("focusCounts", "focus", "focus"),
        ("boardCounts", "board", "boards"),
        ("regimeCounts", "regimes", "regimes"),
        ("methodCounts", "methods", "methods"),
        ("geometryCounts", "geometry", "geometries"),
        ("gasCounts", "real_gas", "gases"),
    ):
        expected = counts(paper_key, meta.get(values_key, []))
        actual = meta.get(meta_key) or {}
        diff = {k: (actual.get(k), expected[k]) for k in expected if actual.get(k) != expected[k]}
        if diff:
            errors.append(f"{meta_key} mismatch: {diff}")

    # Root pages still contain a few hard-coded totals and the taxonomy tag cloud.
    # Only check patterns that are present, so formatting changes do not cause
    # false failures.
    def root_text(name):
        path = ROOT / name
        return path.read_text(encoding="utf-8", errors="ignore") if path.is_file() else ""

    root_checks = (
        ("index.html", r'class="num">(\d+)</span>', total),
        ("index.html", r"本地 PDF：(\d+) 篇", with_pdf),
        ("index.html", r"综述：(\d+) 篇", meta.get("with_review")),
        ("index.html", r"标签：(\d+) 个", len(meta.get("tags", []))),
        ("index.html", r"共 (\d+) 篇", total),
        ("library.html", r"Library · (\d+) records", total),
        ("library.html", r'libTotal">(\d+)<', total),
        ("library.html", r"共 (\d+) 篇", total),
        ("reviews.html", r"通读全库 (\d+) 条记录", total),
        ("reviews.html", r"共 (\d+) 篇", total),
        ("taxonomy.html", r"共 (\d+) 篇", total),
    )
    for name, pattern, expected in root_checks:
        match = re.search(pattern, root_text(name))
        if match and int(match.group(1)) != expected:
            errors.append(f"{name}: {pattern} is {match.group(1)}, expected {expected}")

    taxonomy = root_text("taxonomy.html")
    for url_tag, _label, count in re.findall(
        r'library\.html\?tag=([^"]+)">([^<]*)<span class="tc">(\d+)</span>', taxonomy
    ):
        tag = unquote(url_tag)
        expected = (meta.get("tagCounts") or {}).get(tag)
        if expected is not None and int(count) != expected:
            errors.append(f"taxonomy.html: tag {tag} count {count}, expected {expected}")

    allowed_tags = set(meta.get("tags", []))
    allowed_focus = set(meta.get("focus", []))
    for paper in papers:
        bad = [t for t in (paper.get("tags") or []) if t not in allowed_tags]
        if bad:
            errors.append(f"unknown tags for id {paper.get('id')}: {bad}")
        bad = [f for f in (paper.get("focus") or []) if f not in allowed_focus]
        if bad:
            errors.append(f"unknown focus for id {paper.get('id')}: {bad}")

    seen_doi = {}
    seen_title = {}
    for paper in papers:
        doi = str(paper.get("doi", "") or "").lower()
        title = norm_title(paper.get("title"))
        if doi:
            if doi in seen_doi:
                warnings.append(f"duplicate DOI: {doi} ({seen_doi[doi]} / {paper.get('id')})")
            else:
                seen_doi[doi] = paper.get("id")
        if title:
            if title in seen_title:
                warnings.append(f"duplicate title: {seen_title[title]} / {paper.get('id')}")
            else:
                seen_title[title] = paper.get("id")

    print(f"checked {len(papers)} data papers and {len(pages)} HTML pages")
    for warning in warnings:
        print("WARN", warning)
    for error in errors:
        print("ERROR", error)
    if errors:
        print(f"FAILED: {len(errors)} error(s)")
        return 1
    print("OK: content and data are consistent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
