---
sidebar_position: 3
title: "Agent Loop 内部机制"
description: "AIAgent 执行的详细讲解，包括 API 模式、工具、回调和降级行为"
---

# Agent Loop 内部机制 {#agent-loop-internals}

核心编排引擎是 `run_agent.py` 中的 `AIAgent` 类——大约 10,700 行代码，负责从 prompt 组装到工具分发再到 provider 故障转移的所有事情。

## 核心职责 {#core-responsibilities}

`AIAgent` 负责：

- 通过 `prompt_builder.py` 组装有效的系统 prompt 和工具 schema
- 选择正确的 provider/API 模式（chat_completions、codex_responses、anthropic_messages）
- 发起可中断的模型调用，支持取消操作
- 执行工具调用（顺序执行或通过线程池并发执行）
- 以 OpenAI 消息格式维护对话历史
- 处理压缩、重试和降级模型切换
- 在父 Agent 和子 Agent 之间跟踪迭代预算
- 在上下文丢失前刷新持久化记忆

## 两个入口 {#two-entry-points}

```python
# 简单接口 —— 返回最终响应字符串
response = agent.chat("Fix the bug in main.py")

# 完整接口 —— 返回包含消息、元数据、用量统计的字典
result = agent.run_conversation(
    user_message="Fix the bug in main.py",
    system_message=None,           # 省略时自动构建
    conversation_history=None,      # 省略时从会话自动加载
    task_id="task_abc123"
)
```

`chat()` 是 `run_conversation()` 的轻量包装，从结果字典中提取 `final_response` 字段。

## API 模式 {#api-modes}

Hermes 支持三种 API 执行模式，通过 provider 选择、显式参数和 base URL 启发式规则来确定：

| API 模式 | 用途 | Client 类型 |
|----------|------|-------------|
| `chat_completions` | OpenAI 兼容端点（OpenRouter、自定义、大多数 provider） | `openai.OpenAI` |
| `codex_responses` | OpenAI Codex / Responses API | `openai.OpenAI`，使用 Responses 格式 |
| `anthropic_messages` | 原生 Anthropic Messages API | `anthropic.Anthropic`，通过适配器调用 |

该模式决定了消息的格式、工具调用的结构、响应的解析方式，以及缓存/流式传输的工作方式。三种模式在 API 调用前后都会收敛到相同的内部消息格式（OpenAI 风格的 `role`/`content`/`tool_calls` 字典）。

**模式解析优先级：**
1. 显式 `api_mode` 构造参数（最高优先级）
2. Provider 特定检测（例如 `anthropic` provider → `anthropic_messages`）
3. Base URL 启发式规则（例如 `api.anthropic.com` → `anthropic_messages`）
4. 默认值：`chat_completions`

## 回合生命周期 {#turn-lifecycle}

Agent loop 的每次迭代遵循以下序列：

```text
run_conversation()
  1. 如未提供则生成 task_id
  2. 将用户消息追加到对话历史
  3. 构建或复用缓存的系统 prompt（prompt_builder.py）
  4. 检查是否需要进行预检压缩（上下文占用 >50%）
  5. 从对话历史构建 API 消息
     - chat_completions: 保持 OpenAI 格式不变
     - codex_responses: 转换为 Responses API 输入项
     - anthropic_messages: 通过 anthropic_adapter.py 转换
  6. 注入临时 prompt 层（预算警告、上下文压力提示）
  7. 如在 Anthropic 上则应用 prompt 缓存标记
  8. 发起可中断的 API 调用（_api_call_with_interrupt）
  9. 解析响应：
     - 如有 tool_calls：执行它们，追加结果，回到第 5 步
     - 如为文本响应：持久化会话，按需刷新记忆，返回
```

### 消息格式 {#message-format}

所有消息内部使用 OpenAI 兼容格式：

```python
{"role": "system", "content": "..."}
{"role": "user", "content": "..."}
{"role": "assistant", "content": "...", "tool_calls": [...]}
{"role": "tool", "tool_call_id": "...", "content": "..."}
```

推理内容（来自支持扩展思考的模型）存储在 `assistant_msg["reasoning"]` 中，可通过 `reasoning_callback` 选择性展示。

### 消息交替规则 {#message-alternation-rules}

Agent loop 强制执行严格的消息角色交替：

- 系统消息之后：`User → Assistant → User → Assistant → ...`
- 工具调用期间：`Assistant（带 tool_calls）→ Tool → Tool → ... → Assistant`
- **禁止**连续两条 assistant 消息
- **禁止**连续两条 user 消息
- **仅** `tool` 角色可以有连续条目（并行工具结果）
Provider 会校验这些序列，格式错误的历史记录会被拒绝。

## 可中断的 API 调用 {#interruptible-api-calls}

API 请求被包裹在 `_api_call_with_interrupt()` 中，该函数在后台线程中执行实际的 HTTP 调用，同时监控中断事件：

```text
┌────────────────────────────────────────────────────┐
│  主线程                        API 线程            │
│                                                    │
│   等待：                        HTTP POST          │
│    - 响应就绪          ───▶     发送至 Provider    │
│    - 中断事件                                      │
│    - 超时                                          │
└────────────────────────────────────────────────────┘
```

被中断时（用户发送新消息、`/stop` 命令或信号）：
- API 线程被放弃（响应丢弃）
- Agent 可以处理新输入或干净地关闭
- 部分响应不会被注入到对话历史中

## 工具执行 {#tool-execution}

### 顺序执行 vs 并发执行 {#sequential-vs-concurrent}

当模型返回工具调用时：

- **单个工具调用** → 在主线程中直接执行
- **多个工具调用** → 通过 `ThreadPoolExecutor` 并发执行
  - 例外：标记为交互式的工具（如 `clarify`）强制顺序执行
  - 无论完成顺序如何，结果都会按原始工具调用顺序重新插入

### 执行流程 {#execution-flow}

```text
for each tool_call in response.tool_calls:
    1. 从 tools/registry.py 解析处理器
    2. 触发 pre_tool_call 插件钩子
    3. 检查是否为危险命令（tools/approval.py）
       - 如果是危险命令：调用 approval_callback，等待用户确认
    4. 使用 args + task_id 执行处理器
    5. 触发 post_tool_call 插件钩子
    6. 将 {"role": "tool", "content": result} 追加到历史记录
```

### Agent 级别工具 {#agent-level-tools}

部分工具会在到达 `handle_function_call()` 之前被 `run_agent.py` 拦截：

| 工具 | 拦截原因 |
|------|---------|
| `todo` | 读写 Agent 本地任务状态 |
| `memory` | 写入持久化记忆文件，有字符数限制 |
| `session_search` | 通过 Agent 的会话数据库查询会话历史 |
| `delegate_task` | 生成具有独立上下文的子 Agent |

这些工具直接修改 Agent 状态，并返回合成工具结果，不经过注册表。

## 回调接口 {#callback-surfaces}

`AIAgent` 支持平台特定的回调，可在 CLI、网关和 ACP 集成中实现实时进度展示：

| 回调 | 触发时机 | 使用者 |
|------|---------|--------|
| `tool_progress_callback` | 每次工具执行前/后 | CLI 加载动画、网关进度消息 |
| `thinking_callback` | 模型开始/停止思考时 | CLI "thinking..." 指示器 |
| `reasoning_callback` | 模型返回推理内容时 | CLI 推理展示、网关推理块 |
| `clarify_callback` | 调用 `clarify` 工具时 | CLI 输入提示、网关交互消息 |
| `step_callback` | 每次完整的 Agent 轮次后 | 网关步骤跟踪、ACP 进度 |
| `stream_delta_callback` | 每个流式 token（启用时） | CLI 流式展示 |
| `tool_gen_callback` | 从流式响应中解析出工具调用时 | CLI 加载动画中的工具预览 |
| `status_callback` | 状态变化（思考中、执行中等） | ACP 状态更新 |

## 预算与降级行为 {#budget-and-fallback-behavior}

### 迭代预算 {#iteration-budget}

Agent 通过 `IterationBudget` 跟踪迭代次数：

- 默认：90 次迭代（可通过 `agent.max_turns` 配置）
- 每个 Agent 拥有独立的预算。子 Agent 拥有独立预算，上限为 `delegation.max_iterations`（默认 50）——父 Agent + 子 Agent 的总迭代次数可以超过父 Agent 的上限
- 达到 100% 时，Agent 停止并返回已完成工作的摘要

### 降级模型 {#fallback-model}

当主模型失败时（429 速率限制、5xx 服务器错误、401/403 认证错误）：

1. 检查配置中的 `fallback_providers` 列表
2. 按顺序尝试每个降级选项
3. 成功时，使用新 Provider 继续对话
4. 遇到 401/403 时，在降级前尝试刷新凭证
备用系统也会独立覆盖辅助任务——视觉、压缩、网页提取和会话搜索各自都有独立的备用链，可通过 `auxiliary.*` 配置段进行设置。

## 压缩与持久化 {#compression-and-persistence}

### 压缩触发时机 {#when-compression-triggers}

- **预检**（API 调用前）：如果对话超过模型上下文窗口的 50%
- **网关自动压缩**：如果对话超过 85%（更激进，在轮次之间运行）

### 压缩期间会发生什么 {#what-happens-during-compression}

1. 内存先刷写到磁盘（防止数据丢失）
2. 对话中间轮次被总结为紧凑摘要
3. 最后 N 条消息保持原样（`compression.protect_last_n`，默认：20）
4. 工具调用/结果消息对保持在一起（不会拆分）
5. 生成新的会话谱系 ID（压缩会创建一个"子"会话）

### 会话持久化 {#session-persistence}

每轮结束后：
- 消息保存到会话存储（通过 `hermes_state.py` 的 SQLite）
- 内存变更刷写到 `MEMORY.md` / `USER.md`
- 之后可通过 `/resume` 或 `hermes chat --resume` 恢复会话

## 关键源文件 {#key-source-files}

| 文件 | 用途 |
|------|------|
| `run_agent.py` | AIAgent 类 —— 完整的 Agent 循环（约 10,700 行） |
| `agent/prompt_builder.py` | 从记忆、技能、上下文文件、个性组装系统提示词 |
| `agent/context_engine.py` | ContextEngine 抽象基类 —— 可插拔的上下文管理 |
| `agent/context_compressor.py` | 默认引擎 —— 有损摘要算法 |
| `agent/prompt_caching.py` | Anthropic 提示词缓存标记和缓存指标 |
| `agent/auxiliary_client.py` | 用于副任务的辅助 LLM 客户端（视觉、摘要） |
| `model_tools.py` | 工具模式集合、`handle_function_call()` 分发 |

## 相关文档 {#related-docs}

- [Provider 运行时解析](./provider-runtime.md)
- [提示词组装](./prompt-assembly.md)
- [上下文压缩与提示词缓存](./context-compression-and-caching.md)
- [工具运行时](./tools-runtime.md)
- [架构概览](./architecture.md)
