# 项目规则（通用 AI 入口）

> 适用于 Claude、Codex、Cursor、Copilot 等任何修改本项目的 AI 工具。
> 开始前先读 `PROJECT_MEMORY.md`、`CONTRIBUTING.md` 和 `README.md`。Claude Code 还会自动读取 `CLAUDE.md`。

## 核心规则

1. **不要手写 HTML**：`papers/*.html`、`assets/data.js`、根页面均由 `build/build_site.py` 生成。
2. **不要改底层**：`build/build_site.py`、`assets/app.js`、`assets/style.css`、`build/formula_latex.py`、schema、全局标签词表、目录结构由维护者统一管理；需要修改先说明并等待明确同意。**新增标签/关注点、新增页面功能、修改 schema 或构建逻辑，必须先联系项目作者 @yiluntam。**
3. **新增文献只加一个 JSON**：`records/<github-handle>/<year>/<slug>.json`。一条文献一个文件，不要编辑别人的记录。
4. **PDF 不进 Git**：`pdfs/` 已被忽略；只使用合法开放获取、Zotero 群组库、课题组网盘或用户提供的 PDF。禁止 sci-hub 和绕过付费墙。
5. **不编造**：文献、DOI、作者、年份、摘要、数值、公式和结论必须有题录/摘要/PDF 依据；`evidence` 与 `confidence` 如实填写。
6. **用作者—年份引注**：不要用内部数字 id 代替；中文为主，公式用 Unicode 文本。
7. **提交前检查**：不提交 PDF、`build/figs/`、数据库、临时文件；Git 提交不要添加合作者信息。

## 新增记录流程

```text
复制 records/_TEMPLATE.json
→ records/<handle>/<year>/<slug>.json
→ 填写题录 + content + board/regimes/methods/geometry/tags/focus
→ 检查 DOI/标题不重复
→ 提交 PR
```

`build_site.py` 会自动扫描 `records/**/*.json` 并合并；提交前运行 `python build/validate_records.py`。

## 构建

```bash
cd F:\文献工具
PYTHONIOENCODING=utf-8 python build/build_site.py
node --check assets/app.js
```

Windows 终端必须带 `PYTHONIOENCODING=utf-8`。

## 当前事实

- 283 篇、203 篇有本地 PDF、80 篇 `无全文PDF`。
- 文件名是“作者-年份-期刊-标题”关键词 slug，不是数字 id。
- `build/figs/` 已归档；`assets/figs/` 是运行所需图件，当前缺失引用 0。
- `assets/data.js` 仍含本机绝对路径，公开部署前必须去本地路径。
- 详细架构、主题入口和已知问题见 `PROJECT_MEMORY.md`。
