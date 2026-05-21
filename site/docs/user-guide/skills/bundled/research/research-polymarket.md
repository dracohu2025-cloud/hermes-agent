---
title: "Polymarket — 查询 Polymarket：市场、价格、订单簿、历史"
sidebar_label: "Polymarket"
description: "查询 Polymarket：市场、价格、订单簿、历史"
---

{/* 此页面由网站/脚本/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非本页面。 */}

<a id="polymarket"></a>
# Polymarket

查询 Polymarket：市场、价格、订单簿、历史。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/research/polymarket` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent + Teknium |
| 平台 | linux, macos, windows |

<a id="reference-full-skill-md"></a>
## 参考：完整的 SKILL.md

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。Agent 在该技能激活时将把这些内容视为指令。
:::

<a id="polymarket-prediction-market-data"></a>
# Polymarket — 预测市场数据

使用 Polymarket 公开的 REST API 查询其预测市场数据。
所有端点均为只读，无需任何身份验证。

请参阅 `references/api-endpoints.md`，查看包含 curl 示例的完整端点参考。

<a id="when-to-use"></a>
## 何时使用

- 用户询问预测市场、投注赔率或事件概率
- 用户想知道“某事件发生的赔率是多少？”
- 用户特别询问 Polymarket
- 用户想要市场价格、订单簿数据或价格历史
- 用户要求监控或追踪预测市场的动态

<a id="key-concepts"></a>
## 关键概念

- **事件**包含一个或多个**市场**（一对多关系）
- **市场**是二元结果，Yes/No 价格在 0.00 到 1.00 之间
- 价格即概率：价格 0.65 意味着市场认为概率为 65%
- `outcomePrices` 字段：JSON 编码的数组，例如 `["0.80", "0.20"]`
- `clobTokenIds` 字段：两个代币 ID [Yes, No] 的 JSON 编码数组，用于价格/订单簿查询
- `conditionId` 字段：十六进制字符串，用于价格历史查询
- 交易量以 USDC（美元）计

<a id="three-public-apis"></a>
## 三个公开 API

1. **Gamma API**：位于 `gamma-api.polymarket.com` — 发现、搜索、浏览
2. **CLOB API**：位于 `clob.polymarket.com` — 实时价格、订单簿、历史
3. **数据 API**：位于 `data-api.polymarket.com` — 交易、未平仓合约

<a id="typical-workflow"></a>
## 典型工作流程

当用户询问预测市场赔率时：

1. **搜索**：使用 Gamma API 的 public-search 端点，传入用户的查询
2. **解析**：解析响应 — 提取事件及其嵌套的市场
3. **展示**：展示市场问题、当前价格（百分比）和交易量
4. **深入**：如果用户要求，使用 clobTokenIds 获取订单簿，使用 conditionId 获取历史

<a id="presenting-results"></a>
## 展示结果

将价格格式化为百分比以提升可读性：
- outcomePrices `["0.652", "0.348"]` 变为 “Yes: 65.2%, No: 34.8%”
- 始终显示市场问题和概率
- 尽可能包含交易量

示例：`“某事件会发生吗？” — 65.2% Yes（120万美元交易量）`

<a id="parsing-double-encoded-fields"></a>
## 解析双重编码字段

Gamma API 将 `outcomePrices`、`outcomes` 和 `clobTokenIds` 作为 JSON 字符串返回在 JSON 响应中（双重编码）。使用 Python 处理时，通过 `json.loads(market['outcomePrices'])` 解析以获取实际的数组。

<a id="rate-limits"></a>
## 速率限制

非常宽松 — 正常使用不太可能触发：
- Gamma：每 10 秒 4,000 次请求（通用）
- CLOB：每 10 秒 9,000 次请求（通用）
- 数据：每 10 秒 1,000 次请求（通用）
<a id="limitations"></a>
## 限制

- 此技能为只读——不支持下单交易
- 交易需要基于钱包的加密认证（EIP-712 签名）
- 部分新市场可能没有价格历史记录
- 地理限制适用于交易，但只读数据在全球范围内均可访问
