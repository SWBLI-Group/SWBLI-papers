# 贡献与修改规范

本项目是多成员共同维护的 SWBLI 文献库。目标不是让一个人包揽全部文献，而是让每位成员维护自己负责的主题或批次，同时保证整个库的结构、标签和页面风格一致。

## 1. 核心原则

1. **一条文献一个 JSON 文件**，不要把多条文献写进同一个大 JSON。
2. **只提交内容数据，不手写 HTML**。`papers/<slug>.html` 由构建脚本生成，不要手动编辑。
3. **PDF 不进 Git**。PDF 放本地 `pdfs/`、Zotero 群组库或课题组网盘；Git 只保存题录、摘要和结构化内容。
4. **底层结构冻结**。项目目录、字段 schema、受控标签、构建脚本和页面样式由维护者统一修改；普通贡献只新增/修改自己的记录。
5. **以 DOI 或 Zotero key 作为稳定标识**，不要用“第几篇”或临时数字当主键。

## 2. 固定不变的部分

以下内容属于项目底层，成员不要在自己的 PR 中修改：

```text
build/build_site.py          构建入口
build/*.json                 全局题录/关注点/映射
build/deep/                  深度精读记录
build/formula_latex.py       公式源
assets/app.js                检索、筛选、引用逻辑
assets/style.css             页面样式
assets/data.js               构建生成物
papers/*.html                构建生成物
index.html / library.html    构建生成物
reviews.html / taxonomy.html 构建生成物
schemas/                     记录 schema
```

如果需要新增字段、标签、页面模块或修改构建逻辑，先开 Issue，标题用：

```text
[Schema change] 需要新增的字段或标签
[Build change] 需要修改的构建行为
```

由维护者统一修改 schema、构建脚本和前端，再通知所有成员。

## 3. 成员自己的工作区

新增文献统一放在：

```text
records/<github-handle>/<year>/<slug>.json
```

例如：

```text
records/yiluntam/2026/Bleilebens-2006-ShockWaves-elevated-surface-temperatures.json
```

- `<github-handle>`：贡献者的 GitHub 用户名，便于确定维护边界。
- `<year>`：文献年份，便于按年份浏览。
- `<slug>`：与页面、PDF 一致的“作者-年份-期刊-简要标题”标识，避免中文文件名和特殊字符。
- 每位成员只修改自己目录下的文件；不要直接改别人的记录。
- 如果同一篇文献由多人维护，先在 Issue 中确认唯一负责人，避免重复。

## 4. 单条记录格式

每个 JSON 只描述一篇文献，建议包含以下字段：

```json
{
  "schema_version": 1,
  "doi": "10.1017/jfm.2024.533",
  "zotero_key": "XXXXXXXX",
  "title": "Effects of wall temperature on hypersonic shock wave/turbulent boundary layer interactions",
  "authors": [
    { "first": "Ji", "last": "Zhang" }
  ],
  "year": "2024",
  "journal": "Journal of Fluid Mechanics",
  "journal_abbr": "JFM",
  "volume": "",
  "issue": "",
  "pages": "",
  "language": "en",
  "abstract_orig": "原文摘要……",
  "content": {
    "title_zh": "壁面温度对高超声速激波/湍流边界层干扰的影响",
    "gist": "一句话概括，不超过40字",
    "abstract_zh": "中文摘要，100–260字",
    "background": "研究背景与问题，120–220字",
    "main_work": "本文主要工作，260–420字",
    "method_detail": "方法与算例细节，180–320字",
    "findings": "关键结果与证据，180–320字",
    "conclusions": "本文结论，180–300字",
    "limits": "适用边界与局限，80–180字",
    "problem_solved": "本文解决的问题，60–140字",
    "key_findings": ["发现1", "发现2", "发现3"],
    "derivation_idea": "推导思路，可选",
    "derivation_steps": ["步骤1", "步骤2", "步骤3"],
    "formula": null,
    "review": null
  },
  "board": ["流动分离"],
  "regimes": ["湍流"],
  "real_gas": [],
  "methods": ["数值模拟"],
  "geometry": ["压缩拐角"],
  "tags": ["湍流", "流动分离", "数值模拟"],
  "focus": ["壁温效应", "非定常效应"],
  "evidence": "PDF全文",
  "confidence": "高",
  "pdf_file": "pdfs/zhang-2024-jfm-wall-temperature.pdf",
  "status": "active"
}
```

### 字段约定

- `board`：`流动分离`、`初始分离`、`峰值传热`、`基础与工具`，可多选。
- `regimes`：`层流`、`转捩`、`湍流`、`无粘`、`非定常`、`多流态`。
- `real_gas`：空数组，或 `真实气体效应`、`壁面催化`、`壁面适应`、`振动能激发`、`稀薄气体效应`、`化学非平衡`、`振动能非平衡`。
- `methods`：`理论建模（控制方程）`、`理论建模（数据驱动）`、`稳定性分析`、`实验研究`、`数值模拟`、`综述`、`教材`、`计算工具`。
- `geometry`：`压缩拐角`、`平板`、`平板入射激波`、`双楔`、`双锥`、`轴对称`、`多构型`、`纯方程`、`其他`。
- `tags`：只能使用项目受控词表，不能自造标签。
- `focus`：只能使用 `focus_tags.json` 的受控关注点；必须是正文明确讨论该变量，不能只因标题里出现。
- `evidence`：`摘要+笔记`、`摘要`、`PDF全文`、`PDF摘要/结论页`、`PDF摘要/目录`、`题录/公开摘要（原文摘要缺失）`、`仅题录`。
- `confidence`：`高`、`中`、`低`。
- `pdf_file`：只写相对本地路径，**不要提交 PDF 文件本身**。
- `status`：`active`、`retracted`、`superseded`；撤稿或替换时改这里，不要直接删除别人的记录。

## 5. PDF 与 Zotero

1. 成员先把文献和 PDF 加入 Zotero 群组库，或上传到课题组网盘；
2. 记录中填写 `zotero_key`、`doi`、`pdf_file`；
3. `pdfs/` 只保存在本地，`pdfs/*` 已被 `.gitignore` 排除；
4. 构建时由维护者或本地脚本把 PDF 复制成 `pdfs/<slug>.pdf`；
5. 只使用出版社、arXiv、NASA、机构仓库、开放获取等合法来源；不要使用盗版源。

课题组内部可通过百度网盘获取完整 `pdfs`，链接见根目录 `README.md`。

## 6. 新增与修改流程

### 新增一篇文献

1. 先搜索库和 Issue，确认 DOI/标题没有重复；
2. 在 `records/<你的handle>/<year>/` 下新增一个 JSON；
3. 填写题录、中文内容、标签、关注点和 PDF 信息；
4. 提交 PR，标题格式：

```text
[record] <第一作者> <年份> <简要标题>
```

5. PR 描述中写清楚：
   - DOI；
   - 主题（壁温/稳定性/主动控制/传热/转捩等）；
   - 证据等级；
   - 已知局限；
   - 是否有本地 PDF。

### 修改已有记录

- 只修改自己目录下的记录；
- 修改别人的记录前，先在 Issue 中联系负责人；
- 标签、关注点、结论的修改必须在 PR 描述中说明依据；
- 不接受“只改格式、不改内容”的大规模重排 PR，避免制造冲突。

### 撤稿或替换

不要直接删除记录。把 `status` 改为 `retracted` 或 `superseded`，并在 PR 中说明原因；维护者再决定是否从页面隐藏。

## 7. 评审与合并

每个 PR 至少需要：

- 一位主题负责人审核内容（壁温、稳定性、主动控制等）；
- 一位维护者审核结构、构建和链接；
- CI 通过（schema、重复 DOI、标签、构建）。

评审重点：

1. 题录是否与 DOI/原文一致；
2. 中文摘要是否忠于原文，有没有编造数字；
3. 标签和关注点是否有证据；
4. PDF 来源是否合法；
5. 是否修改了不该改的底层文件。

## 8. 分支与提交

分支名：

```text
contrib/<github-handle>/<slug>
```

提交信息示例：

```text
[record] add Zhang 2024 JFM wall-temperature paper
[fix] correct DOI for Li 2025 CJA paper
[focus] tag Hao 2023 as stability
```

一个 PR 只做一类事情：新增记录、修正记录、修改标签或修改底层结构，不要混在一起。

## 9. 当前过渡状态

现有 `content_A–K.json` 和 `external_meta.json` 是历史数据，暂由维护者统一维护，普通成员不要直接改。

新文献先按本规范的 `records/` 格式提交。`records/` 自动合并进站点的构建函数由维护者接入；在接入前，维护者会在合并 PR 时把记录转入现有内容文件并重建页面。

无论处于哪个阶段，**成员只需要提交 JSON 和 PDF 来源信息，不需要手写 HTML**；`papers/<slug>.html` 始终由 `build_site.py` 生成。

## 10. 维护者检查清单

合并前运行：

```bash
cd F:\文献工具
PYTHONIOENCODING=utf-8 python build/build_site.py
node --check assets/app.js
```

确认：

- `wrote N papers, N detail pages`
- `无全文PDF` 数量与预期一致
- 新条目有页面、有 PDF 或 DOI
- 没有数字文件名残留
- 没有把 `pdfs/` 或大文件提交进 Git
- `git status` 干净

## 11. 一句话总结

**底层结构冻结；每位成员只维护自己的 `records/` JSON 和 PDF 来源；HTML、`assets/data.js` 和页面由构建统一生成；所有改动走 Issue → PR → 主题评审 → 维护者合并。**
