# 本地全文库

本目录保存文献库条目的本地 PDF 副本，供 `papers/<关键词>.html` 详情页直接打开。

- 命名规则：`<作者>-<年份>-<期刊>-<简要标题>.pdf`
- 例：`Bleilebens-Olivier-2006-ShockWaves-elevated-surface-temperatures-hypersonic-shock-wave.pdf`
- `manifest.json`：id、slug、文件名、题名、作者、年份、期刊与 DOI 的对应表。
- `_legacy/`：早期按 DOI 命名的旧副本，仅作备份；站点不再引用。

该目录被 `.gitignore` 排除，不进入 GitHub 仓库：PDF 多为出版社版权文件，且体积达 GB 级。仓库只发布站点与题录；换机器时需从 Zotero 重新复制全文。
