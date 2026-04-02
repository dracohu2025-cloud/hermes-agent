---
sidebar_position: 11
sidebar_label: "插件"
title: "插件"
description: "通过插件系统使用自定义工具、钩子和集成扩展 Hermes"
---

# 插件

Hermes 拥有一个插件系统，可以添加自定义工具、钩子和集成，而无需修改核心代码。

**→ [构建 Hermes 插件](/guides/build-a-hermes-plugin)** — 逐步指南，包含完整的工作示例。

## 快速概览

将一个目录放入 `~/.hermes/plugins/`，里面包含 `plugin.yaml` 和 Python 代码：

```
~/.hermes/plugins/my-plugin/
├── plugin.yaml      # 清单文件
├── __init__.py      # register() — 将 schema 绑定到处理函数
├── schemas.py       # 工具 schema（LLM 可见的部分）
└── tools.py         # 工具处理函数（调用时执行的代码）
```

启动 Hermes —— 你的工具会和内置工具一起出现，模型可以立即调用它们。

### 最简工作示例

下面是一个完整的插件示例，添加了一个 `hello_world` 工具，并通过钩子记录每次工具调用。

**`~/.hermes/plugins/hello-world/plugin.yaml`**

```yaml
name: hello-world
version: "1.0"
description: 一个最简示例插件
```

**`~/.hermes/plugins/hello-world/__init__.py`**

```python
"""最简 Hermes 插件 — 注册一个工具和一个钩子。"""


def register(ctx):
    # --- 工具: hello_world ---
    schema = {
        "name": "hello_world",
        "description": "返回给定名字的友好问候。",
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
        return f"Hello, {name}! 👋  (来自 hello-world 插件)"

    ctx.register_tool("hello_world", schema, handle_hello)

    # --- 钩子: 记录每次工具调用 ---
    def on_tool_call(tool_name, params, result):
        print(f"[hello-world] 工具被调用: {tool_name}")

    ctx.register_hook("post_tool_call", on_tool_call)
```

将这两个文件放入 `~/.hermes/plugins/hello-world/`，重启 Hermes，模型即可立即调用 `hello_world`。钩子会在每次工具调用后打印日志。

项目本地插件位于 `./.hermes/plugins/`，默认禁用。仅在信任的仓库中通过设置环境变量 `HERMES_ENABLE_PROJECT_PLUGINS=true` 启用。

## 插件能做什么

| 功能 | 方式 |
|-----------|-----|
| 添加工具 | `ctx.register_tool(name, schema, handler)` |
| 添加钩子 | `ctx.register_hook("post_tool_call", callback)` |
| 注入消息 | `ctx.inject_message(content, role="user")` — 详见 [注入消息](#injecting-messages) |
| 携带数据文件 | `Path(__file__).parent / "data" / "file.yaml"` |
| 打包技能 | 加载时复制 `skill.md` 到 `~/.hermes/skills/` |
| 环境变量控制 | 在 plugin.yaml 中写 `requires_env: [API_KEY]` |
| 通过 pip 分发 | `[project.entry-points."hermes_agent.plugins"]` |

## 插件发现

| 来源 | 路径 | 用例 |
|--------|------|----------|
| 用户 | `~/.hermes/plugins/` | 个人插件 |
| 项目 | `.hermes/plugins/` | 项目专用插件（需 `HERMES_ENABLE_PROJECT_PLUGINS=true`） |
| pip | `hermes_agent.plugins` entry_points | 分发包 |

## 可用钩子

插件可以注册回调函数，监听这些生命周期事件。详见 **[事件钩子页面](/user-guide/features/hooks#plugin-hooks)**，包含完整细节、回调签名和示例。

| 钩子 | 触发时机 |
|------|-----------|
| `pre_tool_call` | 任何工具执行前 |
| `post_tool_call` | 任何工具返回后 |
| `pre_llm_call` | 每轮一次，LLM 循环前 — 可返回 `{"context": "..."}` 注入系统提示 |
| `post_llm_call` | 每轮一次，LLM 循环结束后 |
| `on_session_start` | 新会话创建时（仅首轮） |
| `on_session_end` | 每次 `run_conversation` 调用结束时 |

## 管理插件

```bash
hermes plugins                  # 交互式切换界面 — 用空格启用/禁用
hermes plugins list             # 表格视图，显示启用/禁用状态
hermes plugins install user/repo  # 从 Git 安装
hermes plugins update my-plugin   # 拉取最新
hermes plugins remove my-plugin   # 卸载
hermes plugins enable my-plugin   # 重新启用已禁用插件
hermes plugins disable my-plugin  # 禁用但不卸载
```

运行 `hermes plugins`（无参数）会启动交互式 curses 复选框界面（和 `hermes tools` 一样），用方向键和空格切换插件状态。

禁用的插件仍然安装着，但加载时会跳过。禁用列表保存在 `config.yaml` 的 `plugins.disabled` 下：

```yaml
plugins:
  disabled:
    - my-noisy-plugin
```

运行时，输入 `/plugins` 可查看当前加载的插件。

## 注入消息 {#injecting-messages}

插件可以用 `ctx.inject_message()` 向当前对话注入消息：

```python
ctx.inject_message("New data arrived from the webhook", role="user")
```

**签名：** `ctx.inject_message(content: str, role: str = "user") -> bool`

工作原理：

- 如果 Agent **空闲**（等待用户输入），消息会排队为下一条输入，开启新一轮对话。
- 如果 Agent **正在执行**（处理中），消息会中断当前操作，就像用户输入新消息并按下回车。
- 非 `"user"` 角色的内容会加上前缀 `[role]`（例如 `[system] ...`）。
- 如果成功排队返回 `True`，如果没有 CLI 引用（如网关模式）返回 `False`。

这让插件如远程控制查看器、消息桥接或 webhook 接收器能从外部源向对话注入消息。

:::note
`inject_message` 仅在 CLI 模式可用。网关模式下没有 CLI 引用，方法会返回 `False`。
:::

详见 **[完整指南](/guides/build-a-hermes-plugin)**，包含处理函数约定、schema 格式、钩子行为、错误处理和常见错误。
