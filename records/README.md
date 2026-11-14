# records/

每个成员在此目录下维护自己的文献记录：

```text
records/<github-handle>/<year>/<slug>.json
```

一条文献一个 JSON，不要把多条文献合并到一个文件。字段、标签、PDF 和 PR 流程见根目录 [CONTRIBUTING.md](../CONTRIBUTING.md)。

`_TEMPLATE.json` 是空白模板，复制后改名即可。不要在这里放 PDF 或大文件。

`build_site.py` 会自动扫描本目录并合并记录；提交前运行 `python build/validate_records.py` 检查。
