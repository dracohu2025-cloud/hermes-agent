---
sidebar_position: 3
title: "Agent 循环原理"
description: "深入解析 AIAgent 执行过程、API 模式、工具、回调以及回退行为"
---

# Agent 循环原理

核心编排引擎是 `run_agent.py` 中的 `AIAgent` 类 —— 这是一个大约 9,200 行的代码库，处理从 Prompt 组装、工具分发到供应商故障转移的所有事务。

## 核心职责

`AIAgent` 负责：

- 通过 `prompt_builder.py` 组装有效的系统 Prompt 和工具 Schema
- 选择正确的供应商/API 模式（chat_completions, codex_responses, anthropic_messages）
- 发起支持取消的可中断模型调用
- 执行工具调用（通过线程池顺序或并发执行）
- 以 OpenAI 消息格式维护对话历史
- 处理压缩、重试和回退模型切换
- 跟踪父 Agent 和子 Agent 的迭代预算
- 在上下文丢失前刷新持久化记忆

## 两个入口点

```python
# 简单接口 —— 返回最终响应字符串
response = agent.chat("Fix the bug in main.py")

# 完整接口 —— 返回包含消息、元数据、使用统计的字典
result = agent.run_conversation(
    user_message="Fix the bug in main.py",
    system_message=None,           # 如果省略则自动构建
    conversation_history=None,      # 如果省略则从会话自动加载
    task_id="task_abc123"
)
```

`chat()` 是对 `run_conversation()` 的一层薄封装，用于从结果字典中提取 `final_response` 字段。

## API 模式

Hermes 支持三种 API 执行模式，根据供应商选择、显式参数和 Base URL 启发式规则确定：

| API 模式 | 用于 | 客户端类型 |
|----------|----------|-------------|
| `chat_completions` | 兼容 OpenAI 的端点（OpenRouter、自定义、大多数供应商） | `openai.OpenAI` |
| `codex_responses` | OpenAI Codex / Responses API | 使用 Responses 格式的 `openai.OpenAI` |
| `anthropic_messages` | 原生 Anthropic Messages API | 通过适配器的 `anthropic.Anthropic` |

该模式决定了消息如何格式化、工具调用如何结构化、响应如何解析以及缓存/流式传输如何工作。在 API 调用前后，所有三种模式都会收敛到相同的内部消息格式（OpenAI 风格的 `role`/`content`/`tool_calls` 字典）。

**模式确定优先级：**
1. 构造函数显式传入的 `api_mode` 参数（最高优先级）
2. 特定供应商检测（例如：`anthropic` 供应商 → `anthropic_messages`）
3. Base URL 启发式规则（例如：`api.anthropic.com` → `anthropic_messages`）
4. 默认值：`chat_completions`

## 轮次生命周期

Agent 循环的每次迭代遵循以下序列：

```text
run_conversation()
  1. 如果未提供则生成 task_id
  2. 将用户消息追加到对话历史
  3. 构建或重用缓存的系统 Prompt (prompt_builder.py)
  4. 检查是否需要预检压缩（上下文占用 >50%）
  5. 从对话历史构建 API 消息
     - chat_completions: 直接使用 OpenAI 格式
     - codex_responses: 转换为 Responses API 输入项
     - anthropic_messages: 通过 anthropic_adapter.py 转换
  6. 注入临时 Prompt 层（预算警告、上下文压力）
  7. 如果使用 Anthropic，应用 Prompt 缓存标记
  8. 发起可中断的 API 调用 (_api_call_with_interrupt)
  9. 解析响应：
     - 如果是 tool_calls：执行它们，追加结果，返回步骤 5 循环
     - 如果是文本响应：持久化会话，必要时刷新记忆，返回结果
```

### 消息格式

所有消息在内部均使用兼容 OpenAI 的格式：

```python
{"role": "system", "content": "..."}
{"role": "user", "content": "..."}
{"role": "assistant", "content": "...", "tool_calls": [...]}
{"role": "tool", "tool_call_id": "...", "content": "..."}
```

推理内容（来自支持深度思考的模型）存储在 `assistant_msg["reasoning"]` 中，并可选地通过 `reasoning_callback` 显示。

### 消息交替规则

Agent 循环强制执行严格的消息角色交替：

- 在系统消息之后：`User → Assistant → User → Assistant → ...`
- 在工具调用期间：`Assistant (带有 tool_calls) → Tool → Tool → ... → Assistant`
- **绝不允许**连续两个 Assistant 消息
- **绝不允许**连续两个 User 消息
- **仅** `tool` 角色可以有连续条目（并行工具结果）

供应商会验证这些序列，并拒绝格式错误的上下文历史。

## 可中断的 API 调用

API 请求被封装在 `_api_call_with_interrupt()` 中，它在后台线程运行实际的 HTTP 调用，同时监控中断事件：

```text
┌──────────────────────┐     ┌──────────────┐
│  主线程              │     │  API 线程     │
│  等待：              │────▶│  向供应商发送  │
│  - 响应就绪          │     │  HTTP POST   │
│  - 中断事件          │     └──────────────┘
│  - 超时              │
└──────────────────────┘
```

当被中断时（用户发送新消息、`/stop` 命令或信号）：
- API 线程被放弃（丢弃响应）
- Agent 可以处理新输入或干净地关闭
- 不会有部分响应被注入到对话历史中

## 工具执行

### 顺序执行 vs 并发执行

当模型返回工具调用时：

- **单个工具调用** → 直接在主线程中执行
- **多个工具调用** → 通过 `ThreadPoolExecutor` 并发执行
  - 特例：标记为交互式的工具（如 `clarify`）强制顺序执行
  - 无论完成顺序如何，结果都会按原始工具调用顺序重新插入

### 执行流程

```text
针对 response.tool_calls 中的每个 tool_call:
    1. 从 tools/registry.py 解析处理器 (handler)
    2. 触发 pre_tool_call 插件钩子
    3. 检查是否为危险命令 (tools/approval.py)
       - 如果危险：调用 approval_callback，等待用户许可
    4. 使用参数 + task_id 执行处理器
    5. 触发 post_tool_call 插件钩子
    6. 将 {"role": "tool", "content": result} 追加到历史记录
```

### Agent 级工具

某些工具在到达 `handle_function_call()` *之前*会被 `run_agent.py` 拦截：

| 工具 | 拦截原因 |
|------|--------------------|
| `todo` | 读写 Agent 本地任务状态 |
| `memory` | 写入具有字符限制的持久化记忆文件 |
| `session_search` | 通过 Agent 的会话数据库查询会话历史 |
| `delegate_task` | 启动具有隔离上下文的子 Agent |

这些工具直接修改 Agent 状态并返回合成的工具结果，不经过注册表。

## 回调接口

`AIAgent` 支持特定平台的回调，以便在 CLI、网关和 ACP 集成中实现实时进度展示：

| 回调 | 触发时机 | 使用者 |
|----------|-----------|---------|
| `tool_progress_callback` | 每次工具执行前后 | CLI 加载动画、网关进度消息 |
| `thinking_callback` | 模型开始/停止思考时 | CLI "thinking..." 指示器 |
| `reasoning_callback` | 模型返回推理内容时 | CLI 推理显示、网关推理块 |
| `clarify_callback` | 调用 `clarify` 工具时 | CLI 输入提示、网关交互式消息 |
| `step_callback` | 每个完整的 Agent 轮次后 | 网关步骤跟踪、ACP 进度 |
| `stream_delta_callback` | 每个流式 Token（启用时） | CLI 流式显示 |
| `tool_gen_callback` | 从流中解析出工具调用时 | CLI 加载动画中的工具预览 |
| `status_callback` | 状态变更（思考中、执行中等） | ACP 状态更新 |

## 预算与回退行为

### 迭代预算

Agent 通过 `IterationBudget` 跟踪迭代次数：

- 默认值：90 次迭代（可通过 `agent.max_turns` 配置）
- 在父 Agent 和子 Agent 之间共享 —— 子 Agent 会消耗父 Agent 的预算
- 通过 `_get_budget_warning()` 实现两级预算压力提示：
  - 使用量达到 70%+（注意级别）：在最后一个工具结果中追加 `[BUDGET: Iteration X/Y. N iterations left. Start consolidating your work.]`
  - 使用量达到 90%+（警告级别）：追加 `[BUDGET WARNING: Iteration X/Y. Only N iteration(s) left. Provide your final response NOW.]`
- 达到 100% 时，Agent 停止并返回已完成工作的摘要

### 回退模型

当主模型失败时（429 频率限制、5xx 服务器错误、401/403 认证错误）：
1. 检查配置中的 `fallback_providers` 列表
2. 按顺序尝试每个备用方案
3. 成功后，使用新的 provider 继续对话
4. 遇到 401/403 错误时，在故障转移前尝试刷新凭据

备用系统还独立覆盖了辅助任务 —— 视觉（vision）、压缩（compression）、网页提取（web extraction）和会话搜索（session search）都有各自的备用链，可通过 `auxiliary.*` 配置部分进行设置。

## 压缩与持久化

### 压缩触发时机

- **Preflight**（API 调用前）：如果对话内容超过模型上下文窗口的 50%
- **Gateway 自动压缩**：如果对话内容超过 85%（更激进，在轮次之间运行）

### 压缩过程中发生了什么

1. 内存首先刷新到磁盘（防止数据丢失）
2. 中间的对话轮次被概括为一段精简的摘要
3. 最后 N 条消息保持原样保留（`compression.protect_last_n`，默认值：20）
4. Tool call/result 消息对保持完整（永不拆分）
5. 生成新的会话谱系 ID（压缩会创建一个“子”会话）

### 会话持久化

在每一轮对话后：
- 消息被保存到会话存储中（通过 `hermes_state.py` 存入 SQLite）
- 内存更改被刷新到 `MEMORY.md` / `USER.md`
- 稍后可以通过 `/resume` 或 `hermes chat --resume` 恢复会话

## 关键源文件

| 文件 | 用途 |
|------|---------|
| `run_agent.py` | AIAgent 类 —— 完整的 Agent 循环（约 9,200 行） |
| `agent/prompt_builder.py` | 从内存、技能、上下文文件、性格设置中组装系统提示词 |
| `agent/context_compressor.py` | 对话压缩算法 |
| `agent/prompt_caching.py` | Anthropic 提示词缓存标记和缓存指标 |
| `agent/auxiliary_client.py` | 用于侧边任务（视觉、摘要）的辅助 LLM 客户端 |
| `model_tools.py` | Tool schema 收集，`handle_function_call()` 调度 |

## 相关文档

- [Provider 运行时解析](./provider-runtime.md)
- [Prompt 组装](./prompt-assembly.md)
- [上下文压缩与 Prompt 缓存](./context-compression-and-caching.md)
- [Tools 运行时](./tools-runtime.md)
- [架构概览](./architecture.md)
