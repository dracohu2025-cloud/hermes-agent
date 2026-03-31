---
sidebar_position: 20
---

# 插件

Hermes 拥有一个插件系统，用于添加自定义工具、钩子、斜杠命令和集成，而无需修改核心代码。

**→ [构建 Hermes 插件](/guides/build-a-hermes-plugin)** — 包含完整工作示例的逐步指南。

## 快速概览

将一个包含 `plugin.yaml` 和 Python 代码的目录放入 `~/.hermes/plugins/`：

```
~/.hermes/plugins/my-plugin/
├── plugin.yaml      # 清单文件
├── __init__.py      # register() — 将模式关联到处理器
├── schemas.py       # 工具模式（LLM 看到的内容）
└── tools.py         # 工具处理器（调用时运行的内容）
```

启动 Hermes — 你的工具将与内置工具一同出现。模型可以立即调用它们。

项目本地插件位于 `./.hermes/plugins/` 下，默认是禁用的。只有在信任的代码库中，才可以通过在启动 Hermes 前设置 `HERMES_ENABLE_PROJECT_PLUGINS=true` 来启用它们。

## 插件能做什么

| 能力 | 实现方式 |
|-----------|-----|
| 添加工具 | `ctx.register_tool(name, schema, handler)` |
| 添加钩子 | `ctx.register_hook("post_tool_call", callback)` |
| 添加斜杠命令 | `ctx.register_command("mycommand", handler)` |
| 附带数据文件 | `Path(__file__).parent / "data" / "file.yaml"` |
| 捆绑技能 | 在加载时将 `skill.md` 复制到 `~/.hermes/skills/` |
| 依赖环境变量 | 在 plugin.yaml 中使用 `requires_env: [API_KEY]` |
| 通过 pip 分发 | `[project.entry-points."hermes_agent.plugins"]` |

## 插件发现

| 来源 | 路径 | 使用场景 |
|--------|------|----------|
| 用户 | `~/.hermes/plugins/` | 个人插件 |
| 项目 | `.hermes/plugins/` | 项目特定插件（需要 `HERMES_ENABLE_PROJECT_PLUGINS=true`） |
| pip | `hermes_agent.plugins` entry_points | 分发包 |

## 可用钩子

插件可以为这些生命周期事件注册回调。查看 **[事件钩子页面](/user-guide/features/hooks#plugin-hooks)** 获取完整详情、回调签名和示例。

| 钩子 | 触发时机 |
|------|-----------|
| `pre_tool_call` | 任何工具执行之前 |
| `post_tool_call` | 任何工具返回之后 |
| `pre_llm_call` | 每轮一次，在 LLM 循环之前 — 可以返回 `{"context": "..."}` 注入到系统提示中 |
| `post_llm_call` | 每轮一次，在 LLM 循环完成之后 |
| `on_session_start` | 新会话创建时（仅第一轮） |
| `on_session_end` | 每次 `run_conversation` 调用结束时 |

## 斜杠命令

插件可以注册在 CLI 和消息平台中都能工作的斜杠命令：

```python
def register(ctx):
    ctx.register_command(
        name="greet",
        handler=lambda args: f"Hello, {args or 'world'}!",
        description="Greet someone",
        args_hint="[name]",
        aliases=("hi",),
    )
```

处理器接收参数字符串（`/greet` 之后的所有内容）并返回要显示的字符串。注册的命令会自动出现在 `/help`、Tab 自动补全、Telegram 机器人菜单和 Slack 子命令映射中。

| 参数 | 描述 |
|-----------|-------------|
| `name` | 不带斜杠的命令名称 |
| `handler` | 接收 `args: str` 并返回 `str | None` 的可调用对象 |
| `description` | 在 `/help` 中显示 |
| `args_hint` | 使用提示，例如 `"[name]"` |
| `aliases` | 替代名称的元组 |
| `cli_only` | 仅在 CLI 中可用 |
| `gateway_only` | 仅在消息平台中可用 |
| `gateway_config_gate` | 配置点路径（例如 `"display.my_option"`）。当在 `cli_only` 命令上设置时，如果配置值为真，则该命令在网关中变为可用。 |

## 管理插件

```bash
hermes plugins                  # 交互式切换界面 — 用复选框启用/禁用
hermes plugins list             # 显示启用/禁用状态的表格视图
hermes plugins install user/repo  # 从 Git 安装
hermes plugins update my-plugin   # 拉取最新版本
hermes plugins remove my-plugin   # 卸载
hermes plugins enable my-plugin   # 重新启用已禁用的插件
hermes plugins disable my-plugin  # 禁用但不移除
```

不带参数运行 `hermes plugins` 会启动一个交互式 curses 复选框列表（与 `hermes tools` 相同的界面），你可以使用方向键和空格键切换插件的启用/禁用状态。

禁用的插件会保留安装状态，但在加载时会被跳过。禁用列表存储在 `config.yaml` 的 `plugins.disabled` 下：

```yaml
plugins:
  disabled:
    - my-noisy-plugin
```

在运行中的会话里，`/plugins` 会显示当前加载了哪些插件。

查看 **[完整指南](/guides/build-a-hermes-plugin)** 了解处理器约定、模式格式、钩子行为、错误处理和常见错误。
