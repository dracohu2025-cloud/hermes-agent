---
title: "AI 提供商"
sidebar_label: "AI 提供商"
sidebar_position: 1
---

# AI 提供商

本页面涵盖了为 Hermes Agent 设置推理提供商的相关内容——从 OpenRouter 和 Anthropic 等云端 API，到 Ollama 和 vLLM 等自托管端点，再到高级路由和回退配置。要使用 Hermes，你至少需要配置一个提供商。

## 推理提供商

你需要至少一种连接到 LLM 的方式。使用 `hermes model` 以交互方式切换提供商和模型，或者直接进行配置：

| 提供商 | 设置方式 |
|----------|-------|
| **Nous Portal** | `hermes model` (OAuth，基于订阅) |
| **OpenAI Codex** | `hermes model` (ChatGPT OAuth，使用 Codex 模型) |
| **GitHub Copilot** | `hermes model` (OAuth 设备代码流，`COPILOT_GITHUB_TOKEN`，`GH_TOKEN`，或 `gh auth token`) |
| **GitHub Copilot ACP** | `hermes model` (启动本地 `copilot --acp --stdio`) |
| **Anthropic** | `hermes model` (通过 Claude Code 认证的 Claude Pro/Max，Anthropic API key，或手动 setup-token) |
| **OpenRouter** | 在 `~/.hermes/.env` 中设置 `OPENROUTER_API_KEY` |
| **AI Gateway** | 在 `~/.hermes/.env` 中设置 `AI_GATEWAY_API_KEY` (提供商: `ai-gateway`) |
| **z.ai / GLM** | 在 `~/.hermes/.env` 中设置 `GLM_API_KEY` (提供商: `zai`) |
| **Kimi / Moonshot** | 在 `~/.hermes/.env` 中设置 `KIMI_API_KEY` (提供商: `kimi-coding`) |
| **MiniMax** | 在 `~/.hermes/.env` 中设置 `MINIMAX_API_KEY` (提供商: `minimax`) |
| **MiniMax China** | 在 `~/.hermes/.env` 中设置 `MINIMAX_CN_API_KEY` (提供商: `minimax-cn`) |
| **Alibaba Cloud** | 在 `~/.hermes/.env` 中设置 `DASHSCOPE_API_KEY` (提供商: `alibaba`，别名: `dashscope`, `qwen`) |
| **Kilo Code** | 在 `~/.hermes/.env` 中设置 `KILOCODE_API_KEY` (提供商: `kilocode`) |
| **OpenCode Zen** | 在 `~/.hermes/.env` 中设置 `OPENCODE_ZEN_API_KEY` (提供商: `opencode-zen`) |
| **OpenCode Go** | 在 `~/.hermes/.env` 中设置 `OPENCODE_GO_API_KEY` (提供商: `opencode-go`) |
| **DeepSeek** | 在 `~/.hermes/.env` 中设置 `DEEPSEEK_API_KEY` (提供商: `deepseek`) |
| **Hugging Face** | 在 `~/.hermes/.env` 中设置 `HF_TOKEN` (提供商: `huggingface`，别名: `hf`) |
| **Google / Gemini** | 在 `~/.hermes/.env` 中设置 `GOOGLE_API_KEY` (或 `GEMINI_API_KEY`) (提供商: `gemini`) |
| **Custom Endpoint** | `hermes model` → 选择 "Custom endpoint" (保存在 `config.yaml` 中) |

:::tip 模型键别名
在 `model:` 配置部分，你可以使用 `default:` 或 `model:` 作为模型 ID 的键名。`model: { default: my-model }` 和 `model: { model: my-model }` 的效果完全相同。
:::

:::info Codex 说明
OpenAI Codex 提供商通过设备代码进行认证（打开 URL，输入代码）。Hermes 会将生成的凭据存储在自己的认证存储中（位于 `~/.hermes/auth.json`），并且在存在时可以导入现有的 Codex CLI 凭据（来自 `~/.codex/auth.json`）。无需安装 Codex CLI。
:::

:::warning
即使在使用 Nous Portal、Codex 或自定义端点时，某些工具（视觉、网页摘要、MoA）也会使用单独的“辅助”模型——默认情况下是通过 OpenRouter 使用 Gemini Flash。配置 `OPENROUTER_API_KEY` 可自动启用这些工具。你也可以配置这些工具使用的模型和提供商——请参阅 [辅助模型](/user-guide/configuration#auxiliary-models)。
:::

### Anthropic (原生)

直接通过 Anthropic API 使用 Claude 模型——无需 OpenRouter 代理。支持三种认证方式：

```bash
# 使用 API key (按 token 付费)
export ANTHROPIC_API_KEY=***
hermes chat --provider anthropic --model claude-sonnet-4-6

# 推荐：通过 `hermes model` 进行认证
# Hermes 将在可用时直接使用 Claude Code 的凭据存储
hermes model

# 使用 setup-token 手动覆盖 (回退 / 旧版)
export ANTHROPIC_TOKEN=***  # setup-token 或手动 OAuth token
hermes chat --provider anthropic

# 自动检测 Claude Code 凭据 (如果你已经在使用 Claude Code)
hermes chat --provider anthropic  # 自动读取 Claude Code 凭据文件
```

当你通过 `hermes model` 选择 Anthropic OAuth 时，Hermes 会优先使用 Claude Code 自己的凭据存储，而不是将 token 复制到 `~/.hermes/.env` 中。这样可以保持 Claude 凭据的可刷新性。

或者进行永久设置：
```yaml
model:
  provider: "anthropic"
  default: "claude-sonnet-4-6"
```

:::tip 别名
`--provider claude` 和 `--provider claude-code` 也可以作为 `--provider anthropic` 的简写使用。
:::

### GitHub Copilot

Hermes 将 GitHub Copilot 作为一等提供商支持，并提供两种模式：

**`copilot` — 直接 Copilot API** (推荐)。使用你的 GitHub Copilot 订阅，通过 Copilot API 访问 GPT-5.x、Claude、Gemini 等模型。

```bash
hermes chat --provider copilot --model gpt-5.4
```

**认证选项** (按此顺序检查)：

1. `COPILOT_GITHUB_TOKEN` 环境变量
2. `GH_TOKEN` 环境变量
3. `GITHUB_TOKEN` 环境变量
4. `gh auth token` CLI 回退

如果未找到 token，`hermes model` 会提供 **OAuth 设备代码登录**——这与 Copilot CLI 和 opencode 使用的流程相同。

:::warning Token 类型
Copilot API **不**支持传统的个人访问令牌 (Personal Access Tokens, `ghp_*`)。支持的 token 类型：

| 类型 | 前缀 | 获取方式 |
|------|--------|------------|
| OAuth token | `gho_` | `hermes model` → GitHub Copilot → 使用 GitHub 登录 |
| 细粒度 PAT | `github_pat_` | GitHub 设置 → 开发者设置 → 细粒度令牌 (需要 **Copilot Requests** 权限) |
| GitHub App token | `ghu_` | 通过 GitHub App 安装 |

如果你的 `gh auth token` 返回的是 `ghp_*` 令牌，请使用 `hermes model` 通过 OAuth 进行认证。
:::

**API 路由**：GPT-5+ 模型（`gpt-5-mini` 除外）会自动使用 Responses API。所有其他模型（GPT-4o、Claude、Gemini 等）使用 Chat Completions。模型会从实时的 Copilot 目录中自动检测。

**`copilot-acp` — Copilot ACP Agent 后端**。将本地 Copilot CLI 作为子进程启动：

```bash
hermes chat --provider copilot-acp --model copilot-acp
# 需要 PATH 中存在 GitHub Copilot CLI 且有现有的 `copilot login` 会话
```

**永久配置：**
```yaml
model:
  provider: "copilot"
  default: "gpt-5.4"
```

| 环境变量 | 描述 |
|---------------------|-------------|
| `COPILOT_GITHUB_TOKEN` | 用于 Copilot API 的 GitHub 令牌 (第一优先级) |
| `HERMES_COPILOT_ACP_COMMAND` | 覆盖 Copilot CLI 二进制路径 (默认: `copilot`) |
| `HERMES_COPILOT_ACP_ARGS` | 覆盖 ACP 参数 (默认: `--acp --stdio`) |

### 一等中文 AI 提供商

这些提供商内置了支持，并拥有专门的提供商 ID。设置 API key 并使用 `--provider` 进行选择：

```bash
# z.ai / 智谱 AI GLM
hermes chat --provider zai --model glm-5
# 需要: ~/.hermes/.env 中的 GLM_API_KEY

# Kimi / Moonshot AI
hermes chat --provider kimi-coding --model kimi-for-coding
# 需要: ~/.hermes/.env 中的 KIMI_API_KEY

# MiniMax (全球端点)
hermes chat --provider minimax --model MiniMax-M2.7
# 需要: ~/.hermes/.env 中的 MINIMAX_API_KEY

# MiniMax (中国端点)
hermes chat --provider minimax-cn --model MiniMax-M2.7
# 需要: ~/.hermes/.env 中的 MINIMAX_CN_API_KEY

# 阿里云 / DashScope (通义千问模型)
hermes chat --provider alibaba --model qwen3.5-plus
# 需要: ~/.hermes/.env 中的 DASHSCOPE_API_KEY
```

或者在 `config.yaml` 中永久设置提供商：
```yaml
model:
  provider: "zai"       # 或: kimi-coding, minimax, minimax-cn, alibaba
  default: "glm-5"
```

可以使用 `GLM_BASE_URL`、`KIMI_BASE_URL`、`MINIMAX_BASE_URL`、`MINIMAX_CN_BASE_URL` 或 `DASHSCOPE_BASE_URL` 环境变量来覆盖基础 URL。

:::note Z.AI 端点自动检测
当使用 Z.AI / GLM 提供商时，Hermes 会自动探测多个端点（全球、中国、编程变体），以找到接受你 API key 的端点。你无需手动设置 `GLM_BASE_URL`——有效的端点会被自动检测并缓存。
:::

### xAI (Grok) Prompt 缓存

当使用 xAI 作为提供商（任何包含 `x.ai` 的基础 URL）时，Hermes 会通过在每个 API 请求中发送 `x-grok-conv-id` 标头来自动启用 Prompt 缓存。这会将请求路由到对话会话中的同一服务器，从而允许 xAI 的基础设施重用缓存的系统提示词和对话历史记录。
无需任何配置——当检测到 xAI 端点且会话 ID 可用时，缓存功能会自动激活。这减少了多轮对话的延迟并降低了成本。

### Hugging Face Inference Providers

[Hugging Face Inference Providers](https://huggingface.co/docs/inference-providers) 通过统一的 OpenAI 兼容端点 (`router.huggingface.co/v1`) 路由至 20 多种开源模型。请求会自动路由到速度最快的可用后端（如 Groq、Together、SambaNova 等），并具备自动故障转移功能。

```bash
# 使用任何可用模型
hermes chat --provider huggingface --model Qwen/Qwen3-235B-A22B-Thinking-2507
# 需要：~/.hermes/.env 中的 HF_TOKEN

# 简短别名
hermes chat --provider hf --model deepseek-ai/DeepSeek-V3.2
```

或者在 `config.yaml` 中永久设置：
```yaml
model:
  provider: "huggingface"
  default: "Qwen/Qwen3-235B-A22B-Thinking-2507"
```

请在 [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) 获取你的令牌，并确保启用了“Make calls to Inference Providers”权限。包含免费层级（每月 0.10 美元额度，提供商费率无加价）。

你可以在模型名称后附加路由后缀：`:fastest`（默认）、`:cheapest` 或 `:provider_name` 以强制使用特定后端。

基础 URL 可以通过 `HF_BASE_URL` 进行覆盖。

## 自定义及自托管 LLM 提供商

Hermes Agent 适用于**任何兼容 OpenAI 的 API 端点**。如果服务器实现了 `/v1/chat/completions`，你就可以将 Hermes 指向它。这意味着你可以使用本地模型、GPU 推理服务器、多提供商路由器或任何第三方 API。

### 常规设置

配置自定义端点有三种方式：

**交互式设置（推荐）：**
```bash
hermes model
# 选择 "Custom endpoint (self-hosted / VLLM / etc.)"
# 输入：API 基础 URL、API 密钥、模型名称
```

**手动配置 (`config.yaml`)：**
```yaml
# 在 ~/.hermes/config.yaml 中
model:
  default: your-model-name
  provider: custom
  base_url: http://localhost:8000/v1
  api_key: your-key-or-leave-empty-for-local
```

:::warning 遗留环境变量
`.env` 中的 `OPENAI_BASE_URL` 和 `LLM_MODEL` 已被**移除**。Hermes 的任何部分都不会读取它们——`config.yaml` 是模型和端点配置的唯一事实来源。如果你的 `.env` 中有陈旧条目，它们会在下次执行 `hermes setup` 或配置迁移时自动清除。请使用 `hermes model` 或直接编辑 `config.yaml`。
:::

这两种方法都会持久化到 `config.yaml`，它是模型、提供商和基础 URL 的事实来源。

### 使用 `/model` 切换模型

配置好自定义端点后，你可以在会话中途切换模型：

```
/model custom:qwen-2.5          # 切换到自定义端点上的模型
/model custom                    # 从端点自动检测模型
/model openrouter:claude-sonnet-4 # 切换回云端提供商
```

如果你配置了**命名自定义提供商**（见下文），请使用三段式语法：

```
/model custom:local:qwen-2.5    # 使用名为 "local" 的自定义提供商及 qwen-2.5 模型
/model custom:work:llama3       # 使用名为 "work" 的自定义提供商及 llama3 模型
```

切换提供商时，Hermes 会将基础 URL 和提供商持久化到配置中，以便重启后依然生效。当从自定义端点切换到内置提供商时，陈旧的基础 URL 会自动清除。

:::tip
`/model custom`（仅命令，不带模型名称）会查询你端点的 `/models` API，如果恰好加载了一个模型，它会自动选中该模型。这对于运行单个模型的本地服务器非常有用。
:::

以下所有内容都遵循相同的模式——只需更改 URL、密钥和模型名称即可。

---

### Ollama — 本地模型，零配置

[Ollama](https://ollama.com/) 可以通过一条命令在本地运行开源权重模型。适用于：快速本地实验、隐私敏感工作、离线使用。支持通过 OpenAI 兼容 API 进行工具调用。

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
# 输入模型名称 (例如 qwen2.5-coder:32b)
```

或者直接配置 `config.yaml`：

```yaml
model:
  default: qwen2.5-coder:32b
  provider: custom
  base_url: http://localhost:11434/v1
  context_length: 32768   # 见下方警告
```

:::caution Ollama 默认上下文长度非常短
Ollama 默认**不会**使用模型的完整上下文窗口。根据你的显存（VRAM），默认值为：

| 可用显存 | 默认上下文 |
|----------------|----------------|
| 小于 24 GB | **4,096 tokens** |
| 24–48 GB | 32,768 tokens |
| 48+ GB | 256,000 tokens |

对于使用工具的 Agent 场景，**你需要至少 16k–32k 的上下文**。在 4k 下，仅系统提示词 + 工具架构就能填满窗口，导致对话空间不足。

**如何增加它**（任选其一）：

```bash
# 选项 1：通过环境变量设置服务器全局配置（推荐）
OLLAMA_CONTEXT_LENGTH=32768 ollama serve

# 选项 2：针对 systemd 管理的 Ollama
sudo systemctl edit ollama.service
# 添加: Environment="OLLAMA_CONTEXT_LENGTH=32768"
# 然后: sudo systemctl daemon-reload && sudo systemctl restart ollama

# 选项 3：将其写入自定义模型（每个模型持久化）
echo -e "FROM qwen2.5-coder:32b\nPARAMETER num_ctx 32768" > Modelfile
ollama create qwen2.5-coder-32k -f Modelfile
```

**你无法通过 OpenAI 兼容 API** (`/v1/chat/completions`) 设置上下文长度。它必须在服务器端或通过 Modelfile 配置。这是将 Ollama 与 Hermes 等工具集成时最常见的困惑来源。
:::

**验证你的上下文设置是否正确：**

```bash
ollama ps
# 查看 CONTEXT 列 — 它应该显示你配置的值
```

:::tip
使用 `ollama list` 列出可用模型。使用 `ollama pull <model>` 从 [Ollama 库](https://ollama.com/library) 拉取任何模型。Ollama 会自动处理 GPU 卸载——大多数设置无需额外配置。
:::

---

### vLLM — 高性能 GPU 推理

[vLLM](https://docs.vllm.ai/) 是生产环境 LLM 服务的事实标准。适用于：GPU 硬件上的最大吞吐量、大型模型服务、连续批处理。

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
# 跳过 API 密钥（如果你用 --api-key 配置了 vLLM，则输入密钥）
# 输入模型名称: meta-llama/Llama-3.1-70B-Instruct
```

**上下文长度：** vLLM 默认读取模型的 `max_position_embeddings`。如果超过了 GPU 内存，它会报错并要求你调低 `--max-model-len`。你也可以使用 `--max-model-len auto` 自动寻找适合的最大值。设置 `--gpu-memory-utilization 0.95`（默认 0.9）可以将更多上下文挤入显存。

**工具调用需要显式标志：**

| 标志 | 用途 |
|------|---------|
| `--enable-auto-tool-choice` | `tool_choice: "auto"`（Hermes 默认值）所必需 |
| `--tool-call-parser <name>` | 模型工具调用格式的解析器 |

支持的解析器：`hermes` (Qwen 2.5, Hermes 2/3), `llama3_json` (Llama 3.x), `mistral`, `deepseek_v3`, `deepseek_v31`, `xlam`, `pythonic`。没有这些标志，工具调用将无法工作——模型会以文本形式输出工具调用。

:::tip
vLLM 支持人类可读的尺寸：`--max-model-len 64k`（小写 k = 1000，大写 K = 1024）。
:::

---

### SGLang — 基于 RadixAttention 的快速服务

[SGLang](https://github.com/sgl-project/sglang) 是 vLLM 的替代方案，具有用于 KV 缓存重用的 RadixAttention。适用于：多轮对话（前缀缓存）、约束解码、结构化输出。

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

**上下文长度：** SGLang 默认会读取模型的配置。使用 `--context-length` 可以覆盖此设置。如果你需要超过模型声明的最大长度，请设置 `SGLANG_ALLOW_OVERWRITE_LONGER_CONTEXT_LEN=1`。

**工具调用：** 使用 `--tool-call-parser` 并为你的模型系列选择合适的解析器：`qwen` (Qwen 2.5)、`llama3`、`llama4`、`deepseekv3`、`mistral`、`glm`。如果不加此标志，工具调用将以纯文本形式返回。

:::caution SGLang 默认最大输出 token 为 128
如果响应看起来被截断了，请在请求中添加 `max_tokens`，或者在服务器端设置 `--default-max-tokens`。如果请求中未指定，SGLang 默认每个响应仅输出 128 个 token。
:::

---

### llama.cpp / llama-server — CPU 与 Metal 推理

[llama.cpp](https://github.com/ggml-org/llama.cpp) 可在 CPU、Apple Silicon (Metal) 和消费级 GPU 上运行量化模型。最适合：在没有数据中心级 GPU 的情况下运行模型、Mac 用户、边缘部署。

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

**上下文长度 (`-c`)：** 近期的构建版本默认值为 `0`，即从 GGUF 元数据中读取模型的训练上下文。对于训练上下文在 128k 以上的模型，这可能会因尝试分配完整的 KV 缓存而导致内存溢出 (OOM)。请根据需要显式设置 `-c`（对于 Agent 使用场景，32k–64k 是一个不错的范围）。如果使用并行槽位 (`-np`)，总上下文会被分配给各个槽位——例如使用 `-c 32768 -np 4` 时，每个槽位仅获得 8k。

然后配置 Hermes 指向它：

```bash
hermes model
# 选择 "Custom endpoint (self-hosted / VLLM / etc.)"
# 输入 URL: http://localhost:8080/v1
# 跳过 API key（本地服务器不需要）
# 输入模型名称 — 如果只加载了一个模型，也可以留空以自动检测
```

这会将端点保存到 `config.yaml`，以便在不同会话间持久生效。

:::caution 工具调用必须使用 `--jinja`
如果不加 `--jinja`，llama-server 会完全忽略 `tools` 参数。模型会尝试通过在响应文本中写入 JSON 来调用工具，但 Hermes 无法将其识别为工具调用——你会看到原始 JSON（如 `{"name": "web_search", ...}`）作为消息打印出来，而不是实际的搜索操作。

原生工具调用支持（性能最佳）：Llama 3.x、Qwen 2.5 (包括 Coder)、Hermes 2/3、Mistral、DeepSeek、Functionary。所有其他模型使用通用处理程序，虽然有效但效率可能较低。完整列表请参阅 [llama.cpp 函数调用文档](https://github.com/ggml-org/llama.cpp/blob/master/docs/function-calling.md)。

你可以通过检查 `http://localhost:8080/props` 来验证工具支持是否已激活——其中应包含 `chat_template` 字段。
:::

:::tip
从 [Hugging Face](https://huggingface.co/models?library=gguf) 下载 GGUF 模型。Q4_K_M 量化在质量和内存占用之间提供了最佳平衡。
:::

---

### LM Studio — 带有本地模型的桌面应用

[LM Studio](https://lmstudio.ai/) 是一款用于运行本地模型的桌面应用，带有图形界面。最适合：喜欢可视化界面的用户、快速模型测试、macOS/Windows/Linux 开发者。

从 LM Studio 应用启动服务器（Developer 选项卡 → Start Server），或者使用 CLI：

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
LM Studio 会从模型元数据中读取上下文长度，但许多 GGUF 模型报告的默认值很低（2048 或 4096）。**请务必在 LM Studio 模型设置中显式设置上下文长度**：

1. 点击模型选择器旁边的齿轮图标
2. 将 "Context Length" 设置为至少 16384（建议 32768）
3. 重新加载模型以使更改生效

或者，使用 CLI：`lms load model-name --context-length 32768`

若要设置每个模型的持久化默认值：My Models 选项卡 → 模型旁边的齿轮图标 → 设置上下文大小。
:::

**工具调用：** 自 LM Studio 0.3.6 起支持。具有原生工具调用训练的模型（Qwen 2.5、Llama 3.x、Mistral、Hermes）会被自动检测并显示工具徽章。其他模型使用通用回退方案，可靠性可能较低。

---

### WSL2 网络（Windows 用户） {#wsl2-networking-windows-users}

由于 Hermes Agent 需要 Unix 环境，Windows 用户需在 WSL2 中运行它。如果你的模型服务器（Ollama、LM Studio 等）运行在 **Windows 主机**上，你需要桥接网络鸿沟——WSL2 使用带有自己子网的虚拟网络适配器，因此 WSL2 内部的 `localhost` 指的是 Linux 虚拟机，**而不是** Windows 主机。

:::tip 都在 WSL2 中？没问题。
如果你的模型服务器也运行在 WSL2 内部（vLLM、SGLang 和 llama-server 的常见做法），`localhost` 可以按预期工作——它们共享同一个网络命名空间。请跳过此部分。
:::

#### 方案 1：镜像网络模式（推荐）

在 **Windows 11 22H2+** 上可用，镜像模式使 `localhost` 在 Windows 和 WSL2 之间双向互通——这是最简单的修复方法。

1. 创建或编辑 `%USERPROFILE%\.wslconfig` (例如 `C:\Users\YourName\.wslconfig`)：
   ```ini
   [wsl2]
   networkingMode=mirrored
   ```

2. 从 PowerShell 重启 WSL：
   ```powershell
   wsl --shutdown
   ```

3. 重新打开你的 WSL2 终端。现在 `localhost` 可以访问 Windows 服务了：
   ```bash
   curl http://localhost:11434/v1/models   # Windows 上的 Ollama — 可用
   ```

:::note Hyper-V 防火墙
在某些 Windows 11 版本上，Hyper-V 防火墙默认会阻止镜像连接。如果启用镜像模式后 `localhost` 仍然无法工作，请在 **管理员 PowerShell** 中运行以下命令：
```powershell
Set-NetFirewallHyperVVMSetting -Name '{40E0AC32-46A5-438A-A0B2-2B479E8F2E90}' -DefaultInboundAction Allow
```
:::

#### 方案 2：使用 Windows 主机 IP（Windows 10 / 旧版本）

如果你无法使用镜像模式，请从 WSL2 内部找到 Windows 主机 IP，并使用该 IP 代替 `localhost`：

```bash
# 获取 Windows 主机 IP（WSL2 虚拟网络的默认网关）
ip route show | grep -i default | awk '{ print $3 }'
# 输出示例: 172.29.192.1
```

在你的 Hermes 配置中使用该 IP：

```yaml
model:
  default: qwen2.5-coder:32b
  provider: custom
  base_url: http://172.29.192.1:11434/v1   # Windows 主机 IP，而非 localhost
```

:::tip 动态助手
WSL2 重启后主机 IP 可能会改变。你可以在 shell 中动态获取它：
```bash
export WSL_HOST=$(ip route show | grep -i default | awk '{ print $3 }')
echo "Windows host at: $WSL_HOST"
curl http://$WSL_HOST:11434/v1/models   # 测试 Ollama
```

或者使用你机器的 mDNS 名称（需要在 WSL2 中安装 `libnss-mdns`）：
```bash
sudo apt install libnss-mdns
curl http://$(hostname).local:11434/v1/models
```
:::

#### 服务器绑定地址（NAT 模式必需）

如果你使用的是 **方案 2**（带有主机 IP 的 NAT 模式），Windows 上的模型服务器必须接受来自 `127.0.0.1` 以外的连接。默认情况下，大多数服务器仅监听 localhost——NAT 模式下的 WSL2 连接来自不同的虚拟子网，会被拒绝。在镜像模式下，`localhost` 直接映射，因此默认的 `127.0.0.1` 绑定可以正常工作。

| 服务器 | 默认绑定 | 修复方法 |
|--------|-------------|------------|
| **Ollama** | `127.0.0.1` | 启动 Ollama 前设置环境变量 `OLLAMA_HOST=0.0.0.0`（Windows 系统设置 → 环境变量，或编辑 Ollama 服务） |
| **LM Studio** | `127.0.0.1` | 在 Developer 选项卡 → Server 设置中启用 **"Serve on Network"** |
| **llama-server** | `127.0.0.1` | 在启动命令中添加 `--host 0.0.0.0` |
| **vLLM** | `0.0.0.0` | 默认已绑定到所有接口 |
| **SGLang** | `127.0.0.1` | 在启动命令中添加 `--host 0.0.0.0` |
**Ollama on Windows (详细说明)：** Ollama 作为 Windows 服务运行。要设置 `OLLAMA_HOST`：
1. 打开 **系统属性** → **环境变量**
2. 添加一个新的 **系统变量**：`OLLAMA_HOST` = `0.0.0.0`
3. 重启 Ollama 服务（或重启电脑）

#### Windows 防火墙

Windows 防火墙将 WSL2 视为一个独立的网络（在 NAT 和镜像模式下均如此）。如果执行上述步骤后连接仍然失败，请为你的模型服务器端口添加一条防火墙规则：

```powershell
# 在管理员权限的 PowerShell 中运行 — 将 PORT 替换为你服务器的端口
New-NetFirewallRule -DisplayName "Allow WSL2 to Model Server" -Direction Inbound -Action Allow -Protocol TCP -LocalPort 11434
```

常见端口：Ollama `11434`，vLLM `8000`，SGLang `30000`，llama-server `8080`，LM Studio `1234`。

#### 快速验证

在 WSL2 内部，测试是否可以访问你的模型服务器：

```bash
# 将 URL 替换为你服务器的地址和端口
curl http://localhost:11434/v1/models          # 镜像模式
curl http://172.29.192.1:11434/v1/models       # NAT 模式（使用你实际的主机 IP）
```

如果你收到了列出模型的 JSON 响应，说明配置成功。在你的 Hermes 配置中使用相同的 URL 作为 `base_url`。

---

### 本地模型故障排除

这些问题会影响与 Hermes 配合使用的**所有**本地推理服务器。

#### 从 WSL2 到 Windows 托管的模型服务器出现“Connection refused”

如果你在 WSL2 内部运行 Hermes，而模型服务器运行在 Windows 主机上，`http://localhost:<port>` 在 WSL2 的默认 NAT 网络模式下将无法工作。请参阅上方的 [WSL2 网络（Windows 用户）](#wsl2-networking-windows-users) 获取修复方法。

#### 工具调用显示为文本而不是执行

模型输出了类似 `{"name": "web_search", "arguments": {...}}` 的消息，而不是实际调用工具。

**原因：** 你的服务器未启用工具调用功能，或者模型不支持通过该服务器的工具调用实现。

| 服务器 | 修复方法 |
|--------|-----|
| **llama.cpp** | 在启动命令中添加 `--jinja` |
| **vLLM** | 添加 `--enable-auto-tool-choice --tool-call-parser hermes` |
| **SGLang** | 添加 `--tool-call-parser qwen`（或相应的解析器） |
| **Ollama** | 工具调用默认启用 — 请确保你的模型支持它（使用 `ollama show model-name` 检查） |
| **LM Studio** | 更新至 0.3.6+ 并使用支持原生工具调用的模型 |

#### 模型似乎遗忘上下文或给出不连贯的回答

**原因：** 上下文窗口太小。当对话超过上下文限制时，大多数服务器会静默丢弃旧消息。仅 Hermes 的系统提示词 + 工具架构就可能占用 4k–8k tokens。

**诊断：**

```bash
# 检查 Hermes 认为的上下文大小
# 查看启动行："Context limit: X tokens"

# 检查服务器实际的上下文
# Ollama: ollama ps (CONTEXT 列)
# llama.cpp: curl http://localhost:8080/props | jq '.default_generation_settings.n_ctx'
# vLLM: 检查启动参数中的 --max-model-len
```

**修复：** 将上下文设置为至少 **32,768 tokens** 以供 Agent 使用。请参阅上方各服务器对应的章节获取具体参数。

#### 启动时显示 "Context limit: 2048 tokens"

Hermes 会自动从服务器的 `/v1/models` 端点检测上下文长度。如果服务器报告的值较低（或根本不报告），Hermes 会使用模型声明的限制，这可能是错误的。

**修复：** 在 `config.yaml` 中显式设置：

```yaml
model:
  default: your-model
  provider: custom
  base_url: http://localhost:11434/v1
  context_length: 32768
```

#### 回答在句子中间被截断

**可能的原因：**
1. **服务器上的 `max_tokens` 设置过低** — SGLang 默认每次响应限制为 128 tokens。请在服务器上设置 `--default-max-tokens`，或在 `config.yaml` 中配置 Hermes 的 `model.max_tokens`。
2. **上下文耗尽** — 模型填满了上下文窗口。请增加上下文长度或在 Hermes 中启用 [上下文压缩](/user-guide/configuration#context-compression)。

---

### LiteLLM Proxy — 多提供商网关

[LiteLLM](https://docs.litellm.ai/) 是一个兼容 OpenAI 的代理，将 100 多个 LLM 提供商统一在一个 API 之下。最适用于：在不更改配置的情况下切换提供商、负载均衡、故障转移链、预算控制。

```bash
# 安装并启动
pip install "litellm[proxy]"
litellm --model anthropic/claude-sonnet-4 --port 4000

# 或者使用配置文件来管理多个模型：
litellm --config litellm_config.yaml --port 4000
```

然后将 Hermes 配置为 `hermes model` → Custom endpoint → `http://localhost:4000/v1`。

带有故障转移功能的 `litellm_config.yaml` 示例：
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

BlockRunAI 开发的 [ClawRouter](https://github.com/BlockRunAI/ClawRouter) 是一个本地路由代理，可根据查询复杂度自动选择模型。它会对请求进行 14 个维度的分类，并将其路由到能够处理该任务的最便宜模型。通过 USDC 加密货币支付（无需 API 密钥）。

```bash
# 安装并启动
npx @blockrun/clawrouter    # 在 8402 端口启动
```

然后将 Hermes 配置为 `hermes model` → Custom endpoint → `http://localhost:8402/v1` → 模型名称 `blockrun/auto`。

路由配置：
| 配置 | 策略 | 节省比例 |
|---------|----------|---------|
| `blockrun/auto` | 质量与成本平衡 | 74-100% |
| `blockrun/eco` | 最便宜 | 95-100% |
| `blockrun/premium` | 最佳质量模型 | 0% |
| `blockrun/free` | 仅限免费模型 | 100% |
| `blockrun/agentic` | 针对工具使用优化 | 不等 |

:::note
ClawRouter 需要在 Base 或 Solana 上使用充值了 USDC 的钱包进行支付。所有请求均通过 BlockRun 的后端 API 进行路由。运行 `npx @blockrun/clawrouter doctor` 可检查钱包状态。
:::

---

### 其他兼容的提供商

任何具有 OpenAI 兼容 API 的服务均可使用。一些热门选项：

| 提供商 | Base URL | 备注 |
|----------|----------|-------|
| [Together AI](https://together.ai) | `https://api.together.xyz/v1` | 云端托管的开源模型 |
| [Groq](https://groq.com) | `https://api.groq.com/openai/v1` | 超高速推理 |
| [DeepSeek](https://deepseek.com) | `https://api.deepseek.com/v1` | DeepSeek 模型 |
| [Fireworks AI](https://fireworks.ai) | `https://api.fireworks.ai/inference/v1` | 快速开源模型托管 |
| [Cerebras](https://cerebras.ai) | `https://api.cerebras.ai/v1` | 晶圆级芯片推理 |
| [Mistral AI](https://mistral.ai) | `https://api.mistral.ai/v1` | Mistral 模型 |
| [OpenAI](https://openai.com) | `https://api.openai.com/v1` | 直接访问 OpenAI |
| [Azure OpenAI](https://azure.microsoft.com) | `https://YOUR.openai.azure.com/` | 企业级 OpenAI |
| [LocalAI](https://localai.io) | `http://localhost:8080/v1` | 自托管，多模型 |
| [Jan](https://jan.ai) | `http://localhost:1337/v1` | 带有本地模型的桌面应用 |

通过 `hermes model` → Custom endpoint 或在 `config.yaml` 中配置上述任何服务：

```yaml
model:
  default: meta-llama/Llama-3.1-70B-Instruct-Turbo
  provider: custom
  base_url: https://api.together.xyz/v1
  api_key: your-together-key
```

---

### 上下文长度检测 {#context-length-detection}

Hermes 使用多源解析链来检测你的模型和提供商的正确上下文窗口：

1. **配置覆盖** — `config.yaml` 中的 `model.context_length`（最高优先级）
2. **自定义提供商模型配置** — `custom_providers[].models.<id>.context_length`
3. **持久化缓存** — 先前发现的值（重启后依然有效）
4. **端点 `/models`** — 查询你服务器的 API（本地/自定义端点）
5. **Anthropic `/v1/models`** — 查询 Anthropic API 获取 `max_input_tokens`（仅限 API-key 用户）
6. **OpenRouter API** — 来自 OpenRouter 的实时模型元数据
7. **Nous Portal** — 将 Nous 模型 ID 与 OpenRouter 元数据进行后缀匹配
8. **[models.dev](https://models.dev)** — 社区维护的注册表，包含 100 多个提供商下 3800 多个模型的特定上下文长度
9. **回退默认值** — 广泛的模型系列模式（默认 128K）
对于大多数设置，这可以直接开箱即用。系统具备提供商感知能力——同一个模型根据服务方的不同，其上下文限制也可能不同（例如，`claude-opus-4.6` 在 Anthropic 直接调用时为 1M，但在 GitHub Copilot 上则为 128K）。

若要显式设置上下文长度，请在模型配置中添加 `context_length`：

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

在配置自定义端点时，`hermes model` 会提示你输入上下文长度。留空则表示自动检测。

:::tip 何时需要手动设置
- 你正在使用 Ollama，且自定义的 `num_ctx` 低于模型的最大值
- 你希望将上下文限制在模型最大值以下（例如，在 128k 模型上限制为 8k 以节省显存）
- 你运行在不暴露 `/v1/models` 的代理（proxy）之后
:::

---

### 命名自定义提供商

如果你同时使用多个自定义端点（例如，一个本地开发服务器和一个远程 GPU 服务器），可以在 `config.yaml` 中将它们定义为命名自定义提供商：

```yaml
custom_providers:
  - name: local
    base_url: http://localhost:8080/v1
    # api_key 已省略 — Hermes 对无需密钥的本地服务器使用 "no-key-required"
  - name: work
    base_url: https://gpu-server.internal.corp/v1
    api_key: corp-api-key
    api_mode: chat_completions   # 可选，从 URL 自动检测
  - name: anthropic-proxy
    base_url: https://proxy.example.com/anthropic
    api_key: proxy-key
    api_mode: anthropic_messages  # 用于兼容 Anthropic 的代理（proxy）
```

在会话期间，可以使用三段式语法在它们之间切换：

```
/model custom:local:qwen-2.5       # 使用带有 qwen-2.5 的 "local" 端点
/model custom:work:llama3-70b      # 使用带有 llama3-70b 的 "work" 端点
/model custom:anthropic-proxy:claude-sonnet-4  # 使用该代理（proxy）
```

你也可以在交互式的 `hermes model` 菜单中选择已命名的自定义提供商。

---

### 选择合适的配置

| 使用场景 | 推荐方案 |
|----------|-------------|
| **只想直接用** | OpenRouter (默认) 或 Nous Portal |
| **本地模型，易于设置** | Ollama |
| **生产环境 GPU 服务** | vLLM 或 SGLang |
| **Mac / 无 GPU** | Ollama 或 llama.cpp |
| **多提供商路由** | LiteLLM Proxy 或 OpenRouter |
| **成本优化** | ClawRouter 或使用 `sort: "price"` 的 OpenRouter |
| **最大化隐私** | Ollama、vLLM 或 llama.cpp (完全本地) |
| **企业 / Azure** | 带自定义端点的 Azure OpenAI |
| **中文 AI 模型** | z.ai (GLM)、Kimi/Moonshot 或 MiniMax (首选提供商) |

:::tip
你可以随时通过 `hermes model` 在提供商之间切换——无需重启。无论使用哪个提供商，你的对话历史、记忆和技能都会保留。
:::

## 可选 API 密钥

| 功能 | 提供商 | 环境变量 |
|---------|----------|--------------|
| 网页抓取 | [Firecrawl](https://firecrawl.dev/) | `FIRECRAWL_API_KEY`, `FIRECRAWL_API_URL` |
| 浏览器自动化 | [Browserbase](https://browserbase.com/) | `BROWSERBASE_API_KEY`, `BROWSERBASE_PROJECT_ID` |
| 图像生成 | [FAL](https://fal.ai/) | `FAL_KEY` |
| 高级 TTS 语音 | [ElevenLabs](https://elevenlabs.io/) | `ELEVENLABS_API_KEY` |
| OpenAI TTS + 语音转录 | [OpenAI](https://platform.openai.com/api-keys) | `VOICE_TOOLS_OPENAI_KEY` |
| RL 训练 | [Tinker](https://tinker-console.thinkingmachines.ai/) + [WandB](https://wandb.ai/) | `TINKER_API_KEY`, `WANDB_API_KEY` |
| 跨会话用户建模 | [Honcho](https://honcho.dev/) | `HONCHO_API_KEY` |
| 语义长期记忆 | [Supermemory](https://supermemory.ai) | `SUPERMEMORY_API_KEY` |

### 自托管 Firecrawl

默认情况下，Hermes 使用 [Firecrawl 云 API](https://firecrawl.dev/) 进行网页搜索和抓取。如果你更喜欢在本地运行 Firecrawl，可以将 Hermes 指向自托管实例。有关完整设置说明，请参阅 Firecrawl 的 [SELF_HOST.md](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md)。

**优势：** 无需 API 密钥，无速率限制，无单页成本，完全的数据主权。

**劣势：** 云版本使用 Firecrawl 专有的 "Fire-engine" 进行高级反机器人绕过（Cloudflare、CAPTCHA、IP 轮换）。自托管版本使用基础的 fetch + Playwright，因此某些受保护的网站可能会失败。搜索功能使用 DuckDuckGo 而非 Google。

**设置：**

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

如果你的自托管实例启用了身份验证，你也可以同时设置 `FIRECRAWL_API_KEY` 和 `FIRECRAWL_API_URL`。

## OpenRouter 提供商路由

使用 OpenRouter 时，你可以控制请求如何在不同提供商之间进行路由。在 `~/.hermes/config.yaml` 中添加 `provider_routing` 部分：

```yaml
provider_routing:
  sort: "throughput"          # "price" (默认), "throughput", 或 "latency"
  # only: ["anthropic"]      # 仅使用这些提供商
  # ignore: ["deepinfra"]    # 跳过这些提供商
  # order: ["anthropic", "google"]  # 按此顺序尝试提供商
  # require_parameters: true  # 仅使用支持所有请求参数的提供商
  # data_collection: "deny"   # 排除可能存储/训练数据的提供商
```

**快捷方式：** 在任何模型名称后附加 `:nitro` 以按吞吐量排序（例如 `anthropic/claude-sonnet-4:nitro`），或附加 `:floor` 以按价格排序。

## 回退模型 (Fallback Model) {#fallback-model}

配置一个备用提供商:模型，当你的主模型失败（速率限制、服务器错误、身份验证失败）时，Hermes 会自动切换到该模型：

```yaml
fallback_model:
  provider: openrouter                    # 必填
  model: anthropic/claude-sonnet-4        # 必填
  # base_url: http://localhost:8000/v1    # 可选，用于自定义端点
  # api_key_env: MY_CUSTOM_KEY           # 可选，自定义端点 API 密钥的环境变量名
```

激活后，回退机制会在会话期间切换模型和提供商，而不会丢失你的对话。每个会话**最多触发一次**。

支持的提供商：`openrouter`, `nous`, `openai-codex`, `copilot`, `copilot-acp`, `anthropic`, `huggingface`, `zai`, `kimi-coding`, `minimax`, `minimax-cn`, `deepseek`, `ai-gateway`, `opencode-zen`, `opencode-go`, `kilocode`, `alibaba`, `custom`。

:::tip
回退功能仅通过 `config.yaml` 配置——没有对应的环境变量。有关其触发时机、支持的提供商以及它如何与辅助任务和委托交互的完整详情，请参阅 [Fallback Providers](/user-guide/features/fallback-providers)。
:::

## 智能模型路由

可选的“廉价 vs 强力”路由允许 Hermes 在处理复杂工作时保留主模型，同时将非常简短/简单的轮次发送给更便宜的模型。

```yaml
smart_model_routing:
  enabled: true
  max_simple_chars: 160
  max_simple_words: 28
  cheap_model:
    provider: openrouter
    model: google/gemini-2.5-flash
    # base_url: http://localhost:8000/v1  # 可选自定义端点
    # api_key_env: MY_CUSTOM_KEY          # 该端点 API 密钥的可选环境变量名
```

工作原理：
- 如果轮次很短、单行，且看起来不涉及复杂的代码/工具/调试，Hermes 可能会将其路由到 `cheap_model`
- 如果轮次看起来很复杂，Hermes 将保持使用你的主模型/提供商
- 如果廉价路由无法顺利解析，Hermes 会自动回退到主模型

此功能设计上较为保守。它旨在处理快速、低风险的轮次，例如：
- 简短的事实性问题
- 快速重写
- 轻量级摘要
它将避免路由以下类型的提示词：
- 编码/调试工作
- 涉及大量工具调用的请求
- 长文本或多行分析请求

当你希望在不完全更改默认模型的情况下降低延迟或成本时，可以使用此功能。

---

## 另请参阅

- [配置](/user-guide/configuration) — 常规配置（目录结构、配置优先级、终端后端、内存、压缩等）
- [环境变量](/reference/environment-variables) — 所有环境变量的完整参考指南
