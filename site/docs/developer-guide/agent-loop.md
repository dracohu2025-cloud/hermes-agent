---
sidebar_position: 3
title: "Agent 循环内部机制"
description: "详细讲解 AIAgent 的执行过程、API 模式、工具、回调以及回退行为"
---

<a id="agent-loop-internals"></a>
# Agent 循环内部机制

核心编排引擎是 `run_agent.py` 中的 `AIAgent` 类——一个超过 15000 行的庞大文件，负责从提示组装到工具调度再到提供商故障切换的所有环节。

<a id="core-responsibilities"></a>
## 核心职责

`AIAgent` 负责以下事项：

- 通过 `prompt_builder.py` 组装有效的系统提示和工具模式
- 选择正确的提供商/API 模式（chat_completions、codex_responses、anthropic_messages）
- 发起支持中断的模型调用并具备取消能力
- 执行工具调用（顺序执行或通过线程池并发执行）
- 以 OpenAI 消息格式维护对话历史
- 处理压缩、重试以及回退模型切换
- 追踪父 Agent 和子 Agent 之间的迭代预算
- 在上下文丢失之前刷新持久化记忆

<a id="two-entry-points"></a>
## 两个入口点

```python
# 简单接口——返回最终回复字符串
response = agent.chat("Fix the bug in main.py")

# 完整接口——返回包含消息、元数据、用量统计的字典
result = agent.run_conversation(
    user_message="Fix the bug in main.py",
    system_message=None,           # 省略时自动构建
    conversation_history=None,      # 省略时从会话自动加载
    task_id="task_abc123"
)
```

`chat()` 是 `run_conversation()` 的一个轻量封装，从结果字典中提取 `final_response` 字段。

<a id="api-modes"></a>
## API 模式

Hermes 支持三种 API 执行模式，根据提供商选择、显式参数和 base URL 启发式规则确定：

| API 模式 | 用途 | 客户端类型 |
|----------|------|------------|
| `chat_completions` | OpenAI 兼容端点（OpenRouter、自定义、大多数提供商） | `openai.OpenAI` |
| `codex_responses` | OpenAI Codex / Responses API | `openai.OpenAI` + Responses 格式 |
| `anthropic_messages` | 原生 Anthropic Messages API | 通过适配器使用 `anthropic.Anthropic` |

模式决定消息如何格式化、工具调用如何结构化、响应如何解析以及缓存/流式如何工作。三种模式在 API 调用前后都会收敛到相同的内部消息格式（OpenAI 风格的 `role`/`content`/`tool_calls` 字典）。

**模式解析顺序：**
1. 显式的 `api_mode` 构造函数参数（最高优先级）
2. 提供商特定检测（例如 `anthropic` 提供商 → `anthropic_messages`）
3. Base URL 启发式规则（例如 `api.anthropic.com` → `anthropic_messages`）
4. 默认值：`chat_completions`

<a id="turn-lifecycle"></a>
## 回合生命周期

Agent 循环的每次迭代遵循以下顺序：

```text
run_conversation()
  1. 若未提供 task_id，则生成一个
  2. 将用户消息追加到对话历史
  3. 构建或复用缓存的系统提示（prompt_builder.py）
  4. 检查是否需要预压缩（上下文超过 50%）
  5. 根据对话历史构建 API 消息
     - chat_completions：直接使用 OpenAI 格式
     - codex_responses：转换为 Responses API 输入项
     - anthropic_messages：通过 anthropic_adapter.py 转换
  6. 注入临时提示层（预算警告、上下文压力）
  7. 如果是 Anthropic 则应用提示缓存标记
  8. 发起可中断的 API 调用（_interruptible_api_call）
  9. 解析响应：
     - 如果是 tool_calls：执行它们，追加结果，返回步骤 5
     - 如果是文本响应：持久化会话，如有需要刷新记忆，返回
```
<a id="message-format"></a>
### 消息格式

所有消息内部均采用 OpenAI 兼容格式：

```python
{"role": "system", "content": "..."}
{"role": "user", "content": "..."}
{"role": "assistant", "content": "...", "tool_calls": [...]}
{"role": "tool", "tool_call_id": "...", "content": "..."}
```

推理内容（来自支持扩展思考的模型）存储在 `assistant_msg["reasoning"]` 中，并可通过 `reasoning_callback` 选择性地显示。

<a id="message-alternation-rules"></a>
### 消息交替规则

Agent loop 强制执行严格的消息角色交替：

- 系统消息之后：`User → Assistant → User → Assistant → ...`
- 工具调用期间：`Assistant (with tool_calls) → Tool → Tool → ... → Assistant`
- **绝不允许**连续两条 assistant 消息
- **绝不允许**连续两条 user 消息
- **只有** `tool` 角色可以连续出现（并行工具结果）

Provider 会验证这些序列，并拒绝格式错误的历史记录。

<a id="interruptible-api-calls"></a>
## 可中断的 API 调用

API 请求被包装在 `_interruptible_api_call()` 中，该函数在后台线程中执行实际的 HTTP 调用，同时监控中断事件：

```text
┌────────────────────────────────────────────────────┐
│  主线程                       API 线程              │
│                                                    │
│  等待：                       HTTP POST             │
│    - 响应就绪           ───▶  发送到 provider       │
│    - 中断事件                                       │
│    - 超时                                           │
└────────────────────────────────────────────────────┘
```

当中断发生时（用户发送新消息、`/stop` 命令或信号）：
- API 线程被放弃（响应被丢弃）
- Agent 可以处理新的输入或正常关闭
- 不会将部分响应注入对话历史

<a id="tool-execution"></a>
## 工具执行

<a id="sequential-vs-concurrent"></a>
### 顺序执行与并发执行

当模型返回工具调用时：

- **单个工具调用** → 直接在主线程中执行
- **多个工具调用** → 通过 `ThreadPoolExecutor` 并发执行
  - 例外：标记为交互式的工具（例如 `clarify`）强制顺序执行
  - 无论完成顺序如何，结果都会按原始工具调用顺序重新插入

<a id="execution-flow"></a>
### 执行流程

```text
for each tool_call in response.tool_calls:
    1. 从 tools/registry.py 解析处理器
    2. 触发 pre_tool_call 插件钩子
    3. 检查是否为危险命令（tools/approval.py）
       - 如果是危险命令：调用 approval_callback，等待用户
    4. 使用参数 + task_id 执行处理器
    5. 触发 post_tool_call 插件钩子
    6. 将 {"role": "tool", "content": result} 追加到历史记录
```

<a id="agent-level-tools"></a>
### Agent 级别工具

部分工具会在到达 `handle_function_call()` **之前**被 `run_agent.py` 拦截：

| 工具 | 拦截原因 |
|------|----------|
| `todo` | 读取/写入 Agent 本地任务状态 |
| `memory` | 写入具有字符限制的持久化记忆文件 |
| `session_search` | 通过 Agent 的会话数据库查询会话历史 |
| `delegate_task` | 生成具有隔离上下文的子 Agent(s) |
这些工具直接修改 Agent 状态，并返回合成的工具结果，而不经过注册中心。

<a id="callback-surfaces"></a>
## 回调接口

`AIAgent` 支持平台特定的回调，这些回调在 CLI、网关和 ACP 集成中实现实时进度：

| 回调 | 触发时机 | 使用方 |
|----------|-----------|---------|
| `tool_progress_callback` | 每次工具执行前后 | CLI 旋转动画、网关进度消息 |
| `thinking_callback` | 模型开始/停止思考时 | CLI "思考中..." 指示器 |
| `reasoning_callback` | 模型返回推理内容时 | CLI 推理显示、网关推理块 |
| `clarify_callback` | 当调用 `clarify` 工具时 | CLI 输入提示、网关交互消息 |
| `step_callback` | 每次完整的 Agent 回合后 | 网关步骤追踪、ACP 进度 |
| `stream_delta_callback` | 每个流式 token（启用时） | CLI 流式显示 |
| `tool_gen_callback` | 当从流中解析出工具调用时 | CLI 旋转动画中的工具预览 |
| `status_callback` | 状态变化（思考、执行等） | ACP 状态更新 |

<a id="budget-and-fallback-behavior"></a>
## 预算与回退行为

<a id="iteration-budget"></a>
### 迭代预算

Agent 通过 `IterationBudget` 跟踪迭代：

- 默认：90 次迭代（可通过 `agent.max_turns` 配置）
- 每个 Agent 有自己的预算。子 Agent 获得独立预算，上限为 `delegation.max_iterations`（默认 50）—— 父 Agent 与子 Agent 的总迭代次数可能超过父 Agent 的上限
- 达到 100% 时，Agent 停止并返回已完成工作的摘要

<a id="fallback-model"></a>
### 回退模型

当主模型失败（429 速率限制、5xx 服务器错误、401/403 认证错误）时：

1. 检查配置中的 `fallback_providers` 列表
2. 按顺序依次尝试每个回退
3. 成功时，用新的提供商继续对话
4. 遇到 401/403 时，在故障切换前尝试刷新凭证

回退系统也独立覆盖辅助任务 —— 视觉、压缩和网页提取各自拥有自己的回退链，可通过 `auxiliary.*` 配置部分进行配置。

<a id="compression-and-persistence"></a>
## 压缩与持久化

<a id="when-compression-triggers"></a>
### 压缩触发时机

- **预检**（API 调用前）：如果对话超出模型上下文窗口的 50%
- **网关自动压缩**：如果对话超出 85%（更激进，在回合之间运行）

<a id="what-happens-during-compression"></a>
### 压缩期间发生了什么

1. 内存首先刷新到磁盘（防止数据丢失）
2. 中间对话回合被总结为紧凑摘要
3. 最后 N 条消息保持完整（`compression.protect_last_n`，默认：20）
4. 工具调用/结果消息对保持在一起（从不拆分）
5. 生成新的会话谱系 ID（压缩创建一个"子"会话）

<a id="session-persistence"></a>
### 会话持久化

每次回合后：

- 消息保存到会话存储（通过 `hermes_state.py` 的 SQLite）
- 内存更改刷新到 `MEMORY.md` / `USER.md`
- 稍后可通过 `/resume` 或 `hermes chat --resume` 恢复会话

<a id="key-source-files"></a>
## 关键源文件

| 文件 | 用途 |
|------|---------|
| `run_agent.py` | AIAgent 类 — 完整的 Agent 循环 |
| `agent/prompt_builder.py` | 从内存、技能、上下文文件、个性组装系统提示 |
| `agent/context_engine.py` | ContextEngine ABC — 可插拔的上下文管理 |
| `agent/context_compressor.py` | 默认引擎 — 有损摘要算法 |
| `agent/prompt_caching.py` | Anthropic 提示缓存标记与缓存指标 |
| `agent/auxiliary_client.py` | 用于辅助任务（视觉、摘要）的辅助 LLM 客户端 |
| `model_tools.py` | 工具模式收集，`handle_function_call()` 分发 |
<a id="related-docs"></a>
## 相关文档

- [Provider 运行时解析](./provider-runtime.md)
- [提示词组装](./prompt-assembly.md)
- [上下文压缩与提示词缓存](./context-compression-and-caching.md)
- [工具运行时](./tools-runtime.md)
- [架构概览](./architecture.md)
