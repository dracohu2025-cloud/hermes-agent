# 上下文压缩与缓存

Hermes Agent 使用双重压缩系统和 Anthropic 提示词缓存（Prompt Caching），以在长对话中高效管理上下文窗口的使用。

源文件：`agent/context_engine.py` (ABC), `agent/context_compressor.py` (默认引擎), `agent/prompt_caching.py`, `gateway/run.py` (会话清理), `run_agent.py` (搜索 `_compress_context`)

## 可插拔上下文引擎

上下文管理构建在 `ContextEngine` ABC (`agent/context_engine.py`) 之上。内置的 `ContextCompressor` 是默认实现，但插件可以将其替换为其他引擎（例如：无损上下文管理）。

```yaml
context:
  engine: "compressor"    # 默认 — 内置有损摘要
  engine: "lcm"           # 示例 — 提供无损上下文的插件
```

引擎负责：
- 决定何时触发压缩 (`should_compress()`)
- 执行压缩 (`compress()`)
- 可选地暴露 Agent 可以调用的工具（例如 `lcm_grep`）
- 跟踪来自 API 响应的 Token 使用情况

选择方式通过 `config.yaml` 中的 `context.engine` 进行配置。解析顺序如下：
1. 检查 `plugins/context_engine/<name>/` 目录
2. 检查通用插件系统 (`register_context_engine()`)
3. 回退到内置的 `ContextCompressor`

插件引擎**永远不会自动激活**——用户必须显式将 `context.engine` 设置为插件名称。默认的 `"compressor"` 始终使用内置引擎。

通过 `hermes plugins` → Provider Plugins → Context Engine 进行配置，或直接编辑 `config.yaml`。

关于构建上下文引擎插件，请参阅 [Context Engine Plugins](/developer-guide/context-engine-plugin)。

## 双重压缩系统

Hermes 拥有两个独立运行的压缩层：

```
                     ┌──────────────────────────┐
  传入消息             │   网关会话清理 (Gateway Session Hygiene) │  在上下文 85% 时触发
  ─────────────────► │   (Agent 前置，粗略估算)   │  大型会话的安全网
                     └─────────────┬────────────┘
                                   │
                                   ▼
                     ┌──────────────────────────┐
                     │   Agent ContextCompressor │  在上下文 50% 时触发 (默认)
                     │   (循环内，真实 Token)     │  常规上下文管理
                     └──────────────────────────┘
```

### 1. 网关会话清理 (85% 阈值)

位于 `gateway/run.py` (搜索 `_maybe_compress_session`)。这是一个在 Agent 处理消息之前运行的**安全网**。它防止了在多轮对话之间（例如 Telegram/Discord 中隔夜积累）会话变得过大时导致的 API 失败。

- **阈值**：固定为模型上下文长度的 85%
- **Token 来源**：优先使用上一轮 API 报告的实际 Token 数；回退到基于字符的粗略估算 (`estimate_messages_tokens_rough`)
- **触发条件**：仅在 `len(history) >= 4` 且启用了压缩时
- **目的**：捕获那些逃脱了 Agent 自身压缩器处理的会话

网关清理阈值特意设置得比 Agent 的压缩器更高。如果将其设置为 50%（与 Agent 相同），会导致长网关会话在每一轮都进行过早的压缩。

### 2. Agent ContextCompressor (50% 阈值，可配置)

位于 `agent/context_compressor.py`。这是运行在 Agent 工具循环内部的**主要压缩系统**，可以访问 API 报告的准确 Token 计数。

## 配置

所有压缩设置均从 `config.yaml` 中的 `compression` 键读取：

```yaml
compression:
  enabled: true              # 启用/禁用压缩 (默认: true)
  threshold: 0.50            # 上下文窗口的比例 (默认: 0.50 = 50%)
  target_ratio: 0.20         # 尾部保留阈值的比例 (默认: 0.20)
  protect_last_n: 20         # 最小受保护的尾部消息数 (默认: 20)
  summary_model: null        # 覆盖摘要模型 (默认: 使用辅助模型)
```

### 参数详情

| 参数 | 默认值 | 范围 | 描述 |
|-----------|---------|-------|-------------|
| `threshold` | `0.50` | 0.0-1.0 | 当提示词 Token ≥ `threshold × context_length` 时触发压缩 |
| `target_ratio` | `0.20` | 0.10-0.80 | 控制尾部保护的 Token 预算：`threshold_tokens × target_ratio` |
| `protect_last_n` | `20` | ≥1 | 始终保留的最近消息的最小数量 |
| `protect_first_n` | `3` | (硬编码) | 系统提示词 + 第一次交互始终保留 |

### 计算值（以 200K 上下文模型及默认配置为例）

```
context_length       = 200,000
threshold_tokens     = 200,000 × 0.50 = 100,000
tail_token_budget    = 100,000 × 0.20 = 20,000
max_summary_tokens   = min(200,000 × 0.05, 12,000) = 10,000
```

## 压缩算法

`ContextCompressor.compress()` 方法遵循 4 阶段算法：

### 阶段 1：修剪旧的工具结果（低成本，无 LLM 调用）

受保护尾部之外的旧工具结果（>200 字符）将被替换为：
```
[Old tool output cleared to save context space]
```

这是一个低成本的预处理步骤，可以从冗长的工具输出（文件内容、终端输出、搜索结果）中节省大量 Token。

### 阶段 2：确定边界

```
┌─────────────────────────────────────────────────────────────┐
│  消息列表                                                     │
│                                                             │
│  [0..2]  ← protect_first_n (系统 + 第一次交互)                │
│  [3..N]  ← 中间轮次 → 摘要化                                  │
│  [N..end] ← 尾部 (按 Token 预算 或 protect_last_n)            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

尾部保护是**基于 Token 预算的**：从末尾向回遍历，累积 Token 直到预算耗尽。如果预算保护的消息数少于 `protect_last_n`，则回退到固定的 `protect_last_n` 计数。

边界经过对齐以避免拆分 `tool_call`/`tool_result` 组。`_align_boundary_backward()` 方法会跳过连续的工具结果以找到父级 Assistant 消息，从而保持组的完整性。

### 阶段 3：生成结构化摘要

中间轮次使用辅助 LLM 结合结构化模板进行摘要：

```
## Goal
[用户试图完成的目标]

## Constraints & Preferences
[用户偏好、编码风格、约束、重要决策]

## Progress
### Done
[已完成的工作 — 具体文件路径、运行的命令、结果]
### In Progress
[当前正在进行的工作]
### Blocked
[遇到的任何阻碍或问题]

## Key Decisions
[重要的技术决策及其原因]

## Relevant Files
[读取、修改或创建的文件 — 每个文件附带简要说明]

## Next Steps
[接下来需要做什么]

## Critical Context
[特定值、错误消息、配置详情]
```

摘要预算随被压缩内容的大小进行缩放：
- 公式：`content_tokens × 0.20` (`_SUMMARY_RATIO` 常量)
- 最小值：2,000 Token
- 最大值：`min(context_length × 0.05, 12,000)` Token

### 阶段 4：组装压缩后的消息

压缩后的消息列表为：
1. 头部消息（首次压缩时在系统提示词后附加说明）
2. 摘要消息（选择角色以避免连续相同角色的违规）
3. 尾部消息（未修改）

孤立的 `tool_call`/`tool_result` 对由 `_sanitize_tool_pairs()` 清理：
- 引用已删除调用的工具结果 → 删除
- 结果已被删除的工具调用 → 注入存根结果

### 迭代重压缩

在后续压缩中，之前的摘要会被传递给 LLM，并指示其**更新**摘要，而不是从头开始总结。这保留了多次压缩过程中的信息——项目从“进行中”移动到“已完成”，添加了新的进度，并删除了过时的信息。

压缩器实例上的 `_previous_summary` 字段用于存储此目的的最后一次摘要文本。
## Before/After Example

### Before Compression (45 messages, ~95K tokens)

```
[0] system:    "You are a helpful assistant..." (system prompt)
[1] user:      "Help me set up a FastAPI project"
[2] assistant: <tool_call> terminal: mkdir project </tool_call>
[3] tool:      "directory created"
[4] assistant: <tool_call> write_file: main.py </tool_call>
[5] tool:      "file written (2.3KB)"
    ... 30 more turns of file editing, testing, debugging ...
[38] assistant: <tool_call> terminal: pytest </tool_call>
[39] tool:      "8 passed, 2 failed\n..."  (5KB output)
[40] user:      "Fix the failing tests"
[41] assistant: <tool_call> read_file: tests/test_api.py </tool_call>
[42] tool:      "import pytest\n..."  (3KB)
[43] assistant: "I see the issue with the test fixtures..."
[44] user:      "Great, also add error handling"
```

### After Compression (25 messages, ~45K tokens)

```
[0] system:    "You are a helpful assistant...
               [Note: Some earlier conversation turns have been compacted...]"
[1] user:      "Help me set up a FastAPI project"
[2] assistant: "[CONTEXT COMPACTION] Earlier turns were compacted...

               ## Goal
               Set up a FastAPI project with tests and error handling

               ## Progress
               ### Done
               - Created project structure: main.py, tests/, requirements.txt
               - Implemented 5 API endpoints in main.py
               - Wrote 10 test cases in tests/test_api.py
               - 8/10 tests passing

               ### In Progress
               - Fixing 2 failing tests (test_create_user, test_delete_user)

               ## Relevant Files
               - main.py — FastAPI app with 5 endpoints
               - tests/test_api.py — 10 test cases
               - requirements.txt — fastapi, pytest, httpx

               ## Next Steps
               - Fix failing test fixtures
               - Add error handling"
[3] user:      "Fix the failing tests"
[4] assistant: <tool_call> read_file: tests/test_api.py </tool_call>
[5] tool:      "import pytest\n..."
[6] assistant: "I see the issue with the test fixtures..."
[7] user:      "Great, also add error handling"
```


## Prompt Caching (Anthropic)

来源：`agent/prompt_caching.py`

通过缓存对话前缀，在多轮对话中将输入 token 成本降低约 75%。使用了 Anthropic 的 `cache_control` 断点。

### 策略：system_and_3

Anthropic 允许每个请求最多设置 4 个 `cache_control` 断点。Hermes 使用了“system_and_3”策略：

```
断点 1：系统提示词（System prompt）           （在所有轮次中保持稳定）
断点 2：倒数第 3 条非系统消息  ─┐
断点 3：倒数第 2 条非系统消息   ├─ 滑动窗口
断点 4：最后一条非系统消息      ─┘
```

### 工作原理

`apply_anthropic_cache_control()` 会对消息进行深拷贝并注入 `cache_control` 标记：

```python
# 缓存标记格式
marker = {"type": "ephemeral"}
# 或者设置 1 小时 TTL：
marker = {"type": "ephemeral", "ttl": "1h"}
```

标记会根据内容类型以不同方式应用：

| 内容类型 | 标记放置位置 |
|-------------|-------------------|
| 字符串内容 | 转换为 `[{"type": "text", "text": ..., "cache_control": ...}]` |
| 列表内容 | 添加到最后一个元素的字典中 |
| None/空 | 添加为 `msg["cache_control"]` |
| 工具消息 | 添加为 `msg["cache_control"]`（仅限 Anthropic 原生 API） |

### 缓存感知设计模式

1. **稳定的系统提示词**：系统提示词作为断点 1，在所有轮次中都会被缓存。请避免在对话中途修改它（压缩操作仅在首次压缩时附加说明）。

2. **消息顺序很重要**：缓存命中需要前缀匹配。在中间添加或删除消息会使后续所有内容的缓存失效。

3. **压缩与缓存的交互**：压缩后，压缩区域的缓存会失效，但系统提示词的缓存依然有效。3 条消息的滑动窗口会在 1-2 轮内重新建立缓存。

4. **TTL 选择**：默认值为 `5m`（5 分钟）。对于用户在轮次之间有间歇的长会话，请使用 `1h`。

### 启用 Prompt Caching

当满足以下条件时，Prompt Caching 会自动启用：
- 模型为 Anthropic Claude 模型（通过模型名称检测）
- 提供商支持 `cache_control`（原生 Anthropic API 或 OpenRouter）

```yaml
# config.yaml — TTL 可配置
model:
  cache_ttl: "5m"   # "5m" 或 "1h"
```

CLI 会在启动时显示缓存状态：
```
💾 Prompt caching: ENABLED (Claude via OpenRouter, 5m TTL)
```


## 上下文压力警告

当达到压缩阈值的 85% 时，Agent 会发出上下文压力警告（注意：不是上下文总量的 85%，而是阈值的 85%，而阈值本身是上下文总量的 50%）：

```
⚠️  Context is 85% to compaction threshold (42,500/50,000 tokens)
```

压缩后，如果使用量降至阈值的 85% 以下，警告状态会被清除。如果压缩未能将使用量降至警告水平以下（说明对话内容过于密集），警告将持续存在，但除非再次超过阈值，否则不会再次触发压缩。
