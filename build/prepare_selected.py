# -*- coding: utf-8 -*-
"""Prepare the curated SWBLI subset from the Zotero dump.

Run from the project root:
    python build/prepare_selected.py
"""
import json
import os
import re
import html

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
SRC = r"C:\Users\TYL13\AppData\Local\Temp\merged_candidates.json"
OUT = os.path.join(BASE, "selected_meta.json")

# Curated SWBLI subset (itemIDs in the merged Zotero snapshot).
IDS = [int(x) for x in """
846 1199 746 1458 1259 764 1316 1056 768 1256 770 1290 1194 1204 1202 822
1210 477 807 850 794 789 475 1190 1299 1462 776 772 868 1200 1216 482 478
1110 1116 462 460 459 1182 1176 1166 1150 1174 1222 1242 1162 1156 1275
1277 1291 1188 968 1460 721 384 799 843 793 856 1306 1466 902 752 895
1009 1010 1014 993 884 997 991 992 461 1324 878 880 503 742 1039 1303
490 489 488 491 501 835 839 834 286 911 975 1350 476 473 472 914 915
917 387 380 932 928 382 339 934 375 1002 1112 499 1069 1078 1089 1086
1091 1094 1064 1071 1073 1172 1255 696 635 645 660 643 623 1297 452
565 451 893 925 744 1126 1123
225 226 227 230 719 1022 1030 1033 1034 1282
""".split()]


def strip_html(s):
    if not s:
        return ""
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    return re.sub(r"[ \t]+", " ", s).strip()


def clean_text(s):
    """Turn the Crossref/CNKI abstract into readable Unicode text."""
    if not s:
        return ""
    s = strip_html(s)
    s = s.replace("$", "")
    reps = {
        r"\times": "×", r"\cdot": "·", r"\pm": "±", r"\sim": "~",
        r"\approx": "≈", r"\leq": "≤", r"\geq": "≥", r"\infty": "∞",
        r"\circ": "°", r"\degree": "°", r"\mu": "μ", r"\rho": "ρ",
        r"\Delta": "Δ", r"\delta": "δ", r"\alpha": "α", r"\beta": "β",
        r"\gamma": "γ", r"\lambda": "λ", r"\theta": "θ", r"\phi": "φ",
        r"\partial": "∂", r"\nabla": "∇", r"\rightarrow": "→",
        r"\left": "", r"\right": "", r"\,": " ", r"\;": " ",
        r"\!": "", r"\ ": " ",
    }
    for k, v in reps.items():
        s = s.replace(k, v)
    s = re.sub(r"\\(?:mathrm|text|textrm|mbox|operatorname)\{([^{}]*)\}", r"\1", s)
    s = re.sub(r"\^\{?(-?\d+)\}?", lambda m: str(m.group(1)).translate(
        str.maketrans("0123456789-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻")), s)
    s = re.sub(r"_\{?([^{}]*)\}?", r"\1", s)
    s = re.sub(r"\s*\\[a-zA-Z]+\s*", " ", s)
    s = re.sub(r"\s+([,.;:)\]])", r"\1", s)
    s = re.sub(r"([(])\s+", r"\1", s)
    s = re.sub(r"\s{2,}", " ", s)
    return s.strip()


def year_of(f):
    d = (f.get("date") or "").strip()
    m = re.search(r"(19|20)\d{2}", d)
    return m.group(0) if m else ""


def author_list(p):
    out = []
    for c in p.get("creators", []):
        if c.get("type") not in (None, "author"):
            continue
        first = (c.get("first") or "").strip()
        last = (c.get("last") or "").strip()
        if not (first or last):
            continue
        out.append({"first": first, "last": last})
    return out


def author_display(authors):
    if not authors:
        return ""
    names = []
    for a in authors:
        if a["first"]:
            names.append(f"{a['first']} {a['last']}")
        else:
            names.append(a["last"])
    if len(names) == 1:
        return names[0]
    if len(names) <= 3:
        return ", ".join(names[:-1]) + " and " + names[-1]
    return names[0] + " et al."


def main():
    with open(SRC, encoding="utf-8") as f:
        merged = json.load(f)
    byid = {p["itemID"]: p for p in merged}
    records = []
    for i in IDS:
        p = byid[i]
        f = p["fields"]
        title = strip_html(f.get("title") or "")
        abstract = clean_text(f.get("abstractNote") or "")
        notes = [n["text"] for n in p.get("all_notes", []) if n.get("text")]
        notes = [re.sub(r"\s+", " ", strip_html(n)).strip() for n in notes]
        notes = [n for n in notes if len(n) > 20]
        authors = author_list(p)
        is_zh = bool(re.search(r"[\u4e00-\u9fff]", title)) or \
            (f.get("language") or "").lower().startswith("zh")
        pdfs = p.get("pdfs", [])
        rec = {
            "id": i,
            "key": p.get("key", ""),
            "type": p.get("type", ""),
            "title": title,
            "season": "",
            "authors": authors,
            "author_display": author_display(authors),
            "year": year_of(f),
            "journal": f.get("publicationTitle") or f.get("conferenceName") or "",
            "journal_abbr": f.get("journalAbbreviation") or "",
            "volume": f.get("volume") or "",
            "issue": f.get("issue") or "",
            "pages": f.get("pages") or f.get("numPages") or "",
            "doi": f.get("DOI") or "",
            "url": f.get("url") or "",
            "publisher": f.get("publisher") or "",
            "place": f.get("place") or "",
            "edition": f.get("edition") or "",
            "isbn": f.get("ISBN") or "",
            "language": "zh" if is_zh else "en",
            "abstract_orig": abstract,
            "notes": notes,
            "zotero_tags": p.get("tags", []),
            "collections": p.get("collections", []),
            "pdfs": pdfs,
            "has_pdf": bool(pdfs),
            "pdftext": (
                os.path.join(BASE, "pdftext", f"{i}.txt")
                if os.path.exists(os.path.join(BASE, "pdftext", f"{i}.txt")) else ""
            ),
        }
        records.append(rec)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=1)
    print(f"wrote {len(records)} records -> {OUT}")
    print("with abstract:", sum(1 for r in records if r["abstract_orig"]))
    print("with notes:", sum(1 for r in records if r["notes"]))
    print("with pdf:", sum(1 for r in records if r["has_pdf"]))
    print("with pdftext:", sum(1 for r in records if r["pdftext"]))


if __name__ == "__main__":
    main()
