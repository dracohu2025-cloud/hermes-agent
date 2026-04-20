---
title: 后备提供者
description: 当您的主模型不可用时，配置自动故障转移至备用 LLM 提供者。
sidebar_label: 后备提供者
sidebar_position: 8
---

# 后备提供者 {#fallback-providers}

Hermes Agent 拥有三层弹性机制，确保在提供者遇到问题时您的会话仍能继续运行：

1.  **[凭证池](./credential-pools.md)** — 在*同一*提供者的多个 API 密钥间轮换（首先尝试）
2.  **主模型后备** — 当您的主模型失败时，自动切换到*不同*的提供者:模型
3.  **辅助任务后备** — 为视觉、压缩、网页提取等侧边任务提供独立的提供者解析

凭证池处理同一提供者内的轮换（例如，多个 OpenRouter 密钥）。本页涵盖跨提供者的后备机制。两者都是可选的，并且独立工作。

## 主模型后备 {#primary-model-fallback}

当您的主要 LLM 提供者遇到错误时 — 如速率限制、服务器过载、认证失败、连接中断 — Hermes 可以在会话中自动切换到备用的提供者:模型组合，而不会丢失您的对话内容。

### 配置 {#configuration}

在 `~/.hermes/config.yaml` 中添加 `fallback_model` 部分：

```yaml
fallback_model:
  provider: openrouter
  model: anthropic/claude-sonnet-4
```

`provider` 和 `model` 都是**必需的**。如果缺少其中任何一个，后备功能将被禁用。

### 支持的提供者 {#supported-providers}

| 提供者 | 配置值 | 要求 |
|----------|-------|-------------|
| AI Gateway | `ai-gateway` | `AI_GATEWAY_API_KEY` |
| OpenRouter | `openrouter` | `OPENROUTER_API_KEY` |
| Nous Portal | `nous` | `hermes auth` (OAuth) |
| OpenAI Codex | `openai-codex` | `hermes model` (ChatGPT OAuth) |
| GitHub Copilot | `copilot` | `COPILOT_GITHUB_TOKEN`、`GH_TOKEN` 或 `GITHUB_TOKEN` |
| GitHub Copilot ACP | `copilot-acp` | 外部进程（编辑器集成） |
| Anthropic | `anthropic` | `ANTHROPIC_API_KEY` 或 Claude Code 凭证 |
| z.ai / GLM | `zai` | `GLM_API_KEY` |
| Kimi / Moonshot | `kimi-coding` | `KIMI_API_KEY` |
| MiniMax | `minimax` | `MINIMAX_API_KEY` |
| MiniMax (中国) | `minimax-cn` | `MINIMAX_CN_API_KEY` |
| DeepSeek | `deepseek` | `DEEPSEEK_API_KEY` |
| NVIDIA NIM | `nvidia` | `NVIDIA_API_KEY` (可选：`NVIDIA_BASE_URL`) |
| Ollama Cloud | `ollama-cloud` | `OLLAMA_API_KEY` |
| Google Gemini (OAuth) | `google-gemini-cli` | `hermes model` (Google OAuth；可选：`HERMES_GEMINI_PROJECT_ID`) |
| Google AI Studio | `gemini` | `GOOGLE_API_KEY` (别名：`GEMINI_API_KEY`) |
| xAI (Grok) | `xai` (别名 `grok`) | `XAI_API_KEY` (可选：`XAI_BASE_URL`) |
| AWS Bedrock | `bedrock` | 标准 boto3 认证 (`AWS_REGION` + `AWS_PROFILE` 或 `AWS_ACCESS_KEY_ID`) |
| Qwen Portal (OAuth) | `qwen-oauth` | `hermes model` (Qwen Portal OAuth；可选：`HERMES_QWEN_BASE_URL`) |
| OpenCode Zen | `opencode-zen` | `OPENCODE_ZEN_API_KEY` |
| OpenCode Go | `opencode-go` | `OPENCODE_GO_API_KEY` |
| Kilo Code | `kilocode` | `KILOCODE_API_KEY` |
| Xiaomi MiMo | `xiaomi` | `XIAOMI_API_KEY` |
| Arcee AI | `arcee` | `ARCEEAI_API_KEY` |
| Alibaba / DashScope | `alibaba` | `DASHSCOPE_API_KEY` |
| Hugging Face | `huggingface` | `HF_TOKEN` |
| 自定义端点 | `custom` | `base_url` + `key_env` (见下文) |

### 自定义端点后备 {#custom-endpoint-fallback}

对于自定义的 OpenAI 兼容端点，添加 `base_url` 和可选的 `key_env`：

```yaml
fallback_model:
  provider: custom
  model: my-local-model
  base_url: http://localhost:8000/v1
  key_env: MY_LOCAL_KEY              # 包含 API 密钥的环境变量名称
```

### 后备触发时机 {#when-fallback-triggers}

当主模型因以下原因失败时，后备机制会自动激活：

- **速率限制** (HTTP 429) — 在重试尝试耗尽后
- **服务器错误** (HTTP 500, 502, 503) — 在重试尝试耗尽后
- **认证失败** (HTTP 401, 403) — 立即（无需重试）
- **未找到** (HTTP 404) — 立即
- **无效响应** — 当 API 重复返回格式错误或空响应时

触发后，Hermes 会：

1.  解析后备提供者的凭证
2.  构建一个新的 API 客户端
3.  原地替换模型、提供者和客户端
4.  重置重试计数器并继续对话

切换是无缝的 — 您的对话历史、工具调用和上下文都会被保留。Agent 会从它中断的地方继续，只是使用了不同的模型。
:::info 一次性生效
每个会话中，后备方案**最多激活一次**。如果后备提供者也失败了，则交由常规错误处理接管（重试，然后显示错误信息）。这可以防止级联故障转移循环。
:::

### 示例 {#examples}
<a id="one-shot"></a>

**将 OpenRouter 作为 Anthropic 原生接口的后备：**
```yaml
model:
  provider: anthropic
  default: claude-sonnet-4-6

fallback_model:
  provider: openrouter
  model: anthropic/claude-sonnet-4
```

**将 Nous Portal 作为 OpenRouter 的后备：**
```yaml
model:
  provider: openrouter
  default: anthropic/claude-opus-4

fallback_model:
  provider: nous
  model: nous-hermes-3
```

**将本地模型作为云端模型的后备：**
```yaml
fallback_model:
  provider: custom
  model: llama-3.1-70b
  base_url: http://localhost:8000/v1
  key_env: LOCAL_API_KEY
```

**将 Codex OAuth 作为后备：**
```yaml
fallback_model:
  provider: openai-codex
  model: gpt-5.3-codex
```

### 后备方案生效的场景 {#where-fallback-works}

| 场景 | 是否支持后备方案 |
|---------|-------------------|
| CLI 会话 | ✔ |
| 消息网关（Telegram、Discord 等） | ✔ |
| 子 Agent 委托 | ✘（子 Agent 不继承后备配置） |
| 定时任务 | ✘（使用固定的提供者运行） |
| 辅助任务（视觉、压缩） | ✘（使用它们自己的提供者链 — 见下文） |

:::tip
`fallback_model` 没有对应的环境变量 — 它完全通过 `config.yaml` 配置。这是有意为之：后备配置是一个深思熟虑的选择，不应被过时的 shell 环境变量覆盖。
:::

---

## 辅助任务的后备方案 {#auxiliary-task-fallback}

Hermes 为辅助任务使用独立的轻量级模型。每个任务都有自己的提供者解析链，这相当于一个内置的后备系统。

### 具有独立提供者解析的任务 {#tasks-with-independent-provider-resolution}

| 任务 | 功能 | 配置键 |
|------|-------------|-----------|
| Vision | 图像分析、浏览器截图 | `auxiliary.vision` |
| Web Extract | 网页摘要 | `auxiliary.web_extract` |
| Compression | 上下文压缩摘要 | `auxiliary.compression` |
| Session Search | 历史会话摘要 | `auxiliary.session_search` |
| Skills Hub | 技能搜索与发现 | `auxiliary.skills_hub` |
| MCP | MCP 辅助操作 | `auxiliary.mcp` |
| Memory Flush | 记忆整合 | `auxiliary.flush_memories` |
| Approval | 智能命令审批分类 | `auxiliary.approval` |
| Title Generation | 会话标题摘要 | `auxiliary.title_generation` |

### 自动检测链 {#auto-detection-chain}

当一个任务的提供者设置为 `"auto"`（默认值）时，Hermes 会按顺序尝试各个提供者，直到有一个可用：

**对于文本任务（压缩、网页提取等）：**

```text
OpenRouter → Nous Portal → 自定义端点 → Codex OAuth →
API-key 提供者（z.ai、Kimi、MiniMax、小米 MiMo、Hugging Face、Anthropic）→ 放弃
```

**对于视觉任务：**

```text
主提供者（如果支持视觉）→ OpenRouter → Nous Portal →
Codex OAuth → Anthropic → 自定义端点 → 放弃
```

如果解析出的提供者在调用时失败，Hermes 还有一个内部重试机制：如果该提供者不是 OpenRouter 且没有设置明确的 `base_url`，它会将 OpenRouter 作为最后的后备方案进行尝试。

### 配置辅助任务提供者 {#configuring-auxiliary-providers}

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

以上每个任务都遵循相同的 **provider / model / base_url** 模式。上下文压缩在 `auxiliary.compression` 下配置：

```yaml
auxiliary:
  compression:
    provider: main                                    # 与其他辅助任务相同的提供者选项
    model: google/gemini-3-flash-preview
    base_url: null                                    # 自定义 OpenAI 兼容端点
```
而备用模型使用：

```yaml
fallback_model:
  provider: openrouter
  model: anthropic/claude-sonnet-4
  # base_url: http://localhost:8000/v1               # 可选自定义端点
```

所有这三项——辅助任务、压缩、备用——的工作方式相同：设置 `provider` 来选择由谁处理请求，`model` 来选择哪个模型，`base_url` 来指向一个自定义端点（会覆盖 provider）。

### 辅助任务的 Provider 选项 {#provider-options-for-auxiliary-tasks}

这些选项仅适用于 `auxiliary:`、`compression:` 和 `fallback_model:` 配置——`"main"` **不是** 顶级 `model.provider` 的有效值。对于自定义端点，请在 `model:` 部分使用 `provider: custom`（参见 [AI Providers](/integrations/providers)）。

| Provider | 描述 | 要求 |
|----------|-------------|-------------|
| `"auto"` | 按顺序尝试 providers 直到一个可用（默认） | 至少配置了一个 provider |
| `"openrouter"` | 强制使用 OpenRouter | `OPENROUTER_API_KEY` |
| `"nous"` | 强制使用 Nous Portal | `hermes auth` |
| `"codex"` | 强制使用 Codex OAuth | `hermes model` → Codex |
| `"main"` | 使用主 Agent 所用的 provider（仅限辅助任务） | 已配置活跃的主 provider |
| `"anthropic"` | 强制使用 Anthropic 原生 API | `ANTHROPIC_API_KEY` 或 Claude Code 凭据 |

### 直接端点覆盖 {#direct-endpoint-override}

对于任何辅助任务，设置 `base_url` 会完全绕过 provider 解析，直接将请求发送到该端点：

```yaml
auxiliary:
  vision:
    base_url: "http://localhost:1234/v1"
    api_key: "local-key"
    model: "qwen2.5-vl"
```

`base_url` 的优先级高于 `provider`。Hermes 使用配置的 `api_key` 进行身份验证，如果未设置则回退到 `OPENAI_API_KEY`。它 **不会** 为自定义端点重用 `OPENROUTER_API_KEY`。

---

## 上下文压缩备用 {#context-compression-fallback}

上下文压缩使用 `auxiliary.compression` 配置块来控制哪个模型和 provider 处理摘要生成：

```yaml
auxiliary:
  compression:
    provider: "auto"                              # auto | openrouter | nous | main
    model: "google/gemini-3-flash-preview"
```

:::info 旧配置迁移
带有 `compression.summary_model` / `compression.summary_provider` / `compression.summary_base_url` 的旧配置会在首次加载时自动迁移到 `auxiliary.compression.*`（配置版本 17）。
:::
<a id="legacy-migration"></a>

如果没有可用的 provider 用于压缩，Hermes 会丢弃中间对话轮次而不生成摘要，而不是让会话失败。

---

## 委派 Provider 覆盖 {#delegation-provider-override}

由 `delegate_task` 生成的子 Agent **不** 使用主备用模型。但是，为了优化成本，可以将它们路由到不同的 provider:model 组合：

```yaml
delegation:
  provider: "openrouter"                      # 覆盖所有子 Agent 的 provider
  model: "google/gemini-3-flash-preview"      # 覆盖模型
  # base_url: "http://localhost:1234/v1"      # 或使用直接端点
  # api_key: "local-key"
```

完整配置细节请参见 [Subagent Delegation](/user-guide/features/delegation)。

---

## Cron 任务 Providers {#cron-job-providers}

Cron 任务在运行时使用当时配置的 provider 执行。它们不支持备用模型。要为 cron 任务使用不同的 provider，请在 cron 任务本身上配置 `provider` 和 `model` 覆盖：

```python
cronjob(
    action="create",
    schedule="every 2h",
    prompt="Check server status",
    provider="openrouter",
    model="google/gemini-3-flash-preview"
)
```

完整配置细节请参见 [Scheduled Tasks (Cron)](/user-guide/features/cron)。

---

## 总结 {#summary}

| 功能 | 备用机制 | 配置位置 |
|---------|-------------------|----------------|
| 主 Agent 模型 | 在 config.yaml 中的 `fallback_model` —— 出错时一次性故障转移 | `fallback_model:` (顶级) |
| 视觉 | 自动检测链 + 内部 OpenRouter 重试 | `auxiliary.vision` |
| 网页提取 | 自动检测链 + 内部 OpenRouter 重试 | `auxiliary.web_extract` |
| 上下文压缩 | 自动检测链，如果不可用则降级为无摘要 | `auxiliary.compression` |
| 会话搜索 | 自动检测链 | `auxiliary.session_search` |
| 技能中心 | 自动检测链 | `auxiliary.skills_hub` |
| MCP 助手 | 自动检测链 | `auxiliary.mcp` |
| 记忆刷新 | 自动检测链 | `auxiliary.flush_memories` |
| 审批分类 | 自动检测链 | `auxiliary.approval` |
| 标题生成 | 自动检测链 | `auxiliary.title_generation` |
| 委派 | 仅 Provider 覆盖（无自动备用） | `delegation.provider` / `delegation.model` |
| Cron 任务 | 仅每个任务的 provider 覆盖（无自动备用） | 每个任务的 `provider` / `model` |
