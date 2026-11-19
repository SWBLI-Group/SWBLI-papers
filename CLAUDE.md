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

1. 修改 `papers/<slug>.html`；
2. 在 PR 描述中提供 `assets/data.js` 条目对象和 `meta.total`、`with_pdf`、`tagCounts`、`focusCounts` 等计数建议；
3. 标签/关注点必须有正文证据；
4. PDF 不放进内容 PR；如需提交全文，走单独的 `pdf-inbox` 分支，只放 `pdfs/`，该分支不合并到 `new`/`main`；
5. 新增标签、页面功能或底层改动必须先联系 @yiluntam。

## 内容规则

- 不编造文献、DOI、作者、年份、摘要、数值或结论；
- 摘要级证据不能写成全文结论；
- 中文为主；公式用 Unicode 文本，不用 LaTeX；
- 用户可见总结用作者—年份引注，不用内部数字 id。

## 检查

```bash
node --check assets/app.js
```

`data.js` 由管理员更新后再运行 `node --check assets/data.js`。

不要运行 `build_site.py`；它会用旧构建源覆盖手工维护的 `papers/` 和 `assets/data.js`。

## 禁止事项

- 不使用 sci-hub 或盗版源；
- 不把 PDF 放进内容 PR；PDF 单独提交到 `pdf-inbox`；
- 不覆盖/删除别人的条目；
- 不在 Git 提交中添加合作者信息（如 `Co-Authored-By`）。
