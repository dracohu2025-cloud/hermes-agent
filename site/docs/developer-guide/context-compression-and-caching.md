# 上下文压缩与缓存 (Context Compression and Caching)

Hermes Agent 使用双重压缩系统和 Anthropic prompt 缓存机制，在长对话中高效管理上下文窗口的使用。

源码文件：`agent/context_compressor.py`、`agent/prompt_caching.py`、`gateway/run.py`（会话清理）、`run_agent.py`（搜索 `_compress_context`）


## 双重压缩系统 (Dual Compression System)

Hermes 拥有两个相互独立的压缩层：

```
                     ┌──────────────────────────┐
  输入消息           │   Gateway 会话清理        │  在上下文达到 85% 时触发
  ─────────────────► │   (Agent 前置，粗略估算)  │  大型会话的安全网
                     └─────────────┬────────────┘
                                   │
                                   ▼
                     ┌──────────────────────────┐
                     │   Agent 上下文压缩器      │  在上下文达到 50% 时触发 (默认)
                     │   (循环内，精确 Token)    │  常规上下文管理
                     └──────────────────────────┘
```

### 1. Gateway 会话清理 (85% 阈值)

位于 `gateway/run.py`（搜索 `_maybe_compress_session`）。这是一个**安全网**，在 Agent 处理消息之前运行。它能防止会话在轮次之间增长过大（例如在 Telegram/Discord 中一夜之间积累的消息）而导致的 API 失败。

- **阈值**：固定为模型上下文长度的 85%
- **Token 来源**：优先使用上一轮 API 实际报告的 Token 数；若无则回退到基于字符的粗略估算 (`estimate_messages_tokens_rough`)
- **触发条件**：仅当 `len(history) >= 4` 且启用了压缩时触发
- **目的**：捕获那些逃过了 Agent 自身压缩器处理的会话

Gateway 清理阈值故意设定得比 Agent 压缩器高。如果将其设为 50%（与 Agent 相同），会导致长会话在 Gateway 每一轮都发生过早压缩。

### 2. Agent 上下文压缩器 (50% 阈值，可配置)

位于 `agent/context_compressor.py`。这是**主要的压缩系统**，运行在 Agent 的工具循环（tool loop）内部，可以访问 API 报告的精确 Token 计数。


## 配置 (Configuration)

所有压缩设置均从 `config.yaml` 的 `compression` 键下读取：

```yaml
compression:
  enabled: true              # 启用/禁用压缩 (默认: true)
  threshold: 0.50            # 上下文窗口比例 (默认: 0.50 = 50%)
  target_ratio: 0.20         # 阈值中保留作为末尾消息的比例 (默认: 0.20)
  protect_last_n: 20         # 最小保护的末尾消息数 (默认: 20)
  summary_model: null        # 覆盖用于生成摘要的模型 (默认: 使用辅助模型)
```

### 参数详情

| 参数 | 默认值 | 范围 | 描述 |
|-----------|---------|-------|-------------|
| `threshold` | `0.50` | 0.0-1.0 | 当 Prompt Token ≥ `threshold × context_length` 时触发压缩 |
| `target_ratio` | `0.20` | 0.10-0.80 | 控制末尾保护的 Token 预算：`threshold_tokens × target_ratio` |
| `protect_last_n` | `20` | ≥1 | 始终保留的最近消息的最小数量 |
| `protect_first_n` | `3` | (硬编码) | 系统提示词 + 第一次对话始终保留 |

### 计算示例 (以 200K 上下文模型及默认值为例)

```
context_length       = 200,000
threshold_tokens     = 200,000 × 0.50 = 100,000
tail_token_budget    = 100,000 × 0.20 = 20,000
max_summary_tokens   = min(200,000 × 0.05, 12,000) = 10,000
```


## 压缩算法 (Compression Algorithm)

`ContextCompressor.compress()` 方法遵循 4 阶段算法：

### 阶段 1：清理旧的工具结果 (低成本，无 LLM 调用)

受保护末尾之外的旧工具结果（>200 字符）会被替换为：
```
[Old tool output cleared to save context space]
```

这是一个低成本的预处理步骤，可以从冗长的工具输出（文件内容、终端输出、搜索结果）中节省大量 Token。

### 阶段 2：确定边界

```
┌─────────────────────────────────────────────────────────────┐
│  消息列表                                                    │
│                                                             │
│  [0..2]  ← protect_first_n (系统提示词 + 第一次对话)          │
│  [3..N]  ← 中间轮次 → 将被摘要 (SUMMARIZED)                  │
│  [N..末尾] ← 末尾 (根据 Token 预算或 protect_last_n 确定)     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

末尾保护是**基于 Token 预算的**：从末尾向前遍历，累加 Token 直到预算耗尽。如果预算保护的消息数过少，则回退到固定的 `protect_last_n` 数量。

边界会自动对齐，以避免拆分 `tool_call`/`tool_result` 组。`_align_boundary_backward()` 方法会越过连续的工具结果找到所属的 Assistant 消息，从而保持组的完整性。

### 阶段 3：生成结构化摘要

中间轮次由辅助 LLM 使用结构化模板进行摘要：

```
## Goal
[用户试图完成的目标]

## Constraints & Preferences
[用户偏好、编码风格、约束条件、重要决策]

## Progress
### Done
[已完成的工作 —— 具体的文件路径、运行的命令、结果]
### In Progress
[目前正在进行的工作]
### Blocked
[遇到的任何阻塞点或问题]

## Key Decisions
[重要的技术决策及其原因]

## Relevant Files
[读取、修改或创建的文件 —— 附带简要说明]

## Next Steps
[下一步需要做什么]

## Critical Context
[特定的数值、错误消息、配置详情]
```

摘要预算随被压缩内容的多少而缩放：
- 公式：`content_tokens × 0.20`（`_SUMMARY_RATIO` 常量）
- 最小值：2,000 Token
- 最大值：`min(context_length × 0.05, 12,000)` Token

### 阶段 4：组装压缩后的消息

压缩后的消息列表包含：
1. 头部消息（在第一次压缩时，系统提示词后会附加一条说明）
2. 摘要消息（选择合适的角色以避免连续相同角色的冲突）
3. 末尾消息（保持原样）

孤立的 `tool_call`/`tool_result` 对由 `_sanitize_tool_pairs()` 清理：
- 引用了已删除调用的工具结果 → 删除
- 结果已被删除的工具调用 → 注入存根结果

### 迭代重新压缩

在后续的压缩中，之前的摘要会传递给 LLM，并指示其**更新**摘要而不是从头开始。这保证了信息在多次压缩中得以保留 —— 事项从 "In Progress" 移动到 "Done"，添加新进展，并删除过时信息。

压缩器实例上的 `_previous_summary` 字段为此目的存储了上一次的摘要文本。


## 压缩前/后示例

### 压缩前 (45 条消息, ~95K Token)

```
[0] system:    "You are a helpful assistant..." (系统提示词)
[1] user:      "Help me set up a FastAPI project"
[2] assistant: <tool_call> terminal: mkdir project </tool_call>
[3] tool:      "directory created"
[4] assistant: <tool_call> write_file: main.py </tool_call>
[5] tool:      "file written (2.3KB)"
    ... 经过 30 轮文件编辑、测试、调试 ...
[38] assistant: <tool_call> terminal: pytest </tool_call>
[39] tool:      "8 passed, 2 failed\n..."  (5KB 输出)
[40] user:      "Fix the failing tests"
[41] assistant: <tool_call> read_file: tests/test_api.py </tool_call>
[42] tool:      "import pytest\n..."  (3KB)
[43] assistant: "I see the issue with the test fixtures..."
[44] user:      "Great, also add error handling"
```

### 压缩后 (25 条消息, ~45K Token)

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

源码位置：`agent/prompt_caching.py`

通过缓存对话前缀，在多轮对话中可降低约 75% 的输入 Token 成本。该功能使用了 Anthropic 的 `cache_control` 断点机制。

### 策略：system_and_3

Anthropic 允许每次请求最多设置 4 个 `cache_control` 断点。Hermes 采用了 "system_and_3" 策略：

```
断点 1：系统提示词 (System prompt)      （在所有轮次中保持稳定）
断点 2：倒数第 3 条非系统消息           ─┐
断点 3：倒数第 2 条非系统消息            ├─ 滚动窗口
断点 4：最后一条非系统消息              ─┘
```

### 工作原理

`apply_anthropic_cache_control()` 会深拷贝消息列表并注入 `cache_control` 标记：

```python
# 缓存标记格式
marker = {"type": "ephemeral"}
# 或者设置 1 小时 TTL：
marker = {"type": "ephemeral", "ttl": "1h"}
```

标记会根据内容类型以不同方式应用：

| 内容类型 | 标记位置 |
|-------------|-------------------|
| 字符串内容 | 转换为 `[{"type": "text", "text": ..., "cache_control": ...}]` |
| 列表内容 | 添加到最后一个元素的字典中 |
| None/空内容 | 添加为 `msg["cache_control"]` |
| 工具消息 (Tool messages) | 添加为 `msg["cache_control"]` (仅限原生 Anthropic) |

### 缓存感知设计模式

1. **稳定的系统提示词**：系统提示词作为断点 1，在所有轮次中都会被缓存。避免在对话中途修改它（压缩功能仅在第一次压缩时追加注释）。

2. **消息顺序至关重要**：缓存命中需要前缀匹配。在中间添加或删除消息会导致其后所有内容的缓存失效。

3. **压缩与缓存的交互**：压缩后，被压缩区域的缓存会失效，但系统提示词的缓存依然存在。滚动的 3 消息窗口会在 1-2 轮内重新建立缓存。

4. **TTL 选择**：默认值为 `5m`（5 分钟）。对于用户在轮次之间有停顿的长会话，建议使用 `1h`。

### 启用 Prompt Caching

当满足以下条件时，Prompt Caching 会自动启用：
- 模型是 Anthropic Claude 模型（通过模型名称检测）
- 提供商支持 `cache_control`（原生 Anthropic API 或 OpenRouter）

```yaml
# config.yaml — TTL 是可配置的
model:
  cache_ttl: "5m"   # "5m" 或 "1h"
```

CLI 在启动时会显示缓存状态：
```
💾 Prompt caching: ENABLED (Claude via OpenRouter, 5m TTL)
```


## 上下文压力警告 (Context Pressure Warnings)

当达到压缩阈值的 85% 时，Agent 会发出上下文压力警告（注意：是阈值的 85%，而不是总上下文的 85% —— 阈值本身通常是总上下文的 50%）：

```
⚠️  Context is 85% to compaction threshold (42,500/50,000 tokens)
```

压缩后，如果使用量降至阈值的 85% 以下，警告状态将被清除。如果压缩后仍无法降至警告线以下（说明对话内容过于密集），警告将持续存在，但直到再次超过阈值前不会重新触发压缩。
