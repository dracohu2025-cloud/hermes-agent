---
sidebar_position: 8
title: "内存提供程序插件"
description: "如何为 Hermes Agent 构建内存提供程序插件"
---

# 构建内存提供程序插件 {#building-a-memory-provider-plugin}

内存提供程序插件为 Hermes Agent 提供了超越内置 MEMORY.md 和 USER.md 的持久化跨会话知识。本指南将介绍如何构建此类插件。

:::tip
内存提供程序是两种**提供程序插件**类型之一。另一种是 [Context Engine Plugins](/developer-guide/context-engine-plugin)，用于替换内置的上下文压缩器。两者遵循相同的模式：单选、配置驱动，并通过 `hermes plugins` 进行管理。
:::

## 目录结构 {#directory-structure}

每个内存提供程序都位于 `plugins/memory/<name>/` 下：

```
plugins/memory/my-provider/
├── __init__.py      # MemoryProvider 实现 + register() 入口点
├── plugin.yaml      # 元数据（名称、描述、钩子）
└── README.md        # 设置说明、配置参考、工具
```

## MemoryProvider 抽象基类 (ABC) {#the-memoryprovider-abc}

你的插件需要实现 `agent/memory_provider.py` 中的 `MemoryProvider` 抽象基类：

```python
from agent.memory_provider import MemoryProvider

class MyMemoryProvider(MemoryProvider):
    @property
    def name(self) -> str:
        return "my-provider"

    def is_available(self) -> bool:
        """检查此提供程序是否可以激活。禁止进行网络调用。"""
        return bool(os.environ.get("MY_API_KEY"))

    def initialize(self, session_id: str, **kwargs) -> None:
        """在 Agent 启动时调用一次。

        kwargs 始终包含：
          hermes_home (str): 当前活动的 HERMES_HOME 路径。用于存储数据。
        """
        self._api_key = os.environ.get("MY_API_KEY", "")
        self._session_id = session_id

    # ... 实现其余方法
```

## 必需方法 {#required-methods}

### 核心生命周期 {#core-lifecycle}

| 方法 | 调用时机 | 是否必须实现？ |
|--------|-----------|-----------------|
| `name` (属性) | 始终 | **是** |
| `is_available()` | Agent 初始化时，激活前 | **是** — 禁止网络调用 |
| `initialize(session_id, **kwargs)` | Agent 启动时 | **是** |
| `get_tool_schemas()` | 初始化后，用于工具注入 | **是** |
| `handle_tool_call(name, args)` | 当 Agent 使用你的工具时 | **是**（如果你有工具） |

### 配置 {#config}

| 方法 | 用途 | 是否必须实现？ |
|--------|---------|-----------------|
| `get_config_schema()` | 为 `hermes memory setup` 声明配置字段 | **是** |
| `save_config(values, hermes_home)` | 将非敏感配置写入原生位置 | **是**（除非仅使用环境变量） |

### 可选钩子 {#optional-hooks}

| 方法 | 调用时机 | 用例 |
|--------|-----------|----------|
| `system_prompt_block()` | 系统提示词组装时 | 静态提供程序信息 |
| `prefetch(query)` | 每次 API 调用前 | 返回已召回的上下文 |
| `queue_prefetch(query)` | 每次对话轮次后 | 为下一轮预热 |
| `sync_turn(user, assistant)` | 每次对话轮次完成后 | 持久化对话 |
| `on_session_end(messages)` | 对话结束时 | 最终提取/刷新 |
| `on_pre_compress(messages)` | 上下文压缩前 | 在丢弃前保存见解 |
| `on_memory_write(action, target, content)` | 内置内存写入时 | 镜像到你的后端 |
| `shutdown()` | 进程退出时 | 清理连接 |

## 配置 Schema {#config-schema}

`get_config_schema()` 返回一个字段描述符列表，供 `hermes memory setup` 使用：

```python
def get_config_schema(self):
    return [
        {
            "key": "api_key",
            "description": "My Provider API key",
            "secret": True,           # → 写入 .env
            "required": True,
            "env_var": "MY_API_KEY",   # 显式环境变量名称
            "url": "https://my-provider.com/keys",  # 获取方式
        },
        {
            "key": "region",
            "description": "Server region",
            "default": "us-east",
            "choices": ["us-east", "eu-west", "ap-south"],
        },
        {
            "key": "project",
            "description": "Project identifier",
            "default": "hermes",
        },
    ]
```

带有 `secret: True` 和 `env_var` 的字段会被写入 `.env`。非敏感字段会传递给 `save_config()`。

:::tip 最小化 vs 完整 Schema
`get_config_schema()` 中的每个字段都会在 `hermes memory setup` 期间提示用户输入。选项较多的提供程序应保持 Schema 最小化——仅包含用户**必须**配置的字段（如 API 密钥、必需凭据）。将可选设置记录在配置文件参考中（例如 `$HERMES_HOME/myprovider.json`），而不是在设置过程中全部询问。这样既能保持设置向导的快速，又能支持高级配置。参考 Supermemory 提供程序的示例——它仅提示输入 API 密钥；所有其他选项都存放在 `supermemory.json` 中。
:::

## 保存配置 {#save-config}

```python
def save_config(self, values: dict, hermes_home: str) -> None:
    """将非敏感配置写入你的原生位置。"""
    import json
<a id="minimal-vs-full-schema"></a>
    from pathlib import Path
    config_path = Path(hermes_home) / "my-provider.json"
    config_path.write_text(json.dumps(values, indent=2))
```

对于仅使用环境变量的提供程序，保持默认的空操作即可。

## 插件入口点 {#plugin-entry-point}

```python
def register(ctx) -> None:
    """由内存插件发现系统调用。"""
    ctx.register_memory_provider(MyMemoryProvider())
```

## plugin.yaml {#plugin-yaml}

```yaml
name: my-provider
version: 1.0.0
description: "此提供程序功能的简短描述。"
hooks:
  - on_session_end    # 列出你实现的钩子
```

## 线程约定 {#threading-contract}

**`sync_turn()` 必须是非阻塞的。** 如果你的后端有延迟（API 调用、LLM 处理），请在守护线程中运行该任务：

```python
def sync_turn(self, user_content, assistant_content):
    def _sync():
        try:
            self._api.ingest(user_content, assistant_content)
        except Exception as e:
            logger.warning("Sync failed: %s", e)

    if self._sync_thread and self._sync_thread.is_alive():
        self._sync_thread.join(timeout=5.0)
    self._sync_thread = threading.Thread(target=_sync, daemon=True)
    self._sync_thread.start()
```

## 配置文件隔离 {#profile-isolation}

所有存储路径**必须**使用 `initialize()` 中的 `hermes_home` 参数，而不是硬编码的 `~/.hermes`：

```python
# 正确 — 配置文件作用域
from hermes_constants import get_hermes_home
data_dir = get_hermes_home() / "my-provider"

# 错误 — 在所有配置文件间共享
data_dir = Path("~/.hermes/my-provider").expanduser()
```

## 测试 {#testing}

查看 `tests/agent/test_memory_plugin_e2e.py` 以获取使用真实 SQLite 提供程序的完整 E2E 测试模式。

```python
from agent.memory_manager import MemoryManager

mgr = MemoryManager()
mgr.add_provider(my_provider)
mgr.initialize_all(session_id="test-1", platform="cli")

# 测试工具路由
result = mgr.handle_tool_call("my_tool", {"action": "add", "content": "test"})

# 测试生命周期
mgr.sync_all("user msg", "assistant msg")
mgr.on_session_end([])
mgr.shutdown_all()
```

## 添加 CLI 命令 {#adding-cli-commands}

内存提供程序插件可以注册自己的 CLI 子命令树（例如 `hermes my-provider status`，`hermes my-provider config`）。这使用基于约定的发现系统——无需更改核心文件。

### 工作原理 {#how-it-works}

1. 在插件目录中添加一个 `cli.py` 文件
2. 定义一个构建 argparse 树的 `register_cli(subparser)` 函数
3. 内存插件系统在启动时通过 `discover_plugin_cli_commands()` 发现它
4. 你的命令将出现在 `hermes <provider-name> <subcommand>` 下

**活动提供程序门控：** 你的 CLI 命令仅在你的提供程序是配置中活动的 `memory.provider` 时才会出现。如果用户尚未配置你的提供程序，你的命令将不会显示在 `hermes --help` 中。

### 示例 {#example}

```python
# plugins/memory/my-provider/cli.py

def my_command(args):
    """由 argparse 调度的处理程序。"""
    sub = getattr(args, "my_command", None)
    if sub == "status":
        print("Provider is active and connected.")
    elif sub == "config":
        print("Showing config...")
    else:
        print("Usage: hermes my-provider <status|config>")

def register_cli(subparser) -> None:
    """构建 hermes my-provider 的 argparse 树。

    在 argparse 设置时由 discover_plugin_cli_commands() 调用。
    """
    subs = subparser.add_subparsers(dest="my_command")
    subs.add_parser("status", help="Show provider status")
    subs.add_parser("config", help="Show provider config")
    subparser.set_defaults(func=my_command)
```
### 参考实现 {#reference-implementation}

请参阅 `plugins/memory/honcho/cli.py` 以获取完整示例，其中包含 13 个子命令、跨配置管理（`--target-profile`）以及配置的读取/写入功能。

### 包含 CLI 的目录结构 {#directory-structure-with-cli}

```
plugins/memory/my-provider/
├── __init__.py      # MemoryProvider 实现 + register()
├── plugin.yaml      # 元数据
├── cli.py           # register_cli(subparser) — CLI 命令
└── README.md        # 设置说明
```

## 单一 Provider 规则 {#single-provider-rule}

同一时间只能激活 **一个** 外部内存 Provider。如果用户尝试注册第二个，MemoryManager 将会拒绝该请求并发出警告。这可以防止工具模式（tool schema）臃肿以及后端冲突。
