---
title: 凭据池
description: 为每个提供商池化多个 API 密钥或 OAuth 令牌，实现自动轮换和速率限制恢复。
sidebar_label: 凭据池
sidebar_position: 9
---

# 凭据池 {#credential-pools}

凭据池允许你为同一提供商注册多个 API 密钥或 OAuth 令牌。当某个密钥达到速率限制或计费配额时，Hermes 会自动轮换到下一个健康密钥——让你的会话保持活跃，无需切换提供商。

这与[回退提供商](./fallback-providers.md)不同，后者会切换到完全不同的*提供商*。凭据池是同一提供商内的轮换；回退提供商是跨提供商故障转移。池会优先尝试——如果池内所有密钥都已耗尽，*然后*回退提供商才会激活。

## 工作原理 {#how-it-works}

```
你的请求
  → 从池中选取密钥（轮询 / 最少使用 / 优先填充 / 随机）
  → 发送给提供商
  → 收到 429 速率限制？
      → 对同一密钥重试一次（瞬时波动）
      → 第二次 429 → 轮换到池中下一个密钥
      → 所有密钥耗尽 → 回退模型（不同提供商）
  → 收到 402 计费错误？
      → 立即轮换到池中下一个密钥（24 小时冷却）
  → 收到 401 身份认证过期？
      → 尝试刷新令牌（OAuth）
      → 刷新失败 → 轮换到池中下一个密钥
  → 成功 → 正常继续
```

## 快速开始 {#quick-start}

如果你已经在 `.env` 中设置了一个 API 密钥，Hermes 会自动将其发现为单密钥池。要体验池化的好处，请添加更多密钥：

```bash
# 添加第二个 OpenRouter 密钥
hermes auth add openrouter --api-key sk-or-v1-your-second-key

# 添加第二个 Anthropic 密钥
hermes auth add anthropic --type api-key --api-key sk-ant-api03-your-second-key

# 添加一个 Anthropic OAuth 凭据（需要 Claude Max 套餐 + 额外使用额度）
hermes auth add anthropic --type oauth
# 打开浏览器进行 OAuth 登录
```

查看你的池：

```bash
hermes auth list
```

输出：
```
openrouter (2 credentials):
  #1  OPENROUTER_API_KEY   api_key env:OPENROUTER_API_KEY ←
  #2  backup-key           api_key manual

anthropic (3 credentials):
  #1  hermes_pkce          oauth   hermes_pkce ←
  #2  claude_code          oauth   claude_code
  #3  ANTHROPIC_API_KEY    api_key env:ANTHROPIC_API_KEY
```

`←` 标记当前选中的凭据。

## 交互式管理 {#interactive-management}

运行 `hermes auth`（不带子命令）进入交互式向导：

```bash
hermes auth
```

这会显示完整的池状态，并提供一个菜单：

```
你想做什么？
  1. 添加凭据
  2. 移除凭据
  3. 重置某个提供商的冷却状态
  4. 设置某个提供商的轮换策略
  5. 退出
```

对于同时支持 API 密钥和 OAuth 的提供商（Anthropic、Nous、Codex），添加流程会询问类型：

```
anthropic 同时支持 API 密钥和 OAuth 登录。
  1. API 密钥（从提供商控制台粘贴密钥）
  2. OAuth 登录（通过浏览器进行身份认证）
请输入 [1/2]：
```

## CLI 命令 {#cli-commands}

| 命令 | 说明 |
|---------|-------------|
| `hermes auth` | 交互式池管理向导 |
| `hermes auth list` | 显示所有池和凭据 |
| `hermes auth list &lt;provider&gt;` | 显示特定提供商的池 |
| `hermes auth add &lt;provider&gt;` | 添加凭据（提示输入类型和密钥） |
| `hermes auth add &lt;provider&gt; --type api-key --api-key &lt;key&gt;` | 以非交互方式添加 API 密钥 |
| `hermes auth add &lt;provider&gt; --type oauth` | 通过浏览器登录添加 OAuth 凭据 |
| `hermes auth remove &lt;provider&gt; &lt;index&gt;` | 按从 1 开始的索引移除凭据 |
| `hermes auth reset &lt;provider&gt;` | 清除所有冷却/耗尽状态 |
## 轮换策略 {#rotation-strategies}

可通过 `hermes auth` → "Set rotation strategy" 或在 `config.yaml` 中配置：

```yaml
credential_pool_strategies:
  openrouter: round_robin
  anthropic: least_used
```

| 策略 | 行为 |
|----------|----------|
| `fill_first`（默认） | 优先使用第一个健康的密钥，直到其额度耗尽，再切换到下一个 |
| `round_robin` | 均匀轮换密钥，每次选择后自动切换 |
| `least_used` | 始终选择请求次数最少的密钥 |
| `random` | 在所有健康密钥中随机选择 |

## 错误恢复 {#error-recovery}

凭证池对不同错误采用不同处理方式：

| 错误 | 行为 | 冷却时间 |
|-------|----------|----------|
| **429 限速** | 对同一密钥重试一次（临时）。若第二次连续 429，则轮换到下一个密钥 | 1 小时 |
| **402 计费/配额** | 立即轮换到下一个密钥 | 24 小时 |
| **401 认证过期** | 先尝试刷新 OAuth 令牌。仅当刷新失败时才轮换 | — |
| **所有密钥耗尽** | 如果配置了 `fallback_model`，则降级使用 | — |

`has_retried_429` 标志位会在每次成功 API 调用后重置，因此单次临时 429 不会触发轮换。

## 自定义端点池 {#custom-endpoint-pools}

自定义 OpenAI 兼容端点（Together.ai、RunPod、本地服务器）拥有自己的凭证池，以 config.yaml 中 `custom_providers` 的端点名称作为键。

当通过 `hermes model` 设置自定义端点时，会自动生成一个名称，例如 "Together.ai" 或 "Local (localhost:8080)"。该名称即成为凭证池的键。

```bash
# 通过 hermes model 设置自定义端点后：
hermes auth list
# 显示：
#   Together.ai (1 credential):
#     #1  config key    api_key config:Together.ai ←

# 为同一端点添加第二个密钥：
hermes auth add Together.ai --api-key sk-together-second-key
```

自定义端点池存储在 `auth.json` 的 `credential_pool` 下，前缀为 `custom:`：

```json
{
  "credential_pool": {
    "openrouter": [...],
    "custom:together.ai": [...]
  }
}
```

## 自动发现 {#auto-discovery}

Hermes 会从多种来源自动发现凭证，并在启动时注入到池中：

| 来源 | 示例 | 自动注入？ |
|--------|---------|-------------|
| 环境变量 | `OPENROUTER_API_KEY`、`ANTHROPIC_API_KEY` | 是 |
| OAuth 令牌（auth.json） | Codex device code、Nous device code | 是 |
| Claude Code 凭证 | `~/.claude/.credentials.json` | 是（Anthropic） |
| Hermes PKCE OAuth | `~/.hermes/auth.json` | 是（Anthropic） |
| 自定义端点配置 | `model.api_key` 在 config.yaml 中 | 是（自定义端点） |
| 手动条目 | 通过 `hermes auth add` 添加 | 持久化存储在 auth.json 中 |

自动注入的条目会在每次加载池时更新——如果你删除了某个环境变量，其对应的池条目会自动清除。手动条目（通过 `hermes auth add` 添加）永远不会被自动清除。

## 委托与子 Agent 共享 {#delegation-subagent-sharing}

当 Agent 通过 `delegate_task` 生成子 Agent 时，父 Agent 的凭证池会自动与子 Agent 共享：

- **相同提供商** —— 子 Agent 获得父 Agent 的完整池，以便在限速时进行密钥轮换
- **不同提供商** —— 子 Agent 加载该提供商自己的池（如果已配置）
- **未配置池** —— 子 Agent 回退到继承的单个 API 密钥
这意味着子 Agent 可以继承父 Agent 的速率限制弹性，无需额外配置。按任务租用凭证可确保子 Agent 在并发轮换密钥时不会相互冲突。

## 线程安全 {#thread-safety}

凭证池对所有状态变更（`select()`、`mark_exhausted_and_rotate()`、`try_refresh_current()`、`mark_used()`）使用线程锁。这确保了网关同时处理多个聊天会话时的安全并发访问。

## 架构 {#architecture}

完整的数据流图请参见仓库中的 [`docs/credential-pool-flow.excalidraw`](https://excalidraw.com/#json=2Ycqhqpi6f12E_3ITyiwh,c7u9jSt5BwrmiVzHGbm87g)。

凭证池集成在提供商解析层：

1. **`agent/credential_pool.py`** — 池管理器：存储、选择、轮换、冷却
2. **`hermes_cli/auth_commands.py`** — CLI 命令和交互式向导
3. **`hermes_cli/runtime_provider.py`** — 支持池的凭证解析
4. **`run_agent.py`** — 错误恢复：429/402/401 → 池轮换 → 回退

## 存储 {#storage}

池状态存储在 `~/.hermes/auth.json` 的 `credential_pool` 键下：

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
  },
}
```

策略存储在 `config.yaml`（而非 `auth.json`）中：

```yaml
credential_pool_strategies:
  openrouter: round_robin
  anthropic: least_used
```
