---
title: "Osint Investigation"
sidebar_label: "Osint Investigation"
description: "公共记录 OSINT 调查框架 — SEC EDGAR 文件、USAspending 合同、参议院游说、OFAC 制裁、ICIJ 离岸泄露、纽约市房产记录、OpenCorporates 注册信息、CourtListener 法庭记录、Wayback Machine 存档、Wikipedia + Wikidata、GDELT 新闻监控。跨来源实体解析、交叉链接分析、时间关联、证据链。仅使用 Python 标准库。"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

<a id="osint-investigation"></a>
# Osint Investigation

公共记录 OSINT 调查框架 — SEC EDGAR 文件、USAspending 合同、参议院游说、OFAC 制裁、ICIJ 离岸泄露、纽约市房产记录 (ACRIS)、OpenCorporates 注册信息、CourtListener 法庭记录、Wayback Machine 存档、Wikipedia + Wikidata、GDELT 新闻监控。跨来源实体解析、交叉链接分析、时间关联、证据链。仅使用 Python 标准库。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/research/osint-investigation` 安装 |
| 路径 | `optional-skills/research/osint-investigation` |
| 版本 | `0.1.0` |
| 作者 | Hermes Agent（改编自 ShinMegamiBoson/OpenPlanter，MIT 许可） |
| 平台 | linux, macos, windows |
| 标签 | `osint`, `investigation`, `public-records`, `sec`, `sanctions`, `corporate-registry`, `property`, `courts`, `due-diligence`, `journalism` |
| 相关技能 | [`domain-intel`](/user-guide/skills/optional/research/research-domain-intel), [`arxiv`](/user-guide/skills/bundled/research/research-arxiv) |

<a id="reference-full-skill-md"></a>
## 参考：完整 SKILL.md

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

<a id="osint-investigation-public-records-cross-reference"></a>
# OSINT 调查 — 公共记录交叉引用

公共记录 OSINT 的调查框架：政府合同、公司文件、游说、制裁、离岸泄露、房产记录、法庭记录、网络存档、知识库和全球新闻。跨异构来源解析实体，构建带有明确置信度的交叉链接，运行统计时间测试，并生成结构化证据链。

**仅使用 Python 标准库。** 零安装。适用于 Linux、macOS、Windows。大多数来源无需 API 密钥即可使用（OpenCorporates 有一个可选的免费令牌，可提高速率限制）。

改编自 MIT 许可的 ShinMegamiBoson/OpenPlanter 项目；扩展覆盖了原始项目未涉及的身份/财产/诉讼/档案/新闻来源。

<a id="when-to-use-this-skill"></a>
## 何时使用此技能

当用户提出以下请求时使用：

- “追踪资金流向” — 政府合同、游说 → 立法、制裁
- 企业尽职调查 — 谁控制着 X 公司，他们在哪里注册，谁担任董事会成员，他们提交过哪些文件
- 制裁筛查 — 实体 X 是否在 OFAC SDN、ICIJ 离岸泄露名单上
- 付费参与调查 — 有离岸关系的承包商、赢得奖项的游说客户
- 房产所有权 — 按姓名或地址查找已记录的契约/抵押贷款（纽约市；对于其他县，请引导用户到相关记录机构）
- 诉讼历史 — 查找联邦和州法院意见及 PACER 案卷
- 多来源实体解析，其中命名方式不同（LLC 后缀、缩写）
- 具有明确置信度级别的证据链构建
- “关于 X 有什么说法” — 国际新闻 (GDELT) + Wikipedia 叙述 + Wayback Machine 恢复失效 URL
不要将此技能用于：

- 通用网络调研 → 使用 `web_search` / `web_extract`
- 域名/基础设施 OSINT → 使用 `domain-intel` 技能
- 学术文献 → 使用 `arxiv` 技能
- 社交媒体个人资料发现 → 使用 `sherlock` 技能（可选）
- 美国**联邦**竞选资金 —— 这里刻意不涵盖 FEC（因为免费 DEMO_KEY 层级的 API 对临时捐款人姓名查询不可靠）。如需查询联邦捐款，请直接引导用户访问 https://www.fec.gov/data/。

<a id="workflow"></a>
## 工作流程

Agent 通过 `terminal` 工具运行脚本。 `SKILL_DIR` 是存放本 SKILL.md 的目录。

<a id="1-identify-which-sources-apply"></a>
### 1. 确定哪些数据源适用

阅读数据源 Wiki 条目以规划调研：

```
ls SKILL_DIR/references/sources/

# 联邦财务 / 监管
cat SKILL_DIR/references/sources/sec-edgar.md       # 公司申报文件
cat SKILL_DIR/references/sources/usaspending.md     # 联邦合同
cat SKILL_DIR/references/sources/senate-ld.md       # 游说
cat SKILL_DIR/references/sources/ofac-sdn.md        # 制裁名单
cat SKILL_DIR/references/sources/icij-offshore.md   # 离岸泄密

# 身份 / 财产 / 诉讼 / 归档 / 新闻
cat SKILL_DIR/references/sources/nyc-acris.md       # 纽约市产权记录
cat SKILL_DIR/references/sources/opencorporates.md  # 全球公司注册信息
cat SKILL_DIR/references/sources/courtlistener.md   # 法院记录（联邦 + 州）
cat SKILL_DIR/references/sources/wayback.md         # Wayback Machine 存档
cat SKILL_DIR/references/sources/wikipedia.md       # Wikipedia + Wikidata
cat SKILL_DIR/references/sources/gdelt.md           # 全球新闻监控
```

每个条目遵循一个 9 节模板：摘要、访问、模式、覆盖范围、交叉引用键、数据质量、获取方式、法律声明、参考文献。

**交叉引用潜力** 部分映射了数据源之间的连接键 —— 先阅读这些内容，以便选择合适的数据对。

<a id="2-acquire-data"></a>
### 2. 获取数据

每个数据源在 `SKILL_DIR/scripts/` 下都有一个仅依赖标准库的获取脚本：

**联邦财务 / 监管**

```bash
# SEC EDGAR 申报文件（公司披露）
python3 SKILL_DIR/scripts/fetch_sec_edgar.py --cik 0000320193 \
    --types 10-K,10-Q --out data/edgar_filings.csv

# USAspending 联邦合同
python3 SKILL_DIR/scripts/fetch_usaspending.py --recipient "EXAMPLE CORP" \
    --fy 2024 --out data/contracts.csv

# Senate LD-1 / LD-2 游说披露
python3 SKILL_DIR/scripts/fetch_senate_ld.py --client "EXAMPLE CORP" \
    --year 2024 --out data/lobbying.csv

# OFAC SDN 制裁名单（完整快照）
python3 SKILL_DIR/scripts/fetch_ofac_sdn.py --out data/ofac_sdn.csv

# ICIJ 离岸泄密 —— 首次使用时下载约 70 MB 的批量 CSV 文件，
# 然后在本地搜索。缓存保留 30 天，位于
# $HERMES_OSINT_CACHE/icij/（默认：~/.cache/hermes-osint/icij/）。
python3 SKILL_DIR/scripts/fetch_icij_offshore.py --entity "EXAMPLE CORP" \
    --out data/icij.csv
```

**身份 / 财产 / 诉讼 / 归档 / 新闻**

```bash
# 纽约市产权记录（地契、抵押、留置权）—— 通过 Socrata 访问 ACRIS
python3 SKILL_DIR/scripts/fetch_nyc_acris.py --name "SMITH, JOHN" \
    --out data/acris.csv
python3 SKILL_DIR/scripts/fetch_nyc_acris.py --address "571 HUDSON" \
    --out data/acris_addr.csv

# OpenCorporates —— 130+ 司法管辖区的公司注册信息
# （需要免费令牌；设置 OPENCORPORATES_API_TOKEN 或通过 --token 传入）
python3 SKILL_DIR/scripts/fetch_opencorporates.py --query "Example Corp" \
    --jurisdiction us_ny --out data/opencorporates.csv

# CourtListener —— 联邦 + 州法院意见、PACER 案卷
python3 SKILL_DIR/scripts/fetch_courtlistener.py --query "Smith v. Example Corp" \
    --type opinions --out data/courts.csv

# Wayback Machine —— 历史网页捕获
python3 SKILL_DIR/scripts/fetch_wayback.py --url "example.com" \
    --match host --collapse digest --out data/wayback.csv

# Wikipedia + Wikidata —— 叙事性传记 + 结构化事实
# 设置 HERMES_OSINT_UA=your-app/1.0 (your@email) 以标识自己
python3 SKILL_DIR/scripts/fetch_wikipedia.py --query "Bill Gates" \
    --out data/wp.csv

# GDELT —— 全球新闻，支持 100+ 语言，约 2015 年至今
python3 SKILL_DIR/scripts/fetch_gdelt.py --query '"Example Corp"' \
    --timespan 1y --out data/gdelt.csv
```
所有输出均为带标题行的标准化 CSV。脚本可幂等地重新运行。

如果某个私有个体不会出现在某个数据源中（例如，非上市公司人员不会出现在 SEC EDGAR 中，非联邦承包商人员不会出现在 USAspending 中，非游说客户不会出现在 Senate LDA 中），脚本会返回 0 行并给出明确警告，而不是静默地写入一个空 CSV。特别是 EDGAR 会在公司名称解析器匹配到个人 Form 3/4/5 申报人而非企业注册人时给出标记。

每个数据源的维基条目中都注明了速率限制说明。默认的获取器会在分页请求之间礼貌地等待。**API 密钥可提高支持此功能的数据源的速率限制**（`SEC_USER_AGENT`、`SENATE_LDA_TOKEN`、`OPENCORPORATES_API_TOKEN`、`COURTLISTENER_TOKEN`）。所有脚本会立即暴露 429 响应并附带上游的配额消息，以便用户知道需要放慢速度或提供密钥。

<a id="3-resolve-entities-across-sources"></a>
### 3. 跨数据源解析实体

规范化名称并在两个 CSV 文件之间查找匹配项：

```bash
# 将游说客户（Senate LDA）与合同接收方（USAspending）进行匹配
python3 SKILL_DIR/scripts/entity_resolution.py \
    --left  data/lobbying.csv   --left-name-col  client_name \
    --right data/contracts.csv  --right-name-col recipient_name \
    --out data/cross_links.csv
```

三个匹配级别，具有明确的置信度：

| 级别 | 方法 | 置信度 |
|------|--------|------------|
| `exact` | 去除后缀/标点后规范化字符串相等 | 高 |
| `fuzzy` | 排序后的令牌相等（词袋匹配） | 中 |
| `token_overlap` | 令牌重叠 ≥60%，共享令牌 ≥2 个，令牌长度 ≥4 个字符 | 低 |

输出 `cross_links.csv` 列：`match_type, confidence, left_name, right_name, left_normalized, right_normalized, left_row, right_row`。

<a id="4-statistical-timing-correlation-optional"></a>
### 4. 统计时间相关性（可选）

使用置换检验测试两个时间序列是否在可疑的紧密时间范围内聚集——例如，游说申报接近合同授予日期：

```bash
python3 SKILL_DIR/scripts/timing_analysis.py \
    --donations data/lobbying.csv --donation-date-col filing_date \
        --donation-amount-col income --donation-donor-col client_name \
        --donation-recipient-col registrant_name \
    --contracts data/contracts.csv --contract-date-col award_date \
        --contract-vendor-col recipient_name \
    --cross-links data/cross_links.csv \
    --permutations 1000 \
    --out data/timing.json
```

脚本的列标记是有意设计的通用名称——原始工具是为捐赠 vs 奖励编写的，但它适用于通过交叉链接连接的任意（事件、收款方）时间序列。零假设：事件时间与奖励日期无关。单尾 p 值 = 平均最近奖励距离 ≤ 观测值的置换比例。每个（支付方、供应商）对至少需要 3 个事件才能运行检验。

<a id="5-build-the-findings-json-evidence-chain"></a>
### 5. 构建发现结果 JSON（证据链）

```bash
python3 SKILL_DIR/scripts/build_findings.py \
    --cross-links data/cross_links.csv \
    --timing data/timing.json \
    --out data/findings.json
```
每个发现项包含 `id, title, severity, confidence, summary, evidence[], sources[]`。
每条证据项都指向来源 CSV 中的特定行。用户（或后续 Agent）可以针对其来源验证每一项声明。

<a id="confidence-and-evidence-discipline"></a>
## 置信度与证据纪律

这是本技能的核心规则。请告知用户：

- 每项声明必须可追溯到某条记录。不允许无依据的断言。
- 置信度等级随声明一起传递。`match_type=fuzzy` 表示“可能”，而非“已确认”。
- 实体解析生成的是候选信息，而非结论。`ACME LLC` 与 `Acme Holdings Group` 之间的 `fuzzy` 匹配是一条线索，而非事实。
- 统计显著性 ≠ 不当行为。p < 0.05 只说明在零假设下该时间模式不太可能出现，并不证明存在腐败。
- 此处所有数据来源均为公开记录。它们仍可能包含不准确信息、过时数据或经过编辑（GDPR、密封记录）。

<a id="adding-a-new-data-source"></a>
## 添加新的数据源

使用模板：

```bash
cp SKILL_DIR/templates/source-template.md \
    SKILL_DIR/references/sources/<your-source>.md
```

填写全部 9 个章节。在 `scripts/` 中编写一个 `fetch_&lt;source&gt;.py` 脚本，该脚本仅使用标准库，并输出标准化的 CSV。同时更新上方“使用时机”部分的来源列表。

<a id="tools-and-their-limits"></a>
## 工具及其限制

- `entity_resolution.py` **不**使用外部模糊匹配库（无 rapidfuzz、无 jellyfish）。Token-bag 匹配是此处能做的上限。如果需要 Levenshtein、音译或语音匹配，请另行 pip 安装。
- `timing_analysis.py` 使用 Python 的 `random` 模块进行排列。为保证可重复性，请传入 `--seed N`。
- `fetch_*.py` 脚本使用 `urllib.request` 并遵循 `Retry-After`。大量频繁使用仍可能违反服务条款——请先阅读每个来源的法律条款。

<a id="legal-note"></a>
## 法律说明

所有第一阶段来源均为公开记录。在其各自访问条款（FOIA、公共记录法、ICIJ 明确发布、OFAC 公开数据）允许下可以进行批量获取。但请注意：

- 某些来源会进行严格的频率限制。请尊重其头部信息。
- 某些来源会编辑注册人信息（WHOIS 上的 GDPR、密封的备案文件）。
- 交叉引用公开记录以识别个人身份可能涉及伦理问题。该技能生成的是证据链，而非指控。
