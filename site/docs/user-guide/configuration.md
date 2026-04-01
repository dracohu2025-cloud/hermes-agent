---
sidebar_position: 2
title: "配置"
description: "配置 Hermes Agent — config.yaml、提供商、模型、API 密钥等"
---

# 配置

所有设置都存储在 `~/.hermes/` 目录中，便于访问。

## 目录结构

```text
~/.hermes/
├── config.yaml     # 设置（模型、终端、TTS、压缩等）
├── .env            # API 密钥和密钥
├── auth.json       # OAuth 提供商凭据（Nous Portal 等）
├── SOUL.md         # 主要 Agent 身份（系统提示词中的槽位 #1）
├── memories/       # 持久化记忆（MEMORY.md, USER.md）
├── skills/         # Agent 创建的技能（通过 skill_manage 工具管理）
├── cron/           # 计划任务
├── sessions/       # 网关会话
└── logs/           # 日志（errors.log, gateway.log — 密钥自动脱敏）
```

## 管理配置

```bash
hermes config              # 查看当前配置
hermes config edit         # 在编辑器中打开 config.yaml
hermes config set KEY VAL  # 设置特定值
hermes config check        # 检查缺失的选项（更新后）
hermes config migrate      # 交互式添加缺失的选项

# 示例：
hermes config set model anthropic/claude-opus-4
hermes config set terminal.backend docker
hermes config set OPENROUTER_API_KEY sk-or-...  # 保存到 .env
```

:::tip
`hermes config set` 命令会自动将值路由到正确的文件 — API 密钥保存到 `.env`，其他所有内容保存到 `config.yaml`。
:::

## 配置优先级

设置按以下顺序解析（优先级从高到低）：

1.  **CLI 参数** — 例如，`hermes chat --model anthropic/claude-sonnet-4`（每次调用覆盖）
2.  **`~/.hermes/config.yaml`** — 所有非密钥设置的主要配置文件
3.  **`~/.hermes/.env`** — 环境变量的后备；**必需**用于密钥（API 密钥、令牌、密码）
4.  **内置默认值** — 当没有其他设置时，硬编码的安全默认值

:::info 经验法则
密钥（API 密钥、机器人令牌、密码）放在 `.env` 中。其他所有内容（模型、终端后端、压缩设置、内存限制、工具集）放在 `config.yaml` 中。当两者都设置时，对于非密钥设置，`config.yaml` 优先。
:::

## 环境变量替换

你可以在 `config.yaml` 中使用 `${VAR_NAME}` 语法引用环境变量：

```yaml
auxiliary:
  vision:
    api_key: ${GOOGLE_API_KEY}
    base_url: ${CUSTOM_VISION_URL}

delegation:
  api_key: ${DELEGATION_KEY}
```

单个值中支持多个引用：`url: "${HOST}:${PORT}"`。如果引用的变量未设置，占位符将按字面保留（`${UNDEFINED_VAR}` 保持不变）。仅支持 `${VAR}` 语法 — 裸 `$VAR` 不会被展开。

## 推理提供商

你至少需要一种连接到 LLM 的方式。使用 `hermes model` 交互式切换提供商和模型，或直接配置：

| 提供商 | 设置 |
|----------|-------|
| **Nous Portal** | `hermes model` (OAuth，基于订阅) |
| **OpenAI Codex** | `hermes model` (ChatGPT OAuth，使用 Codex 模型) |
| **GitHub Copilot** | `hermes model` (OAuth 设备代码流，`COPILOT_GITHUB_TOKEN`、`GH_TOKEN` 或 `gh auth token`) |
| **GitHub Copilot ACP** | `hermes model` (生成本地 `copilot --acp --stdio`) |
| **Anthropic** | `hermes model` (通过 Claude Code 身份验证使用 Claude Pro/Max，Anthropic API 密钥，或手动设置令牌) |
| **OpenRouter** | 在 `~/.hermes/.env` 中设置 `OPENROUTER_API_KEY` |
| **AI Gateway** | 在 `~/.hermes/.env` 中设置 `AI_GATEWAY_API_KEY` (提供商：`ai-gateway`) |
| **z.ai / GLM** | 在 `~/.hermes/.env` 中设置 `GLM_API_KEY` (提供商：`zai`) |
| **Kimi / Moonshot** | 在 `~/.hermes/.env` 中设置 `KIMI_API_KEY` (提供商：`kimi-coding`) |
| **MiniMax** | 在 `~/.hermes/.env` 中设置 `MINIMAX_API_KEY` (提供商：`minimax`) |
| **MiniMax 中国** | 在 `~/.hermes/.env` 中设置 `MINIMAX_CN_API_KEY` (提供商：`minimax-cn`) |
| **阿里云** | 在 `~/.hermes/.env` 中设置 `DASHSCOPE_API_KEY` (提供商：`alibaba`，别名：`dashscope`，`qwen`) |
| **Kilo Code** | 在 `~/.hermes/.env` 中设置 `KILOCODE_API_KEY` (提供商：`kilocode`) |
| **OpenCode Zen** | 在 `~/.hermes/.env` 中设置 `OPENCODE_ZEN_API_KEY` (提供商：`opencode-zen`) |
| **OpenCode Go** | 在 `~/.hermes/.env` 中设置 `OPENCODE_GO_API_KEY` (提供商：`opencode-go`) |
| **Hugging Face** | 在 `~/.hermes/.env` 中设置 `HF_TOKEN` (提供商：`huggingface`，别名：`hf`) |
| **自定义端点** | `hermes model` (保存在 `config.yaml` 中) 或 `OPENAI_BASE_URL` + `OPENAI_API_KEY` 在 `~/.hermes/.env` 中 |

:::tip 模型键别名
在 `model:` 配置部分，你可以使用 `default:` 或 `model:` 作为模型 ID 的键名。`model: { default: my-model }` 和 `model: { model: my-model }` 效果相同。
:::

:::info Codex 说明
OpenAI Codex 提供商通过设备代码进行身份验证（打开 URL，输入代码）。Hermes 将生成的凭据存储在其自己的身份验证存储中，位于 `~/.hermes/auth.json`，并且当存在时可以从 `~/.codex/auth.json` 导入现有的 Codex CLI 凭据。无需安装 Codex CLI。
:::

:::warning
即使使用 Nous Portal、Codex 或自定义端点，一些工具（视觉、网页摘要、MoA）也会使用单独的“辅助”模型 — 默认通过 OpenRouter 使用 Gemini Flash。设置 `OPENROUTER_API_KEY` 会自动启用这些工具。你也可以配置这些工具使用哪个模型和提供商 — 请参阅下面的[辅助模型](#auxiliary-models)。
:::

### Anthropic（原生）

直接通过 Anthropic API 使用 Claude 模型 — 无需 OpenRouter 代理。支持三种身份验证方法：

```bash
# 使用 API 密钥（按令牌付费）
export ANTHROPIC_API_KEY=***
hermes chat --provider anthropic --model claude-sonnet-4-6

# 首选：通过 `hermes model` 进行身份验证
# Hermes 在可用时将直接使用 Claude Code 的凭据存储
hermes model

# 使用设置令牌手动覆盖（后备 / 旧版）
export ANTHROPIC_TOKEN=***  # setup-token 或手动 OAuth 令牌
hermes chat --provider anthropic

# 自动检测 Claude Code 凭据（如果你已使用 Claude Code）
hermes chat --provider anthropic  # 自动读取 Claude Code 凭据文件
```

当你通过 `hermes model` 选择 Anthropic OAuth 时，Hermes 优先使用 Claude Code 自己的凭据存储，而不是将令牌复制到 `~/.hermes/.env`。这使可刷新的 Claude 凭据保持可刷新。

或永久设置：
```yaml
model:
  provider: "anthropic"
  default: "claude-sonnet-4-6"
```

:::tip 别名
`--provider claude` 和 `--provider claude-code` 也可以作为 `--provider anthropic` 的简写。
:::

### GitHub Copilot

Hermes 将 GitHub Copilot 作为一等提供商支持，有两种模式：

**`copilot` — 直接 Copilot API**（推荐）。使用你的 GitHub Copilot 订阅通过 Copilot API 访问 GPT-5.x、Claude、Gemini 和其他模型。

```bash
hermes chat --provider copilot --model gpt-5.4
```

**身份验证选项**（按此顺序检查）：

1.  `COPILOT_GITHUB_TOKEN` 环境变量
2.  `GH_TOKEN` 环境变量
3.  `GITHUB_TOKEN` 环境变量
4.  `gh auth token` CLI 后备

如果未找到令牌，`hermes model` 会提供 **OAuth 设备代码登录** — 与 Copilot CLI 和 opencode 使用的流程相同。

:::warning 令牌类型
Copilot API **不**支持经典的个人访问令牌 (`ghp_*`)。支持的令牌类型：

| 类型 | 前缀 | 如何获取 |
|------|--------|------------|
| OAuth 令牌 | `gho_` | `hermes model` → GitHub Copilot → 使用 GitHub 登录 |
| 细粒度 PAT | `github_pat_` | GitHub 设置 → 开发者设置 → 细粒度令牌（需要 **Copilot 请求** 权限） |
| GitHub App 令牌 | `ghu_` | 通过 GitHub App 安装 |

如果你的 `gh auth token` 返回 `ghp_*` 令牌，请改用 `hermes model` 通过 OAuth 进行身份验证。
:::

**API 路由**：GPT-5+ 模型（除了 `gpt-5-mini`）自动使用 Responses API。所有其他模型（GPT-4o、Claude、Gemini 等）使用 Chat Completions。模型从实时 Copilot 目录中自动检测。

**`copilot-acp` — Copilot ACP Agent 后端**。将本地 Copilot CLI 作为子进程生成：

```bash
hermes chat --provider copilot-acp --model copilot-acp
# 需要 PATH 中有 GitHub Copilot CLI 和现有的 `copilot login` 会话
```

**永久配置：**
```yaml
model:
  provider: "copilot"
  default: "gpt-5.4"
```

| 环境变量 | 描述 |
|---------------------|-------------|
| `COPILOT_GITHUB_TOKEN` | Copilot API 的 GitHub 令牌（最高优先级） |
| `HERMES_COPILOT_ACP_COMMAND` | 覆盖 Copilot CLI 二进制路径（默认：`copilot`） |
| `HERMES_COPILOT_ACP_ARGS` | 覆盖 ACP 参数（默认：`--acp --stdio`） |

### 一等中文 AI 提供商

这些提供商具有内置支持，拥有专用的提供商 ID。设置 API 密钥并使用 `--provider` 进行选择：

```bash
# z.ai / 智谱 AI GLM
hermes chat --provider zai --model glm-4-plus
# 需要：在 ~/.hermes/.env 中设置 GLM_API_KEY

# Kimi / Moonshot AI
hermes chat --provider kimi-coding --model moonshot-v1-auto
# 需要：在 ~/.hermes/.env 中设置 KIMI_API_KEY

# MiniMax（全球端点）
hermes chat --provider minimax --model MiniMax-M2.7
# 需要：在 ~/.hermes/.env 中设置 MINIMAX_API_KEY

# MiniMax（中国端点）
hermes chat --provider minimax-cn --model MiniMax-M2.7
# 需要：在 ~/.hermes/.env 中设置 MINIMAX_CN_API_KEY

# 阿里云 / DashScope（通义千问模型）
hermes chat --provider alibaba --model qwen3.5-plus
# 需要：在 ~/.hermes/.env 中设置 DASHSCOPE_API_KEY
```

或在 `config.yaml` 中永久设置提供商：
```yaml
model:
  provider: "zai"       # 或：kimi-coding, minimax, minimax-cn, alibaba
  default: "glm-4-plus"
```

可以使用 `GLM_BASE_URL`、`KIMI_BASE_URL`、`MINIMAX_BASE_URL`、`MINIMAX_CN_BASE_URL` 或 `DASHSCOPE_BASE_URL` 环境变量覆盖基础 URL。

### Hugging Face 推理提供商

[Hugging Face 推理提供商](https://huggingface.co/docs/inference-providers) 通过统一的 OpenAI 兼容端点 (`router.huggingface.co/v1`) 路由到 20 多个开源模型。请求会自动路由到最快的可用后端（Groq、Together、SambaNova 等），并具有自动故障转移功能。

```bash
# 使用任何可用模型
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

在 [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) 获取你的令牌 — 确保启用“Make calls to Inference Providers”权限。包含免费层（每月 $0.10 信用额度，提供商费率无加价）。

你可以在模型名称后附加路由后缀：`:fastest`（默认）、`:cheapest` 或 `:provider_name` 以强制使用特定后端。

可以使用 `HF_BASE_URL` 覆盖基础 URL。

## 自定义和自托管 LLM 提供商

Hermes Agent 可与 **任何 OpenAI 兼容的 API 端点** 配合使用。如果服务器实现了 `/v1/chat/completions`，你就可以将 Hermes 指向它。这意味着你可以使用本地模型、GPU 推理服务器、多提供商路由器或任何第三方 API。

### 通用设置

配置自定义端点的三种方式：

**交互式设置（推荐）：**
```bash
hermes model
# 选择 "Custom endpoint (self-hosted / VLLM / etc.)"
# 输入：API 基础 URL、API 密钥、模型名称
```

**手动配置 (`config.yaml`):**
```yaml
# 在 ~/.hermes/config.yaml 中
model:
  default: your-model-name
  provider: custom
  base_url: http://localhost:8000/v1
  api_key: your-key-or-leave-empty-for-local
```

**环境变量 (`.env` 文件):**
```bash
# 添加到 ~/.hermes/.env
OPENAI_BASE_URL=http://localhost:8000/v1
OPENAI_API_KEY=your-key     # 对于本地服务器可以是任何非空字符串
LLM_MODEL=your-model-name
```

所有三种方法最终都会进入相同的运行时路径。`hermes model` 将提供商、模型和基础 URL 持久化到 `config.yaml`，因此即使未设置环境变量，后续会话也会继续使用该端点。

### 使用 `/model` 切换模型

配置自定义端点后，你可以在会话中切换模型：

```
/model custom:qwen-2.5          # 切换到自定义端点上的模型
/model custom                    # 从端点自动检测模型
/model openrouter:claude-sonnet-4 # 切换回云提供商
```
如果你配置了**命名的自定义提供商**（见下文），请使用三重语法：

```
/model custom:local:qwen-2.5    # 使用名为 "local" 的自定义提供商和模型 qwen-2.5
/model custom:work:llama3       # 使用名为 "work" 的自定义提供商和模型 llama3
```

切换提供商时，Hermes 会将基础 URL 和提供商信息持久化到配置中，因此更改在重启后依然有效。当从自定义端点切换回内置提供商时，过时的基础 URL 会自动被清除。

:::tip
`/model custom`（不带模型名）会查询你端点的 `/models` API，如果恰好加载了一个模型，则会自动选择它。这对于运行单个模型的本地服务器很有用。
:::

以下所有内容都遵循相同的模式——只需更改 URL、密钥和模型名称。

---

### Ollama — 本地模型，零配置

[Ollama](https://ollama.com/) 只需一条命令即可在本地运行开源模型。最适合：快速本地实验、注重隐私的工作、离线使用。

```bash
# 安装并运行模型
ollama pull llama3.1:70b
ollama serve   # 在端口 11434 启动

# 配置 Hermes
OPENAI_BASE_URL=http://localhost:11434/v1
OPENAI_API_KEY=ollama           # 任何非空字符串
LLM_MODEL=llama3.1:70b
```

Ollama 的 OpenAI 兼容端点支持聊天补全、流式传输和工具调用（适用于支持的模型）。运行较小模型无需 GPU——Ollama 会自动处理 CPU 推理。

:::tip
使用 `ollama list` 列出可用模型。使用 `ollama pull <model>` 从 [Ollama 模型库](https://ollama.com/library) 拉取任何模型。
:::

---

### vLLM — 高性能 GPU 推理

[vLLM](https://docs.vllm.ai/) 是生产级 LLM 服务的标准。最适合：GPU 硬件上的最大吞吐量、服务大型模型、连续批处理。

```bash
# 启动 vLLM 服务器
pip install vllm
vllm serve meta-llama/Llama-3.1-70B-Instruct \
  --port 8000 \
  --tensor-parallel-size 2    # 多 GPU

# 配置 Hermes
OPENAI_BASE_URL=http://localhost:8000/v1
OPENAI_API_KEY=dummy
LLM_MODEL=meta-llama/Llama-3.1-70B-Instruct
```

vLLM 支持工具调用、结构化输出和多模态模型。使用 `--enable-auto-tool-choice` 和 `--tool-call-parser hermes` 来启用 NousResearch 模型的 Hermes 格式工具调用。

---

### SGLang — 带 RadixAttention 的快速服务

[SGLang](https://github.com/sgl-project/sglang) 是 vLLM 的替代方案，具有用于 KV 缓存重用的 RadixAttention。最适合：多轮对话（前缀缓存）、约束解码、结构化输出。

```bash
# 启动 SGLang 服务器
pip install "sglang[all]"
python -m sglang.launch_server \
  --model meta-llama/Llama-3.1-70B-Instruct \
  --port 8000 \
  --tp 2

# 配置 Hermes
OPENAI_BASE_URL=http://localhost:8000/v1
OPENAI_API_KEY=dummy
LLM_MODEL=meta-llama/Llama-3.1-70B-Instruct
```

---

### llama.cpp / llama-server — CPU 和 Metal 推理

[llama.cpp](https://github.com/ggml-org/llama.cpp) 在 CPU、Apple Silicon (Metal) 和消费级 GPU 上运行量化模型。最适合：在没有数据中心 GPU 的情况下运行模型、Mac 用户、边缘部署。

```bash
# 构建并启动 llama-server
cmake -B build && cmake --build build --config Release
./build/bin/llama-server \
  -m models/llama-3.1-8b-instruct-Q4_K_M.gguf \
  --port 8080 --host 0.0.0.0

# 配置 Hermes
OPENAI_BASE_URL=http://localhost:8080/v1
OPENAI_API_KEY=dummy
LLM_MODEL=llama-3.1-8b-instruct
```

:::tip
从 [Hugging Face](https://huggingface.co/models?library=gguf) 下载 GGUF 模型。Q4_K_M 量化在质量和内存使用之间提供了最佳平衡。
:::

---

### LiteLLM Proxy — 多提供商网关

[LiteLLM](https://docs.litellm.ai/) 是一个 OpenAI 兼容的代理，将 100 多个 LLM 提供商统一在一个 API 后面。最适合：无需更改配置即可在提供商之间切换、负载均衡、故障转移链、预算控制。

```bash
# 安装并启动
pip install "litellm[proxy]"
litellm --model anthropic/claude-sonnet-4 --port 4000

# 或者使用配置文件管理多个模型：
litellm --config litellm_config.yaml --port 4000

# 配置 Hermes
OPENAI_BASE_URL=http://localhost:4000/v1
OPENAI_API_KEY=sk-your-litellm-key
LLM_MODEL=anthropic/claude-sonnet-4
```

带故障转移的 `litellm_config.yaml` 示例：
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

### ClawRouter — 成本优化路由

BlockRunAI 出品的 [ClawRouter](https://github.com/BlockRunAI/ClawRouter) 是一个本地路由代理，可根据查询复杂度自动选择模型。它根据 14 个维度对请求进行分类，并路由到能够处理任务的最便宜模型。支付通过 USDC 加密货币进行（无需 API 密钥）。

```bash
# 安装并启动
npx @blockrun/clawrouter    # 在端口 8402 启动

# 配置 Hermes
OPENAI_BASE_URL=http://localhost:8402/v1
OPENAI_API_KEY=dummy
LLM_MODEL=blockrun/auto     # 或：blockrun/eco, blockrun/premium, blockrun/agentic
```

路由配置文件：
| 配置文件 | 策略 | 节省 |
|---------|----------|---------|
| `blockrun/auto` | 质量/成本平衡 | 74-100% |
| `blockrun/eco` | 尽可能便宜 | 95-100% |
| `blockrun/premium` | 最佳质量模型 | 0% |
| `blockrun/free` | 仅限免费模型 | 100% |
| `blockrun/agentic` | 为工具使用优化 | 视情况而定 |

:::note
ClawRouter 需要在 Base 或 Solana 上有一个 USDC 资金钱包用于支付。所有请求都通过 BlockRun 的后端 API 路由。运行 `npx @blockrun/clawrouter doctor` 来检查钱包状态。
:::

---

### 其他兼容提供商

任何提供 OpenAI 兼容 API 的服务都可以使用。一些流行的选项：

| 提供商 | 基础 URL | 备注 |
|----------|----------|-------|
| [Together AI](https://together.ai) | `https://api.together.xyz/v1` | 云托管开源模型 |
| [Groq](https://groq.com) | `https://api.groq.com/openai/v1` | 超快速推理 |
| [DeepSeek](https://deepseek.com) | `https://api.deepseek.com/v1` | DeepSeek 模型 |
| [Fireworks AI](https://fireworks.ai) | `https://api.fireworks.ai/inference/v1` | 快速开源模型托管 |
| [Cerebras](https://cerebras.ai) | `https://api.cerebras.ai/v1` | 晶圆级芯片推理 |
| [Mistral AI](https://mistral.ai) | `https://api.mistral.ai/v1` | Mistral 模型 |
| [OpenAI](https://openai.com) | `https://api.openai.com/v1` | 直接访问 OpenAI |
| [Azure OpenAI](https://azure.microsoft.com) | `https://YOUR.openai.azure.com/` | 企业版 OpenAI |
| [LocalAI](https://localai.io) | `http://localhost:8080/v1` | 自托管，多模型 |
| [Jan](https://jan.ai) | `http://localhost:1337/v1` | 带本地模型的桌面应用 |

```bash
# 示例：Together AI
OPENAI_BASE_URL=https://api.together.xyz/v1
OPENAI_API_KEY=your-together-key
LLM_MODEL=meta-llama/Llama-3.1-70B-Instruct-Turbo
```

---

### 上下文长度检测 {#context-length-detection}

Hermes 使用多源解析链来检测你的模型和提供商的正确上下文窗口：

1.  **配置覆盖** — `config.yaml` 中的 `model.context_length`（最高优先级）
2.  **自定义提供商按模型设置** — `custom_providers[].models.<id>.context_length`
3.  **持久化缓存** — 先前发现的值（重启后保留）
4.  **端点 `/models`** — 查询你服务器的 API（本地/自定义端点）
5.  **Anthropic `/v1/models`** — 查询 Anthropic 的 API 获取 `max_input_tokens`（仅限 API 密钥用户）
6.  **OpenRouter API** — 来自 OpenRouter 的实时模型元数据
7.  **Nous Portal** — 将 Nous 模型 ID 后缀与 OpenRouter 元数据进行匹配
8.  **[models.dev](https://models.dev)** — 社区维护的注册表，包含 100 多个提供商中 3800 多个模型的提供商特定上下文长度
9.  **后备默认值** — 广泛的模型系列模式（默认 128K）

对于大多数设置，这可以开箱即用。该系统是提供商感知的——同一个模型根据服务提供商的不同可能有不同的上下文限制（例如，`claude-opus-4.6` 在 Anthropic 直接服务上是 1M，但在 GitHub Copilot 上是 128K）。

要显式设置上下文长度，请在模型配置中添加 `context_length`：

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

`hermes model` 在配置自定义端点时会提示输入上下文长度。留空则进行自动检测。

:::tip 何时手动设置
- 你使用 Ollama 并设置了低于模型最大值的自定义 `num_ctx`
- 你想将上下文限制在模型最大值以下（例如，在 128k 模型上限制为 8k 以节省 VRAM）
- 你运行在未暴露 `/v1/models` 的代理后面
:::

---

### 命名的自定义提供商

如果你需要处理多个自定义端点（例如，本地开发服务器和远程 GPU 服务器），可以在 `config.yaml` 中将它们定义为命名的自定义提供商：

```yaml
custom_providers:
  - name: local
    base_url: http://localhost:8080/v1
    # 省略 api_key — Hermes 对无需密钥的本地服务器使用 "no-key-required"
  - name: work
    base_url: https://gpu-server.internal.corp/v1
    api_key: corp-api-key
    api_mode: chat_completions   # 可选，根据 URL 自动检测
  - name: anthropic-proxy
    base_url: https://proxy.example.com/anthropic
    api_key: proxy-key
    api_mode: anthropic_messages  # 用于 Anthropic 兼容代理
```

在会话中使用三重语法在它们之间切换：

```
/model custom:local:qwen-2.5       # 使用 "local" 端点和 qwen-2.5
/model custom:work:llama3-70b      # 使用 "work" 端点和 llama3-70b
/model custom:anthropic-proxy:claude-sonnet-4  # 使用代理
```

你也可以从交互式的 `hermes model` 菜单中选择命名的自定义提供商。

---

### 选择合适的设置

| 使用场景 | 推荐 |
|----------|-------------|
| **只想开箱即用** | OpenRouter（默认）或 Nous Portal |
| **本地模型，易于设置** | Ollama |
| **生产级 GPU 服务** | vLLM 或 SGLang |
| **Mac / 无 GPU** | Ollama 或 llama.cpp |
| **多提供商路由** | LiteLLM Proxy 或 OpenRouter |
| **成本优化** | ClawRouter 或带 `sort: "price"` 的 OpenRouter |
| **最大隐私** | Ollama、vLLM 或 llama.cpp（完全本地） |
| **企业 / Azure** | 带自定义端点的 Azure OpenAI |
| **中文 AI 模型** | z.ai (GLM)、Kimi/Moonshot 或 MiniMax（一流提供商） |

:::tip
你可以随时使用 `hermes model` 在提供商之间切换——无需重启。无论你使用哪个提供商，你的对话历史、记忆和技能都会保留。
:::

## 可选的 API 密钥

| 功能 | 提供商 | 环境变量 |
|---------|----------|--------------|
| 网页抓取 | [Firecrawl](https://firecrawl.dev/) | `FIRECRAWL_API_KEY`, `FIRECRAWL_API_URL` |
| 浏览器自动化 | [Browserbase](https://browserbase.com/) | `BROWSERBASE_API_KEY`, `BROWSERBASE_PROJECT_ID` |
| 图像生成 | [FAL](https://fal.ai/) | `FAL_KEY` |
| 高级 TTS 语音 | [ElevenLabs](https://elevenlabs.io/) | `ELEVENLABS_API_KEY` |
| OpenAI TTS + 语音转录 | [OpenAI](https://platform.openai.com/api-keys) | `VOICE_TOOLS_OPENAI_KEY` |
| RL 训练 | [Tinker](https://tinker-console.thinkingmachines.ai/) + [WandB](https://wandb.ai/) | `TINKER_API_KEY`, `WANDB_API_KEY` |
| 跨会话用户建模 | [Honcho](https://honcho.dev/) | `HONCHO_API_KEY` |

### 自托管 Firecrawl

默认情况下，Hermes 使用 [Firecrawl 云 API](https://firecrawl.dev/) 进行网页搜索和抓取。如果你希望本地运行 Firecrawl，可以将 Hermes 指向自托管的实例。完整的设置说明请参阅 Firecrawl 的 [SELF_HOST.md](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md)。

**你将获得：** 无需 API 密钥、无速率限制、无按页计费、完全的数据主权。
**你会失去什么：** 云版本使用 Firecrawl 专有的“Fire-engine”进行高级反机器人绕过（Cloudflare、验证码、IP轮换）。自托管版本使用基础的 fetch + Playwright，因此一些受保护的网站可能会失败。搜索使用 DuckDuckGo 而不是 Google。

**设置步骤：**

1.  克隆并启动 Firecrawl Docker 堆栈（5个容器：API、Playwright、Redis、RabbitMQ、PostgreSQL — 需要约 4-8 GB 内存）：
    ```bash
    git clone https://github.com/firecrawl/firecrawl
    cd firecrawl
    # 在 .env 文件中设置：USE_DB_AUTHENTICATION=false, HOST=0.0.0.0, PORT=3002
    docker compose up -d
    ```

2.  将 Hermes 指向你的实例（无需 API 密钥）：
    ```bash
    hermes config set FIRECRAWL_API_URL http://localhost:3002
    ```

如果你的自托管实例启用了身份验证，也可以同时设置 `FIRECRAWL_API_KEY` 和 `FIRECRAWL_API_URL`。

## OpenRouter 提供商路由

使用 OpenRouter 时，你可以控制请求如何在不同提供商之间路由。在 `~/.hermes/config.yaml` 中添加 `provider_routing` 部分：

```yaml
provider_routing:
  sort: "throughput"          # "price"（默认）、"throughput" 或 "latency"
  # only: ["anthropic"]      # 仅使用这些提供商
  # ignore: ["deepinfra"]    # 跳过这些提供商
  # order: ["anthropic", "google"]  # 按此顺序尝试提供商
  # require_parameters: true  # 仅使用支持所有请求参数的提供商
  # data_collection: "deny"   # 排除可能存储/训练数据的提供商
```

**快捷方式：** 在任何模型名称后附加 `:nitro` 表示按吞吐量排序（例如，`anthropic/claude-sonnet-4:nitro`），或附加 `:floor` 表示按价格排序。

## 备用模型 {#fallback-model}

配置一个备用 provider:model，当你的主模型失败时（速率限制、服务器错误、身份验证失败），Hermes 会自动切换到它：

```yaml
fallback_model:
  provider: openrouter                    # 必需
  model: anthropic/claude-sonnet-4        # 必需
  # base_url: http://localhost:8000/v1    # 可选，用于自定义端点
  # api_key_env: MY_CUSTOM_KEY           # 可选，自定义端点 API 密钥的环境变量名
```

激活后，备用模型会在会话中途切换模型和提供商，而不会丢失你的对话。每个会话**最多触发一次**。

支持的提供商：`openrouter`、`nous`、`openai-codex`、`copilot`、`anthropic`、`huggingface`、`zai`、`kimi-coding`、`minimax`、`minimax-cn`、`custom`。

:::tip
备用模型配置**仅**通过 `config.yaml` 进行 — 没有对应的环境变量。关于触发条件、支持的提供商以及它与辅助任务和委托的交互的完整细节，请参阅[备用提供商](/user-guide/features/fallback-providers)。
:::

## 智能模型路由

可选的廉价与强大模型路由功能，让 Hermes 将复杂工作保留给你的主模型，同时将非常简短/简单的对话轮次发送到更便宜的模型。

```yaml
smart_model_routing:
  enabled: true
  max_simple_chars: 160
  max_simple_words: 28
  cheap_model:
    provider: openrouter
    model: google/gemini-2.5-flash
    # base_url: http://localhost:8000/v1  # 可选的自定义端点
    # api_key_env: MY_CUSTOM_KEY          # 该端点 API 密钥的可选环境变量名
```

工作原理：
- 如果一轮对话简短、单行，且看起来不涉及大量代码/工具/调试工作，Hermes 可能会将其路由到 `cheap_model`
- 如果对话看起来复杂，Hermes 会继续使用你的主模型/提供商
- 如果廉价路由无法干净地解析，Hermes 会自动回退到主模型

这是有意设计为保守的。它适用于快速、低风险的对话轮次，例如：
- 简短的事实性问题
- 快速重写
- 轻量级摘要

它会避免路由看起来像以下情况的提示：
- 编码/调试工作
- 大量使用工具的请求
- 冗长或多行的分析请求

当你想在不完全更改默认模型的情况下降低延迟或成本时，可以使用此功能。

## 终端后端配置

配置 Agent 使用哪个环境来执行终端命令：

```yaml
terminal:
  backend: local    # 或：docker, ssh, singularity, modal, daytona
  cwd: "."          # 工作目录（"." = 当前目录）
  timeout: 180      # 命令超时时间（秒）

  # Docker 特定设置
  docker_image: "nikolaik/python-nodejs:python3.11-nodejs20"
  docker_mount_cwd_to_workspace: false  # 安全：默认关闭。选择是否将启动时的 cwd 挂载到 /workspace。
  docker_forward_env:              # 可选的环境变量显式允许列表，用于传递环境变量
    - "GITHUB_TOKEN"
  docker_volumes:                    # 额外的显式主机挂载
    - "/home/user/projects:/workspace/projects"
    - "/home/user/data:/data:ro"     # :ro 表示只读

  # 容器资源限制（docker, singularity, modal, daytona）
  container_cpu: 1                   # CPU 核心数
  container_memory: 5120             # MB（默认 5GB）
  container_disk: 51200              # MB（默认 50GB）
  container_persistent: true         # 跨会话持久化文件系统

  # 持久化 shell — 在命令之间保持一个长期运行的 bash 进程
  persistent_shell: true             # SSH 后端默认启用
```

### 常见终端后端问题

如果终端命令立即失败或报告终端工具被禁用，请检查以下内容：

- **本地后端**
  - 无特殊要求。当你刚开始使用时，这是最安全的默认设置。

- **Docker 后端**
  - 确保 Docker Desktop（或 Docker 守护进程）已安装并正在运行。
  - Hermes 需要能够找到 `docker` CLI。它首先检查你的 `$PATH`，在 macOS 上还会探测常见的 Docker Desktop 安装位置。运行：
    ```bash
    docker version
    ```
    如果失败，请修复你的 Docker 安装或切换回本地后端：
    ```bash
    hermes config set terminal.backend local
    ```

- **SSH 后端**
  - 必须同时设置 `TERMINAL_SSH_HOST` 和 `TERMINAL_SSH_USER`，例如：
    ```bash
    export TERMINAL_ENV=ssh
    export TERMINAL_SSH_HOST=my-server.example.com
    export TERMINAL_SSH_USER=ubuntu
    ```
  - 如果缺少任一值，Hermes 将记录明确的错误并拒绝使用 SSH 后端。

- **Modal 后端**
  - 你需要一个 `MODAL_TOKEN_ID` 环境变量或一个 `~/.modal.toml` 配置文件。
  - 如果两者都不存在，后端检查将失败，Hermes 会报告 Modal 后端不可用。

如有疑问，请将 `terminal.backend` 设置回 `local`，并首先验证命令能否在那里运行。

### Docker 卷挂载

使用 Docker 后端时，`docker_volumes` 允许你将主机目录与容器共享。每个条目使用标准的 Docker `-v` 语法：`host_path:container_path[:options]`。

```yaml
terminal:
  backend: docker
  docker_volumes:
    - "/home/user/projects:/workspace/projects"   # 读写（默认）
    - "/home/user/datasets:/data:ro"              # 只读
    - "/home/user/outputs:/outputs"               # Agent 写入，你读取
```

这适用于：
- **向 Agent 提供文件**（数据集、配置、参考代码）
- **从 Agent 接收文件**（生成的代码、报告、导出文件）
- **共享工作区**，你和 Agent 都可以访问相同的文件

也可以通过环境变量设置：`TERMINAL_DOCKER_VOLUMES='["/host:/container"]'`（JSON 数组）。

### Docker 凭据转发

默认情况下，Docker 终端会话不会继承任意的主机凭据。如果你需要在容器内使用特定的令牌，请将其添加到 `terminal.docker_forward_env`。

```yaml
terminal:
  backend: docker
  docker_forward_env:
    - "GITHUB_TOKEN"
    - "NPM_TOKEN"
```

Hermes 首先从你当前的 shell 解析每个列出的变量，如果变量已通过 `hermes config set` 保存，则回退到 `~/.hermes/.env`。

:::warning
`docker_forward_env` 中列出的任何内容都会对容器内运行的命令可见。只转发你愿意暴露给终端会话的凭据。
:::

### 可选：将启动目录挂载到 `/workspace`

默认情况下，Docker 沙盒保持隔离。除非你明确选择加入，否则 Hermes **不会**将你当前的主机工作目录传递到容器中。

在 `config.yaml` 中启用它：

```yaml
terminal:
  backend: docker
  docker_mount_cwd_to_workspace: true
```

启用后：
- 如果你从 `~/projects/my-app` 启动 Hermes，该主机目录将被绑定挂载到 `/workspace`
- Docker 后端在 `/workspace` 中启动
- 文件工具和终端命令都能看到相同的已挂载项目

禁用时，除非你通过 `docker_volumes` 显式挂载某些内容，否则 `/workspace` 仍归沙盒所有。

安全权衡：
- `false` 保持沙盒边界
- `true` 让沙盒直接访问你启动 Hermes 的目录

仅当你特意希望容器处理实时主机文件时，才使用此选择加入功能。

### 持久化 Shell

默认情况下，每个终端命令都在其自己的子进程中运行 — 工作目录、环境变量和 shell 变量在命令之间重置。当启用**持久化 shell** 时，一个长期运行的 bash 进程会在 `execute()` 调用之间保持活动状态，以便状态在命令之间得以保留。

这对于 **SSH 后端** 最有用，因为它还消除了每次命令的连接开销。持久化 shell 在 **SSH 后端默认启用**，在本地后端默认禁用。

```yaml
terminal:
  persistent_shell: true   # 默认 — 为 SSH 启用持久化 shell
```

要禁用：

```bash
hermes config set terminal.persistent_shell false
```

**在命令之间持久化的内容：**
- 工作目录（`cd /tmp` 对下一个命令生效）
- 导出的环境变量（`export FOO=bar`）
- Shell 变量（`MY_VAR=hello`）

**优先级：**

| 级别 | 变量 | 默认值 |
|-------|----------|---------|
| 配置 | `terminal.persistent_shell` | `true` |
| SSH 覆盖 | `TERMINAL_SSH_PERSISTENT` | 遵循配置 |
| 本地覆盖 | `TERMINAL_LOCAL_PERSISTENT` | `false` |

每个后端的特定环境变量具有最高优先级。如果你也想在本地后端使用持久化 shell：

```bash
export TERMINAL_LOCAL_PERSISTENT=true
```

:::note
需要 `stdin_data` 或 sudo 的命令会自动回退到一次性模式，因为持久化 shell 的 stdin 已被 IPC 协议占用。
:::

有关每个后端的详细信息，请参阅[代码执行](features/code-execution.md)和 README 的[终端部分](features/tools.md)。

## 记忆配置

```yaml
memory:
  memory_enabled: true
  user_profile_enabled: true
  memory_char_limit: 2200   # 约 800 个 token
  user_char_limit: 1375     # 约 500 个 token
```

## Git 工作树隔离

为在同一仓库上并行运行多个 Agent 启用隔离的 git 工作树：

```yaml
worktree: true    # 始终创建工作树（与 hermes -w 相同）
# worktree: false # 默认 — 仅在传递 -w 标志时创建
```

启用后，每个 CLI 会话都会在 `.worktrees/` 下创建一个新的工作树及其自己的分支。Agent 可以编辑文件、提交、推送和创建 PR，而不会相互干扰。干净的工作树在退出时被移除；脏的工作树被保留以供手动恢复。

你也可以通过在仓库根目录创建 `.worktreeinclude` 文件，列出要复制到工作树中的 git 忽略文件：

```
# .worktreeinclude
.env
.venv/
node_modules/
```

## 上下文压缩 {#context-compression}

Hermes 会自动压缩长对话，以保持在你的模型上下文窗口内。压缩摘要器是一个独立的 LLM 调用 — 你可以将其指向任何提供商或端点。

所有压缩设置都位于 `config.yaml` 中（没有环境变量）。

### 完整参考

```yaml
compression:
  enabled: true                                     # 启用/禁用压缩
  threshold: 0.50                                   # 在达到上下文限制的此百分比时压缩
  summary_model: "google/gemini-3-flash-preview"    # 用于摘要的模型
  summary_provider: "auto"                          # 提供商："auto"、"openrouter"、"nous"、"codex"、"main" 等。
  summary_base_url: null                            # 自定义 OpenAI 兼容端点（覆盖提供商）
```
### 常用配置

**默认（自动检测）—— 无需配置：**
```yaml
compression:
  enabled: true
  threshold: 0.50
```
使用第一个可用的提供商（OpenRouter → Nous → Codex）配合 Gemini Flash。

**强制指定提供商**（基于 OAuth 或 API 密钥）：
```yaml
compression:
  summary_provider: nous
  summary_model: gemini-3-flash
```
适用于任何提供商：`nous`、`openrouter`、`codex`、`anthropic`、`main` 等。

**自定义端点**（自托管、Ollama、zai、DeepSeek 等）：
```yaml
compression:
  summary_model: glm-4.7
  summary_base_url: https://api.z.ai/api/coding/paas/v4
```
指向一个自定义的 OpenAI 兼容端点。使用 `OPENAI_API_KEY` 进行身份验证。

### 三个旋钮如何交互

| `summary_provider` | `summary_base_url` | 结果 |
|---------------------|---------------------|--------|
| `auto`（默认） | 未设置 | 自动检测最佳可用提供商 |
| `nous` / `openrouter` / 等 | 未设置 | 强制使用该提供商，使用其身份验证 |
| 任意值 | 已设置 | 直接使用自定义端点（忽略提供商） |

`summary_model` 必须支持至少与您的主模型一样大的上下文长度，因为它会接收完整的对话中间部分进行压缩。

## 迭代预算压力

当 Agent 处理包含大量工具调用的复杂任务时，可能会在不知不觉中快速消耗其迭代预算（默认：90 轮）。预算压力会在接近限制时自动警告模型：

| 阈值 | 级别 | 模型看到的内容 |
|-----------|-------|---------------------|
| **70%** | 注意 | `[BUDGET: 63/90. 27 次迭代剩余。开始整合工作。]` |
| **90%** | 警告 | `[BUDGET WARNING: 81/90. 仅剩 9 次。立即响应。]` |

警告被注入到最后一个工具结果的 JSON 中（作为 `_budget_warning` 字段），而不是作为单独的消息——这保留了提示缓存，并且不会破坏对话结构。

```yaml
agent:
  max_turns: 90                # 每次对话轮次的最大迭代次数（默认：90）
```

预算压力默认启用。Agent 会自然地看到警告，作为工具结果的一部分，鼓励它在迭代次数用完之前整合工作并给出响应。

## 上下文压力警告

与迭代预算压力不同，上下文压力跟踪对话距离**压缩阈值**有多近——即触发上下文压缩以总结旧消息的点。这有助于您和 Agent 了解对话何时变得过长。

| 进度 | 级别 | 发生的情况 |
|----------|-------|-------------|
| 距离阈值 **≥ 60%** | 信息 | CLI 显示青色进度条；网关发送信息通知 |
| 距离阈值 **≥ 85%** | 警告 | CLI 显示粗体黄色进度条；网关警告即将进行压缩 |

在 CLI 中，上下文压力在工具输出流中显示为进度条：

```
  ◐ context ████████████░░░░░░░░ 62% to compaction  48k threshold (50%) · approaching compaction
```

在消息平台上，会发送纯文本通知：

```
◐ Context: ████████████░░░░░░░░ 62% to compaction (threshold: 50% of window).
```

如果自动压缩被禁用，警告会告知您上下文可能会被截断。

上下文压力是自动的——无需配置。它纯粹作为面向用户的通知触发，不会修改消息流或向模型的上下文中注入任何内容。

## 辅助模型 {#auxiliary-models}

Hermes 使用轻量级的“辅助”模型来处理图像分析、网页摘要和浏览器截图分析等次要任务。默认情况下，这些任务通过自动检测使用 **Gemini Flash**——您无需配置任何内容。

### 通用配置模式

Hermes 中的每个模型槽位——辅助任务、压缩、后备模型——都使用相同的三个旋钮：

| 键 | 作用 | 默认值 |
|-----|-------------|---------|
| `provider` | 用于身份验证和路由的提供商 | `"auto"` |
| `model` | 请求的模型 | 提供商的默认值 |
| `base_url` | 自定义的 OpenAI 兼容端点（覆盖提供商） | 未设置 |

当设置了 `base_url` 时，Hermes 会忽略提供商并直接调用该端点（使用 `api_key` 或 `OPENAI_API_KEY` 进行身份验证）。当只设置了 `provider` 时，Hermes 使用该提供商内置的身份验证和基础 URL。

可用提供商：`auto`、`openrouter`、`nous`、`codex`、`copilot`、`anthropic`、`main`、`zai`、`kimi-coding`、`minimax`，以及任何在[提供商注册表](/reference/environment-variables)中注册的提供商。

### 完整的辅助配置参考

```yaml
auxiliary:
  # 图像分析 (vision_analyze 工具 + 浏览器截图)
  vision:
    provider: "auto"           # "auto", "openrouter", "nous", "codex", "main", 等
    model: ""                  # 例如 "openai/gpt-4o", "google/gemini-2.5-flash"
    base_url: ""               # 自定义 OpenAI 兼容端点（覆盖提供商）
    api_key: ""                # 用于 base_url 的 API 密钥（回退到 OPENAI_API_KEY）
    timeout: 30                # 秒 —— 为慢速的本地视觉模型增加此值

  # 网页摘要 + 浏览器页面文本提取
  web_extract:
    provider: "auto"
    model: ""                  # 例如 "google/gemini-2.5-flash"
    base_url: ""
    api_key: ""
    timeout: 30                # 秒

  # 危险命令批准分类器
  approval:
    provider: "auto"
    model: ""
    base_url: ""
    api_key: ""
    timeout: 30                # 秒

  # 上下文压缩超时（与 compression.* 配置分开）
  compression:
    timeout: 120               # 秒 —— 压缩会总结长对话，需要更多时间
```

:::tip
每个辅助任务都有可配置的 `timeout`（以秒为单位）。默认值：vision 30s，web_extract 30s，approval 30s，compression 120s。如果您为辅助任务使用慢速的本地模型，请增加这些值。
:::

:::info
上下文压缩有自己的顶级 `compression:` 块，包含 `summary_provider`、`summary_model` 和 `summary_base_url`——请参阅上面的[上下文压缩](#context-compression)。后备模型使用 `fallback_model:` 块——请参阅上面的[后备模型](#fallback-model)。这三者都遵循相同的 provider/model/base_url 模式。
:::

### 更改视觉模型

要将图像分析从 Gemini Flash 改为使用 GPT-4o：

```yaml
auxiliary:
  vision:
    model: "openai/gpt-4o"
```

或者通过环境变量（在 `~/.hermes/.env` 中）：

```bash
AUXILIARY_VISION_MODEL=openai/gpt-4o
```

### 提供商选项

| 提供商 | 描述 | 要求 |
|----------|-------------|-------------|
| `"auto"` | 最佳可用（默认）。视觉模型尝试 OpenRouter → Nous → Codex。 | — |
| `"openrouter"` | 强制使用 OpenRouter —— 路由到任何模型（Gemini、GPT-4o、Claude 等） | `OPENROUTER_API_KEY` |
| `"nous"` | 强制使用 Nous Portal | `hermes login` |
| `"codex"` | 强制使用 Codex OAuth（ChatGPT 账户）。支持视觉（gpt-5.3-codex）。 | `hermes model` → Codex |
| `"main"` | 使用您活动的自定义/主端点。这可以来自 `OPENAI_BASE_URL` + `OPENAI_API_KEY`，或者来自通过 `hermes model` / `config.yaml` 保存的自定义端点。适用于 OpenAI、本地模型或任何 OpenAI 兼容的 API。 | 自定义端点凭据 + 基础 URL |

### 常用配置

**使用直接的自定义端点**（对于本地/自托管 API，比 `provider: "main"` 更清晰）：
```yaml
auxiliary:
  vision:
    base_url: "http://localhost:1234/v1"
    api_key: "local-key"
    model: "qwen2.5-vl"
```

`base_url` 的优先级高于 `provider`，因此这是将辅助任务路由到特定端点的最明确方式。对于直接端点覆盖，Hermes 使用配置的 `api_key` 或回退到 `OPENAI_API_KEY`；它不会为该自定义端点重用 `OPENROUTER_API_KEY`。

**使用 OpenAI API 密钥进行视觉分析：**
```yaml
# 在 ~/.hermes/.env 中：
# OPENAI_BASE_URL=https://api.openai.com/v1
# OPENAI_API_KEY=sk-...

auxiliary:
  vision:
    provider: "main"
    model: "gpt-4o"       # 或者使用更便宜的 "gpt-4o-mini"
```

**使用 OpenRouter 进行视觉分析**（路由到任何模型）：
```yaml
auxiliary:
  vision:
    provider: "openrouter"
    model: "openai/gpt-4o"      # 或者 "google/gemini-2.5-flash" 等
```

**使用 Codex OAuth**（ChatGPT Pro/Plus 账户——无需 API 密钥）：
```yaml
auxiliary:
  vision:
    provider: "codex"     # 使用您的 ChatGPT OAuth 令牌
    # model 默认为 gpt-5.3-codex（支持视觉）
```

**使用本地/自托管模型：**
```yaml
auxiliary:
  vision:
    provider: "main"      # 使用您活动的自定义端点
    model: "my-local-model"
```

`provider: "main"` 遵循 Hermes 用于正常聊天的相同自定义端点。该端点可以直接通过 `OPENAI_BASE_URL` 设置，或者通过 `hermes model` 保存一次并持久化在 `config.yaml` 中。

:::tip
如果您使用 Codex OAuth 作为您的主模型提供商，视觉分析会自动工作——无需额外配置。Codex 包含在视觉模型的自动检测链中。
:::

:::warning
**视觉分析需要多模态模型。** 如果您设置 `provider: "main"`，请确保您的端点支持多模态/视觉——否则图像分析将失败。
:::

### 环境变量（旧版）

辅助模型也可以通过环境变量配置。但是，`config.yaml` 是首选方法——它更易于管理，并且支持包括 `base_url` 和 `api_key` 在内的所有选项。

| 设置 | 环境变量 |
|---------|---------------------|
| 视觉提供商 | `AUXILIARY_VISION_PROVIDER` |
| 视觉模型 | `AUXILIARY_VISION_MODEL` |
| 视觉端点 | `AUXILIARY_VISION_BASE_URL` |
| 视觉 API 密钥 | `AUXILIARY_VISION_API_KEY` |
| 网页提取提供商 | `AUXILIARY_WEB_EXTRACT_PROVIDER` |
| 网页提取模型 | `AUXILIARY_WEB_EXTRACT_MODEL` |
| 网页提取端点 | `AUXILIARY_WEB_EXTRACT_BASE_URL` |
| 网页提取 API 密钥 | `AUXILIARY_WEB_EXTRACT_API_KEY` |

压缩和后备模型设置仅支持 config.yaml。

:::tip
运行 `hermes config` 查看您当前的辅助模型设置。只有当覆盖项与默认值不同时才会显示。
:::

## 推理力度

控制模型在响应前“思考”的程度：

```yaml
agent:
  reasoning_effort: ""   # 空 = 中等（默认）。选项：xhigh（最大）、high、medium、low、minimal、none
```

当未设置时（默认），推理力度默认为“中等”——这是一个适用于大多数任务的平衡水平。设置一个值会覆盖它——更高的推理力度在复杂任务上能提供更好的结果，但代价是更多的令牌和延迟。

您也可以在运行时使用 `/reasoning` 命令更改推理力度：

```
/reasoning           # 显示当前力度级别和显示状态
/reasoning high      # 将推理力度设置为高
/reasoning none      # 禁用推理
/reasoning show      # 在每个响应上方显示模型思考过程
/reasoning hide      # 隐藏模型思考过程
```

## 工具使用强制

某些模型（尤其是 GPT 系列）偶尔会将预期操作描述为文本，而不是进行工具调用。工具使用强制会注入指导，引导模型回到实际调用工具。

```yaml
agent:
  tool_use_enforcement: "auto"   # "auto" | true | false | ["model-substring", ...]
```

| 值 | 行为 |
|-------|----------|
| `"auto"`（默认） | 对 GPT 模型（`gpt-`、`openai/gpt-`）启用，对所有其他模型禁用。 |
| `true` | 对所有模型始终启用。 |
| `false` | 始终禁用。 |
| `["gpt-", "o1-", "custom-model"]` | 仅对名称包含所列子字符串之一的模型启用。 |

启用后，系统提示会包含指导，提醒模型进行实际的工具调用，而不是描述它会做什么。这对用户是透明的，并且对已经可靠使用工具的模型没有影响。

## TTS 配置

```yaml
tts:
  provider: "edge"              # "edge" | "elevenlabs" | "openai" | "neutts"
  edge:
    voice: "en-US-AriaNeural"   # 322 种语音，74 种语言
  elevenlabs:
    voice_id: "pNInz6obpgDQGcFmaJgB"
    model_id: "eleven_multilingual_v2"
  openai:
    model: "gpt-4o-mini-tts"
    voice: "alloy"              # alloy, echo, fable, onyx, nova, shimmer
    base_url: "https://api.openai.com/v1"  # 覆盖 OpenAI 兼容的 TTS 端点
  neutts:
    ref_audio: ''
    ref_text: ''
    model: neuphonic/neutts-air-q4-gguf
    device: cpu
```
这同时控制着 `text_to_speech` 工具和语音模式下的语音回复（CLI 或消息网关中的 `/voice tts` 命令）。

## 显示设置 {#display-settings}

```yaml
display:
  tool_progress: all      # off | new | all | verbose
  tool_progress_command: false  # 在消息网关中启用 /verbose 斜杠命令
  skin: default           # 内置或自定义 CLI 皮肤（参见 user-guide/features/skins）
  theme_mode: auto        # auto | light | dark — 支持皮肤感知渲染的色彩方案
  personality: "kawaii"  # 遗留的装饰性字段，仍出现在某些摘要中
  compact: false          # 紧凑输出模式（减少空白）
  resume_display: full    # full（恢复时显示之前的消息）| minimal（仅显示一行摘要）
  bell_on_complete: false # Agent 完成任务时播放终端响铃（适用于长时间任务）
  show_reasoning: false   # 在每个响应上方显示模型推理/思考过程（用 /reasoning show|hide 切换）
  streaming: false        # 令牌到达时实时流式传输到终端
  background_process_notifications: all  # all | result | error | off（仅限网关）
  show_cost: false        # 在 CLI 状态栏显示预估的 $ 成本
```

### 主题模式

`theme_mode` 设置控制皮肤以浅色还是深色模式渲染：

| 模式 | 行为 |
|------|----------|
| `auto` (默认) | 自动检测你的终端背景色。如果检测失败，则回退到 `dark`。 |
| `light` | 强制使用浅色模式皮肤颜色。定义了 `colors_light` 覆盖的皮肤将使用这些颜色，而不是默认的深色模式调色板。 |
| `dark` | 强制使用深色模式皮肤颜色。 |

这适用于任何皮肤——内置的或自定义的。皮肤作者可以在其皮肤定义中提供 `colors_light`，以获得最佳的浅色终端外观。

| 模式 | 你看到的内容 |
|------|-------------|
| `off` | 静默——仅显示最终响应 |
| `new` | 仅在工具变更时显示工具指示器 |
| `all` | 显示每个工具调用及其简短预览（默认） |
| `verbose` | 显示完整的参数、结果和调试日志 |

在 CLI 中，使用 `/verbose` 在这些模式间循环切换。要在消息平台（Telegram、Discord、Slack 等）中使用 `/verbose`，请在上面的 `display` 部分设置 `tool_progress_command: true`。该命令将循环切换模式并保存到配置中。

## 隐私

```yaml
privacy:
  redact_pii: false  # 从 LLM 上下文中剥离个人身份信息（仅限网关）
```

当 `redact_pii` 为 `true` 时，网关会在将系统提示发送给 LLM 之前，从支持的平台中删除个人身份信息：

| 字段 | 处理方式 |
|-------|-----------|
| 电话号码（WhatsApp/Signal 上的用户 ID） | 哈希化为 `user_<12-char-sha256>` |
| 用户 ID | 哈希化为 `user_<12-char-sha256>` |
| 聊天 ID | 数字部分被哈希化，平台前缀保留（`telegram:<hash>`） |
| 主频道 ID | 数字部分被哈希化 |
| 用户姓名 / 用户名 | **不受影响**（用户选择，公开可见） |

**平台支持：** 去标识化适用于 WhatsApp、Signal 和 Telegram。Discord 和 Slack 被排除在外，因为它们的提及系统（`<@user_id>`）需要在 LLM 上下文中使用真实的 ID。

哈希是确定性的——同一用户始终映射到同一哈希值，因此模型仍能区分群聊中的不同用户。路由和投递在内部使用原始值。

## 语音转文本 (STT)

```yaml
stt:
  provider: "local"            # "local" | "groq" | "openai"
  local:
    model: "base"              # tiny, base, small, medium, large-v3
  openai:
    model: "whisper-1"         # whisper-1 | gpt-4o-mini-transcribe | gpt-4o-transcribe
  # model: "whisper-1"         # 遗留的回退键，仍被支持
```

提供商行为：

- `local` 使用在你机器上运行的 `faster-whisper`。请使用 `pip install faster-whisper` 单独安装。
- `groq` 使用 Groq 的 Whisper 兼容端点，并读取 `GROQ_API_KEY`。
- `openai` 使用 OpenAI 语音 API，并读取 `VOICE_TOOLS_OPENAI_KEY`。

如果请求的提供商不可用，Hermes 会自动按此顺序回退：`local` → `groq` → `openai`。

Groq 和 OpenAI 的模型覆盖由环境变量驱动：

```bash
STT_GROQ_MODEL=whisper-large-v3-turbo
STT_OPENAI_MODEL=whisper-1
GROQ_BASE_URL=https://api.groq.com/openai/v1
STT_OPENAI_BASE_URL=https://api.openai.com/v1
```

## 语音模式 (CLI)

```yaml
voice:
  record_key: "ctrl+b"         # CLI 内的按键通话键
  max_recording_seconds: 120    # 长时间录音的硬性停止限制
  auto_tts: false               # 当 /voice on 时自动启用语音回复
  silence_threshold: 200        # 语音检测的 RMS 阈值
  silence_duration: 3.0         # 自动停止前的静音秒数
```

在 CLI 中使用 `/voice on` 启用麦克风模式，使用 `record_key` 开始/停止录音，使用 `/voice tts` 切换语音回复。有关端到端设置和平台特定行为，请参阅[语音模式](/user-guide/features/voice-mode)。

## 流式传输

将令牌实时流式传输到终端或消息平台，而不是等待完整响应。

### CLI 流式传输

```yaml
display:
  streaming: true         # 实时将令牌流式传输到终端
  show_reasoning: true    # 同时流式传输推理/思考令牌（可选）
```

启用后，响应会在一个流式传输框内逐个令牌地显示。工具调用仍会被静默捕获。如果提供商不支持流式传输，它会自动回退到正常显示。

### 网关流式传输 (Telegram, Discord, Slack)

```yaml
streaming:
  enabled: true           # 启用渐进式消息编辑
  edit_interval: 0.3      # 消息编辑之间的秒数
  buffer_threshold: 40    # 强制刷新编辑前累积的字符数
  cursor: " ▉"            # 流式传输期间显示的光标
```

启用后，机器人会在第一个令牌到达时发送一条消息，然后随着更多令牌到达逐步编辑它。不支持消息编辑的平台（Signal、Email）会优雅地跳过流式传输，正常发送最终响应。

:::note
流式传输默认是禁用的。在 `~/.hermes/config.yaml` 中启用它以体验流式传输的用户界面。
:::

## 群聊会话隔离

控制共享聊天是每个房间保持一个对话，还是每个参与者保持一个对话：

```yaml
group_sessions_per_user: true  # true = 在群组/频道中按用户隔离，false = 每个聊天一个共享会话
```

- `true` 是默认且推荐的设置。在 Discord 频道、Telegram 群组、Slack 频道等共享上下文中，当平台提供用户 ID 时，每个发送者都会获得自己的会话。
- `false` 会恢复到旧的共享房间行为。如果你明确希望 Hermes 将频道视为一个协作对话，这可能有用，但这也意味着用户共享上下文、令牌成本和中断状态。
- 私信不受影响。Hermes 仍会像往常一样按聊天/DM ID 来区分私信。
- 无论哪种方式，线程都与其父频道保持隔离；当设置为 `true` 时，每个参与者在线程内也拥有自己的会话。

有关行为细节和示例，请参阅[会话](/user-guide/sessions)和 [Discord 指南](/user-guide/messaging/discord)。

## 未授权私信行为

控制当未知用户发送私信时 Hermes 的行为：

```yaml
unauthorized_dm_behavior: pair

whatsapp:
  unauthorized_dm_behavior: ignore
```

- `pair` 是默认值。Hermes 拒绝访问，但会在私信中回复一个一次性配对码。
- `ignore` 静默丢弃未授权的私信。
- 平台部分会覆盖全局默认值，因此你可以在广泛启用配对的同时，让某个平台保持安静。

## 快捷命令 {#quick-commands}

定义自定义命令，这些命令运行 shell 命令而无需调用 LLM——零令牌消耗，即时执行。特别适用于从消息平台（Telegram、Discord 等）进行快速的服务器检查或实用脚本。

```yaml
quick_commands:
  status:
    type: exec
    command: systemctl status hermes-agent
  disk:
    type: exec
    command: df -h /
  update:
    type: exec
    command: cd ~/.hermes/hermes-agent && git pull && pip install -e .
  gpu:
    type: exec
    command: nvidia-smi --query-gpu=name,utilization.gpu,memory.used,memory.total --format=csv,noheader
```

用法：在 CLI 或任何消息平台中输入 `/status`、`/disk`、`/update` 或 `/gpu`。命令在主机上本地运行并直接返回输出——无需 LLM 调用，不消耗令牌。

- **30 秒超时** — 长时间运行的命令会被终止并显示错误消息
- **优先级** — 快捷命令在技能命令之前被检查，因此你可以覆盖技能名称
- **自动补全** — 快捷命令在调度时解析，不会显示在内置的斜杠命令自动补全表中
- **类型** — 仅支持 `exec`（运行 shell 命令）；其他类型会显示错误
- **随处可用** — CLI、Telegram、Discord、Slack、WhatsApp、Signal、Email、Home Assistant

## 网关流式传输

在消息平台上启用渐进式令牌传递。启用流式传输后，响应会通过消息编辑在 Telegram、Discord 和 Slack 中逐字符显示，而不是等待完整响应。

```yaml
streaming:
  enabled: false              # 启用流式令牌传递（默认：关闭）
  transport: edit             # "edit"（渐进式消息编辑）或 "off"
  edit_interval: 0.3          # 消息编辑之间的最小秒数
  buffer_threshold: 40        # 强制进行编辑前累积的字符数
  cursor: " ▉"               # 流式传输期间显示的光标字符
```

**平台支持：** Telegram、Discord 和 Slack 支持基于编辑的流式传输。不支持消息编辑的平台（Signal、Email、Home Assistant）会在首次尝试时自动检测——流式传输会优雅地在该会话中被禁用，不会产生消息洪流。

**溢出处理：** 如果流式传输的文本超过平台的消息长度限制（约 4096 个字符），当前消息会被最终确定，并自动开始一个新消息。

## 人工延迟

在消息平台中模拟类人的响应节奏：

```yaml
human_delay:
  mode: "off"                  # off | natural | custom
  min_ms: 800                  # 最小延迟（自定义模式）
  max_ms: 2500                 # 最大延迟（自定义模式）
```

## 代码执行

配置沙盒化的 Python 代码执行工具：

```yaml
code_execution:
  timeout: 300                 # 最大执行时间（秒）
  max_tool_calls: 50           # 代码执行内的最大工具调用次数
```

## 网络搜索后端

`web_search`、`web_extract` 和 `web_crawl` 工具支持三个后端提供商。在 `config.yaml` 中或通过 `hermes tools` 配置后端：

```yaml
web:
  backend: firecrawl    # firecrawl | parallel | tavily
```

| 后端 | 环境变量 | 搜索 | 提取 | 爬取 |
|---------|---------|--------|---------|-------|
| **Firecrawl** (默认) | `FIRECRAWL_API_KEY` | ✔ | ✔ | ✔ |
| **Parallel** | `PARALLEL_API_KEY` | ✔ | ✔ | — |
| **Tavily** | `TAVILY_API_KEY` | ✔ | ✔ | ✔ |

**后端选择：** 如果未设置 `web.backend`，则根据可用的 API 密钥自动检测后端。如果只设置了 `TAVILY_API_KEY`，则使用 Tavily。如果只设置了 `PARALLEL_API_KEY`，则使用 Parallel。否则 Firecrawl 是默认值。

**自托管的 Firecrawl：** 设置 `FIRECRAWL_API_URL` 指向你自己的实例。设置自定义 URL 后，API 密钥变为可选（在服务器上设置 `USE_DB_AUTHENTICATION=false` 以禁用身份验证）。

**Parallel 搜索模式：** 设置 `PARALLEL_SEARCH_MODE` 来控制搜索行为——`fast`、`one-shot` 或 `agentic`（默认：`agentic`）。

## 浏览器

配置浏览器自动化行为：

```yaml
browser:
  inactivity_timeout: 120        # 自动关闭空闲会话前的秒数
  record_sessions: false         # 自动将浏览器会话录制为 WebM 视频到 ~/.hermes/browser_recordings/
```

浏览器工具集支持多个提供商。有关 Browserbase、Browser Use 和本地 Chrome CDP 设置的详细信息，请参阅[浏览器功能页面](/user-guide/features/browser)。
## 网站黑名单 {#website-blocklist}

阻止 Agent 的网络和浏览器工具访问特定域名：

```yaml
security:
  website_blocklist:
    enabled: false               # 启用 URL 阻止功能（默认：false）
    domains:                     # 被阻止的域名模式列表
      - "*.internal.company.com"
      - "admin.example.com"
      - "*.local"
    shared_files:                # 从外部文件加载额外规则
      - "/etc/hermes/blocked-sites.txt"
```

启用后，任何匹配被阻止域名模式的 URL 都会在网络或浏览器工具执行前被拒绝。这适用于 `web_search`、`web_extract`、`browser_navigate` 以及任何访问 URL 的工具。

域名规则支持：
- 精确域名：`admin.example.com`
- 通配符子域名：`*.internal.company.com`（阻止所有子域名）
- TLD 通配符：`*.local`

共享文件每行包含一个域名规则（空行和以 `#` 开头的注释行会被忽略）。缺失或无法读取的文件会记录警告，但不会禁用其他网络工具。

策略会缓存 30 秒，因此配置更改无需重启即可快速生效。

## 智能审批

控制 Hermes 如何处理潜在危险的命令：

```yaml
approvals:
  mode: manual   # manual | smart | off
```

| 模式 | 行为 |
|------|----------|
| `manual`（默认） | 在执行任何被标记的命令前提示用户。在 CLI 中，显示交互式审批对话框。在消息传递中，将审批请求加入队列。 |
| `smart` | 使用辅助 LLM 来评估被标记的命令是否确实危险。低风险命令会自动批准，并在会话级别保持持久性。真正有风险的命令会升级给用户处理。 |
| `off` | 跳过所有审批检查。等同于 `HERMES_YOLO_MODE=true`。**请谨慎使用。** |

智能模式对于减少审批疲劳特别有用——它让 Agent 在安全操作上更自主地工作，同时仍能捕获真正具有破坏性的命令。

:::warning
设置 `approvals.mode: off` 会禁用终端命令的所有安全检查。仅在受信任的沙盒环境中使用此设置。
:::

## 检查点

在执行破坏性文件操作前自动创建文件系统快照。详情请参阅[检查点功能页面](/user-guide/features/checkpoints)。

```yaml
checkpoints:
  enabled: true                  # 启用自动检查点（也可用：hermes --checkpoints）
  max_snapshots: 50              # 每个目录保留的最大检查点数
```

## 委派

为委派工具配置子 Agent 行为：

```yaml
delegation:
  # model: "google/gemini-3-flash-preview"  # 覆盖模型（空 = 继承父级）
  # provider: "openrouter"                  # 覆盖提供商（空 = 继承父级）
  # base_url: "http://localhost:1234/v1"    # 直接的 OpenAI 兼容端点（优先于 provider）
  # api_key: "local-key"                    # base_url 的 API 密钥（回退到 OPENAI_API_KEY）
```

**子 Agent provider:model 覆盖：** 默认情况下，子 Agent 继承父 Agent 的提供商和模型。设置 `delegation.provider` 和 `delegation.model` 可以将子 Agent 路由到不同的提供商:模型组合——例如，为主 Agent 使用昂贵/复杂的推理模型，而为范围狭窄的子任务使用廉价/快速的模型。

**直接端点覆盖：** 如果你想要明显的自定义端点路径，请设置 `delegation.base_url`、`delegation.api_key` 和 `delegation.model`。这将直接把子 Agent 发送到该 OpenAI 兼容端点，并优先于 `delegation.provider`。如果省略 `delegation.api_key`，Hermes 仅回退到 `OPENAI_API_KEY`。

委派提供商使用与 CLI/网关启动相同的凭据解析机制。支持所有已配置的提供商：`openrouter`、`nous`、`copilot`、`zai`、`kimi-coding`、`minimax`、`minimax-cn`。设置提供商后，系统会自动解析正确的基础 URL、API 密钥和 API 模式——无需手动连接凭据。

**优先级：** 配置中的 `delegation.base_url` → 配置中的 `delegation.provider` → 父级提供商（继承）。配置中的 `delegation.model` → 父级模型（继承）。仅设置 `model` 而不设置 `provider` 只会更改模型名称，同时保留父级的凭据（对于在同一提供商内切换模型很有用，例如 OpenRouter）。

## 澄清

配置澄清提示行为：

```yaml
clarify:
  timeout: 120                 # 等待用户澄清响应的秒数
```

## 上下文文件（SOUL.md, AGENTS.md）

Hermes 使用两种不同的上下文作用域：

| 文件 | 用途 | 作用域 |
|------|---------|-------|
| `SOUL.md` | **主要 Agent 身份**——定义 Agent 是谁（系统提示中的槽位 #1） | `~/.hermes/SOUL.md` 或 `$HERMES_HOME/SOUL.md` |
| `.hermes.md` / `HERMES.md` | 项目特定指令（最高优先级） | 向上遍历到 git 根目录 |
| `AGENTS.md` | 项目特定指令，编码规范 | 递归目录遍历 |
| `CLAUDE.md` | Claude Code 上下文文件（也会被检测） | 仅工作目录 |
| `.cursorrules` | Cursor IDE 规则（也会被检测） | 仅工作目录 |
| `.cursor/rules/*.mdc` | Cursor 规则文件（也会被检测） | 仅工作目录 |

- **SOUL.md** 是 Agent 的主要身份。它占据系统提示中的槽位 #1，完全替换内置的默认身份。编辑它以完全自定义 Agent 的身份。
- 如果 SOUL.md 缺失、为空或无法加载，Hermes 会回退到内置的默认身份。
- **项目上下文文件使用优先级系统**——只加载一种类型（首次匹配优先）：`.hermes.md` → `AGENTS.md` → `CLAUDE.md` → `.cursorrules`。SOUL.md 总是独立加载。
- **AGENTS.md** 是分层的：如果子目录也有 AGENTS.md，则所有文件都会被合并。
- 如果不存在 SOUL.md，Hermes 会自动生成一个默认的 `SOUL.md`。
- 所有加载的上下文文件都限制在 20,000 个字符以内，并进行智能截断。

另请参阅：
- [个性与 SOUL.md](/user-guide/features/personality)
- [上下文文件](/user-guide/features/context-files)

## 工作目录

| 上下文 | 默认值 |
|---------|---------|
| **CLI (`hermes`)** | 运行命令的当前目录 |
| **消息传递网关** | 主目录 `~`（可通过 `MESSAGING_CWD` 覆盖） |
| **Docker / Singularity / Modal / SSH** | 容器或远程机器内的用户主目录 |

覆盖工作目录：
```bash
# 在 ~/.hermes/.env 或 ~/.hermes/config.yaml 中：
MESSAGING_CWD=/home/myuser/projects    # 网关会话
TERMINAL_CWD=/workspace                # 所有终端会话
```
