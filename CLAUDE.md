# 项目规则（Claude Code 专用入口）

> 先读 `PROJECT_MEMORY.md`、`CONTRIBUTING.md` 和 `README.md`。
> 当前开发分支：`new`。普通成员 PR 提交到 `new`，不要合并到 `main`。

## 修改边界

允许修改：

```text
papers/<slug>.html
assets/data.js
assets/figs/（仅新增图件时）
pdfs/（本地，不进入 Git）
```

禁止修改：

```text
build/
```

`build/` 是底层与历史构建源；改它会被 CI 拒绝。确需修改时先联系作者 @yiluntam，由作者加 `allow-build-change` 标签。

`assets/app.js`、`assets/style.css`、`assets/katex/`、`assets/pdfjs/` 不是日常条目修改所需；要改必须在 PR 中说明原因。

## 新增/修改条目

1. 同时修改 `papers/<slug>.html` 和 `assets/data.js`；
2. 保证 `href`、`pdf_href`、`tags`、`focus` 页面与数据一致；
3. 更新 `assets/data.js` 的 `meta.total`、`with_pdf`、`tagCounts`、`focusCounts` 等计数；
4. 标签/关注点必须有正文证据；
5. PDF 放本地 `pdfs/` 或网盘，不提交 Git；
6. 新增标签、页面功能或底层改动必须先联系 @yiluntam。

## 内容规则

- 不编造文献、DOI、作者、年份、摘要、数值或结论；
- 摘要级证据不能写成全文结论；
- 中文为主；公式用 Unicode 文本，不用 LaTeX；
- 用户可见总结用作者—年份引注，不用内部数字 id。

## 检查

```bash
node --check assets/data.js
node --check assets/app.js
```

不要运行 `build_site.py`；它会用旧构建源覆盖手工维护的 `papers/` 和 `assets/data.js`。

## 禁止事项

- 不使用 sci-hub 或盗版源；
- 不提交 PDF、大文件、数据库；
- 不覆盖/删除别人的条目；
- 不在 Git 提交中添加合作者信息（如 `Co-Authored-By`）。
