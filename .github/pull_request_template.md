## 条目信息

- 条目页面：`papers/...html`
- 文献：作者、年份、题名
- DOI：
- 主题/标签：
- 证据等级：摘要 / PDF全文 / 其他

> `id` 由管理员分配；成员新建页面时把 `data-pid` 留空（`data-pid=""`），不要自行占号。

## data.js 条目对象

> 成员不直接修改 `assets/data.js`；请把建议对象贴在这里，由管理员合并并分配 id。

```js
{
  id: "",              // 管理员填写
  href: "papers/",
  title: "",
  title_zh: "",
  author_display: "",
  year: "",
  venue: "",
  doi: "",
  tags: [],
  focus: [],
  pdf_href: "",
  evidence: "",
  confidence: ""
}
```

## PDF

- PDF 文件名或 DOI：
- 已提交到 `pdf-inbox`：是 / 否
- 本地 `pdfs/` 路径：

## 检查

- [ ] 只改了 `papers/`（必要时 `assets/figs/`）
- [ ] 没有修改 `build/`
- [ ] 没有修改 `assets/data.js`
- [ ] 新页面 `data-pid` 留空，由管理员分配 id
- [ ] 已运行 `python tools/validate_content.py --allow-orphan-pages`
- [ ] 已运行 `node --check assets/app.js`
- [ ] 内容有摘要/PDF 依据，未编造数据
- [ ] 已说明标签/关注点依据
- [ ] 没有把 PDF 放进本 PR
