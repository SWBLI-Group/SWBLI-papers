# -*- coding: utf-8 -*-
"""Fetch citation / reference counts for the SWBLI atlas.

Sources
-------
- OpenAlex: cited_by_count and referenced_works_count (primary).
- Crossref: is-referenced-by-count and references-count (secondary).

The generated file is build/citation_metrics.json and is merged into the
site by build_site.py.  The original Zotero database is never modified.

Usage (run after build_site.py has refreshed assets/data.js):
    python build/fetch_citations.py
"""
from __future__ import annotations

import concurrent.futures
import difflib
import html
import json
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from datetime import date

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
DATA_JS = os.path.join(ROOT, "assets", "data.js")
OUT = os.path.join(BASE, "citation_metrics.json")

MAILTO = "swbli-atlas@example.com"
UA = "SWBLI-atlas/1.0 (mailto:%s)" % MAILTO
AS_OF = date.today().isoformat()
OPENALEX = "https://api.openalex.org"
CROSSREF = "https://api.crossref.org"


def norm_doi(doi: str) -> str:
    if not doi:
        return ""
    s = html.unescape(str(doi)).strip()
    s = re.sub(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)", "", s, flags=re.I)
    return s.strip().lower()


def doi_url(doi: str) -> str:
    return "https://doi.org/" + norm_doi(doi)


def norm_title(s: str) -> str:
    s = html.unescape(str(s or ""))
    s = unicodedata.normalize("NFKC", s).lower()
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"[^\w一-鿿]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def title_sim(a: str, b: str) -> float:
    a, b = norm_title(a), norm_title(b)
    if not a or not b:
        return 0.0
    return difflib.SequenceMatcher(None, a, b).ratio()


def year_int(v):
    m = re.search(r"(19|20)\d{2}", str(v or ""))
    return int(m.group(0)) if m else None


RATE_LIMITED = False


def get_json(url: str, tries: int = 4, timeout: int = 25):
    global RATE_LIMITED
    last = None
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.load(r)
        except urllib.error.HTTPError as exc:
            last = exc
            if exc.code == 429:
                RATE_LIMITED = True
            if exc.code in (400, 404):
                return None
            time.sleep(1.2 * (attempt + 1))
        except Exception as exc:  # network / timeout / JSON
            last = exc
            time.sleep(1.2 * (attempt + 1))
    print(f"!! request failed: {url[:140]} ({last})", file=sys.stderr)
    return None


def load_papers():
    raw = open(DATA_JS, encoding="utf-8").read()
    start = raw.index("{")
    end = raw.rindex("}")
    data = json.loads(raw[start:end + 1])
    return data.get("papers", [])


def openalex_batch(dois):
    """Return {normalized DOI: OpenAlex work} for up to ~50 DOIs."""
    if not dois:
        return {}
    filt = "doi:" + "|".join(doi_url(d) for d in dois)
    params = {
        "filter": filt,
        "per-page": 50,
        "select": "id,doi,title,publication_year,cited_by_count,referenced_works_count,type",
        "mailto": MAILTO,
    }
    url = OPENALEX + "/works?" + urllib.parse.urlencode(params)
    data = get_json(url)
    if not data:
        return {}
    out = {}
    for work in data.get("results", []):
        d = norm_doi(work.get("doi"))
        if d:
            out[d] = work
    return out


def openalex_title_search(title, year):
    if not title:
        return None
    params = {
        "search": title,
        "per-page": 5,
        "select": "id,doi,title,publication_year,cited_by_count,referenced_works_count,type",
        "mailto": MAILTO,
    }
    url = OPENALEX + "/works?" + urllib.parse.urlencode(params)
    data = get_json(url)
    if not data:
        return None
    best = None
    best_meta = None
    for work in data.get("results", []):
        sim = title_sim(title, work.get("title"))
        y = year_int(work.get("publication_year"))
        yy = year_int(year)
        if yy and y and abs(y - yy) > 1:
            continue
        threshold = 0.97 if len(norm_title(title)) < 25 else 0.90
        if sim < threshold:
            continue
        score = (sim, 1 if (yy and y and y == yy) else 0)
        if best is None or score > best_meta:
            best, best_meta = work, score
    if best is None:
        return None
    best["_match"] = "title"
    best["_title_similarity"] = round(best_meta[0], 3)
    return best


def crossref_one(doi):
    d = norm_doi(doi)
    if not d:
        return None
    url = f"{CROSSREF}/works/{urllib.parse.quote(d, safe='')}?mailto={urllib.parse.quote(MAILTO)}"
    data = get_json(url, tries=3, timeout=20)
    if not data:
        return None
    msg = data.get("message") or {}
    cited = msg.get("is-referenced-by-count")
    refs = msg.get("references-count")
    if cited is None and refs is None:
        return None
    return {
        "cited_by": int(cited) if isinstance(cited, int) else None,
        "references": int(refs) if isinstance(refs, int) else None,
        "url": "https://doi.org/" + d,
        "title": (msg.get("title") or [""])[0] if isinstance(msg.get("title"), list) else msg.get("title", ""),
        "match": "doi",
    }


def clean_openalex(work, match):
    return {
        "id": work.get("id"),
        "cited_by": int(work.get("cited_by_count") or 0),
        "references": int(work.get("referenced_works_count") or 0),
        "title": work.get("title") or "",
        "year": work.get("publication_year"),
        "type": work.get("type") or "",
        "match": match,
        "url": work.get("id") or "",
        **({"title_similarity": work.get("_title_similarity")} if work.get("_title_similarity") else {}),
    }


def main():
    papers = load_papers()
    print(f"papers: {len(papers)}")

    # 1) OpenAlex DOI batch
    by_doi = {}
    doi_records = [(p, norm_doi(p.get("doi"))) for p in papers if norm_doi(p.get("doi"))]
    doi_values = []
    seen = set()
    for _, d in doi_records:
        if d not in seen:
            seen.add(d)
            doi_values.append(d)
    openalex_ok = True
    for i in range(0, len(doi_values), 40):
        chunk = doi_values[i:i + 40]
        print(f"OpenAlex DOI batch {i // 40 + 1}/{(len(doi_values) + 39) // 40} ({len(chunk)} DOIs)")
        by_doi.update(openalex_batch(chunk))
        if RATE_LIMITED:
            print("OpenAlex rate limited; skipping OpenAlex and using Crossref only")
            openalex_ok = False
            break
        time.sleep(0.25)

    # 2) Title search for records without a DOI match (skip when rate limited)
    by_title = {}
    if openalex_ok:
        for p in papers:
            d = norm_doi(p.get("doi"))
            if d and d in by_doi:
                continue
            time.sleep(0.16)
            work = openalex_title_search(p.get("title"), p.get("year"))
            if RATE_LIMITED:
                print("OpenAlex rate limited during title search; stopping title lookups")
                openalex_ok = False
                break
            if work:
                by_title[int(p["id"])] = work
                print(f"  title match {p['id']}: {work.get('title', '')[:70]} ({work.get('_title_similarity')})")

    # 3) Crossref for DOI records (parallel, polite)
    crossref = {}
    def worker(item):
        pid, d = item
        return pid, crossref_one(d)

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
        futures = [ex.submit(worker, (int(p["id"]), p.get("doi"))) for p in papers if norm_doi(p.get("doi"))]
        for k, fut in enumerate(concurrent.futures.as_completed(futures), 1):
            try:
                pid, rec = fut.result()
            except Exception:
                continue
            if rec:
                crossref[pid] = rec
            if k % 25 == 0:
                print(f"Crossref {k}/{len(futures)}")

    # 4) Combine; keep previous records when both sources are unavailable,
    # so a temporary rate limit does not erase existing citation data.
    existing = {}
    if os.path.exists(OUT):
        try:
            with open(OUT, encoding="utf-8") as f:
                existing = json.load(f)
        except (OSError, ValueError):
            existing = {}
    out = {}
    for p in papers:
        pid = int(p["id"])
        d = norm_doi(p.get("doi"))
        oa_work = by_doi.get(d) if d else None
        oa_match = "doi"
        if not oa_work:
            oa_work = by_title.get(pid)
            oa_match = "title"
        oa = clean_openalex(oa_work, oa_match) if oa_work else None
        cr = crossref.get(pid)
        if not oa and not cr:
            if str(pid) in existing:
                out[str(pid)] = existing[str(pid)]
            continue
        # Citations: OpenAlex first, Crossref fallback.
        primary = oa or cr
        # References: Crossref's deposited reference list is usually more complete;
        # fall back to OpenAlex when Crossref reports zero/absent.
        ref_source = None
        ref_count = None
        for name, src in (("Crossref", cr), ("OpenAlex", oa)):
            if src and src.get("references") not in (None, 0):
                ref_source, ref_count = name, src.get("references")
                break
        if ref_count is None:
            ref_source = "OpenAlex" if oa else "Crossref"
            ref_count = (oa or cr).get("references")
        rec = {
            "id": pid,
            "cited_by": primary.get("cited_by"),
            "reference_count": ref_count,
            "reference_source": ref_source,
            "source": "OpenAlex" if oa else "Crossref",
            "source_url": primary.get("url") or "",
            "as_of": AS_OF,
            "match": primary.get("match") or "",
            "sources": [],
        }
        if oa:
            rec["sources"].append({"name": "OpenAlex", **oa})
        if cr:
            rec["sources"].append({"name": "Crossref", **cr})
        out[str(pid)] = rec

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"wrote {len(out)} records -> {OUT}")
    print("with OpenAlex:", sum(1 for r in out.values() if any(s["name"] == "OpenAlex" for s in r["sources"])))
    print("with Crossref:", sum(1 for r in out.values() if any(s["name"] == "Crossref" for s in r["sources"])))
    print("matched by title:", sum(1 for r in out.values() if r.get("match") == "title"))


if __name__ == "__main__":
    main()
