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
├─ records\               成员贡献记录（一条文献一个 JSON）
├─ schemas\               贡献记录 JSON Schema
├─ CONTRIBUTING.md        贡献与修改规范
├─ PROJECT_MEMORY.md      项目记忆（架构、现状、已知问题）
├─ CLAUDE.md              Claude Code 项目规则
├─ AGENTS.md              通用 AI 项目规则
├─ .github\               校验工作流与 CODEOWNERS
├─ pdfs\                   本地全文库（不进入 Git）
│  ├─ <作者>-<年份>-<期刊>-<标题>.pdf
│  ├─ manifest.json        id 与文件名的对应表
│  └─ README.md
├─ assets\
│  ├─ data.js              全部文献数据（构建生成）
│  ├─ app.js               筛选、引用、主题切换
│  ├─ style.css
│  ├─ katex\               本地公式渲染
│  ├─ pdfjs\               本地 PDF 解析
│  └─ figs\                深度精读页图件
└─ build\
   ├─ build_site.py        站点构建入口
   ├─ prepare_selected.py  从 Zotero 快照生成题录
   ├─ selected_meta.json   精选题录
   ├─ external_meta.json   外部补入题录
   ├─ content_*.json       结构化中文内容
   ├─ focus_tags.json      壁温/轴对称/动壁等关注点
   ├─ deep\                深度精读记录
   └─ formula_latex.py     公式源
```

> 候选图件、全文抽取文本、检索草稿等构建中间产物已移到项目外的 `F:\文献工具_archive\`，不参与日常构建。`assets\figs\` 已包含站点实际引用的 495 张图；重新做深度精读时再从归档恢复或重新抽取。

## 使用

直接用浏览器打开：

```text
F:\文献工具\index.html
```

不需要服务器、联网或 CDN。

- **找文献**：进入“文献库”，用关键词搜索，或按板块、关注点、年份、流态、方法、构型、真实气体、期刊筛选。
- **看详情**：点击文献标题，进入 `papers\<关键词>.html`。
- **打开全文**：详情页右上角的“PDF ↗”直接打开 `pdfs\<关键词>.pdf`；没有本地全文的条目会显示“无全文pdf”，并提供 DOI 或来源页。
- **复制引用**：详情页底部可选择引用格式，或复制 BibTeX。
- **上传补充 PDF**：无全文条目可在详情页底部选择本地 PDF，浏览器只在本地解析并保存在 IndexedDB，不上传网络。

## 重新构建

修改题录、内容或标签后运行：

```bash
cd F:\文献工具
python build/build_site.py
```

构建会重新生成 `index.html`、`library.html`、`reviews.html`、`taxonomy.html`、`papers\*.html` 和 `assets\data.js`。

需要重新从 Zotero 抓取题录时，先运行：

```bash
python build/prepare_selected.py
python build/build_site.py
```

依赖 Python 3.10+；公式构建可选安装 `latex2mathml`。

## PDF 与 Git

`pdfs\` 保存本地全文副本，方便详情页直接打开，但因版权和体积原因不提交到 Git。换机器后需从 Zotero 重新复制 PDF；`pdfs\manifest.json` 会记录每个条目对应的文件名。

仓库只发布站点、题录和内容数据，不包含出版社 PDF 原件。

## PDF 共享（课题组）

课题组成员可通过以下百度网盘链接获取 `pdfs` 全文库：

```text
链接: https://pan.baidu.com/s/5vKsauxXnsAOAMdVWa4g66Q
```

网盘内容仅供课题组内部学习使用，请勿公开转发。链接如失效，请联系维护者更新。

## 贡献

多人协作、记录格式、标签规范、PR 流程与评审要求见 [CONTRIBUTING.md](CONTRIBUTING.md)。核心原则：**成员只新增自己的 `records/` JSON 和 PDF 来源信息，不手写 HTML，不修改构建脚本和全局数据。**

## AI 协作：记忆与规则

成员使用 AI 大模型修改项目时，先让模型阅读：

| 文件 | 作用 |
|---|---|
| [PROJECT_MEMORY.md](PROJECT_MEMORY.md) | 项目记忆：架构、数据流、当前状态、已知问题 |
| [CLAUDE.md](CLAUDE.md) | Claude Code 自动加载的项目规则 |
| [AGENTS.md](AGENTS.md) | 通用 AI 工具（Codex/Cursor/Copilot 等）的项目规则 |
| [CONTRIBUTING.md](CONTRIBUTING.md) | 人类贡献流程、字段规范与评审要求 |
| [records/_TEMPLATE.json](records/_TEMPLATE.json) | 单条文献 JSON 模板 |

AI 的硬性规则：

1. 新增文献只改 `records/<github-handle>/<year>/<slug>.json`，不手写 `papers/*.html`；
2. `papers/*.html`、`assets/data.js`、构建脚本、前端和全局标签是冻结层；
3. **新增标签/关注点、新增页面功能、修改 schema 或构建逻辑，必须先联系项目作者 @yiluntam**，不能自行实现；
4. PDF 不进 Git，只使用合法开放获取、Zotero 群组库或课题组网盘；
5. 不编造文献、DOI、摘要、数值或结论；用作者—年份引注。

记录提交后运行：

```bash
PYTHONIOENCODING=utf-8 python build/validate_records.py
PYTHONIOENCODING=utf-8 python build/build_site.py
```

GitHub Actions 也会在 PR 中自动运行记录校验和语法检查。
