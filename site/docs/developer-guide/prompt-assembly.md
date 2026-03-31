---
sidebar_position: 5
title: "提示词组装"
description: "Hermes 如何构建系统提示词、保持缓存稳定性以及注入临时层"
---

# 提示词组装

Hermes 有意将以下两者分离：

- **缓存的系统提示词状态**
- **仅在 API 调用时添加的临时内容**

这是本项目最重要的设计选择之一，因为它影响：

- 令牌使用量
- 提示词缓存效率
- 会话连续性
- 记忆准确性

主要文件：

- `run_agent.py`
- `agent/prompt_builder.py`
- `tools/memory_tool.py`

## 缓存的系统提示词层

缓存的系统提示词大致按以下顺序组装：

1.  **代理身份** — 当可用时，从 `HERMES_HOME` 加载 `SOUL.md`，否则回退到 `prompt_builder.py` 中的 `DEFAULT_AGENT_IDENTITY`
2.  工具感知行为指导
3.  Honcho 静态块（激活时）
4.  可选的系统消息
5.  冻结的 MEMORY 快照
6.  冻结的 USER 个人资料快照
7.  技能索引
8.  上下文文件（`AGENTS.md`、`.cursorrules`、`.cursor/rules/*.mdc`）— 如果 `SOUL.md` 已在步骤 1 作为身份加载，则**不会**在此处再次包含
9.  时间戳 / 可选的会话 ID
10. 平台提示

当设置了 `skip_context_files` 时（例如，子代理委托），不会加载 `SOUL.md`，而是使用硬编码的 `DEFAULT_AGENT_IDENTITY`。

## 仅限 API 调用时的层

这些内容特意**不**作为缓存的系统提示词的一部分持久化：

- `ephemeral_system_prompt`
- 预填充消息
- 网关派生的会话上下文覆盖层
- 注入到当前轮次用户消息中的后续轮次 Honcho 回忆

这种分离确保了稳定的前缀部分保持稳定，以便进行缓存。

## 记忆快照

本地记忆和用户个人资料数据在会话开始时作为冻结的快照注入。会话中途的写入会更新磁盘状态，但不会改变已构建的系统提示词，直到新的会话开始或发生强制重建。

## 上下文文件

`agent/prompt_builder.py` 使用**优先级系统**扫描并清理项目上下文文件 — 只加载一种类型（首次匹配成功者优先）：

1.  `.hermes.md` / `HERMES.md`（向上遍历至 git 根目录）
2.  `AGENTS.md`（递归目录遍历）
3.  `CLAUDE.md`（仅当前工作目录）
4.  `.cursorrules` / `.cursor/rules/*.mdc`（仅当前工作目录）

`SOUL.md` 通过 `load_soul_md()` 单独加载，用于身份槽位。当它成功加载时，`build_context_files_prompt(skip_soul=True)` 会防止它出现两次。

长文件在注入前会被截断。

## 技能索引

当技能工具可用时，技能系统会向提示词添加一个紧凑的技能索引。

## 为何如此拆分提示词组装

该架构特意优化以实现：

- 保持提供商端的提示词缓存
- 避免不必要地修改历史记录
- 保持记忆语义易于理解
- 允许网关/ACP/CLI 添加上下文而不污染持久化的提示词状态

## 相关文档

- [上下文压缩与提示词缓存](./context-compression-and-caching.md)
- [会话存储](./session-storage.md)
- [网关内部原理](./gateway-internals.md)
