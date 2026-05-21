---
title: "Llm Wiki — Karpathy的LLM Wiki：构建/查询互联的Markdown知识库"
sidebar_label: "Llm Wiki"
description: "Karpathy的LLM Wiki：构建/查询互联的Markdown知识库"
---

{/* This page is auto-generated from the skill's SKILL.md by website/scripts/generate-skill-docs.py. Edit the source SKILL.md, not this page. */}

<a id="llm-wiki"></a>
# Llm Wiki

Karpathy的LLM Wiki：构建/查询互联的Markdown知识库。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/research/llm-wiki` |
| 版本 | `2.1.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `wiki`, `knowledge-base`, `research`, `notes`, `markdown`, `rag-alternative` |
| 相关技能 | [`obsidian`](/user-guide/skills/bundled/note-taking/note-taking-obsidian), [`arxiv`](/user-guide/skills/bundled/research/research-arxiv) |

<a id="reference-full-skill-md"></a>
## 参考：完整的SKILL.md

:::info
以下是Hermes在激活此技能时加载的完整技能定义。这是Agent在技能激活时看到的指令内容。
:::

<a id="karpathy-s-llm-wiki"></a>
# Karpathy的LLM Wiki

构建并维护一个持久的、不断积累的知识库，以互相关联的Markdown文件形式呈现。
基于 [Andrej Karpathy的LLM Wiki模式](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)。

与传统RAG（每次查询都从头重新发现知识）不同，该Wiki
一次性编译知识并保持其最新。交叉引用已经存在。
矛盾已被标记。综合结果反映了所有摄入的内容。

**分工：** 人类负责整理来源并指导分析方向。Agent
负责总结、交叉引用、归档并维护一致性。

<a id="when-this-skill-activates"></a>
## 技能激活时机

当用户出现以下情况时使用此技能：
- 要求创建、构建或启动一个Wiki或知识库
- 要求将某个来源摄入、添加或处理到他们的Wiki中
- 提出问题，且配置路径下存在现有Wiki
- 要求对其Wiki进行检查、审计或健康评估
- 在研究上下文中引用他们的Wiki、知识库或“笔记”

<a id="wiki-location"></a>
## Wiki位置

**位置：** 通过 `WIKI_PATH` 环境变量设置（例如在 `~/.hermes/.env` 中）。

如果未设置，默认为 `~/wiki`。

```bash
WIKI="${WIKI_PATH:-$HOME/wiki}"
```

Wiki只是一个Markdown文件的目录——可以在Obsidian、VS Code或任何编辑器中打开。
无需数据库，无需特殊工具。

<a id="architecture-three-layers"></a>
## 架构：三层结构

<!-- ascii-guard-ignore -->
```
wiki/
├── SCHEMA.md           # 约定、结构规则、领域配置
├── index.md            # 分节内容目录，含单行摘要
├── log.md              # 时间顺序操作日志（仅追加，每年轮换）
├── raw/                # 第一层：不可变原始资料
│   ├── articles/       # 网络文章、剪辑
│   ├── papers/         # PDF、arxiv论文
│   ├── transcripts/    # 会议记录、访谈
│   └── assets/         # 源引用的图片、图表
├── entities/           # 第二层：实体页面（人物、组织、产品、模型）
├── concepts/           # 第二层：概念/主题页面
├── comparisons/        # 第二层：并排分析
└── queries/            # 第二层：值得保留的已归档查询结果
```
<!-- ascii-guard-ignore-end -->
**第 1 层 — 原始来源：** 不可变。Agent 读取但从不修改这些内容。
**第 2 层 — Wiki：** Agent 拥有的 Markdown 文件。由 Agent 创建、更新和交叉引用。
**第 3 层 — 模式：** `SCHEMA.md` 定义了结构、约定和标签分类法。

<a id="resuming-an-existing-wiki-critical-do-this-every-session"></a>
## 恢复现有 Wiki（关键 — 每次会话都要做）

当用户有一个现有的 wiki 时，**在开始任何操作之前，务必先了解情况**：

① **阅读 `SCHEMA.md`** — 了解领域、约定和标签分类法。
② **阅读 `index.md`** — 了解存在哪些页面及其摘要。
③ **浏览最近的 `log.md`** — 阅读最后 20-30 条记录以了解最近的活动。

```bash
WIKI="${WIKI_PATH:-$HOME/wiki}"
# 会话开始时进行定向读取
read_file "$WIKI/SCHEMA.md"
read_file "$WIKI/index.md"
read_file "$WIKI/log.md" offset=<最后 30 行>
```

只有在完成定向之后，才应该进行摄取、查询或 lint 检查。这可以防止：
- 为已存在的实体创建重复页面
- 遗漏对现有内容的交叉引用
- 与模式的约定相矛盾
- 重复已经记录过的工作

对于大型 wiki（100 页以上），在创建任何新内容之前，还要针对当前主题快速运行 `search_files`。

<a id="initializing-a-new-wiki"></a>
## 初始化新 Wiki

当用户要求创建或启动一个 wiki 时：

1. 确定 wiki 路径（来自 `$WIKI_PATH` 环境变量，或询问用户；默认为 `~/wiki`）
2. 创建上述目录结构
3. 询问用户 wiki 涵盖的领域 — 要具体
4. 编写针对该领域定制的 `SCHEMA.md`（参见下面的模板）
5. 编写包含分段标题的初始 `index.md`
6. 编写包含创建条目的初始 `log.md`
7. 确认 wiki 已就绪，并建议首先摄取的来源

<a id="schema-md-template"></a>
### SCHEMA.md 模板

根据用户的领域进行调整。该模式约束了 Agent 的行为并确保了一致性：

```markdown
# Wiki 模式

## 领域
[此 wiki 涵盖的内容 — 例如，“AI/ML 研究”、“个人健康”、“创业情报”]

## 约定
- 文件名：小写、连字符、无空格（例如，`transformer-architecture.md`）
- 每个 wiki 页面都以 YAML frontmatter 开头（见下文）
- 使用 `[[wikilinks]]` 在页面之间建立链接（每个页面至少 2 个出站链接）
- 更新页面时，始终更新 `updated` 日期
- 每个新页面都必须添加到 `index.md` 的正确部分下
- 每个操作都必须追加到 `log.md` 中
- **来源标记：** 在综合了 3 个或更多来源的页面上，在段落末尾附加 `^[raw/articles/source-file.md]`，这些段落的声明来自特定来源。这允许读者追溯每个声明，而无需重新阅读整个原始文件。对于单来源页面，如果 `sources:` frontmatter 已经足够，则此标记是可选的。

## Frontmatter
  ```yaml
  ---
  title: 页面标题
  created: YYYY-MM-DD
  updated: YYYY-MM-DD
  type: entity | concept | comparison | query | summary
  tags: [来自下面的分类法]
  sources: [raw/articles/source-name.md]
  # 可选的质量信号：
  confidence: high | medium | low        # 声明的支持程度
  contested: true                        # 当页面存在未解决的矛盾时设置
  contradictions: [other-page-slug]      # 与此页面冲突的页面
  ---
  ```

`confidence` 和 `contested` 是可选的，但对于观点性强或快速变化的话题，建议使用。Lint 会标记出 `contested: true` 和 `confidence: low` 的页面以供审查，这样薄弱的声明就不会在不知不觉中固化为公认的 wiki 事实。

### raw/ Frontmatter

原始来源 ALSO 有一个小的 frontmatter 块，以便重新摄取时可以检测到变化：

```yaml
---
source_url: https://example.com/article   # 原始 URL（如果适用）
ingested: YYYY-MM-DD
sha256: &lt;frontmatter 下方原始内容的十六进制摘要>
---
```

`sha256:` 允许将来对同一 URL 的重新摄取在内容未更改时跳过处理，并在内容已更改时标记变化。仅对正文（结束 `---` 之后的所有内容）进行计算，而不是 frontmatter 本身。

## 标签分类法
[为领域定义 10-20 个顶级标签。在使用新标签之前，先在此处添加。]

AI/ML 示例：
- 模型：model, architecture, benchmark, training
- 人员/组织：person, company, lab, open-source
- 技术：optimization, fine-tuning, inference, alignment, data
- 元：comparison, timeline, controversy, prediction

规则：页面上的每个标签都必须出现在此分类法中。如果需要新标签，请先在此处添加，然后再使用。这可以防止标签泛滥。

## 页面阈值
- **创建页面**：当一个实体/概念出现在 2 个或更多来源中，或者是一个来源的核心内容时
- **添加到现有页面**：当一个来源提到已经涵盖的内容时
- **不要创建页面**：对于顺便提及、次要细节或领域之外的内容
- **拆分页面**：当页面超过约 200 行时 — 拆分为子主题并添加交叉链接
- **归档页面**：当其内容完全被取代时 — 移动到 `_archive/`，从索引中移除

## 实体页面
每个值得注意的实体一个页面。包括：
- 概述 / 它是什么
- 关键事实和日期
- 与其他实体的关系（[[wikilinks]]）
- 来源引用

## 概念页面
每个概念或主题一个页面。包括：
- 定义 / 解释
- 当前知识状态
- 未解决的问题或辩论
- 相关概念（[[wikilinks]]）

## 比较页面
并排分析。包括：
- 比较的内容和原因
- 比较维度（首选表格格式）
- 结论或综合
- 来源

## 更新策略
当新信息与现有内容冲突时：
1. 检查日期 — 较新的来源通常取代较旧的来源
2. 如果确实存在矛盾，则注明两种立场及其日期和来源
3. 在 frontmatter 中标记矛盾：`contradictions: [page-name]`
4. 在 lint 报告中标记以供用户审查
```
<a id="index-md-template"></a>
### index.md 模板

索引按类型分区。每个条目占一行：wikilink + 摘要。

```markdown
# Wiki Index

> 内容目录。每个 wiki 页面按其类型列出，并附带一行摘要。
> 请先阅读此页，以便为任何查询找到相关页面。
> 最后更新：YYYY-MM-DD | 总页数：N

## 实体
<!-- 每个分区内按字母顺序排列 -->

## 概念

## 对比

## 查询
```

**扩展规则：** 当任何分区超过 50 个条目时，按首字母或子域拆分为子分区。当索引总数超过 200 个条目时，创建一个 `_meta/topic-map.md`，按主题对页面进行分组，以便更快导航。

<a id="log-md-template"></a>
### log.md 模板

```markdown
# Wiki 日志

> 所有 wiki 操作的按时间顺序记录。仅追加。
> 格式：`## [YYYY-MM-DD] 操作 | 主题`
> 操作：ingest, update, query, lint, create, archive, delete
> 当此文件超过 500 个条目时，进行轮换：重命名为 log-YYYY.md，创建新文件。

## [YYYY-MM-DD] create | Wiki 已初始化
- 领域：[domain]
- 使用 SCHEMA.md、index.md、log.md 创建结构
```

<a id="core-operations"></a>
## 核心操作

<a id="1-ingest"></a>
### 1. 摄取

当用户提供来源（URL、文件、粘贴内容）时，将其集成到 wiki 中：

① **捕获原始来源：**
   - URL → 使用 `web_extract` 获取 markdown，保存到 `raw/articles/`
   - PDF → 使用 `web_extract`（可处理 PDF），保存到 `raw/papers/`
   - 粘贴的文本 → 保存到相应的 `raw/` 子目录
   - 文件名要具有描述性：`raw/articles/karpathy-llm-wiki-2026.md`
   - **添加原始 frontmatter**（`source_url`、`ingested`、正文的 `sha256`）。
     重新摄取同一 URL 时：重新计算 sha256，与存储的值进行比较——
     如果相同则跳过，如果不同则标记差异并更新。这样做成本很低，可以每次重新摄取都执行，并能捕获无声的源更改。

② **与用户讨论要点**——哪些内容有趣、对领域重要。（在自动/定时任务上下文中跳过——直接进行下一步。）

③ **检查已有内容**——搜索 index.md 并使用 `search_files` 查找已提及实体/概念的现有页面。这是不断增长的 wiki 与一堆重复内容的区别所在。

④ **编写或更新 wiki 页面：**
   - **新实体/概念：** 仅当满足 SCHEMA.md 中的页面阈值（2 个以上来源提及，或为一个来源的核心内容）时才创建页面
   - **现有页面：** 添加新信息，更新事实，更新 `updated` 日期。当新信息与现有内容冲突时，遵循更新策略。
   - **交叉引用：** 每个新建或更新的页面必须通过 `[[wikilinks]]` 链接到至少 2 个其他页面。检查现有页面是否已反向链接。
   - **标签：** 仅使用 SCHEMA.md 中分类体系里的标签
   - **来源：** 对于综合 3 个以上来源的页面，在段落末尾附加 `^[raw/articles/source.md]` 标记，指示该段落的论断源自特定来源。
   - **置信度：** 对于观点性强、变化快或单一来源的论断，在 frontmatter 中设置 `confidence: medium` 或 `low`。除非论断在多个来源中得到充分支持，否则不要标记 `high`。
⑤ **更新导航：**
   - 将新页面按字母顺序添加到 `index.md` 中正确的章节下
   - 更新索引头部的“总页面数”和“最后更新”日期
   - 在 `log.md` 中追加：`## [YYYY-MM-DD] ingest | Source Title`
   - 在日志条目中列出每个创建或更新的文件

⑥ **报告变更内容**— 向用户列出所有创建或更新的文件。

单个来源可能触发 5-15 个 wiki 页面的更新。这是正常且期望的结果——它体现了复利效应。

<a id="2-query"></a>
### 2. 查询

当用户询问与 wiki 领域相关的问题时：

① **读取 `index.md`** 以识别相关页面。
② **对于超过 100 页的 wiki**，还需在所有 `.md` 文件中 `search_files` 查找关键术语——仅靠索引可能会遗漏相关内容。
③ **使用 `read_file` 读取相关页面**。
④ **根据汇总的知识合成答案**。引用你所参考的 wiki 页面：“基于 [[page-a]] 和 [[page-b]]...”
⑤ **将有价值的答案归档**— 如果答案是一个重要的比较、深入探讨或新颖的综合，则在 `queries/` 或 `comparisons/` 中创建一个页面。不要归档琐碎的查询——只归档那些重新推导会很麻烦的答案。
⑥ **更新 log.md**，记录查询内容以及是否已归档。

<a id="3-lint"></a>
### 3. 检查

当用户要求检查、健康检查或审计 wiki 时：

① **孤立页面：** 查找没有来自其他页面的入站 `[[wikilinks]]` 的页面。
```python
# 使用 execute_code 进行此操作——跨所有 wiki 页面的程序化扫描
import os, re
from collections import defaultdict
wiki = "<WIKI_PATH>"
# 扫描 entities/、concepts/、comparisons/、queries/ 下的所有 .md 文件
# 提取所有 [[wikilinks]]——构建入站链接映射
# 入站链接数为零的页面即为孤立页面
```

② **损坏的 wikilinks：** 查找指向不存在页面的 `[[links]]`。

③ **索引完整性：** 每个 wiki 页面都应出现在 `index.md` 中。将文件系统与索引条目进行对比。

④ **前置元数据验证：** 每个 wiki 页面必须包含所有必填字段（title、created、updated、type、tags、sources）。标签必须属于分类体系。

⑤ **过时内容：** 那些 `updated` 日期比提及相同实体的最新来源早 90 天以上的页面。

⑥ **矛盾内容：** 相同主题下存在冲突表述的页面。查找共享标签/实体但陈述不同事实的页面。将有 `contested: true` 或 `contradictions:` 前置元数据的页面全部展示给用户审查。

⑦ **质量信号：** 列出带有 `confidence: low` 的页面，以及任何只引用单个来源但未设置 confidence 字段的页面——这些页面要么寻找佐证，要么降级为 `confidence: medium`。

⑧ **来源漂移：** 对于 `raw/` 中带有 `sha256:` 前置元数据的每个文件，重新计算哈希值并标记不匹配的情况。不匹配表示原始文件被编辑过（不应该发生——raw/ 是不可变的）或从已更改的 URL 中导入。不是硬错误，但值得报告。

⑨ **页面大小：** 标记超过 200 行的页面——这些页面应考虑拆分。
⑩ **标签审计：** 列出所有正在使用的标签，标记任何不在 SCHEMA.md 分类法中的标签。

⑪ **日志轮转：** 如果 log.md 超过 500 条记录，则进行轮转。

⑫ **报告发现结果**，需包含具体文件路径和建议操作，并按严重程度分组（损坏链接 > 孤立页面 > 源文件漂移 > 有争议页面 > 陈旧内容 > 样式问题）。

⑬ **追加到 log.md：** `## [YYYY-MM-DD] lint | 发现 N 个问题`

<a id="working-with-the-wiki"></a>
## 使用 Wiki

<a id="searching"></a>
### 搜索

```bash
# 按内容查找页面
search_files "transformer" path="$WIKI" file_glob="*.md"

# 按文件名查找页面
search_files "*.md" target="files" path="$WIKI"

# 按标签查找页面
search_files "tags:.*alignment" path="$WIKI" file_glob="*.md"

# 最近活动
read_file "$WIKI/log.md" offset=<最后 20 行>
```

<a id="bulk-ingest"></a>
### 批量导入

当一次性导入多个来源时，请批量处理更新：
1. 先读取所有来源
2. 识别所有来源中的实体和概念
3. 一次性检查所有实体和概念的现有页面（一次搜索，而非 N 次）
4. 一次性创建/更新页面（避免重复更新）
5. 最后只更新一次 index.md
6. 为整个批次写入一条日志记录

<a id="archiving"></a>
### 归档

当内容完全被取代或领域范围发生变化时：
1. 如果 `_archive/` 目录不存在，则创建它
2. 将页面移动到 `_archive/`，并保留其原始路径（例如 `_archive/entities/old-page.md`）
3. 从 `index.md` 中移除
4. 更新所有链接到该页面的页面——将 wikilink 替换为纯文本 + "(已归档)"
5. 记录归档操作

<a id="obsidian-integration"></a>
### Obsidian 集成

Wiki 目录开箱即用，可作为 Obsidian 仓库使用：
- `[[wikilinks]]` 渲染为可点击的链接
- 图谱视图可视化知识网络
- YAML frontmatter 为 Dataview 查询提供支持
- `raw/assets/` 文件夹存放通过 `![[image.png]]` 引用的图片

为获得最佳效果：
- 将 Obsidian 的附件文件夹设置为 `raw/assets/`
- 在 Obsidian 设置中启用 "Wikilinks"（通常默认开启）
- 安装 Dataview 插件以执行类似 `TABLE tags FROM "entities" WHERE contains(tags, "company")` 的查询

如果同时使用 Obsidian 技能和本技能，请将 `OBSIDIAN_VAULT_PATH` 设置为与 wiki 路径相同的目录。

<a id="obsidian-headless-servers-and-headless-machines"></a>
### Obsidian Headless（服务器和无头机器）

在没有显示器的机器上，使用 `obsidian-headless` 代替桌面应用。它通过 Obsidian Sync 同步仓库，无需图形界面——非常适合在服务器上运行、写入 wiki，而 Obsidian 桌面端在另一台设备上读取的 Agent。

**设置：**
```bash
# 需要 Node.js 22+
npm install -g obsidian-headless

# 登录（需要拥有 Sync 订阅的 Obsidian 账户）
ob login --email <邮箱> --password '<密码>'

# 为 wiki 创建一个远程仓库
ob sync-create-remote --name "LLM Wiki"

# 将 wiki 目录连接到该仓库
cd ~/wiki
ob sync-setup --vault "<仓库ID>"

# 初始同步
ob sync

# 持续同步（前台运行——使用 systemd 实现后台运行）
ob sync --continuous
```

**通过 systemd 实现持续后台同步：**
```ini
# ~/.config/systemd/user/obsidian-wiki-sync.service
[Unit]
Description=Obsidian LLM Wiki 同步服务
After=network-online.target
Wants=network-online.target

[Service]
ExecStart=/path/to/ob sync --continuous
WorkingDirectory=/home/user/wiki
Restart=on-failure
RestartSec=10

[Install]
WantedBy=default.target
```
```bash
systemctl --user daemon-reload
systemctl --user enable --now obsidian-wiki-sync
# 启用 linger，使同步在注销后仍然运行：
sudo loginctl enable-linger $USER
```

这允许 Agent 写入服务器上的 `~/wiki`，而你可以在笔记本或手机上的 Obsidian 中浏览同一个仓库——更改会在几秒钟内生效。

<a id="pitfalls"></a>
## 常见陷阱

- **切勿修改 `raw/` 中的文件**——源文件是不可变的。修改应写在 wiki 页面中。
- **始终先进行定位**——在新会话中进行任何操作之前，先阅读 SCHEMA、index 和最近的日志。跳过此步骤会导致重复和遗漏交叉引用。
- **始终更新 index.md 和 log.md**——跳过会使 wiki 退化。这些是导航的骨干。
- **不要为临时提及创建页面**——遵循 SCHEMA.md 中的页面阈值。一个名字在脚注中出现一次不值得创建一个实体页面。
- **不要创建没有交叉引用的页面**——孤立的页面是不可见的。每个页面必须至少链接到另外两个页面。
- **Frontmatter 是必需的**——它可以实现搜索、过滤和过时检测。
- **标签必须来自分类体系**——自由格式的标签会退化成噪音。首先将新标签添加到 SCHEMA.md，然后再使用它们。
- **保持页面可快速浏览**——一个 wiki 页面应在 30 秒内读完。超过 200 行的页面应拆分。将详细分析移到专门的深入页面。
- **批量更新前先询问**——如果一次提取会影响 10 个以上的现有页面，请先与用户确认范围。
- **轮换日志**——当 log.md 超过 500 条记录时，将其重命名为 `log-YYYY.md` 并重新开始。Agent 应在 lint 期间检查日志大小。
- **显式处理矛盾**——不要静默覆盖。同时记录两个主张并附上日期，在 frontmatter 中标记，并标记以供用户审查。

<a id="related-tools"></a>
## 相关工具

[llm-wiki-compiler](https://github.com/atomicmemory/llm-wiki-compiler) 是一个 Node.js CLI 工具，它受 Karpathy 启发，将源文件编译成概念 wiki。它与 Obsidian 兼容，因此希望使用定时/CLI 驱动编译管线的用户可以将它指向本技能维护的同一个仓库。权衡：它拥有页面生成权（取代 Agent 在页面创建上的判断），并且针对小型语料库进行了调优。当你希望 Agent 参与策展时使用本技能；当你希望批量编译源目录时使用 llmwiki。
