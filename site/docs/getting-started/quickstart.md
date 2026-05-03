---
sidebar_position: 1
title: "快速入门"
description: "从安装到聊天，5分钟内完成与 Hermes Agent 的首次对话"
---

# 快速入门 {#quickstart}

本指南将带你从零开始，完成一个能真正投入使用的 Hermes 配置。安装、选择提供商、验证聊天功能，并清楚知道出问题时该怎么做。

## 适用人群 {#who-this-is-for}

- 新手，想要最短路径完成配置
- 切换提供商，不想因配置错误浪费时间
- 为团队、机器人或常驻工作流搭建 Hermes
- 厌倦了“装好了但啥也干不了”的情况

## 最快路径 {#the-fastest-path}

根据你的目标选择对应行：

| 目标 | 先做这个 | 然后做这个 |
|---|---|---|
| 我只想让 Hermes 在我的机器上跑起来 | `hermes setup` | 运行一次真实聊天，验证它能回复 |
| 我已经知道我的提供商 | `hermes model` | 保存配置，然后开始聊天 |
| 我想要一个机器人或常驻设置 | CLI 工作后执行 `hermes gateway setup` | 连接 Telegram、Discord、Slack 或其他平台 |
| 我想要本地或自托管模型 | `hermes model` → 自定义端点 | 验证端点、模型名称和上下文长度 |
| 我想要多提供商回退 | 先执行 `hermes model` | 在基础聊天正常工作后，再添加路由和回退 |

**经验法则：** 如果 Hermes 无法完成一次普通聊天，先不要添加更多功能。先让一次干净的对话跑通，然后再叠加网关、定时任务、技能、语音或路由。

---

## 1. 安装 Hermes Agent {#1-install-hermes-agent}

运行一行安装命令：

```bash
# Linux / macOS / WSL2 / Android (Termux)
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

:::tip Android / Termux
如果你在手机上安装，请参阅专门的 [Termux 指南](./termux.md)，了解经过测试的手动安装路径、支持的扩展功能以及当前 Android 特有的限制。
:::

:::tip Windows 用户
<a id="windows-users"></a>
先安装 [WSL2](https://learn.microsoft.com/en-us/windows/wsl/install)，然后在 WSL2 终端中运行上面的命令。
:::

安装完成后，重新加载你的 shell：

```bash
source ~/.bashrc   # 或 source ~/.zshrc
```

有关详细的安装选项、前提条件和故障排除，请参阅[安装指南](./installation.md)。

## 2. 选择提供商 {#2-choose-a-provider}

这是最重要的配置步骤。使用 `hermes model` 交互式地选择：

```bash
hermes model
```

好的默认选项：

| 提供商 | 说明 | 如何设置 |
|----------|-----------|---------------|
| **Nous Portal** | 订阅制，零配置 | 通过 `hermes model` 进行 OAuth 登录 |
| **OpenAI Codex** | ChatGPT OAuth，使用 Codex 模型 | 通过 `hermes model` 进行设备码认证 |
| **Anthropic** | 直接使用 Claude 模型 — Max 计划 + 额外用量额度（OAuth），或按 token 付费的 API 密钥 | `hermes model` → OAuth 登录（需要 Max + 额外额度），或 Anthropic API 密钥 |
| **OpenRouter** | 跨多个模型的多提供商路由 | 输入你的 API 密钥 |
| **Z.AI** | GLM / 智谱托管模型 | 设置 `GLM_API_KEY` / `ZAI_API_KEY` |
| **Kimi / Moonshot** | Moonshot 托管的编程和聊天模型 | 设置 `KIMI_API_KEY` |
| **Kimi / Moonshot 中国** | 中国区域的 Moonshot 端点 | 设置 `KIMI_CN_API_KEY` |
| **Arcee AI** | Trinity 模型 | 设置 `ARCEEAI_API_KEY` |
| **GMI Cloud** | 多模型直接 API | 设置 `GMI_API_KEY` |
| **MiniMax (OAuth)** | 通过浏览器 OAuth 使用 MiniMax-M2.7 — 无需 API 密钥 | `hermes model` → MiniMax (OAuth) |
| **MiniMax** | 国际 MiniMax 端点 | 设置 `MINIMAX_API_KEY` |
| **MiniMax 中国** | 中国区域 MiniMax 端点 | 设置 `MINIMAX_CN_API_KEY` |
| **阿里云** | 通过 DashScope 使用 Qwen 模型 | 设置 `DASHSCOPE_API_KEY` |
| **Hugging Face** | 通过统一路由器使用 20+ 个开放模型（Qwen、DeepSeek、Kimi 等） | 设置 `HF_TOKEN` |
| **Kilo Code** | KiloCode 托管模型 | 设置 `KILOCODE_API_KEY` |
| **OpenCode Zen** | 按量付费访问精选模型 | 设置 `OPENCODE_ZEN_API_KEY` |
| **OpenCode Go** | 每月 10 美元订阅开放模型 | 设置 `OPENCODE_GO_API_KEY` |
| **DeepSeek** | 直接 DeepSeek API 访问 | 设置 `DEEPSEEK_API_KEY` |
| **NVIDIA NIM** | 通过 build.nvidia.com 或本地 NIM 使用 Nemotron 模型 | 设置 `NVIDIA_API_KEY`（可选：`NVIDIA_BASE_URL`） |
| **GitHub Copilot** | GitHub Copilot 订阅（GPT-5.x、Claude、Gemini 等） | 通过 `hermes model` 进行 OAuth，或设置 `COPILOT_GITHUB_TOKEN` / `GH_TOKEN` |
| **GitHub Copilot ACP** | Copilot ACP 代理后端（启动本地 `copilot` CLI） | `hermes model`（需要 `copilot` CLI + `copilot login`） |
| **Vercel AI Gateway** | Vercel AI Gateway 路由 | 设置 `AI_GATEWAY_API_KEY` |
| **自定义端点** | VLLM、SGLang、Ollama 或任何兼容 OpenAI 的 API | 设置基础 URL + API 密钥 |
对于大多数首次使用的用户：选择一个提供商，除非你知道为什么要更改，否则接受默认设置。完整的提供商目录（包含环境变量和设置步骤）位于 [Providers](../integrations/providers.md) 页面。

:::caution 最小上下文：64K tokens
Hermes Agent 需要一个至少具有 **64,000 tokens** 上下文窗口的模型。上下文窗口较小的模型无法为多步工具调用工作流维持足够的工作记忆，并会在启动时被拒绝。大多数托管模型（Claude、GPT、Gemini、Qwen、DeepSeek）都能轻松满足这一要求。如果你在运行本地模型，请将其上下文大小设置为至少 64K（例如，对于 llama.cpp 使用 `--ctx-size 65536`，对于 Ollama 使用 `-c 65536`）。
:::

:::tip
你可以随时使用 `hermes model` 切换提供商——没有锁定。有关所有支持的提供商和设置细节的完整列表，请参阅 [AI Providers](../integrations/providers.md)。
<a id="minimum-context-64k-tokens"></a>
:::

### 设置如何存储 {#how-settings-are-stored}

Hermes 将机密信息与普通配置分开：

- **机密信息和令牌** → `~/.hermes/.env`
- **非机密设置** → `~/.hermes/config.yaml`

通过 CLI 设置值是最简单的方法：

```bash
hermes config set model anthropic/claude-opus-4.6
hermes config set terminal.backend docker
hermes config set OPENROUTER_API_KEY sk-or-...
```

正确的值会自动写入正确的文件。

## 3. 运行你的第一次对话 {#3-run-your-first-chat}

```bash
hermes            # classic CLI
hermes --tui      # modern TUI (recommended)
```

你会看到一个欢迎横幅，显示你的模型、可用工具和技能。使用一个具体且易于验证的提示：

:::tip 选择你的界面
Hermes 提供两种终端界面：经典的 `prompt_toolkit` CLI 和更新的 [TUI](../user-guide/tui.md)（具有模态覆盖、鼠标选择和非阻塞输入）。两者共享相同的会话、斜杠命令和配置——分别使用 `hermes` 和 `hermes --tui` 尝试每种界面。
:::

<a id="pick-your-interface"></a>
```
Summarize this repo in 5 bullets and tell me what the main entrypoint is.
```

```
Check my current directory and tell me what looks like the main project file.
```

```
Help me set up a clean GitHub PR workflow for this codebase.
```

**成功的样子：**

- 横幅显示你选择的模型/提供商
- Hermes 无错误地回复
- 它可以在需要时使用工具（终端、文件读取、网络搜索）
- 对话正常进行超过一轮

如果这些都正常，你就已经度过了最困难的部分。

## 4. 验证会话是否正常工作 {#4-verify-sessions-work}

在继续之前，确保恢复功能正常工作：

```bash
hermes --continue    # Resume the most recent session
hermes -c            # Short form
```

这应该会带你回到刚才的会话。如果没有，请检查你是否在同一个配置文件中，以及会话是否实际保存。这在以后你同时管理多个设置或机器时很重要。

## 5. 尝试关键功能 {#5-try-key-features}

### 使用终端 {#use-the-terminal}

```
❯ What's my disk usage? Show the top 5 largest directories.
```

Agent 会代表你运行终端命令并显示结果。

### 斜杠命令 {#slash-commands}

输入 `/` 查看所有命令的自动补全下拉列表：
| 命令 | 功能 |
|---------|-------------|
| `/help` | 显示所有可用命令 |
| `/tools` | 列出可用工具 |
| `/model` | 交互式切换模型 |
| `/personality pirate` | 尝试有趣的个性 |
| `/save` | 保存对话 |

### 多行输入 {#multi-line-input}

按 `Alt+Enter` 或 `Ctrl+J` 添加新行。非常适合粘贴代码或编写详细提示。

### 中断 agent {#interrupt-the-agent}

如果 agent 执行时间过长，输入新消息并按 Enter 键——它会中断当前任务并切换到你的新指令。`Ctrl+C` 同样有效。

## 6. 添加下一层 {#6-add-the-next-layer}

仅在基础聊天正常工作后进行。选择你需要的功能：

### 机器人或共享助手 {#bot-or-shared-assistant}

```bash
hermes gateway setup    # 交互式平台配置
```

连接 [Telegram](/user-guide/messaging/telegram)、[Discord](/user-guide/messaging/discord)、[Slack](/user-guide/messaging/slack)、[WhatsApp](/user-guide/messaging/whatsapp)、[Signal](/user-guide/messaging/signal)、[Email](/user-guide/messaging/email) 或 [Home Assistant](/user-guide/messaging/homeassistant)。

### 自动化与工具 {#automation-and-tools}

- `hermes tools` — 按平台调整工具访问权限
- `hermes skills` — 浏览并安装可复用工作流
- Cron — 仅在机器人或 CLI 设置稳定后使用

### 沙箱终端 {#sandboxed-terminal}

为了安全，在 Docker 容器或远程服务器上运行 agent：

```bash
hermes config set terminal.backend docker    # Docker 隔离
hermes config set terminal.backend ssh       # 远程服务器
```

### 语音模式 {#voice-mode}

```bash
pip install "hermes-agent[voice]"
# 包含 faster-whisper，用于免费本地语音转文字
```

然后在 CLI 中：`/voice on`。按 `Ctrl+B` 开始录音。详见 [语音模式](../user-guide/features/voice-mode.md)。

### 技能 {#skills}

```bash
hermes skills search kubernetes
hermes skills install openai/skills/k8s
```

或在聊天会话中使用 `/skills`。

### MCP 服务器 {#mcp-servers}

```yaml
# 添加到 ~/.hermes/config.yaml
mcp_servers:
  github:
    command: npx
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "ghp_xxx"
```

### 编辑器集成 (ACP) {#editor-integration-acp}

```bash
pip install -e '.[acp]'
hermes acp
```

详见 [ACP 编辑器集成](../user-guide/features/acp.md)。

---

## 常见故障模式 {#common-failure-modes}

以下是浪费最多时间的问题：

| 症状 | 可能原因 | 修复方法 |
|---|---|---|
| Hermes 启动但返回空或错误的回复 | 提供商认证或模型选择错误 | 重新运行 `hermes model` 并确认提供商、模型和认证 |
| 自定义端点“能用”但返回垃圾内容 | 基础 URL、模型名称错误，或实际上不兼容 OpenAI | 先在独立客户端中验证端点 |
| 网关启动但无人能发送消息 | 机器人令牌、允许列表或平台设置不完整 | 重新运行 `hermes gateway setup` 并检查 `hermes gateway status` |
| `hermes --continue` 找不到旧会话 | 切换了配置文件或会话从未保存 | 检查 `hermes sessions list` 并确认你在正确的配置文件中 |
| 模型不可用或出现奇怪的降级行为 | 提供商路由或降级设置过于激进 | 在基础提供商稳定之前关闭路由 |
| `hermes doctor` 标记配置问题 | 配置值缺失或过期 | 修复配置，在添加功能前重新测试普通聊天 |
## 恢复工具包 {#recovery-toolkit}

当感觉不对劲时，按以下顺序操作：

1. `hermes doctor`
2. `hermes model`
3. `hermes setup`
4. `hermes sessions list`
5. `hermes --continue`
6. `hermes gateway status`

这个序列能让你从“状态异常”快速回到已知的正常状态。

---

## 快速参考 {#quick-reference}

| 命令 | 说明 |
|---------|-------------|
| `hermes` | 开始聊天 |
| `hermes model` | 选择你的 LLM 提供商和模型 |
| `hermes tools` | 配置每个平台启用的工具 |
| `hermes setup` | 完整设置向导（一次性配置所有内容） |
| `hermes doctor` | 诊断问题 |
| `hermes update` | 更新到最新版本 |
| `hermes gateway` | 启动消息网关 |
| `hermes --continue` | 恢复上次会话 |

## 下一步 {#next-steps}

- **[CLI 指南](../user-guide/cli.md)** — 掌握终端界面
- **[配置](../user-guide/configuration.md)** — 自定义你的设置
- **[消息网关](../user-guide/messaging/index.md)** — 连接 Telegram、Discord、Slack、WhatsApp、Signal、Email 或 Home Assistant
- **[工具与工具集](../user-guide/features/tools.md)** — 探索可用能力
- **[AI 提供商](../integrations/providers.md)** — 完整提供商列表及设置详情
- **[技能系统](../user-guide/features/skills.md)** — 可复用的工作流与知识
- **[技巧与最佳实践](../guides/tips.md)** — 高级用户技巧
