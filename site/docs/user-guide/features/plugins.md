---
sidebar_position: 11
sidebar_label: "插件"
title: "插件"
description: "通过插件系统，使用自定义工具、钩子和集成来扩展 Hermes"
---

# 插件 {#plugins}

Hermes 拥有一个插件系统，允许你添加自定义工具、钩子和集成，而无需修改核心代码。

**→ [构建一个 Hermes 插件](/guides/build-a-hermes-plugin)** — 包含完整工作示例的逐步指南。

## 快速概览 {#quick-overview}

将一个包含 `plugin.yaml` 和 Python 代码的目录放入 `~/.hermes/plugins/`：

```
~/.hermes/plugins/my-plugin/
├── plugin.yaml      # 清单文件
├── __init__.py      # register() — 将模式连接到处理器
├── schemas.py       # 工具模式（LLM 看到的内容）
└── tools.py         # 工具处理器（调用时运行的内容）
```

启动 Hermes — 你的工具将与内置工具一同出现。模型可以立即调用它们。

### 最小工作示例 {#minimal-working-example}

这是一个完整的插件，它添加了一个 `hello_world` 工具，并通过一个钩子记录每次工具调用。

**`~/.hermes/plugins/hello-world/plugin.yaml`**

```yaml
name: hello-world
version: "1.0"
description: 一个最小示例插件
```

**`~/.hermes/plugins/hello-world/__init__.py`**

```python
"""最小 Hermes 插件 — 注册一个工具和一个钩子。"""


def register(ctx):
    # --- 工具: hello_world ---
    schema = {
        "name": "hello_world",
        "description": "为给定的名字返回友好的问候。",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "要问候的名字",
                }
            },
            "required": ["name"],
        },
    }

    def handle_hello(params):
        name = params.get("name", "World")
        return f"Hello, {name}! 👋  (from the hello-world plugin)"

    ctx.register_tool("hello_world", schema, handle_hello)

    # --- 钩子: 记录每次工具调用 ---
    def on_tool_call(tool_name, params, result):
        print(f"[hello-world] tool called: {tool_name}")

    ctx.register_hook("post_tool_call", on_tool_call)
```

将这两个文件放入 `~/.hermes/plugins/hello-world/`，重启 Hermes，模型就可以立即调用 `hello_world`。该钩子会在每次工具调用后打印一行日志。

位于 `./.hermes/plugins/` 下的项目本地插件默认是禁用的。只有在信任的代码库中，才可以通过在启动 Hermes 前设置 `HERMES_ENABLE_PROJECT_PLUGINS=true` 来启用它们。

## 插件能做什么 {#what-plugins-can-do}

| 能力 | 实现方式 |
|-----------|-----|
| 添加工具 | `ctx.register_tool(name, schema, handler)` |
| 添加钩子 | `ctx.register_hook("post_tool_call", callback)` |
| 添加斜杠命令 | `ctx.register_command(name, handler, description)` — 在 CLI 和网关会话中添加 `/name` |
| 添加 CLI 命令 | `ctx.register_cli_command(name, help, setup_fn, handler_fn)` — 添加 `hermes &lt;plugin&gt; &lt;subcommand&gt;` |
| 注入消息 | `ctx.inject_message(content, role="user")` — 参见 [注入消息](#injecting-messages) |
| 附带数据文件 | `Path(__file__).parent / "data" / "file.yaml"` |
| 打包技能 | `ctx.register_skill(name, path)` — 以 `plugin:skill` 命名空间化，通过 `skill_view("plugin:skill")` 加载 |
| 依赖环境变量 | 在 plugin.yaml 中使用 `requires_env: [API_KEY]` — 在 `hermes plugins install` 期间会提示 |
| 通过 pip 分发 | `[project.entry-points."hermes_agent.plugins"]` |

## 插件发现 {#plugin-discovery}

| 来源 | 路径 | 使用场景 |
|--------|------|----------|
| 用户 | `~/.hermes/plugins/` | 个人插件 |
| 项目 | `.hermes/plugins/` | 项目特定插件（需要 `HERMES_ENABLE_PROJECT_PLUGINS=true`） |
| pip | `hermes_agent.plugins` entry_points | 分发包 |

## 可用的钩子 {#available-hooks}

插件可以为这些生命周期事件注册回调。完整详情、回调签名和示例请参见 **[事件钩子页面](/user-guide/features/hooks#plugin-hooks)**。

| 钩子 | 触发时机 |
|------|-----------|
| [`pre_tool_call`](/user-guide/features/hooks#pre_tool_call) | 在任何工具执行之前 |
| [`post_tool_call`](/user-guide/features/hooks#post_tool_call) | 在任何工具返回之后 |
| [`pre_llm_call`](/user-guide/features/hooks#pre_llm_call) | 每轮一次，在 LLM 循环之前 — 可以返回 `{"context": "..."}` 来 [将上下文注入用户消息](/user-guide/features/hooks#pre_llm_call) |
| [`post_llm_call`](/user-guide/features/hooks#post_llm_call) | 每轮一次，在 LLM 循环之后（仅限成功的轮次） |
| [`on_session_start`](/user-guide/features/hooks#on_session_start) | 新会话创建时（仅限第一轮） |
| [`on_session_end`](/user-guide/features/hooks#on_session_end) | 每次 `run_conversation` 调用结束时 + CLI 退出处理器 |
## 插件类型 {#plugin-types}

Hermes 有三种插件：

| 类型 | 功能 | 选择方式 | 位置 |
|------|-------------|-----------|----------|
| **通用插件** | 添加工具、钩子、斜杠命令、CLI 命令 | 多选（启用/禁用） | `~/.hermes/plugins/` |
| **记忆提供器** | 替换或增强内置记忆 | 单选（一个激活） | `plugins/memory/` |
| **上下文引擎** | 替换内置的上下文压缩器 | 单选（一个激活） | `plugins/context_engine/` |

记忆提供器和上下文引擎属于**提供器插件**——每种类型一次只能激活一个。通用插件可以任意组合启用。

## 管理插件 {#managing-plugins}

```bash
hermes plugins                  # 统一的交互式界面
hermes plugins list             # 带启用/禁用状态的表格视图
hermes plugins install user/repo  # 从 Git 安装
hermes plugins update my-plugin   # 拉取最新版本
hermes plugins remove my-plugin   # 卸载
hermes plugins enable my-plugin   # 重新启用已禁用的插件
hermes plugins disable my-plugin  # 禁用但不移除
```

### 交互式界面 {#interactive-ui}

不带参数运行 `hermes plugins` 会打开一个复合交互界面：

```
插件
  ↑↓ 导航  SPACE 切换  ENTER 配置/确认  ESC 完成

  通用插件
 → [✓] my-tool-plugin — 自定义搜索工具
   [ ] webhook-notifier — 事件钩子

  提供器插件
     记忆提供器          ▸ honcho
     上下文引擎           ▸ compressor
```

- **通用插件区域** — 复选框，用 SPACE 切换
- **提供器插件区域** — 显示当前选择。按 ENTER 进入单选选择器，在其中选择一个激活的提供器。

提供器插件的选择会保存到 `config.yaml`：

```yaml
memory:
  provider: "honcho"      # 空字符串 = 仅使用内置

context:
  engine: "compressor"    # 默认内置压缩器
```

### 禁用通用插件 {#disabling-general-plugins}

被禁用的插件仍然保留在系统中，但在加载时会被跳过。禁用列表存储在 `config.yaml` 的 `plugins.disabled` 下：

```yaml
plugins:
  disabled:
    - my-noisy-plugin
```

在运行中的会话里，使用 `/plugins` 命令可以查看当前加载了哪些插件。

<a id="injecting-messages"></a>
## 注入消息 {#injecting-messages}

插件可以使用 `ctx.inject_message()` 向当前活跃对话注入消息：

```python
ctx.inject_message("New data arrived from the webhook", role="user")
```

**签名：** `ctx.inject_message(content: str, role: str = "user") -> bool`

工作原理：

- 如果 Agent 处于**空闲**状态（等待用户输入），消息会被排队作为下一个输入，并开启一个新的回合。
- 如果 Agent 处于**回合中**（正在运行），消息会中断当前操作——就像用户输入新消息并按了回车一样。
- 对于非 `"user"` 的角色，内容会加上 `[角色]` 前缀（例如 `[system] ...`）。
- 如果消息成功加入队列则返回 `True`，如果没有可用的 CLI 引用（例如在网关模式下）则返回 `False`。

这使得远程控制查看器、消息桥接器或 Webhook 接收器等插件能够从外部源向对话中注入消息。

:::note
`inject_message` 仅在 CLI 模式下可用。在网关模式下，没有 CLI 引用，该方法会返回 `False`。
:::

关于处理器契约、模式格式、钩子行为、错误处理和常见错误，请参阅**[完整指南](/guides/build-a-hermes-plugin)**。
