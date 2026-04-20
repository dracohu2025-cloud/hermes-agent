---
sidebar_position: 3
title: "常见问题与故障排查"
description: "Hermes Agent 的常见问题解答及常见问题的解决方案"
---

# 常见问题与故障排查 {#faq-troubleshooting}

最常见的问题和快速修复方法。

---

## 常见问题 {#frequently-asked-questions}

### Hermes 支持哪些 LLM 提供商？ {#what-llm-providers-work-with-hermes}

Hermes Agent 兼容所有 OpenAI 格式的 API。支持的提供商包括：

- **[OpenRouter](https://openrouter.ai/)** — 用一个 API key 接入数百个模型（推荐，灵活性最高）
- **Nous Portal** — Nous Research 自有的推理端点
- **OpenAI** — GPT-4o、o1、o3 等
- **Anthropic** — Claude 系列模型（通过 OpenRouter 或兼容代理）
- **Google** — Gemini 系列模型（通过 OpenRouter 或兼容代理）
- **z.ai / ZhipuAI** — GLM 系列模型
- **Kimi / Moonshot AI** — Kimi 系列模型
- **MiniMax** — 国际版和中国版端点
- **本地模型** — 通过 [Ollama](https://ollama.com/)、[vLLM](https://docs.vllm.ai/)、[llama.cpp](https://github.com/ggerganov/llama.cpp)、[SGLang](https://github.com/sgl-project/sglang) 或任何兼容 OpenAI 格式的服务器运行

使用 `hermes model` 设置提供商，或直接编辑 `~/.hermes/.env`。所有提供商相关的 key 详见 [环境变量](./environment-variables.md) 参考文档。

### Windows 能用吗？ {#does-it-work-on-windows}

**不能原生运行。** Hermes Agent 需要类 Unix 环境。Windows 用户请安装 [WSL2](https://learn.microsoft.com/en-us/windows/wsl/install)，然后在 WSL2 内部运行 Hermes。标准安装命令在 WSL2 中可以正常使用：

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

### Android / Termux 能用吗？ {#does-it-work-on-android-termux}

可以 — Hermes 现在已经有了在 Android 手机上经过测试的 Termux 安装路径。

快速安装：

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

完整的显式手动步骤、支持的额外组件以及当前限制，请参见 [Termux 指南](../getting-started/termux.md)。

重要提示：完整的 `.[all]` 额外组件目前在 Android 上不可用，因为 `voice` 额外组件依赖 `faster-whisper` → `ctranslate2`，而 `ctranslate2` 没有发布 Android 版本的 wheel 包。请改用经过测试的 `.[termux]` 额外组件。

### 我的数据会被发送到别处吗？ {#is-my-data-sent-anywhere}

API 请求**只发送到你配置的 LLM 提供商**（例如 OpenRouter、你本地的 Ollama 实例）。Hermes Agent 不收集遥测数据、使用数据或分析数据。你的对话、记忆和技能都存储在本地 `~/.hermes/` 目录中。

### 可以离线使用 / 配合本地模型使用吗？ {#can-i-use-it-offline-with-local-models}

可以。运行 `hermes model`，选择 **Custom endpoint**，然后输入你的服务器地址：

```bash
hermes model
# 选择：Custom endpoint (enter URL manually)
# API base URL: http://localhost:11434/v1
# API key: ollama
# Model name: qwen3.5:27b
# Context length: 32768   ← 设置为与你服务器实际上下文窗口一致
```

或者直接在 `config.yaml` 中配置：

```yaml
model:
  default: qwen3.5:27b
  provider: custom
  base_url: http://localhost:11434/v1
```

Hermes 会将端点、提供商和 base URL 持久化到 `config.yaml` 中，重启后依然有效。如果你的本地服务器只加载了一个模型，`/model custom` 会自动检测它。你也可以在 config.yaml 中设置 `provider: custom` —— 这是一个一等公民的提供商，不是其他任何提供商的别名。

这适用于 Ollama、vLLM、llama.cpp server、SGLang、LocalAI 等。详情参见 [配置指南](../user-guide/configuration.md)。

:::tip Ollama 用户
<a id="ollama-users"></a>
如果你在 Ollama 中设置了自定义的 `num_ctx`（例如 `ollama run --num_ctx 16384`），请确保在 Hermes 中设置匹配的上下文长度 —— Ollama 的 `/api/show` 返回的是模型的*最大*上下文，不是你实际配置的 `num_ctx`。
:::

:::tip 本地模型超时问题
<a id="timeouts-with-local-models"></a>
Hermes 会自动检测本地端点并放宽流式超时（读取超时从 120 秒提升到 1800 秒，禁用流停滞检测）。如果在超大上下文下仍然遇到超时，请在 `.env` 中设置 `HERMES_STREAM_READ_TIMEOUT=1800`。详情参见 [本地 LLM 指南](../guides/local-llm-on-mac.md#timeouts)。
:::

### 使用成本是多少？ {#how-much-does-it-cost}

Hermes Agent 本身**免费开源**（MIT 许可证）。你只需要支付所选 LLM API 提供商的使用费用。本地模型完全免费运行。
### 多人可以共用一个实例吗？ {#can-multiple-people-use-one-instance}

可以。[消息网关](../user-guide/messaging/index.md) 支持多个用户通过 Telegram、Discord、Slack、WhatsApp 或 Home Assistant 与同一个 Hermes Agent 实例交互。访问权限通过白名单（指定用户 ID）和 DM 配对（第一个发消息的用户获得访问权）来控制。

### Memory 和 Skills 有什么区别？ {#what-s-the-difference-between-memory-and-skills}

- **Memory** 存储的是**事实**——Agent 知道的关于你、你的项目和你的偏好的信息。Memory 会根据相关性自动检索。
- **Skills** 存储的是**流程**——如何一步步完成某事的指令。Skills 在 Agent 遇到类似任务时被调用。

两者都会跨会话持久保存。详见 [Memory](../user-guide/features/memory.md) 和 [Skills](../user-guide/features/skills.md)。

### 我可以在自己的 Python 项目中使用吗？ {#can-i-use-it-in-my-own-python-project}

可以。导入 `AIAgent` 类，以编程方式使用 Hermes：

```python
from run_agent import AIAgent

agent = AIAgent(model="anthropic/claude-opus-4.7")
response = agent.chat("Explain quantum computing briefly")
```

完整的 API 用法请参考 [Python Library 指南](../user-guide/features/code-execution.md)。

---

## 故障排查 {#troubleshooting}

### 安装问题 {#installation-issues}

#### 安装后提示 `hermes: command not found` {#hermes-command-not-found-after-installation}

**原因：** 你的 shell 还没有重新加载更新后的 PATH。

**解决方法：**
```bash
# 重新加载 shell 配置文件
source ~/.bashrc    # bash
source ~/.zshrc     # zsh

# 或者新开一个终端窗口
```

如果还是不行，检查一下安装位置：
```bash
which hermes
ls ~/.local/bin/hermes
```

:::tip
安装程序会把 `~/.local/bin` 添加到你的 PATH 中。如果你使用了非标准的 shell 配置，需要手动添加 `export PATH="$HOME/.local/bin:$PATH"`。
:::

#### Python 版本过低 {#python-version-too-old}

**原因：** Hermes 需要 Python 3.11 或更高版本。

**解决方法：**
```bash
python3 --version   # 检查当前版本

# 安装更新的 Python
sudo apt install python3.12   # Ubuntu/Debian
brew install python@3.12      # macOS
```

安装程序会自动处理这个问题——如果你在手动安装时看到这个报错，先升级 Python 再试。

#### 提示 `uv: command not found` {#uv-command-not-found}

**原因：** `uv` 包管理器没有安装，或者不在 PATH 中。

**解决方法：**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc
```

#### 安装时出现权限拒绝错误 {#permission-denied-errors-during-install}

**原因：** 对安装目录的写入权限不足。

**解决方法：**
```bash
# 不要对安装程序使用 sudo——它会安装到 ~/.local/bin
# 如果你之前用 sudo 安装过，先清理：
sudo rm /usr/local/bin/hermes
# 然后重新运行标准安装程序
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

---

### 提供商与模型问题 {#provider-model-issues}

#### `/model` 只显示一个提供商 / 无法切换提供商 {#model-only-shows-one-provider-can-t-switch-providers}

**原因：** `/model`（在聊天会话中）只能切换你已经**配置过**的提供商。如果你只设置了 OpenRouter，那 `/model` 就只会显示它。

**解决方法：** 退出当前会话，在终端里用 `hermes model` 来添加新的提供商：

```bash
# 先退出 Hermes 聊天会话（Ctrl+C 或 /quit）

# 运行完整的提供商设置向导
hermes model

# 这样可以：添加提供商、运行 OAuth、输入 API 密钥、配置端点
```

通过 `hermes model` 添加新提供商后，新开一个聊天会话——`/model` 现在就会显示所有已配置的提供商了。

:::tip 快速参考
<a id="quick-reference"></a>
| 想要…… | 使用 |
|-----------|-----|
| 添加新提供商 | `hermes model`（在终端中） |
| 输入/修改 API 密钥 | `hermes model`（在终端中） |
| 在会话中切换模型 | `/model &lt;name&gt;`（在会话内） |
| 切换到不同的已配置提供商 | `/model provider:model`（在会话内） |
:::

#### API 密钥无法使用 {#api-key-not-working}

**原因：** 密钥缺失、已过期、设置不正确，或者不属于当前提供商。

**解决方法：**
```bash
# 查看配置
hermes config show

# 重新配置提供商
hermes model

# 或者直接设置
hermes config set OPENROUTER_API_KEY sk-or-v1-xxxxxxxxxxxx
```
:::warning
确保密钥与提供商匹配。OpenAI 的密钥无法用于 OpenRouter，反之亦然。检查 `~/.hermes/.env` 中是否有冲突的条目。
:::

#### 模型不可用 / 找不到模型 {#model-not-available-model-not-found}

**原因：** 模型标识符不正确，或你的提供商不提供该模型。

**解决方法：**
```bash
# 列出提供商可用的模型
hermes model

# 设置一个有效的模型
hermes config set HERMES_MODEL anthropic/claude-opus-4.7

# 或在单次会话中指定
hermes chat --model openrouter/meta-llama/llama-3.1-70b-instruct
```

#### 速率限制（429 错误） {#rate-limiting-429-errors}

**原因：** 你已超出提供商的速率限制。

**解决方法：** 稍等片刻后重试。如果需要持续使用，可以考虑：
- 升级你的提供商套餐
- 切换到其他模型或提供商
- 使用 `hermes chat --provider &lt;alternative&gt;` 路由到不同的后端

#### 超出上下文长度 {#context-length-exceeded}

**原因：** 对话内容过长，超出了模型的上下文窗口；或者 Hermes 检测到的上下文长度有误。

**解决方法：**
```bash
# 压缩当前会话
/compress

# 或开启一个新会话
hermes chat

# 使用上下文窗口更大的模型
hermes chat --model openrouter/google/gemini-3-flash-preview
```

如果这是第一次长对话就出现该问题，可能是 Hermes 检测到的上下文长度有误。查看它检测到的结果：

留意 CLI 启动时的输出行——它会显示检测到的上下文长度（例如 `📊 Context limit: 128000 tokens`）。你也可以在会话中使用 `/usage` 查看。

要修复上下文检测问题，可以显式设置：

```yaml
# 在 ~/.hermes/config.yaml 中
model:
  default: your-model-name
  context_length: 131072  # 你模型的实际上下文窗口大小
```

或者针对自定义端点，按模型添加：

```yaml
custom_providers:
  - name: "My Server"
    base_url: "http://localhost:11434/v1"
    models:
      qwen3.5:27b:
        context_length: 32768
```

关于自动检测的工作原理和所有覆盖选项，参见 [上下文长度检测](../integrations/providers.md#context-length-detection)。

---

### 终端问题 {#terminal-issues}

#### 命令被拦截，标记为危险操作 {#command-blocked-as-dangerous}

**原因：** Hermes 检测到一个可能具有破坏性的命令（例如 `rm -rf`、`DROP TABLE`）。这是一项安全功能。

**解决方法：** 出现提示时，仔细审查命令并输入 `y` 确认执行。你也可以：
- 让 Agent 使用更安全的替代方案
- 在 [安全文档](../user-guide/security.md) 中查看完整的危险模式列表

:::tip
这是预期行为——Hermes 绝不会静默执行破坏性命令。确认提示会准确展示将要执行的内容。
:::

#### 通过消息网关无法使用 `sudo` {#sudo-not-working-via-messaging-gateway}

**原因：** 消息网关运行在没有交互式终端的环境中，因此 `sudo` 无法提示输入密码。

**解决方法：**
- 在消息场景中避免使用 `sudo`——让 Agent 寻找替代方案
- 如果必须使用 `sudo`，在 `/etc/sudoers` 中为特定命令配置免密码 sudo
- 或者切换到终端界面执行管理任务：`hermes chat`

#### Docker 后端无法连接 {#docker-backend-not-connecting}

**原因：** Docker 守护进程未运行，或当前用户没有权限。

**解决方法：**
```bash
# 检查 Docker 是否运行
docker info

# 将用户添加到 docker 组
sudo usermod -aG docker $USER
newgrp docker

# 验证
docker run hello-world
```

---

### 消息问题 {#messaging-issues}

#### 机器人不回复消息 {#bot-not-responding-to-messages}

**原因：** 机器人未运行、未授权，或你的用户不在白名单中。

**解决方法：**
```bash
# 检查网关是否运行
hermes gateway status

# 启动网关
hermes gateway start

# 查看日志中的错误
cat ~/.hermes/logs/gateway.log | tail -50
```

#### 消息发送失败 {#messages-not-delivering}

**原因：** 网络问题、机器人令牌过期，或平台 webhook 配置错误。

**解决方法：**
- 使用 `hermes gateway setup` 验证机器人令牌是否有效
- 检查网关日志：`cat ~/.hermes/logs/gateway.log | tail -50`
- 对于基于 webhook 的平台（Slack、WhatsApp），确保你的服务器可从公网访问

#### 白名单困惑——谁可以和机器人对话？ {#allowlist-confusion-who-can-talk-to-the-bot}
**原因：** 授权模式决定了谁能访问。

**解决方案：**

| 模式 | 工作原理 |
|------|-------------|
| **Allowlist（白名单）** | 只有配置中列出的用户 ID 可以交互 |
| **DM 配对** | 第一个在私信中发消息的用户获得独占访问权 |
| **Open（开放）** | 任何人都可以交互（生产环境不推荐） |

在 `~/.hermes/config.yaml` 中对应 gateway 的设置下配置。详见 [Messaging 文档](../user-guide/messaging/index.md)。

#### Gateway 无法启动 {#gateway-won-t-start}

**原因：** 缺少依赖、端口冲突或 token 配置错误。

**解决方案：**
```bash
# 安装消息相关依赖
pip install "hermes-agent[telegram]"   # 或 [discord]、[slack]、[whatsapp]

# 检查端口冲突
lsof -i :8080

# 验证配置
hermes config show
```

#### WSL：Gateway 不断断开连接，或 `hermes gateway start` 失败 {#wsl-gateway-keeps-disconnecting-or-hermes-gateway-start-fails}

**原因：** WSL 的 systemd 支持不够稳定。很多 WSL2 安装默认没有启用 systemd，即使启用了，服务也可能在 WSL 重启或 Windows 空闲关机后无法存活。

**解决方案：** 使用前台模式，而不是 systemd 服务：

```bash
# 方案 1：直接前台运行（最简单）
hermes gateway run

# 方案 2：通过 tmux 持久化（关闭终端后仍可运行）
tmux new -s hermes 'hermes gateway run'
# 之后重新连接：tmux attach -t hermes

# 方案 3：通过 nohup 后台运行
nohup hermes gateway run > ~/.hermes/logs/gateway.log 2>&1 &
```

如果你还是想尝试 systemd，先确保已启用：

1. 打开 `/etc/wsl.conf`（不存在则创建）
2. 添加：
   ```ini
   [boot]
   systemd=true
   ```
3. 在 PowerShell 中执行：`wsl --shutdown`
4. 重新打开 WSL 终端
5. 验证：`systemctl is-system-running` 应返回 "running" 或 "degraded"

<a id="auto-start-on-windows-boot"></a>
:::tip Windows 开机自动启动
想要稳定地自动启动，可以用 Windows 任务计划程序在登录时启动 WSL + gateway：
1. 创建一个任务，运行 `wsl -d Ubuntu -- bash -lc 'hermes gateway run'`
2. 设置触发器为"用户登录时"
:::

<a id="macos-node-js-ffmpeg-other-tools-not-found-by-gateway"></a>
#### macOS：Gateway 找不到 Node.js / ffmpeg / 其他工具 {#auto-start-on-windows-boot}

**原因：** launchd 服务继承的 PATH 很精简（`/usr/bin:/bin:/usr/sbin:/sbin`），不包含 Homebrew、nvm、cargo 或其他用户安装的工具目录。这通常会导致 WhatsApp 桥接失败（`node not found`）或语音转录失败（`ffmpeg not found`）。

**解决方案：** 运行 `hermes gateway install` 时，gateway 会捕获你当前的 shell PATH。如果你是先装好了 gateway、后来又安装的这些工具，重新执行 install 来捕获更新后的 PATH：

```bash
hermes gateway install    # 重新快照你当前的 PATH
hermes gateway start      # 检测到更新的 plist 并重新加载
```

你可以验证 plist 中的 PATH 是否正确：
```bash
/usr/libexec/PlistBuddy -c "Print :EnvironmentVariables:PATH" \
  ~/Library/LaunchAgents/ai.hermes.gateway.plist
```

---

### 性能问题 {#performance-issues}

#### 响应慢 {#slow-responses}

**原因：** 模型太大、API 服务器太远，或者系统提示词过长、工具太多。

**解决方案：**
- 尝试更快/更小的模型：`hermes chat --model openrouter/meta-llama/llama-3.1-8b-instruct`
- 减少活跃工具集：`hermes chat -t "terminal"`
- 检查到服务商的网络延迟
- 本地模型的话，确保 GPU 显存充足

#### Token 消耗高 {#high-token-usage}

**原因：** 对话过长、系统提示词冗长，或大量工具调用累积了上下文。

**解决方案：**
```bash
# 压缩对话以减少 token
/compress

# 查看当前 session 的 token 使用情况
/usage
```

:::tip
长会话期间定期使用 `/compress`。它会总结对话历史，显著减少 token 消耗，同时保留关键上下文。
:::

#### Session 过长 {#session-getting-too-long}

**原因：** 长时间对话累积了大量消息和工具输出，接近上下文上限。

**解决方案：**
```bash
# 压缩当前 session（保留关键上下文）
/compress

# 开启新 session，并引用旧 session
hermes chat

# 之后如需恢复特定 session
hermes chat --continue
```

---

### MCP 问题 {#mcp-issues}

#### MCP server 无法连接 {#mcp-server-not-connecting}
**原因：** 服务端二进制文件未找到、命令路径错误，或缺少运行时。

**解决方法：**
```bash
# 确保 MCP 依赖已安装（标准安装中已包含）
cd ~/.hermes/hermes-agent && uv pip install -e ".[mcp]"

# 对于基于 npm 的服务端，确保 Node.js 可用
node --version
npx --version

# 手动测试服务端
npx -y @modelcontextprotocol/server-filesystem /tmp
```

验证你的 `~/.hermes/config.yaml` MCP 配置：
```yaml
mcp_servers:
  filesystem:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/docs"]
```

#### MCP 服务端的工具未显示 {#tools-not-showing-up-from-mcp-server}

**原因：** 服务端已启动但工具发现失败、工具被配置过滤掉，或者服务端不支持你预期的 MCP 能力。

**解决方法：**
- 检查 gateway/agent 日志中的 MCP 连接错误
- 确保服务端响应 `tools/list` RPC 方法
- 检查该服务端下的 `tools.include`、`tools.exclude`、`tools.resources`、`tools.prompts` 或 `enabled` 设置
- 注意资源/提示工具只有在会话实际支持这些能力时才会注册
- 配置更改后使用 `/reload-mcp`

```bash
# 验证 MCP 服务端是否已配置
hermes config show | grep -A 12 mcp_servers

# 配置更改后重启 Hermes 或重新加载 MCP
hermes chat
```

另请参阅：
- [MCP (Model Context Protocol)](/user-guide/features/mcp)
- [Use MCP with Hermes](/guides/use-mcp-with-hermes)
- [MCP Config Reference](/reference/mcp-config-reference)

#### MCP 超时错误 {#mcp-timeout-errors}

**原因：** MCP 服务端响应时间过长，或在执行期间崩溃。

**解决方法：**
- 如果 MCP 服务端配置支持，增加超时时间
- 检查 MCP 服务端进程是否仍在运行
- 对于远程 HTTP MCP 服务端，检查网络连接

:::warning
如果 MCP 服务端在请求中途崩溃，Hermes 会报告超时。请检查服务端自身的日志（不只是 Hermes 日志）来诊断根本原因。
:::

---

## Profiles {#profiles}

### Profile 和直接设置 HERMES_HOME 有什么区别？ {#how-do-profiles-differ-from-just-setting-hermeshome}

Profile 是在 `HERMES_HOME` 之上的一层托管机制。你*可以*在每次命令前手动设置 `HERMES_HOME=/some/path`，但 Profile 会帮你处理所有繁琐工作：创建目录结构、生成 shell 别名（`hermes-work`）、在 `~/.hermes/active_profile` 中跟踪当前激活的 Profile，以及自动同步所有 Profile 的技能更新。它们还与 Tab 补全集成，这样你就不用记路径了。

### 两个 Profile 可以共用同一个 bot token 吗？ {#can-two-profiles-share-the-same-bot-token}

不可以。每个消息平台（Telegram、Discord 等）都需要独占访问一个 bot token。如果两个 Profile 同时尝试使用同一个 token，第二个 gateway 将无法连接。每个 Profile 创建一个单独的 bot —— 对于 Telegram，找 [@BotFather](https://t.me/BotFather) 创建额外的 bot。

### Profile 之间共享记忆或会话吗？ {#do-profiles-share-memory-or-sessions}

不共享。每个 Profile 有自己的记忆存储、会话数据库和技能目录。它们完全隔离。如果你想用现有记忆和会话创建新 Profile，使用 `hermes profile create newname --clone-all` 从当前 Profile 复制所有内容。

### 运行 `hermes update` 会发生什么？ {#what-happens-when-i-run-hermes-update}

`hermes update` 会拉取最新代码并**一次性**重新安装依赖（不是每个 Profile 单独安装）。然后它会自动将更新后的技能同步到所有 Profile。你只需要运行一次 `hermes update` —— 它会覆盖机器上的所有 Profile。

### 可以把 Profile 移到另一台机器吗？ {#can-i-move-a-profile-to-a-different-machine}

可以。将 Profile 导出为可移植的归档文件，然后在另一台机器上导入：

```bash
# 在源机器上
hermes profile export work ./work-backup.tar.gz

# 将文件复制到目标机器，然后执行：
hermes profile import ./work-backup.tar.gz work
```

导入的 Profile 会包含导出时的所有配置、记忆、会话和技能。如果新机器的 setup 不同，你可能需要更新路径或重新向 provider 认证。
### 最多能运行多少个 profile？ {#how-many-profiles-can-i-run}

没有硬性上限。每个 profile 只是 `~/.hermes/profiles/` 下的一个目录。实际限制取决于你的磁盘空间以及系统能承载多少个并发 gateway（每个 gateway 都是一个轻量级 Python 进程）。运行几十个 profile 完全没问题；空闲的 profile 不占用任何资源。

---

## 工作流与模式 {#workflows-patterns}

### 不同任务使用不同模型（多模型工作流） {#using-different-models-for-different-tasks-multi-model-workflows}

**场景：** 你平时用 GPT-5.4，但 Gemini 或 Grok 写社交媒体内容更拿手。每次都手动切换模型太麻烦了。

**解决方案：delegation 配置。** Hermes 可以自动把 subagent 路由到别的模型。在 `~/.hermes/config.yaml` 里这样设置：

```yaml
delegation:
  model: "google/gemini-3-flash-preview"   # subagent 使用这个模型
  provider: "openrouter"                    # subagent 的 provider
```

现在当你让 Hermes "write me a Twitter thread about X"，它会启动一个 `delegate_task` subagent，这个 subagent 就会跑在 Gemini 上，而不是你的主模型。你的主对话仍然留在 GPT-5.4。

你也可以在 prompt 里明确说明：*"Delegate a task to write social media posts about our product launch. Use your subagent for the actual writing."* Agent 会调用 `delegate_task`，自动读取 delegation 配置。

如果只是想临时切换模型、不用 delegation，可以在 CLI 里用 `/model`：

```bash
/model google/gemini-3-flash-preview    # 本次会话切换
# ... 写你的内容 ...
/model openai/gpt-5.4                   # 切回来
```

更多 delegation 机制详见 [Subagent Delegation](../user-guide/features/delegation.md)。

### 一个 WhatsApp 号码跑多个 Agent（按聊天绑定） {#running-multiple-agents-on-one-whatsapp-number-per-chat-binding}

**场景：** 在 OpenClaw 里，你可以把多个独立的 Agent 绑定到特定的 WhatsApp 聊天——一个用于家庭购物清单群，另一个用于私聊。Hermes 能做到吗？

**当前限制：** Hermes 的每个 profile 都需要独立的 WhatsApp 号码/会话。你无法把多个 profile 绑定到同一个 WhatsApp 号码的不同聊天上——WhatsApp bridge（Baileys）每个号码只用一个认证会话。

**变通方案：**

1. **单 profile + 人格切换。** 创建不同的 `AGENTS.md` 上下文文件，或者用 `/personality` 命令按聊天切换行为。Agent 能感知自己在哪个聊天里，并做出相应调整。

2. **用 cron job 处理专项任务。** 比如购物清单追踪，可以设一个 cron job 监控特定聊天并管理清单——不需要单独的 Agent。

3. **用独立的号码。** 如果你需要真正独立的 Agent，就给每个 profile 配一个独立的 WhatsApp 号码。Google Voice 等服务的虚拟号码就能用。

4. **改用 Telegram 或 Discord。** 这些平台更自然地支持按聊天绑定——每个 Telegram 群组或 Discord 频道都有独立的会话，而且你可以在同一账号下跑多个 bot token（每个 profile 一个）。

更多详情见 [Profiles](../user-guide/profiles.md) 和 [WhatsApp 设置](../user-guide/messaging/whatsapp.md)。

### 控制 Telegram 里显示什么（隐藏日志和推理过程） {#controlling-what-shows-up-in-telegram-hiding-logs-and-reasoning}

**场景：** 你在 Telegram 里看到了 gateway 执行日志、Hermes 的推理过程、工具调用详情，而不仅仅是最终输出。

**解决方案：** `config.yaml` 里的 `display.tool_progress` 设置控制显示多少工具活动：

```yaml
display:
  tool_progress: "off"   # 可选：off, new, all, verbose
```

- **`off`** — 只显示最终回复。不显示工具调用、推理过程、日志。
- **`new`** — 新工具调用发生时显示（简短的一行摘要）。
- **`all`** — 显示所有工具活动，包括结果。
- **`verbose`** — 完整细节，包括工具参数和输出。

对于消息平台，通常用 `off` 或 `new` 就够了。修改 `config.yaml` 后，重启 gateway 生效。

如果启用了，也可以用 `/verbose` 命令按会话切换：
```yaml
display:
  tool_progress_command: true   # enables /verbose in the gateway
```

### 在 Telegram 上管理技能（斜杠命令数量限制） {#managing-skills-on-telegram-slash-command-limit}

**场景：** Telegram 有 100 个斜杠命令的上限，而你的技能数量快要超出这个限制了。你想在 Telegram 上禁用一些不需要的技能，但 `hermes skills config` 的设置似乎没有生效。

**解决方案：** 使用 `hermes skills config` 按平台禁用技能。这会写入 `config.yaml`：

```yaml
skills:
  disabled: []                    # 全局禁用的技能
  platform_disabled:
    telegram: [skill-a, skill-b]  # 仅在 telegram 上禁用
```

修改后，**重启 gateway**（`hermes gateway restart` 或杀掉进程重新启动）。Telegram 机器人的命令菜单会在启动时重新构建。

:::tip
描述过长的技能在 Telegram 菜单中会被截断到 40 个字符，以控制 payload 大小。如果技能没有显示出来，可能是总 payload 大小的问题，而不一定是 100 个命令的数量限制——禁用不用的技能对两者都有帮助。
:::

### 共享线程会话（多用户，一个对话） {#shared-thread-sessions-multiple-users-one-conversation}

**场景：** 你有一个 Telegram 或 Discord 线程，里面有多个人 @ 了机器人。你希望这个线程里的所有 @ 都归入同一个共享对话，而不是每个人各自独立的会话。

**当前行为：** Hermes 在大多数平台上按用户 ID 创建会话，所以每个人都有自己的对话上下文。这是出于隐私和上下文隔离的考虑而设计的。

**变通方案：**

1. **使用 Slack。** Slack 的会话按线程划分，而不是按用户。同一线程里的多个用户共享一个对话——这正是你想要的行为。这是最自然的选择。

2. **用群聊指定一个操作人。** 如果一个人是指定的"操作员"，负责转述问题，会话就能保持统一。其他人可以旁观。

3. **使用 Discord 频道。** Discord 的会话按频道划分，所以同频道里的所有用户共享上下文。用一个专用频道来进行共享对话。

### 将 Hermes 迁移到另一台机器 {#exporting-hermes-to-another-machine}

**场景：** 你在一台机器上积累了很多技能、cron 任务和记忆，现在想把所有东西搬到一台新的专用 Linux 机器上。

**解决方案：**

1. 在新机器上安装 Hermes Agent：
   ```bash
   curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
   ```

2. 复制整个 `~/.hermes/` 目录，**但要排除** `hermes-agent` 子目录（那是代码仓库——新安装已经有了自己的）：
   ```bash
   # 在源机器上
   rsync -av --exclude='hermes-agent' ~/.hermes/ newmachine:~/.hermes/
   ```

   或者使用 profile 导出/导入：
   ```bash
   # 在源机器上
   hermes profile export default ./hermes-backup.tar.gz

   # 在目标机器上
   hermes profile import ./hermes-backup.tar.gz default
   ```

3. 在新机器上运行 `hermes setup`，检查 API key 和 provider 配置是否正常。重新认证所有消息平台（特别是 WhatsApp，它需要用二维码配对）。

`~/.hermes/` 目录包含所有内容：`config.yaml`、`.env`、`SOUL.md`、`memories/`、`skills/`、`state.db`（会话）、`cron/`，以及任何自定义插件。代码本身放在 `~/.hermes/hermes-agent/` 里，会重新安装一份新的。

### 安装后重新加载 shell 时报权限拒绝 {#permission-denied-when-reloading-shell-after-install}

**场景：** 运行 Hermes 安装程序后，执行 `source ~/.zshrc` 报权限拒绝错误。

**原因：** 这通常是因为 `~/.zshrc`（或 `~/.bashrc`）的文件权限不正确，或者安装程序没能正常写入。这不是 Hermes 特有的问题——是 shell 配置文件的权限问题。

**解决方案：**
```bash
# 检查权限
ls -la ~/.zshrc

# 如有需要则修复（应该是 -rw-r--r-- 或 644）
chmod 644 ~/.zshrc

# 然后重新加载
source ~/.zshrc

# 或者直接新开一个终端窗口——PATH 变更会自动生效
```

如果安装程序已经添加了 PATH 行但权限不对，你可以手动添加：
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
```
### 首次运行 Agent 时报错 400 {#error-400-on-first-agent-run}

**场景：** 安装一切正常，但第一次聊天尝试就报 HTTP 400 错误。

**原因：** 通常是模型名称不匹配——配置的模型在服务商那里不存在，或者 API key 没有该模型的访问权限。

**解决办法：**
```bash
# 查看当前配置的模型和服务商
hermes config show | head -20

# 重新选择模型
hermes model

# 或者用一个已知可用的模型测试
hermes chat -q "hello" --model anthropic/claude-opus-4.7
```

如果用 OpenRouter，先确认你的 API key 有余额。OpenRouter 返回 400 通常意味着该模型需要付费套餐，或者模型 ID 拼写有误。

---

## 还是没解决？ {#still-stuck}

如果这里没覆盖到你的问题：

1. **搜索已有 issue：** [GitHub Issues](https://github.com/NousResearch/hermes-agent/issues)
2. **向社区求助：** [Nous Research Discord](https://discord.gg/nousresearch)
3. **提交 bug 报告：** 请附上你的操作系统、Python 版本（`python3 --version`）、Hermes 版本（`hermes --version`）以及完整的错误信息
