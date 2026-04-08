---
sidebar_position: 1
title: "快速入门"
description: "与 Hermes Agent 的第一次对话 —— 从安装到聊天只需 2 分钟"
---

# 快速入门

本指南将带你完成 Hermes Agent 的安装、Provider（模型提供商）设置以及开启你的第一次对话。读完本文，你将了解其核心功能以及如何进一步探索。

## 1. 安装 Hermes Agent

运行单行安装命令：

```bash
# Linux / macOS / WSL2
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

:::tip Windows 用户
请先安装 [WSL2](https://learn.microsoft.com/zh-cn/windows/wsl/install)，然后在 WSL2 终端内运行上述命令。
:::

安装完成后，重新加载你的 shell 配置：

```bash
source ~/.bashrc   # 或 source ~/.zshrc
```

## 2. 设置 Provider

安装程序会自动配置你的 LLM Provider。如果以后想更改，可以使用以下命令：

```bash
hermes model       # 选择你的 LLM Provider 和模型
hermes tools       # 配置启用的工具
hermes setup       # 或者一次性配置所有内容
```

`hermes model` 会引导你选择推理 Provider：

| Provider | 说明 | 如何设置 |
|----------|-----------|---------------|
| **Nous Portal** | 基于订阅，零配置 | 通过 `hermes model` 进行 OAuth 登录 |
| **OpenAI Codex** | ChatGPT OAuth，使用 Codex 模型 | 通过 `hermes model` 进行设备代码认证 |
| **Anthropic** | 直接使用 Claude 模型 (Pro/Max 或 API key) | 使用 Claude Code 认证或 Anthropic API key |
| **OpenRouter** | 跨多个模型的路由服务 | 输入你的 API key |
| **Z.AI** | 智谱 (Zhipu) 托管的模型 | 设置 `GLM_API_KEY` / `ZAI_API_KEY` |
| **Kimi / Moonshot** | Moonshot 托管的代码和对话模型 | 设置 `KIMI_API_KEY` |
| **MiniMax** | MiniMax 国际版端点 | 设置 `MINIMAX_API_KEY` |
| **MiniMax China** | MiniMax 中国区端点 | 设置 `MINIMAX_CN_API_KEY` |
| **Alibaba Cloud** | 通过 DashScope 使用通义千问模型 | 设置 `DASHSCOPE_API_KEY` |
| **Hugging Face** | 通过统一路由访问 20+ 开源模型 (Qwen, DeepSeek, Kimi 等) | 设置 `HF_TOKEN` |
| **Kilo Code** | KiloCode 托管的模型 | 设置 `KILOCODE_API_KEY` |
| **OpenCode Zen** | 按需付费访问精选模型 | 设置 `OPENCODE_ZEN_API_KEY` |
| **OpenCode Go** | $10/月订阅访问开源模型 | 设置 `OPENCODE_GO_API_KEY` |
| **DeepSeek** | 直接访问 DeepSeek API | 设置 `DEEPSEEK_API_KEY` |
| **GitHub Copilot** | GitHub Copilot 订阅 (GPT-5.x, Claude, Gemini 等) | 通过 `hermes model` 进行 OAuth，或设置 `COPILOT_GITHUB_TOKEN` / `GH_TOKEN` |
| **GitHub Copilot ACP** | Copilot ACP Agent 后端 (启动本地 `copilot` CLI) | `hermes model` (需要 `copilot` CLI + `copilot login`) |
| **Vercel AI Gateway** | Vercel AI Gateway 路由 | 设置 `AI_GATEWAY_API_KEY` |
| **Custom Endpoint** | VLLM, SGLang, Ollama 或任何兼容 OpenAI 的 API | 设置 base URL + API key |

:::tip
你可以随时通过 `hermes model` 切换 Provider —— 无需修改代码，没有平台锁定。在配置自定义端点时，Hermes 会提示输入上下文窗口大小，并在可能的情况下自动检测。详见 [上下文长度检测](../integrations/providers.md#context-length-detection)。
:::

## 3. 开始聊天

```bash
hermes
```

就这样！你会看到一个欢迎横幅，显示你的模型、可用工具和技能。输入消息并按回车。

```
❯ 你能帮我做什么？
```

该 Agent 拥有访问网页搜索、文件操作、终端命令等工具的权限 —— 全部开箱即用。

## 4. 尝试核心功能

### 让它使用终端

```
❯ 我的磁盘占用情况如何？显示前 5 个最大的目录。
```

Agent 将代表你运行终端命令并向你展示结果。

### 使用斜杠命令

输入 `/` 查看所有命令的自动补全下拉列表：

| 命令 | 功能 |
|---------|-------------|
| `/help` | 显示所有可用命令 |
| `/tools` | 列出可用工具 |
| `/model` | 交互式切换模型 |
| `/personality pirate` | 尝试有趣的“海盗”人格 |
| `/save` | 保存对话 |

### 多行输入

按 `Alt+Enter` 或 `Ctrl+J` 添加新行。非常适合粘贴代码或编写详细的 Prompt。

### 中断 Agent

如果 Agent 运行时间太长，只需输入新消息并按回车 —— 它会中断当前任务并切换到你的新指令。`Ctrl+C` 同样有效。

### 恢复会话

当你退出时，hermes 会打印一条恢复命令：

```bash
hermes --continue    # 恢复最近的会话
hermes -c            # 简写形式
```

## 5. 进一步探索

以下是接下来可以尝试的内容：

### 设置沙盒终端

为了安全起见，可以在 Docker 容器或远程服务器上运行 Agent：

```bash
hermes config set terminal.backend docker    # Docker 隔离
hermes config set terminal.backend ssh       # 远程服务器
```

### 连接即时通讯平台

通过 Telegram、Discord、Slack、WhatsApp、Signal、电子邮件或 Home Assistant 在手机或其他终端上与 Hermes 聊天：

```bash
hermes gateway setup    # 交互式平台配置
```

### 添加语音模式

想要在 CLI 中使用麦克风输入，或在消息平台中获得语音回复？

```bash
pip install "hermes-agent[voice]"

# 可选但推荐，用于免费的本地语音转文字
pip install faster-whisper
```

然后启动 Hermes 并在 CLI 内部启用它：

```text
/voice on
```

按 `Ctrl+B` 进行录音，或使用 `/voice tts` 让 Hermes 朗读回复。参见 [语音模式](../user-guide/features/voice-mode.md) 了解 CLI、Telegram、Discord 及 Discord 语音频道的完整设置。

### 安排自动化任务

```
❯ 每天早上 9 点，检查 Hacker News 上的 AI 新闻，并在 Telegram 上给我发送摘要。
```

Agent 将设置一个 cron 任务，通过 gateway 自动运行。

### 浏览并安装技能 (Skills)

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
- 使用 `--source well-known` 配合文档/网站 URL，从 `/.well-known/skills/index.json` 发现技能。
- 仅在审查过第三方技能后使用 `--force`。它可以覆盖非危险策略块，但不能覆盖 `dangerous` 扫描判定。

或者在聊天中使用 `/skills` 斜杠命令。

### 通过 ACP 在编辑器中使用 Hermes

Hermes 还可以作为 ACP 服务端运行，支持 VS Code、Zed 和 JetBrains 等兼容 ACP 的编辑器：

```bash
pip install -e '.[acp]'
hermes acp
```

参见 [ACP 编辑器集成](../user-guide/features/acp.md) 了解设置详情。

### 尝试 MCP 服务端

通过 Model Context Protocol 连接外部工具：

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
| `hermes model` | 选择你的 LLM Provider 和模型 |
| `hermes tools` | 配置每个平台启用的工具 |
| `hermes setup` | 完整设置向导（一次性配置所有内容） |
| `hermes doctor` | 诊断问题 |
| `hermes update` | 更新到最新版本 |
| `hermes gateway` | 启动消息 Gateway |
| `hermes --continue` | 恢复上次会话 |

## 后续步骤

- **[CLI 指南](../user-guide/cli.md)** — 精通终端界面
- **[配置](../user-guide/configuration.md)** — 自定义你的设置
- **[消息 Gateway](../user-guide/messaging/index.md)** — 连接 Telegram, Discord, Slack, WhatsApp, Signal, Email 或 Home Assistant
- **[工具与工具集](../user-guide/features/tools.md)** — 探索可用功能
