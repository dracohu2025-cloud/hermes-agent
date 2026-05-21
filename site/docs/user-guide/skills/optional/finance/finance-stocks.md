---
title: "股票 — 通过雅虎获取股票报价、历史、搜索、比较、加密货币"
sidebar_label: "股票"
description: "通过雅虎获取股票报价、历史、搜索、比较、加密货币"
---

{/* 此页面由网站脚本 website/scripts/generate-skill-docs.py 根据技能目录下的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

<a id="stocks"></a>
# 股票

通过雅虎获取股票报价、历史、搜索、比较、加密货币。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/finance/stocks` 安装 |
| 路径 | `optional-skills/finance/stocks` |
| 版本 | `0.1.0` |
| 作者 | Mibay (Mibayy), Hermes Agent |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `股票`, `金融`, `市场`, `加密货币`, `投资` |
| 相关技能 | [`dcf-model`](/user-guide/skills/optional/finance/finance-dcf-model), [`comps-analysis`](/user-guide/skills/optional/finance/finance-comps-analysis), [`lbo-model`](/user-guide/skills/optional/finance/finance-lbo-model) |

<a id="reference-full-skill-md"></a>
## 参考：完整的 SKILL.md

:::info
以下是该技能被触发时 Hermes 加载的完整技能定义。这是 Agent 在技能激活时看到的指令内容。
:::

<a id="stocks-skill"></a>
# 股票技能

通过雅虎财经提供只读市场数据。五个命令：`quote`、`search`、`history`、`compare`、`crypto`。仅依赖 Python 标准库——无需 API 密钥，无需 pip 安装。雅虎的接口是非官方的，可能会限流或更改。

<a id="when-to-use"></a>
## 何时使用

- 用户询问当前股票价格（AAPL、TSLA、MSFT……）
- 用户希望通过公司名称查找股票代码
- 用户需要某个日期范围内的 OHLCV 历史或表现
- 用户希望并排比较多个股票代码
- 用户询问加密货币价格（BTC、ETH、SOL……）

<a id="prerequisites"></a>
## 前提条件

仅需 Python 3.8+ 标准库。可选：设置 `ALPHA_VANTAGE_KEY`，以便在雅虎受 crumb 保护的字段返回空值时，补充 `market_cap`、`pe_ratio` 和 52 周高低点数据。免费密钥：https://www.alphavantage.co/support/#api-key

<a id="how-to-run"></a>
## 如何运行

通过 `terminal` 工具调用。安装后：

```
SCRIPT=~/.hermes/skills/finance/stocks/scripts/stocks_client.py
python3 $SCRIPT quote AAPL
```

所有输出均为 stdout 上的 JSON——如需切片，可通过 `jq` 管道处理。

<a id="quick-reference"></a>
## 快速参考

```
python3 $SCRIPT quote AAPL
python3 $SCRIPT quote AAPL MSFT GOOGL TSLA
python3 $SCRIPT search "Tesla"
python3 $SCRIPT history NVDA --range 6mo
python3 $SCRIPT compare AAPL MSFT GOOGL
python3 $SCRIPT crypto BTC ETH SOL
```

<a id="commands"></a>
## 命令

<a id="quote-symbol-symbol2"></a>
### `quote SYMBOL [SYMBOL2 ...]`

当前价格、涨跌额、涨跌幅、成交量、52 周最高/最低。

<a id="search-query"></a>
### `search QUERY`

通过公司名称查找股票代码。返回前 5 个结果：股票代码、名称、交易所、类型。

<a id="history-symbol-range-range"></a>
### `history SYMBOL [--range RANGE]`

日线 OHLCV 及统计（最小值、最大值、平均值、总收益率）。可选范围：`1mo`、`3mo`、`6mo`、`1y`、`5y`。默认：`1mo`。

<a id="compare-symbol1-symbol2"></a>
### `compare SYMBOL1 SYMBOL2 [...]`

并排比较：价格、涨跌幅、52 周表现。

<a id="crypto-symbol-symbol2"></a>
### `crypto SYMBOL [SYMBOL2 ...]`

加密货币价格。传入 `BTC`（脚本会自动追加 `-USD`）。

<a id="pitfalls"></a>
## 注意事项

- 雅虎财经的 API 是非官方的。接口可能在没有通知的情况下更改或限流——如果请求开始失败，原因在此。
- 当雅虎的 crumb 会话尚未建立时，`quote` 命令中的 `market_cap` 和 `pe_ratio` 可能返回空值。设置 `ALPHA_VANTAGE_KEY` 可进行回填。
- 批量请求之间增加少量延迟，以避免触发限流。
- 此技能为只读——不支持下单，不集成账户。
<a id="verification"></a>
## 验证

```
python3 ~/.hermes/skills/finance/stocks/scripts/stocks_client.py quote AAPL
```

返回一个 JSON 对象，包含 `symbol: "AAPL"` 和一个数值类型的 `price` 字段。
