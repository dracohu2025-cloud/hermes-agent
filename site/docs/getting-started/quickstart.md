---
sidebar_position: 1
title: "快速开始"
description: "与 Hermes Agent 的初次对话 —— 从安装到聊天只需 2 分钟"
---

# 快速开始

本指南将引导你完成安装 Hermes Agent、设置提供商并进行首次对话。结束时，你将了解其主要功能以及如何进一步探索。

## 1. 安装 Hermes Agent

运行一行式安装命令：

```bash
# Linux / macOS / WSL2
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

:::tip Windows 用户
请先安装 [WSL2](https://learn.microsoft.com/en-us/windows/wsl/install)，然后在 WSL2 终端内运行上述命令。
:::

安装完成后，重新加载你的 shell：

```bash
source ~/.bashrc   # 或者 source ~/.zshrc
```

## 2. 设置提供商

安装程序会自动配置你的 LLM 提供商。之后如需更改，可以使用以下任一命令：

```bash
hermes model       # 选择你的 LLM 提供商和模型
hermes tools       # 配置启用哪些工具
hermes setup       # 或者一次性配置所有内容
```

`hermes model` 会引导你选择推理提供商：

| 提供商 | 说明 | 如何设置 |
|----------|-----------|---------------|
| **Nous Portal** | 基于订阅，零配置 | 通过 `hermes model` 进行 OAuth 登录 |
| **OpenAI Codex** | ChatGPT OAuth，使用 Codex 模型 | 通过 `hermes model` 进行设备代码认证 |
| **Anthropic** | 直接使用 Claude 模型 (Pro/Max 或 API 密钥) | 通过 `hermes model` 使用 Claude Code 认证，或提供 Anthropic API 密钥 |
| **OpenRouter** | 跨多个模型的多提供商路由 | 输入你的 API 密钥 |
| **Z.AI** | GLM / 智谱托管模型 | 设置 `GLM_API_KEY` / `ZAI_API_KEY` |
| **Kimi / Moonshot** | Moonshot 托管的代码和聊天模型 | 设置 `KIMI_API_KEY` |
| **MiniMax** | 国际版 MiniMax 端点 | 设置 `MINIMAX_API_KEY` |
| **MiniMax China** | 中国区 MiniMax 端点 | 设置 `MINIMAX_CN_API_KEY` |
| **Alibaba Cloud** | 通过 DashScope 使用通义千问模型 | 设置 `DASHSCOPE_API_KEY` |
| **Hugging Face** | 通过统一路由使用 20+ 开源模型 (Qwen, DeepSeek, Kimi 等) | 设置 `HF_TOKEN` |
| **Kilo Code** | KiloCode 托管模型 | 设置 `KILOCODE_API_KEY` |
| **OpenCode Zen** | 按需付费访问精选模型 | 设置 `OPENCODE_ZEN_API_KEY` |
| **OpenCode Go** | 每月 10 美元订阅开源模型 | 设置 `OPENCODE_GO_API_KEY` |
| **Vercel AI Gateway** | Vercel AI Gateway 路由 | 设置 `AI_GATEWAY_API_KEY` |
| **自定义端点** | VLLM, SGLang, Ollama 或任何 OpenAI 兼容的 API | 设置基础 URL + API 密钥 |

:::tip
你可以随时使用 `hermes model` 切换提供商 —— 无需更改代码，没有锁定。配置自定义端点时，Hermes 会提示输入上下文窗口大小，并在可能时自动检测。详情请参阅[上下文长度检测](../user-guide/configuration.md#context-length-detection)。
:::

## 3. 开始聊天

```bash
hermes
```

就这样！你会看到一个欢迎横幅，显示你的模型、可用工具和技能。输入消息并按回车键。

```
❯ 你能帮我做什么？
```

智能体可以访问用于网络搜索、文件操作、终端命令等工具 —— 所有这些都开箱即用。

## 4. 尝试关键功能

### 让它使用终端

```
❯ 我的磁盘使用情况如何？显示前 5 个最大的目录。
```

智能体会代表你运行终端命令并显示结果。

### 使用斜杠命令

输入 `/` 查看所有命令的自动补全下拉列表：

| 命令 | 功能 |
|---------|-------------|
| `/help` | 显示所有可用命令 |
| `/tools` | 列出可用工具 |
| `/model` | 交互式切换模型 |
| `/personality pirate` | 尝试一个有趣的个性 |
| `/save` | 保存对话 |

### 多行输入

按 `Alt+Enter` 或 `Ctrl+J` 添加新行。非常适合粘贴代码或编写详细的提示。

### 中断智能体

如果智能体耗时过长，只需输入新消息并按回车键 —— 它会中断当前任务并切换到你的新指令。`Ctrl+C` 也有效。

### 恢复会话

当你退出时，hermes 会打印一个恢复命令：

```bash
hermes --continue    # 恢复最近的会话
hermes -c            # 简写形式
```

## 5. 进一步探索

接下来可以尝试以下内容：

### 设置沙盒化终端

为了安全起见，可以在 Docker 容器或远程服务器上运行智能体：

```bash
hermes config set terminal.backend docker    # Docker 隔离
hermes config set terminal.backend ssh       # 远程服务器
```

### 连接消息平台

通过 Telegram、Discord、Slack、WhatsApp、Signal、Email 或 Home Assistant 从手机或其他界面与 Hermes 聊天：

```bash
hermes gateway setup    # 交互式平台配置
```

### 添加语音模式

想在 CLI 中使用麦克风输入或在消息平台中听到语音回复吗？

```bash
pip install "hermes-agent[voice]"

# 可选但推荐用于免费的本地语音转文本
pip install faster-whisper
```

然后在 CLI 中启动 Hermes 并启用它：

```text
/voice on
```

按 `Ctrl+B` 录音，或使用 `/voice tts` 让 Hermes 说出它的回复。有关在 CLI、Telegram、Discord 和 Discord 语音频道中的完整设置，请参阅[语音模式](../user-guide/features/voice-mode.md)。

### 安排自动化任务

```
❯ 每天早上 9 点，检查 Hacker News 上的 AI 新闻，并通过 Telegram 发送摘要给我。
```

智能体会通过网关设置一个自动运行的 cron 任务。

### 浏览和安装技能

```bash
hermes skills search kubernetes
hermes skills search react --source skills-sh
hermes skills search https://mintlify.com/docs --source well-known
hermes skills install openai/skills/k8s
hermes skills install official/security/1password
hermes skills install skills-sh/vercel-labs/json-render/json-render-react --force
```

提示：
- 使用 `--source skills-sh` 搜索公共的 `skills.sh` 目录。
- 使用 `--source well-known` 配合文档/站点 URL，从 `/.well-known/skills/index.json` 发现技能。
- 仅在审查第三方技能后使用 `--force`。它可以覆盖非危险策略阻止，但不能覆盖 `dangerous` 扫描判定。

或者在聊天中使用 `/skills` 斜杠命令。

### 通过 ACP 在编辑器内使用 Hermes

Hermes 也可以作为 ACP 服务器运行，用于 VS Code、Zed 和 JetBrains 等兼容 ACP 的编辑器：

```bash
pip install -e '.[acp]'
hermes acp
```

有关设置详情，请参阅 [ACP 编辑器集成](../user-guide/features/acp.md)。

### 尝试 MCP 服务器

通过模型上下文协议连接到外部工具：

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
| `hermes tools` | 按平台配置启用哪些工具 |
| `hermes setup` | 完整设置向导 (一次性配置所有内容) |
| `hermes doctor` | 诊断问题 |
| `hermes update` | 更新到最新版本 |
| `hermes gateway` | 启动消息网关 |
| `hermes --continue` | 恢复上次会话 |

## 后续步骤

- **[CLI 指南](../user-guide/cli.md)** — 掌握终端界面
- **[配置](../user-guide/configuration.md)** — 自定义你的设置
- **[消息网关](../user-guide/messaging/index.md)** — 连接 Telegram、Discord、Slack、WhatsApp、Signal、Email 或 Home Assistant
- **[工具与工具集](../user-guide/features/tools.md)** — 探索可用功能
