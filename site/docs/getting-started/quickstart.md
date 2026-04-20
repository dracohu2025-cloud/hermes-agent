---
sidebar_position: 1
title: "快速开始"
description: "与 Hermes Agent 的初次对话 —— 从安装到聊天，5 分钟内完成"
---

<a id="quickstart"></a>
# 快速开始

本指南将带你从零开始，搭建一个能在实际使用中稳定运行的 Hermes 环境。完成安装、选择服务商、验证聊天功能，并确切知道当出现问题时该如何处理。

<a id="who-this-is-for"></a>
## 适用人群

-   初次接触，希望以最短路径完成可用配置
-   切换服务商，不想因配置错误浪费时间
-   为团队、机器人或常驻工作流设置 Hermes
-   厌倦了“安装成功，但依然无法使用”的情况

<a id="the-fastest-path"></a>
## 最快路径

根据你的目标选择对应行：

| 目标 | 先做这一步 | 然后做这一步 |
|---|---|---|
| 我只想让 Hermes 在我的机器上运行起来 | `hermes setup` | 进行一次真实聊天并验证其响应 |
| 我已经知道要用哪个服务商 | `hermes model` | 保存配置，然后开始聊天 |
| 我想要一个机器人或常驻设置 | 在 CLI 可用后运行 `hermes gateway setup` | 连接 Telegram、Discord、Slack 或其他平台 |
| 我想要本地或自托管模型 | `hermes model` → 自定义端点 | 验证端点、模型名称和上下文长度 |
| 我想要多服务商故障转移 | 先运行 `hermes model` | 仅在基础聊天功能正常后，再添加路由和故障转移 |

**经验法则：** 如果 Hermes 无法完成一次正常的聊天，请先不要添加更多功能。先让一次干净的对话成功运行，然后再叠加网关、定时任务、技能、语音或路由等功能。

---

<a id="1-install-hermes-agent"></a>
## 1. 安装 Hermes Agent

运行一行式安装脚本：

```bash
# Linux / macOS / WSL2 / Android (Termux)
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

:::tip Android / Termux
如果你在手机上安装，请查看专门的 [Termux 指南](./termux.md)，了解经过测试的手动安装路径、支持的额外功能以及当前 Android 特定的限制。
:::

:::tip Windows 用户
<a id="windows-users"></a>
请先安装 [WSL2](https://learn.microsoft.com/en-us/windows/wsl/install)，然后在你的 WSL2 终端内运行上述命令。
:::

安装完成后，重新加载你的 shell：

```bash
source ~/.bashrc   # 或 source ~/.zshrc
```

关于详细的安装选项、先决条件和故障排除，请参阅 [安装指南](./installation.md)。

<a id="2-choose-a-provider"></a>
## 2. 选择服务商

这是最重要的一个设置步骤。使用 `hermes model` 以交互方式完成选择：

```bash
hermes model
```

推荐的默认选项：

| 情况 | 推荐路径 |
|---|---|
| 最少麻烦 | Nous Portal 或 OpenRouter |
| 你已有 Claude 或 Codex 的授权 | Anthropic 或 OpenAI Codex |
| 你想要本地/私有推理 | Ollama 或任何自定义的 OpenAI 兼容端点 |
| 你想要多服务商路由 | OpenRouter |
| 你有一个自定义的 GPU 服务器 | vLLM、SGLang、LiteLLM 或任何 OpenAI 兼容端点 |
对于大多数首次使用的用户：选择一个提供商，除非你知道为什么要修改，否则就接受默认设置。完整的提供商目录、环境变量和设置步骤请查看 [Providers](../integrations/providers.md) 页面。

:::caution 最低上下文要求：64K tokens
Hermes Agent 需要一个至少具有 **64,000 tokens** 上下文的模型。上下文窗口较小的模型无法为多步骤工具调用工作流提供足够的工作内存，将在启动时被拒绝。大多数托管模型（Claude、GPT、Gemini、Qwen、DeepSeek）都能轻松满足此要求。如果你运行的是本地模型，请将其上下文大小设置为至少 64K（例如，对于 llama.cpp 使用 `--ctx-size 65536`，对于 Ollama 使用 `-c 65536`）。
:::
<a id="minimum-context-64k-tokens"></a>

:::tip
你可以随时使用 `hermes model` 切换提供商——没有锁定。有关所有支持的提供商的完整列表和设置详情，请参阅 [AI Providers](../integrations/providers.md)。
:::

<a id="how-settings-are-stored"></a>
### 设置如何存储

Hermes 将密钥与普通配置分开存储：

- **密钥和令牌** → `~/.hermes/.env`
- **非机密设置** → `~/.hermes/config.yaml`

通过 CLI 设置值是最简单的方法：

```bash
hermes config set model anthropic/claude-opus-4.6
hermes config set terminal.backend docker
hermes config set OPENROUTER_API_KEY sk-or-...
```

正确的值会自动存入正确的文件。

<a id="3-run-your-first-chat"></a>
## 3. 运行你的第一次聊天

```bash
hermes            # 经典 CLI
hermes --tui      # 现代 TUI（推荐）
```

你将看到一个欢迎横幅，显示你的模型、可用工具和技能。使用一个具体且易于验证的提示：

:::tip 选择你的界面
<a id="pick-your-interface"></a>
Hermes 附带两种终端界面：经典的 `prompt_toolkit` CLI 和一个较新的 [TUI](../user-guide/tui.md)，后者具有模态叠加层、鼠标选择和非阻塞输入。两者共享相同的会话、斜杠命令和配置——分别使用 `hermes` 和 `hermes --tui` 尝试一下。
:::

```
用 5 个要点总结这个仓库，并告诉我主要的入口点是什么。
```

```
检查我当前的目录，告诉我哪个看起来是主要的项目文件。
```

```
帮我为这个代码库设置一个干净的 GitHub PR 工作流。
```

**成功的样子：**

- 横幅显示你选择的模型/提供商
- Hermes 无错误回复
- 如果需要，它可以使用工具（终端、文件读取、网络搜索）
- 对话可以正常持续多个回合

如果这些都正常，你就已经度过了最困难的部分。

<a id="4-verify-sessions-work"></a>
## 4. 验证会话工作

在继续之前，确保恢复功能正常工作：

```bash
hermes --continue    # 恢复最近的会话
hermes -c            # 简写形式
```
这样应该就能回到你刚才的会话了。如果不行，请检查你是否在同一个配置文件中，以及会话是否确实保存了。这在以后你同时处理多个配置或多台机器时会很重要。

<a id="5-try-key-features"></a>
## 5. 尝试关键功能

<a id="use-the-terminal"></a>
### 使用终端

```
❯ 我的磁盘使用情况如何？显示前 5 个最大的目录。
```

Agent 会代表你运行终端命令并显示结果。

<a id="slash-commands"></a>
### 斜杠命令

输入 `/` 可以查看所有命令的自动补全下拉菜单：

| 命令 | 功能 |
|---------|-------------|
| `/help` | 显示所有可用命令 |
| `/tools` | 列出可用工具 |
| `/model` | 交互式切换模型 |
| `/personality pirate` | 尝试一个有趣的个性 |
| `/save` | 保存对话 |

<a id="multi-line-input"></a>
### 多行输入

按 `Alt+Enter` 或 `Ctrl+J` 可以添加新行。非常适合粘贴代码或编写详细的提示。

<a id="interrupt-the-agent"></a>
### 中断 Agent

如果 Agent 耗时太长，可以输入新消息并按 Enter 键 —— 这会中断当前任务并切换到你的新指令。`Ctrl+C` 也有效。

<a id="6-add-the-next-layer"></a>
## 6. 添加下一层功能

仅在基础聊天功能正常工作后进行。按需选择：

<a id="bot-or-shared-assistant"></a>
### 机器人或共享助手

```bash
hermes gateway setup    # 交互式平台配置
```

连接 [Telegram](/user-guide/messaging/telegram)、[Discord](/user-guide/messaging/discord)、[Slack](/user-guide/messaging/slack)、[WhatsApp](/user-guide/messaging/whatsapp)、[Signal](/user-guide/messaging/signal)、[Email](/user-guide/messaging/email) 或 [Home Assistant](/user-guide/messaging/homeassistant)。

<a id="automation-and-tools"></a>
### 自动化和工具

- `hermes tools` — 按平台调整工具访问权限
- `hermes skills` — 浏览并安装可复用的工作流
- Cron — 仅在你的机器人或 CLI 设置稳定后使用

<a id="sandboxed-terminal"></a>
### 沙盒化终端

为了安全，可以在 Docker 容器或远程服务器上运行 Agent：

```bash
hermes config set terminal.backend docker    # Docker 隔离
hermes config set terminal.backend ssh       # 远程服务器
```

<a id="voice-mode"></a>
### 语音模式

```bash
pip install "hermes-agent[voice]"
# 包含 faster-whisper，用于免费的本地语音转文本
```

然后在 CLI 中：`/voice on`。按 `Ctrl+B` 录音。参见 [语音模式](../user-guide/features/voice-mode.md)。

<a id="skills"></a>
### 技能

```bash
hermes skills search kubernetes
hermes skills install openai/skills/k8s
```

或者在聊天会话中使用 `/skills` 命令。

<a id="mcp-servers"></a>
### MCP 服务器

```yaml
# 添加到 ~/.hermes/config.yaml
mcp_servers:
  github:
    command: npx
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "ghp_xxx"
```
<a id="editor-integration-acp"></a>
### 编辑器集成 (ACP)

```bash
pip install -e '.[acp]'
hermes acp
```

详见 [ACP 编辑器集成](../user-guide/features/acp.md)。

---

<a id="common-failure-modes"></a>
## 常见故障模式

这些问题最浪费时间：

| 现象 | 可能原因 | 解决方法 |
|---|---|---|
| Hermes 能打开但回复为空或异常 | 提供商认证或模型选择错误 | 再次运行 `hermes model` 并确认提供商、模型和认证信息 |
| 自定义端点“可用”但返回乱码 | 基础 URL、模型名称错误，或端点并非真正兼容 OpenAI | 先用单独的客户端验证端点 |
| 网关启动但无人能发送消息 | 机器人令牌、允许列表或平台设置不完整 | 重新运行 `hermes gateway setup` 并检查 `hermes gateway status` |
| `hermes --continue` 找不到旧会话 | 切换了配置文件或会话从未保存 | 检查 `hermes sessions list` 并确认你使用了正确的配置文件 |
| 模型不可用或出现奇怪的降级行为 | 提供商路由或降级设置过于激进 | 在基础提供商稳定前，先关闭路由功能 |
| `hermes doctor` 提示配置问题 | 配置值缺失或已过时 | 修复配置，在添加功能前先用简单聊天测试 |

<a id="recovery-toolkit"></a>
## 恢复工具包

感觉不对劲时，按此顺序操作：

1. `hermes doctor`
2. `hermes model`
3. `hermes setup`
4. `hermes sessions list`
5. `hermes --continue`
6. `hermes gateway status`

这个流程能让你从“感觉不对劲”快速回到已知的正常状态。

---

<a id="quick-reference"></a>
## 速查表

| 命令 | 描述 |
|---------|-------------|
| `hermes` | 开始聊天 |
| `hermes model` | 选择你的 LLM 提供商和模型 |
| `hermes tools` | 配置每个平台启用哪些工具 |
| `hermes setup` | 完整设置向导（一次性配置所有内容） |
| `hermes doctor` | 诊断问题 |
| `hermes update` | 更新到最新版本 |
| `hermes gateway` | 启动消息网关 |
| `hermes --continue` | 恢复上次会话 |

<a id="next-steps"></a>
## 后续步骤

- **[CLI 指南](../user-guide/cli.md)** — 掌握终端界面
- **[配置](../user-guide/configuration.md)** — 自定义你的设置
- **[消息网关](../user-guide/messaging/index.md)** — 连接 Telegram、Discord、Slack、WhatsApp、Signal、Email 或 Home Assistant
- **[工具与工具集](../user-guide/features/tools.md)** — 探索可用功能
- **[AI 提供商](../integrations/providers.md)** — 完整的提供商列表和设置详情
- **[技能系统](../user-guide/features/skills.md)** — 可复用的工作流和知识
- **[技巧与最佳实践](../guides/tips.md)** — 高级用户技巧
