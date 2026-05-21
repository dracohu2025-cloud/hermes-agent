---
title: "Solana"
sidebar_label: "Solana"
description: "通过 USD 计价查询 Solana 区块链数据——钱包余额、带估值的代币持仓、交易详情、NFT、巨鲸监控和实时网络状态。"
---

{/* 此页面由技能目录下的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

<a id="solana"></a>
# Solana

通过 USD 计价查询 Solana 区块链数据——钱包余额、带估值的代币持仓、交易详情、NFT、巨鲸监控和实时网络状态。使用 Solana RPC + CoinGecko，无需 API 密钥。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 可选——使用 `hermes skills install official/blockchain/solana` 安装 |
| 路径 | `optional-skills/blockchain/solana` |
| 版本 | `0.2.0` |
| 作者 | Deniz Alagoz (gizdusum)，由 Hermes Agent 增强 |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `Solana`，`Blockchain`，`Crypto`，`Web3`，`RPC`，`DeFi`，`NFT` |

<a id="reference-full-skill-md"></a>
## 参考：完整 SKILL.md

:::info
以下是在该技能被触发时 Hermes 加载的完整技能定义。此即技能处于激活状态时 Agent 看到的指令。
:::

<a id="solana-blockchain-skill"></a>
# Solana 区块链技能

通过 CoinGecko 查询带有 USD 估价的 Solana 链上数据。
8 条命令：钱包持仓、代币信息、交易详情、活动记录、NFT、
巨鲸发现、网络状态和价格查询。

无需 API 密钥。仅使用 Python 标准库（urllib, json, argparse）。

---

<a id="when-to-use"></a>
## 使用时机

- 用户询问 Solana 钱包余额、代币持有量或持仓价值
- 用户想通过交易签名查看特定交易详情
- 用户想获取 SPL 代币的元数据、价格、供应量或顶级持有者
- 用户想获取某个地址的近期交易历史
- 用户想获取钱包拥有的 NFT
- 用户想查找大额 SOL 转账（巨鲸监控）
- 用户想了解 Solana 网络健康状态、TPS、纪元或 SOL 价格
- 用户询问 "BONK/JUP/SOL 的价格是多少"

---

<a id="prerequisites"></a>
## 前提条件

辅助脚本仅使用 Python 标准库（urllib, json, argparse）。
无需外部包。

价格数据来自 CoinGecko 的免费 API（无需密钥，请求频率约 10-30 次/分钟）。如需更快查询，请使用 `--no-prices` 参数。

---

<a id="quick-reference"></a>
## 快速参考

RPC 端点（默认）：https://api.mainnet-beta.solana.com
覆盖：export SOLANA_RPC_URL=https://your-private-rpc.com

辅助脚本路径：~/.hermes/skills/blockchain/solana/scripts/solana_client.py

```
python3 solana_client.py wallet   <address> [--limit N] [--all] [--no-prices]
python3 solana_client.py tx       <signature>
python3 solana_client.py token    <mint_address>
python3 solana_client.py activity <address> [--limit N]
python3 solana_client.py nft      <address>
python3 solana_client.py whales   [--min-sol N]
python3 solana_client.py stats
python3 solana_client.py price    <mint_or_symbol>
```

---

<a id="procedure"></a>
## 操作步骤

<a id="0-setup-check"></a>
### 0. 环境检查

```bash
python3 --version

# 可选：设置私有 RPC 以获得更好的请求频率
export SOLANA_RPC_URL="https://api.mainnet-beta.solana.com"

# 确认连接正常
python3 ~/.hermes/skills/blockchain/solana/scripts/solana_client.py stats
```

<a id="1-wallet-portfolio"></a>
### 1. 钱包持仓

获取 SOL 余额、SPL 代币持有量（含 USD 估值）、NFT 数量及
持仓总价值。代币按价值排序，过滤掉小额粉尘，已知代币
标注名称（BONK、JUP、USDC 等）。
```bash
python3 ~/.hermes/skills/blockchain/solana/scripts/solana_client.py \
  wallet 9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM
```

标志：
- `--limit N` — 显示前 N 个代币（默认：20）
- `--all` — 显示所有代币，无灰尘过滤，无限制
- `--no-prices` — 跳过 CoinGecko 价格查询（更快，仅 RPC）

输出包括：SOL 余额 + 美元价值、按价值排序的代币列表及价格、灰尘代币数量、NFT 汇总、总持仓组合的美元价值。

<a id="2-transaction-details"></a>
### 2. 交易详情

通过 base58 签名检查完整交易。显示 SOL 和 USD 的余额变化。

```bash
python3 ~/.hermes/skills/blockchain/solana/scripts/solana_client.py \
  tx 5j7s8K...your_signature_here
```

输出：slot、时间戳、手续费、状态、余额变化（SOL + USD）、程序调用。

<a id="3-token-info"></a>
### 3. 代币信息

获取 SPL 代币元数据、当前价格、市值、供应量、小数位数、铸币/冻结权限以及前 5 大持有者。

```bash
python3 ~/.hermes/skills/blockchain/solana/scripts/solana_client.py \
  token DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263
```

输出：名称、符号、小数位数、供应量、价格、市值、前 5 大持有者及其占比。

<a id="4-recent-activity"></a>
### 4. 近期活动

列出某个地址的近期交易（默认：最近 10 笔，最大：25 笔）。

```bash
python3 ~/.hermes/skills/blockchain/solana/scripts/solana_client.py \
  activity 9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM --limit 25
```

<a id="5-nft-portfolio"></a>
### 5. NFT 持仓组合

列出钱包持有的 NFT（启发式规则：amount=1、decimals=0 的 SPL 代币）。

```bash
python3 ~/.hermes/skills/blockchain/solana/scripts/solana_client.py \
  nft 9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM
```

注意：压缩 NFT（cNFT）无法通过此启发式规则检测。

<a id="6-whale-detector"></a>
### 6. 巨鲸检测器

扫描最新区块中带有美元价值的大额 SOL 转账。

```bash
python3 ~/.hermes/skills/blockchain/solana/scripts/solana_client.py \
  whales --min-sol 500
```

注意：仅扫描最新区块——是某个时间点的快照，非历史数据。

<a id="7-network-stats"></a>
### 7. 网络状态

Solana 网络实时状态：当前 slot、epoch、TPS、供应量、验证器版本、SOL 价格和市值。

```bash
python3 ~/.hermes/skills/blockchain/solana/scripts/solana_client.py stats
```

<a id="8-price-lookup"></a>
### 8. 价格查询

通过铸币地址或已知符号快速查询任意代币价格。

```bash
python3 ~/.hermes/skills/blockchain/solana/scripts/solana_client.py price BONK
python3 ~/.hermes/skills/blockchain/solana/scripts/solana_client.py price JUP
python3 ~/.hermes/skills/blockchain/solana/scripts/solana_client.py price SOL
python3 ~/.hermes/skills/blockchain/solana/scripts/solana_client.py price DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263
```

已知符号：SOL、USDC、USDT、BONK、JUP、WETH、JTO、mSOL、stSOL、PYTH、HNT、RNDR、WEN、W、TNSR、DRIFT、bSOL、JLP、WIF、MEW、BOME、PENGU。

---

<a id="pitfalls"></a>
## 注意事项

- **CoinGecko 请求频率限制**——免费版每分钟约 10-30 次请求。价格查询每个代币消耗一次请求。含多个代币的钱包可能无法获取全部价格。使用 `--no-prices` 可加快速度。
- **公共 RPC 请求频率限制**——Solana 主网公共 RPC 会限制请求数。生产环境请将 `SOLANA_RPC_URL` 设为私有端点（Helius、QuickNode、Triton）。
- **NFT 检测基于启发式规则**——amount=1 且 decimals=0。压缩 NFT（cNFT）和 Token-2022 NFT 不会被识别。
- **巨鲸检测器仅扫描最新区块**——非历史数据。查询结果随查询时刻变化。
- **交易历史**——公共 RPC 保留约 2 天，更早的交易可能不可用。
- **代币名称**——约 25 个知名代币会显示名称，其余代币显示缩写的铸币地址。使用 `token` 命令可获取完整信息。
- **429 错误重试**——遇到限频错误时，RPC 和 CoinGecko 调用最多重试 2 次，采用指数退避策略。
---

<a id="verification"></a>
## 验证

```bash
# 应打印当前 Solana 插槽、TPS 和 SOL 价格
python3 ~/.hermes/skills/blockchain/solana/scripts/solana_client.py stats
```
