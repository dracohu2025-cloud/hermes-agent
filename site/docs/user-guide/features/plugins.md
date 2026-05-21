---
sidebar_position: 11
sidebar_label: "插件"
title: "插件"
description: "通过插件系统使用自定义工具、钩子和集成来扩展 Hermes"
---

<a id="plugins"></a>
# 插件

Hermes 拥有一套插件系统，用于添加自定义工具、钩子和集成功能，而无需修改核心代码。

如果你希望为自己、自己的团队或某个项目创建自定义工具，这通常是合适的路径。开发者指南中的 [添加工具](/developer-guide/adding-tools) 页面介绍了内置的 Hermes 核心工具（位于 `tools/` 和 `toolsets.py` 中）。

**→ [构建 Hermes 插件](/guides/build-a-hermes-plugin)** — 包含完整可运行示例的逐步指南。

<a id="quick-overview"></a>
## 快速概览

将包含 `plugin.yaml` 和 Python 代码的目录放入 `~/.hermes/plugins/` 中：

```
~/.hermes/plugins/my-plugin/
├── plugin.yaml      # 清单
├── __init__.py      # register() — 将 schema 连接到处理函数
├── schemas.py       # 工具 schema（LLM 看到的内容）
└── tools.py         # 工具处理函数（调用时执行的内容）
```

启动 Hermes — 你的工具会与内置工具一起出现。模型可以立即调用它们。

<a id="minimal-working-example"></a>
### 最小可运行示例

以下是一个完整的插件，它添加了一个 `hello_world` 工具，并通过钩子记录每次工具调用。

**`~/.hermes/plugins/hello-world/plugin.yaml`**

```yaml
name: hello-world
version: "1.0"
description: A minimal example plugin
```

**`~/.hermes/plugins/hello-world/__init__.py`**

```python
"""Minimal Hermes plugin — registers a tool and a hook."""

import json


def register(ctx):
    # --- 工具：hello_world ---
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

    def handle_hello(params, **kwargs):
        del kwargs
        name = params.get("name", "World")
        return json.dumps({"success": True, "greeting": f"Hello, {name}!"})

    ctx.register_tool(
        name="hello_world",
        toolset="hello_world",
        schema=schema,
        handler=handle_hello,
        description="Return a friendly greeting for the given name.",
    )

    # --- 钩子：记录每次工具调用 ---
    def on_tool_call(tool_name, params, result):
        print(f"[hello-world] tool called: {tool_name}")

    ctx.register_hook("post_tool_call", on_tool_call)
```

将这两个文件放入 `~/.hermes/plugins/hello-world/` 中，重启 Hermes，模型即可立即调用 `hello_world`。每次工具调用后，钩子会打印一行日志。

项目本地插件（位于 `./.hermes/plugins/` 下）默认处于禁用状态。仅对受信任的仓库启用它们，方法是在启动 Hermes 前设置 `HERMES_ENABLE_PROJECT_PLUGINS=true`。

<a id="what-plugins-can-do"></a>
## 插件能做什么

以下每个 `ctx.*` API 都可在插件的 `register(ctx)` 函数内使用。

| 能力 | 方式 |
|-----------|-----|
| 添加工具 | `ctx.register_tool(name=..., toolset=..., schema=..., handler=...)` |
| 添加钩子 | `ctx.register_hook("post_tool_call", callback)` |
| 添加斜杠命令 | `ctx.register_command(name, handler, description)` — 在 CLI 和网关会话中添加 `/name` |
| 从命令调度工具 | `ctx.dispatch_tool(name, args)` — 调用已注册的工具，并自动注入父 Agent 的上下文 |
| 添加 CLI 命令 | `ctx.register_cli_command(name, help, setup_fn, handler_fn)` — 添加 `hermes &lt;plugin&gt; &lt;subcommand&gt;` |
| 注入消息 | `ctx.inject_message(content, role="user")` — 参见 [注入消息](#injecting-messages) |
| 附带数据文件 | `Path(__file__).parent / "data" / "file.yaml"` |
| 绑定技能 | `ctx.register_skill(name, path)` — 以 `plugin:skill` 命名空间加载，通过 `skill_view("plugin:skill")` 使用 |
| 环境变量门控 | 在 `plugin.yaml` 中添加 `requires_env: [API_KEY]` — 在 `hermes plugins install` 时提示 |
| 通过 pip 分发 | `[project.entry-points."hermes_agent.plugins"]` |
| 注册网关平台（Discord、Telegram、IRC 等） | `ctx.register_platform(name, label, adapter_factory, check_fn, ...)` — 参见 [添加平台适配器](/developer-guide/adding-platform-adapters) |
| 注册图像生成后端 | `ctx.register_image_gen_provider(provider)` — 参见 [图像生成提供器插件](/developer-guide/image-gen-provider-plugin) |
| 注册视频生成后端 | `ctx.register_video_gen_provider(provider)` — 参见 [视频生成提供器插件](/developer-guide/video-gen-provider-plugin) |
| 注册上下文压缩引擎 | `ctx.register_context_engine(engine)` — 参见 [上下文引擎插件](/developer-guide/context-engine-plugin) |
| 注册记忆后端 | 在 `plugins/memory/&lt;name&gt;/__init__.py` 中继承 `MemoryProvider` — 参见 [记忆提供器插件](/developer-guide/memory-provider-plugin)（使用独立的发现系统） |
| 运行宿主拥有的 LLM 调用 | `ctx.llm.complete(...)` / `ctx.llm.complete_structured(...)` — 借用用户的活跃模型和认证进行一次性补全，支持可选的 JSON Schema 验证。参见 [插件 LLM 访问](/developer-guide/plugin-llm-access) |
| 注册推理后端（LLM 提供器） | 在 `plugins/model-providers/&lt;name&gt;/__init__.py` 中调用 `register_provider(ProviderProfile(...))` — 参见 [模型提供器插件](/developer-guide/model-provider-plugin)（使用独立的发现系统） |
<a id="plugin-discovery"></a>
## 插件发现

| 来源 | 路径 | 用途 |
|--------|------|----------|
| 内置 | `&lt;repo&gt;/plugins/` | 随 Hermes 一起发布 — 参见[内置插件](/user-guide/features/built-in-plugins) |
| 用户 | `~/.hermes/plugins/` | 个人插件 |
| 项目 | `.hermes/plugins/` | 项目专属插件（需要设置 `HERMES_ENABLE_PROJECT_PLUGINS=true`） |
| pip | `hermes_agent.plugins` entry_points | 分发包 |
| Nix | `services.hermes-agent.extraPlugins` / `extraPythonPackages` | NixOS 声明式安装 — 参见 [Nix 安装](/getting-started/nix-setup#plugins) |

当名称冲突时，后发现的来源会覆盖先发现的来源，因此与内置插件同名的用户插件会替换内置插件。

<a id="plugin-sub-categories"></a>
### 插件子类别

在每个来源中，Hermes 还会识别子类别目录，这些目录将插件路由到专门的发现系统：

| 子目录 | 包含内容 | 发现系统 |
|---|---|---|
| `plugins/`（根目录） | 通用插件 — 工具、钩子、斜杠命令、CLI 命令、内置技能 | `PluginManager`（类型：`standalone` 或 `backend`） |
| `plugins/platforms/&lt;name&gt;/` | 网关通道适配器（`ctx.register_platform()`） | `PluginManager`（类型：`platform`，更深一层） |
| `plugins/image_gen/&lt;name&gt;/` | 图像生成后端（`ctx.register_image_gen_provider()`） | `PluginManager`（类型：`backend`，更深一层） |
| `plugins/memory/&lt;name&gt;/` | 记忆提供者（继承 `MemoryProvider`） | `plugins/memory/__init__.py` 中的**自有加载器**（类型：`exclusive` — 一次只能激活一个） |
| `plugins/context_engine/&lt;name&gt;/` | 上下文压缩引擎（`ctx.register_context_engine()`） | `plugins/context_engine/__init__.py` 中的**自有加载器**（一次只能激活一个） |
| `plugins/model-providers/&lt;name&gt;/` | LLM 提供者配置文件（`register_provider(ProviderProfile(...))`） | `providers/__init__.py` 中的**自有加载器**（首次调用 `get_provider_profile()` 时延迟扫描） |

位于 `~/.hermes/plugins/model-providers/&lt;name&gt;/` 和 `~/.hermes/plugins/memory/&lt;name&gt;/` 的用户插件会覆盖同名的内置插件 — 在 `register_provider()` / `register_memory_provider()` 中遵循后写者胜出规则。放入一个目录，它就会替换内置插件，无需修改仓库。

子类别插件会以**路径派生键**的形式出现在 `hermes plugins list` 和交互式 `hermes plugins` UI 中 — 例如 `observability/langfuse`、`image_gen/openai`、`platforms/teams`。这个键（而不是清单中的 `name:`）是你传递给 `hermes plugins enable …` / `disable …` 的值，也是 `config.yaml` 中 `plugins.enabled` 下要添加的字符串。

<a id="plugins-are-opt-in-with-a-few-exceptions"></a>
## 插件是选择加入的（少数例外）

**通用插件和用户安装的后端默认是禁用的** — 发现机制会找到它们（因此它们会出现在 `hermes plugins` 和 `/plugins` 中），但在你将插件名称添加到 `~/.hermes/config.yaml` 的 `plugins.enabled` 之前，任何带有钩子或工具的插件都不会加载。这样可以防止第三方代码未经你明确同意就运行。

```yaml
plugins:
  enabled:
    - my-tool-plugin
    - disk-cleanup
  disabled:       # 可选的黑名单 — 如果名称同时出现在两个列表中，则始终优先
    - noisy-plugin
```
三种切换状态的方式：

```bash
hermes plugins                    # 交互式切换（空格键勾选/取消勾选）
hermes plugins enable <名称>      # 添加到允许列表
hermes plugins disable <名称>     # 从允许列表中移除并添加到禁用列表
```

执行 `hermes plugins install owner/repo` 后，系统会询问 `立即启用 '名称' 吗？[y/N]` — 默认不启用。如果希望脚本化安装，可使用 `--enable` 或 `--no-enable` 跳过询问。

<a id="what-the-allow-list-does-not-gate"></a>
### 允许列表不限制哪些内容

有几类插件绕过了 `plugins.enabled` 检查——它们是 Hermes 内置功能的一部分，如果默认受限会被坏基本功能：

| 插件类型 | 激活方式 |
|---|---|
| **内置平台插件**（位于 `plugins/platforms/` 下的 IRC、Teams 等） | 自动加载，确保所有随网关通道开箱即用。实际通道通过 `config.yaml` 中的 `gateway.platforms.<名称>.enabled` 开启。 |
| **内置后端**（位于 `plugins/image_gen/` 下的图像生成提供商等） | 自动加载，确保默认后端“开箱即用”。通过 `config.yaml` 中的 `<类别>.provider` 选择（例如 `image_gen.provider: openai`）。 |
| **记忆提供者**（`plugins/memory/`） | 全部发现；只有一个是活跃的，由 `config.yaml` 中的 `memory.provider` 指定。 |
| **上下文引擎**（`plugins/context_engine/`） | 全部发现；只有一个活跃，由 `config.yaml` 中的 `context.engine` 指定。 |
| **模型提供者**（`plugins/model-providers/`） | 位于 `plugins/model-providers/` 下的所有内置提供者在首次调用 `get_provider_profile()` 时被发现并注册。用户每次通过 `--provider` 或 `config.yaml` 选择一个。 |
| **通过 pip 安装的 `backend` 插件** | 通过 `plugins.enabled` 手动启用（与普通插件相同）。 |
| **用户安装的平台**（位于 `~/.hermes/plugins/platforms/`） | 通过 `plugins.enabled` 手动启用——第三方网关适配器需要明确同意。 |

简而言之：**内置的“始终有效”基础设施自动加载；第三方通用插件需要手动启用。** `plugins.enabled` 允许列表专门用于控制用户放入 `~/.hermes/plugins/` 的任意代码。

<a id="migration-for-existing-users"></a>
### 现有用户的迁移

当您升级到支持手动启用插件的 Hermes 版本（配置模式 v21 及以上）时，任何已安装在 `~/.hermes/plugins/` 下且之前不在 `plugins.disabled` 中的用户插件，**会自动继承**到 `plugins.enabled` 中。您现有的配置会继续生效。**内置独立插件不会自动继承**——即使是现有用户也需要明确手动启用。（内置平台/后端插件从来不需要继承，因为它们从未被限制。）

<a id="available-hooks"></a>
## 可用钩子

插件可以为以下生命周期事件注册回调。完整详情、回调签名和示例请参见 **[事件钩子页面](/user-guide/features/hooks#plugin-hooks)**。

| 钩子 | 触发时机 |
|------|---------|
| [`pre_tool_call`](/user-guide/features/hooks#pre_tool_call) | 任何工具执行之前 |
| [`post_tool_call`](/user-guide/features/hooks#post_tool_call) | 任何工具返回之后 |
| [`pre_llm_call`](/user-guide/features/hooks#pre_llm_call) | 每轮一次，在 LLM 循环之前——可以返回 `{"context": "..."}` 来[向用户消息注入上下文](/user-guide/features/hooks#pre_llm_call) |
| [`post_llm_call`](/user-guide/features/hooks#post_llm_call) | 每轮一次，在 LLM 循环之后（仅成功完成的轮次） |
| [`on_session_start`](/user-guide/features/hooks#on_session_start) | 新会话创建时（仅第一轮） |
| [`on_session_end`](/user-guide/features/hooks#on_session_end) | 每次 `run_conversation` 调用结束时 + CLI 退出处理器 |
| [`on_session_finalize`](/user-guide/features/hooks#on_session_finalize) | CLI/网关销毁活跃会话时（`/new`、垃圾回收、CLI 退出） |
| [`on_session_reset`](/user-guide/features/hooks#on_session_reset) | 网关切换新会话密钥时（`/new`、`/reset`、`/clear`、空闲轮换） |
| [`subagent_stop`](/user-guide/features/hooks#subagent_stop) | `delegate_task` 完成后，每个子 Agent 触发一次 |
| [`pre_gateway_dispatch`](/user-guide/features/hooks#pre_gateway_dispatch) | 网关收到用户消息后，在身份验证和调度之前。返回 `{"action": "skip" \| "rewrite" \| "allow", ...}` 以影响流程。 |
<a id="plugin-types"></a>
## 插件类型

Hermes 有四种插件：

| 类型 | 功能 | 选择方式 | 位置 |
|------|-------------|-----------|----------|
| **通用插件** | 添加工具、钩子、斜杠命令、CLI 命令 | 多选（启用/禁用） | `~/.hermes/plugins/` |
| **记忆提供者** | 替换或增强内置记忆 | 单选（一个激活） | `plugins/memory/` |
| **上下文引擎** | 替换内置上下文压缩器 | 单选（一个激活） | `plugins/context_engine/` |
| **模型提供者** | 声明推理后端（OpenRouter、Anthropic 等） | 多注册，通过 `--provider` / `config.yaml` 选择 | `plugins/model-providers/` |

记忆提供者和上下文引擎是**提供者插件**——每种类型一次只能激活一个。模型提供者也是插件，但可以同时加载多个；用户通过 `--provider` 或 `config.yaml` 一次选择一个。通用插件可以任意组合启用。

<a id="pluggable-interfaces-where-to-go-for-each"></a>
## 可插拔接口——每种需求该去哪里

上表展示了四种插件类别，但在"通用插件"中，`PluginContext` 暴露了多个不同的扩展点——而且 Hermes 也接受 Python 插件系统之外的扩展（配置驱动的后端、shell 钩子命令、外部服务器等）。使用下表找到你想构建的内容对应的文档：

| 想添加… | 方式 | 编写指南 |
|---|---|---|
| 一个 LLM 可以调用的**工具** | Python 插件——`ctx.register_tool()` | [构建 Hermes 插件](/guides/build-a-hermes-plugin) · [添加工具](/developer-guide/adding-tools) |
| 一个**生命周期钩子**（LLM 前/后、会话开始/结束、工具过滤器） | Python 插件——`ctx.register_hook()` | [钩子参考](/user-guide/features/hooks) · [构建 Hermes 插件](/guides/build-a-hermes-plugin) |
| 一个 CLI/网关的**斜杠命令** | Python 插件——`ctx.register_command()` | [构建 Hermes 插件](/guides/build-a-hermes-plugin) · [扩展 CLI](/developer-guide/extending-the-cli) |
| 一个 `hermes &lt;thing&gt;` 的**子命令** | Python 插件——`ctx.register_cli_command()` | [扩展 CLI](/developer-guide/extending-the-cli) |
| 一个插件自带的**技能** | Python 插件——`ctx.register_skill()` | [创建技能](/developer-guide/creating-skills) |
| 一个**推理后端**（LLM 提供者：OpenAI 兼容、Codex、Anthropic-Messages、Bedrock） | 提供者插件——在 `plugins/model-providers/&lt;name&gt;/` 中调用 `register_provider(ProviderProfile(...))` | **[模型提供者插件](/developer-guide/model-provider-plugin)** · [添加提供者](/developer-guide/adding-providers) |
| 一个**网关通道**（Discord / Telegram / IRC / Teams 等） | 平台插件——在 `plugins/platforms/&lt;name&gt;/` 中调用 `ctx.register_platform()` | [添加平台适配器](/developer-guide/adding-platform-adapters) |
| 一个**记忆后端**（Honcho、Mem0、Supermemory 等） | 记忆插件——在 `plugins/memory/&lt;name&gt;/` 中继承 `MemoryProvider` | [记忆提供者插件](/developer-guide/memory-provider-plugin) |
| 一个**上下文压缩策略** | 上下文引擎插件——`ctx.register_context_engine()` | [上下文引擎插件](/developer-guide/context-engine-plugin) |
| 一个**图像生成后端**（DALL·E、SDXL 等） | 后端插件——`ctx.register_image_gen_provider()` | [图像生成提供者插件](/developer-guide/image-gen-provider-plugin) |
| 一个**视频生成后端**（Veo、Kling、Pixverse、Grok-Imagine、Runway 等） | 后端插件——`ctx.register_video_gen_provider()` | [视频生成提供者插件](/developer-guide/video-gen-provider-plugin) |
| 一个**TTS 后端**（任何 CLI——Piper、VoxCPM、Kokoro、xtts、语音克隆脚本等） | 配置驱动——在 `config.yaml` 的 `tts.providers.&lt;name&gt;` 下声明，类型为 `type: command` | [TTS 设置](/user-guide/features/tts#custom-command-providers) |
| 一个**STT 后端**（自定义 whisper 二进制、本地 ASR CLI） | 配置驱动——将 `HERMES_LOCAL_STT_COMMAND` 环境变量设置为 shell 模板 | [语音消息转录（STT）](/user-guide/features/tts#voice-message-transcription-stt) |
| 通过 **MCP 的外部工具**（文件系统、GitHub、Linear、Notion、任何 MCP 服务器） | 配置驱动——在 `config.yaml` 中声明 `mcp_servers.&lt;name&gt;`，包含 `command:` / `url:`。Hermes 自动发现服务器的工具并将其与内置工具一起注册。 | [MCP](/user-guide/features/mcp) |
| **额外的技能来源**（自定义 GitHub 仓库、私有技能索引） | CLI——`hermes skills tap add &lt;repo&gt;` | [技能中心](/user-guide/features/skills#skills-hub) · [发布自定义 tap](/user-guide/features/skills#publishing-a-custom-skill-tap) |
| **网关事件钩子**（在 `gateway:startup`、`session:start`、`agent:end`、`command:*` 时触发） | 将 `HOOK.yaml` + `handler.py` 放入 `~/.hermes/hooks/&lt;name&gt;/` | [事件钩子](/user-guide/features/hooks#gateway-event-hooks) |
| **Shell 钩子**（在事件发生时运行 shell 命令——通知、审计日志、桌面提醒） | 配置驱动——在 `config.yaml` 的 `hooks:` 下声明 | [Shell 钩子](/user-guide/features/hooks#shell-hooks) |
:::note
并非所有功能都是 Python 插件。部分扩展点有意采用**配置驱动的 Shell 命令**（TTS、STT、Shell 钩子），这样你已有的任何 CLI 都可以直接作为插件使用，而无需编写 Python 代码。另一些扩展点是**外部服务器**（MCP），Agent 会连接它们并自动注册其中的工具。还有一些是**即插即用的目录**（gateway 钩子），自带清单格式。请根据你的集成场景选择最合适的扩展方式；上表中每个扩展方式的编写指南都涵盖了占位符、发现机制和示例。
:::

<a id="nixos-declarative-plugins"></a>
## NixOS 声明式插件

在 NixOS 上，插件可以通过模块选项声明式安装——无需执行 `hermes plugins install`。详见 **[Nix 安装指南](/getting-started/nix-setup#plugins)**。

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

声明式插件会以 `nix-managed-` 为前缀进行符号链接——它们可以与手动安装的插件共存，当从 Nix 配置中移除时，会自动清理干净。

<a id="managing-plugins"></a>
## 管理插件

```bash
hermes plugins                                       # 统一的交互式界面
hermes plugins list                                  # 表格：已启用 / 已禁用 / 未启用
hermes plugins install user/repo                     # 从 Git 安装，然后提示 是否启用？[y/N]
hermes plugins install user/repo --enable            # 安装并启用（无提示）
hermes plugins install user/repo --no-enable         # 安装但保持禁用状态（无提示）
hermes plugins update my-plugin                      # 拉取最新版本
hermes plugins remove my-plugin                      # 卸载
hermes plugins enable my-plugin                      # 加入允许列表（扁平插件）
hermes plugins enable observability/langfuse         # 加入允许列表（子类别插件）
hermes plugins disable my-plugin                     # 从允许列表中移除并加入禁用列表
```

对于位于子类别目录下的插件（例如 `plugins/observability/langfuse/`、`plugins/image_gen/openai/`），请使用完整的 `<类别>/<插件>` 键——这正是 `hermes plugins list` 在 **名称** 列中显示的内容。

<a id="interactive-ui"></a>
### 交互式界面

不带参数运行 `hermes plugins` 会打开一个复合交互屏幕：

```
插件
  ↑↓ 导航  SPACE 切换  ENTER 配置/确认  ESC 完成

  常规插件
 → [✓] my-tool-plugin — 自定义搜索工具
   [ ] webhook-notifier — 事件钩子
   [ ] disk-cleanup — 自动清理临时文件 [bundled]
   [ ] observability/langfuse — 将跟踪记录/LLM 调用/工具发送到 Langfuse [bundled]

  提供商插件
     内存提供商          ▸ honcho
     上下文引擎           ▸ compressor
```

- **常规插件部分** — 复选框，按 SPACE 切换。勾选 = 在 `plugins.enabled` 中，未勾选 = 在 `plugins.disabled`（显式关闭）。
- **提供商插件部分** — 显示当前选择。按 ENTER 进入单选器，选择其中一个活跃的提供商。
- 捆绑插件会在同一列表中显示，并带有 `[bundled]` 标签。
Provider 插件选择结果会保存到 `config.yaml` 中：

```yaml
memory:
  provider: "honcho"      # 空字符串 = 仅使用内置

context:
  engine: "compressor"    # 默认内置压缩器
```

<a id="enabled-vs-disabled-vs-neither"></a>
### 已启用、已禁用与未启用

插件分为三种状态：

| 状态 | 含义 | 在 `plugins.enabled` 中？ | 在 `plugins.disabled` 中？ |
|---|---|---|---|
| `enabled` | 下次会话时加载 | 是 | 否 |
| `disabled` | 显式关闭 — 即使也出现在 `enabled` 中也不会加载 | （无关） | 是 |
| `not enabled` | 已发现但从未主动启用 | 否 | 否 |

新安装或捆绑的插件默认状态为 `not enabled`（未启用）。`hermes plugins list` 会显示所有三种不同状态，这样你就可以区分哪些被显式关闭了，哪些只是等待启用。

在运行中的会话里，`/plugins` 会显示当前已加载的插件。

<a id="injecting-messages"></a>
## 注入消息 {#injecting-messages}

插件可以使用 `ctx.inject_message()` 将消息注入到当前对话中：

```python
ctx.inject_message("New data arrived from the webhook", role="user")
```

**签名：** `ctx.inject_message(content: str, role: str = "user") -> bool`

工作原理：

- 如果 Agent 处于**空闲**状态（等待用户输入），消息会被排队作为下一个输入并开始一个新回合。
- 如果 Agent 处于**回合中间**（正在主动运行），消息会中断当前操作——就像用户输入一条新消息并按下了回车键。
- 对于非 `"user"` 角色，内容会加上 `[role]` 前缀（例如 `[system] ...`）。
- 如果消息成功排队则返回 `True`，如果没有可用的 CLI 引用（例如在网关模式下）则返回 `False`。

这使远程控制查看器、消息桥接器或 webhook 接收器等插件能够从外部源向对话中注入消息。

:::note
`inject_message` 仅在 CLI 模式下可用。在网关模式下，没有 CLI 引用，该方法返回 `False`。
:::

有关处理程序协议、模式格式、钩子行为、错误处理及常见错误的完整说明，请参阅**[[完整指南](/guides/build-a-hermes-plugin)**。
