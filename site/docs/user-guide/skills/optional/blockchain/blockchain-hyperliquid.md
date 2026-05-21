---
title: "Hyperliquid — Hyperliquid 市场数据、账户历史、交易回顾"
sidebar_label: "Hyperliquid"
description: "Hyperliquid 市场数据、账户历史、交易回顾"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

<a id="hyperliquid"></a>
# Hyperliquid

Hyperliquid 市场数据、账户历史、交易回顾。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/blockchain/hyperliquid` 安装 |
| 路径 | `optional-skills/blockchain/hyperliquid` |
| 版本 | `0.1.0` |
| 作者 | Hugo Sequier (Hugo-SEQUIER), Hermes Agent |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `Hyperliquid`, `Blockchain`, `Crypto`, `Trading`, `Perpetuals`, `Spot`, `DeFi` |

<a id="reference-full-skill-md"></a>
## 参考：完整 SKILL.md

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

<a id="hyperliquid-skill"></a>
# Hyperliquid 技能

通过公共 `/info` 端点查询 Hyperliquid 市场和账户数据。
只读 — 无需 API 密钥，无需签名，不下单。

12 个命令：`dexs`、`markets`、`spots`、`candles`、`funding`、`l2`、`state`、
`spot-balances`、`fills`、`orders`、`review`、`export`。仅使用标准库
（`urllib`、`json`、`argparse`）。

---

<a id="when-to-use"></a>
## 何时使用

- 用户询问 Hyperliquid 永续或现货市场数据、K线、资金费率或 L2 订单簿
- 用户想查看钱包的永续仓位、现货余额、成交记录或订单
- 用户希望结合近期成交与市场背景进行交易后回顾
- 用户想查看构建者部署的永续 DEX 或 HIP-3 市场
- 用户需要标准化的 JSON 格式 K线 + 资金费率导出，用于回测准备

---

<a id="prerequisites"></a>
## 前置条件

仅使用标准库 — 无需外部包，无需 API 密钥。

脚本读取 `~/.hermes/.env` 中的两个可选默认值：

- `HYPERLIQUID_API_URL` — 默认为 `https://api.hyperliquid.xyz`。设置为
  `https://api.hyperliquid-testnet.xyz` 以使用测试网。
- `HYPERLIQUID_USER_ADDRESS` — `state`、`spot-balances`、
  `fills`、`orders` 和 `review` 的默认地址。如果未设置，请将地址作为第一个位置参数传入。

当前工作目录中的项目 `.env` 文件也会作为开发环境的后备配置被识别。

辅助脚本：`~/.hermes/skills/blockchain/hyperliquid/scripts/hyperliquid_client.py`

---

<a id="how-to-run"></a>
## 如何运行

通过 `terminal` 工具调用：

```bash
python3 ~/.hermes/skills/blockchain/hyperliquid/scripts/hyperliquid_client.py <command> [args]
```

在任何命令后添加 `--json` 以获取机器可读的输出。

---

<a id="quick-reference"></a>
## 快速参考

```bash
hyperliquid_client.py dexs
hyperliquid_client.py markets [--dex DEX] [--limit N] [--sort volume|oi|funding_abs|change_abs|name]
hyperliquid_client.py spots [--limit N]
hyperliquid_client.py candles <coin> [--interval 1h] [--hours 24] [--limit N]
hyperliquid_client.py funding <coin> [--hours 72] [--limit N]
hyperliquid_client.py l2 <coin> [--levels N]
hyperliquid_client.py state [address] [--dex DEX]
hyperliquid_client.py spot-balances [address] [--limit N]
hyperliquid_client.py fills [address] [--hours N] [--limit N] [--aggregate-by-time]
hyperliquid_client.py orders [address] [--limit N]
hyperliquid_client.py review [address] [--coin COIN] [--hours N] [--fills N]
hyperliquid_client.py export <coin> [--interval 1h] [--hours N] [--output PATH]
```
对于 `state`、`spot-balances`、`fills`、`orders` 和 `review`，当 `~/.hermes/.env` 中设置了 `HYPERLIQUID_USER_ADDRESS` 时，地址是可选的。

---

<a id="procedure"></a>
## 操作步骤

<a id="1-discover-dexs-and-markets"></a>
### 1. 发现 DEX 与市场

```bash
python3 ~/.hermes/skills/blockchain/hyperliquid/scripts/hyperliquid_client.py dexs

python3 ~/.hermes/skills/blockchain/hyperliquid/scripts/hyperliquid_client.py \
  markets --limit 15 --sort volume

python3 ~/.hermes/skills/blockchain/hyperliquid/scripts/hyperliquid_client.py \
  spots --limit 15
```

- `--dex` 只适用于永续合约端点；省略即使用第一个永续合约 DEX。
- 现货交易对可能显示为 `PURR/USDC` 或 `@107` 这样的别名。
- HIP-3 市场的币种带有 DEX 前缀，例如 `mydex:BTC`。

<a id="2-pull-historical-market-data"></a>
### 2. 拉取历史市场数据

```bash
python3 ~/.hermes/skills/blockchain/hyperliquid/scripts/hyperliquid_client.py \
  candles BTC --interval 1h --hours 72 --limit 48

python3 ~/.hermes/skills/blockchain/hyperliquid/scripts/hyperliquid_client.py \
  funding BTC --hours 168 --limit 30
```

时间范围端点会分页。对于更大的窗口，可以带上更晚的 `startTime` 重复执行，或者使用下方的 `export`。

<a id="3-inspect-live-order-book"></a>
### 3. 查看实时订单簿

```bash
python3 ~/.hermes/skills/blockchain/hyperliquid/scripts/hyperliquid_client.py \
  l2 BTC --levels 10
```

当被问及订单簿深度、短期流动性或大单的潜在市场影响时使用此命令。

<a id="4-review-an-account"></a>
### 4. 查看账户

```bash
python3 ~/.hermes/skills/blockchain/hyperliquid/scripts/hyperliquid_client.py \
  state 0xabc...

python3 ~/.hermes/skills/blockchain/hyperliquid/scripts/hyperliquid_client.py \
  spot-balances
```

`state` 返回永续合约持仓；`spot-balances` 返回现货库存。  
这些用于回答如“我的持仓如何？”、“我持有哪些资产？”、“可提现多少？”

<a id="5-review-fills-and-orders"></a>
### 5. 查看成交记录与订单

```bash
python3 ~/.hermes/skills/blockchain/hyperliquid/scripts/hyperliquid_client.py \
  fills 0xabc... --hours 72 --limit 25

python3 ~/.hermes/skills/blockchain/hyperliquid/scripts/hyperliquid_client.py \
  orders --limit 25
```

<a id="6-generate-a-trade-review"></a>
### 6. 生成交易回顾

```bash
python3 ~/.hermes/skills/blockchain/hyperliquid/scripts/hyperliquid_client.py \
  review 0xabc... --hours 72 --fills 50

python3 ~/.hermes/skills/blockchain/hyperliquid/scripts/hyperliquid_client.py \
  review --coin BTC --hours 168
```

报告已实现盈亏、手续费、胜/负次数、币种分布、每个交易永续合约的市场趋势与平均资金费率，以及启发式分析（手续费拖累、集中度、逆势亏损）。

如需更深入的交易后分析：先通过 `review` 找到问题币种或窗口 → 拉取该周期的 `fills` 和 `orders` → 拉取每个交易币种的 `candles` 和 `funding` → 将决策质量与结果质量分开评判。

<a id="7-export-a-reusable-dataset"></a>
### 7. 导出可复用的数据集

```bash
python3 ~/.hermes/skills/blockchain/hyperliquid/scripts/hyperliquid_client.py \
  export BTC --interval 1h --hours 168 --output ./btc-1h-7d.json

python3 ~/.hermes/skills/blockchain/hyperliquid/scripts/hyperliquid_client.py \
  export BTC --interval 15m --hours 72 --end-time-ms 1760000000000
```
输出 JSON 包含：Schema 版本、源元数据、精确时间窗口、标准化 K 线行、标准化资金费率行、汇总统计。使用 `--end-time-ms` 可实现可复现的时间窗口。

---

<a id="pitfalls"></a>
## 注意事项

- 公共信息接口有速率限制。大量历史查询可能返回截断的时间窗口；请使用后续的 `startTime` 值进行迭代。
- `fills --hours ...` 使用 `userFillsByTime`，该接口仅暴露最近一段滚动窗口，并非完整的归档历史。
- `historicalOrders` 仅返回近期订单，不是完整导出。
- `review` 命令基于启发式，无法仅从成交记录重建意图、订单放置质量或真实滑点。
- `export` 命令写入的是标准化数据集，而非回测引擎。你仍需要自己的滑点/成交模型。
- 现货别名（如 `@107`）是有效的标识符，即使 UI 显示了更友好的名称。
- `l2` 是时间点快照，不是时间序列。

---

<a id="verification"></a>
## 验证

```bash
python3 ~/.hermes/skills/blockchain/hyperliquid/scripts/hyperliquid_client.py \
  markets --limit 5
```

应打印按 24 小时名义成交量排名的 Hyperliquid 永续合约市场前五名。
