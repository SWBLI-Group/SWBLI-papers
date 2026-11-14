# 激波/边界层干扰文献图谱（SWBLI Literature Atlas）

本地离线、可检索的 Zotero 文献可视化站点。以**流动分离**、**初始分离**与**峰值传热**为主线，按文章类型、期刊目录、年代、层流/转捩/湍流、真实气体效应、关注点、建模方法与构型重新编目；每篇文献提供中文摘要、研究背景、主要工作、方法与算例细节、关键结果、结论、适用边界、关联文献与 12 种引用风格（另附 BibTeX；中文文献另加英文期刊的 in Chinese 格式）。每篇另附 OpenAlex/Crossref 的**被引数、参考文献数与来源链接**，文献库可按被引或参考文献数排序。

其中 **130 篇有可用全文的文献**另有按 IMRaD 组织的深度精读页：阅读说明、一句话/三句话摘要（区分原文、AI 概括与 AI 推断）、核心内容清单、研究缺口、流动条件与几何构型、关键参数、方法与数据、**核心推导与公式**、主要发现与证据、机制链、结论/贡献/局限、工程意义、**从原文 PDF 抓取的核心图件**、可引用素材与最终核验。公式与符号统一用 LaTeX 公式块呈现，页面加载**本地 KaTeX**（`assets/katex/`），无需联网；旧版 `formula_latex.py` 的公式仍以构建期 MathML 保留为回退。

## 打开方式

直接用浏览器打开：

```text
F:\文献工具\index.html
```

不需要服务器、不需要联网，也不依赖任何 CDN。`assets/data.js` 内含全部文献数据，`papers/<id>.html` 为逐篇详情页。

> 本地 PDF 使用 `file:///C:/Users/TYL13/Zotero/storage/...` 链接。若浏览器阻止本地文件跳转，可在详情页复制 PDF 路径，或把站点放到本地 HTTP 服务下打开。

### 在详情页补入 PDF

每个详情页底部都有“上传 PDF 并更新本页”。把单篇论文 PDF 拖入或选中后，站点用本地 PDF.js 在浏览器内解析，不上传网络：

- 更新本页“PDF ↗”按钮和侧栏文件名，PDF 以 Blob 链接直接打开；
- 抽取首页题录、原摘要、IMRaD 章节文本、关键句、图注和最多 6 页含图页面缩略图；
- 记录保存到本机浏览器的 IndexedDB（库名 `swbli-uploaded-pdfs`），刷新后仍在；换浏览器或清理站点数据会丢失；
- 可下载解析 JSON，或下载“AI 精读输入包”交给 paper-reader 流程生成同等级的中文 IMRaD 深读。浏览器端只做文本与页面抽取，不翻译、不补写公式推导，也不臆测原文没有的结论；
- 年份优先取详情页题录年份；只有题录无年份时才回退到 PDF 元数据，并标注“PDF 元数据”。

## 目录

```text
F:\文献工具\
├─ index.html              总览仪表盘
├─ library.html            文献库（搜索 + 分面筛选）
├─ reviews.html            综述与研究空白
├─ taxonomy.html           分类体系、标签、引用风格与证据说明
├─ papers\<id>.html        逐篇详情页
├─ assets\
│  ├─ style.css            暖纸编辑风格、亮/暗主题
│  ├─ app.js               筛选、引用复制、被引排序、主题切换
│  ├─ upload.js            详情页 PDF 上传、本地解析与 IndexedDB 持久化
│  ├─ pdfjs\               本地 PDF.js 3.11.174（legacy 构建，不依赖 CDN）
│  ├─ katex\               本地 KaTeX 0.16.22（CSS/JS/字体）
│  ├─ figs\<id>\           深度精读页引用的核心图件（构建时复制）
│  └─ data.js              构建产物（自动生成）
├─ data\                   预留数据目录
└─ build\
   ├─ prepare_selected.py  从 Zotero 快照生成精选元数据
   ├─ selected_meta.json   145 条精选文献元数据
   ├─ external_meta.json   109 条外部检索补入的文献元数据（含 2026-11 从 Zotero 新补的 13 条）
   ├─ crawl\                检索候选、Crossref/arXiv 元数据与新增内容草稿
   ├─ pdftext\             无摘要条目的 PDF 抽取文本
   ├─ pdftext_all\         本地 PDF 全文抽取文本（内容拓展用）
   ├─ enhance_packets\     内容拓展批次输入
   ├─ enhance_out\         内容拓展批次输出
   ├─ content_enhanced.json 详情页拓展内容覆盖层（按 id 合并）
   ├─ CONTENT_SPEC.md      内容与分类规范
   ├─ content_A–J.json     结构化中文内容（content_G 为 10 本教材，content_H 为新增 52 条，content_I 为补充 21 条，content_J 为 Zotero 新补 13 条）
   ├─ formula_latex.py     76 篇文献的旧版公式 LaTeX 源（161 个公式块）
   ├─ deep\<id>.json       130 篇 IMRaD 深度精读记录（推导、公式、图件、核验）
   ├─ deep_input\<id>.md   每篇的精读材料包（题录 + 图件清单 + 带页码全文）
   ├─ figs\<id>\           抽取的候选图件与 figures.json 清单
   ├─ pdftext_paged\       带 PAGE 标记的全文抽取
   ├─ read_manifest.json   130 篇可精读文献清单
   ├─ fetch_citations.py    从 OpenAlex/Crossref 抓取被引与参考文献数
   ├─ citation_metrics.json 抓取结果缓存（构建时合并，不联网）
   └─ build_site.py        生成全部 HTML 与 data.js
```

## 重新生成

日常改内容只需运行一个文件：

```bash
cd F:\文献工具
python build/build_site.py
```

它会重新生成 `index.html`、`library.html`、`reviews.html`、`taxonomy.html`、`papers/*.html` 和 `assets/data.js`，并把深度精读记录引用的图件复制到 `assets/figs/`。改了 `build/content_*.json`、`build/deep/*.json`、`build/formula_latex.py`、`build/meta_overrides.json` 或 `assets/style.css` 后，都运行这一个命令即可。

深度精读层的生成与校验（新增文献或重跑某篇时）：

```bash
# 1. 抽取带页码全文与候选图件（仅对本地 PDF）
python "C:/Users/TYL13/.claude/skills/paper-reader/scripts/extract_pdf.py"
# 2. 按 paper-reader 规范精读 build/deep_input/<id>.md，写入 build/deep/<id>.json
# 3. 校验字段、LaTeX、图件与页码
python "C:/Users/TYL13/.claude/skills/paper-reader/scripts/validate_deep.py" --deep build/deep --figs build/figs
# 4. 重建站点
python build/build_site.py
```

校验器只报“警告”不阻断构建；当前 130 篇记录 0 错误，4 条警告均为“原文无完整解析推导、只列定义/建模链”的预期情况。

只有**从 Zotero 重新抓取元数据**（增删文献、更新题录/摘要/PDF 路径）时，才先运行：

```bash
python build/prepare_selected.py
python build/build_site.py
```

前置：Python 3.10+，以及构建期依赖 `latex2mathml`（`python -m pip install latex2mathml`）；Zotero 数据库快照路径见 `build/prepare_selected.py`。`latex2mathml` 只在构建时使用，生成的页面本身不依赖它。

`prepare_selected.py` 读取 `selected_meta.json` 中固定的 itemID 列表；如需增删文献，修改其 `IDS` 列表，并同步补充内容 JSON。

## 分类口径

- **板块**：`流动分离`、`初始分离`、`峰值传热`、`基础与工具`（教材、计算工具、纯无粘激波背景）。`初始分离` 收录以分离起始条件、初始分离尺度或分离判据为主要研究对象的文献，并与 `流动分离` 叠加；人工清单维护在 `build/build_site.py` 的 `INITIAL_SEPARATION_IDS`。
- **文章类型**：`教材`、`会议`、`期刊`、`报告`、`综述`、`学位论文`、`预印本`。由 Zotero 类型、出版机构、arXiv 来源与综述标记派生。NASA、NACA、AGARD、AIAA 与大学/实验室技术报告统一归入 `报告`，不再按发布机构细分；报告不再同时算作期刊。NASA 报告仍可在“期刊目录”中用 `NASA报告` 标签单独筛选。综述同时保留其发表载体类型，因此各类型篇数之和可大于总数。
- **年代**：`2000~至今`、`1900~2000`。按出版年份派生，2000 年归入 `2000~至今`，两桶互斥；无年份条目不进入年代桶，界面显示“未标注”。当前 254 条均有年份：`2000~至今` 188 篇、`1900~2000` 66 篇。
- **流态**：可多值，取值为 `层流`、`转捩`、`湍流`、`无粘`、`非定常`、`多流态`。`无粘` 用于纯激波反射/马赫反射与无粘激波干扰研究，`非定常` 用于以分离泡振荡、运动激波/壁面或全局非定常为主线的研究；非定常工作同时标注层流/转捩/湍流，一篇文献可带多个流态，界面显示为“层流 / 非定常”等。教材、综述与零维/通用模型等不针对单一流态的工作归入 `多流态`。
- **真实气体效应**：`真实气体效应` 总标签 + `壁面催化`、`壁面适应`、`振动能激发`、`稀薄气体效应`、`化学非平衡`、`振动能非平衡`。
- **关注点**：`马赫数效应`、`雷诺数效应`、`壁温效应`、`轴对称效应`、`三维效应`、`湍流效应`、`动壁效应`、`非定常效应`。与“对象”标签（流态、构型）不同，关注点回答“这篇文献是否把该参数当作变量并明确讨论其影响”。判定采用证据型标准：Mach/Re 至少两个独立条件或覆盖较宽范围且有趋势结论；壁温至少冷/热两条件并讨论分离或热流响应；轴对称、三维、动壁、非定常须讨论该效应本身，不能只因“轴对称构型”“三维网格”或“求解器可算非定常”而标注；湍流须以湍流物理、转捩或湍流建模为主要内容，不能只因来流是湍流。标注集中在 `build/focus_tags.json`（当前 184 条），未标注条目保持为空，不再自动回退。当前计数：非定常 53、湍流 43、三维 48、雷诺数 42、壁温 37、轴对称 32、马赫数 30、动壁 21（同一篇可带多个关注点，故合计大于篇数）。
- **方法**：`理论建模（控制方程）`、`理论建模（数据驱动）`、`稳定性分析`、`实验研究`、`数值模拟`、`综述`、`教材`、`计算工具`。
- **构型**：`压缩拐角`、`平板`、`平板入射激波`、`双楔`、`双锥`、`轴对称`、`多构型`、`纯方程`、`其他`。平板入射激波类文献同时带 `平板` 与 `平板入射激波` 两个构型；锥/裙、圆锥激波等回转体干扰带 `轴对称`，必要时与 `双锥` 并用。教材、综述或覆盖两种以上构型的对比研究归入 `多构型`；没有特定几何、只做方程/理论推导或零维模型的工作归入 `纯方程`；确有特定构型但不在上述类别中的（鳍、唇罩、交叉激波等）归入 `其他`。
- **期刊目录**：只给流体力学与航空航天经典/核心期刊单独设短标签，例如 `JFM`、`POF`、`AIAA J`、`Shock Waves`、`CJA`、`AST`、`IJHMT`、`航空学报`；其余期刊统一归入 `其他`。AIAA 会议论文标为 `AIAA Paper`，NASA 报告标为 `NASA报告`；教材、学位论文、其余会议论文、其余报告与预印本统一标为 `非期刊`。目录行开头另有 `课题组文章` 快捷标签，按作者自动派生，可与任一目录标签叠加使用，因此计数会与其他标签重叠。刊名映射表与 `其他`/`AIAA Paper`/`NASA报告` 的回退规则在 `build/build_site.py` 的 `JOURNAL_ABBREVIATIONS` 与 `journal_tags_for()` 中维护。
- **标签**：见 `build/CONTENT_SPEC.md` 的受控词表。`课题组文章` 为派生标签，由作者 `Bao Lin / 鲍麟`、`Yu Yong-Liang / 余永亮`、`Wang Zhi-Hui / 王智慧` 自动识别，中英文姓名与姓名顺序均做归一化，无需在内容 JSON 中手工填写。当前识别出 15 篇课题组文章。

## 引用格式

每篇文献的引用下拉提供：JFM、Physics of Fluids、Chinese Journal of Aeronautics、Aerospace Science and Technology、AIAA Journal、Physical Review Fluids、Advances in Aerodynamics、Shock Waves、Acta Mechanica Sinica（力学学报英文）、力学学报、气体物理、力学快报（英文），以及 BibTeX。

中文文献（`language == "zh"`）另提供一种英文期刊引用格式：保留中文作者、中文题名与中文出处，采用作者—年份制，并在整条引文末尾加 `(in Chinese)`。

风格只改变排版，**文献出处保留原刊名/原出版社**，不会把一篇 JFM 论文写成 AIAA Journal。中文风格对期刊采用 `[J]` 与 `卷(期): 页码`，对图书采用 `[M]` 与“版次. 出版地: 出版社, 年份”；英文风格对图书使用“版次. 出版社, 出版地”，BibTeX 使用 `@book` 并写入 `publisher / address / edition / isbn`，不再套用期刊卷期和页码。

## 被引与参考文献数据

被引数和参考文献数由 `build/fetch_citations.py` 抓取并缓存到 `build/citation_metrics.json`，构建时合并进 `assets/data.js`。数据源与口径：

- **OpenAlex**：被引主口径，取 `cited_by_count` 与 `referenced_works_count`；有 DOI 时按 DOI 批量匹配，无 DOI 或 DOI 未命中时按题名 + 年份做严格匹配。
- **Crossref**：辅助口径，取 `is-referenced-by-count` 与 `references-count`；只走 DOI，不按题名猜测。参考文献数优先用 Crossref（通常更完整），Crossref 缺失或为 0 时回退 OpenAlex。
- 详情页“学术影响”同时列出两个平台的数值、匹配方式和来源链接；不同平台的收录范围与计数口径不同，数值只用于相对浏览，未匹配文献不补零。
- 卡片徽标显示 `被引 N`；达到展示阈值（当前 ≥100 次）显示红色 `高被引 N`。文献库排序新增 `被引：高 → 低` 与 `参考文献：多 → 少`，无数据条目排在末尾。
- 当前覆盖 **185 / 254** 篇（截至 2026-11-09）。未匹配的 69 篇主要是中文期刊、CNKI 学位论文、部分教材/专著和无 DOI 记录；这些平台未收录或不返回可用计数，页面会明确显示“未检索到匹配记录”。

更新流程：

```bash
cd F:\文献工具
python build/build_site.py      # 先刷新 assets/data.js（新增文献时尤其需要）
python build/fetch_citations.py # 联网抓取，写入 citation_metrics.json
python build/build_site.py      # 合并新数据并重新生成页面
```

`fetch_citations.py` 会使用 OpenAlex 批量 DOI 接口和 Crossref 逐 DOI 请求；若遇到平台限流，脚本会退避重试。构建本身完全离线，只有显式运行抓取脚本时才联网。

## 公式显示

深度精读页的公式与符号以 LaTeX 源码保存在 `build/deep/<id>.json` 的 `derivation.steps[].latex`（纯源码，不带 `$`），`build_site.py` 输出为 `\[...\]` 块，浏览器端由本地 KaTeX 0.16.22 渲染。KaTeX 的 CSS、JS、字体与初始化脚本都在 `assets/katex/`，因此断网也能正常显示。

旧版简化页的公式仍以 LaTeX 保存在 `build/formula_latex.py`，构建时用 `latex2mathml` 转为 MathML 嵌入，页面下方保留“LaTeX 源码”折叠块。修改旧版公式时编辑该文件中对应 `id` 的列表；修改深度页公式时编辑 `build/deep/<id>.json`。两者改完都运行 `python build/build_site.py`。

## 证据等级

详情页标注内容依据与置信度：`摘要+笔记`、`摘要`、`PDF全文`、`PDF摘要/结论页`、`仅题录`。中文摘要为翻译或节译；研究背景、主要工作、方法与算例细节、关键结果、结论与适用边界为依据原文的结构化提炼。拓展内容位于 `build/content_enhanced.json`，构建时按 id 合并到基础内容之上；定量结论请以原文为准。

深度精读页另按用户给定的文献阅读协议工作：只用材料包中的全文、图注与最多 6 页原 PDF 复核；每条关键判断标【原文明确】【AI概括】【AI推断】并给出页码/节/图/表/式位置；材料缺失写“文中未提及”，解析不清写“受限于材料，无法确认”；原文没有的推导不补写。若某篇的推导页只列定义式或建模链，说明原作者没有给出从守恒律出发的完整解析推导，而不是抓取遗漏。

## 已排除范围

HCW、燃烧、纯爆轰噪声，以及与 SWBLI 无关的传热/制动/鳍片文献不纳入。教材、软件文档与纯无粘激波背景保留在“基础与工具”，用于支撑主板块。本轮从 Zotero“空气动力学教材”集合补入 10 本教材/专著，教材标签不再为空。

教材扫描中明确未纳入的条目：id 405《Transport Phenomena》属化工传递现象，与空气动力学/SWBLI 无关；id 690 是 ISSW-2022 会议论文集而非教材；id 1032、1035 只有丛书/物理系列前言，不是完整教材。id 719 原 Zotero 题名与作者误填为丛书名和丛书编辑，已按版权页更正为 *Shock Wave Reflection Phenomena*、Gabi Ben-Dor、Springer 2007。

《分离流动的某些进展》（id 968）是一般分离流动综述，不属于 SWBLI 专题综述：它仍作为分离流动背景保留在文献库与详情页，但不进入“综述与研究空白”页，也不参与综述排序和“文章类型=综述”筛选。专题综述页的逐篇卡片严格按出版年份从新到旧排列（同一年按条目号），相关性优先序只用于首页推荐。“跨文献综合判断”不是固定文案，而是通读全库 254 条记录（含 27 篇综述）后按主题归纳的 10 条判断，每条给出代表性条目号/年份、共识与仍存在的分歧；全库增删后应随构建重新核对。

## 数据来源

本地 Zotero 库（去重后精选 145 条：135 篇论文/报告 + 10 本教材/专著），元数据包含题名、作者、期刊或出版社、卷期页码或版次/ISBN、DOI、摘要、Zotero 笔记、分类路径与本地 PDF 路径。构建过程不修改 Zotero 原始数据库，只读取快照副本。

另有 109 条通过 Crossref、arXiv、OpenAlex 与 Zotero 学位论文扫描补入，写入 `build/external_meta.json` 与 `build/content_H.json`、`build/content_I.json`、`build/content_J.json`，构建时与主库合并，当前总计 254 条（240 篇论文/报告/学位论文/预印本 + 14 本教材/专著）。前 52 条补入重点是近五年增长最快、原库最薄弱的方向：

- `2001–2014`：全局稳定性、绝对/对流不稳定性、瞬态增长、预解分析、输入–输出、三波共振与二次失稳（14 篇）。
- `2015–2026`：高超声速湍流 DNS/LES、壁面模化 LES、壁面热流与分离–加热耦合、RANS 不确定性与传热封闭（12 篇）。
- `2027–2040`：三维后掠/锥形/双鳍/轴对称干扰、Görtler 涡、有限宽激波发生器、三维膨胀–压缩构型（14 篇，其中 2 篇为综述）。
- `2041–2048`：干扰长度与分离泡标度、高焓修正、非定常分离起始与低频机制（8 篇）。
- 学位论文 4 篇：粗糙壁热流–阻力关联（250）、任意催化壁传热理论（754）、湍流分离尺度预测（755）、压缩拐角壁面效应（909）。

前 52 条的中文摘要、推导思路、关键发现与结论均据摘要/PDF 整理；其中 2020、2023、2024 三条原文摘要未能获取，内容依据题录与公开摘要推断，`evidence` 标注为“题录/公开摘要”，`confidence` 为“低”，引用时请核对原文。前 52 条新增条目中 18 条带本地 PDF，存放于 `pdfs/` 或 Zotero 存储目录；跨库 DOI/标题去重已在构建前完成。

后续补充 21 条（content_I，16 条带本地 PDF），重点为：低超声速分离长度标度（1480）、再附峰值热流关联（474）、轻微稀薄三温度 NSF（680）、运动平板 SWBLI（803/809）、超声速动态压缩拐角热流（1005）、低频非定常实验（874）、RANS 壁温效应（1476）、尾迹型强干扰模型（1477）、非定常分离判据（1482）、MacCormack 数值方法（1485）、宽域进气道控制（990）、鼓包控制综述（989）、AGARDograph 203（1472）及两本专著（1132、1286）。类型分布为 13 篇期刊论文、3 篇会议论文、3 份报告（含 1 份 NASA 报告与 AGARD 综述讲义）、2 本专著，其中 4 篇属综述性质；依据层级为 16 条高（PDF 全文）、4 条中（摘要或出版社目录）、1 条低（仅题录）。这一批已逐条对照 PDF 全文、Crossref 摘要或出版社章节目录核查；无全文或刊源待核的条目（1192、995、1120 仅有摘要级信息；1005 有全文但刊源与年份待核）在 `evidence` 与 `confidence` 中明确标注依据层级，未把题录推测写成实验结论。
