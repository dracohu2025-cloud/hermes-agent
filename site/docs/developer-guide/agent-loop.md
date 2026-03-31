---
sidebar_position: 3
title: "Agent 循环内部机制"
description: "详细解析 AIAgent 的执行流程、API 模式、工具、回调以及后备行为"
---

# Agent 循环内部机制

核心编排引擎是 `run_agent.py` 中的 `AIAgent`。

## 核心职责

`AIAgent` 负责：

- 组装有效的提示词和工具模式
- 选择正确的提供商/API 模式
- 发起可中断的模型调用
- 执行工具调用（顺序或并发）
- 维护会话历史记录
- 处理压缩、重试和后备模型

## API 模式

Hermes 目前支持三种 API 执行模式：

| API 模式 | 用途 |
|----------|----------|
| `chat_completions` | OpenAI 兼容的聊天端点，包括 OpenRouter 和大多数自定义端点 |
| `codex_responses` | OpenAI Codex / Responses API 路径 |
| `anthropic_messages` | 原生的 Anthropic Messages API |

模式由显式参数、提供商选择以及基础 URL 启发式规则共同决定。

## 轮次生命周期

```text
run_conversation()
  -> 生成有效的 task_id
  -> 追加当前用户消息
  -> 加载或构建缓存的系统提示
  -> 可能进行预检压缩
  -> 构建 api_messages
  -> 注入临时提示层
  -> 在适当时应用提示缓存
  -> 发起可中断的 API 调用
  -> 如果是工具调用：执行它们，追加工具结果，循环
  -> 如果是最终文本：持久化，清理，返回响应
```

## 可中断的 API 调用

Hermes 封装了 API 请求，以便可以从 CLI 或网关中断它们。

这很重要，因为：

- Agent 可能处于一个长时间的 LLM 调用中
- 用户可能在执行过程中发送新消息
- 后台系统可能需要取消语义

## 工具执行模式

Hermes 使用两种执行策略：

- 顺序执行，用于单个或交互式工具
- 并发执行，用于多个非交互式工具

并发工具执行在将工具响应重新插入对话历史记录时，会保留消息/结果的顺序。

## 回调接口

`AIAgent` 支持平台/集成回调，例如：

- `tool_progress_callback`
- `thinking_callback`
- `reasoning_callback`
- `clarify_callback`
- `step_callback`
- `stream_delta_callback`
- `tool_gen_callback`
- `status_callback`

这些回调是 CLI、网关和 ACP 集成如何流式传输中间进度以及处理交互式批准/澄清流程的方式。

## 预算和后备行为

Hermes 跟踪主 Agent 和子 Agent 之间共享的迭代预算。它还会在可用迭代窗口接近结束时注入预算压力提示。

后备模型支持允许 Agent 在主路径在支持的故障路径中失败时，切换提供商/模型。

## 压缩和持久化

在长时间运行之前和期间，Hermes 可能会：

- 在上下文丢失前刷新内存
- 压缩中间的对话轮次
- 压缩后将会话谱系拆分为新的会话 ID
- 保留最近的上下文和结构化的工具调用/结果一致性

## 接下来要阅读的关键文件

- `run_agent.py`
- `agent/prompt_builder.py`
- `agent/context_compressor.py`
- `agent/prompt_caching.py`
- `model_tools.py`

## 相关文档

- [提供商运行时解析](./provider-runtime.md)
- [提示词组装](./prompt-assembly.md)
- [上下文压缩与提示词缓存](./context-compression-and-caching.md)
- [工具运行时](./tools-runtime.md)
