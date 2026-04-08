---
title: 凭据池 (Credential Pools)
description: 为每个提供商配置多个 API Key 或 OAuth 令牌，实现自动轮换和速率限制恢复。
sidebar_label: 凭据池
sidebar_position: 9
---

# 凭据池 (Credential Pools)

凭据池允许你为同一个提供商注册多个 API Key 或 OAuth 令牌。当某个 Key 达到速率限制（rate limit）或计费配额时，Hermes 会自动轮换到下一个健康的 Key —— 从而在不切换提供商的情况下保持会话活跃。

这与 [备用提供商 (fallback providers)](./fallback-providers.md) 不同，后者是完全切换到 *另一个* 不同的提供商。凭据池是同提供商内的轮换；备用提供商是跨提供商的故障转移。系统会优先尝试凭据池 —— 如果池中所有 Key 都耗尽了，*才会* 激活备用提供商。

## 工作原理

```
你的请求
  → 从池中选取 Key (round_robin / least_used / fill_first / random)
  → 发送至提供商
  → 遇到 429 速率限制？
      → 重试当前 Key 一次（针对瞬时波动）
      → 第二次 429 → 轮换至池中下一个 Key
      → 所有 Key 均耗尽 → 激活 fallback_model（不同提供商）
  → 遇到 402 计费错误？
      → 立即轮换至池中下一个 Key（进入 24 小时冷却期）
  → 遇到 401 认证过期？
      → 尝试刷新令牌 (OAuth)
      → 刷新失败 → 轮换至池中下一个 Key
  → 成功 → 正常继续
```

## 快速上手

如果你已经在 `.env` 中设置了 API Key，Hermes 会自动将其识别为包含 1 个 Key 的凭据池。要发挥凭据池的优势，请添加更多 Key：

```bash
# 添加第二个 OpenRouter Key
hermes auth add openrouter --api-key sk-or-v1-your-second-key

# 添加第二个 Anthropic Key
hermes auth add anthropic --type api-key --api-key sk-ant-api03-your-second-key

# 添加 Anthropic OAuth 凭据 (Claude Code 订阅)
hermes auth add anthropic --type oauth
# 将打开浏览器进行 OAuth 登录
```

查看你的凭据池：

```bash
hermes auth list
```

输出示例：
```
openrouter (2 credentials):
  #1  OPENROUTER_API_KEY   api_key env:OPENROUTER_API_KEY ←
  #2  backup-key           api_key manual

anthropic (3 credentials):
  #1  hermes_pkce          oauth   hermes_pkce ←
  #2  claude_code          oauth   claude_code
  #3  ANTHROPIC_API_KEY    api_key env:ANTHROPIC_API_KEY
```

`←` 标记表示当前选中的凭据。

## 交互式管理

不带子命令运行 `hermes auth` 即可进入交互式向导：

```bash
hermes auth
```

这将显示完整的凭据池状态并提供菜单：

```
What would you like to do?
  1. Add a credential
  2. Remove a credential
  3. Reset cooldowns for a provider
  4. Set rotation strategy for a provider
  5. Exit
```

对于同时支持 API Key 和 OAuth 的提供商（如 Anthropic、Nous、Codex），添加流程会询问类型：

```
anthropic supports both API keys and OAuth login.
  1. API key (paste a key from the provider dashboard)
  2. OAuth login (authenticate via browser)
Type [1/2]:
```

## CLI 命令

| 命令 | 描述 |
|---------|-------------|
| `hermes auth` | 交互式凭据池管理向导 |
| `hermes auth list` | 显示所有凭据池和凭据 |
| `hermes auth list <provider>` | 显示特定提供商的凭据池 |
| `hermes auth add <provider>` | 添加凭据（会提示选择类型和输入 Key） |
| `hermes auth add <provider> --type api-key --api-key <key>` | 以非交互方式添加 API Key |
| `hermes auth add <provider> --type oauth` | 通过浏览器登录添加 OAuth 凭据 |
| `hermes auth remove <provider> <index>` | 通过从 1 开始的索引删除凭据 |
| `hermes auth reset <provider>` | 清除所有冷却/耗尽状态 |

## 轮换策略

可以通过 `hermes auth` → "Set rotation strategy" 进行配置，或在 `config.yaml` 中设置：

```yaml
credential_pool_strategies:
  openrouter: round_robin
  anthropic: least_used
```

| 策略 | 行为 |
|----------|----------|
| `fill_first` (默认) | 优先使用第一个健康的 Key 直到耗尽，然后再移动到下一个 |
| `round_robin` | 均匀循环使用所有 Key，每次选择后进行轮换 |
| `least_used` | 始终选择请求计数最低的 Key |
| `random` | 在健康的 Key 中随机选择 |

## 错误恢复

凭据池对不同错误的处理方式不同：

| 错误 | 行为 | 冷却时间 |
|-------|----------|----------|
| **429 Rate Limit** | 重试当前 Key 一次（瞬时错误）。连续第二次 429 则轮换至下一个 Key | 1 小时 |
| **402 Billing/Quota** | 立即轮换至下一个 Key | 24 小时 |
| **401 Auth Expired** | 首先尝试刷新 OAuth 令牌。仅在刷新失败时才轮换 | — |
| **所有 Key 均耗尽** | 如果配置了 `fallback_model`，则回退到备用模型 | — |

`has_retried_429` 标志会在每次 API 调用成功后重置，因此单个瞬时 429 不会触发轮换。

## 自定义端点池

自定义的 OpenAI 兼容端点（如 Together.ai、RunPod、本地服务器）拥有各自的凭据池，其键名为 `config.yaml` 中 `custom_providers` 定义的端点名称。

当你通过 `hermes model` 设置自定义端点时，它会自动生成一个名称，如 "Together.ai" 或 "Local (localhost:8080)"。该名称即为凭据池的键。

```bash
# 通过 hermes model 设置自定义端点后：
hermes auth list
# 显示：
#   Together.ai (1 credential):
#     #1  config key    api_key config:Together.ai ←

# 为同一个端点添加第二个 Key：
hermes auth add Together.ai --api-key sk-together-second-key
```

自定义端点池存储在 `auth.json` 的 `credential_pool` 下，带有 `custom:` 前缀：

```json
{
  "credential_pool": {
    "openrouter": [...],
    "custom:together.ai": [...]
  }
}
```

## 自动发现

Hermes 会自动从多个来源发现凭据，并在启动时填充凭据池：

| 来源 | 示例 | 是否自动填充？ |
|--------|---------|-------------|
| 环境变量 | `OPENROUTER_API_KEY`, `ANTHROPIC_API_KEY` | 是 |
| OAuth 令牌 (auth.json) | Codex 设备代码, Nous 设备代码 | 是 |
| Claude Code 凭据 | `~/.claude/.credentials.json` | 是 (Anthropic) |
| Hermes PKCE OAuth | `~/.hermes/auth.json` | 是 (Anthropic) |
| 自定义端点配置 | `config.yaml` 中的 `model.api_key` | 是 (自定义端点) |
| 手动条目 | 通过 `hermes auth add` 添加 | 持久化在 auth.json |

自动填充的条目在每次加载凭据池时都会更新 —— 如果你删除了某个环境变量，其对应的池条目也会自动清除。手动条目（通过 `hermes auth add` 添加）永远不会被自动清除。

## 委派与 Subagent 共享

当 Agent 通过 `delegate_task` 生成 Subagents 时，父级 Agent 的凭据池会自动共享给子级：

- **相同提供商** —— 子级接收父级的完整凭据池，从而在遇到速率限制时能够轮换 Key。
- **不同提供商** —— 子级加载该提供商自己的凭据池（如果已配置）。
- **未配置凭据池** —— 子级回退到继承的单个 API Key。

这意味着 Subagents 享有与父级相同的速率限制弹性，无需额外配置。基于任务的凭据租赁机制确保了子级在并发轮换 Key 时不会发生冲突。

## 线程安全

凭据池对所有状态变更（`select()`、`mark_exhausted_and_rotate()`、`try_refresh_current()`、`mark_used()`）均使用线程锁。这确保了网关在同时处理多个聊天会话时，并发访问是安全的。

## 架构

有关完整的数据流图，请参阅仓库中的 [`docs/credential-pool-flow.excalidraw`](https://excalidraw.com/#json=2Ycqhqpi6f12E_3ITyiwh,c7u9jSt5BwrmiVzHGbm87g)。

凭据池集成在提供商解析层：

1. **`agent/credential_pool.py`** — 池管理器：负责存储、选择、轮换和冷却。
2. **`hermes_cli/auth_commands.py`** — CLI 命令和交互式向导。
3. **`hermes_cli/runtime_provider.py`** — 感知凭据池的凭据解析。
4. **`run_agent.py`** — 错误恢复：429/402/401 → 池轮换 → 备用方案。

## 存储

凭据池状态存储在 `~/.hermes/auth.json` 的 `credential_pool` 键下：

```json
{
  "version": 1,
  "credential_pool": {
    "openrouter": [
      {
        "id": "abc123",
        "label": "OPENROUTER_API_KEY",
        "auth_type": "api_key",
        "priority": 0,
        "source": "env:OPENROUTER_API_KEY",
        "access_token": "sk-or-v1-...",
        "last_status": "ok",
        "request_count": 142
      }
    ]
  }
}
```
策略存储在 `config.yaml` 中（而不是 `auth.json`）：

```yaml
credential_pool_strategies:
  openrouter: round_robin
  anthropic: least_used
```
