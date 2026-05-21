---
title: 回退提供方
description: 当主模型不可用时，自动切换到备用 LLM 提供方。
sidebar_label: 回退提供方
sidebar_position: 8
---

<a id="fallback-providers"></a>
# 回退提供方

Hermes Agent 提供三层韧性机制，确保当提供方出现问题时会话仍可继续运行：

1. **[凭据池](./credential-pools.md)** — 在*同一*提供方内轮换多个 API 密钥（优先尝试）
2. **主模型回退** — 主模型失败时自动切换至*不同*的提供商:模型组合
3. **辅助任务回退** — 针对视觉、压缩、网页提取等副任务独立解析提供方

凭据池处理同一提供方内的轮换（例如多个 OpenRouter 密钥）。本页介绍跨提供方回退。两者均为可选，且相互独立。

<a id="primary-model-fallback"></a>
## 主模型回退

当主 LLM 提供方遇到错误（速率限制、服务器过载、认证失败、连接断开）时，Hermes 可在会话中自动切换到备用提供方:模型组合，无需丢失对话内容。

<a id="configuration"></a>
### 配置

最简便的方法是通过交互式管理器：

```bash
hermes fallback
```

`hermes fallback` 复用了 `hermes model` 的提供方选择器——相同的提供方列表、相同的凭据提示、相同的验证。使用子命令 `add`、`list`（别名 `ls`）、`remove`（别名 `rm`）和 `clear` 来管理回退链。更改会持久保存在 `config.yaml` 顶层的 `fallback_providers:` 列表中。

如果你更倾向于直接编辑 YAML，请在 `~/.hermes/config.yaml` 中添加 `fallback_model` 配置项：

```yaml
fallback_model:
  provider: openrouter
  model: anthropic/claude-sonnet-4
```

`provider` 和 `model` 均为**必填**。缺少任一字段时，回退功能将被禁用。

:::note `fallback_model` 与 `fallback_providers`
<a id="fallbackmodel-vs-fallbackproviders"></a>
`fallback_model`（单数）是旧版单回退配置项——Hermes 仍为向后兼容而保留它。`fallback_providers`（复数，列表）支持按顺序尝试多个回退；`hermes fallback` 会将结果写入此配置项。当两者同时存在时，Hermes 会合并它们，并以 `fallback_providers` 为准。
:::

<a id="supported-providers"></a>
### 支持的提供方

| 提供方 | 标识符 | 要求 |
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
| GMI Cloud | `gmi` | `GMI_API_KEY`（可选：`GMI_BASE_URL`） |
| StepFun | `stepfun` | `STEPFUN_API_KEY`（可选：`STEPFUN_BASE_URL`） |
| Ollama Cloud | `ollama-cloud` | `OLLAMA_API_KEY` |
| Google Gemini（OAuth） | `google-gemini-cli` | `hermes model`（Google OAuth；可选：`HERMES_GEMINI_PROJECT_ID`） |
| Google AI Studio | `gemini` | `GOOGLE_API_KEY`（别名：`GEMINI_API_KEY`） |
| xAI（Grok） | `xai`（别名 `grok`） | `XAI_API_KEY`（可选：`XAI_BASE_URL`） |
| xAI Grok OAuth（SuperGrok） | `xai-oauth`（别名 `grok-oauth`） | `hermes model` → xAI Grok OAuth（浏览器登录；需 SuperGrok 订阅） |
| AWS Bedrock | `bedrock` | 标准 boto3 认证（`AWS_REGION` + `AWS_PROFILE` 或 `AWS_ACCESS_KEY_ID`） |
| Qwen Portal（OAuth） | `qwen-oauth` | `hermes model`（Qwen 门户 OAuth；可选：`HERMES_QWEN_BASE_URL`） |
| MiniMax（OAuth） | `minimax-oauth` | `hermes model`（MiniMax 门户 OAuth） |
| OpenCode Zen | `opencode-zen` | `OPENCODE_ZEN_API_KEY` |
| OpenCode Go | `opencode-go` | `OPENCODE_GO_API_KEY` |
| Kilo Code | `kilocode` | `KILOCODE_API_KEY` |
| 小米 MiMo | `xiaomi` | `XIAOMI_API_KEY` |
| Arcee AI | `arcee` | `ARCEEAI_API_KEY` |
| GMI Cloud | `gmi` | `GMI_API_KEY` |
| 阿里云 / DashScope | `alibaba` | `DASHSCOPE_API_KEY` |
| 阿里云编码计划 | `alibaba-coding-plan` | `ALIBABA_CODING_PLAN_API_KEY`（回退至 `DASHSCOPE_API_KEY`） |
| Kimi / Moonshot（中国） | `kimi-coding-cn` | `KIMI_CN_API_KEY` |
| StepFun | `stepfun` | `STEPFUN_API_KEY` |
| 腾讯 TokenHub | `tencent-tokenhub` | `TOKENHUB_API_KEY` |
| Microsoft Foundry | `azure-foundry` | `AZURE_FOUNDRY_API_KEY` + `AZURE_FOUNDRY_BASE_URL` |
| LM Studio（本地） | `lmstudio` | `LM_API_KEY`（本地可无） + `LM_BASE_URL` |
| Hugging Face | `huggingface` | `HF_TOKEN` |
| 自定义端点 | `custom` | `base_url` + `key_env`（见下方说明） |
<a id="custom-endpoint-fallback"></a>
### 自定义端点回退

对于自定义的兼容 OpenAI 的端点，添加 `base_url` 和可选的 `key_env`：

```yaml
fallback_model:
  provider: custom
  model: my-local-model
  base_url: http://localhost:8000/v1
  key_env: MY_LOCAL_KEY              # 包含 API 密钥的环境变量名
```

<a id="when-fallback-triggers"></a>
### 回退触发时机

当主模型出现以下故障时，回退会自动激活：

- **速率限制**（HTTP 429）—— 重试次数用尽后
- **服务器错误**（HTTP 500、502、503）—— 重试次数用尽后
- **认证失败**（HTTP 401、403）—— 立即触发（重试无意义）
- **未找到**（HTTP 404）—— 立即触发
- **无效响应**—— 当 API 反复返回格式错误或空响应时

触发时，Hermes 会：

1. 解析回退提供商的凭证
2. 构建一个新的 API 客户端
3. 原地替换模型、提供商和客户端
4. 重置重试计数器并继续对话

切换是无缝的——你的对话历史、工具调用和上下文都会保留。Agent 会从它停下的地方继续，只是换了一个不同的模型。

:::info 按轮次，而非按会话
回退是**按轮次作用**的：每个新的用户消息都会先恢复使用主模型。如果主模型在某一轮中失败，回退仅在该轮中激活。下一条消息时，Hermes 会再次尝试主模型。在单轮中，回退最多激活一次——如果回退也失败，则进入正常错误处理（重试，然后返回错误消息）。这可以防止单轮内出现级联故障转移循环，同时让主模型每轮都有新的机会。
:::
<a id="per-turn-not-per-session"></a>

<a id="examples"></a>
### 示例

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

<a id="where-fallback-works"></a>
### 回退生效的场景

| 上下文 | 是否支持回退 |
|---------|-------------------|
| CLI 会话 | ✔ |
| 消息网关（Telegram、Discord 等） | ✔ |
| 子 Agent 委派 | ✘（子 Agent 不继承回退配置） |
| 定时任务 | ✘（使用固定提供商运行） |
| 辅助任务（视觉、压缩） | ✘（使用自己的提供商链——见下文） |

:::tip
`fallback_model` 没有对应的环境变量——它只能通过 `config.yaml` 配置。这是有意为之：回退配置是一个需要慎重考虑的选择，不应该被过期的 shell 导出变量覆盖。
:::

---

<a id="auxiliary-task-fallback"></a>
## 辅助任务回退

Hermes 为辅助任务使用独立的轻量级模型。每个任务都有自己的提供商解析链，作为内置的回退系统。
<a id="tasks-with-independent-provider-resolution"></a>
### 独立提供方解析的任务

| 任务 | 功能说明 | 配置键 |
|------|-------------|-----------|
| Vision | 图像分析、浏览器截图 | `auxiliary.vision` |
| Web Extract | 网页摘要 | `auxiliary.web_extract` |
| Compression | 上下文压缩摘要 | `auxiliary.compression` |
| Skills Hub | 技能搜索和发现 | `auxiliary.skills_hub` |
| MCP | MCP 辅助操作 | `auxiliary.mcp` |
| Approval | 智能命令审批分类 | `auxiliary.approval` |
| Title Generation | 会话标题摘要 | `auxiliary.title_generation` |
| Triage Specifier | `hermes kanban specify` / dashboard ✨ 按钮 — 将一行分类任务充实为完整的规格说明 | `auxiliary.triage_specifier` |

<a id="auto-detection-chain"></a>
### 自动检测链

当某个任务的提供方设为 `"auto"`（默认值）时，Hermes 会按顺序尝试提供方，直到某个可用为止：

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

如果已解析的提供方在调用时失败，Hermes 也有内部重试机制：如果提供方不是 OpenRouter 且未设置显式的 `base_url`，它会将 OpenRouter 作为最后的备用方案。

<a id="configuring-auxiliary-providers"></a>
### 配置辅助任务提供方

每个任务可以在 `config.yaml` 中独立配置：

```yaml
auxiliary:
  vision:
    provider: "auto"              # auto | openrouter | nous | codex | main | anthropic
    model: ""                     # 例如 "openai/gpt-4o"
    base_url: ""                  # 直接端点（优先于 provider）
    api_key: ""                   # base_url 的 API 密钥

  web_extract:
    provider: "auto"
    model: ""

  compression:
    provider: "auto"
    model: ""

  skills_hub:
    provider: "auto"
    model: ""

  mcp:
    provider: "auto"
    model: ""
```

以上每个任务都遵循相同的 **provider / model / base_url** 模式。上下文压缩在 `auxiliary.compression` 下配置：

```yaml
auxiliary:
  compression:
    provider: main                                    # 与其他辅助任务相同的提供方选项
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

三者（auxiliary、compression、fallback）的工作方式相同：设置 `provider` 选择处理请求的提供方，设置 `model` 选择模型，设置 `base_url` 指向自定义端点（会覆盖 provider）。

<a id="provider-options-for-auxiliary-tasks"></a>
### 辅助任务的提供方选项

这些选项仅适用于 `auxiliary:`、`compression:`、`fallback_model:` 配置 — `"main"` **不**是顶级 `model.provider` 的有效值。对于自定义端点，请在你的 `model:` 部分中使用 `provider: custom`（参见 [AI 提供方（Providers）](/integrations/providers)）。
| 提供商 | 描述 | 要求 |
|----------|-------------|-------------|
| `"auto"` | 按顺序尝试提供商，直到其中一个可用（默认） | 至少配置一个提供商 |
| `"openrouter"` | 强制使用 OpenRouter | `OPENROUTER_API_KEY` |
| `"nous"` | 强制使用 Nous Portal | `hermes auth` |
| `"codex"` | 强制使用 Codex OAuth | `hermes model` → Codex |
| `"main"` | 使用主Agent所使用的任何提供商（仅限辅助任务） | 已配置活跃的主提供商 |
| `"anthropic"` | 强制使用 Anthropic 原生 | `ANTHROPIC_API_KEY` 或 Claude Code 凭据 |

<a id="direct-endpoint-override"></a>
### 直接端点覆盖

对于任何辅助任务，设置 `base_url` 将完全绕过提供商解析，并直接将请求发送到该端点：

```yaml
auxiliary:
  vision:
    base_url: "http://localhost:1234/v1"
    api_key: "local-key"
    model: "qwen2.5-vl"
```

`base_url` 优先于 `provider`。Hermes 使用配置的 `api_key` 进行身份验证，如果未设置，则回退到 `OPENAI_API_KEY`。它**不会**为自定义端点重复使用 `OPENROUTER_API_KEY`。

---

<a id="auxiliary-capacity-error-fallback"></a>
## 辅助任务容量错误回退

当你设置一个显式的辅助提供商（例如 `auxiliary.vision.provider: glm`）时，Hermes 会将其视为你的首选——但如果该提供商确实因为**容量错误**（HTTP 402 需要付款、HTTP 429 每日配额耗尽、连接失败）而无法提供请求服务，Hermes 会通过一个分层链进行回退，而不是静默失败：

1. **主辅助提供商** — 你配置的那个（总是首先尝试）
2. **`auxiliary.&lt;task&gt;.fallback_chain`** — 你的每个任务覆盖列表（如果你编写了的话）
3. **主Agent提供商 + 模型** — 最后的安全网（总是会尝试，即使你没有编写链）
4. **警告并重新抛出** — 如果每一层都失败，Hermes 会在 WARNING 级别记录 `Auxiliary &lt;task&gt;: ... all fallbacks exhausted` 并重新抛出原始错误

瞬时的 HTTP 429 速率限制（`Retry-After: ...`）被视为请求约束，而不是容量问题——它们会遵循你显式指定的提供商，并且**不会**触发回退阶梯。只有每日/每月配额耗尽、付款错误和连接失败才会绕过显式提供商的检查。

对于使用 `provider: auto`（没有显式辅助提供商）的用户，现有的自动检测链会替代步骤 2–3 运行。它的第一步已经是主Agent模型，因此使用 `auto` 的用户无需任何配置就能得到相同的结果。

<a id="optional-per-task-fallback-chain"></a>
### 可选：每个任务的回退链

如果你希望使用不同于"主Agent模型优先"的回退排序，请显式配置 `fallback_chain`。每个条目至少需要 `provider`；`model`、`base_url` 和 `api_key` 是可选的。

```yaml
auxiliary:
  vision:
    provider: glm
    model: glm-4v-flash
    fallback_chain:
      - provider: openrouter
        model: google/gemini-3-flash-preview
      - provider: nous
        model: anthropic/claude-sonnet-4

  compression:
    provider: openrouter
    fallback_chain:
      - provider: openai
        model: gpt-4o-mini
```
你**不需要**配置 `fallback_chain` 就能获得回退能力——主 Agent 的安全网始终在运行。只有当你希望使用与默认顺序不同的顺序时，才需要使用它。

<a id="provider-quota-errors-that-trigger-fallback"></a>
### 触发回退的提供商配额错误

Hermes 将这些视为等同于 402 信用额度耗尽的容量问题（而非瞬时速率限制）：

- Bedrock / LiteLLM：`Too many tokens per day`、`daily limit`、`tokens per day`
- Vertex AI / GCP：`quota exceeded`、`resource exhausted`、`RESOURCE_EXHAUSTED`
- 通用：`daily quota`、`quota_exceeded`

如果你的提供商返回了不同的每日配额耗尽短语，而 Hermes 没有触发回退，那是一个 bug——请提交一个包含确切错误字符串的 issue。

---

<a id="context-compression-fallback"></a>
## 上下文压缩回退

上下文压缩使用 `auxiliary.compression` 配置块来控制哪个模型和提供商处理摘要：

```yaml
auxiliary:
  compression:
    provider: "auto"                              # auto | openrouter | nous | main
    model: "google/gemini-3-flash-preview"
```

:::info 旧版迁移
包含 `compression.summary_model` / `compression.summary_provider` / `compression.summary_base_url` 的旧配置会在首次加载时自动迁移到 `auxiliary.compression.*`（配置版本 17）。
:::
<a id="legacy-migration"></a>

如果没有可用的压缩提供商，Hermes 会丢弃中间对话轮次而不生成摘要，而不是让会话失败。

---

<a id="delegation-provider-override"></a>
## 委派提供商覆盖

由 `delegate_task` 生成的子 Agent **不会**使用主回退模型。但是，它们可以被路由到不同的提供商:模型对，以实现成本优化：

```yaml
delegation:
  provider: "openrouter"                      # 覆盖所有子 Agent 的提供商
  model: "google/gemini-3-flash-preview"      # 覆盖模型
  # base_url: "http://localhost:1234/v1"      # 或使用直接端点
  # api_key: "local-key"
```

完整的配置详情请参见[子 Agent 委派](/user-guide/features/delegation)。

---

<a id="cron-job-providers"></a>
## Cron 任务提供商

Cron 任务使用执行时配置的任何提供商运行。它们不支持回退模型。要为 cron 任务使用不同的提供商，请在 cron 任务本身上配置 `provider` 和 `model` 覆盖：

```python
cronjob(
    action="create",
    schedule="every 2h",
    prompt="Check server status",
    provider="openrouter",
    model="google/gemini-3-flash-preview"
)
```

完整的配置详情请参见[计划任务 (Cron)](/user-guide/features/cron)。

---

<a id="summary"></a>
## 总结

| 功能 | 回退机制 | 配置位置 |
|---------|-------------------|----------------|
| 主 Agent 模型 | `fallback_model` 在 config.yaml 中——出错时每轮故障转移（每轮恢复主模型） | `fallback_model:`（顶层） |
| 辅助任务（任意）——自动用户 | 容量错误时的完整自动检测链（先主 Agent 模型，然后提供商链） | `auxiliary.&lt;task&gt;.provider: auto` |
| 辅助任务（任意）——显式提供商 | `fallback_chain`（如果设置）→ 主 Agent 模型 → 警告并抛出，仅在容量错误时 | `auxiliary.&lt;task&gt;.fallback_chain` |
| 视觉 | 分层（见上文）+ 内部 OpenRouter 重试 | `auxiliary.vision` |
| 网页提取 | 分层（见上文）+ 内部 OpenRouter 重试 | `auxiliary.web_extract` |
| 上下文压缩 | 分层（见上文）；如果所有层都不可用，则降级为无摘要 | `auxiliary.compression` |
| 技能中心 | 分层（见上文） | `auxiliary.skills_hub` |
| MCP 助手 | 分层（见上文） | `auxiliary.mcp` |
| 审批分类 | 分层（见上文） | `auxiliary.approval` |
| 标题生成 | 分层（见上文） | `auxiliary.title_generation` |
| 分诊指定器 | 分层（见上文） | `auxiliary.triage_specifier` |
| 委派 | 仅提供商覆盖（无自动回退） | `delegation.provider` / `delegation.model` |
| Cron 任务 | 仅按任务提供商覆盖（无自动回退） | 按任务 `provider` / `model` |
