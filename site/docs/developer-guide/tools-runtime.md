---
sidebar_position: 9
title: "工具运行时"
description: "工具注册表、工具集、分发和终端环境的运行时行为"
---

# 工具运行时

Hermes 工具是自注册的函数，它们被分组到工具集中，并通过一个中央注册/分发系统来执行。

主要文件：

- `tools/registry.py`
- `model_tools.py`
- `toolsets.py`
- `tools/terminal_tool.py`
- `tools/environments/*`

## 工具注册模型

每个工具模块在导入时都会调用 `registry.register(...)`。

`model_tools.py` 负责导入/发现工具模块，并构建模型使用的模式列表。

## 工具集解析

工具集是命名的工具包。Hermes 通过以下方式解析它们：

- 显式启用/禁用的工具集列表
- 平台预设（`hermes-cli`、`hermes-telegram` 等）
- 动态 MCP 工具集
- 精心策划的特殊用途集合，如 `hermes-acp`

## 分发

在运行时，工具通过中央注册表进行分发，但对于一些 Agent 级别的工具（如内存/待办事项/会话搜索处理），存在 Agent 循环的例外情况。

## 终端/运行时环境

终端系统支持多种后端：

- local
- docker
- ssh
- singularity
- modal
- daytona

它还支持：

- 按任务覆盖当前工作目录
- 后台进程管理
- PTY 模式
- 危险命令的审批回调

## 并发性

工具调用可以顺序执行或并发执行，具体取决于工具组合和交互需求。

## 相关文档

- [工具集参考](../reference/toolsets-reference.md)
- [内置工具参考](../reference/tools-reference.md)
- [Agent 循环内部原理](./agent-loop.md)
- [ACP 内部原理](./acp-internals.md)
