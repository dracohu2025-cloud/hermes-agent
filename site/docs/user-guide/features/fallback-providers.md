---
title: 回退提供商
description: 当主模型不可用时，自动切换到备用 LLM 提供商。
sidebar_label: 回退提供商
sidebar_position: 8
---

# 回退提供商 {#fallback-providers}

Hermes Agent 拥有三层弹性机制，可在提供商出现问题时保持会话正常运行：

1. **[凭证池](./credential-pools.md)** — 在*同一*提供商的不同 API 密钥之间轮换（优先尝试）
2. **主模型回退** — 当主模型失败时，自动切换到*不同的*提供商:模型组合
3. **辅助任务回退** — 为视觉、压缩、网页提取等辅助任务独立解析提供商

凭证池处理同一提供商内的轮换（例如多个 OpenRouter 密钥）。本页介绍跨提供商回退。两者均为可选，且独立工作。

## 主模型回退 {#primary-model-fallback}

当主 LLM 提供商遇到错误（速率限制、服务器过载、认证失败、连接断开）时，Hermes 可以在会话中自动切换到备用提供商:模型组合，而不会丢失对话。

### 配置 {#configuration}

最简单的方式是通过交互式管理器：

```bash
hermes fallback
```

`hermes fallback` 复用了 `hermes model` 的提供商选择器——相同的提供商列表、相同的凭证提示、相同的验证。按 `a` 添加回退，`↑`/`↓` 调整顺序，`d` 删除，`q` 保存并退出。更改会持久化到 `config.yaml` 中的 `model.fallback_providers` 下。

如果你更愿意直接编辑 YAML，可以在 `~/.hermes/config.yaml` 中添加 `fallback_model` 部分：

```yaml
fallback_model:
  provider: openrouter
  model: anthropic/claude-sonnet-4
```

`provider` 和 `model` 都是**必需的**。如果缺少任意一个，回退将被禁用。
:::note `fallback_model` 与 `fallback_providers`
<a id="fallbackmodel-vs-fallbackproviders"></a>
`fallback_model`（单数）是旧的单回退键——Hermes 仍保留它以保持向后兼容。`fallback_providers`（复数，列表）支持按顺序尝试多个回退；`hermes fallback` 会写入此键。当两者都设置时，Hermes 会合并它们，其中 `fallback_providers` 优先。
:::

### 支持的提供商 {#supported-providers}

| 提供商 | 值 | 要求 |
|----------|-------|-------------|
| AI Gateway | `ai-gateway` | `AI_GATEWAY_API_KEY` |
| OpenRouter | `openrouter` | `OPENROUTER_API_KEY` |
| Nous Portal | `nous` | `hermes auth`（OAuth） |
| OpenAI Codex | `openai-codex` | `hermes model`（ChatGPT OAuth） |
| GitHub Copilot | `copilot` | `COPILOT_GITHUB_TOKEN`、`GH_TOKEN` 或 `GITHUB_TOKEN` |
| GitHub Copilot ACP | `copilot-acp` | 外部进程（编辑器集成） |
| Anthropic | `anthropic` | `ANTHROPIC_API_KEY` 或 Claude Code 凭据 |
| z.ai / GLM | `zai` | `GLM_API_KEY` |
| Kimi / Moonshot | `kimi-coding` | `KIMI_API_KEY` |
| MiniMax | `minimax` | `MINIMAX_API_KEY` |
| MiniMax（中国） | `minimax-cn` | `MINIMAX_CN_API_KEY` |
| DeepSeek | `deepseek` | `DEEPSEEK_API_KEY` |
| NVIDIA NIM | `nvidia` | `NVIDIA_API_KEY`（可选：`NVIDIA_BASE_URL`） |
| Ollama Cloud | `ollama-cloud` | `OLLAMA_API_KEY` |
| Google Gemini（OAuth） | `google-gemini-cli` | `hermes model`（Google OAuth；可选：`HERMES_GEMINI_PROJECT_ID`） |
| Google AI Studio | `gemini` | `GOOGLE_API_KEY`（别名：`GEMINI_API_KEY`） |
| xAI（Grok） | `xai`（别名 `grok`） | `XAI_API_KEY`（可选：`XAI_BASE_URL`） |
| AWS Bedrock | `bedrock` | 标准 boto3 认证（`AWS_REGION` + `AWS_PROFILE` 或 `AWS_ACCESS_KEY_ID`） |
| Qwen Portal（OAuth） | `qwen-oauth` | `hermes model`（Qwen Portal OAuth；可选：`HERMES_QWEN_BASE_URL`） |
| MiniMax（OAuth） | `minimax-oauth` | `hermes model`（MiniMax 门户 OAuth） |
| OpenCode Zen | `opencode-zen` | `OPENCODE_ZEN_API_KEY` |
| OpenCode Go | `opencode-go` | `OPENCODE_GO_API_KEY` |
| Kilo Code | `kilocode` | `KILOCODE_API_KEY` |
| 小米 MiMo | `xiaomi` | `XIAOMI_API_KEY` |
| Arcee AI | `arcee` | `ARCEEAI_API_KEY` |
| GMI Cloud | `gmi` | `GMI_API_KEY` |
| 阿里云 / DashScope | `alibaba` | `DASHSCOPE_API_KEY` |
| 阿里云编码计划 | `alibaba-coding-plan` | `ALIBABA_CODING_PLAN_API_KEY`（回退到 `DASHSCOPE_API_KEY`） |
| Kimi / Moonshot（中国） | `kimi-coding-cn` | `KIMI_CN_API_KEY` |
| StepFun | `stepfun` | `STEPFUN_API_KEY` |
| 腾讯 TokenHub | `tencent-tokenhub` | `TOKENHUB_API_KEY` |
| Azure AI Foundry | `azure-foundry` | `AZURE_FOUNDRY_API_KEY` + `AZURE_FOUNDRY_BASE_URL` |
| LM Studio（本地） | `lmstudio` | `LM_API_KEY`（本地可无） + `LM_BASE_URL` |
| Hugging Face | `huggingface` | `HF_TOKEN` |
| 自定义端点 | `custom` | `base_url` + `key_env`（见下文） |
### 自定义端点回退 {#custom-endpoint-fallback}

对于自定义的兼容 OpenAI 的端点，添加 `base_url` 和可选的 `key_env`：

```yaml
fallback_model:
  provider: custom
  model: my-local-model
  base_url: http://localhost:8000/v1
  key_env: MY_LOCAL_KEY              # env var name containing the API key
```

### 回退触发条件 {#when-fallback-triggers}

当主模型因以下原因失败时，回退会自动激活：

- **速率限制**（HTTP 429）——重试次数用尽后
- **服务器错误**（HTTP 500、502、503）——重试次数用尽后
- **认证失败**（HTTP 401、403）——立即触发（重试无意义）
- **未找到**（HTTP 404）——立即触发
- **无效响应**——当 API 反复返回格式错误或空响应时

触发时，Hermes 会：

1. 解析回退提供商的凭据
2. 构建新的 API 客户端
3. 原地替换模型、提供商和客户端
4. 重置重试计数器并继续对话

切换是无缝的——你的对话历史、工具调用和上下文都会被保留。Agent 会从它离开的地方继续，只是换了一个不同的模型。

<a id="per-turn-not-per-session"></a>
:::info 按轮次，而非按会话
回退是**按轮次作用域**的：每个新的用户消息都会从恢复主模型开始。如果主模型在轮次中间失败，回退仅在该轮次激活。下一条消息时，Hermes 会再次尝试主模型。在单个轮次内，回退最多激活一次——如果回退也失败，则正常错误处理接管（重试，然后返回错误消息）。这防止了轮次内的级联故障转移循环，同时让主模型每轮都有新的机会。
:::
### 示例 {#examples}

**将 OpenRouter 作为 Anthropic 原生模型的回退：**
```yaml
model:
  provider: anthropic
  default: claude-sonnet-4-6

fallback_model:
  provider: openrouter
  model: anthropic/claude-sonnet-4
```

**将 Nous Portal 作为 OpenRouter 的回退：**
```yaml
model:
  provider: openrouter
  default: anthropic/claude-opus-4

fallback_model:
  provider: nous
  model: nous-hermes-3
```

**将本地模型作为云端模型的回退：**
```yaml
fallback_model:
  provider: custom
  model: llama-3.1-70b
  base_url: http://localhost:8000/v1
  key_env: LOCAL_API_KEY
```

**将 Codex OAuth 作为回退：**
```yaml
fallback_model:
  provider: openai-codex
  model: gpt-5.3-codex
```

### 回退功能生效的场景 {#where-fallback-works}

| 场景 | 是否支持回退 |
|---------|-------------------|
| CLI 会话 | ✔ |
| 消息网关（Telegram、Discord 等） | ✔ |
| 子 Agent 委派 | ✘ (子 Agent 不继承回退配置) |
| 定时任务 | ✘ (使用固定 provider 运行) |
| 辅助任务（视觉、压缩） | ✘ (使用自己的 provider 链 — 见下文) |

:::tip
`fallback_model` 没有对应的环境变量 —— 它完全通过 `config.yaml` 配置。这是有意为之：回退配置是一种深思熟虑的选择，不应该被过时的 shell 导出变量所覆盖。
:::

---

## 辅助任务回退 {#auxiliary-task-fallback}

Hermes 使用单独的轻量模型处理辅助任务。每个任务都有自己独立的 provider 解析链，充当内置回退系统。

### 具有独立 provider 解析的任务 {#tasks-with-independent-provider-resolution}
| 任务 | 功能说明 | 配置键 |
|------|-------------|-----------|
| 视觉 | 图像分析、浏览器截图 | `auxiliary.vision` |
| 网页提取 | 网页摘要 | `auxiliary.web_extract` |
| 压缩 | 上下文压缩摘要 | `auxiliary.compression` |
| 会话搜索 | 历史会话摘要 | `auxiliary.session_search` |
| 技能中心 | 技能搜索与发现 | `auxiliary.skills_hub` |
| MCP | MCP 辅助操作 | `auxiliary.mcp` |
| 审批 | 智能命令审批分类 | `auxiliary.approval` |
| 标题生成 | 会话标题摘要 | `auxiliary.title_generation` |

### 自动检测链 {#auto-detection-chain}

当任务的提供者设置为 `"auto"`（默认值）时，Hermes 会按顺序尝试提供者，直到其中一个成功：

**对于文本任务（压缩、网页提取等）：**

```text
OpenRouter → Nous Portal → Custom endpoint → Codex OAuth →
API-key providers (z.ai, Kimi, MiniMax, Xiaomi MiMo, Hugging Face, Anthropic) → give up
```

**对于视觉任务：**

```text
Main provider (if vision-capable) → OpenRouter → Nous Portal →
Codex OAuth → Anthropic → Custom endpoint → give up
```

如果解析出的提供者在调用时失败，Hermes 还有一个内部重试机制：如果提供者不是 OpenRouter 且没有设置显式的 `base_url`，它会尝试将 OpenRouter 作为最后的备用方案。

### 配置辅助提供者 {#configuring-auxiliary-providers}

每个任务都可以在 `config.yaml` 中独立配置：

```yaml
auxiliary:
  vision:
    provider: "auto"              # auto | openrouter | nous | codex | main | anthropic
    model: ""                     # e.g. "openai/gpt-4o"
    base_url: ""                  # direct endpoint (takes precedence over provider)
    api_key: ""                   # API key for base_url

  web_extract:
    provider: "auto"
    model: ""

  compression:
    provider: "auto"
    model: ""

  session_search:
    provider: "auto"
    model: ""
    timeout: 30
    max_concurrency: 3
    extra_body: {}

  skills_hub:
    provider: "auto"
    model: ""

  mcp:
    provider: "auto"
    model: ""
```
上述每个任务都遵循相同的 **provider / model / base_url** 模式。上下文压缩在 `auxiliary.compression` 下配置：

```yaml
auxiliary:
  compression:
    provider: main                                    # 与其他辅助任务相同的 provider 选项
    model: google/gemini-3-flash-preview
    base_url: null                                    # 自定义 OpenAI 兼容端点
```

而回退模型使用：

```yaml
fallback_model:
  provider: openrouter
  model: anthropic/claude-sonnet-4
  # base_url: http://localhost:8000/v1               # 可选的自定义端点
```

对于 `auxiliary.session_search`，Hermes 还支持：

- `max_concurrency` 限制同时运行的会话摘要数量
- `extra_body` 在摘要调用时传递 provider 特定的 OpenAI 兼容请求字段

示例：

```yaml
auxiliary:
  session_search:
    provider: main
    model: glm-4.5-air
    max_concurrency: 2
    extra_body:
      enable_thinking: false
```

如果你的 provider 不支持原生的 OpenAI 兼容推理控制字段，那么 `extra_body` 对此部分无效；此时 `max_concurrency` 仍然有助于减少请求突发导致的 429 错误。

三者——辅助任务、压缩、回退——工作方式相同：设置 `provider` 选择处理请求的服务商，`model` 选择模型，`base_url` 指向自定义端点（覆盖 provider 的默认端点）。

### 辅助任务的 Provider 选项 {#provider-options-for-auxiliary-tasks}

这些选项仅适用于 `auxiliary:`、`compression:` 和 `fallback_model:` 配置——`"main"` **不是** 顶层 `model.provider` 的有效值。对于自定义端点，请在 `model:` 部分使用 `provider: custom`（参见 [AI Providers](/integrations/providers)）。
| Provider | 描述 | 要求 |
|----------|------|------|
| `"auto"` | 按顺序尝试提供商，直到某个生效（默认） | 至少配置一个提供商 |
| `"openrouter"` | 强制使用 OpenRouter | `OPENROUTER_API_KEY` |
| `"nous"` | 强制使用 Nous Portal | `hermes auth` |
| `"codex"` | 强制使用 Codex OAuth | `hermes model` → Codex |
| `"main"` | 使用主 Agent 所用的任何提供商（仅限辅助任务） | 已配置活跃的主提供商 |
| `"anthropic"` | 强制使用 Anthropic 原生 | `ANTHROPIC_API_KEY` 或 Claude Code 凭据 |

### 直接端点覆盖 {#direct-endpoint-override}

对于任何辅助任务，设置 `base_url` 会完全绕过提供商解析，直接将请求发送到该端点：

```yaml
auxiliary:
  vision:
    base_url: "http://localhost:1234/v1"
    api_key: "local-key"
    model: "qwen2.5-vl"
```

`base_url` 优先级高于 `provider`。Hermes 使用配置的 `api_key` 进行身份验证，若未设置则回退到 `OPENAI_API_KEY`。它**不会**为自定义端点复用 `OPENROUTER_API_KEY`。

---

## 上下文压缩回退 {#context-compression-fallback}

上下文压缩使用 `auxiliary.compression` 配置块来控制处理摘要的模型和提供商：

```yaml
auxiliary:
  compression:
    provider: "auto"                              # auto | openrouter | nous | main
    model: "google/gemini-3-flash-preview"
```

<a id="legacy-migration"></a>
:::info 旧版迁移
旧配置中的 `compression.summary_model` / `compression.summary_provider` / `compression.summary_base_url` 会在首次加载时自动迁移到 `auxiliary.compression.*`（配置版本 17）。
:::
如果没有可用的压缩提供方，Hermes 会丢弃中间对话轮次而不生成摘要，但不会导致会话失败。

---

## 委托提供方覆盖（Delegation Provider Override） {#delegation-provider-override}

由 `delegate_task` 生成的子 Agent **不会**使用主回退模型。不过，它们可以被路由到不同的 provider:model 组合，以实现成本优化：

```yaml
delegation:
  provider: "openrouter"                      # 为所有子 Agent 覆盖提供方
  model: "google/gemini-3-flash-preview"      # 覆盖模型
  # base_url: "http://localhost:1234/v1"      # 或使用直接端点
  # api_key: "local-key"
```

完整配置说明请参见 [子 Agent 委托](/user-guide/features/delegation)。

---

## Cron 任务提供方 {#cron-job-providers}

Cron 任务在执行时使用当前配置的提供方，不支持回退模型。若要为 Cron 任务使用不同的提供方，请在 Cron 任务本身上配置 `provider` 和 `model` 覆盖：

```python
cronjob(
    action="create",
    schedule="every 2h",
    prompt="Check server status",
    provider="openrouter",
    model="google/gemini-3-flash-preview"
)
```

完整配置说明请参见 [定时任务（Cron）](/user-guide/features/cron)。

---

## 总结 {#summary}

| 功能 | 回退机制 | 配置位置 |
|---------|-------------------|----------------|
| 主 Agent 模型 | `fallback_model` 在 config.yaml 中 — 出错时每轮切换回退（每轮开始时恢复主模型） | `fallback_model:`（顶层） |
| 视觉 | 自动检测链 + 内部 OpenRouter 重试 | `auxiliary.vision` |
| 网页提取 | 自动检测链 + 内部 OpenRouter 重试 | `auxiliary.web_extract` |
| 上下文压缩 | 自动检测链，不可用时降级为不生成摘要 | `auxiliary.compression` |
| 会话搜索 | 自动检测链 | `auxiliary.session_search` |
| 技能中心 | 自动检测链 | `auxiliary.skills_hub` |
| MCP 辅助 | 自动检测链 | `auxiliary.mcp` |
| 审批分类 | 自动检测链 | `auxiliary.approval` |
| 标题生成 | 自动检测链 | `auxiliary.title_generation` |
| 委托 | 仅提供方覆盖（无自动回退） | `delegation.provider` / `delegation.model` |
| Cron 任务 | 仅任务级提供方覆盖（无自动回退） | 任务级 `provider` / `model` |
