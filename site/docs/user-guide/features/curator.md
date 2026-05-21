---
sidebar_position: 3
title: "策展器"
description: "对 Agent 创建的技能进行后台维护——使用追踪、过时、归档以及 LLM 驱动的审查"
---

<a id="curator"></a>
# 策展器

策展器是一个针对 **Agent 创建的技能** 的后台维护流程。它追踪每个技能被查看、使用和修补的频率，将长期未使用的技能从 `active → stale → archived` 状态迁移，并定期启动一次简短的辅助模型审查，提出合并建议或修补漂移。

它的存在是为了防止通过 [自我改进循环](/user-guide/features/skills#agent-managed-skills-skill_manage-tool) 创建的技能无限堆积。每次 Agent 解决一个新问题并保存一个技能时，该技能都会落入 `~/.hermes/skills/`。如果没有维护，最终你会得到大量狭窄的近似重复项，污染目录并浪费令牌。

策展器 **从不触碰** 捆绑技能（随仓库发布）或从中心安装的技能（来自 [agentskills.io](https://agentskills.io)）。它只审查 Agent 自己创作的技能。它也 **从不自动删除**——最坏的结果是归档到 `~/.hermes/skills/.archive/`，这是可恢复的。

跟踪问题 [#7816](https://github.com/NousResearch/hermes-agent/issues/7816)。

<a id="how-it-runs"></a>
## 运行方式

策展器由不活跃检查触发，而不是 cron 守护进程。在 CLI 会话启动时，以及在网关的 cron-ticker 线程内的周期性触发中，Hermes 会检查：

1. 自上次策展器运行以来是否已过去足够的时间（`interval_hours`，默认 **7 天**），以及
2. Agent 是否已空闲足够长的时间（`min_idle_hours`，默认 **2 小时**）。

如果两者都为真，它会生成一个 `AIAgent` 的后台分支——与记忆/技能自我改进提示使用的模式相同。该分支在自己的提示缓存中运行，从不触及活跃对话。

:::info 首次运行行为
<a id="first-run-behavior"></a>
在全新安装（或 `hermes update` 后首次触发策展器之前的安装）时，策展器 **不会立即运行**。首次观察会将 `last_run_at` 设置为“现在”，并将第一次实际运行推迟整整一个 `interval_hours`。这给了你一个完整的间隔来审查你的技能库，固定任何重要的内容，或者在策展器触及之前完全选择退出。

如果你想在实际运行前看看策展器 *会* 做什么，请运行 `hermes curator run --dry-run`——它会生成相同的审查报告，但不会修改库。
:::

一次运行包含两个阶段：

1. **自动转换**（确定性，无需 LLM）。在 `stale_after_days`（30）内未使用的技能变为 `stale`；在 `archive_after_days`（90）内未使用的技能被移动到 `~/.hermes/skills/.archive/`。
2. **LLM 审查**（单次辅助模型传递，`max_iterations=8`）。分支 Agent 调查 Agent 创建的技能，可以使用 `skill_view` 读取其中任何一个，并针对每个技能决定是保留、修补（通过 `skill_manage`）、合并重叠的技能，还是通过终端工具归档。

固定的技能对策展器的自动转换和 Agent 自己的 `skill_manage` 工具都是禁止访问的。请参见下面的 [固定技能](#pinning-a-skill)。

<a id="configuration"></a>
## 配置

所有设置都位于 `config.yaml` 中的 `curator:` 下（不是 `.env`——这不是秘密）。默认值：
```yaml
curator:
  enabled: true
  interval_hours: 168          # 7 天
  min_idle_hours: 2
  stale_after_days: 30
  archive_after_days: 90
```

要完全禁用，请设置 `curator.enabled: false`。

<a id="running-the-review-on-a-cheaper-aux-model"></a>
### 在更便宜的辅助模型上运行审查

curator 的 LLM 审查过程是一个常规的辅助任务槽——`auxiliary.curator`——与视觉、压缩、会话搜索等并列。"Auto" 表示"使用我的主聊天模型"；覆盖该槽位，可以为审查过程固定特定的提供方 + 模型。

**最简单的方法——`hermes model`：**

```bash
hermes model                   # → "辅助模型——侧任务路由"
                               # → 选择"Curator" → 选择提供方 → 选择模型
```

同样的选择器也可以在 Web 仪表盘的 **Models** 选项卡下使用。

**直接 config.yaml（等效方式）：**

```yaml
auxiliary:
  curator:
    provider: openrouter
    model: google/gemini-3-flash-preview
    timeout: 600               # 宽松设置——审查可能需要几分钟
```

将 `provider: auto`（默认值）保留，则审查过程将通过你的主聊天模型进行路由，与其他所有辅助任务的行为一致。

:::note 旧版配置
早期版本曾使用一个独立的 `curator.auxiliary.{provider,model}` 块。该路径仍然有效，但会输出弃用日志行——请迁移到上面的 `auxiliary.curator`，以便 curator 与其他所有辅助任务共享相同的底层机制（`hermes model`、仪表盘 Models 选项卡、`base_url`、`api_key`、`timeout`、`extra_body`）。
<a id="legacy-config"></a>
:::

<a id="cli"></a>
## CLI

```bash
hermes curator status         # 上次运行、计数、固定列表、LRU 前 5 名
hermes curator run            # 立即触发审查（阻塞直到 LLM 过程完成）
hermes curator run --background  # 即发即忘：在后台线程中启动 LLM 过程
hermes curator run --dry-run  # 仅预览——报告但不做任何修改
hermes curator backup         # 手动创建 ~/.hermes/skills/ 的快照
hermes curator rollback       # 从最新的快照恢复
hermes curator rollback --list     # 列出可用快照
hermes curator rollback --id <ts>  # 恢复指定快照
hermes curator rollback -y         # 跳过确认提示
hermes curator pause          # 停止运行，直到恢复
hermes curator resume
hermes curator pin <skill>    # 永远不要自动转换此技能
hermes curator unpin <skill>
hermes curator restore <skill>  # 将已归档的技能移回活动状态
```

<a id="backups-and-rollback"></a>
## 备份与回滚

在每次实际的 curator 过程之前，Hermes 都会将 `~/.hermes/skills/` 的 tar.gz 快照保存到 `~/.hermes/skills/.curator_backups/&lt;utc-iso&gt;/skills.tar.gz`。如果某次过程归档或合并了你不想被改动的内容，你可以通过一条命令撤销整个运行：

```bash
hermes curator rollback        # 恢复最新快照（需要确认）
hermes curator rollback -y     # 跳过提示
hermes curator rollback --list # 查看所有快照（包含原因和大小）
```

回滚本身是可逆的：在替换技能树之前，Hermes 会创建另一个快照，标记为 `pre-rollback to &lt;target-id&gt;`，因此可以通过 `--id` 回滚到该快照来撤销错误的回滚。
你还可以随时使用 `hermes curator backup --reason "before-refactor"` 手动创建快照。`--reason` 字符串会写入快照的 `manifest.json` 中，并在 `--list` 中显示。

快照会按 `curator.backup.keep`（默认 5）进行清理，以控制磁盘使用量：

```yaml
curator:
  backup:
    enabled: true
    keep: 5
```

设置 `curator.backup.enabled: false` 可禁用自动快照。即使备份被禁用，手动执行 `hermes curator backup` 命令仍然有效，但前提是你先将 `enabled` 设为 `true` —— 该标志对称地控制着两条路径，因此不可能在变更运行时意外跳过预运行快照。

`hermes curator status` 还会列出最近最少使用的五个技能 —— 这是快速查看哪些技能即将过时的方法。

在运行中的会话（CLI 或网关平台）内，也可以通过 `/curator` 斜杠命令使用相同的子命令。

<a id="what-agent-created-means"></a>
## “agent-created” 的含义

如果一个技能的名称**不在**以下列表中，则被视为 agent-created：

- `~/.hermes/skills/.bundled_manifest`（安装时从仓库复制的技能），以及
- `~/.hermes/skills/.hub/lock.json`（通过 `hermes skills install` 安装的技能）

`~/.hermes/skills/` 中的其他所有内容都归 curator 管辖。这包括：

- Agent 在对话期间通过 `skill_manage(action="create")` 保存的技能。
- 你手动创建的、带有手写 `SKILL.md` 的技能。
- 通过你指定的外部技能目录添加的技能。

:::warning 你手写的技能与 agent 保存的技能看起来一样
<a id="your-hand-written-skills-look-the-same-as-agent-saved-ones"></a>
这里的来源是**二元的**（bundled/hub 与其他）。Curator 无法区分你依赖的用于私有工作流的手写技能与自我改进循环在会话期间保存的技能。两者都归入 "agent-created" 类别。

在第一次实际扫描之前（安装后默认 7 天），花点时间：

1. 运行 `hermes curator run --dry-run` 查看 curator 将提出的具体建议。
2. 使用 `hermes curator pin &lt;name&gt;` 保护任何你不想被触及的技能。
3. 或者如果你更愿意自己管理库，请在 `config.yaml` 中设置 `curator.enabled: false`。

归档始终可以通过 `hermes curator restore &lt;name&gt;` 恢复，但事先固定比事后追踪合并要容易得多。
:::

如果你想保护某个特定技能不被触及 —— 例如你依赖的手写技能 —— 请使用 `hermes curator pin &lt;name&gt;`。详见下一节。

<a id="pinning-a-skill"></a>
## 固定技能

固定可以保护技能不被删除 —— 无论是 curator 的自动归档操作还是 agent 的 `skill_manage(action="delete")` 工具调用。一旦技能被固定：

- **Curator** 在自动转换（`active → stale → archived`）时会跳过该技能，并且其 LLM 审查环节会被指示不去动它。
- **Agent 的 `skill_manage` 工具**会拒绝对其执行 `delete` 操作，并提示用户使用 `hermes curator unpin &lt;name&gt;`。补丁和编辑仍然可以通过，因此当问题出现时，agent 可以改进固定技能的内容，而不需要进行固定/解除固定/重新固定的繁琐操作。
固定和解固定：

```bash
hermes curator pin <skill>
hermes curator unpin <skill>
```

该标志以 `"pinned": true` 的形式存储在技能条目的 `~/.hermes/skills/.usage.json` 文件中，因此在会话之间持久保留。

只有 **agent 创建的** 技能才能被固定——捆绑安装和从中心安装的技能本身就不受 curator 变更的影响，如果你尝试固定，`hermes curator pin` 会拒绝并给出解释信息。

如果你想要比“不删除”更强的保证——例如，在 agent 仍然读取技能的同时完全冻结其内容——直接用编辑器编辑 `~/.hermes/skills/&lt;name&gt;/SKILL.md`。固定机制保护的是工具驱动的删除，而不是你自己的文件系统访问。

<a id="usage-telemetry"></a>
## 使用遥测

curator 在 `~/.hermes/skills/.usage.json` 维护一个伴生文件，每个技能对应一个条目：

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

- `view_count`: agent 对技能调用 `skill_view`。
- `use_count`: 技能被加载到对话的提示中。
- `patch_count`: 对技能运行 `skill_manage patch/edit/write_file/remove_file`。

捆绑安装和从中心安装的技能明确排除在遥测写入之外。

<a id="per-run-reports"></a>
## 每次运行报告

每次 curator 运行都会在 `~/.hermes/logs/curator/` 下写入一个带时间戳的目录：

```
~/.hermes/logs/curator/
└── 20260429-111512/
    ├── run.json      # 机器可读：完整保真度、统计信息、LLM 输出
    └── REPORT.md     # 人类可读的摘要
```

`REPORT.md` 提供了一种快速查看某次运行做了什么的途径——哪些技能发生了状态转换、LLM 评审员说了什么、它修补了哪些技能。便于审计，无需 grep `agent.log`。

<a id="rename-map-in-the-summary"></a>
### 摘要中的重命名映射

如果某次运行将多个技能合并到一个总括技能下（或合并了近似的重复技能），则在运行结束时打印的用户可见摘要中会包含一个明确的重命名映射，显示 curator 应用的每个 `旧名称 → 新名称` 对。这是对每个技能转换行的补充，因此当一波重命名发生时，你可以一眼看出，而不需要比对 JSON 报告。这个提示也会在 `hermes curator pin` 下显示，这样如果你想锁定新标签，可以立即固定总括名称。

<a id="restoring-an-archived-skill"></a>
## 恢复已归档的技能

如果 curator 归档了你仍然想要的内容：

```bash
hermes curator restore <skill-name>
```

这将把技能从 `~/.hermes/skills/.archive/` 移回到活动目录树中，并将其状态重置为 `active`。如果此后有一个捆绑安装或中心安装的技能以同名被安装（会遮蔽上游），则恢复操作会拒绝执行。

<a id="disabling-per-environment"></a>
## 按环境禁用

curator 默认启用。要禁用它：

- **仅针对一个配置文件：** 编辑 `~/.hermes/config.yaml`（或当前活动配置文件的配置）并设置 `curator.enabled: false`。
- **仅针对一次运行：** `hermes curator pause`——暂停会在会话之间持续生效；使用 `resume` 重新启用。
如果 `min_idle_hours` 尚未过去，curator 也会拒绝运行，因此在活跃的开发机上，它自然只会在空闲时段运行。

<a id="see-also"></a>
## 参见

- [技能系统](/user-guide/features/skills) — 技能的一般工作方式，以及创造它们的自我改进循环
- [记忆](/user-guide/features/memory) — 一个维护长期记忆的并行后台审查
- [内建技能目录](/reference/skills-catalog)
- [Issue #7816](https://github.com/NousResearch/hermes-agent/issues/7816) — 原始提案与设计讨论
