# 无全文 PDF 下载清单

当前无本地全文：**79 篇**。

## 获取方式

- **OA/机构库（可先试）**：直接打开 `oa_url`，或把 DOI 交给 CST/机构订阅。
- **CST/订阅（有 DOI）**：在 CST 中按 DOI 或标题下载。
- **CNKI/无 DOI**：在知网按标题检索；这几篇没有 DOI。

下载后把 PDF 放到 `pdfs/incoming/`，运行：

```bash
PYTHONIOENCODING=utf-8 python tools/import_downloaded_pdfs.py
```

导入后，在 `papers/<slug>.html` 和 `assets/data.js` 中更新该条目的 PDF 按钮/`pdf_href`；不要运行 `build_site.py`。

## 统计

- CST/订阅（有 DOI）：58 篇
- OA/机构库（可先试）：17 篇
- CNKI/无 DOI：4 篇

完整逐条清单见 `docs/no_pdf_downloads.csv`。
