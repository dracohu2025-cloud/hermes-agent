---
title: "Openclaw 迁移 — 将用户的 OpenClaw 自定义配置迁移到 Hermes Agent 中"
sidebar_label: "Openclaw 迁移"
description: "将用户的 OpenClaw 自定义配置迁移到 Hermes Agent 中"
---

{/* 此页由 website/scripts/generate-skill-docs.py 从技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，不要编辑此页。 */}

# Openclaw 迁移 {#openclaw-migration}

将用户的 OpenClaw 自定义配置迁移到 Hermes Agent 中。从 `~/.openclaw` 导入兼容 Hermes 的记忆、SOUL.md、命令允许列表、用户技能以及选定的工作区资产，然后精确报告哪些内容无法迁移及其原因。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/migration/openclaw-migration` 安装 |
| 路径 | `optional-skills/migration/openclaw-migration` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent (Nous Research) |
| 许可证 | MIT |
| 标签 | `Migration`, `OpenClaw`, `Hermes`, `Memory`, `Persona`, `Import` |
| 相关技能 | [`hermes-agent`](/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-hermes-agent) |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是此技能被触发时 Hermes 加载的完整技能定义。这是技能激活时 Agent 看到的指令。
:::

# OpenClaw -> Hermes 迁移 {#openclaw-hermes-migration}

当用户希望以最少的手动清理工作将 OpenClaw 配置迁移到 Hermes Agent 时，使用此技能。

## CLI 命令 {#cli-command}

如需快速、非交互式的迁移，请使用内置的 CLI 命令：

```bash
hermes claw migrate              # 完整交互式迁移
hermes claw migrate --dry-run    # 预览将迁移的内容
hermes claw migrate --preset user-data   # 迁移时不包含机密
hermes claw migrate --overwrite  # 覆盖已有冲突
hermes claw migrate --source /custom/path/.openclaw  # 自定义源路径
```

CLI 命令会运行下文所述的同一个迁移脚本。当你希望通过交互式引导迁移，并附带 dry-run 预览和逐项冲突解决时，可使用此技能（通过 Agent）。

**首次设置：** `hermes setup` 向导会自动检测 `~/.openclaw` 并提供迁移选项，在开始配置之前。

## 此技能的功能 {#what-this-skill-does}

它使用 `scripts/openclaw_to_hermes.py` 来：

- 将 `SOUL.md` 以 `SOUL.md` 的名称导入 Hermes 主目录
- 将 OpenClaw 的 `MEMORY.md` 和 `USER.md` 转换为 Hermes 记忆条目
- 将 OpenClaw 命令审批模式合并到 Hermes 的 `command_allowlist` 中
- 迁移兼容 Hermes 的消息设置，如 `TELEGRAM_ALLOWED_USERS` 和 `MESSAGING_CWD`
- 将 OpenClaw 技能复制到 `~/.hermes/skills/openclaw-imports/`
- 可选地将 OpenClaw 工作区指令文件复制到选定的 Hermes 工作区
- 将兼容的工作区资产（如 `workspace/tts/`）镜像到 `~/.hermes/tts/`
- 归档没有直接 Hermes 目标的非机密文档
- 生成结构化的报告，列出已迁移项、冲突项、跳过项及其原因

## 路径解析 {#path-resolution}

辅助脚本位于此技能目录中：

- `scripts/openclaw_to_hermes.py`

当此技能从 Skills Hub 安装时，通常的位置为：

- `~/.hermes/skills/migration/openclaw-migration/scripts/openclaw_to_hermes.py`
不要猜测像 `~/.hermes/skills/openclaw-migration/...` 这样的短路径。

在运行辅助脚本之前：

1. 优先使用 `~/.hermes/skills/migration/openclaw-migration/` 下的安装路径。
2. 如果该路径失败，检查已安装的技能目录，并相对于已安装的 `SKILL.md` 解析脚本。
3. 仅当安装位置缺失或技能被手动移动时，才将 `find` 作为后备方案使用。
4. 调用终端工具时，不要传递 `workdir: "~"`。应使用绝对目录（例如用户的主目录），或完全省略 `workdir`。

使用 `--migrate-secrets` 参数时，它还会导入一小部分允许列表中的 Hermes 兼容密钥，目前包括：

- `TELEGRAM_BOT_TOKEN`

## 默认工作流程 {#default-workflow}

1. 先通过空运行进行检查。
2. 呈现一个简单的摘要，说明哪些可以迁移、哪些不能迁移、哪些将被归档。
3. 如果 `clarify` 工具可用，则使用它来获取用户决策，而不是要求用户提供自由格式的文本回复。
4. 如果空运行发现导入的技能目录存在冲突，在执行前询问如何处理这些冲突。
5. 在执行前，让用户在两种支持的迁移模式中选择。
6. 仅当用户希望将工作区指令文件迁移过来时，才询问目标工作区路径。
7. 使用匹配的预设和标志执行迁移。
8. 总结结果，特别是：
   - 哪些已迁移
   - 哪些已归档以供人工审查
   - 哪些被跳过及其原因

## 用户交互协议 {#user-interaction-protocol}

Hermes CLI 支持使用 `clarify` 工具进行交互式提示，但其限制为：

- 一次只能选择一个选项
- 最多 4 个预定义选项
- 一个自动的 `其他` 自由文本选项

它**不**支持在单个提示中进行真正的多选复选框。

对于每次 `clarify` 调用：

- 始终包含一个非空的 `question`
- 仅对真正的可选项提示包含 `choices`
- 将 `choices` 保持在 2-4 个纯字符串选项
- 永远不要发出占位符或截断的选项，例如 `...`
- 永远不要用额外的空格填充或修饰选项
- 永远不要在问题中包含虚假的表单字段，例如 `在此输入目录`、要填写的空行，或像 `_____` 这样的下划线
- 对于开放式的路径问题，只问简单的句子；用户在面板下方的正常 CLI 提示符中输入

如果 `clarify` 调用返回错误，请检查错误文本，修正负载，并使用有效的 `question` 和干净的 `choices` 重试一次。

当 `clarify` 可用且空运行揭示了任何需要用户决策的事项时，你的**下一步操作必须是调用 `clarify` 工具**。
不要以普通的助手消息结束本轮对话，例如：

- "让我呈现选项"
- "你想做什么？"
- "以下是选项"

如果需要用户决策，请在生成更多文本之前通过 `clarify` 收集它。
如果存在多个未解决的决策，不要在它们之间插入解释性的助手消息。在收到一个 `clarify` 响应后，你的下一步操作通常应该是下一个必要的 `clarify` 调用。
当 dry run 报告出现以下情况时，将 `workspace-agents` 视为未解决的决策：

- `kind="workspace-agents"`
- `status="skipped"`
- 原因中包含 `No workspace target was provided`

在这种情况下，你必须在执行前询问 workspace 指令。不要默默将其视为跳过决策。

由于这个限制，请使用以下简化的决策流程：

1. 对于 `SOUL.md` 冲突，使用 `clarify`，选项包括：
   - `keep existing`
   - `overwrite with backup`
   - `review first`
2. 如果 dry run 显示一个或多个 `kind="skill"` 项且 `status="conflict"`，使用 `clarify`，选项包括：
   - `keep existing skills`
   - `overwrite conflicting skills with backup`
   - `import conflicting skills under renamed folders`
3. 对于 workspace 指令，使用 `clarify`，选项包括：
   - `skip workspace instructions`
   - `copy to a workspace path`
   - `decide later`
4. 如果用户选择复制 workspace 指令，则追问一个开放式的 `clarify` 问题，要求提供**绝对路径**。
5. 如果用户选择 `skip workspace instructions` 或 `decide later`，则不带 `--workspace-target` 继续执行。
5. 对于迁移模式，使用 `clarify`，提供以下 3 个选项：
   - `user-data only`
   - `full compatible migration`
   - `cancel`
6. `user-data only` 表示：迁移用户数据和兼容配置，但**不**导入允许列表中的密钥。
7. `full compatible migration` 表示：迁移相同的兼容用户数据，并在存在时导入允许列表中的密钥。
8. 如果 `clarify` 不可用，则用普通文本提出相同问题，但仍将答案限制为 `user-data only`、`full compatible migration` 或 `cancel`。

执行门控：

- 当 `workspace-agents` 因 `No workspace target was provided` 被跳过且未解决时，不得执行。
- 解决该问题的唯一有效方式是：
  - 用户明确选择 `skip workspace instructions`
  - 用户明确选择 `decide later`
  - 用户在选择 `copy to a workspace path` 后提供 workspace 路径
- dry run 中缺少 workspace target 本身并不代表允许执行。
- 当任何必需的 `clarify` 决策未解决时，不得执行。

使用以下精确的 `clarify` 载荷形状作为默认模式：

- `{"question":"Your existing SOUL.md conflicts with the imported one. What should I do?","choices":["keep existing","overwrite with backup","review first"]}`
- `{"question":"One or more imported OpenClaw skills already exist in Hermes. How should I handle those skill conflicts?","choices":["keep existing skills","overwrite conflicting skills with backup","import conflicting skills under renamed folders"]}`
- `{"question":"Choose migration mode: migrate only user data, or run the full compatible migration including allowlisted secrets?","choices":["user-data only","full compatible migration","cancel"]}`
- `{"question":"Do you want to copy the OpenClaw workspace instructions file into a Hermes workspace?","choices":["skip workspace instructions","copy to a workspace path","decide later"]}`
- `{"question":"Please provide an absolute path where the workspace instructions should be copied."}`
## 决策到命令映射 {#decision-to-command-mapping}

将用户决策精确映射到命令标志：

- 如果用户对 `SOUL.md` 选择了“保留现有”，则**不要**添加 `--overwrite`。
- 如果用户选择了“覆盖并备份”，则添加 `--overwrite`。
- 如果用户选择了“先审查”，则在执行前停止并审查相关文件。
- 如果用户选择了“保留现有技能”，则添加 `--skill-conflict skip`。
- 如果用户选择了“覆盖冲突技能并备份”，则添加 `--skill-conflict overwrite`。
- 如果用户选择了“在重命名文件夹下导入冲突技能”，则添加 `--skill-conflict rename`。
- 如果用户选择了“仅用户数据”，则使用 `--preset user-data` 执行，并且**不要**添加 `--migrate-secrets`。
- 如果用户选择了“完整兼容迁移”，则使用 `--preset full --migrate-secrets` 执行。
- 仅当用户明确提供了绝对工作区路径时，才添加 `--workspace-target`。
- 如果用户选择了“跳过工作区说明”或“稍后决定”，则不要添加 `--workspace-target`。

在执行之前，用通俗语言重述确切的命令计划，并确保它与用户的选择一致。

## 运行后报告规则 {#post-run-reporting-rules}

执行后，将脚本的 JSON 输出视为事实来源。

1. 所有计数基于 `report.summary`。
2. 仅当条目的 `status` 正好为 `migrated` 时，才将其列在“成功迁移”下。
3. 除非报告显示该条目为 `migrated`，否则不要声称冲突已解决。
4. 除非 `kind="soul"` 的报告项具有 `status="migrated"`，否则不要说 `SOUL.md` 已被覆盖。
5. 如果 `report.summary.conflict > 0`，则需包含冲突部分，而不是默默暗示成功。
6. 如果计数与列出的条目不一致，则在回复前修正列表以匹配报告。
7. 当报告中提供 `output_dir` 路径时，包含该路径，以便用户可以检查 `report.json`、`summary.md`、备份和归档文件。
8. 对于内存或用户配置文件溢出，除非报告明确显示归档路径，否则不要声称条目已归档。如果存在 `details.overflow_file`，则说明完整的溢出列表已导出到该位置。
9. 如果技能是在重命名的文件夹下导入的，请报告最终目标位置，并提及 `details.renamed_from`。
10. 如果存在 `report.skill_conflict_mode`，则将其用作所选导入技能冲突策略的事实来源。
11. 如果条目具有 `status="skipped"`，则不要将其描述为已覆盖、已备份、已迁移或已解决。
12. 如果 `kind="soul"` 具有 `status="skipped"` 且原因为 `Target already matches source`，则说明它保持不变，并且不要提及备份。
13. 如果重命名的导入技能具有空的 `details.backup`，则不要暗示现有的 Hermes 技能已被重命名或备份。只说导入的副本已放置在新目标中，并引用 `details.renamed_from` 作为保持原样的预先存在的文件夹。

## 迁移预设 {#migration-presets}

在正常使用中优先选择以下两个预设：

- `user-data`
- `full`

`user-data` 包括：

- `soul`
- `workspace-agents`
- `memory`
- `user-profile`
- `messaging-settings`
- `command-allowlist`
- `skills`
- `tts-assets`
- `archive`
`full` 包含 `user-data` 中的所有内容，外加：

- `secret-settings`

辅助脚本仍然支持类别级别的 `--include` / `--exclude`，但请将其视为高级回退方案，而非默认的用户体验。

## 命令 {#commands}

带完整发现的试运行：

```bash
python3 ~/.hermes/skills/migration/openclaw-migration/scripts/openclaw_to_hermes.py
```

使用终端工具时，建议采用绝对路径调用方式，例如：

```json
{"command":"python3 /home/USER/.hermes/skills/migration/openclaw-migration/scripts/openclaw_to_hermes.py","workdir":"/home/USER"}
```

使用 user-data 预设的试运行：

```bash
python3 ~/.hermes/skills/migration/openclaw-migration/scripts/openclaw_to_hermes.py --preset user-data
```

执行 user-data 迁移：

```bash
python3 ~/.hermes/skills/migration/openclaw-migration/scripts/openclaw_to_hermes.py --execute --preset user-data --skill-conflict skip
```

执行完整兼容迁移：

```bash
python3 ~/.hermes/skills/migration/openclaw-migration/scripts/openclaw_to_hermes.py --execute --preset full --migrate-secrets --skill-conflict skip
```

包含工作区指令的执行：

```bash
python3 ~/.hermes/skills/migration/openclaw-migration/scripts/openclaw_to_hermes.py --execute --preset user-data --skill-conflict rename --workspace-target "/absolute/workspace/path"
```

默认不要使用 `$PWD` 或家目录作为工作区目标。请先询问明确的工作区路径。

## 重要规则 {#important-rules}

1. 除非用户明确要求立即执行，否则先进行试运行再写入。
2. 默认不迁移密钥。令牌、认证 blob、设备凭据和原始网关配置应保留在 OpenClaw 之外，除非用户明确要求迁移密钥。
3. 除非用户明确要求，否则不要静默覆盖非空的 Hermes 目标。启用覆盖时，辅助脚本会保留备份。
4. 始终向用户提供跳过的项目报告。该报告是迁移的一部分，不是可选的附加项。
5. 优先使用主 OpenClaw 工作区（`~/.openclaw/workspace/`），而不是 `workspace.default/`。仅当主文件缺失时，才将默认工作区作为回退。
6. 即使在密钥迁移模式下，也只迁移目标位置为空的 Hermes 密钥。不支持的认证 blob 仍必须报告为已跳过。
7. 如果试运行显示大量资产复制、冲突的 `SOUL.md` 或溢出的内存条目，请在执行前单独指出。
8. 如果用户不确定，默认选择 `user-data only`。
9. 仅当用户明确提供了目标工作区路径时，才包含 `workspace-agents`。
10. 将类别级别的 `--include` / `--exclude` 视为高级逃生舱，而非正常流程。
11. 如果可以使用 `clarify`，不要用模糊的“你想做什么？”来结束试运行摘要。应使用结构化的后续提示。
12. 当实际的选择提示可用时，不要使用开放式的 `clarify` 提示。优先使用可选项，仅对绝对路径或文件审查请求使用自由文本。
13. 试运行后，如果仍有未解决的决策，不要只做总结就停止。立即使用 `clarify` 处理优先级最高的阻塞决策。
14. 后续问题的优先级顺序：
    - `SOUL.md` 冲突
    - 导入的技能冲突
    - 迁移模式
    - 工作区指令目标
15. 不要在同一消息中承诺稍后呈现选项。应通过实际调用 `clarify` 来呈现。
16. 在迁移模式回答之后，明确检查 `workspace-agents` 是否仍未解决。如果是，你的下一步操作必须是工作区指令的 `clarify` 调用。
17. 在任何 `clarify` 回答之后，如果仍有其他必需的决策，不要叙述刚刚决定了什么。立即询问下一个必需的问题。
## 预期结果 {#expected-result}

成功运行后，用户应获得以下结果：

- Hermes 角色状态已导入
- Hermes 记忆文件已填充转换后的 OpenClaw 知识
- OpenClaw 技能位于 `~/.hermes/skills/openclaw-imports/` 目录下
- 一份迁移报告，显示所有冲突、遗漏或不支持的数据
