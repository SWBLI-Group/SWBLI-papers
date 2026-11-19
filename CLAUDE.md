# 项目规则（Claude Code 专用入口）

> 先读 `PROJECT_MEMORY.md`、`CONTRIBUTING.md` 和 `README.md`。
> 当前开发分支：`new`。普通成员 PR 提交到 `new`，不要合并到 `main`。

## 修改边界

允许修改：

```text
papers/<slug>.html
assets/figs/（仅新增图件时）
pdfs/（本地，不进入 Git）
```

`assets/data.js` 只由管理员更新，成员不要改。

禁止修改：

```text
build/
```

`build/` 是底层与历史构建源；改它会被 CI 拒绝。确需修改时先联系作者 @yiluntam，由作者加 `allow-build-change` 标签。

`assets/app.js`、`assets/style.css`、`assets/katex/`、`assets/pdfjs/` 不是日常条目修改所需；要改必须在 PR 中说明原因。

## 新增/修改条目

1. 修改 `papers/<slug>.html`；新页面把 `data-pid` 留空，不得自行分配 id；
2. 在 PR 描述中提供 `assets/data.js` 条目对象（`id` 留空）和 `meta.total`、`with_pdf`、`tagCounts`、`focusCounts` 等计数建议；
3. 标签/关注点必须有正文证据；
4. PDF 不放进内容 PR；如需提交全文，走单独的 `pdf-inbox` 分支，只放 `pdfs/`，该分支不合并到 `new`/`main`；
5. 新增/删除本地 PDF 后由管理员运行 `python tools/update_pdf_hashes.py`，更新 `pdfs/library_hashes.json`；`pdf-inbox` PR 会用 SHA-256 查重；
6. 新增标签、页面功能或底层改动必须先联系 @yiluntam；
7. 不通过修改 CI、添加标签或绕过检查来让校验变绿。

## 内容规则

- 不编造文献、DOI、作者、年份、摘要、数值或结论；
- 摘要级证据不能写成全文结论；
- 中文为主；公式用 Unicode 文本，不用 LaTeX；
- 用户可见总结用作者—年份引注，不用内部数字 id。

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

校验会检查重复 `id`、重复页面 `data-pid`、页面/数据双向对应、本地 PDF、受控标签、各分面计数和根页面硬编码总数。重复 id 是硬错误，必须由管理员重新分配，不能改别人页面来“消重”。

不要运行 `build_site.py`；它会用旧构建源覆盖手工维护的 `papers/` 和 `assets/data.js`。

## 分支与 main

- `new` 是日常贡献分支；`main` 是发布/稳定快照，已于 2026-11-19 与 `new` 同步；
- 普通成员不向 `main` 开 PR，也不直接 push；
- `main` 的 ruleset 只拦截目标为 `main` 的操作，在 `new` 上工作放行是正常的；
- 不要修改 ruleset、CI 或绕过检查；需要发布同步时由作者操作。

## 禁止事项

- 不使用 sci-hub 或盗版源；
- 不把 PDF 放进内容 PR；PDF 单独提交到 `pdf-inbox`；
- 不覆盖/删除别人的条目；
- 不自行分配 id 或复用已删除条目的 id；
- 不在 Git 提交中添加合作者信息（如 `Co-Authored-By`）。
