# 贡献与修改规范（new 分支）

本分支采用“条目页面 + 数据索引”的直接维护方式。**`build/` 是唯一禁止修改的底层**，其余站点文件通过 PR 提交，由作者审核。

> 开发分支：`new`。所有成员 PR 请提交到 `new`，不要合并到 `main`。`main` 是发布/稳定快照，由作者保护；当前项目尚未正式发布，`main` 会随 `new` 的验收结果同步更新。

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

### id 分配（防止撞号）

`id` 是 `assets/data.js` 的内部编号，**不再由成员自行生成**。旧规则中的 DOI/SHA-1 取号作废。

1. 成员新建页面时，把 `data-pid` 留空：`<body data-pid="">`；
2. PR 描述中的 `data.js` 对象把 `id` 留空，由管理员分配；
3. 管理员从当前最大 `id` 之后取未占用的数字，或使用已约定号段；不得复用已删除条目的 id；
4. 管理员合并 `data.js` 时，同时填写页面的 `data-pid`；
5. 合并后运行严格校验，确认 id 唯一且页面与数据一致。

禁止多人各自按 DOI 哈希取号；这仍是撞号的主要来源。`tools/validate_content.py` 会把重复 `id`、重复 `href`、重复页面 `data-pid` 直接判为失败。

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

字段和页面必须一一对应；尤其 `id`/`data-pid`、`href`、`pdf_href`、`tags`、`focus` 不能与页面不一致。

### 合并前必须通过的一致性校验

```bash
# 成员 PR：允许新页面暂时没有 data.js 条目
python tools/validate_content.py --allow-orphan-pages

# 管理员更新 data.js 后 / 合并到 new、main 前：严格模式
python tools/validate_content.py
```

脚本检查：

- 重复 `id`、重复 `href`、重复页面 `data-pid`；
- 每个 `data.js` 条目都有页面，每个页面都有数据条目；
- 页面 `data-pid` 与数据 `id` 一致；
- `href` 文件存在；本地 `pdf_href` 文件存在；
- `tags`、`focus` 属于 `meta` 受控词表；
- `meta.total`、`with_pdf`、`tagCounts`、`focusCounts`、`boardCounts`、`regimeCounts`、`methodCounts`、`geometryCounts`、`gasCounts` 与 `papers` 一致；
- 根页面 `index.html`、`library.html`、`reviews.html`、`taxonomy.html` 的硬编码总数和标签云计数与 `meta` 一致；
- 重复 DOI/标题以 `WARN` 输出，供管理员复核。

当前库中已存在的重复项（993/2069 同一 CNKI 论文、1132/492 同题）是已知警告；新增重复必须由管理员核对后合并或说明，不得当作没看见。`assets/data.js` 单行且很大，不要用自动格式化工具重排。

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

补充规则：

- 单个 PDF 建议小于 50 MB；GitHub 单文件硬上限 100 MB，超过时不要提交，改用网盘并在 PR 中说明；
- 文件名统一为 `pdfs/<slug>.pdf`，与条目页面同名，不加空格和临时后缀；
- 只提交你有权共享的全文；出版社版权 PDF 仅限课题组内部流转，不要放进公开仓库；
- `pdf-inbox` 只放 PDF 和必要说明，不放 `papers/`、`assets/`、`build/` 或压缩包；
- 作者导入本地后，再在内容 PR 中更新 `pdf_href`，并运行严格校验。

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
3. 本地检查：

```bash
node --check assets/app.js
python tools/validate_content.py --allow-orphan-pages
```

CI 还会运行 `validate-content`，检查重复 id、重复页面 `data-pid`、页面/数据一致性和根页面计数。成员 PR 允许“新页面暂时没有 data.js 条目”，但重复 id 或重复 `data-pid` 会直接失败。

管理员在 PR 中合并 `data.js` 后，改为严格模式：

```bash
node --check assets/data.js
python tools/validate_content.py
```

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
- `id` 是否由管理员分配、是否唯一，页面 `data-pid` 是否已填；
- 是否只改了 `papers/`、`assets/`、`pdfs/` 等允许路径；
- 是否误改 `build/`；
- 标签/关注点是否有证据；
- PDF 来源是否合法、体积是否可接受；
- 是否编造数值、DOI、作者或结论；
- 中文内容是否通顺、与原文一致；
- `validate-content`、`guard-build`、`guard-data` 是否全部通过。

## 10. 分支、main 与 ruleset

- `new`：日常贡献与审核分支；
- `main`：发布/稳定快照，只接受作者确认后的合并；当前未正式发布，`main` 需要随 `new` 同步；
- 普通成员不要向 `main` 开 PR，也不要直接 push；
- 管理员在发布节点用 PR 或受保护合并把 `new` 合入 `main`，合并前必须通过严格校验；
- 作者在 GitHub 设置中保护 `main`：Require PR、Require review、Require status checks、禁止 force push 和删除。

### GitHub ruleset 不生效时的检查清单

Ruleset 只对**目标分支匹配**的推送/PR 生效；在 `new` 上工作不会被 `main` 的 ruleset 拦截，这是正常现象。若在 `main` 上也没有拦截，逐项检查：

1. **目标**：Target branches 包含 `main`（或 `refs/heads/main`），不是只写了 `new` 或 `*` 之外的错误模式；
2. **状态**：Enforcement status 是 **Active**，不是 Evaluate/Disabled；
3. **绕过名单**：Bypass list 里是否包含 Organization admin / Repository admin / 你自己；组织所有者通常可绕过，测试时要用普通成员账号；
4. **规则内容**：至少启用 Restrict deletions、Block force pushes、Require a pull request before merging、Required approvals ≥ 1、Require status checks；
5. **检查名称**：Required checks 要选实际出现过的 `guard-build`、`guard-data`、`validate-content`；工作流从未运行过时，下拉列表里可能找不到；
6. **迁移遗留**：仓库从个人账号转到 Organization 后，旧 ruleset 可能仍留在个人仓库；请在 `SWBLI-Group/SWBLI-papers` 下重新创建并确认；
7. **测试方式**：用普通成员账号直接 `git push origin HEAD:main`，应被拒绝；向 `main` 开 PR，应要求审核和检查通过。

如果组织所有者账号能直接推 `main`，说明 bypass 包含了管理员；这不代表 ruleset 坏了，但普通成员仍应被拦截。要验证真实效果，必须用非管理员账号测试。

### 管理员与备份

- 至少指定 1 名备份管理员，避免只有 @yiluntam 能合并、恢复或改 ruleset；
- 定期保留仓库镜像（`git clone --mirror`）和 `assets/data.js` 备份；PDF 仍以网盘/Zotero 为准；
- 不要为了赶进度关闭 required checks 或把成员加进 bypass 名单。

## 11. 一句话

**成员只改 `papers/`（必要时 `assets/figs/`），`assets/data.js` 由管理员更新并分配 id；改完运行 `tools/validate_content.py`；PDF 走 `pdf-inbox`；`build/` 禁止修改；所有 PR 提到 `new`，由作者审核，不直接合并 `main`。**
