---
title: 备用供应商
description: 当主模型不可用时，配置自动切换到备份 LLM 供应商。
sidebar_label: 备用供应商
sidebar_position: 8
---

# 备用供应商

Hermes Agent 有三层容错机制，确保当供应商遇到问题时你的会话仍能继续运行：

1. **[凭证池](./credential-pools.md)** — 在同一供应商的不同 API 密钥之间轮换（首先尝试）
2. **主模型备用** — 当你的主模型失败时，自动切换到不同的供应商:模型组合
3. **辅助任务备用** — 为诸如视觉处理、压缩、网页提取等辅助任务提供独立的供应商选择

凭证池处理同一供应商内部的轮换（例如，多个 OpenRouter 密钥）。本页内容涵盖跨供应商备用。两者都是可选的，并且独立工作。

## 主模型备用

当你的主 LLM 供应商遇到错误 — 速率限制、服务器负载过高、认证失败、连接中断 — Hermes 可以在会话中自动切换到备份供应商:模型组合，而不会丢失你的对话。

### 配置

在 `~/.hermes/config.yaml` 中添加 `fallback_model` 部分：

```yaml
fallback_model:
  provider: openrouter
  model: anthropic/claude-sonnet-4
```

`provider` 和 `model` 都是**必需的**。如果任一缺失，备用功能将被禁用。

### 支持的供应商

| 供应商 | 配置值 | 要求 |
|----------|-------|-------------|
| AI Gateway | `ai-gateway` | `AI_GATEWAY_API_KEY` |
| OpenRouter | `openrouter` | `OPENROUTER_API_KEY` |
| Nous Portal | `nous` | `hermes auth` (OAuth) |
| OpenAI Codex | `openai-codex` | `hermes model` (ChatGPT OAuth) |
| GitHub Copilot | `copilot` | `COPILOT_GITHUB_TOKEN`, `GH_TOKEN`, 或 `GITHUB_TOKEN` |
| GitHub Copilot ACP | `copilot-acp` | 外部进程（编辑器集成） |
| Anthropic | `anthropic` | `ANTHROPIC_API_KEY` 或 Claude Code 凭证 |
| z.ai / GLM | `zai` | `GLM_API_KEY` |
| Kimi / Moonshot | `kimi-coding` | `KIMI_API_KEY` |
| MiniMax | `minimax` | `MINIMAX_API_KEY` |
| MiniMax (中国) | `minimax-cn` | `MINIMAX_CN_API_KEY` |
| DeepSeek | `deepseek` | `DEEPSEEK_API_KEY` |
| OpenCode Zen | `opencode-zen` | `OPENCODE_ZEN_API_KEY` |
| OpenCode Go | `opencode-go` | `OPENCODE_GO_API_KEY` |
| Kilo Code | `kilocode` | `KILOCODE_API_KEY` |
| Xiaomi MiMo | `xiaomi` | `XIAOMI_API_KEY` |
| Alibaba / DashScope | `alibaba` | `DASHSCOPE_API_KEY` |
| Hugging Face | `huggingface` | `HF_TOKEN` |
| 自定义端点 | `custom` | `base_url` + `api_key_env`（见下文） |

### 自定义端点备用

对于自定义的 OpenAI 兼容端点，添加 `base_url` 和可选的 `api_key_env`：

```yaml
fallback_model:
  provider: custom
  model: my-local-model
  base_url: http://localhost:8000/v1
  api_key_env: MY_LOCAL_KEY          # 包含 API 密钥的环境变量名
```

### 备用触发时机

当主模型因以下原因失败时，备用会自动激活：

- **速率限制**（HTTP 429） — 耗尽重试尝试后
- **服务器错误**（HTTP 500, 502, 503） — 耗尽重试尝试后
- **认证失败**（HTTP 401, 403） — 立即（无需重试）
- **未找到**（HTTP 404） — 立即
- **无效响应** — API 多次返回格式错误或空响应时

触发时，Hermes：

1. 为备用供应商解析凭证
2. 构建新的 API 客户端
3. 原地替换模型、供应商和客户端
4. 重置重试计数器并继续对话

切换是无缝的 — 你的对话历史、工具调用和上下文都会被保留。Agent 会从刚才中断的地方继续，只是使用不同的模型。

:::info 一次性备用
备用在每个会话中最多激活**一次**。如果备用供应商也失败，则由正常的错误处理接管（重试，然后显示错误消息）。这防止了级联备用循环。
:::

### 示例

**OpenRouter 作为 Anthropic 原生模型的备用：**
```yaml
model:
  provider: anthropic
  default: claude-sonnet-4-6

fallback_model:
  provider: openrouter
  model: anthropic/claude-sonnet-4
```

**Nous Portal 作为 OpenRouter 的备用：**
```yaml
model:
  provider: openrouter
  default: anthropic/claude-opus-4

fallback_model:
  provider: nous
  model: nous-hermes-3
```

**本地模型作为云模型的备用：**
```yaml
fallback_model:
  provider: custom
  model: llama-3.1-70b
  base_url: http://localhost:8000/v1
  api_key_env: LOCAL_API_KEY
```

**Codex OAuth 作为备用：**
```yaml
fallback_model:
  provider: openai-codex
  model: gpt-5.3-codex
```

### 备用适用的场景

| 场景 | 支持备用 |
|---------|-------------------|
| CLI 会话 | ✔ |
| 消息网关（Telegram, Discord 等） | ✔ |
| Subagent 委派 | ✘（subagents 不继承备用配置） |
| Cron 作业 | ✘（使用固定的供应商运行） |
| 辅助任务（视觉处理、压缩） | ✘（使用它们自己的供应商链 — 见下文） |

:::tip
没有针对 `fallback_model` 的环境变量 — 它完全通过 `config.yaml` 配置。这是有意为之：备用配置是一个有意的选择，不应被过时的 shell 导出覆盖。
:::

---

## 辅助任务备用

Hermes 使用独立的轻量级模型处理辅助任务。每个任务都有自己的供应商选择链，作为一个内置的备用系统。

### 具有独立供应商选择的任务

| 任务 | 功能 | 配置键 |
|------|-------------|-----------|
| Vision | 图像分析、浏览器截图 | `auxiliary.vision` |
| Web Extract | 网页内容摘要 | `auxiliary.web_extract` |
| Compression | 上下文压缩摘要 | `auxiliary.compression` 或 `compression.summary_provider` |
| Session Search | 历史会话摘要 | `auxiliary.session_search` |
| Skills Hub | 技能搜索和发现 | `auxiliary.skills_hub` |
| MCP | MCP 助手操作 | `auxiliary.mcp` |
| Memory Flush | 记忆合并 | `auxiliary.flush_memories` |

### 自动检测链

当一个任务的供应商设置为 `"auto"`（默认）时，Hermes 按顺序尝试供应商直到找到一个可用：

**对于文本任务（压缩、网页提取等）：**

```text
OpenRouter → Nous Portal → 自定义端点 → Codex OAuth →
API 密钥供应商（z.ai, Kimi, MiniMax, Xiaomi MiMo, Hugging Face, Anthropic） → 放弃
```

**对于视觉任务：**

```text
主供应商（如果支持视觉） → OpenRouter → Nous Portal →
Codex OAuth → Anthropic → 自定义端点 → 放弃
```

如果在调用时选择的供应商失败，Hermes 也有内部重试机制：如果供应商不是 OpenRouter 且未设置明确的 `base_url`，它会将 OpenRouter 作为最后的备用尝试。

### 配置辅助供应商

每个任务可以在 `config.yaml` 中独立配置：

```yaml
auxiliary:
  vision:
    provider: "auto"              # auto | openrouter | nous | codex | main | anthropic
    model: ""                     # 例如 "openai/gpt-4o"
    base_url: ""                  # 直接端点地址（优先于 provider）
    api_key: ""                   # base_url 的 API 密钥

  web_extract:
    provider: "auto"
    model: ""

  compression:
    provider: "auto"
    model: ""

  session_search:
    provider: "auto"
    model: ""

  skills_hub:
    provider: "auto"
    model: ""

  mcp:
    provider: "auto"
    model: ""

  flush_memories:
    provider: "auto"
    model: ""
```

以上每个任务都遵循相同的 **provider / model / base_url** 模式。上下文压缩使用它自己的顶层块：

```yaml
compression:
  summary_provider: main                             # 与辅助任务相同的供应商选项
  summary_model: google/gemini-3-flash-preview
  summary_base_url: null                             # 自定义 OpenAI 兼容端点
```

而备用模型使用：

```yaml
fallback_model:
  provider: openrouter
  model: anthropic/claude-sonnet-4
  # base_url: http://localhost:8000/v1               # 可选的自定义端点
```

三者 — 辅助任务、压缩、备用 — 都以相同的方式工作：设置 `provider` 来选择处理请求的供应商，`model` 来选择哪个模型，`base_url` 指向自定义端点（会覆盖 provider）。

### 辅助任务的供应商选项
这些选项仅适用于 `auxiliary:`、`compression:` 和 `fallback_model:` 配置 —— `"main"` **不是**顶层 `model.provider` 的有效值。对于自定义端点，请在 `model:` 部分使用 `provider: custom`（参见 [AI 提供商](/integrations/providers)）。

| 提供商 | 描述 | 要求 |
|----------|-------------|-------------|
| `"auto"` | 按顺序尝试提供商直到一个可用（默认） | 至少配置了一个提供商 |
| `"openrouter"` | 强制使用 OpenRouter | `OPENROUTER_API_KEY` |
| `"nous"` | 强制使用 Nous Portal | `hermes auth` |
| `"codex"` | 强制使用 Codex OAuth | `hermes model` → Codex |
| `"main"` | 使用主 Agent 所用的任何提供商（仅限辅助任务） | 已配置活跃的主提供商 |
| `"anthropic"` | 强制使用 Anthropic 原生 | `ANTHROPIC_API_KEY` 或 Claude Code 凭据 |

### 直接端点覆盖

对于任何辅助任务，设置 `base_url` 将完全绕过提供商解析，直接将请求发送到该端点：

```yaml
auxiliary:
  vision:
    base_url: "http://localhost:1234/v1"
    api_key: "local-key"
    model: "qwen2.5-vl"
```

`base_url` 的优先级高于 `provider`。Hermes 使用配置的 `api_key` 进行身份验证，如果未设置则回退到 `OPENAI_API_KEY`。它**不会**为自定义端点重用 `OPENROUTER_API_KEY`。

---

## 上下文压缩回退

除了辅助系统，上下文压缩还有一个遗留配置路径：

```yaml
compression:
  summary_provider: "auto"                    # auto | openrouter | nous | main
  summary_model: "google/gemini-3-flash-preview"
```

这等同于配置 `auxiliary.compression.provider` 和 `auxiliary.compression.model`。如果两者都设置了，`auxiliary.compression` 的值优先级更高。

如果没有可用于压缩的提供商，Hermes 会丢弃对话中间轮次而不生成摘要，而不是让会话失败。

---

## 委派任务提供商覆盖

由 `delegate_task` 生成的子 Agent **不**使用主回退模型。但是，为了优化成本，可以将它们路由到不同的提供商:模型组合：

```yaml
delegation:
  provider: "openrouter"                      # 覆盖所有子 Agent 的提供商
  model: "google/gemini-3-flash-preview"      # 覆盖模型
  # base_url: "http://localhost:1234/v1"      # 或使用直接端点
  # api_key: "local-key"
```

完整配置细节请参见 [子 Agent 委派](/user-guide/features/delegation)。

---

## 定时任务提供商

定时任务使用执行时配置的任何提供商运行。它们不支持回退模型。要为定时任务使用不同的提供商，请在定时任务本身上配置 `provider` 和 `model` 覆盖：

```python
cronjob(
    action="create",
    schedule="every 2h",
    prompt="Check server status",
    provider="openrouter",
    model="google/gemini-3-flash-preview"
)
```

完整配置细节请参见 [定时任务 (Cron)](/user-guide/features/cron)。

---

## 总结

| 功能 | 回退机制 | 配置位置 |
|---------|-------------------|----------------|
| 主 Agent 模型 | config.yaml 中的 `fallback_model` —— 出错时一次性故障转移 | `fallback_model:` (顶层) |
| 视觉 | 自动检测链 + 内部 OpenRouter 重试 | `auxiliary.vision` |
| 网页提取 | 自动检测链 + 内部 OpenRouter 重试 | `auxiliary.web_extract` |
| 上下文压缩 | 自动检测链，如果不可用则降级为无摘要 | `auxiliary.compression` 或 `compression.summary_provider` |
| 会话搜索 | 自动检测链 | `auxiliary.session_search` |
| 技能中心 | 自动检测链 | `auxiliary.skills_hub` |
| MCP 助手 | 自动检测链 | `auxiliary.mcp` |
| 内存刷新 | 自动检测链 | `auxiliary.flush_memories` |
| 委派 | 仅提供商覆盖（无自动回退） | `delegation.provider` / `delegation.model` |
| 定时任务 | 仅每任务提供商覆盖（无自动回退） | 每任务的 `provider` / `model` |
