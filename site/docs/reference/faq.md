---
sidebar_position: 3
title: "常见问题与故障排除"
description: "Hermes Agent 的常见问题解答及故障解决方案"
---

# 常见问题与故障排除

针对最常见问题和故障的快速解答与修复方案。

---

## 常见问题解答

### Hermes 支持哪些 LLM 提供商？

Hermes Agent 支持任何兼容 OpenAI 的 API。支持的提供商包括：

- **[OpenRouter](https://openrouter.ai/)** — 通过一个 API Key 访问数百个模型（推荐，灵活性高）
- **Nous Portal** — Nous Research 自有的推理端点
- **OpenAI** — GPT-4o, o1, o3 等
- **Anthropic** — Claude 模型（通过 OpenRouter 或兼容的代理）
- **Google** — Gemini 模型（通过 OpenRouter 或兼容的代理）
- **z.ai / ZhipuAI** — GLM 模型
- **Kimi / Moonshot AI** — Kimi 模型
- **MiniMax** — 全球及中国区端点
- **本地模型** — 通过 [Ollama](https://ollama.com/), [vLLM](https://docs.vllm.ai/), [llama.cpp](https://github.com/ggerganov/llama.cpp), [SGLang](https://github.com/sgl-project/sglang) 或任何兼容 OpenAI 的服务器

使用 `hermes model` 或编辑 `~/.hermes/.env` 来设置你的提供商。请参阅[环境变量](./environment-variables.md)参考以获取所有提供商的 Key。

### 它能在 Windows 上运行吗？

**原生不支持。** Hermes Agent 需要类 Unix 环境。在 Windows 上，请安装 [WSL2](https://learn.microsoft.com/en-us/windows/wsl/install) 并在其中运行 Hermes。标准的安装命令在 WSL2 中可以完美运行：

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

### 它能在 Android / Termux 上运行吗？

可以 — Hermes 现在拥有针对 Android 手机的已测试 Termux 安装路径。

快速安装：

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

有关完整的显式手动步骤、支持的扩展功能及当前限制，请参阅 [Termux 指南](../getting-started/termux.md)。

重要提示：完整的 `.[all]` 扩展目前在 Android 上不可用，因为 `voice` 扩展依赖于 `faster-whisper` → `ctranslate2`，而 `ctranslate2` 没有发布 Android 版本的 wheel 包。请改用已测试的 `.[termux]` 扩展。

### 我的数据会被发送到别处吗？

API 调用**仅发送至你配置的 LLM 提供商**（例如 OpenRouter 或你本地的 Ollama 实例）。Hermes Agent 不会收集遥测数据、使用情况数据或分析信息。你的对话、记忆和技能都存储在本地的 `~/.hermes/` 目录中。

### 我可以离线使用它或使用本地模型吗？

可以。运行 `hermes model`，选择 **Custom endpoint**，然后输入你服务器的 URL：

```bash
hermes model
# 选择：Custom endpoint (手动输入 URL)
# API base URL: http://localhost:11434/v1
# API key: ollama
# Model name: qwen3.5:27b
# Context length: 32768   ← 设置为与你服务器实际上下文窗口匹配的值
```

或者直接在 `config.yaml` 中配置：

```yaml
model:
  default: qwen3.5:27b
  provider: custom
  base_url: http://localhost:11434/v1
```

Hermes 会将端点、提供商和 base URL 持久化到 `config.yaml` 中，以便重启后依然有效。如果你的本地服务器恰好加载了一个模型，`/model custom` 会自动检测到它。你也可以在 `config.yaml` 中设置 `provider: custom` —— 它是一个一等公民提供商，而不是其他任何东西的别名。

这适用于 Ollama、vLLM、llama.cpp 服务器、SGLang、LocalAI 等。详情请参阅[配置指南](../user-guide/configuration.md)。

:::tip Ollama 用户
如果你在 Ollama 中设置了自定义的 `num_ctx`（例如 `ollama run --num_ctx 16384`），请确保在 Hermes 中设置匹配的上下文长度 —— Ollama 的 `/api/show` 报告的是模型的*最大*上下文，而不是你配置的有效 `num_ctx`。
:::

:::tip 本地模型超时问题
Hermes 会自动检测本地端点并放宽流式传输超时限制（读取超时从 120 秒提高到 1800 秒，禁用陈旧流检测）。如果你在处理超大上下文时仍然遇到超时，请在 `.env` 中设置 `HERMES_STREAM_READ_TIMEOUT=1800`。详情请参阅 [本地 LLM 指南](../guides/local-llm-on-mac.md#timeouts)。
:::

### 它收费吗？

Hermes Agent 本身是**免费且开源的**（MIT 许可证）。你只需支付所选提供商的 LLM API 使用费用。本地模型运行完全免费。

### 多个人可以使用同一个实例吗？

可以。通过[消息网关](../user-guide/messaging/index.md)，多个用户可以通过 Telegram、Discord、Slack、WhatsApp 或 Home Assistant 与同一个 Hermes Agent 实例进行交互。访问权限通过允许列表（特定用户 ID）和私聊配对（第一个发送消息的用户获得访问权限）进行控制。

### 记忆（Memory）和技能（Skills）有什么区别？

- **记忆**存储的是**事实** —— 即 Agent 关于你、你的项目和偏好的了解。记忆会根据相关性自动检索。
- **技能**存储的是**程序** —— 即如何完成某项任务的分步说明。当 Agent 遇到类似任务时，会调用相应的技能。

两者在会话之间都会持久保存。详情请参阅 [记忆](../user-guide/features/memory.md) 和 [技能](../user-guide/features/skills.md)。

### 我可以在自己的 Python 项目中使用它吗？

可以。导入 `AIAgent` 类并以编程方式使用 Hermes：

```python
from run_agent import AIAgent

agent = AIAgent(model="openrouter/nous/hermes-3-llama-3.1-70b")
response = agent.chat("简要解释量子计算")
```

有关完整的 API 使用方法，请参阅 [Python 库指南](../user-guide/features/code-execution.md)。

---

## 故障排除

### 安装问题

#### 安装后提示 `hermes: command not found`

**原因：** 你的 Shell 没有重新加载更新后的 PATH。

**解决方案：**
```bash
# 重新加载你的 Shell 配置文件
source ~/.bashrc    # bash
source ~/.zshrc     # zsh

# 或者开启一个新的终端会话
```

如果仍然无效，请检查安装位置：
```bash
which hermes
ls ~/.local/bin/hermes
```

:::tip
安装程序会将 `~/.local/bin` 添加到你的 PATH 中。如果你使用非标准 Shell 配置，请手动添加 `export PATH="$HOME/.local/bin:$PATH"`。
:::

#### Python 版本过旧

**原因：** Hermes 需要 Python 3.11 或更高版本。

**解决方案：**
```bash
python3 --version   # 检查当前版本

# 安装更新的 Python
sudo apt install python3.12   # Ubuntu/Debian
brew install python@3.12      # macOS
```

安装程序会自动处理此问题 —— 如果你在手动安装过程中看到此错误，请先升级 Python。

#### `uv: command not found`

**原因：** `uv` 包管理器未安装或不在 PATH 中。

**解决方案：**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc
```

#### 安装期间出现权限被拒绝错误

**原因：** 写入安装目录的权限不足。

**解决方案：**
```bash
# 不要使用 sudo 运行安装程序 —— 它会安装到 ~/.local/bin
# 如果你之前使用 sudo 安装过，请清理：
sudo rm /usr/local/bin/hermes
# 然后重新运行标准安装程序
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

---

### 提供商与模型问题

#### API Key 无效

**原因：** Key 缺失、过期、设置错误或属于错误的提供商。

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
确保 Key 与提供商匹配。OpenAI 的 Key 不能用于 OpenRouter，反之亦然。检查 `~/.hermes/.env` 中是否有冲突的条目。
:::

#### 模型不可用 / 找不到模型

**原因：** 模型标识符不正确，或者在你的提供商处不可用。

**解决方案：**
```bash
# 列出你提供商可用的模型
hermes model

# 设置一个有效的模型
hermes config set HERMES_MODEL openrouter/nous/hermes-3-llama-3.1-70b

# 或者在单次会话中指定
hermes chat --model openrouter/meta-llama/llama-3.1-70b-instruct
```

#### 速率限制（429 错误）

**原因：** 你已超过提供商的速率限制。

**解决方案：** 稍等片刻后重试。对于持续的使用需求，请考虑：
- 升级你的提供商套餐
- 切换到不同的模型或提供商
- 使用 `hermes chat --provider <alternative>` 路由到不同的后端
#### Context length exceeded

**原因：** 对话长度超过了模型的上下文窗口，或者 Hermes 检测到的模型上下文长度不正确。

**解决方案：**
```bash
# 压缩当前会话
/compress

# 或者开启一个新会话
hermes chat

# 使用具有更大上下文窗口的模型
hermes chat --model openrouter/google/gemini-3-flash-preview
```

如果这是在第一次长对话中发生，可能是 Hermes 对你的模型上下文长度识别有误。请检查它检测到的数值：

查看 CLI 启动行 — 它会显示检测到的上下文长度（例如 `📊 Context limit: 128000 tokens`）。你也可以在会话期间通过 `/usage` 命令查看。

若要修复上下文检测，请手动设置：

```yaml
# 在 ~/.hermes/config.yaml 中
model:
  default: your-model-name
  context_length: 131072  # 你模型实际的上下文窗口大小
```

或者对于自定义端点，按模型进行添加：

```yaml
custom_providers:
  - name: "My Server"
    base_url: "http://localhost:11434/v1"
    models:
      qwen3.5:27b:
        context_length: 32768
```

请参阅 [Context Length Detection](../integrations/providers.md#context-length-detection) 了解自动检测的工作原理及所有覆盖选项。

---

### 终端问题

#### Command blocked as dangerous

**原因：** Hermes 检测到了潜在的破坏性命令（例如 `rm -rf`、`DROP TABLE`）。这是一项安全功能。

**解决方案：** 当出现提示时，请检查命令并输入 `y` 进行确认。你也可以：
- 要求 Agent 使用更安全的替代方案
- 在 [Security docs](../user-guide/security.md) 中查看危险命令模式的完整列表

:::tip
这是预期的工作方式 — Hermes 绝不会在不经提示的情况下运行破坏性命令。批准提示会明确显示即将执行的内容。
:::

#### `sudo` not working via messaging gateway

**原因：** 消息网关在运行时没有交互式终端，因此 `sudo` 无法提示输入密码。

**解决方案：**
- 在消息中避免使用 `sudo` — 要求 Agent 寻找替代方案
- 如果必须使用 `sudo`，请在 `/etc/sudoers` 中为特定命令配置免密 sudo
- 或者切换到终端界面进行管理任务：`hermes chat`

#### Docker backend not connecting

**原因：** Docker 守护进程未运行或用户权限不足。

**解决方案：**
```bash
# 检查 Docker 是否正在运行
docker info

# 将你的用户添加到 docker 组
sudo usermod -aG docker $USER
newgrp docker

# 验证
docker run hello-world
```

---

### 消息传递问题

#### Bot not responding to messages

**原因：** 机器人未运行、未授权，或者你的用户不在允许列表中。

**解决方案：**
```bash
# 检查网关是否正在运行
hermes gateway status

# 启动网关
hermes gateway start

# 查看错误日志
cat ~/.hermes/logs/gateway.log | tail -50
```

#### Messages not delivering

**原因：** 网络问题、机器人令牌过期或平台 Webhook 配置错误。

**解决方案：**
- 使用 `hermes gateway setup` 验证你的机器人令牌是否有效
- 检查网关日志：`cat ~/.hermes/logs/gateway.log | tail -50`
- 对于基于 Webhook 的平台（Slack、WhatsApp），确保你的服务器是公开可访问的

#### Allowlist confusion — who can talk to the bot?

**原因：** 授权模式决定了谁可以获得访问权限。

**解决方案：**

| 模式 | 工作原理 |
|------|-------------|
| **Allowlist** | 只有配置中列出的用户 ID 才能交互 |
| **DM pairing** | 私聊中第一个发送消息的用户获得独占访问权 |
| **Open** | 任何人都可以交互（不建议在生产环境使用） |

在 `~/.hermes/config.yaml` 的网关设置下进行配置。请参阅 [Messaging docs](../user-guide/messaging/index.md)。

#### Gateway won't start

**原因：** 缺少依赖项、端口冲突或令牌配置错误。

**解决方案：**
```bash
# 安装消息传递依赖项
pip install "hermes-agent[telegram]"   # 或 [discord], [slack], [whatsapp]

# 检查端口冲突
lsof -i :8080

# 验证配置
hermes config show
```

#### WSL: Gateway keeps disconnecting or `hermes gateway start` fails

**原因：** WSL 对 systemd 的支持不稳定。许多 WSL2 安装没有启用 systemd，即使启用了，服务也可能无法在 WSL 重启或 Windows 空闲关机后存活。

**解决方案：** 使用前台模式代替 systemd 服务：

```bash
# 选项 1：直接前台运行（最简单）
hermes gateway run

# 选项 2：通过 tmux 持久化（终端关闭后依然运行）
tmux new -s hermes 'hermes gateway run'
# 稍后重新连接：tmux attach -t hermes

# 选项 3：通过 nohup 后台运行
nohup hermes gateway run > ~/.hermes/logs/gateway.log 2>&1 &
```

如果你仍想尝试 systemd，请确保它已启用：

1. 打开 `/etc/wsl.conf`（如果不存在则创建）
2. 添加：
   ```ini
   [boot]
   systemd=true
   ```
3. 在 PowerShell 中执行：`wsl --shutdown`
4. 重新打开你的 WSL 终端
5. 验证：`systemctl is-system-running` 应该显示 "running" 或 "degraded"

:::tip Windows 开机自启
为了实现可靠的自动启动，请使用 Windows 任务计划程序在登录时启动 WSL + 网关：
1. 创建一个任务，运行 `wsl -d Ubuntu -- bash -lc 'hermes gateway run'`
2. 设置触发器为用户登录时
:::

#### macOS: Node.js / ffmpeg / other tools not found by gateway

**原因：** launchd 服务继承的是最小化的 PATH (`/usr/bin:/bin:/usr/sbin:/sbin`)，其中不包含 Homebrew、nvm、cargo 或其他用户安装的工具目录。这通常会导致 WhatsApp 桥接失败（`node not found`）或语音转录失败（`ffmpeg not found`）。

**解决方案：** 当你运行 `hermes gateway install` 时，网关会捕获你的 shell PATH。如果你在设置网关后安装了工具，请重新运行安装命令以捕获更新后的 PATH：

```bash
hermes gateway install    # 重新快照你当前的 PATH
hermes gateway start      # 检测更新后的 plist 并重新加载
```

你可以验证 plist 是否具有正确的 PATH：
```bash
/usr/libexec/PlistBuddy -c "Print :EnvironmentVariables:PATH" \
  ~/Library/LaunchAgents/ai.hermes.gateway.plist
```

---

### 性能问题

#### Slow responses

**原因：** 模型过大、API 服务器距离过远，或系统提示词过重且包含大量工具。

**解决方案：**
- 尝试更快/更小的模型：`hermes chat --model openrouter/meta-llama/llama-3.1-8b-instruct`
- 减少启用的工具集：`hermes chat -t "terminal"`
- 检查你到服务商的网络延迟
- 对于本地模型，确保你有足够的 GPU 显存

#### High token usage

**原因：** 对话过长、系统提示词冗长，或大量工具调用积累了上下文。

**解决方案：**
```bash
# 压缩对话以减少 token
/compress

# 检查会话 token 使用情况
/usage
```

:::tip
在长会话期间定期使用 `/compress`。它会总结对话历史并显著减少 token 使用量，同时保留上下文。
:::

#### Session getting too long

**原因：** 扩展对话积累了消息和工具输出，接近上下文限制。

**解决方案：**
```bash
# 压缩当前会话（保留关键上下文）
/compress

# 开启一个引用旧会话的新会话
hermes chat

# 如果需要，稍后恢复特定会话
hermes chat --continue
```

---

### MCP 问题

#### MCP server not connecting

**原因：** 找不到服务器二进制文件、命令路径错误或缺少运行时。

**解决方案：**
```bash
# 确保已安装 MCP 依赖项（标准安装中已包含）
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

#### Tools not showing up from MCP server

**原因：** 服务器已启动但工具发现失败、工具被配置过滤，或者服务器不支持你预期的 MCP 功能。
**解决方案：**
- 检查 gateway/agent 日志，查看是否有 MCP 连接错误
- 确保服务器响应 `tools/list` RPC 方法
- 检查该服务器下的 `tools.include`、`tools.exclude`、`tools.resources`、`tools.prompts` 或 `enabled` 设置
- 请记住，资源/提示词工具仅在会话实际支持这些功能时才会注册
- 修改配置后，请使用 `/reload-mcp`

```bash
# 验证 MCP 服务器是否已配置
hermes config show | grep -A 12 mcp_servers

# 修改配置后重启 Hermes 或重新加载 MCP
hermes chat
```

另请参阅：
- [MCP (Model Context Protocol)](/user-guide/features/mcp)
- [在 Hermes 中使用 MCP](/guides/use-mcp-with-hermes)
- [MCP 配置参考](/reference/mcp-config-reference)

#### MCP 超时错误

**原因：** MCP 服务器响应时间过长，或在执行过程中崩溃。

**解决方案：**
- 如果支持，请在 MCP 服务器配置中增加超时时间
- 检查 MCP 服务器进程是否仍在运行
- 对于远程 HTTP MCP 服务器，请检查网络连接

:::warning
如果 MCP 服务器在请求过程中崩溃，Hermes 将报告超时。请检查服务器自身的日志（不仅仅是 Hermes 日志）以诊断根本原因。
:::

---

## Profiles（配置文件） {#profiles}

### Profiles 与直接设置 HERMES_HOME 有什么区别？

Profiles 是 `HERMES_HOME` 之上的一个管理层。你*可以*在每次命令前手动设置 `HERMES_HOME=/some/path`，但 Profiles 会为你处理所有繁琐工作：创建目录结构、生成 shell 别名 (`hermes-work`)、在 `~/.hermes/active_profile` 中跟踪当前活跃的 Profile，并自动在所有 Profile 间同步技能更新。它们还与 Tab 补全功能集成，让你无需记忆路径。

### 两个 Profile 可以共享同一个机器人 Token 吗？

不可以。每个消息平台（Telegram、Discord 等）都需要对机器人 Token 的独占访问权。如果两个 Profile 尝试同时使用同一个 Token，第二个网关将无法连接。请为每个 Profile 创建单独的机器人——对于 Telegram，请联系 [@BotFather](https://t.me/BotFather) 创建额外的机器人。

### Profile 之间共享内存或会话吗？

不共享。每个 Profile 都有自己的内存存储、会话数据库和技能目录。它们是完全隔离的。如果你想用现有的内存和会话启动一个新的 Profile，请使用 `hermes profile create newname --clone-all` 从当前 Profile 复制所有内容。

### 运行 `hermes update` 时会发生什么？

`hermes update` 会拉取最新代码并重新安装依赖项，且**仅执行一次**（而不是每个 Profile 执行一次）。然后，它会自动将更新后的技能同步到所有 Profile。你只需要运行一次 `hermes update`，它就会覆盖机器上的所有 Profile。

### 可以将 Profile 移动到另一台机器吗？

可以。将 Profile 导出为便携式归档文件，然后在另一台机器上导入：

```bash
# 在源机器上
hermes profile export work ./work-backup.tar.gz

# 将文件复制到目标机器，然后执行：
hermes profile import ./work-backup.tar.gz work
```

导入的 Profile 将包含导出时的所有配置、内存、会话和技能。如果新机器的设置不同，你可能需要更新路径或重新进行提供商身份验证。

### 我可以运行多少个 Profile？

没有硬性限制。每个 Profile 只是 `~/.hermes/profiles/` 下的一个目录。实际限制取决于你的磁盘空间以及系统能处理多少个并发网关（每个网关都是一个轻量级的 Python 进程）。运行几十个 Profile 是没问题的；每个空闲的 Profile 不会占用资源。

---

## Workflows & Patterns（工作流与模式）

### 为不同任务使用不同模型（多模型工作流）

**场景：** 你将 GPT-5.4 作为日常主力模型，但 Gemini 或 Grok 在撰写社交媒体内容方面表现更好。每次手动切换模型很麻烦。

**解决方案：委托配置 (Delegation config)。** Hermes 可以自动将子 Agent 路由到不同的模型。在 `~/.hermes/config.yaml` 中进行设置：

```yaml
delegation:
  model: "google/gemini-3-flash-preview"   # 子 Agent 使用此模型
  provider: "openrouter"                    # 子 Agent 的提供商
```

现在，当你告诉 Hermes“帮我写一个关于 X 的 Twitter 帖子”并且它生成了一个 `delegate_task` 子 Agent 时，该子 Agent 将在 Gemini 上运行，而不是你的主模型。你的主要对话仍保留在 GPT-5.4 上。

你也可以在提示词中明确指出：*“委托一个任务来撰写关于我们产品发布会的社交媒体帖子。使用你的子 Agent 进行实际撰写。”* Agent 将使用 `delegate_task`，它会自动读取委托配置。

对于无需委托的一次性模型切换，请在 CLI 中使用 `/model`：

```bash
/model google/gemini-3-flash-preview    # 为当前会话切换
# ... 撰写你的内容 ...
/model openai/gpt-5.4                   # 切回
```

有关委托工作原理的更多信息，请参阅 [Subagent Delegation](../user-guide/features/delegation.md)。

### 在一个 WhatsApp 号码上运行多个 Agent（按聊天绑定）

**场景：** 在 OpenClaw 中，你有多个独立的 Agent 绑定到特定的 WhatsApp 聊天中——一个用于家庭购物清单群组，另一个用于私人聊天。Hermes 能做到吗？

**当前限制：** Hermes 的每个 Profile 都需要自己的 WhatsApp 号码/会话。你不能将多个 Profile 绑定到同一个 WhatsApp 号码下的不同聊天中——WhatsApp 桥接器 (Baileys) 每个号码仅使用一个已验证的会话。

**变通方法：**

1. **使用带有角色切换的单个 Profile。** 创建不同的 `AGENTS.md` 上下文文件，或使用 `/personality` 命令来根据聊天内容改变行为。Agent 可以识别它所在的聊天并进行调整。

2. **对特定任务使用 Cron 作业。** 对于购物清单跟踪器，设置一个 Cron 作业来监控特定聊天并管理列表——无需单独的 Agent。

3. **使用不同的号码。** 如果你需要真正独立的 Agent，请为每个 Profile 配对一个专属的 WhatsApp 号码。来自 Google Voice 等服务的虚拟号码可以实现这一点。

4. **改用 Telegram 或 Discord。** 这些平台对按聊天绑定的支持更自然——每个 Telegram 群组或 Discord 频道都有自己的会话，你可以在同一个账号上运行多个机器人 Token（每个 Profile 一个）。

有关更多详细信息，请参阅 [Profiles](../user-guide/profiles.md) 和 [WhatsApp setup](../user-guide/messaging/whatsapp.md)。

### 控制 Telegram 中的显示内容（隐藏日志和推理过程）

**场景：** 你在 Telegram 中看到了网关执行日志、Hermes 推理过程和工具调用详情，而不仅仅是最终输出。

**解决方案：** `config.yaml` 中的 `display.tool_progress` 设置控制了工具活动的显示程度：

```yaml
display:
  tool_progress: "off"   # 选项：off, new, all, verbose
```

- **`off`** — 仅显示最终响应。没有工具调用、推理过程或日志。
- **`new`** — 在新工具调用发生时显示（简短的一行）。
- **`all`** — 显示所有工具活动，包括结果。
- **`verbose`** — 完整详情，包括工具参数和输出。

对于消息平台，通常建议设置为 `off` 或 `new`。编辑 `config.yaml` 后，重启网关以使更改生效。

你也可以使用 `/verbose` 命令（如果已启用）在每个会话中切换此设置：

```yaml
display:
  tool_progress_command: true   # 在网关中启用 /verbose
```

### 管理 Telegram 上的技能（斜杠命令限制）

**场景：** Telegram 有 100 个斜杠命令的限制，而你的技能数量正在超过这个限制。你想禁用在 Telegram 上不需要的技能，但 `hermes skills config` 设置似乎没有生效。

**解决方案：** 使用 `hermes skills config` 按平台禁用技能。这会写入 `config.yaml`：

```yaml
skills:
  disabled: []                    # 全局禁用技能
  platform_disabled:
    telegram: [skill-a, skill-b]  # 仅在 telegram 上禁用
```

更改此设置后，**重启网关**（执行 `hermes gateway restart` 或关闭并重新启动）。Telegram 机器人命令菜单会在启动时重建。
:::tip
为了保持在有效载荷大小限制内，Telegram 菜单中描述过长的 Skill 会被截断为 40 个字符。如果 Skill 没有显示，这可能是总有效载荷大小的问题，而不是 100 个命令的限制——禁用不使用的 Skill 对两者都有帮助。
:::

### 共享线程会话（多用户，单次对话）

**场景：** 你有一个 Telegram 或 Discord 线程，其中有多个人提到了机器人。你希望该线程中的所有提及都属于同一个共享对话，而不是每个用户分开的会话。

**当前行为：** Hermes 在大多数平台上创建以用户 ID 为键的会话，因此每个人都有自己的对话上下文。这是出于隐私和上下文隔离的设计考虑。

**变通方法：**

1. **使用 Slack。** Slack 会话以线程为键，而不是以用户为键。同一线程中的多个用户共享一个对话——这正是你所描述的行为。这是最自然的适配方式。

2. **使用单用户群聊。** 如果有一个人被指定为“操作员”来转发问题，会话将保持统一。其他人可以阅读。

3. **使用 Discord 频道。** Discord 会话以频道为键，因此同一频道中的所有用户共享上下文。请使用专用频道进行共享对话。

### 将 Hermes 迁移到另一台机器

**场景：** 你在一台机器上构建了 Skill、cron 任务和记忆，并希望将所有内容移动到一台新的专用 Linux 机器上。

**解决方案：**

1. 在新机器上安装 Hermes Agent：
   ```bash
   curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
   ```

2. 复制整个 `~/.hermes/` 目录，**但要排除** `hermes-agent` 子目录（这是代码仓库——新安装的会有自己的仓库）：
   ```bash
   # 在源机器上
   rsync -av --exclude='hermes-agent' ~/.hermes/ newmachine:~/.hermes/
   ```

   或者使用配置导出/导入：
   ```bash
   # 在源机器上
   hermes profile export default ./hermes-backup.tar.gz

   # 在目标机器上
   hermes profile import ./hermes-backup.tar.gz default
   ```

3. 在新机器上，运行 `hermes setup` 以验证 API 密钥和提供商配置是否正常工作。重新验证任何消息平台（特别是使用二维码配对的 WhatsApp）。

`~/.hermes/` 目录包含所有内容：`config.yaml`、`.env`、`SOUL.md`、`memories/`、`skills/`、`state.db`（会话）、`cron/` 以及任何自定义插件。代码本身位于 `~/.hermes/hermes-agent/` 中，是全新安装的。

### 安装后重新加载 shell 时出现权限被拒绝

**场景：** 运行 Hermes 安装程序后，`source ~/.zshrc` 报错权限被拒绝。

**原因：** 这通常发生在 `~/.zshrc`（或 `~/.bashrc`）的文件权限不正确，或者安装程序无法干净地写入它时。这不是 Hermes 特有的问题，而是 shell 配置权限问题。

**解决方案：**
```bash
# 检查权限
ls -la ~/.zshrc

# 如果需要，进行修复（应为 -rw-r--r-- 或 644）
chmod 644 ~/.zshrc

# 然后重新加载
source ~/.zshrc

# 或者直接打开一个新的终端窗口——它会自动获取 PATH 更改
```

如果安装程序添加了 PATH 行但权限错误，你可以手动添加：
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
```

### 首次运行 Agent 时出现 400 错误

**场景：** 设置完成，但第一次聊天尝试失败，显示 HTTP 400。

**原因：** 通常是模型名称不匹配——配置的模型在你的提供商处不存在，或者 API 密钥没有访问权限。

**解决方案：**
```bash
# 检查配置了什么模型和提供商
hermes config show | head -20

# 重新运行模型选择
hermes model

# 或者使用已知良好的模型进行测试
hermes chat -q "hello" --model anthropic/claude-sonnet-4.6
```

如果使用 OpenRouter，请确保你的 API 密钥有余额。来自 OpenRouter 的 400 错误通常意味着该模型需要付费计划，或者模型 ID 有拼写错误。

---

## 仍然遇到问题？

如果这里没有涵盖你的问题：

1. **搜索现有问题：** [GitHub Issues](https://github.com/NousResearch/hermes-agent/issues)
2. **询问社区：** [Nous Research Discord](https://discord.gg/nousresearch)
3. **提交错误报告：** 请包含你的操作系统、Python 版本（`python3 --version`）、Hermes 版本（`hermes --version`）以及完整的错误消息。
