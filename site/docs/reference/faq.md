---
sidebar_position: 3
title: "常见问题与故障排除"
description: "Hermes Agent 常见问题及常见问题解决方案"
---

# 常见问题与故障排除

针对最常见的问题和疑问，提供快速解答和解决方法。

---

## 常见问题

### Hermes 支持哪些 LLM 提供商？

Hermes Agent 兼容任何支持 OpenAI API 的提供商。支持的提供商包括：

- **[OpenRouter](https://openrouter.ai/)** — 通过一个 API 密钥访问数百个模型（推荐，灵活性高）
- **Nous Portal** — Nous Research 自家的推理端点
- **OpenAI** — GPT-4o、o1、o3 等
- **Anthropic** — Claude 模型（通过 OpenRouter 或兼容代理）
- **Google** — Gemini 模型（通过 OpenRouter 或兼容代理）
- **z.ai / ZhipuAI** — GLM 模型
- **Kimi / Moonshot AI** — Kimi 模型
- **MiniMax** — 全球及中国端点
- **本地模型** — 通过 [Ollama](https://ollama.com/)、[vLLM](https://docs.vllm.ai/)、[llama.cpp](https://github.com/ggerganov/llama.cpp)、[SGLang](https://github.com/sgl-project/sglang) 或任何兼容 OpenAI 的服务器

你可以用 `hermes model` 命令或编辑 `~/.hermes/.env` 来设置提供商。所有提供商密钥请参见[环境变量](./environment-variables.md)参考。

### 它能在 Windows 上运行吗？

**不能原生运行。** Hermes Agent 需要类 Unix 环境。在 Windows 上，请安装 [WSL2](https://learn.microsoft.com/en-us/windows/wsl/install)，并在其中运行 Hermes。WSL2 中的标准安装命令完全可用：

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

### 我的数据会被发送到哪里吗？

API 调用**只会发送到你配置的 LLM 提供商**（例如 OpenRouter，或你本地的 Ollama 实例）。Hermes Agent 不会收集遥测、使用数据或分析数据。你的对话、记忆和技能都保存在本地的 `~/.hermes/` 目录。

### 可以离线使用或用本地模型吗？

可以。运行 `hermes model`，选择 **Custom endpoint**，然后输入你的服务器 URL：

```bash
hermes model
# 选择：Custom endpoint（手动输入 URL）
# API 基础 URL: http://localhost:11434/v1
# API 密钥: ollama
# 模型名称: qwen3.5:27b
# 上下文长度: 32768   ← 设置为与你服务器实际上下文窗口匹配
```

或者直接在 `config.yaml` 中配置：

```yaml
model:
  default: qwen3.5:27b
  provider: custom
  base_url: http://localhost:11434/v1
```

Hermes 会将端点、提供商和基础 URL 保存在 `config.yaml`，重启后依然生效。如果你的本地服务器只加载了一个模型，`/model custom` 会自动检测。你也可以在 `config.yaml` 中设置 `provider: custom` — 它是一个一级提供商，不是别名。

这适用于 Ollama、vLLM、llama.cpp 服务器、SGLang、LocalAI 等。详情请参见[配置指南](../user-guide/configuration.md)。

:::tip Ollama 用户
如果你在 Ollama 中设置了自定义的 `num_ctx`（例如 `ollama run --num_ctx 16384`），请确保在 Hermes 中设置匹配的上下文长度 — Ollama 的 `/api/show` 显示的是模型的*最大*上下文，而不是你配置的实际 `num_ctx`。
:::

### 使用成本是多少？

Hermes Agent 本身是**免费且开源**的（MIT 许可证）。你只需为所选提供商的 LLM API 使用付费。本地模型完全免费运行。

### 多人可以共用一个实例吗？

可以。[消息网关](../user-guide/messaging/index.md)支持多个用户通过 Telegram、Discord、Slack、WhatsApp 或 Home Assistant 与同一个 Hermes Agent 实例交互。访问通过允许列表（指定用户 ID）和私信配对（第一个发消息的用户获得访问权限）控制。

### 记忆和技能有什么区别？

- **记忆**存储的是**事实**——Agent 知道的关于你、你的项目和偏好的信息。记忆会根据相关性自动检索。
- **技能**存储的是**操作流程**——完成任务的步骤说明。Agent 遇到类似任务时会调用技能。

两者都会跨会话保存。详情请参见[记忆](../user-guide/features/memory.md)和[技能](../user-guide/features/skills.md)。

### 可以在我自己的 Python 项目中使用吗？

可以。导入 `AIAgent` 类，编程调用 Hermes：

```python
from hermes.agent import AIAgent

agent = AIAgent(model="openrouter/nous/hermes-3-llama-3.1-70b")
response = agent.chat("Explain quantum computing briefly")
```

完整 API 用法请参见[Python 库指南](../user-guide/features/code-execution.md)。

---

## 故障排除

### 安装问题

#### 安装后出现 `hermes: command not found`

**原因：** 你的 shell 没有重新加载更新后的 PATH。

**解决方法：**
```bash
# 重新加载 shell 配置
source ~/.bashrc    # bash
source ~/.zshrc     # zsh

# 或者打开一个新的终端会话
```

如果仍然无效，检查安装位置：
```bash
which hermes
ls ~/.local/bin/hermes
```

:::tip
安装程序会将 `~/.local/bin` 添加到 PATH。如果你使用了非标准的 shell 配置，请手动添加 `export PATH="$HOME/.local/bin:$PATH"`。
:::

#### Python 版本过旧

**原因：** Hermes 需要 Python 3.11 或更高版本。

**解决方法：**
```bash
python3 --version   # 查看当前版本

# 安装新版 Python
sudo apt install python3.12   # Ubuntu/Debian
brew install python@3.12      # macOS
```

安装程序会自动处理此问题——如果你手动安装时遇到此错误，请先升级 Python。

#### 出现 `uv: command not found`

**原因：** 没有安装 `uv` 包管理器，或未加入 PATH。

**解决方法：**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc
```

#### 安装时出现权限拒绝错误

**原因：** 没有写入安装目录的权限。

**解决方法：**
```bash
# 不要用 sudo 安装——安装到 ~/.local/bin
# 如果之前用 sudo 安装过，先清理：
sudo rm /usr/local/bin/hermes
# 然后重新运行标准安装命令
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

---

### 提供商与模型问题

#### API 密钥无效

**原因：** 密钥缺失、过期、设置错误或对应错误的提供商。

**解决方法：**
```bash
# 查看配置
hermes config show

# 重新配置提供商
hermes model

# 或直接设置
hermes config set OPENROUTER_API_KEY sk-or-v1-xxxxxxxxxxxx
```

:::warning
确保密钥对应正确的提供商。OpenAI 的密钥不能用在 OpenRouter，反之亦然。检查 `~/.hermes/.env` 是否有冲突条目。
:::

#### 模型不可用 / 找不到模型

**原因：** 模型标识符错误或提供商不支持该模型。

**解决方法：**
```bash
# 列出提供商支持的模型
hermes model

# 设置有效模型
hermes config set HERMES_MODEL openrouter/nous/hermes-3-llama-3.1-70b

# 或会话时指定
hermes chat --model openrouter/meta-llama/llama-3.1-70b-instruct
```

#### 频率限制（429 错误）

**原因：** 超过了提供商的调用频率限制。

**解决方法：** 等待一会儿再试。长期使用建议：
- 升级提供商套餐
- 切换到其他模型或提供商
- 使用 `hermes chat --provider <alternative>` 路由到其他后端

#### 超出上下文长度限制

**原因：** 对话内容超过模型的上下文窗口，或 Hermes 检测到的上下文长度不正确。

**解决方法：**
```bash
# 压缩当前会话
/compress

# 或开启新会话
hermes chat

# 使用上下文窗口更大的模型
hermes chat --model openrouter/google/gemini-2.0-flash-001
```

如果第一次长对话就出现此问题，可能是 Hermes 检测的上下文长度不对。查看检测结果：

启动时命令行会显示检测到的上下文长度（例如 `📊 Context limit: 128000 tokens`）。会话中也可以用 `/usage` 查看。

修正上下文长度，显式设置：

```yaml
# 在 ~/.hermes/config.yaml 中
model:
  default: your-model-name
  context_length: 131072  # 你的模型实际上下文窗口
```

---
或者对于自定义端点，可以按模型添加：

```yaml
custom_providers:
  - name: "My Server"
    base_url: "http://localhost:11434/v1"
    models:
      qwen3.5:27b:
        context_length: 32768
```

有关自动检测的工作原理及所有覆盖选项，请参见[上下文长度检测](../integrations/providers.md#context-length-detection)。

---

### 终端问题

#### 命令被阻止为危险命令

**原因：** Hermes 检测到潜在破坏性的命令（例如 `rm -rf`、`DROP TABLE`）。这是一个安全功能。

**解决方案：** 当出现提示时，审查命令并输入 `y` 以批准。你也可以：
- 让 Agent 使用更安全的替代方案
- 查看[安全文档](../user-guide/security.md)中的所有危险模式列表

:::tip
这是预期的行为——Hermes 从不默默执行破坏性命令。批准提示会准确显示将要执行的内容。
:::

#### 通过消息网关使用 `sudo` 无效

**原因：** 消息网关在无交互终端环境下运行，`sudo` 无法提示输入密码。

**解决方案：**
- 避免在消息中使用 `sudo`，让 Agent 寻找替代方案
- 如果必须使用 `sudo`，请在 `/etc/sudoers` 中配置特定命令的免密码 sudo
- 或切换到终端界面执行管理任务：`hermes chat`

#### Docker 后端无法连接

**原因：** Docker 守护进程未运行或用户权限不足。

**解决方案：**
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

### 消息问题

#### 机器人不响应消息

**原因：** 机器人未运行、未授权，或你的用户不在允许列表中。

**解决方案：**
```bash
# 检查网关是否运行
hermes gateway status

# 启动网关
hermes gateway start

# 查看错误日志
cat ~/.hermes/logs/gateway.log | tail -50
```

#### 消息未送达

**原因：** 网络问题、机器人令牌过期或平台 webhook 配置错误。

**解决方案：**
- 使用 `hermes gateway setup` 验证机器人令牌是否有效
- 检查网关日志：`cat ~/.hermes/logs/gateway.log | tail -50`
- 对于基于 webhook 的平台（Slack、WhatsApp），确保服务器可公开访问

#### 允许列表混淆——谁能和机器人对话？

**原因：** 授权模式决定谁有访问权限。

**解决方案：**

| 模式 | 工作方式 |
|------|----------|
| **Allowlist** | 只有配置中列出的用户 ID 可以交互 |
| **DM pairing** | 第一个在私信中发消息的用户获得独占访问权 |
| **Open** | 任何人都可以交互（不建议用于生产环境） |

在 `~/.hermes/config.yaml` 中的网关设置下配置。详见[消息文档](../user-guide/messaging/index.md)。

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

**原因：** launchd 服务继承了一个最小的 PATH（`/usr/bin:/bin:/usr/sbin:/sbin`），不包含 Homebrew、nvm、cargo 或其他用户安装的工具目录。这通常导致 WhatsApp 桥接（`node not found`）或语音转录（`ffmpeg not found`）失败。

**解决方案：** 网关在运行 `hermes gateway install` 时会捕获你的 shell PATH。如果你在设置网关后安装了工具，请重新运行安装以捕获更新后的 PATH：

```bash
hermes gateway install    # 重新快照当前 PATH
hermes gateway start      # 识别更新的 plist 并重新加载
```

你可以验证 plist 是否包含正确的 PATH：
```bash
/usr/libexec/PlistBuddy -c "Print :EnvironmentVariables:PATH" \
  ~/Library/LaunchAgents/ai.hermes.gateway.plist
```

---

### 性能问题

#### 响应缓慢

**原因：** 模型较大、API 服务器距离远，或系统提示包含大量工具。

**解决方案：**
- 尝试更快/更小的模型：`hermes chat --model openrouter/meta-llama/llama-3.1-8b-instruct`
- 减少激活的工具集：`hermes chat -t "terminal"`
- 检查到提供者的网络延迟
- 对于本地模型，确保有足够的 GPU 显存

#### 令牌使用量高

**原因：** 对话过长、系统提示冗长或多次调用工具导致上下文积累。

**解决方案：**
```bash
# 压缩对话以减少令牌
/compress

# 查看会话令牌使用情况
/usage
```

:::tip
在长会话中定期使用 `/compress`。它会总结对话历史，大幅减少令牌使用，同时保留上下文。
:::

#### 会话过长

**原因：** 长时间对话积累了大量消息和工具输出，接近上下文限制。

**解决方案：**
```bash
# 压缩当前会话（保留关键上下文）
/compress

# 启动新会话并引用旧会话
hermes chat

# 需要时稍后继续特定会话
hermes chat --continue
```

---

### MCP 问题

#### MCP 服务器无法连接

**原因：** 找不到服务器二进制文件、命令路径错误或缺少运行时。

**解决方案：**
```bash
# 确保安装了 MCP 依赖（标准安装已包含）
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

#### MCP 服务器工具未显示

**原因：** 服务器已启动但工具发现失败，工具被配置过滤，或服务器不支持你期望的 MCP 功能。

**解决方案：**
- 检查网关/Agent 日志中的 MCP 连接错误
- 确保服务器响应 `tools/list` RPC 方法
- 审查该服务器下的 `tools.include`、`tools.exclude`、`tools.resources`、`tools.prompts` 或 `enabled` 设置
- 记住资源/提示工具仅在会话实际支持相关功能时注册
- 修改配置后使用 `/reload-mcp`

```bash
# 验证 MCP 服务器配置
hermes config show | grep -A 12 mcp_servers

# 配置更改后重启 Hermes 或重新加载 MCP
hermes chat
```

另见：
- [MCP（模型上下文协议）](/user-guide/features/mcp)
- [在 Hermes 中使用 MCP](/guides/use-mcp-with-hermes)
- [MCP 配置参考](/reference/mcp-config-reference)

#### MCP 超时错误

**原因：** MCP 服务器响应过慢或执行时崩溃。

**解决方案：**
- 如果支持，增加 MCP 服务器配置中的超时时间
- 检查 MCP 服务器进程是否仍在运行
- 对于远程 HTTP MCP 服务器，检查网络连接

:::warning
如果 MCP 服务器在请求中途崩溃，Hermes 会报告超时。请检查服务器自身日志（不仅是 Hermes 日志）以诊断根本原因。
:::

---

## 配置文件（Profiles） {#profiles}

### 配置文件和直接设置 HERMES_HOME 有何不同？

配置文件是在 `HERMES_HOME` 之上的管理层。你*可以*在每次命令前手动设置 `HERMES_HOME=/some/path`，但配置文件帮你处理所有细节：创建目录结构、生成 shell 别名（`hermes-work`）、跟踪活动配置文件（`~/.hermes/active_profile`），并自动同步所有配置文件的技能更新。它们还集成了标签补全，免去你记路径的麻烦。

### 两个配置文件可以共用同一个机器人令牌吗？

不行。每个平台（Telegram、Discord 等）都要求机器人令牌独占访问。如果两个配置文件同时使用同一个令牌，第二个网关会连接失败。请为每个配置文件创建独立机器人——Telegram 上可以找 [@BotFather](https://t.me/BotFather) 创建额外机器人。
### 配置文件会共享内存或会话吗？

不会。每个配置文件都有自己的内存存储、会话数据库和技能目录，彼此完全隔离。如果你想用已有的内存和会话启动一个新配置文件，可以使用 `hermes profile create newname --clone-all` 来复制当前配置文件的所有内容。

### 运行 `hermes update` 会发生什么？

`hermes update` 会拉取最新代码并重新安装依赖，**只执行一次**（不是针对每个配置文件单独执行）。然后它会自动将更新后的技能同步到所有配置文件。你只需运行一次 `hermes update` —— 它会覆盖机器上的所有配置文件。

### 我可以把配置文件迁移到另一台机器吗？

可以。先将配置文件导出为一个便携的归档文件，然后在另一台机器上导入：

```bash
# 在源机器上
hermes profile export work ./work-backup.tar.gz

# 将文件复制到目标机器，然后执行：
hermes profile import ./work-backup.tar.gz work
```

导入的配置文件会包含导出时的所有配置、内存、会话和技能。如果新机器的环境不同，可能需要更新路径或重新认证服务提供商。

### 我最多能运行多少个配置文件？

没有硬性限制。每个配置文件只是 `~/.hermes/profiles/` 目录下的一个文件夹。实际限制取决于你的磁盘空间和系统能同时处理多少个网关（每个网关是一个轻量级的 Python 进程）。运行几十个配置文件没问题；每个空闲的配置文件不会占用资源。

---

## 仍然遇到问题？

如果这里没有涵盖你的问题：

1. **搜索已有问题：** [GitHub Issues](https://github.com/NousResearch/hermes-agent/issues)
2. **向社区求助：** [Nous Research Discord](https://discord.gg/nousresearch)
3. **提交错误报告：** 请附上你的操作系统、Python 版本（`python3 --version`）、Hermes 版本（`hermes --version`）以及完整的错误信息

---
