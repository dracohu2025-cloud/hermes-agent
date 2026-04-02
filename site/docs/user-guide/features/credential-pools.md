---
title: 凭证池
description: 为每个提供商池化多个 API 密钥或 OAuth 令牌，实现自动轮换和速率限制恢复。
sidebar_label: 凭证池
sidebar_position: 9
---

# 凭证池

凭证池允许你为同一个提供商注册多个 API 密钥或 OAuth 令牌。当某个密钥触发速率限制或计费配额时，Hermes 会自动切换到下一个健康的密钥——保持会话不中断，而无需更换提供商。

这与[备用提供商](./fallback-providers.md)不同，后者是切换到*不同*的提供商。凭证池是同一提供商内部的轮换；备用提供商是跨提供商的故障切换。系统优先尝试凭证池——如果所有池内密钥都用尽，*才*启用备用提供商。

## 工作原理

```
你的请求
  → 从池中选取密钥（轮询 / 最少使用 / 先填满 / 随机）
  → 发送给提供商
  → 收到 429 速率限制？
      → 同一密钥重试一次（短暂波动）
      → 第二次 429 → 切换到下一个池内密钥
      → 所有密钥用尽 → 启用 fallback_model（不同提供商）
  → 收到 402 计费错误？
      → 立即切换到下一个池内密钥（24 小时冷却）
  → 收到 401 认证过期？
      → 尝试刷新令牌（OAuth）
      → 刷新失败 → 切换到下一个池内密钥
  → 成功 → 正常继续
```

## 快速开始

如果你已经在 `.env` 中设置了 API 密钥，Hermes 会自动识别为一个单密钥池。要使用凭证池功能，添加更多密钥：

```bash
# 添加第二个 OpenRouter 密钥
hermes auth add openrouter --api-key sk-or-v1-your-second-key

# 添加第二个 Anthropic 密钥
hermes auth add anthropic --type api-key --api-key sk-ant-api03-your-second-key

# 添加 Anthropic OAuth 凭证（Claude Code 订阅）
hermes auth add anthropic --type oauth
# 会打开浏览器进行 OAuth 登录
```

查看你的凭证池：

```bash
hermes auth list
```

输出示例：
```
openrouter (2 个凭证):
  #1  OPENROUTER_API_KEY   api_key env:OPENROUTER_API_KEY ←
  #2  backup-key           api_key manual

anthropic (3 个凭证):
  #1  hermes_pkce          oauth   hermes_pkce ←
  #2  claude_code          oauth   claude_code
  #3  ANTHROPIC_API_KEY    api_key env:ANTHROPIC_API_KEY
```

`←` 标记当前选中的凭证。

## 交互式管理

运行 `hermes auth`（无子命令）进入交互式向导：

```bash
hermes auth
```

会显示完整的凭证池状态并提供菜单：

```
你想执行什么操作？
  1. 添加凭证
  2. 移除凭证
  3. 重置提供商的冷却状态
  4. 设置提供商的轮换策略
  5. 退出
```

对于同时支持 API 密钥和 OAuth 的提供商（Anthropic、Nous、Codex），添加流程会询问类型：

```
anthropic 支持 API 密钥和 OAuth 登录。
  1. API 密钥（从提供商控制台粘贴密钥）
  2. OAuth 登录（通过浏览器认证）
请输入 [1/2]:
```

## CLI 命令

| 命令 | 说明 |
|---------|-------------|
| `hermes auth` | 交互式凭证池管理向导 |
| `hermes auth list` | 显示所有凭证池和凭证 |
| `hermes auth list <provider>` | 显示指定提供商的凭证池 |
| `hermes auth add <provider>` | 添加凭证（交互式选择类型和密钥） |
| `hermes auth add <provider> --type api-key --api-key <key>` | 非交互式添加 API 密钥 |
| `hermes auth add <provider> --type oauth` | 通过浏览器登录添加 OAuth 凭证 |
| `hermes auth remove <provider> <index>` | 按 1 基索引移除凭证 |
| `hermes auth reset <provider>` | 清除所有冷却和用尽状态 |

## 轮换策略

可通过 `hermes auth` → “设置轮换策略” 或在 `config.yaml` 中配置：

```yaml
credential_pool_strategies:
  openrouter: round_robin
  anthropic: least_used
```

| 策略 | 行为 |
|----------|----------|
| `fill_first`（默认） | 使用第一个健康密钥直到用尽，再切换到下一个 |
| `round_robin` | 均匀循环使用密钥，每次选择后轮换 |
| `least_used` | 总是选择请求次数最少的密钥 |
| `random` | 在健康密钥中随机选择 |

## 错误恢复

凭证池对不同错误有不同处理：

| 错误 | 行为 | 冷却时间 |
|-------|----------|----------|
| **429 速率限制** | 同一密钥重试一次（短暂波动），第二次连续 429 切换到下一个密钥 | 1 小时 |
| **402 计费/配额** | 立即切换到下一个密钥 | 24 小时 |
| **401 认证过期** | 先尝试刷新 OAuth 令牌，刷新失败才切换密钥 | — |
| **所有密钥用尽** | 如果配置了 `fallback_model`，则切换到备用提供商 | — |

`has_retried_429` 标志在每次成功调用后重置，因此单次短暂的 429 不会触发轮换。

## 自定义端点池

自定义的 OpenAI 兼容端点（如 Together.ai、RunPod、本地服务器）会有自己的凭证池，池键名来自 `config.yaml` 中 `custom_providers` 的端点名称。

通过 `hermes model` 设置自定义端点时，会自动生成类似 “Together.ai” 或 “Local (localhost:8080)” 的名称，作为池的键名。

```bash
# 通过 hermes model 设置自定义端点后：
hermes auth list
# 显示：
#   Together.ai (1 个凭证):
#     #1  config key    api_key config:Together.ai ←

# 为同一端点添加第二个密钥：
hermes auth add Together.ai --api-key sk-together-second-key
```

自定义端点池存储在 `auth.json` 的 `credential_pool` 下，键名前缀为 `custom:`：

```json
{
  "credential_pool": {
    "openrouter": [...],
    "custom:together.ai": [...]
  }
}
```

## 自动发现

Hermes 会自动从多种来源发现凭证，并在启动时初始化凭证池：

| 来源 | 示例 | 是否自动初始化 |
|--------|---------|-------------|
| 环境变量 | `OPENROUTER_API_KEY`、`ANTHROPIC_API_KEY` | 是 |
| OAuth 令牌（auth.json） | Codex 设备码、Nous 设备码 | 是 |
| Claude Code 凭证 | `~/.claude/.credentials.json` | 是（Anthropic） |
| Hermes PKCE OAuth | `~/.hermes/auth.json` | 是（Anthropic） |
| 自定义端点配置 | `config.yaml` 中的 `model.api_key` | 是（自定义端点） |
| 手动添加 | 通过 `hermes auth add` 添加 | 保存在 auth.json 中 |

自动初始化的条目在每次加载池时更新——如果移除环境变量，对应的池条目会自动删除。手动添加的条目不会被自动删除。

## 线程安全

凭证池对所有状态变更操作（`select()`、`mark_exhausted_and_rotate()`、`try_refresh_current()`、`mark_used()`）使用线程锁，确保在网关同时处理多个聊天会话时的安全并发访问。

## 架构

完整数据流图请参见仓库中的 [`docs/credential-pool-flow.excalidraw`](https://excalidraw.com/#json=2Ycqhqpi6f12E_3ITyiwh,c7u9jSt5BwrmiVzHGbm87g)。

凭证池集成在提供商解析层：

1. **`agent/credential_pool.py`** — 池管理器：存储、选择、轮换、冷却
2. **`hermes_cli/auth_commands.py`** — CLI 命令和交互式向导
3. **`hermes_cli/runtime_provider.py`** — 支持凭证池的凭证解析
4. **`run_agent.py`** — 错误恢复：429/402/401 → 池轮换 → 备用提供商

## 存储

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
  "credential_pool_strategies": {
    "openrouter": "round_robin"
  }
}
```

策略配置存储在 `config.yaml`（而非 `auth.json`）：

```yaml
credential_pool_strategies:
  openrouter: round_robin
  anthropic: least_used
```
