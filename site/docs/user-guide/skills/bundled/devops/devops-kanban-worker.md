---
title: "看板工作者（Kanban Worker）— Hermes 看板工作者的陷阱、示例与边界情况"
sidebar_label: "看板工作者"
description: "Hermes 看板工作者的陷阱、示例与边界情况"
---

{/* 此页面由技能目录中的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

<a id="kanban-worker"></a>
# 看板工作者

Hermes 看板工作者的陷阱、示例与边界情况。生命周期本身会作为 `KANBAN_GUIDANCE`（来自 agent/prompt_builder.py）自动注入到每个工作者的系统提示中；当你需要了解特定场景的更深层细节时，加载此技能即可。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/devops/kanban-worker` |
| 版本 | `2.0.0` |
| 平台 | linux, macos, windows |
| 标签 | `kanban`、`multi-agent`、`collaboration`、`workflow`、`pitfalls` |
| 相关技能 | [`kanban-orchestrator`](/user-guide/skills/bundled/devops/devops-kanban-orchestrator) |

<a id="reference-full-skill-md"></a>
## 参考：完整 SKILL.md

:::info
以下是 Hermes 在该技能被触发时加载的完整技能定义。这是技能激活时 Agent 看到的指令。
:::

<a id="kanban-worker-pitfalls-and-examples"></a>
# 看板工作者——陷阱与示例

> 你正在看到此技能，是因为 Hermes 看板调度器以 `--skills kanban-worker` 参数生成了你作为工作者的实例——它会被自动加载到每个被调度的工作者中。**生命周期**（6个步骤：定向 → 工作 → 心跳 → 阻塞/完成）也位于自动注入到你系统提示中的 `KANBAN_GUIDANCE` 块里。此技能提供更深层的细节：良好的交接格式、重试诊断、边界情况。

<a id="workspace-handling"></a>
## 工作空间处理

你的工作空间类型决定了你在 `$HERMES_KANBAN_WORKSPACE` 内的行为方式：

| 类型 | 说明 | 工作方式 |
|---|---|---|
| `scratch` | 全新的临时目录，仅你独享 | 自由读写；任务归档后会被垃圾回收。 |
| `dir:&lt;path&gt;` | 共享持久目录 | 其他运行会读取你所写的内容。将其视为长期状态。路径保证为绝对路径（内核拒绝相对路径）。 |
| `worktree` | 解析路径处的 Git worktree | 如果不存在 `.git`，先从主仓库运行 `git worktree add &lt;path&gt; &lt;branch&gt;`，然后进入目录并正常操作。在此提交工作。 |

<a id="tenant-isolation"></a>
## 租户隔离

如果设置了 `$HERMES_TENANT`，则该任务属于某个租户命名空间。在读取或写入持久化内存时，请为内存条目添加租户前缀，以避免上下文在租户间泄露：

- 良好：`business-a: Acme 是我们最大的客户`
- 不良（泄露）：`Acme 是我们最大的客户`

<a id="good-summary-metadata-shapes"></a>
## 良好的概要 + 元数据格式

`kanban_complete(summary=..., metadata=...)` 交接是下游工作者读取你工作成果的方式。以下模式能正常工作：

**编码任务：**
```python
kanban_complete(
    summary="shipped rate limiter — token bucket, keys on user_id with IP fallback, 14 tests pass",
    metadata={
        "changed_files": ["rate_limiter.py", "tests/test_rate_limiter.py"],
        "tests_run": 14,
        "tests_passed": 14,
        "decisions": ["user_id primary, IP fallback for unauthenticated requests"],
    },
)
```

**需要人工审查的编码任务（review-required）：**
对于大多数涉及代码变更的任务，工作并非真正*完成*，直到有人类审查者过目。应使用 `kanban_block` 而非 `kanban_complete`，并在 `reason` 前加上 `review-required: ` 前缀，以便看板将该行标记为需要审查。先将结构化元数据（变更文件、测试计数、diff/PR URL）放入评论中，因为 `kanban_block` 只携带人类可读的原因——评论是持久的注释渠道。审查者要么批准并运行 `hermes kanban unblock &lt;id&gt;`（这会重新生成你，并附带评论线程以供后续跟进），要么通过另一条评论要求修改。

```python
import json

kanban_comment(
    body="review-required handoff:\n" + json.dumps({
        "changed_files": ["rate_limiter.py", "tests/test_rate_limiter.py"],
        "tests_run": 14,
        "tests_passed": 14,
        "diff_path": "/path/to/worktree",  # or PR url if pushed
        "decisions": ["user_id primary, IP fallback for unauthenticated requests"],
    }, indent=2),
)
kanban_block(
    reason="review-required: rate limiter shipped, 14/14 tests pass — needs eyes on the user_id/IP fallback choice before merging",
)
```

仅在任务真正终结时才使用 `kanban_complete`——例如，一行拼写修复、没有功能影响的文档变更，或者产出本身就是研究报告的研究任务。

**研究任务：**
```python
kanban_complete(
    summary="3 competing libraries reviewed; vLLM wins on throughput, SGLang on latency, Tensorrt-LLM on memory efficiency",
    metadata={
        "sources_read": 12,
        "recommendation": "vLLM",
        "benchmarks": {"vllm": 1.0, "sglang": 0.87, "trtllm": 0.72},
    },
)
```

**审查任务：**
```python
kanban_complete(
    summary="reviewed PR #123; 2 blocking issues found (SQL injection in /search, missing CSRF on /settings)",
    metadata={
        "pr_number": 123,
        "findings": [
            {"severity": "critical", "file": "api/search.py", "line": 42, "issue": "raw SQL concat"},
            {"severity": "high", "file": "api/settings.py", "issue": "missing CSRF middleware"},
        ],
        "approved": False,
    },
)
```

设计 `metadata` 的结构，以便下游解析器（审查者、聚合器、调度器）无需重新阅读你的文字即可使用。

<a id="claiming-cards-you-actually-created"></a>
## 认领你自己创建的卡片

如果你的运行产生了新的看板任务（通过 `kanban_create`），请在 `kanban_complete` 的 `created_cards` 中传入这些 id。内核会验证每个 id 存在且由你的配置文件创建；任何虚假 id 都会导致完成失败，并列出错误信息，被拒绝的尝试会永久记录在任务的事件日志中。**只列出你从成功的 `kanban_create` 返回值中捕获的 id——绝不要从文字中编造 id，绝不要粘贴之前运行中的 id，绝不要认领其他工作线程创建的卡片。**

```python
# GOOD — capture return values, then claim them.
c1 = kanban_create(title="remediate SQL injection", assignee="security-worker")
c2 = kanban_create(title="fix CSRF middleware", assignee="web-worker")

kanban_complete(
    summary="Review done; spawned remediations for both findings.",
    metadata={"pr_number": 123, "approved": False},
    created_cards=[c1["task_id"], c2["task_id"]],
)
```
```python
# BAD — claiming ids you don't have captured return values for.
kanban_complete(
    summary="Created remediation cards t_a1b2c3d4, t_deadbeef",  # hallucinated
    created_cards=["t_a1b2c3d4", "t_deadbeef"],                   # → gate rejects
)
```

如果 `kanban_create` 调用失败（异常、工具错误），卡片就没有被创建——不要为它添加虚假的 ID。重试创建，或者省略该 ID 并在 your summary 中说明失败原因。扫描摘要的文本检查也会捕获你在自由格式摘要中引用的、但实际上不存在的 `t_&lt;hex&gt;` 引用；这些不会阻止完成，但会在仪表板的任务上显示为建议性警告。

<a id="block-reasons-that-get-answered-fast"></a>
## 能快速得到答复的阻塞原因

错误示例：`"stuck"` —— 人类没有上下文信息。

正确示例：用一句话说明你需要做的具体决策。把更长的上下文作为评论留下。

```python
kanban_comment(
    task_id=os.environ["HERMES_KANBAN_TASK"],
    body="Full context: I have user IPs from Cloudflare headers but some users are behind NATs with thousands of peers. Keying on IP alone causes false positives.",
)
kanban_block(reason="Rate limit key choice: IP (simple, NAT-unsafe) or user_id (requires auth, skips anonymous endpoints)?")
```

阻塞消息会显示在仪表板/网关通知器中。评论是更深层的上下文，人类在打开任务时会阅读。

<a id="heartbeats-worth-sending"></a>
## 值得发送的心跳信号

好的心跳信号会说明进展：`"epoch 12/50, loss 0.31"`、`"scanned 1.2M/2.4M rows"`、`"uploaded 47/120 videos"`。

糟糕的心跳信号：`"still working"`、空备注、间隔小于一秒。最多每几分钟发一次；对于不超过两分钟的任务，完全跳过。

<a id="retry-scenarios"></a>
## 重试场景

如果你打开任务并且 `kanban_show` 返回 `runs: [...]` 包含一个或多个已关闭的运行，那么你就是一个重试实例。之前运行的 `outcome` / `summary` / `error` 会告诉你什么没起作用。不要重复那条路径。典型的重试诊断信息：

- `outcome: "timed_out"` —— 之前的尝试达到了 `max_runtime_seconds`。你可能需要拆分工作或缩短时间。
- `outcome: "crashed"` —— 内存溢出或段错误。减少内存占用。
- `outcome: "spawn_failed"` + `error: "..."` —— 通常是配置问题（缺少凭据、PATH 错误）。通过 `kanban_block` 询问人类，而不要盲目重试。
- `outcome: "reclaimed"` + `summary: "task archived..."` —— 操作员在之前运行期间将任务归档；你很可能根本不应该运行，请仔细检查状态。
- `outcome: "blocked"` —— 之前的尝试被阻塞；现在线程中应该已经有了取消阻塞的评论。

<a id="do-not"></a>
## 不要

- 使用 `delegate_task` 代替 `kanban_create`。`delegate_task` 用于你运行内部的短推理子任务；`kanban_create` 用于跨 Agent 的交接，这些交接会超过一次 API 循环。
- 在 `$HERMES_KANBAN_WORKSPACE` 之外修改文件，除非任务正文要求这样做。
- 创建分配给你自己的后续任务——要分配给正确的专长 Agent。
- 完成一个你实际上没有完成的任务。改为阻塞它。

<a id="pitfalls"></a>
## 陷阱

**任务状态可能在调度和你启动之间发生变化。** 从调度器认领到你的进程实际启动之间，任务可能已经被阻塞、重新分配或归档。总是先执行 `kanban_show`。如果它报告 `blocked` 或 `archived`，停止运行——你不应该再继续。
**工作区可能包含过时的构建产物。** 尤其是 `dir:` 和 `worktree` 工作区会残留之前运行的文件。请阅读评论线程——它通常解释了为什么你要再次运行，以及工作区当前的状态。

**当有指导可用时，不要依赖 CLI。** `kanban_*` 工具在所有终端后端（Docker、Modal、SSH）上都能工作。在容器化后端中，终端里的 `hermes kanban &lt;verb&gt;` 会失败，因为 CLI 没有安装在那里。如有疑问，请使用工具。

<a id="cli-fallback-for-scripting"></a>
## CLI 回退（用于脚本编写）

每个工具都有对应的 CLI 命令供人类操作者和脚本使用：
- `kanban_show` ↔ `hermes kanban show &lt;id&gt; --json`
- `kanban_complete` ↔ `hermes kanban complete &lt;id&gt; --summary "..." --metadata '{...}'`
- `kanban_block` ↔ `hermes kanban block &lt;id&gt; "reason"`
- `kanban_create` ↔ `hermes kanban create "title" --assignee &lt;profile&gt; [--parent &lt;id&gt;]`
- 等等。

在 Agent 内部使用工具；CLI 是为终端前的人类准备的。
