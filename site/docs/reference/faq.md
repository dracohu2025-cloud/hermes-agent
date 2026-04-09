---
sidebar_position: 3
title: "常见问题与故障排除"
description: "Hermes Agent 的常见问题解答及常见问题解决方案"
---

# 常见问题与故障排除

针对最常见问题和故障的快速解答与修复方案。

---

## 常见问题

### Hermes 支持哪些 LLM 供应商？

Hermes Agent 支持任何兼容 OpenAI API 的接口。支持的供应商包括：

- **[OpenRouter](https://openrouter.ai/)** — 通过一个 API 密钥访问数百个模型（推荐，灵活性最高）
- **Nous Portal** — Nous Research 自己的推理端点
- **OpenAI** — GPT-4o, o1, o3 等
- **Anthropic** — Claude 模型（通过 OpenRouter 或兼容代理）
- **Google** — Gemini 模型（通过 OpenRouter 或兼容代理）
- **z.ai / 智谱 AI** — GLM 模型
- **Kimi / Moonshot AI** — Kimi 模型
- **MiniMax** — 全球及中国区端点
- **本地模型** — 通过 [Ollama](https://ollama.com/)、[vLLM](https://docs.vllm.ai/)、[llama.cpp](https://github.com/ggerganov/llama.cpp)、[SGLang](https://github.com/sgl-project/sglang) 或任何兼容 OpenAI 的服务器

使用 `hermes model` 命令或编辑 `~/.hermes/.env` 来设置你的供应商。查看 [环境变量](./environment-variables.md) 参考文档以获取所有供应商的密钥配置。

### 它能在 Windows 上运行吗？

**不能原生运行。** Hermes Agent 需要类 Unix 环境。在 Windows 上，请安装 [WSL2](https://learn.microsoft.com/zh-cn/windows/wsl/install) 并在其中运行 Hermes。标准的安装命令在 WSL2 中可以完美运行：

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

### 我的数据会被发送到哪里吗？

API 调用**仅发送到你配置的 LLM 供应商**（例如 OpenRouter 或你本地的 Ollama 实例）。Hermes Agent 不会收集遥测数据、使用数据或分析数据。你的对话、记忆和技能都存储在本地的 `~/.hermes/` 目录中。

### 我可以离线使用或配合本地模型使用吗？

可以。运行 `hermes model`，选择 **Custom endpoint**，然后输入你服务器的 URL：

```bash
hermes model
# 选择: Custom endpoint (enter URL manually)
# API base URL: http://localhost:11434/v1
# API key: ollama
# Model name: qwen3.5:27b
# Context length: 32768   ← 设置为匹配你服务器实际的上下文窗口
```

或者直接在 `config.yaml` 中配置：

```yaml
model:
  default: qwen3.5:27b
  provider: custom
  base_url: http://localhost:11434/v1
```

Hermes 会将端点、供应商和基础 URL 持久化在 `config.yaml` 中，因此重启后依然有效。如果你的本地服务器只加载了一个模型，`/model custom` 会自动检测到它。你也可以在 config.yaml 中设置 `provider: custom` —— 它是一个原生支持的供应商，而不是其他任何东西的别名。

这适用于 Ollama、vLLM、llama.cpp server、SGLang、LocalAI 等。详见 [配置指南](../user-guide/configuration.md)。

:::tip Ollama 用户提示
如果你在 Ollama 中设置了自定义的 `num_ctx`（例如 `ollama run --num_ctx 16384`），请确保在 Hermes 中设置匹配的上下文长度 —— 因为 Ollama 的 `/api/show` 报告的是模型的*最大*上下文，而不是你配置的有效 `num_ctx`。
:::

### 使用费用是多少？

Hermes Agent 本身是**免费且开源的**（MIT 许可证）。你只需为你选择的供应商支付 LLM API 使用费。运行本地模型则是完全免费的。

### 多个人可以共用一个实例吗？

可以。[消息网关](../user-guide/messaging/index.md) 允许通过 Telegram、Discord、Slack、WhatsApp 或 Home Assistant 让多个用户与同一个 Hermes Agent 实例交互。访问权限通过白名单（特定用户 ID）和私聊配对（第一个发送消息的用户获得访问权）进行控制。

### 记忆（Memory）和技能（Skills）有什么区别？

- **记忆 (Memory)** 存储**事实** —— Agent 了解到的关于你、你的项目和偏好的信息。记忆会根据相关性自动检索。
- **技能 (Skills)** 存储**程序** —— 关于如何执行任务的步骤说明。当 Agent 遇到类似任务时会回想起技能。

两者都会跨会话持久化。详见 [记忆](../user-guide/features/memory.md) 和 [技能](../user-guide/features/skills.md)。

### 我可以在自己的 Python 项目中使用它吗？

可以。导入 `AIAgent` 类即可通过编程方式使用 Hermes：

```python
from run_agent import AIAgent

agent = AIAgent(model="openrouter/nous/hermes-3-llama-3.1-70b")
response = agent.chat("简要解释量子计算")
```

详见 [Python 库指南](../user-guide/features/code-execution.md) 以获取完整的 API 用法。

---

## 故障排除

### 安装问题

#### 安装后提示 `hermes: command not found`

**原因：** 你的 Shell 尚未重新加载更新后的 PATH。

**解决方案：**
```bash
# 重新加载你的 Shell 配置文件
source ~/.bashrc    # bash
source ~/.zshrc     # zsh

# 或者开启一个新的终端会话
```

如果仍然无效，请验证安装位置：
```bash
which hermes
ls ~/.local/bin/hermes
```

:::tip
安装程序会将 `~/.local/bin` 添加到你的 PATH 中。如果你使用非标准的 Shell 配置，请手动添加 `export PATH="$HOME/.local/bin:$PATH"`。
:::

#### Python 版本过旧

**原因：** Hermes 需要 Python 3.11 或更高版本。

**解决方案：**
```bash
python3 --version   # 检查当前版本

# 安装更新版本的 Python
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

#### 安装过程中出现权限拒绝（Permission denied）错误

**原因：** 对安装目录没有足够的写入权限。

**解决方案：**
```bash
# 不要对安装程序使用 sudo —— 它会安装到 ~/.local/bin
# 如果你之前使用了 sudo 安装，请先清理：
sudo rm /usr/local/bin/hermes
# 然后重新运行标准安装程序
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

---

### 供应商与模型问题

#### API 密钥无效

**原因：** 密钥缺失、过期、设置错误或供应商不匹配。

**解决方案：**
```bash
# 检查你的配置
hermes config show

# 重新配置你的供应商
hermes model

# 或者直接设置
hermes config set OPENROUTER_API_KEY sk-or-v1-xxxxxxxxxxxx
```

:::warning
确保密钥与供应商匹配。OpenAI 的密钥无法在 OpenRouter 上使用，反之亦然。检查 `~/.hermes/.env` 是否存在冲突的条目。
:::

#### 模型不可用 / 找不到模型

**原因：** 模型标识符不正确，或者你的供应商不提供该模型。

**解决方案：**
```bash
# 列出你供应商可用的模型
hermes model

# 设置一个有效的模型
hermes config set HERMES_MODEL openrouter/nous/hermes-3-llama-3.1-70b

# 或者在单次会话中指定
hermes chat --model openrouter/meta-llama/llama-3.1-70b-instruct
```

#### 频率限制（429 错误）

**原因：** 你超过了供应商的频率限制。

**解决方案：** 等待片刻后重试。如需持续使用，请考虑：
- 升级你的供应商套餐
- 切换到不同的模型或供应商
- 使用 `hermes chat --provider <alternative>` 路由到不同的后端

#### 超过上下文长度

**原因：** 对话内容超出了模型的上下文窗口，或者 Hermes 检测到的模型上下文长度有误。

**解决方案：**
```bash
# 压缩当前会话
/compress

# 或者开启一个新会话
hermes chat

# 使用具有更大上下文窗口的模型
hermes chat --model openrouter/google/gemini-3-flash-preview
```

如果这种情况发生在第一次长对话中，可能是 Hermes 识别的模型上下文长度不正确。检查它的检测结果：

查看 CLI 启动时的提示行 —— 它会显示检测到的上下文长度（例如 `📊 Context limit: 128000 tokens`）。你也可以在会话中使用 `/usage` 查看。

要修复上下文检测，请显式设置它：

```yaml
# 在 ~/.hermes/config.yaml 中
model:
  default: your-model-name
  context_length: 131072  # 你模型实际的上下文窗口
```
或者对于自定义端点，可以按模型添加：

```yaml
custom_providers:
  - name: "My Server"
    base_url: "http://localhost:11434/v1"
    models:
      qwen3.5:27b:
        context_length: 32768
```

关于自动检测的工作原理及所有覆盖选项，请参阅 [上下文长度检测](../integrations/providers.md#context-length-detection)。

---

### 终端问题

#### 命令因危险而被拦截

**原因：** Hermes 检测到了潜在的破坏性命令（例如 `rm -rf`，`DROP TABLE`）。这是一项安全特性。

**解决方案：** 收到提示时，请检查命令并输入 `y` 来批准执行。你也可以：
- 要求 Agent 使用更安全的替代方案
- 在 [安全文档](../user-guide/security.md) 中查看完整的危险模式列表

:::tip
这符合设计预期 —— Hermes 绝不会静默运行破坏性命令。审批提示会让你清楚地看到即将执行的内容。
:::

#### `sudo` 在消息网关中无法工作

**原因：** 消息网关在没有交互式终端的情况下运行，因此 `sudo` 无法提示输入密码。

**解决方案：**
- 避免在消息中使用 `sudo` —— 要求 Agent 寻找替代方案
- 如果必须使用 `sudo`，请在 `/etc/sudoers` 中为特定命令配置免密 sudo
- 或者切换到终端界面执行管理任务：`hermes chat`

#### Docker 后端无法连接

**原因：** Docker 守护进程未运行或用户缺少权限。

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

#### Bot 不响应消息

**原因：** Bot 未运行、未授权，或者你的用户不在允许列表中。

**解决方案：**
```bash
# 检查网关是否正在运行
hermes gateway status

# 启动网关
hermes gateway start

# 查看日志中的错误
cat ~/.hermes/logs/gateway.log | tail -50
```

#### 消息无法送达

**原因：** 网络问题、Bot 令牌过期或平台 Webhook 配置错误。

**解决方案：**
- 使用 `hermes gateway setup` 验证你的 Bot 令牌是否有效
- 检查网关日志：`cat ~/.hermes/logs/gateway.log | tail -50`
- 对于基于 Webhook 的平台（Slack、WhatsApp），确保你的服务器可以从公网访问

#### 允许列表困惑 —— 谁可以和 Bot 对话？

**原因：** 授权模式决定了谁拥有访问权限。

**解决方案：**

| 模式 | 工作原理 |
|------|-------------|
| **Allowlist** | 只有配置中列出的用户 ID 可以交互 |
| **DM pairing** | 第一个在私聊中发送消息的用户获得专属访问权 |
| **Open** | 任何人都可以交互（不建议在生产环境使用） |

在 `~/.hermes/config.yaml` 的网关设置下进行配置。请参阅 [消息文档](../user-guide/messaging/index.md)。

#### 网关无法启动

**原因：** 缺少依赖、端口冲突或令牌配置错误。

**解决方案：**
```bash
# 安装消息依赖
pip install "hermes-agent[telegram]"   # 或 [discord], [slack], [whatsapp]

# 检查端口冲突
lsof -i :8080

# 验证配置
hermes config show
```

#### macOS：网关找不到 Node.js / ffmpeg / 其他工具

**原因：** launchd 服务继承的是极简的 PATH (`/usr/bin:/bin:/usr/sbin:/sbin`)，其中不包含 Homebrew、nvm、cargo 或其他用户安装工具的目录。这通常会导致 WhatsApp 桥接器（`node not found`）或语音转录（`ffmpeg not found`）崩溃。

**解决方案：** 当你运行 `hermes gateway install` 时，网关会捕获你当前的 shell PATH。如果你在设置网关后安装了新工具，请重新运行安装命令以捕获更新后的 PATH：

```bash
hermes gateway install    # 重新快照当前的 PATH
hermes gateway start      # 检测更新后的 plist 并重新加载
```

你可以验证 plist 是否包含正确的 PATH：
```bash
/usr/libexec/PlistBuddy -c "Print :EnvironmentVariables:PATH" \
  ~/Library/LaunchAgents/ai.hermes.gateway.plist
```

---

### 性能问题

#### 响应缓慢

**原因：** 模型过大、API 服务器距离较远，或者带有大量工具的系统提示词（System Prompt）过重。

**解决方案：**
- 尝试更快/更小的模型：`hermes chat --model openrouter/meta-llama/llama-3.1-8b-instruct`
- 减少激活的工具集：`hermes chat -t "terminal"`
- 检查你到 Provider 的网络延迟
- 对于本地模型，确保你有足够的 GPU 显存（VRAM）

#### Token 使用量高

**原因：** 对话过长、系统提示词冗长，或大量的工具调用累积了上下文。

**解决方案：**
```bash
# 压缩对话以减少 token
/compress

# 检查会话 token 使用情况
/usage
```

:::tip
在长会话中定期使用 `/compress`。它会总结对话历史，在保留上下文的同时显著减少 token 使用量。
:::

#### 会话变得太长

**原因：** 持续的对话累积了消息和工具输出，接近了上下文限制。

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

#### MCP 服务器无法连接

**原因：** 找不到服务器二进制文件、命令路径错误或缺少运行时。

**解决方案：**
```bash
# 确保已安装 MCP 依赖（标准安装中已包含）
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

#### MCP 服务器的工具没有显示

**原因：** 服务器已启动但工具发现失败、工具被配置过滤掉，或者服务器不支持你预期的 MCP 能力。

**解决方案：**
- 检查网关/Agent 日志中的 MCP 连接错误
- 确保服务器响应 `tools/list` RPC 方法
- 检查该服务器下的 `tools.include`、`tools.exclude`、`tools.resources`、`tools.prompts` 或 `enabled` 设置
- 请记住，资源/提示词工具只有在会话实际支持这些能力时才会注册
- 修改配置后使用 `/reload-mcp`

```bash
# 验证 MCP 服务器配置
hermes config show | grep -A 12 mcp_servers

# 修改配置后重启 Hermes 或重新加载 MCP
hermes chat
```

另请参阅：
- [MCP (Model Context Protocol)](/user-guide/features/mcp)
- [在 Hermes 中使用 MCP](/guides/use-mcp-with-hermes)
- [MCP 配置参考](/reference/mcp-config-reference)

#### MCP 超时错误

**原因：** MCP 服务器响应时间过长，或者在执行过程中崩溃。

**解决方案：**
- 如果支持，在 MCP 服务器配置中增加超时时间
- 检查 MCP 服务器进程是否仍在运行
- 对于远程 HTTP MCP 服务器，检查网络连接性

:::warning
如果 MCP 服务器在请求中途崩溃，Hermes 会报告超时。请检查服务器自身的日志（而不仅仅是 Hermes 日志）来诊断根本原因。
:::

---

## Profile (配置文件) {#profiles}

### Profile 与直接设置 HERMES_HOME 有什么区别？

Profile 是在 `HERMES_HOME` 之上的管理层。你*可以*在每个命令前手动设置 `HERMES_HOME=/some/path`，但 Profile 为你处理了所有底层工作：创建目录结构、生成 shell 别名（`hermes-work`）、在 `~/.hermes/active_profile` 中跟踪当前激活的 Profile，并自动在所有 Profile 之间同步技能更新。它们还集成了 Tab 补全功能，因此你不需要记住路径。

### 两个 Profile 可以共享同一个 Bot 令牌吗？

不可以。每个消息平台（Telegram、Discord 等）都需要对 Bot 令牌的排他性访问。如果两个 Profile 尝试同时使用同一个令牌，第二个网关将无法连接。请为每个 Profile 创建一个独立的 Bot —— 对于 Telegram，请联系 [@BotFather](https://t.me/BotFather) 创建额外的 Bot。
### Profile 是否共享记忆或 Session？

不共享。每个 Profile 都有自己独立的记忆存储、Session 数据库和 Skills 目录。它们是完全隔离的。如果你想使用现有的记忆和 Session 创建一个新 Profile，请使用 `hermes profile create newname --clone-all` 来复制当前 Profile 的所有内容。

### 运行 `hermes update` 时会发生什么？

`hermes update` 会拉取最新代码并重新安装依赖项，且**仅执行一次**（不是按 Profile 执行）。随后它会自动将更新后的 Skills 同步到所有 Profile。你只需要运行一次 `hermes update` —— 它涵盖了机器上的每一个 Profile。

### 我可以将 Profile 迁移到另一台机器吗？

可以。将 Profile 导出为便携式归档文件，然后在另一台机器上导入：

```bash
# 在源机器上
hermes profile export work ./work-backup.tar.gz

# 将文件复制到目标机器，然后执行：
hermes profile import ./work-backup.tar.gz work
```

导入的 Profile 将包含导出时的所有配置、记忆、Session 和 Skills。如果新机器的设置不同，你可能需要更新路径或重新向 Provider 进行身份验证。

### 我可以运行多少个 Profile？

没有硬性限制。每个 Profile 只是 `~/.hermes/profiles/` 下的一个目录。实际限制取决于你的磁盘空间以及系统可以处理多少个并发 Gateway（每个 Gateway 都是一个轻量级的 Python 进程）。运行几十个 Profile 是没问题的；每个空闲的 Profile 不会消耗资源。

---

## 工作流与模式

### 为不同任务使用不同模型（多模型工作流）

**场景：** 你使用 GPT-5.4 作为日常主力，但 Gemini 或 Grok 编写社交媒体内容的效果更好。每次手动切换模型非常繁琐。

**解决方案：任务委派（Delegation）配置。** Hermes 可以自动将 sub-agents 路由到不同的模型。在 `~/.hermes/config.yaml` 中设置：

```yaml
delegation:
  model: "google/gemini-3-flash-preview"   # sub-agents 使用此模型
  provider: "openrouter"                    # sub-agents 使用的 Provider
```

现在，当你告诉 Hermes “帮我写一段关于 X 的 Twitter 推文”并触发 `delegate_task` sub-agent 时，该 sub-agent 将在 Gemini 上运行，而不是你的主模型。你的主对话仍保持在 GPT-5.4 上。

你也可以在 Prompt 中明确说明：*“委派一个任务来编写关于我们产品发布的社交媒体帖子。使用你的 sub-agent 进行实际编写。”* Agent 将使用 `delegate_task`，它会自动采用委派配置。

对于不涉及委派的一次性模型切换，请在 CLI 中使用 `/model`：

```bash
/model google/gemini-3-flash-preview    # 为当前 Session 切换
# ... 编写你的内容 ...
/model openai/gpt-5.4                   # 切换回来
```

有关委派工作原理的更多信息，请参阅 [Subagent Delegation](../user-guide/features/delegation.md)。

### 在一个 WhatsApp 号码上运行多个 Agent（按聊天绑定）

**场景：** 在 OpenClaw 中，你可以将多个独立的 Agent 绑定到特定的 WhatsApp 聊天中 —— 一个用于家庭购物清单群组，另一个用于你的私聊。Hermes 能做到吗？

**当前限制：** 每个 Hermes Profile 都需要自己的 WhatsApp 号码/Session。你不能将多个 Profile 绑定到同一个 WhatsApp 号码下的不同聊天中 —— WhatsApp 桥接器（Baileys）每个号码使用一个经过身份验证的 Session。

**变通方法：**

1. **使用带有性格切换的单一 Profile。** 创建不同的 `AGENTS.md` 上下文文件，或使用 `/personality` 命令根据聊天更改行为。Agent 会识别它所在的聊天并进行适配。

2. **为专门任务使用 Cron Job。** 对于购物清单追踪器，设置一个 Cron Job 来监控特定聊天并管理清单 —— 不需要独立的 Agent。

3. **使用不同的号码。** 如果你需要真正独立的 Agent，请为每个 Profile 配备自己的 WhatsApp 号码。Google Voice 等服务提供的虚拟号码可以胜任。

4. **改用 Telegram 或 Discord。** 这些平台更自然地支持按聊天绑定 —— 每个 Telegram 群组或 Discord 频道都有自己的 Session，你可以在同一个账户上运行多个 Bot Token（每个 Profile 一个）。

更多详情请参阅 [Profiles](../user-guide/profiles.md) 和 [WhatsApp 设置](../user-guide/messaging/whatsapp.md)。

### 控制 Telegram 中显示的内容（隐藏日志和推理过程）

**场景：** 你在 Telegram 中看到了 Gateway 执行日志、Hermes 推理过程和 Tool Call 详情，而你只想看到最终输出。

**解决方案：** `config.yaml` 中的 `display.tool_progress` 设置控制显示多少 Tool 活动：

```yaml
display:
  tool_progress: "off"   # 选项：off, new, all, verbose
```

- **`off`** —— 仅显示最终回复。不显示 Tool Call、推理过程或日志。
- **`new`** —— 在 Tool Call 发生时显示（简短的单行提示）。
- **`all`** —— 显示所有 Tool 活动，包括结果。
- **`verbose`** —— 完整详情，包括 Tool 参数和输出。

对于即时通讯平台，通常选择 `off` 或 `new`。修改 `config.yaml` 后，重启 Gateway 以使更改生效。

你也可以通过 `/verbose` 命令（如果已启用）在每个 Session 中切换此设置：

```yaml
display:
  tool_progress_command: true   # 在 Gateway 中启用 /verbose
```

### 在 Telegram 上管理 Skills（斜杠命令限制）

**场景：** Telegram 有 100 个斜杠命令的限制，而你的 Skills 已经超过了这个限制。你想在 Telegram 上禁用不需要的 Skills，但 `hermes skills config` 的设置似乎没有生效。

**解决方案：** 使用 `hermes skills config` 按平台禁用 Skills。这会写入 `config.yaml`：

```yaml
skills:
  disabled: []                    # 全局禁用的 Skills
  platform_disabled:
    telegram: [skill-a, skill-b]  # 仅在 Telegram 上禁用
```

更改此设置后，**重启 Gateway**（`hermes gateway restart` 或手动结束并重新启动）。Telegram Bot 的命令菜单会在启动时重新构建。

:::tip
描述非常长的 Skills 在 Telegram 菜单中会被截断为 40 个字符，以符合 Payload 大小限制。如果 Skills 没有出现，可能是总 Payload 大小问题，而不仅仅是 100 个命令的数量限制 —— 禁用不常用的 Skills 对解决这两个问题都有帮助。
:::

### 共享 Thread Session（多用户，一个对话）

**场景：** 你有一个 Telegram 或 Discord Thread，其中有多个人 @ 机器人。你希望该 Thread 中的所有提及都成为一个共享对话的一部分，而不是按用户区分的独立 Session。

**当前行为：** Hermes 在大多数平台上以用户 ID 为键创建 Session，因此每个人都有自己的对话上下文。这是为了隐私和上下文隔离而设计的。

**变通方法：**

1. **使用 Slack。** Slack Session 是以 Thread 为键的，而不是用户。同一 Thread 中的多个用户共享一个对话 —— 这正是你所描述的行为。这是最自然的选择。

2. **在群聊中使用单一用户。** 如果由一个人担任指定的“操作员”来转达问题，Session 将保持统一。其他人可以旁观。

3. **使用 Discord 频道。** Discord Session 是以频道为键的，因此同一频道中的所有用户共享上下文。为共享对话使用专用频道。

### 将 Hermes 导出到另一台机器

**场景：** 你在一部机器上积累了 Skills、Cron Jobs 和记忆，并希望将所有内容迁移到一台新的专用 Linux 机器上。

**解决方案：**

1. 在新机器上安装 Hermes Agent：
   ```bash
   curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
   ```

2. 复制整个 `~/.hermes/` 目录，但**排除** `hermes-agent` 子目录（那是代码仓库 —— 新安装的程序有自己的仓库）：
   ```bash
   # 在源机器上
   rsync -av --exclude='hermes-agent' ~/.hermes/ newmachine:~/.hermes/
   ```

   或者使用 Profile 导出/导入功能：
   ```bash
   # 在源机器上
   hermes profile export default ./hermes-backup.tar.gz

   # 在目标机器上
   hermes profile import ./hermes-backup.tar.gz default
   ```
3. 在新机器上，运行 `hermes setup` 来验证 API keys 和 provider 配置是否正常工作。重新认证所有消息平台（特别是使用二维码配对的 WhatsApp）。

`~/.hermes/` 目录包含了所有内容：`config.yaml`、`.env`、`SOUL.md`、`memories/`、`skills/`、`state.db`（会话）、`cron/` 以及任何自定义插件。代码本身位于 `~/.hermes/hermes-agent/` 并会被重新安装。

### 安装后重新加载 shell 时提示 Permission denied

**场景：** 运行 Hermes 安装程序后，执行 `source ~/.zshrc` 报错权限不足（permission denied）。

**原因：** 这通常是因为 `~/.zshrc`（或 `~/.bashrc`）的文件权限不正确，或者安装程序无法正常写入该文件。这不是 Hermes 特有的问题，而是 shell 配置文件的权限问题。

**解决方案：**
```bash
# 检查权限
ls -la ~/.zshrc

# 如果需要则修复权限（应该是 -rw-r--r-- 或 644）
chmod 644 ~/.zshrc

# 然后重新加载
source ~/.zshrc

# 或者直接打开一个新的终端窗口 —— 它会自动加载 PATH 变更
```

如果安装程序添加了 PATH 行但权限有误，你可以手动添加：
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
```

### 首次运行 Agent 时出现 Error 400

**场景：** 设置过程很顺利，但第一次尝试对话时失败并返回 HTTP 400 错误。

**原因：** 通常是模型名称不匹配 —— 配置的模型在你的 provider 中不存在，或者你的 API key 没有该模型的访问权限。

**解决方案：**
```bash
# 检查配置的模型和 provider
hermes config show | head -20

# 重新运行模型选择
hermes model

# 或者使用一个已知可用的模型进行测试
hermes chat -q "hello" --model anthropic/claude-sonnet-4.6
```

如果使用 OpenRouter，请确保你的 API key 中有余额。OpenRouter 返回 400 通常意味着该模型需要付费计划，或者模型 ID 存在拼写错误。

---

## 仍然无法解决？

如果你的问题在这里没有提到：

1. **搜索现有 Issue：** [GitHub Issues](https://github.com/NousResearch/hermes-agent/issues)
2. **咨询社区：** [Nous Research Discord](https://discord.gg/nousresearch)
3. **提交 Bug 报告：** 请包含你的操作系统、Python 版本（`python3 --version`）、Hermes 版本（`hermes --version`）以及完整的错误信息。
