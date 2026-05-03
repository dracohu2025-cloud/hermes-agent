---
sidebar_position: 3
title: "常见问题与故障排查"
description: "关于 Hermes Agent 的常见问题及常见问题的解决方案"
---

# 常见问题与故障排查 {#faq-troubleshooting}

针对最常见的问题及异常，提供快速解答与修复方法。

---

## 常见问题 {#frequently-asked-questions}

### Hermes 支持哪些 LLM 提供商？ {#what-llm-providers-work-with-hermes}

Hermes Agent 支持所有兼容 OpenAI 的 API。支持的提供商包括：

- **[OpenRouter](https://openrouter.ai/)** —— 通过一个 API Key 访问数百种模型（推荐，更灵活）
- **Nous Portal** —— Nous Research 自家的推理端点
- **OpenAI** —— GPT-4o、o1、o3 等
- **Anthropic** —— Claude 模型（通过 OpenRouter 或兼容代理）
- **Google** —— Gemini 模型（通过 OpenRouter 或兼容代理）
- **z.ai / 智谱AI** —— GLM 模型
- **Kimi / Moonshot AI** —— Kimi 模型
- **MiniMax** —— 全球及中国端点
- **本地模型** —— 通过 [Ollama](https://ollama.com/)、[vLLM](https://docs.vllm.ai/)、[llama.cpp](https://github.com/ggerganov/llama.cpp)、[SGLang](https://github.com/sgl-project/sglang)，或任何兼容 OpenAI 的服务器

使用 `hermes model` 命令或编辑 `~/.hermes/.env` 文件来设置提供商。有关所有提供商的密钥，请参考[环境变量](./environment-variables.md)文档。

### 能在 Windows 上运行吗？ {#does-it-work-on-windows}

**不能原生运行。** Hermes Agent 需要类 Unix 环境。在 Windows 上，请安装 [WSL2](https://learn.microsoft.com/en-us/windows/wsl/install)，然后在其中运行 Hermes。标准安装命令在 WSL2 中完美运行：

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

### 能在 Android / Termux 上运行吗？ {#does-it-work-on-android-termux}

可以 —— Hermes 现在有经过测试的 Termux 安装路径，适用于 Android 手机。

快速安装：

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

如需完整的显式手动步骤、支持的额外依赖以及当前限制，请参阅 [Termux 指南](../getting-started/termux.md)。

重要提示：完整的 `.[all]` 额外依赖目前在 Android 上不可用，因为 `voice` 额外依赖依赖于 `faster-whisper` → `ctranslate2`，而 `ctranslate2` 没有发布 Android 的 wheel 包。请改用经过测试的 `.[termux]` 额外依赖。

### 我的数据会被发送到其他地方吗？ {#is-my-data-sent-anywhere}

API 调用**仅发送给你配置的 LLM 提供商**（例如 OpenRouter、本地的 Ollama 实例）。Hermes Agent 不会收集遥测信息、使用数据或分析数据。你的对话、记忆和技能都存储在本地 `~/.hermes/` 目录中。

### 可以离线使用 / 使用本地模型吗？ {#can-i-use-it-offline-with-local-models}

可以。运行 `hermes model`，选择 **Custom endpoint**，然后输入你服务器的 URL：

```bash
hermes model
# 选择：Custom endpoint (enter URL manually)
# API base URL: http://localhost:11434/v1
# API key: ollama
# Model name: qwen3.5:27b
# Context length: 32768   ← 设置此值以匹配你服务器的实际上下文窗口
```

或者直接在 `config.yaml` 中配置：

```yaml
model:
  default: qwen3.5:27b
  provider: custom
  base_url: http://localhost:11434/v1
```

Hermes 会将 endpoint、provider 和 base URL 持久化到 `config.yaml` 中，因此重启后仍会保留。如果你的本地服务器只加载了一个模型，`/model custom` 会自动检测到它。你也可以在 `config.yaml` 中设置 `provider: custom` —— 它是一个一等公民级别的 provider，不是任何其他 provider 的别名。
这适用于 Ollama、vLLM、llama.cpp server、SGLang、LocalAI 等。详情请参阅[配置指南](../user-guide/configuration.md)。

:::tip Ollama 用户
<a id="ollama-users"></a>
如果您在 Ollama 中设置了自定义的 `num_ctx`（如 `ollama run --num_ctx 16384`），请确保在 Hermes 中设置匹配的上下文长度 —— Ollama 的 `/api/show` 报告的是模型的*最大*上下文，而不是您配置的有效 `num_ctx`。
:::

:::tip 本地模型的超时问题
Hermes 会自动检测本地端点并放宽流式超时（读取超时从 120 秒提高到 1800 秒，并禁用过期流检测）。如果您仍然遇到超大上下文的超时问题，请在 `.env` 中设置 `HERMES_STREAM_READ_TIMEOUT=1800`。详情请参阅[本地 LLM 指南](../guides/local-llm-on-mac.md#timeouts)。
:::

<a id="how-much-does-it-cost"></a>
### 使用 Hermes Agent 需要多少费用？ {#ollama-users}

Hermes Agent 本身是**免费且开源**的（MIT 许可证）。您只需为所选提供商的 LLM API 使用付费。本地模型运行完全免费。
<a id="timeouts-with-local-models"></a>

### 多人可以共用一个实例吗？ {#can-multiple-people-use-one-instance}

可以。[消息网关](../user-guide/messaging/index.md) 允许多个用户通过 Telegram、Discord、Slack、WhatsApp 或 Home Assistant 与同一个 Hermes Agent 实例交互。访问通过白名单（特定用户 ID）和 DM 配对（第一个发消息的用户声明访问权限）进行控制。

### 记忆（Memory）和技能（Skills）有什么区别？ {#what-s-the-difference-between-memory-and-skills}

- **记忆**存储**事实**——Agent 了解的关于您、您的项目和偏好的信息。记忆会根据相关性自动检索。
- **技能**存储**流程**——完成某事的逐步说明。当 Agent 遇到类似任务时会回忆技能。

两者都会跨会话持久化。详情请参阅[记忆](../user-guide/features/memory.md)和[技能](../user-guide/features/skills.md)。

### 我可以在自己的 Python 项目中使用它吗？ {#can-i-use-it-in-my-own-python-project}

可以。导入 `AIAgent` 类并以编程方式使用 Hermes：

```python
from run_agent import AIAgent

agent = AIAgent(model="anthropic/claude-opus-4.7")
response = agent.chat("Explain quantum computing briefly")
```

完整 API 用法请参阅[Python 库指南](../user-guide/features/code-execution.md)。

---

## 故障排除 {#troubleshooting}

### 安装问题 {#installation-issues}

#### 安装后提示 `hermes: command not found` {#hermes-command-not-found-after-installation}

**原因：** 您的 shell 尚未重新加载更新后的 PATH。

**解决方案：**
```bash
# 重新加载 shell 配置文件
source ~/.bashrc    # bash
source ~/.zshrc     # zsh

# 或启动新的终端会话
```

如果仍然无效，请验证安装位置：
```bash
which hermes
ls ~/.local/bin/hermes
```

:::tip
安装程序会将 `~/.local/bin` 添加到您的 PATH 中。如果您使用的是非标准 shell 配置，请手动添加 `export PATH="$HOME/.local/bin:$PATH"`。
:::

#### Python 版本过低 {#python-version-too-old}

**原因：** Hermes 需要 Python 3.11 或更新版本。

**解决方案：**
```bash
python3 --version   # 检查当前版本

# 安装更新版本的 Python
sudo apt install python3.12   # Ubuntu/Debian
brew install python@3.12      # macOS
```

安装程序会自动处理此问题 —— 如果您在手动安装过程中看到此错误，请先升级 Python。
#### 终端命令提示 `node: command not found`（或 `nvm`、`pyenv`、`asdf` 等） {#terminal-commands-say-node-command-not-found-or-nvm-pyenv-asdf}

**原因：** Hermes 在启动时通过运行 `bash -l` 构建每个会话的环境快照。Bash 登录 shell 会读取 `/etc/profile`、`~/.bash_profile` 和 `~/.profile`，但**不会加载 `~/.bashrc`**——因此那些安装在这些文件中的工具（`nvm`、`asdf`、`pyenv`、`cargo`、自定义 `PATH` 导出）对快照不可见。这种情况最常见于 Hermes 在 systemd 下运行，或在一个没有预加载交互式 shell 配置的最小化 shell 中。

**解决方案：** Hermes 默认会自动加载 `~/.bashrc`。如果这还不够——例如，你是 zsh 用户，PATH 在 `~/.zshrc` 中，或者你从独立文件初始化 `nvm`——可以在 `~/.hermes/config.yaml` 中列出要加载的额外文件：

```yaml
terminal:
  shell_init_files:
    - ~/.zshrc                     # zsh 用户：将 zsh 管理的 PATH 拉入 bash 快照
    - ~/.nvm/nvm.sh                # 直接初始化 nvm（无论 shell 类型均可工作）
    - /etc/profile.d/cargo.sh      # 系统级 rc 文件
  # 设置此列表后，默认的 ~/.bashrc 自动加载将不会添加——
  # 如果两者都需要，请显式包含：
  #   - ~/.bashrc
  #   - ~/.zshrc
```

缺失的文件会被静默跳过。加载过程在 bash 中执行，因此依赖 zsh 特有语法的文件可能会报错——如果担心这个问题，可以只加载设置 PATH 的部分（例如直接加载 nvm 的 `nvm.sh`），而不是整个 rc 文件。

要禁用自动加载行为（仅使用严格的登录 shell 语义）：

```yaml
terminal:
  auto_source_bashrc: false
```

#### `uv: command not found` {#uv-command-not-found}

**原因：** `uv` 包管理器未安装或不在 PATH 中。

**解决方案：**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc
```

#### 安装时出现权限拒绝错误 {#permission-denied-errors-during-install}

**原因：** 对安装目录的写入权限不足。

**解决方案：**
```bash
# 不要对安装程序使用 sudo——它会安装到 ~/.local/bin
# 如果你之前用 sudo 安装过，请清理：
sudo rm /usr/local/bin/hermes
# 然后重新运行标准安装程序
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

---

### 提供商与模型问题 {#provider-model-issues}

#### `/model` 只显示一个提供商 / 无法切换提供商 {#model-only-shows-one-provider-can-t-switch-providers}

**原因：** `/model`（在聊天会话内）只能在你**已经配置过**的提供商之间切换。如果你只设置了 OpenRouter，那么 `/model` 只会显示它。

**解决方案：** 退出当前会话，在终端中使用 `hermes model` 添加新的提供商：

```bash
# 先退出 Hermes 聊天会话（Ctrl+C 或 /quit）

# 运行完整的提供商设置向导
hermes model

# 这允许你：添加提供商、运行 OAuth、输入 API 密钥、配置端点
```

通过 `hermes model` 添加新提供商后，启动一个新的聊天会话——`/model` 现在会显示所有已配置的提供商。

<a id="quick-reference"></a>
:::tip 快速参考
| 想要... | 使用 |
|-----------|-----|
| 添加新提供商 | `hermes model`（在终端中） |
| 输入/更改 API 密钥 | `hermes model`（在终端中） |
| 在会话中切换模型 | `/model <名称>`（在会话内） |
| 切换到其他已配置的提供商 | `/model provider:model`（在会话内） |
:::
#### API 密钥不工作 {#api-key-not-working}

**原因：** 密钥缺失、已过期、设置错误，或使用了错误的提供商。

**解决方案：**
```bash
# 检查你的配置
hermes config show

# 重新配置你的提供商
hermes model

# 或者直接设置
hermes config set OPENROUTER_API_KEY sk-or-v1-xxxxxxxxxxxx
```

:::warning
请确保密钥与提供商匹配。OpenAI 的密钥不能用于 OpenRouter，反之亦然。检查 `~/.hermes/.env` 中是否有冲突的条目。
:::

#### 模型不可用 / 模型未找到 {#model-not-available-model-not-found}

**原因：** 模型标识符不正确，或者你的提供商上不可用。

**解决方案：**
```bash
# 列出你的提供商可用的模型
hermes model

# 设置一个有效的模型
hermes config set HERMES_MODEL anthropic/claude-opus-4.7

# 或者按会话指定
hermes chat --model openrouter/meta-llama/llama-3.1-70b-instruct
```

#### 速率限制（429 错误） {#rate-limiting-429-errors}

**原因：** 你超出了提供商的速率限制。

**解决方案：** 稍等片刻后重试。对于持续使用，请考虑：
- 升级你的提供商套餐
- 切换到不同的模型或提供商
- 使用 `hermes chat --provider &lt;alternative&gt;` 路由到不同的后端

#### 上下文长度超出 {#context-length-exceeded}

**原因：** 对话对于模型的上下文窗口来说变得过长，或者 Hermes 检测到了错误的上下文长度。

**解决方案：**
```bash
# 压缩当前会话
/compress

# 或者开始一个新会话
hermes chat

# 使用具有更大上下文窗口的模型
hermes chat --model openrouter/google/gemini-3-flash-preview
```

如果这发生在第一次长对话时，Hermes 可能对你的模型检测到了错误的上下文长度。检查它检测到的内容：

查看 CLI 启动行——它会显示检测到的上下文长度（例如 `📊 Context limit: 128000 tokens`）。你也可以在会话期间使用 `/usage` 检查。

要修复上下文检测，请显式设置它：

```yaml
# 在 ~/.hermes/config.yaml 中
model:
  default: your-model-name
  context_length: 131072  # 你模型的实际上下文窗口
```

或者对于自定义端点，按模型添加：

```yaml
custom_providers:
  - name: "My Server"
    base_url: "http://localhost:11434/v1"
    models:
      qwen3.5:27b:
        context_length: 32768
```

请参阅 [上下文长度检测](../integrations/providers.md#context-length-detection) 了解自动检测的工作原理以及所有覆盖选项。

---

### 终端问题 {#terminal-issues}

#### 命令被阻止为危险命令 {#command-blocked-as-dangerous}

**原因：** Hermes 检测到可能具有破坏性的命令（例如 `rm -rf`、`DROP TABLE`）。这是一项安全功能。

**解决方案：** 当提示时，请审查命令并输入 `y` 以批准。你也可以：
- 要求 Agent 使用更安全的替代方案
- 在 [安全文档](../user-guide/security.md) 中查看危险模式的完整列表

:::tip
这是预期行为——Hermes 永远不会静默运行破坏性命令。批准提示会准确显示将要执行的内容。
:::

#### 通过消息网关使用 `sudo` 不工作 {#sudo-not-working-via-messaging-gateway}

**原因：** 消息网关在没有交互式终端的情况下运行，因此 `sudo` 无法提示输入密码。
**解决方案：**
- 在消息中避免使用 `sudo` — 让 Agent 寻找替代方案
- 如果必须使用 `sudo`，请在 `/etc/sudoers` 中为特定命令配置免密码 sudo
- 或者切换到终端界面执行管理任务：`hermes chat`

#### Docker 后端无法连接 {#docker-backend-not-connecting}

**原因：** Docker 守护进程未运行，或用户缺少权限。

**解决方案：**
```bash
# 检查 Docker 是否在运行
docker info

# 将当前用户添加到 docker 用户组
sudo usermod -aG docker $USER
newgrp docker

# 验证
docker run hello-world
```

---

### 消息问题 {#messaging-issues}

#### 机器人不回复消息 {#bot-not-responding-to-messages}

**原因：** 机器人未运行、未授权，或者您的用户不在允许列表中。

**解决方案：**
```bash
# 检查网关是否在运行
hermes gateway status

# 启动网关
hermes gateway start

# 查看日志中的错误信息
cat ~/.hermes/logs/gateway.log | tail -50
```

#### 消息无法送达 {#messages-not-delivering}

**原因：** 网络问题、机器人令牌过期，或平台 Webhook 配置错误。

**解决方案：**
- 使用 `hermes gateway setup` 验证机器人令牌是否有效
- 检查网关日志：`cat ~/.hermes/logs/gateway.log | tail -50`
- 对于基于 Webhook 的平台（Slack、WhatsApp），请确保您的服务器可公开访问

#### 允许列表混淆 — 谁可以和机器人对话？ {#allowlist-confusion-who-can-talk-to-the-bot}

**原因：** 授权模式决定了谁能获得访问权限。

**解决方案：**

| 模式 | 工作原理 |
|------|---------|
| **允许列表** | 只有配置中列出的用户 ID 可以交互 |
| **私信配对** | 第一个在私信中发送消息的用户获得独占访问权 |
| **开放** | 任何人都可以交互（不推荐用于生产环境） |

在 `~/.hermes/config.yaml` 中，于网关设置下进行配置。请参阅[消息文档](../user-guide/messaging/index.md)。

#### 网关无法启动 {#gateway-won-t-start}

**原因：** 缺少依赖、端口冲突，或令牌配置错误。

**解决方案：**
```bash
# 安装消息依赖
pip install "hermes-agent[telegram]"   # 或 [discord]、[slack]、[whatsapp]

# 检查端口冲突
lsof -i :8080

# 验证配置
hermes config show
```

#### WSL：网关持续断开连接，或 `hermes gateway start` 失败 {#wsl-gateway-keeps-disconnecting-or-hermes-gateway-start-fails}

**原因：** WSL 的 systemd 支持不可靠。许多 WSL2 安装未启用 systemd，即使启用了，服务也可能无法在 WSL 重启或 Windows 空闲关机后继续运行。

**解决方案：** 使用前台模式代替 systemd 服务：

```bash
# 选项 1：直接前台运行（最简单）
hermes gateway run

# 选项 2：通过 tmux 持久化运行（关闭终端后仍可运行）
tmux new -s hermes 'hermes gateway run'
# 稍后重新连接：tmux attach -t hermes

# 选项 3：通过 nohup 后台运行
nohup hermes gateway run > ~/.hermes/logs/gateway.log 2>&1 &
```

如果您仍想尝试 systemd，请确保已启用它：

1. 打开 `/etc/wsl.conf`（如果不存在则创建）
2. 添加：
   ```ini
   [boot]
   systemd=true
   ```
3. 在 PowerShell 中执行：`wsl --shutdown`
4. 重新打开 WSL 终端
5. 验证：`systemctl is-system-running` 应显示 "running" 或 "degraded"
:::tip Windows 开机自启动
如需可靠的自动启动，请使用 Windows 任务计划程序在登录时启动 WSL 和网关：
1. 创建一个任务，运行 `wsl -d Ubuntu -- bash -lc 'hermes gateway run'`
2. 将其设置为在用户登录时触发
:::

#### macOS：网关找不到 Node.js / ffmpeg / 其他工具 {#macos-node-js-ffmpeg-other-tools-not-found-by-gateway}
<a id="auto-start-on-windows-boot"></a>

**原因：** launchd 服务继承了一个极简的 PATH（`/usr/bin:/bin:/usr/sbin:/sbin`），其中不包含 Homebrew、nvm、cargo 或其他用户安装的工具目录。这通常会导致 WhatsApp 桥接失败（`node not found`）或语音转录失败（`ffmpeg not found`）。

**解决方案：** 当你运行 `hermes gateway install` 时，网关会捕获你的 shell PATH。如果你在设置网关后安装了工具，请重新运行安装以捕获更新后的 PATH：

```bash
hermes gateway install    # 重新快照当前 PATH
hermes gateway start      # 检测更新后的 plist 并重新加载
```

你可以验证 plist 中是否包含正确的 PATH：
```bash
/usr/libexec/PlistBuddy -c "Print :EnvironmentVariables:PATH" \
  ~/Library/LaunchAgents/ai.hermes.gateway.plist
```

---

### 性能问题 {#performance-issues}

#### 响应慢 {#slow-responses}

**原因：** 模型过大、API 服务器距离远、或系统提示词过重且包含大量工具。

**解决方案：**
- 尝试更快/更小的模型：`hermes chat --model openrouter/meta-llama/llama-3.1-8b-instruct`
- 减少激活的工具集：`hermes chat -t "terminal"`
- 检查到提供商的网络延迟
- 对于本地模型，确保有足够的 GPU VRAM

#### Token 用量高 {#high-token-usage}

**原因：** 对话过长、系统提示词冗长、或多次工具调用累积上下文。

**解决方案：**
```bash
# 压缩对话以减少 token
/compress

# 检查会话 token 用量
/usage
```

:::tip
在长时间会话中定期使用 `/compress`。它会总结对话历史，显著减少 token 用量，同时保留上下文。
:::

#### 会话过长 {#session-getting-too-long}

**原因：** 长时间对话会累积大量消息和工具输出，接近上下文限制。

**解决方案：**
```bash
# 压缩当前会话（保留关键上下文）
/compress

# 启动一个新会话，并引用旧会话
hermes chat

# 之后如需恢复特定会话
hermes chat --continue
```

---

### MCP 问题 {#mcp-issues}

#### MCP 服务器无法连接 {#mcp-server-not-connecting}

**原因：** 服务器二进制文件未找到、命令路径错误、或缺少运行时。

**解决方案：**
```bash
# 确保 MCP 依赖已安装（标准安装中已包含）
cd ~/.hermes/hermes-agent && uv pip install -e ".[mcp]"

# 对于基于 npm 的服务器，确保 Node.js 可用
node --version
npx --version

# 手动测试服务器
npx -y @modelcontextprotocol/server-filesystem /tmp
```

验证你的 `~/.hermes/config.yaml` MCP 配置：
```yaml
mcp_servers:
  filesystem:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/docs"]
```

#### MCP 服务器的工具未显示 {#tools-not-showing-up-from-mcp-server}

**原因：** 服务器已启动但工具发现失败、工具被配置过滤掉、或服务器不支持你期望的 MCP 能力。
**解决方案：**
- 检查网关/Agent 日志中的 MCP 连接错误
- 确保服务器响应 `tools/list` RPC 方法
- 检查该服务器下的 `tools.include`、`tools.exclude`、`tools.resources`、`tools.prompts` 或 `enabled` 设置
- 请记住，资源/提示工具仅在会话实际支持这些能力时才会注册
- 更改配置后使用 `/reload-mcp`

```bash
# 验证 MCP 服务器已配置
hermes config show | grep -A 12 mcp_servers

# 配置更改后重启 Hermes 或重新加载 MCP
hermes chat
```

另请参阅：
- [MCP（模型上下文协议）](/user-guide/features/mcp)
- [将 MCP 与 Hermes 结合使用](/guides/use-mcp-with-hermes)
- [MCP 配置参考](/reference/mcp-config-reference)

#### MCP 超时错误 {#mcp-timeout-errors}

**原因：** MCP 服务器响应时间过长，或在执行过程中崩溃。

**解决方案：**
- 如果支持，请在 MCP 服务器配置中增加超时时间
- 检查 MCP 服务器进程是否仍在运行
- 对于远程 HTTP MCP 服务器，请检查网络连接

:::warning
如果 MCP 服务器在请求中途崩溃，Hermes 会报告超时。请检查服务器自身的日志（而不仅仅是 Hermes 日志）以诊断根本原因。
:::

---

## 配置文件（Profiles） {#profiles}

### 配置文件与直接设置 HERMES_HOME 有何不同？ {#how-do-profiles-differ-from-just-setting-hermeshome}

配置文件是建立在 `HERMES_HOME` 之上的一个管理层次。你*可以*在每个命令前手动设置 `HERMES_HOME=/some/path`，但配置文件会为你处理所有底层工作：创建目录结构、生成 shell 别名（`hermes-work`）、在 `~/.hermes/active_profile` 中跟踪当前活动的配置文件，并自动在所有配置文件之间同步技能更新。它们还与 Tab 补全集成，这样你就不必记住路径了。

### 两个配置文件可以共享同一个机器人令牌吗？ {#can-two-profiles-share-the-same-bot-token}

不可以。每个消息平台（Telegram、Discord 等）都需要独占一个机器人令牌。如果两个配置文件同时尝试使用同一个令牌，第二个网关将无法连接。请为每个配置文件创建一个独立的机器人——对于 Telegram，请与 [@BotFather](https://t.me/BotFather) 对话以创建更多机器人。

### 配置文件之间会共享记忆或会话吗？ {#do-profiles-share-memory-or-sessions}

不会。每个配置文件拥有自己的记忆存储、会话数据库和技能目录。它们是完全隔离的。如果你想用现有的记忆和会话启动一个新配置文件，请使用 `hermes profile create newname --clone-all` 从当前配置文件复制所有内容。

### 当我运行 `hermes update` 时会发生什么？ {#what-happens-when-i-run-hermes-update}

`hermes update` 会拉取最新代码并**一次性**重新安装依赖（而不是每个配置文件都安装一次）。然后它会自动将更新后的技能同步到所有配置文件。你只需运行一次 `hermes update`——它就会覆盖机器上的每个配置文件。

### 我可以运行多少个配置文件？ {#how-many-profiles-can-i-run}

没有硬性限制。每个配置文件只是 `~/.hermes/profiles/` 下的一个目录。实际限制取决于你的磁盘空间以及系统能同时处理多少个网关（每个网关是一个轻量级 Python 进程）。运行几十个配置文件没有问题；每个空闲的配置文件不消耗任何资源。
---

## 工作流与模式 {#workflows-patterns}

### 为不同任务使用不同模型（多模型工作流） {#using-different-models-for-different-tasks-multi-model-workflows}

**场景：** 你日常使用 GPT-5.4，但 Gemini 或 Grok 写社交媒体内容更好。每次手动切换模型很麻烦。

**解决方案：委托配置。** Hermes 可以自动将子任务路由到不同模型。在 `~/.hermes/config.yaml` 中设置：

```yaml
delegation:
  model: "google/gemini-3-flash-preview"   # 子任务使用此模型
  provider: "openrouter"                    # 子任务的提供商
```

现在，当你告诉 Hermes "帮我写一条关于 X 的 Twitter 推文" 时，它会生成一个 `delegate_task` 子任务，该子任务在 Gemini 上运行，而不是你的主模型。你的主对话仍保留在 GPT-5.4 上。

你也可以在提示中明确说明：*"委托一个任务来写关于我们产品发布的社交媒体帖子。让子任务实际完成写作。"* Agent 会使用 `delegate_task`，它会自动应用委托配置。

如需一次性切换模型而不使用委托，可在 CLI 中使用 `/model`：

```bash
/model google/gemini-3-flash-preview    # 本次会话切换
# ... 写你的内容 ...
/model openai/gpt-5.4                   # 切换回来
```

更多关于委托的工作原理，请参阅 [子任务委托](../user-guide/features/delegation.md)。

### 在同一个 WhatsApp 号码上运行多个 Agent（按聊天绑定） {#running-multiple-agents-on-one-whatsapp-number-per-chat-binding}

**场景：** 在 OpenClaw 中，你有多个独立的 Agent 绑定到特定的 WhatsApp 聊天——一个用于家庭购物清单群组，另一个用于你的私人聊天。Hermes 能做到吗？

**当前限制：** Hermes 的每个配置文件都需要自己的 WhatsApp 号码/会话。你无法将多个配置文件绑定到同一个 WhatsApp 号码的不同聊天上——WhatsApp 桥接（Baileys）每个号码只使用一个经过身份验证的会话。

**变通方案：**

1. **使用单个配置文件并切换人格。** 创建不同的 `AGENTS.md` 上下文文件，或使用 `/personality` 命令按聊天更改行为。Agent 会看到它所在的聊天并相应调整。

2. **使用定时任务处理特定任务。** 对于购物清单追踪器，设置一个定时任务来监控特定聊天并管理清单——无需单独的 Agent。

3. **使用不同的号码。** 如果你需要真正独立的 Agent，请为每个配置文件配对一个独立的 WhatsApp 号码。Google Voice 等服务的虚拟号码可以做到这一点。

4. **改用 Telegram 或 Discord。** 这些平台更自然地支持按聊天绑定——每个 Telegram 群组或 Discord 频道都有自己的会话，你可以在同一个账户上运行多个机器人令牌（每个配置文件一个）。

更多详情请参阅 [配置文件](../user-guide/profiles.md) 和 [WhatsApp 设置](../user-guide/messaging/whatsapp.md)。

### 控制 Telegram 中显示的内容（隐藏日志和推理过程） {#controlling-what-shows-up-in-telegram-hiding-logs-and-reasoning}

**场景：** 你在 Telegram 中看到网关执行日志、Hermes 推理过程和工具调用细节，而不是只有最终输出。

**解决方案：** `config.yaml` 中的 `display.tool_progress` 设置控制工具活动的显示程度：
```yaml
display:
  tool_progress: "off"   # 可选值: off, new, all, verbose
```

- **`off`** — 仅显示最终回复。不显示工具调用、推理过程或日志。
- **`new`** — 显示新发生的工具调用（简短的一行摘要）。
- **`all`** — 显示所有工具活动，包括结果。
- **`verbose`** — 显示完整细节，包括工具参数和输出。

对于消息平台，通常使用 `off` 或 `new`。编辑 `config.yaml` 后，需要重启网关才能使更改生效。

你也可以通过 `/verbose` 命令（如果启用）在每个会话中切换此设置：

```yaml
display:
  tool_progress_command: true   # 在网关中启用 /verbose 命令
```

### 在 Telegram 上管理技能（斜杠命令限制） {#managing-skills-on-telegram-slash-command-limit}

**场景：** Telegram 有 100 个斜杠命令的限制，而你的技能数量正在超过这个限制。你想在 Telegram 上禁用不需要的技能，但 `hermes skills config` 的设置似乎没有生效。

**解决方案：** 使用 `hermes skills config` 按平台禁用技能。这会写入 `config.yaml`：

```yaml
skills:
  disabled: []                    # 全局禁用的技能
  platform_disabled:
    telegram: [skill-a, skill-b]  # 仅在 telegram 上禁用
```

更改后，**重启网关**（`hermes gateway restart` 或终止并重新启动）。Telegram 机器人命令菜单会在启动时重建。

:::tip
描述过长的技能在 Telegram 菜单中会被截断为 40 个字符，以保持在有效载荷大小限制内。如果技能没有显示，可能是总有效载荷大小的问题，而不是 100 个命令数量的限制——禁用不使用的技能对两者都有帮助。
:::

### 共享线程会话（多个用户，一个对话） {#shared-thread-sessions-multiple-users-one-conversation}

**场景：** 你有一个 Telegram 或 Discord 线程，其中有多人提及机器人。你希望该线程中的所有提及都属于一个共享对话，而不是每个用户单独的会话。

**当前行为：** Hermes 在大多数平台上使用用户 ID 作为会话键，因此每个人都有自己的对话上下文。这是出于隐私和上下文隔离的设计。

**变通方案：**

1. **使用 Slack。** Slack 的会话键是线程，而不是用户。同一线程中的多个用户共享一个对话——这正是你描述的行为。这是最自然的选择。

2. **使用单个用户的群聊。** 如果一个人是负责转达问题的指定“操作员”，那么会话将保持统一。其他人可以阅读。

3. **使用 Discord 频道。** Discord 的会话键是频道，因此同一频道中的所有用户共享上下文。使用专用频道进行共享对话。

### 将 Hermes 导出到另一台机器 {#exporting-hermes-to-another-machine}

**场景：** 你在一台机器上构建了技能、定时任务和记忆，并希望将所有内容迁移到一台新的专用 Linux 机器上。

**解决方案：**

1. 在新机器上安装 Hermes Agent：
   ```bash
   curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
   ```

2. 在**源机器**上，创建完整备份：
   ```bash
   hermes backup
   ```
   这会创建一个包含整个 `~/.hermes/` 目录（配置、API 密钥、记忆、技能、会话和配置文件）的 zip 文件，并保存到你的主目录中，文件名为 `~/hermes-backup-<时间戳>.zip`。
3. 将压缩包复制到新机器并导入：
   ```bash
   # 在源机器上
   scp ~/hermes-backup-<timestamp>.zip newmachine:~/

   # 在新机器上
   hermes import ~/hermes-backup-<timestamp>.zip
   ```

4. 在新机器上运行 `hermes setup`，验证 API 密钥和提供商配置是否正常。

### 将单个配置文件迁移到另一台机器 {#moving-a-single-profile-to-another-machine}

**场景：** 你想移动或共享某个特定的配置文件，而不是整个安装。

```bash
# 在源机器上
hermes profile export work ./work-backup.tar.gz

# 将文件复制到目标机器，然后：
hermes profile import ./work-backup.tar.gz work
```

导入的配置文件将包含导出时的所有配置、记忆、会话和技能。如果新机器的环境不同，你可能需要更新路径或重新认证提供商。

### `hermes backup` 与 `hermes profile export` 对比 {#hermes-backup-vs-hermes-profile-export}

| 特性 | `hermes backup` | `hermes profile export` |
| :--- | :--- | :--- |
| **使用场景** | **完整机器迁移** | **移植/共享特定配置文件** |
| **范围** | 全局（整个 `~/.hermes` 目录） | 本地（单个配置文件目录） |
| **包含内容** | 所有配置文件、全局配置、API 密钥、会话 | 单个配置文件：SOUL.md、记忆、会话、技能 |
| **凭据** | **包含**（`.env` 和 `auth.json`） | **排除**（为安全共享而剥离） |
| **格式** | `.zip` | `.tar.gz` |

**手动备用方案（rsync）：** 如果你更倾向于直接复制文件，请排除代码仓库：
```bash
rsync -av --exclude='hermes-agent' ~/.hermes/ newmachine:~/.hermes/
```

:::tip
即使 Hermes 正在运行，`hermes backup` 也能生成一致的快照。恢复后的归档文件会排除机器本地的运行时文件，如 `gateway.pid` 和 `cron.pid`。
:::

### 安装后重新加载 shell 时出现权限拒绝错误 {#permission-denied-when-reloading-shell-after-install}

**场景：** 运行 Hermes 安装程序后，`source ~/.zshrc` 报权限拒绝错误。

**原因：** 这通常是因为 `~/.zshrc`（或 `~/.bashrc`）的文件权限不正确，或者安装程序无法正常写入。这不是 Hermes 特有的问题，而是 shell 配置文件的权限问题。

**解决方案：**
```bash
# 检查权限
ls -la ~/.zshrc

# 如果需要，修复权限（应为 -rw-r--r-- 或 644）
chmod 644 ~/.zshrc

# 然后重新加载
source ~/.zshrc

# 或者直接打开一个新终端窗口——它会自动加载 PATH 变更
```

如果安装程序添加了 PATH 行但权限错误，你可以手动添加：
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
```

### 首次运行 Agent 时出现 400 错误 {#error-400-on-first-agent-run}

**场景：** 设置顺利完成，但首次聊天尝试失败，返回 HTTP 400。

**原因：** 通常是模型名称不匹配——配置的模型在你的提供商中不存在，或者 API 密钥没有访问权限。

**解决方案：**
```bash
# 检查配置的模型和提供商
hermes config show | head -20

# 重新运行模型选择
hermes model

# 或者使用已知可用的模型进行测试
hermes chat -q "hello" --model anthropic/claude-opus-4.7
```
如果使用 OpenRouter，请确保你的 API 密钥有足够的额度。来自 OpenRouter 的 400 错误通常意味着该模型需要付费计划，或者模型 ID 存在拼写错误。

---

## 仍然卡住了？ {#still-stuck}

如果你的问题未在此处涵盖：

1. **搜索已有问题：** [GitHub Issues](https://github.com/NousResearch/hermes-agent/issues)
2. **向社区提问：** [Nous Research Discord](https://discord.gg/nousresearch)
3. **提交错误报告：** 请附上你的操作系统、Python 版本（`python3 --version`）、Hermes 版本（`hermes --version`）以及完整的错误信息
