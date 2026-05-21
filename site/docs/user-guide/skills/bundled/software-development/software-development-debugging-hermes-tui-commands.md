---
title: "调试 Hermes TUI 命令 — 调试 Hermes TUI 斜杠命令：Python、网关、Ink UI"
sidebar_label: "调试 Hermes TUI 命令"
description: "调试 Hermes TUI 斜杠命令：Python、网关、Ink UI"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。如有修改请编辑源文件 SKILL.md，而不是本页面。 */}

<a id="debugging-hermes-tui-commands"></a>
# 调试 Hermes TUI 命令

调试 Hermes TUI 斜杠命令：Python、网关、Ink UI。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/software-development/debugging-hermes-tui-commands` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent |
| 许可 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `debugging`, `hermes-agent`, `tui`, `slash-commands`, `typescript`, `python` |
| 相关技能 | [`python-debugpy`](/user-guide/skills/bundled/software-development/software-development-python-debugpy), [`node-inspect-debugger`](/user-guide/skills/bundled/software-development/software-development-node-inspect-debugger), [`systematic-debugging`](/user-guide/skills/bundled/software-development/software-development-systematic-debugging) |

<a id="reference-full-skill-md"></a>
## 参考：完整的 SKILL.md

:::info
以下是此技能被触发时 Hermes 加载的完整技能定义。这就是 Agent 在该技能激活时看到的指令。
:::

<a id="debugging-hermes-tui-slash-commands"></a>
# 调试 Hermes TUI 斜杠命令

<a id="overview"></a>
## 概述

Hermes 斜杠命令横跨三个层次——Python 命令注册表、`tui_gateway` JSON-RPC 桥接层以及 Ink/TypeScript 前端。当某个命令行为异常（自动补全缺失、在 CLI 中可用但在 TUI 中不行、配置已持久化但 UI 未更新）时，问题几乎总是出在某个层次与其他层次不同步。

当你在 Hermes TUI 中遇到斜杠命令的问题时，请使用本技能，特别是当命令未显示在自动补全中、在 TUI 中无法正常工作，或者需要添加/更新命令时。

<a id="when-to-use"></a>
## 何时使用

- 某个斜杠命令存在于代码库的一部分，但无法完整工作
- 需要在后端和前端同时添加一个命令
- 特定命令的自动补全不起作用
- 命令行为在 CLI 和 TUI 之间不一致
- 某个命令持久化了配置，但没有在 TUI 中实时生效

<a id="architecture-overview"></a>
## 架构概览

<!-- ascii-guard-ignore -->
```
Python 后端 (hermes_cli/commands.py)     <- 权威 COMMAND_REGISTRY
       │
       ▼
TUI 网关 (tui_gateway/server.py)         <- slash.exec / command.dispatch
       │
       ▼
TUI 前端 (ui-tui/src/app/slash/)        <- 本地处理器 + 穿透
```
<!-- ascii-guard-ignore-end -->

命令定义必须在 Python 和 TypeScript 中一致注册才能正常工作。Python 的 `COMMAND_REGISTRY` 是以下内容的权威来源：CLI 分发、网关帮助、Telegram BotCommand 菜单、Slack 子命令映射以及发送到 Ink 的自动补全数据。

<a id="investigation-steps"></a>
## 调查步骤

1. **检查命令是否存在于 TUI 前端：**
   ```bash
   search_files --pattern "/commandname" --file_glob "*.ts" --path ui-tui/
   search_files --pattern "/commandname" --file_glob "*.tsx" --path ui-tui/
   ```

2. **检查 TUI 命令定义：**
   ```bash
   read_file ui-tui/src/app/slash/commands/core.ts
   # 如果不在那里：
   search_files --pattern "commandname" --path ui-tui/src/app/slash/commands --target files
   ```
3. **检查该命令是否存在于 Python 后端：**
   ```bash
   search_files --pattern "CommandDef" --file_glob "*.py" --path hermes_cli/
   search_files --pattern "commandname" --path hermes_cli/commands.py --context 3
   ```

4. **检查网关实现：**
   ```bash
   search_files --pattern "complete.slash|slash.exec" --path tui_gateway/
   ```

<a id="fix-missing-command-autocomplete"></a>
## 修复：缺少命令自动补全

如果指令存在于 TUI 中但未出现在自动补全列表：

1. 在 `hermes_cli/commands.py` 的 `COMMAND_REGISTRY` 中添加 `CommandDef` 条目：
   ```python
   CommandDef("commandname", "Description of the command", "Session",
              cli_only=True, aliases=("alias",),
              args_hint="[arg1|arg2|arg3]",
              subcommands=("arg1", "arg2", "arg3")),
   ```

2. 仔细选择 `cli_only` 与网关可用性：
   - `cli_only=True` – 仅出现在交互式 CLI/TUI 中
   - `gateway_only=True` – 仅出现在消息平台中
   - 都不设置 – 所有地方可用
   - `gateway_config_gate="display.foo"` – 网关中通过配置控制可用性

3. 确保 `subcommands` 与 TUI 显示的预期 Tab 补全选项一致。

4. 如果命令在服务端运行，在 `cli.py` 的 `HermesCLI.process_command()` 中添加处理函数：
   ```python
   elif canonical == "commandname":
       self._handle_commandname(cmd_original)
   ```

5. 对于网关可用的命令，在 `gateway/run.py` 中添加处理函数：
   ```python
   if canonical == "commandname":
       return await self._handle_commandname(event)
   ```

<a id="common-issues"></a>
## 常见问题

1. **命令在 TUI 中显示但不在自动补全中。** 命令已在 TUI 代码库中定义，但缺少在 `hermes_cli/commands.py` 的 `COMMAND_REGISTRY` 中的定义。自动补全数据来自 Python。

2. **命令显示在自动补全中但无法执行。** 检查 `tui_gateway/server.py` 中的命令处理函数和 `ui-tui/src/app/createSlashHandler.ts` 中的前端处理函数。如果命令在 Ink 中是本地专用的，则必须在 `app.tsx` 的内置分支中处理；否则它会落入 `slash.exec`，必须有 Python 处理函数。

3. **命令行为在 CLI 和 TUI 之间不同。** 命令可能存在不同的实现。同时检查 `cli.py::process_command` 和 TUI 的本地处理函数。本地 TUI 处理函数优先于网关分发。

4. **命令持久化配置但未实时生效。** 对于 TUI 本地命令，仅更新 `config.set` 是不够的。还需要立即更新相关的 nanostore 状态（通常是 `patchUiState(...)`），并通过渲染组件传递新状态。例如：`/details collapsed` 必须实时更新详情可见性，而不仅仅是保存 `details_mode`；会话中的全局 `/details &lt;mode&gt;` 可能需要一个单独的命令覆盖标志，以便实时命令可以覆盖内置部分默认值，同时启动/配置同步保留默认展开的思考/工具行为。

5. **网关分发静默忽略该命令。** 网关只分发它知道的命令。检查 `GATEWAY_KNOWN_COMMANDS`（自动从 `COMMAND_REGISTRY` 派生）是否包含该规范名称。如果命令是 `cli_only` 且带有 `gateway_config_gate`，请验证该 gated 配置值是否为真值。
<a id="debugging-tactics"></a>
## 调试策略

当表面检查无法发现 bug 时：

- **Python 端卡死或行为异常：** 使用 `python-debugpy` 技能在 `_SlashWorker.exec` 或命令处理函数中设置断点。在处理器入口处设置 `remote-pdb` 是最快的路径。
- **Ink 端无响应：** 使用 `node-inspect-debugger` 技能在 `app.tsx` 的斜杠命令分发或本地命令分支中设置断点。在 `npm run build` 之后执行 `sb('dist/app.js', &lt;line&gt;)`。
- **注册表不匹配 / 不确定哪一端有问题：** 将规范的 `COMMAND_REGISTRY` 条目与 TUI 的本地命令列表进行逐项对比。

<a id="pitfalls"></a>
## 常见陷阱

- 别忘了在 `CommandDef` 中为命令设置合适的类别（例如 "Session"、"Configuration"、"Tools & Skills"、"Info"、"Exit"）
- 确保所有别名都已正确注册到 `aliases` 元组中——不需要修改其他文件，所有下游功能（Telegram 菜单、Slack 映射、自动补全、帮助信息）都基于此派生
- 对于包含子命令的命令，确保 `CommandDef` 中的 `subcommands` 元组与 TUI 代码中的一致
- `cli_only=True` 的命令在网关/消息平台中无法工作——除非你添加了 `gateway_config_gate` 且该门控条件为真
- 添加实时 UI 状态后，要搜索所有使用旧属性/辅助函数的消费者，并将新状态贯穿到所有渲染路径中，而不仅仅是活跃的流式路径。TUI 详情渲染至少有两个重要路径：实时的 `StreamingAssistant`/`ToolTrail` 和转录/待处理的 `MessageLine` 行。`/clean` 操作应明确检查这两个路径。
- 在测试前重新构建 TUI（`npm --prefix ui-tui run build`）——tsx 监视模式在首次启动时可能会有延迟

<a id="verification"></a>
## 验证

修复后：

1. 重新构建 TUI：
   ```bash
   cd /home/bb/hermes-agent && npm --prefix ui-tui run build
   ```

2. 运行 TUI 并测试命令：
   ```bash
   hermes --tui
   ```

3. 输入 `/` 并验证命令是否出现在自动补全建议中，且显示预期的描述和参数提示。

4. 执行命令并确认：
   - 预期行为已触发
   - 任何持久化的配置已正确更新（`read_file ~/.hermes/config.yaml`）
   - 实时 UI 状态立即反映更改（而不仅仅是在重启后）

5. 如果该命令也可在网关中使用，请至少在一个消息平台上测试（或运行网关测试：`scripts/run_tests.sh tests/gateway/`）。
