# PDF inbox

本分支只用于接收成员提交的 PDF 全文，不合并到 `new` 或 `main`。

## 提交方式

1. 从 `pdf-inbox` 拉分支：

```bash
git switch pdf-inbox
git pull
git switch -c pdf/<你的GitHub用户名>/<slug>
```

2. 把 PDF 放到：

```text
pdfs/<DOI 或 slug>.pdf
```

3. 提交 PR，目标分支选 `pdf-inbox`；
4. PR 中写清 DOI、题名、年份、来源（出版社/arXiv/NASA/CST/学校订阅）；
5. 作者审核后下载 PDF，放入本地 `pdfs/`，再合并对应的 `new` 内容 PR。

## 规则

- 只放 PDF，不改 `papers/`、`assets/`、`build/`；
- 不使用 sci-hub 或盗版源；
- 本分支不合并到 `new`/`main`；
- 文件尽量按 `pdfs/<slug>.pdf` 或 `pdfs/<DOI>.pdf` 命名。
