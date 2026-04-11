---
sidebar_position: 1
title: "快速入门"
description: "与 Hermes Agent 的第一次对话——从安装到开始聊天仅需 2 分钟"
---

# 快速入门

本指南将带你完成 Hermes Agent 的安装、配置提供商，并进行第一次对话。阅读完本指南，你将了解核心功能以及如何进一步探索。

## 1. 安装 Hermes Agent

运行一行安装命令：

```bash
# Linux / macOS / WSL2 / Android (Termux)
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

:::tip Android / Termux
如果你是在手机上安装，请参阅专门的 [Termux 指南](./termux.md)，了解经过测试的手动安装路径、支持的额外功能以及当前 Android 特有的限制。
:::

:::tip Windows 用户
请先安装 [WSL2](https://learn.microsoft.com/en-us/windows/wsl/install)，然后在 WSL2 终端中运行上述命令。
:::

安装完成后，重新加载你的 shell：

```bash
source ~/.bashrc   # 或者 source ~/.zshrc
```

## 2. 设置提供商

安装程序会自动配置你的 LLM 提供商。若后续需要更改，请使用以下命令：

```bash
hermes model       # 选择你的 LLM 提供商和模型
hermes tools       # 配置启用的工具
hermes setup       # 或一次性配置所有内容
```

`hermes model` 会引导你选择推理提供商：

| 提供商 | 说明 | 设置方式 |
|----------|-----------|---------------|
| **Nous Portal** | 基于订阅，零配置 | 通过 `hermes model` 进行 OAuth 登录 |
| **OpenAI Codex** | ChatGPT OAuth，使用 Codex 模型 | 通过 `hermes model` 进行设备代码验证 |
| **Anthropic** | 直接使用 Claude 模型 (Pro/Max 或 API Key) | 使用 Claude Code 验证的 `hermes model`，或使用 Anthropic API Key |
| **OpenRouter** | 跨多种模型的多提供商路由 | 输入你的 API Key |
| **Z.AI** | GLM / 智谱托管模型 | 设置 `GLM_API_KEY` / `ZAI_API_KEY` |
| **Kimi / Moonshot** | Moonshot 托管的编程和聊天模型 | 设置 `KIMI_API_KEY` |
| **MiniMax** | 国际版 MiniMax 端点 | 设置 `MINIMAX_API_KEY` |
| **MiniMax China** | 中国区 MiniMax 端点 | 设置 `MINIMAX_CN_API_KEY` |
| **Alibaba Cloud** | 通过 DashScope 使用通义千问 (Qwen) 模型 | 设置 `DASHSCOPE_API_KEY` |
| **Hugging Face** | 通过统一路由使用 20+ 开源模型 (Qwen, DeepSeek, Kimi 等) | 设置 `HF_TOKEN` |
| **Kilo Code** | KiloCode 托管模型 | 设置 `KILOCODE_API_KEY` |
| **OpenCode Zen** | 按量付费访问精选模型 | 设置 `OPENCODE_ZEN_API_KEY` |
| **OpenCode Go** | 10 美元/月订阅访问开源模型 | 设置 `OPENCODE_GO_API_KEY` |
| **DeepSeek** | 直接访问 DeepSeek API | 设置 `DEEPSEEK_API_KEY` |
| **GitHub Copilot** | GitHub Copilot 订阅 (GPT-5.x, Claude, Gemini 等) | 通过 `hermes model` 进行 OAuth，或使用 `COPILOT_GITHUB_TOKEN` / `GH_TOKEN` |
| **GitHub Copilot ACP** | Copilot ACP agent 后端 (启动本地 `copilot` CLI) | `hermes model` (需要 `copilot` CLI + `copilot login`) |
| **Vercel AI Gateway** | Vercel AI Gateway 路由 | 设置 `AI_GATEWAY_API_KEY` |
| **Custom Endpoint** | VLLM, SGLang, Ollama 或任何兼容 OpenAI 的 API | 设置基础 URL + API Key |

:::tip
你可以随时使用 `hermes model` 切换提供商——无需更改代码，也不会被锁定。配置自定义端点时，Hermes 会提示输入上下文窗口大小，并在可能的情况下自动检测。详情请参阅 [上下文长度检测](../integrations/providers.md#context-length-detection)。
:::

## 3. 开始聊天

```bash
hermes
```

就是这样！你将看到一个欢迎横幅，显示你的模型、可用工具和技能。输入消息并按回车键即可。

```
❯ 你能帮我做什么？
```

该 Agent 开箱即用，具备网页搜索、文件操作、终端命令执行等多种工具。

## 4. 尝试核心功能

### 让它使用终端

```
❯ 我的磁盘使用情况如何？显示占用空间最大的前 5 个目录。
```

Agent 将代表你运行终端命令并向你展示结果。

### 使用斜杠命令

输入 `/` 查看所有命令的自动补全下拉菜单：

| 命令 | 功能 |
|---------|-------------|
| `/help` | 显示所有可用命令 |
| `/tools` | 列出可用工具 |
| `/model` | 交互式切换模型 |
| `/personality pirate` | 尝试一种有趣的个性 |
| `/save` | 保存对话 |

### 多行输入

按 `Alt+Enter` 或 `Ctrl+J` 添加新行。这非常适合粘贴代码或编写详细的提示词。

### 中断 Agent

如果 Agent 执行时间过长，只需输入一条新消息并按回车键——它会中断当前任务并切换到你的新指令。`Ctrl+C` 同样有效。

### 恢复会话

当你退出时，hermes 会打印一条恢复命令：

```bash
hermes --continue    # 恢复最近的会话
hermes -c            # 简写形式
```

## 5. 进一步探索

以下是一些你可以尝试的操作：

### 设置沙盒终端

为了安全起见，可以在 Docker 容器或远程服务器中运行 Agent：

```bash
hermes config set terminal.backend docker    # Docker 隔离
hermes config set terminal.backend ssh       # 远程服务器
```

### 连接消息平台

通过 Telegram、Discord、Slack、WhatsApp、Signal、电子邮件或 Home Assistant 在手机或其他终端上与 Hermes 聊天：

```bash
hermes gateway setup    # 交互式平台配置
```

### 添加语音模式

想要在 CLI 中使用麦克风输入，或在消息平台中获取语音回复？

```bash
pip install "hermes-agent[voice]"

# 可选但推荐，用于免费的本地语音转文字
pip install faster-whisper
```

然后启动 Hermes 并在 CLI 中启用它：

```text
/voice on
```

按 `Ctrl+B` 进行录音，或使用 `/voice tts` 让 Hermes 朗读回复。请参阅 [语音模式](../user-guide/features/voice-mode.md) 了解在 CLI、Telegram、Discord 和 Discord 语音频道中的完整设置。

### 调度自动化任务

```
❯ 每天早上 9 点，检查 Hacker News 上的 AI 新闻，并通过 Telegram 发送摘要给我。
```

Agent 将设置一个 cron 任务，通过网关自动运行。

### 浏览并安装技能

```bash
hermes skills search kubernetes
hermes skills search react --source skills-sh
hermes skills search https://mintlify.com/docs --source well-known
hermes skills install openai/skills/k8s
hermes skills install official/security/1password
hermes skills install skills-sh/vercel-labs/json-render/json-render-react --force
```

提示：
- 使用 `--source skills-sh` 搜索公共 `skills.sh` 目录。
- 使用 `--source well-known` 配合文档/站点 URL，从 `/.well-known/skills/index.json` 中发现技能。
- 仅在审查第三方技能后使用 `--force`。它可能会覆盖非危险策略拦截，但无法覆盖 `dangerous`（危险）扫描结果。

或者在聊天中使用 `/skills` 斜杠命令。

### 通过 ACP 在编辑器中使用 Hermes

Hermes 也可以作为 ACP 服务器运行，供 VS Code、Zed 和 JetBrains 等支持 ACP 的编辑器使用：

```bash
pip install -e '.[acp]'
hermes acp
```

请参阅 [ACP 编辑器集成](../user-guide/features/acp.md) 了解设置详情。

### 尝试 MCP 服务器

通过模型上下文协议 (Model Context Protocol) 连接外部工具：

```yaml
# 添加到 ~/.hermes/config.yaml
mcp_servers:
  github:
    command: npx
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "ghp_xxx"
```

---

## 快速参考

| 命令 | 描述 |
|---------|-------------|
| `hermes` | 开始聊天 |
| `hermes model` | 选择你的 LLM 提供商和模型 |
| `hermes tools` | 配置每个平台启用的工具 |
| `hermes setup` | 完整设置向导（一次性配置所有内容） |
| `hermes doctor` | 诊断问题 |
| `hermes update` | 更新到最新版本 |
| `hermes gateway` | 启动消息网关 |
| `hermes --continue` | 恢复上次会话 |

## 后续步骤

- **[CLI 指南](../user-guide/cli.md)** — 掌握终端界面
- **[配置](../user-guide/configuration.md)** — 自定义你的设置
- **[消息网关](../user-guide/messaging/index.md)** — 连接 Telegram、Discord、Slack、WhatsApp、Signal、电子邮件或 Home Assistant
- **[工具与工具集](../user-guide/features/tools.md)** — 探索可用功能
