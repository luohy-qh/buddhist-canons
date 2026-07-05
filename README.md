<div align="center">

# buddhist-canons-lineage

**把 19 部 2429 篇佛教大藏经整理成可检索、可追溯、原文与 AI 归纳分明的 Agent Skill。**

Claude Code / Codex / OpenCode 等 Agent Skill。装进 agent 后，可以用自然语言按法义、修法、经名、部类、概念或原文引用检索大藏经资料，输出源自经典的学习型梳理、法义/修法/术语对比、逐部复习路径，以及可追溯到「经名·卷数·朝代·译者·段落」的原文证据。

[![Skill](https://img.shields.io/badge/Agent-Skill-orange.svg)](./SKILL.md)
[![Canon](https://img.shields.io/badge/大藏经-19部-8a2be2.svg)](./SKILL.md)
[![Cards](https://img.shields.io/badge/证据卡-97540-blue.svg)](./references/citation_index.json)
[![Lineage](https://img.shields.io/badge/distilled--by-lineage--skill-green.svg)](https://github.com/JuneYaooo/lineage-skill)

</div>

> **提示**：本项目仍在持续整理与勘误中，蒸馏产物由大语言模型生成，难免有个别误抽或误归属。引用于讲说、著述、传播前请务必回核原文（见下方「引用与追溯」）。

---

## 蒸馏方法

本项目的蒸馏方法来自 [lineage-skill](https://github.com/JuneYaooo/lineage-skill)：把高密度的原始材料整理成可溯源、可迁移、可产出的 Agent Skill。本项目在其基础上，针对佛典的特殊要求（引用必须精确、原文不能与后人概括混淆）做了强化：证据卡区分「原文」与「AI 归纳」，并为每一篇建立可追溯的出处索引。

## 能做什么

- **法义与修法检索**：按概念（如止观、缘起、五停心观、安般数息）、修法步骤、法相定义，跨 19 部经典检索，返回原文与结构化归纳。
- **原文 / AI 归纳分明**：`quote` 卡为经文原句（检索中标【原文】）；`method`/`concept`/`summary` 等为蒸馏模型的概括改写（标【AI 归纳】），二者永不混淆。
- **精确到段的出处**：绝大多数证据卡出处为「经名 (卷数)〖朝代 译者〗· 段#N」，可回溯到原始文本块核对。
- **置信度过滤**：每张卡带 `confidence`（high/medium/low）；对外检索默认只返回 `high`。
- **逐部复习路径**：按部类、概念、修法整理主题地图，适合系统学习。
- **回核原文**：任意一张卡都可用 `fetch_course_evidence.py` 拉出所在文本块的原文与同块全部卡，用于高影响结论的溯源。

## 适合哪些场景

| 场景 | 适合程度 | 说明 |
| --- | --- | --- |
| 系统学习某一部类 | 很适合 | 从部、概念、修法、原文几个入口检索与复习。 |
| 查某个法义/概念的经证 | 很适合 | 返回原文引用与归纳，附精确出处。 |
| 查某种修法的下手处 | 很适合 | 如止观、数息、五停心观，返回步骤与原文。 |
| 跨部对比同一主题 | 很适合 | 一个关键词可命中多部（如「五缘」跨唯识/中观/律）。 |
| 核对引用出处 | 很适合 | 每张卡可追溯到经名·卷·译者·段落，并可回核原文。 |
| 整理学习笔记 | 适合 | 可生成带出处的 Markdown。 |
| 作为法义裁定/宗派定论依据 | 不适合 | 本 skill 是修学辅助，非教证权威，不作法义定论。 |
| 替代善知识指导修持 | 不适合 | 戒律、密法、灌顶等修持须依止具格师长，不可据检索自行行持。 |

## 覆盖范围

由 **19 部佛教典籍、2429 篇文本、12332 个文本块**蒸馏出 **97540 张证据卡**（全部经大语言模型抽取）。

| 部 (course) | 中文部名 | 篇 | 文本块 | 证据卡 |
| --- | --- | ---: | ---: | ---: |
| `esoteric` | 密教部 | 606 | 2584 | 17613 |
| `sutra-collection` | 经集部 | 422 | 1852 | 13874 |
| `schools` | 经疏部（诸宗） | 184 | 1166 | 10249 |
| `sutra-commentary` | 释经论部 | 110 | 825 | 7733 |
| `apocrypha` | 古逸部·疑似部 | 181 | 920 | 7210 |
| `history` | 史传部 | 95 | 643 | 5766 |
| `vinaya-commentary-treatise-commentary` | 律疏部·论疏部 | 46 | 440 | 4299 |
| `lotus-avatamsaka` | 法华部·华严部 | 96 | 514 | 4280 |
| `agama` | 阿含部 | 155 | 548 | 3557 |
| `misc-nonbuddhist-catalogue` | 事汇部·外教部·目录部 | 66 | 387 | 3148 |
| `vinaya` | 律部 | 87 | 427 | 3056 |
| `abhidharma` | 毗昙部 | 61 | 352 | 3011 |
| `madhyamaka-yoga` | 中观部·瑜伽部 | 63 | 341 | 2877 |
| `avadana` | 本缘部 | 71 | 351 | 2846 |
| `treatise-collection` | 论集部 | 69 | 349 | 2752 |
| `ratnakuta-nirvana` | 宝积部·涅槃部 | 37 | 221 | 1923 |
| `prajnaparamita` | 般若部 | 47 | 209 | 1636 |
| `mahavaipulya` | 大集部 | 28 | 184 | 1616 |
| `dharani` | 陀罗尼 | 5 | 19 | 94 |
| **合计** | **19 部** | **2429** | **12332** | **97540** |

**不含**：上述之外的典籍、藏外文献、各家现代注疏与讲记。

## 证据卡类型

| 卡型 | 数量 | 性质 |
| --- | ---: | --- |
| `quote` | 29027 | **原文**：经文原句摘录 |
| `concept` | 21993 | AI 归纳：法相/概念定义 |
| `case` | 12997 | AI 归纳：事例/公案 |
| `method` | 11757 | AI 归纳：修法/操作步骤 |
| `boundary` | 10331 | AI 归纳：适用边界/简别 |
| `workflow` | 3550 | AI 归纳：流程 |
| `diagnostic` | 2947 | AI 归纳：辨别/判准 |
| `task` / `failure_mode` / `template` / `rubric` / `open_question` / `transfer` | 4938 | AI 归纳：其他辅助卡型 |

> 除 `quote` 外，所有卡型均为蒸馏模型对原文的概括或改写，**不得直接当作经文原句引用**。

## 目录结构

```
buddhist-canons-mentor-practitioner-lineage/
├── SKILL.md                       # Skill 说明、覆盖边界与免责声明（agent 入口）
├── references/
│   ├── citation_index.json        # source_id → 可追溯出处（经名·卷·朝代·译者）
│   ├── course_package.json        # 归一化的全库对象（概念/方法/引用/案例…）
│   ├── okf/                        # 渐进式阅读索引（27000+ 概念）
│   └── source_courses/<部>/        # 各部原始产物
│       ├── text_distillation/evidence_cards.jsonl   # 证据卡
│       └── text_sources/chunks.jsonl                # 源文本块
└── scripts/
    ├── search_course_notes.py     # 关键词检索（多部、UTF-8、置信过滤、原文/AI标注）
    └── fetch_course_evidence.py   # 按 card-id / chunk-id 回核原文
```

## 安装

把下面这段 prompt 丢给你的 AI 助手：

```text
帮我安装 buddhist-canons skill：
https://github.com/luohy-qh/buddhist-canons
```

agent 会 clone 仓库，再把目录安装到对应的 skills 目录（如 `~/.claude/skills/` 或 `~/.mavis/skills/`）。装完后重启对应 agent，让 skill 元数据重新加载。

> 也可手动 clone 后，把整个 `buddhist-canons-mentor-practitioner-lineage/` 目录拷入你的 agent skills 目录。

## 使用示例

```text
用 buddhist-canons 帮我梳理「止观」禅修怎么下手，要原文出处。
```

```text
用 buddhist-canons 查「安般数息」在各部里的具体修法，区分原文和归纳。
```

```text
用 buddhist-canons 对比「五停心观」在毗昙部和诸宗经疏里的讲法。
```

```text
用 buddhist-canons 找「缘起」相关的经文原句，只要 high 置信。
```

也可以直接用脚本：

```bash
# 检索（默认只返回 high 置信，跨全部 19 部）
python scripts/search_course_notes.py "止观" --type method --limit 10

# 限定某一部
python scripts/search_course_notes.py "念佛" --dept ratnakuta-nirvana

# 回核某张卡/某个文本块的原文
python scripts/fetch_course_evidence.py --card-id <id>
python scripts/fetch_course_evidence.py --chunk-id <id>
```

## 引用与追溯

- **出处格式**：`<部> · 经名 (卷数)〖朝代 译者〗 · 段#N`。例如：`agama · 增一阿含经 (51卷)〖东晋 瞿昙僧伽提婆译〗 · 段#2`。
- **原文 vs AI 归纳**：检索输出中【原文】为经文原句，【AI 归纳】为模型概括；引用经文时只采用【原文】，并回核原始文本块。
- **极少数经名补全**：源头采集时有 4 篇未带经名，其经名取自**源文件正文自述**（大正藏号行）人工核对补全，记录在 `scripts/weak_citation_overrides.json`；凡有外部补充（如个别译者）均在出处中显式标注依据，绝不据经号臆造经名。
- **回核原文**：涉及高影响结论、争议法义或对外引用时，用 `fetch_course_evidence.py` 拉出原文核对。

## 安全与边界说明

本项目仅用于佛教经典的**学习、检索与出处核对**，是修学辅助工具，**不是教证权威**：

- 不构成法义裁定、宗派定论或修行指导。
- 蒸馏产物由大语言模型生成，存在个别误抽/误归属；一切经文引用须回核原文。
- 涉及戒律持守、密法修持、灌顶、观修次第等，须依止具格师长（善知识）指导，不可仅凭检索结果自行行持。
- 佛经引用错误会以讹传讹，务请审慎。

## 版权与用途说明

本项目仅作个人修学、资料整理与技术交流使用，不作商业用途。所收录经典文本版权/公共领域状态归原权利人或相应来源所有；如有不适宜公开的内容，请联系删除。

## 项目缘起

这套工具来自一个个人修学需求：作者在系统研读佛典，看到课程蒸馏方法对复杂知识整理很有效，于是把大藏经蒸馏成一个便于检索、追溯和复习的 Agent Skill，顺手打磨到「引用可追溯、原文与 AI 分明、宁缺不臆造」的程度。

开源出来，是希望它也能帮到同样在研读佛典、经论的同修。初衷是辅助深度学习、检索资料、核对出处与建立知识结构，不提供法义裁定或修行指导。

## 致谢

首先感谢历代译经三藏与祖师大德的传译与注疏，感谢将大藏经数字化、整理、校勘与公开分享的各方长期努力——没有这些基础，本项目无法在现有文本之上做结构化蒸馏与索引。

本项目的蒸馏方法基于 [lineage-skill](https://github.com/JuneYaooo/lineage-skill)，一并致谢。

## 共建邀请

欢迎佛教学习者、研究者，以及对知识蒸馏、Agent Skill、资料检索与 AI 辅助学习感兴趣的开发者共同维护。

尤其是文本转录/OCR 误差、经名与译者勘误、出处核对、检索体验、提示词与索引结构优化，欢迎通过 issue / PR 协助修正。所有共建仍以修学、检索与出处校对为边界，不提供法义裁定或修行指导。

---

*Distilled with [lineage-skill](https://github.com/JuneYaooo/lineage-skill) · 仅供非商业的学习交流使用。*
