---
sidebar_position: 3
sidebar_label: "Git Worktrees"
title: "Git Worktrees"
description: "使用 git worktrees 和隔离的检出环境，在同一个仓库上安全地运行多个 Hermes Agent"
---

# Git Worktrees

Hermes Agent 经常被用于大型且长期维护的仓库。当你想要：

- 在同一个项目上**并行运行多个 Agent**，或者
- 让实验性的重构与主分支保持隔离，

Git **worktrees**（工作树）是为每个 Agent 提供独立检出环境且无需复制整个仓库的最安全方式。

本页将介绍如何将 worktrees 与 Hermes 结合使用，使每个会话都拥有一个干净、隔离的工作目录。

## 为什么在 Hermes 中使用 Worktrees？

Hermes 将**当前工作目录**视为项目根目录：

- CLI：你运行 `hermes` 或 `hermes chat` 的目录
- 消息网关：由 `MESSAGING_CWD` 设置的目录

如果你在**同一个检出目录**中运行多个 Agent，它们的更改可能会互相干扰：

- 一个 Agent 可能会删除或重写另一个 Agent 正在使用的文件。
- 很难分清哪些更改属于哪个实验。

通过使用 worktrees，每个 Agent 都会获得：

- 自己的**分支和工作目录**
- 自己的 **Checkpoint Manager 历史记录**，用于执行 `/rollback`

另请参阅：[Checkpoints 与 /rollback](./checkpoints-and-rollback.md)。

## 快速上手：创建一个 Worktree

在你的主仓库（包含 `.git/` 的目录）中，为一个功能分支创建一个新的 worktree：

```bash
# 进入主仓库根目录
cd /path/to/your/repo

# 在 ../repo-feature 中创建一个新分支和 worktree
git worktree add ../repo-feature feature/hermes-experiment
```

这将创建：

- 一个新目录：`../repo-feature`
- 一个在该目录中检出的新分支：`feature/hermes-experiment`

现在你可以 `cd` 进入新的 worktree 并在那里运行 Hermes：

```bash
cd ../repo-feature

# 在 worktree 中启动 Hermes
hermes
```

Hermes 将会：

- 将 `../repo-feature` 视为项目根目录。
- 使用该目录进行上下文文件读取、代码编辑和工具调用。
- 使用**独立的 Checkpoint 历史记录**进行 `/rollback`，其范围仅限于此 worktree。

## 并行运行多个 Agent

你可以创建多个 worktree，每个都有自己的分支：

```bash
cd /path/to/your/repo

git worktree add ../repo-experiment-a feature/hermes-a
git worktree add ../repo-experiment-b feature/hermes-b
```

在不同的终端中：

```bash
# 终端 1
cd ../repo-experiment-a
hermes

# 终端 2
cd ../repo-experiment-b
hermes
```

每个 Hermes 进程：

- 在各自的分支上工作（`feature/hermes-a` 对比 `feature/hermes-b`）。
- 在不同的影子仓库哈希下写入 Checkpoint（由 worktree 路径派生）。
- 可以独立使用 `/rollback` 而不影响另一个进程。

这在以下场景中特别有用：

- 运行批量重构。
- 针对同一任务尝试不同的方案。
- 针对同一个上游仓库同时开启 CLI 和网关会话。

## 安全地清理 Worktree

当你完成实验后：

1. 决定是保留还是放弃这些工作。
2. 如果你想保留：
   - 像往常一样将分支合并到主分支。
3. 移除 worktree：

```bash
cd /path/to/your/repo

# 移除 worktree 目录及其引用
git worktree remove ../repo-feature
```

注意：

- 如果 worktree 中有未提交的更改，除非你强制执行，否则 `git worktree remove` 会拒绝移除。
- 移除 worktree **不会**自动删除分支；你可以使用常规的 `git branch` 命令来删除或保留分支。
- 位于 `~/.hermes/checkpoints/` 下的 Hermes Checkpoint 数据在移除 worktree 时不会被自动清理，但这些数据通常占用空间很小。

## 最佳实践

- **每个 Hermes 实验使用一个 worktree**
  - 为每个实质性的更改创建一个专用的分支/worktree。
  - 这样可以保持 Diff 聚焦，并使 PR 保持小巧且易于评审。
- **根据实验内容命名分支**
  - 例如：`feature/hermes-checkpoints-docs`，`feature/hermes-refactor-tests`。
- **频繁提交**
  - 使用 Git Commit 记录高层级的里程碑。
  - 使用 [Checkpoints 和 /rollback](./checkpoints-and-rollback.md) 作为工具驱动编辑过程中的安全网。
- **使用 worktrees 时避免从裸仓库根目录运行 Hermes**
  - 优先使用 worktree 目录，这样每个 Agent 都有明确的作用域。

## 使用 `hermes -w`（自动 Worktree 模式）

Hermes 内置了一个 `-w` 标志，可以**自动创建一个带有独立分支的一次性 Git Worktree**。你不需要手动设置 worktree —— 只需 `cd` 进入你的仓库并运行：

```bash
cd /path/to/your/repo
hermes -w
```

Hermes 将会：

- 在你仓库内的 `.worktrees/` 下创建一个临时 worktree。
- 检出一个隔离的分支（例如 `hermes/hermes-<hash>`）。
- 在该 worktree 中运行完整的 CLI 会话。

这是获得 worktree 隔离最简单的方法。你也可以将其与单次查询结合使用：

```bash
hermes -w -q "修复 issue #123"
```

对于并行 Agent，只需打开多个终端并在每个终端中运行 `hermes -w` —— 每次调用都会自动获得自己的 worktree 和分支。

## 总结

- 使用 **Git Worktrees** 为每个 Hermes 会话提供干净的独立检出环境。
- 使用**分支**来记录实验的高层级历史。
- 使用 **Checkpoints + `/rollback`** 来纠正每个 worktree 内部的编辑错误。

这种组合为你提供了：

- 强有力的保证，确保不同的 Agent 和实验互不干扰。
- 快速的迭代周期，并能轻松从错误的编辑中恢复。
- 干净、可评审的 Pull Request。
