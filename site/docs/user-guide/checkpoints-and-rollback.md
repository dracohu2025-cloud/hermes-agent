---
sidebar_position: 8
sidebar_label: "Checkpoints & Rollback"
title: "Checkpoints 与 /rollback"
description: "使用影子 git 仓库和自动快照，为破坏性操作提供文件系统安全网"
---

# Checkpoints 与 `/rollback` {#checkpoints-and-rollback}

Hermes Agent 会在执行 **破坏性操作** 之前自动为你的项目拍摄快照，并允许你通过一条命令恢复。Checkpoints **默认开启** —— 当没有触发文件修改工具时，它不会产生任何开销。

这一安全网由内部的 **Checkpoint Manager** 驱动，它在 `~/.hermes/checkpoints/` 下维护一个独立的影子 git 仓库 —— 你项目真实的 `.git` 永远不会被触碰。

## 什么会触发 Checkpoint {#what-triggers-a-checkpoint}

在以下操作之前，系统会自动创建 Checkpoint：

- **文件工具** —— `write_file` 和 `patch`
- **破坏性终端命令** —— `rm`、`mv`、`sed -i`、`truncate`、`shred`、输出重定向 (`>`)，以及 `git reset`/`clean`/`checkout`

Agent 在**每个会话轮次中，针对每个目录最多创建一个 Checkpoint**，因此长时间的会话不会导致快照泛滥。

## 快速参考 {#quick-reference}

| 命令 | 描述 |
|---------|-------------|
| `/rollback` | 列出所有 Checkpoints 及其变更统计 |
| `/rollback <N>` | 恢复到 Checkpoint N（同时撤销上一个对话轮次） |
| `/rollback diff <N>` | 预览 Checkpoint N 与当前状态之间的差异 |
| `/rollback <N> <file>` | 从 Checkpoint N 恢复单个文件 |

## Checkpoints 工作原理 {#how-checkpoints-work}

从高层架构来看：

- Hermes 会检测工具是否即将修改工作树中的**文件**。
- 在每个对话轮次（每个目录）中，它会执行一次：
  - 为该文件解析出一个合理的项目根目录。
  - 初始化或重用与该目录绑定的**影子 git 仓库**。
  - 暂存并提交当前状态，并附带简短、易读的触发原因。
- 这些提交构成了 Checkpoint 历史记录，你可以通过 `/rollback` 进行检查和恢复。

```mermaid
flowchart LR
  user["用户命令\n(hermes, gateway)"]
  agent["AIAgent\n(run_agent.py)"]
  tools["文件与终端工具"]
  cpMgr["CheckpointManager"]
  shadowRepo["影子 git 仓库\n~/.hermes/checkpoints/<hash>"]

  user --> agent
  agent -->|"工具调用"| tools
  tools -->|"修改前\nensure_checkpoint()"| cpMgr
  cpMgr -->|"git add/commit"| shadowRepo
  cpMgr -->|"成功 / 跳过"| tools
  tools -->|"应用变更"| agent
```

## 配置 {#configuration}

Checkpoints 默认启用。在 `~/.hermes/config.yaml` 中进行配置：

```yaml
checkpoints:
  enabled: true          # 总开关 (默认: true)
  max_snapshots: 50      # 每个目录的最大 Checkpoint 数量
```

若要禁用：

```yaml
checkpoints:
  enabled: false
```

禁用后，Checkpoint Manager 将不执行任何操作，也不会尝试 git 操作。

## 列出 Checkpoints {#listing-checkpoints}

在 CLI 会话中输入：

```
/rollback
```

Hermes 会返回一个显示变更统计的格式化列表：

```text
📸 Checkpoints for /path/to/project:

  1. 4270a8c  2026-03-16 04:36  before patch  (1 file, +1/-0)
  2. eaf4c1f  2026-03-16 04:35  before write_file
  3. b3f9d2e  2026-03-16 04:34  before terminal: sed -i s/old/new/ config.py  (1 file, +1/-1)

  /rollback <N>             恢复到 Checkpoint N
  /rollback diff <N>        预览自 Checkpoint N 以来的变更
  /rollback <N> <file>      从 Checkpoint N 恢复单个文件
```

每个条目显示：

- 短哈希 (Short hash)
- 时间戳
- 原因（触发快照的操作）
- 变更摘要（修改的文件数、插入/删除行数）

## 使用 `/rollback diff` 预览变更 {#previewing-changes-with-rollback-diff}

在执行恢复之前，可以预览自某个 Checkpoint 以来发生了哪些变化：

```
/rollback diff 1
```

这将显示 git diff 统计摘要以及实际的差异内容：

```text
test.py | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)

diff --git a/test.py b/test.py
--- a/test.py
+++ b/test.py
@@ -1 +1 @@
-print('original content')
+print('modified content')
```

较长的 diff 会被限制在 80 行以内，以避免刷屏。

## 使用 `/rollback` 进行恢复 {#restoring-with-rollback}

通过编号恢复到指定的 Checkpoint：

```
/rollback 1
```

在后台，Hermes 会：

1. 验证影子仓库中是否存在目标提交。
2. 为当前状态拍摄一个 **rollback 前快照**，以便你稍后可以“撤销这次撤销”。
3. 恢复工作目录中被追踪的文件。
4. **撤销上一个对话轮次**，使 Agent 的上下文与恢复后的文件系统状态保持一致。

成功后显示：

```text
✅ 已恢复到 Checkpoint 4270a8c5: before patch
已自动保存 rollback 前的快照。
(^_^)b 已撤销 4 条消息。移除内容: "Now update test.py to ..."
  历史记录中剩余 4 条消息。
  对话轮次已撤销，以匹配恢复后的文件状态。
```

对话撤销功能确保 Agent 不会“记得”那些已经被回滚的变更，从而避免在下一轮对话中产生困惑。

## 单文件恢复 {#single-file-restore}

仅从 Checkpoint 恢复单个文件，而不影响目录中的其他部分：

```
/rollback 1 src/broken_file.py
```

当 Agent 修改了多个文件但你只想回退其中一个时，这非常有用。

## 安全与性能保护 {#safety-and-performance-guards}

为了保持 Checkpoint 过程的安全和高效，Hermes 应用了多项保护措施：

- **Git 可用性** —— 如果在 `PATH` 中找不到 `git`，Checkpoints 将被透明地禁用。
- **目录范围** —— Hermes 会跳过范围过大的目录（如根目录 `/`、家目录 `$HOME`）。
- **仓库大小** —— 包含超过 50,000 个文件的目录将被跳过，以避免缓慢的 git 操作。
- **无变更快照** —— 如果自上次快照以来没有发生任何变化，则会跳过该 Checkpoint。
- **非致命错误** —— Checkpoint Manager 内部的所有错误都会以 debug 级别记录日志；你的工具将继续运行。

## Checkpoints 存储位置 {#where-checkpoints-live}

所有影子仓库都存储在：

```text
~/.hermes/checkpoints/
  ├── <hash1>/   # 某个工作目录的影子 git 仓库
  ├── <hash2>/
  └── ...
```

每个 `<hash>` 都是根据工作目录的绝对路径生成的。在每个影子仓库中，你会发现：

- 标准的 git 内部文件 (`HEAD`, `refs/`, `objects/`)
- 一个包含精选忽略列表的 `info/exclude` 文件
- 一个指向原始项目根目录的 `HERMES_WORKDIR` 文件

通常情况下，你永远不需要手动触碰这些文件。

## 最佳实践 {#best-practices}

- **保持 Checkpoints 开启** —— 它们默认开启，且在没有文件修改时零开销。
- **恢复前使用 `/rollback diff`** —— 预览将要发生的变更，以便选择正确的 Checkpoint。
- **仅想撤销 Agent 驱动的变更时，使用 `/rollback`** 而不是 `git reset`。
- **结合 Git worktrees 使用** 以获得最大安全性 —— 将每个 Hermes 会话保持在独立的 worktree/分支中，并将 Checkpoints 作为额外的保护层。

关于在同一个仓库上并行运行多个 Agents，请参阅 [Git worktrees](./git-worktrees.md) 指南。
