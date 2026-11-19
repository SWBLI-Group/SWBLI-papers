# 项目记忆（Project Memory）

> 给人类维护者和 AI 大模型的项目级背景。开始改项目前，先读本文件、`CONTRIBUTING.md` 和根目录 `README.md`。
>
> 最后更新：2026-11-19
> 当前开发分支：`new`；后续日常只在 `new` 修改，`main` 按周期/发布节点从 `new` 更新

## 1. 项目是什么

`F:\文献工具` 是一个离线的 SWBLI / 高超声速激波/边界层干扰文献图谱：

- 静态 HTML 站点；直接打开 `index.html` 即可；
- 每篇文献有中文摘要、主要工作、结论、局限、关联文献、引用格式；
- 有本地全文的条目可打开 PDF；
- 当前分支采用“条目页面 + 数据索引”的直接维护方式，不再使用 `records/` JSON。

当前规模：

| 项目 | 当前值 |
|---|---:|
| 文献总数 | 285 |
| 有本地 PDF | 206 |
| 无本地 PDF | 79 |
| 综述 | 27 |
| 关注点标签 | 10 个 |
| 标签（tag） | 36 个 |
| 深度精读记录 | 130 |

## 2. 当前文件职责

```text
papers/<slug>.html      单篇条目页面（成员可直接修改）
assets/data.js          文献库前端索引（仅管理员更新）
assets/figs/            深度精读图件（仅在需要时修改）
pdfs/<slug>.pdf         本地全文（不进入 Git）
index.html              总览
library.html            文献库壳页面
reviews.html            综述页
taxonomy.html           分类说明
build/                  底层与历史构建源（禁止修改、禁止日常运行）
docs/                   无全文清单与补全说明
tools/validate_content.py  页面/数据一致性校验（含重复 id）
```

## 3. 固定底层

**`build/` 是唯一禁止成员修改的目录。**

```text
build/build_site.py
build/*.json
build/deep/
build/formula_latex.py
build/CONTENT_SPEC.md
```

普通 PR 改 `build/` 会被 `.github/workflows/guard-build.yml` 拒绝；普通成员改 `assets/data.js` 或 `pdfs/library_hashes.json` 会被 `.github/workflows/guard-data.yml` 拒绝。确需修改时联系作者 @yiluntam，由作者加 `allow-build-change` / `allow-data-change` 标签。

## 4. 成员可修改的内容

```text
papers/<slug>.html
assets/figs/（仅新增图件时）
pdfs/（本地，不进入 Git）
```

`assets/data.js` 和 `pdfs/library_hashes.json` 只由管理员更新；成员在 PR 描述中提供条目对象和 meta 计数建议。

根页面 `index.html`、`library.html`、`reviews.html`、`taxonomy.html` 的统计/入口由管理员按需更新，并和 `assets/data.js` 保持一致。

`assets/app.js`、`assets/style.css`、`assets/katex/`、`assets/pdfjs/` 不是日常条目修改所需；如果确实要改，PR 中说明原因，由作者重点审核。

## 5. assets 是什么

| 路径 | 作用 | 新增条目是否必须改 |
|---|---|---|
| `assets/data.js` | 卡片、搜索、筛选、标签、关注点、PDF 链接的全部前端数据 | **管理员更新** |
| `assets/figs/` | 深度精读页图件 | 只有新增图件时改 |
| `assets/app.js` | 搜索、分面、引用复制、PDF 打开等交互 | 通常不需要 |
| `assets/style.css` | 页面样式 | 通常不需要 |
| `assets/katex/` | 本地公式渲染 | 不需要 |
| `assets/pdfjs/` | 本地 PDF 解析 | 不需要 |

只改 `papers/` 页面而不改 `assets/data.js`，新条目不会出现在文献库、搜索结果和筛选中。

## 6. 条目编辑规则

成员负责：

1. `papers/<slug>.html`：正文、题录、标签、DOI、PDF 按钮；
2. 可选 `assets/figs/` 图件；
3. PR 描述中的 `assets/data.js` 条目对象和 `meta` 计数建议。

管理员负责：

1. 为条目分配唯一 `id`，填写页面的 `data-pid`；
2. 把条目对象合并进 `assets/data.js`；
3. 更新 `meta.total`、`with_pdf`、`tagCounts`、`focusCounts`；
4. 检查 `href`、`pdf_href`、`tags`、`focus` 页面与数据一致。

### id 分配与校验

- 成员新页面 `data-pid` 留空，`data.js` 对象 `id` 留空；管理员统一分配，禁止成员按 DOI 哈希自行取号。
- 成员 PR 运行 `python tools/validate_content.py --allow-orphan-pages`；管理员合并 `data.js` 后运行严格模式 `python tools/validate_content.py`。
- 校验覆盖：重复 `id`/`href`/页面 `data-pid`、页面与数据双向对应、`pdf_href` 是否存在、受控标签、各分面计数、根页面硬编码总数和标签云。
- 重复 DOI/标题以 `WARN` 输出；当前已知 993/2069 同一 CNKI 论文、1132/492 同题，新增重复必须复核。
- CI：`.github/workflows/validate-content.yml`，PR 用宽松模式（允许新页面暂未进 `data.js`）；推送 `new` 时仅在本次改动包含 `assets/data.js` 才用严格模式，推送 `main` 始终严格；成员页面合并后、管理员更新 `data.js` 前 `new` 可暂时处于“页面未入索引”的过渡状态。

## 7. PDF 与版权

PDF 走独立提交通道：

- **内容 PR** 提交到 `new`：只改 `papers/`，不放 PDF；`assets/data.js` 由管理员更新；
- **PDF PR** 提交到 `pdf-inbox` 分支：只放 `pdfs/<DOI 或 slug>.pdf`，不合并到 `new`/`main`；
- 作者从 `pdf-inbox` 下载 PDF，放入本地 `pdfs/`，再合并内容 PR；
- `pdfs/library_hashes.json` 保存本地 PDF 的 SHA-256（不含全文），用于 `pdf-inbox` PR 查重；新增/删除本地 PDF 后运行 `python tools/update_pdf_hashes.py`；
- `pdf-inbox` PR 检查只接受新增 PDF，拒绝重复哈希、非 PDF、超大文件和修改已有 PDF；
- `new`/`main` 的 CI 拒绝被 Git 跟踪的 `pdfs/*.pdf`，防止用 `git add -f` 绕过 `.gitignore`；
- 课题组内部也可用百度网盘/Zotero 群组库分发；
- 只使用合法来源：出版社、arXiv、NASA、HAL、机构仓库、学校/CST 订阅、课题组 Zotero；
- **禁止 sci-hub 和绕过付费墙**；
- `assets/data.js` 的 PDF 路径已改为相对路径 / 空值（`pdf_local_abs`、`pdf_source`、`pdfs`）；公开部署前仍应复核。

## 8. 分支与审核

- `new`：日常贡献与审核分支；
- `main`：发布/稳定快照，由作者保护；当前落后于 `new`（`new` 已加入 2101/2102 等新条目），按周期/发布节点由作者从 `new` 更新；
- 普通成员不要向 `main` 开 PR，也不要直接 push；
- PR 目标选 `new`；
- 作者在 GitHub 设置中保护 `main`：Require PR、Require review、Require status checks、禁止 force push 和删除；
- `CODEOWNERS` 默认所有 PR 由 @yiluntam 审核；`guard-build.yml` 拒绝 `build/` 修改；`guard-data.yml` 拒绝成员改 `assets/data.js` 或 `pdfs/library_hashes.json`；`validate-content.yml` 检查重复 id、数据一致性和被跟踪的 PDF 二进制；
- ruleset 只对目标为 `main` 的推送/PR 生效；在 `new` 上工作被“放行”是正常的。若 `main` 也没拦截，检查 target、Active 状态、bypass 名单、required checks 名称，以及仓库转到 Organization 后旧 ruleset 是否还留在个人仓库；
- 组织所有者通常可绕过 ruleset，必须用普通成员账号验证；另指定至少 1 名备份管理员。

## 9. 不要运行构建

`build_site.py` 会按 `build/` 里的旧源重写 `papers/` 和 `assets/data.js`，会覆盖成员手工维护的页面。当前分支日常不要运行：

```bash
python build/build_site.py
```

如果确实要运行，先联系作者。

## 10. 关键主题入口

不要凭记忆直接下结论；先在 `assets/data.js` 中找对应条目，再读页面或 PDF。

| 主题 | 代表条目 |
|---|---|
| 壁温效应 | Bleilebens & Olivier 2006、Zhu 等 2017、Zuo 等 2022、Zhang 等 2026、Helm & Martín 2021 |
| 稳定性 | Yao 等 2007、Guiho 等 2016、Hao 2023、Zhang 等 2026 |
| 主动控制 | van Dommelen 等 2014、Ma 等 2023、Tao 等 2025、Guo 等 2025 |
| 轴对称 | 洪雨婷 2023、Funderburk 等 2019、Mosele 等 2023 |
| 非定常 | Touré & Schülein、Hao 2023、Zhou 等 2024 |
| 真实气体 | Davis & Sturtevant 2000、徐敬惟 2026、居光敬 2025 |

## 11. AI 工作方式

AI 进入项目后应：

1. 先读 `PROJECT_MEMORY.md`、`CONTRIBUTING.md`、`README.md`；
2. 只改 `papers/`（必要时 `assets/figs/`），不改 `build/`，不改 `assets/data.js`；
3. 新增/修改条目时改页面，并在 PR 描述中提供 `data.js` 条目对象；
4. 新增标签/关注点、页面功能或修改底层结构，必须先联系作者 @yiluntam；
5. 不编造文献、DOI、摘要、数值或结论；
6. PDF 不进 Git，不碰 sci-hub；
7. 改完运行 `node --check assets/app.js` 和 `python tools/validate_content.py --allow-orphan-pages`；管理员更新 `data.js` 后再运行 `node --check assets/data.js` 和严格模式校验；
8. 不自行分配 id；新页面 `data-pid` 留空，由管理员填写；
9. 不覆盖别人的条目；删除/替换先说明；
10. 不通过改 CI、加标签或绕过校验来让检查变绿；
11. Git 提交不要添加合作者信息。

## 12. 一句话

**成员只改 `papers/`；`assets/data.js` 由管理员更新并分配 id；改完跑 `tools/validate_content.py`；`pdfs/` 本地保存或走 `pdf-inbox`；`build/` 完全冻结；PR 提到 `new`，作者审核，不直接合并 `main`。**
