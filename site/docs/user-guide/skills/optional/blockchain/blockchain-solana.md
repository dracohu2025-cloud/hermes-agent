---
title: "Solana"
sidebar_label: "Solana"
description: "查询 Solana 区块链数据，附带 USD 价格——钱包余额、含价值的代币组合、交易详情、NFT、鲸鱼检测以及实时网络状态。"
---

{/* 本页由技能目录下的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而不是本页。 */}

# Solana {#solana}

查询 Solana 区块链数据，附带 USD 价格——钱包余额、含价值的代币组合、交易详情、NFT、鲸鱼检测以及实时网络状态。使用 Solana RPC + CoinGecko，无需 API 密钥。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 可选——通过 `hermes skills install official/blockchain/solana` 安装 |
| 路径 | `optional-skills/blockchain/solana` |
| 版本 | `0.2.0` |
| 作者 | Deniz Alagoz (gizdusum)，由 Hermes Agent 增强 |
| 许可协议 | MIT |
| 标签 | `Solana`、`Blockchain`、`Crypto`、`Web3`、`RPC`、`DeFi`、`NFT` |

## 参考：完整的 SKILL.md {#reference-full-skill-md}

:::info
以下是 Hermes 在该技能被触发时加载的完整技能定义。技能激活时，代理会将其作为指令来执行。
:::

# Solana 区块链技能 {#solana-blockchain-skill}

查询 Solana 链上数据，并通过 CoinGecko 附带 USD 价格。
共 8 条命令：钱包组合、代币信息、交易、活动记录、NFT、
鲸鱼检测、网络状态以及价格查询。

无需 API 密钥。仅使用 Python 标准库（urllib、json、argparse）。

---

## 使用时机 {#when-to-use}

- 用户询问 Solana 钱包余额、代币持仓或组合价值
- 用户想通过签名查看特定交易
- 用户想要 SPL 代币的元数据、价格、供应量或前几大持有者
- 用户想要某个地址的近期交易历史
- 用户想要钱包拥有的 NFT
- 用户想要寻找大额 SOL 转账（鲸鱼检测）
- 用户想要 Solana 网络健康状况、TPS、纪元或 SOL 价格
- 用户询问“BONK/JUP/SOL 的价格是多少？”

---

## 前提条件 {#prerequisites}

辅助脚本仅使用 Python 标准库（urllib、json、argparse）。
无需外部包。

价格数据来自 CoinGecko 的免费 API（无需密钥，速率限制
约为 10-30 次/分钟）。如需更快查询，可使用 `--no-prices` 标志。

---

## 快速参考 {#quick-reference}

RPC 端点（默认）：https://api.mainnet-beta.solana.com
覆盖方式：export SOLANA_RPC_URL=https://your-private-rpc.com

辅助脚本路径：~/.hermes/skills/blockchain/solana/scripts/solana_client.py

```
python3 solana_client.py wallet   <地址> [--limit N] [--all] [--no-prices]
python3 solana_client.py tx       <签名>
python3 solana_client.py token    <铸币地址>
python3 solana_client.py activity <地址> [--limit N]
python3 solana_client.py nft      <地址>
python3 solana_client.py whales   [--min-sol N]
python3 solana_client.py stats
python3 solana_client.py price    <铸币地址或符号>
```

---

## 执行步骤 {#procedure}

### 0. 环境检查 {#0-setup-check}

```bash
python3 --version

# 可选：设置私有 RPC 以获得更好的速率限制
export SOLANA_RPC_URL="https://api.mainnet-beta.solana.com"

# 确认连接正常
python3 ~/.hermes/skills/blockchain/solana/scripts/solana_client.py stats
```

### 1. 钱包组合 {#1-wallet-portfolio}

获取 SOL 余额、带有 USD 价值的 SPL 代币持仓、NFT 数量以及
组合总值。代币按价值排序，过滤灰尘代币，已知代币会标记名称（BONK、JUP、USDC 等）。
```bash
python3 ~/.hermes/skills/blockchain/solana/scripts/solana_client.py \
  wallet 9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM
```

标志：
- `--limit N` — 显示前 N 个代币（默认：20）
- `--all` — 显示所有代币，无灰尘过滤，无限制
- `--no-prices` — 跳过 CoinGecko 价格查询（更快，仅使用 RPC）

输出包括：SOL 余额 + 美元价值，按价值排序的代币列表及价格，灰尘数量，NFT 摘要，总持仓美元价值。

### 2. 交易详情 {#2-transaction-details}

通过 base58 签名检查完整交易。显示 SOL 和 USD 的余额变化。

```bash
python3 ~/.hermes/skills/blockchain/solana/scripts/solana_client.py \
  tx 5j7s8K...your_signature_here
```

输出：插槽、时间戳、费用、状态、余额变化（SOL + USD）、程序调用。

### 3. 代币信息 {#3-token-info}

获取 SPL 代币元数据、当前价格、市值、供应量、小数位数、铸币/冻结权限以及前 5 大持有者。

```bash
python3 ~/.hermes/skills/blockchain/solana/scripts/solana_client.py \
  token DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263
```

输出：名称、符号、小数位数、供应量、价格、市值、前 5 大持有者及其占比。

### 4. 近期活动 {#4-recent-activity}

列出某个地址的近期交易（默认：最近 10 笔，最多：25 笔）。

```bash
python3 ~/.hermes/skills/blockchain/solana/scripts/solana_client.py \
  activity 9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM --limit 25
```

### 5. NFT 持仓 {#5-nft-portfolio}

列出钱包拥有的 NFT（启发式：amount=1、decimals=0 的 SPL 代币）。

```bash
python3 ~/.hermes/skills/blockchain/solana/scripts/solana_client.py \
  nft 9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM
```

注意：压缩 NFT（cNFT）无法通过此启发式检测到。

### 6. 巨鲸检测器 {#6-whale-detector}

扫描最新区块中带有美元价值的大额 SOL 转账。

```bash
python3 ~/.hermes/skills/blockchain/solana/scripts/solana_client.py \
  whales --min-sol 500
```

注意：仅扫描最新区块——即时快照，非历史数据。

### 7. 网络状态 {#7-network-stats}

Solana 网络实时健康状态：当前插槽、纪元、TPS、供应量、验证者版本、SOL 价格和市值。

```bash
python3 ~/.hermes/skills/blockchain/solana/scripts/solana_client.py stats
```

### 8. 价格查询 {#8-price-lookup}

通过铸币地址或已知符号快速查询任意代币价格。

```bash
python3 ~/.hermes/skills/blockchain/solana/scripts/solana_client.py price BONK
python3 ~/.hermes/skills/blockchain/solana/scripts/solana_client.py price JUP
python3 ~/.hermes/skills/blockchain/solana/scripts/solana_client.py price SOL
python3 ~/.hermes/skills/blockchain/solana/scripts/solana_client.py price DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263
```

已知符号：SOL、USDC、USDT、BONK、JUP、WETH、JTO、mSOL、stSOL、PYTH、HNT、RNDR、WEN、W、TNSR、DRIFT、bSOL、JLP、WIF、MEW、BOME、PENGU。

---

## 注意事项 {#pitfalls}

- **CoinGecko 速率限制** — 免费层每分钟约 10-30 次请求。价格查询每个代币消耗 1 次请求。持有大量代币的钱包可能无法获取所有代币的价格。使用 `--no-prices` 可加快速度。
- **公共 RPC 速率限制** — Solana 主网公共 RPC 对请求有限制。生产环境请将 `SOLANA_RPC_URL` 设置为私有端点（Helius、QuickNode、Triton）。
- **NFT 检测为启发式** — 条件为 amount=1 且 decimals=0。压缩 NFT（cNFT）和 Token-2022 NFT 不会出现。
- **巨鲸检测器仅扫描最新区块** — 非历史数据。结果因查询时刻而异。
- **交易历史** — 公共 RPC 保留约 2 天。较早的交易可能无法获取。
- **代币名称** — 约 25 种知名代币会显示名称，其他代币显示缩写铸币地址。使用 `token` 命令获取完整信息。
- **429 重试** — 遇到速率限制错误时，RPC 和 CoinGecko 调用最多重试 2 次，采用指数退避策略。
---

## 验证 {#verification}

```bash
# 应输出当前 Solana 的 slot、TPS 和 SOL 价格
python3 ~/.hermes/skills/blockchain/solana/scripts/solana_client.py stats
```
