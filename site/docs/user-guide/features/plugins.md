---
sidebar_position: 11
sidebar_label: "插件"
title: "插件"
description: "通过插件系统使用自定义工具、钩子和集成来扩展 Hermes"
---

# 插件

Hermes 拥有一个插件系统，无需修改核心代码即可添加自定义工具、钩子和集成。

**→ [构建 Hermes 插件](/guides/build-a-hermes-plugin)** —— 包含完整工作示例的分步指南。

## 快速概览

在 `~/.hermes/plugins/` 目录下放入一个包含 `plugin.yaml` 和 Python 代码的文件夹即可：

```
~/.hermes/plugins/my-plugin/
├── plugin.yaml      # 清单文件
├── __init__.py      # register() — 将模式（schema）连接到处理程序
├── schemas.py       # 工具模式（LLM 可见的内容）
└── tools.py         # 工具处理程序（调用时执行的内容）
```

启动 Hermes 后，你的工具就会与内置工具一起出现。模型可以立即调用它们。

### 最小工作示例

这是一个完整的插件示例，它添加了一个 `hello_world` 工具，并通过钩子记录每一次工具调用。

**`~/.hermes/plugins/hello-world/plugin.yaml`**

```yaml
name: hello-world
version: "1.0"
description: 一个最小的插件示例
```

**`~/.hermes/plugins/hello-world/__init__.py`**

```python
"""最小的 Hermes 插件 — 注册一个工具和一个钩子。"""


def register(ctx):
    # --- 工具: hello_world ---
    schema = {
        "name": "hello_world",
        "description": "为给定的名称返回友好的问候。",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "要问候的名称",
                }
            },
            "required": ["name"],
        },
    }

    def handle_hello(params):
        name = params.get("name", "World")
        return f"Hello, {name}! 👋  (来自 hello-world 插件)"

    ctx.register_tool("hello_world", schema, handle_hello)

    # --- 钩子: 记录每一次工具调用 ---
    def on_tool_call(tool_name, params, result):
        print(f"[hello-world] 工具已调用: {tool_name}")

    ctx.register_hook("post_tool_call", on_tool_call)
```

将这两个文件放入 `~/.hermes/plugins/hello-world/`，重启 Hermes，模型即可立即调用 `hello_world`。该钩子会在每次工具调用后打印一行日志。

默认情况下，`./.hermes/plugins/` 下的项目本地插件是禁用的。仅在受信任的仓库中，通过在启动 Hermes 前设置 `HERMES_ENABLE_PROJECT_PLUGINS=true` 来启用它们。

## 插件的功能

| 功能 | 实现方式 |
|-----------|-----|
| 添加工具 | `ctx.register_tool(name, schema, handler)` |
| 添加钩子 | `ctx.register_hook("post_tool_call", callback)` |
| 添加 CLI 命令 | `ctx.register_cli_command(name, help, setup_fn, handler_fn)` — 添加 `hermes <plugin> <subcommand>` |
| 注入消息 | `ctx.inject_message(content, role="user")` — 参见 [注入消息](#injecting-messages) |
| 携带数据文件 | `Path(__file__).parent / "data" / "file.yaml"` |
| 捆绑技能 | 在加载时将 `skill.md` 复制到 `~/.hermes/skills/` |
| 环境变量门控 | 在 `plugin.yaml` 中设置 `requires_env: [API_KEY]` — 在 `hermes plugins install` 时会提示输入 |
| 通过 pip 分发 | `[project.entry-points."hermes_agent.plugins"]` |

## 插件发现

| 来源 | 路径 | 用途 |
|--------|------|----------|
| 用户 | `~/.hermes/plugins/` | 个人插件 |
| 项目 | `.hermes/plugins/` | 项目特定插件（需要 `HERMES_ENABLE_PROJECT_PLUGINS=true`） |
| pip | `hermes_agent.plugins` entry_points | 分发包 |

## 可用钩子

插件可以为这些生命周期事件注册回调。有关完整详情、回调签名和示例，请参阅 **[事件钩子页面](/user-guide/features/hooks#plugin-hooks)**。

| 钩子 | 触发时机 |
|------|-----------|
| [`pre_tool_call`](/user-guide/features/hooks#pre_tool_call) | 在任何工具执行之前 |
| [`post_tool_call`](/user-guide/features/hooks#post_tool_call) | 在任何工具返回之后 |
| [`pre_llm_call`](/user-guide/features/hooks#pre_llm_call) | 每个回合一次，在 LLM 循环之前 — 可返回 `{"context": "..."}` 以[将上下文注入用户消息](/user-guide/features/hooks#pre_llm_call) |
| [`post_llm_call`](/user-guide/features/hooks#post_llm_call) | 每个回合一次，在 LLM 循环之后（仅限成功的回合） |
| [`on_session_start`](/user-guide/features/hooks#on_session_start) | 创建新会话时（仅限第一回合） |
| [`on_session_end`](/user-guide/features/hooks#on_session_end) | 每次 `run_conversation` 调用结束 + CLI 退出处理程序 |

## 插件类型

Hermes 有三种插件：

| 类型 | 功能 | 选择方式 | 位置 |
|------|-------------|-----------|----------|
| **通用插件** | 添加工具、钩子、CLI 命令 | 多选（启用/禁用） | `~/.hermes/plugins/` |
| **内存提供程序** | 替换或增强内置内存 | 单选（一次仅一个活跃） | `plugins/memory/` |
| **上下文引擎** | 替换内置上下文压缩器 | 单选（一次仅一个活跃） | `plugins/context_engine/` |

内存提供程序和上下文引擎属于**提供程序插件** —— 每种类型一次只能激活一个。通用插件可以以任意组合启用。

## 管理插件

```bash
hermes plugins                  # 统一交互式 UI
hermes plugins list             # 显示已启用/禁用状态的表格视图
hermes plugins install user/repo  # 从 Git 安装
hermes plugins update my-plugin   # 拉取最新版本
hermes plugins remove my-plugin   # 卸载
hermes plugins enable my-plugin   # 重新启用已禁用的插件
hermes plugins disable my-plugin  # 禁用而不删除
```

### 交互式 UI

不带参数运行 `hermes plugins` 会打开一个复合交互界面：

```
Plugins
  ↑↓ 导航  SPACE 切换  ENTER 配置/确认  ESC 完成

  通用插件
 → [✓] my-tool-plugin — 自定义搜索工具
   [ ] webhook-notifier — 事件钩子

  提供程序插件
     内存提供程序          ▸ honcho
     上下文引擎           ▸ compressor
```

- **通用插件部分** — 复选框，使用 SPACE 键切换
- **提供程序插件部分** — 显示当前选择。按 ENTER 键进入单选列表，选择一个活跃的提供程序。

提供程序插件的选择会保存到 `config.yaml` 中：

```yaml
memory:
  provider: "honcho"      # 空字符串 = 仅使用内置

context:
  engine: "compressor"    # 默认内置压缩器
```

### 禁用通用插件

禁用的插件会保留在安装目录中，但在加载时会被跳过。禁用列表存储在 `config.yaml` 的 `plugins.disabled` 下：

```yaml
plugins:
  disabled:
    - my-noisy-plugin
```

在运行的会话中，`/plugins` 命令会显示当前加载了哪些插件。

## 注入消息 {#injecting-messages}

插件可以使用 `ctx.inject_message()` 将消息注入到当前对话中：

```python
ctx.inject_message("来自 webhook 的新数据已到达", role="user")
```

**签名：** `ctx.inject_message(content: str, role: str = "user") -> bool`

工作原理：

- 如果 Agent 处于**空闲状态**（等待用户输入），消息将排队作为下一次输入并开启一个新回合。
- 如果 Agent 处于**回合中**（正在运行），消息会中断当前操作 —— 就像用户输入新消息并按回车键一样。
- 对于非 `"user"` 角色，内容会加上 `[role]` 前缀（例如 `[system] ...`）。
- 如果消息成功排队，返回 `True`；如果无法获取 CLI 引用（例如在网关模式下），返回 `False`。

这使得远程控制查看器、消息桥接器或 webhook 接收器等插件能够从外部源向对话中输入消息。

:::note
`inject_message` 仅在 CLI 模式下可用。在网关模式下，没有 CLI 引用，该方法将返回 `False`。
:::

请参阅 **[完整指南](/guides/build-a-hermes-plugin)** 以了解处理程序契约、模式格式、钩子行为、错误处理和常见错误。
