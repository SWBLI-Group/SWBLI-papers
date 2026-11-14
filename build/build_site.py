# -*- coding: utf-8 -*-
"""Build the static SWBLI literature atlas.

Usage:
    python build/build_site.py
"""
import html
import json
import math
import os
import re
import shutil
import sys
import unicodedata
from datetime import date
from pathlib import Path
from urllib.parse import quote as urlquote

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
META_PATH = BASE / "selected_meta.json"
CONTENT_GLOB = "content_*.json"
CITATION_METRICS_PATH = BASE / "citation_metrics.json"
# “高被引”只是一个便于浏览的展示阈值，不代表学科评价结论。
HIGH_CITED_MIN = 100

# LaTeX formulas are converted to MathML at build time so the generated
# site remains fully offline (no MathJax / KaTeX CDN request at runtime).
if str(BASE) not in sys.path:
    sys.path.insert(0, str(BASE))
try:
    from formula_latex import FORMULA_LATEX
except ImportError:  # pragma: no cover - allows building without the extra file
    FORMULA_LATEX = {}
try:
    from latex2mathml.converter import convert as latex_to_mathml
except ImportError:  # pragma: no cover
    latex_to_mathml = None

ALLOWED_BOARDS = ["流动分离", "初始分离", "峰值传热", "基础与工具"]
ALLOWED_FOCUS = ["马赫数效应", "雷诺数效应", "壁温效应", "轴对称效应", "三维效应", "湍流效应", "动壁效应", "非定常效应"]
# 流态是多值分面：同一篇文献可以同时是“层流 + 非定常”或“无粘 + 非定常”。
ALLOWED_REGIMES = ["层流", "转捩", "湍流", "无粘", "非定常", "多流态"]
ALLOWED_GASES = ["真实气体效应", "壁面催化", "壁面适应", "振动能激发", "稀薄气体效应", "化学非平衡", "振动能非平衡"]
ALLOWED_METHODS = ["理论建模（控制方程）", "理论建模（数据驱动）", "稳定性分析", "实验研究", "数值模拟", "综述", "教材", "计算工具"]
ALLOWED_GEOMETRIES = ["压缩拐角", "平板", "平板入射激波", "双楔", "双锥", "轴对称", "多构型", "纯方程", "其他"]
ALLOWED_ARTICLE_TYPES = ["教材", "会议", "期刊", "报告", "综述", "学位论文", "预印本"]
# 2000 年归入“2000~至今”，保证两个年代桶互斥。
ALLOWED_ERAS = ["2000~至今", "1900~2000"]
# 968《分离流动的某些进展》是一般分离流动综述，不纳入 SWBLI 专题综述页。
OUT_OF_SCOPE_REVIEW_IDS = {968}
# 专题综述按与 SWBLI 的相关性人工排序；未列出的综述排在后面。
REVIEW_PRIORITY = [501, 488, 491, 489, 490, 993, 1460, 1002, 835, 839, 834, 286, 2027, 2028]
# “初始分离”板块：以分离起始、初始分离条件或分离判据为主要研究对象的文献。
# 仅在正文中顺带提到“起始分离”的论文不纳入。
INITIAL_SEPARATION_IDS = {
    384, 461, 755, 768, 770, 776, 1064, 1069, 1071, 1073,
    1297, 1458, 1462, 1482, 2021, 2036,
}
# 关注点标签：读取 build/focus_tags.json 的人工标注。未标注条目保持为空，
# 不再按三维标签、轴对称构型或非定常流态自动回退，避免把构型/流态误当效应。
FOCUS_TAGS_PATH = BASE / "focus_tags.json"
DEEP_DIR = BASE / "deep"
FIGS_DIR = BASE / "figs"
ASSET_FIGS_DIR = ROOT / "assets" / "figs"
TAG_ORDER = [
    "课题组文章", "层流", "转捩", "湍流", "无粘", "非定常", "真实气体效应", "壁面催化", "壁面适应", "振动能激发",
    "稀薄气体效应", "化学非平衡", "振动能非平衡", "流动分离", "传热建模",
    "经验关联", "数据驱动", "理论建模", "实验研究", "数值模拟", "稳定性分析",
    "三维效应", "计算工具", "无粘激波干扰", "教材", "综述", "非定常性",
    "压缩拐角", "平板", "平板入射激波", "双楔", "双锥", "轴对称",
    "多构型", "纯方程", "无全文pdf",
]
ALLOWED_TAGS = set(TAG_ORDER)

# 期刊目录：只给流体力学与航空航天领域的经典/核心期刊单独设标签，
# 其余期刊统一归入“其他”，避免长尾刊名把目录撑得过长。
# 教材、学位论文、会议论文、报告与预印本归入“非期刊”；
# AIAA 会议论文与 NASA 报告另设专门标签，便于从目录中直接筛出。
JOURNAL_ABBREVIATIONS = {
    # 流体力学
    "journal of fluid mechanics": "JFM",
    "physics of fluids": "POF",
    "physical review fluids": "PRF",
    "annual review of fluid mechanics": "ARFM",
    "computers & fluids": "C&F",
    "fluid dynamics": "Fluid Dyn.",
    "experiments in fluids": "Exp. Fluids",
    "international journal of heat and fluid flow": "IJHFF",
    "international journal of heat and mass transfer": "IJHMT",
    # 航空航天
    "aiaa journal": "AIAA J",
    "shock waves": "Shock Waves",
    "aerospace science and technology": "AST",
    "progress in aerospace sciences": "PAS",
    "chinese journal of aeronautics": "CJA",
    "the aeronautical journal": "Aeronaut. J.",
    "acta astronautica": "Acta Astronaut.",
    "journal of spacecraft and rockets": "J. Spacecr. Rockets",
    "journal of the aeronautical sciences": "JAS",
    "journal of jet propulsion": "J. Jet Propuls.",
    "ceas space journal": "CEAS Space J.",
    "zeitschrift für flugwissenschaften und weltraumforschung": "ZFW",
    # 中文核心期刊
    "航空学报": "航空学报",
    "力学学报": "力学学报",
    "空气动力学学报": "空气动力学学报",
    "气体物理": "气体物理",
    "航空动力": "航空动力",
}
JOURNAL_ABBR_ALIASES = {
    "j. fluid mech.": "JFM",
    "phys. fluids": "POF",
    "aiaa j.": "AIAA J",
}
JOURNAL_GROUP_TAG = "课题组文章"
JOURNAL_NON_TAG = "非期刊"
JOURNAL_UNKNOWN_TAG = "刊名待核实"
JOURNAL_OTHER_TAG = "其他"
JOURNAL_AIAA_TAG = "AIAA Paper"
JOURNAL_NASA_TAG = "NASA报告"

# Flat-plate studies whose content geometry is currently "其他" rather than
# the incident-shock facet.  Papers already carrying "平板入射激波" get the
# broader "平板" geometry automatically.
FLAT_PLATE_IDS = {
    387, 339, 1064, 1069, 1078, 1094, 1150, 1156, 1162, 1166,
    1172, 1174, 1188, 1216, 1222, 1242, 1255,
}

# Authors of the research group; matching is case/punctuation-insensitive.
# Both English and Chinese forms are listed because Zotero stores Chinese
# papers with CJK surnames and no given-name field.
GROUP_AUTHORS = {
    ("bao", "lin"),
    ("yu", "yongliang"),
    ("wang", "zhihui"),
}
GROUP_AUTHOR_ALIASES = {
    "linbao", "baolin",
    "yongliangyu", "yuliangyong", "yuyongliang",
    "zhihuiwang", "wangzhihui",
    "鲍麟", "王智慧",
    "余永亮", "于永亮", "余勇亮", "于勇亮",
}

PALETTE = ["var(--teal)", "var(--red)", "var(--gold)", "var(--blue)", "var(--green)", "var(--faint)"]
METHOD_SHORT = {
    "理论建模（控制方程）": "控制方程",
    "理论建模（数据驱动）": "数据驱动",
    "稳定性分析": "稳定性",
    "实验研究": "实验",
    "数值模拟": "数值",
    "综述": "综述",
    "教材": "教材",
    "计算工具": "工具",
}
CITE_LABELS = {
    "jfm": "JFM（Cambridge）",
    "pof": "Physics of Fluids（AIP）",
    "cja": "Chinese Journal of Aeronautics（Elsevier）",
    "ast": "Aerospace Science and Technology（Elsevier）",
    "aiaa": "AIAA Journal",
    "prf": "Physical Review Fluids（APS）",
    "aia": "Advances in Aerodynamics（Springer）",
    "shock": "Shock Waves（Springer）",
    "ams": "Acta Mechanica Sinica（力学学报英文）",
    "lxxb": "力学学报",
    "qtl": "气体物理",
    "taml": "力学快报（英文）",
    "zh_en": "英文期刊（中文文献，in Chinese）",
    "bibtex": "BibTeX",
}


# --------------------------------------------------------------------------
# loading and normalization
# --------------------------------------------------------------------------

def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def as_list(v):
    if v is None:
        return []
    if isinstance(v, list):
        return v
    return [v]


def clean_str(v):
    return re.sub(r"\s+", " ", str(v or "")).strip()


def journal_tags_for(p):
    """Map a venue to a short journal label.

    Classic fluid-mechanics/aerospace journals keep their own label; other
    serials fall back to '其他'. AIAA conference papers and NASA reports get
    dedicated labels so they remain filterable from the journal directory.
    """
    kind = clean_str(p.get("type"))
    has_venue = False
    for field in ("journal", "journal_abbr"):
        key = clean_str(p.get(field)).lower()
        if not key:
            continue
        has_venue = True
        tag = JOURNAL_ABBREVIATIONS.get(key) or JOURNAL_ABBR_ALIASES.get(key)
        if tag:
            return [tag]
    venue = " ".join(
        clean_str(p.get(field))
        for field in ("journal", "journal_abbr", "publisher", "institution")
    )
    if kind == "report" and re.search(
        r"\bNASA\b|national aeronautics and space administration", venue, re.I
    ):
        return [JOURNAL_NASA_TAG]
    if kind in ("conferencePaper", "journalArticle") and re.search(
        r"\bAIAA\b|american institute of aeronautics|aerospace sciences meeting"
        r"|fluid and plasma\s*dynamics conference",
        venue,
        re.I,
    ):
        return [JOURNAL_AIAA_TAG]
    if has_venue:
        return [JOURNAL_OTHER_TAG] if kind == "journalArticle" else [JOURNAL_NON_TAG]
    if kind == "journalArticle":
        return [JOURNAL_UNKNOWN_TAG]
    return [JOURNAL_NON_TAG]


_MATH_SYMBOLS = {
    r"\times": "×", r"\cdot": "·", r"\pm": "±", r"\mp": "∓",
    r"\le": "≤", r"\leq": "≤", r"\ge": "≥", r"\geq": "≥",
    r"\ne": "≠", r"\neq": "≠", r"\approx": "≈", r"\sim": "∼",
    r"\infty": "∞", r"\partial": "∂", r"\nabla": "∇",
    r"\alpha": "α", r"\beta": "β", r"\gamma": "γ", r"\delta": "δ",
    r"\epsilon": "ε", r"\varepsilon": "ε", r"\zeta": "ζ", r"\eta": "η",
    r"\theta": "θ", r"\kappa": "κ", r"\lambda": "λ", r"\mu": "μ",
    r"\nu": "ν", r"\xi": "ξ", r"\pi": "π", r"\rho": "ρ",
    r"\sigma": "σ", r"\tau": "τ", r"\phi": "φ", r"\varphi": "φ",
    r"\chi": "χ", r"\psi": "ψ", r"\omega": "ω", r"\Omega": "Ω",
    r"\Delta": "Δ", r"\Gamma": "Γ", r"\Lambda": "Λ", r"\Sigma": "Σ",
    r"\Phi": "Φ", r"\Psi": "Ψ",
}


def plain_math(v):
    """Normalise stray LaTeX in generated content to text + Unicode."""
    s = clean_str(v).replace("$", "")
    s = re.sub(r"\\left|\\right", "", s)
    for _ in range(4):
        s2 = re.sub(r"\\d?frac\{([^{}]*)\}\{([^{}]*)\}", r"(\1)/(\2)", s)
        if s2 == s:
            break
        s = s2
    s = re.sub(r"\\sqrt\{([^{}]*)\}", r"√(\1)", s)
    s = re.sub(r"\\(?:mathrm|text|mathit|mathbf|mathsf|rm|it|bf)\{([^{}]*)\}", r"\1", s)
    for k in sorted(_MATH_SYMBOLS, key=len, reverse=True):
        s = s.replace(k, _MATH_SYMBOLS[k])
    s = re.sub(r"\^\{([^{}]*)\}", r"^(\1)", s)
    s = re.sub(r"_\{([^{}]*)\}", r"_(\1)", s)
    s = s.replace("{", "(").replace("}", ")")
    s = polish_citation(s)
    return s


def norm_tags(tags):
    out = []
    for t in as_list(tags):
        t = clean_str(t)
        if t in ALLOWED_TAGS and t not in out:
            out.append(t)
    return out


def person_key(value):
    return re.sub(r"[^a-z]", "", str(value or "").lower())


def name_key(value):
    """Keep letters and CJK characters, drop spaces and punctuation."""
    return re.sub(r"[^0-9a-z一-鿿]", "", str(value or "").lower())


def is_group_author_paper(authors):
    """True when any author matches the three group authors in EN or ZH form."""
    for author in as_list(authors):
        if not isinstance(author, dict):
            continue
        last = name_key(author.get("last"))
        first = name_key(author.get("first"))
        if (person_key(author.get("last")), person_key(author.get("first"))) in GROUP_AUTHORS:
            return True
        candidates = {last + first, first + last, last}
        if candidates & GROUP_AUTHOR_ALIASES:
            return True
    return False


def year_int(y):
    m = re.search(r"(19|20)\d{2}", str(y or ""))
    return int(m.group(0)) if m else 0


def era_for(y):
    """Publication-era facet. Unknown years stay empty (shown as 未标注)."""
    yi = year_int(y)
    if not yi:
        return ""
    if yi >= 2000:
        return "2000~至今"
    if yi >= 1900:
        return "1900~2000"
    return ""


def article_types_for(p):
    """Derive a multi-valued article-type facet from Zotero type + review flag."""
    kind = p.get("type", "")
    out = []
    if kind == "thesis":
        out.append("学位论文")
    elif kind == "preprint":
        out.append("预印本")
    elif kind in ("conferencePaper", "bookSection"):
        out.append("会议")
    elif kind == "book":
        out.append("教材")
    elif kind == "report":
        # 报告不再按发布机构细分，NASA、NACA、AGARD、大学/实验室报告统一为“报告”。
        out.append("报告")
    else:
        # journalArticle, preprint: formal serial publication
        out.append("期刊")
    if "教材" in p.get("methods", []):
        out.append("教材")
    if p.get("review") and p.get("id") not in OUT_OF_SCOPE_REVIEW_IDS:
        out.append("综述")
    return [t for t in ALLOWED_ARTICLE_TYPES if t in set(out)]


def inscope_reviews(papers):
    """Reviews that belong to the SWBLI survey page, most relevant first."""
    reviews = [p for p in papers if p.get("review") and p["id"] not in OUT_OF_SCOPE_REVIEW_IDS]
    rank = {pid: i for i, pid in enumerate(REVIEW_PRIORITY)}
    reviews.sort(key=lambda p: (rank.get(p["id"], len(rank)), -year_int(p["year"]), p["id"]))
    return reviews


def build_author_display(authors):
    if not authors:
        return "Anon."
    names = []
    for a in authors:
        if a.get("first"):
            names.append(f"{a['first']} {a['last']}")
        else:
            names.append(a.get("last", ""))
    if len(names) == 1:
        return names[0]
    if len(names) <= 3:
        return ", ".join(names[:-1]) + " and " + names[-1]
    return names[0] + " et al."


def build_author_full(authors):
    return "; ".join(
        (f"{a.get('first','')} {a.get('last','')}".strip()) for a in authors
    ) if authors else "Anon."


def norm_content(meta_by_id, content):
    """Merge one content record with its bibliographic metadata."""
    pid = int(content.get("id"))
    m = meta_by_id[pid]
    c = dict(content)

    board = [b for b in as_list(c.get("board")) if b in ALLOWED_BOARDS]
    if pid in INITIAL_SEPARATION_IDS and "初始分离" not in board:
        board.append("初始分离")
    board = [b for b in ALLOWED_BOARDS if b in set(board)]
    if not board:
        board = ["基础与工具"]

    raw_regimes = as_list(c.get("regimes")) or as_list(c.get("regime"))
    regimes = []
    for r in raw_regimes:
        if r in ALLOWED_REGIMES and r not in regimes:
            regimes.append(r)
    # “多流态”是跨流态/通用工作的兜底标签；一旦给出了具体流态，
    # 就不再保留“多流态”，避免与具体流态并列造成重复计数。
    specific = [r for r in regimes if r != "多流态"]
    if specific:
        regimes = specific
    else:
        regimes = ["多流态"]
    regime = regimes[0] if len(regimes) == 1 else "多流态"
    regime_display = " / ".join(regimes)

    gases = [g for g in as_list(c.get("real_gas")) if g in ALLOWED_GASES]
    if any(g != "真实气体效应" for g in gases) and "真实气体效应" not in gases:
        gases.insert(0, "真实气体效应")
    if "真实气体效应" in gases and len(gases) == 1:
        pass

    methods = [x for x in as_list(c.get("methods")) if x in ALLOWED_METHODS]
    if not methods:
        methods = ["理论建模（控制方程）"]

    geoms = [g for g in as_list(c.get("geometry")) if g in ALLOWED_GEOMETRIES]
    if not geoms:
        # 新数据应显式写“多构型”或“纯方程”；缺失时按“纯方程”兜底。
        geoms = ["纯方程"]
    # "平板" is the base geometry; incident-shock flat-plate cases carry both
    # facets, and a small explicit set covers flat-plate boundary-layer papers
    # that were previously filed under "其他".
    if ("平板入射激波" in geoms or pid in FLAT_PLATE_IDS) and "平板" not in geoms:
        geoms.append("平板")
    geoms = [g for g in ALLOWED_GEOMETRIES if g in set(geoms)]

    tags = norm_tags(c.get("tags"))
    # facet -> controlled tag coherence
    for r in regimes:
        if r in ("层流", "转捩", "湍流", "无粘", "非定常") and r not in tags:
            tags.append(r)
    for g in gases:
        if g not in tags:
            tags.append(g)
    for g in geoms:
        if g in ALLOWED_TAGS and g not in tags:
            tags.append(g)
    method_tag_map = {
        "理论建模（控制方程）": ["理论建模"],
        "理论建模（数据驱动）": ["理论建模", "数据驱动"],
        "稳定性分析": ["稳定性分析"],
        "实验研究": ["实验研究"],
        "数值模拟": ["数值模拟"],
        "综述": ["综述"],
        "教材": ["教材"],
        "计算工具": ["计算工具"],
    }
    for meth in methods:
        for t in method_tag_map.get(meth, []):
            if t not in tags:
                tags.append(t)
    if "流动分离" in board and "流动分离" not in tags:
        tags.append("流动分离")
    if is_group_author_paper(m.get("authors", [])) and "课题组文章" not in tags:
        tags.append("课题组文章")
    if pid in OUT_OF_SCOPE_REVIEW_IDS:
        tags = [t for t in tags if t != "综述"]
    tags = [t for t in TAG_ORDER if t in set(tags)]

    # 关注点是“文中把该参数作为变量并明确讨论其影响”的证据型标签，
    # 不再从构型/流态自动回退，避免把“三维计算”误标成“三维效应”。
    # 人工标注集中在 build/focus_tags.json；未标注的条目保持为空。
    focus = [f for f in as_list(c.get("focus")) if f in ALLOWED_FOCUS]
    focus = [f for f in ALLOWED_FOCUS if f in set(focus)]

    formula = c.get("formula")
    if isinstance(formula, str):
        formula = {"name": "核心公式", "expr": formula, "idea": ""}
    if not isinstance(formula, dict) or not clean_str(formula.get("expr")):
        formula = None
    else:
        formula = {
            "name": clean_str(formula.get("name")) or "核心公式",
            "expr": plain_math(formula.get("expr")),
            "idea": plain_math(formula.get("idea")),
        }

    review = c.get("review")
    if isinstance(review, str):
        review = {"sections": [], "status": review, "gaps": ""}
    if not isinstance(review, dict) or not (review.get("sections") or review.get("status") or review.get("gaps")):
        review = None
    if pid in OUT_OF_SCOPE_REVIEW_IDS:
        review = None
    if review:
        secs = []
        for s in as_list(review.get("sections")):
            if isinstance(s, dict) and (s.get("name") or s.get("summary")):
                secs.append({"name": clean_str(s.get("name")), "summary": clean_str(s.get("summary"))})
            elif isinstance(s, str):
                secs.append({"name": "", "summary": clean_str(s)})
        review = {
            "sections": secs,
            "status": clean_str(review.get("status")),
            "gaps": clean_str(review.get("gaps")),
        }

    abstract = clean_str(c.get("abstract_zh")) or clean_str(m.get("abstract_orig"))[:420]
    main_work = clean_str(c.get("main_work"))
    conclusions = clean_str(c.get("conclusions"))
    background = clean_str(c.get("background"))
    method_detail = clean_str(c.get("method_detail"))
    findings = clean_str(c.get("findings"))
    limits = clean_str(c.get("limits"))
    derivation_idea = clean_str(c.get("derivation_idea"))
    derivation_steps = [clean_str(x) for x in as_list(c.get("derivation_steps")) if clean_str(x)]
    problem_solved = clean_str(c.get("problem_solved"))
    key_findings = [clean_str(x) for x in as_list(c.get("key_findings")) if clean_str(x)]
    if not main_work:
        main_work = "该条目的结构化摘要暂缺；可参考原始摘要与 Zotero 笔记进一步核对。"
    if not conclusions:
        conclusions = "该条目的结论提炼暂缺；建议结合原文摘要与结论部分阅读。"

    p = {
        "id": pid,
        "key": m.get("key", ""),
        "type": m.get("type", ""),
        "title": m.get("title", ""),
        "title_zh": clean_str(c.get("title_zh")) or m.get("title", ""),
        "gist": clean_str(c.get("gist")),
        "authors": m.get("authors", []),
        "author_display": m.get("author_display") or build_author_display(m.get("authors", [])),
        "author_full": build_author_full(m.get("authors", [])),
        "year": m.get("year", ""),
        "era": era_for(m.get("year", "")),
        "journal": m.get("journal", ""),
        "journal_abbr": m.get("journal_abbr", ""),
        "publisher": m.get("publisher", ""),
        "place": m.get("place", ""),
        "edition": m.get("edition", ""),
        "isbn": m.get("isbn", ""),
        "volume": m.get("volume", ""),
        "issue": m.get("issue", ""),
        "pages": m.get("pages", ""),
        "doi": m.get("doi", ""),
        "url": m.get("url", ""),
        "language": m.get("language", "en"),
        "abstract_orig": m.get("abstract_orig", ""),
        "notes": m.get("notes", []),
        "collections": m.get("collections", []),
        "zotero_tags": m.get("zotero_tags", []),
        "board": board,
        "regime": regime,
        "regimes": regimes,
        "regime_display": regime_display,
        "real_gas": gases,
        "methods": methods,
        "geometry": geoms,
        "focus": focus,
        "tags": tags,
        "abstract_zh": abstract,
        "main_work": main_work,
        "conclusions": conclusions,
        "background": background,
        "method_detail": method_detail,
        "findings": findings,
        "limits": limits,
        "derivation_idea": derivation_idea,
        "derivation_steps": derivation_steps,
        "problem_solved": problem_solved,
        "key_findings": key_findings,
        "scope_note": (
            "该文是一般分离流动综述，不属于激波/边界层干扰专题综述；"
            "本图谱仅将其保留为分离流动背景，不纳入“综述与研究空白”页。"
            if pid in OUT_OF_SCOPE_REVIEW_IDS else ""
        ),
        "formula": formula,
        "review": review,
        "related": [],
        "evidence": clean_str(c.get("evidence")) or "摘要",
        "confidence": clean_str(c.get("confidence")) or "中",
        "pdfs": m.get("pdfs", []),
        "pdf_href": "",
        "pdf_name": "",
        "href": f"papers/{pid}.html",
    }
    p["journal_tags"] = journal_tags_for(p)
    if p["type"] == "book":
        pub = clean_str(p.get("publisher")) or clean_str(p.get("journal")) or "—"
        place = clean_str(p.get("place"))
        edition = clean_str(p.get("edition"))
        venue = f"{pub}, {place}" if place else pub
        if edition:
            venue = f"{edition}; {venue}"
        p["venue"] = venue
    else:
        p["venue"] = clean_str(p.get("journal")) or clean_str(p.get("journal_abbr")) or ""

    if p["pdfs"]:
        raw = p["pdfs"][0]
        p["pdf_name"] = os.path.basename(raw)
        try:
            p["pdf_href"] = Path(raw).as_uri()
        except Exception:
            p["pdf_href"] = "file:///" + raw.replace("\\", "/").replace(" ", "%20")
    # 状态标签：没有本地全文时自动标记，便于检索并配合 DOI/来源链接使用。
    # 放在 TAG_ORDER 末尾，避免它抢占“同标签文献”的首个主题标签。
    if not p["pdf_href"] and "无全文pdf" not in p["tags"]:
        p["tags"].append("无全文pdf")
    p["article_types"] = article_types_for(p)
    return p


# --------------------------------------------------------------------------
# citations
# --------------------------------------------------------------------------

def initials(first):
    if not first:
        return ""
    parts = re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ]+", first)
    return " ".join(p[0].upper() + "." for p in parts)


def author_amp(authors):
    items = []
    for a in authors:
        last = a.get("last", "").strip()
        ini = initials(a.get("first", ""))
        items.append(f"{last}, {ini}" if ini else last)
    if not items:
        return "Anon."
    if len(items) <= 6:
        if len(items) == 1:
            return items[0]
        return ", ".join(items[:-1]) + " & " + items[-1]
    return items[0] + " et al."


def author_and(authors):
    items = []
    for a in authors:
        last = a.get("last", "").strip()
        ini = initials(a.get("first", ""))
        items.append(f"{last}, {ini}" if ini else last)
    if not items:
        return "Anon."
    if len(items) <= 6:
        if len(items) == 1:
            return items[0]
        return ", ".join(items[:-1]) + ", and " + items[-1]
    return items[0] + " et al."


def author_comma(authors):
    items = []
    for a in authors:
        last = a.get("last", "").strip()
        ini = initials(a.get("first", ""))
        items.append(f"{last}, {ini}" if ini else last)
    if not items:
        return "Anon."
    if len(items) > 6:
        return items[0] + " et al."
    return ", ".join(items)


def author_aiaa(authors):
    if not authors:
        return "Anon."
    first = authors[0]
    head = f"{first.get('last','')}, {initials(first.get('first',''))}".strip().rstrip(",")
    rest = []
    for a in authors[1:]:
        ini = initials(a.get("first", ""))
        rest.append(f"{ini} {a.get('last','')}".strip())
    if len(authors) > 6:
        return head + " et al."
    if not rest:
        return head
    if len(rest) == 1:
        return head + ", and " + rest[0]
    return head + ", " + ", ".join(rest[:-1]) + ", and " + rest[-1]


def author_gb(authors):
    items = []
    for a in authors:
        last = a.get("last", "").strip()
        ini = initials(a.get("first", "")).replace(".", "").strip()
        items.append(f"{last} {ini}".strip())
    if not items:
        return "Anon."
    if len(items) > 6:
        return items[0] + ", et al"
    return ", ".join(items)


def author_full_list(authors):
    items = []
    for a in authors:
        last = a.get("last", "").strip()
        first = a.get("first", "").strip()
        items.append(f"{last}, {first}" if first else last)
    return " and ".join(items) if items else "Anon."


def clean_title(t):
    t = clean_str(t)
    return t.rstrip(". ")


def polish_citation(s):
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r"\.{2,}", ".", s)
    s = re.sub(r"\?\.", "?", s)
    s = re.sub(r"!\.", "!", s)
    s = re.sub(r",\.", ",", s)
    return s


def en_pages(pages):
    s = clean_str(pages)
    return re.sub(r"(\d)-(\d)", r"\1–\2", s)


def cite_data(p):
    authors = p.get("authors", [])
    a_amp = author_amp(authors)
    a_and = author_and(authors)
    a_comma = author_comma(authors)
    a_aiaa = author_aiaa(authors)
    a_gb = author_gb(authors)
    a_full = author_full_list(authors)
    year = p.get("year", "")
    title = clean_title(p.get("title", ""))
    is_book = p.get("type") == "book"
    publisher = clean_str(p.get("publisher")) or clean_str(p.get("journal")) or "—"
    place = clean_str(p.get("place"))
    edition = clean_str(p.get("edition"))
    journal = publisher if is_book else (
        clean_str(p.get("journal")) or clean_str(p.get("journal_abbr"))
        or clean_str(p.get("publisher")) or "—"
    )
    book_pub = f"{publisher}, {place}" if place else publisher
    book_venue = f"{edition}. {book_pub}" if edition else book_pub
    book_venue_zh = f"{edition}. " if edition else ""
    book_venue_zh += f"{place}: {publisher}" if place else publisher
    vol = clean_str(p.get("volume"))
    issue = clean_str(p.get("issue"))
    pages = en_pages(p.get("pages", ""))
    doi = clean_str(p.get("doi"))
    url = clean_str(p.get("url"))
    link = f"https://doi.org/{doi}" if doi else url
    # Some CNKI exports end in an empty query (filename=/dbname=); drop those.
    if link and re.search(r"(?:filename|dbname|dbcode)=$", link):
        link = ""

    vol_issue = ""
    if vol and issue:
        vol_issue = f"{vol} ({issue})"
    elif vol:
        vol_issue = vol
    elif issue:
        vol_issue = f"({issue})"

    def tail(prefix=" "):
        bits = []
        if vol_issue:
            bits.append(vol_issue)
        if pages:
            bits.append(pages)
        s = ", ".join(bits)
        return (prefix + s) if s else ""

    def link_tail(prefix=" "):
        if link:
            return prefix + link
        return ""

    out = {}

    # 1. JFM / Cambridge author-year
    if is_book:
        s = f"{a_amp} {year} {title}. {book_venue}."
    else:
        s = f"{a_amp} {year} {title}. {journal}{tail()}."
    if link:
        s += f" {link}"
    out["jfm"] = {"label": CITE_LABELS["jfm"], "text": polish_citation(s)}

    # 2. Physics of Fluids / AIP
    if is_book:
        s = f'{a_and}. "{title}." {book_venue} ({year}).'
    else:
        s = f'{a_and}. "{title}." {journal}{tail()} ({year}).'
    if link:
        s += f" {link}"
    out["pof"] = {"label": CITE_LABELS["pof"], "text": polish_citation(s)}

    # 3. Chinese Journal of Aeronautics / Elsevier
    if is_book:
        s = f"{a_comma}. {title}. {book_venue}, {year}."
    else:
        s = f"{a_comma}. {title}. {journal}, {year}"
        if vol_issue:
            s += f", {vol_issue}"
        if pages:
            s += f": {pages}"
        s += "."
    if link:
        s += f" {link}"
    out["cja"] = {"label": CITE_LABELS["cja"], "text": polish_citation(s)}

    # 4. Aerospace Science and Technology / Elsevier
    if is_book:
        s = f"{a_comma}. {title}. {book_venue}, {year}."
    else:
        s = f"{a_comma}. {title}. {journal}, {year}"
        if vol_issue:
            s += f", {vol_issue}"
        if pages:
            s += f": {pages}"
        s += "."
    if link:
        s += f" {link}"
    out["ast"] = {"label": CITE_LABELS["ast"], "text": polish_citation(s)}

    # 5. AIAA Journal
    vn = []
    if vol:
        vn.append(f"Vol. {vol}")
    if issue:
        vn.append(f"No. {issue}")
    vns = ", ".join(vn)
    if is_book:
        s = f'{a_aiaa}, "{title}," {book_venue}, {year}.'
    else:
        s = f'{a_aiaa}, "{title}," {journal}'
        if vns:
            s += f", {vns}"
        s += f", {year}"
        if pages:
            s += f", pp. {pages}"
        s += "."
    if link:
        s += f" {link}"
    out["aiaa"] = {"label": CITE_LABELS["aiaa"], "text": polish_citation(s)}

    # 6. Physical Review Fluids / APS
    if is_book:
        s = f'{a_and}, "{title}," {book_venue} ({year}).'
    else:
        s = f'{a_and}, "{title}," {journal}'
        if vol:
            s += f" {vol}"
        if pages:
            s += f", {pages}"
        s += f" ({year})."
    if link:
        s += f" {link}"
    out["prf"] = {"label": CITE_LABELS["prf"], "text": polish_citation(s)}

    # 7-9. Springer style
    for key in ("aia", "shock", "ams"):
        if is_book:
            s = f"{a_comma}. {title}. {book_venue} ({year})."
        else:
            s = f"{a_comma}. {title}. {journal}"
            if vol:
                s += f" {vol}"
            if pages:
                s += f", {pages}"
            s += f" ({year})."
        if link:
            s += f" {link}"
        out[key] = {"label": CITE_LABELS[key], "text": polish_citation(s)}

    # 10-12. Chinese styles
    for key, jname in (("lxxb", "力学学报"), ("qtl", "气体物理")):
        if is_book:
            s = f"{a_gb}. {title}[M]. {book_venue_zh}, {year}."
        else:
            s = f"{a_gb}. {title}[J]. {journal}, {year}"
            if vol_issue:
                s += f", {vol_issue}"
            if pages:
                s += f": {pages}"
            s += "."
        if link:
            s += f" {link}"
        out[key] = {"label": CITE_LABELS[key], "text": polish_citation(s)}

    if is_book:
        s = f"{a_comma}. {title}. {book_venue}, {year}."
    else:
        s = f"{a_comma}. {title}. {journal}, {year}"
        if vol_issue:
            s += f", {vol_issue}"
        if pages:
            s += f": {pages}"
        s += "."
    if link:
        s += f" {link}"
    out["taml"] = {"label": CITE_LABELS["taml"], "text": polish_citation(s)}

    # 13. Chinese-language paper cited in an English-language journal.
    # Keep the original Chinese author names and title; append "(in Chinese)".
    if p.get("language") == "zh":
        if is_book:
            s = f"{a_amp} ({year}). {title}. {book_venue_zh}."
        else:
            s = f"{a_amp} ({year}). {title}. {journal}"
            if vol_issue:
                s += f", {vol_issue}"
            if pages:
                s += f", {pages}"
            s += "."
        if link:
            s += f" {link}"
        s += " (in Chinese)."
        out["zh_en"] = {"label": CITE_LABELS["zh_en"], "text": polish_citation(s)}

    # 14. BibTeX
    first_last = re.sub(r"[^A-Za-z0-9]", "", (authors[0].get("last", "") if authors else ""))
    if not first_last:
        first_last = f"p{p['id']}"
    first_word = re.sub(r"[^A-Za-z0-9]", "", title.split()[0].lower()) if title.split() else "paper"
    bkey = f"{first_last.lower()}{year}{first_word}"
    entry = "article"
    if p.get("type") == "conferencePaper":
        entry = "inproceedings"
    elif p.get("type") == "book":
        entry = "book"
    elif p.get("type") == "bookSection":
        entry = "incollection"
    elif p.get("type") == "thesis":
        entry = "phdthesis"
    elif p.get("type") == "report":
        entry = "techreport"
    elif p.get("type") == "preprint":
        entry = "misc"
    fields = [("author", a_full), ("title", "{" + title + "}")]
    if entry in ("inproceedings", "incollection"):
        fields.append(("booktitle", journal))
        publisher = clean_str(p.get("publisher"))
        if publisher:
            fields.append(("publisher", publisher))
    elif entry == "book":
        fields.append(("publisher", publisher))
        if place:
            fields.append(("address", place))
        if edition:
            fields.append(("edition", edition))
        if p.get("isbn"):
            fields.append(("isbn", clean_str(p.get("isbn"))))
    elif entry == "phdthesis":
        fields.append(("school", journal))
    elif entry == "techreport":
        fields.append(("institution", clean_str(p.get("publisher")) or journal))
        fields.append(("number", journal))
    elif entry == "misc":
        fields.append(("howpublished", journal))
    else:
        fields.append(("journal", journal))
    fields.append(("year", year))
    if vol:
        fields.append(("volume", vol))
    if issue:
        fields.append(("number", issue))
    if pages and entry not in ("book", "phdthesis"):
        fields.append(("pages", pages.replace("–", "--")))
    if doi:
        fields.append(("doi", doi))
    if url and not doi:
        fields.append(("url", url))
    body = ",\n".join(f"  {k} = {{{v}}}" for k, v in fields if v)
    out["bibtex"] = {"label": CITE_LABELS["bibtex"], "text": f"@{entry}{{{bkey},\n{body}\n}}"}

    return out


# --------------------------------------------------------------------------
# related papers
# --------------------------------------------------------------------------

def compute_related(papers, manual):
    by_id = {p["id"]: p for p in papers}
    for p in papers:
        candidates = []
        tags = set(p["tags"]) - {"课题组文章", "无全文pdf"}
        boards = set(p["board"])
        geoms = set(p["geometry"])
        for q in papers:
            if q["id"] == p["id"]:
                continue
            score = 0
            score += 2 * len(tags & (set(q["tags"]) - {"课题组文章", "无全文pdf"}))
            score += 3 * len(boards & set(q["board"]))
            score += 3 * len(geoms & set(q["geometry"]))
            shared_regimes = (set(p["regimes"]) & set(q["regimes"])) - {"多流态"}
            if shared_regimes:
                score += 1
            if p["year"] and q["year"] and abs(year_int(p["year"]) - year_int(q["year"])) <= 3:
                score += 0.5
            if score > 0:
                candidates.append((score, q["id"]))
        candidates.sort(key=lambda x: (-x[0], x[1]))
        chosen = []
        for rid in manual.get(p["id"], []):
            if rid in by_id and rid != p["id"] and rid not in chosen:
                chosen.append(rid)
        for _, rid in candidates:
            if len(chosen) >= 4:
                break
            if rid not in chosen:
                chosen.append(rid)
        p["related"] = chosen[:4]
    # connection counts used for "core papers"
    deg = {p["id"]: 0 for p in papers}
    for p in papers:
        for rid in p["related"]:
            deg[rid] = deg.get(rid, 0) + 1
            deg[p["id"]] = deg.get(p["id"], 0) + 1
    for p in papers:
        p["connections"] = deg.get(p["id"], 0)


# --------------------------------------------------------------------------
# HTML helpers
# --------------------------------------------------------------------------

def e(s):
    return html.escape(str(s if s is not None else ""), quote=True)


def paras(text):
    t = clean_str(text)
    if not t:
        return ""
    parts = [x.strip() for x in re.split(r"\n{2,}|\r\n\r\n", str(text)) if x.strip()]
    if len(parts) <= 1:
        return f"<p>{e(t)}</p>"
    return "".join(f"<p>{e(p)}</p>" for p in parts)


def conclusion_html(text):
    t = clean_str(text)
    if not t:
        return ""
    parts = [x.strip(" 。；;") for x in re.split(r"[；;]\s*", t) if x.strip(" 。；;")]
    if len(parts) >= 3:
        return '<div class="concl-list">' + "".join(f'<div class="ci"><span>{e(x)}</span></div>' for x in parts) + "</div>"
    return f"<p>{e(t)}</p>"


def donut_svg(items, size=168, stroke=24):
    total = sum(max(0, v) for _, v, _ in items)
    r = (size - stroke) / 2
    c = 2 * math.pi * r
    cx = cy = size / 2
    chunks = []
    if total <= 0:
        chunks.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="var(--paper-2)" stroke-width="{stroke}"/>')
    else:
        offset = 0.0
        for _, v, color in items:
            if v <= 0:
                continue
            seg = c * v / total
            draw = max(seg - 2.2, 0.8)
            chunks.append(
                f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{color}" '
                f'stroke-width="{stroke}" stroke-dasharray="{draw:.2f} {c - draw:.2f}" '
                f'stroke-dashoffset="{-offset:.2f}" transform="rotate(-90 {cx} {cy})" stroke-linecap="butt"/>'
            )
            offset += seg
    return f'<svg viewBox="0 0 {size} {size}" width="{size}" height="{size}" role="img" aria-hidden="true">{"".join(chunks)}</svg>'


def legend_html(items):
    rows = []
    for name, v, color in items:
        rows.append(
            f'<div class="legend-row"><span class="dot" style="background:{color}"></span>'
            f'<span class="lname" title="{e(name)}">{e(name)}</span><span class="lv">{v}</span></div>'
        )
    return '<div class="legend">' + "".join(rows) + "</div>"


def hbars_html(items, color="var(--teal)"):
    mx = max([v for _, v in items] or [1]) or 1
    rows = []
    for name, v in items:
        pct = max(2, round(v / mx * 100)) if v else 0
        rows.append(
            f'<div class="hbar" style="--accent:{color}"><span title="{e(name)}">{e(name)}</span>'
            f'<div class="track"><div class="fill" style="width:{pct}%"></div></div>'
            f'<span class="hv">{v}</span></div>'
        )
    return '<div class="hbars">' + "".join(rows) + "</div>"


def matrix_html(meta, papers):
    regimes = list(ALLOWED_REGIMES)
    methods = ALLOWED_METHODS
    counts = {}
    mx = 1
    for r in regimes:
        for m in methods:
            n = sum(1 for p in papers if (r in p.get("regimes", []) or (r == "多流态" and len(p.get("regimes", [])) > 1)) and m in p["methods"])
            counts[(r, m)] = n
            mx = max(mx, n)
    head = "".join(f"<th>{e(METHOD_SHORT[m])}</th>" for m in methods)
    rows = []
    for r in regimes:
        cells = []
        for m in methods:
            n = counts[(r, m)]
            pct = round(n / mx * 82) if n else 0
            cls = "" if n else ' class="zero"'
            style = f"background:color-mix(in srgb, var(--teal) {pct}%, transparent)" if n else ""
            cells.append(f'<td{cls} style="{style}" title="{e(r)} × {e(m)}：{n} 篇">{n if n else "·"}</td>')
        rows.append(f'<tr><th class="row-h">{e(r)}</th>{"".join(cells)}</tr>')
    return f'<div class="table-wrap"><table class="matrix"><thead><tr><th></th>{head}</tr></thead><tbody>{"".join(rows)}</tbody></table></div>'


def timeline_html(meta, papers):
    decades = list(range(1950, 2030, 10))
    counts = {d: 0 for d in decades}
    for p in papers:
        y = year_int(p["year"])
        if y:
            d = y - (y % 10)
            if d in counts:
                counts[d] += 1
    mx = max(counts.values()) if counts else 1
    cols = []
    labs = []
    for d in decades:
        v = counts[d]
        h = max(2, round(v / mx * 130)) if v else 2
        cols.append(f'<div class="tl-col"><span class="tl-val">{v or ""}</span><div class="tl-bar" style="height:{h}px"></div></div>')
        labs.append(f"<span>{str(d)[2:]}s</span>")
    pins = []
    pin_ids = [846, 1259, 822, 477, 843, 799, 380, 932, 384, 1039]
    by = {p["id"]: p for p in papers}
    for pid in pin_ids:
        p = by.get(pid)
        if p:
            pins.append(f'<a class="tl-pin" href="{e(p["href"])}"><b>{e(p["year"])}</b>{e(p["author_display"].split(" et al.")[0].split(",")[0])}</a>')
    return (
        '<div class="timeline"><div class="tl-bars">' + "".join(cols) + '</div>'
        '<div class="tl-lab">' + "".join(labs) + "</div>"
        '<div class="tl-pins">' + "".join(pins) + "</div></div>"
    )


def citation_html(p):
    cites = p.get("citations") or {}
    if not cites:
        return ""
    keys = list(cites.keys())
    opts = "".join(f'<option value="{e(k)}">{e(cites[k]["label"])}</option>' for k in keys)
    return f'''<details class="cite" data-cite data-pid="{p["id"]}">
      <summary>引用格式 <span aria-hidden="true">▾</span></summary>
      <div class="cite-pop">
        <div class="cite-top"><select data-cite-select aria-label="选择引用格式">{opts}</select>
        <button class="btn small" type="button" data-copy-cite>复制</button></div>
        <pre data-cite-pre>{e(cites[keys[0]]["text"])}</pre>
        <div class="cite-foot"><span class="hint">按各刊常见风格排版，出处保留原刊名</span>{f'<a href="https://doi.org/{e(p["doi"])}" target="_blank" rel="noopener">DOI ↗</a>' if p.get("doi") else ""}</div>
      </div>
    </details>'''


def board_badge(b):
    cls = "teal" if b == "流动分离" else "blue" if b == "初始分离" else "red" if b == "峰值传热" else "gold"
    return f'<span class="badge {cls}">{e(b)}</span>'


def tags_html(p, limit=99, root=""):
    """root="" for pages at site root, root="../" for pages under papers/."""
    # 状态标签优先显示，避免条目标签较多时被截断；但存储顺序仍把它放在末尾。
    ordered = [t for t in p["tags"] if t == "无全文pdf"] + [t for t in p["tags"] if t != "无全文pdf"]
    out = []
    for t in ordered[:limit]:
        status = t == "无全文pdf"
        title = ' title="本库无全文文件，可通过 DOI 或来源页获取"' if status else ""
        out.append(
            f'<a class="tag{" no-pdf" if status else ""}" '
            f'href="{root}library.html?tag={e(t)}"{title}>{e(t)}</a>'
        )
    return "".join(out)


def detail_href(p, nested=False):
    """p["href"] is papers/<id>.html; inside papers/ use just <id>.html."""
    return p["href"].split("/")[-1] if nested else p["href"]


def access_btn(p, small=True):
    """No local PDF: point to the DOI, or to the source page when no DOI exists."""
    cls = f'btn {"small " if small else ""}ghost'
    if p.get("doi"):
        return (f'<a class="{cls}" href="https://doi.org/{e(p["doi"])}" target="_blank" rel="noopener" '
                f'title="通过 DOI 获取原文">DOI ↗</a>')
    if p.get("url"):
        return (f'<a class="{cls}" href="{e(p["url"])}" target="_blank" rel="noopener" '
                f'title="打开来源页面">来源 ↗</a>')
    return ""


def pdf_btn(p, small=True, allow_upload=False):
    if p.get("pdf_href"):
        return (f'<a class="btn {"small " if small else ""}ghost" data-pdf-link href="{e(p["pdf_href"])}" '
                f'target="_blank" rel="noopener">PDF ↗</a>')
    link = access_btn(p, small=small)
    if allow_upload:
        return (link + '<span class="pdf-slot" data-pdf-slot>'
                '<button class="btn small primary" type="button" data-upload-trigger '
                'aria-controls="pdfUpload">上传 PDF 补充全文</button></span>')
    return link or '<span class="badge pdf-missing" data-pdf-slot>无本地 PDF</span>'


def fmt_count(v):
    return "—" if v is None else f"{int(v):,}"


def citation_badge(p):
    """Small, sortable indicator shown on cards and detail pages."""
    if p.get("cited_by") is None:
        return ""
    hot = ' hot' if p.get("highly_cited") else ""
    src = p.get("citation_source") or "学术平台"
    ref_src = p.get("reference_source") or src
    tip = f"{src} 被引 {fmt_count(p.get('cited_by'))} 次；{ref_src} 记录参考文献 {fmt_count(p.get('reference_count'))} 篇"
    if p.get("citation_as_of"):
        tip += f"，截至 {p['citation_as_of']}"
    label = "高被引" if p.get("highly_cited") else "被引"
    return f'<span class="badge cite{hot}" title="{e(tip)}">{label} {fmt_count(p.get("cited_by"))}</span>'


def reference_badge(p):
    """Secondary indicator for the outgoing reference count."""
    if p.get("reference_count") is None:
        return ""
    src = p.get("reference_source") or p.get("citation_source") or "学术平台"
    tip = f"{src} 记录的参考文献 {fmt_count(p.get('reference_count'))} 篇"
    return f'<span class="badge ref" title="{e(tip)}">参考 {fmt_count(p.get("reference_count"))}</span>'


def journal_badge(p):
    """Short journal label, e.g. JFM / POF; non-journals are marked explicitly."""
    return "".join(
        f'<span class="badge journal{" non" if t == JOURNAL_NON_TAG else ""}" title="期刊目录：{e(t)}">{e(t)}</span>'
        for t in (p.get("journal_tags") or [])
    )


def citation_metrics_html(p):
    """Detail-page block with source-disaggregated counts."""
    sources = p.get("citation_sources") or []
    if p.get("cited_by") is None and not sources:
        return ('<div class="hr" style="margin:14px 0"></div><h4>学术影响</h4>'
                '<p class="small muted">未在 OpenAlex / Crossref 检索到匹配记录。'
                '中文文献、教材或学位论文可能未被这些平台完整收录；这里不推测、不补零。</p>')
    rows = []
    for s in sources:
        name = s.get("name") or "平台"
        url = s.get("url") or ""
        label = f'{name} ↗' if url else name
        cite = fmt_count(s.get("cited_by"))
        refs = fmt_count(s.get("references"))
        match = "题名匹配" if s.get("match") == "title" else "DOI 匹配"
        inner = f'<span class="cs-name">{e(label)}</span><span class="cs-num">被引 {cite} · 参考 {refs} <em>{e(match)}</em></span>'
        rows.append(f'<a class="cite-source" href="{e(url)}" target="_blank" rel="noopener">{inner}</a>' if url else f'<div class="cite-source">{inner}</div>')
    primary = p.get("citation_source") or ""
    match_label = "题名匹配" if p.get("citation_match") == "title" else "DOI 匹配"
    as_of = p.get("citation_as_of") or ""
    return f'''<div class="hr" style="margin:14px 0"></div><h4>学术影响</h4>
      <div class="cm-grid">
        <div class="cm"><strong>{fmt_count(p.get("cited_by"))}</strong><span>被引</span></div>
        <div class="cm"><strong>{fmt_count(p.get("reference_count"))}</strong><span>参考文献</span></div>
      </div>
      <div class="citation-sources">{''.join(rows)}</div>
      <div class="evidence-note">被引主口径：{e(primary)}（{e(match_label)}）；参考文献优先采用 Crossref，缺失时用 OpenAlex{('，截至 ' + e(as_of)) if as_of else ''}。不同平台收录范围与计数口径不同；高被引标识阈值为 ≥{HIGH_CITED_MIN} 次，仅供浏览排序，不代表学科评价。</div>'''


def card_html(p, lib=False):
    kicker = "".join(board_badge(b) for b in p["board"])
    kicker += "".join(
        f'<span class="badge gold">{e(t)}</span>'
        for t in p.get("article_types", []) if t != "期刊"
    )
    kicker += journal_badge(p)
    kicker += f'<span class="badge">{e(p["regime"])}</span>'
    if p["methods"]:
        kicker += f'<span class="badge blue">{e(p["methods"][0])}</span>'
    kicker += citation_badge(p)
    if lib:
        kicker += reference_badge(p)
    abstract = f'<p class="lc-abs">{e(p["abstract_zh"])}</p>' if lib else ""
    accent = "red" if "峰值传热" in p["board"] else "blue" if "初始分离" in p["board"] else "teal" if "流动分离" in p["board"] else "gold"
    if "流动分离" in p["board"] and "峰值传热" in p["board"]:
        accent = "both"
    cls = "paper-card lib-card both" if lib and accent == "both" else ("paper-card lib-card" if lib else "paper-card")
    style = "" if accent == "both" else f' style="--accent:var(--{accent})"'
    return f'''<article class="{cls}"{style}>
      <div class="{'lc-top' if lib else ''}">
        <div class="{'lc-main' if lib else ''}">
          <div class="pc-kicker">{kicker}</div>
          <h3><a href="{e(p["href"])}">{e(p["title"])}</a></h3>
          <div class="{'lc-zh' if lib else 'zh-title'}">{e(p["title_zh"])}</div>
          <div class="{'lc-meta' if lib else 'pc-meta'}">
            <span>{e(p["author_display"])}</span>
            <span>{e(p["venue"])}{(" · " + e(p["year"])) if p["year"] else ""}</span>
            {f'<span>Vol. {e(p["volume"])}{("(" + e(p["issue"]) + ")") if p["issue"] else ""}</span>' if p["volume"] else ""}
            {f'<span>{e(p["pages"])}</span>' if p["pages"] else ""}
          </div>
          {abstract}
          <div class="pc-tags">{tags_html(p, 6 if lib else 4)}</div>
        </div>
        <div class="{'lc-actions' if lib else ''}">
          {citation_html(p)}
          {pdf_btn(p)}
        </div>
      </div>
    </article>'''


def page_shell(title, body, root="", active=""):
    nav = [("index.html", "总览", "index"), ("library.html", "文献库", "library"),
           ("reviews.html", "综述与空白", "reviews"), ("taxonomy.html", "方法与规范", "taxonomy")]
    nav_html = "".join(
        f'<a href="{root}{href}" class="{"active" if active == key else ""}">{label}</a>'
        for href, label, key in nav
    )
    return f'''<!doctype html>
<html lang="zh-CN" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="高超声速激波/边界层干扰文献库：流动分离与峰值传热的知识地图。">
<meta name="color-scheme" content="light dark">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'><circle cx='32' cy='32' r='30' fill='%231e5f63'/><text x='32' y='39' font-size='18' text-anchor='middle' fill='%23fff9ee' font-family='monospace'>SW</text></svg>">
<link rel="stylesheet" href="{root}assets/style.css">
<link rel="stylesheet" href="{root}assets/katex/katex.min.css">
</head>
<body>
<a class="skip" href="#main">跳到正文</a>
<header class="topbar">
  <div class="topbar-inner">
    <a class="brand" href="{root}index.html"><span class="mark">SW</span>激波 / 边界层干扰文献图谱</a>
    <nav class="nav">{nav_html}</nav>
    <div class="top-actions"><button class="icon-btn" id="themeBtn" type="button" aria-label="切换主题">◐</button></div>
  </div>
</header>
{body}
<footer class="footer">
  <div class="wrap footer-inner">
    <div><span class="fmark">SWBLI Literature Atlas</span> · 本地离线文献图谱 · 数据来自 Zotero 文献库</div>
    <div>共 {len(DATA_PAPERS)} 篇 · 生成于 {date.today().isoformat()} · <a href="{root}taxonomy.html">分类与证据说明</a></div>
  </div>
</footer>
<script src="{root}assets/data.js"></script>
<script src="{root}assets/app.js"></script>
<script src="{root}assets/upload.js"></script>
<script defer src="{root}assets/katex/katex.min.js"></script>
<script defer src="{root}assets/katex/auto-render.min.js"></script>
<script defer src="{root}assets/katex/katex-init.js"></script>
</body>
</html>'''


# --------------------------------------------------------------------------
# page renderers
# --------------------------------------------------------------------------

def render_index(meta, papers):
    total = len(papers)
    board_counts = meta["boardCounts"]
    regime_items = [(r, meta["regimeCounts"].get(r, 0), PALETTE[i % len(PALETTE)]) for i, r in enumerate(ALLOWED_REGIMES)]
    method_items = [(m, meta["methodCounts"].get(m, 0), PALETTE[i % len(PALETTE)]) for i, m in enumerate(ALLOWED_METHODS)]

    def board_card(key, cls, title, en, desc):
        rows = [(r, meta["boardRegime"].get(key, {}).get(r, 0)) for r in ALLOWED_REGIMES]
        mx = max([v for _, v in rows] or [1]) or 1
        bars = "".join(
            f'<div class="rb"><div class="bar" style="height:{max(3, round(v / mx * 46))}px" title="{n}：{v}"></div><span class="rl">{n[:1] if n != "多流态" else "多"}</span></div>'
            for n, v in rows
        )
        top_tags = meta["boardTags"].get(key, [])[:3]
        tag_html = "".join(f"<span>{e(t)}</span>" for t in top_tags)
        return f'''<a class="board-card {cls}" href="library.html?board={e(key)}">
          <div class="bc-top">
            <div><div class="bc-kicker">{e(en)}</div><h3>{e(title)}</h3><div class="bc-en">{e(desc)}</div></div>
            <div class="bc-count">{board_counts.get(key, 0)}<small> 篇</small></div>
          </div>
          <div class="bc-mid"><div class="regime-bars">{bars}</div><div class="bc-tags">{tag_html}</div></div>
          <span class="bc-arrow">→</span>
        </a>'''

    # 课题组文章优先：前三个位置留给组内高关联论文，其余位置给全库高关联论文。
    group = sorted(
        [p for p in papers if "课题组文章" in p["tags"]],
        key=lambda p: (-p["connections"], -year_int(p["year"])),
    )
    others = sorted(
        [p for p in papers if "课题组文章" not in p["tags"]],
        key=lambda p: (-p["connections"], -year_int(p["year"])),
    )
    top = group[:3] + others[: max(0, 6 - len(group[:3]))]
    featured = "".join(card_html(p) for p in top)
    cited_top = sorted(
        [p for p in papers if p.get("cited_by") is not None],
        key=lambda p: (-p["cited_by"], -year_int(p["year"])),
    )[:6]
    cited_featured = "".join(card_html(p) for p in cited_top)
    reviews = inscope_reviews(papers)
    review_items = reviews[:3]
    review_html = "".join(
        f'''<div class="review-part"><h4><a href="{e(p["href"])}">{e(p["title_zh"])}</a></h4>
        <p>{e((p["review"].get("gaps") or p["review"].get("status") or "")[:190])}{"…" if len((p["review"].get("gaps") or p["review"].get("status") or "")) > 190 else ""}</p></div>'''
        for p in review_items
    )

    body = f'''<main id="main">
<section class="hero"><div class="wrap">
  <div class="hero-grid">
    <div class="reveal">
      <div class="eyebrow">Zotero Library · Shock-Wave / Boundary-Layer Interaction</div>
      <h1>把激波/边界层干扰，<br>读成一张<em>可检索的地图</em>。</h1>
      <p class="lede">从流动分离的判据与尺度，到再附峰值热流的理论模型；从层流三层结构，到转捩与湍流的稳定性分析。{total} 篇文献按流动分离、初始分离与峰值传热三条主线重新编目，并为每篇提供中文摘要、主要工作、结论与 12 种引用风格（另附 BibTeX；中文文献另加英文期刊的 in Chinese 格式）。</p>
      <div class="hero-actions">
        <a class="btn primary" href="library.html">进入文献库 →</a>
        <a class="btn" href="taxonomy.html">查看分类体系</a>
      </div>
    </div>
    <div class="hero-side reveal">
      <p class="note">“分离是激波与边界层相互作用的起点，峰值热流则是它留给壁面的代价。”</p>
      <div class="sig">— 以流动分离与峰值传热为两条主线</div>
      <div class="hr"></div>
      <div class="sig">本地 PDF：{meta["with_pdf"]} 篇 · SWBLI 专题综述：{len(reviews)} 篇 · 标签：{len(meta["tags"])} 个</div>
      <div class="sig">平台被引数据：{meta["withCitation"]} / {total} 篇（OpenAlex 主、Crossref 辅，截至 {e(meta["citationAsOf"])}）</div>
    </div>
  </div>
  <div class="stats">
    <div class="stat"><span class="num">{total}</span><span class="lab">篇精选文献</span></div>
    <div class="stat"><span class="num">{len(reviews)}</span><span class="lab">篇 SWBLI 专题综述</span></div>
    <div class="stat"><span class="num">12</span><span class="lab">种期刊风格 + 中文 in Chinese</span></div>
  </div>
</div></section>

<section class="wrap">
  <div class="board-grid">
    {board_card("流动分离", "sep", "流动分离", "FLOW SEPARATION", "判据、分离尺度、三层结构、非定常分离与流动控制")}
    {board_card("初始分离", "onset", "初始分离", "INITIAL SEPARATION", "分离起始条件、初始分离尺度、分离判据与起始点预测")}
    {board_card("峰值传热", "heat", "峰值传热", "PEAK HEAT TRANSFER", "再附热流、斜驻点模型、真实气体效应与热防护")}
  </div>
  <p class="board-note">教材、计算工具与纯无粘激波背景归入 <a href="library.html?board=基础与工具">基础与工具</a>；综述按覆盖内容同时归入相关板块；初始分离文献同时保留流动分离板块。</p>
</section>

<section class="wrap grid-2" style="margin-top:20px">
  <div class="panel reveal">
    <div class="panel-head"><h2>流态构成</h2><a class="more" href="library.html">筛选 →</a></div>
    <div class="chart-flex">
      <div class="donut-wrap">{donut_svg(regime_items)}<div class="donut-center"><span class="dc-num">{total}</span><span class="dc-lab">PAPERS</span></div></div>
      {legend_html(regime_items)}
    </div>
  </div>
  <div class="panel reveal">
    <div class="panel-head"><h2>方法构成</h2><a class="more" href="taxonomy.html">方法说明 →</a></div>
    <div class="chart-flex">
      <div class="donut-wrap">{donut_svg(method_items)}<div class="donut-center"><span class="dc-num">{len(ALLOWED_METHODS)}</span><span class="dc-lab">METHODS</span></div></div>
      {legend_html(method_items)}
    </div>
  </div>
</section>

<section class="wrap panel reveal" style="margin-top:20px">
  <div class="panel-head"><h2>流态 × 方法</h2><span class="muted small">交叉计数，颜色越深文献越集中</span></div>
  {matrix_html(meta, papers)}
</section>

<section class="wrap panel reveal" style="margin-top:20px">
  <div class="panel-head"><h2>时间脉络</h2><span class="muted small">按十年统计；下方为各阶段的坐标性工作</span></div>
  {timeline_html(meta, papers)}
</section>

<section class="wrap grid-2" style="margin-top:20px">
  <div class="panel reveal">
    <div class="panel-head"><h2>真实气体效应</h2><span class="muted small">可多选标签</span></div>
    {hbars_html([(g, meta["gasCounts"].get(g, 0)) for g in ALLOWED_GASES], "var(--red)")}
  </div>
  <div class="panel reveal">
    <div class="panel-head"><h2>构型分布</h2><span class="muted small">压缩拐角、入射激波、锥体、多构型与纯方程</span></div>
    {hbars_html([(g, meta["geometryCounts"].get(g, 0)) for g in ALLOWED_GEOMETRIES], "var(--gold)")}
  </div>
</section>

<section class="wrap panel reveal" style="margin-top:20px">
  <div class="panel-head"><h2>关联度最高的文献</h2><a class="more" href="library.html?sort=connections">按关联度浏览 →</a></div>
  <div class="featured-grid">{featured}</div>
</section>

<section class="wrap panel reveal" style="margin-top:20px">
  <div class="panel-head"><h2>被引最多的文献</h2><a class="more" href="library.html?sort=citations">按被引浏览 →</a></div>
  <div class="featured-grid">{cited_featured or '<p class="muted">尚无平台被引数据。</p>'}</div>
  <p class="muted small" style="margin-top:12px">被引数来自 OpenAlex（主）与 Crossref（辅），由 DOI 或题名匹配，截至 {e(meta["citationAsOf"])}。不同平台收录范围不同，数值只用于相对浏览；未匹配的文献不补零。</p>
</section>

<section class="wrap panel reveal" style="margin-top:20px">
  <div class="panel-head"><h2>综述与研究空白</h2><a class="more" href="reviews.html">全部综述 →</a></div>
  <div class="review-block">{review_html or '<p class="muted">暂无综述条目。</p>'}</div>
</section>

<section class="wrap panel reveal" style="margin-top:20px;margin-bottom:40px">
  <div class="panel-head"><h2>三条阅读路径</h2><span class="muted small">从经典到前沿</span></div>
  <div class="grid-3">
    <div class="review-part"><h4>① 分离判据与三层结构</h4><p>Lighthill &amp; Newman (1953) → Chapman (1958) → Lees &amp; Reeves (1964) → Stewartson &amp; Williams (1969) → Katzer (1989)。</p><p><a href="library.html?tag=理论建模">按“理论建模”筛选 →</a></p></div>
    <div class="review-part"><h4>② 峰值热流与真实气体</h4><p>方芳 &amp; 鲍麟 (2021) → 李贤冬等 (2021) → Ju et al. (2024, 2026)；关注振动能激发、壁面催化与稀薄气体效应。</p><p><a href="library.html?board=峰值传热">进入峰值传热板块 →</a></p></div>
    <div class="review-part"><h4>③ 非定常与稳定性</h4><p>Guiho et al. (2016) → Song et al. (2023) → Song et al. (2025)；配合 Robinet 的全局稳定性与转捩边界层非定常分析。</p><p><a href="library.html?tag=稳定性分析">按“稳定性分析”筛选 →</a></p></div>
  </div>
</section>
</main>'''
    return page_shell("激波/边界层干扰文献图谱", body, "", "index")


def render_library(meta, papers):
    body = f'''<main id="main">
<section class="library-head"><div class="wrap">
  <div class="eyebrow">Library · {len(papers)} records</div>
  <h1>文献库</h1>
  <p class="lede">标题保持原文，点开进入详情页；每张卡片可展开 12 种引用风格与 BibTeX，中文文献另有英文期刊的 in Chinese 格式。检索切面整体可拉起/收起，内部类别默认直接展开，仅“期刊目录”可再折叠；关注点按“参数覆盖范围 + 正文明确讨论”标注，不再从构型或流态自动回退。被引与参考文献数来自 OpenAlex（主）和 Crossref（辅），可按被引排序；筛选和排序条件会写入网址，便于收藏与分享。</p>
</div></section>

<div class="filter-shell"><div class="wrap">
  <div class="filter-top">
    <label class="searchbox"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.6-3.6"/></svg>
      <input id="libSearch" type="search" placeholder="搜索标题、作者、摘要、标签、DOI…" autocomplete="off">
    </label>
    <select id="libSort" aria-label="排序方式">
      <option value="year-desc">年份：新 → 旧</option>
      <option value="year-asc">年份：旧 → 新</option>
      <option value="citations">被引：高 → 低</option>
      <option value="references">参考文献：多 → 少</option>
      <option value="connections">关联度</option>
      <option value="title">标题 A → Z</option>
    </select>
    <span class="filter-count"><b id="libCount">{len(papers)}</b> / <span id="libTotal">{len(papers)}</span> 篇</span>
    <button class="btn small ghost" id="libReset" type="button">重置</button>
  </div>
  <details class="facet-shell" id="facetShell">
    <summary class="facet-shell-summary">
      <span class="facet-shell-caret" aria-hidden="true"></span>
      <span class="facet-shell-title">检索切面</span>
      <span class="facet-shell-hint">板块、文章类型、关注点、标签、年代、流态、方法、构型、真实气体、期刊目录</span>
      <span class="facet-state" id="facetShellState"></span>
    </summary>
    <div class="facet-rows">
      <div class="facet-block" data-facets="board" data-label="板块">
        <div class="facet-head"><span class="flabel">板块</span><span class="facet-state"></span></div>
      </div>
      <div class="facet-block" data-facets="articleType" data-label="文章类型">
        <div class="facet-head"><span class="flabel">文章类型</span><span class="facet-state"></span></div>
      </div>
      <div class="facet-block" data-facets="focus" data-label="关注点">
        <div class="facet-head"><span class="flabel">关注点</span><span class="facet-state"></span></div>
      </div>
      <details class="facet-block facet-journal" data-facets="tag" data-label="标签">
        <summary class="facet-head"><span class="facet-caret" aria-hidden="true"></span><span class="flabel">标签</span><span class="facet-state"></span></summary>
      </details>
      <div class="facet-block" data-facets="era" data-label="年代">
        <div class="facet-head"><span class="flabel">年代</span><span class="facet-state"></span></div>
      </div>
      <div class="facet-block" data-facets="regime" data-label="流态">
        <div class="facet-head"><span class="flabel">流态</span><span class="facet-state"></span></div>
      </div>
      <div class="facet-block" data-facets="method" data-label="方法">
        <div class="facet-head"><span class="flabel">方法</span><span class="facet-state"></span></div>
      </div>
      <div class="facet-block" data-facets="geometry" data-label="构型">
        <div class="facet-head"><span class="flabel">构型</span><span class="facet-state"></span></div>
      </div>
      <div class="facet-block" data-facets="gas" data-label="真实气体">
        <div class="facet-head"><span class="flabel">真实气体</span><span class="facet-state"></span></div>
      </div>
      <details class="facet-block facet-journal" data-facets="journal" data-label="期刊目录">
        <summary class="facet-head"><span class="facet-caret" aria-hidden="true"></span><span class="flabel">期刊目录</span><span class="facet-state"></span></summary>
      </details>
    </div>
  </details>
  <div class="active-filters" id="activeFilters"></div>
</div></div>

<div class="wrap"><div class="library-list" id="libraryList"></div></div>
<noscript><div class="wrap"><div class="noscript">文献库筛选需要启用 JavaScript。你仍可直接打开各篇详情页。</div></div></noscript>
</main>'''
    return page_shell("文献库 · 激波/边界层干扰", body, "", "library")


def render_reviews(meta, papers):
    # 逐篇卡片按出版年份从新到旧排列；相关性优先序只用于首页推荐。
    reviews = sorted(inscope_reviews(papers), key=lambda p: (-year_int(p["year"]), p["id"]))
    cards = []
    for p in reviews:
        secs = "".join(
            f'<div class="rc-sec"><b>{e(s["name"] or "专题")}</b><span>{e(s["summary"])}</span></div>'
            for s in (p["review"].get("sections") or [])
        )
        status = p["review"].get("status", "")
        gaps = p["review"].get("gaps", "")
        cards.append(f'''<article class="panel review-card">
          <div class="rc-top"><div><h3><a href="{e(p["href"])}">{e(p["title"])}</a></h3>
          <div class="rc-src">{e(p["author_display"])} · {e(p["journal"])} {e(p["year"])}</div></div>
          <div class="pc-tags">{tags_html(p, 3)}</div></div>
          <div class="rc-secs">{secs}</div>
          {f'<div class="rc-status"><b>发展现状</b>{e(status)}</div>' if status else ""}
          {f'<div class="rc-gaps"><b>研究空白</b>{e(gaps)}</div>' if gaps else ""}
        </article>''')

    # 阅读全库 218 条记录后重写：每条都给出代表性条目/年份；有分歧的地方保留分歧。
    synthesis = [
        ("层流分离：局部理论成熟，统一判据未闭合并",
         "自由干扰与三层理论已能自洽解释分离区上游的局部压力上升（822/1969；846/1953；1256/1967），并给出 K²=χσ、Mδ=1.3χ̄^{1/2} 等起始分离判据（384/2025；768/1967）。但 15°–18° 的起始分离角在部分实验中与 Re 无关（776/1976；1462/1975），冷壁实验却使 Chapman 标度失效（1204/1968）、分离长度强烈依赖 Mach 数（1056/1967）。二维定常、非定常与三维分离仍没有唯一可计算的分离点/线定义。", False),
        ("分离长度标度：二维可折叠，冷壁、高焓与三维仍需修正",
         "质量守恒型长度 L*、激波强度 S* 与相似参数 K、χ̄ 已把压缩拐角、入射激波和部分湍流数据折叠到近线性关系（461/2013；1480/2024；1039/2026，后者多数误差 <15%）。但标度对 Re、Mach、壁温与钝化半径的依赖仍有不同写法（742/2020；462/2015；477/1989；1200/2014），冷壁会改变自由干扰常数（1204/1968），高焓与三维构型尚未统一。", False),
        ("低频非定常：现象学共识，因果链仍有竞争解释",
         "分离激波的低频运动、剪切层大尺度结构与再附区脉动在实验和 DNS 中反复出现（452/2015；721/2017；880/2022；1009/2025），全局稳定性分析还能给出临界激波角与低频增益（793/2023；2007/2022）。但“上游边界层强迫”“下游分离泡收缩/膨胀”“全局模态”三类机制仍未被唯一判别，三维干扰中低频呼吸甚至可能被抑制而以斜剪切层对流不稳定为主（490/2023）。", True),
        ("湍流建模：平均压力可用，热流与分离尺度仍不可靠",
         "SST 等模型改善了逆压梯度分离（1350/1994），RANS 对二维典型干扰的时均压力骨架仍具工程价值（2025/2026）。但起始分离角随 Re 不变（776/1976；1462/1975）与压升随 M、Re 变化（1458/1959）并不构成同一套普适规律；分离区热流、压力脉动与三维角区分离对涡黏和激波-湍流相互作用高度敏感（878/2021；2024/2019；2028/2024）。", False),
        ("峰值热流：斜驻点机制前进，催化与稀薄耦合仍是主误差",
         "斜驻点-三层模型与剪切层压缩/耗散分析已把再附峰值热流与分离泡几何、来流条件联系起来（380/2021；499/2020；915/2012），但催化壁可使峰值再增约 30%（934/2026），局部催化/粗糙度甚至可超过完全催化驻点值（382/2023），振动激发与传感器材料又能造成 18% 与 62% 量级的偏差（387/2020）。峰值位置与量级仍缺少同时包含催化、稀薄、振动非平衡与三维效应的高频数据。", True),
        ("壁温效应：方向一致，定量标度分歧明显",
         "热壁增大、冷壁缩小层流分离泡的方向在实验、DNS 与 RANS 中一致（1112/2006；1204/1968；1324/2017；2023/2021），并存在临界壁温与 L/δ∝(Tw/Tr)^0.85 等半理论关系（1210/1990；1324/2017）。但经典关联式的壁温/总温缩放存在系统性缺陷（1110/2014），高焓条件下分离缩小而峰值热流仍可被低估（744/2013），后掠干扰中冷却还会差异化影响主/二次分离（2036/2026）。", False),
        ("动壁效应：上下游行壁不是对称问题",
         "顺流运动的壁面缩短分离、逆流运动拉长分离，这一点在 M=2.3–3 的运动平板计算中一致（803/2020；809/2021），并可用移动激波坐标系与真实 Ms 重写标度（742/2020）。但上、下游运动壁的 MRS 判据并不普遍成立：下游壁可出现边缘分离与代数奇异（1064/1996），上游壁的分离可呈楔形、由膨胀扇而非激波诱发（1086/2012；1091/2020），临界状态还出现 α=1/5、β=-3/10 的新标度（1094/2025）。", True),
        ("三维、后掠与锥形：准锥形框架有效，近场与对称面失效",
         "后掠压缩拐角、后掠入射激波与鳍片干扰在准锥形坐标下表现出相似性，角区压力波、主/二次分离与 λ 激波构成共同拓扑（2027/2023；490/2023；2033/2021；2037/2025）。但锥形渐近在激波发生器近区与对称面失效，三维分离缺少类似二维的统一长度尺度；后掠角还可能扩大分离并激发新的中频展向行波（2035/2026），高焓真实气体下的三维数据尤其稀缺（2028/2024）。", True),
        ("流动控制：局部收益明确，宽域适应与耐久性未验证",
         "鼓包、后掠唇罩、抽吸-扰流片、振荡涡流发生器、微射流与凹面都能在特定工况显著缩短分离或降低热流（989/2023；997/2023；993/2023；991/2023；992/2024；1120/2025），部分方案报告 25%–80% 的分离区缩减。但收益高度依赖来流角、后掠与干扰强度，阻力代价、宽速域控制律、作动器耐久性和全尺寸验证仍普遍缺失（990/2025；2027/2023）。", True),
        ("地面试验与验证：设施不能同时复现，天地换算仍是瓶颈",
         "脉冲设施中压力与热流的建立时间分别可达 0.2 ms 与 2.1 ms，数值仍可能低估约 2 倍，现有标度并非普适（451/2017）；高焓设施难以同时复现 Mach 数、Re 数与真实气体化学（835/2006；1460/1986；834/2019）。HIFiRE 等飞行试验提供了关键锚点（839/2015），但高频传热、三维角区、高焓化学非平衡与飞行条件下的同步数据仍然稀缺（2016/2024；2028/2024）。", True),
    ]
    syn = "".join(
        f'<div class="syn-item{" gap" if gap else ""}"><h3>{e(t)}</h3><p>{e(d)}</p></div>'
        for t, d, gap in synthesis
    )

    body = f'''<main id="main">
<section class="review-hero"><div class="wrap">
  <div class="eyebrow">Reviews · Status &amp; Gaps</div>
  <h1>综述与研究空白</h1>
  <p class="lede">逐篇综述卡片按出版年份从新到旧排列；先给出跨文献的综合判断，再展开各篇如何划分问题、已经形成哪些共识、哪些结论仍然互相矛盾。一般分离流动综述（如《分离流动的某些进展》）不属于本专题，未纳入本页。</p>
</div></section>

<section class="wrap panel synthesis reveal">
  <div class="panel-head"><h2>跨文献综合判断</h2><span class="muted small">通读全库 {len(papers)} 条记录（含 {len(reviews)} 篇综述）归纳；括号内为条目号/年份</span></div>
  <div class="syn-grid">{syn}</div>
</section>

<section class="wrap" style="margin-top:20px;margin-bottom:44px">
  <div class="panel-head" style="margin:26px 0 14px"><h2>逐篇综述卡片</h2><span class="muted small">{len(reviews)} 篇</span></div>
  <div class="review-grid">{''.join(cards) or '<p class="muted">暂无综述条目。</p>'}</div>
</section>
</main>'''
    return page_shell("综述与研究空白 · SWBLI", body, "", "reviews")


def render_taxonomy(meta, papers):
    tags = meta["tags"]
    tagcloud = "".join(
        f'<a href="library.html?tag={e(t)}">{e(t)}<span class="tc">{meta["tagCounts"].get(t, 0)}</span></a>'
        for t in tags
    )
    journalcloud = "".join(
        f'<a href="library.html?journal={urlquote(j, safe="")}">{e(j)}<span class="tc">{meta["journalCounts"].get(j, 0)}</span></a>'
        for j in meta["journals"]
    )
    focuscloud = "".join(
        f'<a href="library.html?focus={urlquote(f, safe="")}">{e(f)}<span class="tc">{meta["focusCounts"].get(f, 0)}</span></a>'
        for f in meta["focus"]
    )
    focus_rows = "".join(
        f'<li><b>{e(f)}</b><span>{e(d)}（{meta["focusCounts"].get(f, 0)} 篇）</span></li>'
        for f, d in [
            ("马赫数效应", "覆盖多个 Mach 值或较宽范围，并在正文明确讨论 Mach 对分离、热流、稳定性或尺度的影响/趋势"),
            ("雷诺数效应", "覆盖多个 Re 或较宽范围，并明确讨论 Re 的影响或“弱依赖/无关”结论；仅用 Re 做无量纲化不算"),
            ("壁温效应", "比较至少两个壁温条件（或系统综述），讨论壁温、冷却或加热对分离、热流或稳定性的影响"),
            ("轴对称效应", "讨论轴对称性/轴对称构型本身对干扰结构、分离与传热的影响，而非仅几何为回转体"),
            ("三维效应", "把三维性、后掠、有限宽、展向压力梯度或三维分离拓扑作为研究重点，而非仅用三维网格"),
            ("湍流效应", "以湍流物理、湍流模型、激波—湍流相互作用或层流—湍流对比为核心，而非仅工况为湍流"),
            ("动壁效应", "以运动壁面/运动平板本身为自变量，讨论上下游行壁对分离、剪切或稳定性的影响"),
            ("非定常效应", "以非定常性、自持振荡、全局稳定性或运动激波/俯仰等为核心，而非仅求解器可算非定常"),
        ]
    )
    board_rows = "".join(
        f'<li><b>{e(b)}</b><span>{e(desc)}（{meta["boardCounts"].get(b, 0)} 篇）</span></li>'
        for b, desc in [
            ("流动分离", "分离判据、分离泡尺度、三层结构、非定常分离与流动控制"),
            ("初始分离", "分离起始条件、初始分离尺度、分离判据与起始点预测；可与流动分离板块叠加"),
            ("峰值传热", "再附峰值热流、斜驻点模型、真实气体效应、热防护与实验测量"),
            ("基础与工具", "教材、计算工具、纯无粘激波背景，以及无法归入单一板块的交叉文献"),
        ]
    )
    regime_rows = "".join(
        f'<li><b>{e(r)}</b><span>{e(d)}（{meta["regimeCounts"].get(r, 0)} 篇）</span></li>'
        for r, d in [
            ("层流", "以理论建模、渐近展开、稳定性分析与经典实验为主"),
            ("转捩", "关注扰动增长、转捩位置、分离泡非定常与转捩控制"),
            ("湍流", "关注分离长度、压力平台、壁面热流与湍流模型"),
            ("无粘", "无粘激波反射/干扰、自由干扰与无粘稳定性判据"),
            ("非定常", "关注分离泡振荡、低频非定常、运动激波/壁面与全局不稳定性；可同时带层流/转捩/湍流"),
            ("多流态", "同时讨论两种以上具体流态，或教材/综述/通用模型等不针对单一流态的工作"),
        ]
    )
    gas_rows = "".join(
        f'<li><b>{e(g)}</b><span>{e(d)}（{meta["gasCounts"].get(g, 0)} 篇）</span></li>'
        for g, d in [
            ("真实气体效应", "高温真实气体效应的总标签；含以下任一子项时自动加入"),
            ("壁面催化", "壁面催化复合对组分扩散与热流的影响"),
            ("壁面适应", "壁面能量适应系数、气-壁相互作用"),
            ("振动能激发", "振动能激发/松弛对热力学与输运的影响"),
            ("稀薄气体效应", "滑移、温度跳跃、DSMC 或非平衡边界条件"),
            ("化学非平衡", "有限速率化学反应、组分扩散与冻结/平衡极限"),
            ("振动能非平衡", "双温度模型、振动能方程与振动-平动松弛"),
        ]
    )
    method_rows = "".join(
        f'<li><b>{e(m)}</b><span>{e(d)}（{meta["methodCounts"].get(m, 0)} 篇）</span></li>'
        for m, d in [
            ("理论建模（控制方程）", "从 N-S/边界层方程、渐近展开、积分关系或守恒律出发"),
            ("理论建模（数据驱动）", "以实验/数值数据拟合、标度或机器学习为主"),
            ("稳定性分析", "LST、BiGlobal、全局/ resolvent 分析、直接模拟"),
            ("实验研究", "风洞、激波管、T4/HEG 等脉冲设备与测量技术"),
            ("数值模拟", "DNS/LES/RANS/LENS/DSMC 等"),
            ("综述", "领域进展、争议与研究空白"),
            ("教材", "气体动力学、边界层、高超声速流动基础"),
            ("计算工具", "开源求解器、物理模型库与数值框架"),
        ]
    )
    geom_rows = "".join(
        f'<li><b>{e(g)}</b><span>{e(d)}（{meta["geometryCounts"].get(g, 0)} 篇）</span></li>'
        for g, d in [
            ("压缩拐角", "二维/准二维压缩拐角、后掠压缩面与拐角曲率变化"),
            ("平板", "平板边界层、运动平板与平板入射激波的基础构型"),
            ("平板入射激波", "斜激波入射平板边界层，含运动平板入射激波"),
            ("双楔", "双楔/双尖楔构型，含激波-激波干扰与分离"),
            ("双锥", "双锥/锥-裙构型"),
            ("轴对称", "圆锥、锥-台阶等回转体或轴对称流动"),
            ("多构型", "教材、综述或对比研究，覆盖两种以上构型"),
            ("纯方程", "无特定几何构型的纯理论、方程推导或零维模型"),
            ("其他", "确有特定构型但不在上述类别中，如鳍、唇罩、交叉激波等"),
        ]
    )
    article_type_rows = "".join(
        f'<li><b>{e(t)}</b><span>{e(d)}（{meta["articleTypeCounts"].get(t, 0)} 篇）</span></li>'
        for t, d in [
            ("教材", "教科书、专著或教材章节；含 Zotero 中“空气动力学教材”集合的图书"),
            ("会议", "会议论文或会议论文集中的章节"),
            ("期刊", "正式发表的期刊论文"),
            ("报告", "NASA、NACA、AGARD、AIAA、大学或实验室等技术报告、备忘录与研究简报；不再按发布机构细分，NASA 报告可在“期刊目录”中用专门标签筛选"),
            ("综述", "面向 SWBLI 或相关高温气动问题的综述；一般分离流动综述不纳入"),
            ("学位论文", "博士/硕士学位论文"),
            ("预印本", "arXiv 等尚未正式发表、但具有较高参考价值的新近工作"),
        ]
    )
    era_rows = "".join(
        f'<li><b>{e(era)}</b><span>{e(d)}（{meta["eraCounts"].get(era, 0)} 篇）</span></li>'
        for era, d in [
            ("2000~至今", "2000 年及以后发表的期刊论文、会议论文、教材与专著；2000 年归入本类"),
            ("1900~2000", "1900–1999 年发表的文献；经典论文、早期报告与旧版专著"),
        ]
    )
    era_unknown_note = (
        f'<p class="muted small">另有 {meta["eraUnknown"]} 条年代未标注，不进入两个年代桶。</p>'
        if meta.get("eraUnknown") else ""
    )
    evidence_rows = "".join(
        f'<tr><td>{e(k)}</td><td class="num">{v}</td><td>{e(d)}</td></tr>'
        for k, v, d in [
            ("摘要+笔记", meta["evidenceCounts"].get("摘要+笔记", 0), "摘要与 Zotero 笔记互相印证"),
            ("摘要", meta["evidenceCounts"].get("摘要", 0), "仅有摘要，结论提炼相对保守"),
            ("PDF全文", meta["evidenceCounts"].get("PDF全文", 0), "依据全文或摘要/结论页"),
            ("PDF摘要/结论页", meta["evidenceCounts"].get("PDF摘要/结论页", 0), "依据抽取的 PDF 片段"),
            ("仅题录", meta["evidenceCounts"].get("仅题录", 0), "仅有题名/出处，内容为谨慎推断"),
        ]
    )
    cite_rows = "".join(
        f'<tr><td>{e(CITE_LABELS[k])}</td><td>{e(desc)}</td></tr>'
        for k, desc in [
            ("jfm", "作者—年份制，& 连接作者，出处保留卷(期)、页码"),
            ("pof", "AIP 风格，作者、引号标题、年份与 DOI"),
            ("cja", "Elsevier 作者—年份制，卷(期): 页码"),
            ("ast", "Elsevier 作者—年份制，卷(期): 页码"),
            ("aiaa", "AIAA 风格，Vol./No./pp. 与引号标题"),
            ("prf", "APS 风格，卷、页码与年份"),
            ("aia", "Springer 风格，卷、页码与年份"),
            ("shock", "Springer 风格，卷、页码与年份"),
            ("ams", "Springer 风格，卷、页码与年份"),
            ("lxxb", "中文 GB/T 7714 风格：期刊用 [J] 与卷(期): 页码，图书用 [M] 与版次/出版地: 出版社"),
            ("qtl", "中文 GB/T 7714 风格：期刊用 [J] 与卷(期): 页码，图书用 [M] 与版次/出版地: 出版社"),
            ("taml", "Elsevier 作者—年份制，卷(期): 页码"),
            ("zh_en", "英文期刊引用中文文献：作者—年份制，保留中文题名与出处，末尾加 (in Chinese)"),
            ("bibtex", "可直接粘贴到 LaTeX/BibTeX"),
        ]
    )

    body = f'''<main id="main">
<section class="tax-hero"><div class="wrap">
  <div class="eyebrow">Taxonomy · Method · Evidence</div>
  <h1>分类体系与检索口径</h1>
  <p class="lede">这套分类不是简单的主题词表，而是围绕两个问题组织：<b>是否发生分离、从何时开始分离</b>、<b>壁面承受多大热流</b>。流态、真实气体效应、建模方式、构型、关注点与年代是六个检索切面；标签用于跨切面检索。</p>
</div></section>

<section class="wrap tax-grid">
  <div>
    <div class="panel tax-block"><h2>板块</h2><ul class="tax-list">{board_rows}</ul></div>
    <div class="panel tax-block"><h2>三种流态</h2><ul class="tax-list">{regime_rows}</ul></div>
    <div class="panel tax-block"><h2>真实气体效应</h2><ul class="tax-list">{gas_rows}</ul></div>
    <div class="panel tax-block"><h2>关注点标签</h2><p class="muted small">用于筛选“这篇文献重点研究哪一种效应”，与流态、构型等对象标签不同；一篇文献可同时关注多种效应。判定要求：文献覆盖较宽的马赫数、雷诺数、壁温等参数范围，并在正文中明确讨论该参数对分离、热流或稳定性的影响；只在算例表中列一个固定值的不计入。</p><div class="tagcloud">{focuscloud}</div><ul class="tax-list" style="margin-top:10px">{focus_rows}</ul></div>
    <div class="panel tax-block"><h2>期刊目录</h2><p class="muted small">只给流体力学与航空航天经典/核心期刊单独设短标签，如 JFM、POF、AIAA J；其余期刊统一归入“其他”。AIAA 会议论文与 NASA 报告分别用“AIAA Paper”“NASA报告”标出；教材、学位论文、其他会议论文、其他报告与预印本归入“非期刊”。“课题组文章”是叠加在目录上的快捷标签，可与任一目录标签同时使用，因此计数会重叠。</p><details class="tax-collapse"><summary>展开 {len(meta["journals"])} 个目录标签</summary><div class="tagcloud">{journalcloud}</div></details></div>
    <div class="panel tax-block"><h2>建模与研究方法</h2><ul class="tax-list">{method_rows}</ul></div>
  </div>
  <div>
    <div class="panel tax-block"><h2>构型</h2><p class="muted small">“平板”是基础构型；平板入射激波类文献同时带有“平板”与“平板入射激波”两个构型。</p><ul class="tax-list">{geom_rows}</ul></div>
    <div class="panel tax-block"><h2>文章类型</h2><p class="muted small">由 Zotero 类型与综述标记派生；综述同时保留其发表载体类型，因此各类型篇数之和可大于总数。</p><ul class="tax-list">{article_type_rows}</ul></div>
    <div class="panel tax-block"><h2>年代</h2><p class="muted small">按出版年份二分，2000 年归入“2000~至今”。年代只作检索切面，不改写文献的类型或流态。</p><ul class="tax-list">{era_rows}</ul>{era_unknown_note}</div>
    <div class="panel tax-block"><h2>受控标签</h2><p>点击标签直接进入文献库筛选。标签按在精选库中的出现次数排序，括号内为篇数；“课题组文章”按作者名自动派生。</p><div class="tagcloud">{tagcloud}</div></div>
    <div class="panel tax-block"><h2>证据等级</h2><p>每篇详情页标注内容依据，避免把推断写成原文结论。</p><div class="table-wrap"><table class="data"><thead><tr><th>等级</th><th>篇数</th><th>说明</th></tr></thead><tbody>{evidence_rows}</tbody></table></div></div>
  </div>
</section>

<section class="wrap grid-2" style="margin-top:20px;margin-bottom:44px">
  <div class="panel"><div class="panel-head"><h2>12 种引用风格 + BibTeX + 中文 in Chinese</h2></div>
    <p class="muted small">每篇文献的引用下拉均提供 12 种引用风格与 BibTeX；中文文献另提供英文期刊引用格式，末尾为 <b>(in Chinese)</b>。图书自动改用“版次 + 出版社 + 出版地”的格式，不再套用期刊卷期。风格只改变排版，<b>文献出处保留原刊名/原出版社</b>，不会把一篇 JFM 论文写成 AIAA Journal。</p>
    <div class="table-wrap"><table class="data"><thead><tr><th>风格</th><th>要点</th></tr></thead><tbody>{cite_rows}</tbody></table></div>
  </div>
  <div class="panel"><div class="panel-head"><h2>数据来源与边界</h2></div>
    <p>文献元数据来自本地 Zotero 库（去重后精选）。摘要优先使用 Zotero 摘要；缺失时从本地 PDF 抽取摘要/结论页。中文摘要为翻译或节译，主要工作与结论为依据原文的结构化提炼。</p>
    <p>详情页按 IMRaD 结构组织：阅读说明 → 一句话/三句话 → 核心内容清单 → 引言 → 条件与参数 → 方法 → 核心推导 → 结果与证据 → 机制 → 讨论/局限 → 工程意义 → 核心图件 → 可引用素材 → 核验。公式以 LaTeX 源码保存，页面用本地打包的 KaTeX 渲染（离线，无 CDN）；核心图件由 PDF 按图注位置裁取并回链原页。</p>
    <p>已排除 HCW、燃烧、纯爆轰噪声及与 SWBLI 无关的传热/制动/鳍片文献。教材、软件文档与纯无粘激波背景保留在“基础与工具”，用于支撑主板块。</p>
    <p>被引数优先来自 OpenAlex（DOI 批量匹配；无 DOI 时按题名 + 年份严格匹配），参考文献数优先来自 Crossref（DOI 匹配，通常更完整），两者都列出以便核对，结果缓存在 <span class="kbd">build/citation_metrics.json</span>。不同平台收录范围与计数口径不同，未匹配文献不补零；卡片上的“高被引”只是 ≥{HIGH_CITED_MIN} 次的浏览阈值，不是学科评价。</p>
    <p class="muted small">日常修改内容后运行 <span class="kbd">python build/build_site.py</span> 即可；更新被引数据时运行 <span class="kbd">python build/fetch_citations.py</span> 后再构建；只有重新抓取 Zotero 元数据时，才先运行 <span class="kbd">python build/prepare_selected.py</span>。</p>
  </div>
</section>
</main>'''
    return page_shell("分类体系与检索口径 · SWBLI", body, "", "taxonomy")


def formula_math_html(p):
    """Render the formula block, preferring build-time LaTeX -> MathML."""
    f = p["formula"]
    idea = f'<p class="fidea">{e(f["idea"])}</p>' if f.get("idea") else ""
    lines = [clean_str(x) for x in as_list(f.get("latex")) if clean_str(x)]
    if not lines:
        return (
            f'<div class="formula-box"><div class="fname">{e(f["name"])}</div>\n'
            f'          <div class="fexpr">{e(f["expr"])}</div>\n'
            f'          {idea}</div>'
        )

    blocks = []
    for line in lines:
        if latex_to_mathml is None:
            break
        try:
            blocks.append(f'<div class="fmath-line">{latex_to_mathml(line, display="block")}</div>')
        except Exception:
            blocks.append(f'<div class="fmath-line fexpr">{e(line)}</div>')
    if not blocks:
        blocks.append(f'<div class="fmath-line fexpr">{e(f["expr"])}</div>')

    source = "\n".join(lines)
    return (
        f'<div class="formula-box"><div class="fname">{e(f["name"])}</div>\n'
        f'          <div class="fmath">{"".join(blocks)}</div>\n'
        f'          <details class="fsrc"><summary>LaTeX 源码</summary><pre>{e(source)}</pre></details>\n'
        f'          {idea}</div>'
    )


ATTR_CLASS = {"原文明确": "ok", "AI概括": "mid", "AI推断": "warn"}


def attr_badge(value):
    value = clean_str(value)
    if not value:
        return ""
    return f'<span class="attr {ATTR_CLASS.get(value, "")}">{e(value)}</span>'


def data_table(headers, rows, cls="data deep-table"):
    if not rows:
        return '<p class="muted">文中未提及。</p>'
    head = "".join(f"<th>{e(h)}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>" for row in rows)
    return (f'<div class="table-wrap"><table class="{cls}"><thead><tr>{head}</tr></thead>'
            f'<tbody>{body}</tbody></table></div>')


def latex_lines(items):
    out = []
    for tex in items or []:
        tex = str(tex).strip().strip("$")
        if tex:
            out.append(f'<div class="math-block">\\[{e(tex)}\\]</div>')
    return "".join(out)


def deep_derivation_html(der):
    der = der or {}
    idea = f'<p class="derive-idea">{e(der.get("idea"))}</p>' if clean_str(der.get("idea")) else ""
    assumptions = [clean_str(x) for x in as_list(der.get("assumptions")) if clean_str(x)]
    asm = ""
    if assumptions:
        asm = '<div class="deep-sub"><h3>关键假设</h3><ul class="tight-list">' + "".join(
            f"<li>{e(x)}</li>" for x in assumptions) + "</ul></div>"
    steps = []
    for i, st in enumerate(as_list(der.get("steps")), 1):
        if not isinstance(st, dict):
            continue
        src = f'<div class="src-line">依据：{e(st.get("source"))}</div>' if clean_str(st.get("source")) else ""
        steps.append(
            f'<div class="derive-step"><div class="ds-head"><span class="ds-no">{i}</span>{e(st.get("title"))}</div>'
            f'<p>{e(st.get("text"))}</p>{latex_lines(st.get("latex"))}{src}</div>'
        )
    steps_html = ('<div class="deep-sub"><h3>推导过程</h3>' + "".join(steps) + "</div>") if steps else ""
    result = f'<div class="deep-result"><strong>推导结果：</strong>{e(der.get("result"))}</div>' if clean_str(der.get("result")) else ""
    limits = f'<p class="muted small"><strong>适用边界：</strong>{e(der.get("limits"))}</p>' if clean_str(der.get("limits")) else ""
    if not der.get("exists"):
        note = '<p class="muted">原文未给出从守恒律出发的完整解析推导；以下仅列出材料中可核对的定义或建模链，不补写教科书推导。</p>'
        return f'<div class="derivation-block">{note}{idea}{asm}{steps_html}{result}{limits}</div>'
    return f'<div class="derivation-block">{idea}{asm}{steps_html}{result}{limits}</div>'


def deep_figures_html(pid, figures):
    cards = []
    for f in figures or []:
        fn = clean_str(f.get("file"))
        if not fn:
            continue
        cap = clean_str(f.get("caption_zh")) or clean_str(f.get("caption_orig"))
        orig = clean_str(f.get("caption_orig"))
        orig_html = f'<div class="fg-orig">{e(orig)}</div>' if orig and orig != cap else ""
        cards.append(
            f'<figure class="deep-fig"><a href="../assets/figs/{pid}/{e(fn)}" target="_blank" rel="noopener">'
            f'<img loading="lazy" src="../assets/figs/{pid}/{e(fn)}" alt="{e(cap)}"></a>'
            f'<figcaption><div class="fg-title">图 {e(f.get("n"))} · 第 {e(f.get("page"))} 页</div>'
            f'<div class="fg-cap">{e(cap)}</div>{orig_html}'
            f'<div class="fg-why">支持的结论：{e(f.get("why"))}</div></figcaption></figure>'
        )
    return f'<div class="deep-figs">{"".join(cards)}</div>' if cards else '<p class="muted">未抓取到可用图件。</p>'


def deep_sections(p):
    d = p.get("deep") or {}
    if not d:
        return None
    im = d.get("imrad") or {}
    secs = []

    read_bits = [clean_str(d.get("read_note"))]
    if p.get("article_types"):
        read_bits.append("文章类型：" + "、".join(p["article_types"]))
    secs.append(("阅读说明", paras(" ".join(x for x in read_bits if x))))

    three = "".join(
        f'<li>{e(x.get("text"))} {attr_badge(x.get("attr"))}</li>'
        for x in as_list(d.get("three_sentence")) if isinstance(x, dict)
    )
    secs.append((
        "一句话核心与三句话摘要",
        f'<p class="one-line">{e(d.get("one_line"))}</p><ol class="three-sentence">{three}</ol>',
    ))

    core = [
        [e(c.get("point")), e(c.get("type")), f'<span class="grade g{e(c.get("grade"))}">{e(c.get("grade"))}</span>',
         e(c.get("source")), attr_badge(c.get("attr"))]
        for c in as_list(d.get("core_points")) if isinstance(c, dict)
    ]
    secs.append(("核心内容清单", data_table(["要点", "类型", "重要性", "原文依据", "属性"], core)))

    secs.append(("引言：研究问题与领域缺口", paras(im.get("introduction"))))

    rows = [[e(c.get("item")), e(c.get("value")), e(c.get("source")), e(c.get("note"))]
            for c in as_list(d.get("conditions")) if isinstance(c, dict)]
    secs.append(("流动条件与几何构型", data_table(["项目", "数值/描述", "依据", "备注"], rows)))

    rows = [[e(c.get("name")), e(c.get("definition")), e(c.get("value")), e(c.get("relation")), e(c.get("source"))]
            for c in as_list(d.get("key_parameters")) if isinstance(c, dict)]
    secs.append(("核心现象与关键参数", data_table(["参数", "定义", "数值", "关系/说明", "依据"], rows)))

    rows = [[e(c.get("item")), e(c.get("value")), e(c.get("source")), e(c.get("note"))]
            for c in as_list(d.get("methods")) if isinstance(c, dict)]
    secs.append(("方法与数据", paras(im.get("methods")) + data_table(["项目", "内容", "依据", "备注"], rows)))

    secs.append(("核心推导与公式", deep_derivation_html(d.get("derivation"))))

    findings = [
        [e(c.get("finding")), e(c.get("evidence")), e(c.get("type")), e(c.get("strength")),
         e(c.get("source")), attr_badge(c.get("attr"))]
        for c in as_list(d.get("findings")) if isinstance(c, dict)
    ]
    secs.append(("结果：主要发现与关键证据",
                 paras(im.get("results")) + data_table(["发现", "证据", "证据类型", "强度", "位置", "属性"], findings)))
    secs.append(("机制解释与论证链", paras(d.get("mechanism"))))

    contrib = "".join(f"<li>{e(x)}</li>" for x in as_list(d.get("contributions")) if clean_str(x))
    disc = paras(im.get("discussion"))
    disc += f'<div class="deep-sub"><h3>作者结论</h3>{paras(d.get("conclusions"))}</div>'
    if contrib:
        disc += f'<div class="deep-sub"><h3>主要贡献</h3><ul class="tight-list">{contrib}</ul></div>'
    disc += f'<div class="deep-sub"><h3>局限与未解决问题</h3>{paras(d.get("limits"))}</div>'
    secs.append(("讨论：结论、贡献与局限", disc))

    secs.append(("对高速流动与工程的意义", paras(d.get("significance"))))
    secs.append(("核心图件", deep_figures_html(p["id"], d.get("figures"))))

    quotes = [
        [f'“{e(q.get("text"))}”', e(q.get("supports")), e(q.get("source")), e(q.get("use"))]
        for q in as_list(d.get("quotes")) if isinstance(q, dict)
    ]
    secs.append(("可引用原文素材", data_table(["原文短句", "可支持的观点", "位置", "使用建议"], quotes)))

    ver = d.get("verification") or {}
    ver_rows = [
        ["仅基于全文", e(ver.get("text_only"))],
        ["A 级要点有依据", e(ver.get("a_grade_supported"))],
        ["属性标注", e(ver.get("attributes_marked"))],
        ["覆盖范围", e(ver.get("coverage"))],
        ["无编造", e(ver.get("no_fabrication"))],
    ]
    oq = "".join(f"<li>{e(x)}</li>" for x in as_list(ver.get("open_questions")) if clean_str(x))
    oq_html = f'<div class="deep-sub"><h3>需回原文确认</h3><ul class="tight-list">{oq}</ul></div>' if oq else ""
    secs.append(("最终核验", data_table(["核验项", "结论"], ver_rows) + oq_html))
    return secs


def render_paper(p, prev, nxt):
    board_badges = "".join(board_badge(b) for b in p["board"])
    gas = "、".join(p["real_gas"]) if p["real_gas"] else "未考虑 / 不适用"
    methods = "、".join(p["methods"])
    geoms = "、".join(p["geometry"])
    formula = ""
    if p["formula"]:
        formula = formula_math_html(p)
    review = ""
    if p["review"]:
        secs = "".join(
            f'<div class="review-part"><h4>{e(s["name"] or "专题")}</h4><p>{e(s["summary"])}</p></div>'
            for s in (p["review"].get("sections") or [])
        )
        review = f'''<div class="review-block">{secs}
          {f'<div class="review-part"><h4>发展现状</h4><p>{e(p["review"].get("status"))}</p></div>' if p["review"].get("status") else ""}
          {f'<div class="review-part review-gaps"><h4>研究空白</h4><p>{e(p["review"].get("gaps"))}</p></div>' if p["review"].get("gaps") else ""}
          </div>'''
    related = "".join(
        f'''<div class="related-card"><div class="rc-meta">{e(by_id[rid]["year"])} · {e(by_id[rid]["venue"])}</div>
        <a href="{e(detail_href(by_id[rid], nested=True))}">{e(by_id[rid]["title"])}</a></div>'''
        for rid in p["related"] if rid in by_id
    )
    notes = ""
    if p.get("notes"):
        note_html = "".join(f"<p>{e(n[:900])}{'…' if len(n) > 900 else ''}</p>" for n in p["notes"][:3])
        notes = f'<details class="orig-abstract"><summary>Zotero 笔记摘录</summary>{note_html}</details>'
    orig = ""
    if p.get("abstract_orig"):
        orig = f'<details class="orig-abstract"><summary>原始摘要（英文/原文）</summary><p>{e(p["abstract_orig"])}</p></details>'
    doi = f'<a href="https://doi.org/{e(p["doi"])}" target="_blank" rel="noopener">DOI ↗</a>' if p.get("doi") else ""
    pdf_action = pdf_btn(p, small=False, allow_upload=True)
    copy_path = f'<button class="btn small ghost" type="button" data-copy-path="{e(p["pdfs"][0])}">复制 PDF 路径</button>' if p.get("pdfs") else ""
    prev_link = f'<a href="{e(detail_href(prev, nested=True))}"><span class="pn-lab">上一篇</span>{e(prev["title"][:70])}</a>' if prev else "<span></span>"
    next_link = f'<a href="{e(detail_href(nxt, nested=True))}" style="text-align:right"><span class="pn-lab">下一篇</span>{e(nxt["title"][:70])}</a>' if nxt else "<span></span>"
    collections = "".join(f'<span class="tag">{e(c)}</span>' for c in p["collections"][:3])

    scope = ""
    if p.get("scope_note"):
        scope = f'<div class="scope-note">{e(p["scope_note"])}</div>'
    sections = [
        ("中文摘要", f'<div class="abstract-box">{paras(p["abstract_zh"])}</div>{scope}{orig}'),
    ]
    if p.get("background"):
        sections.append(("研究背景与问题", paras(p["background"])))
    sections.append(("本文主要工作", paras(p["main_work"])))
    if p.get("method_detail"):
        sections.append(("方法与算例细节", paras(p["method_detail"])))
    if p.get("derivation_idea") or p.get("derivation_steps"):
        steps = "".join(f"<li>{e(s)}</li>" for s in p.get("derivation_steps", []))
        steps_html = f'<ol class="derive-steps">{steps}</ol>' if steps else ""
        idea_html = f'<p class="derive-idea">{e(p["derivation_idea"])}</p>' if p.get("derivation_idea") else ""
        sections.append(("推导思路与核心思想", idea_html + steps_html))
    if p.get("findings"):
        sections.append(("关键结果与证据", paras(p["findings"])))
    if formula:
        sections.append(("关键公式与基本思想", formula))
    if p.get("problem_solved") or p.get("key_findings"):
        solved = f'<p class="solved-line"><strong>解决的问题：</strong>{e(p["problem_solved"])}</p>' if p.get("problem_solved") else ""
        kf = "".join(f"<li>{e(x)}</li>" for x in p.get("key_findings", []))
        kf_html = f'<div class="key-findings"><h3>重要发现与推断</h3><ul>{kf}</ul></div>' if kf else ""
        sections.append(("问题、发现与推断", solved + kf_html))
    sections.append(("本文结论", conclusion_html(p["conclusions"])))
    if p.get("limits"):
        sections.append(("适用边界与局限", paras(p["limits"])))
    if review:
        sections.append(("综述视角：分类、现状与空白", review))
    sections.append((
        "关联文献",
        f'<p class="muted small">依据标签、板块、构型与作者脉络自动关联，可据此追踪同一问题的前序与后续工作。</p>'
        f'<div class="related-grid">{related or "<p class=\'muted\'>暂无关联。</p>"}</div>',
    ))
    sections.append((
        "引用格式",
        f'<p class="muted small">选择期刊风格后复制；出处保留原刊名。BibTeX 可直接用于 LaTeX。</p>{citation_html(p)}',
    ))
    deep_secs = deep_sections(p)
    if deep_secs:
        # IMRaD 深度阅读记录优先；保留中文摘要、关联文献与引用格式。
        sections = [sections[0]] + deep_secs + sections[-2:]
    sections_html = "".join(
        f'<section class="content-section"><h2><span class="no">{i:02d}</span>{title}</h2>{inner}</section>'
        for i, (title, inner) in enumerate(sections, 1)
    )

    body = f'''<main id="main"><div class="wrap detail-wrap" data-pid="{p["id"]}">
  <div class="breadcrumb"><a href="../library.html">文献库</a><span>/</span><a href="../library.html?board={e(p["board"][0])}">{e(p["board"][0])}</a><span>/</span><span>{e(p["year"])}</span></div>
  <section class="detail-hero">
    <div>
      <div class="kicker">{board_badges}{journal_badge(p)}<span class="badge">{e(p["regime_display"])}</span>{''.join(f'<span class="badge blue">{e(m)}</span>' for m in p["methods"])}{citation_badge(p)}</div>
      <h1>{e(p["title"])}</h1>
      <p class="title-zh">{e(p["title_zh"])}</p>
      <div class="authors">{e(p["author_full"])}</div>
      <div class="source">{e(p["venue"])}{(" · " + e(p["year"])) if p["year"] else ""}{(", Vol. " + e(p["volume"])) if p["volume"] else ""}{("(" + e(p["issue"]) + ")") if p["issue"] else ""}{(": " + e(p["pages"])) if p["pages"] else ""}</div>
      <div class="doi">{doi}</div>
      <div class="detail-actions">{pdf_action}{copy_path}<a class="btn small" href="../library.html?tag={e(p["tags"][0]) if p["tags"] else ""}">同标签文献</a></div>
    </div>
    <aside class="side-card">
      <h4>编目信息</h4>
      <div class="fact"><span class="fk">板块</span><span class="fv">{"、".join(p["board"])}</span></div>
      <div class="fact"><span class="fk">文章类型</span><span class="fv">{e("、".join(p["article_types"]))}</span></div>
      <div class="fact"><span class="fk">期刊目录</span><span class="fv">{e("、".join(p.get("journal_tags") or []))}</span></div>
      <div class="fact"><span class="fk">年代</span><span class="fv">{e(p.get("era") or "未标注")}</span></div>
      <div class="fact"><span class="fk">流态</span><span class="fv">{e(p["regime_display"])}</span></div>
      <div class="fact"><span class="fk">方法</span><span class="fv">{e(methods)}</span></div>
      <div class="fact"><span class="fk">构型</span><span class="fv">{e(geoms)}</span></div>
      <div class="fact"><span class="fk">真实气体</span><span class="fv">{e(gas)}</span></div>
      <div class="fact"><span class="fk">关注点</span><span class="fv">{e("、".join(p.get("focus") or []) or "—")}</span></div>
      <div class="fact"><span class="fk">证据</span><span class="fv">{e(p["evidence"])} · {e(p["confidence"])}</span></div>
      <div class="pc-tags">{tags_html(p, root="../")}</div>
      <div class="evidence-note">内容依据：{e(p["evidence"])}；置信度：{e(p["confidence"])}。定量结论请以原文为准。</div>
      {citation_metrics_html(p)}
    </aside>
  </section>

  <div class="detail-body">
    <div class="detail-main">
      {sections_html}
      <section class="content-section upload-section" id="pdfUpload" data-pid="{p["id"]}" data-year="{e(p["year"]) if p["year"] and p["year"] != "—" else ""}" data-has-pdf="{1 if p.get("pdf_href") else 0}">
        <h2><span class="no">PDF</span>{'上传 PDF 并更新本页' if p.get("pdf_href") else '补充 PDF（本条目暂无本地 PDF）'}</h2>
        {'' if p.get("pdf_href") else '<p class="upload-missing-note">本条目目前没有本地 PDF。上传后只保存在本机浏览器，不会写入项目文件，也不会上传网络；刷新页面仍会保留，换浏览器或清理站点数据后会丢失。</p>'}
        <p class="muted small">本页缺少全文、摘要或图件时，可在浏览器本地补入 PDF。解析完全在本机完成，不上传网络；完成后会更新本页的 PDF 打开链接、原摘要、IMRaD 机器抽取、关键句与含图页面。复杂的公式语义与中文深度解读仍以原文和既有精读记录为准。</p>
        <div class="upload-drop" id="pdfDrop">
          <div class="upload-icon" aria-hidden="true">⇧</div>
          <div><b>拖入 PDF</b><span>或点击选择文件；建议单篇论文，≤ 80 MB</span></div>
          <label class="btn small" for="pdfFile">选择 PDF</label>
          <input id="pdfFile" type="file" accept="application/pdf,.pdf" hidden>
        </div>
        <div class="upload-status" id="pdfUploadStatus" role="status"></div>
        <div class="parsed-panel" id="pdfParsed"></div>
      </section>
      {notes}
      <div class="prevnext">{prev_link}{next_link}</div>
    </div>
    <aside class="detail-side">
      <div class="side-card">
        <h4>Zotero 分类</h4>
        <div class="pc-tags">{collections}</div>
        <div class="hr" style="margin:14px 0"></div>
        <h4>本地文件</h4>
        <p class="small muted" style="word-break:break-all" data-pdf-name>{e(p["pdf_name"]) if p["pdf_name"] else "无本地 PDF"}</p>
        {pdf_action}
      </div>
    </aside>
  </div>
</div></main>'''
    return page_shell(f"{p['title']} · SWBLI", body, "../", "library")


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

DATA_PAPERS = []
by_id = {}


def main():
    global DATA_PAPERS, by_id
    meta_list = load_json(META_PATH)
    # 外部检索补充（Crossref/OpenAlex/arXiv + 本地学位论文）与 Zotero 快照分开存放，
    # 避免重新运行 prepare_selected.py 时被覆盖。
    external_path = BASE / "external_meta.json"
    if external_path.exists():
        external = load_json(external_path)
        have = {int(m["id"]) for m in meta_list}
        added = [m for m in external if int(m["id"]) not in have]
        meta_list.extend(added)
        print(f"loaded {len(added)} external records")
    meta_by_id = {int(m["id"]): m for m in meta_list}
    citation_metrics = {}
    if CITATION_METRICS_PATH.exists():
        try:
            for key, rec in load_json(CITATION_METRICS_PATH).items():
                citation_metrics[int(key)] = rec
        except Exception as exc:
            print(f"!! cannot parse citation_metrics.json: {exc}")
        print(f"loaded citation metrics for {len(citation_metrics)} records")
    overrides_path = BASE / "meta_overrides.json"
    if overrides_path.exists():
        for key, patch in load_json(overrides_path).items():
            rec = meta_by_id.get(int(key))
            if not rec:
                print(f"!! metadata override for unknown id {key}")
                continue
            rec.update(patch)
            if "authors" in patch and "author_display" not in patch:
                rec["author_display"] = ""
        print(f"applied {len(load_json(overrides_path))} metadata overrides")
    contents = []
    for path in sorted(BASE.glob(CONTENT_GLOB)):
        if path.name in ("content_schema.json", "content_enhanced.json"):
            continue
        try:
            arr = load_json(path)
        except Exception as exc:
            print(f"!! cannot parse {path.name}: {exc}")
            continue
        if isinstance(arr, list):
            contents.extend(arr)
            print(f"loaded {len(arr):3d} from {path.name}")
    # optional expanded-content overlay; keeps the six base content files stable
    enhanced_path = BASE / "content_enhanced.json"
    if enhanced_path.exists():
        enhanced = {}
        for rec in load_json(enhanced_path):
            try:
                enhanced[int(rec["id"])] = rec
            except Exception:
                continue
        for c in contents:
            try:
                patch = enhanced.get(int(c["id"]))
            except Exception:
                patch = None
            if patch:
                c.update({k: v for k, v in patch.items() if k != "id"})
        print(f"merged {len(enhanced)} expanded content records")

    # last definition wins for duplicate ids
    c_by_id = {}
    for c in contents:
        try:
            c_by_id[int(c["id"])] = c
        except Exception:
            continue

    # 人工标注的关注点标签，集中维护，避免分散到九个内容文件。
    if FOCUS_TAGS_PATH.exists():
        focus_map = load_json(FOCUS_TAGS_PATH)
        applied = 0
        for key, values in focus_map.items():
            try:
                pid = int(key)
            except (TypeError, ValueError):
                continue
            if pid in c_by_id:
                c_by_id[pid]["focus"] = values
                applied += 1
            else:
                print(f"!! focus tag for unknown id {key}")
        print(f"applied {applied} focus tag records")

    deep_by_id = {}
    if DEEP_DIR.exists():
        for path in sorted(DEEP_DIR.glob("*.json")):
            try:
                rec = load_json(path)
                pid = int(rec.get("id", path.stem))
                deep_by_id[pid] = rec
            except Exception as exc:
                print(f"!! cannot parse deep record {path.name}: {exc}")
        print(f"loaded {len(deep_by_id)} deep-reading records")
        # Copy only the figures actually cited by a deep record into assets so
        # the generated site can be moved without the build/ directory.
        copied = 0
        for pid, rec in deep_by_id.items():
            for fig in as_list(rec.get("figures")):
                fn = clean_str(fig.get("file")) if isinstance(fig, dict) else ""
                if not fn:
                    continue
                src = FIGS_DIR / str(pid) / fn
                if not src.exists():
                    print(f"!! missing deep figure {pid}/{fn}")
                    continue
                dst_dir = ASSET_FIGS_DIR / str(pid)
                dst_dir.mkdir(parents=True, exist_ok=True)
                dst = dst_dir / fn
                if not dst.exists() or dst.stat().st_mtime < src.stat().st_mtime:
                    shutil.copy2(src, dst)
                    copied += 1
        print(f"copied {copied} deep figures into assets/figs")

    missing = [i for i in meta_by_id if i not in c_by_id]
    extra = [i for i in c_by_id if i not in meta_by_id]
    if missing:
        print(f"!! missing content for {len(missing)} ids: {missing[:30]}")
    if extra:
        print(f"!! content ids not in selection: {extra[:30]}")

    papers = []
    for pid, m in meta_by_id.items():
        c = c_by_id.get(pid, {
            "id": pid, "title_zh": m.get("title", ""), "board": ["基础与工具"],
            "regime": "多流态", "methods": ["综述"], "geometry": ["多构型"],
            "tags": ["综述"], "abstract_zh": (m.get("abstract_orig") or "")[:400],
            "main_work": "", "conclusions": "", "evidence": "仅题录", "confidence": "低",
        })
        p = norm_content(meta_by_id, c)
        p["deep"] = deep_by_id.get(pid)
        p["citations"] = cite_data(p)
        metrics = citation_metrics.get(pid)
        if metrics:
            p["cited_by"] = metrics.get("cited_by")
            p["reference_count"] = metrics.get("reference_count")
            p["reference_source"] = metrics.get("reference_source")
            p["citation_source"] = metrics.get("source")
            p["citation_source_url"] = metrics.get("source_url")
            p["citation_as_of"] = metrics.get("as_of")
            p["citation_match"] = metrics.get("match")
            p["citation_sources"] = metrics.get("sources") or []
            p["highly_cited"] = p.get("cited_by") is not None and p["cited_by"] >= HIGH_CITED_MIN
        if p["formula"] and p["id"] in FORMULA_LATEX:
            p["formula"]["latex"] = list(FORMULA_LATEX[p["id"]])
        papers.append(p)

    # manual related + automatic related
    manual = {}
    for c in contents:
        try:
            pid = int(c["id"])
            rel = [int(x) for x in as_list(c.get("related")) if str(x).isdigit()]
            if rel:
                manual[pid] = rel
        except Exception:
            continue
    compute_related(papers, manual)
    for p in papers:
        p["citation_count"] = len(p["citations"])
    no_latex = [p["id"] for p in papers if p["formula"] and not p["formula"].get("latex")]
    if no_latex:
        print(f"!! formulas without LaTeX source: {no_latex}")
    if FORMULA_LATEX and latex_to_mathml is None:
        print("!! latex2mathml is not installed; LaTeX formulas fall back to plain text")

    # sort for navigation: year ascending, then title
    papers.sort(key=lambda p: (year_int(p["year"]) or 9999, p["title"]))
    DATA_PAPERS = papers
    by_id = {p["id"]: p for p in papers}

    # metadata counts
    def count_by(key, values):
        return {v: sum(1 for p in papers if v in as_list(p.get(key)) or p.get(key) == v) for v in values}

    board_counts = {b: sum(1 for p in papers if b in p["board"]) for b in ALLOWED_BOARDS}
    def has_regime(p, r):
        if r == "多流态":
            return "多流态" in p.get("regimes", []) or len(p.get("regimes", [])) > 1
        return r in p.get("regimes", [])
    regime_counts = {r: sum(1 for p in papers if has_regime(p, r)) for r in ALLOWED_REGIMES}
    method_counts = {m: sum(1 for p in papers if m in p["methods"]) for m in ALLOWED_METHODS}
    focus_counts = {f: sum(1 for p in papers if f in p.get("focus", [])) for f in ALLOWED_FOCUS}
    geometry_counts = {g: sum(1 for p in papers if g in p["geometry"]) for g in ALLOWED_GEOMETRIES}
    gas_counts = {g: sum(1 for p in papers if g in p["real_gas"]) for g in ALLOWED_GASES}
    article_type_counts = {t: sum(1 for p in papers if t in p["article_types"]) for t in ALLOWED_ARTICLE_TYPES}
    journal_counts = {}
    for p in papers:
        for j in p.get("journal_tags", []):
            journal_counts[j] = journal_counts.get(j, 0) + 1
    journal_counts[JOURNAL_GROUP_TAG] = sum(1 for p in papers if JOURNAL_GROUP_TAG in p["tags"])
    journal_tail = [JOURNAL_OTHER_TAG, JOURNAL_AIAA_TAG, JOURNAL_NASA_TAG, JOURNAL_NON_TAG]
    journal_values = sorted(
        [j for j in journal_counts if j not in ([JOURNAL_GROUP_TAG] + journal_tail)],
        key=lambda j: (-journal_counts[j], j),
    )
    journal_values = [JOURNAL_GROUP_TAG] + journal_values + journal_tail
    era_counts = {e: sum(1 for p in papers if p.get("era") == e) for e in ALLOWED_ERAS}
    era_unknown = sum(1 for p in papers if not p.get("era"))
    tag_counts = {t: sum(1 for p in papers if t in p["tags"]) for t in TAG_ORDER}
    evidence_counts = {}
    for p in papers:
        evidence_counts[p["evidence"]] = evidence_counts.get(p["evidence"], 0) + 1
    with_citation = sum(1 for p in papers if p.get("cited_by") is not None)
    citation_dates = sorted({p.get("citation_as_of") for p in papers if p.get("citation_as_of")})
    citation_as_of = citation_dates[-1] if citation_dates else ""

    board_regime = {}
    board_tags = {}
    for b in ALLOWED_BOARDS:
        board_regime[b] = {r: sum(1 for p in papers if b in p["board"] and has_regime(p, r)) for r in ALLOWED_REGIMES}
        tc = {}
        for p in papers:
            if b in p["board"]:
                for t in p["tags"]:
                    tc[t] = tc.get(t, 0) + 1
        board_tags[b] = [t for t, _ in sorted(tc.items(), key=lambda x: (-x[1], TAG_ORDER.index(x[0])))[:5]]

    meta = {
        "title": "激波/边界层干扰文献图谱",
        "total": len(papers),
        "with_pdf": sum(1 for p in papers if p["pdf_href"]),
        "with_review": len(inscope_reviews(papers)),
        "withCitation": with_citation,
        "citationAsOf": citation_as_of,
        "highlyCitedMin": HIGH_CITED_MIN,
        "boards": ALLOWED_BOARDS,
        "articleTypes": ALLOWED_ARTICLE_TYPES,
        "journals": journal_values,
        "journalCounts": journal_counts,
        "withJournal": sum(1 for p in papers if any(j != JOURNAL_NON_TAG for j in p.get("journal_tags", []))),
        "eras": ALLOWED_ERAS,
        "regimes": ALLOWED_REGIMES,
        "methods": ALLOWED_METHODS,
        "geometries": ALLOWED_GEOMETRIES,
        "gases": ALLOWED_GASES,
        "tags": sorted(TAG_ORDER, key=lambda t: (-tag_counts.get(t, 0), TAG_ORDER.index(t))),
        "boardCounts": board_counts,
        "regimeCounts": regime_counts,
        "methodCounts": method_counts,
        "focus": ALLOWED_FOCUS,
        "focusCounts": focus_counts,
        "geometryCounts": geometry_counts,
        "gasCounts": gas_counts,
        "articleTypeCounts": article_type_counts,
        "eraCounts": era_counts,
        "eraUnknown": era_unknown,
        "tagCounts": tag_counts,
        "evidenceCounts": evidence_counts,
        "boardRegime": board_regime,
        "boardTags": board_tags,
        "generated": date.today().isoformat(),
    }

    # write data.js
    data = {"meta": meta, "papers": papers}
    js = "window.SWBLI_DATA = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n"
    js = js.replace("</", "<\\/")
    (ROOT / "assets" / "data.js").write_text(js, encoding="utf-8")

    # pages
    (ROOT / "index.html").write_text(render_index(meta, papers), encoding="utf-8")
    (ROOT / "library.html").write_text(render_library(meta, papers), encoding="utf-8")
    (ROOT / "reviews.html").write_text(render_reviews(meta, papers), encoding="utf-8")
    (ROOT / "taxonomy.html").write_text(render_taxonomy(meta, papers), encoding="utf-8")

    papers_dir = ROOT / "papers"
    papers_dir.mkdir(exist_ok=True)
    for i, p in enumerate(papers):
        prev = papers[i - 1] if i > 0 else None
        nxt = papers[i + 1] if i + 1 < len(papers) else None
        (papers_dir / f"{p['id']}.html").write_text(render_paper(p, prev, nxt), encoding="utf-8")

    print(f"wrote {len(papers)} papers, {len(papers)} detail pages")
    print("boards:", board_counts)
    print("regimes:", regime_counts)
    print("methods:", method_counts)
    print("article types:", article_type_counts)
    print("eras:", era_counts, "unknown:", era_unknown)
    print("reviews:", meta["with_review"], "pdf:", meta["with_pdf"])
    print("citation metrics:", f'{meta["withCitation"]}/{len(papers)}', "as of", meta["citationAsOf"])
    print("group papers:", tag_counts.get("课题组文章", 0))
    print("data.js:", (ROOT / "assets" / "data.js").stat().st_size, "bytes")


if __name__ == "__main__":
    main()
