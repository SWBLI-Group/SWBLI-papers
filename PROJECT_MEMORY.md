# 项目记忆（Project Memory）

> 给人类维护者和 AI 大模型的项目级背景。开始改项目前，先读本文件、`CONTRIBUTING.md` 和根目录 `README.md`。
>
> 最后更新：2026-11-14

## 1. 项目是什么

`F:\文献工具` 是一个离线的 SWBLI / 高超声速激波/边界层干扰文献图谱：

- 静态 HTML 站点；直接打开 `index.html` 即可，不需要服务器；
- 每篇文献有中文摘要、主要工作、结论、局限、关联文献、引用格式；
- 有本地全文的条目可直接打开 PDF；
- 文献数据由 `build/` 下的题录、内容 JSON 和深读 JSON 构建生成。

当前规模：

| 项目 | 当前值 |
|---|---:|
| 文献总数 | 283 |
| 有本地 PDF | 203 |
| `无全文pdf` / 文章类型 `无全文PDF` | 80 |
| 综述 | 27 |
| 关注点标签 | 10 个 |
| 标签（tag） | 36 个 |
| 深度精读记录 | 130 |
| 关注点标注 | 211 条 |

## 2. 数据流

```text
build/selected_meta.json       145 条历史精选题目
build/external_meta.json       138 条外部补入题目
        ↓
build/content_A–K.json         结构化中文内容
build/content_enhanced.json    内容覆盖层
build/focus_tags.json          关注点（按 id）
build/deep/<id>.json           深度精读（130 篇）
build/formula_latex.py         公式 LaTeX 源
build/citation_metrics.json    被引/参考文献缓存
build/meta_overrides.json      题录覆盖
        ↓  python build/build_site.py
papers/<slug>.html             每篇详情页（生成物）
assets/data.js                 全部前端数据（生成物）
index.html / library.html / reviews.html / taxonomy.html
```

`papers/<slug>.html`、`assets/data.js` 和四个根页面都是**生成物**，不要手改。

## 3. 构建命令

```bash
cd F:\文献工具
PYTHONIOENCODING=utf-8 python build/build_site.py
node --check assets/app.js
```

Windows 终端默认 GBK，Python 必须带 `PYTHONIOENCODING=utf-8`；否则中文或上标会触发 `UnicodeEncodeError`。

构建行为：

- 读取 `build/content_*.json`（自动扫描）；
- 合并 `selected_meta.json` + `external_meta.json`；
- 合并 `focus_tags.json`、`content_enhanced.json`、`deep/*.json`；
- 把 PDF 复制到 `pdfs/<slug>.pdf`（源路径来自题录 `pdfs`，缺失时按 `pdfs/_oa_sources/`）；
- 生成关键词文件名页面，删除旧数字页面；
- `build/figs/` 已归档到项目外；构建使用现有 `assets/figs/`，当前缺失引用为 0。

## 4. 文件命名与 id

- 详情页：`papers/<作者>-<年份>-<期刊>-<简要标题>.html`
- PDF：`pdfs/<同名>.pdf`
- 作者取第一作者；两位列两位；三人以上加 `et-al`；
- 期刊用 `journal_abbr`；标题取前 7 个有意义的关键词；
- 中文文献保留汉字，英文文献用 ASCII；
- `id` 只是内部键，不再出现在页面 URL 中。不要用 `501` 这类 id 向用户引注，正文用作者—年份。

## 5. 固定底层与可改区域

### 固定底层，普通成员/AI 不要改

```text
build/build_site.py
build/prepare_selected.py
build/fetch_citations.py
build/*.json（全局题录、关注点、覆盖层）
build/deep/
build/formula_latex.py
assets/app.js
assets/style.css
assets/data.js（生成物）
papers/*.html（生成物）
index.html / library.html / reviews.html / taxonomy.html（生成物）
schemas/、标签词表、项目目录结构
```

### 成员可维护

```text
records/<github-handle>/<year>/<slug>.json
```

一条文献一个 JSON。PDF 放本地 `pdfs/`、Zotero 群组库或课题组网盘，不进 Git。

### 需要改底层时

先开 Issue：

```text
[Schema change] 需要新增的字段或标签
[Build change] 需要修改的构建行为
```

**新增标签/关注点、新增页面功能、修改 schema 或构建逻辑，必须先联系作者 @yiluntam**，由作者统一改 schema、标签词表、构建和前端，再通知所有成员。不要自行实现或合并。

## 6. 内容质量规则

- 只使用题录、摘要、Zotero 笔记或 PDF 原文；不得编造数值、公式、实验条件或结论。
- 摘要级证据不能写成全文结论；`evidence` 必须如实标注：
  `摘要+笔记`、`摘要`、`PDF全文`、`PDF摘要/结论页`、`PDF摘要/目录`、`题录/公开摘要（原文摘要缺失）`、`仅题录`。
- 置信度只用 `高`、`中`、`低`。
- 关注点必须是“正文明确把该参数当变量并讨论其影响”，不能只因标题/构型/网格出现。
- 标签只能使用受控词表；不要自造标签。
- 中文为主；公式用文本 + Unicode（∂u/∂t、∑ⱼ、√2、∇×B），不要 LaTeX。
- 对用户总结时用作者—年份引注，不用内部数字 id 代替。

## 7. PDF 与版权

- `pdfs/` 已被 `.gitignore` 排除，不进入 GitHub。
- 只使用合法来源：出版社开放获取、arXiv、NASA NTRS、HAL、机构仓库、课题组 Zotero 群组库、用户提供的 PDF。
- **不要使用 sci-hub 或其他盗版源**；不要绕过付费墙。
- 课题组内部通过百度网盘分发 PDF，链接见根目录 `README.md`。
- 公开仓库只发布题录、摘要、结构化内容和站点代码，不发布出版社 PDF。
- 注意：`assets/data.js` 目前仍含本机绝对路径（`pdf_local_abs`、`pdf_source`、`pdfs`）。公开部署前应先做去本地路径的构建，否则会暴露本机目录。

## 8. 当前协作状态

- `records/` 目录、`records/_TEMPLATE.json`、`schemas/record.schema.json`、`build/validate_records.py`、GitHub Actions 和 `CODEOWNERS` 已建立。
- `build_site.py` 已自动扫描 `records/**/*.json`，按 DOI/Zotero key/标题生成稳定内部 id，并与历史 `content_*.json` 合并。
- 重复 DOI/标题会被跳过；运行 `python build/validate_records.py` 可在提交前检查。
- `content_A–K.json` 和 `external_meta.json` 是历史数据，普通成员不要直接改。
- 知网 KNS 接口需要安全验证，无法稳定批量抓取；中文期刊建议用 CNKI 导出 RIS/BibTeX，再入库。

## 9. 关键主题入口

不要凭记忆直接下结论；先按这些入口取 id，再读内容或 PDF。

| 主题 | 查找方式 | 代表条目 |
|---|---|---|
| 壁温效应 | `focus_tags.json` 中 `壁温效应` | Bleilebens & Olivier 2006 (1112)、Zhu 等 2017 (1324)、Zuo 等 2022 (1476)、Zhang 等 2026 (1303)、Helm & Martín 2021 (1505) |
| 稳定性 | `focus_tags.json` 中 `稳定性` | Yao 等 2007 (1306)、Guiho 等 2016 (843)、Hao 2023 (2078)、Zhang 等 2026 (2097) |
| 主动控制 | `focus_tags.json` 中 `主动控制` | van Dommelen 等 2014 (1176)、Ma 等 2023 (2091)、Tao 等 2025 (2093)、Guo 等 2025 (2094) |
| 轴对称 | `focus_tags.json` 中 `轴对称效应` | 洪雨婷 2023 (2069)、Funderburk 等 2019 (1507)、Mosele 等 2023 (1563)、JFM 2026 (2098) |
| 非定常 | `focus_tags.json` 中 `非定常效应` | Touré & Schülein (742/503)、Hao 2023 (2078)、Zhou 等 2024 (2079) |
| 真实气体 | `content_*` 的 `real_gas` | Davis & Sturtevant 2000 (1116)、徐敬惟 2026 (909)、居光敬 2025 (754) |

内容位置：

- 中文摘要/结论：`build/content_*.json`
- 深读：`build/deep/<id>.json`
- 页面数据：`assets/data.js`
- 全文：`pdfs/<slug>.pdf`

## 10. AI 工作方式

AI 进入项目后应：

1. 先读 `PROJECT_MEMORY.md`、`CONTRIBUTING.md`、`README.md`；
2. 明确任务属于“新增/修改文献记录”还是“修改底层代码”；
3. 新增/修改文献时只动 `records/<handle>/...json`，不要手写 HTML；
4. 需要改 `build_site.py`、`app.js`、schema、标签词表，或新增标签/页面功能时，必须先说明影响并联系作者 @yiluntam，等待明确同意；
5. 不编造文献、DOI、摘要、数值或结论；
6. 不把 PDF、`pdfs/`、`build/figs/`、大文件提交到 Git；
7. 修改后运行构建和检查，报告真实结果；
8. 不覆盖别人的记录；不 delete 别人的文件；
9. 需要 Git 提交时不要添加合作者信息（如 `Co-Authored-By`）。

## 11. 一句话

**底层冻结、记录分散、构建统一、内容有据、PDF 不进 Git。**
