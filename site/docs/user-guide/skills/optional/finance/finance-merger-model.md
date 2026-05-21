---
title: "并购模型 —— 在 Excel 中构建增值/稀释（并购）模型 —— 形式损益表、协同效应、融资组合、每股收益影响"
sidebar_label: "并购模型"
description: "在 Excel 中构建增值/稀释（并购）模型 —— 形式损益表、协同效应、融资组合、每股收益影响"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 从技能的 SKILL.md 自动生成。编辑源文件 SKILL.md，而不是此页面。 */}

<a id="merger-model"></a>
# 并购模型

在 Excel 中构建增值/稀释（并购）模型 —— 形式损益表、协同效应、融资组合、每股收益影响。与 excel-author 技能配合使用。用于并购推介、董事会材料或交易评估。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 可选 —— 通过 `hermes skills install official/finance/merger-model` 安装 |
| 路径 | `optional-skills/finance/merger-model` |
| 版本 | `1.0.0` |
| 作者 | Anthropic（由 Nous Research 改编） |
| 许可证 | Apache-2.0 |
| 平台 | linux, macos, windows |
| 标签 | `finance`, `m-and-a`, `merger`, `accretion-dilution`, `excel`, `openpyxl`, `modeling`, `investment-banking` |
| 相关技能 | [`excel-author`](/user-guide/skills/optional/finance/finance-excel-author), [`pptx-author`](/user-guide/skills/optional/finance/finance-pptx-author), [`dcf-model`](/user-guide/skills/optional/finance/finance-dcf-model), [`3-statement-model`](/user-guide/skills/optional/finance/finance-3-statement-model) |

<a id="reference-full-skill-md"></a>
## 参考：完整 SKILL.md

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是该技能激活时 Agent 看到的指令。
:::

<a id="environment"></a>
## 环境

此技能假设**使用 headless openpyxl** —— 你将生成一个 .xlsx 文件保存在磁盘上。
遵循 `excel-author` 技能的约定，包括单元格颜色、公式、命名区域和敏感性表格。
交付前重新计算：`python /path/to/excel-author/scripts/recalc.py ./out/model.xlsx`。

# 并购模型

为并购交易构建增值/稀释分析。模型包括形式每股收益影响、协同效应敏感性以及购买价格分配。在评估潜在收购、为推介准备并购后果分析或就交易条款提供建议时使用。

<a id="workflow"></a>
## 工作流

<a id="step-1-gather-inputs"></a>
### 第一步：收集输入项

**收购方：**
- 公司名称、当前股价、流通股数
- 过去十二个月（LTM）和未来十二个月（NTM）每股收益（通用会计准则和调整后）
- 市盈率
- 税前债务成本、税率
- 资产负债表上的现金、现有债务

**目标公司：**
- 公司名称、当前股价、流通股数（如果公开）
- 过去十二个月（LTM）和未来十二个月（NTM）每股收益或净利润
- 企业价值或股权价值

**交易条款：**
- 每股收购报价（或相对于当前价格的溢价）
- 对价组合：现金占比 vs. 股票占比
- 为支付现金部分而新筹集的债务
- 预期协同效应（收入和成本）及其分阶段实现时间表
- 交易费用和融资成本
- 预期完成日期

<a id="step-2-purchase-price-analysis"></a>
### 第二步：购买价格分析

| 项目 | 价值 |
|------|------|
| 每股收购报价 | |
| 相对于当前价格的溢价 | |
| 股权价值 | |
| 加：假设的净债务 | |
| 企业价值 | |
| 隐含企业价值/息税折旧摊销前利润 | |
| 隐含市盈率 | |

<a id="step-3-sources-uses"></a>
### 第三步：资金来源与用途

| 资金来源 | 金额 | 资金用途 | 金额 |
|---------|------|--------|------|
| 新债务 | | 股权收购对价 | |
| 现有现金 | | 目标公司债务再融资 | |
| 新发行股权 | | 交易费用 | |
| | | 融资费用 | |
| **合计** | | **合计** | |
<a id="step-4-pro-forma-eps-accretion-dilution"></a>
### 第四步：模拟每股收益（增值/稀释）

逐年计算（第1-3年）：

| | 独立 | 模拟 | 增值/(稀释) |
|---|-----------|-----------|---------------------|
| 收购方净利润 | | | |
| 目标公司净利润 | | | |
| 协同效应（税后） | | | |
| 现金放弃的利息（税后） | | | |
| 新债务利息（税后） | | | |
| 无形资产摊销（税后） | | | |
| 模拟净利润 | | | |
| 模拟股份数 | | | |
| **模拟每股收益** | | | |
| **增值 / (稀释) %** | | | |

<a id="step-5-sensitivity-analysis"></a>
### 第五步：敏感性分析

**增值/稀释 vs. 协同效应与收购溢价：**

| | 0百万美元协同 | 25百万美元协同 | 50百万美元协同 | 75百万美元协同 | 100百万美元协同 |
|---|---------|----------|----------|----------|-----------|
| 溢价15% | | | | | |
| 溢价20% | | | | | |
| 溢价25% | | | | | |
| 溢价30% | | | | | |

**增值/稀释 vs. 现金/股票支付比例：**

| | 100%现金 | 75/25 | 50/50 | 25/75 | 100%股票 |
|---|-----------|-------|-------|-------|------------|
| 第1年 | | | | | |
| 第2年 | | | | | |

<a id="step-6-breakeven-synergies"></a>
### 第六步：盈亏平衡协同效应

计算交易在第1年实现每股收益中性所需的最低协同效应。

<a id="step-7-output"></a>
### 第七步：输出

- Excel工作簿，包含：
  - 假设参数页
  - 资金来源与用途
  - 模拟利润表
  - 增值/稀释汇总
  - 敏感性分析表
  - 盈亏平衡分析
- 用于推介手册的一页合并后果摘要

<a id="important-notes"></a>
## 重要说明

- 在相关情况下始终同时展示GAAP和调整后（现金）每股收益
- 股票交易：使用收购方当前股价计算换股比例，注意新股带来的稀释
- 包含购买价格分配——商誉和无形资产摊销对GAAP每股收益有影响
- 协同效应的逐步实现至关重要——第1年通常仅为稳定期协同效应的25-50%
- 不要忘记已使用现金放弃的利息收入以及新债务产生的利息支出
- 协同效应和利息调整的税率应与收购方的边际税率一致

<a id="data-sources-mcp-first-web-fallback"></a>
## 数据来源 — 优先使用MCP，备用网页搜索

下文许多段落提到“使用标准普尔Kensho MCP / Daloopa MCP / FactSet MCP”。这些是源自原Cowork插件环境的商业金融数据MCP。在Hermes中：

- **如果你已配置任何结构化金融数据MCP**（Hermes支持MCP — 参见 `native-mcp` 技能），请优先将其用于当期可比交易、先例交易和文件归档。
- **否则**，回退至：
  - 针对美国证券交易委员会EDGAR（`https://www.sec.gov/cgi-bin/browse-edgar`）使用 `web_search` / `web_extract` 获取美国归档文件
  - 公司投资者关系页面获取新闻稿、财报演示稿
  - 使用 `browser_navigate` 访问交互式数据门户
  - 用户提供的数据（当上下文中没有时明确询问）
- **切勿编造**。如果某个倍数、先例或文件编号无法获取，则将该单元格标记为 `[UNSOURCED]` 并告知用户。

<a id="attribution"></a>
## 署名

本技能改编自Anthropic的金融服务插件包（Apache-2.0）。已移除Office-JS / Cowork实时Excel路径；此版本通过 `excel-author` 技能的规范将目标定为无头openpyxl。原文地址：https://github.com/anthropics/financial-services
