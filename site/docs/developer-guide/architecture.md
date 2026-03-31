---
sidebar_position: 1
title: "架构"
description: "Hermes Agent 内部结构 — 主要子系统、执行路径及后续阅读指引"
---

# 架构

本文档是 Hermes Agent 内部结构的顶层地图。该项目已发展成一个超越单一循环的复杂系统，因此按子系统来理解是最佳方式。

## 高层结构

```text
hermes-agent/
├── run_agent.py              # AIAgent 核心循环
├── cli.py                    # 交互式终端 UI
├── model_tools.py            # 工具发现与编排
├── toolsets.py               # 工具分组和预设
├── hermes_state.py           # SQLite 会话/状态数据库
├── batch_runner.py           # 批量轨迹生成
│
├── agent/                    # 提示词构建、压缩、缓存、元数据、轨迹
├── hermes_cli/               # 命令入口点、认证、设置、模型、配置、诊断
├── tools/                    # 工具实现和终端环境
├── gateway/                  # 消息网关、会话路由、投递、配对、钩子
├── cron/                     # 定时任务存储和调度器
├── honcho_integration/       # Honcho 记忆集成
├── acp_adapter/              # ACP 编辑器集成服务器
├── acp_registry/             # ACP 注册表清单 + 图标
├── environments/             # Hermes RL / 基准测试环境框架
├── skills/                   # 内置技能
├── optional-skills/          # 官方可选技能
└── tests/                    # 测试套件
```

## 推荐阅读顺序

如果你是代码库的新手，请按此顺序阅读：

1.  本页
2.  [Agent 循环内部机制](./agent-loop.md)
3.  [提示词组装](./prompt-assembly.md)
4.  [Provider 运行时解析](./provider-runtime.md)
5.  [添加 Providers](./adding-providers.md)
6.  [工具运行时](./tools-runtime.md)
7.  [会话存储](./session-storage.md)
8.  [网关内部机制](./gateway-internals.md)
9.  [上下文压缩与提示词缓存](./context-compression-and-caching.md)
10. [ACP 内部机制](./acp-internals.md)
11. [环境、基准测试与数据生成](./environments.md)

## 主要子系统

### Agent 循环

核心的同步编排引擎是 `run_agent.py` 中的 `AIAgent`。

它负责：

-   provider/API 模式选择
-   提示词构建
-   工具执行
-   重试和回退
-   回调
-   压缩和持久化

详见 [Agent 循环内部机制](./agent-loop.md)。

### 提示词系统

提示词构建逻辑分布在：

-   `run_agent.py`
-   `agent/prompt_builder.py`
-   `agent/prompt_caching.py`
-   `agent/context_compressor.py`

详见：

-   [提示词组装](./prompt-assembly.md)
-   [上下文压缩与提示词缓存](./context-compression-and-caching.md)

### Provider/运行时解析

Hermes 有一个共享的运行时 provider 解析器，供 CLI、网关、cron、ACP 和辅助调用使用。

详见 [Provider 运行时解析](./provider-runtime.md)。

### 工具运行时

工具注册表、工具集、终端后端、进程管理器和调度规则共同构成了一个独立的子系统。

详见 [工具运行时](./tools-runtime.md)。

### 会话持久化

历史会话状态主要存储在 SQLite 中，其谱系在压缩分割后仍被保留。

详见 [会话存储](./session-storage.md)。

### 消息网关

网关是一个长期运行的编排层，用于平台适配器、会话路由、配对、投递和 cron 定时触发。

详见 [网关内部机制](./gateway-internals.md)。

### ACP 集成

ACP 通过 stdio/JSON-RPC 将 Hermes 暴露为编辑器原生的智能体。

详见：

-   [ACP 编辑器集成](../user-guide/features/acp.md)
-   [ACP 内部机制](./acp-internals.md)

### Cron

Cron 作业被实现为一流的智能体任务，而不仅仅是 shell 任务。

详见 [Cron 内部机制](./cron-internals.md)。

### RL / 环境 / 轨迹

Hermes 附带了一个完整的环境框架，用于评估、RL 集成和 SFT 数据生成。

详见：

-   [环境、基准测试与数据生成](./environments.md)
-   [轨迹与训练格式](./trajectory-format.md)

## 设计主题

贯穿整个代码库有几个跨领域的设计主题：

-   提示词稳定性至关重要
-   工具执行必须是可观察且可中断的
-   会话持久化必须能经受长期运行的考验
-   平台前端应共享一个智能体核心
-   可选子系统应尽可能保持松耦合

## 实现说明

将 Hermes 视为“一个 OpenAI 兼容的聊天循环加上一些工具”的旧思维模型已不再适用。当前的 Hermes 包括：

-   多种 API 模式
-   辅助模型路由
-   ACP 编辑器集成
-   网关特定的会话和投递语义
-   RL 环境基础设施
-   具有谱系感知持久化能力的提示词缓存和压缩逻辑

请将本页作为地图，然后深入阅读特定子系统的文档以了解真正的实现细节。
