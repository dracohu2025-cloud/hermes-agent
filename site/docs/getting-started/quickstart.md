---
sidebar_position: 1
title: "快速入门"
description: "从安装到聊天，5分钟内完成与 Hermes Agent 的首次对话"
---

<a id="quickstart"></a>
# 快速入门

本指南将带你从零开始，完成一套可实际使用的 Hermes 环境搭建。安装、选择提供商、验证聊天功能，并清楚知道出问题时该怎么做。

<a id="prefer-to-watch"></a>
## 想先看视频？

**Onchain AI Garage** 制作了一期大师课，手把手讲解安装、配置和基本命令——如果你更愿意跟着视频操作，这是本页面的好搭档。更多内容请查看完整的 [Hermes Agent 教程与用例](https://www.youtube.com/channel/UCqB1bhMwGsW-yefBxYwFCCg) 播放列表。

<div style={{position: 'relative', paddingBottom: '56.25%', height: 0, overflow: 'hidden', maxWidth: '100%', marginBottom: '1.5rem'}}>
  <iframe
    style={{position: 'absolute', top: 0, left: 0, width: '100%', height: '100%'}}
    src="https://www.youtube-nocookie.com/embed/R3YOGfTBcQg"
    title="Hermes Agent 大师课：安装、配置、基本命令"
    frameBorder="0"
    allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
    allowFullScreen
  ></iframe>
</div>

<a id="who-this-is-for"></a>
## 适用人群

- 完全新手，想要最短路径完成环境搭建
- 正在切换提供商，不想因配置错误浪费时间
- 为团队、机器人或常驻工作流搭建 Hermes
- 受够了"装是装了，但啥也干不了"

<a id="the-fastest-path"></a>
## 最快路径

根据你的目标选择对应行：

| 目标 | 先做这个 | 再做这个 |
|---|---|---|
| 我只想让 Hermes 在我的机器上跑起来 | `hermes setup` | 运行一次真实聊天，验证它能正常回复 |
| 我已经知道用哪个提供商 | `hermes model` | 保存配置，然后开始聊天 |
| 我想要一个机器人或常驻工作流 | CLI 工作后执行 `hermes gateway setup` | 连接 Telegram、Discord、Slack 或其他平台 |
| 我想要本地或自托管模型 | `hermes model` → 自定义端点 | 验证端点、模型名称和上下文长度 |
| 我想要多提供商回退 | 先执行 `hermes model` | 基础聊天正常工作后，再添加路由和回退 |

**经验法则：** 如果 Hermes 连一次普通聊天都无法完成，就不要再添加更多功能。先确保一次干净的对话能正常工作，然后再叠加 gateway、cron、技能、语音或路由。

---

<a id="1-install-hermes-agent"></a>
## 1. 安装 Hermes Agent

**选项 A — pip（最简单）：**

```bash
pip install hermes-agent
hermes postinstall     # 可选：安装 Node.js、浏览器、ripgrep、ffmpeg 并运行 setup
```

PyPI 发布版跟踪的是打了标签的版本（主版本/次版本），而不是 `main` 分支上的每次提交。想要尝鲜最新版，请使用选项 B。

**选项 B — git 安装器（跟踪 main 分支）：**

```bash
# Linux / macOS / WSL2 / Android (Termux)
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

:::tip Android / Termux
如果你在手机上安装，请查看专门的 [Termux 指南](./termux.md)，了解经过测试的手动安装路径、支持的扩展功能以及当前 Android 特有的限制。
:::

<a id="windows-users"></a>
:::tip Windows 用户
先安装 [WSL2](https://learn.microsoft.com/en-us/windows/wsl/install)，然后在 WSL2 终端中运行上面的命令。
:::
完成后，重新加载你的 shell：

```bash
source ~/.bashrc   # 或 source ~/.zshrc
```

有关详细的安装选项、系统要求和故障排除，请参阅 [安装指南](./installation.md)。

<a id="2-choose-a-provider"></a>
## 2. 选择 Provider（提供商）

这是设置中最重要的步骤。运行 `hermes model` 可以交互式地完成选择：

```bash
hermes model
```

推荐默认选项：

| Provider（提供商） | 说明 | 设置方式 |
|----------|-----------|---------------|
| **Nous Portal** | 订阅制，零配置 | 通过 `hermes model` 进行 OAuth 登录 |
| **OpenAI Codex** | ChatGPT OAuth，使用 Codex 模型 | 通过 `hermes model` 进行设备码认证 |
| **Anthropic** | 直接使用 Claude 模型——Max 套餐 + 额外用量积分（OAuth），或按 token 付费的 API key | `hermes model` → OAuth 登录（需 Max 套餐 + 额外积分），或 Anthropic API key |
| **OpenRouter** | 跨多个模型的多提供商路由 | 输入你的 API key |
| **Z.AI** | GLM / 智谱托管模型 | 设置 `GLM_API_KEY` / `ZAI_API_KEY` |
| **Kimi / Moonshot** | Moonshot 托管的代码与对话模型 | 设置 `KIMI_API_KEY`（或 Kimi-Coding 专用的 `KIMI_CODING_API_KEY`） |
| **Kimi / Moonshot 中国区** | 中国区域 Moonshot 端点 | 设置 `KIMI_CN_API_KEY` |
| **Arcee AI** | Trinity 模型 | 设置 `ARCEEAI_API_KEY` |
| **GMI Cloud** | 多模型直接 API | 设置 `GMI_API_KEY` |
| **MiniMax（OAuth）** | 通过浏览器 OAuth 使用 MiniMax-M2.7——无需 API key | `hermes model` → MiniMax (OAuth) |
| **MiniMax** | 国际版 MiniMax 端点 | 设置 `MINIMAX_API_KEY` |
| **MiniMax 中国区** | 中国区域 MiniMax 端点 | 设置 `MINIMAX_CN_API_KEY` |
| **阿里云** | 通过 DashScope 使用 Qwen 模型 | 设置 `DASHSCOPE_API_KEY` |
| **Hugging Face** | 通过统一路由使用 20+ 开源模型（Qwen、DeepSeek、Kimi 等） | 设置 `HF_TOKEN` |
| **AWS Bedrock** | 通过原生 Converse API 使用 Claude、Nova、Llama、DeepSeek | IAM 角色或 `aws configure`（[指南](../guides/aws-bedrock.md)） |
| **Kilo Code** | KiloCode 托管的模型 | 设置 `KILOCODE_API_KEY` |
| **OpenCode Zen** | 按量付费访问精选模型 | 设置 `OPENCODE_ZEN_API_KEY` |
| **OpenCode Go** | 每月 $10 订阅开源模型 | 设置 `OPENCODE_GO_API_KEY` |
| **DeepSeek** | 直接访问 DeepSeek API | 设置 `DEEPSEEK_API_KEY` |
| **NVIDIA NIM** | 通过 build.nvidia.com 或本地 NIM 使用 Nemotron 模型 | 设置 `NVIDIA_API_KEY`（可选：`NVIDIA_BASE_URL`） |
| **GitHub Copilot** | GitHub Copilot 订阅（GPT-5.x、Claude、Gemini 等） | 通过 `hermes model` 进行 OAuth，或设置 `COPILOT_GITHUB_TOKEN` / `GH_TOKEN` |
| **GitHub Copilot ACP** | Copilot ACP Agent 后端（衍生本地 `copilot` CLI） | `hermes model`（需安装 `copilot` CLI 并执行 `copilot login`） |
| **Vercel AI Gateway** | Vercel AI Gateway 路由 | 设置 `AI_GATEWAY_API_KEY` |
| **自定义端点** | VLLM、SGLang、Ollama 或任何兼容 OpenAI 的 API | 设置 base URL 和 API key |

对于大多数首次使用用户：选择一个 Provider（提供商），除非你知道为什么要修改，否则接受默认值。完整的 Provider（提供商）目录（包含环境变量和设置步骤）请参见 [Providers（提供商）](../integrations/providers.md) 页面。
:::caution 最低上下文：64K tokens
Hermes Agent 需要一个至少拥有 **64,000 tokens** 上下文的模型。上下文窗口较小的模型无法为多步工具调用工作流维持足够的工作记忆，启动时会被拒绝。大多数托管模型（Claude、GPT、Gemini、Qwen、DeepSeek）都很容易满足这一要求。如果你运行的是本地模型，请将其上下文大小设置为至少 64K（例如，对于 llama.cpp 使用 `--ctx-size 65536`，对于 Ollama 使用 `-c 65536`）。
:::

:::tip
你可以随时使用 `hermes model` 切换供应商——无锁定。有关所有受支持供应商的完整列表和设置详情，请参阅 [AI Providers](../integrations/providers.md)。
<a id="minimum-context-64k-tokens"></a>
:::

<a id="how-settings-are-stored"></a>
### 设置的存储方式

Hermes 将机密信息与普通配置分开：

- **机密信息和令牌** → `~/.hermes/.env`
- **非机密设置** → `~/.hermes/config.yaml`

通过 CLI 正确设置值是最简单的方法：

```bash
hermes config set model anthropic/claude-opus-4.6
hermes config set terminal.backend docker
hermes config set OPENROUTER_API_KEY sk-or-...
```

正确的值会自动写入正确的文件。

<a id="3-run-your-first-chat"></a>
## 3. 运行你的第一次聊天

```bash
hermes            # classic CLI
hermes --tui      # modern TUI (recommended)
```

你会看到一个欢迎横幅，其中包含你的模型、可用工具和技能。使用一个具体且易于验证的提示：

:::tip 选择你的界面
Hermes 提供两种终端界面：经典的 `prompt_toolkit` CLI 和更新的 [TUI](../user-guide/tui.md)，后者支持模态覆盖、鼠标选择和非阻塞输入。两者共享相同的会话、斜杠命令和配置——分别用 `hermes` 和 `hermes --tui` 试试。
:::

<a id="pick-your-interface"></a>
```
用5个要点总结这个仓库，并告诉我主要入口点是什么。
```

```
检查我当前的目录，告诉我哪个看起来是主项目文件。
```

```
帮我为这个代码库设置一个干净的GitHub PR工作流程。
```

**成功的迹象：**

- 横幅显示了你选择的模型/供应商
- Hermes 无错误回复
- 如果需要，它可以使用工具（终端、文件读取、网络搜索）
- 对话正常进行多轮

如果这些都正常，你就度过了最困难的部分。

<a id="4-verify-sessions-work"></a>
## 4. 验证会话功能

在继续之前，确保恢复功能正常：

```bash
hermes --continue    # Resume the most recent session
hermes -c            # Short form
```

这应该能把你带回到刚刚的会话。如果没有，请检查你是否在同一个配置文件中，以及会话是否确实保存了。这在稍后你同时处理多个设置或机器时很重要。

<a id="5-try-key-features"></a>
## 5. 尝试关键功能

<a id="use-the-terminal"></a>
### 使用终端

```
❯ 我的磁盘使用情况如何？显示最大的5个目录。
```

Agent 会代表你运行终端命令并显示结果。

<a id="slash-commands"></a>
### 斜杠命令

输入 `/` 查看所有命令的自动完成下拉列表：

| 命令 | 功能 |
|---------|-------------|
| `/help` | 显示所有可用命令 |
| `/tools` | 列出可用工具 |
| `/model` | 交互式切换模型 |
| `/personality pirate` | 尝试一个有趣的个性 |
| `/save` | 保存对话 |
<a id="multi-line-input"></a>
### 多行输入

按 `Alt+Enter`、`Ctrl+J` 或 `Shift+Enter` 可添加新行。`Shift+Enter` 需要终端将其作为独立序列发送（默认 Kitty / foot / WezTerm / Ghostty；启用 Kitty 键盘协议后的 iTerm2 / Alacritty / VS Code 终端）。`Alt+Enter` 和 `Ctrl+J` 在所有终端中均有效。

<a id="interrupt-the-agent"></a>
### 中断 Agent

如果 Agent 响应过慢，键入新消息并回车即可——它会中断当前任务并切换到你的新指令。`Ctrl+C` 同样有效。

<a id="6-add-the-next-layer"></a>
## 6. 添加下一层

在基础聊天功能正常工作后再进行。按需选择：

<a id="bot-or-shared-assistant"></a>
### 机器人或共享助手

```bash
hermes gateway setup    # Interactive platform configuration
```

可连接 [Telegram](/user-guide/messaging/telegram)、[Discord](/user-guide/messaging/discord)、[Slack](/user-guide/messaging/slack)、[WhatsApp](/user-guide/messaging/whatsapp)、[Signal](/user-guide/messaging/signal)、[Email](/user-guide/messaging/email)、[Home Assistant](/user-guide/messaging/homeassistant) 或 [Microsoft Teams](/user-guide/messaging/teams)。

<a id="automation-and-tools"></a>
### 自动化与工具

- `hermes tools` — 按平台调整工具权限
- `hermes skills` — 浏览并安装可复用的工作流
- Cron — 仅在机器人或 CLI 配置稳定后

<a id="sandboxed-terminal"></a>
### 沙箱终端

出于安全考虑，将 Agent 运行在 Docker 容器或远程服务器中：

```bash
hermes config set terminal.backend docker    # Docker isolation
hermes config set terminal.backend ssh       # Remote server
```

<a id="voice-mode"></a>
### 语音模式

```bash
# From the Hermes install directory (the curl installer placed it at
# ~/.hermes/hermes-agent on Linux/macOS or %LOCALAPPDATA%\hermes\hermes-agent on Windows):
cd ~/.hermes/hermes-agent
uv pip install -e ".[voice]"
# Includes faster-whisper for free local speech-to-text
```

然后在 CLI 中：`/voice on`。按 `Ctrl+B` 录制。详见 [Voice Mode](../user-guide/features/voice-mode.md)。

<a id="skills"></a>
### 技能

```bash
hermes skills search kubernetes
hermes skills install openai/skills/k8s
```

或在聊天会话中使用 `/skills`。

<a id="mcp-servers"></a>
### MCP 服务器

```yaml
# Add to ~/.hermes/config.yaml
mcp_servers:
  github:
    command: npx
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "ghp_xxx"
```

<a id="editor-integration-acp"></a>
### 编辑器集成（ACP）

ACP 支持随标准 `[all]` 附加组件一同提供，因此 curl 安装程序已包含它。只需运行：

```bash
hermes acp
```

（如果安装时未使用 `[all]`，请先运行 `cd ~/.hermes/hermes-agent && uv pip install -e ".[acp]"`。）

详见 [ACP Editor Integration](../user-guide/features/acp.md)。

---

<a id="common-failure-modes"></a>
## 常见故障模式

这些是最浪费时间的问题：

| 症状 | 可能原因 | 解决方法 |
|---|---|---|
| Hermes 打开但返回空响应或混乱回复 | 提供方认证或模型选择错误 | 重新运行 `hermes model`，确认提供方、模型和认证 |
| 自定义端点“能用”但返回垃圾信息 | 基础 URL、模型名错误，或实际上不兼容 OpenAI | 先在单独客户端中验证端点 |
| 网关启动但无人能向其发送消息 | 机器人令牌、白名单或平台配置不完整 | 重新运行 `hermes gateway setup` 并检查 `hermes gateway status` |
| `hermes --continue` 找不到旧会话 | 切换了配置文件或会话未保存 | 检查 `hermes sessions list` 并确认你在正确的配置文件中 |
| 模型不可用或出现奇怪的回退行为 | 提供方路由或回退设置过于激进 | 在基础提供方稳定前保持路由关闭 |
| `hermes doctor` 标记配置问题 | 配置值缺失或过期 | 修复配置，在添加功能前重新测试简单聊天 |
<a id="recovery-toolkit"></a>
## 恢复工具包

当感觉不对劲时，按以下顺序操作：

1. `hermes doctor`
2. `hermes model`
3. `hermes setup`
4. `hermes sessions list`
5. `hermes --continue`
6. `hermes gateway status`

这个序列可以快速把你从“不对劲的状态”恢复到一个已知的良好状态。

---

<a id="quick-reference"></a>
## 快速参考

| 命令 | 描述 |
|------|------|
| `hermes` | 开始聊天 |
| `hermes model` | 选择你的 LLM 提供商和模型 |
| `hermes tools` | 配置每个平台启用的工具 |
| `hermes setup` | 完整设置向导（一次性配置所有内容） |
| `hermes doctor` | 诊断问题 |
| `hermes update` | 更新到最新版本 |
| `hermes gateway` | 启动消息网关 |
| `hermes --continue` | 恢复上次会话 |

<a id="next-steps"></a>
## 下一步

- **[CLI 指南](../user-guide/cli.md)** — 掌握终端界面
- **[配置](../user-guide/configuration.md)** — 自定义设置
- **[消息网关](../user-guide/messaging/index.md)** — 连接 Telegram、Discord、Slack、WhatsApp、Signal、电子邮件、Home Assistant、Teams 等
- **[工具与工具集](../user-guide/features/tools.md)** — 探索可用能力
- **[AI 提供商](../integrations/providers.md)** — 完整的提供商列表和设置细节
- **[技能系统](../user-guide/features/skills.md)** — 可复用工作流和知识
- **[技巧与最佳实践](../guides/tips.md)** — 高级用户技巧
