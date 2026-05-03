# 上下文压缩与缓存 {#context-compression-and-caching}

Hermes Agent 使用双重压缩系统和 Anthropic 提示缓存，在长对话中高效管理上下文窗口的使用。

源文件：`agent/context_engine.py`（ABC）、`agent/context_compressor.py`（默认引擎）、`agent/prompt_caching.py`、`gateway/run.py`（会话卫生）、`run_agent.py`（搜索 `_compress_context`）

## 可插拔的上下文引擎 {#pluggable-context-engine}

上下文管理基于 `ContextEngine` ABC（`agent/context_engine.py`）。内置的 `ContextCompressor` 是默认实现，但插件可以用其他引擎替换它（例如无损上下文管理）。

```yaml
context:
  engine: "compressor"    # 默认——内置的有损摘要
  engine: "lcm"           # 示例——提供无损上下文的插件
```

引擎负责：
- 决定何时触发压缩（`should_compress()`）
- 执行压缩（`compress()`）
- 可选地暴露 Agent 可以调用的工具（例如 `lcm_grep`）
- 跟踪 API 响应中的 token 使用量

选择通过 `config.yaml` 中的 `context.engine` 配置驱动。解析顺序：
1. 检查 `plugins/context_engine/&lt;name&gt;/` 目录
2. 检查通用插件系统（`register_context_engine()`）
3. 回退到内置的 `ContextCompressor`

插件引擎**永远不会自动激活**——用户必须显式地将 `context.engine` 设置为插件的名称。默认的 `"compressor"` 始终使用内置引擎。

通过 `hermes plugins` → Provider Plugins → Context Engine 配置，或直接编辑 `config.yaml`。

有关构建上下文引擎插件，请参阅[上下文引擎插件](/developer-guide/context-engine-plugin)。

## 双重压缩系统 {#dual-compression-system}

Hermes 有两个独立的压缩层，它们独立运行：

```
                     ┌──────────────────────────┐
  传入消息            │   网关会话卫生            │  在上下文的 85% 触发
  ─────────────────► │   (pre-agent, 粗略估计)   │  大型会话的安全网
                     └─────────────┬────────────┘
                                   │
                                   ▼
                     ┌──────────────────────────┐
                     │   Agent ContextCompressor │  在上下文的 50% 触发（默认）
                     │   (循环内，真实 token)    │  正常的上下文管理
                     └──────────────────────────┘
```

### 1. 网关会话卫生（85% 阈值） {#1-gateway-session-hygiene-85-threshold}

位于 `gateway/run.py`（搜索 `Session hygiene: auto-compress`）。这是一个**安全网**，在 Agent 处理消息之前运行。它防止会话在轮次之间增长过大时导致 API 失败（例如 Telegram/Discord 中隔夜累积的消息）。

- **阈值**：固定为模型上下文长度的 85%
- **Token 来源**：优先使用上一轮 API 报告的实际 token；回退到基于字符的粗略估计（`estimate_messages_tokens_rough`）
- **触发条件**：仅当 `len(history) >= 4` 且压缩已启用时
- **目的**：捕获那些逃脱了 Agent 自身压缩器的会话
网关的卫生阈值故意设置得比 Agent 的压缩器更高。
如果设为 50%（与 Agent 相同），在长网关会话中每次轮次都会触发过早压缩。

### 2. Agent ContextCompressor（50% 阈值，可配置） {#2-agent-contextcompressor-50-threshold-configurable}

位于 `agent/context_compressor.py`。这是运行在 Agent 工具循环内部的**主要压缩系统**，可以访问 API 报告的准确 token 计数。


## 配置 {#configuration}

所有压缩设置均从 `config.yaml` 的 `compression` 键下读取：

```yaml
compression:
  enabled: true              # 启用/禁用压缩（默认：true）
  threshold: 0.50            # 上下文窗口比例（默认：0.50 = 50%）
  target_ratio: 0.20         # 保留尾部占阈值的比例（默认：0.20）
  protect_last_n: 20         # 最小保护尾部消息数（默认：20）

# 在 auxiliary 下配置摘要模型/提供商：
auxiliary:
  compression:
    model: null              # 覆盖摘要模型（默认：自动检测）
    provider: auto           # 提供商："auto"、"openrouter"、"nous"、"main" 等
    base_url: null           # 自定义 OpenAI 兼容端点
```

### 参数详情 {#parameter-details}

| 参数 | 默认值 | 范围 | 描述 |
|-----------|---------|-------|-------------|
| `threshold` | `0.50` | 0.0-1.0 | 当提示 token ≥ `threshold × context_length` 时触发压缩 |
| `target_ratio` | `0.20` | 0.10-0.80 | 控制尾部保护 token 预算：`threshold_tokens × target_ratio` |
| `protect_last_n` | `20` | ≥1 | 始终保留的最近消息最小数量 |
| `protect_first_n` | `3` | （硬编码） | 始终保留系统提示 + 首次交互 |

### 计算值（以默认值下的 200K 上下文模型为例） {#computed-values-for-a-200k-context-model-at-defaults}

```
context_length       = 200,000
threshold_tokens     = 200,000 × 0.50 = 100,000
tail_token_budget    = 100,000 × 0.20 = 20,000
max_summary_tokens   = min(200,000 × 0.05, 12,000) = 10,000
```


## 压缩算法 {#compression-algorithm}

`ContextCompressor.compress()` 方法遵循 4 阶段算法：

### 阶段 1：修剪旧工具结果（廉价，无需 LLM 调用） {#phase-1-prune-old-tool-results-cheap-no-llm-call}

受保护尾部之外的旧工具结果（>200 字符）将被替换为：
```
[Old tool output cleared to save context space]
```

这是一个廉价的预处理步骤，可从冗长的工具输出（文件内容、终端输出、搜索结果）中节省大量 token。

### 阶段 2：确定边界 {#phase-2-determine-boundaries}

```
┌─────────────────────────────────────────────────────────────┐
│  消息列表                                                   │
│                                                             │
│  [0..2]  ← protect_first_n（系统提示 + 首次交互）            │
│  [3..N]  ← 中间轮次 → 被摘要                                │
│  [N..end] ← 尾部（基于 token 预算或 protect_last_n）        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

尾部保护基于 **token 预算**：从末尾向前遍历，累积 token 直到预算耗尽。如果预算保护的消息数少于固定值，则回退到 `protect_last_n` 计数。
边界对齐是为了避免拆分 `tool_call` / `tool_result` 组。
`_align_boundary_backward()` 方法会向后遍历连续的 tool result，找到对应的 parent assistant 消息，保持组完整。

### 阶段 3：生成结构化摘要 {#phase-3-generate-structured-summary}

:::warning 摘要模型的上下文长度
摘要模型的上下文窗口必须**至少等于**主 Agent 模型的窗口。整个中间部分会通过一次 `call_llm(task="compression")` 调用发送给摘要模型。如果摘要模型的上下文较小，API 会返回上下文长度错误 —— `_generate_summary()` 会捕获该错误，记录一条警告，并返回 `None`。然后压缩器会**不带摘要**地丢弃中间轮次，静默丢失对话上下文。这是导致压缩质量下降的最常见原因。
:::

<a id="summary-model-context-length"></a>
中间轮次使用辅助 LLM 和结构化模板进行摘要：

```
## Goal
[What the user is trying to accomplish]

## Constraints & Preferences
[User preferences, coding style, constraints, important decisions]

## Progress
### Done
[Completed work — specific file paths, commands run, results]
### In Progress
[Work currently underway]
### Blocked
[Any blockers or issues encountered]

## Key Decisions
[Important technical decisions and why]

## Relevant Files
[Files read, modified, or created — with brief note on each]

## Next Steps
[What needs to happen next]

## Critical Context
[Specific values, error messages, configuration details]
```

摘要预算随压缩内容量缩放：
- 公式：`content_tokens × 0.20`（`_SUMMARY_RATIO` 常量）
- 最小值：2,000 tokens
- 最大值：`min(context_length × 0.05, 12,000)` tokens

### 阶段 4：组装压缩后的消息列表 {#phase-4-assemble-compressed-messages}

压缩后的消息列表为：
1. 头部消息（首次压缩时会在系统提示后追加一条说明）
2. 摘要消息（选用的角色避免连续同角色冲突）
3. 尾部消息（未修改）

孤立的 `tool_call`/`tool_result` 对由 `_sanitize_tool_pairs()` 清理：
- 引用已移除调用的 tool result → 移除
- 调用结果被移除的 tool call → 注入桩结果

### 迭代重压缩 {#iterative-re-compression}

在后续压缩中，之前的摘要会传递给 LLM，并指示**更新**它，而非从头开始摘要。这样可以在多次压缩之间保留信息 —— 项目从“进行中”变为“已完成”，添加新的进展，移除过时信息。

压缩器实例上的 `_previous_summary` 字段会为此目的存储最后一次摘要文本。


## 压缩前后示例 {#before-after-example}

### 压缩前（45 条消息，约 95K tokens） {#before-compression-45-messages-95k-tokens}

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
### 压缩后（25 条消息，约 45K token） {#after-compression-25-messages-45k-tokens}

```
[0] system:    "你是一个有用的助手...
               [注意：一些早期的对话轮次已被压缩...]"
[1] user:      "帮我搭建一个 FastAPI 项目"
[2] assistant: "[上下文压缩] 早期的轮次已被压缩...

               ## 目标
               搭建一个包含测试和错误处理的 FastAPI 项目

               ## 进度
               ### 已完成
               - 创建项目结构：main.py、tests/、requirements.txt
               - 在 main.py 中实现了 5 个 API 端点
               - 在 tests/test_api.py 中编写了 10 个测试用例
               - 8/10 测试通过

               ### 进行中
               - 修复 2 个失败的测试（test_create_user、test_delete_user）

               ## 相关文件
               - main.py — 包含 5 个端点的 FastAPI 应用
               - tests/test_api.py — 10 个测试用例
               - requirements.txt — fastapi、pytest、httpx

               ## 下一步
               - 修复失败的测试夹具
               - 添加错误处理"
[3] user:      "修复失败的测试"
[4] assistant: <tool_call> read_file: tests/test_api.py </tool_call>
[5] tool:      "import pytest\n..."
[6] assistant: "我看到测试夹具的问题..."
[7] user:      "很好，再添加错误处理"
```

## 提示缓存（Anthropic） {#prompt-caching-anthropic}

来源：`agent/prompt_caching.py`

通过缓存对话前缀，在多轮对话中将输入 token 成本降低约 75%。使用 Anthropic 的 `cache_control` 断点。

### 策略：system_and_3 {#strategy-systemand3}

Anthropic 允许每个请求最多 4 个 `cache_control` 断点。Hermes 使用“system_and_3”策略：

```
断点 1：系统提示（在所有轮次中保持稳定）
断点 2：倒数第 3 条非系统消息  ─┐
断点 3：倒数第 2 条非系统消息   ├─ 滑动窗口
断点 4：最后一条非系统消息      ─┘
```

### 工作原理 {#how-it-works}

`apply_anthropic_cache_control()` 深度复制消息并注入 `cache_control` 标记：

```python
# 缓存标记格式
marker = {"type": "ephemeral"}
# 或使用 1 小时 TTL：
marker = {"type": "ephemeral", "ttl": "1h"}
```

根据内容类型，标记的应用方式不同：

| 内容类型 | 标记位置 |
|-------------|-------------------|
| 字符串内容 | 转换为 `[{"type": "text", "text": ..., "cache_control": ...}]` |
| 列表内容 | 添加到最后一个元素的字典中 |
| 无/空 | 添加为 `msg["cache_control"]` |
| 工具消息 | 添加为 `msg["cache_control"]`（仅限原生 Anthropic） |

### 缓存感知设计模式 {#cache-aware-design-patterns}

1. **稳定的系统提示**：系统提示是断点 1，并在所有轮次中缓存。避免在对话中途修改它（压缩仅在第一次压缩时追加一条注释）。

2. **消息顺序很重要**：缓存命中需要前缀匹配。在中间添加或删除消息会使之后的所有缓存失效。

3. **压缩与缓存的交互**：压缩后，压缩区域的缓存失效，但系统提示缓存仍然有效。滚动 3 条消息的窗口会在 1-2 轮内重新建立缓存。
4. **TTL 选择**：默认值为 `5m`（5 分钟）。对于用户会在轮次之间休息的长时间会话，请使用 `1h`。

### 启用提示缓存 {#enabling-prompt-caching}

提示缓存在以下情况下自动启用：
- 模型是 Anthropic Claude 模型（通过模型名称检测）
- 提供商支持 `cache_control`（原生 Anthropic API 或 OpenRouter）

```yaml
# config.yaml — TTL is configurable (must be "5m" or "1h")
prompt_caching:
  cache_ttl: "5m"
```

CLI 在启动时显示缓存状态：
```
💾 Prompt caching: ENABLED (Claude via OpenRouter, 5m TTL)
```

## 上下文压力警告 {#context-pressure-warnings}

中间的上下文压力警告已被移除（参见 `run_agent.py` 中的迭代预算块，其中注明：“没有中间压力警告——它们会导致模型在复杂任务上过早‘放弃’”）。当提示词 token 达到配置的 `compression.threshold`（默认 50%）时，压缩会触发，且没有事先的警告步骤；gateway session hygiene 作为二级安全网，在模型上下文窗口的 85% 时触发。
