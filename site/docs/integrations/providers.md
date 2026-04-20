---
title: "AI Providers"
sidebar_label: "AI Providers"
sidebar_position: 1
---

# AI Providers {#ai-providers}

本页介绍如何为 Hermes Agent 配置推理提供商——从 OpenRouter、Anthropic 等云 API，到 Ollama、vLLM 等自托管端点，再到高级路由和回退配置。你需要至少配置一个提供商才能使用 Hermes。

## 推理提供商 {#inference-providers}

你需要至少一种连接 LLM 的方式。使用 `hermes model` 交互式切换提供商和模型，或直接进行配置：

| Provider | Setup |
|----------|-------|
| **Nous Portal** | `hermes model`（OAuth，基于订阅） |
| **OpenAI Codex** | `hermes model`（ChatGPT OAuth，使用 Codex 模型） |
| **GitHub Copilot** | `hermes model`（OAuth 设备码流程，`COPILOT_GITHUB_TOKEN`、`GH_TOKEN` 或 `gh auth token`） |
| **GitHub Copilot ACP** | `hermes model`（启动本地 `copilot --acp --stdio`） |
| **Anthropic** | `hermes model`（通过 Claude Code 认证使用 Claude Pro/Max、Anthropic API key 或手动 setup-token） |
| **OpenRouter** | `OPENROUTER_API_KEY` 配置在 `~/.hermes/.env` |
| **AI Gateway** | `AI_GATEWAY_API_KEY` 配置在 `~/.hermes/.env`（provider: `ai-gateway`） |
| **z.ai / GLM** | `GLM_API_KEY` 配置在 `~/.hermes/.env`（provider: `zai`） |
| **Kimi / Moonshot** | `KIMI_API_KEY` 配置在 `~/.hermes/.env`（provider: `kimi-coding`） |
| **Kimi / Moonshot (China)** | `KIMI_CN_API_KEY` 配置在 `~/.hermes/.env`（provider: `kimi-coding-cn`；别名：`kimi-cn`、`moonshot-cn`） |
| **Arcee AI** | `ARCEEAI_API_KEY` 配置在 `~/.hermes/.env`（provider: `arcee`；别名：`arcee-ai`、`arceeai`） |
| **MiniMax** | `MINIMAX_API_KEY` 配置在 `~/.hermes/.env`（provider: `minimax`） |
| **MiniMax China** | `MINIMAX_CN_API_KEY` 配置在 `~/.hermes/.env`（provider: `minimax-cn`） |
| **Alibaba Cloud** | `DASHSCOPE_API_KEY` 配置在 `~/.hermes/.env`（provider: `alibaba`，别名：`dashscope`、`qwen`） |
| **Kilo Code** | `KILOCODE_API_KEY` 配置在 `~/.hermes/.env`（provider: `kilocode`） |
| **Xiaomi MiMo** | `XIAOMI_API_KEY` 配置在 `~/.hermes/.env`（provider: `xiaomi`，别名：`mimo`、`xiaomi-mimo`） |
| **OpenCode Zen** | `OPENCODE_ZEN_API_KEY` 配置在 `~/.hermes/.env`（provider: `opencode-zen`） |
| **OpenCode Go** | `OPENCODE_GO_API_KEY` 配置在 `~/.hermes/.env`（provider: `opencode-go`） |
| **DeepSeek** | `DEEPSEEK_API_KEY` 配置在 `~/.hermes/.env`（provider: `deepseek`） |
| **Hugging Face** | `HF_TOKEN` 配置在 `~/.hermes/.env`（provider: `huggingface`，别名：`hf`） |
| **Google / Gemini** | `GOOGLE_API_KEY`（或 `GEMINI_API_KEY`）配置在 `~/.hermes/.env`（provider: `gemini`） |
| **Google Gemini (OAuth)** | `hermes model` → 选择 "Google Gemini (OAuth)"（provider: `google-gemini-cli`，支持免费额度，浏览器 PKCE 登录） |
| **Custom Endpoint** | `hermes model` → 选择 "Custom endpoint"（保存在 `config.yaml`） |

:::tip Model key alias
在 `model:` 配置段中，你可以用 `default:` 或 `model:` 作为模型 ID 的键名。`model: { default: my-model }` 和 `model: { model: my-model }` 效果完全相同。
:::


### Google Gemini via OAuth (`google-gemini-cli`) {#google-gemini-via-oauth-google-gemini-cli}

`google-gemini-cli` 提供商使用 Google 的 Cloud Code Assist 后端——也就是 Google 自家 `gemini-cli` 工具所用的同一套 API。它同时支持**免费额度**（个人账号每日 generous 配额）和**付费档位**（通过 GCP 项目的 Standard/Enterprise）。

**快速开始：**

```bash
hermes model
# → 选择 "Google Gemini (OAuth)"
# → 查看政策警告，确认
# → 浏览器打开 accounts.google.com，登录
# → 完成 — Hermes 会在首次请求时自动为你开通免费额度
```

Hermes 默认内置了 Google **公开的** `gemini-cli` 桌面端 OAuth 客户端——与 Google 在其开源 `gemini-cli` 中包含的凭据相同。桌面端 OAuth 客户端不是机密性质的（安全性由 PKCE 保障）。你无需安装 `gemini-cli`，也无需注册自己的 GCP OAuth 客户端。

**认证机制：**
- 对 `accounts.google.com` 使用 PKCE 授权码流程
- 浏览器回调地址为 `http://127.0.0.1:8085/oauth2callback`（端口被占用时自动回退到临时端口）
- Token 保存在 `~/.hermes/auth/google_oauth.json`（权限 0600，原子写入，跨进程 `fcntl` 锁）
- 到期前 60 秒自动刷新
- 无头环境（SSH、`HERMES_HEADLESS=1`）→ 降级为粘贴模式
- 并发刷新去重——两个同时进行的请求不会触发双重刷新
- `invalid_grant`（刷新 token 被撤销）→ 清空凭据文件，提示用户重新登录
**推理工作方式：**
- 流量发往 `https://cloudcode-pa.googleapis.com/v1internal:generateContent`
  （流式请求为 `:streamGenerateContent?alt=sse`），而不是付费的 `v1beta/openai` 端点
- 请求体会包装成 `{project, model, user_prompt_id, request}` 结构
- OpenAI 格式的 `messages[]`、`tools[]`、`tool_choice` 会被转换为 Gemini 原生的
  `contents[]`、`tools[].functionDeclarations`、`toolConfig` 格式
- 响应再转回 OpenAI 格式，这样 Hermes 的其他部分无需改动即可正常工作

**层级与项目 ID：**

| 你的情况 | 操作方式 |
|---|---|
| 个人 Google 账号，想使用免费层级 | 什么都不用做 — 登录后即可开始聊天 |
| Workspace / Standard / Enterprise 账号 | 将 `HERMES_GEMINI_PROJECT_ID` 或 `GOOGLE_CLOUD_PROJECT` 设为你的 GCP 项目 ID |
| 受 VPC-SC 保护的企业组织 | Hermes 检测到 `SECURITY_POLICY_VIOLATED` 后会自动强制使用 `standard-tier` |

免费层级会在首次使用时自动分配一个 Google 托管的项目，无需配置 GCP。

**配额监控：**

```
/gquota
```

显示各模型剩余的 Code Assist 配额，带进度条：

```
Gemini Code Assist quota  (project: 123-abc)

  gemini-2.5-pro                      ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░   85%
  gemini-2.5-flash [input]            ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░   92%
```

:::warning 政策风险
Google 认为将 Gemini CLI 的 OAuth 客户端用于第三方软件属于违反政策的行为。已有用户报告账号受到限制。若想将风险降到最低，建议通过 `gemini` provider 使用你自己的 API key。Hermes 会在开始 OAuth 前显示明确警告，并要求你确认后才继续。
<a id="policy-risk"></a>
:::

**自定义 OAuth 客户端（可选）：**

如果你想注册自己的 Google OAuth 客户端 —— 例如把配额和授权范围限制在自己的 GCP 项目内 —— 可以设置：

```bash
HERMES_GEMINI_CLIENT_ID=your-client.apps.googleusercontent.com
HERMES_GEMINI_CLIENT_SECRET=...   # Desktop 客户端可选
```

在 [console.cloud.google.com/apis/credentials](https://console.cloud.google.com/apis/credentials)
注册一个 **Desktop app** OAuth 客户端，并启用 Generative Language API。

:::info Codex 说明
OpenAI Codex provider 通过设备码方式认证（打开网址、输入验证码）。Hermes 将获取到的凭证保存在自己的认证存储 `~/.hermes/auth.json` 中，也能在检测到 `~/.codex/auth.json` 时导入已有的 Codex CLI 凭证。无需安装 Codex CLI。
<a id="codex-note"></a>
:::

:::warning
即使使用 Nous Portal、Codex 或自定义端点，部分工具（视觉、网页摘要、MoA）仍会使用单独的"辅助"模型 —— 默认是通过 OpenRouter 调用的 Gemini Flash。设置 `OPENROUTER_API_KEY` 后这些工具会自动启用。你也可以配置这些工具使用的具体模型和 provider —— 详见 [辅助模型](/user-guide/configuration#auxiliary-models)。
:::

:::tip Nous Tool Gateway
付费 Nous Portal 订阅者还可以使用 **[Tool Gateway](/user-guide/features/tool-gateway)** —— 网页搜索、图像生成、TTS 和浏览器自动化都通过你的订阅路由。无需额外 API key。在 `hermes model` 设置时会自动提供该选项，也可以稍后通过 `hermes tools` 启用。
:::

### 两条模型管理命令 {#two-commands-for-model-management}

Hermes 有**两条**模型命令，用途各不相同：

| 命令 | 运行位置 | 功能 |
|---------|-------------|--------------|
| **`hermes model`** | 终端中（不在任何会话内） | 完整的设置向导 —— 添加 provider、执行 OAuth、输入 API key、配置端点 |
| **`/model`** | Hermes 聊天会话内部 | 在**已配置好**的 provider 和模型之间快速切换 |

如果你想切换到一个还没配置过的 provider（例如目前只配了 OpenRouter，想改用 Anthropic），需要用 `hermes model` 而不是 `/model`。先退出当前会话（`Ctrl+C` 或 `/quit`），运行 `hermes model` 完成 provider 设置，再开启新会话。

### Anthropic（原生） {#anthropic-native}

直接通过 Anthropic API 使用 Claude 模型 —— 无需 OpenRouter 中转。支持三种认证方式：
```bash
# 使用 API key（按 token 计费）
export ANTHROPIC_API_KEY=***
hermes chat --provider anthropic --model claude-sonnet-4-6

# 推荐方式：通过 `hermes model` 认证
# Hermes 会在可用时直接使用 Claude Code 的凭据存储
hermes model

# 手动通过 setup-token 覆盖（备用 / 旧版方式）
export ANTHROPIC_TOKEN=***  # setup-token 或手动 OAuth token
hermes chat --provider anthropic

# 自动检测 Claude Code 凭据（如果你已经在用 Claude Code）
hermes chat --provider anthropic  # 自动读取 Claude Code 的凭据文件
```

当你通过 `hermes model` 选择 Anthropic OAuth 时，Hermes 会优先使用 Claude Code 自身的凭据存储，而不是把 token 复制到 `~/.hermes/.env`。这样可以让 Claude 的可刷新凭据继续保持可刷新。

或者永久设置：
```yaml
model:
  provider: "anthropic"
  default: "claude-sonnet-4-6"
```

:::tip 别名
`--provider claude` 和 `--provider claude-code` 也可以作为 `--provider anthropic` 的简写。
<a id="aliases"></a>
:::

### GitHub Copilot {#github-copilot}

Hermes 将 GitHub Copilot 作为一等提供商支持，提供两种模式：

**`copilot` — 直接调用 Copilot API**（推荐）。使用你的 GitHub Copilot 订阅，通过 Copilot API 访问 GPT-5.x、Claude、Gemini 等模型。

```bash
hermes chat --provider copilot --model gpt-5.4
```

**认证选项**（按以下顺序检查）：

1. `COPILOT_GITHUB_TOKEN` 环境变量
2. `GH_TOKEN` 环境变量
3. `GITHUB_TOKEN` 环境变量
4. `gh auth token` CLI 回退

如果找不到 token，`hermes model` 会提供 **OAuth 设备码登录** —— 与 Copilot CLI 和 opencode 使用的流程相同。

:::warning Token 类型
<a id="token-types"></a>
Copilot API **不**支持经典的 Personal Access Token（`ghp_*`）。支持的 token 类型：

| 类型 | 前缀 | 获取方式 |
|------|--------|------------|
| OAuth token | `gho_` | `hermes model` → GitHub Copilot → Login with GitHub |
| Fine-grained PAT | `github_pat_` | GitHub Settings → Developer settings → Fine-grained tokens（需要 **Copilot Requests** 权限） |
| GitHub App token | `ghu_` | 通过 GitHub App 安装获取 |

如果你的 `gh auth token` 返回的是 `ghp_*` token，请改用 `hermes model` 通过 OAuth 认证。
:::

**API 路由**：GPT-5+ 模型（`gpt-5-mini` 除外）自动使用 Responses API。其他所有模型（GPT-4o、Claude、Gemini 等）使用 Chat Completions。模型从实时 Copilot 目录中自动检测。

**`copilot-acp` — Copilot ACP Agent 后端**。将本地 Copilot CLI 作为子进程启动：

```bash
hermes chat --provider copilot-acp --model copilot-acp
# 需要 GitHub Copilot CLI 在 PATH 中，且已有 `copilot login` 会话
```

**永久配置：**
```yaml
model:
  provider: "copilot"
  default: "gpt-5.4"
```

| 环境变量 | 说明 |
|---------------------|-------------|
| `COPILOT_GITHUB_TOKEN` | 用于 Copilot API 的 GitHub token（第一优先级） |
| `HERMES_COPILOT_ACP_COMMAND` | 覆盖 Copilot CLI 二进制路径（默认：`copilot`） |
| `HERMES_COPILOT_ACP_ARGS` | 覆盖 ACP 参数（默认：`--acp --stdio`） |

### 国产 AI 提供商（一等支持） {#first-class-chinese-ai-providers}

这些提供商内置支持，拥有专属的 provider ID。设置 API key 后，用 `--provider` 选择即可：

```bash
# z.ai / 智谱 AI GLM
hermes chat --provider zai --model glm-5
# 需要：GLM_API_KEY 配置在 ~/.hermes/.env

# Kimi / Moonshot AI（国际版：api.moonshot.ai）
hermes chat --provider kimi-coding --model kimi-for-coding
# 需要：KIMI_API_KEY 配置在 ~/.hermes/.env

# Kimi / Moonshot AI（国内版：api.moonshot.cn）
hermes chat --provider kimi-coding-cn --model kimi-k2.5
# 需要：KIMI_CN_API_KEY 配置在 ~/.hermes/.env

# MiniMax（全球节点）
hermes chat --provider minimax --model MiniMax-M2.7
# 需要：MINIMAX_API_KEY 配置在 ~/.hermes/.env

# MiniMax（国内节点）
hermes chat --provider minimax-cn --model MiniMax-M2.7
# 需要：MINIMAX_CN_API_KEY 配置在 ~/.hermes/.env

# 阿里云 / DashScope（通义千问模型）
hermes chat --provider alibaba --model qwen3.5-plus
# 需要：DASHSCOPE_API_KEY 配置在 ~/.hermes/.env

# 小米 MiMo
hermes chat --provider xiaomi --model mimo-v2-pro
# 需要：XIAOMI_API_KEY 配置在 ~/.hermes/.env

# Arcee AI（Trinity 模型）
hermes chat --provider arcee --model trinity-large-thinking
# 需要：ARCEEAI_API_KEY 配置在 ~/.hermes/.env
```
或者在 `config.yaml` 中永久设置 provider：
```yaml
model:
  provider: "zai"       # 可选：kimi-coding, kimi-coding-cn, minimax, minimax-cn, alibaba, xiaomi, arcee
  default: "glm-5"
```

Base URL 可以通过 `GLM_BASE_URL`、`KIMI_BASE_URL`、`MINIMAX_BASE_URL`、`MINIMAX_CN_BASE_URL`、`DASHSCOPE_BASE_URL` 或 `XIAOMI_BASE_URL` 环境变量覆盖。

:::note Z.AI 端点自动探测
使用 Z.AI / GLM provider 时，Hermes 会自动探测多个端点（全球版、中国版、编程版），找到能接受你 API key 的那个。不需要手动设置 `GLM_BASE_URL`——可用的端点会被自动探测并缓存。
:::
<a id="z-ai-endpoint-auto-detection"></a>

### xAI (Grok) — Responses API + 提示词缓存 {#xai-grok-responses-api-prompt-caching}

xAI 通过 Responses API（`codex_responses` transport）接入，Grok 4 模型自动支持推理——不需要 `reasoning_effort` 参数，服务器默认就会推理。在 `~/.hermes/.env` 中设置 `XAI_API_KEY`，然后在 `hermes model` 中选择 xAI，或者直接输入 `/model grok-4-1-fast-reasoning` 快捷切换。

当使用 xAI 作为 provider（任意包含 `x.ai` 的 base URL）时，Hermes 会自动启用提示词缓存，每次 API 请求都会带上 `x-grok-conv-id` header。这会把同一会话中的请求路由到同一台服务器，让 xAI 的基础设施复用缓存的系统提示词和对话历史。

无需配置——检测到 xAI 端点且存在 session ID 时，缓存会自动激活。这能降低多轮对话的延迟和费用。

xAI 还提供了独立的 TTS 端点（`/v1/tts`）。在 `hermes tools` → Voice & TTS 中选择 **xAI TTS**，或查看 [Voice & TTS](../user-guide/features/tts.md#text-to-speech) 页面了解配置。

### Ollama Cloud — 托管 Ollama 模型，OAuth + API Key {#ollama-cloud-managed-ollama-models-oauth-api-key}

[Ollama Cloud](https://ollama.com/cloud) 托管了与本地 Ollama 相同的开源权重模型目录，但不需要 GPU。在 `hermes model` 中选择 **Ollama Cloud**，从 [ollama.com/settings/keys](https://ollama.com/settings/keys) 粘贴你的 API key，Hermes 会自动发现可用模型。

```bash
hermes model
# → 选择 "Ollama Cloud"
# → 粘贴你的 OLLAMA_API_KEY
# → 从发现的模型中选择（gpt-oss:120b, glm-4.6:cloud, qwen3-coder:480b-cloud 等）
```

或者直接写 `config.yaml`：
```yaml
model:
  provider: "ollama-cloud"
  default: "gpt-oss:120b"
```

模型目录从 `ollama.com/v1/models` 动态获取，缓存一小时。`model:tag` 格式（如 `qwen3-coder:480b-cloud`）在规范化过程中会被保留——不要用短横线替代。

:::tip Ollama Cloud 与本地 Ollama 的区别
<a id="ollama-cloud-vs-local-ollama"></a>
两者使用相同的 OpenAI 兼容 API。Cloud 是一等 provider（`--provider ollama-cloud`，`OLLAMA_API_KEY`）；本地 Ollama 通过 Custom Endpoint 流程接入（base URL `http://localhost:11434/v1`，无需 key）。Cloud 适合本地跑不动的大模型；本地适合注重隐私或离线工作的场景。
:::

### AWS Bedrock {#aws-bedrock}

通过 AWS Bedrock 使用 Anthropic Claude、Amazon Nova、DeepSeek v3.2、Meta Llama 4 等模型。使用 AWS SDK（`boto3`）的凭证链——不需要 API key，标准 AWS 认证即可。

```bash
# 最简单的方式——~/.aws/credentials 中的命名 profile
hermes chat --provider bedrock --model us.anthropic.claude-sonnet-4-6

# 或者显式指定环境变量
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
  # discovery: true            # 从 IAM 自动发现 region
  # guardrail:                 # 可选的 Bedrock Guardrails
  #   id: "your-guardrail-id"
  #   version: "DRAFT"
```

认证使用标准 boto3 链：显式的 `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY`、`~/.aws/credentials` 中的 `AWS_PROFILE`、EC2/ECS/Lambda 上的 IAM 角色、IMDS 或 SSO。如果你已经用 AWS CLI 登录过，就不需要额外设置环境变量。
Bedrock 底层使用 **Converse API** —— 请求会被转换为 Bedrock 的模型无关格式，因此相同的配置可以同时用于 Claude、Nova、DeepSeek 和 Llama 模型。只有在你调用非默认区域端点时才需要设置 `BEDROCK_BASE_URL`。

有关 IAM 设置、区域选择和跨区域推理的详细步骤，请参阅 [AWS Bedrock 指南](/guides/aws-bedrock)。

### Qwen Portal (OAuth) {#qwen-portal-oauth}

阿里巴巴 Qwen Portal，支持浏览器 OAuth 登录。在 `hermes model` 中选择 **Qwen OAuth (Portal)**，通过浏览器登录后，Hermes 会自动保存刷新令牌。

```bash
hermes model
# → 选择 "Qwen OAuth (Portal)"
# → 浏览器打开；用阿里巴巴账号登录
# → 确认 — 凭据保存到 ~/.hermes/auth.json

hermes chat   # 使用 portal.qwen.ai/v1 端点
```

或者在 `config.yaml` 中配置：
```yaml
model:
  provider: "qwen-oauth"
  default: "qwen3-coder-plus"
```

只有 portal 端点发生变更时才需要设置 `HERMES_QWEN_BASE_URL`（默认：`https://portal.qwen.ai/v1`）。

:::tip Qwen OAuth 与 DashScope（阿里巴巴）对比
`qwen-oauth` 使用面向消费者的 Qwen Portal 并通过 OAuth 登录 —— 适合个人用户。`alibaba` provider 则使用 DashScope 的企业 API，需要 `DASHSCOPE_API_KEY` —— 适合程序化 / 生产负载。两者都接入 Qwen 系列模型，但位于不同的端点。
:::

<a id="qwen-oauth-vs-dashscope-alibaba"></a>
### NVIDIA NIM {#nvidia-nim}

通过 [build.nvidia.com](https://build.nvidia.com)（免费 API key）或本地 NIM 端点使用 Nemotron 及其他开源模型。

```bash
# 云端 (build.nvidia.com)
hermes chat --provider nvidia --model nvidia/nemotron-3-super-120b-a12b
# 需要：在 ~/.hermes/.env 中设置 NVIDIA_API_KEY

# 本地 NIM 端点 —— 覆盖 base URL
NVIDIA_BASE_URL=http://localhost:8000/v1 hermes chat --provider nvidia --model nvidia/nemotron-3-super-120b-a12b
```

或在 `config.yaml` 中永久设置：
```yaml
model:
  provider: "nvidia"
  default: "nvidia/nemotron-3-super-120b-a12b"
```

:::tip 本地 NIM
对于本地部署（DGX Spark、本地 GPU），设置 `NVIDIA_BASE_URL=http://localhost:8000/v1`。NIM 暴露的 OpenAI 兼容聊天补全 API 与 build.nvidia.com 相同，因此云端和本地切换只需改一行环境变量。
:::
<a id="local-nim"></a>

### Hugging Face Inference Providers {#hugging-face-inference-providers}

[Hugging Face Inference Providers](https://huggingface.co/docs/inference-providers) 通过统一的 OpenAI 兼容端点（`router.huggingface.co/v1`）路由到 20 多个开源模型。请求会自动路由到最快的可用后端（Groq、Together、SambaNova 等），并支持自动故障转移。

```bash
# 使用任意可用模型
hermes chat --provider huggingface --model Qwen/Qwen3-235B-A22B-Thinking-2507
# 需要：在 ~/.hermes/.env 中设置 HF_TOKEN

# 短别名
hermes chat --provider hf --model deepseek-ai/DeepSeek-V3.2
```

或在 `config.yaml` 中永久设置：
```yaml
model:
  provider: "huggingface"
  default: "Qwen/Qwen3-235B-A22B-Thinking-2507"
```

在 [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) 获取你的 token —— 确保开启 "Make calls to Inference Providers" 权限。包含免费额度（每月 $0.10 额度，按提供商原价计费，不加价）。

你可以在模型名后追加路由后缀：`:fastest`（默认）、`:cheapest`，或 `:provider_name` 来强制指定后端。

可通过 `HF_BASE_URL` 覆盖 base URL。

## 自定义与自托管 LLM Provider {#custom-self-hosted-llm-providers}

Hermes Agent 支持**任何 OpenAI 兼容的 API 端点**。只要服务器实现了 `/v1/chat/completions`，你就可以让 Hermes 指向它。这意味着你可以使用本地模型、GPU 推理服务器、多提供商路由器，或任何第三方 API。

### 通用设置 {#general-setup}

三种配置自定义端点的方式：

**交互式设置（推荐）：**
```bash
hermes model
# 选择 "Custom endpoint (self-hosted / VLLM / etc.)"
# 输入：API base URL、API key、Model name
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
`.env` 中的 `OPENAI_BASE_URL` 和 `LLM_MODEL` 已**移除**。Hermes 的任何部分都不再读取这两个变量——`config.yaml` 是模型和端点配置的唯一定源。如果你的 `.env` 中还有残留条目，下次运行 `hermes setup` 或配置迁移时会自动清除。请使用 `hermes model` 命令或直接编辑 `config.yaml`。
<a id="legacy-env-vars"></a>

:::

两种方法都会持久化到 `config.yaml`，该文件是模型、提供商和 base URL 的唯一定源。

### 用 `/model` 切换模型 {#switching-models-with-model}

:::warning hermes model 与 /model 的区别
<a id="hermes-model-vs-model"></a>
**`hermes model`**（在终端中运行，不在任何聊天会话内）是**完整的提供商设置向导**。用它来添加新提供商、运行 OAuth 流程、输入 API 密钥、配置自定义端点。

**`/model`**（在活跃的 Hermes 聊天会话中输入）只能**在已设置好的提供商和模型之间切换**。它不能添加新提供商、运行 OAuth 或提示输入 API 密钥。如果你只配置了一个提供商（例如 OpenRouter），`/model` 只会显示该提供商的模型。

**要添加新提供商：** 退出当前会话（`Ctrl+C` 或 `/quit`），运行 `hermes model`，设置好新提供商，再开启新会话。
:::

至少配置好一个自定义端点后，你就可以在会话中途切换模型：

```
/model custom:qwen-2.5          # 切换到自定义端点上的某个模型
/model custom                    # 从端点自动检测模型
/model openrouter:claude-sonnet-4 # 切回云提供商
```

如果你配置了**具名自定义提供商**（见下文），使用三段式语法：

```
/model custom:local:qwen-2.5    # 使用名为 "local" 的自定义提供商，模型为 qwen-2.5
/model custom:work:llama3       # 使用名为 "work" 的自定义提供商，模型为 llama3
```

切换提供商时，Hermes 会将 base URL 和提供商持久化到配置中，以便重启后仍然生效。从自定义端点切换到内置提供商时，过期的 base URL 会自动清除。

:::tip
`/model custom`（裸写，不带模型名）会查询端点的 `/models` API，如果恰好只加载了一个模型，就自动选中。适合只跑单个模型的本地服务器。
:::

下面的内容都遵循相同的模式——只需改 URL、密钥和模型名即可。

---

### Ollama — 本地模型，零配置 {#ollama-local-models-zero-config}

[Ollama](https://ollama.com/) 一条命令就能在本地运行开源权重模型。最适合：快速本地实验、隐私敏感的工作、离线使用。通过兼容 OpenAI 的 API 支持工具调用。

```bash
# 安装并运行模型
ollama pull qwen2.5-coder:32b
ollama serve   # 在 11434 端口启动
```

然后配置 Hermes：

```bash
hermes model
# 选择 "Custom endpoint (self-hosted / VLLM / etc.)"
# 输入 URL: http://localhost:11434/v1
# 跳过 API 密钥（Ollama 不需要）
# 输入模型名（例如 qwen2.5-coder:32b）
```

或直接配置 `config.yaml`：

```yaml
model:
  default: qwen2.5-coder:32b
  provider: custom
  base_url: http://localhost:11434/v1
  context_length: 32768   # 见下方警告
```

<a id="ollama-defaults-to-very-low-context-lengths"></a>
:::caution Ollama 默认使用很低的上下文长度
Ollama **默认不会**使用模型的完整上下文窗口。具体默认值取决于你的显存：

| 可用显存 | 默认上下文长度 |
|----------|--------------|
| 小于 24 GB | **4,096 tokens** |
| 24–48 GB | 32,768 tokens |
| 48 GB 以上 | 256,000 tokens |

配合工具进行 Agent 使用时，**至少需要 16k–32k 上下文**。在 4k 下，系统提示词 + 工具模式就可能占满整个窗口，对话内容没地方放。

**提升方法**（任选其一）：

```bash
# 方案 1：通过环境变量全局设置（推荐）
OLLAMA_CONTEXT_LENGTH=32768 ollama serve

# 方案 2：针对 systemd 管理的 Ollama
sudo systemctl edit ollama.service
# 添加：Environment="OLLAMA_CONTEXT_LENGTH=32768"
# 然后执行：sudo systemctl daemon-reload && sudo systemctl restart ollama

# 方案 3：打包到自定义模型中（按模型持久化）
echo -e "FROM qwen2.5-coder:32b\nPARAMETER num_ctx 32768" > Modelfile
ollama create qwen2.5-coder-32k -f Modelfile
```
**你无法通过 OpenAI 兼容 API**（`/v1/chat/completions`）**设置上下文长度**。必须在服务端或通过 Modelfile 进行配置。这是将 Ollama 与 Hermes 等工具集成时最常见的困惑来源。
:::

**验证上下文是否设置正确：**

```bash
ollama ps
# 查看 CONTEXT 列 —— 它应该显示你配置的值
```

:::tip
用 `ollama list` 列出可用模型。用 `ollama pull &lt;model&gt;` 从 [Ollama 模型库](https://ollama.com/library) 拉取任意模型。Ollama 自动处理 GPU 卸载 —— 大多数场景无需额外配置。
:::

---

### vLLM — 高性能 GPU 推理 {#vllm-high-performance-gpu-inference}

[vLLM](https://docs.vllm.ai/) 是生产环境 LLM 服务的标准方案。最适合：GPU 硬件上的最大吞吐、大型模型服务、连续批处理。

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
# 输入模型名称: meta-llama/Llama-3.1-70B-Instruct
```

**上下文长度：** vLLM 默认读取模型的 `max_position_embeddings`。如果该值超出你的 GPU 显存，它会报错并要求你将 `--max-model-len` 设得更低。你也可以用 `--max-model-len auto` 自动寻找能容纳的最大值。设置 `--gpu-memory-utilization 0.95`（默认 0.9）可以把更多上下文塞进显存。

**Tool calling 需要显式指定标志：**

| 标志 | 用途 |
|------|---------|
| `--enable-auto-tool-choice` | `tool_choice: "auto"` 所需（Hermes 的默认值） |
| `--tool-call-parser &lt;name&gt;` | 模型 tool call 格式的解析器 |

支持的解析器：`hermes`（Qwen 2.5、Hermes 2/3）、`llama3_json`（Llama 3.x）、`mistral`、`deepseek_v3`、`deepseek_v31`、`xlam`、`pythonic`。没有这些标志，tool call 将无法工作 —— 模型会把 tool call 作为普通文本输出。

:::tip
vLLM 支持人类可读的大小写法：`--max-model-len 64k`（小写 k = 1000，大写 K = 1024）。
:::

---

### SGLang — 基于 RadixAttention 的快速服务 {#sglang-fast-serving-with-radixattention}

[SGLang](https://github.com/sgl-project/sglang) 是 vLLM 的替代方案，采用 RadixAttention 实现 KV cache 复用。最适合：多轮对话（前缀缓存）、约束解码、结构化输出。

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
# 输入 URL: http://localhost:30000/v1
# 输入模型名称: meta-llama/Llama-3.1-70B-Instruct
```

**上下文长度：** SGLang 默认从模型配置读取。用 `--context-length` 覆盖。如果你需要超出模型声明的最大值，设置 `SGLANG_ALLOW_OVERWRITE_LONGER_CONTEXT_LEN=1`。

**Tool calling：** 使用 `--tool-call-parser` 并选择适合你模型系列的解析器：`qwen`（Qwen 2.5）、`llama3`、`llama4`、`deepseekv3`、`mistral`、`glm`。没有这个标志，tool call 会以纯文本形式返回。

:::caution SGLang 默认最大输出 128 个 token
<a id="sglang-defaults-to-128-max-output-tokens"></a>
如果响应看起来被截断了，在请求中添加 `max_tokens`，或在服务端设置 `--default-max-tokens`。如果请求中未指定，SGLang 默认每个响应仅 128 个 token。
:::

---

### llama.cpp / llama-server — CPU 与 Metal 推理 {#llama-cpp-llama-server-cpu-metal-inference}

[llama.cpp](https://github.com/ggml-org/llama.cpp) 可在 CPU、Apple Silicon（Metal）和消费级 GPU 上运行量化模型。最适合：无需数据中心 GPU 运行模型、Mac 用户、边缘部署。

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
**上下文长度 (`-c`)：** 近期版本默认值为 `0`，会从 GGUF 元数据中读取模型的训练上下文长度。对于训练上下文在 128k 以上的模型，这可能导致分配完整 KV 缓存时内存溢出。建议显式设置 `-c` 为你需要的值（Agent 场景下 32k–64k 比较合适）。如果使用并行槽位 (`-np`)，总上下文会在各槽位之间均分 —— 使用 `-c 32768 -np 4` 时，每个槽位只有 8k。

然后配置 Hermes 指向该服务：

```bash
hermes model
# 选择 "Custom endpoint (self-hosted / VLLM / etc.)"
# 输入 URL: http://localhost:8080/v1
# 跳过 API key（本地服务器不需要）
# 输入模型名称 —— 如果仅加载了一个模型，也可以留空自动检测
```

这会将端点保存到 `config.yaml`，跨会话持久生效。

:::caution `--jinja` 是 tool calling 的必需参数
没有 `--jinja`，llama-server 会完全忽略 `tools` 参数。模型会尝试通过在响应文本中写 JSON 来调用工具，但 Hermes 不会将其识别为工具调用 —— 你会看到类似 `{"name": "web_search", ...}` 的原始 JSON 被当作消息打印出来，而不是真正执行搜索。

<a id="jinja-is-required-for-tool-calling"></a>
原生 tool calling 支持（最佳性能）：Llama 3.x、Qwen 2.5（含 Coder）、Hermes 2/3、Mistral、DeepSeek、Functionary。其他模型使用通用处理程序，可以工作但效率可能较低。完整列表参见 [llama.cpp function calling 文档](https://github.com/ggml-org/llama.cpp/blob/master/docs/function-calling.md)。

你可以通过检查 `http://localhost:8080/props` 验证 tool 支持是否已激活 —— `chat_template` 字段应当存在。
:::

:::tip
从 [Hugging Face](https://huggingface.co/models?library=gguf) 下载 GGUF 模型。Q4_K_M 量化在质量与内存占用之间取得了最佳平衡。
:::

---

### LM Studio —— 带图形界面的本地模型桌面应用 {#lm-studio-desktop-app-with-local-models}

[LM Studio](https://lmstudio.ai/) 是一款用于运行本地模型的桌面应用，提供图形界面。最适合：喜欢可视化界面的用户、快速测试模型、macOS/Windows/Linux 上的开发者。

从 LM Studio 应用启动服务器（Developer 标签页 → Start Server），或使用命令行：

```bash
lms server start                        # 在 1234 端口启动
lms load qwen2.5-coder --context-length 32768
```

然后配置 Hermes：

```bash
hermes model
# 选择 "Custom endpoint (self-hosted / VLLM / etc.)"
# 输入 URL: http://localhost:1234/v1
# 跳过 API key（LM Studio 不需要）
# 输入模型名称
```

:::caution 上下文长度通常默认为 2048
LM Studio 从模型元数据读取上下文长度，但很多 GGUF 模型报告的值偏低（2048 或 4096）。**务必在 LM Studio 模型设置中显式设置上下文长度**：
<a id="context-length-often-defaults-to-2048"></a>

1. 点击模型选择器旁的齿轮图标
2. 将 "Context Length" 设为至少 16384（建议 32768）
3. 重新加载模型使更改生效

或者使用命令行：`lms load model-name --context-length 32768`

要设置持久的单模型默认值：My Models 标签页 → 模型上的齿轮图标 → 设置 context size。
:::

**Tool calling：** LM Studio 0.3.6 起支持。具有原生 tool-calling 训练的模型（Qwen 2.5、Llama 3.x、Mistral、Hermes）会被自动检测并显示 tool 徽章。其他模型使用通用降级方案，可靠性可能较低。

---

### WSL2 网络配置（Windows 用户） {#wsl2-networking-windows-users}

由于 Hermes Agent 需要 Unix 环境，Windows 用户在 WSL2 内运行。如果你的模型服务器（Ollama、LM Studio 等）运行在 **Windows 宿主机** 上，需要打通网络 —— WSL2 使用独立的虚拟网卡和子网，因此 WSL2 内的 `localhost` 指的是 Linux 虚拟机，**而不是** Windows 宿主机。

:::tip 都在 WSL2 里？没问题。
<a id="both-in-wsl2-no-problem"></a>
如果你的模型服务器也运行在 WSL2 内（vLLM、SGLang 和 llama-server 常见这种情况），`localhost` 可以正常工作 —— 它们共享同一网络命名空间。跳过本节。
:::

#### 方案 1：镜像网络模式（推荐） {#option-1-mirrored-networking-mode-recommended}

**Windows 11 22H2+** 可用，镜像模式让 `localhost` 在 Windows 和 WSL2 之间双向互通 —— 最简单的解决办法。
1. 创建或编辑 `%USERPROFILE%\.wslconfig`（例如 `C:\Users\YourName\.wslconfig`）：
   ```ini
   [wsl2]
   networkingMode=mirrored
   ```

2. 在 PowerShell 中重启 WSL：
   ```powershell
   wsl --shutdown
   ```

3. 重新打开 WSL2 终端。此时 `localhost` 可以访问 Windows 服务了：
   ```bash
   curl http://localhost:11434/v1/models   # Windows 上的 Ollama — 可以访问
   ```

:::note Hyper-V 防火墙
在某些 Windows 11 版本中，Hyper-V 防火墙默认会阻止镜像连接。如果启用镜像模式后 `localhost` 仍然无法使用，请在**管理员 PowerShell** 中运行：
```powershell
Set-NetFirewallHyperVVMSetting -Name '{40E0AC32-46A5-438A-A0B2-2B479E8F2E90}' -DefaultInboundAction Allow
```
:::
<a id="hyper-v-firewall"></a>

#### 方案 2：使用 Windows 主机 IP（Windows 10 / 旧版本） {#option-2-use-the-windows-host-ip-windows-10-older-builds}

如果无法使用镜像模式，可以在 WSL2 内部找到 Windows 主机的 IP，然后用它代替 `localhost`：

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

:::tip 动态获取 helper
WSL2 重启后主机 IP 可能会变。你可以在 shell 中动态获取：
```bash
export WSL_HOST=$(ip route show | grep -i default | awk '{ print $3 }')
echo "Windows host at: $WSL_HOST"
<a id="dynamic-helper"></a>
curl http://$WSL_HOST:11434/v1/models   # 测试 Ollama
```

或者使用你机器的 mDNS 名称（WSL2 中需要安装 `libnss-mdns`）：
```bash
sudo apt install libnss-mdns
curl http://$(hostname).local:11434/v1/models
```
:::

#### 服务器绑定地址（NAT 模式必需） {#server-bind-address-required-for-nat-mode}

如果你使用**方案 2**（NAT 模式 + 主机 IP），Windows 上的模型服务器必须接受来自 `127.0.0.1` 外部的连接。默认情况下，大多数服务器只监听 localhost —— NAT 模式下 WSL2 的连接来自另一个虚拟子网，会被拒绝。在镜像模式下，`localhost` 直接映射，所以默认的 `127.0.0.1` 绑定就能正常工作。

| 服务器 | 默认绑定 | 解决方法 |
|--------|---------|---------|
| **Ollama** | `127.0.0.1` | 启动 Ollama 前设置环境变量 `OLLAMA_HOST=0.0.0.0`（Windows 系统设置 → 环境变量，或编辑 Ollama 服务） |
| **LM Studio** | `127.0.0.1` | 在 Developer 标签页 → Server settings 中启用 **"Serve on Network"** |
| **llama-server** | `127.0.0.1` | 在启动命令中添加 `--host 0.0.0.0` |
| **vLLM** | `0.0.0.0` | 默认已绑定到所有接口 |
| **SGLang** | `127.0.0.1` | 在启动命令中添加 `--host 0.0.0.0` |

**Windows 上的 Ollama（详细说明）：** Ollama 以 Windows 服务形式运行。设置 `OLLAMA_HOST` 的步骤：
1. 打开**系统属性** → **环境变量**
2. 添加一个新的**系统变量**：`OLLAMA_HOST` = `0.0.0.0`
3. 重启 Ollama 服务（或重启电脑）

#### Windows 防火墙 {#windows-firewall}

Windows 防火墙将 WSL2 视为独立的网络（NAT 和镜像模式都是如此）。如果完成上述步骤后连接仍然失败，请为模型服务器的端口添加防火墙规则：

```powershell
# 在管理员 PowerShell 中运行 —— 将 PORT 替换为你服务器的端口
New-NetFirewallRule -DisplayName "Allow WSL2 to Model Server" -Direction Inbound -Action Allow -Protocol TCP -LocalPort 11434
```

常见端口：Ollama `11434`、vLLM `8000`、SGLang `30000`、llama-server `8080`、LM Studio `1234`。

#### 快速验证 {#quick-verification}

在 WSL2 内部测试能否访问你的模型服务器：

```bash
# 将 URL 替换为你服务器的地址和端口
curl http://localhost:11434/v1/models          # 镜像模式
curl http://172.29.192.1:11434/v1/models       # NAT 模式（使用你实际的主机 IP）
```

如果能收到列出模型的 JSON 响应，就说明没问题了。在 Hermes 配置中使用相同的 URL 作为 `base_url`。

---

### 本地模型故障排查 {#troubleshooting-local-models}

这些问题会影响 Hermes 使用**所有**本地推理服务器时的情况。

#### 从 WSL2 连接 Windows 上的模型服务器时出现 "Connection refused" {#connection-refused-from-wsl2-to-a-windows-hosted-model-server}
如果你在 WSL2 里运行 Hermes，而模型服务器跑在 Windows 宿主机上，WSL2 默认的 NAT 网络模式下 `http://localhost:&lt;port&gt;` 是连不通的。修复方法见上文 [WSL2 网络问题](#wsl2-networking-windows-users)。

#### 工具调用显示为文本，没有实际执行 {#tool-calls-appear-as-text-instead-of-executing}

模型输出类似 `{"name": "web_search", "arguments": {...}}` 这样的消息，但并没有真正调用工具。

**原因：** 你的服务器没有启用工具调用功能，或者该模型不支持服务器当前的工具调用实现方式。

| 服务器 | 修复方法 |
|--------|---------|
| **llama.cpp** | 启动命令加上 `--jinja` |
| **vLLM** | 加上 `--enable-auto-tool-choice --tool-call-parser hermes` |
| **SGLang** | 加上 `--tool-call-parser qwen`（或其他合适的解析器） |
| **Ollama** | 工具调用默认已启用——确认你的模型支持该功能（用 `ollama show model-name` 检查） |
| **LM Studio** | 升级到 0.3.6+，并使用原生支持工具的模型 |

#### 模型似乎忘记上下文，或回答不连贯 {#model-seems-to-forget-context-or-give-incoherent-responses}

**原因：** 上下文窗口太小。对话超过上下文限制后，大多数服务器会静默丢弃较早的消息。Hermes 的系统提示词 + 工具 schema 本身就可能占用 4k–8k token。

**排查方法：**

```bash
# 查看 Hermes 认为上下文是多少
# 看启动日志里的这一行："Context limit: X tokens"

# 查看服务器的实际上下文设置
# Ollama: ollama ps（看 CONTEXT 列）
# llama.cpp: curl http://localhost:8080/props | jq '.default_generation_settings.n_ctx'
# vLLM: 检查启动参数里的 --max-model-len
```

**修复：** Agent 使用场景下，上下文至少设置为 **32,768 token**。各服务器的具体参数见上文对应章节。

#### 启动时显示 "Context limit: 2048 tokens" {#context-limit-2048-tokens-at-startup}

Hermes 会自动从服务器的 `/v1/models` 端点探测上下文长度。如果服务器返回的值很低（或者根本没返回），Hermes 就会采用模型声明的限制，而这个值可能是错的。

**修复：** 在 `config.yaml` 里显式指定：

```yaml
model:
  default: your-model
  provider: custom
  base_url: http://localhost:11434/v1
  context_length: 32768
```

#### 回复说到一半就断了 {#responses-get-cut-off-mid-sentence}

**可能的原因：**

1. **服务器的输出上限（`max_tokens`）太低** —— SGLang 默认每次回复最多 128 个 token。可以在服务器端设置 `--default-max-tokens`，或在 Hermes 的 config.yaml 里配置 `model.max_tokens`。注意：`max_tokens` 只控制单次回复长度，跟对话历史能有多长没关系（那个是 `context_length` 控制的）。
2. **上下文耗尽** —— 模型填满了上下文窗口。增大 `model.context_length`，或在 Hermes 中开启[上下文压缩](/user-guide/configuration#context-compression)。

---

### LiteLLM Proxy — 多供应商网关 {#litellm-proxy-multi-provider-gateway}

[LiteLLM](https://docs.litellm.ai/) 是一个兼容 OpenAI API 的代理，能把 100 多个 LLM 供应商统一成一套接口。最适合这些场景：无需改配置就能切换供应商、负载均衡、故障自动 fallback、预算控制。

```bash
# 安装并启动
pip install "litellm[proxy]"
litellm --model anthropic/claude-sonnet-4 --port 4000

# 或者用配置文件启动多模型：
litellm --config litellm_config.yaml --port 4000
```

然后在 Hermes 里执行 `hermes model` → Custom endpoint → 填入 `http://localhost:4000/v1`。

带 fallback 的 `litellm_config.yaml` 示例：
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

BlockRunAI 开发的 [ClawRouter](https://github.com/BlockRunAI/ClawRouter) 是一个本地路由代理，能根据查询复杂度自动选择模型。它会从 14 个维度对请求分类，然后路由到能胜任任务的最低成本模型。通过 USDC 加密货币付费（不需要 API key）。

```bash
# 安装并启动
npx @blockrun/clawrouter    # 默认在 8402 端口启动
```
然后用 `hermes model` → Custom endpoint → `http://localhost:8402/v1` → 模型名称 `blockrun/auto` 来配置 Hermes。

路由配置：
| 配置 | 策略 | 节省 |
|---------|----------|---------|
| `blockrun/auto` | 质量/成本平衡 | 74-100% |
| `blockrun/eco` | 最低成本 | 95-100% |
| `blockrun/premium` | 最佳质量模型 | 0% |
| `blockrun/free` | 仅免费模型 | 100% |
| `blockrun/agentic` | 针对工具使用优化 | 视情况而定 |

:::note
ClawRouter 需要在 Base 或 Solana 上有一个充值 USDC 的钱包用于付款。所有请求都通过 BlockRun 的后端 API 路由。运行 `npx @blockrun/clawrouter doctor` 可检查钱包状态。
:::

---

### 其他兼容的提供商 {#other-compatible-providers}

任何提供 OpenAI 兼容 API 的服务都可以使用。一些热门选项：

| 提供商 | Base URL | 说明 |
|----------|----------|-------|
| [Together AI](https://together.ai) | `https://api.together.xyz/v1` | 云端托管的开源模型 |
| [Groq](https://groq.com) | `https://api.groq.com/openai/v1` | 超快推理 |
| [DeepSeek](https://deepseek.com) | `https://api.deepseek.com/v1` | DeepSeek 模型 |
| [Fireworks AI](https://fireworks.ai) | `https://api.fireworks.ai/inference/v1` | 快速开源模型托管 |
| [Cerebras](https://cerebras.ai) | `https://api.cerebras.ai/v1` | 晶圆级芯片推理 |
| [Mistral AI](https://mistral.ai) | `https://api.mistral.ai/v1` | Mistral 模型 |
| [OpenAI](https://openai.com) | `https://api.openai.com/v1` | 直接访问 OpenAI |
| [Azure OpenAI](https://azure.microsoft.com) | `https://YOUR.openai.azure.com/` | 企业级 OpenAI |
| [LocalAI](https://localai.io) | `http://localhost:8080/v1` | 自托管，多模型 |
| [Jan](https://jan.ai) | `http://localhost:1337/v1` | 带本地模型的桌面应用 |

以上任意一个都可以用 `hermes model` → Custom endpoint 配置，或者在 `config.yaml` 中设置：

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
:::note 两个设置，容易搞混
**`context_length`** 是**总上下文窗口**——输入和输出 token 的合计预算（例如 Claude Opus 4.6 是 200,000）。Hermes 用它来决定何时压缩历史记录，以及验证 API 请求。

**`model.max_tokens`** 是**输出上限**——模型在*单次响应*中最多能生成的 token 数。它跟你的对话历史能有多长完全没关系。`max_tokens` 这个业界通用的名字很容易让人困惑；Anthropic 的原生 API 后来已经把它改名为 `max_output_tokens` 来避免歧义。

当自动检测把窗口大小搞错时，设置 `context_length`。
只有当你需要限制单次回复最长能有多少时，才设置 `model.max_tokens`。
:::

Hermes 使用多源解析链来检测你的模型和提供商的正确上下文窗口：

1. **配置覆盖** — `config.yaml` 中的 `model.context_length`（最高优先级）
2. **自定义提供商单模型** — `custom_providers[].models.&lt;id&gt;.context_length`
3. **持久缓存** — 之前发现的值（重启后仍然保留）
4. **端点 `/models`** — 查询你的服务器 API（本地/自定义端点）
5. **Anthropic `/v1/models`** — 查询 Anthropic API 获取 `max_input_tokens`（仅限 API key 用户）
6. **OpenRouter API** — OpenRouter 的实时模型元数据
7. **Nous Portal** — 用后缀匹配 Nous 模型 ID 与 OpenRouter 元数据
8. **[models.dev](https://models.dev)** — 社区维护的注册表，包含 3800+ 模型、100+ 提供商的提供商专属上下文长度
9. **兜底默认值** — 宽泛的模型家族模式（默认 128K）

大多数场景下开箱即用。这个系统是提供商感知的——同一个模型在不同提供商那里可能有不同的上下文限制（例如 `claude-opus-4.6` 在 Anthropic 直连是 1M，但在 GitHub Copilot 上是 128K）。

要显式设置上下文长度，在你的模型配置中添加 `context_length`：
```yaml
model:
  default: "qwen3.5:9b"
  base_url: "http://localhost:8080/v1"
  context_length: 131072  # tokens
```

对于自定义端点，你也可以按模型设置上下文长度：

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

`hermes model` 在配置自定义端点时会提示输入上下文长度。留空即可自动检测。

:::tip 什么时候需要手动设置
- 你使用 Ollama，且自定义的 `num_ctx` 低于模型上限
- 你想限制上下文长度低于模型上限（比如在 128k 的模型上限制为 8k 以节省显存）
- 你运行在不会暴露 `/v1/models` 的代理后面
<a id="when-to-set-this-manually"></a>
:::

---

### 命名自定义 Provider {#named-custom-providers}

如果你同时使用多个自定义端点（比如本地开发服务器和远程 GPU 服务器），可以在 `config.yaml` 中将它们定义为命名自定义 Provider：

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

会话中随时可以用三段式语法切换：

```
/model custom:local:qwen-2.5       # 使用 "local" 端点和 qwen-2.5
/model custom:work:llama3-70b      # 使用 "work" 端点和 llama3-70b
/model custom:anthropic-proxy:claude-sonnet-4  # 使用代理
```

你也可以在交互式的 `hermes model` 菜单中选择命名自定义 Provider。

---

### 如何选择合适的配置 {#choosing-the-right-setup}

| 使用场景 | 推荐方案 |
|----------|----------|
| **只想快速跑起来** | OpenRouter（默认）或 Nous Portal |
| **本地模型，简单部署** | Ollama |
| **生产级 GPU 推理** | vLLM 或 SGLang |
| **Mac / 无 GPU** | Ollama 或 llama.cpp |
| **多 Provider 路由** | LiteLLM Proxy 或 OpenRouter |
| **成本优化** | ClawRouter 或带 `sort: "price"` 的 OpenRouter |
| **极致隐私** | Ollama、vLLM 或 llama.cpp（完全本地） |
| **企业 / Azure** | 带自定义端点的 Azure OpenAI |
| **中文 AI 模型** | z.ai（GLM）、Kimi/Moonshot（`kimi-coding` 或 `kimi-coding-cn`）、MiniMax 或 Xiaomi MiMo（一级 Provider） |

:::tip
你可以随时用 `hermes model` 切换 Provider，无需重启。无论使用哪个 Provider，对话历史、记忆和技能都会保留。
:::

## 可选 API 密钥 {#optional-api-keys}

| 功能 | Provider | 环境变量 |
|---------|----------|--------------|
| 网页抓取 | [Firecrawl](https://firecrawl.dev/) | `FIRECRAWL_API_KEY`, `FIRECRAWL_API_URL` |
| 浏览器自动化 | [Browserbase](https://browserbase.com/) | `BROWSERBASE_API_KEY`, `BROWSERBASE_PROJECT_ID` |
| 图像生成 | [FAL](https://fal.ai/) | `FAL_KEY` |
| 高级 TTS 语音 | [ElevenLabs](https://elevenlabs.io/) | `ELEVENLABS_API_KEY` |
| OpenAI TTS + 语音转录 | [OpenAI](https://platform.openai.com/api-keys) | `VOICE_TOOLS_OPENAI_KEY` |
| Mistral TTS + 语音转录 | [Mistral](https://console.mistral.ai/) | `MISTRAL_API_KEY` |
| RL 训练 | [Tinker](https://tinker-console.thinkingmachines.ai/) + [WandB](https://wandb.ai/) | `TINKER_API_KEY`, `WANDB_API_KEY` |
| 跨会话用户建模 | [Honcho](https://honcho.dev/) | `HONCHO_API_KEY` |
| 语义化长期记忆 | [Supermemory](https://supermemory.ai) | `SUPERMEMORY_API_KEY` |

### 自建 Firecrawl {#self-hosting-firecrawl}

默认情况下，Hermes 使用 [Firecrawl 云 API](https://firecrawl.dev/) 进行网页搜索和抓取。如果你希望在本地运行 Firecrawl，可以将 Hermes 指向自建实例。完整的搭建说明请参考 Firecrawl 的 [SELF_HOST.md](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md)。
**你能得到的：** 无需 API 密钥、没有速率限制、没有按页计费、完全的数据主权。

**你会失去的：** 云端版本使用 Firecrawl 专有的 "Fire-engine" 来进行高级反爬虫绕过（Cloudflare、CAPTCHA、IP 轮换）。自托管版本使用基础的 fetch + Playwright，因此某些受保护的网站可能会抓取失败。搜索使用 DuckDuckGo 而非 Google。

**设置步骤：**

1. 克隆并启动 Firecrawl Docker 堆栈（5 个容器：API、Playwright、Redis、RabbitMQ、PostgreSQL — 需要约 4-8 GB 内存）：
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

如果你的自托管实例启用了认证，也可以同时设置 `FIRECRAWL_API_KEY` 和 `FIRECRAWL_API_URL`。

## OpenRouter Provider 路由 {#openrouter-provider-routing}

使用 OpenRouter 时，你可以控制请求如何在不同 Provider 之间路由。在 `~/.hermes/config.yaml` 中添加 `provider_routing` 配置节：

```yaml
provider_routing:
  sort: "throughput"          # "price"（默认）、"throughput" 或 "latency"
  # only: ["anthropic"]      # 只使用这些 Provider
  # ignore: ["deepinfra"]    # 跳过这些 Provider
  # order: ["anthropic", "google"]  # 按此顺序尝试 Provider
  # require_parameters: true  # 只使用支持所有请求参数的 Provider
  # data_collection: "deny"   # 排除可能存储/训练数据的 Provider
```

**快捷方式：** 在任何模型名称后追加 `:nitro` 即可按吞吐量排序（例如 `anthropic/claude-sonnet-4:nitro`），或追加 `:floor` 按价格排序。

## 备用模型 {#fallback-model}

配置一个备用的 provider:model，当主模型失败时（速率限制、服务器错误、认证失败），Hermes 会自动切换过去：

```yaml
fallback_model:
  provider: openrouter                    # 必填
  model: anthropic/claude-sonnet-4        # 必填
  # base_url: http://localhost:8000/v1    # 可选，用于自定义端点
  # key_env: MY_CUSTOM_KEY               # 可选，自定义端点 API 密钥的环境变量名
```

激活后，备用模型会在会话中途切换模型和 Provider，而不会丢失对话内容。每个会话**最多触发一次**。

支持的 Provider：`openrouter`、`nous`、`openai-codex`、`copilot`、`copilot-acp`、`anthropic`、`gemini`、`google-gemini-cli`、`qwen-oauth`、`huggingface`、`zai`、`kimi-coding`、`kimi-coding-cn`、`minimax`、`minimax-cn`、`deepseek`、`nvidia`、`xai`、`ollama-cloud`、`bedrock`、`ai-gateway`、`opencode-zen`、`opencode-go`、`kilocode`、`xiaomi`、`arcee`、`alibaba`、`custom`。

:::tip
备用模型只能通过 `config.yaml` 配置，没有对应的环境变量。关于触发条件、支持的 Provider、以及与辅助任务和委托的交互方式的完整详情，请参阅 [Fallback Providers](/user-guide/features/fallback-providers)。
:::

## 智能模型路由 {#smart-model-routing}

可选的"便宜 vs 强力"路由功能让 Hermes 将主模型留给复杂任务，而把非常短/简单的轮次发给更便宜的模型。

```yaml
smart_model_routing:
  enabled: true
  max_simple_chars: 160
  max_simple_words: 28
  cheap_model:
    provider: openrouter
    model: google/gemini-2.5-flash
    # base_url: http://localhost:8000/v1  # 可选的自定义端点
    # key_env: MY_CUSTOM_KEY              # 可选的该端点 API 密钥环境变量名
```

工作原理：
- 如果一轮对话很短、只有单行，且看起来不涉及代码/工具/调试，Hermes 可能会将其路由到 `cheap_model`
- 如果一轮对话看起来比较复杂，Hermes 会留在你的主模型/Provider 上
- 如果便宜的路由无法干净利落地完成，Hermes 会自动回退到主模型

这个机制故意设计得很保守。它适用于快速、低风险的轮次，例如：
- 简短的事实性问题
- 快速改写
- 轻量摘要

它会避免路由看起来像是以下类型的提示：
- 编码/调试工作
- 重度依赖工具的请求
- 长文本或多行分析请求
当你想降低延迟或成本，又不想完全更换默认模型时，可以使用这种方式。

---

## 另请参阅 {#see-also}

- [配置](/user-guide/configuration) — 通用配置（目录结构、配置优先级、终端后端、内存、压缩等）
- [环境变量](/reference/environment-variables) — 所有环境变量的完整参考
