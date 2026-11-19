# 本地全文库

本目录保存文献库条目的本地 PDF 副本，供 `papers/<关键词>.html` 详情页直接打开。

- 命名规则：`<作者>-<年份>-<期刊>-<简要标题>.pdf`
- 例：`Bleilebens-Olivier-2006-ShockWaves-elevated-surface-temperatures-hypersonic-shock-wave.pdf`
- `manifest.json`：id、slug、文件名、题名、作者、年份、期刊与 DOI 的对应表（本地文件，不进入 Git）。
- `library_hashes.json`：本地 PDF 的 SHA-256 清单，**会进入 Git**；只用于查重，不含 PDF 内容。
- 早期按 DOI 命名的旧副本和开放获取源文件已清理；站点只引用当前关键词文件名的 PDF。

新增或删除本地 PDF 后，重新生成哈希清单：

```bash
python tools/update_pdf_hashes.py
```

`pdf-inbox` 的 PR 检查会用这个清单判断上传文件是否已经在文献库中；同一 SHA-256 的文件会被拒绝。

该目录中的 PDF 被 `.gitignore` 排除，不进入 GitHub 仓库：PDF 多为出版社版权文件，且体积达 GB 级。`library_hashes.json` 是唯一例外。仓库只发布站点与题录；换机器时需从 Zotero 重新复制全文。

本项目另设独立分支 `pdf-inbox` 用于接收成员提交的 PDF；该分支只放 PDF，不合并到 `new`/`main`。

课题组内部可通过百度网盘获取完整 `pdfs`：

```text
链接: https://pan.baidu.com/s/5vKsauxXnsAOAMdVWa4g66Q
```

仅供课题组内部学习使用，请勿公开转发。
