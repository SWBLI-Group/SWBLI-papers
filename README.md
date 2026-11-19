# 激波/边界层干扰文献图谱

一个离线、可检索的 SWBLI / 高超声速激波/边界层干扰文献库。每个条目包含中文摘要、研究背景、主要工作、关键结果、结论、适用边界、关联文献和引用格式；有本地全文的条目可直接打开 PDF。

## 项目结构

```text
F:\文献工具\
├─ index.html              总览
├─ library.html            文献库（搜索 + 分面筛选）
├─ reviews.html            综述与研究空白
├─ taxonomy.html           分类体系与检索口径
├─ papers\
│  └─ <作者>-<年份>-<期刊>-<标题>.html
├─ assets\
│  ├─ data.js              文献库前端索引（搜索、筛选、卡片）
│  ├─ app.js               筛选、引用、主题切换
│  ├─ style.css
│  ├─ katex\               本地公式渲染
│  ├─ pdfjs\               本地 PDF 解析
│  └─ figs\                深度精读页图件
├─ pdfs\                   本地全文库（不进入 Git）
│  ├─ <作者>-<年份>-<期刊>-<标题>.pdf
│  ├─ manifest.json        id 与文件名的对应表
│  └─ README.md
├─ docs\                   无全文清单与 PDF 补全说明
├─ tools\                  PDF 导入等辅助脚本
├─ build\                  底层与历史构建源（成员禁止修改）
├─ CONTRIBUTING.md         贡献与修改规范
├─ PROJECT_MEMORY.md       项目记忆（架构、现状、已知问题）
├─ CLAUDE.md               Claude Code 项目规则
└─ AGENTS.md               通用 AI 项目规则
```

## 使用

直接用浏览器打开：

```text
F:\文献工具\index.html
```

不需要服务器、联网或 CDN。

- **找文献**：进入“文献库”，用关键词搜索，或按板块、关注点、年份、流态、方法、构型、真实气体、期刊筛选。
- **看详情**：点击文献标题，进入 `papers\<关键词>.html`。
- **打开全文**：详情页的“PDF ↗”打开 `pdfs\<关键词>.pdf`；没有本地全文的条目显示“无全文PDF”，并提供 DOI 或来源页。
- **复制引用**：详情页底部可选择引用格式，或复制 BibTeX。

## 当前修改规则

当前开发分支是 **`new`**。普通成员只通过 PR 提交到 `new`，不要合并到 `main`。

### 成员可修改

```text
papers/<slug>.html      条目页面
assets/figs/            仅新增图件时
pdfs/                   本地全文，不进入 Git
```

`assets/data.js` 是文献库索引，**只由管理员更新**；普通成员不要修改。成员新增/修改条目时，在 PR 描述中提供一个 `data.js` 条目对象，由管理员合并进 `assets/data.js` 并更新 `meta` 计数。

根页面 `index.html`、`library.html`、`reviews.html`、`taxonomy.html` 由管理员按需更新统计。

`docs/` 下的 PDF 清单与获取说明可以更新；`README.md`、`CONTRIBUTING.md`、`PROJECT_MEMORY.md`、`CLAUDE.md`、`AGENTS.md` 是规则/记忆文档，修改需作者审核。

### 禁止修改

```text
build/
```

`build/` 是底层与历史构建源。普通 PR 改 `build/` 会被 CI 拒绝；确需修改时先联系作者 @yiluntam，由作者加 `allow-build-change` 标签。

### 新增/修改条目

成员负责：

1. `papers/<slug>.html`：正文、题录、标签、DOI、PDF 按钮；
2. 可选 `assets/figs/` 图件；
3. 在 PR 描述中提供 `assets/data.js` 的条目对象和 `meta` 计数建议。

管理员负责：

1. 把条目对象合并进 `assets/data.js`；
2. 更新 `meta.total`、`with_pdf`、`tagCounts`、`focusCounts` 等计数；
3. 检查页面与数据一致。

在管理员更新 `assets/data.js` 之前，新条目不会出现在文献库、搜索和筛选中。

### PDF 规则

PDF 分两条通道：

1. **内容 PR**：提交到 `new`，只改 `papers/`，不放 PDF；`assets/data.js` 由管理员更新；
2. **PDF 提交 PR**：提交到 `pdf-inbox` 分支，只放 `pdfs/<DOI 或 slug>.pdf`，不合并到 `new`/`main`。

作者从 `pdf-inbox` 下载 PDF，放入本地 `pdfs/`，再合并内容 PR。这样 PDF 可以直接提交和审核，但不会进入站点分支。只使用合法来源，不使用 sci-hub。

课题组百度网盘：

```text
链接: https://pan.baidu.com/s/5vKsauxXnsAOAMdVWa4g66Q
```

### 分支与审核

- `new`：日常贡献与审核分支；
- `main`：由作者保护，只接受作者确认后的合并；
- PR 目标选 `new`，不要向 `main` 开 PR；
- 所有 PR 由作者 @yiluntam 审核。

## assets 是什么

| 路径 | 作用 | 新增条目是否必须改 |
|---|---|---|
| `assets/data.js` | 卡片、搜索、筛选、标签、关注点、PDF 链接的全部前端数据 | **管理员更新**，成员不要改 |
| `assets/figs/` | 深度精读页图件 | 只有新增图件时改 |
| `assets/app.js` | 搜索、分面、引用复制、PDF 打开等交互 | 通常不需要 |
| `assets/style.css` | 页面样式 | 通常不需要 |
| `assets/katex/` | 本地公式渲染 | 不需要 |
| `assets/pdfjs/` | 本地 PDF 解析 | 不需要 |

## 不要运行构建

`build_site.py` 会按 `build/` 的旧源重写 `papers/` 和 `assets/data.js`，覆盖成员手工维护的页面。当前分支日常不要运行构建；确需运行先联系作者。

## AI 协作：记忆与规则

成员使用 AI 大模型修改项目时，先让模型阅读：

| 文件 | 作用 |
|---|---|
| [PROJECT_MEMORY.md](PROJECT_MEMORY.md) | 项目记忆：架构、数据流、当前状态、已知问题 |
| [CLAUDE.md](CLAUDE.md) | Claude Code 自动加载的项目规则 |
| [AGENTS.md](AGENTS.md) | 通用 AI 工具（Codex/Cursor/Copilot 等）的项目规则 |
| [CONTRIBUTING.md](CONTRIBUTING.md) | 人类贡献流程、字段规范与评审要求 |

AI 的硬性规则：

1. 只改 `papers/`，必要时 `assets/figs/`；`assets/data.js` 由管理员更新；
2. 不改 `build/`；
3. 新增标签/关注点、页面功能或底层结构，必须先联系项目作者 @yiluntam；
4. 不编造文献、DOI、摘要、数值或结论；
5. PDF 不进内容 PR，提交到 `pdf-inbox`；
6. 不改 `assets/data.js`；PR 中提供数据条目对象供管理员合并。

## 补全无全文条目

当前无本地全文的条目清单：

- [docs/no_pdf_downloads.csv](docs/no_pdf_downloads.csv)
- [docs/PDF_ACQUISITION.md](docs/PDF_ACQUISITION.md)

在 CST、学校图书馆或 CNKI 下载后，把 PDF 放进 `pdfs/incoming/`，运行：

```bash
PYTHONIOENCODING=utf-8 python tools/import_downloaded_pdfs.py --dry-run
PYTHONIOENCODING=utf-8 python tools/import_downloaded_pdfs.py
```

脚本会按 id、DOI 或标题匹配并复制成关键词文件名；只使用合法来源。
