---
sidebar_position: 8
title: "会话存储"
description: "Hermes 如何将会话存储在 SQLite 中、维护谱系关系以及提供召回/搜索功能"
---

# 会话存储

Hermes 使用基于 SQLite 的会话存储作为历史对话状态的主要事实来源。

主要文件：

- `hermes_state.py`
- `gateway/session.py`
- `tools/session_search_tool.py`

## 主数据库

主存储位于：

```text
~/.hermes/state.db
```

它包含：

- 会话
- 消息
- 元数据，例如令牌计数和标题
- 谱系关系
- 全文搜索索引

## 每个会话存储的内容

重要会话元数据的示例：

- 会话 ID
- 来源/平台
- 标题
- 创建/更新时间戳
- 令牌计数
- 工具调用计数
- 存储的系统提示快照
- 压缩拆分后的父会话 ID

## 谱系

当 Hermes 压缩对话时，它可以在新的会话 ID 下继续，同时通过 `parent_session_id` 保留祖先关系。

这意味着恢复/搜索可以沿着会话家族进行，而不是将每个压缩片段视为无关的。

## Gateway 与 CLI 持久化

- CLI 直接使用状态数据库进行恢复/历史记录/搜索
- gateway 维护活跃会话映射，并且可能还维护额外的平台转录/状态文件
- 为了兼容性，一些遗留的 JSON/JSONL 产物仍然存在，但 SQLite 是主要的历史存储

## 会话搜索

`session_search` 工具使用会话数据库的搜索功能来检索和总结相关的过往工作。

## 相关文档

- [Gateway 内部机制](./gateway-internals.md)
- [提示词组装](./prompt-assembly.md)
- [上下文压缩与提示词缓存](./context-compression-and-caching.md)
