---
title: "AI 提供商"
sidebar_label: "AI 提供商"
sidebar_position: 1
---

<a id="ai-providers"></a>
# AI 提供商

本章介绍如何为 Hermes Agent 配置推理提供商——从 OpenRouter、Anthropic 等云 API，到 Ollama、vLLM 等自托管端点，再到高级路由和回退配置。你需要至少配置一个提供商才能使用 Hermes。

<a id="inference-providers"></a>
## 推理提供商

你至少需要一种方式连接 LLM。使用 `hermes model` 可以交互式切换提供商和模型，也可以直接配置：

| 提供商 | 配置方式 |
|--------|----------|
| **Nous Portal** | `hermes model`（OAuth，订阅制） |
| **OpenAI Codex** | `hermes model`（ChatGPT OAuth，使用 Codex 模型） |
| **GitHub Copilot** | `hermes model`（OAuth 设备码流程，`COPILOT_GITHUB_TOKEN`、`GH_TOKEN` 或 `gh auth token`） |
| **GitHub Copilot ACP** | `hermes model`（启动本地 `copilot --acp --stdio`） |
| **Anthropic** | `hermes model`（通过 OAuth 使用 Claude Max + 额外用量额度；也支持 Anthropic API key 或手动设置 token——见下方注释） |
| **OpenRouter** | 在 `~/.hermes/.env` 中设置 `OPENROUTER_API_KEY` |
| **NovitaAI** | 在 `~/.hermes/.env` 中设置 `NOVITA_API_KEY`（provider: `novita`，200+ 模型，Model API，Agent Sandbox，GPU Cloud） |
| **AI Gateway** | 在 `~/.hermes/.env` 中设置 `AI_GATEWAY_API_KEY`（provider: `ai-gateway`） |
| **z.ai / GLM** | 在 `~/.hermes/.env` 中设置 `GLM_API_KEY`（provider: `zai`） |
| **Kimi / Moonshot** | 在 `~/.hermes/.env` 中设置 `KIMI_API_KEY`（provider: `kimi-coding`） |
| **Kimi / Moonshot（中国）** | 在 `~/.hermes/.env` 中设置 `KIMI_CN_API_KEY`（provider: `kimi-coding-cn`；别名：`kimi-cn`、`moonshot-cn`） |
| **Arcee AI** | 在 `~/.hermes/.env` 中设置 `ARCEEAI_API_KEY`（provider: `arcee`；别名：`arcee-ai`、`arceeai`） |
| **GMI Cloud** | 在 `~/.hermes/.env` 中设置 `GMI_API_KEY`（provider: `gmi`；别名：`gmi-cloud`、`gmicloud`） |
| **MiniMax** | 在 `~/.hermes/.env` 中设置 `MINIMAX_API_KEY`（provider: `minimax`） |
| **MiniMax（中国）** | 在 `~/.hermes/.env` 中设置 `MINIMAX_CN_API_KEY`（provider: `minimax-cn`） |
| **xAI (Grok) — Responses API** | 在 `~/.hermes/.env` 中设置 `XAI_API_KEY`（provider: `xai`） |
| **xAI Grok OAuth (SuperGrok)** | `hermes model` → 选择「xAI Grok OAuth (SuperGrok Subscription)」——浏览器登录，无需 API key。详见 [指南](../guides/xai-grok-oauth.md) |
| **Qwen Cloud（阿里 DashScope）** | 在 `~/.hermes/.env` 中设置 `DASHSCOPE_API_KEY`（provider: `alibaba`） |
| **阿里云（编程方案）** | `DASHSCOPE_API_KEY`（provider: `alibaba-coding-plan`，别名：`alibaba_coding`）——独立计费 SKU，不同端点 |
| **Kilo Code** | 在 `~/.hermes/.env` 中设置 `KILOCODE_API_KEY`（provider: `kilocode`） |
| **小米 MiMo** | 在 `~/.hermes/.env` 中设置 `XIAOMI_API_KEY`（provider: `xiaomi`，别名：`mimo`、`xiaomi-mimo`） |
| **腾讯 TokenHub** | 在 `~/.hermes/.env` 中设置 `TOKENHUB_API_KEY`（provider: `tencent-tokenhub`，别名：`tencent`、`tokenhub`、`tencentmaas`） |
| **OpenCode Zen** | 在 `~/.hermes/.env` 中设置 `OPENCODE_ZEN_API_KEY`（provider: `opencode-zen`） |
| **OpenCode Go** | 在 `~/.hermes/.env` 中设置 `OPENCODE_GO_API_KEY`（provider: `opencode-go`） |
| **DeepSeek** | 在 `~/.hermes/.env` 中设置 `DEEPSEEK_API_KEY`（provider: `deepseek`） |
| **Hugging Face** | 在 `~/.hermes/.env` 中设置 `HF_TOKEN`（provider: `huggingface`，别名：`hf`） |
| **Google / Gemini** | 在 `~/.hermes/.env` 中设置 `GOOGLE_API_KEY`（或 `GEMINI_API_KEY`）（provider: `gemini`） |
| **Google Gemini (OAuth)** | `hermes model` → 选择「Google Gemini (OAuth)」（provider: `google-gemini-cli`，支持免费套餐，浏览器 PKCE 登录） |
| **LM Studio** | `hermes model` → 选择「LM Studio」（provider: `lmstudio`，可选 `LM_API_KEY`） |
| **自定义端点** | `hermes model` → 选择「Custom endpoint」（保存到 `config.yaml`） |
对于官方 API 密钥路径，请参阅专门的 [Google Gemini 指南](/guides/google-gemini)。

:::tip 模型键别名
<a id="model-key-alias"></a>
在 `model:` 配置部分，你可以使用 `default:` 或 `model:` 作为模型 ID 的键名。`model: { default: my-model }` 和 `model: { model: my-model }` 两者效果相同。
:::


<a id="google-gemini-via-oauth-google-gemini-cli"></a>
### 通过 OAuth 使用 Google Gemini（`google-gemini-cli`）

`google-gemini-cli` 提供者使用的是 Google 的 Cloud Code Assist 后端——也就是 Google 自己的 `gemini-cli` 工具所使用的同一个 API。它同时支持**免费层**（个人账户有慷慨的每日配额）和**付费层**（通过 GCP 项目使用 Standard/Enterprise）。

**快速开始：**

```bash
hermes model
# → 选择 "Google Gemini (OAuth)"
# → 查看策略警告，确认
# → 浏览器打开 accounts.google.com，登录
# → 完成——Hermes 会在首次请求时自动为你配置免费层
```

Hermes 默认携带了 Google 的**公开** `gemini-cli` 桌面 OAuth 客户端——也就是 Google 在其开源 `gemini-cli` 中包含的相同凭据。桌面 OAuth 客户端并非机密（PKCE 提供了安全性）。你无需安装 `gemini-cli` 或注册自己的 GCP OAuth 客户端。
**认证工作原理：**
- 基于 PKCE 授权码流程，对接 `accounts.google.com`
- 浏览器回调地址为 `http://127.0.0.1:8085/oauth2callback`（若端口占用则使用临时端口作为备用）
- Token 存储在 `~/.hermes/auth/google_oauth.json`（权限 0600，原子写入，跨进程 fcntl 锁）
- 过期前 60 秒自动刷新
- 无头环境（SSH、`HERMES_HEADLESS=1`）→ 回退到粘贴模式
- 飞行中刷新去重 — 两个并发请求不会重复刷新
- `invalid_grant`（refresh token 被撤销）→ 凭据文件被清除，提示用户重新登录

**推理工作原理：**
- 流量发送至 `https://cloudcode-pa.googleapis.com/v1internal:generateContent`（或 `:streamGenerateContent?alt=sse` 用于流式），而不是付费的 `v1beta/openai` 端点
- 请求体包裹为 `{project, model, user_prompt_id, request}`
- OpenAI 格式的 `messages[]`、`tools[]`、`tool_choice` 被转换为 Gemini 原生格式的 `contents[]`、`tools[].functionDeclarations`、`toolConfig`
- 响应被转换回 OpenAI 格式，这样 Hermes 的其他部分无需改动即可正常工作
**层级与项目 ID：**

| 你的情况 | 操作 |
|---|---|
| 个人 Google 账号，希望使用免费套餐 | 无需操作 — 登录即可开始聊天 |
| Workspace / Standard / Enterprise 账号 | 将 `HERMES_GEMINI_PROJECT_ID` 或 `GOOGLE_CLOUD_PROJECT` 设置为你的 GCP 项目 ID |
| 启用了 VPC-SC 保护的组织 | Hermes 检测到 `SECURITY_POLICY_VIOLATED` 并自动强制使用 `standard-tier` |

免费套餐会在首次使用时自动预配一个 Google 托管项目。无需进行 GCP 设置。

**配额监控：**

```
/gquota
```

显示每个模型剩余的 Code Assist 配额，并附带进度条：

```
Gemini Code Assist quota  (project: 123-abc)

  gemini-2.5-pro                      ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░   85%
  gemini-2.5-flash [input]            ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░   92%
```

<a id="policy-risk"></a>
:::warning 策略风险
Google 认为将 Gemini CLI OAuth 客户端与第三方软件配合使用属于违反策略的行为。部分用户已反馈账号受限。为了获得最低风险的使用体验，建议改用 `gemini` 提供商，通过你自己的 API 密钥进行操作。在进行 OAuth 之前，Hermes 会展示明确警告并要求用户确认。
:::
**自定义 OAuth 客户端（可选）：**

如果你更希望注册自己的 Google OAuth 客户端——例如，将配额和授权范围限制在你自己的 GCP 项目内——请设置：

```bash
HERMES_GEMINI_CLIENT_ID=your-client.apps.googleusercontent.com
HERMES_GEMINI_CLIENT_SECRET=...   # 桌面客户端可选
```

在 [console.cloud.google.com/apis/credentials](https://console.cloud.google.com/apis/credentials) 注册一个 **桌面应用** OAuth 客户端，并确保启用了 Generative Language API。

<a id="codex-note"></a>
:::info Codex 说明
OpenAI Codex 提供商通过设备码进行认证（打开 URL，输入代码）。Hermes 将生成的凭据存储在其自己的认证存储中（`~/.hermes/auth.json`），并且在存在时可以从 `~/.codex/auth.json` 导入现有的 Codex CLI 凭据。无需安装 Codex CLI。

如果令牌刷新失败并出现致命错误（HTTP 4xx、`invalid_grant`、授权被撤销等），Hermes 会将该刷新令牌标记为失效并停止重放，这样你就不会看到一连串相同的认证失败信息。后续请求会返回一条带类型的重新认证消息。运行 `hermes auth add codex-oauth`（或 `hermes model` → OpenAI Codex）以开始一次全新的设备码登录；下次成功交换后，隔离状态会自动解除。
:::
:::warning
即便在使用 Nous Portal、Codex 或自定义端点时，某些工具（视觉、网页摘要、MoA）也会使用独立的“辅助”模型。默认情况下（`auxiliary.*.provider: "auto"`），Hermes 会将这些任务路由到你的**主聊天模型**——也就是你在 `hermes model` 中选择的同一个模型。你可以单独覆盖每个任务，将其路由到更便宜/更快的模型（例如 OpenRouter 上的 Gemini Flash）——详见[辅助模型](/user-guide/configuration#auxiliary-models)。
:::

:::tip Nous 工具网关
<a id="nous-tool-gateway"></a>
付费的 Nous Portal 订阅用户还可以使用 **[工具网关](/user-guide/features/tool-gateway)**——通过你的订阅即可使用网页搜索、图像生成、TTS 和浏览器自动化，无需额外的 API 密钥。在 `hermes model` 设置过程中会自动提供，也可以稍后通过 `hermes tools` 启用。
:::

<a id="two-commands-for-model-management"></a>
### 两个模型管理命令

Hermes 提供**两个**用途不同的模型命令：

| 命令 | 运行位置 | 作用 |
|---------|-------------|--------------|
| **`hermes model`** | 你的终端（在任何会话之外） | 完整设置向导——添加供应商、运行 OAuth、输入 API 密钥、配置端点 |
| **`/model`** | 在 Hermes 聊天会话内部 | 在**已配置好**的供应商和模型之间快速切换 |
如果你尝试切换到一个尚未配置过的提供商（例如，你只配置了 OpenRouter 但想用 Anthropic），你需要使用 `hermes model`，而不是 `/model`。先退出当前会话（`Ctrl+C` 或 `/quit`），运行 `hermes model`，完成提供商设置，然后启动一个新会话。

<a id="nous-portal"></a>
### Nous Portal

通过 Nous Research 的门户提供基于订阅的 Hermes-4 模型访问（`Hermes-4-70B`、`Hermes-4.3-36B`、`Hermes-4-405B`）。运行 `hermes model`，选择 **Nous Portal**，通过浏览器登录——Hermes 会将一个长期有效的刷新令牌存储在 `~/.hermes/auth.json` 中。

该刷新令牌也会通过共享令牌存储在所有配置文件之间共享，因此在一个配置文件中登录后，其他配置文件也会同步生效。

<a id="token-handling"></a>
#### 令牌处理

Hermes 在每次推理调用时，会根据你存储的 Nous 刷新令牌生成一个短期有效的 JWT，而不是重复使用长期有效的 API 密钥。令牌的生命周期完全自动处理——刷新、生成、在遇到临时 401 时重试——你完全看不到这个过程。

如果门户使刷新令牌失效（密码更改、手动撤销、会话过期），则该无效刷新令牌会被本地隔离，这样 Hermes 就不会再重复使用它，你也不会看到一连串相同的 401 错误。下一次调用时会明确提示“需要重新认证”。运行 `hermes auth add nous` 重新登录；下一次成功登录后，隔离会自动解除。
<a id="anthropic-native"></a>
### Anthropic（原生）

直接通过 Anthropic API 使用 Claude 模型——无需 OpenRouter 代理。支持三种认证方式：

<a id="requires-claude-max-extra-usage-credits"></a>
:::caution 需要 Claude Max "额外使用" 积分
通过 `hermes model` → Anthropic OAuth（或 `hermes auth add anthropic --type oauth`）进行认证时，Hermes 会以 Claude Code 的身份路由到您的 Anthropic 账户。**这仅在您订阅了 Claude Max 套餐并且购买了额外使用积分的情况下才能生效。** 基础 Max 套餐配额（Claude Code 默认包含的使用量）不会被 Hermes 消耗——仅消耗您额外添加的透支积分。Claude Pro 订阅者无法使用此路径。

如果您没有 Max + 额外积分，请改用 `ANTHROPIC_API_KEY`——请求将按 token 计费，从该密钥所属的组织账户扣除（标准 API 定价，与任何 Claude 订阅无关）。
:::

```bash
# 使用 API 密钥（按 token 计费）
export ANTHROPIC_API_KEY=***
hermes chat --provider anthropic --model claude-sonnet-4-6

# 推荐：通过 `hermes model` 认证
# Hermes 会在可用时直接使用 Claude Code 的凭据存储
hermes model

# 使用 setup-token 手动覆盖（备用/旧式方式）
export ANTHROPIC_TOKEN=***  # setup-token 或手动 OAuth 令牌
hermes chat --provider anthropic

# 自动检测 Claude Code 凭据（如果您已经使用 Claude Code）
hermes chat --provider anthropic  # 自动读取 Claude Code 凭据文件
```
当你通过 `hermes model` 选择 Anthropic OAuth 时，Hermes 会优先使用 Claude Code 自身的凭据存储，而不是将令牌复制到 `~/.hermes/.env` 中。这样可以让可刷新的 Claude 凭据保持可刷新。

或者永久设置：
```yaml
model:
  provider: "anthropic"
  default: "claude-sonnet-4-6"
```

:::tip 别名
<a id="aliases"></a>
`--provider claude` 和 `--provider claude-code` 也可作为 `--provider anthropic` 的简写。
:::

<a id="github-copilot"></a>
### GitHub Copilot

Hermes 将 GitHub Copilot 作为一等提供商支持，并提供两种模式：

**`copilot` — 直接 Copilot API**（推荐）。使用你的 GitHub Copilot 订阅，通过 Copilot API 访问 GPT-5.x、Claude、Gemini 等模型。

```bash
hermes chat --provider copilot --model gpt-5.4
```

**身份验证选项**（按此顺序检查）：

1. `COPILOT_GITHUB_TOKEN` 环境变量
2. `GH_TOKEN` 环境变量
3. `GITHUB_TOKEN` 环境变量
4. `gh auth token` CLI 回退

如果未找到令牌，`hermes model` 会提供 **OAuth 设备码登录**——与 Copilot CLI 和 opencode 使用的流程相同。
<a id="token-types"></a>
:::warning Token 类型
Copilot API **不**支持经典的个人访问令牌（`ghp_*`）。支持的令牌类型：

| 类型 | 前缀 | 获取方式 |
|------|--------|------------|
| OAuth 令牌 | `gho_` | `hermes model` → GitHub Copilot → 使用 GitHub 登录 |
| 细粒度 PAT | `github_pat_` | GitHub 设置 → 开发者设置 → 细粒度令牌（需要 **Copilot 请求** 权限） |
| GitHub App 令牌 | `ghu_` | 通过 GitHub App 安装 |

如果你的 `gh auth token` 返回的是 `ghp_*` 令牌，请改用 `hermes model` 通过 OAuth 进行身份验证。

:::

<a id="copilot-auth-behavior-in-hermes"></a>
:::info Hermes 中的 Copilot 认证行为
Hermes 会将受支持的 GitHub 令牌（`gho_*`、`github_pat_*` 或 `ghu_*`）直接发送到 `api.githubcopilot.com`，并包含 Copilot 特定的请求头（`Editor-Version`、`Copilot-Integration-Id`、`Openai-Intent`、`x-initiator`）。

当收到 HTTP 401 响应时，Hermes 会在回退前执行一次性的凭据恢复：

1. 通过常规优先级链重新解析令牌（`COPILOT_GITHUB_TOKEN` → `GH_TOKEN` → `GITHUB_TOKEN` → `gh auth token`）
2. 使用刷新后的请求头重新构建共享的 OpenAI 客户端
3. 重试该请求一次

:::
一些较旧的社区代理使用 `api.github.com/copilot_internal/v2/token` 交换流程。该端点可能对某些账户类型不可用（返回 404）。因此，Hermes 将直接令牌认证作为主要路径，并依赖运行时凭据刷新和重试来保证健壮性。
:::

**API 路由**：GPT-5+ 模型（`gpt-5-mini` 除外）自动使用 Responses API。所有其他模型（GPT-4o、Claude、Gemini 等）使用 Chat Completions。模型会从实时 Copilot 目录中自动检测。

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
<a id="first-class-api-key-providers"></a>
### 一级 API 密钥提供商

这些提供商拥有内置支持，并带有专用提供商 ID。设置 API 密钥后，使用 `--provider` 进行选择：

```bash
# NovitaAI 模型 API
hermes chat --provider novita --model moonshotai/kimi-k2.5
# 需要：在 ~/.hermes/.env 中设置 NOVITA_API_KEY

# z.ai / 智谱 GLM
hermes chat --provider zai --model glm-5
# 需要：在 ~/.hermes/.env 中设置 GLM_API_KEY

# Kimi / Moonshot AI（国际：api.moonshot.ai）
hermes chat --provider kimi-coding --model kimi-for-coding
# 需要：在 ~/.hermes/.env 中设置 KIMI_API_KEY

# Kimi / Moonshot AI（中国：api.moonshot.cn）
hermes chat --provider kimi-coding-cn --model kimi-k2.5
# 需要：在 ~/.hermes/.env 中设置 KIMI_CN_API_KEY

# MiniMax（全球端点）
hermes chat --provider minimax --model MiniMax-M2.7
# 需要：在 ~/.hermes/.env 中设置 MINIMAX_API_KEY

# MiniMax（中国端点）
hermes chat --provider minimax-cn --model MiniMax-M2.7
# 需要：在 ~/.hermes/.env 中设置 MINIMAX_CN_API_KEY

# 通义千问 / DashScope（Qwen 模型）
hermes chat --provider alibaba --model qwen3.5-plus
# 需要：在 ~/.hermes/.env 中设置 DASHSCOPE_API_KEY

# 小米 MiMo
hermes chat --provider xiaomi --model mimo-v2-pro
# 需要：在 ~/.hermes/.env 中设置 XIAOMI_API_KEY

# 腾讯 TokenHub（Hy3 Preview）
hermes chat --provider tencent-tokenhub --model hy3-preview
# 需要：在 ~/.hermes/.env 中设置 TOKENHUB_API_KEY

# Arcee AI（Trinity 模型）
hermes chat --provider arcee --model trinity-large-thinking
# 需要：在 ~/.hermes/.env 中设置 ARCEEAI_API_KEY

# GMI Cloud
# 使用 GMI 的 /v1/models 端点返回的精确模型 ID。
hermes chat --provider gmi --model zai-org/GLM-5.1-FP8
# 需要：在 ~/.hermes/.env 中设置 GMI_API_KEY
```
或者在 `config.yaml` 中永久设置 provider：
```yaml
model:
  provider: "gmi"
  default: "zai-org/GLM-5.1-FP8"
```

可以通过 `NOVITA_BASE_URL`、`GLM_BASE_URL`、`KIMI_BASE_URL`、`MINIMAX_BASE_URL`、`MINIMAX_CN_BASE_URL`、`DASHSCOPE_BASE_URL`、`XIAOMI_BASE_URL`、`GMI_BASE_URL` 或 `TOKENHUB_BASE_URL` 环境变量来覆盖基础 URL。

:::note Z.AI 端点自动检测
<a id="z-ai-endpoint-auto-detection"></a>
当使用 Z.AI / GLM provider 时，Hermes 会自动探测多个端点（全局、中国、编码变体）以找到一个能接受你的 API 密钥的端点。你无需手动设置 `GLM_BASE_URL` —— 可用的端点会被自动检测并缓存。
:::

<a id="xai-grok-responses-api-prompt-caching"></a>
### xAI (Grok) — Responses API + 提示缓存

xAI 通过 Responses API（`codex_responses` 传输方式）连接，以在 Grok 4 模型上实现自动推理支持——无需 `reasoning_effort` 参数，默认情况下服务器会进行推理。在 `~/.hermes/.env` 中设置 `XAI_API_KEY`，然后在 `hermes model` 中选择 xAI，或者直接使用快捷方式 `/model grok-4-1-fast-reasoning`。
SuperGrok 和 X Premium+ 订阅用户可以通过浏览器 OAuth 登录，而无需使用 API 密钥——在 `hermes model` 中选择 **xAI Grok OAuth (SuperGrok Subscription)**，或运行 `hermes auth add xai-oauth`。同一个 OAuth 不记名令牌会被直接连接到 xAI 的工具（TTS、图像生成、视频生成、转录）自动复用。完整流程请参阅 [xAI Grok OAuth 指南](../guides/xai-grok-oauth.md)——如果在远程主机上运行 Hermes，还需查看 [通过 SSH / 远程主机使用 OAuth](../guides/oauth-over-ssh.md) 了解所需的 `ssh -L` 隧道。

当使用 xAI 作为提供商（任何包含 `x.ai` 的基础 URL）时，Hermes 会自动启用提示缓存，方法是在每次 API 请求中发送 `x-grok-conv-id` 标头。这将对话会话中的请求路由到同一台服务器，使 xAI 的基础设施能够重复使用缓存的系统提示和对话历史记录。

无需任何配置——当检测到 xAI 端点且会话 ID 可用时，缓存会自动激活。这降低了多轮对话的延迟和成本。
xAI 还提供了一个专用的 TTS 端点（`/v1/tts`）。在 `hermes tools` → Voice & TTS 中选择 **xAI TTS**，或查看 [Voice & TTS](../user-guide/features/tts.md#text-to-speech) 页面了解配置。

<a id="novitaai"></a>
### NovitaAI

[NovitaAI](https://novita.ai) 是一个面向构建者和 Agent 的 AI 原生云平台。它的三条产品线分别是：提供 200+ 个模型的 Model API、用于构建和运行 AI Agent 的 Agent Sandbox，以及可伸缩计算的 GPU Cloud——所有这些都可以在一个平台上获得。

```bash
# 使用任何可用的模型
hermes chat --provider novita --model moonshotai/kimi-k2.5
# 需要：在 ~/.hermes/.env 中设置 NOVITA_API_KEY

# 短别名
hermes chat --provider novita-ai --model deepseek/deepseek-v3-0324
```

或者在 `config.yaml` 中永久设置：
```yaml
model:
  provider: "novita"
  default: "moonshotai/kimi-k2.5"
  base_url: "https://api.novita.ai/openai/v1"
```

前往 [novita.ai/settings/key-management](https://novita.ai/settings/key-management) 获取你的 API 密钥。可以通过 `NOVITA_BASE_URL` 覆盖基础 URL。
<a id="ollama-cloud-managed-ollama-models-oauth-api-key"></a>
### Ollama Cloud — 托管版 Ollama 模型，支持 OAuth + API Key

[Ollama Cloud](https://ollama.com/cloud) 托管了与本地 Ollama 相同的开源模型目录，但无需 GPU。在 `hermes model` 中选择 **Ollama Cloud**，粘贴从 [ollama.com/settings/keys](https://ollama.com/settings/keys) 获取的 API key，Hermes 会自动发现可用模型。

```bash
hermes model
# → 选择 "Ollama Cloud"
# → 粘贴你的 OLLAMA_API_KEY
# → 从发现的模型中选择（gpt-oss:120b、glm-4.6:cloud、qwen3-coder:480b-cloud 等）
```

或者直接使用 `config.yaml`：
```yaml
model:
  provider: "ollama-cloud"
  default: "gpt-oss:120b"
```

模型目录会从 `ollama.com/v1/models` 动态获取并缓存一小时。`model:tag` 格式（例如 `qwen3-coder:480b-cloud`）会通过标准化保留——请勿使用短横线。

<a id="ollama-cloud-vs-local-ollama"></a>
:::tip Ollama Cloud 与本地 Ollama 的区别
两者都使用相同的 OpenAI 兼容 API。Cloud 是一等提供商（`--provider ollama-cloud`、`OLLAMA_API_KEY`）；本地 Ollama 通过自定义端点流程访问（基础 URL `http://localhost:11434/v1`，无需 key）。对于本地无法运行的大模型，请使用 Cloud；需要隐私或离线工作时，请使用本地版本。
:::
<a id="aws-bedrock"></a>
### AWS Bedrock

通过 AWS Bedrock 使用 Anthropic Claude、Amazon Nova、DeepSeek v3.2、Meta Llama 4 等模型。采用 AWS SDK（`boto3`）凭证链——无需 API 密钥，只需标准 AWS 认证。

```bash
# 最简单的方式——使用 ~/.aws/credentials 中的命名配置文件
hermes chat --provider bedrock --model us.anthropic.claude-sonnet-4-6

# 或通过显式环境变量
AWS_PROFILE=myprofile AWS_REGION=us-east-1 hermes chat --provider bedrock --model us.anthropic.claude-sonnet-4-6
```

也可以永久保存在 `config.yaml` 中：
```yaml
model:
  provider: "bedrock"
  default: "us.anthropic.claude-sonnet-4-6"
bedrock:
  region: "us-east-1"          # 或设置 AWS_REGION
  # profile: "myprofile"       # 或设置 AWS_PROFILE
  # discovery: true            # 从 IAM 自动发现区域
  # guardrail:                 # 可选的 Bedrock Guardrails
  #   guardrail_identifier: "your-guardrail-id"
  #   guardrail_version: "DRAFT"
```

认证使用标准的 boto3 链：显式设置 `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY`、来自 `~/.aws/credentials` 的 `AWS_PROFILE`、EC2/ECS/Lambda 上的 IAM 角色、IMDS 或 SSO。如果你已经通过 AWS CLI 完成认证，则无需设置任何环境变量。
Bedrock 底层使用 **Converse API**——请求会被转换为 Bedrock 不依赖具体模型的形式，因此同一配置可用于 Claude、Nova、DeepSeek 和 Llama 模型。仅当调用非默认区域端点时，才需要设置 `BEDROCK_BASE_URL`。

参见 [AWS Bedrock 指南](/guides/aws-bedrock)，了解 IAM 设置、区域选择和跨区域推理的详细说明。

<a id="qwen-portal-oauth"></a>
### Qwen Portal (OAuth)

阿里巴巴的 Qwen Portal 支持基于浏览器的 OAuth 登录。在 `hermes model` 中选择 **Qwen OAuth (Portal)**，通过浏览器登录，Hermes 会持久化保存刷新令牌。

```bash
hermes model
# → pick "Qwen OAuth (Portal)"
# → browser opens; sign in with your Alibaba account
# → confirm — credentials are saved to ~/.hermes/auth.json

hermes chat   # uses portal.qwen.ai/v1 endpoint
```

或者配置 `config.yaml`：
```yaml
model:
  provider: "qwen-oauth"
  default: "qwen3-coder-plus"
```

仅当门户端点变更时，才需要设置 `HERMES_QWEN_BASE_URL`（默认：`https://portal.qwen.ai/v1`）。
:::tip Qwen OAuth 与 Qwen Cloud（阿里云 DashScope）的区别
<a id="qwen-oauth-vs-qwen-cloud-alibaba-dashscope"></a>
`qwen-oauth` 使用面向消费者的 Qwen 门户，通过 OAuth 登录——适合个人用户。`alibaba` 提供方使用 Qwen Cloud（阿里云 DashScope），需要 `DASHSCOPE_API_KEY`——适合程序化/生产环境工作负载。两者都路由到 Qwen 系列模型，但端点不同。
:::

<a id="alibaba-cloud-coding-plan"></a>
### 阿里云（Coding Plan）

如果你订阅了阿里云的 **Coding Plan**（一个独立于标准 DashScope API 访问的定价 SKU），Hermes 会将其作为一等提供方暴露出来：`alibaba-coding-plan`。端点：`https://coding-intl.dashscope.aliyuncs.com/v1`。它与常规的 `alibaba` 提供方一样兼容 OpenAI，但使用不同的基础 URL 和计费方式。

```yaml
model:
  provider: alibaba_coding     # alibaba-coding-plan 的别名
  model: qwen3-coder-plus
```

或者通过 CLI 使用：

```bash
hermes chat --provider alibaba_coding --model qwen3-coder-plus
```

`alibaba_coding` 使用与 `alibaba` 条目相同的 `DASHSCOPE_API_KEY`——无需单独密钥，只是路由目标不同。在此提供方注册之前，在 `config.yaml` 中设置 `provider: alibaba_coding` 的用户会静默地回退到 OpenRouter 路由。
<a id="minimax-oauth"></a>
### MiniMax（OAuth）

通过浏览器 OAuth 登录使用 MiniMax-M2.7 — 无需 API 密钥。在 `hermes model` 中选 **MiniMax (OAuth)**，通过浏览器登录，Hermes 会持久保存访问令牌和刷新令牌。底层使用兼容 Anthropic Messages 的端点（`/anthropic`）。

```bash
hermes model
# → 选择 "MiniMax (OAuth)"
# → 浏览器打开；使用你的 MiniMax 账号登录（全球或中国区）
# → 确认 — 凭据会保存到 ~/.hermes/auth.json

hermes chat   # 使用 api.minimax.io/anthropic 端点
```

或配置 `config.yaml`：
```yaml
model:
  provider: "minimax-oauth"
  default: "MiniMax-M2.7"
```

支持的模型：`MiniMax-M2.7`（主模型）和 `MiniMax-M2.7-highspeed`（默认辅助模型）。OAuth 方式会忽略 `MINIMAX_API_KEY` / `MINIMAX_BASE_URL`。

<a id="minimax-oauth-vs-api-key"></a>
:::tip MiniMax OAuth vs API 密钥
`minimax-oauth` 使用 MiniMax 面向消费者的门户，通过 OAuth 登录，无需设置结算。而 `minimax` 和 `minimax-cn` 提供程序使用 `MINIMAX_API_KEY` / `MINIMAX_CN_API_KEY` — 用于编程访问。完整步骤请参考 [MiniMax OAuth 指南](/guides/minimax-oauth)。
:::
<a id="nvidia-nim"></a>
### NVIDIA NIM

Nemotron 及其他开源模型可通过 [build.nvidia.com](https://build.nvidia.com)（免费 API 密钥）或本地 NIM 端点使用。

```bash
# 云端（build.nvidia.com）
hermes chat --provider nvidia --model nvidia/nemotron-3-super-120b-a12b
# 需要：在 ~/.hermes/.env 中设置 NVIDIA_API_KEY

# 本地 NIM 端点 — 覆盖 base URL
NVIDIA_BASE_URL=http://localhost:8000/v1 hermes chat --provider nvidia --model nvidia/nemotron-3-super-120b-a12b
```

或者在 `config.yaml` 中永久设置：
```yaml
model:
  provider: "nvidia"
  default: "nvidia/nemotron-3-super-120b-a12b"
```

<a id="local-nim"></a>
:::tip 本地 NIM
对于本地部署（DGX Spark、本地 GPU），设置 `NVIDIA_BASE_URL=http://localhost:8000/v1`。NIM 暴露与 build.nvidia.com 相同的 OpenAI 兼容聊天补全 API，因此云端与本地切换只需更改一行环境变量。
:::

Hermes 会自动在每个发往 `build.nvidia.com` 的请求中添加 NIM 计费来源头信息 — 无需配置。这将确保在 NVIDIA 计费仪表板中按正确的来源记录消耗。
<a id="gmi-cloud"></a>
### GMI Cloud

通过 [GMI Cloud](https://www.gmicloud.ai/) 使用开放和推理模型 — 兼容 OpenAI 的 API，使用 API 密钥认证。

```bash
# GMI Cloud
hermes chat --provider gmi --model deepseek-ai/DeepSeek-R1
# 需要：在 ~/.hermes/.env 中设置 GMI_API_KEY
```

或者在 `config.yaml` 中永久设置：
```yaml
model:
  provider: "gmi"
  default: "deepseek-ai/DeepSeek-R1"
```

可以通过 `GMI_BASE_URL` 覆盖基础 URL（默认值：`https://api.gmi-serving.com/v1`）。

<a id="stepfun"></a>
### StepFun

通过 [StepFun](https://platform.stepfun.com) 使用 Step 系列模型 — 兼容 OpenAI 的 API，使用 API 密钥认证。

```bash
# StepFun
hermes chat --provider stepfun --model step-3-mini
# 需要：在 ~/.hermes/.env 中设置 STEPFUN_API_KEY
```

或者在 `config.yaml` 中永久设置：
```yaml
model:
  provider: "stepfun"
  default: "step-3-mini"
```

可以通过 `STEPFUN_BASE_URL` 覆盖基础 URL（默认值：`https://api.stepfun.com/v1`）。

<a id="hugging-face-inference-providers"></a>
### Hugging Face Inference Providers

[Hugging Face Inference Providers](https://huggingface.co/docs/inference-providers) 通过统一的 OpenAI 兼容端点（`router.huggingface.co/v1`）路由到 20 多个开放模型。请求会自动路由到最快的可用后端（Groq、Together、SambaNova 等），并具备自动故障转移功能。
```bash
# 使用任意可用模型
hermes chat --provider huggingface --model Qwen/Qwen3-235B-A22B-Thinking-2507
# 需要：在 ~/.hermes/.env 中设置 HF_TOKEN

# 短别名
hermes chat --provider hf --model deepseek-ai/DeepSeek-V3.2
```

或者在 `config.yaml` 中永久设置：
```yaml
model:
  provider: "huggingface"
  default: "Qwen/Qwen3-235B-A22B-Thinking-2507"
```

在 [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) 获取你的令牌——确保启用“允许调用推理提供商”权限。包含免费套餐（每月 $0.10 额度，提供商费率无加价）。

你可以向模型名称追加路由后缀：`:fastest`（默认）、`:cheapest` 或 `:provider_name` 以强制指定特定后端。

基础 URL 可通过 `HF_BASE_URL` 覆盖。

<a id="custom-self-hosted-llm-providers"></a>
## 自定义与自托管 LLM 提供商

Hermes Agent 可与**任何兼容 OpenAI 的 API 端点**配合使用。如果某个服务器实现了 `/v1/chat/completions`，你就可以将 Hermes 指向它。这意味着你可以使用本地模型、GPU 推理服务器、多提供商路由器或任何第三方 API。
<a id="general-setup"></a>
### 通用设置

有三种方式配置自定义端点：

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

:::warning 传统环境变量
<a id="legacy-env-vars"></a>
`.env` 中的 `OPENAI_BASE_URL` 和 `LLM_MODEL` **已移除**。Hermes 的任何部分都不会读取它们——`config.yaml` 是模型和端点配置的唯一真实来源。如果你的 `.env` 中有过期条目，下次运行 `hermes setup` 或配置迁移时会自动清除。请使用 `hermes model` 或直接编辑 `config.yaml`。
:::

两种方式都会持久化到 `config.yaml`，这是模型、提供者和基础 URL 的真实来源。

<a id="switching-models-with-model"></a>
### 使用 `/model` 切换模型

<a id="hermes-model-vs-model"></a>
:::warning hermes model 与 /model 的区别
**`hermes model`**（在终端中运行，不进入聊天会话）是**完整的提供者设置向导**。使用它可以添加新的提供者、运行 OAuth 流程、输入 API 密钥以及配置自定义端点。
**`/model`**（在活动的 Hermes 会话中输入）只能**在你已设置的提供者和模型之间切换**。它不能添加新的提供者、运行 OAuth 或提示输入 API 密钥。如果你只配置了一个提供者（例如 OpenRouter），`/model` 只会显示该提供者的模型。

**添加新提供者：**退出当前会话（`Ctrl+C` 或 `/quit`），运行 `hermes model`，设置好新的提供者，然后启动一个新会话。
:::

一旦你至少配置了一个自定义端点，就可以在会话中途切换模型：

```
/model custom:qwen-2.5          # 切换到自定义端点上的模型
/model custom                    # 自动检测端点上的模型
/model openrouter:claude-sonnet-4 # 切换回云提供者
```

如果你配置了**命名自定义提供者**（见下文），使用三重语法：

```
/model custom:local:qwen-2.5    # 使用名为 "local" 的自定义提供者和模型 qwen-2.5
/model custom:work:llama3       # 使用名为 "work" 的自定义提供者和 llama3
```
当切换提供商时，Hermes 会将基 URL 和提供商持久化到配置中，以便更改在重启后仍然有效。当从自定义端点切换到内置提供商时，旧的基 URL 会自动清除。

:::tip
`/model custom`（裸命令，不带模型名称）会查询你端点的 `/models` API，如果恰好加载了一个模型，则自动选择该模型。适用于本地运行单个模型的服务器。
:::

下面的所有内容都遵循相同的模式——只需更改 URL、密钥和模型名称即可。

---

<a id="ollama-local-models-zero-config"></a>
### Ollama — 本地模型，零配置

[Ollama](https://ollama.com/) 可一条命令在本地运行开放权重模型。最适合：快速本地实验、隐私敏感型工作、离线使用。通过兼容 OpenAI 的 API 支持工具调用。

```bash
# 安装并运行一个模型
ollama pull qwen2.5-coder:32b
ollama serve   # 在 11434 端口启动
```

然后配置 Hermes：

```bash
hermes model
# 选择 "Custom endpoint (self-hosted / VLLM / etc.)"
# 输入 URL：http://localhost:11434/v1
# 跳过 API 密钥（Ollama 不需要）
# 输入模型名称（例如 qwen2.5-coder:32b）
```
或者直接配置 `config.yaml`：

```yaml
model:
  default: qwen2.5-coder:32b
  provider: custom
  base_url: http://localhost:11434/v1
  context_length: 32768   # 参见下方警告
```

<a id="ollama-defaults-to-very-low-context-lengths"></a>
:::caution Ollama 默认使用极低的上下文长度
Ollama **默认不会**使用模型完整的上下文窗口。根据你的 VRAM，默认值如下：

| 可用 VRAM | 默认上下文 |
|-----------|------------|
| 小于 24 GB | **4,096 tokens** |
| 24–48 GB | 32,768 tokens |
| 48+ GB | 256,000 tokens |

对于使用工具的 Agent，**你至少需要 16k–32k 的上下文**。在 4k 下，仅系统提示词和工具架构就会填满窗口，导致对话没有空间。

**如何增加上下文长度**（任选其一）：

```bash
# 选项 1：通过环境变量设置服务器范围（推荐）
OLLAMA_CONTEXT_LENGTH=32768 ollama serve

# 选项 2：对于 systemd 管理的 Ollama
sudo systemctl edit ollama.service
# 添加：Environment="OLLAMA_CONTEXT_LENGTH=32768"
# 然后：sudo systemctl daemon-reload && sudo systemctl restart ollama

# 选项 3：将配置嵌入自定义模型（每个模型持久化）
echo -e "FROM qwen2.5-coder:32b\nPARAMETER num_ctx 32768" > Modelfile
ollama create qwen2.5-coder-32k -f Modelfile
```
**你不能通过 OpenAI 兼容的 API（`/v1/chat/completions`）设置上下文长度。** 必须在服务端或通过 Modelfile 配置。这是在使用 Ollama 与 Hermes 等工具集成时最容易混淆的地方。

:::

**确认你的上下文已正确设置：**

```bash
ollama ps
# 查看 CONTEXT 列——它应显示你配置的值
```

:::tip
使用 `ollama list` 列出可用模型。使用 `ollama pull &lt;model&gt;` 从 [Ollama 库](https://ollama.com/library) 拉取任何模型。Ollama 会自动处理 GPU 卸载 —— 大多数情况下无需配置。
:::

---

<a id="vllm-high-performance-gpu-inference"></a>
### vLLM —— 高性能 GPU 推理

[vLLM](https://docs.vllm.ai/) 是生产环境 LLM 服务的标准。最佳适用场景：在 GPU 硬件上获得最大吞吐量、服务大型模型、连续批处理。

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
# 跳过 API key（如果你用 --api-key 配置了 vLLM，则输入 key）
# 输入模型名称: meta-llama/Llama-3.1-70B-Instruct
```

**上下文长度：** vLLM 默认读取模型的 `max_position_embeddings`。如果该值超出了你的 GPU 显存，它会报错并要求你调低 `--max-model-len`。你也可以使用 `--max-model-len auto` 来自动找到可容纳的最大长度。设置 `--gpu-memory-utilization 0.95`（默认 0.9）可以在 VRAM 中挤出更多上下文空间。

**工具调用需要显式标记：**

| 标记 | 用途 |
|------|------|
| `--enable-auto-tool-choice` | `tool_choice: "auto"` 所必需的（Hermes 中的默认值） |
| `--tool-call-parser <名称>` | 模型工具调用格式的解析器 |

支持的解析器：`hermes`（Qwen 2.5，Hermes 2/3）、`llama3_json`（Llama 3.x）、`mistral`、`deepseek_v3`、`deepseek_v31`、`xlam`、`pythonic`。如果没有这些标记，工具调用将无法工作——模型会以文本形式输出工具调用。
:::tip
vLLM 支持人类可读的大小格式：`--max-model-len 64k`（小写 k = 1000，大写 K = 1024）。
:::

---

<a id="sglang-fast-serving-with-radixattention"></a>
### SGLang — 基于 RadixAttention 的快速推理

[SGLang](https://github.com/sgl-project/sglang) 是 vLLM 的替代方案，利用 RadixAttention 实现 KV 缓存复用。最适合：多轮对话（前缀缓存）、约束解码、结构化输出。

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
# 选择 "Custom endpoint (self-hosted / VLLM / etc.)"
# 输入 URL：http://localhost:30000/v1
# 输入模型名称：meta-llama/Llama-3.1-70B-Instruct
```

**上下文长度：** SGLang 默认从模型配置中读取。使用 `--context-length` 可覆盖默认值。如果需要超过模型声明的最大长度，请设置 `SGLANG_ALLOW_OVERWRITE_LONGER_CONTEXT_LEN=1`。

**工具调用：** 使用 `--tool-call-parser` 并指定与模型系列匹配的解析器：`qwen`（Qwen 2.5）、`llama3`、`llama4`、`deepseekv3`、`mistral`、`glm`。如果不加此标志，工具调用将以纯文本形式返回。
:::caution SGLang 默认最大输出 token 数为 128
<a id="sglang-defaults-to-128-max-output-tokens"></a>
如果响应看起来被截断了，请在请求中添加 `max_tokens`，或在服务器上设置 `--default-max-tokens`。如果请求中未指定，SGLang 每个响应默认只输出 128 个 token。
:::

---

<a id="llama-cpp-llama-server-cpu-metal-inference"></a>
### llama.cpp / llama-server — CPU 与 Metal 推理

[llama.cpp](https://github.com/ggml-org/llama.cpp) 可在 CPU、Apple Silicon (Metal) 和消费级 GPU 上运行量化模型。适用场景：在没有数据中心 GPU 的情况下运行模型、Mac 用户、边缘部署。

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

**上下文长度（`-c`）：** 最近的构建版本默认值为 `0`，会从 GGUF 元数据中读取模型的训练上下文长度。对于具有 128k+ 训练上下文的模型，尝试分配完整的 KV 缓存可能导致内存不足（OOM）。请显式设置 `-c` 为你需要的值（Agent 使用场景下 32k–64k 是一个不错的范围）。如果使用并行槽位（`-np`），总上下文会被平均分配到各个槽位——搭配 `-c 32768 -np 4` 时，每个槽位只有 8k。
然后配置 Hermes 指向该端点：

```bash
hermes model
# 选择 "Custom endpoint (self-hosted / VLLM / etc.)"
# 输入 URL: http://localhost:8080/v1
# 跳过 API 密钥（本地服务器不需要）
# 输入模型名称——如果只加载了一个模型，留空可自动检测
```

这会将该端点保存到 `config.yaml` 中，使其在会话间持久化。

<a id="jinja-is-required-for-tool-calling"></a>
:::caution 工具调用需要 `--jinja` 参数
如果不加 `--jinja`，llama-server 会完全忽略 `tools` 参数。模型会尝试通过在响应文本中写入 JSON 来调用工具，但 Hermes 不会将其识别为工具调用——你会看到类似 `{"name": "web_search", ...}` 的原始 JSON 作为消息输出，而不是实际执行搜索。

原生工具调用支持（性能最佳）：Llama 3.x、Qwen 2.5（包括 Coder）、Hermes 2/3、Mistral、DeepSeek、Functionary。其他所有模型使用通用处理器，虽然也能工作但效率可能较低。完整列表请参阅 [llama.cpp 函数调用文档](https://github.com/ggml-org/llama.cpp/blob/master/docs/function-calling.md)。
---
你可以通过访问 `http://localhost:8080/props` 来验证工具支持是否已启用——`chat_template` 字段应该会显示出来。

:::tip
从 [Hugging Face](https://huggingface.co/models?library=gguf) 下载 GGUF 模型。Q4_K_M 量化在质量与内存占用之间取得了最佳平衡。
:::

---

<a id="lm-studio-desktop-app-with-local-models"></a>
### LM Studio — 运行本地模型的桌面应用

[LM Studio](https://lmstudio.ai/) 是一款桌面应用，提供图形用户界面来运行本地模型。最适合：偏好可视化界面、想快速测试模型的用户，以及 macOS/Windows/Linux 开发者。

在 LM Studio 应用中启动服务器（开发者选项卡 → 启动服务器），或使用 CLI：

```bash
lms server start                        # 在 1234 端口启动
lms load qwen2.5-coder --context-length 32768
```

然后配置 Hermes：

```bash
hermes model
# 选择 "LM Studio"
# 按 Enter 使用 http://localhost:1234/v1
# 在已发现的模型中选一个
# 如果 LM Studio 服务器启用了身份验证，按提示输入 LM_API_KEY
```

Hermes 会自动加载一个具有 64K 上下文长度的 LM Studio 模型。
在 LM Studio 中更改上下文长度：

1. 点击模型选择器旁边的齿轮图标
2. 将“上下文长度”（Context Length）设置为至少 64000，以获得流畅体验
3. 重新加载模型以使更改生效
4. 如果您的机器无法容纳 64000，请考虑使用上下文长度更大的小型模型。

或者使用 CLI：`lms load model-name --context-length 64000`

您可以使用 CLI 估算模型能否适配：`lms load model-name --context-length 64000 --estimate-only`

要设置持久的模型级默认值：前往“我的模型”选项卡 → 点击模型上的齿轮图标 → 设置上下文大小。
:::

**工具调用（Tool calling）：** 自 LM Studio 0.3.6 起支持。原生支持工具调用训练的模型（Qwen 2.5、Llama 3.x、Mistral、Hermes）会被自动检测并显示工具徽章。其他模型使用通用回退方案，可靠性可能较低。

---

<a id="wsl2-networking-windows-users"></a>
### WSL2 网络（Windows 用户）

由于 Hermes Agent 需要 Unix 环境，Windows 用户需在 WSL2 中运行。如果您的模型服务器（Ollama、LM Studio 等）运行在 **Windows 主机** 上，则需要桥接网络缺口——WSL2 使用带有自身子网的虚拟网络适配器，因此 WSL2 内的 `localhost` 指向的是 Linux 虚拟机，**而不是** Windows 主机。
:::tip 两边都在 WSL2 里？没问题。
<a id="both-in-wsl2-no-problem"></a>
如果你的模型服务器也在 WSL2 内部运行（vLLM、SGLang 和 llama-server 常见这种情况），`localhost` 可以正常通信——因为它们共享同一网络命名空间。直接跳过本小节即可。
:::

<a id="option-1-mirrored-networking-mode-recommended"></a>
#### 方案一：镜像网络模式（推荐）

**Windows 11 22H2+** 提供镜像模式，能让 `localhost` 在 Windows 与 WSL2 之间双向互通——这是最简便的修复方法。

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
   curl http://localhost:11434/v1/models   # Ollama（Windows 端）—— 可以访问
   ```

<a id="hyper-v-firewall"></a>
:::note Hyper-V 防火墙
在某些 Windows 11 版本中，Hyper-V 防火墙默认会阻止镜像连接。如果启用镜像模式后 `localhost` 仍然无法使用，请在**管理员 PowerShell** 中运行以下命令：
```powershell
Set-NetFirewallHyperVVMSetting -Name '{40E0AC32-46A5-438A-A0B2-2B479E8F2E90}' -DefaultInboundAction Allow
```
:::
<a id="option-2-use-the-windows-host-ip-windows-10-older-builds"></a>
#### 选项 2：使用 Windows 主机 IP（Windows 10 / 老版本）

如果你无法使用镜像模式，可以从 WSL2 内部找到 Windows 主机 IP，并用它代替 `localhost`：

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

:::tip 动态获取助手
<a id="dynamic-helper"></a>
主机 IP 在 WSL2 重启后可能会变。你可以在 shell 中动态获取它：
```bash
export WSL_HOST=$(ip route show | grep -i default | awk '{ print $3 }')
echo "Windows 主机地址：$WSL_HOST"
curl http://$WSL_HOST:11434/v1/models   # 测试 Ollama
```

或者使用你机器的 mDNS 名称（需要在 WSL2 中安装 `libnss-mdns`）：
```bash
sudo apt install libnss-mdns
curl http://$(hostname).local:11434/v1/models
```
:::

<a id="server-bind-address-required-for-nat-mode"></a>
#### 服务器绑定地址（NAT 模式必需）
如果你使用的是**方案 2**（NAT 模式，使用宿主机 IP），Windows 上的模型服务器必须接受来自 `127.0.0.1` 之外的连接。默认情况下，大多数服务器只监听 localhost——NAT 模式下的 WSL2 连接来自不同的虚拟子网，会被拒绝。在镜像模式下，`localhost` 直接映射，因此默认的 `127.0.0.1` 绑定可以正常工作。

| 服务器 | 默认绑定 | 如何修复 |
|--------|---------|----------|
| **Ollama** | `127.0.0.1` | 在启动 Ollama 之前设置 `OLLAMA_HOST=0.0.0.0` 环境变量（Windows 系统设置 → 环境变量，或编辑 Ollama 服务） |
| **LM Studio** | `127.0.0.1` | 在开发者选项卡 → 服务器设置中启用 **“Serve on Network”（在网络上提供服务）** |
| **llama-server** | `127.0.0.1` | 在启动命令中添加 `--host 0.0.0.0` |
| **vLLM** | `0.0.0.0` | 默认已绑定所有接口 |
| **SGLang** | `127.0.0.1` | 在启动命令中添加 `--host 0.0.0.0` |

**Windows 上的 Ollama（详细说明）：** Ollama 作为 Windows 服务运行。要设置 `OLLAMA_HOST`：
1. 打开**系统属性** → **环境变量**
2. 添加一个新的**系统变量**：`OLLAMA_HOST` = `0.0.0.0`
3. 重启 Ollama 服务（或重启系统）
<a id="windows-firewall"></a>
#### Windows 防火墙

Windows 防火墙将 WSL2 视为一个独立的网络（在 NAT 和镜像模式下均如此）。如果完成上述步骤后连接仍然失败，请为模型服务器的端口添加一条防火墙规则：

```powershell
# 在管理员 PowerShell 中运行 — 将 PORT 替换为你的服务器端口
New-NetFirewallRule -DisplayName "允许 WSL2 连接模型服务器" -Direction Inbound -Action Allow -Protocol TCP -LocalPort 11434
```

常用端口：Ollama `11434`、vLLM `8000`、SGLang `30000`、llama-server `8080`、LM Studio `1234`。

<a id="quick-verification"></a>
#### 快速验证

在 WSL2 内部，测试能否连接到模型服务器：

```bash
# 将 URL 替换为你的服务器地址和端口
curl http://localhost:11434/v1/models          # 镜像模式
curl http://172.29.192.1:11434/v1/models       # NAT 模式（使用你的实际主机 IP）
```

如果返回一个列出模型的 JSON 响应，则说明配置正确。请使用相同的 URL 作为 Hermes 配置中的 `base_url`。

---

<a id="troubleshooting-local-models"></a>
### 本地模型故障排查

以下问题会影响与 Hermes 一同使用的**所有**本地推理服务器。
<a id="connection-refused-from-wsl2-to-a-windows-hosted-model-server"></a>
#### 从 WSL2 连接 Windows 上托管的模型服务器时出现 "Connection refused"

如果你在 WSL2 中运行 Hermes，而模型服务器在 Windows 宿主机上，那么在 WSL2 默认的 NAT 网络模式下，`http://localhost:&lt;port&gt;` 将无法正常工作。请参考上方的 [WSL2 网络配置](#wsl2-networking-windows-users) 了解解决方法。

<a id="tool-calls-appear-as-text-instead-of-executing"></a>
#### 工具调用显示为文本而非实际执行

模型输出类似 `{"name": "web_search", "arguments": {...}}` 的消息，而不是实际调用工具。

**原因：** 你的服务器未启用工具调用功能，或者该模型不支持通过服务器的工具调用实现。

| 服务器 | 修复方法 |
|--------|----------|
| **llama.cpp** | 在启动命令中添加 `--jinja` |
| **vLLM** | 添加 `--enable-auto-tool-choice --tool-call-parser hermes` |
| **SGLang** | 添加 `--tool-call-parser qwen`（或合适的解析器） |
| **Ollama** | 工具调用默认已启用 — 请确保你的模型支持该功能（使用 `ollama show model-name` 检查） |
| **LM Studio** | 更新到 0.3.6 及以上版本，并使用原生支持工具的模型 |
<a id="model-seems-to-forget-context-or-give-incoherent-responses"></a>
#### 模型似乎会忘记上下文或给出不连贯的回复

**原因：** 上下文窗口太小。当对话超出上下文限制时，大多数服务端会静默丢弃较早的消息。Hermes 的系统提示词 + 工具模式本身就可能占用 4k–8k tokens。

**诊断：**

```bash
# 检查 Hermes 认为的上下文大小
# 查看启动行："Context limit: X tokens"

# 检查你服务端的实际上下文
# Ollama: ollama ps（CONTEXT 列）
# llama.cpp: curl http://localhost:8080/props | jq '.default_generation_settings.n_ctx'
# vLLM: 在启动参数中检查 --max-model-len
```

**修复：** 对于 Agent 使用，将上下文至少设置为 **32,768 tokens**。有关具体参数，请参见上方每个服务端对应的说明。

<a id="context-limit-2048-tokens-at-startup"></a>
#### 启动时显示 "Context limit: 2048 tokens"

Hermes 会从你的服务端的 `/v1/models` 端点自动检测上下文长度。如果服务端报告了一个较低的值（或者根本没有报告），Hermes 就会使用模型声明的限制，而这个限制可能是错误的。

**修复：** 在 `config.yaml` 中明确设置：

--- END DOCUMENT CHUNK ---
```yaml
model:
  default: your-model
  provider: custom
  base_url: http://localhost:11434/v1
  context_length: 32768
```

<a id="responses-get-cut-off-mid-sentence"></a>
#### 回复在半句中截断

**可能原因：**
1. **服务器上的输出上限（`max_tokens`）过低** — SGLang 默认每个回复为 128 个 token。请在服务器上设置 `--default-max-tokens`，或在 config.yaml 中为 Hermes 配置 `model.max_tokens`。注意：`max_tokens` 仅控制回复长度，与你对话历史可以有多长无关（那是 `context_length` 的事）。
2. **上下文耗尽** — 模型填满了它的上下文窗口。请增大 `model.context_length` 或在 Hermes 中启用[上下文压缩](/user-guide/configuration#context-compression)。

---

<a id="litellm-proxy-multi-provider-gateway"></a>
### LiteLLM 代理 — 多提供商网关

[LiteLLM](https://docs.litellm.ai/) 是一个兼容 OpenAI 的代理，它将 100 多个 LLM 提供商统一在单个 API 之后。最适合：在不修改配置的情况下切换提供商、负载均衡、回退链路、预算控制。

```bash
# 安装并启动
pip install "litellm[proxy]"
litellm --model anthropic/claude-sonnet-4 --port 4000

# 或使用配置文件支持多个模型：
litellm --config litellm_config.yaml --port 4000
```
然后使用 `hermes model` → 自定义端点 → `http://localhost:4000/v1` 配置 Hermes。

带故障切换的示例 `litellm_config.yaml`：
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

<a id="clawrouter-cost-optimized-routing"></a>
### ClawRouter — 成本优化路由

由 BlockRunAI 开发的 [ClawRouter](https://github.com/BlockRunAI/ClawRouter) 是一个本地路由代理，可根据查询复杂度自动选择模型。它会在 14 个维度上对请求进行分类，并路由到能够处理该任务的最便宜模型。支付方式为 USDC 加密货币（无需 API 密钥）。

```bash
# 安装并启动
npx @blockrun/clawrouter    # 默认在端口 8402 启动
```

然后使用 `hermes model` → 自定义端点 → `http://localhost:8402/v1` → 模型名称 `blockrun/auto` 配置 Hermes。

路由方案：
| 方案 | 策略 | 节省成本 |
|---------|----------|---------|
| `blockrun/auto` | 均衡质量/成本 | 74-100% |
| `blockrun/eco` | 尽可能最便宜 | 95-100% |
| `blockrun/premium` | 最佳质量模型 | 0% |
| `blockrun/free` | 仅免费模型 | 100% |
| `blockrun/agentic` | 针对工具使用优化 | 不定 |
:::note
ClawRouter 需要在 Base 或 Solana 上有一个存入 USDC 的钱包用于支付。所有请求都会经过 BlockRun 的后端 API。运行 `npx @blockrun/clawrouter doctor` 检查钱包状态。
:::

---

<a id="other-compatible-providers"></a>
### 其他兼容的提供商

任何兼容 OpenAI API 的服务都可以使用。以下是一些常用的选项：

| 提供商 | 基础 URL | 说明 |
|----------|----------|------|
| [Together AI](https://together.ai) | `https://api.together.xyz/v1` | 云托管的开源模型 |
| [Groq](https://groq.com) | `https://api.groq.com/openai/v1` | 超快推理 |
| [DeepSeek](https://deepseek.com) | `https://api.deepseek.com/v1` | DeepSeek 模型 |
| [Fireworks AI](https://fireworks.ai) | `https://api.fireworks.ai/inference/v1` | 快速开源模型托管 |
| [GMI Cloud](https://www.gmicloud.ai/) | `https://api.gmi-serving.com/v1` | 托管的 OpenAI 兼容推理 |
| [Cerebras](https://cerebras.ai) | `https://api.cerebras.ai/v1` | 晶圆级芯片推理 |
| [Mistral AI](https://mistral.ai) | `https://api.mistral.ai/v1` | Mistral 模型 |
| [OpenAI](https://openai.com) | `https://api.openai.com/v1` | 直接访问 OpenAI |
| [Azure OpenAI](https://azure.microsoft.com) | `https://YOUR.openai.azure.com/` | 企业级 OpenAI |
| [LocalAI](https://localai.io) | `http://localhost:8080/v1` | 自托管，多模型支持 |
| [Jan](https://jan.ai) | `http://localhost:1337/v1` | 带本地模型的桌面应用 |
通过 `hermes model` → Custom endpoint 或在 `config.yaml` 中配置任意一个：

```yaml
model:
  default: meta-llama/Llama-3.1-70B-Instruct-Turbo
  provider: custom
  base_url: https://api.together.xyz/v1
  api_key: your-together-key
```

---

<a id="context-length-detection"></a>
### 上下文长度检测 {#context-length-detection}

<a id="two-settings-easy-to-confuse"></a>
:::note 两个设置，容易混淆
**`context_length`** 是 **总上下文窗口**——输入和输出 token 的合并预算（例如 Claude Opus 4.6 为 200,000）。Hermes 用它来决定何时压缩历史记录以及验证 API 请求。

**`model.max_tokens`** 是 **输出上限**——模型在 *单次响应* 中可生成的最大 token 数。它与对话历史能有多长无关。行业标准名称 `max_tokens` 是常见的混淆来源；Anthropic 的原生 API 已将其改为 `max_output_tokens` 以更清晰。

当自动检测得到的窗口大小有误时，设置 `context_length`。
仅当需要限制单次响应的长度时，设置 `model.max_tokens`。
:::
Hermes 使用多源解析链来检测你的模型和提供商对应的上下文窗口：

1. **配置覆盖** — `config.yaml` 中的 `model.context_length`（最高优先级）
2. **每个模型的自定义提供商** — `custom_providers[].models.&lt;id&gt;.context_length`
3. **持久缓存** — 之前发现的值（重启后依然保留）
4. **`/models` 端点** — 查询你的服务器 API（本地/自定义端点）
5. **Anthropic `/v1/models`** — 查询 Anthropic 的 API 获取 `max_input_tokens`（仅限 API 密钥用户）
6. **OpenRouter API** — 来自 OpenRouter 的实时模型元数据
7. **Nous Portal** — 将 Nous 模型 ID 与 OpenRouter 元数据进行后缀匹配
8. **[models.dev](https://models.dev)** — 社区维护的注册表，涵盖 100 多个提供商、3800+ 个模型的特定提供商上下文长度
9. **回退默认值** — 宽泛的模型族模式（默认 128K）

对于大多数配置，这开箱即用。系统能够感知提供商——同一个模型根据谁提供服务可以有不同的上下文限制（例如，`claude-opus-4.6` 在 Anthropic 直连上是 1M，但在 GitHub Copilot 上只有 128K）。
要显式设置上下文长度，请在模型配置中添加 `context_length`：

```yaml
model:
  default: "qwen3.5:9b"
  base_url: "http://localhost:8080/v1"
  context_length: 131072  # tokens
```

对于自定义端点，你还可以按模型设置上下文长度：

```yaml
custom_providers:
  - name: "My Local LLM"
    base_url: "http://localhost:11434/v1"
    models:
      qwen3.5:27b:
        context_length: 32768
      deepseek-r1:70b:
        context_length: 65536
```

`hermes model` 在配置自定义端点时会提示输入上下文长度。留空则会自动检测。

:::tip 何时需要手动设置
<a id="when-to-set-this-manually"></a>
- 你在使用 Ollama 且自定义 `num_ctx` 低于模型的最大值
- 你想将上下文限制在模型最大值以下（例如，在 128k 模型上只使用 8k 以节省显存）
- 你的服务运行在一个不暴露 `/v1/models` 端点的代理后面
:::

---

<a id="named-custom-providers"></a>
### 命名自定义 Provider

如果你同时使用多个自定义端点（例如，一个本地开发服务器和一个远程 GPU 服务器），你可以在 `config.yaml` 中将其定义为命名自定义 provider：
```yaml
custom_providers:
  - name: local
    base_url: http://localhost:8080/v1
    # api_key 已省略 — Hermes 对无密钥的本地服务器使用 "no-key-required"
  - name: work
    base_url: https://gpu-server.internal.corp/v1
    key_env: CORP_API_KEY
    api_mode: chat_completions   # 由 `hermes model` → 自定义端点向导显式设置；自动检测仍作为后备方案
  - name: anthropic-proxy
    base_url: https://proxy.example.com/anthropic
    key_env: ANTHROPIC_PROXY_KEY
    api_mode: anthropic_messages  # 用于兼容 Anthropic 的代理
```

`hermes model` → 自定义端点向导现在会显式提示输入 `api_mode`，并将你的回答持久化到 `config.yaml` 中。当该字段留空时，基于 URL 的自动检测（例如 `/anthropic` 路径 → `anthropic_messages`）仍会作为后备方案执行。

在会话中切换它们，使用三重语法：

```
/model custom:local:qwen-2.5       # 使用 "local" 端点搭配 qwen-2.5
/model custom:work:llama3-70b      # 使用 "work" 端点搭配 llama3-70b
/model custom:anthropic-proxy:claude-sonnet-4  # 使用代理
```
您也可以从交互式 `hermes model` 菜单中选择已命名的自定义提供商。

---

<a id="cookbook-together-ai-groq-perplexity"></a>
### 操作指南：Together AI、Groq、Perplexity

[其他兼容提供商](#other-compatible-providers) 中列出的云提供商都使用 OpenAI 的 REST 方言，因此它们在 `custom_providers:` 下的配置方式相同。以下是三个可直接使用的配置示例。每个配置都需放入 `~/.hermes/config.yaml`，对应的 API 密钥则放入 `~/.hermes/.env`。

<a id="together-ai"></a>
#### Together AI

托管开放权重模型（Llama、MiniMax、Gemma、DeepSeek、Qwen），价格远低于第一方 API。是多模型集群的不错默认选择。

```yaml
# ~/.hermes/config.yaml
custom_providers:
  - name: together
    base_url: https://api.together.xyz/v1
    key_env: TOGETHER_API_KEY
    # api_mode: chat_completions  # 默认值 — 无需设置

model:
  default: MiniMaxAI/MiniMax-M2.7   # 或来自 together.ai/models 的任何模型
  provider: custom:together
```

```bash
# ~/.hermes/.env
TOGETHER_API_KEY=your-together-key
```

在会话中切换模型：
```
/model custom:together:meta-llama/Llama-3.3-70B-Instruct-Turbo
/model custom:together:google/gemma-4-31b-it
/model custom:together:deepseek-ai/DeepSeek-V3
```

Together 的 `/v1/models` 端点可用，所以 `hermes model` 能自动发现可用的模型。

<a id="groq"></a>
#### Groq

超快推理（Llama-3.3-70B 上约 500 tok/s）。目录较小，但对于延迟敏感的交互式使用非常强劲。

```yaml
# ~/.hermes/config.yaml
custom_providers:
  - name: groq
    base_url: https://api.groq.com/openai/v1
    key_env: GROQ_API_KEY

model:
  default: llama-3.3-70b-versatile
  provider: custom:groq
```

```bash
# ~/.hermes/.env
GROQ_API_KEY=your-groq-key
```

<a id="perplexity"></a>
#### Perplexity

当你需要一个能自动进行实时网络搜索并提供引用的模型时，Perplexity 很有用。它对可用的模型要求严格——请查看 [perplexity.ai/settings/api](https://www.perplexity.ai/settings/api) 了解当前列表。

```yaml
# ~/.hermes/config.yaml
custom_providers:
  - name: perplexity
    base_url: https://api.perplexity.ai
    key_env: PERPLEXITY_API_KEY

model:
  default: sonar
  provider: custom:perplexity
```
```bash
# ~/.hermes/.env
PERPLEXITY_API_KEY=your-perplexity-key
```

<a id="multiple-providers-in-one-config"></a>
#### 在单个配置中使用多个 Provider

三种配置方式可以组合使用——将它们全部放在一起，然后通过 `/model custom:<名称>:<模型>` 在每次对话中切换：

```yaml
custom_providers:
  - name: together
    base_url: https://api.together.xyz/v1
    key_env: TOGETHER_API_KEY
  - name: groq
    base_url: https://api.groq.com/openai/v1
    key_env: GROQ_API_KEY
  - name: perplexity
    base_url: https://api.perplexity.ai
    key_env: PERPLEXITY_API_KEY

model:
  default: MiniMaxAI/MiniMax-M2.7
  provider: custom:together      # 启动时使用 Together；之后可自由切换
```

<a id="troubleshooting"></a>
:::tip 故障排查
- 在 CLI 验证器修复（#15083）之后，`hermes doctor` 应该不会对这些名称中的任何一个打印 `Unknown provider` 警告。
- 如果某个 provider 的 `/v1/models` 端点不可达（Perplexity 是常见情况），`hermes model` 会保留该模型并给出警告，而不是直接拒绝——参见 #15136。
- 如果想完全跳过 `custom_providers:`，直接使用 `provider: custom` 配合 `CUSTOM_BASE_URL` 环境变量，请参见 #15103。
:::
---

<a id="choosing-the-right-setup"></a>
### 选择合适的配置

| 使用场景 | 推荐方案 |
|----------|----------|
| **开箱即用** | OpenRouter（默认）或 Nous Portal |
| **本地模型，简单配置** | Ollama |
| **生产环境 GPU 服务** | vLLM 或 SGLang |
| **Mac / 无 GPU** | Ollama 或 llama.cpp |
| **多提供商路由** | LiteLLM Proxy 或 OpenRouter |
| **成本优化** | ClawRouter 或 OpenRouter（搭配 `sort: "price"`） |
| **最高隐私保护** | Ollama、vLLM 或 llama.cpp（完全本地） |
| **企业 / Azure** | 使用自定义端点的 Azure OpenAI |
| **中文 AI 模型** | z.ai（GLM）、Kimi/Moonshot（`kimi-coding` 或 `kimi-coding-cn`）、MiniMax、小米 MiMo 或腾讯混元 TokenHub（一级提供商） |

:::tip
你可以随时使用 `hermes model` 切换提供商——无需重启。无论使用哪个提供商，你的对话历史、记忆和技能都会保留。
:::

<a id="optional-api-keys"></a>
## 可选 API 密钥

| 功能 | 提供商 | 环境变量 |
|---------|----------|--------------|
| 网页抓取 | [Firecrawl](https://firecrawl.dev/) | `FIRECRAWL_API_KEY`、`FIRECRAWL_API_URL` |
| 浏览器自动化 | [Browserbase](https://browserbase.com/) | `BROWSERBASE_API_KEY`、`BROWSERBASE_PROJECT_ID` |
| 图像生成 | [FAL](https://fal.ai/) | `FAL_KEY` |
| 高级 TTS 语音 | [ElevenLabs](https://elevenlabs.io/) | `ELEVENLABS_API_KEY` |
| OpenAI TTS + 语音转录 | [OpenAI](https://platform.openai.com/api-keys) | `VOICE_TOOLS_OPENAI_KEY` |
| Mistral TTS + 语音转录 | [Mistral](https://console.mistral.ai/) | `MISTRAL_API_KEY` |
| 跨会话用户建模 | [Honcho](https://honcho.dev/) | `HONCHO_API_KEY` |
| 语义长期记忆 | [Supermemory](https://supermemory.ai) | `SUPERMEMORY_API_KEY` |
<a id="self-hosting-firecrawl"></a>
### 自托管 Firecrawl

默认情况下，Hermes 使用 [Firecrawl 云 API](https://firecrawl.dev/) 进行网络搜索和抓取。如果你更愿意在本地运行 Firecrawl，可以将 Hermes 指向一个自托管实例。有关完整的安装说明，请参见 Firecrawl 的 [SELF_HOST.md](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md)。

**你获得的好处：** 无需 API 密钥，没有速率限制，没有按页计费，完全的数据主权。

**你失去的：** 云版本使用 Firecrawl 专有的 "Fire-engine" 进行高级反爬绕过（Cloudflare、CAPTCHAs、IP 轮换）。自托管版本使用基本的 fetch + Playwright，因此一些受保护的网站可能会失败。搜索使用 DuckDuckGo 而非 Google。

**安装步骤：**

1. 克隆并启动 Firecrawl Docker 栈（5 个容器：API、Playwright、Redis、RabbitMQ、PostgreSQL——需要约 4-8 GB 内存）：
   ```bash
   git clone https://github.com/firecrawl/firecrawl
   cd firecrawl
   # In .env, set: USE_DB_AUTHENTICATION=false, HOST=0.0.0.0, PORT=3002
   docker compose up -d
   ```
2. 将 Hermes 指向你的实例（无需 API 密钥）：
   ```bash
   hermes config set FIRECRAWL_API_URL http://localhost:3002
   ```

如果自托管实例启用了身份验证，你也可以同时设置 `FIRECRAWL_API_KEY` 和 `FIRECRAWL_API_URL`。

<a id="openrouter-provider-routing"></a>
## OpenRouter 提供商路由

使用 OpenRouter 时，你可以控制请求在提供商之间的路由方式。在 `~/.hermes/config.yaml` 中添加 `provider_routing` 部分：

```yaml
provider_routing:
  sort: "throughput"          # "price" (default), "throughput", or "latency"
  # only: ["anthropic"]      # Only use these providers
  # ignore: ["deepinfra"]    # Skip these providers
  # order: ["anthropic", "google"]  # Try providers in this order
  # require_parameters: true  # Only use providers that support all request params
  # data_collection: "deny"   # Exclude providers that may store/train on data
```

**快捷方式：** 在任何模型名称后追加 `:nitro` 可按吞吐量排序（例如 `anthropic/claude-sonnet-4:nitro`），追加 `:floor` 可按价格排序。
<a id="openrouter-pareto-code-router"></a>
## OpenRouter Pareto Code Router

OpenRouter 在 `openrouter/pareto-code` 提供了一个实验性的编码模型路由器，它会自动将请求路由到满足编码质量门槛的最便宜模型（排名依据 [Artificial Analysis](https://artificialanalysis.ai/)）。选择此模型并在 `~/.hermes/config.yaml` 中调整 `min_coding_score` 参数：

```yaml
model:
  provider: openrouter
  model: openrouter/pareto-code

openrouter:
  min_coding_score: 0.65   # 0.0–1.0；值越高 = 编码能力越强（也更贵）。默认值 0.65。
```

注意事项：

- `min_coding_score` **仅**在 `model.model` 为 `openrouter/pareto-code` 时才会发送。对于其他任何模型，该值均无效。
- 设置为空字符串（或删除该行）可让 OpenRouter 选择当前可用的最强编码模型——这是省略插件块时的文档化行为。
- 在给定日期内，选择结果按分数确定，但实际选中的模型会随着帕累托前沿的变化（新模型、基准测试更新）而变动。
- 有关路由器的完整行为，请参阅 OpenRouter 的 [Pareto Router 文档](https://openrouter.ai/docs/guides/routing/routers/pareto-router)。
- 若要将 Pareto Code 路由器用于特定的**辅助任务**（压缩、视觉等）而非主 Agent，请在该任务下设置 `extra_body.plugins`——参见 [辅助模型 → OpenRouter 路由与辅助任务的 Pareto Code](/user-guide/configuration#openrouter-routing--pareto-code-for-auxiliary-tasks)。
<a id="fallback-providers"></a>
## 备用提供商

配置一个备份提供商链，当主模型失败时（速率限制、服务器错误、认证失败），Hermes 会按顺序尝试这些提供商。标准格式是在顶层使用 `fallback_providers:` 列表：

```yaml
fallback_providers:
  - provider: openrouter
    model: anthropic/claude-sonnet-4
  - provider: anthropic
    model: claude-sonnet-4
    # base_url: http://localhost:8000/v1    # 可选，用于自定义端点
    # api_mode: chat_completions           # 可选覆盖
```

为了向后兼容，仍然支持旧式的单对 `fallback_model:` 字典格式：

```yaml
fallback_model:
  provider: openrouter
  model: anthropic/claude-sonnet-4
```

当启用时，备用机制会在会话中途切换模型和提供商，而不会丢失你的对话。链会逐条尝试；每个会话只触发一次。

支持的提供商：`openrouter`、`nous`、`openai-codex`、`copilot`、`copilot-acp`、`anthropic`、`gemini`、`google-gemini-cli`、`qwen-oauth`、`huggingface`、`zai`、`kimi-coding`、`kimi-coding-cn`、`minimax`、`minimax-cn`、`minimax-oauth`、`deepseek`、`nvidia`、`xai`、`xai-oauth`、`ollama-cloud`、`bedrock`、`ai-gateway`、`azure-foundry`、`opencode-zen`、`opencode-go`、`kilocode`、`xiaomi`、`arcee`、`gmi`、`stepfun`、`lmstudio`、`alibaba`、`alibaba-coding-plan`、`tencent-tokenhub`、`custom`。
:::tip
回退完全通过 `config.yaml` 配置，或通过 `hermes fallback` 交互式进行。有关何时触发回退、链如何推进、以及回退如何与辅助任务和委托交互的完整细节，请参阅[回退 Provider](/user-guide/features/fallback-providers)。
:::

---

<a id="see-also"></a>
## 另请参阅

- [配置](/user-guide/configuration) — 通用配置（目录结构、配置优先级、终端后端、内存、压缩等）
- [环境变量](/reference/environment-variables) — 所有环境变量的完整参考
