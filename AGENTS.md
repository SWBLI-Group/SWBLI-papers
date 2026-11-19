# 项目规则（通用 AI 入口）

> 适用于 Claude、Codex、Cursor、Copilot 等 AI 工具。
> 开始前读 `PROJECT_MEMORY.md`、`CONTRIBUTING.md` 和 `README.md`。Claude Code 还会自动读取 `CLAUDE.md`。
> 当前开发分支：`new`；PR 提到 `new`，不直接合并 `main`。

## 修改边界

只改：

```text
papers/<slug>.html
assets/figs/（仅新增图件时）
pdfs/（本地，不进入 Git）
```

`assets/data.js` 和 `pdfs/library_hashes.json` 只由管理员更新，成员不要改。

禁止改：

```text
build/
```

`build/` 是底层与历史构建源。普通 PR 改 `build/` 会被 `.github/workflows/guard-build.yml` 拒绝；确需修改先联系作者 @yiluntam，由作者加 `allow-build-change` 标签。

`assets/app.js`、`assets/style.css`、`assets/katex/`、`assets/pdfjs/` 不是日常条目修改所需；要改必须说明原因并由作者审核。

## 条目规则

成员负责：

1. `papers/<slug>.html`：正文、题录、标签、DOI、PDF 按钮；新页面 `data-pid` 留空；
2. PR 描述中的 `assets/data.js` 条目对象（`id` 留空）；
3. `meta` 计数建议（`total`、`with_pdf`、`tagCounts`、`focusCounts` 等）。

管理员负责分配唯一 id、更新 `assets/data.js` 并填写页面 `data-pid`；在管理员更新前，条目不会出现在文献库、搜索和筛选中。不要自行按 DOI 哈希取号。

## 内容与 PDF

- 不编造文献、DOI、摘要、数值或结论；
- 中文为主；公式用 Unicode 文本；
- 用户可见总结用作者—年份引注；
- PDF 不放进内容 PR；不得用 `git add -f` 把 `pdfs/*.pdf` 带进 `new`/`main`（CI 会拒绝）；如需提交全文，走单独的 `pdf-inbox` 分支，只放 `pdfs/`，该分支不合并到 `new`/`main`；
- 新增/删除本地 PDF 后由管理员运行 `python tools/update_pdf_hashes.py`，更新 `pdfs/library_hashes.json`；`pdf-inbox` PR 会用 SHA-256 查重；
- 只使用合法来源，不使用 sci-hub 或绕过付费墙；
- 新增标签/关注点、页面功能或底层改动必须先联系 @yiluntam。

## 检查

```bash
node --check assets/app.js
python tools/validate_content.py --allow-orphan-pages
```

`data.js` 由管理员更新后，改为严格模式：

```bash
node --check assets/data.js
python tools/validate_content.py
```

校验会检查重复 `id`、重复页面 `data-pid`、页面/数据双向对应、本地 PDF、受控标签、各分面计数和根页面硬编码总数。重复 id 是硬错误，不能通过改别人页面来消除。

不要运行 `build_site.py`；它会覆盖手工维护的 `papers/` 和 `assets/data.js`。

## 分支与 main

- `new` 是日常贡献分支；`main` 是发布/稳定快照，已于 2026-11-19 与 `new` 同步。
- 普通成员不向 `main` 开 PR，也不直接 push。
- `main` 的 ruleset 只拦截目标为 `main` 的操作，在 `new` 上工作被放行是正常的。
- 不修改 ruleset、CI 或绕过检查；发布同步由作者操作。

## 当前事实

- 283 篇、204 篇有本地 PDF、79 篇 `无全文PDF`。
- 文件名是“作者-年份-期刊-标题”关键词 slug。
- `build/figs/` 已归档；`assets/figs/` 是运行图件。
- `assets/data.js` 仍含本机绝对路径，公开部署前必须去本地路径。
- 当前已知重复：993/2069 同一 CNKI 论文、1132/492 同题；新增重复必须复核。
