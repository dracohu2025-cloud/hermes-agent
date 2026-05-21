---
sidebar_position: 3
title: "常见问题与故障排除"
description: "关于 Hermes Agent 的常见问题及常见问题的解决方案"
---

<a id="faq-troubleshooting"></a>
# 常见问题与故障排除

最常见问题和情况的快速解答与修复。

---

<a id="frequently-asked-questions"></a>
## 常见问题

<a id="what-llm-providers-work-with-hermes"></a>
### Hermes 支持哪些 LLM 提供商？

Hermes Agent 可与任何兼容 OpenAI 的 API 配合使用。支持的提供商包括：

- **[OpenRouter](https://openrouter.ai/)** — 通过一个 API 密钥访问数百个模型（推荐用于灵活性）
- **Nous Portal** — Nous Research 自己的推理端点
- **OpenAI** — GPT-5.4、GPT-5-codex、GPT-4.1、GPT-4o 等
- **Anthropic** — Claude 模型（直接 API，通过 `hermes login anthropic` 的 OAuth，OpenRouter，或任何兼容的代理）
- **Google** — Gemini 模型（通过 `gemini` 提供商的直接 API，`google-gemini-cli` OAuth 提供商，OpenRouter，或兼容代理）
- **z.ai / 智谱AI** — GLM 模型
- **Kimi / 月之暗面** — Kimi 模型
- **MiniMax** — 全球和中国端点
- **本地模型** — 通过 [Ollama](https://ollama.com/)、[vLLM](https://docs.vllm.ai/)、[llama.cpp](https://github.com/ggerganov/llama.cpp)、[SGLang](https://github.com/sgl-project/sglang) 或任何兼容 OpenAI 的服务器

使用 `hermes model` 或编辑 `~/.hermes/.env` 来设置您的提供商。有关所有提供商密钥，请参阅[环境变量](./environment-variables.md)参考。

<a id="does-it-work-on-windows"></a>
### 它能在 Windows 上运行吗？

**不能原生运行。** Hermes Agent 需要类 Unix 环境。在 Windows 上，安装 [WSL2](https://learn.microsoft.com/en-us/windows/wsl/install) 并在其中运行 Hermes。标准安装命令在 WSL2 中完美运行：
```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

<a id="i-run-hermes-in-wsl2-what-s-the-best-way-to-control-my-normal-windows-chrome"></a>
### 我在WSL2中运行Hermes。控制常规Windows版Chrome的最佳方式是什么？

推荐通过MCP桥接代替`/browser connect`。

推荐模式：

- 在WSL2内运行Hermes
- 继续使用Windows上已登录的常规Chrome
- 通过`cmd.exe`或`powershell.exe`添加`chrome-devtools-mcp`作为MCP服务器
- 让Hermes使用由此产生的MCP浏览器工具

这比试图强制Hermes核心浏览器传输直接跨WSL2/Windows边界进行附加更可靠。

参见：

- [在Hermes中使用MCP](../guides/use-mcp-with-hermes.md#wsl2-bridge-hermes-in-wsl-to-windows-chrome)
- [浏览器自动化](../user-guide/features/browser.md#wsl2--windows-chrome-prefer-mcp-over-browser-connect)

<a id="does-it-work-on-android-termux"></a>
### 它能在Android / Termux上运行吗？

可以——Hermes现在有一个经过测试的Android手机Termux安装路径。

快速安装：

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

如需完整明确的步骤、支持的附加功能以及当前限制，请参阅[Termux指南](../getting-started/termux.md)。

重要警告：完整的`.[all]`附加功能目前无法在Android上使用，因为`voice`附加功能依赖`faster-whisper` → `ctranslate2`，而`ctranslate2`没有发布Android wheel包。请改用经过测试的`.[termux]`附加功能。

<a id="is-my-data-sent-anywhere"></a>
### 我的数据会被发送到其他地方吗？

API调用**只会**发送到你配置的LLM提供商（例如OpenRouter、本地的Ollama实例）。Hermes Agent不收集遥测、使用数据或分析信息。你的对话、记忆和技能存储在本地`~/.hermes/`目录中。
<a id="can-i-use-it-offline-with-local-models"></a>
### 可以离线使用 / 搭配本地模型吗？

可以。运行 `hermes model`，选择 **Custom endpoint**，然后输入你的服务器地址：

```bash
hermes model
# 选择: Custom endpoint (enter URL manually)
# API base URL: http://localhost:11434/v1
# API key: ollama
# Model name: qwen3.5:27b
# Context length: 32768   ← 设为与你服务器实际上下文窗口一致的值
```

也可以直接在 `config.yaml` 中配置：

```yaml
model:
  default: qwen3.5:27b
  provider: custom
  base_url: http://localhost:11434/v1
```

Hermes 会将 endpoint、provider 和 base_url 持久化到 `config.yaml` 中，重启后仍然生效。如果你的本地服务器正好只加载了一个模型，`/model custom` 会自动检测到它。你也可以直接在 config.yaml 中设置 `provider: custom`——这是一个一等公民级的 provider，而不是其他任何 provider 的别名。

这适用于 Ollama、vLLM、llama.cpp server、SGLang、LocalAI 等。详情请参见 [配置指南](../user-guide/configuration.md)。

<a id="ollama-users"></a>
:::tip Ollama 用户
如果你在 Ollama 中设置了自定义的 `num_ctx`（例如 `ollama run --num_ctx 16384`），请确保在 Hermes 中设置对应的上下文长度——Ollama 的 `/api/show` 报告的是模型的*最大*上下文，而不是你实际配置的有效 `num_ctx`。
:::

<a id="timeouts-with-local-models"></a>
:::tip 本地模型超时
Hermes 会自动检测本地端点并放宽流式超时（读取超时从 120s 提高到 1800s，并禁用过期流检测）。如果你在超长上下文上仍然遇到超时，可以在 `.env` 中设置 `HERMES_STREAM_READ_TIMEOUT=1800`。详情请参见 [本地 LLM 指南](../guides/local-llm-on-mac.md#timeouts)。
:::
<a id="how-much-does-it-cost"></a>
### 费用是多少？

Hermes Agent 本身是**免费且开源的**（MIT 许可证）。你只需为所选供应商的 LLM API 使用付费。本地模型则完全免费运行。

<a id="can-multiple-people-use-one-instance"></a>
### 多个人可以使用同一个实例吗？

可以。[消息网关](../user-guide/messaging/index.md) 允许多个用户通过 Telegram、Discord、Slack、WhatsApp 或 Home Assistant 与同一个 Hermes Agent 实例交互。访问权限通过允许列表（特定用户 ID）和 DM 配对（第一个发送消息的用户获得访问权限）来控制。

<a id="what-s-the-difference-between-memory-and-skills"></a>
### 记忆和技能有什么区别？

- **记忆**存储的是**事实**——Agent 了解的关于你、你的项目和偏好的信息。记忆会根据相关性自动检索。
- **技能**存储的是**流程**——完成某件事的逐步说明。当 Agent 遇到类似任务时会调用技能。

两者都会在多次会话中持久保留。详情请参阅[记忆](../user-guide/features/memory.md)和[技能](../user-guide/features/skills.md)。

<a id="can-i-use-it-in-my-own-python-project"></a>
### 我可以在自己的 Python 项目中使用它吗？

可以。导入 `AIAgent` 类并以编程方式使用 Hermes：

```python
from run_agent import AIAgent

agent = AIAgent(model="anthropic/claude-opus-4.7")
response = agent.chat("简要解释一下量子计算")
```

完整的 API 用法请参阅 [Python 库指南](../user-guide/features/code-execution.md)。

---

<a id="troubleshooting"></a>
## 故障排除

<a id="installation-issues"></a>
### 安装问题

<a id="hermes-command-not-found-after-installation"></a>
#### 安装后出现 `hermes: command not found`

**原因：** 你的 shell 尚未重新加载更新后的 PATH。
**解决方案：**
```bash
# 重新加载 shell 配置文件
source ~/.bashrc    # bash
source ~/.zshrc     # zsh

# 或者启动一个新的终端会话
```

如果仍然无效，请检查安装位置：
```bash
which hermes
ls ~/.local/bin/hermes
```

:::tip
安装程序已将 `~/.local/bin` 添加到 PATH 中。如果你使用的是非标准 shell 配置，请手动添加 `export PATH="$HOME/.local/bin:$PATH"`。
:::

<a id="python-version-too-old"></a>
#### Python 版本过低

**原因：** Hermes 需要 Python 3.11 或更新版本。

**解决方案：**
```bash
python3 --version   # 检查当前版本

# 安装较新版本的 Python
sudo apt install python3.12   # Ubuntu/Debian
brew install python@3.12      # macOS
```

安装程序会自动处理此问题——如果在手动安装过程中看到此错误，请先升级 Python。

<a id="terminal-commands-say-node-command-not-found-or-nvm-pyenv-asdf"></a>
#### 终端命令提示 `node: command not found`（或 `nvm`、`pyenv`、`asdf` 等）

**原因：** Hermes 会在启动时通过运行一次 `bash -l` 来构建会话环境快照。Bash 登录 shell 会读取 `/etc/profile`、`~/.bash_profile` 和 `~/.profile`，但**不会加载 `~/.bashrc`**——因此安装在这些文件中的工具（`nvm`、`asdf`、`pyenv`、`cargo`、自定义 `PATH` 导出）在快照中不可见。这种情况最常见于 Hermes 在 systemd 下或在一个没有任何预加载交互式 shell 配置文件的最小 shell 中运行时。

**解决方案：** 默认情况下，Hermes 会自动加载 `~/.bashrc`。如果这还不够——例如，你是 zsh 用户，你的 PATH 位于 `~/.zshrc` 中，或者你从独立文件初始化 `nvm`——请在 `~/.hermes/config.yaml` 中列出要加载的额外文件：
```yaml
terminal:
  shell_init_files:
    - ~/.zshrc                     # zsh 用户：将 zsh 管理的 PATH 引入 bash 快照
    - ~/.nvm/nvm.sh                # 直接初始化 nvm（无论使用何种 shell 均有效）
    - /etc/profile.d/cargo.sh      # 系统级 rc 文件
  # 设置此列表后，默认的 ~/.bashrc 自动加载将不会添加——
  # 若需要两者兼顾，请显式包含它：
  #   - ~/.bashrc
  #   - ~/.zshrc
```

缺失的文件会被静默跳过。加载过程在 bash 中执行，因此依赖 zsh 特有语法的文件可能会报错——如果担心这个问题，请只加载设置 PATH 的部分（例如直接加载 nvm 的 `nvm.sh`），而不是整个 rc 文件。

要禁用自动加载行为（仅使用严格的登录 shell 语义）：

```yaml
terminal:
  auto_source_bashrc: false
```

<a id="uv-command-not-found"></a>
#### `uv: command not found`

**原因：** `uv` 包管理器未安装或不在 PATH 中。

**解决方案：**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc
```

<a id="permission-denied-errors-during-install"></a>
#### 安装过程中出现权限被拒绝的错误

**原因：** 对安装目录的写入权限不足。

**解决方案：**
```bash
# 不要对安装程序使用 sudo —— 它会安装到 ~/.local/bin
# 如果你之前用 sudo 安装过，请清理：
sudo rm /usr/local/bin/hermes
# 然后重新运行标准安装程序
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

---

<a id="provider-model-issues"></a>
### Provider 与模型问题

<a id="model-only-shows-one-provider-can-t-switch-providers"></a>
#### `/model` 只显示一个 provider / 无法切换 provider
**原因：** `/model`（在聊天会话中）只能在你**已经配置好**的提供商之间切换。如果你只设置了 OpenRouter，那么 `/model` 只会显示这一个选项。

**解决方法：** 退出当前会话，在终端中使用 `hermes model` 来添加新的提供商：

```bash
# 先退出 Hermes 聊天会话（按 Ctrl+C 或输入 /quit）

# 运行完整的提供商设置向导
hermes model

# 这可以让你：添加提供商、运行 OAuth、输入 API 密钥、配置端点
```

通过 `hermes model` 添加新提供商后，重新开始一个新的聊天会话 — 此时 `/model` 会显示所有已配置的提供商。

:::tip 快速参考
| 想要... | 使用 |
<a id="quick-reference"></a>
|-----------|-----|
| 添加新提供商 | `hermes model`（在终端中） |
| 输入/更改 API 密钥 | `hermes model`（在终端中） |
| 在会话中切换模型 | `/model <名称>`（在会话中） |
| 切换到其他已配置的提供商 | `/model 提供商:模型`（在会话中） |
:::

<a id="api-key-not-working"></a>
#### API 密钥不工作

**原因：** 密钥缺失、已过期、设置错误，或者对应了错误的提供商。

**解决方法：**
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

<a id="model-not-available-model-not-found"></a>
#### 模型不可用 / 模型未找到

**原因：** 模型标识符不正确，或者你的提供商上不可用。
**解决方案：**
```bash
# 列出你当前提供商可用的模型
hermes model

# 设置一个有效的模型
hermes config set HERMES_MODEL anthropic/claude-opus-4.7

# 或按会话指定
hermes chat --model openrouter/meta-llama/llama-3.1-70b-instruct
```

<a id="rate-limiting-429-errors"></a>
#### 速率限制（429 错误）

**原因：** 超过了提供商的速率限制。

**解决方案：** 稍等片刻后重试。如果需要持续使用，可以考虑：
- 升级你的提供商套餐
- 切换到其他模型或提供商
- 使用 `hermes chat --provider <替代>` 将请求路由到不同的后端

<a id="context-length-exceeded"></a>
#### 上下文长度超限

**原因：** 对话长度超过了模型上下文窗口的限制，或者 Hermes 检测到的上下文长度与你使用的模型不匹配。

**解决方案：**
```bash
# 压缩当前会话
/compress

# 或开启一个新会话
hermes chat

# 使用上下文窗口更大的模型
hermes chat --model openrouter/google/gemini-3-flash-preview
```

如果这种情况在第一次长对话时就出现，可能是 Hermes 对该模型检测到的上下文长度有误。你可以检查它检测到的值：

查看 CLI 启动时的输出行——它会显示检测到的上下文长度（例如 `📊 Context limit: 128000 tokens`）。你也可以在会话期间通过 `/usage` 查看。

要修复上下文检测问题，可以手动设置：

```yaml
# 在 ~/.hermes/config.yaml 中
model:
  default: your-model-name
  context_length: 131072  # 模型的实际上下文窗口
```

或者针对自定义端点，按模型单独添加：

```yaml
custom_providers:
  - name: "My Server"
    base_url: "http://localhost:11434/v1"
    models:
      qwen3.5:27b:
        context_length: 32768
```
请参阅[上下文长度检测](../integrations/providers.md#context-length-detection)了解自动检测的工作原理以及所有覆盖选项。

---

<a id="terminal-issues"></a>
### 终端问题

<a id="command-blocked-as-dangerous"></a>
#### 命令被阻止为危险操作

**原因：** Hermes 检测到一条可能具有破坏性的命令（例如 `rm -rf`、`DROP TABLE`）。这是一项安全功能。

**解决方案：** 当被提示时，请审查该命令并输入 `y` 以批准。你也可以：
- 让 Agent 使用更安全的替代方案
- 在[安全文档](../user-guide/security.md)中查看危险模式的完整列表

:::tip
此为预期行为——Hermes 从不静默执行破坏性命令。审批提示会精确显示将要执行的内容。
:::

<a id="sudo-not-working-via-messaging-gateway"></a>
#### `sudo` 在消息网关中无法工作

**原因：** 消息网关在没有交互式终端的情况下运行，因此 `sudo` 无法提示输入密码。

**解决方案：**
- 在消息中避免使用 `sudo`——让 Agent 寻找替代方案
- 如果必须使用 `sudo`，可在 `/etc/sudoers` 中为特定命令配置无密码 sudo
- 或者切换到终端界面执行管理任务：`hermes chat`

<a id="docker-backend-not-connecting"></a>
#### Docker 后端无法连接

**原因：** Docker 守护进程未运行，或当前用户缺少权限。

**解决方案：**
```bash
# 检查 Docker 是否运行
docker info

# 将你的用户添加到 docker 组
sudo usermod -aG docker $USER
newgrp docker

# 验证
docker run hello-world
```

---

<a id="messaging-issues"></a>
### 消息问题

<a id="bot-not-responding-to-messages"></a>
#### 机器人未响应消息

**原因：** 机器人未运行、未获得授权，或者你的用户不在允许列表中。
**解决方案：**
```bash
# 检查网关是否运行
hermes gateway status

# 启动网关
hermes gateway start

# 查看日志排查错误
cat ~/.hermes/logs/gateway.log | tail -50
```

<a id="messages-not-delivering"></a>
#### 消息无法送达

**原因：** 网络问题、机器人令牌过期或平台 webhook 配置有误。

**解决方案：**
- 使用 `hermes gateway setup` 验证机器人令牌是否有效
- 查看网关日志：`cat ~/.hermes/logs/gateway.log | tail -50`
- 对于基于 webhook 的平台（Slack、WhatsApp），确保服务器可正常从公网访问

<a id="allowlist-confusion-who-can-talk-to-the-bot"></a>
#### 授权列表（Allowlist）困惑——谁可以和机器人对话？

**原因：** 授权模式决定了哪些用户有权访问。

**解决方案：**

| 模式 | 工作方式 |
|------|----------|
| **Allowlist（白名单）** | 只有配置文件中列出的用户 ID 可以交互 |
| **DM pairing（私聊配对）** | 第一个通过私信发消息的用户获得独占访问权 |
| **Open（开放）** | 任何人都可以交互（不建议生产环境使用） |

在 `~/.hermes/config.yaml` 中对应网关的设置下进行配置。参见[消息文档](../user-guide/messaging/index.md)。

<a id="gateway-won-t-start"></a>
#### 网关无法启动

**原因：** 缺少依赖、端口冲突或令牌配置有误。

**解决方案：**
```bash
# 安装核心消息网关依赖
pip install "hermes-agent[messaging]"  # Telegram、Discord、Slack 及共享网关依赖

# 检查端口冲突
lsof -i :8080

# 验证配置
hermes config show
```

<a id="wsl-gateway-keeps-disconnecting-or-hermes-gateway-start-fails"></a>
#### WSL：网关频繁断开连接或 `hermes gateway start` 启动失败

**原因：** WSL 的 systemd 支持并不可靠。许多 WSL2 安装并未启用 systemd，即便启用了，服务也可能在 WSL 重启或 Windows 空闲关机后无法保持运行。
**解决方案：** 改用前台模式而非 systemd 服务：

```bash
# 选项1：直接前台运行（最简单）
hermes gateway run

# 选项2：通过 tmux 持久化（关闭终端后仍在运行）
tmux new -s hermes 'hermes gateway run'
# 重新连接：tmux attach -t hermes

# 选项3：通过 nohup 后台运行
nohup hermes gateway run > ~/.hermes/logs/gateway.log 2>&1 &
```

如果仍想尝试 systemd，请确保已启用：

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
<a id="auto-start-on-windows-boot"></a>
如需可靠的自启动，可使用 Windows 任务计划程序在登录时启动 WSL 和 gateway：
1. 创建一个任务，运行 `wsl -d Ubuntu -- bash -lc 'hermes gateway run'`
2. 将触发器设为用户登录时
:::

<a id="macos-node-js-ffmpeg-other-tools-not-found-by-gateway"></a>
#### macOS：Gateway 找不到 Node.js / ffmpeg / 其他工具

**原因：** launchd 服务继承了一个极简的 PATH（`/usr/bin:/bin:/usr/sbin:/sbin`），其中不包含 Homebrew、nvm、cargo 或其他用户安装的工具目录。这通常会导致 WhatsApp 桥接失败（`node not found`）或语音转文字失败（`ffmpeg not found`）。

**解决方案：** 当你运行 `hermes gateway install` 时，gateway 会捕获你的 shell PATH。如果在设置 gateway 后又安装了新工具，请重新运行 install 以捕获更新后的 PATH：

```bash
hermes gateway install    # 重新快照当前 PATH
hermes gateway start      # 检测到更新的 plist 并重新加载
```
你可以验证 plist 是否具有正确的 PATH：
```bash
/usr/libexec/PlistBuddy -c "Print :EnvironmentVariables:PATH" \
  ~/Library/LaunchAgents/ai.hermes.gateway.plist
```

---

<a id="performance-issues"></a>
### 性能问题

<a id="slow-responses"></a>
#### 响应缓慢

**原因：** 模型过大、API 服务器距离远，或系统提示词过于冗长且包含大量工具。

**解决方案：**
- 尝试更快/更小的模型：`hermes chat --model openrouter/meta-llama/llama-3.1-8b-instruct`
- 减少启用的工具集：`hermes chat -t "terminal"`
- 检查到提供商的网络延迟
- 如果是本地模型，请确保有足够的 GPU VRAM

<a id="high-token-usage"></a>
#### 令牌用量过高

**原因：** 对话较长、系统提示词详细，或者工具调用过多导致上下文累积。

**解决方案：**
```bash
# 压缩对话以减少令牌
/compress

# 检查会话令牌用量
/usage
```

:::tip
在长时间会话中定期使用 `/compress`。它会总结对话历史，显著减少令牌用量，同时保留上下文。
:::

<a id="session-getting-too-long"></a>
#### 会话过长

**原因：** 长时间对话会累积大量消息和工具输出，接近上下文限制。

**解决方案：**
```bash
# 压缩当前会话（保留关键上下文）
/compress

# 启动新会话，并引用旧会话
hermes chat

# 如果需要，稍后可恢复特定会话
hermes chat --continue
```

---

<a id="mcp-issues"></a>
### MCP 问题

<a id="mcp-server-not-connecting"></a>
#### MCP 服务器无法连接

**原因：** 未找到服务器二进制文件、命令路径错误或缺少运行时。

**解决方案：**
```bash
# 确保 MCP 依赖已安装（标准安装已包含）
cd ~/.hermes/hermes-agent && uv pip install -e ".[mcp]"

# 对于基于 npm 的服务器，请确保 Node.js 可用
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

<a id="tools-not-showing-up-from-mcp-server"></a>
#### MCP 服务器的工具未显示

**原因：** 服务器已启动但工具发现失败、工具被配置过滤，或者该服务器不支持你预期的 MCP 能力。

**解决方案：**
- 检查 gateway/Agent 日志中的 MCP 连接错误
- 确保服务器响应 `tools/list` RPC 方法
- 检查该服务器下的 `tools.include`、`tools.exclude`、`tools.resources`、`tools.prompts` 或 `enabled` 设置
- 注意：resource/prompt 实用工具只有在会话实际支持这些能力时才会注册
- 修改配置后使用 `/reload-mcp` 重新加载

```bash
# 验证 MCP 服务器是否已配置
hermes config show | grep -A 12 mcp_servers

# 更改配置后重启 Hermes 或重新加载 MCP
hermes chat
```

另请参阅：
- [MCP（模型上下文协议）](/user-guide/features/mcp)
- [将 MCP 与 Hermes 配合使用](/guides/use-mcp-with-hermes)
- [MCP 配置参考](/reference/mcp-config-reference)

<a id="mcp-timeout-errors"></a>
#### MCP 超时错误

**原因：** MCP 服务器响应时间过长，或在执行过程中崩溃。

**解决方案：**
- 如果支持，增加 MCP 服务器配置中的超时时间
- 检查 MCP 服务器进程是否仍在运行
- 对于远程 HTTP MCP 服务器，检查网络连接

:::warning
如果 MCP 服务器在请求途中崩溃，Hermes 会报告超时。请检查服务器自身的日志（而不仅仅是 Hermes 日志）来诊断根因。
:::
---

<a id="profiles"></a>
## 配置文件

<a id="how-do-profiles-differ-from-just-setting-hermeshome"></a>
### 配置文件与直接设置 HERMES_HOME 有何不同？

配置文件是构建在 `HERMES_HOME` 之上的一层管理机制。你*可以*在每次执行命令前手动设置 `HERMES_HOME=/some/path`，但配置文件会替你处理所有底层工作：创建目录结构、生成 shell 别名（`hermes-work`）、在 `~/.hermes/active_profile` 中追踪当前激活的配置文件，以及自动在所有配置文件间同步技能更新。配置文件还能与 Tab 补全功能集成，这样你就不必记住路径了。

<a id="can-two-profiles-share-the-same-bot-token"></a>
### 两个配置文件可以共用同一个机器人令牌吗？

不可以。每个消息平台（Telegram、Discord 等）都要求对机器人令牌拥有独占访问权。如果两个配置文件试图同时使用同一个令牌，第二个网关将无法连接。请为每个配置文件创建独立的机器人——对于 Telegram，可以联系 [@BotFather](https://t.me/BotFather) 创建更多机器人。

<a id="do-profiles-share-memory-or-sessions"></a>
### 配置文件之间会共享记忆或会话吗？

不会。每个配置文件拥有独立的记忆存储、会话数据库和技能目录。它们是完全隔离的。如果你想用已有的记忆和会话启动一个新配置文件，可以使用 `hermes profile create newname --clone-all` 从当前配置文件复制所有内容。

<a id="what-happens-when-i-run-hermes-update"></a>
### 运行 `hermes update` 时会发生什么？

`hermes update` 会拉取最新代码并**一次性**（而非按配置文件）重新安装依赖。然后它会自动将更新后的技能同步到所有配置文件。你只需运行一次 `hermes update`——它就会覆盖机器上的所有配置文件。

<a id="how-many-profiles-can-i-run"></a>
### 我可以运行多少个配置文件？
没有硬性限制。每个配置文件只是 `~/.hermes/profiles/` 下的一个目录。实际限制取决于你的磁盘空间以及系统能同时处理多少个网关（每个网关是一个轻量级 Python 进程）。运行几十个配置文件没问题；每个空闲的配置文件不消耗任何资源。

---

<a id="workflows-patterns"></a>
## 工作流与模式

<a id="using-different-models-for-different-tasks-multi-model-workflows"></a>
### 为不同任务使用不同模型（多模型工作流）

**场景：** 你日常使用 GPT-5.4，但 Gemini 或 Grok 写社交媒体内容更好。每次手动切换模型很繁琐。

**解决方案：委托配置。** Hermes 可以自动将子 Agent 路由到不同的模型。在 `~/.hermes/config.yaml` 中设置：

```yaml
delegation:
  model: "google/gemini-3-flash-preview"   # 子 Agent 使用此模型
  provider: "openrouter"                    # 子 Agent 的提供商
```

现在，当你告诉 Hermes“帮我写一条关于 X 的 Twitter 推文”时，它会生成一个 `delegate_task` 子 Agent，该子 Agent 在 Gemini 上运行，而不是你的主模型。你的主对话仍保持在 GPT-5.4 上。

你也可以在提示中明确说明：*“委托一个任务来写关于我们产品发布的社交媒体帖子。让子 Agent 实际撰写。”* Agent 会使用 `delegate_task`，它会自动应用委托配置。

对于不使用委托的一次性模型切换，请在 CLI 中使用 `/model`：

```bash
/model google/gemini-3-flash-preview    # 为此会话切换
# ... 撰写你的内容 ...
/model openai/gpt-5.4                   # 切换回来
```
关于委托如何工作的更多信息，请参阅[子Agent委托](../user-guide/features/delegation.md)。

<a id="running-multiple-agents-on-one-whatsapp-number-per-chat-binding"></a>
### 在单个 WhatsApp 号码上运行多个 Agent（按聊天绑定）

**场景：** 在 OpenClaw 中，你有多个独立的 Agent 绑定到特定的 WhatsApp 聊天——一个用于家庭购物清单群组，另一个用于你的私人聊天。Hermes 能做到这一点吗？

**当前限制：** 每个 Hermes 配置文件都需要自己的 WhatsApp 号码/会话。你无法将多个配置文件绑定到同一个 WhatsApp 号码的不同聊天上——WhatsApp 桥接（Baileys）每个号码只使用一个经过认证的会话。

**变通方案：**

1. **使用单一配置文件并切换人格。** 创建不同的 `AGENTS.md` 上下文文件，或使用 `/personality` 命令来按聊天改变行为。Agent 知道自己当前在哪个聊天中，并能相应调整。

2. **使用定时任务处理专项任务。** 对于购物清单追踪器，设置一个定时任务来监控特定聊天并管理清单——无需单独的 Agent。

3. **使用不同的号码。** 如果你需要真正独立的 Agent，请为每个配置文件搭配独立的 WhatsApp 号码。来自 Google Voice 等服务的虚拟号码可以满足需求。

4. **改用 Telegram 或 Discord。** 这些平台更自然地支持按聊天绑定——每个 Telegram 群组或 Discord 频道都会获得自己的会话，并且你可以在同一个账户上运行多个机器人令牌（每个配置文件一个）。

更多详情，请参阅[配置文件](../user-guide/profiles.md)与[WhatsApp 设置](../user-guide/messaging/whatsapp.md)。
<a id="controlling-what-shows-up-in-telegram-hiding-logs-and-reasoning"></a>
### 控制 Telegram 上显示的内容（隐藏日志和推理过程）

**场景：** 你在 Telegram 中看到了网关执行日志、Hermes 推理过程和工具调用详情，而不仅仅是最终输出。

**解决方案：** `config.yaml` 中的 `display.tool_progress` 设置控制工具活动的显示程度：

```yaml
display:
  tool_progress: "off"   # 选项：off, new, all, verbose
```

- **`off`** — 仅显示最终响应。不显示工具调用、推理过程和日志。
- **`new`** — 显示新发生的工具调用（简短的一行信息）。
- **`all`** — 显示所有工具活动，包括结果。
- **`verbose`** — 显示完整细节，包括工具参数和输出。

对于消息平台，通常使用 `off` 或 `new`。编辑 `config.yaml` 后，重启网关以使更改生效。

你也可以通过 `/verbose` 命令（如果启用）在每个会话中切换此设置：

```yaml
display:
  tool_progress_command: true   # 在网关中启用 /verbose 命令
```

<a id="managing-skills-on-telegram-slash-command-limit"></a>
### 管理 Telegram 上的技能（斜杠命令限制）

**场景：** Telegram 有 100 个斜杠命令的限制，而你的技能数量正在超过这个限制。你想在 Telegram 上禁用不需要的技能，但 `hermes skills config` 的设置似乎没有生效。

**解决方案：** 使用 `hermes skills config` 按平台禁用技能。这会写入 `config.yaml`：

```yaml
skills:
  disabled: []                    # 全局禁用的技能
  platform_disabled:
    telegram: [skill-a, skill-b]  # 仅在 telegram 上禁用
```
修改此项后，**请重启网关**（`hermes gateway restart` 或者终止并重新启动）。Telegram 机器人的命令菜单会在启动时重建。

:::tip
描述非常长的技能在 Telegram 菜单中会被截断到 40 个字符，以保持在载荷大小限制内。如果技能没有显示，可能是总载荷大小的问题，而不是 100 条命令数量限制——禁用未使用的技能对两者都有帮助。
:::

<a id="shared-thread-sessions-multiple-users-one-conversation"></a>
### 共享线程会话（多个用户，一个对话）

**场景：** 你有一个 Telegram 或 Discord 线程，其中有多人提及机器人。你希望该线程中的所有提及都属于一个共享对话，而不是每个用户独立的会话。

**当前行为：** Hermes 在大多数平台上使用用户 ID 作为会话标识，因此每个人都有自己的对话上下文。这是为了隐私和上下文隔离而设计的。

**替代方案：**

1. **使用 Slack。** Slack 会话以线程为标识，而不是用户。同一线程中的多个用户共享一个对话——这正是你描述的行为。这是最自然的匹配方式。

2. **使用单个用户的群聊。** 如果指定一个人作为“操作员”来传递问题，会话将保持统一。其他人可以跟着阅读。

3. **使用 Discord 频道。** Discord 会话以频道为标识，因此同一频道中的所有用户共享上下文。使用专用频道进行共享对话。

<a id="exporting-hermes-to-another-machine"></a>
### 将 Hermes 导出到另一台机器

**场景：** 你在一台机器上构建了技能、定时任务和记忆，并希望将所有内容迁移到一台新的专用 Linux 机器上。
**解决方案：**

1. 在新机器上安装 Hermes Agent：
   ```bash
   curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
   ```

2. 在**源机器**上创建完整备份：
   ```bash
   hermes backup
   ```
   这会将整个 `~/.hermes/` 目录（包括配置、API 密钥、记忆、技能、会话和配置文件）打包成一个 zip 文件，并保存到用户主目录，文件名为 `~/hermes-backup-<时间戳>.zip`。

3. 将压缩包复制到新机器并导入：
   ```bash
   # 在源机器上
   scp ~/hermes-backup-<时间戳>.zip 新机器:~/ 

   # 在新机器上
   hermes import ~/hermes-backup-<时间戳>.zip
   ```

4. 在新机器上运行 `hermes setup`，验证 API 密钥和提供者配置是否正常。

<a id="moving-a-single-profile-to-another-machine"></a>
### 将单个配置文件迁移到另一台机器

**场景：** 你想迁移或共享某个特定配置文件，而非整个安装。

```bash
# 在源机器上
hermes profile export work ./work-backup.tar.gz

# 将文件复制到目标机器，然后：
hermes profile import ./work-backup.tar.gz work
```

导入的配置文件将包含导出时的全部配置、记忆、会话和技能。如果新机器的环境不同，可能需要更新路径或重新认证提供者。

<a id="hermes-backup-vs-hermes-profile-export"></a>
### `hermes backup` 与 `hermes profile export` 的区别

| 特性 | `hermes backup` | `hermes profile export` |
| :--- | :--- | :--- |
| **使用场景** | **整机迁移** | **移植/共享特定配置文件** |
| **范围** | 全局（整个 `~/.hermes` 目录） | 本地（单个配置文件目录） |
| **包含内容** | 所有配置文件、全局配置、API 密钥、会话 | 单个配置文件：SOUL.md、记忆、会话、技能 |
| **凭据** | **包含**（`.env` 和 `auth.json`） | **不包含**（为安全共享已移除） |
| **格式** | `.zip` | `.tar.gz` |
**Manual fallback (rsync):** 如果你更倾向于直接复制文件，可以排除代码仓库：
```bash
rsync -av --exclude='hermes-agent' ~/.hermes/ newmachine:~/.hermes/
```

:::tip
`hermes backup` 会在 Hermes 正在运行时生成一致的快照。恢复后的归档文件会排除机器本地的运行时文件，例如 `gateway.pid` 和 `cron.pid`。
:::

<a id="permission-denied-when-reloading-shell-after-install"></a>
### 安装后重新加载 shell 时出现权限拒绝错误

**场景：** 运行 Hermes 安装程序后，`source ~/.zshrc` 报权限拒绝错误。

**原因：** 这通常是因为 `~/.zshrc`（或 `~/.bashrc`）的文件权限不正确，或者安装程序无法正常写入该文件。这不是 Hermes 特有的问题，而是 shell 配置文件的权限问题。

**解决方案：**
```bash
# 检查权限
ls -la ~/.zshrc

# 如有需要则修复（应为 -rw-r--r-- 或 644）
chmod 644 ~/.zshrc

# 然后重新加载
source ~/.zshrc

# 或者直接打开一个新终端窗口——它会自动加载 PATH 变更
```

如果安装程序添加了 PATH 行但权限错误，你可以手动添加：
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
```

<a id="error-400-on-first-agent-run"></a>
### 首次运行 agent 时出现 400 错误

**场景：** 安装设置一切正常，但首次聊天尝试失败，返回 HTTP 400。

**原因：** 通常是模型名称不匹配——配置的模型在你的提供商上不存在，或者 API 密钥没有该模型的访问权限。

**解决方案：**
```bash
# 检查当前配置的模型和提供商
hermes config show | head -20

# 重新运行模型选择
hermes model

# 或者用一个已知可用的模型进行测试
hermes chat -q "hello" --model anthropic/claude-opus-4.7
```
如果使用 OpenRouter，请确保你的 API 密钥有足够的额度。OpenRouter 返回 400 错误通常意味着该模型需要付费计划，或者模型 ID 存在拼写错误。

---

<a id="still-stuck"></a>
## 仍然卡住了？

如果你的问题未在此处涵盖：

1. **搜索已有问题：** [GitHub Issues](https://github.com/NousResearch/hermes-agent/issues)
2. **向社区求助：** [Nous Research Discord](https://discord.gg/nousresearch)
3. **提交错误报告：** 请附上你的操作系统、Python 版本（`python3 --version`）、Hermes 版本（`hermes --version`）以及完整的错误信息
