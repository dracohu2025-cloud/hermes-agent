---
sidebar_position: 11
sidebar_label: "插件"
title: "插件"
description: "通过插件系统使用自定义工具、钩子和集成来扩展 Hermes"
---

# 插件 {#plugins}

Hermes 拥有一个插件系统，用于添加自定义工具、钩子和集成，而无需修改核心代码。

**→ [构建一个 Hermes 插件](/guides/build-a-hermes-plugin)** — 包含完整可运行示例的分步指南。

## 快速概览 {#quick-overview}

将包含 `plugin.yaml` 和 Python 代码的目录放入 `~/.hermes/plugins/`：

```
~/.hermes/plugins/my-plugin/
├── plugin.yaml      # 清单文件
├── __init__.py      # register() — 将 schema 与处理函数关联
├── schemas.py       # 工具 schema（LLM 看到的内容）
└── tools.py         # 工具处理函数（被调用时执行的内容）
```

启动 Hermes — 你的工具会与内置工具一同出现。模型可以立即调用它们。

### 最小工作示例 {#minimal-working-example}

以下是一个完整的插件，它添加了一个 `hello_world` 工具，并通过钩子记录每次工具调用。

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
    # --- 工具：hello_world ---
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
        return f"Hello, {name}! 👋  (来自 hello-world 插件)"

    ctx.register_tool("hello_world", schema, handle_hello)

    # --- 钩子：记录每次工具调用 ---
    def on_tool_call(tool_name, params, result):
        print(f"[hello-world] 工具被调用：{tool_name}")

    ctx.register_hook("post_tool_call", on_tool_call)
```

将这两个文件放入 `~/.hermes/plugins/hello-world/`，重启 Hermes，模型就可以立即调用 `hello_world`。每次工具调用后，钩子会打印一行日志。

项目本地插件（位于 `./.hermes/plugins/`）默认是禁用的。仅对受信任的仓库启用它们，方法是在启动 Hermes 前设置 `HERMES_ENABLE_PROJECT_PLUGINS=true`。

## 插件能做什么 {#what-plugins-can-do}

| 能力 | 如何实现 |
|-----------|-----|
| 添加工具 | `ctx.register_tool(name, schema, handler)` |
| 添加钩子 | `ctx.register_hook("post_tool_call", callback)` |
| 添加斜杠命令 | `ctx.register_command(name, handler, description)` — 在 CLI 和网关会话中添加 `/name` |
| 添加 CLI 命令 | `ctx.register_cli_command(name, help, setup_fn, handler_fn)` — 添加 `hermes &lt;plugin&gt; &lt;subcommand&gt;` |
| 注入消息 | `ctx.inject_message(content, role="user")` — 参见 [注入消息](#injecting-messages) |
| 附带数据文件 | `Path(__file__).parent / "data" / "file.yaml"` |
| 打包技能 | `ctx.register_skill(name, path)` — 以 `plugin:skill` 命名空间，通过 `skill_view("plugin:skill")` 加载 |
| 基于环境变量控制 | 在 plugin.yaml 中设置 `requires_env: [API_KEY]` — 在 `hermes plugins install` 时提示 |
| 通过 pip 分发 | `[project.entry-points."hermes_agent.plugins"]` |
## 插件发现 {#plugin-discovery}

| 来源   | 路径                             | 用途                                                                 |
|--------|----------------------------------|----------------------------------------------------------------------|
| 内置   | `<仓库>/plugins/`                | 随 Hermes 发布 — 参见[内置插件](/user-guide/features/built-in-plugins) |
| 用户   | `~/.hermes/plugins/`             | 个人插件                                                             |
| 项目   | `.hermes/plugins/`               | 项目级插件（需要设置 `HERMES_ENABLE_PROJECT_PLUGINS=true`）          |
| pip    | `hermes_agent.plugins` 入口点    | 分发包                                                               |
| Nix    | `services.hermes-agent.extraPlugins` / `extraPythonPackages` | NixOS 声明式安装 — 参见 [Nix 配置](/getting-started/nix-setup#plugins) |

当名称冲突时，后列出的来源会覆盖先列出的来源，因此与内置插件同名的用户插件会替换内置插件。

## 插件需手动启用 {#plugins-are-opt-in}

**每个插件——无论是用户安装的、内置的还是 pip 安装的——默认都是禁用的。** 发现机制会找到它们（因此它们会出现在 `hermes plugins` 和 `/plugins` 中），但除非你将插件名称添加到 `~/.hermes/config.yaml` 的 `plugins.enabled` 中，否则不会加载任何内容。这样可以防止任何带有钩子或工具的插件未经你的明确同意就运行。

```yaml
plugins:
  enabled:
    - my-tool-plugin
    - disk-cleanup
  disabled:       # 可选拒绝列表——如果某名称同时出现在两个列表中，禁用列表优先
    - noisy-plugin
```

三种切换状态的方式：

```bash
hermes plugins                    # 交互式开关（空格键勾选/取消）
hermes plugins enable <name>      # 添加到允许列表
hermes plugins disable <name>     # 从允许列表中移除并添加到禁用列表
```

执行 `hermes plugins install owner/repo` 后，你会被询问 `Enable 'name' now? [y/N]` —— 默认选否。对于脚本化安装，可使用 `--enable` 或 `--no-enable` 跳过提示。

### 现有用户的迁移 {#migration-for-existing-users}

当你升级到支持手动启用插件的 Hermes 版本（配置模式 v21+）时，任何已经安装在 `~/.hermes/plugins/` 下且不在 `plugins.disabled` 中的用户插件，都会**自动被纳入** `plugins.enabled`。你现有的配置会继续正常工作。内置插件**不会**被自动纳入——即使是现有用户也必须手动启用。

## 可用的钩子 {#available-hooks}

插件可以为这些生命周期事件注册回调函数。完整详情、回调签名和示例请参见**[事件钩子页面](/user-guide/features/hooks#plugin-hooks)**。

| 钩子                                                               | 触发时机                                  |
|--------------------------------------------------------------------|-------------------------------------------|
| [`pre_tool_call`](/user-guide/features/hooks#pre_tool_call)   | 任何工具执行前                            |
| [`post_tool_call`](/user-guide/features/hooks#post_tool_call) | 任何工具返回后                            |
| [`pre_llm_call`](/user-guide/features/hooks#pre_llm_call)     | 每轮一次，在 LLM 循环之前——可返回 `{"context": "..."}` 以[将上下文注入用户消息](/user-guide/features/hooks#pre_llm_call) |
| [`post_llm_call`](/user-guide/features/hooks#post_llm_call)   | 每轮一次，在 LLM 循环之后（仅成功轮次）   |
| [`on_session_start`](/user-guide/features/hooks#on_session_start) | 新会话创建时（仅第一轮）                |
| [`on_session_end`](/user-guide/features/hooks#on_session_end) | 每次 `run_conversation` 调用结束时 + CLI 退出处理 |
| [`on_session_finalize`](/user-guide/features/hooks#on_session_finalize) | CLI/网关拆解活跃会话时（`/new`、GC、CLI退出） |
| [`on_session_reset`](/user-guide/features/hooks#on_session_reset) | 网关换入新会话密钥时（`/new`、`/reset`、`/clear`、空闲轮换） |
| [`subagent_stop`](/user-guide/features/hooks#subagent_stop)   | 每个子 Agent 在 `delegate_task` 完成后    |
| [`pre_gateway_dispatch`](/user-guide/features/hooks#pre_gateway_dispatch) | 网关收到用户消息后、验证和分发前。返回 `{"action": "skip" \| "rewrite" \| "allow", ...}` 以影响流程。 |
## 插件类型 {#plugin-types}

Hermes 有三种插件：

| 类型 | 功能 | 选择方式 | 位置 |
|------|-------------|-----------|----------|
| **通用插件** | 添加工具、钩子、斜杠命令、CLI 命令 | 多选（启用/禁用） | `~/.hermes/plugins/` |
| **记忆提供者** | 替换或增强内置记忆 | 单选（一个生效） | `plugins/memory/` |
| **上下文引擎** | 替换内置上下文压缩器 | 单选（一个生效） | `plugins/context_engine/` |

记忆提供者和上下文引擎属于**提供者插件**——每种类型同时只能有一个生效。通用插件可以任意组合启用。

## NixOS 声明式插件 {#nixos-declarative-plugins}

在 NixOS 上，可以通过模块选项声明式安装插件——无需执行 `hermes plugins install`。完整详情请参阅 **[Nix 设置指南](/getting-started/nix-setup#plugins)**。

```nix
services.hermes-agent = {
  # 目录插件（包含 plugin.yaml 的源码树）
  extraPlugins = [ (pkgs.fetchFromGitHub { ... }) ];
  # 入口点插件（pip 包）
  extraPythonPackages = [ (pkgs.python312Packages.buildPythonPackage { ... }) ];
  # 在配置中启用
  settings.plugins.enabled = [ "my-plugin" ];
};
```

声明式插件会以 `nix-managed-` 前缀进行符号链接——它们与手动安装的插件共存，当从 Nix 配置中移除时会自动清理。

## 管理插件 {#managing-plugins}

```bash
hermes plugins                               # 统一交互界面
hermes plugins list                          # 表格：已启用 / 已禁用 / 未启用
hermes plugins install user/repo             # 从 Git 安装，然后提示 启用？[y/N]
hermes plugins install user/repo --enable    # 安装并启用（无提示）
hermes plugins install user/repo --no-enable # 安装但保持禁用（无提示）
hermes plugins update my-plugin              # 拉取最新版本
hermes plugins remove my-plugin              # 卸载
hermes plugins enable my-plugin              # 添加到允许列表
hermes plugins disable my-plugin             # 从允许列表移除并添加到禁用列表
```

### 交互界面 {#interactive-ui}

运行不带参数的 `hermes plugins` 会打开一个组合式交互界面：

```
插件
  ↑↓ 导航  SPACE 切换  ENTER 配置/确认  ESC 完成

  通用插件
 → [✓] my-tool-plugin — 自定义搜索工具
   [ ] webhook-notifier — 事件钩子
   [ ] disk-cleanup — 自动清理临时文件 [内置]

  提供者插件
     记忆提供者          ▸ honcho
     上下文引擎           ▸ compressor
```

- **通用插件区域** —— 复选框，按 SPACE 切换。选中 = 在 `plugins.enabled` 中，未选中 = 在 `plugins.disabled` 中（显式关闭）。
- **提供者插件区域** —— 显示当前选择。按 ENTER 进入单选选择器，选择要生效的提供者。
- 内置插件会出现在同一列表中，并带有 `[内置]` 标签。

提供者插件的选择会保存到 `config.yaml`：

```yaml
memory:
  provider: "honcho"      # 空字符串 = 仅使用内置

context:
  engine: "compressor"    # 默认内置压缩器
```
### 已启用 vs. 已禁用 vs. 未启用 {#enabled-vs-disabled-vs-neither}

插件处于三种状态之一：

| 状态 | 含义 | 在 `plugins.enabled` 中？ | 在 `plugins.disabled` 中？ |
|---|---|---|---|
| `enabled` | 下次会话时加载 | 是 | 否 |
| `disabled` | 显式关闭——即使也在 `enabled` 中也不会加载 | （无关） | 是 |
| `not enabled` | 已发现但从未选择启用 | 否 | 否 |

新安装或捆绑的插件默认状态为 `not enabled`。`hermes plugins list` 会显示所有三种不同状态，这样你就能区分哪些是显式关闭的，哪些只是等待启用。

在运行中的会话里，`/plugins` 会显示当前已加载的插件。

## 注入消息 {#injecting-messages}

插件可以使用 `ctx.inject_message()` 向当前对话注入消息：

```python
ctx.inject_message("New data arrived from the webhook", role="user")
```

**签名：** `ctx.inject_message(content: str, role: str = "user") -> bool`

工作原理：

- 如果 Agent 处于**空闲**状态（等待用户输入），消息会被排队作为下一个输入，并开始新的一轮。
- 如果 Agent 处于**回合中**（正在运行），消息会中断当前操作——就像用户输入新消息并按下回车一样。
- 对于非 `"user"` 角色，内容会以 `[role]` 作为前缀（例如 `[system] ...`）。
- 如果消息成功排队，返回 `True`；如果没有可用的 CLI 引用（例如在网关模式下），返回 `False`。

这使得远程控制查看器、消息桥接或 Webhook 接收器等插件能够从外部来源向对话中注入消息。

:::note
`inject_message` 仅在 CLI 模式下可用。在网关模式下，没有 CLI 引用，该方法会返回 `False`。
:::

有关处理程序契约、模式格式、钩子行为、错误处理和常见错误，请参阅 **[完整指南](/guides/build-a-hermes-plugin)**。
