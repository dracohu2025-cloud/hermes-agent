---
sidebar_position: 11
sidebar_label: "Plugins"
title: "Plugins"
description: "通过插件系统，使用自定义工具、钩子和集成来扩展 Hermes"
---

# Plugins

Hermes 拥有一个插件系统，用于在不修改核心代码的情况下添加自定义工具、钩子（hooks）和集成。

**→ [构建 Hermes 插件](/guides/build-a-hermes-plugin)** — 包含完整运行示例的分步指南。

## 快速概览

在 `~/.hermes/plugins/` 目录下创建一个包含 `plugin.yaml` 和 Python 代码的文件夹即可：

```
~/.hermes/plugins/my-plugin/
├── plugin.yaml      # 清单文件
├── __init__.py      # register() — 将 schema 与处理函数连接起来
├── schemas.py       # 工具 schema（LLM 看到的内容）
└── tools.py         # 工具处理函数（调用时运行的内容）
```

启动 Hermes — 你的工具将与内置工具一起出现。模型可以立即调用它们。

### 最小可行示例

这是一个完整的插件，它添加了一个 `hello_world` 工具，并通过钩子记录每次工具调用。

**`~/.hermes/plugins/hello-world/plugin.yaml`**

```yaml
name: hello-world
version: "1.0"
description: A minimal example plugin
```

**`~/.hermes/plugins/hello-world/__init__.py`**

```python
"""Minimal Hermes plugin — registers a tool and a hook."""


def register(ctx):
    # --- 工具: hello_world ---
    schema = {
        "name": "hello_world",
        "description": "Returns a friendly greeting for the given name.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Name to greet",
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

将这两个文件放入 `~/.hermes/plugins/hello-world/`，重启 Hermes，模型就可以立即调用 `hello_world` 了。该钩子会在每次工具执行后打印一行日志。

位于 `./.hermes/plugins/` 的项目本地插件默认是禁用的。仅在启动 Hermes 前设置 `HERMES_ENABLE_PROJECT_PLUGINS=true`，才为受信任的仓库启用它们。

## 插件可以做什么

| 能力 | 如何实现 |
|-----------|-----|
| 添加工具 | `ctx.register_tool(name, schema, handler)` |
| 添加钩子 | `ctx.register_hook("post_tool_call", callback)` |
| 添加 CLI 命令 | `ctx.register_cli_command(name, help, setup_fn, handler_fn)` — 添加 `hermes <plugin> <subcommand>` |
| 注入消息 | `ctx.inject_message(content, role="user")` — 参见 [注入消息](#injecting-messages) |
| 携带数据文件 | `Path(__file__).parent / "data" / "file.yaml"` |
| 捆绑 skills | 在加载时将 `skill.md` 复制到 `~/.hermes/skills/` |
| 环境变量限制 | 在 plugin.yaml 中设置 `requires_env: [API_KEY]` — 在 `hermes plugins install` 时提示 |
| 通过 pip 分发 | `[project.entry-points."hermes_agent.plugins"]` |

## 插件发现机制

| 来源 | 路径 | 使用场景 |
|--------|------|----------|
| 用户 | `~/.hermes/plugins/` | 个人插件 |
| 项目 | `.hermes/plugins/` | 项目特定插件（需要 `HERMES_ENABLE_PROJECT_PLUGINS=true`） |
| pip | `hermes_agent.plugins` entry_points | 分发的软件包 |

## 可用钩子

插件可以为这些生命周期事件注册回调。有关完整详情、回调签名和示例，请参阅 **[事件钩子页面](/user-guide/features/hooks#plugin-hooks)**。

| 钩子 | 触发时机 |
|------|-----------|
| [`pre_tool_call`](/user-guide/features/hooks#pre_tool_call) | 任何工具执行之前 |
| [`post_tool_call`](/user-guide/features/hooks#post_tool_call) | 任何工具返回之后 |
| [`pre_llm_call`](/user-guide/features/hooks#pre_llm_call) | 每轮对话一次，在 LLM 循环之前 — 可以返回 `{"context": "..."}` 来[向用户消息注入上下文](/user-guide/features/hooks#pre_llm_call) |
| [`post_llm_call`](/user-guide/features/hooks#post_llm_call) | 每轮对话一次，在 LLM 循环之后（仅限成功的轮次） |
| [`on_session_start`](/user-guide/features/hooks#on_session_start) | 创建新会话（仅限第一轮） |
| [`on_session_end`](/user-guide/features/hooks#on_session_end) | 每次 `run_conversation` 调用结束时 + CLI 退出处理程序 |

## 管理插件

```bash
hermes plugins                  # 交互式切换 UI — 通过复选框启用/禁用
hermes plugins list             # 表格视图，显示启用/禁用状态
hermes plugins install user/repo  # 从 Git 安装
hermes plugins update my-plugin   # 拉取最新版本
hermes plugins remove my-plugin   # 卸载
hermes plugins enable my-plugin   # 重新启用已禁用的插件
hermes plugins disable my-plugin  # 禁用但不移除
```

不带参数运行 `hermes plugins` 会启动一个交互式的 curses 复选框列表（与 `hermes tools` 的 UI 相同），你可以使用方向键和空格键切换插件的开启/关闭。

禁用的插件仍保持安装状态，但在加载过程中会被跳过。禁用列表存储在 `config.yaml` 的 `plugins.disabled` 下：

```yaml
plugins:
  disabled:
    - my-noisy-plugin
```

在运行中的会话中，`/plugins` 命令会显示当前已加载的插件。

## 注入消息

插件可以使用 `ctx.inject_message()` 向当前对话注入消息：

```python
ctx.inject_message("New data arrived from the webhook", role="user")
```

**签名：** `ctx.inject_message(content: str, role: str = "user") -> bool`

工作原理：

- 如果 Agent 处于 **空闲** 状态（等待用户输入），该消息将作为下一个输入排队并开启新的一轮对话。
- 如果 Agent 处于 **对话中**（正在运行），该消息将中断当前操作 — 效果等同于用户输入新消息并按下回车。
- 对于非 `"user"` 角色，内容会带上 `[role]` 前缀（例如 `[system] ...`）。
- 如果消息成功排队则返回 `True`，如果没有可用的 CLI 引用（例如在 gateway 模式下）则返回 `False`。

这使得远程控制查看器、消息桥接器或 webhook 接收器等插件能够将来自外部源的消息喂给对话。

:::note
`inject_message` 仅在 CLI 模式下可用。在 gateway 模式下，由于没有 CLI 引用，该方法会返回 `False`。
:::

有关处理函数约定、schema 格式、钩子行为、错误处理和常见错误的详细信息，请参阅 **[完整指南](/guides/build-a-hermes-plugin)**。
