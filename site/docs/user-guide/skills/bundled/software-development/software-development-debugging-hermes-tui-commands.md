---
title: "调试 Hermes TUI 命令 — 调试 Hermes TUI 斜杠命令：Python、网关、Ink UI"
sidebar_label: "调试 Hermes TUI 命令"
description: "调试 Hermes TUI 斜杠命令：Python、网关、Ink UI"
---

{/* 此页面由技能目录中的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# 调试 Hermes TUI 命令 {#debugging-hermes-tui-commands}

调试 Hermes TUI 斜杠命令：Python、网关、Ink UI。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/software-development/debugging-hermes-tui-commands` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 标签 | `debugging`, `hermes-agent`, `tui`, `slash-commands`, `typescript`, `python` |
| 相关技能 | [`python-debugpy`](/user-guide/skills/bundled/software-development/software-development-python-debugpy), [`node-inspect-debugger`](/user-guide/skills/bundled/software-development/software-development-node-inspect-debugger), [`systematic-debugging`](/user-guide/skills/bundled/software-development/software-development-systematic-debugging) |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是技能激活时 Agent 看到的指令。
:::

# 调试 Hermes TUI 斜杠命令 {#debugging-hermes-tui-slash-commands}

## 概述 {#overview}

Hermes 斜杠命令跨越三个层次——Python 命令注册表、tui_gateway JSON-RPC 桥接层，以及 Ink/TypeScript 前端。当某个命令行为异常（自动补全中缺失、在 CLI 中正常但在 TUI 中失效、配置已持久化但 UI 未更新）时，问题几乎总是某一层与其他层不同步导致的。

当你在 Hermes TUI 中遇到斜杠命令相关问题时，请使用此技能，尤其是当命令未出现在自动补全中、在 TUI 中无法正常工作，或者需要添加/更新命令时。

## 何时使用 {#when-to-use}

- 斜杠命令存在于代码库的某一部分，但无法完全正常工作
- 需要在后端和前端同时添加某个命令
- 特定命令的自动补全功能失效
- 命令在 CLI 和 TUI 中的行为不一致
- 命令持久化了配置，但未在 TUI 中实时生效

## 架构概览 {#architecture-overview}

<!-- ascii-guard-ignore -->
```
Python 后端 (hermes_cli/commands.py)     <- 权威 COMMAND_REGISTRY
       │
       ▼
TUI 网关 (tui_gateway/server.py)         <- slash.exec / command.dispatch
       │
       ▼
TUI 前端 (ui-tui/src/app/slash/)        <- 本地处理器 + 降级处理
```
<!-- ascii-guard-ignore-end -->

命令定义必须在 Python 和 TypeScript 中一致注册，才能正常工作。Python 的 `COMMAND_REGISTRY` 是以下内容的权威来源：CLI 分发、网关帮助、Telegram BotCommand 菜单、Slack 子命令映射，以及发送给 Ink 的自动补全数据。

## 调查步骤 {#investigation-steps}

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
3. **检查命令是否存在于 Python 后端：**
   ```bash
   search_files --pattern "CommandDef" --file_glob "*.py" --path hermes_cli/
   search_files --pattern "commandname" --path hermes_cli/commands.py --context 3
   ```

4. **检查网关实现：**
   ```bash
   search_files --pattern "complete.slash|slash.exec" --path tui_gateway/
   ```

## 修复：缺少命令自动补全 {#fix-missing-command-autocomplete}

如果命令在 TUI 中存在但自动补全不显示：

1. 在 `hermes_cli/commands.py` 的 `COMMAND_REGISTRY` 中添加一个 `CommandDef` 条目：
   ```python
   CommandDef("commandname", "Description of the command", "Session",
              cli_only=True, aliases=("alias",),
              args_hint="[arg1|arg2|arg3]",
              subcommands=("arg1", "arg2", "arg3")),
   ```

2. 仔细选择 `cli_only` 与网关可用性：
   - `cli_only=True` — 仅在交互式 CLI/TUI 中可用
   - `gateway_only=True` — 仅在消息平台中可用
   - 两者都不设置 — 所有地方都可用
   - `gateway_config_gate="display.foo"` — 在网关中通过配置控制可用性

3. 确保 `subcommands` 与 TUI 显示的预期 Tab 补全选项匹配。

4. 如果命令在服务端运行，在 `cli.py` 的 `HermesCLI.process_command()` 中添加一个处理器：
   ```python
   elif canonical == "commandname":
       self._handle_commandname(cmd_original)
   ```

5. 对于网关可用的命令，在 `gateway/run.py` 中添加一个处理器：
   ```python
   if canonical == "commandname":
       return await self._handle_commandname(event)
   ```

## 常见问题 {#common-issues}

1. **命令在 TUI 中显示但不在自动补全中。** 命令在 TUI 代码库中已定义，但缺少 `hermes_cli/commands.py` 中的 `COMMAND_REGISTRY` 条目。自动补全数据来自 Python。

2. **命令在自动补全中显示但无法工作。** 检查 `tui_gateway/server.py` 中的命令处理器和 `ui-tui/src/app/createSlashHandler.ts` 中的前端处理器。如果命令仅在 Ink 中本地可用，则必须在 `app.tsx` 的内置分支中处理；否则会回退到 `slash.exec`，并且必须有一个 Python 处理器。

3. **命令在 CLI 和 TUI 中的行为不同。** 命令可能有不同的实现。检查 `cli.py::process_command` 和 TUI 的本地处理器。本地 TUI 处理器优先于网关分发。

4. **命令持久化了配置但未实时生效。** 对于 TUI 本地命令，仅更新 `config.set` 是不够的。还需要立即更新相关的 nanostore 状态（通常使用 `patchUiState(...)`），并通过渲染组件传递任何新状态。例如：`/details collapsed` 必须实时更新详情可见性，而不仅仅是保存 `details_mode`；会话内的全局 `/details &lt;mode&gt;` 可能需要一个单独的命令覆盖标志，以便实时命令可以覆盖内置部分默认值，同时启动/配置同步保留默认展开的思考/工具行为。

5. **网关分发静默忽略命令。** 网关只分发它知道的命令。检查 `GATEWAY_KNOWN_COMMANDS`（自动从 `COMMAND_REGISTRY` 派生）是否包含规范名称。如果命令是 `cli_only` 并带有 `gateway_config_gate`，请验证该门控配置值是否为真。
## 调试策略 {#debugging-tactics}

当表面层级的检查无法发现 bug 时：

- **Python 侧卡死或行为异常：** 使用 `python-debugpy` skill 在 `_SlashWorker.exec` 或命令处理函数内打断点。在处理入口处设置 `remote-pdb` 是最快的路径。
- **Ink 侧无响应：** 使用 `node-inspect-debugger` skill 在 `app.tsx` 的斜杠分发逻辑或本地命令分支处打断点。执行 `npm run build` 后使用 `sb('dist/app.js', &lt;line&gt;)`。
- **注册表不匹配 / 不确定哪一侧有问题：** 将规范的 `COMMAND_REGISTRY` 条目与 TUI 的本地命令列表逐一对比。

## 常见陷阱 {#pitfalls}

- 别忘了在 `CommandDef` 中为命令设置合适的类别（例如："Session"、"Configuration"、"Tools & Skills"、"Info"、"Exit"）
- 确保所有别名都正确注册在 `aliases` 元组中——无需修改其他文件，下游的一切（Telegram 菜单、Slack 映射、自动补全、帮助信息）都由此派生
- 对于带子命令的命令，确保 `CommandDef` 中的 `subcommands` 元组与 TUI 代码中的一致
- 标记为 `cli_only=True` 的命令无法在网关/消息平台中使用——除非你添加了一个 `gateway_config_gate` 并且该门控为真值
- 添加实时 UI 状态后，请搜索所有使用了旧属性/辅助函数的地方，并将新状态贯穿到所有渲染路径中，而不仅仅是活跃的流式路径。TUI 详情渲染至少有两个重要路径：实时 `StreamingAssistant`/`ToolTrail` 以及转录/待处理 `MessageLine` 行。一次 `/clean` 操作应当显式检查两者。
- 在测试前重新构建 TUI（`npm --prefix ui-tui run build`）——tsx watch 模式在首次启动时可能会滞后

## 验证 {#verification}

修复后：

1. 重新构建 TUI：
   ```bash
   cd /home/bb/hermes-agent && npm --prefix ui-tui run build
   ```

2. 运行 TUI 并测试命令：
   ```bash
   hermes --tui
   ```

3. 输入 `/` 并验证命令是否出现在自动补全建议中，且带有预期的描述和参数提示。

4. 执行命令并确认：
   - 预期行为已触发
   - 任何持久化的配置已正确更新（`read_file ~/.hermes/config.yaml`）
   - 实时 UI 状态立即反映了更改（不仅仅是重启后）

5. 如果该命令也可在网关中使用，请至少从一个消息平台测试它（或运行网关测试：`scripts/run_tests.sh tests/gateway/`）。
