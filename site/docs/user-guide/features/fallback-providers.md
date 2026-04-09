---
title: 备用提供商 (Fallback Providers)
description: 当您的主要模型不可用时，配置自动故障转移到备用 LLM 提供商。
sidebar_label: 备用提供商
sidebar_position: 8
---

# 备用提供商 (Fallback Providers)

Hermes Agent 具有三层弹性机制，可在提供商遇到问题时保持您的会话正常运行：

1. **[凭据池 (Credential pools)](./credential-pools.md)** — 在*同一*提供商的多个 API 密钥之间轮换（优先尝试）
2. **主模型回退 (Primary model fallback)** — 当您的主模型失败时，自动切换到*不同*的提供商:模型组合
3. **辅助任务回退 (Auxiliary task fallback)** — 针对视觉、压缩和网页提取等辅助任务的独立提供商解析

凭据池处理同提供商轮换（例如，多个 OpenRouter 密钥）。本页面介绍跨提供商回退。两者均为可选，且独立工作。

## 主模型回退 (Primary Model Fallback)

当您的主 LLM 提供商遇到错误（如速率限制、服务器过载、身份验证失败、连接中断）时，Hermes 可以在会话期间自动切换到备用提供商:模型组合，而不会丢失您的对话。

### 配置

在 `~/.hermes/config.yaml` 中添加 `fallback_model` 部分：

```yaml
fallback_model:
  provider: openrouter
  model: anthropic/claude-sonnet-4
```

`provider` 和 `model` 均为**必填项**。如果缺少其中任何一项，回退功能将被禁用。

### 支持的提供商

| 提供商 | 值 | 要求 |
|----------|-------|-------------|
| AI Gateway | `ai-gateway` | `AI_GATEWAY_API_KEY` |
| OpenRouter | `openrouter` | `OPENROUTER_API_KEY` |
| Nous Portal | `nous` | `hermes auth` (OAuth) |
| OpenAI Codex | `openai-codex` | `hermes model` (ChatGPT OAuth) |
| GitHub Copilot | `copilot` | `COPILOT_GITHUB_TOKEN`, `GH_TOKEN`, 或 `GITHUB_TOKEN` |
| GitHub Copilot ACP | `copilot-acp` | 外部进程（编辑器集成） |
| Anthropic | `anthropic` | `ANTHROPIC_API_KEY` 或 Claude Code 凭据 |
| z.ai / GLM | `zai` | `GLM_API_KEY` |
| Kimi / Moonshot | `kimi-coding` | `KIMI_API_KEY` |
| MiniMax | `minimax` | `MINIMAX_API_KEY` |
| MiniMax (China) | `minimax-cn` | `MINIMAX_CN_API_KEY` |
| DeepSeek | `deepseek` | `DEEPSEEK_API_KEY` |
| OpenCode Zen | `opencode-zen` | `OPENCODE_ZEN_API_KEY` |
| OpenCode Go | `opencode-go` | `OPENCODE_GO_API_KEY` |
| Kilo Code | `kilocode` | `KILOCODE_API_KEY` |
| Alibaba / DashScope | `alibaba` | `DASHSCOPE_API_KEY` |
| Hugging Face | `huggingface` | `HF_TOKEN` |
| 自定义端点 | `custom` | `base_url` + `api_key_env` (见下文) |

### 自定义端点回退

对于兼容 OpenAI 的自定义端点，请添加 `base_url` 以及可选的 `api_key_env`：

```yaml
fallback_model:
  provider: custom
  model: my-local-model
  base_url: http://localhost:8000/v1
  api_key_env: MY_LOCAL_KEY          # 包含 API 密钥的环境变量名称
```

### 回退触发时机

当主模型出现以下错误时，回退会自动激活：

- **速率限制** (HTTP 429) — 在耗尽重试次数后
- **服务器错误** (HTTP 500, 502, 503) — 在耗尽重试次数后
- **身份验证失败** (HTTP 401, 403) — 立即触发（重试无意义）
- **未找到** (HTTP 404) — 立即触发
- **无效响应** — 当 API 反复返回格式错误或空响应时

触发时，Hermes 会：

1. 解析备用提供商的凭据
2. 构建新的 API 客户端
3. 原位替换模型、提供商和客户端
4. 重置重试计数器并继续对话

切换过程是无缝的——您的对话历史、工具调用和上下文都会被保留。Agent 会从中断的地方继续执行，只是换用了不同的模型。

:::info 一次性触发
回退在每个会话中**最多激活一次**。如果备用提供商也失败了，将采用常规错误处理（重试，然后报错）。这可以防止级联故障循环。
:::

### 示例

**以 OpenRouter 作为 Anthropic 原生模型的备用：**
```yaml
model:
  provider: anthropic
  default: claude-sonnet-4-6

fallback_model:
  provider: openrouter
  model: anthropic/claude-sonnet-4
```

**以 Nous Portal 作为 OpenRouter 的备用：**
```yaml
model:
  provider: openrouter
  default: anthropic/claude-opus-4

fallback_model:
  provider: nous
  model: nous-hermes-3
```

**以本地模型作为云端模型的备用：**
```yaml
fallback_model:
  provider: custom
  model: llama-3.1-70b
  base_url: http://localhost:8000/v1
  api_key_env: LOCAL_API_KEY
```

**以 Codex OAuth 作为备用：**
```yaml
fallback_model:
  provider: openai-codex
  model: gpt-5.3-codex
```

### 回退适用范围

| 上下文 | 是否支持回退 |
|---------|-------------------|
| CLI 会话 | ✔ |
| 消息网关 (Telegram, Discord 等) | ✔ |
| 子 Agent 委派 (Subagent delegation) | ✘ (子 Agent 不会继承回退配置) |
| 定时任务 (Cron jobs) | ✘ (以固定提供商运行) |
| 辅助任务 (视觉、压缩) | ✘ (使用它们自己的提供商链 — 见下文) |

:::tip
`fallback_model` 没有对应的环境变量——它只能通过 `config.yaml` 进行配置。这是有意为之：回退配置是一个慎重的选择，不应被过期的 shell 导出变量所覆盖。
:::

---

## 辅助任务回退 (Auxiliary Task Fallback)

Hermes 为辅助任务使用单独的轻量级模型。每个任务都有自己的提供商解析链，作为内置的回退系统。

### 具有独立提供商解析的任务

| 任务 | 功能 | 配置键 |
|------|-------------|-----------|
| 视觉 (Vision) | 图像分析、浏览器截图 | `auxiliary.vision` |
| 网页提取 (Web Extract) | 网页摘要 | `auxiliary.web_extract` |
| 压缩 (Compression) | 上下文压缩摘要 | `auxiliary.compression` 或 `compression.summary_provider` |
| 会话搜索 (Session Search) | 历史会话摘要 | `auxiliary.session_search` |
| 技能中心 (Skills Hub) | 技能搜索与发现 | `auxiliary.skills_hub` |
| MCP | MCP 辅助操作 | `auxiliary.mcp` |
| 内存清理 (Memory Flush) | 内存整合 | `auxiliary.flush_memories` |

### 自动检测链

当任务的提供商设置为 `"auto"`（默认值）时，Hermes 会按顺序尝试提供商，直到有一个成功为止：

**对于文本任务（压缩、网页提取等）：**

```text
OpenRouter → Nous Portal → 自定义端点 → Codex OAuth →
API 密钥提供商 (z.ai, Kimi, MiniMax, Hugging Face, Anthropic) → 放弃
```

**对于视觉任务：**

```text
主提供商 (如果具备视觉能力) → OpenRouter → Nous Portal →
Codex OAuth → Anthropic → 自定义端点 → 放弃
```

如果解析出的提供商在调用时失败，Hermes 还有内部重试机制：如果提供商不是 OpenRouter 且未设置明确的 `base_url`，它会尝试将 OpenRouter 作为最后的备用方案。

### 配置辅助提供商

每个任务都可以在 `config.yaml` 中独立配置：

```yaml
auxiliary:
  vision:
    provider: "auto"              # auto | openrouter | nous | codex | main | anthropic
    model: ""                     # 例如 "openai/gpt-4o"
    base_url: ""                  # 直接端点（优先级高于 provider）
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

上述每个任务都遵循相同的 **provider / model / base_url** 模式。上下文压缩使用其自己的顶层代码块：

```yaml
compression:
  summary_provider: main                             # 与辅助任务相同的提供商选项
  summary_model: google/gemini-3-flash-preview
  summary_base_url: null                             # 兼容 OpenAI 的自定义端点
```

回退模型使用：

```yaml
fallback_model:
  provider: openrouter
  model: anthropic/claude-sonnet-4
  # base_url: http://localhost:8000/v1               # 可选的自定义端点
```

所有这三者（辅助、压缩、回退）的工作方式相同：设置 `provider` 来选择处理请求的对象，设置 `model` 来选择模型，设置 `base_url` 来指向自定义端点（会覆盖 provider）。

### 辅助任务的提供商选项

这些选项仅适用于 `auxiliary:`、`compression:` 和 `fallback_model:` 配置——`"main"` 对于您的顶层 `model.provider` 而言**不是**有效值。对于自定义端点，请在您的 `model:` 部分使用 `provider: custom`（参见 [AI 提供商](/integrations/providers)）。
| 提供商 (Provider) | 描述 | 要求 |
|----------|-------------|-------------|
| `"auto"` | 按顺序尝试提供商，直到有一个可用（默认） | 至少配置一个提供商 |
| `"openrouter"` | 强制使用 OpenRouter | `OPENROUTER_API_KEY` |
| `"nous"` | 强制使用 Nous Portal | `hermes auth` |
| `"codex"` | 强制使用 Codex OAuth | `hermes model` → Codex |
| `"main"` | 使用主 Agent 所用的提供商（仅限辅助任务） | 已配置有效的主提供商 |
| `"anthropic"` | 强制使用 Anthropic 原生接口 | `ANTHROPIC_API_KEY` 或 Claude Code 凭据 |

### 直接端点覆盖 (Direct Endpoint Override)

对于任何辅助任务，设置 `base_url` 将完全绕过提供商解析，直接向该端点发送请求：

```yaml
auxiliary:
  vision:
    base_url: "http://localhost:1234/v1"
    api_key: "local-key"
    model: "qwen2.5-vl"
```

`base_url` 的优先级高于 `provider`。Hermes 会使用配置的 `api_key` 进行身份验证，如果未设置，则回退到 `OPENROUTER_API_KEY`。它**不会**将 `OPENROUTER_API_KEY` 用于自定义端点。

---

## 上下文压缩回退 (Context Compression Fallback)

除了辅助系统外，上下文压缩还有一个旧版的配置路径：

```yaml
compression:
  summary_provider: "auto"                    # auto | openrouter | nous | main
  summary_model: "google/gemini-3-flash-preview"
```

这等同于配置 `auxiliary.compression.provider` 和 `auxiliary.compression.model`。如果两者都已设置，则 `auxiliary.compression` 的值具有优先权。

如果没有任何提供商可用于压缩，Hermes 会直接丢弃对话中间的轮次，而不生成摘要，从而避免会话失败。

---

## 委派提供商覆盖 (Delegation Provider Override)

由 `delegate_task` 产生的子 Agent **不会**使用主回退模型。但是，为了优化成本，可以将它们路由到不同的“提供商:模型”组合：

```yaml
delegation:
  provider: "openrouter"                      # 覆盖所有子 Agent 的提供商
  model: "google/gemini-3-flash-preview"      # 覆盖模型
  # base_url: "http://localhost:1234/v1"      # 或者使用直接端点
  # api_key: "local-key"
```

有关完整配置详情，请参阅 [子 Agent 委派 (Subagent Delegation)](/user-guide/features/delegation)。

---

## 定时任务提供商 (Cron Job Providers)

定时任务 (Cron jobs) 在执行时会使用当时配置的任何提供商。它们不支持回退模型。若要为定时任务使用不同的提供商，请在定时任务本身上配置 `provider` 和 `model` 覆盖：

```python
cronjob(
    action="create",
    schedule="every 2h",
    prompt="Check server status",
    provider="openrouter",
    model="google/gemini-3-flash-preview"
)
```

有关完整配置详情，请参阅 [定时任务 (Cron)](/user-guide/features/cron)。

---

## 总结

| 功能 | 回退机制 | 配置位置 |
|---------|-------------------|----------------|
| 主 Agent 模型 | `config.yaml` 中的 `fallback_model` — 出错时一次性故障转移 | `fallback_model:` (顶层) |
| 视觉 (Vision) | 自动检测链 + 内部 OpenRouter 重试 | `auxiliary.vision` |
| 网页提取 | 自动检测链 + 内部 OpenRouter 重试 | `auxiliary.web_extract` |
| 上下文压缩 | 自动检测链，不可用时降级为不生成摘要 | `auxiliary.compression` 或 `compression.summary_provider` |
| 会话搜索 | 自动检测链 | `auxiliary.session_search` |
| 技能中心 (Skills hub) | 自动检测链 | `auxiliary.skills_hub` |
| MCP 助手 | 自动检测链 | `auxiliary.mcp` |
| 内存清理 | 自动检测链 | `auxiliary.flush_memories` |
| 委派 (Delegation) | 仅提供商覆盖（无自动回退） | `delegation.provider` / `delegation.model` |
| 定时任务 | 仅单任务提供商覆盖（无自动回退） | 单任务 `provider` / `model` |
