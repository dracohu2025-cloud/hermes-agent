---
title: "Openclaw Migration — 将用户的 OpenClaw 定制配置迁移到 Hermes Agent"
sidebar_label: "Openclaw Migration"
description: "将用户的 OpenClaw 定制配置迁移到 Hermes Agent"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 从技能文件的 SKILL.md 自动生成。请编辑源文件 SKILL.md，不要编辑此页面。 */}

<a id="openclaw-migration"></a>
# Openclaw Migration

将用户的 OpenClaw 定制配置迁移到 Hermes Agent。从 `~/.openclaw` 导入兼容 Hermes 的记忆、SOUL.md、命令白名单、用户技能及选定的工作区资源，然后精确报告哪些内容无法迁移及其原因。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/migration/openclaw-migration` 安装 |
| 路径 | `optional-skills/migration/openclaw-migration` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent (Nous Research) |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `Migration`, `OpenClaw`, `Hermes`, `Memory`, `Persona`, `Import` |
| 相关技能 | [`hermes-agent`](/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-hermes-agent) |

<a id="reference-full-skill-md"></a>
## 参考：完整 SKILL.md

:::info
以下是该技能被触发时 Hermes 加载的完整技能定义。当技能激活时，Agent 会看到这些指令。
:::

<a id="openclaw-hermes-migration"></a>
# OpenClaw -> Hermes Migration

当用户希望以最少的手动清理工作将 OpenClaw 配置迁移到 Hermes Agent 时，使用此技能。

<a id="cli-command"></a>
## CLI 命令

如需快速、非交互式的迁移，请使用内置的 CLI 命令：

```bash
hermes claw migrate              # 完整交互式迁移
hermes claw migrate --dry-run    # 预览将要迁移的内容
hermes claw migrate --preset user-data   # 迁移时不包含机密信息
hermes claw migrate --overwrite  # 覆盖现有冲突
hermes claw migrate --source /custom/path/.openclaw  # 自定义源路径
```

CLI 命令执行与下文描述相同的迁移脚本。当你需要经过引导的交互式迁移、支持 dry-run 预览和逐项冲突解决时，可使用此技能（通过 Agent）。

**首次设置：** `hermes setup` 向导会自动检测 `~/.openclaw`，并在配置开始之前提供迁移选项。

<a id="what-this-skill-does"></a>
## 此技能的功能

它使用 `scripts/openclaw_to_hermes.py` 执行以下操作：

- 将 `SOUL.md` 导入到 Hermes 主目录，保存为 `SOUL.md`
- 将 OpenClaw 的 `MEMORY.md` 和 `USER.md` 转换为 Hermes 记忆条目
- 将 OpenClaw 的命令批准模式合并到 Hermes 的 `command_allowlist` 中
- 迁移兼容 Hermes 的消息设置，例如 `TELEGRAM_ALLOWED_USERS` 和 `MESSAGING_CWD`
- 将 OpenClaw 技能复制到 `~/.hermes/skills/openclaw-imports/`
- 可选地将 OpenClaw 工作区指令文件复制到指定的 Hermes 工作区
- 镜像兼容的工作区资源，如 `workspace/tts/`，到 `~/.hermes/tts/`
- 归档没有直接 Hermes 目的地的非机密文档
- 生成结构化的报告，列出已迁移项、冲突项、跳过项及其原因

<a id="path-resolution"></a>
## 路径解析

辅助脚本位于此技能目录中的以下位置：

- `scripts/openclaw_to_hermes.py`

当此技能从 Skills Hub 安装时，其默认位置为：
- `~/.hermes/skills/migration/openclaw-migration/scripts/openclaw_to_hermes.py`

不要猜测更短的路径，比如 `~/.hermes/skills/openclaw-migration/...`。

运行辅助脚本前：

1. 优先使用安装路径 `~/.hermes/skills/migration/openclaw-migration/`。
2. 如果该路径无效，检查已安装的技能目录，并解析相对于已安装的 `SKILL.md` 的脚本路径。
3. 仅当安装位置缺失或技能文件被手动移动时，才使用 `find` 作为备选方案。
4. 调用终端工具时，不要传递 `workdir: "~"`。请使用绝对路径，例如用户的家目录，或者完全省略 `workdir`。

使用 `--migrate-secrets` 参数时，它还会导入一小部分已列入允许列表的、与 Hermes 兼容的密钥，目前包括：

- `TELEGRAM_BOT_TOKEN`

<a id="default-workflow"></a>
## 默认工作流程

1. 首先进行空运行（dry run）检查。
2. 给出一个简单的摘要，说明哪些可以迁移、哪些不能迁移、哪些会被归档。
3. 如果 `clarify` 工具可用，请使用它来获取用户决策，而不是要求用户提供自由格式的文字回复。
4. 如果空运行发现导入的技能目录存在冲突，则在执行前询问如何处理这些冲突。
5. 在执行前，让用户从两种支持的迁移模式中选择一种。
6. 仅当用户希望将工作区说明文件（workspace instructions file）一并带入时，才询问目标工作区路径。
7. 使用匹配的预设和标志执行迁移。
8. 总结结果，尤其要说明：
   - 哪些内容已迁移
   - 哪些内容已归档以供人工审查
   - 哪些内容被跳过以及原因

<a id="user-interaction-protocol"></a>
## 用户交互协议

Hermes CLI 支持 `clarify` 工具进行交互式提示，但其限制如下：

- 每次只能选择一个选项
- 最多提供 4 个预定义选项
- 自动包含一个“其他”自由文本选项

它**不**支持在单次提示中实现真正的多选复选框。

对于每次 `clarify` 调用：

- 始终包含一个非空的 `question`
- 仅对真正的可选项提示包含 `choices`
- 将 `choices` 保持为 2-4 个纯字符串选项
- 切勿发出占位符或截断的选项，例如 `...`
- 切勿用额外空白填充或修饰 `choices`
- 切勿在 `question` 中包含虚拟表单字段，例如 `enter directory here`、待填写的空行，或像 `_____` 这样的下划线
- 对于开放式路径问题，只询问一句简单的句子；用户会在面板下方的普通 CLI 提示符中输入

如果 `clarify` 调用返回错误，请检查错误文本，修正有效载荷，并使用有效的 `question` 和干净的选项重试一次。

当 `clarify` 可用且空运行显示需要用户做出任何决策时，你的**下一步行动必须是调用 `clarify` 工具**。
不要用普通的助手消息结束本轮对话，例如：

- "我来展示选项"
- "你想怎么做？"
- "这里是选项"

如果需要用户决策，请先通过 `clarify` 收集，然后再生成更多文字。
如果还有多个未解决的决策，不要在它们之间插入解释性的助手消息。收到一个 `clarify` 响应后，你的下一步行动通常应该是下一个必需的 `clarify` 调用。
当试运行报告出现以下情况时，将 `workspace-agents` 视为未解决的决策：

- `kind="workspace-agents"`
- `status="skipped"`
- 原因包含 `No workspace target was provided`

在这种情况下，你必须在执行前询问工作区指令。不要默默将其视为跳过决策。

由于这个限制，请使用以下简化的决策流程：

1. 对于 `SOUL.md` 冲突，使用 `clarify` 并提供以下选项：
   - `keep existing`（保留现有）
   - `overwrite with backup`（用备份覆盖）
   - `review first`（先审查）
2. 如果试运行显示一个或多个 `kind="skill"` 项的状态为 `status="conflict"`，使用 `clarify` 并提供以下选项：
   - `keep existing skills`（保留现有技能）
   - `overwrite conflicting skills with backup`（用备份覆盖冲突技能）
   - `import conflicting skills under renamed folders`（在重命名文件夹下导入冲突技能）
3. 对于工作区指令，使用 `clarify` 并提供以下选项：
   - `skip workspace instructions`（跳过工作区指令）
   - `copy to a workspace path`（复制到工作区路径）
   - `decide later`（稍后决定）
4. 如果用户选择复制工作区指令，则提出一个后续的开放式 `clarify` 问题，要求提供**绝对路径**。
5. 如果用户选择 `skip workspace instructions` 或 `decide later`，则不带 `--workspace-target` 继续执行。
5. 对于迁移模式，使用 `clarify` 并提供以下 3 个选项：
   - `user-data only`（仅用户数据）
   - `full compatible migration`（完整兼容迁移）
   - `cancel`（取消）
6. `user-data only` 表示：迁移用户数据和兼容配置，但**不**导入允许列表中的密钥。
7. `full compatible migration` 表示：迁移相同的兼容用户数据，并在存在时导入允许列表中的密钥。
8. 如果 `clarify` 不可用，则用普通文本提出相同的问题，但仍将答案限制为 `user-data only`、`full compatible migration` 或 `cancel`。

执行门控：

- 当 `workspace-agents` 因 `No workspace target was provided` 被跳过且未解决时，不要执行。
- 解决该问题的唯一有效方式是：
  - 用户明确选择 `skip workspace instructions`
  - 用户明确选择 `decide later`
  - 用户在选择 `copy to a workspace path` 后提供工作区路径
- 试运行中缺少工作区目标本身并不代表允许执行。
- 当任何必需的 `clarify` 决策未解决时，不要执行。

使用以下精确的 `clarify` 载荷形状作为默认模式：

- `{"question":"Your existing SOUL.md conflicts with the imported one. What should I do?","choices":["keep existing","overwrite with backup","review first"]}`
- `{"question":"One or more imported OpenClaw skills already exist in Hermes. How should I handle those skill conflicts?","choices":["keep existing skills","overwrite conflicting skills with backup","import conflicting skills under renamed folders"]}`
- `{"question":"Choose migration mode: migrate only user data, or run the full compatible migration including allowlisted secrets?","choices":["user-data only","full compatible migration","cancel"]}`
- `{"question":"Do you want to copy the OpenClaw workspace instructions file into a Hermes workspace?","choices":["skip workspace instructions","copy to a workspace path","decide later"]}`
- `{"question":"Please provide an absolute path where the workspace instructions should be copied."}`
<a id="decision-to-command-mapping"></a>
## 决策到命令的映射

将用户决策精确映射到命令标志：

- 如果用户选择 `keep existing`（保留现有）的 `SOUL.md`，则 **不要** 添加 `--overwrite`。
- 如果用户选择 `overwrite with backup`（覆盖并备份），则添加 `--overwrite`。
- 如果用户选择 `review first`（先审查），则在执行前停止并审查相关文件。
- 如果用户选择 `keep existing skills`（保留现有技能），则添加 `--skill-conflict skip`。
- 如果用户选择 `overwrite conflicting skills with backup`（覆盖冲突技能并备份），则添加 `--skill-conflict overwrite`。
- 如果用户选择 `import conflicting skills under renamed folders`（在重命名文件夹下导入冲突技能），则添加 `--skill-conflict rename`。
- 如果用户选择 `user-data only`（仅用户数据），则使用 `--preset user-data` 执行，并且 **不要** 添加 `--migrate-secrets`。
- 如果用户选择 `full compatible migration`（完整兼容迁移），则使用 `--preset full --migrate-secrets` 执行。
- 仅当用户明确提供了绝对工作区路径时，才添加 `--workspace-target`。
- 如果用户选择 `skip workspace instructions`（跳过工作区说明）或 `decide later`（稍后决定），则不添加 `--workspace-target`。

在执行之前，用通俗语言重述确切的命令计划，并确保与用户的选择一致。

<a id="post-run-reporting-rules"></a>
## 执行后报告规则

执行后，将脚本的 JSON 输出视为真实来源。

1. 所有计数以 `report.summary` 为基础。
2. 只有当状态严格为 `migrated` 时，才将该条目列入“已成功迁移”。
3. 除非报告显示该条目为 `migrated`，否则不得声称冲突已解决。
4. 除非 `kind="soul"` 的条目报告 `status="migrated"`，否则不得说 `SOUL.md` 被覆盖。
5. 如果 `report.summary.conflict > 0`，则需包含冲突部分，而不要暗中暗示成功。
6. 如果计数与所列条目不一致，则在响应前调整列表以匹配报告。
7. 在报告可用时，包含 `output_dir` 路径，以便用户可以检查 `report.json`、`summary.md`、备份文件和归档文件。
8. 对于记忆或用户配置文件的溢出，除非报告明确显示了归档路径，否则不得说条目已被归档。如果存在 `details.overflow_file`，则说明完整的溢出列表已导出到该文件。
9. 如果技能是在重命名的文件夹下导入的，则报告最终目标位置，并提及 `details.renamed_from`。
10. 如果存在 `report.skill_conflict_mode`，则将其作为所选导入技能冲突策略的真实来源。
11. 如果条目的 `status="skipped"`，则不得将其描述为已覆盖、已备份、已迁移或已解决。
12. 如果 `kind="soul"` 的条目的 `status="skipped"` 且原因为 `Target already matches source`（目标已与源匹配），则说明其未被更改，且不得提及备份。
13. 如果重命名的导入技能的 `details.backup` 为空，则不得暗示现有的 Hermes 技能已被重命名或备份。只需说明导入的副本已放置到新目标位置，并引用 `details.renamed_from` 作为保持不变的原文件夹。

<a id="migration-presets"></a>
## 迁移预设

在常规使用中，建议优先使用以下两个预设：

- `user-data`
- `full`

`user-data` 包含：

- `soul`
- `workspace-agents`
- `memory`
- `user-profile`
- `messaging-settings`
- `command-allowlist`
- `skills`
- `tts-assets`
- `archive`
`full` 包含 `user-data` 中的所有内容，再加上：

- `secret-settings`

辅助脚本仍然支持类别级别的 `--include` / `--exclude`，但将其视为高级回退方案，而非默认的用户体验。

<a id="commands"></a>
## 命令

带完整发现的试运行：

```bash
python3 ~/.hermes/skills/migration/openclaw-migration/scripts/openclaw_to_hermes.py
```

使用终端工具时，建议采用绝对路径调用模式，例如：

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

执行完整的兼容迁移：

```bash
python3 ~/.hermes/skills/migration/openclaw-migration/scripts/openclaw_to_hermes.py --execute --preset full --migrate-secrets --skill-conflict skip
```

执行包含工作区指令的迁移：

```bash
python3 ~/.hermes/skills/migration/openclaw-migration/scripts/openclaw_to_hermes.py --execute --preset user-data --skill-conflict rename --workspace-target "/absolute/workspace/path"
```

默认情况下，不要使用 `$PWD` 或家目录作为工作区目标。首先要求用户给出明确的工作区路径。

<a id="important-rules"></a>
## 重要规则

1. 除非用户明确要求立即执行，否则先进行试运行再写入。
2. 默认不迁移密钥。令牌、认证 blob、设备凭据和原始网关配置应当留在 Hermes 之外，除非用户明确要求密钥迁移。
3. 不要静默覆盖非空的 Hermes 目标，除非用户明确要求这样做。启用覆盖时，辅助脚本会保留备份。
4. 始终向用户提供跳过项报告。该报告是迁移过程的一部分，不是可选的附加项。
5. 优先使用 OpenClaw 主工作区（`~/.openclaw/workspace/`），而不是 `workspace.default/`。仅当主文件缺失时，才将默认工作区作为回退。
6. 即使在密钥迁移模式下，也只迁移目标位置为干净的 Hermes 的密钥。不支持的认证 blob 仍必须报告为已跳过。
7. 如果试运行显示有大资产复制、冲突的 `SOUL.md` 或溢出的记忆条目，在开始执行之前必须单独指出这些情况。
8. 如果用户不确定，默认使用 `user-data only`。
9. 仅当用户明确提供了目标工作区路径时，才包含 `workspace-agents`。
10. 将类别级别的 `--include` / `--exclude` 视为高级逃生舱口，而非正常流程。
11. 如果有 `clarify` 可用，不要以模糊的“您想做什么？”结束试运行总结。应改用结构化后续提示。
12. 当真实的选择提示符可用时，不要使用开放式 `clarify` 提示。优先使用可选项，然后仅对绝对路径或文件审查请求使用自由文本。
13. 试运行后，如果仍有未解决的决策，绝不要在总结后停下。立即使用 `clarify` 处理优先级最高的阻塞性决策。
14. 后续问题的优先级顺序：
    - `SOUL.md` 冲突
    - 导入的技能冲突
    - 迁移模式
    - 工作区指令目标
15. 不要在同一个消息中承诺稍后呈现选项。必须实际调用 `clarify` 来呈现它们。
16. 在得到迁移模式答案后，显式检查 `workspace-agents` 是否仍未解决。如果是，你的下一个操作必须是调用工作区指令的 `clarify`。
17. 任何 `clarify` 答案之后，如果仍有其他必需的决策需要处理，不要复述刚决定的内容。立即提出下一个必需的问题。
<a id="expected-result"></a>
## 预期结果

成功运行后，用户应该拥有：

- 导入的 Hermes 角色状态
- 填充了转换后的 OpenClaw 知识的 Hermes 记忆文件
- OpenClaw 技能位于 `~/.hermes/skills/openclaw-imports/` 下
- 一份迁移报告，显示所有冲突、遗漏或不支持的数据
