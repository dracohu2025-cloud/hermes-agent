---
sidebar_position: 9
title: "Context Engine 插件"
description: "如何构建一个用于替换内置 ContextCompressor 的 Context Engine 插件"
---

# 构建 Context Engine 插件

Context Engine 插件用于替换内置的 `ContextCompressor`，提供另一种管理对话上下文的策略。例如，你可以构建一个无损上下文管理（Lossless Context Management, LCM）引擎，通过构建知识 DAG（有向无环图）来代替有损的摘要算法。

## 工作原理

Agent 的上下文管理构建在 `ContextEngine` 抽象基类（ABC）之上（位于 `agent/context_engine.py`）。内置的 `ContextCompressor` 是默认实现。插件引擎必须实现相同的接口。

同一时间只能激活**一个** Context Engine。选择方式由配置驱动：

```yaml
# config.yaml
context:
  engine: "compressor"    # 默认内置引擎
  engine: "lcm"           # 激活名为 "lcm" 的插件引擎
```

插件引擎**不会自动激活**——用户必须显式地将 `context.engine` 设置为插件的名称。

## 目录结构

每个 Context Engine 都位于 `plugins/context_engine/<name>/` 目录下：

```
plugins/context_engine/lcm/
├── __init__.py      # 导出 ContextEngine 子类
├── plugin.yaml      # 元数据（名称、描述、版本）
└── ...              # 引擎所需的任何其他模块
```

## ContextEngine 抽象基类 (ABC)

你的引擎必须实现以下**必需**方法：

```python
from agent.context_engine import ContextEngine

class LCMEngine(ContextEngine):

    @property
    def name(self) -> str:
        """短标识符，例如 'lcm'。必须与 config.yaml 中的值匹配。"""
        return "lcm"

    def update_from_response(self, usage: dict) -> None:
        """在每次 LLM 调用后，携带 usage 字典被调用。

        从响应中更新 self.last_prompt_tokens, self.last_completion_tokens,
        self.last_total_tokens。
        """

    def should_compress(self, prompt_tokens: int = None) -> bool:
        """如果本轮应该触发压缩，则返回 True。"""

    def compress(self, messages: list, current_tokens: int = None) -> list:
        """压缩消息列表并返回一个新的（可能更短的）列表。

        返回的列表必须是符合 OpenAI 格式的消息序列。
        """
```

### 你的引擎必须维护的类属性

Agent 会直接读取这些属性用于显示和日志记录：

```python
last_prompt_tokens: int = 0
last_completion_tokens: int = 0
last_total_tokens: int = 0
threshold_tokens: int = 0        # 触发压缩的阈值
context_length: int = 0          # 模型的完整上下文窗口
compression_count: int = 0       # compress() 已运行的次数
```

### 可选方法

这些方法在抽象基类中已有合理的默认实现。你可以根据需要进行重写：

| 方法 | 默认行为 | 重写场景 |
|--------|---------|--------------|
| `on_session_start(session_id, **kwargs)` | 无操作 | 需要加载持久化状态（DAG、数据库）时 |
| `on_session_end(session_id, messages)` | 无操作 | 需要刷新状态、关闭连接时 |
| `on_session_reset()` | 重置 Token 计数器 | 有需要清除的会话级状态时 |
| `update_model(model, context_length, ...)` | 更新 context_length 和阈值 | 在切换模型时需要重新计算预算时 |
| `get_tool_schemas()` | 返回 `[]` | 引擎提供 Agent 可调用的工具（例如 `lcm_grep`）时 |
| `handle_tool_call(name, args, **kwargs)` | 返回错误 JSON | 你实现了工具处理逻辑时 |
| `should_compress_preflight(messages)` | 返回 `False` | 你可以在 API 调用前进行低成本预估时 |
| `get_status()` | 标准 Token/阈值字典 | 有需要展示的自定义指标时 |

## 引擎工具

Context Engine 可以暴露 Agent 直接调用的工具。通过 `get_tool_schemas()` 返回模式，并在 `handle_tool_call()` 中处理调用：

```python
def get_tool_schemas(self):
    return [{
        "name": "lcm_grep",
        "description": "搜索上下文知识图谱",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "搜索查询"}
            },
            "required": ["query"],
        },
    }]

def handle_tool_call(self, name, args, **kwargs):
    if name == "lcm_grep":
        results = self._search_dag(args["query"])
        return json.dumps({"results": results})
    return json.dumps({"error": f"未知工具: {name}"})
```

引擎工具会在启动时注入到 Agent 的工具列表中并自动分发——无需手动注册。

## 注册

### 通过目录注册（推荐）

将你的引擎放在 `plugins/context_engine/<name>/` 中。`__init__.py` 必须导出一个 `ContextEngine` 子类。发现系统会自动找到并实例化它。

### 通过通用插件系统注册

通用插件也可以注册 Context Engine：

```python
def register(ctx):
    engine = LCMEngine(context_length=200000)
    ctx.register_context_engine(engine)
```

同一时间只能注册一个引擎。如果第二个插件尝试注册，系统会拒绝并发出警告。

## 生命周期

```
1. 引擎实例化（插件加载或目录发现）
2. on_session_start() — 对话开始
3. update_from_response() — 每次 API 调用后
4. should_compress() — 每轮检查
5. compress() — 当 should_compress() 返回 True 时调用
6. on_session_end() — 会话结束（CLI 退出、/reset、网关过期）
```

`on_session_reset()` 会在执行 `/new` 或 `/reset` 时被调用，用于在不完全关闭的情况下清除会话级状态。

## 配置

用户可以通过 `hermes plugins` → Provider Plugins → Context Engine 选择你的引擎，或者通过编辑 `config.yaml` 来选择：

```yaml
context:
  engine: "lcm"   # 必须与你引擎的 name 属性匹配
```

`compression` 配置块（`compression.threshold`、`compression.protect_last_n` 等）是内置 `ContextCompressor` 专用的。如果需要，你的引擎应在初始化时从 `config.yaml` 读取并定义自己的配置格式。

## 测试

```python
from agent.context_engine import ContextEngine

def test_engine_satisfies_abc():
    engine = YourEngine(context_length=200000)
    assert isinstance(engine, ContextEngine)
    assert engine.name == "your-name"

def test_compress_returns_valid_messages():
    engine = YourEngine(context_length=200000)
    msgs = [{"role": "user", "content": "hello"}]
    result = engine.compress(msgs)
    assert isinstance(result, list)
    assert all("role" in m for m in result)
```

查看 `tests/agent/test_context_engine.py` 获取完整的 ABC 合约测试套件。

## 参阅

- [Context Compression and Caching](/developer-guide/context-compression-and-caching) — 内置压缩器的工作原理
- [Memory Provider Plugins](/developer-guide/memory-provider-plugin) — 类似的单选式内存插件系统
- [Plugins](/user-guide/features/plugins) — 通用插件系统概述
