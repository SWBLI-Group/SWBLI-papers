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

## 自动查重

PR 会运行 `validate-pdf-inbox`：

- 只允许新增 `pdfs/<name>.pdf`，不允许修改/删除已有文件或改动其他目录；
- 检查文件头、大小和命名；
- 计算 SHA-256，与 `new` 分支的 `pdfs/library_hashes.json` 比对；已在本地文献库中的 PDF 会被拒绝；
- 同一个 PR 内或 `pdf-inbox` 中已有相同内容的 PDF 也会被拒绝。

因此，文件名不同但内容相同的 PDF 也会被识别为“不是新 PDF”。

## 规则

- 只放 PDF，不改 `papers/`、`assets/`、`build/`；
- 不使用 sci-hub 或盗版源；
- 本分支不合并到 `new`/`main`；
- 文件尽量按 `pdfs/<slug>.pdf` 或 `pdfs/<DOI>.pdf` 命名；
- pdf-inbox 只作为中转，作者下载后应定期清理已处理的 PDF，避免仓库体积持续增长。
