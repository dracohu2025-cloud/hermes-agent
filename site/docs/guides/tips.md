---
sidebar_position: 1
title: "技巧与最佳实践"
description: "充分发挥 Hermes Agent 效用的实用建议——提示词技巧、CLI 快捷键、上下文文件、记忆、成本优化与安全"
---

<a id="tips-best-practices"></a>
# 技巧与最佳实践

这是一份能让你立即更高效使用 Hermes Agent 的实用技巧速查合集。每个章节针对不同方面——浏览标题，直接跳转到你感兴趣的部分。

---

<a id="getting-the-best-results"></a>
## 获得最佳结果

<a id="be-specific-about-what-you-want"></a>
### 明确说明你的需求

模糊的提示词只会得到模糊的结果。与其说“修复代码”，不如说“修复 `api/handlers.py` 第 47 行的 TypeError——`process_request()` 函数从 `parse_body()` 收到了 `None`”。你提供的上下文越多，需要的迭代次数就越少。

<a id="provide-context-up-front"></a>
### 提前提供上下文

在请求中预先提供相关细节：文件路径、错误信息、预期行为。一条精心编写的消息胜过三轮澄清。直接粘贴错误回溯信息——Agent 可以解析它们。

<a id="use-context-files-for-recurring-instructions"></a>
### 使用上下文文件处理重复指令

如果你发现自己总是重复相同的指令（“用制表符不要用空格”、“我们用 pytest”、“API 在 `/api/v2`”），把它们放到一个 `AGENTS.md` 文件中。Agent 每次会话都会自动读取它——设置完成后零成本。

<a id="let-the-agent-use-its-tools"></a>
### 让 Agent 使用它的工具

不要试图手把手指导每一步。说“找到并修复失败的测试”，而不是“打开 `tests/test_foo.py`，看第 42 行，然后……”。Agent 拥有文件搜索、终端访问和代码执行能力——让它自己去探索和迭代。

<a id="use-skills-for-complex-workflows"></a>
### 使用技能处理复杂工作流

在编写冗长的提示词解释如何做某事之前，先检查一下是否已有对应的技能。输入 `/skills` 浏览可用技能，或者直接调用，比如 `/axolotl` 或 `/github-pr-workflow`。

<a id="cli-power-user-tips"></a>
## CLI 高级用户技巧

<a id="multi-line-input"></a>
### 多行输入

按 **Alt+Enter**、**Ctrl+J** 或 **Shift+Enter** 插入换行而不发送消息。`Shift+Enter` 仅在终端将其作为独立按键发送时有效（默认在 Kitty / foot / WezTerm / Ghostty 中；启用 Kitty 键盘协议后，在 iTerm2 / Alacritty / VS Code 终端中也有效）。另外两个快捷键在所有终端中都有效。

<a id="paste-detection"></a>
### 粘贴检测

CLI 会自动检测多行粘贴。直接粘贴代码块或错误回溯信息——它不会把每一行当作单独的消息发送。粘贴内容会被缓冲并作为一条消息发送。

<a id="interrupt-and-redirect"></a>
### 中断与重定向

在 Agent 响应过程中按一次 **Ctrl+C** 即可中断。然后你可以输入新消息来重定向它。在 2 秒内连续按两次 Ctrl+C 可强制退出。当 Agent 开始走错方向时，这招非常有用。

<a id="resume-sessions-with-c"></a>
### 使用 `-c` 恢复会话

上次会话忘了什么？运行 `hermes -c` 即可从上次中断的地方精确恢复，完整对话历史也会还原。你也可以按标题恢复：`hermes -r "我的研究项目"`。

<a id="clipboard-image-paste"></a>
### 剪贴板图片粘贴

按 **Ctrl+V** 将剪贴板中的图片直接粘贴到聊天中。Agent 会使用视觉能力分析截图、图表、错误弹窗或 UI 原型——无需先保存到文件。

<a id="slash-command-autocomplete"></a>
### 斜杠命令自动补全

输入 `/` 并按 **Tab** 键查看所有可用命令。这包括内置命令（`/compress`、`/model`、`/title`）和所有已安装的技能。你不需要记住任何东西——Tab 补全会帮你搞定。
:::tip
使用 `/verbose` 循环切换工具输出显示模式：**关闭 → 仅新内容 → 全部 → 详细**。「全部」模式适合观察 Agent 做了什么；「关闭」模式对简单问答最清爽。
:::

<a id="context-files"></a>
## 上下文文件

<a id="agents-md-your-project-s-brain"></a>
### AGENTS.md：项目的「大脑」

在项目根目录创建 `AGENTS.md`，写入架构决策、编码约定和项目专属说明。该文件会被自动注入到每次对话中，这样 Agent 能始终了解你的项目规则。

```markdown
# 项目上下文
- 这是一个使用 SQLAlchemy ORM 的 FastAPI 后端项目
- 数据库操作始终使用 async/await
- 测试文件放在 tests/ 中，使用 pytest-asyncio
- 禁止提交 .env 文件
```

<a id="soul-md-customize-personality"></a>
### SOUL.md：定制个性

想让 Hermes 拥有稳定的默认语气？编辑 `~/.hermes/SOUL.md`（如果你自定义了 Hermes 主目录，则编辑 `$HERMES_HOME/SOUL.md`）。Hermes 会自动生成初始 SOUL 文件，并将该全局文件用作实例级的个性来源。

完整教程请参见 [将 SOUL.md 与 Hermes 配合使用](/guides/use-soul-with-hermes)。

```markdown
# 灵魂
你是一位资深后端工程师。说话要简洁直接。
除非被提问，否则不要做额外解释。优先用一行代码解决问题，而不是冗长的方案。
始终考虑错误处理和边界情况。
```

使用 `SOUL.md` 定义持久的个性。使用 `AGENTS.md` 定义项目专属指令。

<a id="cursorrules-compatibility"></a>
### 兼容 .cursorrules

如果你已经有 `.cursorrules` 或 `.cursor/rules/*.mdc` 文件，Hermes 也能读取它们。无需重复编写编码约定——它们会自动从工作目录加载。

<a id="discovery"></a>
### 发现机制

Hermes 在会话启动时从当前工作目录加载顶层 `AGENTS.md`。子目录中的 `AGENTS.md` 文件会在工具调用期间（通过 `subdirectory_hints.py`）延迟发现，并注入到工具结果中——它们不会提前加载到系统提示词中。

:::tip
保持上下文文件精炼且聚焦。每个字符都计入令牌预算，因为它们会被注入到每一条消息中。
:::

<a id="memory-skills"></a>
## 记忆与技能

<a id="memory-vs-skills-what-goes-where"></a>
### 记忆 vs. 技能：各放何处

**记忆**用来存放事实：你的环境、偏好、项目位置以及 Agent 了解到的关于你的信息。**技能**用来存放步骤：多步工作流、工具专属说明和可复用的方案。记忆负责「是什么」，技能负责「怎么做」。

<a id="when-to-create-skills"></a>
### 何时创建技能

如果你发现某个任务需要 5 步以上且你会再次执行，就让 Agent 为其创建一个技能。例如说「把你刚才做的事保存为技能，命名为 `deploy-staging`」。下次只需输入 `/deploy-staging`，Agent 就会加载完整的流程。

<a id="managing-memory-capacity"></a>
### 管理记忆容量

记忆容量是有意限制的（MEMORY.md 约 2200 字符，USER.md 约 1375 字符）。当记忆快满时，Agent 会合并条目。你可以通过说「清理你的记忆」或「替换旧的 Python 3.9 记录——我们现在用 3.12 了」来帮助管理。

<a id="let-the-agent-remember"></a>
### 让 Agent 记住

在一次高效的会话结束后，说「记住这个，下次用」，Agent 就会保存关键要点。你也可以说得更具体：「保存到记忆：我们的 CI 使用 GitHub Actions，工作流文件是 `deploy.yml`。」
:::warning
记忆是一个冻结的快照——会话期间所做的更改在下一个会话开始之前不会出现在系统提示中。Agent 会立即写入磁盘，但提示缓存不会在会话中途失效。
:::

<a id="performance-cost"></a>
## 性能与成本

<a id="don-t-break-the-prompt-cache"></a>
### 不要破坏提示缓存

大多数 LLM 提供商都会缓存系统提示前缀。如果你保持系统提示稳定（相同的上下文文件、相同的记忆），会话中的后续消息将获得**缓存命中**，从而显著降低成本。避免在会话中途更改模型或系统提示。

<a id="use-compress-before-hitting-limits"></a>
### 在达到限制前使用 /compress

长时间会话会累积大量 token。当你注意到响应变慢或被截断时，运行 `/compress`。这会总结对话历史，保留关键上下文，同时大幅减少 token 数量。使用 `/usage` 检查当前状态。

<a id="delegate-for-parallel-work"></a>
### 委托进行并行工作

需要同时研究三个主题？让 Agent 使用 `delegate_task` 并设置并行子任务。每个子 Agent 独立运行，拥有自己的上下文，只有最终摘要会返回——这能大幅减少主会话的 token 使用量。

<a id="use-executecode-for-batch-operations"></a>
### 使用 execute_code 进行批量操作

与其逐个运行终端命令，不如让 Agent 编写一个一次性完成所有操作的脚本。"编写一个 Python 脚本，将所有 `.jpeg` 文件重命名为 `.jpg` 并运行它"比逐个重命名文件更便宜、更快速。

<a id="choose-the-right-model"></a>
### 选择合适的模型

使用 `/model` 在会话中途切换模型。对于复杂的推理和架构决策，使用前沿模型（Claude Sonnet/Opus、GPT-4o）。对于简单的任务，如格式化、重命名或生成样板代码，切换到更快的模型。

:::tip
定期运行 `/usage` 查看你的 token 消耗。运行 `/insights` 获取过去 30 天使用模式的更全面视图。
:::

<a id="messaging-tips"></a>
## 消息提示

<a id="set-a-home-channel"></a>
### 设置主频道

在你偏好的 Telegram 或 Discord 聊天中使用 `/sethome` 将其指定为主频道。定时任务结果和计划任务输出会发送到这里。如果没有设置，Agent 就没有地方发送主动消息。

<a id="use-title-to-organize-sessions"></a>
### 使用 /title 组织会话

使用 `/title auth-refactor` 或 `/title research-llm-quantization` 为你的会话命名。命名后的会话可以通过 `hermes sessions list` 轻松查找，并通过 `hermes -r "auth-refactor"` 恢复。未命名的会话会堆积起来，变得难以区分。

<a id="dm-pairing-for-team-access"></a>
### 私信配对实现团队访问

与其手动收集用户 ID 来创建白名单，不如启用私信配对。当团队成员向机器人发送私信时，他们会获得一个一次性配对码。你使用 `hermes pairing approve telegram XKGH5N7P` 批准即可——简单又安全。

<a id="tool-progress-display-modes"></a>
### 工具进度显示模式

使用 `/verbose` 控制你看到的工具活动量。在消息平台上，少即是多——保持为"new"模式，只查看新的工具调用。在 CLI 中，"all"模式能让你实时看到 Agent 所做的一切，体验更佳。

:::tip
在消息平台上，会话会在空闲时间（默认：24 小时）后或每天凌晨 4 点自动重置。如果你需要更长的会话，可以在 `~/.hermes/config.yaml` 中按平台进行调整。
:::
<a id="security"></a>
## 安全

<a id="use-docker-for-untrusted-code"></a>
### 使用 Docker 运行不受信任的代码

当处理不受信任的仓库或运行不熟悉的代码时，请使用 Docker 或 Daytona 作为终端后端。在 `.env` 文件中设置 `TERMINAL_BACKEND=docker`。容器内的破坏性命令不会影响宿主系统。

```bash
# In your .env:
TERMINAL_BACKEND=docker
TERMINAL_DOCKER_IMAGE=hermes-sandbox:latest
```

<a id="avoid-windows-encoding-pitfalls"></a>
### 避免 Windows 编码陷阱

在 Windows 上，某些默认编码（如 `cp125x`）无法表示所有 Unicode 字符，这会在测试或脚本中写入文件时导致 `UnicodeEncodeError`。

- 优先使用明确的 UTF-8 编码打开文件：

```python
with open("results.txt", "w", encoding="utf-8") as f:
    f.write("✓ All good\n")
```

- 在 PowerShell 中，你也可以将当前会话切换到 UTF-8 编码，以处理控制台和原生命令输出：

```powershell
$OutputEncoding = [Console]::OutputEncoding = [Text.UTF8Encoding]::new($false)
```

这会让 PowerShell 及其子进程使用 UTF-8 编码，有助于避免仅 Windows 环境下出现的故障。

<a id="review-before-choosing-always"></a>
### 选择 "Always" 前请三思

当 agent 触发危险命令审批（如 `rm -rf`、`DROP TABLE` 等）时，你会看到四个选项：**once**、**session**、**always**、**deny**。在选择 "always" 之前请仔细考虑——它会将该模式永久加入白名单。建议先选 "session"，直到你熟悉为止。

<a id="command-approval-is-your-safety-net"></a>
### 命令审批是您的安全网

Hermes 在执行前会对照一份精心维护的危险模式列表检查每条命令。这包括递归删除、SQL 删除、将 curl 输出通过管道传给 shell 等。不要在生产环境中禁用它——它的存在是有充分理由的。

:::warning
当在容器后端（Docker、Singularity、Modal、Daytona）中运行时，危险命令检查会被**跳过**，因为容器本身就是安全边界。请确保你的容器镜像已妥善锁定。
:::

<a id="use-allowlists-for-messaging-bots"></a>
### 为消息机器人使用白名单

切勿在具有终端访问权限的机器人上设置 `GATEWAY_ALLOW_ALL_USERS=true`。始终使用平台特定的白名单（`TELEGRAM_ALLOWED_USERS`、`DISCORD_ALLOWED_USERS`）或 DM 配对来控制谁可以与你的 agent 交互。

```bash
# Recommended: explicit allowlists per platform
TELEGRAM_ALLOWED_USERS=123456789,987654321
DISCORD_ALLOWED_USERS=123456789012345678

# Or use cross-platform allowlist
GATEWAY_ALLOWED_USERS=123456789,987654321
```

---

*有应该收录在本页的技巧？欢迎提交 issue 或 PR——社区贡献永远受欢迎。*
