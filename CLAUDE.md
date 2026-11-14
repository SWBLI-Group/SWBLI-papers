# 项目规则（Claude Code 专用入口）

> 开始任何修改前，先读 `PROJECT_MEMORY.md`、`CONTRIBUTING.md` 和 `README.md`。
> 本文件是项目级规则；如果与用户当次明确要求冲突，以用户当次要求为准，但必须先说明影响。

## 先判断任务类型

1. **新增/修改文献记录**：只改 `records/<github-handle>/<year>/<slug>.json`。
2. **修改站点/构建/标签体系**：属于维护者操作。先说明要改哪些文件、为什么、影响范围，等待明确同意后再动。
3. **只写文档/总结**：可以改 `README.md`、`PROJECT_MEMORY.md`、`CONTRIBUTING.md`，不要顺手改生成物。

## 绝对不要做

- 不要手改 `papers/*.html`、`assets/data.js`、`index.html`、`library.html`、`reviews.html`、`taxonomy.html`；它们由 `build/build_site.py` 生成。
- 不要手改 `build/build_site.py`、`assets/app.js`、`assets/style.css`、`build/formula_latex.py`、schema、全局标签词表，除非维护者明确要求。
- **新增标签/关注点、新增页面功能、修改 schema 或构建逻辑，必须先联系项目作者 @yiluntam；不得自行实现或合并。**
- 不要把 `pdfs/`、`build/figs/`、大 PDF、数据库或临时构建产物提交到 Git。
- 不要使用 sci-hub 或其他盗版源；不要绕过付费墙。
- 不要编造文献、DOI、作者、年份、摘要、数值或结论。
- 不要用内部数字 id 代替作者—年份引注。
- 不要覆盖或删除别人的 `records/` 记录；撤稿改 `status`。
- 不要在 Git 提交中添加合作者信息（如 `Co-Authored-By`）。

## 新增一条文献

1. 先用 DOI 和标题检查是否已在库中；重复则不要新增。
2. 复制 `records/_TEMPLATE.json` 到 `records/<handle>/<year>/<slug>.json`。
3. 填写题录、中文内容、`board/regimes/methods/geometry/tags/focus/evidence/confidence`。
4. 只使用受控标签；`focus` 必须有正文证据。
5. PDF 只写本地相对路径 `pdf_file`，不要把 PDF 提交到 Git。
6. `build_site.py` 会自动扫描 `records/**/*.json` 并合并；提交前运行 `python build/validate_records.py`。

## 内容质量

- `abstract_zh` 100–260 字；`main_work` 260–420 字；`conclusions` 180–300 字；`limits` 80–180 字。
- 摘要级证据不能写成全文结论；`evidence` 和 `confidence` 必须如实填写。
- 中文为主；公式用 Unicode 文本，不用 LaTeX。
- 用户可见总结用作者—年份引注，例如 `Bleilebens & Olivier（2006）`。

## 构建与检查

```bash
cd F:\文献工具
PYTHONIOENCODING=utf-8 python build/build_site.py
node --check assets/app.js
```

Windows 终端必须加 `PYTHONIOENCODING=utf-8`。构建后检查：

- `wrote N papers, N detail pages`
- `无全文PDF` 数量符合预期
- 新条目有页面，PDF 或 DOI 可点
- 没有数字文件名残留
- `git status` 没有 PDF/临时文件

## 当前项目事实

- 283 篇、203 篇有本地 PDF、80 篇 `无全文PDF`。
- 页面文件名是关键词 slug，不再是数字 id。
- `build/figs/` 已归档到项目外；构建使用 `assets/figs/`，当前缺失引用为 0。
- `assets/data.js` 仍含本机绝对路径；公开部署前必须做去本地路径构建。
- `records/` 已由 `build_site.py` 自动扫描并合并；`build/validate_records.py` 和 GitHub Actions 负责校验。
- 详细背景见 `PROJECT_MEMORY.md`。
