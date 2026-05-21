---
sidebar_position: 9
title: "使用 Ollama 在本地运行 Hermes——零 API 成本"
description: "逐步指南：通过 Ollama 和开放权重模型（如 Gemma 4）将 Hermes Agent 完全运行在自己的机器上，无需云 API 密钥或付费订阅"
---

<a id="run-hermes-locally-with-ollama-zero-api-cost"></a>
# 使用 Ollama 在本地运行 Hermes——零 API 成本

<a id="the-problem"></a>
## 问题

云端 LLM API 按 token 计费。一次密集的编码会话可能花费 5–20 美元。对于个人项目、学习或隐私敏感的工作，这笔费用累积起来不小——而且每个对话都发送给了第三方。

<a id="what-this-guide-solves"></a>
## 本指南解决的问题

你将把 Hermes Agent 完全配置在自己的硬件上运行，使用 [Ollama](https://ollama.com) 作为模型后端。无需 API 密钥，无需订阅，数据不会离开你的机器。配置完成后，Hermes 的工作方式与使用 OpenRouter 或 Anthropic 时完全一样——终端命令、文件编辑、网页浏览、任务委派——但模型在本地运行。

完成后，你将拥有：

- Ollama 提供一个或多个开放权重模型
- Hermes 连接到 Ollama 作为自定义端点
- 一个可工作的本地 Agent，能够编辑文件、运行命令和浏览网页
- 可选：一个完全由自己硬件驱动的 Telegram/Discord 机器人

<a id="what-you-need"></a>
## 你需要什么

| 组件 | 最低要求 | 推荐配置 |
|-----------|---------|-------------|
| **内存** | 8 GB（适用于 3B 模型） | 32+ GB（适用于 27B+ 模型） |
| **存储** | 5 GB 空闲 | 30+ GB（适用于多个模型） |
| **CPU** | 4 核 | 8+ 核（AMD EPYC、Ryzen、Intel Xeon） |
| **GPU** | 不需要 | NVIDIA GPU 且拥有 8+ GB 显存能显著提升速度 |

:::tip 仅使用 CPU 也能运行，但响应会较慢
Ollama 可以在仅使用 CPU 的服务器上运行。一个现代 8 核 CPU 上运行 9B 模型大约能得到 ~10 tokens/秒。31B 模型在 CPU 上较慢（约 2–5 tokens/秒）——每次响应需要 30–120 秒，但可以工作。GPU 能大幅改善这一情况。对于仅使用 CPU 的配置，通过环境变量增加 API 超时时间（这不是 `config.yaml` 的键）：
<a id="cpu-only-works-but-expect-slower-responses"></a>

```bash
# ~/.hermes/.env
HERMES_API_TIMEOUT=1800   # 30 分钟——为较慢的本地模型预留充足时间
```
:::

<a id="step-1-install-ollama"></a>
## 第一步：安装 Ollama

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

验证是否运行：

```bash
ollama --version
curl http://localhost:11434/api/tags   # 应返回 {"models":[]}
```

<a id="step-2-pull-a-model"></a>
## 第二步：拉取模型

根据你的硬件选择：

| 模型 | 磁盘大小 | 所需内存 | 工具调用 | 最适合场景 |
|-------|-------------|------------|:------------:|----------|
| `gemma4:31b` | ~20 GB | 24+ GB | 是 | 最佳质量——工具使用和推理能力强 |
| `gemma2:27b` | ~16 GB | 20+ GB | 否 | 对话任务，无工具使用 |
| `gemma2:9b` | ~5 GB | 8+ GB | 否 | 快速聊天、问答——无法调用工具 |
| `llama3.2:3b` | ~2 GB | 4+ GB | 否 | 轻量级快速回答 |

<a id="tool-calling-matters"></a>
:::warning 工具调用很重要
Hermes 是一个 **agentic** 助手——它通过工具调用编辑文件、运行命令和浏览网页。不支持工具调用的模型只能聊天；它们无法执行操作。要获得完整的 Hermes 体验，请使用支持工具的模型（如 `gemma4:31b`）。
:::

拉取你选择的模型：

```bash
ollama pull gemma4:31b
```

<a id="multiple-models"></a>
:::info 多个模型
你可以拉取多个模型，并在 Hermes 内部通过 `/model` 切换它们。Ollama 会按需将活动模型加载到内存中，并自动卸载空闲模型。
:::
验证模型是否正常工作：

```bash
curl http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemma4:31b",
    "messages": [{"role": "user", "content": "Say hello"}],
    "max_tokens": 50
  }'
```

你应该会看到一条包含模型回复的 JSON 响应。

<a id="step-3-configure-hermes"></a>
## 第三步：配置 Hermes

运行 Hermes 设置向导：

```bash
hermes setup
```

当提示选择 provider 时，选择 **Custom Endpoint**，然后输入：

- **Base URL：** `http://localhost:11434/v1`
- **API Key：** 留空或输入 `no-key`（Ollama 不需要 API Key）
- **Model：** `gemma4:31b`（或你拉取的其他模型）

或者，直接编辑 `~/.hermes/config.yaml`：

```yaml
model:
  default: "gemma4:31b"
  provider: "custom"
  base_url: "http://localhost:11434/v1"
```

<a id="step-4-start-using-hermes"></a>
## 第四步：开始使用 Hermes

```bash
hermes
```

就这样。你现在已经运行了一个完全本地的 Agent。试试看：

```
You：列出此目录下所有 Python 文件，并统计每个文件的代码行数

You：阅读 README.md，总结这个项目是做什么的

You：创建一个 Python 脚本，获取胡志明市的天气
```

Hermes 会使用终端工具、文件操作和你的本地模型——无需云端调用。

<a id="step-5-pick-the-right-model-for-your-task"></a>
## 第五步：为任务选择合适的模型

并非所有任务都需要最大的模型。这里有一份实用指南：

| 任务 | 推荐模型 | 原因 |
|------|---------|------|
| 文件编辑、代码、终端命令 | `gemma4:31b` | 唯一具备可靠工具调用能力的模型 |
| 快速问答（无需使用工具） | `gemma2:9b` | 对话任务响应速度快 |
| 轻量聊天 | `llama3.2:3b` | 速度最快，但能力非常有限 |

:::note
对于完整的 Agent 工作（编辑文件、运行命令、浏览网页），`gemma4:31b` 是目前支持工具调用的最佳本地选项。请查看 [Ollama 的模型库](https://ollama.com/library) 以获取更新的模型——工具调用支持正在快速扩展。
:::

在会话中随时切换模型：

```
/model gemma2:9b
```

<a id="step-6-optimize-for-speed"></a>
## 第六步：优化速度

<a id="increase-ollama-s-context-window"></a>
### 增加 Ollama 的上下文窗口

默认情况下，Ollama 使用 2048 token 的上下文。对于 Agent 工作（工具调用、长对话），你需要更多：

```bash
# 创建一个扩展上下文的 Modelfile
cat > /tmp/Modelfile << 'EOF'
FROM gemma4:31b
PARAMETER num_ctx 16384
EOF

ollama create gemma4-16k -f /tmp/Modelfile
```

然后更新你的 Hermes 配置，将模型名称改为 `gemma4-16k`。

<a id="keep-the-model-loaded"></a>
### 保持模型常驻内存

默认情况下，Ollama 会在 5 分钟无活动后卸载模型。对于持久运行的网关机器人，请保持模型加载：

```bash
# 设置 keep-alive 为 24 小时
curl http://localhost:11434/api/generate \
  -d '{"model": "gemma4:31b", "keep_alive": "24h"}'
```

或者在 Ollama 的环境中全局设置：

```bash
# /etc/systemd/system/ollama.service.d/override.conf
[Service]
Environment="OLLAMA_KEEP_ALIVE=24h"
```

<a id="use-gpu-offloading-if-available"></a>
### 使用 GPU 卸载（如果可用）

如果你有 NVIDIA GPU，Ollama 会自动将层卸载到 GPU 上。用以下命令检查：
```bash
ollama ps   # 显示当前加载的模型以及 GPU 层数量
```

对于 12 GB GPU 上的 31B 模型，你会得到部分卸载（约 40 层在 GPU，其余在 CPU），这仍然能带来显著的速度提升。

<a id="step-7-run-as-a-gateway-bot-optional"></a>
## 步骤 7：作为网关机器人运行（可选）

一旦 Hermes 在 CLI 中本地运行，你可以将其作为 Telegram 或 Discord 机器人暴露出来——仍然完全运行在你的硬件上。

<a id="telegram"></a>
### Telegram

1. 通过 [@BotFather](https://t.me/BotFather) 创建一个机器人并获取 token
2. 添加到 `~/.hermes/config.yaml`：

```yaml
model:
  default: "gemma4:31b"
  provider: "custom"
  base_url: "http://localhost:11434/v1"

platforms:
  telegram:
    enabled: true
    token: "YOUR_TELEGRAM_BOT_TOKEN"
```

3. 启动网关：

```bash
hermes gateway
```

现在在 Telegram 上给你的机器人发消息——它会用本地模型回复。

<a id="discord"></a>
### Discord

1. 在 [discord.com/developers](https://discord.com/developers/applications) 创建一个 Discord 应用
2. 添加到配置：

```yaml
platforms:
  discord:
    enabled: true
    token: "YOUR_DISCORD_BOT_TOKEN"
```

3. 启动：`hermes gateway`

<a id="step-8-set-up-fallbacks-optional"></a>
## 步骤 8：设置回退（可选）

本地模型在处理复杂任务时可能比较吃力。设置一个云回退，仅在本地模型失败时激活：

```yaml
model:
  default: "gemma4:31b"
  provider: "custom"
  base_url: "http://localhost:11434/v1"

fallback_providers:
  - provider: openrouter
    model: anthropic/claude-sonnet-4
```

这样一来，你 90% 的使用都是免费的（本地），只有困难任务才会用到付费 API。

<a id="troubleshooting"></a>
## 故障排查

<a id="connection-refused-on-startup"></a>
### 启动时遇到 "Connection refused"

Ollama 未运行。启动它：

```bash
sudo systemctl start ollama
# 或者
ollama serve
```

<a id="slow-responses"></a>
### 响应缓慢

- **检查模型大小与内存：** 如果模型需要的内存超出可用内存，它会交换到磁盘。使用更小的模型或增加内存。
- **检查 `ollama ps`：** 如果没有卸载 GPU 层，响应会受 CPU 限制。这在纯 CPU 服务器上是正常的。
- **减少上下文：** 长对话会降低推理速度。定期使用 `/compress`，或者在配置中设置更低的压缩阈值。

<a id="model-doesn-t-follow-tool-calls"></a>
### 模型不遵循工具调用

较小的模型（3B、7B）有时会忽略工具调用指令，生成纯文本而不是结构化函数调用。解决方案：

- **使用更大的模型**——`gemma4:31b` 或 `gemma2:27b` 处理工具调用的能力远优于 3B/7B 模型。
- **Hermes 有自动修复功能**——它能检测损坏的工具调用并尝试自动修复。
- **设置回退**——如果本地模型连续失败 3 次，Hermes 会回退到云服务商。

<a id="context-window-errors"></a>
### 上下文窗口错误

Ollama 默认的上下文（2048 tokens）对于 Agent 相关工作来说太小了。请参阅[步骤 6](#step-6-optimize-for-speed) 来增加它。

<a id="cost-comparison"></a>
## 成本对比

以下是本地运行相比云 API 能节省的费用，基于一次典型的编码会话（约 100K token 输入，20K token 输出）：

| 提供商 | 单次会话成本 | 月度（每天使用） |
|----------|-----------------|---------------------|
| Anthropic Claude Sonnet | ~$0.80 | ~$24 |
| OpenRouter (GPT-4o) | ~$0.60 | ~$18 |
| **Ollama（本地）** | **$0.00** | **$0.00** |
你唯一的成本是电费——大约每次会话 0.01–0.05 美元，具体取决于硬件。

<a id="what-works-well-locally"></a>
## 本地运行效果良好的场景

- **文件编辑与代码生成**——9B 及以上的模型能很好地处理
- **终端命令**——Hermes 封装命令、执行它并读取输出，与模型无关
- **网页浏览**——浏览器工具负责抓取，模型只负责解读结果
- **定时任务和计划任务**——与云端设置完全一致
- **多平台网关**——Telegram、Discord、Slack 均支持本地模型

<a id="what-s-better-with-cloud-models"></a>
## 云端模型表现更好的场景

- **非常复杂的多步推理**——70B+ 或云端模型（如 Claude Opus）明显更优
- **长上下文窗口**——云端模型支持 100K–1M tokens，本地模型通常只有 8K–32K
- **长回复的生成速度**——在长内容生成时，云端推理比仅用 CPU 的本地模型更快

最佳折中点：日常任务用本地模型，困难任务设置云端备用。
