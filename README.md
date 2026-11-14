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
   ├─ audit\               标签与深读的审计记录（不参与构建）
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
