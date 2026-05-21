---
title: "Evm — 只读EVM客户端：钱包、代币、Gas，覆盖8条链"
sidebar_label: "Evm"
description: "只读EVM客户端：钱包、代币、Gas，覆盖8条链"
---

{/* 此页面由技能目录下的 SKILL.md 自动生成，生成脚本为 website/scripts/generate-skill-docs.py。请编辑源文件 SKILL.md，而非此页面。 */}

<a id="evm"></a>
# Evm

只读EVM客户端：钱包、代币、Gas，覆盖8条链。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/blockchain/evm` 安装 |
| 路径 | `optional-skills/blockchain/evm` |
| 版本 | `1.0.0` |
| 作者 | Mibayy (@Mibayy), youssefea (@youssefea), ethernet8023 (@ethernet8023), Hermes Agent |
| 许可协议 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `EVM`, `Ethereum`, `BNB`, `BSC`, `Base`, `Arbitrum`, `Polygon`, `Optimism`, `Avalanche`, `zkSync`, `Blockchain`, `Crypto`, `Web3`, `DeFi`, `NFT`, `ENS`, `Whale`, `Security` |
| 相关技能 | [`solana`](/user-guide/skills/optional/blockchain/blockchain-solana) |

<a id="reference-full-skill-md"></a>
## 参考：完整的 SKILL.md

:::info
以下是 Hermes 在该技能被触发时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

<a id="evm-blockchain-skill"></a>
# EVM区块链技能

查询8条链上的 EVM 兼容区块链数据，并支持美元计价。
14个命令：钱包组合、代币信息、交易、活动、Gas 追踪、
网络统计、价格查询、多链扫描、巨鲸检测、ENS 解析、
授权检查器、合约检查器、交易解码器。

支持8条链：Ethereum、BNB Chain (BSC)、Base、Arbitrum One、Polygon、
Optimism、Avalanche (C-Chain)、zkSync Era。

无需 API 密钥。零外部依赖——仅 Python 标准库
（urllib、json、argparse、threading）。
> **取代了独立的 `base` 技能。** 之前属于 `optional-skills/blockchain/base/` 的 Base 链专属代币（AERO、DEGEN、TOSHI、BRETT、WELL、cbETH、cbBTC、wstETH、rETH）以及所有 Base RPC 功能现已整合到此技能中。如需查询 Base 链，请在任意命令后加上 `--chain base`。

---

<a id="when-to-use"></a>
## 适用场景
- 用户询问某个 EVM 链上的钱包余额或投资组合
- 用户希望同时在所有链上检查同一个钱包
- 用户想通过交易哈希查看详情（或解码交易内容）
- 用户需要 ERC-20 代币元数据、价格、供应量或市值
- 用户想要某个地址的近期的交易历史
- 用户需要当前 Gas 价格或跨链比较手续费
- 用户想查找最近区块中的大额鲸鱼转账
- 用户要求解析 ENS 名称（vitalik.eth）或反向查询地址
- 用户想检查某个合约是否存在危险的代币授权
- 用户想检查智能合约（是否为代理？ERC-20？ERC-721？字节码大小？）
- 用户想在交易前跨链比较 Gas 成本

---

<a id="prerequisites"></a>
## 前置条件
仅需 Python 3.8+ 标准库，无需 pip 安装。
价格查询：CoinGecko 免费 API（有速率限制，约 10-30 次/分钟）。
ENS 解析：ensideas.com 公共 API。
交易解码：4byte.directory 公共 API。

覆盖 RPC 端点：`export EVM_RPC_URL=https://your-rpc.com`

辅助脚本路径：`~/.hermes/skills/blockchain/evm/scripts/evm_client.py`

---

<a id="quick-reference"></a>
## 快速参考

```
SCRIPT=~/.hermes/skills/blockchain/evm/scripts/evm_client.py

# 网络与价格
python3 $SCRIPT stats                            # 以太坊状态
python3 $SCRIPT stats --chain arbitrum           # Arbitrum 状态
python3 $SCRIPT compare                          # 全部 8 条链的 Gas + 价格对比

# 钱包
python3 $SCRIPT wallet 0xd8dA...96045            # 投资组合（ETH + ERC-20）
python3 $SCRIPT wallet 0xd8dA...96045 --chain bsc
python3 $SCRIPT multichain 0xd8dA...96045        # 同一钱包在所有链上的情况

# 代币与价格
python3 $SCRIPT price ETH
python3 $SCRIPT price 0xdAC1...1ec7              # 按合约地址查询
python3 $SCRIPT token 0xdAC1...1ec7              # ERC-20 元数据 + 市值

# 交易
python3 $SCRIPT tx 0x5c50...f060                 # 交易详情
python3 $SCRIPT decode 0x5c50...f060             # 解码输入数据（来自 4byte.directory）
python3 $SCRIPT activity 0xd8dA...96045          # 近期交易

# Gas
python3 $SCRIPT gas                              # Gas 价格 + 费用估算
python3 $SCRIPT gas --chain optimism

# 安全
python3 $SCRIPT allowance 0xd8dA...96045         # 危险的 ERC-20 授权查询
python3 $SCRIPT contract 0xdAC1...1ec7           # 合约检查（是否为代理？符合哪些标准？）

# ENS
python3 $SCRIPT ens vitalik.eth                  # 名称 → 地址 + 资料
python3 $SCRIPT ens 0xd8dA...96045               # 地址 → ENS 名称

# 鲸鱼检测
python3 $SCRIPT whale                            # 大额转账（最近 20 个区块，>1 万美元）
python3 $SCRIPT whale --blocks 50 --min-usd 100000 --chain arbitrum
```
---

<a id="procedure"></a>
## 操作步骤

<a id="0-setup-check"></a>
### 0. 环境检查
```bash
python3 --version   # 3.8+ required
python3 ~/.hermes/skills/blockchain/evm/scripts/evm_client.py stats
```

<a id="1-wallet-portfolio"></a>
### 1. 钱包持仓
原生代币余额 + 已知 ERC-20 代币，按美元价值排序。
```bash
python3 $SCRIPT wallet 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045
python3 $SCRIPT wallet 0xd8dA... --chain bsc --no-prices   # faster
```

<a id="2-multi-chain-scan"></a>
### 2. 多链扫描
使用线程同时扫描全部 8 条链上的同一地址。
```bash
python3 $SCRIPT multichain 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045
```
输出：每条链的本地余额 + 代币持有量 + 美元总价值。

<a id="3-compare-gas-prices"></a>
### 3. 对比（Gas + 价格）
并行查询全部 8 条链，显示最便宜/最贵的链。
```bash
python3 $SCRIPT compare
```

<a id="4-transaction-details-decode"></a>
### 4. 交易详情与解码
```bash
python3 $SCRIPT tx 0x5c504ed432cb51138bcf09aa5e8a410dd4a1e204ef84bfed1be16dfba1b22060
python3 $SCRIPT decode 0x5c504ed...   # Shows human-readable function signature
```
解码使用 4byte.directory 将 0xa9059cbb 转换为 transfer(address,uint256)。

<a id="5-ens-resolution"></a>
### 5. ENS 解析
```bash
python3 $SCRIPT ens vitalik.eth          # -> 0xd8dA... + avatar + social links
python3 $SCRIPT ens 0xd8dA...96045       # -> vitalik.eth
```

<a id="6-allowance-checker-security"></a>
### 6. 授权额度检查（安全）
检查授予已知 DEX/桥接合约的 ERC-20 额度。
```bash
python3 $SCRIPT allowance 0xYourWallet
```
将无限额度标记为**高风险**。

<a id="7-contract-inspector"></a>
### 7. 合约检查器
```bash
python3 $SCRIPT contract 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48   # USDC (proxy)
python3 $SCRIPT contract 0xdAC17F958D2ee523a2206206994597C13D831ec7   # USDT (ERC-20)
```
检测：代理合约（EIP-1967/EIP-1167）、ERC-20、ERC-721、ERC-165。显示代理合约的字节码大小及实现地址。
<a id="8-whale-detection"></a>
### 8. 巨鲸检测
```bash
python3 $SCRIPT whale                                    # 以太坊，最近20个区块，金额>1万美元
python3 $SCRIPT whale --blocks 50 --min-usd 50000 --chain bsc
```

<a id="9-gas-tracker"></a>
### 9. Gas 追踪器
```bash
python3 $SCRIPT gas
python3 $SCRIPT gas --chain polygon
```
显示以下操作的 gwei 价格 + USD 成本：转账、ERC-20 转账、授权、兑换、NFT 铸造、NFT 转账。

---

<a id="supported-chains"></a>
## 支持的链
| Key       | Name           | Native | Chain ID |
|-----------|----------------|--------|----------|
| ethereum  | Ethereum       | ETH    | 1        |
| bsc       | BNB Chain      | BNB    | 56       |
| base      | Base           | ETH    | 8453     |
| arbitrum  | Arbitrum One   | ETH    | 42161    |
| polygon   | Polygon        | POL    | 137      |
| optimism  | Optimism       | ETH    | 10       |
| avalanche | Avalanche C    | AVAX   | 43114    |
| zksync    | zkSync Era     | ETH    | 324      |

---

<a id="pitfalls"></a>
## 常见陷阱
- CoinGecko 免费版限制：约 10-30 请求/分钟。使用 `--no-prices` 可加快钱包扫描速度。
- 公共 RPC 可能限流。生产环境请将 `EVM_RPC_URL` 设置为私有节点。
- `wallet` 和 `allowance` 仅检查已知的代币列表（每条链约 30 个代币）。如需完整代币发现，请使用区块浏览器。
- `activity` 仅扫描最近的区块（最多 200 个）。如需完整历史，请使用 Etherscan API。
- `multichain` 会启动 8 个并行线程——可能触发公共 RPC 的速率限制。
- ENS 解析依赖单个公共节点（ensideas.com / ens.vitalik.ca），无备用方案。如果该节点不可用，`ens` 命令将失败——请稍后重试或使用区块浏览器。
- 交易解码依赖单个公共节点（4byte.directory），无备用方案。不在其数据库中的函数选择器会显示为 `unknown`。
- **L2 gas 估算仅针对 L2 执行层。** 在 Base、Arbitrum、Optimism 和 zkSync 等 Rollup 上，实际交易成本还包括 L1 数据发布费用，该费用取决于 calldata 大小和当前 L1 gas 价格。`gas` 命令不估算这一 L1 部分。对于 Base，请参考网络的 L1 费用预言机（合约 `0x420000000000000000000000000000000000000F`）。
- 地址 / 交易哈希输入会进行有效性校验（0x 前缀 + 长度 + 十六进制格式），但 **不强制** EIP-55 校验和大小写（RPC 节点接受任意大小写的十六进制字符串）。
---

<a id="verification"></a>
## 验证
```bash
# 应显示当前区块、Gas 价格、ETH 价格
python3 ~/.hermes/skills/blockchain/evm/scripts/evm_client.py stats

# 应解析 vitalik.eth 为 0xd8dA...
python3 ~/.hermes/skills/blockchain/evm/scripts/evm_client.py ens vitalik.eth
```
