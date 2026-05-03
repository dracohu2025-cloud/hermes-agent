---
title: "AI 提供商"
sidebar_label: "AI 提供商"
sidebar_position: 1
---

# AI 提供商 {#ai-providers}

本页介绍如何为 Hermes Agent 配置推理提供商——从 OpenRouter、Anthropic 等云 API，到 Ollama、vLLM 等自托管端点，再到高级路由和回退配置。你需要至少配置一个提供商才能使用 Hermes。

## 推理提供商 {#inference-providers}

你需要至少一种方式连接到 LLM。使用 `hermes model` 可以交互式切换提供商和模型，也可以直接配置：

| 提供商 | 配置方式 |
|----------|-------|
| **Nous Portal** | `hermes model`（OAuth，基于订阅） |
| **OpenAI Codex** | `hermes model`（ChatGPT OAuth，使用 Codex 模型） |
| **GitHub Copilot** | `hermes model`（OAuth 设备码流程，`COPILOT_GITHUB_TOKEN`、`GH_TOKEN` 或 `gh auth token`） |
| **GitHub Copilot ACP** | `hermes model`（启动本地 `copilot --acp --stdio`） |
| **Anthropic** | `hermes model`（Claude Max + 通过 OAuth 获取额外使用额度；也支持 Anthropic API 密钥或手动设置 token——见下方说明） |
| **OpenRouter** | `OPENROUTER_API_KEY` 放在 `~/.hermes/.env` 中 |
| **AI Gateway** | `AI_GATEWAY_API_KEY` 放在 `~/.hermes/.env` 中（provider: `ai-gateway`） |
| **z.ai / GLM** | `GLM_API_KEY` 放在 `~/.hermes/.env` 中（provider: `zai`） |
| **Kimi / Moonshot** | `KIMI_API_KEY` 放在 `~/.hermes/.env` 中（provider: `kimi-coding`） |
| **Kimi / Moonshot（中国）** | `KIMI_CN_API_KEY` 放在 `~/.hermes/.env` 中（provider: `kimi-coding-cn`；别名：`kimi-cn`、`moonshot-cn`） |
| **Arcee AI** | `ARCEEAI_API_KEY` 放在 `~/.hermes/.env` 中（provider: `arcee`；别名：`arcee-ai`、`arceeai`） |
| **GMI Cloud** | `GMI_API_KEY` 放在 `~/.hermes/.env` 中（provider: `gmi`；别名：`gmi-cloud`、`gmicloud`） |
| **MiniMax** | `MINIMAX_API_KEY` 放在 `~/.hermes/.env` 中（provider: `minimax`） |
| **MiniMax 中国** | `MINIMAX_CN_API_KEY` 放在 `~/.hermes/.env` 中（provider: `minimax-cn`） |
| **阿里云** | `DASHSCOPE_API_KEY` 放在 `~/.hermes/.env` 中（provider: `alibaba`） |
| **阿里云编码计划** | `DASHSCOPE_API_KEY`（provider: `alibaba-coding-plan`，别名：`alibaba_coding`）——独立计费 SKU，不同端点 |
| **Kilo Code** | `KILOCODE_API_KEY` 放在 `~/.hermes/.env` 中（provider: `kilocode`） |
| **小米 MiMo** | `XIAOMI_API_KEY` 放在 `~/.hermes/.env` 中（provider: `xiaomi`，别名：`mimo`、`xiaomi-mimo`） |
| **腾讯 TokenHub** | `TOKENHUB_API_KEY` 放在 `~/.hermes/.env` 中（provider: `tencent-tokenhub`，别名：`tencent`、`tokenhub`、`tencentmaas`） |
| **OpenCode Zen** | `OPENCODE_ZEN_API_KEY` 放在 `~/.hermes/.env` 中（provider: `opencode-zen`） |
| **OpenCode Go** | `OPENCODE_GO_API_KEY` 放在 `~/.hermes/.env` 中（provider: `opencode-go`） |
| **DeepSeek** | `DEEPSEEK_API_KEY` 放在 `~/.hermes/.env` 中（provider: `deepseek`） |
| **Hugging Face** | `HF_TOKEN` 放在 `~/.hermes/.env` 中（provider: `huggingface`，别名：`hf`） |
| **Google / Gemini** | `GOOGLE_API_KEY`（或 `GEMINI_API_KEY`）放在 `~/.hermes/.env` 中（provider: `gemini`） |
| **Google Gemini（OAuth）** | `hermes model` → "Google Gemini (OAuth)"（provider: `google-gemini-cli`，支持免费套餐，浏览器 PKCE 登录） |
| **LM Studio** | `hermes model` → "LM Studio"（provider: `lmstudio`，可选 `LM_API_KEY`） |
| **自定义端点** | `hermes model` → 选择 "Custom endpoint"（保存在 `config.yaml` 中） |
:::tip 模型键别名
<a id="model-key-alias"></a>
在 `model:` 配置段中，你可以使用 `default:` 或 `model:` 作为模型 ID 的键名。`model: { default: my-model }` 和 `model: { model: my-model }` 的效果完全一致。
:::

### 通过 OAuth 使用 Google Gemini（`google-gemini-cli`） {#google-gemini-via-oauth-google-gemini-cli}

`google-gemini-cli` 提供者使用 Google 的 Cloud Code Assist 后端——与 Google 自己的 `gemini-cli` 工具所用的 API 相同。它同时支持**免费层**（个人账户每日慷慨配额）和**付费层**（通过 GCP 项目使用 Standard/Enterprise）。

**快速开始：**

```bash
hermes model
# → 选择 "Google Gemini (OAuth)"
# → 查看策略警告，确认
# → 浏览器打开 accounts.google.com，登录
# → 完成——Hermes 会在首次请求时自动配置你的免费层
```

Hermes 默认携带 Google 的**公开** `gemini-cli` 桌面 OAuth 客户端——与 Google 在其开源 `gemini-cli` 中包含的凭据相同。桌面 OAuth 客户端并非机密（PKCE 提供安全性）。你无需安装 `gemini-cli` 或注册自己的 GCP OAuth 客户端。

**认证原理：**
- 针对 `accounts.google.com` 的 PKCE 授权码流程
- 浏览器回调地址为 `http://127.0.0.1:8085/oauth2callback`（若端口被占用，则回退到临时端口）
- 令牌存储在 `~/.hermes/auth/google_oauth.json`（权限 0600，原子写入，跨进程 `fcntl` 锁）
- 过期前 60 秒自动刷新
- 无头环境（SSH、`HERMES_HEADLESS=1`）→ 回退到粘贴模式
- 飞行中刷新去重——两个并发请求不会重复刷新
- `invalid_grant`（撤销的刷新令牌）→ 清除凭据文件，提示用户重新登录

**推理原理：**
- 流量发送到 `https://cloudcode-pa.googleapis.com/v1internal:generateContent`（或流式 `:streamGenerateContent?alt=sse`），而非付费的 `v1beta/openai` 端点
- 请求体包装为 `{project, model, user_prompt_id, request}`
- OpenAI 格式的 `messages[]`、`tools[]`、`tool_choice` 被转换为 Gemini 原生的 `contents[]`、`tools[].functionDeclarations`、`toolConfig` 格式
- 响应被转换回 OpenAI 格式，以便 Hermes 其余部分无需改动

**层级与项目 ID：**

| 你的情况 | 操作 |
|---|---|
| 个人 Google 账户，想用免费层 | 无需操作——登录后即可开始聊天 |
| Workspace / Standard / Enterprise 账户 | 将 `HERMES_GEMINI_PROJECT_ID` 或 `GOOGLE_CLOUD_PROJECT` 设置为你的 GCP 项目 ID |
| 受 VPC-SC 保护的组织 | Hermes 会检测到 `SECURITY_POLICY_VIOLATED` 并自动强制使用 `standard-tier` |

免费层会在首次使用时自动配置一个 Google 管理的项目。无需 GCP 设置。

**配额监控：**

```
/gquota
```

显示每个模型的 Code Assist 剩余配额，带进度条：

```
Gemini Code Assist quota  (project: 123-abc)

  gemini-2.5-pro                      ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░   85%
  gemini-2.5-flash [input]            ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░   92%
```

<a id="policy-risk"></a>
:::warning 策略风险
Google 认为将 Gemini CLI OAuth 客户端与第三方软件一起使用属于违反策略。部分用户报告过账户限制。为了最低风险体验，建议改用 `gemini` 提供者并使用你自己的 API 密钥。Hermes 会在 OAuth 开始前显示明确警告并要求用户确认。
:::
**自定义 OAuth 客户端（可选）：**

如果你想注册自己的 Google OAuth 客户端（例如，将配额和授权范围限定在你自己的 GCP 项目内），请设置：

```bash
HERMES_GEMINI_CLIENT_ID=your-client.apps.googleusercontent.com
HERMES_GEMINI_CLIENT_SECRET=...   # 桌面客户端可选
```

在 [console.cloud.google.com/apis/credentials](https://console.cloud.google.com/apis/credentials) 注册一个 **桌面应用** OAuth 客户端，并启用 Generative Language API。

:::info Codex 说明
OpenAI Codex 提供者通过设备码（打开 URL，输入代码）进行身份验证。Hermes 将生成的凭据存储在自己的认证存储中（`~/.hermes/auth.json`），并且可以在存在时导入现有的 Codex CLI 凭据（`~/.codex/auth.json`）。无需安装 Codex CLI。
<a id="codex-note"></a>
:::

:::warning
即使使用 Nous Portal、Codex 或自定义端点，某些工具（视觉、网页摘要、MoA）也会使用单独的“辅助”模型。默认情况下（`auxiliary.*.provider: "auto"`），Hermes 会将这些任务路由到你的**主聊天模型**——即你在 `hermes model` 中选择的同一个模型。你可以单独覆盖每个任务，将其路由到更便宜/更快的模型（例如 OpenRouter 上的 Gemini Flash）——请参阅[辅助模型](/user-guide/configuration#auxiliary-models)。
:::

:::tip Nous Tool Gateway
付费的 Nous Portal 订阅者还可以使用 **[Tool Gateway](/user-guide/features/tool-gateway)**——通过你的订阅路由的网页搜索、图像生成、TTS 和浏览器自动化。无需额外的 API 密钥。在 `hermes model` 设置期间会自动提供，或者稍后使用 `hermes tools` 启用。
:::

### 两个模型管理命令 {#two-commands-for-model-management}

Hermes 有**两个**用于不同目的的模型命令：

| 命令 | 运行位置 | 作用 |
|---------|-------------|--------------|
| **`hermes model`** | 你的终端（在任何会话之外） | 完整设置向导——添加提供者、运行 OAuth、输入 API 密钥、配置端点 |
| **`/model`** | 在 Hermes 聊天会话内部 | 在**已配置**的提供者和模型之间快速切换 |

如果你尝试切换到尚未设置的提供者（例如，你只配置了 OpenRouter，现在想使用 Anthropic），你需要使用 `hermes model`，而不是 `/model`。先退出当前会话（`Ctrl+C` 或 `/quit`），运行 `hermes model`，完成提供者设置，然后启动新会话。

### Anthropic（原生） {#anthropic-native}

直接通过 Anthropic API 使用 Claude 模型——无需 OpenRouter 代理。支持三种认证方式：

<a id="requires-claude-max-extra-usage-credits"></a>
:::caution 需要 Claude Max “额外使用”额度
当你通过 `hermes model` → Anthropic OAuth（或通过 `hermes auth add anthropic --type oauth`）进行身份验证时，Hermes 会以 Claude Code 的形式路由到你的 Anthropic 账户。**这仅在你有 Claude Max 计划并购买了额外使用额度时才有效。** 基础 Max 计划额度（Claude Code 默认包含的使用量）不会被 Hermes 消耗——只有你额外添加的超额额度才会被消耗。Claude Pro 订阅者无法使用此路径。
:::
如果你没有 Max + extra credits，可以使用 `ANTHROPIC_API_KEY` 替代——请求将按该密钥所属组织的 token 计费（标准 API 定价，与任何 Claude 订阅无关）。
:::

```bash
# 使用 API 密钥（按 token 计费）
export ANTHROPIC_API_KEY=***
hermes chat --provider anthropic --model claude-sonnet-4-6

# 推荐：通过 `hermes model` 进行身份验证
# Hermes 会直接使用 Claude Code 的凭据存储（如果可用）
hermes model

# 使用 setup-token 手动覆盖（回退 / 旧版）
export ANTHROPIC_TOKEN=***  # setup-token 或手动 OAuth token
hermes chat --provider anthropic

# 自动检测 Claude Code 凭据（如果你已经在使用 Claude Code）
hermes chat --provider anthropic  # 自动读取 Claude Code 凭据文件
```

当你通过 `hermes model` 选择 Anthropic OAuth 时，Hermes 会优先使用 Claude Code 自身的凭据存储，而不是将 token 复制到 `~/.hermes/.env`。这样可以让可刷新的 Claude 凭据保持可刷新状态。

或者永久设置：
```yaml
model:
  provider: "anthropic"
  default: "claude-sonnet-4-6"
```

:::tip 别名
<a id="aliases"></a>
`--provider claude` 和 `--provider claude-code` 也可以作为 `--provider anthropic` 的简写。
:::

### GitHub Copilot {#github-copilot}

Hermes 将 GitHub Copilot 作为一等公民提供商，支持两种模式：

**`copilot` — 直接 Copilot API**（推荐）。使用你的 GitHub Copilot 订阅，通过 Copilot API 访问 GPT-5.x、Claude、Gemini 等模型。

```bash
hermes chat --provider copilot --model gpt-5.4
```

**身份验证选项**（按此顺序检查）：

1. `COPILOT_GITHUB_TOKEN` 环境变量
2. `GH_TOKEN` 环境变量
3. `GITHUB_TOKEN` 环境变量
4. `gh auth token` CLI 回退

如果未找到 token，`hermes model` 会提供 **OAuth 设备码登录**——与 Copilot CLI 和 opencode 使用的流程相同。

<a id="token-types"></a>
:::warning Token 类型
Copilot API **不**支持经典 Personal Access Tokens（`ghp_*`）。支持的 token 类型：

| 类型 | 前缀 | 获取方式 |
|------|------|----------|
| OAuth token | `gho_` | `hermes model` → GitHub Copilot → 使用 GitHub 登录 |
| Fine-grained PAT | `github_pat_` | GitHub 设置 → 开发者设置 → Fine-grained tokens（需要 **Copilot Requests** 权限） |
| GitHub App token | `ghu_` | 通过 GitHub App 安装 |

如果你的 `gh auth token` 返回的是 `ghp_*` token，请改用 `hermes model` 通过 OAuth 进行身份验证。
:::

<a id="copilot-auth-behavior-in-hermes"></a>
:::info Hermes 中的 Copilot 身份验证行为
Hermes 将支持的 GitHub token（`gho_*`、`github_pat_*` 或 `ghu_*`）直接发送到 `api.githubcopilot.com`，并包含 Copilot 专用头部（`Editor-Version`、`Copilot-Integration-Id`、`Openai-Intent`、`x-initiator`）。

在收到 HTTP 401 时，Hermes 会在回退前执行一次性的凭据恢复：

1. 通过正常优先级链重新解析 token（`COPILOT_GITHUB_TOKEN` → `GH_TOKEN` → `GITHUB_TOKEN` → `gh auth token`）
2. 使用刷新后的头部重建共享的 OpenAI 客户端
3. 重试该请求一次
:::
:::tip
一些较旧的社区代理使用 `api.github.com/copilot_internal/v2/token` 交换流程。该端点可能对某些账户类型不可用（返回 404）。因此，Hermes 将直接令牌认证作为主要路径，并依赖运行时凭据刷新 + 重试来保证健壮性。
:::

**API 路由**：GPT-5+ 模型（`gpt-5-mini` 除外）自动使用 Responses API。所有其他模型（GPT-4o、Claude、Gemini 等）使用 Chat Completions。模型从实时 Copilot 目录中自动检测。

**`copilot-acp` — Copilot ACP Agent 后端**。将本地 Copilot CLI 作为子进程启动：

```bash
hermes chat --provider copilot-acp --model copilot-acp
# 需要 GitHub Copilot CLI 在 PATH 中，并且已有 `copilot login` 会话
```

**永久配置：**
```yaml
model:
  provider: "copilot"
  default: "gpt-5.4"
```

| 环境变量 | 描述 |
|---------------------|-------------|
| `COPILOT_GITHUB_TOKEN` | 用于 Copilot API 的 GitHub 令牌（最高优先级） |
| `HERMES_COPILOT_ACP_COMMAND` | 覆盖 Copilot CLI 二进制路径（默认：`copilot`） |
| `HERMES_COPILOT_ACP_ARGS` | 覆盖 ACP 参数（默认：`--acp --stdio`） |

### 一级 API 密钥提供商 {#first-class-api-key-providers}

这些提供商具有内置支持，带有专用提供商 ID。设置 API 密钥并使用 `--provider` 选择：

```bash
# z.ai / 智谱AI GLM
hermes chat --provider zai --model glm-5
# 需要：~/.hermes/.env 中的 GLM_API_KEY

# Kimi / Moonshot AI（国际：api.moonshot.ai）
hermes chat --provider kimi-coding --model kimi-for-coding
# 需要：~/.hermes/.env 中的 KIMI_API_KEY

# Kimi / Moonshot AI（中国：api.moonshot.cn）
hermes chat --provider kimi-coding-cn --model kimi-k2.5
# 需要：~/.hermes/.env 中的 KIMI_CN_API_KEY

# MiniMax（全球端点）
hermes chat --provider minimax --model MiniMax-M2.7
# 需要：~/.hermes/.env 中的 MINIMAX_API_KEY

# MiniMax（中国端点）
hermes chat --provider minimax-cn --model MiniMax-M2.7
# 需要：~/.hermes/.env 中的 MINIMAX_CN_API_KEY

# 阿里云 / DashScope（Qwen 模型）
hermes chat --provider alibaba --model qwen3.5-plus
# 需要：~/.hermes/.env 中的 DASHSCOPE_API_KEY

# 小米 MiMo
hermes chat --provider xiaomi --model mimo-v2-pro
# 需要：~/.hermes/.env 中的 XIAOMI_API_KEY

# 腾讯 TokenHub（Hy3 Preview）
hermes chat --provider tencent-tokenhub --model hy3-preview
# 需要：~/.hermes/.env 中的 TOKENHUB_API_KEY

# Arcee AI（Trinity 模型）
hermes chat --provider arcee --model trinity-large-thinking
# 需要：~/.hermes/.env 中的 ARCEEAI_API_KEY

# GMI Cloud
# 使用 GMI 的 /v1/models 端点返回的确切模型 ID。
hermes chat --provider gmi --model zai-org/GLM-5.1-FP8
# 需要：~/.hermes/.env 中的 GMI_API_KEY
```

或者在 `config.yaml` 中永久设置提供商：
```yaml
model:
  provider: "gmi"
  default: "zai-org/GLM-5.1-FP8"
```

基础 URL 可以通过 `GLM_BASE_URL`、`KIMI_BASE_URL`、`MINIMAX_BASE_URL`、`MINIMAX_CN_BASE_URL`、`DASHSCOPE_BASE_URL`、`XIAOMI_BASE_URL`、`GMI_BASE_URL` 或 `TOKENHUB_BASE_URL` 环境变量覆盖。
:::note Z.AI 端点自动检测
使用 Z.AI / GLM 提供商时，Hermes 会自动探测多个端点（全球、中国、编码变体）以找到接受你 API 密钥的那个。你无需手动设置 `GLM_BASE_URL` —— 工作端点会被自动检测并缓存。
:::
<a id="z-ai-endpoint-auto-detection"></a>

### xAI (Grok) — Responses API + 提示缓存 {#xai-grok-responses-api-prompt-caching}

xAI 通过 Responses API（`codex_responses` 传输协议）集成，为 Grok 4 模型提供自动推理支持 —— 不需要 `reasoning_effort` 参数，服务器默认会进行推理。在 `~/.hermes/.env` 中设置 `XAI_API_KEY`，然后在 `hermes model` 中选择 xAI，或者用快捷方式将 `grok` 放入 `/model grok-4-1-fast-reasoning`。

当使用 xAI 作为提供商（任何包含 `x.ai` 的基础 URL）时，Hermes 会自动启用提示缓存，每次 API 请求都会发送 `x-grok-conv-id` 头部。这会将同一对话会话中的请求路由到同一台服务器，使 xAI 的基础设施能够重用缓存的系统提示和对话历史。

无需配置 —— 当检测到 xAI 端点且存在会话 ID 时，缓存会自动激活。这可以降低多轮对话的延迟和成本。

xAI 还附带一个专用的 TTS 端点（`/v1/tts`）。在 `hermes tools` → Voice & TTS 中选择 **xAI TTS**，或查看 [Voice & TTS](../user-guide/features/tts.md#text-to-speech) 页面了解配置。

### Ollama Cloud — 托管 Ollama 模型，OAuth + API 密钥 {#ollama-cloud-managed-ollama-models-oauth-api-key}

[Ollama Cloud](https://ollama.com/cloud) 托管与本地 Ollama 相同的开放权重目录，但无需 GPU。在 `hermes model` 中选择 **Ollama Cloud**，粘贴来自 [ollama.com/settings/keys](https://ollama.com/settings/keys) 的 API 密钥，Hermes 会自动发现可用模型。

```bash
hermes model
# → 选择 "Ollama Cloud"
# → 粘贴你的 OLLAMA_API_KEY
# → 从发现的模型中选择（gpt-oss:120b, glm-4.6:cloud, qwen3-coder:480b-cloud 等）
```

或者直接使用 `config.yaml`：
```yaml
model:
  provider: "ollama-cloud"
  default: "gpt-oss:120b"
```

模型目录会从 `ollama.com/v1/models` 动态获取并缓存一小时。`model:tag` 表示法（例如 `qwen3-coder:480b-cloud`）通过规范化保持原样 —— 不要使用破折号。

:::tip Ollama Cloud vs 本地 Ollama
<a id="ollama-cloud-vs-local-ollama"></a>
两者都使用相同的兼容 OpenAI 的 API。Cloud 是一等提供商（`--provider ollama-cloud`，`OLLAMA_API_KEY`）；本地 Ollama 通过自定义端点流程（基础 URL `http://localhost:11434/v1`，无密钥）访问。对于无法在本地运行的大型模型，使用 Cloud；为了隐私或离线工作，使用本地。
:::

### AWS Bedrock {#aws-bedrock}

Anthropic Claude、Amazon Nova、DeepSeek v3.2、Meta Llama 4 以及其他模型通过 AWS Bedrock 使用。采用 AWS SDK (`boto3`) 凭证链 —— 无需 API 密钥，只需标准的 AWS 认证。

```bash
# 最简单 —— 在 ~/.aws/credentials 中使用命名配置文件
hermes chat --provider bedrock --model us.anthropic.claude-sonnet-4-6

# 或者使用显式环境变量
AWS_PROFILE=myprofile AWS_REGION=us-east-1 hermes chat --provider bedrock --model us.anthropic.claude-sonnet-4-6
```
或者在 `config.yaml` 中永久配置：
```yaml
model:
  provider: "bedrock"
  default: "us.anthropic.claude-sonnet-4-6"
bedrock:
  region: "us-east-1"          # 或设置 AWS_REGION
  # profile: "myprofile"       # 或设置 AWS_PROFILE
  # discovery: true            # 从 IAM 自动发现区域
  # guardrail:                 # 可选的 Bedrock Guardrails
  #   id: "your-guardrail-id"
  #   version: "DRAFT"
```

认证使用标准的 boto3 链：显式的 `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY`、来自 `~/.aws/credentials` 的 `AWS_PROFILE`、EC2/ECS/Lambda 上的 IAM 角色、IMDS 或 SSO。如果你已经通过 AWS CLI 认证，则无需设置环境变量。

Bedrock 底层使用 **Converse API** —— 请求会被转换为 Bedrock 的模型无关格式，因此同一份配置适用于 Claude、Nova、DeepSeek 和 Llama 模型。仅当你要调用非默认的区域端点时，才需要设置 `BEDROCK_BASE_URL`。

有关 IAM 设置、区域选择和跨区域推理的详细说明，请参阅 [AWS Bedrock 指南](/guides/aws-bedrock)。

### Qwen Portal (OAuth) {#qwen-portal-oauth}

阿里巴巴的 Qwen Portal，支持基于浏览器的 OAuth 登录。在 `hermes model` 中选择 **Qwen OAuth (Portal)**，通过浏览器登录，Hermes 会持久化保存 refresh token。

```bash
hermes model
# → 选择 "Qwen OAuth (Portal)"
# → 浏览器打开；使用你的阿里云账号登录
# → 确认 — 凭据已保存到 ~/.hermes/auth.json

hermes chat   # 使用 portal.qwen.ai/v1 端点
```

或者配置 `config.yaml`：
```yaml
model:
  provider: "qwen-oauth"
  default: "qwen3-coder-plus"
```

仅当 Portal 端点地址变更时，才需要设置 `HERMES_QWEN_BASE_URL`（默认值：`https://portal.qwen.ai/v1`）。

:::tip Qwen OAuth 与 DashScope（阿里云）的区别
`qwen-oauth` 使用面向消费者的 Qwen Portal 进行 OAuth 登录——适合个人用户。而 `alibaba` provider 使用 DashScope 的企业 API，需要 `DASHSCOPE_API_KEY`——适合程序化/生产环境。两者都路由到 Qwen 系列模型，但端点不同。
<a id="qwen-oauth-vs-dashscope-alibaba"></a>
:::

### 阿里云 Coding Plan {#alibaba-coding-plan}

如果你订阅了阿里云的 **Coding Plan**（一种独立于标准 DashScope API 访问的定价 SKU），Hermes 会将其作为一等 provider 暴露出来：`alibaba-coding-plan`。端点：`https://coding-intl.dashscope.aliyuncs.com/v1`。它与常规的 `alibaba` provider 一样兼容 OpenAI，但使用不同的基础 URL 和计费方式。

```yaml
model:
  provider: alibaba_coding     # alibaba-coding-plan 的别名
  model: qwen3-coder-plus
```

或者通过 CLI：

```bash
hermes chat --provider alibaba_coding --model qwen3-coder-plus
```

`alibaba_coding` 使用与 `alibaba` 条目相同的 `DASHSCOPE_API_KEY`——无需单独的密钥，只是路由目标不同。在此 provider 注册之前，在 `config.yaml` 中设置 `provider: alibaba_coding` 的用户会静默地回退到 OpenRouter 路由。

### MiniMax (OAuth) {#minimax-oauth}

MiniMax-M2.7 通过浏览器 OAuth 登录——无需 API 密钥。在 `hermes model` 中选择 **MiniMax (OAuth)**，通过浏览器登录，Hermes 会持久化保存 access 和 refresh token。底层使用 Anthropic Messages 兼容端点（`/anthropic`）。
```bash
hermes model
# → 选择 "MiniMax (OAuth)"
# → 浏览器打开；用你的 MiniMax 账号（全球或中国区）登录
# → 确认 — 凭据会保存到 ~/.hermes/auth.json

hermes chat   # 使用 api.minimax.io/anthropic 端点
```

或者在 `config.yaml` 中配置：
```yaml
model:
  provider: "minimax-oauth"
  default: "MiniMax-M2.7"
```

支持的模型：`MiniMax-M2.7`（主模型）和 `MiniMax-M2.7-highspeed`（作为默认辅助模型）。OAuth 路径会忽略 `MINIMAX_API_KEY` / `MINIMAX_BASE_URL`。

:::tip MiniMax OAuth 与 API key 的区别
`minimax-oauth` 使用 MiniMax 面向消费者的门户，通过 OAuth 登录——无需设置计费。`minimax` 和 `minimax-cn` 提供商使用 `MINIMAX_API_KEY` / `MINIMAX_CN_API_KEY`——用于程序化访问。完整指南请参阅 [MiniMax OAuth 指南](/guides/minimax-oauth)。
:::
<a id="minimax-oauth-vs-api-key"></a>

### NVIDIA NIM {#nvidia-nim}

通过 [build.nvidia.com](https://build.nvidia.com)（免费 API key）或本地 NIM 端点使用 Nemotron 及其他开源模型。

```bash
# 云端（build.nvidia.com）
hermes chat --provider nvidia --model nvidia/nemotron-3-super-120b-a12b
# 需要：在 ~/.hermes/.env 中设置 NVIDIA_API_KEY

# 本地 NIM 端点——覆盖 base URL
NVIDIA_BASE_URL=http://localhost:8000/v1 hermes chat --provider nvidia --model nvidia/nemotron-3-super-120b-a12b
```

或者永久设置在 `config.yaml` 中：
```yaml
model:
  provider: "nvidia"
  default: "nvidia/nemotron-3-super-120b-a12b"
```

:::tip 本地 NIM
对于本地部署（DGX Spark、本地 GPU），设置 `NVIDIA_BASE_URL=http://localhost:8000/v1`。NIM 暴露了与 build.nvidia.com 相同的 OpenAI 兼容聊天补全 API，因此在云端和本地之间切换只需一行环境变量更改。
<a id="local-nim"></a>
:::

### Hugging Face Inference Providers {#hugging-face-inference-providers}

[Hugging Face Inference Providers](https://huggingface.co/docs/inference-providers) 通过统一的 OpenAI 兼容端点（`router.huggingface.co/v1`）路由到 20 多个开放模型。请求会自动路由到最快的可用后端（Groq、Together、SambaNova 等），并自动故障转移。

```bash
# 使用任何可用模型
hermes chat --provider huggingface --model Qwen/Qwen3-235B-A22B-Thinking-2507
# 需要：在 ~/.hermes/.env 中设置 HF_TOKEN

# 短别名
hermes chat --provider hf --model deepseek-ai/DeepSeek-V3.2
```

或者永久设置在 `config.yaml` 中：
```yaml
model:
  provider: "huggingface"
  default: "Qwen/Qwen3-235B-A22B-Thinking-2507"
```

在 [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) 获取你的 token——确保启用“Make calls to Inference Providers”权限。包含免费套餐（每月 $0.10 额度，不额外加价）。

你可以在模型名称后附加路由后缀：`:fastest`（默认）、`:cheapest` 或 `:provider_name` 以强制使用特定后端。

可以通过 `HF_BASE_URL` 覆盖 base URL。

## 自定义与自托管 LLM 提供商 {#custom-self-hosted-llm-providers}

Hermes Agent 适用于**任何 OpenAI 兼容的 API 端点**。如果服务器实现了 `/v1/chat/completions`，你就可以将 Hermes 指向它。这意味着你可以使用本地模型、GPU 推理服务器、多提供商路由器或任何第三方 API。
### 通用设置 {#general-setup}

配置自定义端点有三种方式：

**交互式设置（推荐）：**
```bash
hermes model
# 选择 "Custom endpoint (self-hosted / VLLM / etc.)"
# 输入：API 基础 URL、API 密钥、模型名称
```

**手动配置（`config.yaml`）：**
```yaml
# 在 ~/.hermes/config.yaml 中
model:
  default: your-model-name
  provider: custom
  base_url: http://localhost:8000/v1
  api_key: your-key-or-leave-empty-for-local
```

:::warning 旧版环境变量
`.env` 中的 `OPENAI_BASE_URL` 和 `LLM_MODEL` 已被**移除**。Hermes 的任何部分都不会读取它们——`config.yaml` 是模型和端点配置的唯一真实来源。如果你的 `.env` 中有过时的条目，它们会在下次执行 `hermes setup` 或配置迁移时自动清除。请使用 `hermes model` 或直接编辑 `config.yaml`。
<a id="legacy-env-vars"></a>
:::

两种方式都会持久化到 `config.yaml`，该文件是模型、提供者和基础 URL 的唯一真实来源。

### 使用 `/model` 切换模型 {#switching-models-with-model}

:::warning hermes model 与 /model 的区别
<a id="hermes-model-vs-model"></a>
**`hermes model`**（在终端中运行，不在任何聊天会话内）是**完整的提供者设置向导**。用于添加新的提供者、运行 OAuth 流程、输入 API 密钥以及配置自定义端点。

**`/model`**（在活跃的 Hermes 聊天会话中输入）只能**在已设置好的提供者和模型之间切换**。它无法添加新的提供者、运行 OAuth 或提示输入 API 密钥。如果你只配置了一个提供者（例如 OpenRouter），`/model` 只会显示该提供者的模型。

**要添加新的提供者：** 退出当前会话（`Ctrl+C` 或 `/quit`），运行 `hermes model`，设置好新的提供者，然后启动一个新会话。
:::

一旦你配置了至少一个自定义端点，就可以在会话中切换模型：

```
/model custom:qwen-2.5          # 切换到自定义端点上的模型
/model custom                    # 从端点自动检测模型
/model openrouter:claude-sonnet-4 # 切换回云提供者
```

如果你配置了**命名自定义提供者**（见下文），请使用三重语法：

```
/model custom:local:qwen-2.5    # 使用名为 "local" 的自定义提供者，模型为 qwen-2.5
/model custom:work:llama3       # 使用名为 "work" 的自定义提供者，模型为 llama3
```

切换提供者时，Hermes 会将基础 URL 和提供者持久化到配置中，以便重启后更改仍然生效。当从自定义端点切换到内置提供者时，过时的基础 URL 会自动清除。

:::tip
`/model custom`（裸命令，不带模型名称）会查询端点的 `/models` API，如果只加载了一个模型，则自动选择该模型。对于运行单个模型的本地服务器非常有用。
:::

以下所有内容都遵循相同的模式——只需更改 URL、密钥和模型名称。

---

### Ollama — 本地模型，零配置 {#ollama-local-models-zero-config}

[Ollama](https://ollama.com/) 通过一条命令在本地运行开放权重模型。最适合：快速本地实验、隐私敏感工作、离线使用。通过兼容 OpenAI 的 API 支持工具调用。

```bash
# 安装并运行一个模型
ollama pull qwen2.5-coder:32b
ollama serve   # 在端口 11434 上启动
```
然后配置 Hermes：

```bash
hermes model
# 选择 "Custom endpoint (self-hosted / VLLM / etc.)"
# 输入 URL: http://localhost:11434/v1
# 跳过 API key（Ollama 不需要）
# 输入模型名称（例如 qwen2.5-coder:32b）
```

或者直接编辑 `config.yaml`：

```yaml
model:
  default: qwen2.5-coder:32b
  provider: custom
  base_url: http://localhost:11434/v1
  context_length: 32768   # 见下方警告
```

:::caution Ollama 默认上下文长度非常低
<a id="ollama-defaults-to-very-low-context-lengths"></a>
Ollama **默认不会**使用模型完整的上下文窗口。根据你的显存，默认值如下：

| 可用显存 | 默认上下文 |
|----------------|----------------|
| 小于 24 GB | **4,096 tokens** |
| 24–48 GB | 32,768 tokens |
| 48+ GB | 256,000 tokens |

对于使用工具的 Agent，**你至少需要 16k–32k 的上下文**。在 4k 下，仅系统提示词和工具 schema 就可能填满窗口，没有空间留给对话。

**如何增加上下文长度**（任选其一）：

```bash
# 选项 1：通过环境变量设置服务器全局（推荐）
OLLAMA_CONTEXT_LENGTH=32768 ollama serve

# 选项 2：对于 systemd 管理的 Ollama
sudo systemctl edit ollama.service
# 添加：Environment="OLLAMA_CONTEXT_LENGTH=32768"
# 然后：sudo systemctl daemon-reload && sudo systemctl restart ollama

# 选项 3：将其嵌入自定义模型（每个模型持久化）
echo -e "FROM qwen2.5-coder:32b\nPARAMETER num_ctx 32768" > Modelfile
ollama create qwen2.5-coder-32k -f Modelfile
```

**你不能通过 OpenAI 兼容的 API**（`/v1/chat/completions`）设置上下文长度。必须在服务端或通过 Modelfile 配置。这是将 Ollama 与 Hermes 等工具集成时最容易混淆的地方。
:::

**验证上下文是否设置正确：**

```bash
ollama ps
# 查看 CONTEXT 列——它应该显示你配置的值
```

:::tip
使用 `ollama list` 列出可用模型。使用 `ollama pull &lt;model&gt;` 从 [Ollama 库](https://ollama.com/library) 拉取任何模型。Ollama 会自动处理 GPU 卸载——大多数情况下无需配置。
:::

---

### vLLM — 高性能 GPU 推理 {#vllm-high-performance-gpu-inference}

[vLLM](https://docs.vllm.ai/) 是生产级 LLM 服务的标准。最适合：在 GPU 硬件上实现最大吞吐量、服务大型模型、连续批处理。

```bash
pip install vllm
vllm serve meta-llama/Llama-3.1-70B-Instruct \
  --port 8000 \
  --max-model-len 65536 \
  --tensor-parallel-size 2 \
  --enable-auto-tool-choice \
  --tool-call-parser hermes
```

然后配置 Hermes：

```bash
hermes model
# 选择 "Custom endpoint (self-hosted / VLLM / etc.)"
# 输入 URL: http://localhost:8000/v1
# 跳过 API key（如果你用 --api-key 配置了 vLLM，则输入一个）
# 输入模型名称：meta-llama/Llama-3.1-70B-Instruct
```

**上下文长度：** vLLM 默认读取模型的 `max_position_embeddings`。如果该值超过你的 GPU 内存，它会报错并要求你设置更低的 `--max-model-len`。你也可以使用 `--max-model-len auto` 自动找到能容纳的最大值。设置 `--gpu-memory-utilization 0.95`（默认 0.9）以在显存中挤出更多上下文。
**工具调用需要显式标志：**

| 标志 | 用途 |
|------|------|
| `--enable-auto-tool-choice` | 对于 `tool_choice: "auto"`（Hermes 默认值）是必需的 |
| `--tool-call-parser &lt;name&gt;` | 模型工具调用格式的解析器 |

支持的解析器：`hermes`（Qwen 2.5、Hermes 2/3）、`llama3_json`（Llama 3.x）、`mistral`、`deepseek_v3`、`deepseek_v31`、`xlam`、`pythonic`。没有这些标志，工具调用将无法工作——模型会将工具调用输出为文本。

:::tip
vLLM 支持人类可读的尺寸：`--max-model-len 64k`（小写 k = 1000，大写 K = 1024）。
:::

---

### SGLang — 使用 RadixAttention 实现快速服务 {#sglang-fast-serving-with-radixattention}

[SGLang](https://github.com/sgl-project/sglang) 是 vLLM 的替代方案，利用 RadixAttention 实现 KV 缓存复用。适用于：多轮对话（前缀缓存）、受限解码、结构化输出。

```bash
pip install "sglang[all]"
python -m sglang.launch_server \
  --model meta-llama/Llama-3.1-70B-Instruct \
  --port 30000 \
  --context-length 65536 \
  --tp 2 \
  --tool-call-parser qwen
```

然后配置 Hermes：

```bash
hermes model
# 选择 "Custom endpoint（自托管 / VLLM 等）"
# 输入 URL：http://localhost:30000/v1
# 输入模型名称：meta-llama/Llama-3.1-70B-Instruct
```

**上下文长度：** SGLang 默认从模型配置中读取。使用 `--context-length` 覆盖。如果需要超过模型声明的最大长度，设置 `SGLANG_ALLOW_OVERWRITE_LONGER_CONTEXT_LEN=1`。

**工具调用：** 使用 `--tool-call-parser` 并指定适合你模型系列的解析器：`qwen`（Qwen 2.5）、`llama3`、`llama4`、`deepseekv3`、`mistral`、`glm`。没有这个标志，工具调用将以纯文本形式返回。

:::caution SGLang 默认最多输出 128 个 token
<a id="sglang-defaults-to-128-max-output-tokens"></a>
如果回复似乎被截断，请在请求中添加 `max_tokens`，或在服务器上设置 `--default-max-tokens`。如果请求中未指定，SGLang 每次回复默认只有 128 个 token。
:::

---

### llama.cpp / llama-server — CPU 和 Metal 推理 {#llama-cpp-llama-server-cpu-metal-inference}

[llama.cpp](https://github.com/ggml-org/llama.cpp) 在 CPU、Apple Silicon（Metal）和消费级 GPU 上运行量化模型。适用于：无需数据中心 GPU 即可运行模型、Mac 用户、边缘部署。

```bash
# 构建并启动 llama-server
cmake -B build && cmake --build build --config Release
./build/bin/llama-server \
  --jinja -fa \
  -c 32768 \
  -ngl 99 \
  -m models/qwen2.5-coder-32b-instruct-Q4_K_M.gguf \
  --port 8080 --host 0.0.0.0
```

**上下文长度（`-c`）：** 最近的构建默认值为 `0`，会从 GGUF 元数据中读取模型的训练上下文。对于训练上下文为 128k+ 的模型，尝试分配完整的 KV 缓存可能会导致 OOM。请根据需要明确设置 `-c`（Agent 使用 32k–64k 是一个不错的范围）。如果使用并行插槽（`-np`），总上下文会在插槽之间分配——如果使用 `-c 32768 -np 4`，每个插槽只获得 8k。

然后将 Hermes 指向它：

```bash
hermes model
# 选择 "Custom endpoint（自托管 / VLLM 等）"
# 输入 URL：http://localhost:8080/v1
# 跳过 API 密钥（本地服务器不需要）
# 输入模型名称——如果只加载了一个模型，留空可自动检测
```
这将端点保存到 `config.yaml`，使其在会话间持久化。

:::caution 工具调用必须使用 `--jinja`
如果不加 `--jinja`，llama-server 会完全忽略 `tools` 参数。模型会尝试通过在响应文本中写 JSON 来调用工具，但 Hermes 不会将其识别为工具调用——你会看到类似 `{"name": "web_search", ...}` 的原始 JSON 作为消息输出，而不是真正的搜索。
<a id="jinja-is-required-for-tool-calling"></a>

原生工具调用支持（性能最佳）：Llama 3.x、Qwen 2.5（包含 Coder）、Hermes 2/3、Mistral、DeepSeek、Functionary。其他所有模型使用通用处理程序，虽然可用但效率可能较低。完整列表请参见 [llama.cpp 函数调用文档](https://github.com/ggml-org/llama.cpp/blob/master/docs/function-calling.md)。

你可以通过检查 `http://localhost:8080/props` 来验证工具支持是否启用——`chat_template` 字段应该存在。
:::

:::tip
从 [Hugging Face](https://huggingface.co/models?library=gguf) 下载 GGUF 模型。Q4_K_M 量化在质量与内存占用之间提供了最佳平衡。
:::

---

### LM Studio —— 带本地模型的桌面应用 {#lm-studio-desktop-app-with-local-models}

[LM Studio](https://lmstudio.ai/) 是一款用于运行本地模型的桌面应用，提供图形界面。最适合：喜欢可视化界面的用户、快速模型测试、macOS/Windows/Linux 上的开发者。

从 LM Studio 应用启动服务器（开发者选项卡 → 启动服务器），或者使用 CLI：

```bash
lms server start                        # 在端口 1234 上启动
lms load qwen2.5-coder --context-length 32768
```

然后配置 Hermes：

```bash
hermes model
# 选择 "LM Studio"
# 按 Enter 使用 http://localhost:1234/v1
# 选择一个发现的模型
# 如果 LM Studio 服务器启用了身份验证，按提示输入 LM_API_KEY
```

Hermes 会自动加载具有 64K 上下文长度的 LM Studio 模型

在 LM Studio 中更改上下文长度：

1. 点击模型选择器旁边的齿轮图标
2. 将 "Context Length" 设置为至少 64000，以获得流畅体验
3. 重新加载模型使更改生效
4. 如果你的机器无法容纳 64000，可以考虑使用具有更大上下文长度的更小模型。

或者使用 CLI：`lms load model-name --context-length 64000`

你可以使用 CLI 估算模型是否适合：`lms load model-name --context-length 64000 --estimate-only`

设置持久的每模型默认值：我的模型选项卡 → 模型上的齿轮图标 → 设置上下文大小。

**工具调用：** 自 LM Studio 0.3.6 起支持。具有原生工具调用训练的模型（Qwen 2.5、Llama 3.x、Mistral、Hermes）会自动检测并显示工具徽章。其他模型使用可能不太可靠的通用回退。

---

### WSL2 网络（Windows 用户） {#wsl2-networking-windows-users}

由于 Hermes Agent 需要 Unix 环境，Windows 用户在 WSL2 内运行它。如果你的模型服务器（Ollama、LM Studio 等）运行在 **Windows 主机**上，你需要桥接网络差距——WSL2 使用拥有自己子网的虚拟网络适配器，因此 WSL2 中的 `localhost` 指向的是 Linux 虚拟机，**而不是** Windows 主机。
:::tip 两个都在 WSL2 里？没问题。
如果你的模型服务器也运行在 WSL2 内部（vLLM、SGLang 和 llama-server 常见这种情况），`localhost` 可以正常使用——它们共享同一个网络命名空间。跳过本节即可。
:::
<a id="both-in-wsl2-no-problem"></a>

#### 选项 1：镜像网络模式（推荐） {#option-1-mirrored-networking-mode-recommended}

**Windows 11 22H2+** 可用，镜像模式让 `localhost` 在 Windows 和 WSL2 之间双向互通——最简单的修复方式。

1. 创建或编辑 `%USERPROFILE%\.wslconfig`（例如 `C:\Users\你的用户名\.wslconfig`）：
   ```ini
   [wsl2]
   networkingMode=mirrored
   ```

2. 在 PowerShell 中重启 WSL：
   ```powershell
   wsl --shutdown
   ```

3. 重新打开 WSL2 终端。现在 `localhost` 可以访问 Windows 服务：
   ```bash
   curl http://localhost:11434/v1/models   # Windows 上的 Ollama —— 可以工作
   ```

:::note Hyper-V 防火墙
在某些 Windows 11 版本中，Hyper-V 防火墙默认会阻止镜像连接。如果启用镜像模式后 `localhost` 仍然无法工作，请在**管理员 PowerShell** 中运行以下命令：
<a id="hyper-v-firewall"></a>
```powershell
Set-NetFirewallHyperVVMSetting -Name '{40E0AC32-46A5-438A-A0B2-2B479E8F2E90}' -DefaultInboundAction Allow
```
:::

#### 选项 2：使用 Windows 主机 IP（Windows 10 / 旧版本） {#option-2-use-the-windows-host-ip-windows-10-older-builds}

如果无法使用镜像模式，可以从 WSL2 内部找到 Windows 主机 IP，然后用它代替 `localhost`：

```bash
# 获取 Windows 主机 IP（WSL2 虚拟网络的默认网关）
ip route show | grep -i default | awk '{ print $3 }'
# 示例输出：172.29.192.1
```

在 Hermes 配置中使用该 IP：

```yaml
model:
  default: qwen2.5-coder:32b
  provider: custom
  base_url: http://172.29.192.1:11434/v1   # Windows 主机 IP，不是 localhost
```

:::tip 动态获取
<a id="dynamic-helper"></a>
主机 IP 在 WSL2 重启后可能会变化。你可以在 shell 中动态获取它：
```bash
export WSL_HOST=$(ip route show | grep -i default | awk '{ print $3 }')
echo "Windows 主机地址：$WSL_HOST"
curl http://$WSL_HOST:11434/v1/models   # 测试 Ollama
```

或者使用机器的 mDNS 名称（需要在 WSL2 中安装 `libnss-mdns`）：
```bash
sudo apt install libnss-mdns
curl http://$(hostname).local:11434/v1/models
```
:::

#### 服务器绑定地址（NAT 模式必需） {#server-bind-address-required-for-nat-mode}

如果你使用**选项 2**（NAT 模式 + 主机 IP），Windows 上的模型服务器必须接受来自 `127.0.0.1` 之外的连接。默认情况下，大多数服务器只监听 localhost——NAT 模式下 WSL2 的连接来自不同的虚拟子网，会被拒绝。在镜像模式下，`localhost` 直接映射，因此默认的 `127.0.0.1` 绑定可以正常工作。

| 服务器 | 默认绑定 | 如何修复 |
|--------|---------|----------|
| **Ollama** | `127.0.0.1` | 在启动 Ollama 之前设置 `OLLAMA_HOST=0.0.0.0` 环境变量（Windows 系统设置 → 环境变量，或编辑 Ollama 服务） |
| **LM Studio** | `127.0.0.1` | 在开发者选项卡 → 服务器设置中启用 **"Serve on Network"** |
| **llama-server** | `127.0.0.1` | 在启动命令中添加 `--host 0.0.0.0` |
| **vLLM** | `0.0.0.0` | 默认已绑定所有接口 |
| **SGLang** | `127.0.0.1` | 在启动命令中添加 `--host 0.0.0.0` |
**Windows 上的 Ollama（详细说明）：** Ollama 以 Windows 服务形式运行。要设置 `OLLAMA_HOST`：
1. 打开 **系统属性** → **环境变量**
2. 添加一个新的 **系统变量**：`OLLAMA_HOST` = `0.0.0.0`
3. 重启 Ollama 服务（或重启系统）

#### Windows 防火墙 {#windows-firewall}

Windows 防火墙将 WSL2 视为一个独立的网络（在 NAT 和镜像模式下都是如此）。如果执行上述步骤后连接仍然失败，请为模型服务器的端口添加一条防火墙规则：

```powershell
# 在管理员 PowerShell 中运行 — 将 PORT 替换为你的服务器端口
New-NetFirewallRule -DisplayName "允许 WSL2 访问模型服务器" -Direction Inbound -Action Allow -Protocol TCP -LocalPort 11434
```

常见端口：Ollama `11434`，vLLM `8000`，SGLang `30000`，llama-server `8080`，LM Studio `1234`。

#### 快速验证 {#quick-verification}

在 WSL2 内部，测试能否访问你的模型服务器：

```bash
# 将 URL 替换为你的服务器地址和端口
curl http://localhost:11434/v1/models          # 镜像模式
curl http://172.29.192.1:11434/v1/models       # NAT 模式（使用你的实际主机 IP）
```

如果返回一个列出你模型的 JSON 响应，说明配置正确。在 Hermes 配置中使用相同的 URL 作为 `base_url`。

---

### 本地模型故障排查 {#troubleshooting-local-models}

以下问题会影响 **所有** 与 Hermes 配合使用的本地推理服务器。

#### 从 WSL2 访问 Windows 上托管的模型服务器时出现“连接被拒绝” {#connection-refused-from-wsl2-to-a-windows-hosted-model-server}

如果你在 WSL2 内部运行 Hermes，而模型服务器在 Windows 主机上，那么在 WSL2 的默认 NAT 网络模式下，`http://localhost:&lt;port&gt;` 将无法工作。请参考上面的 [WSL2 网络配置](#wsl2-networking-windows-users) 部分进行修复。

#### 工具调用显示为文本而非实际执行 {#tool-calls-appear-as-text-instead-of-executing}

模型输出类似 `{"name": "web_search", "arguments": {...}}` 的消息，而不是实际调用工具。

**原因：** 你的服务器未启用工具调用功能，或者模型不支持该服务器提供的工具调用实现。

| 服务器 | 修复方法 |
|--------|----------|
| **llama.cpp** | 在启动命令中添加 `--jinja` |
| **vLLM** | 添加 `--enable-auto-tool-choice --tool-call-parser hermes` |
| **SGLang** | 添加 `--tool-call-parser qwen`（或合适的解析器） |
| **Ollama** | 工具调用默认已启用 — 确保你的模型支持（使用 `ollama show model-name` 检查） |
| **LM Studio** | 更新到 0.3.6+ 并使用原生支持工具的模型 |

#### 模型似乎忘记上下文或给出不连贯的回复 {#model-seems-to-forget-context-or-give-incoherent-responses}

**原因：** 上下文窗口太小。当对话超过上下文限制时，大多数服务器会静默丢弃较早的消息。Hermes 的系统提示词 + 工具模式本身就可能占用 4k–8k token。

**诊断方法：**

```bash
# 检查 Hermes 认为的上下文大小
# 查看启动行："Context limit: X tokens"

# 检查服务器的实际上下文
# Ollama: ollama ps（CONTEXT 列）
# llama.cpp: curl http://localhost:8080/props | jq '.default_generation_settings.n_ctx'
# vLLM: 检查启动参数中的 --max-model-len
```

**修复方法：** 将上下文设置为至少 **32,768 tokens** 用于 Agent 使用。请参考上面各服务器的具体参数说明。
#### 启动时提示"上下文限制：2048 tokens" {#context-limit-2048-tokens-at-startup}

Hermes 会自动从服务器的 `/v1/models` 端点检测上下文长度。如果服务器报告的值较低（或根本没有报告），Hermes 会使用模型声明的限制，这可能是错误的。

**解决方法：** 在 `config.yaml` 中显式设置：

```yaml
model:
  default: your-model
  provider: custom
  base_url: http://localhost:11434/v1
  context_length: 32768
```

#### 回复在句子中间被截断 {#responses-get-cut-off-mid-sentence}

**可能的原因：**
1. **服务器上的输出上限（`max_tokens`）过低** — SGLang 默认每个回复为 128 个 token。在服务器上设置 `--default-max-tokens`，或在 Hermes 的 config.yaml 中配置 `model.max_tokens`。注意：`max_tokens` 仅控制回复长度——与对话历史能有多长无关（那是 `context_length` 的事）。
2. **上下文耗尽** — 模型填满了它的上下文窗口。增加 `model.context_length` 或在 Hermes 中启用[上下文压缩](/user-guide/configuration#context-compression)。

---

### LiteLLM 代理 — 多提供商网关 {#litellm-proxy-multi-provider-gateway}

[LiteLLM](https://docs.litellm.ai/) 是一个兼容 OpenAI 的代理，它将 100 多个 LLM 提供商统一到单个 API 后面。最适合：无需更改配置即可切换提供商、负载均衡、回退链、预算控制。

```bash
# 安装并启动
pip install "litellm[proxy]"
litellm --model anthropic/claude-sonnet-4 --port 4000

# 或者使用配置文件来管理多个模型：
litellm --config litellm_config.yaml --port 4000
```

然后使用 `hermes model` → 自定义端点 → `http://localhost:4000/v1` 配置 Hermes。

带回退功能的 `litellm_config.yaml` 示例：
```yaml
model_list:
  - model_name: "best"
    litellm_params:
      model: anthropic/claude-sonnet-4
      api_key: sk-ant-...
  - model_name: "best"
    litellm_params:
      model: openai/gpt-4o
      api_key: sk-...
router_settings:
  routing_strategy: "latency-based-routing"
```

---

### ClawRouter — 成本优化路由 {#clawrouter-cost-optimized-routing}

[ClawRouter](https://github.com/BlockRunAI/ClawRouter) 由 BlockRunAI 开发，是一个本地路由代理，可根据查询复杂度自动选择模型。它会在 14 个维度上对请求进行分类，并路由到能处理该任务的最便宜的模型。支付通过 USDC 加密货币进行（无需 API 密钥）。

```bash
# 安装并启动
npx @blockrun/clawrouter    # 在端口 8402 上启动
```

然后使用 `hermes model` → 自定义端点 → `http://localhost:8402/v1` → 模型名称 `blockrun/auto` 配置 Hermes。

路由配置：
| 配置 | 策略 | 节省成本 |
|---------|----------|---------|
| `blockrun/auto` | 平衡质量/成本 | 74-100% |
| `blockrun/eco` | 尽可能便宜 | 95-100% |
| `blockrun/premium` | 最佳质量模型 | 0% |
| `blockrun/free` | 仅限免费模型 | 100% |
| `blockrun/agentic` | 针对工具使用优化 | 视情况而定 |

:::note
ClawRouter 需要一个在 Base 或 Solana 上充值的 USDC 钱包用于支付。所有请求都通过 BlockRun 的后端 API 路由。运行 `npx @blockrun/clawrouter doctor` 检查钱包状态。
:::

### 上下文长度检测 {#context-length-detection}

<a id="two-settings-easy-to-confuse"></a>
:::note 两个容易混淆的设置
**`context_length`** 是 **总上下文窗口** — 输入和输出 token 的合计预算（例如 Claude Opus 4.6 为 200,000）。Hermes 使用它来决定何时压缩历史记录以及验证 API 请求。

**`model.max_tokens`** 是 **输出上限** — 模型在*单次响应*中最多可以生成的 token 数量。它与你的对话历史能有多长无关。行业标准名称 `max_tokens` 是常见的混淆来源；Anthropic 的原生 API 后来已将其重命名为 `max_output_tokens` 以更清晰。

当自动检测得到的窗口大小不正确时，请设置 `context_length`。
仅当你需要限制单个响应的长度时，才设置 `model.max_tokens`。
:::

Hermes 使用多源解析链来检测你的模型和提供商的正确上下文窗口：

1. **配置覆盖** — `config.yaml` 中的 `model.context_length`（最高优先级）
2. **自定义提供商按模型设置** — `custom_providers[].models.&lt;id&gt;.context_length`
3. **持久缓存** — 之前发现的值（重启后仍保留）
4. **端点 `/models`** — 查询你的服务器 API（本地/自定义端点）
5. **Anthropic `/v1/models`** — 查询 Anthropic 的 API 以获取 `max_input_tokens`（仅限 API 密钥用户）
6. **OpenRouter API** — 来自 OpenRouter 的实时模型元数据
7. **Nous Portal** — 将 Nous 模型 ID 与 OpenRouter 元数据进行后缀匹配
8. **[models.dev](https://models.dev)** — 社区维护的注册表，包含 100 多个提供商中 3800 多个模型的特定提供商上下文长度
9. **回退默认值** — 广泛的模型家族模式（默认 128K）

---
对于大多数配置来说，这开箱即用。系统能感知提供商——同一个模型可能因服务方不同而有不同的上下文限制（例如，`claude-opus-4.6` 在 Anthropic 直连时是 1M，但在 GitHub Copilot 上则是 128K）。

要显式设置上下文长度，请在模型配置中添加 `context_length`：

```yaml
model:
  default: "qwen3.5:9b"
  base_url: "http://localhost:8080/v1"
  context_length: 131072  # 令牌数
```

对于自定义端点，你也可以按模型设置上下文长度：

```yaml
custom_providers:
  - name: "我的本地 LLM"
    base_url: "http://localhost:11434/v1"
    models:
      qwen3.5:27b:
        context_length: 32768
      deepseek-r1:70b:
        context_length: 65536
```

使用 `hermes model` 配置自定义端点时，会提示输入上下文长度。留空则自动检测。

:::tip 何时需要手动设置
- 你正在使用 Ollama，且自定义的 `num_ctx` 低于模型的最大值
<a id="when-to-set-this-manually"></a>
- 你想将上下文限制在模型最大值以下（例如，在 128k 模型上设为 8k 以节省显存）
- 你的请求经过一个不暴露 `/v1/models` 的代理
:::

---

### 命名的自定义提供商 {#named-custom-providers}

如果你使用多个自定义端点（例如，本地开发服务器和远程 GPU 服务器），你可以在 `config.yaml` 中将其定义为命名的自定义提供商：

```yaml
custom_providers:
  - name: local
    base_url: http://localhost:8080/v1
    # api_key 省略 — Hermes 对无密钥的本地服务器使用 "no-key-required"
  - name: work
    base_url: https://gpu-server.internal.corp/v1
    key_env: CORP_API_KEY
    api_mode: chat_completions   # 可选，从 URL 自动检测
  - name: anthropic-proxy
    base_url: https://proxy.example.com/anthropic
    key_env: ANTHROPIC_PROXY_KEY
    api_mode: anthropic_messages  # 用于兼容 Anthropic 的代理
```

在会话中切换它们，使用三重语法：

```
/model custom:local:qwen-2.5       # 使用 "local" 端点和 qwen-2.5
/model custom:work:llama3-70b      # 使用 "work" 端点和 llama3-70b
/model custom:anthropic-proxy:claude-sonnet-4  # 使用代理
```

你也可以从交互式 `hermes model` 菜单中选择命名的自定义提供商。

---

### 选择合适的配置 {#choosing-the-right-setup}

| 使用场景 | 推荐 |
|----------|------|
| **只要能用就行** | OpenRouter（默认）或 Nous Portal |
| **本地模型，简单配置** | Ollama |
| **生产环境 GPU 服务** | vLLM 或 SGLang |
| **Mac / 无 GPU** | Ollama 或 llama.cpp |
| **多提供商路由** | LiteLLM Proxy 或 OpenRouter |
| **成本优化** | ClawRouter 或 OpenRouter（配合 `sort: "price"`） |
| **最大隐私保护** | Ollama、vLLM 或 llama.cpp（完全本地） |
| **企业 / Azure** | 使用自定义端点的 Azure OpenAI |
| **中国 AI 模型** | z.ai（GLM）、Kimi/Moonshot（`kimi-coding` 或 `kimi-coding-cn`）、MiniMax、小米 MiMo 或腾讯 TokenHub（一级提供商） |

:::tip
你可以随时使用 `hermes model` 切换提供商，无需重启。你的对话历史、记忆和技能会随你一起迁移，无论使用哪个提供商。
:::
## 可选 API 密钥 {#optional-api-keys}

| 功能 | 提供商 | 环境变量 |
|---------|----------|--------------|
| 网页抓取 | [Firecrawl](https://firecrawl.dev/) | `FIRECRAWL_API_KEY`, `FIRECRAWL_API_URL` |
| 浏览器自动化 | [Browserbase](https://browserbase.com/) | `BROWSERBASE_API_KEY`, `BROWSERBASE_PROJECT_ID` |
| 图像生成 | [FAL](https://fal.ai/) | `FAL_KEY` |
| 高级 TTS 语音 | [ElevenLabs](https://elevenlabs.io/) | `ELEVENLABS_API_KEY` |
| OpenAI TTS + 语音转录 | [OpenAI](https://platform.openai.com/api-keys) | `VOICE_TOOLS_OPENAI_KEY` |
| Mistral TTS + 语音转录 | [Mistral](https://console.mistral.ai/) | `MISTRAL_API_KEY` |
| 强化学习训练 | [Tinker](https://tinker-console.thinkingmachines.ai/) + [WandB](https://wandb.ai/) | `TINKER_API_KEY`, `WANDB_API_KEY` |
| 跨会话用户建模 | [Honcho](https://honcho.dev/) | `HONCHO_API_KEY` |
| 语义长期记忆 | [Supermemory](https://supermemory.ai) | `SUPERMEMORY_API_KEY` |

### 自托管 Firecrawl {#self-hosting-firecrawl}

默认情况下，Hermes 使用 [Firecrawl 云 API](https://firecrawl.dev/) 进行网页搜索和抓取。如果你更倾向于在本地运行 Firecrawl，可以将 Hermes 指向自托管实例。完整的设置说明请参见 Firecrawl 的 [SELF_HOST.md](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md)。

**你得到的好处：** 无需 API 密钥，无速率限制，无按页计费，完全的数据主权。

**你失去的：** 云版本使用 Firecrawl 专有的 "Fire-engine" 进行高级反爬绕过（Cloudflare、CAPTCHA、IP 轮换）。自托管版本使用基本的 fetch + Playwright，因此某些受保护的网站可能会失败。搜索使用 DuckDuckGo 而非 Google。

**设置步骤：**

1. 克隆并启动 Firecrawl Docker 栈（5 个容器：API、Playwright、Redis、RabbitMQ、PostgreSQL — 需要约 4-8 GB 内存）：
   ```bash
   git clone https://github.com/firecrawl/firecrawl
   cd firecrawl
   # 在 .env 中设置：USE_DB_AUTHENTICATION=false, HOST=0.0.0.0, PORT=3002
   docker compose up -d
   ```

2. 将 Hermes 指向你的实例（无需 API 密钥）：
   ```bash
   hermes config set FIRECRAWL_API_URL http://localhost:3002
   ```

如果你的自托管实例启用了身份验证，你也可以同时设置 `FIRECRAWL_API_KEY` 和 `FIRECRAWL_API_URL`。

## OpenRouter 提供商路由 {#openrouter-provider-routing}

使用 OpenRouter 时，你可以控制请求如何在提供商之间路由。在 `~/.hermes/config.yaml` 中添加 `provider_routing` 部分：

```yaml
provider_routing:
  sort: "throughput"          # "price"（默认）、"throughput" 或 "latency"
  # only: ["anthropic"]      # 仅使用这些提供商
  # ignore: ["deepinfra"]    # 跳过这些提供商
  # order: ["anthropic", "google"]  # 按此顺序尝试提供商
  # require_parameters: true  # 仅使用支持所有请求参数的提供商
  # data_collection: "deny"   # 排除可能存储/训练数据的提供商
```

**快捷方式：** 在任何模型名称后追加 `:nitro` 以按吞吐量排序（例如 `anthropic/claude-sonnet-4:nitro`），或追加 `:floor` 以按价格排序。
## 备用模型 {#fallback-model}

配置一个备用提供商:模型，当您的主模型出现故障（速率限制、服务器错误、认证失败）时，Hermes 会自动切换到该备用模型：

```yaml
fallback_model:
  provider: openrouter                    # 必填
  model: anthropic/claude-sonnet-4        # 必填
  # base_url: http://localhost:8000/v1    # 可选，用于自定义端点
  # key_env: MY_CUSTOM_KEY               # 可选，自定义端点 API 密钥的环境变量名
```

激活后，备用模型会在会话中途切换模型和提供商，而不会丢失您的对话。每个会话**最多触发一次**。

支持的提供商：`openrouter`、`nous`、`openai-codex`、`copilot`、`copilot-acp`、`anthropic`、`gemini`、`google-gemini-cli`、`qwen-oauth`、`huggingface`、`zai`、`kimi-coding`、`kimi-coding-cn`、`minimax`、`minimax-cn`、`minimax-oauth`、`deepseek`、`nvidia`、`xai`、`ollama-cloud`、`bedrock`、`ai-gateway`、`opencode-zen`、`opencode-go`、`kilocode`、`xiaomi`、`arcee`、`gmi`、`alibaba`、`tencent-tokenhub`、`custom`。

:::tip
备用模型完全通过 `config.yaml` 配置——没有对应的环境变量。有关触发条件、支持的提供商以及它与辅助任务和委托的交互方式的完整详情，请参阅[备用提供商](/user-guide/features/fallback-providers)。
:::

---

## 另请参阅 {#see-also}

- [配置](/user-guide/configuration) — 通用配置（目录结构、配置优先级、终端后端、内存、压缩等）
- [环境变量](/reference/environment-variables) — 所有环境变量的完整参考
