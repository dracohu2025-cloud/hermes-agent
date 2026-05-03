---
title: "看板 Worker — Hermes 看板 Worker 的陷阱、示例与边界情况"
sidebar_label: "看板 Worker"
description: "Hermes 看板 Worker 的陷阱、示例与边界情况"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 从技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# 看板 Worker {#kanban-worker}

Hermes 看板 Worker 的陷阱、示例与边界情况。生命周期本身会作为 KANBAN_GUIDANCE（来自 agent/prompt_builder.py）自动注入到每个 Worker 的系统提示中；当你需要了解特定场景的更多细节时，加载的就是这个技能。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/devops/kanban-worker` |
| 版本 | `2.0.0` |
| 标签 | `kanban`、`multi-agent`、`collaboration`、`workflow`、`pitfalls` |
| 相关技能 | [`kanban-orchestrator`](/user-guide/skills/bundled/devops/devops-kanban-orchestrator) |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这就是技能激活时 Agent 看到的指令。
:::

# 看板 Worker — 陷阱与示例 {#kanban-worker-pitfalls-and-examples}

> 你看到这个技能是因为 Hermes 看板调度器以 `--skills kanban-worker` 参数将你生成为一个 Worker——它会被自动加载到每个被调度的 Worker 中。**生命周期**（6 个步骤：定向 → 工作 → 心跳 → 阻塞/完成）也存在于自动注入到系统提示中的 `KANBAN_GUIDANCE` 块里。这个技能提供了更深入的细节：良好的交接格式、重试诊断、边界情况。

## 工作空间处理 {#workspace-handling}

你的工作空间类型决定了你在 `$HERMES_KANBAN_WORKSPACE` 内部的行为方式：

| 类型 | 说明 | 工作方式 |
|---|---|---|
| `scratch` | 全新的临时目录，仅属于你 | 可自由读写；任务归档后会被垃圾回收。 |
| `dir:&lt;path&gt;` | 共享的持久化目录 | 其他运行实例会读取你写入的内容。将其视为长期存在的状态。路径保证是绝对路径（内核拒绝相对路径）。 |
| `worktree` | 解析路径下的 Git 工作树 | 如果 `.git` 不存在，先从主仓库运行 `git worktree add &lt;path&gt; &lt;branch&gt;`，然后 cd 进入并正常操作。在此处提交工作。 |

## 租户隔离 {#tenant-isolation}

如果设置了 `$HERMES_TENANT`，则该任务属于某个租户命名空间。在读写持久化内存时，请为内存条目添加租户前缀，以避免上下文跨租户泄露：

- 正确：`business-a: Acme is our biggest customer`
- 错误（泄露）：`Acme is our biggest customer`

## 良好的摘要与元数据格式 {#good-summary-metadata-shapes}

`kanban_complete(summary=..., metadata=...)` 交接是下游 Worker 了解你工作成果的方式。以下是一些有效的模式：

**编码任务：**
```python
kanban_complete(
    summary="完成了速率限制器——令牌桶，基于 user_id 的键，IP 回退，14 个测试通过",
    metadata={
        "changed_files": ["rate_limiter.py", "tests/test_rate_limiter.py"],
        "tests_run": 14,
        "tests_passed": 14,
        "decisions": ["user_id 为主键，未认证请求使用 IP 回退"],
    },
)
```

**研究任务：**
```python
kanban_complete(
    summary="评估了 3 个竞争库；vLLM 在吞吐量上胜出，SGLang 在延迟上胜出，Tensorrt-LLM 在内存效率上胜出",
    metadata={
        "sources_read": 12,
        "recommendation": "vLLM",
        "benchmarks": {"vllm": 1.0, "sglang": 0.87, "trtllm": 0.72},
    },
)
```
**Review task:**
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

设计 `metadata` 的结构，让下游解析器（审查者、聚合器、调度器）无需重新阅读你的描述就能直接使用。

## 能快速得到回复的阻塞原因 {#block-reasons-that-get-answered-fast}

不好的写法：`"stuck"` —— 人类没有上下文。

好的写法：一句话说明你需要的具体决策。更长的上下文可以放在评论里。

```python
kanban_comment(
    task_id=os.environ["HERMES_KANBAN_TASK"],
    body="Full context: I have user IPs from Cloudflare headers but some users are behind NATs with thousands of peers. Keying on IP alone causes false positives.",
)
kanban_block(reason="Rate limit key choice: IP (simple, NAT-unsafe) or user_id (requires auth, skips anonymous endpoints)?")
```

阻塞消息会显示在仪表盘/网关通知器中。评论则是人类打开任务时阅读的深层上下文。

## 值得发送的心跳 {#heartbeats-worth-sending}

好的心跳会说明进度：`"epoch 12/50, loss 0.31"`、`"scanned 1.2M/2.4M rows"`、`"uploaded 47/120 videos"`。

不好的心跳：`"still working"`、空备注、小于秒级间隔。最多每隔几分钟发送一次；对于大约2分钟以内的任务，完全跳过。

## 重试场景 {#retry-scenarios}

如果你打开任务，`kanban_show` 返回 `runs: [...]` 且其中包含一个或多个已关闭的运行，那么你就是一次重试。之前运行的 `outcome` / `summary` / `error` 会告诉你哪里没成功。不要重复那条路径。典型的重试诊断：

- `outcome: "timed_out"` —— 之前的尝试达到了 `max_runtime_seconds`。你可能需要拆分工作或缩短它。
- `outcome: "crashed"` —— OOM 或段错误。减少内存占用。
- `outcome: "spawn_failed"` + `error: "..."` —— 通常是配置问题（缺少凭据、PATH 错误）。通过 `kanban_block` 询问人类，而不是盲目重试。
- `outcome: "reclaimed"` + `summary: "task archived..."` —— 操作员在之前运行期间归档了任务；你可能根本不应该运行，请仔细检查状态。
- `outcome: "blocked"` —— 之前的尝试被阻塞；现在线程中应该已经有了解除阻塞的评论。

## 不要 {#do-not}

- 用 `delegate_task` 替代 `kanban_create`。`delegate_task` 用于你运行内部的短推理子任务；`kanban_create` 用于跨 Agent 的交接，其生命周期超过一次 API 循环。
- 修改 `$HERMES_KANBAN_WORKSPACE` 之外的文件，除非任务正文要求这样做。
- 创建分配给自己的后续任务 —— 应分配给正确的专家。
- 完成一个你实际上没有完成的任务。改为阻塞它。

## 陷阱 {#pitfalls}

**任务状态可能在调度和你启动之间发生变化。** 从调度器认领到你的进程实际启动之间，任务可能已被阻塞、重新分配或归档。始终先执行 `kanban_show`。如果它报告 `blocked` 或 `archived`，立即停止 —— 你不应该运行。
**工作区可能包含过时的产物。** 尤其是 `dir:` 和 `worktree` 工作区可能会保留之前运行的文件。请阅读评论线程——它通常会说明为什么你要重新运行，以及工作区当前处于什么状态。

**在有指导工具可用时，不要依赖 CLI。** `kanban_*` 工具在所有终端后端（Docker、Modal、SSH）中都能工作。从你的终端工具运行 `hermes kanban &lt;verb&gt;` 会在容器化后端中失败，因为 CLI 没有安装在那里。如有疑问，请使用工具。

## CLI 回退（用于脚本编写） {#cli-fallback-for-scripting}

每个工具都有对应的 CLI 版本，供人工操作和脚本使用：
- `kanban_show` ↔ `hermes kanban show &lt;id&gt; --json`
- `kanban_complete` ↔ `hermes kanban complete &lt;id&gt; --summary "..." --metadata '{...}'`
- `kanban_block` ↔ `hermes kanban block &lt;id&gt; "reason"`
- `kanban_create` ↔ `hermes kanban create "title" --assignee &lt;profile&gt; [--parent &lt;id&gt;]`
- 等等。

在 Agent 内部使用工具；CLI 是为终端前的人类准备的。
