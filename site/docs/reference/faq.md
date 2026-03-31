---
sidebar_position: 3
title: "常见问题与故障排除"
description: "关于 Hermes Agent 的常见问题及解决方案"
---

# 常见问题与故障排除

针对最常见问题和故障的快速解答与修复方法。

---

## 常见问题

### Hermes 支持哪些 LLM 提供商？

Hermes Agent 兼容任何 OpenAI 格式的 API。支持的提供商包括：

- **[OpenRouter](https://openrouter.ai/)** — 通过一个 API 密钥访问数百个模型（推荐，灵活性高）
- **Nous Portal** — Nous Research 自家的推理端点
- **OpenAI** — GPT-4o, o1, o3 等
- **Anthropic** — Claude 模型（通过 OpenRouter 或兼容代理）
- **Google** — Gemini 模型（通过 OpenRouter 或兼容代理）
- **z.ai / ZhipuAI** — GLM 模型
- **Kimi / Moonshot AI** — Kimi 模型
- **MiniMax** — 全球和中国区端点
- **本地模型** — 通过 [Ollama](https://ollama.com/)、[vLLM](https://docs.vllm.ai/)、[llama.cpp](https://github.com/ggerganov/llama.cpp)、[SGLang](https://github.com/sgl-project/sglang) 或任何 OpenAI 兼容服务器

使用 `hermes model` 命令或编辑 `~/.hermes/.env` 文件来设置你的提供商。所有提供商的配置键请参阅[环境变量](./environment-variables.md)参考。

### 它能在 Windows 上运行吗？

**原生不支持。** Hermes Agent 需要类 Unix 环境。在 Windows 上，请安装 [WSL2](https://learn.microsoft.com/en-us/windows/wsl/install) 并在其中运行 Hermes。标准安装命令在 WSL2 中完全可用：

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

### 我的数据会被发送到哪里？

API 调用**仅发送到你配置的 LLM 提供商**（例如 OpenRouter、你本地的 Ollama 实例）。Hermes Agent 不收集遥测数据、使用数据或分析数据。你的对话、记忆和技能都本地存储在 `~/.hermes/` 目录中。

### 我能离线使用吗 / 能使用本地模型吗？

可以。运行 `hermes model`，选择 **Custom endpoint**，然后输入你的服务器 URL：

```bash
hermes model
# 选择：Custom endpoint (enter URL manually)
# API base URL: http://localhost:11434/v1
# API key: ollama
# Model name: qwen3.5:27b
# Context length: 32768   ← 将此值设置为与你服务器实际上下文窗口匹配
```

或者直接在 `config.yaml` 中配置：

```yaml
model:
  default: qwen3.5:27b
  provider: custom
  base_url: http://localhost:11434/v1
```

Hermes 会将端点、提供商和基础 URL 持久化保存在 `config.yaml` 中，因此重启后配置依然有效。如果你的本地服务器只加载了一个模型，`/model custom` 会自动检测它。你也可以在 config.yaml 中设置 `provider: custom` — 它是一个独立的提供商，不是其他任何东西的别名。

这适用于 Ollama、vLLM、llama.cpp 服务器、SGLang、LocalAI 等。详情请参阅[配置指南](../user-guide/configuration.md)。

:::tip Ollama 用户
如果你在 Ollama 中设置了自定义的 `num_ctx`（例如 `ollama run --num_ctx 16384`），请确保在 Hermes 中设置匹配的上下文长度 — Ollama 的 `/api/show` 报告的是模型的*最大*上下文长度，而不是你配置的有效 `num_ctx`。
:::

### 费用是多少？

Hermes Agent 本身是**免费且开源的**（MIT 许可证）。你只需为你选择的 LLM 提供商的 API 使用量付费。本地模型完全免费运行。

### 多人能使用同一个实例吗？

可以。[消息网关](../user-guide/messaging/index.md)允许多个用户通过 Telegram、Discord、Slack、WhatsApp 或 Home Assistant 与同一个 Hermes Agent 实例交互。访问权限通过允许列表（特定用户 ID）和私聊配对（第一个发送消息的用户获得访问权）来控制。

### 记忆和技能有什么区别？

- **记忆**存储**事实** — 智能体了解到的关于你、你的项目和偏好的信息。记忆会根据相关性自动检索。
- **技能**存储**流程** — 如何做某事的逐步说明。当智能体遇到类似任务时会回忆技能。

两者都会在会话间持久化。详情请参阅[记忆](../user-guide/features/memory.md)和[技能](../user-guide/features/skills.md)。

### 我能在自己的 Python 项目中使用它吗？

可以。导入 `AIAgent` 类并以编程方式使用 Hermes：

```python
from hermes.agent import AIAgent

agent = AIAgent(model="openrouter/nous/hermes-3-llama-3.1-70b")
response = agent.chat("简要解释一下量子计算")
```

完整的 API 用法请参阅 [Python 库指南](../user-guide/features/code-execution.md)。

---

## 故障排除

### 安装问题

#### 安装后出现 `hermes: command not found`

**原因：** 你的 shell 没有重新加载更新后的 PATH。

**解决方案：**
```bash
# 重新加载你的 shell 配置文件
source ~/.bashrc    # bash
source ~/.zshrc     # zsh

# 或者启动一个新的终端会话
```

如果仍然不行，请验证安装位置：
```bash
which hermes
ls ~/.local/bin/hermes
```

:::tip
安装程序会将 `~/.local/bin` 添加到你的 PATH 中。如果你使用非标准的 shell 配置，请手动添加 `export PATH="$HOME/.local/bin:$PATH"`。
:::

#### Python 版本太旧

**原因：** Hermes 需要 Python 3.11 或更高版本。

**解决方案：**
```bash
python3 --version   # 检查当前版本

# 安装更新的 Python
sudo apt install python3.12   # Ubuntu/Debian
brew install python@3.12      # macOS
```

安装程序会自动处理这个问题 — 如果你在手动安装时看到此错误，请先升级 Python。

#### `uv: command not found`

**原因：** `uv` 包管理器未安装或不在 PATH 中。

**解决方案：**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc
```

#### 安装期间出现权限被拒绝错误

**原因：** 对安装目录的写入权限不足。

**解决方案：**
```bash
# 不要对安装程序使用 sudo — 它安装到 ~/.local/bin
# 如果你之前用 sudo 安装过，请清理：
sudo rm /usr/local/bin/hermes
# 然后重新运行标准安装程序
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

---

### 提供商与模型问题

#### API 密钥无效

**原因：** 密钥缺失、已过期、设置错误或属于错误的提供商。

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
确保密钥与提供商匹配。OpenAI 密钥不能用于 OpenRouter，反之亦然。检查 `~/.hermes/.env` 中是否有冲突的条目。
:::

#### 模型不可用 / 找不到模型

**原因：** 模型标识符不正确或你的提供商不提供该模型。

**解决方案：**
```bash
# 列出你的提供商可用的模型
hermes model

# 设置一个有效的模型
hermes config set HERMES_MODEL openrouter/nous/hermes-3-llama-3.1-70b

# 或者按会话指定
hermes chat --model openrouter/meta-llama/llama-3.1-70b-instruct
```

#### 速率限制（429 错误）

**原因：** 你已超过提供商的速率限制。

**解决方案：** 稍等片刻再重试。对于持续使用，请考虑：
- 升级你的提供商套餐
- 切换到不同的模型或提供商
- 使用 `hermes chat --provider <alternative>` 路由到不同的后端

#### 超出上下文长度

**原因：** 对话内容过长，超过了模型的上下文窗口，或者 Hermes 检测到的模型上下文长度有误。

**解决方案：**
```bash
# 压缩当前会话
/compress

# 或者开始一个新的会话
hermes chat

# 使用具有更大上下文窗口的模型
hermes chat --model openrouter/google/gemini-2.0-flash-001
```

如果这种情况发生在第一次长对话时，Hermes 可能对你的模型上下文长度检测有误。检查它检测到了什么：

查看 CLI 启动行 — 它会显示检测到的上下文长度（例如 `📊 Context limit: 128000 tokens`）。你也可以在会话中使用 `/usage` 命令查看。

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

关于自动检测的工作原理和所有覆盖选项，请参阅[上下文长度检测](../user-guide/configuration.md#context-length-detection)。

---

### 终端问题

#### 命令被阻止，视为危险

**原因：** Hermes 检测到一个可能具有破坏性的命令（例如 `rm -rf`、`DROP TABLE`）。这是一个安全功能。

**解决方案：** 当提示时，检查命令并输入 `y` 来批准它。你也可以：
- 要求智能体使用更安全的替代方案
- 在[安全文档](../user-guide/security.md)中查看完整的危险模式列表

:::tip
这是预期行为 — Hermes 永远不会静默运行破坏性命令。批准提示会向你显示将要执行的确切内容。
:::

#### 通过消息网关 `sudo` 不工作

**原因：** 消息网关运行时没有交互式终端，因此 `sudo` 无法提示输入密码。

**解决方案：**
- 在消息传递中避免使用 `sudo` — 要求智能体寻找替代方案
- 如果必须使用 `sudo`，请在 `/etc/sudoers` 中为特定命令配置免密码 sudo
- 或者切换到终端界面执行管理任务：`hermes chat`

#### Docker 后端无法连接

**原因：** Docker 守护进程未运行或用户缺少权限。

**解决方案：**
```bash
# 检查 Docker 是否在运行
docker info

# 将你的用户添加到 docker 组
sudo usermod -aG docker $USER
newgrp docker

# 验证
docker run hello-world
```

---

### 消息传递问题

#### 机器人不回复消息

**原因：** 机器人未运行、未授权，或者你的用户不在允许列表中。

**解决方案：**
```bash
# 检查网关是否在运行
hermes gateway status

# 启动网关
hermes gateway start

# 检查日志中的错误
cat ~/.hermes/logs/gateway.log | tail -50
```

#### 消息未送达

**原因：** 网络问题、机器人令牌过期或平台 Webhook 配置错误。

**解决方案：**
- 使用 `hermes gateway setup` 验证你的机器人令牌是否有效
- 检查网关日志：`cat ~/.hermes/logs/gateway.log | tail -50`
- 对于基于 Webhook 的平台（Slack、WhatsApp），确保你的服务器可公开访问

#### 允许列表困惑 — 谁可以和机器人对话？

**原因：** 授权模式决定了谁有访问权限。

**解决方案：**

| 模式 | 工作原理 |
|------|-------------|
| **允许列表** | 只有配置中列出的用户 ID 可以交互 |
| **私聊配对** | 第一个在私聊中发送消息的用户获得独占访问权 |
| **开放** | 任何人都可以交互（不推荐用于生产环境） |

在你的网关设置下的 `~/.hermes/config.yaml` 中配置。请参阅[消息传递文档](../user-guide/messaging/index.md)。

#### 网关无法启动

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

#### macOS：网关找不到 Node.js / ffmpeg / 其他工具

**原因：** launchd 服务继承了一个最小的 PATH（`/usr/bin:/bin:/usr/sbin:/sbin`），其中不包含 Homebrew、nvm、cargo 或其他用户安装的工具目录。这通常会破坏 WhatsApp 桥接（`node not found`）或语音转录（`ffmpeg not found`）。

**解决方案：** 当你运行 `hermes gateway install` 时，网关会捕获你的 shell PATH。如果你在设置网关之后安装了工具，请重新运行安装以捕获更新后的 PATH：

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
#### 响应缓慢

**原因：** 模型过大、API 服务器距离过远，或者系统提示词过于复杂且包含大量工具。

**解决方案：**
- 尝试使用更快/更小的模型：`hermes chat --model openrouter/meta-llama/llama-3.1-8b-instruct`
- 减少活跃的工具集：`hermes chat -t "terminal"`
- 检查你到服务提供商的网络延迟
- 对于本地模型，确保你有足够的 GPU 显存

#### 令牌使用量过高

**原因：** 对话过长、系统提示词过于冗长，或者大量工具调用累积了上下文。

**解决方案：**
```bash
# 压缩对话以减少令牌使用
/compress

# 检查会话令牌使用情况
/usage
```

:::tip
在长时间会话中定期使用 `/compress` 命令。它会总结对话历史，在保留上下文的同时显著减少令牌使用量。
:::

#### 会话变得过长

**原因：** 长时间的对话会累积消息和工具输出，接近上下文长度限制。

**解决方案：**
```bash
# 压缩当前会话（保留关键上下文）
/compress

# 开启一个引用旧会话的新会话
hermes chat

# 如果需要，稍后恢复特定的会话
hermes chat --continue
```

---

### MCP 问题

#### MCP 服务器无法连接

**原因：** 找不到服务器二进制文件、命令路径错误或缺少运行时环境。

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

验证你的 `~/.hermes/config.yaml` 中的 MCP 配置：
```yaml
mcp_servers:
  filesystem:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/docs"]
```

#### MCP 服务器的工具未显示

**原因：** 服务器已启动但工具发现失败、工具被配置过滤掉，或者服务器不支持你期望的 MCP 能力。

**解决方案：**
- 检查网关/代理日志中的 MCP 连接错误
- 确保服务器响应 `tools/list` RPC 方法
- 检查该服务器配置下的任何 `tools.include`、`tools.exclude`、`tools.resources`、`tools.prompts` 或 `enabled` 设置
- 请记住，资源/提示词工具仅在会话实际支持这些能力时才会被注册
- 更改配置后使用 `/reload-mcp`

```bash
# 验证 MCP 服务器是否已配置
hermes config show | grep -A 12 mcp_servers

# 更改配置后重启 Hermes 或重新加载 MCP
hermes chat
```

另请参阅：
- [MCP (Model Context Protocol)](/docs/user-guide/features/mcp)
- [在 Hermes 中使用 MCP](/docs/guides/use-mcp-with-hermes)
- [MCP 配置参考](/docs/reference/mcp-config-reference)

#### MCP 超时错误

**原因：** MCP 服务器响应时间过长，或者执行过程中崩溃。

**解决方案：**
- 如果支持，在你的 MCP 服务器配置中增加超时时间
- 检查 MCP 服务器进程是否仍在运行
- 对于远程 HTTP MCP 服务器，检查网络连接

:::warning
如果 MCP 服务器在请求中途崩溃，Hermes 会报告超时。请检查服务器自身的日志（不仅仅是 Hermes 日志）来诊断根本原因。
:::

---

## 配置文件 {#profiles}

### 配置文件与直接设置 HERMES_HOME 有何不同？

配置文件是建立在 `HERMES_HOME` 之上的一个管理层。你*可以*在每次命令前手动设置 `HERMES_HOME=/some/path`，但配置文件为你处理了所有底层工作：创建目录结构、生成 shell 别名（`hermes-work`）、在 `~/.hermes/active_profile` 中跟踪活动配置文件，以及自动在所有配置文件间同步技能更新。它们还与标签页补全集成，因此你无需记住路径。

### 两个配置文件可以共享同一个机器人令牌吗？

不可以。每个消息平台（Telegram、Discord 等）都需要独占访问一个机器人令牌。如果两个配置文件同时尝试使用同一个令牌，第二个网关将无法连接。请为每个配置文件创建一个独立的机器人——对于 Telegram，请与 [@BotFather](https://t.me/BotFather) 对话来创建额外的机器人。

### 配置文件之间共享内存或会话吗？

不共享。每个配置文件都有自己的内存存储、会话数据库和技能目录。它们是完全隔离的。如果你想基于现有的记忆和会话创建一个新的配置文件，可以使用 `hermes profile create newname --clone-all` 来从当前配置文件复制所有内容。

### 运行 `hermes update` 会发生什么？

`hermes update` 会拉取最新代码并重新安装依赖项**一次**（不是针对每个配置文件）。然后它会自动将更新后的技能同步到所有配置文件。你只需要运行一次 `hermes update`——它会覆盖机器上的所有配置文件。

### 我可以将配置文件移动到另一台机器吗？

可以。将配置文件导出为可移植的归档文件，然后在另一台机器上导入：

```bash
# 在源机器上
hermes profile export work ./work-backup.tar.gz

# 将文件复制到目标机器，然后：
hermes profile import ./work-backup.tar.gz work
```

导入的配置文件将拥有导出时的所有配置、记忆、会话和技能。如果新机器的设置不同，你可能需要更新路径或重新向服务提供商进行身份验证。

### 我可以运行多少个配置文件？

没有硬性限制。每个配置文件只是 `~/.hermes/profiles/` 下的一个目录。实际限制取决于你的磁盘空间以及系统能处理多少个并发网关（每个网关都是一个轻量级的 Python 进程）。运行数十个配置文件是可以的；每个空闲的配置文件不占用任何资源。

---

## 仍然卡住？

如果你的问题未在此处涵盖：

1.  **搜索现有问题：** [GitHub Issues](https://github.com/NousResearch/hermes-agent/issues)
2.  **询问社区：** [Nous Research Discord](https://discord.gg/nousresearch)
3.  **提交错误报告：** 请包含你的操作系统、Python 版本（`python3 --version`）、Hermes 版本（`hermes --version`）以及完整的错误信息
