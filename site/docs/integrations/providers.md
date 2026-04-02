---
title: "AI 提供商"
sidebar_label: "AI 提供商"
sidebar_position: 1
---

# AI 提供商

本页介绍如何为 Hermes Agent 设置推理提供商——从云端 API（如 OpenRouter 和 Anthropic），到自托管端点（如 Ollama 和 vLLM），再到高级路由和回退配置。使用 Hermes 至少需要配置一个提供商。

## 推理提供商

你至少需要一种方式连接到 LLM。可以使用 `hermes model` 交互式切换提供商和模型，或者直接配置：

| 提供商 | 设置方式 |
|----------|-------|
| **Nous Portal** | `hermes model`（OAuth，基于订阅） |
| **OpenAI Codex** | `hermes model`（ChatGPT OAuth，使用 Codex 模型） |
| **GitHub Copilot** | `hermes model`（OAuth 设备码流程，`COPILOT_GITHUB_TOKEN`、`GH_TOKEN` 或 `gh auth token`） |
| **GitHub Copilot ACP** | `hermes model`（启动本地 `copilot --acp --stdio`） |
| **Anthropic** | `hermes model`（通过 Claude Code 认证、Anthropic API key 或手动 setup-token 使用 Claude Pro/Max） |
| **OpenRouter** | 在 `~/.hermes/.env` 中设置 `OPENROUTER_API_KEY` |
| **AI Gateway** | 在 `~/.hermes/.env` 中设置 `AI_GATEWAY_API_KEY`（提供商：`ai-gateway`） |
| **z.ai / GLM** | 在 `~/.hermes/.env` 中设置 `GLM_API_KEY`（提供商：`zai`） |
| **Kimi / Moonshot** | 在 `~/.hermes/.env` 中设置 `KIMI_API_KEY`（提供商：`kimi-coding`） |
| **MiniMax** | 在 `~/.hermes/.env` 中设置 `MINIMAX_API_KEY`（提供商：`minimax`） |
| **MiniMax China** | 在 `~/.hermes/.env` 中设置 `MINIMAX_CN_API_KEY`（提供商：`minimax-cn`） |
| **阿里云** | 在 `~/.hermes/.env` 中设置 `DASHSCOPE_API_KEY`（提供商：`alibaba`，别名：`dashscope`、`qwen`） |
| **Kilo Code** | 在 `~/.hermes/.env` 中设置 `KILOCODE_API_KEY`（提供商：`kilocode`） |
| **OpenCode Zen** | 在 `~/.hermes/.env` 中设置 `OPENCODE_ZEN_API_KEY`（提供商：`opencode-zen`） |
| **OpenCode Go** | 在 `~/.hermes/.env` 中设置 `OPENCODE_GO_API_KEY`（提供商：`opencode-go`） |
| **DeepSeek** | 在 `~/.hermes/.env` 中设置 `DEEPSEEK_API_KEY`（提供商：`deepseek`） |
| **Hugging Face** | 在 `~/.hermes/.env` 中设置 `HF_TOKEN`（提供商：`huggingface`，别名：`hf`） |
| **自定义端点** | `hermes model`（保存在 `config.yaml`）或在 `~/.hermes/.env` 中设置 `OPENAI_BASE_URL` + `OPENAI_API_KEY` |

:::tip 模型键别名
在 `model:` 配置部分，你可以使用 `default:` 或 `model:` 作为模型 ID 的键名。`model: { default: my-model }` 和 `model: { model: my-model }` 两者效果相同。
:::

:::info Codex 说明
OpenAI Codex 提供商通过设备码认证（打开 URL，输入代码）。Hermes 会将生成的凭据存储在自己的认证存储中，路径为 `~/.hermes/auth.json`，并且如果存在，会自动导入 Codex CLI 的凭据文件 `~/.codex/auth.json`。无需安装 Codex CLI。
:::

:::warning
即使使用 Nous Portal、Codex 或自定义端点，一些工具（视觉、网页摘要、MoA）会使用单独的“辅助”模型——默认是通过 OpenRouter 的 Gemini Flash。设置 `OPENROUTER_API_KEY` 会自动启用这些工具。你也可以配置这些工具使用的模型和提供商——详见[辅助模型](/user-guide/configuration#auxiliary-models)。
:::

### Anthropic（原生）

通过 Anthropic API 直接使用 Claude 模型——无需 OpenRouter 代理。支持三种认证方式：

```bash
# 使用 API key（按 token 付费）
export ANTHROPIC_API_KEY=***
hermes chat --provider anthropic --model claude-sonnet-4-6

# 推荐：通过 `hermes model` 认证
# Hermes 会直接使用 Claude Code 的凭据存储（如果可用）
hermes model

# 手动覆盖，使用 setup-token（回退/旧版）
export ANTHROPIC_TOKEN=***  # setup-token 或手动 OAuth token
hermes chat --provider anthropic

# 自动检测 Claude Code 凭据（如果你已经使用 Claude Code）
hermes chat --provider anthropic  # 自动读取 Claude Code 凭据文件
```

当你通过 `hermes model` 选择 Anthropic OAuth 时，Hermes 会优先使用 Claude Code 自身的凭据存储，而不是复制 token 到 `~/.hermes/.env`，这样可以保持可刷新凭据的刷新能力。

或者永久设置：
```yaml
model:
  provider: "anthropic"
  default: "claude-sonnet-4-6"
```

:::tip 别名
`--provider claude` 和 `--provider claude-code` 也可以作为 `--provider anthropic` 的简写。
:::

### GitHub Copilot

Hermes 支持 GitHub Copilot 作为一流提供商，提供两种模式：

**`copilot` — 直接 Copilot API**（推荐）。使用你的 GitHub Copilot 订阅，通过 Copilot API 访问 GPT-5.x、Claude、Gemini 等模型。

```bash
hermes chat --provider copilot --model gpt-5.4
```

**认证选项**（按顺序检查）：

1. `COPILOT_GITHUB_TOKEN` 环境变量
2. `GH_TOKEN` 环境变量
3. `GITHUB_TOKEN` 环境变量
4. `gh auth token` CLI 回退

如果找不到 token，`hermes model` 会提供 **OAuth 设备码登录** —— 与 Copilot CLI 和 opencode 使用的流程相同。

:::warning Token 类型
Copilot API **不支持**传统的个人访问令牌（`ghp_*`）。支持的 token 类型：

| 类型 | 前缀 | 获取方式 |
|------|--------|------------|
| OAuth token | `gho_` | `hermes model` → GitHub Copilot → 使用 GitHub 登录 |
| 细粒度 PAT | `github_pat_` | GitHub 设置 → 开发者设置 → 细粒度令牌（需要 **Copilot Requests** 权限） |
| GitHub App token | `ghu_` | 通过 GitHub App 安装获得 |

如果你的 `gh auth token` 返回的是 `ghp_*` token，请使用 `hermes model` 通过 OAuth 认证。
:::

**API 路由**：GPT-5+ 模型（除 `gpt-5-mini` 外）自动使用 Responses API。其他模型（GPT-4o、Claude、Gemini 等）使用 Chat Completions。模型从实时 Copilot 目录自动检测。

**`copilot-acp` — Copilot ACP Agent 后端**。作为子进程启动本地 Copilot CLI：

```bash
hermes chat --provider copilot-acp --model copilot-acp
# 需要 PATH 中有 GitHub Copilot CLI，并且已有 `copilot login` 会话
```

**永久配置：**
```yaml
model:
  provider: "copilot"
  default: "gpt-5.4"
```

| 环境变量 | 说明 |
|---------------------|-------------|
| `COPILOT_GITHUB_TOKEN` | Copilot API 的 GitHub token（优先级最高） |
| `HERMES_COPILOT_ACP_COMMAND` | 覆盖 Copilot CLI 二进制路径（默认：`copilot`） |
| `HERMES_COPILOT_ACP_ARGS` | 覆盖 ACP 参数（默认：`--acp --stdio`） |

### 一流的中文 AI 提供商

这些提供商内置支持，带有专用提供商 ID。设置 API key 并用 `--provider` 选择：

```bash
# z.ai / ZhipuAI GLM
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

# 阿里云 / DashScope（Qwen 模型）
hermes chat --provider alibaba --model qwen3.5-plus
# 需要：在 ~/.hermes/.env 中设置 DASHSCOPE_API_KEY
```

或者在 `config.yaml` 中永久设置提供商：
```yaml
model:
  provider: "zai"       # 或者：kimi-coding、minimax、minimax-cn、alibaba
  default: "glm-4-plus"
```

基础 URL 可以通过环境变量 `GLM_BASE_URL`、`KIMI_BASE_URL`、`MINIMAX_BASE_URL`、`MINIMAX_CN_BASE_URL` 或 `DASHSCOPE_BASE_URL` 覆盖。

### Hugging Face 推理提供商

[Hugging Face 推理提供商](https://huggingface.co/docs/inference-providers) 通过统一的 OpenAI 兼容端点（`router.huggingface.co/v1`）路由 20 多个开源模型。请求会自动路由到最快的可用后端（Groq、Together、SambaNova 等），并支持自动故障切换。

```bash
# 使用任意可用模型
hermes chat --provider huggingface --model Qwen/Qwen3-235B-A22B-Thinking-2507
# 需要：在 ~/.hermes/.env 中设置 HF_TOKEN

# 简写别名
hermes chat --provider hf --model deepseek-ai/DeepSeek-V3.2
```

或者在 `config.yaml` 中永久设置：
```yaml
model:
  provider: "huggingface"
  default: "Qwen/Qwen3-235B-A22B-Thinking-2507"
```
在 [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) 获取你的 token —— 确保启用了“Make calls to Inference Providers”权限。免费套餐包含每月 0.10 美元的额度，且对提供商费率无加价。

你可以在模型名称后添加路由后缀：`:fastest`（默认）、`:cheapest`，或 `:provider_name` 来强制使用特定后端。

基础 URL 可以通过 `HF_BASE_URL` 覆盖。

## 自定义和自托管 LLM 提供商

Hermes Agent 支持 **任何兼容 OpenAI API 的端点**。只要服务器实现了 `/v1/chat/completions`，你就可以指向它。这意味着你可以使用本地模型、GPU 推理服务器、多提供商路由器，或任何第三方 API。

### 通用设置

配置自定义端点有三种方式：

**交互式设置（推荐）：**
```bash
hermes model
# 选择“Custom endpoint (self-hosted / VLLM / etc.)”
# 输入：API 基础 URL、API key、模型名称
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

:::warning 旧环境变量
`.env` 中的 `OPENAI_BASE_URL` 和 `LLM_MODEL` 已 **弃用**。CLI 完全忽略 `LLM_MODEL`（只有网关会读取）。请使用 `hermes model` 或直接编辑 `config.yaml` —— 两者都能正确持久化，支持重启和 Docker 容器。
:::

这两种方式都会持久化到 `config.yaml`，它是模型、提供商和基础 URL 的权威配置文件。

### 使用 `/model` 切换模型

配置好自定义端点后，你可以在会话中途切换模型：

```
/model custom:qwen-2.5          # 切换到自定义端点上的模型
/model custom                    # 从端点自动检测模型
/model openrouter:claude-sonnet-4 # 切换回云端提供商
```

如果你配置了 **命名的自定义提供商**（见下文），使用三段式语法：

```
/model custom:local:qwen-2.5    # 使用名为 "local" 的自定义提供商，模型为 qwen-2.5
/model custom:work:llama3       # 使用名为 "work" 的自定义提供商，模型为 llama3
```

切换提供商时，Hermes 会将基础 URL 和提供商信息持久化到配置中，确保重启后依然生效。切换回内置提供商时，旧的基础 URL 会自动清除。

:::tip
`/model custom`（不带模型名）会调用你的端点的 `/models` API，如果只有一个模型加载，则自动选择。适合运行单模型的本地服务器。
:::

下面的内容都遵循同样的模式 —— 只需更改 URL、密钥和模型名称。

---

### Ollama — 本地模型，零配置

[Ollama](https://ollama.com/) 通过一条命令在本地运行开源模型。适合快速本地试验、隐私敏感工作和离线使用。支持通过兼容 OpenAI 的 API 调用工具。

```bash
# 安装并运行模型
ollama pull qwen2.5-coder:32b
ollama serve   # 默认启动在 11434 端口
```

然后配置 Hermes：

```bash
hermes model
# 选择“Custom endpoint (self-hosted / VLLM / etc.)”
# 输入 URL：http://localhost:11434/v1
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

:::caution Ollama 默认上下文长度很低
Ollama 默认不会使用模型的完整上下文窗口。根据你的显存，默认值如下：

| 可用显存       | 默认上下文长度    |
|----------------|------------------|
| 小于 24 GB     | **4,096 tokens** |
| 24–48 GB       | 32,768 tokens    |
| 48 GB 及以上   | 256,000 tokens   |

对于带工具调用的 Agent 使用，**至少需要 16k–32k 的上下文长度**。4k 时，系统提示和工具 schema 就可能占满窗口，没法继续对话。

**如何增加上下文长度**（任选其一）：

```bash
# 方案 1：通过环境变量设置全局（推荐）
OLLAMA_CONTEXT_LENGTH=32768 ollama serve

# 方案 2：systemd 管理的 Ollama
sudo systemctl edit ollama.service
# 添加：Environment="OLLAMA_CONTEXT_LENGTH=32768"
# 然后执行：sudo systemctl daemon-reload && sudo systemctl restart ollama

# 方案 3：内置到自定义模型（每个模型持久）
echo -e "FROM qwen2.5-coder:32b\nPARAMETER num_ctx 32768" > Modelfile
ollama create qwen2.5-coder-32k -f Modelfile
```

**无法通过兼容 OpenAI 的 API**（`/v1/chat/completions`）设置上下文长度，必须在服务器端或通过 Modelfile 配置。这是集成 Ollama 和 Hermes 等工具时最常见的困惑来源。
:::

**确认上下文长度设置正确：**

```bash
ollama ps
# 查看 CONTEXT 列，应该显示你配置的值
```

:::tip
用 `ollama list` 查看可用模型。通过 `ollama pull <model>` 从 [Ollama 库](https://ollama.com/library) 拉取任意模型。Ollama 会自动处理 GPU 卸载，大多数情况下无需额外配置。
:::

---

### vLLM — 高性能 GPU 推理

[vLLM](https://docs.vllm.ai/) 是生产级 LLM 服务的标准。适合：GPU 硬件上的最大吞吐量、大模型服务、连续批处理。

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
# 选择“Custom endpoint (self-hosted / VLLM / etc.)”
# 输入 URL：http://localhost:8000/v1
# 跳过 API key（如果你用 --api-key 配置了 vLLM，则输入）
# 输入模型名称：meta-llama/Llama-3.1-70B-Instruct
```

**上下文长度：** vLLM 默认读取模型的 `max_position_embeddings`。如果超过显存，会报错并提示你降低 `--max-model-len`。你也可以用 `--max-model-len auto` 自动寻找最大可用值。设置 `--gpu-memory-utilization 0.95`（默认 0.9）可让显存利用率更高，支持更长上下文。

**工具调用需要显式参数：**

| 参数 | 作用 |
|------|------|
| `--enable-auto-tool-choice` | 支持 Hermes 默认的 `tool_choice: "auto"` |
| `--tool-call-parser <name>` | 指定模型工具调用格式的解析器 |

支持的解析器有：`hermes`（Qwen 2.5、Hermes 2/3）、`llama3_json`（Llama 3.x）、`mistral`、`deepseek_v3`、`deepseek_v31`、`xlam`、`pythonic`。没有这些参数，工具调用会被当作普通文本输出。

:::tip
vLLM 支持人类可读的大小写单位：`--max-model-len 64k`（小写 k = 1000，大写 K = 1024）。
:::

---

### SGLang — 使用 RadixAttention 的快速服务

[SGLang](https://github.com/sgl-project/sglang) 是 vLLM 的替代方案，采用 RadixAttention 复用 KV 缓存。适合：多轮对话（前缀缓存）、受限解码、结构化输出。

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
# 选择“Custom endpoint (self-hosted / VLLM / etc.)”
# 输入 URL：http://localhost:30000/v1
# 输入模型名称：meta-llama/Llama-3.1-70B-Instruct
```

**上下文长度：** SGLang 默认读取模型配置。可用 `--context-length` 覆盖。如果需要超过模型声明的最大值，设置环境变量 `SGLANG_ALLOW_OVERWRITE_LONGER_CONTEXT_LEN=1`。

**工具调用：** 使用 `--tool-call-parser` 指定对应模型族的解析器：`qwen`（Qwen 2.5）、`llama3`、`llama4`、`deepseekv3`、`mistral`、`glm`。没有该参数，工具调用会作为纯文本返回。

:::caution SGLang 默认最大输出仅 128 tokens
如果回复被截断，请在请求中添加 `max_tokens`，或在服务器端设置 `--default-max-tokens`。SGLang 默认每次响应最多 128 tokens（如果请求中未指定）。
:::

---

### llama.cpp / llama-server — CPU 和 Metal 推理
[llama.cpp](https://github.com/ggml-org/llama.cpp) 支持在 CPU、Apple Silicon（Metal）和消费级 GPU 上运行量化模型。适合：没有数据中心 GPU 的用户、Mac 用户、边缘部署。

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

**上下文长度（`-c`）：** 最新版本默认是 `0`，表示从 GGUF 元数据中读取模型的训练上下文长度。对于训练上下文超过 128k 的模型，尝试分配完整的 KV 缓存可能会导致内存溢出。请根据需要显式设置 `-c`（32k–64k 是 Agent 使用的合适范围）。如果使用并行槽位（`-np`），总上下文会在槽位间分配——例如 `-c 32768 -np 4`，每个槽位只有 8k。

然后配置 Hermes 指向该服务：

```bash
hermes model
# 选择“Custom endpoint (self-hosted / VLLM / etc.)”
# 输入 URL: http://localhost:8080/v1
# 跳过 API key（本地服务器不需要）
# 输入模型名称 — 如果只加载了一个模型，可以留空自动检测
```

这会将端点保存到 `config.yaml`，以便会话间保持。

:::caution `--jinja` 是调用工具的必需参数
如果没有 `--jinja`，llama-server 会完全忽略 `tools` 参数。模型会尝试通过在响应文本中写入 JSON 来调用工具，但 Hermes 不会识别为工具调用——你会看到类似 `{"name": "web_search", ...}` 的原始 JSON 作为消息打印，而不是实际执行搜索。

原生工具调用支持（性能最佳）：Llama 3.x、Qwen 2.5（含 Coder）、Hermes 2/3、Mistral、DeepSeek、Functionary。其他模型使用通用处理器，虽然可用但效率可能较低。完整列表见 [llama.cpp function calling docs](https://github.com/ggml-org/llama.cpp/blob/master/docs/function-calling.md)。

你可以通过访问 `http://localhost:8080/props` 来验证工具支持是否激活——应包含 `chat_template` 字段。
:::

:::tip
从 [Hugging Face](https://huggingface.co/models?library=gguf) 下载 GGUF 模型。Q4_K_M 量化在质量和内存使用之间提供了最佳平衡。
:::

---

### LM Studio — 带本地模型的桌面应用

[LM Studio](https://lmstudio.ai/) 是一款带 GUI 的本地模型运行桌面应用。适合：喜欢图形界面、快速测试模型、macOS/Windows/Linux 开发者。

从 LM Studio 应用的 Developer 标签页启动服务器（Start Server），或使用命令行：

```bash
lms server start                        # 默认端口 1234
lms load qwen2.5-coder --context-length 32768
```

然后配置 Hermes：

```bash
hermes model
# 选择“Custom endpoint (self-hosted / VLLM / etc.)”
# 输入 URL: http://localhost:1234/v1
# 跳过 API key（LM Studio 不需要）
# 输入模型名称
```

:::caution 上下文长度通常默认为 2048
LM Studio 会从模型元数据读取上下文长度，但许多 GGUF 模型报告的默认值较低（2048 或 4096）。**务必在 LM Studio 的模型设置中显式设置上下文长度**：

1. 点击模型选择器旁的齿轮图标
2. 将“Context Length”设置为至少 16384（推荐 32768）
3. 重新加载模型使设置生效

或者使用命令行：`lms load model-name --context-length 32768`

要设置持久的每模型默认值：My Models 标签页 → 模型齿轮图标 → 设置上下文大小。
:::

**工具调用：** 自 LM Studio 0.3.6 起支持。带有原生工具调用训练的模型（Qwen 2.5、Llama 3.x、Mistral、Hermes）会自动检测并显示工具徽章。其他模型使用通用回退方案，可能不够稳定。

---

### 本地模型故障排查

以下问题影响所有与 Hermes 配合使用的本地推理服务器。

#### 工具调用显示为文本而非执行

模型输出类似 `{"name": "web_search", "arguments": {...}}` 的消息，而不是实际调用工具。

**原因：** 服务器未启用工具调用，或模型不支持服务器的工具调用实现。

| 服务器 | 解决方法 |
|--------|----------|
| **llama.cpp** | 启动命令中添加 `--jinja` |
| **vLLM** | 添加 `--enable-auto-tool-choice --tool-call-parser hermes` |
| **SGLang** | 添加 `--tool-call-parser qwen`（或相应解析器） |
| **Ollama** | 工具调用默认启用 — 确认模型支持（用 `ollama show model-name` 检查） |
| **LM Studio** | 升级到 0.3.6+ 并使用支持原生工具的模型 |

#### 模型似乎忘记上下文或回答不连贯

**原因：** 上下文窗口太小。对话超过上下文限制时，大多数服务器会静默丢弃较早消息。Hermes 的系统提示和工具模式本身就可能占用 4k–8k 令牌。

**诊断：**

```bash
# 查看 Hermes 认为的上下文大小
# 启动日志中查找："Context limit: X tokens"

# 查看服务器实际上下文
# Ollama: ollama ps（CONTEXT 列）
# llama.cpp: curl http://localhost:8080/props | jq '.default_generation_settings.n_ctx'
# vLLM: 查看启动参数中的 --max-model-len
```

**解决：** Agent 使用时上下文至少设置为 **32,768 令牌**。具体参数见各服务器章节。

#### 启动时显示“Context limit: 2048 tokens”

Hermes 会从服务器的 `/v1/models` 端点自动检测上下文长度。如果服务器报告的值很低（或根本没报告），Hermes 会使用模型声明的限制，可能不准确。

**解决：** 在 `config.yaml` 中显式设置：

```yaml
model:
  default: your-model
  provider: custom
  base_url: http://localhost:11434/v1
  context_length: 32768
```

#### 回答中途被截断

**可能原因：**
1. **服务器的 `max_tokens` 设置过低** — SGLang 默认每次响应 128 令牌。可在服务器端设置 `--default-max-tokens`，或在 Hermes 的 `config.yaml` 中配置 `model.max_tokens`。
2. **上下文耗尽** — 模型填满了上下文窗口。增加上下文长度或在 Hermes 中启用[上下文压缩](/user-guide/configuration#context-compression)。

---

### LiteLLM Proxy — 多提供商网关

[LiteLLM](https://docs.litellm.ai/) 是一个兼容 OpenAI 的代理，统一了 100 多个大模型提供商，提供单一 API。适合：无需改配置即可切换提供商、负载均衡、回退链、预算控制。

```bash
# 安装并启动
pip install "litellm[proxy]"
litellm --model anthropic/claude-sonnet-4 --port 4000

# 或使用配置文件支持多个模型：
litellm --config litellm_config.yaml --port 4000
```

然后用 `hermes model` 配置 Hermes，选择自定义端点，输入 `http://localhost:4000/v1`。

示例 `litellm_config.yaml`（带回退）：
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

[ClawRouter](https://github.com/BlockRunAI/ClawRouter) 由 BlockRunAI 开发，是一个本地路由代理，根据查询复杂度自动选择模型。它会在 14 个维度上分类请求，并路由到能处理任务且最便宜的模型。支付使用 USDC 加密货币（无需 API key）。

```bash
# 安装并启动
npx @blockrun/clawrouter    # 默认端口 8402
```

然后用 `hermes model` 配置 Hermes，选择自定义端点，输入 `http://localhost:8402/v1`，模型名填 `blockrun/auto`。

路由配置：
| 配置文件 | 策略 | 节省比例 |
|---------|----------|---------|
| `blockrun/auto` | 质量/成本平衡 | 74-100% |
| `blockrun/eco` | 尽可能便宜 | 95-100% |
| `blockrun/premium` | 最高质量模型 | 0% |
| `blockrun/free` | 仅免费模型 | 100% |
| `blockrun/agentic` | 针对工具使用优化 | 视情况而定 |

:::note
ClawRouter 需要在 Base 或 Solana 上有 USDC 余额的钱包进行支付。所有请求都会通过 BlockRun 的后端 API 路由。运行 `npx @blockrun/clawrouter doctor` 检查钱包状态。
:::
---

### 其他兼容的 Provider

任何支持 OpenAI 兼容 API 的服务都可以使用。一些常见选项：

| Provider | 基础 URL | 备注 |
|----------|----------|-------|
| [Together AI](https://together.ai) | `https://api.together.xyz/v1` | 云端托管的开源模型 |
| [Groq](https://groq.com) | `https://api.groq.com/openai/v1` | 超高速推理 |
| [DeepSeek](https://deepseek.com) | `https://api.deepseek.com/v1` | DeepSeek 模型 |
| [Fireworks AI](https://fireworks.ai) | `https://api.fireworks.ai/inference/v1` | 快速开源模型托管 |
| [Cerebras](https://cerebras.ai) | `https://api.cerebras.ai/v1` | 片上大规模芯片推理 |
| [Mistral AI](https://mistral.ai) | `https://api.mistral.ai/v1` | Mistral 模型 |
| [OpenAI](https://openai.com) | `https://api.openai.com/v1` | 直接访问 OpenAI |
| [Azure OpenAI](https://azure.microsoft.com) | `https://YOUR.openai.azure.com/` | 企业级 OpenAI |
| [LocalAI](https://localai.io) | `http://localhost:8080/v1` | 自托管，多模型支持 |
| [Jan](https://jan.ai) | `http://localhost:1337/v1` | 带本地模型的桌面应用 |

你可以通过 `hermes model` → 自定义端点，或者在 `config.yaml` 中配置这些服务：

```yaml
model:
  default: meta-llama/Llama-3.1-70B-Instruct-Turbo
  provider: custom
  base_url: https://api.together.xyz/v1
  api_key: your-together-key
```

---

### 上下文长度检测 {#context-length-detection}

Hermes 使用多源解析链来检测模型和 Provider 的正确上下文窗口：

1. **配置覆盖** — `model.context_length` 在 config.yaml 中（优先级最高）
2. **每模型自定义 Provider** — `custom_providers[].models.<id>.context_length`
3. **持久缓存** — 之前发现的值（重启后依然有效）
4. **`/models` 端点** — 查询你的服务器 API（本地/自定义端点）
5. **Anthropic `/v1/models`** — 查询 Anthropic API 的 `max_input_tokens`（仅限 API-key 用户）
6. **OpenRouter API** — 来自 OpenRouter 的实时模型元数据
7. **Nous Portal** — 通过后缀匹配 Nous 模型 ID 与 OpenRouter 元数据
8. **[models.dev](https://models.dev)** — 社区维护的注册表，包含 100+ Provider、3800+ 模型的上下文长度
9. **默认回退** — 广泛的模型家族模式（默认 128K）

大多数情况下，这个机制开箱即用。系统会识别 Provider —— 同一个模型在不同服务商下上下文限制可能不同（例如 `claude-opus-4.6` 在 Anthropic 直连是 1M，但在 GitHub Copilot 是 128K）。

如果想显式设置上下文长度，可以在模型配置中添加 `context_length`：

```yaml
model:
  default: "qwen3.5:9b"
  base_url: "http://localhost:8080/v1"
  context_length: 131072  # 以 token 计
```

对于自定义端点，也可以针对每个模型设置上下文长度：

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

`hermes model` 在配置自定义端点时会提示输入上下文长度，留空则自动检测。

:::tip 何时手动设置上下文长度
- 你使用 Ollama 并自定义了比模型最大值更低的 `num_ctx`
- 你想限制上下文长度低于模型最大值（例如在 128k 模型上用 8k 以节省显存）
- 你在代理后面运行，且代理不支持暴露 `/v1/models` 端点
:::

---

### 命名的自定义 Provider

如果你同时使用多个自定义端点（比如本地开发服务器和远程 GPU 服务器），可以在 `config.yaml` 中定义命名的自定义 Provider：

```yaml
custom_providers:
  - name: local
    base_url: http://localhost:8080/v1
    # 省略 api_key — Hermes 对无密钥的本地服务器默认允许访问
  - name: work
    base_url: https://gpu-server.internal.corp/v1
    api_key: corp-api-key
    api_mode: chat_completions   # 可选，自动从 URL 识别
  - name: anthropic-proxy
    base_url: https://proxy.example.com/anthropic
    api_key: proxy-key
    api_mode: anthropic_messages  # 适用于 Anthropic 兼容代理
```

你可以用三段式语法在会话中切换：

```
/model custom:local:qwen-2.5       # 使用 "local" 端点的 qwen-2.5
/model custom:work:llama3-70b      # 使用 "work" 端点的 llama3-70b
/model custom:anthropic-proxy:claude-sonnet-4  # 使用代理
```

也可以在交互式 `hermes model` 菜单中选择命名的自定义 Provider。

---

### 选择合适的配置方案

| 使用场景 | 推荐方案 |
|----------|-------------|
| **只想快速使用** | OpenRouter（默认）或 Nous Portal |
| **本地模型，简单配置** | Ollama |
| **生产级 GPU 服务** | vLLM 或 SGLang |
| **Mac / 无 GPU** | Ollama 或 llama.cpp |
| **多 Provider 路由** | LiteLLM Proxy 或 OpenRouter |
| **成本优化** | ClawRouter 或 OpenRouter（`sort: "price"`） |
| **最高隐私** | Ollama、vLLM 或 llama.cpp（完全本地） |
| **企业 / Azure** | Azure OpenAI + 自定义端点 |
| **中文 AI 模型** | z.ai（GLM）、Kimi/Moonshot 或 MiniMax（一线 Provider） |

:::tip
你可以随时用 `hermes model` 切换 Provider，无需重启。无论用哪个 Provider，你的对话历史、记忆和技能都会保留。
:::

## 可选 API Key

| 功能 | Provider | 环境变量 |
|---------|----------|--------------|
| 网页爬取 | [Firecrawl](https://firecrawl.dev/) | `FIRECRAWL_API_KEY`, `FIRECRAWL_API_URL` |
| 浏览器自动化 | [Browserbase](https://browserbase.com/) | `BROWSERBASE_API_KEY`, `BROWSERBASE_PROJECT_ID` |
| 图像生成 | [FAL](https://fal.ai/) | `FAL_KEY` |
| 高级 TTS 语音 | [ElevenLabs](https://elevenlabs.io/) | `ELEVENLABS_API_KEY` |
| OpenAI TTS + 语音转录 | [OpenAI](https://platform.openai.com/api-keys) | `VOICE_TOOLS_OPENAI_KEY` |
| 强化学习训练 | [Tinker](https://tinker-console.thinkingmachines.ai/) + [WandB](https://wandb.ai/) | `TINKER_API_KEY`, `WANDB_API_KEY` |
| 跨会话用户建模 | [Honcho](https://honcho.dev/) | `HONCHO_API_KEY` |

### 自托管 Firecrawl

默认情况下，Hermes 使用 [Firecrawl 云 API](https://firecrawl.dev/) 进行网页搜索和爬取。如果你想本地运行 Firecrawl，可以让 Hermes 指向自托管实例。完整设置说明见 Firecrawl 的 [SELF_HOST.md](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md)。

**优点：** 无需 API Key，无速率限制，无页面费用，数据完全自主。

**缺点：** 云端版本使用 Firecrawl 专有的“Fire-engine”实现高级反爬（Cloudflare、验证码、IP 轮换）。自托管版本使用基础 fetch + Playwright，部分受保护网站可能无法访问。搜索使用 DuckDuckGo 替代 Google。

**设置步骤：**

1. 克隆并启动 Firecrawl Docker 堆栈（5 个容器：API、Playwright、Redis、RabbitMQ、PostgreSQL，需约 4-8 GB 内存）：
   ```bash
   git clone https://github.com/firecrawl/firecrawl
   cd firecrawl
   # 在 .env 文件中设置：USE_DB_AUTHENTICATION=false, HOST=0.0.0.0, PORT=3002
   docker compose up -d
   ```

2. 让 Hermes 指向你的实例（无需 API Key）：
   ```bash
   hermes config set FIRECRAWL_API_URL http://localhost:3002
   ```

如果你的自托管实例启用了认证，也可以同时设置 `FIRECRAWL_API_KEY` 和 `FIRECRAWL_API_URL`。

## OpenRouter Provider 路由

使用 OpenRouter 时，你可以控制请求如何在 Provider 之间路由。向 `~/.hermes/config.yaml` 添加 `provider_routing` 配置：

```yaml
provider_routing:
  sort: "throughput"          # "price"（默认）、"throughput" 或 "latency"
  # only: ["anthropic"]      # 只使用这些 Provider
  # ignore: ["deepinfra"]    # 跳过这些 Provider
  # order: ["anthropic", "google"]  # 按顺序尝试这些 Provider
  # require_parameters: true  # 只使用支持所有请求参数的 Provider
  # data_collection: "deny"   # 排除可能存储/训练数据的 Provider
```

**快捷方式：** 在模型名后加 `:nitro` 以按吞吐量排序（例如 `anthropic/claude-sonnet-4:nitro`），或加 `:floor` 以按价格排序。

---
## 备用模型 {#fallback-model}

配置一个备用提供商:model，当你的主模型出现故障（如速率限制、服务器错误、认证失败）时，Hermes 会自动切换到该模型：

```yaml
fallback_model:
  provider: openrouter                    # 必填
  model: anthropic/claude-sonnet-4        # 必填
  # base_url: http://localhost:8000/v1    # 可选，自定义端点
  # api_key_env: MY_CUSTOM_KEY           # 可选，自定义端点的 API 密钥环境变量名
```

启用后，备用模型会在会话中途切换模型和提供商，且不会丢失你的对话内容。每个会话最多触发一次。

支持的提供商：`openrouter`、`nous`、`openai-codex`、`copilot`、`anthropic`、`huggingface`、`zai`、`kimi-coding`、`minimax`、`minimax-cn`、`custom`。

:::tip
备用模型只能通过 `config.yaml` 配置——没有对应的环境变量。关于触发时机、支持的提供商，以及它如何与辅助任务和委托交互的详细信息，请参见 [备用提供商](/user-guide/features/fallback-providers)。
:::

## 智能模型路由

可选的“便宜模型 vs 强大模型”路由功能，让 Hermes 在处理复杂任务时使用主模型，而将非常短小或简单的对话轮次发送给更便宜的模型。

```yaml
smart_model_routing:
  enabled: true
  max_simple_chars: 160
  max_simple_words: 28
  cheap_model:
    provider: openrouter
    model: google/gemini-2.5-flash
    # base_url: http://localhost:8000/v1  # 可选自定义端点
    # api_key_env: MY_CUSTOM_KEY          # 可选该端点的 API 密钥环境变量名
```

工作原理：
- 如果对话轮次简短、单行且看起来不涉及代码/工具/调试，Hermes 可能会将其路由到 `cheap_model`
- 如果对话轮次看起来复杂，Hermes 会继续使用你的主模型/提供商
- 如果便宜模型路由无法顺利完成，Hermes 会自动回退到主模型

此设计故意保守，适合快速、低风险的对话轮次，比如：
- 简短的事实性问题
- 快速改写
- 轻量级摘要

它会避免路由以下类型的提示：
- 编码/调试工作
- 依赖工具较多的请求
- 长篇或多行的分析任务

当你想降低延迟或成本，但又不想完全更换默认模型时，可以使用此功能。

---

## 另请参阅

- [配置](/user-guide/configuration) — 通用配置（目录结构、配置优先级、终端后端、内存、压缩等）
- [环境变量](/reference/environment-variables) — 所有环境变量的完整参考
