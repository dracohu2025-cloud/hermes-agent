---
sidebar_position: 3
title: "Curator"
description: "对 Agent 创建的技能进行后台维护——使用追踪、过期处理、归档以及 LLM 驱动的审查"
---

# Curator {#curator}

Curator 是一个针对 **Agent 创建的技能** 的后台维护流程。它会追踪每个技能被查看、使用和修补的频率，将长期未使用的技能通过 `active → stale → archived` 状态进行转移，并定期启动一个简短的辅助模型审查，提出合并建议或修补偏差。

它的存在是为了防止通过[自我改进循环](/user-guide/features/skills#agent-managed-skills-skill_manage-tool)创建的技能无限堆积。每次 Agent 解决一个新问题并保存一个技能时，该技能都会存放在 `~/.hermes/skills/` 目录下。如果没有维护，你最终会得到几十个狭窄的、近乎重复的技能，它们会污染技能目录并浪费 Token。

Curator **从不触碰** 捆绑技能（随仓库一起发布）或从 Hub 安装的技能（来自 [agentskills.io](https://agentskills.io)）。它只审查 Agent 自己创作的技能。它也 **从不自动删除** —— 最坏的情况是归档到 `~/.hermes/skills/.archive/`，这是可恢复的。

追踪 [issue #7816](https://github.com/NousResearch/hermes-agent/issues/7816)。

## 运行方式 {#how-it-runs}

Curator 由不活跃检查触发，而不是由 cron 守护进程触发。在 CLI 会话启动时，以及在网关的 cron-ticker 线程内的周期性滴答中，Hermes 会检查：

1. 自上次 curator 运行以来是否已过去足够的时间（`interval_hours`，默认 **7 天**），并且
2. Agent 是否已空闲足够长的时间（`min_idle_hours`，默认 **2 小时**）。

如果两者都为真，它会启动一个 `AIAgent` 的后台分支——这与记忆/技能自我改进提示使用的模式相同。该分支在其自己的提示缓存中运行，并且从不触及活跃的对话。

:::info 首次运行行为
<a id="first-run-behavior"></a>
在全新安装（或 `hermes update` 后，首次在安装 curator 之前触发时），curator **不会立即运行**。首次观察会将 `last_run_at` 设置为“现在”，并将第一次实际运行推迟整整一个 `interval_hours`。这给了你一个完整的间隔时间来审查你的技能库，固定任何重要的技能，或者在 curator 触及它们之前完全选择退出。

如果你想在 curator 实际运行之前看看它 *会* 做什么，请运行 `hermes curator run --dry-run` —— 它会产生相同的审查报告，但不会修改技能库。
:::

一次运行包含两个阶段：

1. **自动状态转换**（确定性，无需 LLM）。在 `stale_after_days`（30 天）内未使用的技能变为 `stale`；在 `archive_after_days`（90 天）内未使用的技能被移动到 `~/.hermes/skills/.archive/`。
2. **LLM 审查**（单次辅助模型传递，`max_iterations=8`）。分支 Agent 会调查 Agent 创建的技能，可以使用 `skill_view` 读取其中任何一个，并针对每个技能决定是保留、修补（通过 `skill_manage`）、合并重叠的技能，还是通过终端工具进行归档。

被固定的技能对 curator 的自动转换和 Agent 自己的 `skill_manage` 工具都是禁区。请参阅下面的[固定技能](#pinning-a-skill)。

## 配置 {#configuration}

所有设置都位于 `config.yaml` 的 `curator:` 下（不是 `.env` —— 这不是秘密）。默认值：
```yaml
curator:
  enabled: true
  interval_hours: 168          # 7 天
  min_idle_hours: 2
  stale_after_days: 30
  archive_after_days: 90
```

要完全禁用，请设置 `curator.enabled: false`。

### 在更便宜的辅助模型上运行审查 {#running-the-review-on-a-cheaper-aux-model}

curator 的 LLM 审查通道是一个常规的辅助任务槽位——`auxiliary.curator`——与 Vision、Compression、Session Search 等并列。"Auto" 表示"使用我的主聊天模型"；覆盖该槽位可以固定一个特定的 provider + model 用于审查通道。

**最简单的方式——`hermes model`：**

```bash
hermes model                   # → "辅助模型 — 侧任务路由"
                               # → 选择 "Curator" → 选择 provider → 选择 model
```

同样的选择器也可以在 Web 仪表盘的 **Models** 标签页下找到。

**直接修改 config.yaml（等效）：**

```yaml
auxiliary:
  curator:
    provider: openrouter
    model: google/gemini-3-flash-preview
    timeout: 600               # 宽松设置——审查可能需要几分钟
```

保留 `provider: auto`（默认值）会让审查通道使用你的主聊天模型，与其他所有辅助任务的行为一致。

:::note 旧版配置
早期版本使用了一个独立的 `curator.auxiliary.{provider,model}` 块。该路径仍然有效，但会输出一条弃用日志——请迁移到上面的 `auxiliary.curator`，这样 curator 就能与其他所有辅助任务共享相同的底层机制（`hermes model`、仪表盘 Models 标签页、`base_url`、`api_key`、`timeout`、`extra_body`）。
<a id="legacy-config"></a>
:::

## CLI {#cli}

```bash
hermes curator status         # 上次运行时间、计数、固定列表、LRU 前 5
hermes curator run            # 立即触发审查（默认后台运行）
hermes curator run --sync     # 同上，但会阻塞直到 LLM 通道完成
hermes curator run --dry-run  # 仅预览——报告但不做任何修改
hermes curator backup         # 手动创建 ~/.hermes/skills/ 的快照
hermes curator rollback       # 从最新快照恢复
hermes curator rollback --list     # 列出可用快照
hermes curator rollback --id <ts>  # 恢复指定快照
hermes curator rollback -y         # 跳过确认提示
hermes curator pause          # 暂停运行，直到恢复
hermes curator resume
hermes curator pin <skill>    # 永远不自动转换此技能
hermes curator unpin <skill>
hermes curator restore <skill>  # 将已归档的技能移回活跃状态
```

## 备份与回滚 {#backups-and-rollback}

在每次真正的 curator 运行之前，Hermes 会为 `~/.hermes/skills/` 创建一个 tar.gz 快照，存放在 `~/.hermes/skills/.curator_backups/&lt;utc-iso&gt;/skills.tar.gz`。如果某次运行归档或合并了你不想被改动的内容，你可以用一条命令撤销整个运行：

```bash
hermes curator rollback        # 恢复最新快照（需确认）
hermes curator rollback -y     # 跳过提示
hermes curator rollback --list # 查看所有快照，包含原因和大小
```

回滚本身是可逆的：在替换技能树之前，Hermes 会再创建一个标记为 `pre-rollback to &lt;target-id&gt;` 的快照，因此误回滚可以通过 `--id` 向前回滚到该快照来撤销。
你也可以随时通过 `hermes curator backup --reason "before-refactor"` 手动创建快照。`--reason` 字符串会写入快照的 `manifest.json`，并在 `--list` 中显示。

快照会根据 `curator.backup.keep`（默认 5）进行修剪，以控制磁盘用量：

```yaml
curator:
  backup:
    enabled: true
    keep: 5
```

将 `curator.backup.enabled: false` 可禁用自动快照。当备份被禁用时，手动 `hermes curator backup` 命令仍然有效，但前提是你先设置了 `enabled: true`——该标志对称地控制两条路径，因此无法在变异运行中意外跳过运行前快照。

`hermes curator status` 还会列出最近最少使用的五个技能——快速查看哪些技能可能即将过时。

这些子命令在运行中的会话（CLI 或网关平台）内也可通过 `/curator` 斜杠命令使用。

## “agent-created”的含义 {#what-agent-created-means}

如果技能的名称**不在**以下列表中，则视为 agent-created：

- `~/.hermes/skills/.bundled_manifest`（安装时从仓库复制的技能）
- `~/.hermes/skills/.hub/lock.json`（通过 `hermes skills install` 安装的技能）

`~/.hermes/skills/` 中所有其他内容都归 curator 管理。包括：

- Agent 在对话中通过 `skill_manage(action="create")` 保存的技能。
- 你手动编写 `SKILL.md` 创建的技能。
- 通过你指向 Hermes 的外部技能目录添加的技能。

:::warning 你手写的技能与 agent 保存的技能看起来一样
<a id="your-hand-written-skills-look-the-same-as-agent-saved-ones"></a>
这里的来源是**二元的**（bundled/hub 与其余所有）。Curator 无法区分你依赖的手写技能（用于私有工作流）与自我改进循环在会话中途保存的技能。两者都属于“agent-created”桶。

在第一次实际运行之前（默认安装后 7 天），请花点时间：

1. 运行 `hermes curator run --dry-run` 查看 curator 会提出哪些建议。
2. 使用 `hermes curator pin &lt;name&gt;` 保护你不想被触碰的任何内容。
3. 或者如果你更愿意自己管理技能库，在 `config.yaml` 中设置 `curator.enabled: false`。

存档始终可以通过 `hermes curator restore &lt;name&gt;` 恢复，但事先固定比事后追查合并更容易。
:::

如果你想保护某个特定技能不被触碰——例如你依赖的手写技能——请使用 `hermes curator pin &lt;name&gt;`。请参阅下一节。

## 固定技能 {#pinning-a-skill}

固定是对自动和 agent 驱动的更改的硬性防护。一旦技能被固定：

- **Curator** 在自动转换（`active → stale → archived`）中跳过它，并且其 LLM 审查过程被指示不要动它。
- **Agent 的 `skill_manage` 工具**拒绝对其执行任何写入操作。对 `edit`、`patch`、`delete`、`write_file` 和 `remove_file` 的调用会返回一个拒绝，告诉模型要求用户运行 `hermes curator unpin &lt;name&gt;`。这可以防止 agent 在对话中途静默重写技能。
使用以下命令进行固定和取消固定：

```bash
hermes curator pin <skill>
hermes curator unpin <skill>
```

该标志以 `"pinned": true` 的形式存储在技能对应的 `~/.hermes/skills/.usage.json` 条目中，因此跨会话持久保留。

只有 **Agent 创建的** 技能才能被固定——捆绑安装和从中心安装的技能从一开始就不受 curator 变更影响，如果你尝试固定它们，`hermes curator pin` 会拒绝并给出解释性消息。

如果你需要自行更新已固定的技能，直接用编辑器编辑 `~/.hermes/skills/&lt;name&gt;/SKILL.md`。固定只保护 Agent 的工具路径，不会影响你自身的文件系统访问。

## 使用遥测 {#usage-telemetry}

curator 在 `~/.hermes/skills/.usage.json` 维护一个侧车文件，每个技能对应一个条目：

```json
{
  "my-skill": {
    "use_count": 12,
    "view_count": 34,
    "last_used_at": "2026-04-24T18:12:03Z",
    "last_viewed_at": "2026-04-23T09:44:17Z",
    "patch_count": 3,
    "last_patched_at": "2026-04-20T22:01:55Z",
    "created_at": "2026-03-01T14:20:00Z",
    "state": "active",
    "pinned": false,
    "archived_at": null
  }
}
```

计数器在以下情况下递增：

- `view_count`：Agent 对该技能调用 `skill_view`。
- `use_count`：技能被加载到对话的提示中。
- `patch_count`：对该技能执行 `skill_manage patch/edit/write_file/remove_file`。

捆绑安装和从中心安装的技能被明确排除在遥测写入之外。

## 每次运行的报告 {#per-run-reports}

每次 curator 运行都会在 `~/.hermes/logs/curator/` 下写入一个带时间戳的目录：

```
~/.hermes/logs/curator/
└── 20260429-111512/
    ├── run.json      # 机器可读：完整保真度、统计信息、LLM 输出
    └── REPORT.md     # 人类可读摘要
```

`REPORT.md` 是快速查看某次运行做了什么的好方法——哪些技能发生了状态转换、LLM 审查者说了什么、修补了哪些技能。适合审计，无需 grep `agent.log`。

## 恢复已归档的技能 {#restoring-an-archived-skill}

如果 curator 归档了你仍然需要的技能：

```bash
hermes curator restore <skill-name>
```

这会将技能从 `~/.hermes/skills/.archive/` 移回活动树，并将其状态重置为 `active`。如果之后有同名的捆绑安装或中心安装技能被安装（会遮蔽上游），恢复操作会拒绝。

## 按环境禁用 {#disabling-per-environment}

curator 默认开启。要关闭它：

- **仅针对一个配置文件：** 编辑 `~/.hermes/config.yaml`（或当前活动配置文件的配置），设置 `curator.enabled: false`。
- **仅针对一次运行：** `hermes curator pause`——暂停会跨会话持久保留；使用 `resume` 重新启用。

如果 `min_idle_hours` 尚未过去，curator 也会拒绝运行，因此在活跃的开发机器上，它自然只会在空闲时段运行。

## 另请参阅 {#see-also}

- [技能系统](/user-guide/features/skills) —— 技能的一般工作原理以及创建它们的自我改进循环
- [记忆](/user-guide/features/memory) —— 一个并行的后台审查，维护长期记忆
- [捆绑技能目录](/reference/skills-catalog)
- [Issue #7816](https://github.com/NousResearch/hermes-agent/issues/7816) —— 原始提案和设计讨论
