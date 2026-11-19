# 贡献与修改规范（new 分支）

本分支采用“条目页面 + 数据索引”的直接维护方式。**`build/` 是唯一禁止修改的底层**，其余站点文件通过 PR 提交，由作者审核。

> 开发分支：`new`。所有成员 PR 请提交到 `new`，不要合并到 `main`。`main` 由作者保护。

## 1. 可修改与不可修改

### 禁止修改

```text
build/
```

`build/` 里的脚本、题录、内容 JSON、深读记录和公式源都是维护者底层。普通 PR 修改 `build/` 会被 CI 拒绝；确需修改时先联系作者 @yiluntam，由作者加 `allow-build-change` 标签。

`assets/data.js` 同样只由管理员更新；普通成员 PR 修改它会被 `guard-data` 拒绝。成员在 PR 描述中提供条目对象，由作者合并。

### 成员可修改

```text
papers/<slug>.html      条目页面
assets/figs/            可选：条目新增图件
pdfs/                   本地全文（不进入 Git）
```

`assets/data.js` 是文献库索引，**只由管理员更新**；普通成员不要修改。成员在 PR 描述中提供一个 `data.js` 条目对象，由管理员合并并更新 `meta` 计数。

根页面 `index.html`、`library.html`、`reviews.html`、`taxonomy.html` 也由管理员按需更新统计。

`docs/` 下的 PDF 清单和获取说明可以随 PR 更新；但 `README.md`、`CONTRIBUTING.md`、`PROJECT_MEMORY.md`、`CLAUDE.md`、`AGENTS.md` 属于项目规则/记忆，普通成员不要直接改，确有需要请在 PR 中提出，由作者审核。

`assets/app.js`、`assets/style.css`、`assets/katex/`、`assets/pdfjs/` 也不是日常条目修改所需；如果确实要改，请在 PR 中说明原因，由作者重点审核。

## 2. assets 是什么

| 路径 | 作用 | 新增条目是否必须改 |
|---|---|---|
| `assets/data.js` | 文献库全部前端数据：卡片、搜索、筛选、标签、关注点、PDF 链接 | **管理员更新**，成员不要修改 |
| `assets/figs/` | 深度精读页引用的图件 | 只有新增图件时改 |
| `assets/app.js` | 搜索、分面、引用复制、PDF 打开等交互 | 通常不需要 |
| `assets/style.css` | 页面样式 | 通常不需要 |
| `assets/katex/` | 本地公式渲染 | 不需要 |
| `assets/pdfjs/` | 本地 PDF 解析 | 不需要 |

**关键：** 成员只改 `papers/<slug>.html`，并在 PR 描述中提供 `assets/data.js` 条目对象；管理员合并 `data.js` 后，条目才会出现在文献库和筛选中。

## 3. 新增一条文献

1. 复制一个结构相近的 `papers/<slug>.html`，改成新页面；
2. 修改页面中的题录、中文内容、标签、DOI、PDF 按钮；
3. 在 PR 描述中贴出对应 `assets/data.js` 条目对象（可复制本文下方参考格式）；
4. 在 PR 描述中写出 `meta` 计数建议（`total`、`with_pdf`、`tagCounts`、`focusCounts` 等）；
5. 把 PDF 放到本地 `pdfs/<slug>.pdf`，或提交到 `pdf-inbox`，**不要放进内容 PR**；
6. 提交 PR 到 `new` 分支，等待管理员审核并更新 `assets/data.js`。

建议 `id` 使用 DOI（或 Zotero key）的 SHA-1 前 7 位转成整数，避免多人撞号；也可以先联系作者分配。

### data.js 条目对象参考

```js
{
  id: 2101,
  href: "papers/<作者>-<年份>-<期刊>-<标题>.html",
  title: "英文题名",
  title_zh: "中文题名",
  author_display: "第一作者 et al.",
  year: "2026",
  venue: "期刊名",
  doi: "10.xxxx/xxxx",
  abstract_zh: "...",
  main_work: "...",
  conclusions: "...",
  limits: "...",
  board: ["流动分离"],
  regimes: ["湍流"],
  methods: ["数值模拟"],
  geometry: ["压缩拐角"],
  tags: ["湍流", "流动分离", "数值模拟"],
  focus: ["壁温效应"],
  pdf_href: "pdfs/<slug>.pdf",
  pdf_name: "<slug>.pdf",
  evidence: "PDF全文",
  confidence: "高"
}
```

字段和页面必须一一对应；尤其 `href`、`pdf_href`、`tags`、`focus` 不能与页面不一致。

## 4. 修改已有条目

1. 直接在 `papers/<slug>.html` 改内容；
2. 在 PR 描述中给出 `assets/data.js` 对应对象的新值；
3. 如果修改标签/关注点，同时给出 `meta.tagCounts`、`meta.focusCounts` 的更新建议；
4. 如果删除 PDF，同时说明 `pdf_href` 的新值；
5. 提交 PR，由管理员更新 `assets/data.js` 并合并。

### 删除条目

不要直接删除别人的页面。把条目标记为撤稿/替换，或先在 Issue/PR 中说明；由作者确认后再删。

## 5. PDF 规则：内容 PR 与 PDF 提交分开

PDF 采用两条通道，避免把大文件和站点内容混在一个 PR 里：

### A. 内容 PR（提交到 `new`）

只改：

```text
papers/<slug>.html
assets/figs/（可选）
```

`assets/data.js` 由管理员更新。

**不要在这个 PR 里放 PDF。** `new` 分支的 `pdfs/` 继续由 `.gitignore` 排除。

### B. PDF 提交 PR（提交到 `pdf-inbox` 分支）

专门用于上传全文，不合并到 `new`：

```text
pdf-inbox 分支
└─ pdfs/<DOI 或 slug>.pdf
```

- 只提交 PDF，不改 `papers/`、`assets/` 和 `build/`；
- 作者审核后从 `pdf-inbox` 下载 PDF；
- 作者把 PDF 放入本地项目的 `pdfs/`，再合并对应的内容 PR；
- `pdf-inbox` 永远不合并到 `new`/`main`。

这样 PDF 可以被直接提交、审核和使用，但不会进入站点分支，也不会把 1.2 GB 二进制带进 `new`。

只使用合法来源：出版社、arXiv、NASA、机构仓库、学校/CST 订阅、课题组 Zotero；禁止 sci-hub 和绕过付费墙。

## 6. 标签与关注点

- 标签、关注点可以在当次条目 PR 中提出；
- 新增标签必须在页面和 PR 描述中的 `data.js` 条目里体现；`meta` 计数由管理员更新；
- 关注点必须有正文证据，不能只因标题或构型出现；
- 新增全局标签/页面功能属于底层变更，PR 中必须写明理由，由作者 @yiluntam 审核。

## 7. 不要运行构建

`build/` 禁止修改，日常也不要运行 `build_site.py`：

- 它会根据 `build/` 的旧数据重写 `papers/` 和 `assets/data.js`；
- 会覆盖成员手工维护的页面；
- 当前分支的条目页面和 `assets/data.js` 是直接维护源。

如果确实需要运行构建，先联系作者。

## 8. PR 流程

1. 从 `new` 拉分支：

```bash
git switch new
git pull
git switch -c contrib/<你的GitHub用户名>/<slug>
```

2. 修改 `papers/`，可选 `assets/figs/`；不要改 `assets/data.js`；
3. 本地检查页面链接：

```bash
node --check assets/app.js
```

如果本地确实改了 `data.js`，管理员合并前再运行 `node --check assets/data.js`。

4. 提交 PR，目标分支选 **`new`**，不要选 `main`；
5. PR 标题：

```text
[entry] <第一作者> <年份> <简要标题>
```

6. PR 描述写清：

- 改了哪个 `papers/` 页面；
- PR 描述中的 `data.js` 条目对象和 id；
- 新增/修改的标签和关注点；
- PDF 本地文件名/网盘位置；
- 证据等级（摘要/全文）；
- 是否有不确定内容。

7. 作者审核后合并到 `new`；**不要自行合并到 `main`**。

## 9. 评审重点

- 页面与管理员合并后的 `assets/data.js` 是否一致；
- 是否只改了 `papers/`、`assets/`、`pdfs/` 等允许路径；
- 是否误改 `build/`；
- 标签/关注点是否有证据；
- PDF 来源是否合法；
- 是否编造数值、DOI、作者或结论；
- 中文内容是否通顺、与原文一致。

## 10. 分支与 main

- `new`：日常贡献与审核分支；
- `main`：由作者保护，只接受作者确认后的合并；
- 普通成员不要向 `main` 开 PR，也不要直接 push；
- 作者在 GitHub 设置中保护 `main`：Require PR、Require review、Require status checks、禁止 force push。

## 11. 一句话

**成员只改 `papers/`（必要时 `assets/figs/`），`assets/data.js` 由管理员更新；PDF 走 `pdf-inbox`；`build/` 禁止修改；所有 PR 提到 `new`，由作者审核，不直接合并 `main`。**
