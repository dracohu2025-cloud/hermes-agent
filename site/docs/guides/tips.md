---
sidebar_position: 1
title: "技巧与最佳实践"
description: "充分利用 Hermes Agent 的实用建议 —— 包括 Prompt 技巧、CLI 快捷键、上下文文件、Memory、成本优化以及安全"
---

# 技巧与最佳实践 {#tips-best-practices}

这是一份能让你在使用 Hermes Agent 时立竿见影提高效率的实用技巧合集。每个部分针对不同的方面 —— 你可以浏览标题并跳转到相关内容。

---

## 获取最佳结果 {#getting-the-best-results}

### 明确你的需求 {#be-specific-about-what-you-want}

模糊的 Prompt 会产生模糊的结果。不要说“修复代码”，而要说“修复 `api/handlers.py` 第 47 行的 TypeError —— `process_request()` 函数从 `parse_body()` 接收到了 `None`”。你提供的上下文越多，需要的迭代次数就越少。

### 提前提供上下文 {#provide-context-up-front}

在请求的开头就提供相关细节：文件路径、错误信息、预期行为。一条精心编写的消息胜过三轮澄清。直接粘贴错误堆栈（tracebacks）—— Agent 可以解析它们。

### 为重复性指令使用上下文文件 {#use-context-files-for-recurring-instructions}

如果你发现自己总是在重复同样的指令（“使用 tab 而不是空格”、“我们使用 pytest”、“API 在 `/api/v2`”），请将它们放入 `AGENTS.md` 文件中。Agent 在每次会话中都会自动读取它 —— 设置完成后无需额外操作。

### 让 Agent 使用它的工具 {#let-the-agent-use-its-tools}

不要试图手把手指导每一步。说“找到并修复失败的测试”，而不是“打开 `tests/test_foo.py`，查看第 42 行，然后……”。Agent 拥有文件搜索、终端访问和代码执行权限 —— 让它去探索和迭代。

### 为复杂工作流使用 Skills {#use-skills-for-complex-workflows}

在编写长篇 Prompt 解释如何操作之前，先检查是否已有相关的 Skill。输入 `/skills` 浏览可用 Skill，或者直接调用一个，例如 `/axolotl` 或 `/github-pr-workflow`。

## CLI 高级用户技巧 {#cli-power-user-tips}

### 多行输入 {#multi-line-input}

按下 **Alt+Enter**（或 **Ctrl+J**）插入换行符而不发送。这让你可以在按下 Enter 发送之前，编写多行 Prompt、粘贴代码块或组织复杂的请求。

### 粘贴检测 {#paste-detection}

CLI 会自动检测多行粘贴。直接粘贴代码块或错误堆栈即可 —— 它不会将每一行作为单独的消息发送。粘贴内容会被缓冲并作为一条消息发送。

### 中断与重定向 {#interrupt-and-redirect}

按下一次 **Ctrl+C** 可以在 Agent 响应中途将其中断。然后你可以输入新消息来重定向它。在 2 秒内连按两次 Ctrl+C 可强制退出。当 Agent 开始偏离正确方向时，这非常有用。

### 使用 `-c` 恢复会话 {#resume-sessions-with-c}

忘记了上次会话的内容？运行 `hermes -c` 即可从上次中断的地方恢复，并还原完整的对话历史。你也可以通过标题恢复：`hermes -r "my research project"`。

### 剪贴板图片粘贴 {#clipboard-image-paste}

按下 **Ctrl+V** 直接将剪贴板中的图片粘贴到聊天中。Agent 会使用视觉能力分析截图、图表、错误弹窗或 UI 原型 —— 无需先保存为文件。

### 斜杠命令自动补全 {#slash-command-autocomplete}

输入 `/` 并按下 **Tab** 键查看所有可用命令。这包括内置命令（`/compress`、`/model`、`/title`）以及所有已安装的 Skill。你不需要记住任何东西 —— Tab 补全能帮你搞定。

:::tip
使用 `/verbose` 循环切换工具输出显示模式：**off → new → all → verbose**。“all” 模式非常适合观察 Agent 的动作；“off” 模式对于简单的问答最清爽。
:::

## 上下文文件 {#context-files}

### AGENTS.md：项目的“大脑” {#agents-md-your-project-s-brain}

在项目根目录创建一个 `AGENTS.md`，包含架构决策、编码规范和项目特定指令。它会自动注入到每个会话中，因此 Agent 始终了解你的项目规则。

```markdown
# Project Context
- 这是一个使用 SQLAlchemy ORM 的 FastAPI 后端
- 数据库操作始终使用 async/await
- 测试文件放在 tests/ 目录下并使用 pytest-asyncio
- 严禁提交 .env 文件
```

### SOUL.md：自定义个性 {#soul-md-customize-personality}

想让 Hermes 拥有稳定的默认语气？编辑 `~/.hermes/SOUL.md`（如果你使用了自定义 Hermes 目录，则编辑 `$HERMES_HOME/SOUL.md`）。Hermes 现在会自动生成一个初始 SOUL，并使用该全局文件作为整个实例的个性来源。

有关完整指南，请参阅 [在 Hermes 中使用 SOUL.md](/guides/use-soul-with-hermes)。

```markdown
# Soul
你是一名资深后端工程师。说话要简练直接。
除非被要求，否则跳过解释。比起冗长的方案，更倾向于单行代码。
始终考虑错误处理和边缘情况。
```

使用 `SOUL.md` 设定持久的个性。使用 `AGENTS.md` 设定项目特定的指令。

### .cursorrules 兼容性 {#cursorrules-compatibility}

已经有 `.cursorrules` 或 `.cursor/rules/*.mdc` 文件了？Hermes 也会读取它们。无需重复你的编码规范 —— 它们会自动从当前工作目录加载。

### 发现机制 {#discovery}

Hermes 在会话开始时从当前工作目录加载顶层的 `AGENTS.md`。子目录中的 `AGENTS.md` 文件会在工具调用期间（通过 `subdirectory_hints.py`）被延迟发现并注入到工具结果中 —— 它们不会预先加载到 System Prompt 中。

:::tip
保持上下文文件聚焦且简洁。由于它们会被注入到每一条消息中，每个字符都会占用你的 Token 预算。
:::

## Memory 与 Skills {#memory-skills}

### Memory vs. Skills：该放哪里 {#memory-vs-skills-what-goes-where}

**Memory** 用于存储事实：你的环境、偏好、项目位置以及 Agent 了解到的关于你的信息。**Skills** 用于存储流程：多步骤工作流、特定工具的指令和可复用的方案。Memory 存“是什么”，Skills 存“怎么做”。

### 何时创建 Skills {#when-to-create-skills}

如果你发现一个任务需要 5 步以上且你会再次执行它，请让 Agent 为其创建一个 Skill。说“把你刚才做的操作保存为一个名为 `deploy-staging` 的 Skill”。下次只需输入 `/deploy-staging`，Agent 就会加载完整的流程。

### 管理 Memory 容量 {#managing-memory-capacity}

Memory 是有意识限制大小的（`MEMORY.md` 约 2,200 字符，`USER.md` 约 1,375 字符）。当存满时，Agent 会合并条目。你可以通过说“清理你的 Memory”或“替换掉旧的 Python 3.9 笔记 —— 我们现在用 3.12 了”来提供帮助。

### 让 Agent 记住 {#let-the-agent-remember}

在一次高效的会话结束后，说“记住这次的重点以便下次使用”，Agent 就会保存关键信息。你也可以很具体：“把我们的 CI 使用带有 `deploy.yml` 工作流的 GitHub Actions 这一点保存到 Memory 中。”

:::warning
Memory 是一个冻结的快照 —— 会话期间所做的更改直到下次会话开始才会出现在 System Prompt 中。Agent 会立即写入磁盘，但 Prompt 缓存不会在会话中途失效。
:::

## 性能与成本 {#performance-cost}

### 不要破坏 Prompt 缓存 {#don-t-break-the-prompt-cache}

大多数 LLM 提供商都会缓存 System Prompt 前缀。如果你保持 System Prompt 稳定（相同的上下文文件、相同的 Memory），会话中的后续消息将获得**缓存命中（cache hits）**，从而显著降低成本。避免在会话中途更改模型或 System Prompt。

### 在达到限制前使用 /compress {#use-compress-before-hitting-limits}

长会话会累积 Token。当你注意到响应变慢或被截断时，运行 `/compress`。这会总结对话历史，在保留关键上下文的同时大幅减少 Token 数量。使用 `/usage` 查看当前状态。

### 委派并行任务 {#delegate-for-parallel-work}

需要同时研究三个主题？让 Agent 使用 `delegate_task` 并配合并行子任务。每个 sub-agent 独立运行并拥有自己的上下文，只有最终总结会返回 —— 这能极大地减少主对话的 Token 使用量。

### 使用 execute_code 进行批量操作 {#use-executecode-for-batch-operations}

与其逐个运行终端命令，不如让 Agent 编写一个脚本一次性完成所有操作。“写一个 Python 脚本把所有 `.jpeg` 文件重命名为 `.jpg` 并运行它”比逐个重命名文件更便宜、更快速。

### 选择合适的模型 {#choose-the-right-model}

使用 `/model` 在会话中途切换模型。对于复杂的推理和架构决策，使用顶级模型（Claude Sonnet/Opus, GPT-4o）。对于格式化、重命名或生成样板代码等简单任务，切换到更快的模型。

:::tip
定期运行 `/usage` 查看你的 Token 消耗。运行 `/insights` 查看过去 30 天使用模式的更广泛视图。
:::

## 消息技巧 {#messaging-tips}

### 设置主频道 {#set-a-home-channel}
在您偏好的 Telegram 或 Discord 聊天中使用 `/sethome` 来将其指定为 Home 频道。Cron 任务结果和定时任务输出都会发送到这里。如果没有设置，Agent 将无法发送主动消息。

### 使用 /title 整理会话 {#use-title-to-organize-sessions}

使用 `/title auth-refactor` 或 `/title research-llm-quantization` 为您的会话命名。命名的会话可以通过 `hermes sessions list` 轻松找到，并使用 `hermes -r "auth-refactor"` 恢复。未命名的会话堆积起来后将难以区分。

### 团队访问的 DM 配对 {#dm-pairing-for-team-access}

与其手动收集用户 ID 来配置白名单，不如启用 DM 配对（DM pairing）。当团队成员给机器人发私信时，他们会获得一个一次性配对码。您只需通过 `hermes pairing approve telegram XKGH5N7P` 批准即可 —— 既简单又安全。

### 工具进度显示模式 {#tool-progress-display-modes}

使用 `/verbose` 来控制您看到的工具活动量。在即时通讯平台中，通常越简洁越好 —— 保持在 "new" 模式以仅查看新的工具调用。在 CLI 中，"all" 模式可以为您提供 Agent 执行所有操作的实时视图。

:::tip
在即时通讯平台上，会话会在空闲一段时间（默认 24 小时）或每天凌晨 4 点自动重置。如果需要更长的会话时间，可以在 `~/.hermes/config.yaml` 中按平台进行调整。
:::

## 安全性 {#security}

### 对不可信代码使用 Docker {#use-docker-for-untrusted-code}

在处理不可信的仓库或运行不熟悉的代码时，请使用 Docker 或 Daytona 作为您的终端后端。在 `.env` 中设置 `TERMINAL_BACKEND=docker`。容器内的破坏性命令不会伤害您的宿主系统。

```bash
# 在您的 .env 中：
TERMINAL_BACKEND=docker
TERMINAL_DOCKER_IMAGE=hermes-sandbox:latest
```

### 避免 Windows 编码陷阱 {#avoid-windows-encoding-pitfalls}

在 Windows 上，某些默认编码（如 `cp125x`）无法表示所有 Unicode 字符，这可能会在测试或脚本中写入文件时导致 `UnicodeEncodeError`。

- 建议在打开文件时显式指定 UTF-8 编码：

```python
with open("results.txt", "w", encoding="utf-8") as f:
    f.write("✓ All good\n")
```

- 在 PowerShell 中，您也可以将当前会话的控制台和原生命令输出切换为 UTF-8：

```powershell
$OutputEncoding = [Console]::OutputEncoding = [Text.UTF8Encoding]::new($false)
```

这能让 PowerShell 及其子进程保持 UTF-8 编码，有助于避免仅在 Windows 上出现的失败。

### 在选择 "Always" 之前仔细检查 {#review-before-choosing-always}

当 Agent 触发危险命令审批（如 `rm -rf`、`DROP TABLE` 等）时，您会看到四个选项：**once**（单次）、**session**（会话级）、**always**（始终）、**deny**（拒绝）。在选择 "always" 之前请三思 —— 它会永久将该模式加入白名单。在您完全放心之前，建议先使用 "session"。

### 命令审批是您的安全网 {#command-approval-is-your-safety-net}

Hermes 在执行前会根据一份精心挑选的危险模式列表检查每个命令。这包括递归删除、SQL 删除、将 curl 结果通过管道传给 shell 等。不要在生产环境中禁用此功能 —— 它的存在是有充分理由的。

:::warning
当在容器后端（Docker、Singularity、Modal、Daytona）运行时，危险命令检查会被**跳过**，因为容器本身就是安全边界。请确保您的容器镜像已妥善锁定。
:::

### 为即时通讯机器人使用白名单 {#use-allowlists-for-messaging-bots}

永远不要在具有终端访问权限的机器人上设置 `GATEWAY_ALLOW_ALL_USERS=true`。务必使用特定平台的白名单（`TELEGRAM_ALLOWED_USERS`、`DISCORD_ALLOWED_USERS`）或 DM 配对来控制谁可以与您的 Agent 交互。

```bash
# 推荐做法：为每个平台设置显式白名单
TELEGRAM_ALLOWED_USERS=123456789,987654321
DISCORD_ALLOWED_USERS=123456789012345678

# 或者使用跨平台白名单
GATEWAY_ALLOWED_USERS=123456789,987654321
```

---

*有想要分享的技巧？欢迎提交 Issue 或 PR —— 我们非常欢迎社区贡献。*
