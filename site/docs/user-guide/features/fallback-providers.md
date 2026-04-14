---
title: 后备服务提供商
description: 当你的主要模型不可用时，配置自动故障转移至备用 LLM 服务提供商。
sidebar_label: 后备服务提供商
sidebar_position: 8
---

# 后备服务提供商

Hermes Agent 拥有三层韧性机制，确保服务提供商遇到问题时你的会话仍能持续运行：

1. **[凭证池](./credential-pools.md)** — 在同一提供商内轮换多个 API 密钥（优先尝试）
2. **主要模型后备** — 当你的主模型失败时，自动切换到另一家提供商:模型组合
3. **辅助任务后备** — 为侧边任务（如视觉、压缩和网页提取）提供独立的提供商解析机制

凭证池处理同一提供商内的轮换（例如多个 OpenRouter 密钥）。本文介绍跨提供商的后备机制。两者都是可选的，且独立工作。

## 主要模型后备

当你的主要 LLM 提供商遇到错误（如速率限制、服务器过载、认证失败、连接断开）时，Hermes 可以在会话中途自动切换到备份的提供商:模型组合，而不丢失你的对话内容。

### 配置

在 `~/.hermes/config.yaml` 中添加一个 `fallback_model` 部分：

```yaml
fallback_model:
  provider: openrouter
  model: anthropic/claude-sonnet-4
```

`provider` 和 `model` 都是**必需的**。如果缺少任何一个，后备机制将被禁用。

### 支持的提供商

| 提供商 | 配置值 | 要求 |
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

### 自定义端点后备

对于自定义的 OpenAI 兼容端点，添加 `base_url` 和可选的 `api_key_env`：

```yaml
fallback_model:
  provider: custom
  model: my-local-model
  base_url: http://localhost:8000/v1
  api_key_env: MY_LOCAL_KEY          # 包含 API 密钥的环境变量名
```

### 后备触发时机

后备机制会在主要模型因以下原因失败时自动激活：

- **速率限制** (HTTP 429) — 在耗尽重试次数后
- **服务器错误** (HTTP 500, 502, 503) — 在耗尽重试次数后
- **认证失败** (HTTP 401, 403) — 立即（无需重试）
- **找不到** (HTTP 404) — 立即
- **无效响应** — 当 API 多次返回格式错误或空响应时

触发时，Hermes 会：

1. 解析后备提供商的凭证
2. 构建一个新的 API 客户端
3. 原地替换模型、提供商和客户端
4. 重置重试计数器并继续对话

切换是无缝的 — 你的对话历史、工具调用和上下文都会被保留。Agent 会从它中断的地方继续执行，只是使用了一个不同的模型。

:::info 单次后备
后备机制在每个会话中**最多激活一次**。如果后备提供商也失败了，则正常的错误处理机制接管（重试，然后是错误信息）。这防止了级联故障转移循环。
:::

### 示例

**OpenRouter 作为 Anthropic 原生提供商的后备：**
```yaml
model:
  provider: anthropic
  default: claude-sonnet-4-6

fallback_model:
  provider: openrouter
  model: anthropic/claude-sonnet-4
```

**Nous Portal 作为 OpenRouter 的后备：**
```yaml
model:
  provider: openrouter
  default: anthropic/claude-opus-4

fallback_model:
  provider: nous
  model: nous-hermes-3
```

**本地模型作为云服务的后备：**
```yaml
fallback_model:
  provider: custom
  model: llama-3.1-70b
  base_url: http://localhost:8000/v1
  api_key_env: LOCAL_API_KEY
```

**Codex OAuth 作为后备：**
```yaml
fallback_model:
  provider: openai-codex
  model: gpt-5.3-codex
```

### 后备适用场景

| 场景 | 是否支持后备 |
|---------|-------------------|
| CLI 会话 | ✔ |
| 消息网关（Telegram, Discord 等） | ✔ |
| 子 Agent 委派 | ✘（子 Agent 不继承后备配置） |
| 定时任务 | ✘（使用固定的提供商运行） |
| 辅助任务（视觉、压缩） | ✘（使用它们自己的提供商链 — 见下文） |

:::tip
`fallback_model` 没有环境变量 — 它仅通过 `config.yaml` 配置。这是有意为之的：后备配置是一个深思熟虑的选择，不应被过期的 shell 导出变量覆盖。
:::

---

## 辅助任务后备

Hermes 为侧边任务使用独立的轻量级模型。每个任务都有其自己的提供商解析链，充当内置的后备系统。

### 具有独立提供商解析的任务

| 任务 | 功能 | 配置键 |
|------|-------------|-----------|
| 视觉 | 图像分析、浏览器截图 | `auxiliary.vision` |
| 网页提取 | 网页摘要 | `auxiliary.web_extract` |
| 压缩 | 上下文压缩摘要 | `auxiliary.compression` |
| 会话搜索 | 过往会话摘要 | `auxiliary.session_search` |
| 技能中心 | 技能搜索与发现 | `auxiliary.skills_hub` |
| MCP | MCP 辅助操作 | `auxiliary.mcp` |
| 记忆刷新 | 记忆整合 | `auxiliary.flush_memories` |

### 自动检测链

当任务的提供商设置为 `"auto"`（默认值）时，Hermes 会按顺序尝试提供商直到一个可用：

**对于文本任务（压缩、网页提取等）：**

```text
OpenRouter → Nous Portal → 自定义端点 → Codex OAuth →
API-key providers (z.ai, Kimi, MiniMax, Xiaomi MiMo, Hugging Face, Anthropic) → 放弃
```

**对于视觉任务：**

```text
主提供商（如果具备视觉能力） → OpenRouter → Nous Portal →
Codex OAuth → Anthropic → 自定义端点 → 放弃
```

如果解析出的提供商在调用时失败，Hermes 还有一个内部重试机制：如果提供商不是 OpenRouter 且没有设置显式的 `base_url`，它会尝试 OpenRouter 作为最后的备用后备。

### 配置辅助任务提供商

每个任务可以在 `config.yaml` 中独立配置：

```yaml
auxiliary:
  vision:
    provider: "auto"              # auto | openrouter | nous | codex | main | anthropic
    model: ""                     # 例如 "openai/gpt-4o"
    base_url: ""                  # 直接端点（优先于 provider）
    api_key: ""                   # 用于 base_url 的 API 密钥

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

以上每个任务都遵循相同的**provider / model / base_url** 模式。上下文压缩在 `auxiliary.compression` 下配置：

```yaml
auxiliary:
  compression:
    provider: main                                    # 与其他辅助任务相同的提供商选项
    model: google/gemini-3-flash-preview
    base_url: null                                    # 自定义 OpenAI 兼容端点
```

而后备模型使用：

```yaml
fallback_model:
  provider: openrouter
  model: anthropic/claude-sonnet-4
  # base_url: http://localhost:8000/v1               # 可选的自定义端点
```

所有三者 — 辅助任务、压缩、后备 — 都以相同的方式工作：设置 `provider` 来选择处理请求的对象，`model` 来选择哪个模型，`base_url` 指向自定义端点（覆盖 provider）。

### 辅助任务的提供商选项
这些选项仅适用于 `auxiliary:`、`compression:` 和 `fallback_model:` 配置 —— `"main"` **不是**顶级 `model.provider` 的有效值。对于自定义端点，请在 `model:` 部分使用 `provider: custom`（参见 [AI 提供商](/integrations/providers)）。

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

上下文压缩使用 `auxiliary.compression` 配置块来控制哪个模型和提供商处理摘要生成：

```yaml
auxiliary:
  compression:
    provider: "auto"                              # auto | openrouter | nous | main
    model: "google/gemini-3-flash-preview"
```

:::info 旧版迁移
带有 `compression.summary_model` / `compression.summary_provider` / `compression.summary_base_url` 的旧配置在首次加载时会自动迁移到 `auxiliary.compression.*`（配置版本 17）。
:::

如果没有可用的提供商进行压缩，Hermes 会丢弃中间对话轮次而不生成摘要，而不是让会话失败。

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
| 主 Agent 模型 | config.yaml 中的 `fallback_model` —— 出错时一次性故障转移 | `fallback_model:` (顶级) |
| 视觉 | 自动检测链 + 内部 OpenRouter 重试 | `auxiliary.vision` |
| 网页提取 | 自动检测链 + 内部 OpenRouter 重试 | `auxiliary.web_extract` |
| 上下文压缩 | 自动检测链，如果不可用则降级为无摘要 | `auxiliary.compression` |
| 会话搜索 | 自动检测链 | `auxiliary.session_search` |
| 技能中心 | 自动检测链 | `auxiliary.skills_hub` |
| MCP 助手 | 自动检测链 | `auxiliary.mcp` |
| 内存刷新 | 自动检测链 | `auxiliary.flush_memories` |
| 委派 | 仅提供商覆盖（无自动回退） | `delegation.provider` / `delegation.model` |
| 定时任务 | 仅每任务提供商覆盖（无自动回退） | 每任务的 `provider` / `model` |
