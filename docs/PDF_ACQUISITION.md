# 补全无全文 PDF

当前文献库有 **79 篇**没有本地 PDF。逐条清单：

- `docs/no_pdf_downloads.csv`：id、作者、年份、题名、期刊、DOI、获取路径、OA/机构库链接、目标文件名
- `docs/no_pdf_downloads.md`：统计与操作说明

## 获取路径

| 路径 | 数量 | 做法 |
|---|---:|---|
| OA/机构库 | 17 | 先点 `oa_url`；若被反爬拦截，仍可用 CST/学校订阅按 DOI 下载 |
| CST/订阅（有 DOI） | 58 | 在 CST 或学校图书馆按 DOI/题名下载 |
| CNKI/无 DOI | 4 | 在知网按题名检索；这 4 篇没有 DOI |

不要使用 sci-hub 或其他盗版源。

## 下载后如何入库

1. 把下载到的 PDF 放到：

```text
pdfs/incoming/
```

文件名可以是 `2085.pdf`、DOI（如 `10.1017_jfm.2024.533.pdf`），或任意包含 DOI/标题的文件名。

2. 先试运行匹配：

```bash
cd F:\文献工具
PYTHONIOENCODING=utf-8 python build/import_downloaded_pdfs.py --dry-run
```

3. 匹配无误后正式导入：

```bash
PYTHONIOENCODING=utf-8 python build/import_downloaded_pdfs.py
PYTHONIOENCODING=utf-8 python build/build_site.py
```

脚本会按以下顺序匹配：

1. 文件名是内部 id（如 `2085.pdf`）；
2. 文件名或 PDF 前几页中的 DOI；
3. PDF 前几页中的规范化标题。

匹配成功后复制为 `pdfs/<作者>-<年份>-<期刊>-<标题>.pdf`，下一次构建自动挂到详情页。

## 说明

- 我无法代登录你的 CST 账号，也不能绕过付费墙；这里提供的是**可核验的下载清单 + 导入工具**。
- 如果 CST 下载的是扫描版 PDF、没有文本层，请把文件名改成内部 id（例如 `2050.pdf`），脚本仍可匹配。
- 导入后运行 `python build/validate_records.py` 和 `python build/build_site.py` 检查。
