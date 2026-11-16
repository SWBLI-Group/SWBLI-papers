# 项目规则（通用 AI 入口）

> 适用于 Claude、Codex、Cursor、Copilot 等 AI 工具。
> 开始前读 `PROJECT_MEMORY.md`、`CONTRIBUTING.md` 和 `README.md`。Claude Code 还会自动读取 `CLAUDE.md`。
> 当前开发分支：`new`；PR 提到 `new`，不直接合并 `main`。

## 修改边界

只改：

```text
papers/<slug>.html
assets/data.js
assets/figs/（仅新增图件时）
pdfs/（本地，不进入 Git）
```

禁止改：

```text
build/
```

`build/` 是底层与历史构建源。普通 PR 改 `build/` 会被 `.github/workflows/guard-build.yml` 拒绝；确需修改先联系作者 @yiluntam，由作者加 `allow-build-change` 标签。

`assets/app.js`、`assets/style.css`、`assets/katex/`、`assets/pdfjs/` 不是日常条目修改所需；要改必须说明原因并由作者审核。

## 条目规则

新增/修改一条文献必须同时改：

1. `papers/<slug>.html`：正文、题录、标签、DOI、PDF 按钮；
2. `assets/data.js`：同一 `id` 的索引对象；
3. `meta` 计数（`total`、`with_pdf`、`tagCounts`、`focusCounts` 等）。

只改页面、不改 `assets/data.js`，条目不会出现在文献库、搜索和筛选中。

## 内容与 PDF

- 不编造文献、DOI、摘要、数值或结论；
- 中文为主；公式用 Unicode 文本；
- 用户可见总结用作者—年份引注；
- PDF 放本地 `pdfs/` 或网盘，不进入 Git；
- 只使用合法来源，不使用 sci-hub 或绕过付费墙；
- 新增标签/关注点、页面功能或底层改动必须先联系 @yiluntam。

## 检查

```bash
node --check assets/data.js
node --check assets/app.js
```

不要运行 `build_site.py`；它会覆盖手工维护的 `papers/` 和 `assets/data.js`。

## 当前事实

- 283 篇、204 篇有本地 PDF、79 篇 `无全文PDF`。
- 文件名是“作者-年份-期刊-标题”关键词 slug。
- `build/figs/` 已归档；`assets/figs/` 是运行图件。
- `assets/data.js` 仍含本机绝对路径，公开部署前必须去本地路径。
