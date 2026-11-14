# -*- coding: utf-8 -*-
"""Validate records/ contributions without external dependencies.

Run:
    python build/validate_records.py
"""
import json
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
RECORDS_DIR = ROOT / "records"
DATA_PATH = ROOT / "assets" / "data.js"

BOARDS = {"流动分离", "初始分离", "峰值传热", "基础与工具"}
REGIMES = {"层流", "转捩", "湍流", "无粘", "非定常", "多流态"}
GASES = {"真实气体效应", "壁面催化", "壁面适应", "振动能激发", "稀薄气体效应", "化学非平衡", "振动能非平衡"}
METHODS = {"理论建模（控制方程）", "理论建模（数据驱动）", "稳定性分析", "实验研究", "数值模拟", "综述", "教材", "计算工具"}
GEOMETRIES = {"压缩拐角", "平板", "平板入射激波", "双楔", "双锥", "轴对称", "多构型", "纯方程", "其他"}
TAGS = {
    "课题组文章", "层流", "转捩", "湍流", "无粘", "非定常", "真实气体效应", "壁面催化",
    "壁面适应", "振动能激发", "稀薄气体效应", "化学非平衡", "振动能非平衡", "流动分离",
    "传热建模", "经验关联", "数据驱动", "理论建模", "实验研究", "数值模拟", "稳定性分析",
    "三维效应", "计算工具", "无粘激波干扰", "教材", "综述", "非定常性", "压缩拐角",
    "平板", "平板入射激波", "双楔", "双锥", "轴对称", "多构型", "纯方程",
}
FOCUS = {"马赫数效应", "雷诺数效应", "壁温效应", "轴对称效应", "三维效应", "湍流效应", "动壁效应", "非定常效应", "稳定性", "主动控制"}
EVIDENCE = {"摘要+笔记", "摘要", "PDF全文", "PDF摘要/结论页", "PDF摘要/目录", "题录/公开摘要（原文摘要缺失）", "仅题录"}
CONFIDENCE = {"高", "中", "低"}
STATUS = {"active", "retracted", "superseded"}
CONTENT_REQUIRED = {"title_zh", "gist", "abstract_zh", "main_work", "conclusions"}


def norm_title(t):
    return re.sub(r"[^0-9a-z一-鿿]+", "", str(t or "").lower())


def load_existing():
    if not DATA_PATH.exists():
        return set(), set()
    text = DATA_PATH.read_text(encoding="utf-8")
    data = json.loads(text[text.index("=") + 1:].strip().rstrip(";"))
    papers = data.get("papers", [])
    dois = {str(p.get("doi", "")).lower() for p in papers if p.get("doi")}
    titles = {norm_title(p.get("title")) for p in papers if p.get("title")}
    return dois, titles


def main():
    errors = []
    warnings = []
    existing_dois, existing_titles = load_existing()
    record_dois = set()
    record_titles = set()
    files = []
    if RECORDS_DIR.exists():
        files = sorted(
            p for p in RECORDS_DIR.rglob("*.json")
            if not p.name.startswith("_") and not p.name.startswith(".")
        )
    for path in files:
        rel = path.relative_to(ROOT)
        try:
            rec = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"{rel}: JSON parse error: {exc}")
            continue
        if not isinstance(rec, dict):
            errors.append(f"{rel}: top-level value must be an object")
            continue
        if rec.get("schema_version") != 1:
            errors.append(f"{rel}: schema_version must be 1")
        title = str(rec.get("title") or "").strip()
        if len(title) < 3:
            errors.append(f"{rel}: title is required")
        authors = rec.get("authors")
        if not isinstance(authors, list) or not authors:
            errors.append(f"{rel}: authors must be a non-empty array")
        if not str(rec.get("year") or "").strip():
            errors.append(f"{rel}: year is required")
        doi = str(rec.get("doi") or "").strip().lower()
        nt = norm_title(title)
        if doi and doi in existing_dois:
            errors.append(f"{rel}: DOI already exists in the library: {doi}")
        if nt and nt in existing_titles:
            errors.append(f"{rel}: title already exists in the library: {title[:80]}")
        if doi and doi in record_dois:
            errors.append(f"{rel}: duplicate DOI among records: {doi}")
        if nt and nt in record_titles:
            errors.append(f"{rel}: duplicate title among records: {title[:80]}")
        if doi:
            record_dois.add(doi)
        if nt:
            record_titles.add(nt)
        content = rec.get("content")
        if not isinstance(content, dict):
            errors.append(f"{rel}: content must be an object")
            content = {}
        for key in CONTENT_REQUIRED:
            if not str(content.get(key) or "").strip():
                errors.append(f"{rel}: content.{key} is required")
        gist = str(content.get("gist") or "")
        if len(gist) > 40:
            warnings.append(f"{rel}: content.gist is {len(gist)} chars (recommended <=40)")
        for key, allowed in (
            ("board", BOARDS), ("regimes", REGIMES), ("real_gas", GASES),
            ("methods", METHODS), ("geometry", GEOMETRIES), ("tags", TAGS), ("focus", FOCUS),
        ):
            values = rec.get(key)
            if not isinstance(values, list):
                errors.append(f"{rel}: {key} must be an array")
                continue
            bad = [v for v in values if v not in allowed]
            if bad:
                errors.append(f"{rel}: invalid {key}: {bad}")
        if rec.get("evidence") not in EVIDENCE:
            errors.append(f"{rel}: invalid evidence: {rec.get('evidence')!r}")
        if rec.get("confidence") not in CONFIDENCE:
            errors.append(f"{rel}: invalid confidence: {rec.get('confidence')!r}")
        if rec.get("status", "active") not in STATUS:
            errors.append(f"{rel}: invalid status: {rec.get('status')!r}")
        pdf_file = str(rec.get("pdf_file") or "").strip()
        if pdf_file:
            p = Path(pdf_file)
            if not p.is_absolute():
                p = ROOT / p
            if not p.is_file():
                warnings.append(f"{rel}: pdf_file not found locally: {pdf_file}")
        if rec.get("status", "active") != "active":
            warnings.append(f"{rel}: status is {rec.get('status')}; build will skip it")
    print(f"checked {len(files)} record(s)")
    for w in warnings:
        print("WARN", w)
    for e in errors:
        print("ERROR", e)
    if errors:
        print(f"FAILED: {len(errors)} error(s)")
        return 1
    print("OK: records are valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
